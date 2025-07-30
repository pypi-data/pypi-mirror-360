import os
import warnings
import logging


import pandas as pnd
import cobra


import gempipe

from ..commons import get_expcon
from ..commons import log_metrics

from .simarena import grow_on_media
from .simarena import synthesize_on_media
from .simarena import omission_on_media
from .simarena import cnps_on_media
from .simarena import essential_genes_on_media
from .simarena import growth_factors_on_media
from .simarena import write_excel_model



def main(args, logger):

    
    # adjust out folder path                      
    while args.outdir.endswith('/'):              
        args.outdir = args.outdir[:-1]
    os.makedirs(f'{args.outdir}/', exist_ok=True)
    
    
    # check file structure ('expcon'= experimental constraints)
    expcon = get_expcon(logger)
    if type(expcon)==int: return 1


    # load model
    logger.info("Reading input model...")
    model = None
    if args.inmodel.endswith('.xml'):
        # avoids warnings like "'Mendoza.WCFS1.emapper' is not a valid SBML 'SId'.":
        # As ~90 loggers are active, not knowing the actual one, temporarly silence every logger: 
        loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        previous_levels = {logger: logger.level for logger in loggers}
        for logger in loggers:
            logger.setLevel(logging.CRITICAL)  # setting to "logging.CRITICAL" is not sufficient
        model = cobra.io.read_sbml_model(args.inmodel)  # read SBML with invalid 'SId'
        for logger, level in previous_levels.items():
            logger.setLevel(level)
    elif args.inmodel.endswith('.json'):
        model = cobra.io.load_json_model(args.inmodel)
    log_metrics(logger, model, outmode='loaded_model')
    
    
    # reset growth environment befor saving the model
    gempipe.reset_growth_env(model)
        
        
    # check presence of input media
    if args.fba == '-':
        logger.error("No media provided! Cannot do growth simulations without growth media.")
        return 1
        
        
    # growth simulations based on media
    df_G = grow_on_media(logger, model, expcon, args.fba, args.fva)
    if type(df_G)==int: return 1
    
    # test synthesis based on media
    df_S = synthesize_on_media(logger, model, expcon, args.fba, args.synth)
    if type(df_S)==int: return 1
    
    # perform single omission experiments based on media
    df_O = omission_on_media(logger, model, expcon, args.fba, args.omission)
    if type(df_O)==int: return 1
    
    # perform alternative substrate anaysis based on media
    df_C = cnps_on_media(logger, model, expcon, args.fba, args.cnps)
    if type(df_C)==int: return 1
    
    # predict essential genes
    df_E = essential_genes_on_media(logger, model, expcon, args.fba, args.essential)
    if type(df_E)==int: return 1
    
    # predict growth factors
    df_F = growth_factors_on_media(logger, model, expcon, args.fba, args.factors)
    if type(df_F)==int: return 1
        
    
    # save simulations:
    write_excel_model(model, f'{args.outdir}/{model.id}.runsims.xlsx',  df_G, df_S, df_O, df_C, df_E, df_F)  
    logger.info(f"'{args.outdir}/{model.id}.runsims.xlsx' created!")

    
    return 0