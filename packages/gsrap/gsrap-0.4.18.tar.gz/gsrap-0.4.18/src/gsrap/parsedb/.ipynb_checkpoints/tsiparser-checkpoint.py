from importlib import resources
import pickle
import os
import requests
import io


import pandas as pnd
import gempipe
import cobra


from .repeating import check_gpr
from .repeating import check_author
from .repeating import check_rstring_arrow
from .repeating import add_reaction
from .repeating import get_deprecated_kos

from ..commons import get_biomass_dict



def get_db(logger):
    
    
    logger.info("Downloading the database...")
    sheet_id = "1dXJBIFjCghrdvQtxEOYlVNWAQU4mK-nqLWyDQeUZqek"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    response = requests.get(url)  # download the requested file
    if response.status_code == 200:
        excel_data = io.BytesIO(response.content)   # load into memory
        exceldb = pnd.ExcelFile(excel_data)
    else:
        logger.error(f"Error during download. Please contact the developer.")
        return 1
    
    
    # check table presence
    sheet_names = exceldb.sheet_names
    for i in ['T', 'R', 'M', 'authors']: 
        if i not in sheet_names:
            logger.error(f"Sheet '{i}' is missing!")
            return 1
        
        
    # load the tables
    db = {}
    db['T'] = exceldb.parse('T')
    db['R'] = exceldb.parse('R')
    db['M'] = exceldb.parse('M')
    db['authors'] = exceldb.parse('authors')
    
    
    # check table headers
    headers = {}
    headers['T'] = ['rid', 'rstring', 'kr', 'gpr_manual', 'name', 'author', 'notes']
    headers['R'] = ['rid', 'rstring', 'kr', 'gpr_manual', 'name', 'author', 'notes']
    headers['M'] = ['pure_mid', 'formula', 'charge', 'kc', 'name', 'inchikey', 'author', 'notes']
    headers['authors'] = ['username', 'first_name', 'last_name', 'role', 'mail']
    for i in db.keys(): 
        if set(db[i].columns) != set(headers[i]):
            logger.error(f"Sheet '{i}' is missing the columns {set(headers[i]) - set(db[i].columns)}.")
            return 1
        
    return db
    

    
