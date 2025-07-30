import warnings
from importlib import resources

import pandas as pnd
import cobra

import gempipe

from ..commons import get_biomass_dict
from ..commons import apply_medium_given_column
from ..commons import verify_growth
from ..commons import import_from_universe

__OPTTHR__ = 0.001   # optimization threshold



def include_forced(logger, model, universe, force_inclusion):
    
    
    if force_inclusion != '-':
        introduced_rids = []
        forced_rids = force_inclusion.split(',')
        
        modeled_rids = [r.id for r in model.reactions]
        universal_rids = [r.id for r in universe.reactions]
        
        for rid in forced_rids: 
            
            if rid not in universal_rids:
                logger.info(f"Ignoring reaction ID '{rid}' since it's not included in the universe.")
                continue
            
            if rid not in modeled_rids:
                import_from_universe(model, universe, rid, gpr='')
                introduced_rids.append(rid)
            else:
                logger.debug(f"Requested reaction ID '{rid}' was already included.")
                
        logger.info(f"Reactions forcibly included and orphans: {introduced_rids}.")
        
        
        
def remove_forced(logger, model, universe, force_removal):
    
    
    if force_removal != '-':
        removed_rids = []
        forced_rids = force_removal.split(',')
        
        modeled_rids = [r.id for r in model.reactions]
        universal_rids = [r.id for r in universe.reactions]
        
        for rid in forced_rids: 
            
            if rid not in universal_rids:
                logger.info(f"Ignoring reaction ID '{rid}' since it's not included in the universe.")
                continue
            
            if rid not in modeled_rids:
                logger.debug(f"Requested reaction ID '{rid}' was already excluded from the model.")
            else:
                removed_rids.append(rid)

        # remove collected reactions:
        with warnings.catch_warnings():
            # avoid warnings like "python3.9/site-packages/cobra/core/group.py:147: UserWarning: need to pass in a list"
            warnings.simplefilter("ignore")
            model.remove_reactions(removed_rids) # this works also with rids instaead of Rs

        logger.info(f"Reactions forcibly removed: {removed_rids}.")
        


def get_repository_nogenes(logger, universe, exclude_orphans):
    # Provide a gene-free, evetually orphan-free  repository: reference or universe.


    # make an editable copy:
    repository_nogenes = universe.copy()
    
    
    if exclude_orphans:
            
            
        # collect orphan:
        to_remove = []
        for r in repository_nogenes.reactions: 
            if len(r.genes) == 0:
                if len(r.metabolites) != 1 and r.id != 'Biomass':   # exclude exchanges/sinks/demands/biomass
                    to_remove.append(r)
                    logger.debug(f"Removing orphan: {r.id} ({r.reaction}).")
              
            
        # remove orphan reactions:
        with warnings.catch_warnings():
            # avoid warnings like "python3.9/site-packages/cobra/core/group.py:147: UserWarning: need to pass in a list"
            warnings.simplefilter("ignore")
            repository_nogenes.remove_reactions(to_remove)
        logger.info(f"Removed {len(to_remove)} orphans before gap-filling.")


    # remove genes to avoid the "ValueError: id purP is already present in list"
    cobra.manipulation.delete.remove_genes(repository_nogenes, [g.id for g in repository_nogenes.genes], remove_reactions=False)

    
    return repository_nogenes



