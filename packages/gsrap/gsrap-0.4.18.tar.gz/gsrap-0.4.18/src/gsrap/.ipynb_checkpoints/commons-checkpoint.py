import io
import requests
import warnings
import logging

import pandas as pnd

import cobra
import gempipe

__OPTTHR__ = 0.001   # optimization threshold



def fba_no_warnings(model): 
    
    # Ignore eventual "UserWarning: Solver status is 'infeasible'."
    with warnings.catch_warnings():  # temporarily suppress warnings for this block
        warnings.simplefilter("ignore")  # ignore all warnings
        
        # disable warnings
        cobra_logger = logging.getLogger("cobra.util.solver")
        old_level = cobra_logger.level
        cobra_logger.setLevel(logging.ERROR)   

        # perform FBA: 
        res = model.optimize()
        obj_value = res.objective_value
        status = res.status

        # restore original behaviour: 
        cobra_logger.setLevel(old_level)   

        return res, obj_value, status
    
    
    
def verify_growth(model, boolean=True):
        
    global __OPTTHR__
    
    
    res, obj_value, status = fba_no_warnings(model)
    if boolean:
        if obj_value < __OPTTHR__ or status=='infeasible':
            return False
        else: return True
    else:
        if status =='infeasible':
            return 'infeasible'
        elif obj_value < __OPTTHR__:
            return 0
        else:
            return round(obj_value, 3)


        
def force_id_on_sbml(file_path, model_id):
    
    with open(file_path, 'r') as file:
        content = file.read()
    content = content.replace(
        f'<model metaid="meta_{model_id}" fbc:strict="true">', 
        f'<model metaid="meta_{model_id}" id="{model_id}" fbc:strict="true">'
    )
    with open(file_path, 'w') as file:
        file.write(content)
        

        
def get_expcon(logger):
    
    
    logger.info("Downloading the experimental constraints file...")
    sheet_id = "1qGbIIipHJgYQjk3M0xDWKvnTkeInPoTeH9unDQkZPwg"
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
    for i in ['media', 'PM1', 'PM2A', 'PM3B', 'PM4A', 'authors']: 
        if i not in sheet_names:
            logger.error(f"Sheet '{i}' is missing!")
            return 1
        
        
    # load the tables
    expcon = {}
    expcon['media'] = exceldb.parse('media')
    expcon['PM1'] = exceldb.parse('PM1')
    expcon['PM2A'] = exceldb.parse('PM2A')
    expcon['PM3B'] = exceldb.parse('PM3B')
    expcon['PM4A'] = exceldb.parse('PM4A')
    expcon['authors'] = exceldb.parse('authors')
    
    
    # assign substrates as index
    expcon['media'].index = expcon['media'].iloc[:, 1]
    # remove first 2 useless column (empty & substrates)
    expcon['media'] = expcon['media'].iloc[:, 2:]
    
    
    for sheet in ['PM1', 'PM2A', 'PM3B', 'PM4A']:
        # assign wells as index
        expcon[sheet].index = expcon[sheet].iloc[:, 2]
        # remove first 3 useless columns
        expcon[sheet] = expcon[sheet].iloc[:, 3:]
    

    return expcon