def introduce_metabolites(logger, db, model, idcollection_dict, keggm_to_bigg, goodbefore, onlyauthor):
    goodbefore_reached = False

    
    logger.debug("Checking duplicated metabolite IDs...")
    if len(set(db['M']['pure_mid'].to_list())) != len(db['M']): 
        pure_mids = db['M']['pure_mid'].to_list()
        duplicates = list(set([item for item in pure_mids if pure_mids.count(item) > 1]))
        logger.error(f"Sheet 'M' has duplicated metabolites: {duplicates}.")
        return 1
   
        
    # parse M:
    logger.debug("Parsing metabolites...")
    db['M'] = db['M'].set_index('pure_mid', drop=True, verify_integrity=True)
    kc_ids_modeled = set()   # account for kc codes modeled
    for pure_mid, row in db['M'].iterrows():
        
        
        # skip empty lines!
        if type(pure_mid) != str: continue
        if pure_mid.strip() == '': continue
        if pure_mid == goodbefore:
            goodbefore_reached = True
        
        
        # parse author
        response = check_author(logger, pure_mid, row, db, 'M')
        if type(response) == int: return 1
        else: authors = response
        
        
        # manage goodbefore/onlyauthor
        if goodbefore != None and goodbefore_reached:
            if onlyauthor != None and onlyauthor not in authors:
                authors_string = '; '.join(authors)
                logger.info(f"Skipping metabolite '{pure_mid}' (authors '{authors_string}') as requested with --goodbefore[0] '{goodbefore}' and --onlyauthor '{onlyauthor}'.")
                continue
            if onlyauthor == None:
                logger.info(f"Skipping metabolite '{pure_mid}' as requested with --goodbefore[0] '{goodbefore}'.")
                continue
        
        
        # parse formula:
        if pnd.isna(row['formula']):
            logger.error(f"Metabolite '{pure_mid}' has missing formula: '{row['formula']}'.")
            return 1
  
        
        # parse charge: 
        if pnd.isna(row['charge']): 
            logger.error(f"Metabolite '{pure_mid}' has missing charge: '{row['charge']}'.")
            return 1
        
        
        # check if 'kc' codes are real:
        if pnd.isna(row['kc']): 
            logger.error(f"Metabolite '{pure_mid}' has missing KEGG annotation (kc): '{row['kc']}'.")
            return 1
        kc_ids = row['kc'].split(';')
        kc_ids = [i.strip() for i in kc_ids]
        for kc_id in kc_ids:
            if kc_id == 'CXXXXX':  # not in KEGG; could be knowledge gap (e.g. methyl group acceptor in R10404)
                logger.debug(f"Metabolite '{pure_mid}' is not in KEGG ('{kc_id}')!")
                continue  
            if kc_id not in idcollection_dict['kc']:
                logger.error(f"Metabolite '{pure_mid}' has invalid KEGG annotation (kc): '{kc_id}'.")
                return 1
            if kc_id in kc_ids_modeled:
                logger.error(f"KEGG annotation (kc) '{kc_id}' used in metabolite '{pure_mid}' is duplicated.")
                return 1
            if kc_id != 'CXXXXX':
                kc_ids_modeled.add(kc_id)
            
            
        # check the existance of the inchikey
        if pnd.isna(row['inchikey']): 
            logger.error(f"Metabolite '{pure_mid}' has missing inchikey: '{row['inchikey']}'.")
            return 1
        # check inchikey format:
        if len(row['inchikey']) != 27 or row['inchikey'][14] != '-' or row['inchikey'][25] != '-':
            logger.error(f"Metabolite '{pure_mid}' has badly formatted inchikey: '{row['inchikey']}'.")
            return 1
        
        
        # check if this 'kc' is already in BiGG (rely on MNX)
        eqbiggids = set()
        for kc_id in kc_ids:
            if kc_id != 'CXXXXX':
                if kc_id in keggm_to_bigg.keys():
                    for eqbiggid in keggm_to_bigg[kc_id]:
                        eqbiggids.add(eqbiggid)
        if pure_mid not in eqbiggids and eqbiggids != set():
            logger.debug(f"Metabolites '{'; '.join(kc_ids)}' already in BiGG as {eqbiggids} ({authors} gave '{pure_mid}').")        
        
        
        # add metabolite to model
        m = cobra.Metabolite(f'{pure_mid}_c')
        model.add_metabolites([m])
        m = model.metabolites.get_by_id(f'{pure_mid}_c')
        m.name = row['name'].strip()
        m.formula = row['formula']
        m.charge = row['charge']
        m.compartment='c'
        # add kc annotations to model
        m.annotation['kegg.compound'] = kc_ids
        
    
    if goodbefore != None and goodbefore_reached == False:
        logger.info(f"Metabolite '{goodbefore}' never reached. Are you sure about your --goodbefore?")
                    
                    
    return model
    
    
    
def introduce_reactions(logger, db, model, idcollection_dict, keggr_to_bigg, goodbefore, onlyauthor): 
    goodbefore_reached = False
                    
    
    logger.debug("Checking duplicated reaction IDs...")
    if len(set(db['R']['rid'].to_list())) != len(db['R']): 
        pure_mids = db['R']['rid'].to_list()
        duplicates = list(set([item for item in pure_mids if pure_mids.count(item) > 1]))
        logger.error(f"Sheet 'R' has duplicated reactions: {duplicates}.")
        return 1
    
        
    # parse R:
    logger.debug("Parsing reactions...")
    db['R'] = db['R'].set_index('rid', drop=True, verify_integrity=True)
    for rid, row in db['R'].iterrows():
        
        
        # skip empty lines!
        if type(rid) != str: continue
        if rid.strip() == '': continue
        if rid == goodbefore:
            goodbefore_reached = True
        
        
        # parse author
        response = check_author(logger, rid, row, db, 'R')
        if type(response) == int: return 1
        else: authors = response
                    
                    
        # manage goodbefore/onlyauthor
        if goodbefore != None and goodbefore_reached:
            if onlyauthor != None and onlyauthor not in authors:
                authors_string = '; '.join(authors)
                logger.info(f"Skipping reaction '{rid}' (authors '{authors_string}') as requested with --goodbefore[1] '{goodbefore}' and --onlyauthor '{onlyauthor}'.")
                continue
            if onlyauthor == None:
                logger.info(f"Skipping reaction '{rid}' as requested with --goodbefore[1] '{goodbefore}'.")
                continue
        
        
        # parse reaction string
        response = check_rstring_arrow(logger, rid, row, 'R')
        if response == 1: return 1
        

        # check if 'kr' codes are real:
        if pnd.isna(row['kr']): 
            logger.error(f"Reaction '{rid}' has missing KEGG annotation (kr): '{row['kr']}'.")
            return 1
        kr_ids = row['kr'].split(';')
        kr_ids = [i.strip() for i in kr_ids]
        for kr_id in kr_ids:
            if kr_id == 'RXXXXX':  # not in KEGG; could be knowledge gap 
                logger.debug(f"Reaction '{rid}' is not in KEGG ('{kr_id}')!")
                continue  
            if kr_id not in idcollection_dict['kr']:
                logger.error(f"Reaction '{rid}' has invalid KEGG annotation (kr): '{kr_id}'.")
                return 1
        
            
        # check GPR:
        response = check_gpr(logger, rid, row, kr_ids, idcollection_dict, 'R')
        if response == 1: return 1
    
    
        # check if this 'kr' is already in BiGG (rely on MNX)
        eqbiggids = set()
        for kr_id in kr_ids:
            if kr_id != 'RXXXXX':
                if kr_id in keggr_to_bigg.keys():
                    for eqbiggid in keggr_to_bigg[kr_id]:
                        eqbiggids.add(eqbiggid)
        if rid not in eqbiggids and eqbiggids != set():
            logger.debug(f"Reactions '{'; '.join(kr_ids)}' already in BiGG as {eqbiggids} ({authors} gave '{rid}').") 
        
        
        # add reaction to model
        response = add_reaction(logger, model, rid, row, kr_ids, 'R')
        if response == 1: return 1
               
    
    if goodbefore != None and goodbefore_reached == False:
        logger.info(f"Reaction '{goodbefore}' never reached. Are you sure about your --goodbefore?")
    
    
    return model
      
    
    
