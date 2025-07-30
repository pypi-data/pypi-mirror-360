import os
import pickle


import cobra


from ..commons import log_metrics

from .tsiparser import get_db
from .tsiparser import introduce_metabolites
from .tsiparser import introduce_reactions
from .tsiparser import introduce_transporters
from .tsiparser import introduce_sinks_demands
from .tsiparser import introduce_biomass
from .tsiparser import translate_annotate_genes
from .tsiparser import set_up_groups
from .tsiparser import check_biomass_precursors
from .tsiparser import check_metabolites_biosynthesis
from .tsiparser import check_completeness
from .tsiparser import show_contributions



def main(args, logger):
    
    
    # adjust out folder path                      
    while args.outdir.endswith('/'):              
        args.outdir = args.outdir[:-1]
    os.makedirs(f'{args.outdir}/', exist_ok=True)
    
    
    # check compatibility of input parameters
    if args.progress==False and args.module==True: 
        logger.error(f"You cannot ask --module without --progress (see --help).")
        return 1
    if args.progress==False and args.focus!='-':
        logger.error(f"You cannot ask --focus without --progress (see --help).")
        return 1
    if args.progress==False and args.zeroes==True:
        logger.error(f"You cannot ask --zeroes without --progress (see --help).")
        return 1
    
    
    # check 'goodbefore' and 'onlyauthor' params
    if args.goodbefore == '-' and args.onlyauthor != '-':
        logger.error(f"--onlyauthor must be used in conjunction with --goodbefore.")
        return 1
    if   args.goodbefore == '-': args.goodbefore = [None, None, None]
    elif len(args.goodbefore.split('-')) != 3: 
        logger.error(f"Invalid syntax detected for --goodbefore.")
        return 1
    else:
        args.goodbefore = args.goodbefore.split('-')
        if args.goodbefore[0] == 'None': args.goodbefore[0] = None
        if args.goodbefore[1] == 'None': args.goodbefore[1] = None
        if args.goodbefore[2] == 'None': args.goodbefore[2] = None
    if args.onlyauthor == '-': args.onlyauthor = None
    
    
    # check and extract the required 'gsrap.maps' file
    if os.path.exists(f'{args.inmaps}') == False:
        logger.error(f"File 'gsrap.maps' not found at {args.inmaps}.")
        return 1
    try: 
        with open(f'{args.inmaps}', 'rb') as f:
            inmaps = pickle.load(f)  
    except: 
        logger.error(f"Provided file {args.inmaps} has an incorrect format.")
        return 1
    idcollection_dict = inmaps['idcollection_dict']
    summary_dict = inmaps['summary_dict']
    keggc_to_bigg = inmaps['keggc_to_bigg']
    keggr_to_bigg = inmaps['keggr_to_bigg']
    
    
    # download database and check its structure
    db = get_db(logger)
    if type(db)==int: return 1
                                    
        
    # create the model
    model = cobra.Model('newuni')
        
    
    # introduce M / R / T
    model = introduce_metabolites(logger, db, model, idcollection_dict, keggc_to_bigg, args.goodbefore[0], args.onlyauthor)
    if type(model)==int: return 1
    model = introduce_reactions(logger, db, model, idcollection_dict, keggr_to_bigg, args.goodbefore[1], args.onlyauthor)
    if type(model)==int: return 1
    model = introduce_transporters(logger, db, model, idcollection_dict, keggr_to_bigg, args.goodbefore[2], args.onlyauthor)
    if type(model)==int: return 1


    # introduce sinks / demands (exchanges where included during T)
    model = introduce_sinks_demands(logger, model)
    if type(model)==int: return 1


    # introducce biomass
    model = introduce_biomass(logger, db, model)
    if type(model)==int: return 1


    # translate Gs to symbols and annotate them (EC, COG, GO, ...)
    model = translate_annotate_genes(logger, model, idcollection_dict)
    if type(model)==int: return 1


    # introduce collectionas (groups of Rs as maps/modules)
    model = set_up_groups(logger, model, idcollection_dict)
    if type(model)==int: return 1
    
    
    # output the universe
    cobra.io.save_json_model(model, f'{args.outdir}/newuni.json')
    cobra.io.write_sbml_model(model, f'{args.outdir}/newuni.xml')   # groups are saved only to SBML 
    logger.info(f"'{args.outdir}/newuni.json' created!")
    logger.info(f"'{args.outdir}/newuni.xml' created!")
    log_metrics(logger, model, outmode='uni_features')

    
    response = check_completeness(logger, model, args.progress, args.module, args.focus, args.eggnog, args.zeroes, idcollection_dict, summary_dict)
    if response==1: return 1


    # show simple statistics of contributions
    show_contributions(logger, db)


    response = check_biomass_precursors(logger, model, args.precursors)
    if response==1: return 1

    
    response = check_metabolites_biosynthesis(logger, model, args.outdir, args.biosynth)
    if response==1: return 1

      
    return 0