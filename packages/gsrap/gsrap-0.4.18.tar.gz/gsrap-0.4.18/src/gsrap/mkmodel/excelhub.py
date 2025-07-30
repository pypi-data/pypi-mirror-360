import pandas as pnd



def write_excel_model(model, filepath, df_B, df_P):
    
    df_R = []
    df_M = []
    df_T = []
    df_A = []
    
    # format df_B:  # biomass assembly
    df_B.insert(0, 'mid', '')  # new columns as first
    df_B['mid'] = df_B.index
    df_B = df_B.reset_index(drop=True)
    
    # format df_P:  phenotype screening (Biolog(R))
    df_P.insert(0, 'plate:well', '')  # new columns as first
    df_P['plate:well'] = df_P.index
    df_P = df_P.reset_index(drop=True)
    
    
    
    for r in model.reactions:
        
        
        # handle artificial reactions
        if r.id == 'Biomass':
            df_A.append({'rid': r.id, 'rstring': r.reaction, 'type': 'biomass', 'name': r.name})
            
            
        elif len(r.metabolites) == 1:
            if len(r.metabolites)==1 and list(r.metabolites)[0].id.rsplit('_',1)[-1] == 'e': 
                df_A.append({'rid': r.id, 'rstring': r.reaction, 'type': 'exchange', 'name': r.name})
            elif r.lower_bound < 0 and r.upper_bound > 0:
                df_A.append({'rid': r.id, 'rstring': r.reaction, 'type': 'sink', 'name': r.name})
            elif r.lower_bound == 0 and r.upper_bound > 0:
                df_A.append({'rid': r.id, 'rstring': r.reaction, 'type': 'demand', 'name': r.name})
          
        
        else: # more than 1 metabolite involved
            
            # get kr codes: 
            if 'kegg.reaction' not in r.annotation.keys():  kr_ids = ''
            else:  
                kr_ids = r.annotation['kegg.reaction']
                if type(kr_ids) == str: kr_ids = [kr_ids]
                kr_ids = '; '.join([i for i in kr_ids if i!='RXXXXX'])

            # introduce reaction in the correct table: 
            r_dict = {'rid': r.id, 'rstring': r.reaction, 'kr': kr_ids, 'gpr': r.gene_reaction_rule, 'name': r.name}
            if len(set([m.id.rsplit('_',1)[-1] for m in r.metabolites])) == 1:
                df_R.append(r_dict)
            else: df_T.append(r_dict)
        
        
    for m in model.metabolites: 
        
        # get kc codes: 
        if 'kegg.compound' not in m.annotation.keys():  kc_ids = ''
        else:  
            kc_ids = m.annotation['kegg.compound']
            if type(kc_ids) == str: kc_ids = [kc_ids]
            kc_ids = '; '.join([i for i in kc_ids if i!='CXXXXX'])
        
        df_M.append({'mid': m.id, 'formula': m.formula, 'charge': m.charge, 'kc': kc_ids, 'name': m.name})

    
    
    df_R = pnd.DataFrame.from_records(df_R)
    df_M = pnd.DataFrame.from_records(df_M)
    df_T = pnd.DataFrame.from_records(df_T)
    df_A = pnd.DataFrame.from_records(df_A)
    with pnd.ExcelWriter(filepath) as writer:
        df_R.to_excel(writer, sheet_name='Reactions', index=False)
        df_M.to_excel(writer, sheet_name='Metabolites', index=False)
        df_T.to_excel(writer, sheet_name='Transporters', index=False)
        df_A.to_excel(writer, sheet_name='Artificials', index=False)
        df_B.to_excel(writer, sheet_name='Biomass', index=False)
        if len(df_P)!=0: df_P.to_excel(writer, sheet_name='Biolog®', index=False)