def introduce_transporters(logger, db, model, idcollection_dict, keggr_to_bigg, goodbefore, onlyauthor): 
    goodbefore_reached = False
                    
    
    
    def clone_to_external(model, mid_c, mid_e):
    
        m = cobra.Metabolite(f'{mid_e}')
        model.add_metabolites([m])
        
        m_c = model.metabolites.get_by_id(f'{mid_c}')
        m_e = model.metabolites.get_by_id(f'{mid_e}')
        m_e.compartment='e'
        
        m_e.name = m_c.name
        m_e.formula = m_c.formula
        m_e.charge = m_c.charge
        m_e.annotation = m_c.annotation
            
    
    def add_exchange_reaction(model, mid_e):
        
        r = cobra.Reaction(f'EX_{mid_e}')
        model.add_reactions([r])
        r = model.reactions.get_by_id(f'EX_{mid_e}')
        r.name = f"Exchange for {model.metabolites.get_by_id(mid_e).name}"
        r.build_reaction_from_string(f'{mid_e} --> ')
        if mid_e in [
            # basics:
            'glc__D_e', 'nh4_e', 'pi_e', 'so4_e', 'h2o_e', 'h_e', 'o2_e', 'co2_e',
            # metals: 
            'cu2_e', 'mobd_e', 'fe2_e', 'cobalt2_e',
        ]:
            r.bounds = (-1000, 1000)
        else:
            r.bounds = (0, 1000)
    
    
    
    # get all already inserted metabolites
    mids_parsed = [m.id for m in model.metabolites]
    rids_parsed = [r.id for r in model.reactions]
    
    
    # protons may not have an explicit transporter
    clone_to_external(model, 'h_c', 'h_e')
    mids_parsed.append('h_e')
    add_exchange_reaction(model, 'h_e')
    rids_parsed.append(f'EX_h_e')
    
    
    # parse T:
    logger.debug("Parsing transporters...")
    db['T'] = db['T'].set_index('rid', drop=True, verify_integrity=True)
    for rid, row in db['T'].iterrows():
        
        
        # skip empty lines!
        if type(rid) != str: continue
        if rid.strip() == '': continue
        if rid == goodbefore:
            goodbefore_reached = True
        
        
        # parse author
        response = check_author(logger, rid, row, db, 'T')
        if type(response) == int: return 1
        else: authors = response
                    
                    
        # manage goodbefore/onlyauthor
        if goodbefore != None and goodbefore_reached:
            if onlyauthor != None and onlyauthor not in authors:
                authors_string = '; '.join(authors)
                logger.info(f"Skipping transport '{rid}' (authors '{authors_string}') as requested with --goodbefore[2] '{goodbefore}' and --onlyauthor '{onlyauthor}'.")
                continue
            if onlyauthor == None:
                logger.info(f"Skipping transport '{rid}' as requested with --goodbefore[2] '{goodbefore}'.")
                continue
        
        
        # parse reaction string
        response = check_rstring_arrow(logger, rid, row, 'T')
        if response == 1: return 1
    
    
        # check if 'kr' codes are real:
        if pnd.isna(row['kr']): 
            logger.error(f"Reaction '{rid}' has missing KEGG annotation (kr): '{row['kr']}'.")
            return 1
        if row['kr'] != '-':
            kr_ids = row['kr'].split(';')
            kr_ids = [i.strip() for i in kr_ids]
            for kr_id in kr_ids:
                if kr_id not in idcollection_dict['kr']:
                    logger.error(f"Reaction '{rid}' has invalid KEGG annotation (kr): '{kr_id}'.")
                    return 1
        else: kr_ids = []

            
        # check GPR:
        response = check_gpr(logger, rid, row, kr_ids, idcollection_dict, 'T')
        if response == 1: return 1
        
        
        # get involved metabolites:
        involved_mids = row['rstring'].split(' ')
        involved_mids = [i for i in involved_mids if i not in ['-->', '<=>']]
        
        
        # the external metabolite must be already modeled as cytosolic
        for mid in involved_mids: 
            if mid.endswith('_e'):
                mid_e = mid
                mid_c = mid.rsplit('_', 1)[0] + '_c'
                if mid_c not in mids_parsed:
                    logger.error(f"{rid}: the metabolite '{mid_c}', counterpart of '{mid_e}', was not previously modeled.")
                    return 1
                
                # add external metabolite to model
                if mid_e not in mids_parsed:
                    clone_to_external(model, mid_c, mid_e)
                    mids_parsed.append(mid_e)
                    
                # add exchange reaction to model
                if f'EX_{mid_e}' not in rids_parsed:
                    add_exchange_reaction(model, mid_e)
                    rids_parsed.append(f'EX_{mid_e}')
                    
                    
        # check if this 'kr' is already in BiGG (rely on MNX)
        eqbiggids = set()
        for kr_id in kr_ids:
            if kr_id != '-':  # (was 'RXXXXX' for metabolic reactions)
                if kr_id in keggr_to_bigg.keys():
                    for eqbiggid in keggr_to_bigg[kr_id]:
                        eqbiggids.add(eqbiggid)
        if rid not in eqbiggids and eqbiggids != set():
            logger.debug(f"Reactions '{'; '.join(kr_ids)}' already in BiGG as {eqbiggids} ({authors} gave '{rid}').") 
                    
                    
        # add reaction to model
        response = add_reaction(logger, model, rid, row, kr_ids, 'T')
        if response == 1: return 1
        
        
    if goodbefore != None and goodbefore_reached == False:
        logger.info(f"Transport '{goodbefore}' never reached. Are you sure about your --goodbefore?")
        
    
    return model