def gapfill_on_media(logger, model, universe, expcon, media, varprec, exclude_orphans):
    
    
    
    # get biomass precursors to gap-fill: 
    biomass_mids = []
    for value in get_biomass_dict().values(): biomass_mids = biomass_mids + value
    
    
    # prepare biomass sheet for excel output
    df_B = pnd.DataFrame()
    df_B['name'] = None
    df_B['status'] = None
    df_B['coeff'] = None
    for mid in biomass_mids:
        
        df_B.loc[mid, 'name'] = universe.metabolites.get_by_id(mid).name
        df_B.loc[mid, 'coeff'] = 0.001
        if mid in varprec.keys():
            df_B.loc[mid, 'status'] = f'conditional: ({varprec[mid]})'
            if mid not in [m.id for m in  model.reactions.Biomass.reactants]:  
                df_B.loc[mid, 'coeff'] = 'removed'
        else:  # biomass precursor is NOT variable (it's mandatory)
            df_B.loc[mid, 'status'] = 'mandatory'
            
    
    # get involved media:
    if media == '-':
        logger.info(f"No media provided: gap-filling will be skipped.")
        return df_B
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
        
        
    # get the repository of reactions:
    repository_nogenes = get_repository_nogenes(logger, universe, exclude_orphans)
    
    
    logger.info(f"Gap-filling for biomass on {len(media)} media...")
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column on the excel output
        df_B[f'{medium}'] = None
        logger.debug(f"Gap-filling on medium '{medium}'...")
                    
            
        # apply medium both on universe and model:
        response = apply_medium_given_column(logger, repository_nogenes, medium, expcon['media'][medium])
        if response == 1: return 1
        if not verify_growth(repository_nogenes):
            logger.error(f"Medium '{medium}' does not support growth of universe.")
            return 1
        
        response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
        if response == 1: return 1
        if verify_growth(model):
            logger.info(f"No need to gapfill model on medium '{medium}'.")
            continue


        # launch gap-filling separately for each biomass precursor:
        for mid in biomass_mids:
            # skip conditional precursors: 
            if mid in [m.id for m in model.reactions.Biomass.reactants]:
            
                # save time if it can already be synthesized
                if gempipe.can_synth(model, mid)[0]:
                    df_B.loc[mid, f'{medium}'] = '/'
                    logger.debug(f"Gap-filled 0 reactions on medium '{medium}' for '{mid}': [].")
                    continue   # save time!

                    
                # otherwise perform the actual gap-fill:    
                suggested_rids = gempipe.perform_gapfilling(model, repository_nogenes, mid, nsol=1, minflux=0.1, boost=True, verbose=False)
                if suggested_rids == None:
                    logger.error(f"The gap-filling problem seems too hard for '{mid}' on medium '{medium}': should '{mid}' be included in '{medium}'?")
                    return 1
                
                df_B.loc[mid, f'{medium}'] = '; '.join([f'+{i}' for i in suggested_rids]) 
                logger.debug(f"Gap-filled {len(suggested_rids)} reactions on medium '{medium}' for '{mid}': {suggested_rids}.")
                for rid in suggested_rids:
                    import_from_universe(model, repository_nogenes, rid, gpr='')
                
                
    return df_B




def edit_trans_reacs(model, exr):
    
    pass
    



