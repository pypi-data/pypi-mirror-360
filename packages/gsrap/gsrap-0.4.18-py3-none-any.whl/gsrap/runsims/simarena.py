import pandas as pnd
import cobra


import gempipe 

from ..commons import apply_medium_given_column
from ..commons import verify_growth

__OPTTHR__ = 0.001   # optimization threshold



def grow_on_media(logger, model, expcon, media, fva):
    obj_id = 'max(obj)'
    
    
    # prepare biomass sheet for excel output
    df_G = pnd.DataFrame()
    
    
    # get involved media:
    if media == '-':
        logger.info(f"No media provided: growth simulations will be skipped.")
        return df_G
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
    
    
    # initialize dataframe
    df_G.loc[obj_id, 'name'] = f'Objective reaction {gempipe.get_objectives(model)}'
    for r in model.reactions:
        df_G.loc[r.id, 'name'] = r.name
        
        
    logger.info(f"Growing on {len(media)} media...")
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column con the excel output
        df_G[f'{medium}'] = '/'
        logger.debug(f"Growing on medium '{medium}'...")
                    
        
        # apply medium
        response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
        if response == 1: return 1

    
        # perform FBA
        res_fba = verify_growth(model, boolean=False)
        df_G.loc[obj_id, f'{medium}'] = res_fba
        
        
        # perform FVA if requested:
        if fva and (res_fba not in [0, 'infeasible']):
            logger.debug(f"FVA on medium '{medium}'...")
            df_fva = cobra.flux_analysis.flux_variability_analysis(model, model.reactions, fraction_of_optimum=0.9)
            for rid, row in df_fva.iterrows():
                df_G.loc[rid, f'{medium}'] = f"({round(row['minimum'], 3)}, {round(row['maximum'], 3)})"

    
    return df_G

    

def synthesize_on_media(logger, model, expcon, media, synth):
    
    global __OPTTHR__
    
    # prepare biomass sheet for excel output
    df_S = pnd.DataFrame()
    
    
    # get involved media:
    if synth == False:
        return df_S
    if media == '-':
        logger.info(f"No media provided: biosynthesis test will be skipped.")
        return df_S
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
    
    
    # initialize dataframe
    logger.info(f"Testing synthesis on {len(media)} media...")
    for m in model.metabolites:
        df_S.loc[m.id, 'name'] = m.name
        
        
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column con the excel output
        df_S[f'{medium}'] = None
        logger.debug(f"Testing synthesis on medium '{medium}'...")
                    
        
        # apply medium
        response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
        if response == 1: return 1

    
        for m in model.metabolites:
            if m.id.endswith('_c'):
                binary, obj_value, status = gempipe.can_synth(model, m.id)
                if status =='infeasible':
                    df_S.loc[m.id, f'{medium}'] = 'infeasible'
                elif obj_value == 0:
                    df_S.loc[m.id, f'{medium}'] = 0
                elif obj_value < __OPTTHR__:
                    df_S.loc[m.id, f'{medium}'] = f'<{__OPTTHR__}'
                else:
                    df_S.loc[m.id, f'{medium}'] = round(obj_value, 3)

    
    return df_S



