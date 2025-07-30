import os
import io
import requests
import logging
import warnings
from pathlib import Path


import pandas as pnd
import cobra


import gempipe


from ..commons import log_metrics

__OPTTHR__ = 0.001   # optimization threshold

    
    
    
def check_inputs(logger, universe, eggnog):
    
    
    # check if files exist
    if os.path.isfile(universe) == False: 
        logger.error(f"Provided --universe doesn't exist: {universe}.")
        return 1
    if os.path.isfile(eggnog) == False: 
        logger.error(f"Provided --eggnog doesn't exist: {eggnog}.")
        return 1
    
    
    # check the universe model format
    if universe.endswith('.xml'):
        universe = cobra.io.read_sbml_model(universe)
    else: 
        logger.error(f"Provided --universe must be in cobrapy-compatible SBML format (.xml extension).")
        return 1
    
    
    # log main universe metrics:
    log_metrics(logger, universe, outmode='starting_uni')
        
        
    # load eggnog annotations
    eggnog = pnd.read_csv(eggnog, sep='\t', comment='#', header=None)
    eggnog.columns = 'query	seed_ortholog	evalue	score	eggNOG_OGs	max_annot_lvl	COG_category	Description	Preferred_name	GOs	EC	KEGG_ko	KEGG_Pathway	KEGG_Module	KEGG_Reaction	KEGG_rclass	BRITE	KEGG_TC	CAZy	BiGG_Reaction	PFAMs'.split('\t')
    eggnog = eggnog.set_index('query', drop=True, verify_integrity=True)
    
    return [universe, eggnog]



def parse_eggnog(eggnog):
    
    
    # PART 1. get KO codes available
    gid_to_kos = {}
    ko_to_gids = {}
    for gid, kos in eggnog['KEGG_ko'].items():
        if kos == '-': 
            continue
            
        if gid not in gid_to_kos.keys(): 
            gid_to_kos[gid] = set()
            
        kos = kos.split(',')
        kos = [i.replace('ko:', '') for i in kos]
        for ko in kos: 
            if ko not in ko_to_gids.keys(): 
                ko_to_gids[ko] = set()
                
            # populate dictionaries
            ko_to_gids[ko].add(gid)
            gid_to_kos[gid].add(ko)

    
    return ko_to_gids, gid_to_kos



def get_modeled_kos(model):
    
    
    # get modeled KO ids:
    modeled_gid_to_ko = {}
    modeled_ko_to_gid = {}
    
    for g in model.genes:
        if g.id in ['orphan', 'spontaneous']: 
            continue
        corresponding_ko = g.annotation['ko']
        
        modeled_gid_to_ko[g.id] = corresponding_ko
        modeled_ko_to_gid[corresponding_ko] = g.id
        
    modeled_kos = list(modeled_gid_to_ko.values())
        
    return modeled_kos, modeled_gid_to_ko, modeled_ko_to_gid



def subtract_kos(logger, model, eggonog_ko_to_gids):
    
    
    modeled_kos, _, modeled_ko_to_gid = get_modeled_kos(model)
        
        
    to_remove = []  # genes to delete
    for ko in modeled_kos: 
        if ko not in eggonog_ko_to_gids.keys():
            gid_to_remove = modeled_ko_to_gid[ko]
            to_remove.append(model.genes.get_by_id(gid_to_remove))
            
    
    # remove also orphan reactions!
    to_remove.append(model.genes.get_by_id('orphan'))
    
    
    # delete marked genes!
    # trick to avoid the WARNING "cobra/core/group.py:147: UserWarning: need to pass in a list" 
    # triggered when trying to remove reactions that are included in groups. 
    with warnings.catch_warnings():  # temporarily suppress warnings for this block
        warnings.simplefilter("ignore")  # ignore all warnings
        cobra_logger = logging.getLogger("cobra.util.solver")
        old_level = cobra_logger.level
        cobra_logger.setLevel(logging.ERROR)   

        cobra.manipulation.delete.remove_genes(model, to_remove, remove_reactions=True)

        # restore original behaviour: 
        cobra_logger.setLevel(old_level)   
        
   
    logger.info(f"Found {len(model.genes)} modeled orthologs.")
    return 0



def translate_remaining_kos(logger, model, eggonog_ko_to_gids):
    
    
    _, modeled_gid_to_ko, _ = get_modeled_kos(model) 
    
    
    # iterate reactions:
    for r in model.reactions:

        gpr = r.gene_reaction_rule

        # force each gid to be surrounded by spaces: 
        gpr = ' ' + gpr.replace('(', ' ( ').replace(')', ' ) ') + ' '
        
        for gid in modeled_gid_to_ko.keys():
            if f' {gid} ' in gpr:
                
                new_gids = eggonog_ko_to_gids[modeled_gid_to_ko[gid]]
                gpr = gpr.replace(f' {gid} ', f' ({" or ".join(new_gids)}) ')       
            

        # remove spaces between parenthesis
        gpr = gpr.replace(' ( ', '(').replace(' ) ', ')')
        # remove spaces at the extremes: 
        gpr = gpr[1: -1]


        # New genes are introduced. Parethesis at the extremes are removed if not necessary. 
        r.gene_reaction_rule = gpr
        r.update_genes_from_gpr()
            
            
    # remaining old 'Cluster_'s need to removed.
    # remove if (1) hte ID starts with clusters AND (2) they are no more associated with any reaction
    to_remove = []
    for g in model.genes:
        
        if g.id in ['orphan', 'spontaneous']:
            continue
            
        if g.id in modeled_gid_to_ko.keys() and len(g.reactions)==0:
            to_remove.append(g)
            
    # warning suppression not needed here, as no reaction is actually removed.
    cobra.manipulation.delete.remove_genes(model, to_remove, remove_reactions=True)
    
        
    logger.info(f"Translated orthologs to {len(model.genes)} genes.")
    return 0
        
    