def biolog_on_media(logger, model, universe, expcon, media, biolog, exclude_orphans, cnps):
    global __OPTTHR__
    
    
    
    # prepare biomass sheet for excel output
    df_P = pnd.DataFrame()
    
    
    # load assets:
    official_pm_tables = {}
    for pm in ['PM1', 'PM2A', 'PM3B', 'PM4A']:
        with resources.path("gsrap.assets", f"{pm}.csv") as asset_path: 
            official_pm_tables[pm] = pnd.read_csv(asset_path, index_col=1, names=['plate','substrate','source','u1','u2','u3','u4','kc','cas'])
    
    
    # format starting C/N/P/S sources as EXR:
    if biolog == '-':  # 'cnps' is != '-' as checked during main()
        return df_P
    if len(cnps.split(',')) != 4:
        logger.error("Parameter --cnps must be formatted as 4 comma-sperated metabolite IDs (order: C, N, P and S).")
        return 1
    cnps = cnps.split(',')
    # add '_e and 'EX_' where needed.
    cnps = [i + '_e' for i in cnps if i.endswith('_e')==False]
    cnps = ["EX_" + i for i in cnps if i.startswith('EX_')==False]
    cnps = {source: exr for source, exr in zip(['carbon', 'nitrogen','sulfur','phosphorus'], cnps)}
    
    
    # get involved media:
    if media == '-':
        logger.info(f"No media provided: Biolog(R)-based model curation will be skipped.")
        return df_P
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
    
    
    # get plates for this strain
    avail_plates = []
    for pm in ['PM1', 'PM2A', 'PM3B', 'PM4A']:
        if biolog in expcon[pm].columns: 
            avail_plates.append(pm)
    if avail_plates == []:
        logger.info(f"No Biolog(R) plates found for strain '{biolog}': Biolog(R)-based model curation will be skipped.")
        return df_P
    else:
        logger.info(f"Found {len(avail_plates)} Biolog(R) plates for strain '{biolog}': {sorted(avail_plates)}.")
        
        
    # get kc-to-exr dict using built-in annotations:
    kc_to_exr = {}
    for m in model.metabolites: 
        if m.id.endswith('_e') == False:
            continue
        if 'kegg.compound' not in m.annotation.keys():
            continue
        kc_ids = m.annotation['kegg.compound']
        if type(kc_ids) == str: kc_ids = [kc_ids]
        kc_ids = [i for i in kc_ids if i != 'CXXXXX']  
        for kc_id in kc_ids:
            kc_to_exr[kc_id] = f'EX_{m.id}'
        
        
    # prepare rows:
    for pm in avail_plates:
        for well, row in official_pm_tables[pm].iterrows():
            # write substrate name:
            df_P.loc[f"{pm}:{well}", 'substrate'] = row['substrate']
            
            
            # write source type:
            if pm in ['PM1', 'PM2A']: 
                df_P.loc[f"{pm}:{well}", 'source'] = 'carbon'
            elif pm == 'PM3B': 
                df_P.loc[f"{pm}:{well}", 'source'] = 'nitrogen'
            else:
                if well[0] in ['F','G','H']: df_P.loc[f"{pm}:{well}", 'source'] = 'sulfur'
                else: df_P.loc[f"{pm}:{well}", 'source'] = 'phosphorus'
            
            
            # get kc and write the correspondent exchange
            kc = row['kc']
            if type(kc)==float: 
                if row['substrate'] == 'Negative Control': 
                    df_P.loc[f"{pm}:{well}", 'exchange'] = ''   # nagative control well
                else:
                    df_P.loc[f"{pm}:{well}", 'exchange'] = 'missing KEGG codes'  # No C/D/G codes at all
            elif kc.startswith('C'):
                if kc not in kc_to_exr.keys():
                    df_P.loc[f"{pm}:{well}", 'exchange'] = f'NA ({kc})'   # kc available, but still no transporters in db.
                else:
                    df_P.loc[f"{pm}:{well}", 'exchange'] = kc_to_exr[kc]
            elif kc.startswith('D'):
                df_P.loc[f"{pm}:{well}", 'exchange'] =  'unhandled KEGG DRUG code'  # TODO manage exchanges in this case
            elif kc.startswith('G'):
                df_P.loc[f"{pm}:{well}", 'exchange'] =  'unhandled KEGG GLYCAN code'  # TODO manage exchanges in this case
            else:
                df_P.loc[f"{pm}:{well}", 'exchange'] =  '???'  # there should be no other cases
    

                
    # get the repository of reactions:
    repository_nogenes = get_repository_nogenes(logger, universe, exclude_orphans)
    
    
    logger.info(f"Performing Biolog(R)-based model curation on {len(media)} media...")
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column on the excel output
        df_P[f'{medium}'] = None
        logger.debug(f"Performing Biolog(R)-based model curation on medium '{medium}'...")
        
        
        # apply medium both on universe and model:
        # (growth was already verified in 'gapfill_on_media')
        response = apply_medium_given_column(logger, repository_nogenes, medium, expcon['media'][medium])
        if response == 1: return 1
        response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
        if response == 1: return 1
        # 'universe' is already on its minimal medium glc__D/nh4/pi/so4
        # (universe is not used during gap-filling)
    
    
        # iterate pm:wells
        for index, row in df_P.iterrows():
            
            
            # get needed infos
            pm, well = index.split(':')
            source = row['source']
            exr = df_P.loc[f"{pm}:{well}", 'exchange']
            if exr.startswith('EX_') == False:
                exr = None
            start_exr = cnps[source]
            experimental = expcon[pm].loc[well, biolog]
            
            
            # check if 'start_exr' is in the medium (model or universe is the same here)
            if start_exr not in model.medium.keys():
                logger.error(f"Provided starting {source} source ('{start_exr}') is not used in '{medium}' medium. Please correct the --cnps parameter.")
                return 1
            
            
            # skip if transporters for this well are not yet implemented:
            if exr == None:
                continue
        
        
            # Ok the exr is contained in this medium. Proceed with the 2 FBAs:
            performed_gapfilling = False
            suggested_rids = None
            performed_transedit = False
            removing_rids = None
            
            with universe, repository_nogenes, model:
                
                
                # adabpt the atmsphere of the minimal medium:
                if 'EX_o2_e' not in model.medium.keys(): universe.reactions.get_by_id('EX_o2_e').lower_bound = 0 
                if 'EX_co2_e' not in model.medium.keys(): universe.reactions.get_by_id('EX_co2_e').lower_bound = 0 
                
                # save the lower bound for the new exr
                lb = repository_nogenes.reactions.get_by_id(start_exr).lower_bound
                
                # 1st FBA
                # universe
                if   source=='carbon':     universe.reactions.get_by_id('EX_glc__D_e').lower_bound = 0
                elif source=='nitrogen':   universe.reactions.get_by_id('EX_nh4_e').lower_bound = 0
                elif source=='phosphorus': universe.reactions.get_by_id('EX_pi_e').lower_bound = 0
                elif source=='sulfur':     universe.reactions.get_by_id('EX_so4_e').lower_bound = 0
                fba0_unive = verify_growth(universe, boolean=False)
                # repository
                repository_nogenes.reactions.get_by_id(start_exr).lower_bound = 0
                fba0_repos = verify_growth(repository_nogenes, boolean=False)
                # model
                model.reactions.get_by_id(start_exr).lower_bound = 0
                fba0_model = verify_growth(model, boolean=False)         
                
                # 2nd FBA
                # universe
                universe.reactions.get_by_id(exr).lower_bound = -1000
                fba1_unive = verify_growth(universe, boolean=False)
                # repository
                repository_nogenes.reactions.get_by_id(exr).lower_bound = lb
                fba1_repos = verify_growth(repository_nogenes, boolean=False)
                # model
                model.reactions.get_by_id(exr).lower_bound = lb
                fba1_model = verify_growth(model, boolean=False)
                   
                 
                
                # universe cannot utilize this substrate: 
                if (fba1_unive == 'infeasible') \
                or (fba0_unive == 'infeasible' and fba1_unive != 'infeasible' and fba1_unive < __OPTTHR__) \
                or (fba0_unive != 'infeasible' and fba1_unive != 'infeasible' and fba1_unive <= fba0_unive):

                    logger.debug(f"Substrate {pm}':'{well}':'{exr}' (E: {experimental}; Um: {fba0_unive} ▶ {fba1_unive}; Rm: {fba0_repos} ▶ {fba1_repos}; Sm: {fba0_model} ▶ {fba1_model}): universe is unable. Please expand and/or correct the universe.")
                    df_P.loc[index, f'{medium}'] = f"universe unable"
                    #return 1

                # model cannot utilize this substrate on medium:
                elif (fba1_model == 'infeasible') \
                  or (fba0_model == 'infeasible' and fba1_model != 'infeasible' and fba1_model < __OPTTHR__) \
                  or (fba0_model != 'infeasible' and fba1_model != 'infeasible' and fba1_model <= fba0_model):

                    # mismatch FN:
                    if experimental == 1:

                        # universe cannot reproduce experimental in the medium:
                        if (fba1_repos == 'infeasible') \
                        or (fba0_repos == 'infeasible' and fba1_repos != 'infeasible' and fba1_repos < __OPTTHR__) \
                        or (fba0_repos != 'infeasible' and fba1_repos != 'infeasible' and fba1_repos <= fba0_repos):

                            logger.debug(f"Substrate {pm}':'{well}':'{exr}' (E: {experimental}; Um: {fba0_unive} ▶ {fba1_unive}; Rm: {fba0_repos} ▶ {fba1_repos}; Sm: {fba0_model} ▶ {fba1_model}): universe is unable in this medium. Please expand and/or correct the universe.")
                            df_P.loc[index, f'{medium}'] = f"universe unable in medium"
                            #return 1 

                        # universe can be used for gapfilling:
                        else:
                            logger.debug(f"Substrate {pm}':'{well}':'{exr}' (E: {experimental}; Um: {fba0_unive} ▶ {fba1_unive}; Rm: {fba0_repos} ▶ {fba1_repos}; Sm: {fba0_model} ▶ {fba1_model}): gap-filling for this substrate...")

                            # perform the actual gap-filling: 
                            performed_gapfilling = True
                            minflux = __OPTTHR__ if fba1_repos == 'infeasible' else fba1_repos + __OPTTHR__
                            
                            suggested_rids = gempipe.perform_gapfilling(model, repository_nogenes, nsol=1, minflux=minflux, boost=False, verbose=False)
                            if suggested_rids == None:
                                logger.error(f"The gap-filling problem seems too hard for substrate {pm}':'{well}':'{exr} in medium '{medium}'.")
                                return 1

                            df_P.loc[index, f'{medium}'] = '; '.join([f'+{i}' for i in suggested_rids]) 
                            logger.debug(f"Gap-filled {len(suggested_rids)} reactions on medium '{medium}' for substrate {pm}':'{well}':'{exr}: {suggested_rids}.")

                    # it's a match! TN
                    else:
                        logger.debug(f"Substrate {pm}':'{well}':'{exr}' (E: {experimental}; Um: {fba0_unive} ▶ {fba1_unive}; Rm: {fba0_repos} ▶ {fba1_repos}; Sm: {fba0_model} ▶ {fba1_model}): TN match.")
                        df_P.loc[index, f'{medium}'] = f"/"

                # model can utilize this substrate on medium:
                else:

                    # mismatch FP
                    if experimental == 0:

                        logger.debug(f"Substrate {pm}':'{well}':'{exr}' (E: {experimental}; Um: {fba0_unive} ▶ {fba1_unive}; Rm: {fba0_repos} ▶ {fba1_repos}; Sm: {fba0_model} ▶ {fba1_model}): trying to improve accuracy of tranport reactions...")
                        df_P.loc[index, f'{medium}'] = f"TRANSPORT"
                        
                        edit_trans_reacs(model, exr)

                    # it's a match! TP
                    else:
                        logger.debug(f"Substrate {pm}':'{well}':'{exr}' (E: {experimental}; Um: {fba0_unive} ▶ {fba1_unive}; Rm: {fba0_repos} ▶ {fba1_repos}; Sm: {fba0_model} ▶ {fba1_model}): TP match.")
                        df_P.loc[index, f'{medium}'] = f"/"
            
            
            
            # apply modifications:
            if performed_gapfilling == True:
                for rid in suggested_rids:
                    import_from_universe(model, repository_nogenes, rid, gpr='')
            if performed_transedit == True:
                pass   # TODO
            

    return df_P



def remove_disconnected(logger, model):
    
    to_remove = []
    for m in model.metabolites:
        if len(m.reactions) == 0:
            to_remove.append(m)
    model.remove_metabolites(to_remove)
    logger.info(f"Removed {len(to_remove)} disconnected metabolites.")
    
    
    