def omission_on_media(logger, model, expcon, media, omission):
        
    
    # define metabolites for single omission experiments  
    # Note: they are all universal
    pure_mids = set([
        # 20 aminoacids
        'ala__L', 'arg__L', 'asn__L', 'asp__L', 'cys__L', 
        'gln__L', 'glu__L', 'gly', 'his__L', 'ile__L', 
        'leu__L', 'lys__L', 'met__L', 'phe__L', 'pro__L', 
        'ser__L', 'thr__L', 'trp__L', 'tyr__L', 'val__L', 
        # 5 nucleotides
        'ade', 'gua', 'csn', 'thym', 'ura'])
    modeled_rids = [r.id for r in model.reactions]
    
    
    # prepare biomass sheet for excel output
    df_O = pnd.DataFrame()
    
    
    # get involved media:
    if omission == False:
        return df_O
    if media == '-':
        logger.info(f"No media provided: single omissions will be skipped.")
        return df_O
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
    
        
    # check if the target exchange reaction exists:
    for pure_mid in list(pure_mids):
        if f'EX_{pure_mid}_e' not in modeled_rids:
            logger.debug(f"Exchange reaction 'EX_{pure_mid}_e' not found during single omissions: it will be ignored.")
            df_O.loc[pure_mid, 'name'] = 'NA'
            pure_mids = pure_mids - set([pure_mid]) 
        else:  # initialize dataframe
            m = model.metabolites.get_by_id(f'{pure_mid}_e')
            df_O.loc[pure_mid, 'name'] = m.name
    
    
    logger.info(f"Performing single omissions on {len(media)} media...")
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column on the excel output
        df_O[f'{medium}'] = None
        logger.debug(f"Performing single omissions on medium '{medium}'...")
        
        
        # apply medium
        response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
        if response == 1: return 1


        # set up exchange reactions:
        for pure_mid1 in pure_mids:
            for pure_mid2 in pure_mids:
                exr_id = f'EX_{pure_mid2}_e'
                
                if pure_mid2 != pure_mid1:
                    model.reactions.get_by_id(exr_id).lower_bound = -1000
                else:
                    model.reactions.get_by_id(exr_id).lower_bound = -0
                    
                    
            # perform FBA
            res_fba = verify_growth(model, boolean=False)
            df_O.loc[pure_mid1, f'{medium}'] = res_fba
               
            
    return df_O



def clean_formula(formula):
    
    # avoid confusion with 'C':
    formula = formula.replace('Ca', '').replace('Co', '').replace('Cu', '').replace('Cd', '').replace('Cr', '').replace('Cs', '').replace('Cl', '')   
    # avoid confusion with 'N':
    formula = formula.replace('Na', '').replace('Nb', '').replace('Ni', '').replace('Ne', '')
    # avoid confusion with 'P':
    formula = formula.replace('Pd', '').replace('Pt', '').replace('Pb', '').replace('Po', '')
    # avoid confusion with 'S':
    formula = formula.replace('Sc', '').replace('Si', '').replace('Sn', '').replace('Sb', '').replace('Se', '')
    
    return formula



def get_CNPS_sources(model):
    
    CNPS_sources = {'C': set(), 'N': set(), 'P': set(), 'S': set()}
    for r in model.reactions: 
        if len(r.metabolites)==1 and list(r.metabolites)[0].id.endswith('_e'):
            m = list(r.metabolites)[0]
            
            formula = m.formula
            formula = clean_formula(formula)
            
            if 'C' in formula: CNPS_sources['C'].add(r.id)
            if 'N' in formula: CNPS_sources['N'].add(r.id)
            if 'P' in formula: CNPS_sources['P'].add(r.id)
            if 'S' in formula: CNPS_sources['S'].add(r.id)
    
    return CNPS_sources


    
def get_source_name(atom):
    
    if atom=='C': return 'carbon'
    elif atom=='N': return 'nitrogen'
    elif atom=='P': return 'phosphorus'
    elif atom=='S': return 'sulfur'
    
    
    