def introduce_sinks_demands(logger, model): 
    
    sinks = ['apoACP', 'apocarb', 'thioca', 'THI5p_b', 'cyE']
    demands = ['scp', 'amob', 'dialurate', 'THI5p_a' ]
    
    
    for puremid in sinks: 
        r = cobra.Reaction(f'sn_{puremid}_c')
        model.add_reactions([r])
        r = model.reactions.get_by_id(f'sn_{puremid}_c')
        r.name = f"Sink for {model.metabolites.get_by_id(f'{puremid}_c').name}"
        r.build_reaction_from_string(f'{puremid}_c <=> ')
        r.bounds = (-1000, 1000)
    
    
    for puremid in demands: 
        r = cobra.Reaction(f'dm_{puremid}_c')
        model.add_reactions([r])
        r = model.reactions.get_by_id(f'dm_{puremid}_c')
        r.name = f"Demand for {model.metabolites.get_by_id(f'{puremid}_c').name}"
        r.build_reaction_from_string(f'{puremid}_c --> ')
        r.bounds = (0, 1000)
    
    
    return model



def introduce_biomass(logger, db, model): 
    
    
    biomass_dict = get_biomass_dict()
    
    
    rstring =           f'0.001 {" + 0.001 ".join(biomass_dict["ribo_nucleotides"])}'
    rstring = rstring + f' + 0.001 {" + 0.001 ".join(biomass_dict["deoxyribo_nucleotides"])}'
    rstring = rstring + f' + 0.001 {" + 0.001 ".join(biomass_dict["amino_acids"])}'
    rstring = rstring + f' + 0.001 {" + 0.001 ".join(biomass_dict["cofactors_uni"])}'
    rstring = rstring + f' + 0.001 {" + 0.001 ".join(biomass_dict["cofactors_con"])}'
    rstring = rstring + f' + 0.001 {" + 0.001 ".join(biomass_dict["cofactors_add"])}'
    rstring = rstring + f' + 0.001 {" + 0.001 ".join(biomass_dict["lipids"])}'
    rstring = rstring + f' + 0.001 {" + 0.001 ".join(biomass_dict["membrane_wall"])}'
    rstring = rstring + f' + 0.001 atp_c + 0.001 h2o_c --> 0.001 adp_c + 0.001 h_c + 0.001 pi_c'
    
    
    r = cobra.Reaction('Biomass')
    model.add_reactions([r])
    r = model.reactions.get_by_id('Biomass')
    r.name = 'Biomass assembly reaction'
    r.build_reaction_from_string(rstring)
    
    
    # set as objective:
    model.objective = 'Biomass'
    
    
    return model



