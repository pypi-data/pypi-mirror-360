import os
from pathlib import Path


import gempipe
import cobra


from ..commons import get_expcon
from ..commons import force_id_on_sbml
from ..commons import log_metrics

from .unipruner import check_inputs
from .unipruner import parse_eggnog
from .unipruner import subtract_kos
from .unipruner import translate_remaining_kos
from .unipruner import restore_gene_annotations
from .unipruner import adjust_biomass_equation

from .gapfiller import include_forced
from .gapfiller import gapfill_on_media
from .gapfiller import remove_forced
from .gapfiller import biolog_on_media
from .gapfiller import remove_disconnected

from .excelhub import write_excel_model



def main(args, logger):
    
    
    # adjust out folder path                      
    while args.outdir.endswith('/'):              
        args.outdir = args.outdir[:-1]
    os.makedirs(f'{args.outdir}/', exist_ok=True)
    
    
    # check compatibility of input parameters:
    if args.cnps == '-' and args.biolog != '-':
        logger.error("Missing starting C/N/P/S sources: --biolog must be used in conjunction with --cnps.")
        return 1
    
    
    # check input files:
    response = check_inputs(logger, args.universe, args.eggnog)
    if type(response)==int:
        return 1
    universe = response[0]
    eggnog = response[1]
        
    
    # check file structure ('expcon'= experimental constraints)
    expcon = get_expcon(logger)
    if type(expcon)==int: return 1

    
    
    ###### PRUNING
    # get important dictionaries: 'eggnog_ko_to_gids' and 'eggonog_gid_to_kos'
    eggnog_ko_to_gids, eggonog_gid_to_kos = parse_eggnog(eggnog)
    
    # create a copy of the universe
    model = universe.copy()
    model.id = Path(args.eggnog).stem        
    
    # prune reactions
    subtract_kos(logger, model, eggnog_ko_to_gids)
    
    # translate KOs to the actual genes
    translate_remaining_kos(logger, model, eggnog_ko_to_gids)
    restore_gene_annotations(logger, model, universe, eggonog_gid_to_kos)
    
    
    
    ###### GAPFILLING
    # force inclusion of reactions:  
    include_forced(logger, model, universe, args.force_inclusion)
    #
    # adjust biomass equation:
    # get the variable precursors dataframe ('variable_precs_df')
    varprec = adjust_biomass_equation(logger, model, universe, args.conditional)
    #
    # gap-fill based on media:
    df_B = gapfill_on_media(logger, model, universe, expcon, args.gap_fill, varprec, args.exclude_orphans)
    if type(df_B)==int: return 1
    #
    # force removal of reactions
    remove_forced(logger, model, universe, args.force_removal)
    #
    # perform Biolog(R) simulations based on media. Gap-filling is included. 
    df_P = biolog_on_media(logger, model, universe, expcon, args.gap_fill, args.biolog, args.exclude_orphans, args.cnps)
    if type(df_P)==int: return 1
    

    
    # remove disconnected metabolites
    remove_disconnected(logger, model)
    
    
    # reset growth environment befor saving the model
    gempipe.reset_growth_env(model)
                     
        
    # output the model:
    cobra.io.save_json_model(model, f'{args.outdir}/{model.id}.json')        # JSON
    cobra.io.write_sbml_model(model, f'{args.outdir}/{model.id}.xml')        # SBML   # groups are saved only to SBML
    force_id_on_sbml(f'{args.outdir}/{model.id}.xml', model.id)   # force introduction of the 'id=""' field
    write_excel_model(model, f'{args.outdir}/{model.id}.mkmodel.xlsx', df_B, df_P)  
    logger.info(f"'{args.outdir}/{model.id}.json' created!")
    logger.info(f"'{args.outdir}/{model.id}.xml' created!")
    logger.info(f"'{args.outdir}/{model.id}.mkmodel.xlsx' created!")
    log_metrics(logger, model, outmode='recon_model')
    
    
    
    return 0