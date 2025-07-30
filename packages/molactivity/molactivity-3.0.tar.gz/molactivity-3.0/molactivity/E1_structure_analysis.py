import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import Draw, Descriptors
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem.Scaffolds import MurckoScaffold
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import os

class SMILESAnalyzer:
    
    def __init__(self, smiles_data=None, file_path=None, smiles_column='SMILES', activity_column=None):

        self.molecules = []
        self.invalid_smiles = []
        self.valid_smiles = []
        self.activity_data = None
        
        if file_path:
            self.data = pd.read_csv(file_path)
            smiles_list = self.data[smiles_column].tolist()
            if activity_column:
                self.activity_data = self.data[activity_column].tolist()
        elif isinstance(smiles_data, pd.DataFrame):
            self.data = smiles_data
            smiles_list = self.data[smiles_column].tolist()
            if activity_column:
                self.activity_data = self.data[activity_column].tolist()
        elif isinstance(smiles_data, list):
            smiles_list = smiles_data
            self.data = pd.DataFrame({smiles_column: smiles_list})
        else:
            smiles_list = []
            self.data = pd.DataFrame()
        
        for i, smiles in enumerate(smiles_list):
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                self.molecules.append(mol)
                self.valid_smiles.append(smiles)
            else:
                self.invalid_smiles.append(smiles)
        
        print(f"Loaded {len(self.molecules)} valid molecules. Found {len(self.invalid_smiles)} invalid SMILES.")

    def analyze_common_substructures(self, substructures_dict=None):

        if substructures_dict is None:
            substructures_dict = {
                'Benzene': 'c1ccccc1',
                'Phenol': 'c1ccccc1O',
                'Pyridine': 'c1ccncc1',
                'Pyrimidine': 'c1cncnc1',
                'Pyrrole': 'c1cc[nH]c1',
                'Imidazole': 'c1c[nH]cn1',
                'Pyrazole': 'c1cn[nH]c1',
                'Thiophene': 'c1ccsc1',
                'Furan': 'c1ccoc1',
                'Indole': 'c1ccc2c(c1)[nH]cc2',
                'Naphthalene': 'c1ccc2ccccc2c1',
                'Carboxylic Acid': 'C(=O)O',
                'Ester': 'C(=O)OC',
                'Amide': 'C(=O)N',
                'Primary Amine': '[NH2]',
                'Secondary Amine': '[NH1]',
                'Tertiary Amine': '[NH0]',
                'Hydroxyl': '[OH]',
                'Ketone': '[CX3](=O)[CX4]',
                'Aldehyde': '[CX3H1](=O)',
                'Nitro': '[N+](=O)[O-]',
                'Sulfonamide': 'S(=O)(=O)N',
                'Sulfone': 'S(=O)(=O)',
                'Ether': 'COC',
                'Nitrile': 'C#N',
                'Halogen (F)': '[F]',
                'Halogen (Cl)': '[Cl]',
                'Halogen (Br)': '[Br]',
                'Halogen (I)': '[I]',
                'Alkene': 'C=C',
                'Alkyne': 'C#C',
                'Urea': 'NC(=O)N',
                'Guanidine': 'NC(=N)N',
                'Phosphate': 'P(=O)([O-])[O-]',
                'Thiol': '[SH]',
                'Thioether': 'CSC'
            }
        
        results = {}
        for name, smarts in substructures_dict.items():
            pattern = Chem.MolFromSmarts(smarts)
            if pattern:
                matches = [mol.HasSubstructMatch(pattern) for mol in self.molecules]
                count = sum(matches)
                percentage = (count / len(self.molecules)) * 100 if self.molecules else 0
                results[name] = {
                    'SMARTS': smarts,
                    'Count': count,
                    'Percentage': percentage
                }
        
        results_df = pd.DataFrame(results).T
        results_df = results_df.sort_values('Count', ascending=False)
        return results_df
    
    def analyze_scaffolds(self, n=10):

        scaffolds = []
        for mol in self.molecules:
            try:
                scaffold = MurckoScaffold.GetScaffoldForMol(mol)
                scaffolds.append(Chem.MolToSmiles(scaffold))
            except:
                scaffolds.append(None)
        
        scaffold_counts = Counter(filter(None, scaffolds))
        top_scaffolds = scaffold_counts.most_common(n)
        
        results = []
        for scaffold, count in top_scaffolds:
            percentage = (count / len(self.molecules)) * 100
            mol = Chem.MolFromSmiles(scaffold)
            results.append({
                'Scaffold': scaffold,
                'Count': count,
                'Percentage': percentage,
                'Molecule': mol
            })
        
        return pd.DataFrame(results)
    
    def analyze_ring_systems(self):

        ring_counts = []
        aromatic_ring_counts = []
        aliphatic_ring_counts = []
        
        for mol in self.molecules:
    
            num_rings = Chem.rdMolDescriptors.CalcNumRings(mol)
            ring_counts.append(num_rings)
            
            aromatic_rings = Chem.rdMolDescriptors.CalcNumAromaticRings(mol)
            aromatic_ring_counts.append(aromatic_rings)
            
            aliphatic_rings = num_rings - aromatic_rings
            aliphatic_ring_counts.append(aliphatic_rings)
        
        results = {
            'Total Molecules': len(self.molecules),
            'Ring Statistics': {
                'Average Rings per Molecule': np.mean(ring_counts),
                'Median Rings per Molecule': np.median(ring_counts),
                'Max Rings in a Molecule': max(ring_counts),
                'Molecules with No Rings': ring_counts.count(0),
                'Percentage with No Rings': (ring_counts.count(0) / len(ring_counts)) * 100,
                'Ring Count Distribution': Counter(ring_counts)
            },
            'Aromatic Ring Statistics': {
                'Average Aromatic Rings': np.mean(aromatic_ring_counts),
                'Molecules with Aromatic Rings': len([c for c in aromatic_ring_counts if c > 0]),
                'Percentage with Aromatic Rings': (len([c for c in aromatic_ring_counts if c > 0]) / len(aromatic_ring_counts)) * 100,
                'Aromatic Ring Distribution': Counter(aromatic_ring_counts)
            },
            'Aliphatic Ring Statistics': {
                'Average Aliphatic Rings': np.mean(aliphatic_ring_counts),
                'Molecules with Aliphatic Rings': len([c for c in aliphatic_ring_counts if c > 0]),
                'Percentage with Aliphatic Rings': (len([c for c in aliphatic_ring_counts if c > 0]) / len(aliphatic_ring_counts)) * 100,
                'Aliphatic Ring Distribution': Counter(aliphatic_ring_counts)
            }
        }
        
        return results
    
    def analyze_functional_groups(self):

        return self.analyze_common_substructures()
    
    def analyze_physicochemical_properties(self):

        properties = defaultdict(list)
        
        for mol in self.molecules:
            properties['MW'].append(Descriptors.MolWt(mol))
            properties['LogP'].append(Descriptors.MolLogP(mol))
            properties['TPSA'].append(Descriptors.TPSA(mol))
            properties['HBA'].append(Descriptors.NumHAcceptors(mol))
            properties['HBD'].append(Descriptors.NumHDonors(mol))
            properties['RotBonds'].append(Descriptors.NumRotatableBonds(mol))
            properties['HeavyAtoms'].append(mol.GetNumHeavyAtoms())
            properties['Rings'].append(Descriptors.RingCount(mol))
            properties['AromaticRings'].append(Descriptors.NumAromaticRings(mol))
            properties['Fsp3'].append(Descriptors.FractionCSP3(mol))
        
        df = pd.DataFrame(properties)
        
        stats = {
            'Property': [],
            'Min': [],
            'Max': [],
            'Mean': [],
            'Median': []
        }
        
        for col in df.columns:
            stats['Property'].append(col)
            stats['Min'].append(df[col].min())
            stats['Max'].append(df[col].max())
            stats['Mean'].append(df[col].mean())
            stats['Median'].append(df[col].median())
        
        return pd.DataFrame(stats), df
    
    def generate_visualizations(self, output_dir='analysis_results'):

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        substructure_df = self.analyze_common_substructures()
        substructure_df = substructure_df.sort_values('Count', ascending=False).head(20)
        
        plt.figure(figsize=(12, 8))
        plt.barh(substructure_df.index, substructure_df['Count'])
        plt.title('Top 20 Common Substructures')
        plt.xlabel('Count')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'top_substructures.png'), dpi=300)
        
        stats_df, props_df = self.analyze_physicochemical_properties()
        
        for prop in ['MW', 'LogP', 'TPSA', 'HBA', 'HBD', 'RotBonds']:
            plt.figure(figsize=(10, 6))
            plt.hist(props_df[prop], bins=20)
            plt.title(f'Distribution of {prop}')
            plt.xlabel(prop)
            plt.ylabel('Count')
            plt.savefig(os.path.join(output_dir, f'{prop}_distribution.png'), dpi=300)
        
        scaffold_df = self.analyze_scaffolds(n=10)
        if not scaffold_df.empty and 'Molecule' in scaffold_df.columns:
            scaffold_mols = [m for m in scaffold_df['Molecule'] if m is not None]
            if scaffold_mols:
                legends = [f"{i+1}. Count/Percentage: {int(row['Count'])}, {row['Percentage']:.1f}%" 
                          for i, row in scaffold_df.iterrows()]
                
                try:
                    mol_count = len(scaffold_mols)
                    mols_per_row = 5
                    rows = (mol_count + mols_per_row - 1) // mols_per_row  
                    
                    mol_width, mol_height = 400, 350  
                    
                    x_gap, y_gap = 20, 20  
                    
                    panel_width = mol_width * mols_per_row + x_gap * (mols_per_row - 1)
                    panel_height = mol_height * rows + y_gap * (rows - 1) + 40  
                    
                    drawer = rdMolDraw2D.MolDraw2DCairo(panel_width, panel_height)
                    drawer.SetFontSize(14)  
                    
                    for i, mol in enumerate(scaffold_mols):
                        if mol is None:
                            continue
                            
                        row = i // mols_per_row
                        col = i % mols_per_row
                        
                        x_offset = col * (mol_width + x_gap)
                        y_offset = row * (mol_height + y_gap)
                        
                        drawer.SetOffset(x_offset, y_offset)
                        drawer.SetPanelSize(mol_width, mol_height)
                        
                        drawer.DrawMolecule(mol, legend=legends[i] if i < len(legends) else "")
                        
                    drawer.FinishDrawing()
                    with open(os.path.join(output_dir, 'top_scaffolds.png'), 'wb') as f:
                        f.write(drawer.GetDrawingText())
                    
                except Exception as e:
                    try:
                        img = Draw.MolsToGridImage(
                            scaffold_mols, 
                            molsPerRow=5,
                            subImgSize=(500, 400), 
                            legends=legends
                        )
                        img.save(os.path.join(output_dir, 'top_scaffolds.png'))
                    except Exception as e2:
                        print(f"failed: {e2}")

        report_data = []
        
        report_data.append({
            'Category': 'Dataset Information',
            'Item': 'Total molecules analyzed',
            'Count': len(self.molecules),
            'Percentage': '',
            'Average': '',
            'Range_Min': '',
            'Range_Max': '',
            'Median': '',
            'SMARTS': '',
            'SMILES': '',
            'Additional_Info': ''
        })
        
        report_data.append({
            'Category': 'Dataset Information',
            'Item': 'Invalid SMILES found',
            'Count': len(self.invalid_smiles),
            'Percentage': '',
            'Average': '',
            'Range_Min': '',
            'Range_Max': '',
            'Median': '',
            'SMARTS': '',
            'SMILES': '',
            'Additional_Info': ''
        })
        
        for idx, (name, row) in enumerate(substructure_df.iterrows(), 1):
            report_data.append({
                'Category': 'Common Substructures',
                'Item': name,
                'Count': row['Count'],
                'Percentage': f"{row['Percentage']:.1f}%",
                'Average': '',
                'Range_Min': '',
                'Range_Max': '',
                'Median': '',
                'SMARTS': row['SMARTS'],
                'SMILES': '',
                'Additional_Info': ''
            })
        
        ring_info = self.analyze_ring_systems()
        report_data.append({
            'Category': 'Ring System Analysis',
            'Item': 'Average rings per molecule',
            'Count': '',
            'Percentage': '',
            'Average': f"{ring_info['Ring Statistics']['Average Rings per Molecule']:.1f}",
            'Range_Min': '',
            'Range_Max': ring_info['Ring Statistics']['Max Rings in a Molecule'],
            'Median': ring_info['Ring Statistics']['Median Rings per Molecule'],
            'SMARTS': '',
            'SMILES': '',
            'Additional_Info': f"Molecules with no rings: {ring_info['Ring Statistics']['Molecules with No Rings']}"
        })
        
        report_data.append({
            'Category': 'Ring System Analysis',
            'Item': 'Molecules with aromatic rings',
            'Count': ring_info['Aromatic Ring Statistics']['Molecules with Aromatic Rings'],
            'Percentage': f"{ring_info['Aromatic Ring Statistics']['Percentage with Aromatic Rings']:.1f}%",
            'Average': f"{ring_info['Aromatic Ring Statistics']['Average Aromatic Rings']:.1f}",
            'Range_Min': '',
            'Range_Max': '',
            'Median': '',
            'SMARTS': '',
            'SMILES': '',
            'Additional_Info': ''
        })
        
        report_data.append({
            'Category': 'Ring System Analysis',
            'Item': 'Molecules with aliphatic rings',
            'Count': ring_info['Aliphatic Ring Statistics']['Molecules with Aliphatic Rings'],
            'Percentage': f"{ring_info['Aliphatic Ring Statistics']['Percentage with Aliphatic Rings']:.1f}%",
            'Average': f"{ring_info['Aliphatic Ring Statistics']['Average Aliphatic Rings']:.1f}",
            'Range_Min': '',
            'Range_Max': '',
            'Median': '',
            'SMARTS': '',
            'SMILES': '',
            'Additional_Info': ''
        })
        
        for idx, row in stats_df.iterrows():
            report_data.append({
                'Category': 'Physicochemical Properties',
                'Item': row['Property'],
                'Count': '',
                'Percentage': '',
                'Average': f"{row['Mean']:.1f}",
                'Range_Min': f"{row['Min']:.1f}",
                'Range_Max': f"{row['Max']:.1f}",
                'Median': f"{row['Median']:.1f}",
                'SMARTS': '',
                'SMILES': '',
                'Additional_Info': ''
            })
        
        for idx, row in scaffold_df.iterrows():
            report_data.append({
                'Category': 'Top Scaffolds',
                'Item': f"Scaffold {idx+1}",
                'Count': row['Count'],
                'Percentage': f"{row['Percentage']:.1f}%",
                'Average': '',
                'Range_Min': '',
                'Range_Max': '',
                'Median': '',
                'SMARTS': '',
                'SMILES': row['Scaffold'],
                'Additional_Info': ''
            })
        
        report_df = pd.DataFrame(report_data)
        report_df.to_csv(os.path.join(output_dir, 'analysis_report.csv'), index=False)
        
        return output_dir
    
    def compare_active_inactive(self, activity_threshold=0.5):

        if self.activity_data is None:
            print("No activity data available for comparison")
            return None
        
        active_indices = [i for i, activity in enumerate(self.activity_data) if activity >= activity_threshold]
        inactive_indices = [i for i, activity in enumerate(self.activity_data) if activity < activity_threshold]
        
        active_mols = [self.molecules[i] for i in active_indices]
        inactive_mols = [self.molecules[i] for i in inactive_indices]
        
        print(f"Active molecules: {len(active_mols)}")
        print(f"Inactive molecules: {len(inactive_mols)}")
        
        active_analyzer = SMILESAnalyzer([self.valid_smiles[i] for i in active_indices])
        inactive_analyzer = SMILESAnalyzer([self.valid_smiles[i] for i in inactive_indices])
        
        active_substructures = active_analyzer.analyze_common_substructures()
        inactive_substructures = inactive_analyzer.analyze_common_substructures()
        
        comparative_df = pd.DataFrame()
        
        for idx, row in active_substructures.iterrows():
            active_count = row['Count']
            active_pct = row['Percentage']
            
            if idx in inactive_substructures.index:
                inactive_count = inactive_substructures.loc[idx, 'Count']
                inactive_pct = inactive_substructures.loc[idx, 'Percentage']
            else:
                inactive_count = 0
                inactive_pct = 0
            
            enrichment = (active_pct / inactive_pct) if inactive_pct > 0 else float('inf')
            
            comparative_df.loc[idx, 'Active Count'] = active_count
            comparative_df.loc[idx, 'Active %'] = active_pct
            comparative_df.loc[idx, 'Inactive Count'] = inactive_count
            comparative_df.loc[idx, 'Inactive %'] = inactive_pct
            comparative_df.loc[idx, 'Enrichment Ratio'] = enrichment
        
        return comparative_df.sort_values('Enrichment Ratio', ascending=False)
    
    def save_analysis_report(self, output_file="smiles_analysis_report.csv"):
 
        substructure_df = self.analyze_common_substructures()
        
        substructure_df.to_csv(output_file)
        return output_file