def restore_gene_annotations(logger, model, universe, eggonog_gid_to_kos):
    
    
    for g in model.genes:
        if g.id == 'spontaneous': 
            continue
            
        names = []    
        for ko in eggonog_gid_to_kos[g.id]:
            
            # get the corresponding universal gene:
            uni_g = None
            for ug in universe.genes:
                if 'ko' not in ug.annotation.keys():
                    continue
                if ug.annotation['ko']==ko:  # take the first (and only)
                    uni_g = ug
                    break
            if uni_g == None:  
                # The ko provided by eggnog-mapper is still not modeled in the universe.
                # Multiple ko are possible for each gene. Of these, only 1 could b modeled.
                continue
            
            
            # transfer annotations of this ko/universal gene:
            for key in uni_g.annotation.keys():
                if key == 'ko':
                    continue   # resulting models will loose links to kos.
                if key not in g.annotation:
                    g.annotation[key] = []
                items = uni_g.annotation[key]
                if type(items)==str:  items = [items]
                for i in items:
                    g.annotation[key].append(i)
                    
            # collect names
            names.append(uni_g.name)
        g.name = '; '.join(names)



def adjust_biomass_equation(logger, model, universe, conditional_threshold):
    
    
    # Note: universal and conditional precursors have been defined in 10.1016/j.ymben.2016.12.002 .
    precursor_to_pathway = {  # listing alternative biosynthetic pathways
        
        ##### cofactors_con #####
        #'f4200_c', # coenzyme f420 (electron transfer in methanogens, actinobacteria , and others)
        #'ptrc_c',   # Putrescine
        #'spmd_c',   # Sperimidine
        'pheme_c': ['M00868', 'M00121', 'M00926'],   # protoheme (heme)
        'mql8_c': ['M00116', 'M00930', 'M00931'],  # menaquinol
        'q8h2_c': ['M00117', 'M00989', 'M00128'],  # ubiquinol
        # Methionaquinone
        #'btn_c',    # B7: biotin
        #'ACP_c',    # Acyl-carrier protein
        'adocbl_c': ['M00122'],   # vitamin B12 (cobolamin)
        # Lipoate
        #'uacgam_c'  # uridine diphosphate N-Acetylglucosamine (UDP-GlcNAc)
        
        ##### cofactors_add #####
        'hemeO_c': ['gr_HemeO'],  # heme-O
        'sheme_c': ['M00846'],   # siroheme
        'moco_c': ['M00880'],  # molybdenum cofactor
        'phllqol_c': ['M00932'],  # phylloquinol
        'gthrd_c': ['M00118'],  # Reduced glutathione
        'br_c': ['gr_br'],  # bacterioruberin
        
        
        ##### lipids #####
        #'pe120_c', # phosphatidyl-ethanolamine (12:0;12:0)
        #'pg120_c', # phosphatidyl-glycerol (12:0;12:0)
        #'clpn120_c', # cardiolipin (12:0;12:0;12:0;12:0)
        
        ##### membrane_wall #####
        # 1-lysyl phosphatidylglycerol (plantarum)
        'peptidoSTA_c': ['gr_ptdSTA'], # peptidoglycan (dependant on 'udcpdp_c')
        'WTAgg40r_20n_20a_P_c': ['gr_WTA3'], # teichoic acids
        'WTArg40r_20g_20a_P_c': ['gr_WTA2'], # teichoic acids
        'WTAg40g_20g_20a_P_c':  ['gr_WTA1'], # teichoic acids
        'LTAgg40g_20n_20a_c':  ['gr_LTA1'], # lipoteichoic acids
        'LTAga40g_20t_20a_c':  ['gr_LTA2'], # lipoteichoic acids            
        # capsular polysaccharides
        # kdo_lipid_A
        
    }
    modeled_rids = [r.id for r in model.reactions]
    
    
    cnt_removed = 0
    varprec = {}  # dictionary of variable biomass precursors
    for precursor, pathways in precursor_to_pathway.items(): 
        
        pathway_to_absence = {}
        pathway_to_compstring = {}   # completeness string
        for pathway in pathways:   # 2+ pathways might lead to the same precursor
            # initialize counters:
            cnt_members_tot = 0
            cnt_members_present = 0

            
            if pathway not in [gr.id for gr in universe.groups]:
                continue   # still missing from the universe
                
            for member in universe.groups.get_by_id(pathway).members:
                cnt_members_tot += 1    
                if member.id in modeled_rids:
                    cnt_members_present += 1
            # populate dicts:
            pathway_to_absence[pathway] = (cnt_members_present / cnt_members_tot) < conditional_threshold
            pathway_to_compstring[pathway] = f'{pathway}: {cnt_members_present}/{cnt_members_tot}'
            

        varprec[precursor] = '; '.join(list(pathway_to_compstring.values()))
        if all(list(pathway_to_absence.values())):
            cnt_removed += 1
            logger.debug(f"Biomass precursor '{precursor}' seems not required ({varprec[precursor]}).")
            # add metabolites to the right side (they will disappear if the balance if 0)
            model.reactions.Biomass.add_metabolites({precursor: 0.001})

       
    logger.info(f"Removed {cnt_removed} biomass precursors.")
    return varprec
    

    