def translate_annotate_genes(logger, model, idcollection_dict):
    

       
    ko_to_name = idcollection_dict['ko_to_name']
    ko_to_symbols = idcollection_dict['ko_to_symbols']
    ko_to_ecs = idcollection_dict['ko_to_ecs']
    ko_to_cogs = idcollection_dict['ko_to_cogs']
    ko_to_gos = idcollection_dict['ko_to_gos']
    
    
    # translation dicts: assign to each KO a symbol that is unique in the universe model.
    ko_to_sym = {}
    sym_to_ko = {}
    cnt = 0
    for g in model.genes:
        if g.id in ['orphan', 'spontaneous']: 
            continue
        ko = g.id
        cnt += 1
        
        if ko in get_deprecated_kos():
            # if the ko is deprecated, it was not included in 'ko_to_symbols'
            ko_to_sym[ko] = ko
            sym_to_ko[ko] = ko
            continue
            
        for symbol in ko_to_symbols[ko]:  # iterate the available symbols for this KO
            if symbol not in sym_to_ko.keys():   # take the first available (not yet used)
                ko_to_sym[ko] = symbol
                sym_to_ko[symbol] = ko
                break
        
        if cnt != len(ko_to_sym):  # no symbol was assigned (symbol was already taken by another KO)
            cnt_dups = 2
            symbol = list(ko_to_symbols[ko])[0] + f'_{cnt_dups}'   # generate a new symbol
            while cnt != len(ko_to_sym):   # until a symbol is assigned
                if symbol not in sym_to_ko.keys():   # if the new symbol fits
                    ko_to_sym[ko] = symbol
                    sym_to_ko[symbol] = ko
                cnt_dups += 1
                symbol = list(ko_to_symbols[ko])[0] + f'_{cnt_dups}'   # retry with the next one
                

                
    
    # insert annotations
    for g in model.genes:
        if g.id in ['orphan', 'spontaneous']: 
            continue
        ko = g.id
        g.annotation['ko'] = ko
        
        if ko not in get_deprecated_kos():
            # deprecated kos are missing from these dicts
            g.name = ko_to_name[ko]
            g.annotation['symbols'] = list(ko_to_symbols[ko])
            g.annotation['ec'] = list(ko_to_ecs[ko])
            g.annotation['cog'] = list(ko_to_cogs[ko])
            g.annotation['go'] = list(ko_to_gos[ko])
        
    
        
    # finally apply translations of IDs
    translation_dict = ko_to_sym
    translation_dict['orphan'] = 'orphan'
    translation_dict['spontaneous'] = 'spontaneous'
    cobra.manipulation.rename_genes(model, translation_dict)
    
    
    return model
    