def apply_medium_given_column(logger, model, medium, column, is_reference=False):
        
        
    # retrieve metadata
    description = column.iloc[0]
    doi = column.iloc[1]
    author = column.iloc[2]
    units = column.iloc[3]

    
    # convert substrates to dict
    column = column.iloc[4:]
    column = column.to_dict()

    
    # add trace elements:
    column['fe2'] = 'NL'
    column['mobd'] = 'NL'
    column['cobalt2'] = 'NL'


    # reset exchanges
    gempipe.reset_growth_env(model)    
    modeled_rids = [r.id for r in model.reactions]


    for substrate, value in column.items():

        if type(value)==float:
            continue   # empty cell, exchange will remain close

            
        # check if exchange is modeled
        if is_reference == False: 
            if f'EX_{substrate}_e' not in modeled_rids:
                logger.error(f"No exchange reaction found for substrate '{substrate}' in medium '{medium}'.")
                return 1
        else:  # external reference models might follow different standards.
            # The exr might not be present. 
            if f'EX_{substrate}_e' not in modeled_rids:
                logger.info(f"Reference has no exchange reaction for '{substrate}' in medium '{medium}': this substrate will be ignored.")
                continue


        # case "not limiting"
        value = value.strip().rstrip()
        if value == 'NL':   # non-limiting case
            model.reactions.get_by_id(f'EX_{substrate}_e').lower_bound = -1000


        # case "single value"
        elif '+-' not in value and '±' not in value:  # single number case
            value = value.replace(' ', '')  # eg "- 0.03" --> "-0.03"
            try: value = float(value)
            except: 
                logger.error(f"Invalid value found in medium '{medium}': '{substrate}' {value}.")
                return 1
            model.reactions.get_by_id(f'EX_{substrate}_e').lower_bound = value


        # case "with experimental error"
        else:  # value +- error
            if '±' in value: 
                value, error = value.split('±', 1)
            else: value, error = value.split('+-', 1)
            value = value.rstrip()
            error = error.strip()
            value = value.replace(' ', '')  # eg "- 0.03" --> "-0.03"
            try: value = float(value)
            except: 
                logger.error(f"Invalid value found in medium '{medium}': '{substrate}' {value} +- {error}.")
                return 1
            try: error = float(error)
            except: 
                logger.error(f"Invalid value found in medium '{medium}': '{substrate}' {value} +- {error}.")
                return 1
            model.reactions.get_by_id(f'EX_{substrate}_e').lower_bound = value -error
            model.reactions.get_by_id(f'EX_{substrate}_e').upper_bound = value +error

    return 0
        
     
    
def log_metrics(logger, model, outmode='starting_uni'):
    
    
    G = len([g.id for g in model.genes])
    R = len([r.id for r in model.reactions if len(set([m.id.rsplit('_',1)[-1] for m in r.metabolites]))==1])
    T = len([r.id for r in model.reactions if len(set([m.id.rsplit('_',1)[-1] for m in r.metabolites]))!=1])
    M = len([m.id for m in model.metabolites])
    uM = len(set([m.id.rsplit('_',1)[0] for m in model.metabolites]))
    gr = len([gr.id for gr in model.groups])
    bP = len([m.id for m in model.reactions.get_by_id('Biomass').reactants])

    
    if   outmode == 'starting_uni':
        logger.info(f"Starting universe: [oG: {G}, R: {R}, T: {T}, uM: {uM}, bP: {bP}]")
    elif outmode == 'uni_features':
        biomass = round(model.slim_optimize(), 3)
        logger.info(f"Universe features: [oG: {G}, R: {R}, T: {T}, uM: {uM}, bP: {bP}, Biomass: {biomass}]")
    elif outmode == 'recon_model':
        logger.info(f"Resulting model: [G: {G}, R: {R}, T: {T}, uM: {uM}, bP: {bP}]")
    elif outmode == 'loaded_model':
        logger.info(f"Loaded model: [G: {G}, R: {R}, T: {T}, uM: {uM}, bP: {bP}]")

        