def cnps_on_media(logger, model, expcon, media, cnps):
    
    
    # prepare biomass sheet for excel output
    df_C = pnd.DataFrame()
    
    
    # get involved media:
    if cnps == '-':
        return df_C
    if media == '-':
        logger.info(f"No media provided: alternative substrate analysis will be skipped.")
        return df_C
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
    
    
    # get main/starting C/N/P/S sources:
    if cnps == 'std': cnps = 'glc__D,nh4,pi,so4'
    startings = cnps.split(',')
    if len(startings) != 4: 
        logger.error(f"Starting sources must be 4: C, N, P, and S, in this order ({len(startings)} provided: {startings}).")
        return 1
    modeled_rids = [r.id for r in model.reactions]
    source_to_exr = {}
    for mid, source in zip(startings, ['C','N','P','S']):
        if mid.endswith('_e'): 
            mid_e = mid
        else: mid_e = mid + '_e'
        exr_id = f'EX_{mid_e}'
        if exr_id not in modeled_rids:
            logger.error(f"Expected exchange for {source} source not found (provided metabolite: '{mid}'; expected exchange: '{exr_id}').")
            return 1
        else:
            m = model.metabolites.get_by_id(mid_e)
            if source not in clean_formula(m.formula):
                logger.error(f"{source} source provided ('{mid}') does not contain {source} atoms.")
                return 1
            else:
                source_to_exr[source] = exr_id
            

    # define rows
    CNPS_sources = get_CNPS_sources(model)
    for source in ['C','N','P','S']:
        for exr_id in CNPS_sources[source]:
            m = list(model.reactions.get_by_id(exr_id).metabolites)[0]
            df_C.loc[f"[{source}] {exr_id}", 'source'] = get_source_name(source)
            df_C.loc[f"[{source}] {exr_id}", 'exchange'] = exr_id 
            df_C.loc[f"[{source}] {exr_id}", 'name'] = m.name    
    
    
    logger.info(f"Performing alternative substrate analysis on {len(media)} media...")
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column on the excel output
        df_C[f'{medium}'] = None
        logger.debug(f"Performing alternative substrate analysis on medium '{medium}'...")
        
        
        not_part = set()
        for source in ['C','N','P','S']:
            for exr_id in CNPS_sources[source]:
                
                # apply medium
                response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
                if response == 1: return 1
            
                
                # maybe the starting substrate is not part of the medium
                if source_to_exr[source] not in list(model.medium.keys()):
                    not_part.add(f"[{source}] {source_to_exr[source]}")
                    df_C.loc[f"[{source}] {exr_id}", medium] = f"NA"
                    continue
                
            
                model.reactions.get_by_id(source_to_exr[source]).lower_bound = -0
                obj0 = verify_growth(model, boolean=False)
                model.reactions.get_by_id(exr_id).lower_bound = -1000
                obj1 = verify_growth(model, boolean=False)
                
                
                if obj1 == 'infeasible':
                    df_C.loc[f"[{source}] {exr_id}", medium] = 'infeasible'
                elif obj0 == 'infeasible':
                    df_C.loc[f"[{source}] {exr_id}", medium] = f"{obj1} (Δ=/)"
                else:
                    df_C.loc[f"[{source}] {exr_id}", medium] = f"{obj1} (Δ={obj1-obj0})"
        
    
        # log if some starting source was not contained in this medium
        if not_part != set(): 
            logger.debug(f"Specified starting sources {not_part} were not contained in medium '{medium}'.")
    
    return df_C
    


def essential_genes_on_media(logger, model, expcon, media, essential):
    
    global __OPTTHR__
    
    
    # prepare biomass sheet for excel output
    df_E = pnd.DataFrame()
    
    
    # get involved media:
    if essential == False:
        return df_E
    if media == '-':
        logger.info(f"No media provided: essential genes prediction will be skipped.")
        return df_E
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
    

    # define rows
    for g in model.genes:
        if g.id in ['spontaneous', 'orphan']:
            continue
        df_E.loc[f"{g.id}", 'name'] = g.name    
        df_E.loc[f"{g.id}", 'involving'] = '; '.join([r.id for r in g.reactions])
    
    
    logger.info(f"Predicting essential genes on {len(media)} media...")
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column on the excel output
        df_E[f'{medium}'] = None
        logger.debug(f"Predicting essential genes on medium '{medium}'...")
        
        
        # apply medium
        response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
        if response == 1: return 1
    
    
        # verify growth:
        obj = verify_growth(model, boolean=False)
        if obj in ['infeasible', 0]:
            df_E[f'{medium}'] = 'NA'
            continue
    
        
        single = cobra.flux_analysis.single_gene_deletion(model)
        for index, row in single.iterrows(): 
            gid = list(row['ids'])[0]  # they are single deletions
            if gid in ['spontaneous', 'orphan']:
                continue
                

            if row['status'] == 'infeasible': 
                df_E.loc[f"{gid}", medium] = 'True'
            elif row['growth'] < __OPTTHR__:
                df_E.loc[f"{gid}", medium] = 'True'
            else: 
                df_E.loc[f"{gid}", medium] = round(row['growth'], 3)
    
    return df_E