def set_up_groups(logger, model, idcollection_dict):
    

       
    kr_to_maps = idcollection_dict['kr_to_maps']
    map_to_name = idcollection_dict['map_to_name']
    kr_to_mds = idcollection_dict['kr_to_mds']
    md_to_name = idcollection_dict['md_to_name']
    
    
    # define groups of available contents
    groups = {}   # mixing maps and mds
    for r in model.reactions:
        
        if 'kegg.reaction' not in r.annotation.keys():
            continue   # Biomass, exchanges, demands, sinks, transporters
        kr_ids = r.annotation['kegg.reaction']
            
        for kr_id in kr_ids:
            if kr_id == 'RXXXXX':
                continue
            
            # insert maps
            for map_id in kr_to_maps[kr_id]:
                if map_id not in groups.keys():
                    groups[map_id] = set()
                groups[map_id].add(r)
                
            # insert mds
            for md_id in kr_to_mds[kr_id]:
                if md_id not in groups.keys():
                    groups[md_id] = set()
                groups[md_id].add(r)
                
    # finally insert groups
    for group_id in groups.keys():
                
        # get group name
        if group_id.startswith('map'):
            name = map_to_name[group_id]
        if group_id.startswith('M'):
            name = md_to_name[group_id]
                    
        actual_group = cobra.core.Group(
            group_id, 
            name = name,
            members = list(groups[group_id]),
            kind = 'partonomy',
        )
        model.add_groups([actual_group])
        
        
        
    # insert custom groups:
    custom_groups = {
        'gr_ptdSTA': ['UAMAGLL', 'UMNS', 'UPPNAPT', 'UAGPT2', 'UAGPGAL', 'UAGPN6GT', 'UAAGGTLGAGT', 'UAAGGTLG3AGT', 'PPTGP'],
        'gr_HemeO': ['HEMEOS'],
        'gr_WTA1': ['ACGAMT', 'UNDBD', 'WTAGPT', 'WTAGPP', 'WTAUGLCT2', 'WTAALAT3', 'WTAPL3'],
        'gr_WTA2': ['ACGAMT', 'UNDBD', 'WTAGPT', 'WTARBT2', 'WTARPP2', 'WTAUGLCT', 'WTAALAT2', 'WTAPL2'],
        'gr_WTA3': ['ACGAMT', 'UNDBD', 'WTAGPT', 'WTAGPT2', 'WTARPP', 'WTAGLCNACT', 'WTAALAT', 'WTAPL'],
        'gr_LTA1': ['UGDIAT', 'UGLDIAT', 'GGGDAGF2', 'LIPOPO2', 'LTANACT', 'LTAALAT2'],
        'gr_LTA2': ['UGDIAT', 'UGADIAT', 'GGGDAGF', 'LIPOPO', 'LTAGAT', 'LTAALAT'],
        'gr_br': ['LYEH1', 'HIPCD1', 'LYEH2', 'HIPCD2', 'BHBRH1', 'BHBRH2'],
    }
    for group_id in custom_groups.keys():
        actual_group = cobra.core.Group(
            group_id, 
            name = group_id,
            members = [model.reactions.get_by_id(rid) for rid in custom_groups[group_id]],
            kind = 'partonomy',
        )
        model.add_groups([actual_group])
        
        
    return model


    
def check_biomass_precursors(logger, universe, precursors):
    
    
    if not precursors:
        return 0
        
        
    # check production of biomass precursors: 
    logger.info("Checking biosynthesis of every biomass component...")
    print()
    mids = gempipe.check_reactants(universe, 'Biomass')
    if mids == []: 
        print("No blocked biomass component detected!")
    print()


    
def check_metabolites_biosynthesis(logger, universe, outdir, biosynth):
    
    
    if not biosynth:
        return 0
    
    
    # check biosynthesis of every modeled metabolite:
    logger.info("Checking biosynthesis of every metabolite...")
    df_rows = []
    for m in universe.metabolites:
        if m.id.endswith('_c'):
            dem = '/'
            binary, obj_value, status = gempipe.can_synth(universe, m.id)
            
            
            # check if it's dead-end metabolite (dem)
            if binary == False:
                dem = False
                is_consumed = False
                is_produced = False
                for r in m.reactions:
                    if m.id in [m2.id for m2 in r.reactants]:
                        is_consumed = True
                    if m.id in [m2.id for m2 in r.products]:
                        is_produced = True
                if   is_consumed and not is_produced:
                    dem = 'no_production'
                elif is_produced and not is_consumed:
                    dem = 'no_consumption' 
                    
                    
            df_rows.append({'mid': m.id, 'binary': binary, 'obj_value': obj_value, 'status': status, 'dead-end': dem})
    df_rows = pnd.DataFrame.from_records(df_rows)
    df_rows = df_rows.set_index('mid', drop=True, verify_integrity=True)

    
    # save table as excel: 
    df_rows.to_excel(f'{outdir}/biosynth.xlsx')
    logger.info(f"'{outdir}/biosynth.xlsx' created!")
             
    
    return 0

  
    