def get_biomass_dict():
    
    
    # Note: universal and conditional precursors have been defined in Xavier2017 .
    # Here presented in the same order of Xavier2017 .
    # Xavier2017: 10.1016/j.ymben.2016.12.002.
    biomass_dict = {
        ##### UNIVERSAL #####
        'ribo_nucleotides': [
            'atp_c', 'ctp_c', 'gtp_c', 'utp_c'
        ],
        'deoxyribo_nucleotides': [
            'datp_c', 'dctp_c', 'dgtp_c', 'dttp_c'
        ],
        'amino_acids': [
            'ala__L_c', 'arg__L_c', 'asn__L_c', 'asp__L_c', 'cys__L_c', 
            'gln__L_c', 'glu__L_c', 'gly_c',    'his__L_c', 'ile__L_c', 
            'leu__L_c', 'lys__L_c', 'met__L_c', 'ser__L_c', 'pro__L_c', 
            'thr__L_c', 'trp__L_c', 'tyr__L_c', 'val__L_c', 'phe__L_c'
        ],
        'cofactors_uni': [
            'nad_c',    # B3: Nicotinamide -adenine dinucleotide phosphate
            'nadp_c',   # B3: Nicotinamide -adenine dinucleotide phosphate
            'coa_c',    # B5: Coenzyme A  (dependant on 'pnto__R_c')
            'fad_c',    # B2: Flavin adenine dinucleotide
            'fmn_c',    # B2: Flavin mononucleotide
            'ribflv_c', # B2: ribovlavin. Non-active form acording to Xavier2017 but anyway included.
            #'f4200_c', # B2: included by Xavier2017 in 'universal' but the description seems conditional.
            'thf_c',    # B9: tetrahydrofolate 
            '10fthf_c', # B9: 10-Formyltetrahydrofolate
            '5mthf_c',  # B9: 5-Methyltetrahydrofolate
            'thmpp_c',  # B1: Thiamine diphosphate
            'pydx5p_c', # B6: pyridoxal 5-phosphate
            'amet_c',   # SAM: S-adenosyl-methionine
        ],
        ##### CONDITIONAL #####
        'cofactors_con': [
            #'f4200_c', # coenzyme f420 (electron transfer in methanogens, actinobacteria , and others)
            'ptrc_c',   # Putrescine
            'spmd_c',   # Sperimidine
            'pheme_c',  # protoheme
            'mql8_c',   # menaquinol / manaquinone (mqn8_c)
            'q8h2_c',   # ubiquinol / ubiquinone (q8_c)
            # Methionaquinone
            'btn_c',    # B7: biotin
            'ACP_c',    # Acyl-carrier protein
            'adocbl_c', # B12: Adenosylcobalamin
            # Lipoate
            'uacgam_c'  # uridine diphosphate N-Acetylglucosamine (UDP-GlcNAc)
        ],
        ##### ADDED ##### (conditionals not included or lumped in Xavier2017)
        'cofactors_add': [
            'hemeO_c',  # heme-O
            'sheme_c',  # siroheme
            'moco_c',   # molybdenum cofactor
            'phllqol_c',# phylloquinol / phylloquinone (phllqne_c)
            'gthrd_c',  # glutathione (reduced)
            'br_c',     # bacterioruberin
        ],
        'lipids': [
            'pe120_c', # phosphatidyl-ethanolamine (12:0;12:0)
            'pg120_c', # phosphatidyl-glycerol (12:0;12:0)
            'clpn120_c', # cardiolipin (12:0;12:0;12:0;12:0)
            # 1-lysyl phosphatidylglycerol (plantarum)
        ],
        'membrane_wall': [
            'peptidoSTA_c', # peptidoglycan (dependant on 'udcpdp_c')
            'WTAgg40r_20n_20a_P_c', # teichoic acids
            'WTArg40r_20g_20a_P_c', # teichoic acids
            'WTAg40g_20g_20a_P_c', # teichoic acids
            'LTAgg40g_20n_20a_c', # lipoteichoic acids
            'LTAga40g_20t_20a_c', # lipoteichoic acids            
            # capsular polysaccharides
            # kdo_lipid_A
        ],
        'energy_stock': [
            # glycogen
            # starch
            # PHA / PHB
        ]
    }
    return biomass_dict



def import_from_universe(model, universe, rid, bounds=None, gpr=None):

    
    # get the universal reaction
    ru = universe.reactions.get_by_id(rid)
    
    # create a new empty reaction
    r = cobra.Reaction(rid)
    model.add_reactions([r])
    r = model.reactions.get_by_id(rid)
    
    # copy the name
    r.name = ru.name
    
    # build string all universal metabolites are still there
    # (remove__disconnected is called later):
    r.build_reaction_from_string(ru.reaction)
    
    # set bounds
    if bounds != None: r.bounds = bounds
    else: r.bounds = ru.bounds
        
    # set GPR
    if gpr != None:
        r.gene_reaction_rule = gpr
    else:
        r.gene_reaction_rule = ''
    r.update_genes_from_gpr()