def growth_factors_on_media(logger, model, expcon, media, factors):
        
    
    # prepare biomass sheet for excel output
    df_F = pnd.DataFrame()
    
    
    # get involved media:
    if factors == False:
        return df_F
    if media == '-':
        logger.info(f"No media provided: essential genes prediction will be skipped.")
        return df_F
    media = media.split(',')
    # at least 1 medium must exist:
    if any([i in expcon['media'].columns for i in media])==False:
        logger.error(f"None of the provided media IDs exist. Available media are {list(expcon['media'].columns)}.")
        return 1
    
    
    # define rows
    df_F['mid'] = ''
    df_F['name'] = ''

    
    logger.info(f"Predicting growth factors on {len(media)} media...")
    for medium in media: 
        if medium not in expcon['media'].columns:
            logger.info(f"Medium '{medium}' does not exists and will be ignored.")
            continue
        # create dedicated column on the excel output
        df_F[f'{medium}'] = None
        logger.debug(f"Predicting growth factors on medium '{medium}'...")
        
        
        # apply medium
        response = apply_medium_given_column(logger, model, medium, expcon['media'][medium])
        if response == 1: return 1
    
    
        # verify growth:
        obj = verify_growth(model, boolean=False)
        if obj not in ['infeasible', 0]:
            df_F[f'{medium}'] = ''
        else:
            while obj in ['infeasible', 0]:
                res_dict = gempipe.sensitivity_analysis(model, scaled=False, top=1)
                for exr_id, value in res_dict.items():
                    if value < 0:
                        model.reactions.get_by_id(exr_id).lower_bound = -1000
                        obj = verify_growth(model, boolean=False)
                        df_F.loc[exr_id, f'{medium}'] = 'ADD'

         
    # populate 'mid'/'name' columns:
    for exr_id, row in df_F.iterrows():
        r = model.reactions.get_by_id(exr_id)
        m = list(r.metabolites)[0]
        df_F.loc[exr_id, 'mid'] = m.id.rsplit('_', 1)[0]
        df_F.loc[exr_id, 'name'] = m.name
    # replace index with 'mid':
    df_F = df_F.set_index('mid', drop=True)
        
        
    return df_F


    

def write_excel_model(model, filepath, df_G, df_S, df_O, df_C, df_E, df_F):
    

    
    # format df_G:  # growth tests
    df_G.insert(0, 'rid', '')  # new columns as first
    df_G['rid'] = df_G.index
    df_G = df_G.reset_index(drop=True)
    
    # format df_S:  # biosynthetic capabilities
    df_S.insert(0, 'mid', '')  # new columns as first
    df_S['mid'] = df_S.index
    df_S = df_S.reset_index(drop=True)
    
    # format df_O:  # single omission
    df_O.insert(0, 'mid', '')  # new columns as first
    df_O['mid'] = df_O.index
    df_O = df_O.reset_index(drop=True)
    
    # format df_C:  phenotype screening (CNPS)
    df_C.insert(0, 'substrate', '')  # new columns as first
    df_C['substrate'] = df_C.index
    df_C = df_C.reset_index(drop=True)
    
    # format df_E:  essential genes
    df_E.insert(0, 'gid', '')  # new columns as first
    df_E['gid'] = df_E.index
    df_E = df_E.reset_index(drop=True)
    
    # format df_F:  growth factors
    df_F.insert(0, 'mid', '')  # new columns as first
    df_F['mid'] = df_F.index
    df_F = df_F.reset_index(drop=True)
    
    
    
    with pnd.ExcelWriter(filepath) as writer:
        if len(df_G)!=0: df_G.to_excel(writer, sheet_name='Growth', index=False)
        if len(df_S)!=0: df_S.to_excel(writer, sheet_name='Synthesis', index=False)
        if len(df_O)!=0: df_O.to_excel(writer, sheet_name='Omission', index=False)
        if len(df_C)!=0: df_C.to_excel(writer, sheet_name='Substrates', index=False)
        if len(df_E)!=0: df_E.to_excel(writer, sheet_name='Essential', index=False)
        if len(df_F)!=0: df_F.to_excel(writer, sheet_name='Factors', index=False)