def parse_eggnog(model, eggnog, idcollection_dict):
    
    
    eggnog = pnd.read_csv(eggnog, sep='\t', comment='#', header=None)
    eggnog.columns = 'query	seed_ortholog	evalue	score	eggNOG_OGs	max_annot_lvl	COG_category	Description	Preferred_name	GOs	EC	KEGG_ko	KEGG_Pathway	KEGG_Module	KEGG_Reaction	KEGG_rclass	BRITE	KEGG_TC	CAZy	BiGG_Reaction	PFAMs'.split('\t')
    eggnog = eggnog.set_index('query', drop=True, verify_integrity=True)
    
    
    # PART 1. get KO codes available
    kos_org = set()
    for gid, kos in eggnog['KEGG_ko'].items():
        if kos == '-': 
            continue
        kos = kos.split(',')
        kos = [i.replace('ko:', '') for i in kos]
        for ko in kos: 
            kos_org.add(ko)
            
            
    # PART 2. get reactions in the organism (even the GPR is not complete)
    kr_to_kos = idcollection_dict['kr_to_kos']
    krs_org = set()
    for kr, kos in kr_to_kos.items(): 
        if any([ko in kos_org for ko in kos]):
            krs_org.add(kr)
    
    
    return krs_org
    
    
    
def check_completeness(logger, model, progress, module, focus, eggnog, zeroes, idcollection_dict, summary_dict): 
    # check KEGG annotations in the universe model to get '%' of completeness per pathway/module.
    
            
            
    # get the reference set of kr codes (all kegg or organism specific): 
    if eggnog != '-':
        kr_uni = parse_eggnog(model, eggnog, idcollection_dict)
        kr_uni_label = "'eggnog annotation'"
    else: 
        kr_uni = idcollection_dict['kr']
        kr_uni_label = "'whole KEGG'"
    
    
    # get all the 'kr' annotations in the model
    kr_ids_modeled = set()
    for r in model.reactions: 
        if 'kegg.reaction' in r.annotation.keys():
            for kr_id in r.annotation['kegg.reaction']:
                kr_ids_modeled.add(kr_id)
    logger.info(f"Universe coverage for {kr_uni_label}: {round(len(kr_ids_modeled.intersection(kr_uni))/len(kr_uni)*100, 0)}%!")
    
    
    # get all the map / md codes:
    map_ids = set()
    md_ids = set()
    for i in summary_dict:
        map_ids.add(i['map_id'])
        for j in i['mds']:
            md_ids.add(j['md_id'])
            
            
    # check if 'focus' exist
    if focus != '-' and focus not in map_ids and focus not in md_ids:
        logger.error(f"The ID provided with --focus does not exist: {focus}.")
        return 1
    if focus.startswith('map'):
        logger.debug(f"With --focus {focus}, --module will switch to False.")
        module = False
    if focus != '-':
        missing_logger = ()
    
    
    # define some counters:
    maps_finished = set()
    maps_noreac = set()
    maps_missing = set()
    maps_partial = set()

    
    list_coverage  = []
    
    
    # iterate over each map:
    for i in summary_dict:
        
        
        # get ID and name: 
        map_id = i['map_id']
        map_name_short = f"{i['map_name'][:20]}"
        if len(i['map_name']) > 20: 
            map_name_short = map_name_short + '...'
        else:  # add spaces as needed: 
            map_name_short = map_name_short + ''.join([' ' for i in range(23-len(map_name_short))])
            
            
        # check if this map was (at least partially) covered:
        map_krs = set([kr for kr in i['kr_ids'] if kr in kr_uni])
        missing = map_krs - kr_ids_modeled
        present = kr_ids_modeled.intersection(map_krs)
        if focus == map_id: 
            missing_logger = (map_id, missing)

        
        if missing == set() and map_krs != set():
            maps_finished.add(map_id)
            
        elif map_krs == set():
            maps_noreac.add(map_id)
            
        elif missing == map_krs:
            maps_missing.add(map_id)
            
            if zeroes:
                list_coverage.append({
                    'map_id': map_id,
                    'map_name_short': map_name_short, 
                    'perc_completeness': 0,
                    'perc_completeness_str': ' 0',
                    'present': present,
                    'missing': missing,
                    'md_ids': [j['md_id'] for j in i['mds']],
                })
            
        elif len(missing) < len(map_krs):
            maps_partial.add(map_id)
            
            # get '%' of completeness:
            perc_completeness = len(present)/len(map_krs)*100
            perc_completeness_str = str(round(perc_completeness))   # version to be printed
            if len(perc_completeness_str)==1: 
                perc_completeness_str = ' ' + perc_completeness_str
                
            list_coverage.append({
                'map_id': map_id,
                'map_name_short': map_name_short, 
                'perc_completeness': perc_completeness,
                'perc_completeness_str': perc_completeness_str,
                'present': present,
                'missing': missing,
                'md_ids': [j['md_id'] for j in i['mds']],
            })
                
            
    # order list by '%' of completness and print:
    list_coverage = sorted(list_coverage, key=lambda x: x['perc_completeness'], reverse=True)
    for i in list_coverage:
        if progress:
            if focus=='-' or focus in i['md_ids'] or focus==i['map_id']:
                logger.info(f"{i['map_id']}: {i['map_name_short']} {i['perc_completeness_str']}% completed, {len(i['present'])} added, {len(i['missing'])} missing.")
        
        
        # get the correspondent pathway element of the 'summary_dict'
        right_item = None
        for k in summary_dict:
            if k['map_id'] == i['map_id']:
                right_item = k
                
                
        # define some counters:
        mds_completed = set()
        mds_noreac = set()
        mds_missing = set()
        mds_partial = set()


        list_coverage_md  = []
        spacer = '    '


        # iterate over each module:
        for z in right_item['mds']:


            # get ID and name: 
            md_id = z['md_id']
            md_name_short = f"{z['md_name'][:20]}"
            if len(z['md_name']) > 20: 
                md_name_short = md_name_short + '...'
            else:  # add spaces as needed: 
                md_name_short = md_name_short + ''.join([' ' for i in range(23-len(md_name_short))])


            # check if this module was (at least partially) covered:
            md_krs = set([kr for kr in z['kr_ids_md'] if kr in kr_uni])
            missing = md_krs - kr_ids_modeled
            present = kr_ids_modeled.intersection(md_krs)
            if focus == md_id: 
                missing_logger = (md_id, missing)
            
            
            if missing == set() and md_krs != set():
                mds_completed.add(md_id)

            elif md_krs == set():
                mds_noreac.add(md_id)

            elif missing == md_krs:
                mds_missing.add(md_id)
                
                if zeroes:
                    list_coverage_md.append({
                        'md_id': md_id,
                        'md_name_short': md_name_short, 
                        'perc_completeness': 0,
                        'perc_completeness_str': ' 0',
                        'present': present,
                        'missing': missing,
                    })
                
            elif len(missing) < len(md_krs):
                mds_partial.add(md_id)

                # get '%' of completeness:
                perc_completeness = len(present)/len(md_krs)*100
                perc_completeness_str = str(round(perc_completeness))   # version to be printed
                if len(perc_completeness_str)==1: 
                    perc_completeness_str = ' ' + perc_completeness_str

                list_coverage_md.append({
                    'md_id': md_id,
                    'md_name_short': md_name_short, 
                    'perc_completeness': perc_completeness,
                    'perc_completeness_str': perc_completeness_str,
                    'present': present,
                    'missing': missing,
                })
               
            
        # order list by '%' of completness and print:
        list_coverage_md = sorted(list_coverage_md, key=lambda x: x['perc_completeness'], reverse=True)
        for z in list_coverage_md:
            if module:
                if focus=='-' or focus==z['md_id']:
                    logger.info(f"{spacer}{z['md_id']}: {z['md_name_short']} {z['perc_completeness_str']}% completed, {len(z['present'])} added, {len(z['missing'])} missing.")
        
        
        # print summary:
        if module and focus=='-':
            logger.info(f"{spacer}Modules of {right_item['map_id']}: completed {len(mds_completed)} - partial {len(mds_partial)} - missing {len(mds_missing)} - noreac {len(mds_noreac)}")
    if focus != '-':
        logger.info(f"Missing reactions focusing on {missing_logger[0]}: {' '.join(list(missing_logger[1]))}.")
    logger.info(f"Maps: finished {len(maps_finished)} - partial {len(maps_partial)} - missing {len(maps_missing)} - noreac {len(maps_noreac)}")
            
        
    return 0     



def show_contributions(logger, db):
    
    # create a counter for each author
    cnt = {author: 0 for author in db['authors']['username']}
    cnt_tot = 0
    for rid, row in db['R'].iterrows():
        for author in row['author'].split(';'):
            author = author.rstrip().strip()
            cnt[author] += 1
            cnt_tot += 1
    for rid, row in db['T'].iterrows():
        for author in row['author'].split(';'):
            author = author.rstrip().strip()
            cnt[author] += 1
            cnt_tot += 1
        
    # compute percentages:
    pct = {author: cnt[author]/cnt_tot*100 for author in cnt.keys()}
    # sort in descending order: 
    pct = dict(sorted(pct.items(), key=lambda item: item[1], reverse=True))
    # convert to string:
    pct = {author: f'{round(pct[author],2)}%' for author in pct.keys()}
    logger.debug(f"Contributions: {pct}.")
        

    
