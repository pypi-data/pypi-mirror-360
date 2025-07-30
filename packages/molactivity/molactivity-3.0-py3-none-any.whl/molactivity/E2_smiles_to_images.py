import os
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Draw, rdDepictor

class smiles_to_images():

    def __init__(self, dataset='test', input_file='./predict_sample2.csv', output_dir='./ImageData', 
                 line_width=3.0, atom_font_size=0.8, atom_font_weight='normal', 
                 image_size=(2500, 2500), image_format='png', max_atoms=200):
        self.dataset = dataset
        self.input_file = input_file
        self.output_dir = output_dir
        self.line_width = line_width
        self.atom_font_size = atom_font_size
        self.atom_font_weight = atom_font_weight
        self.default_image_size = image_size
        self.original_format = image_format.lower()
        self.image_format = image_format.lower()
        self.max_atoms = max_atoms   
        
        if self.image_format in ['jpg', 'jpeg']:
            self.image_format = 'png'  
        elif self.image_format in ['tif', 'tiff']:
            self.image_format = 'png' 
        
        data = pd.read_csv(self.input_file)
        self.smiles = data.SMILES
        self.id = data.ID
        self.unable_to_draw = []  
        self.gen_sav_images()

    def is_peptide_like(self, smile):
        peptide_patterns = ['NC(=O)', 'C(=O)N', 'CCCCN', 'CCC(=O)O', 'CC(C)C', 'c1ccccc1']
        count = sum(1 for pattern in peptide_patterns if pattern in smile)
        return count >= 3 and len(smile) > 200

    def is_complex_molecule(self, mol, smile):
        if mol is None:
            return True
            
        num_atoms = mol.GetNumAtoms()
        num_bonds = mol.GetNumBonds()
        
        if num_atoms > self.max_atoms:
            return True
        
        if self.max_atoms <= 200: 
            peptide_limit = 150
            if self.is_peptide_like(smile) and num_atoms > peptide_limit:
                return True
            
        if num_atoms > 50 and num_bonds / num_atoms > 1.5:
            return True
            
        return False

    def smile_to_png(self, smile, smile_id):
        try:
            mol = Chem.MolFromSmiles(smile)
            if mol is None:
                self.unable_to_draw.append({
                    'ID': smile_id,
                    'SMILES': smile,
                    'Reason': 'Invalid SMILES - could not parse',
                    'Atoms': 0,
                    'Is_Peptide': False
                })
                return
            
            num_atoms = mol.GetNumAtoms()
            is_peptide = self.is_peptide_like(smile)
            
            if self.is_complex_molecule(mol, smile):
                self.unable_to_draw.append({
                    'ID': smile_id,
                    'SMILES': smile,
                    'Reason': f'Too complex - {num_atoms} atoms (limit: {self.max_atoms})',
                    'Atoms': num_atoms,
                    'Is_Peptide': is_peptide
                })
                return
            
            if num_atoms > 120:
                try:
                    bond_length = 2.5 if is_peptide else 2.0
                    rdDepictor.Compute2DCoords(mol, bondLength=bond_length)
                except:
                    rdDepictor.Compute2DCoords(mol)
                img_size = (self.default_image_size[0] * 4, self.default_image_size[1] * 4)
                line_width = max(1.0, self.line_width * 0.5) 
                
            elif num_atoms > 80:
                try:
                    bond_length = 2.0 if is_peptide else 1.8
                    rdDepictor.Compute2DCoords(mol, bondLength=bond_length)
                except:
                    rdDepictor.Compute2DCoords(mol)
                img_size = (self.default_image_size[0] * 3, self.default_image_size[1] * 3)
                line_width = max(1.0, self.line_width * 0.7)
                
            elif num_atoms > 50:
                try:
                    bond_length = 1.8 if is_peptide else 1.6
                    rdDepictor.Compute2DCoords(mol, bondLength=bond_length)
                except:
                    rdDepictor.Compute2DCoords(mol)
                img_size = (int(self.default_image_size[0] * 2), int(self.default_image_size[1] * 2))
                line_width = self.line_width
                
            elif num_atoms > 25:
                try:
                    rdDepictor.Compute2DCoords(mol, bondLength=1.5)
                except:
                    rdDepictor.Compute2DCoords(mol)
                img_size = (int(self.default_image_size[0] * 1.2), int(self.default_image_size[1] * 1.2))
                line_width = self.line_width
            else:
                rdDepictor.Compute2DCoords(mol)
                img_size = self.default_image_size
                line_width = self.line_width
                        
            output_path = f'{self.output_dir}/{smile_id}.{self.image_format}'
            
            try:
                from rdkit.Chem.Draw import rdMolDraw2D
                
                drawer = None
                try:
                    drawer = rdMolDraw2D.MolDraw2DCairo(img_size[0], img_size[1])
                except:
                    try:
                        drawer = rdMolDraw2D.MolDraw2DAgg(img_size[0], img_size[1])
                    except:
                        pass
                
                if drawer is not None:
                    drawer.SetLineWidth(line_width)
                    opts = drawer.drawOptions()
                    opts.atomLabelFontSize = max(12, int(50 - num_atoms * 0.3))  
                    opts.bondLineWidth = line_width
                    
                    drawer.DrawMolecule(mol)
                    drawer.FinishDrawing()
                    img_data = drawer.GetDrawingText()
                    
                    with open(output_path, 'wb') as f:
                        f.write(img_data)
                else:
                    Draw.MolToFile(mol, output_path, 
                                  size=img_size, 
                                  kekulize=True,
                                  wedgeBonds=True,
                                  bondLineWidth=line_width)
                            
            except Exception as drawing_error:
                try:
                    Draw.MolToFile(mol, output_path, 
                                  size=img_size, 
                                  kekulize=True,
                                  wedgeBonds=True,
                                  bondLineWidth=line_width)
                except Exception as basic_error:
                    self.unable_to_draw.append({
                        'ID': smile_id,
                        'SMILES': smile,
                        'Reason': f'Drawing error: {str(basic_error)}',
                        'Atoms': num_atoms,
                        'Is_Peptide': is_peptide
                    })
                        
        except Exception as e:
            self.unable_to_draw.append({
                'ID': smile_id,
                'SMILES': smile,
                'Reason': f'Processing error: {str(e)}',
                'Atoms': num_atoms if 'num_atoms' in locals() else 0,
                'Is_Peptide': is_peptide if 'is_peptide' in locals() else False
            })

    def gen_sav_images(self):
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"Starting image generation... ({len(self.smiles)} molecules)")
        print(f"Max atoms limit: {self.max_atoms}")
        
        for s, i in zip(self.smiles, self.id):
            self.smile_to_png(s, i)
        
        if self.unable_to_draw:
            unable_df = pd.DataFrame(self.unable_to_draw)
            unable_csv_path = os.path.join(self.output_dir, 'unable_to_draw_smiles.csv')
            unable_df.to_csv(unable_csv_path, index=False)
            print(f"\nSaved {len(self.unable_to_draw)} unable-to-draw molecules to '{unable_csv_path}'")

            print("\n=== Unable to Draw Summary ===")
            print(f"Total molecules: {len(self.smiles)}")
            print(f"Successfully drawn: {len(self.smiles) - len(self.unable_to_draw)}")
            print(f"Unable to draw: {len(self.unable_to_draw)}")
            
            reason_counts = unable_df['Reason'].value_counts()
            print("\nReasons for unable to draw:")
            for reason, count in reason_counts.items():
                print(f"  - {reason}: {count} molecules")
                
            print("\nPeptide molecules unable to draw:")
            peptide_unable = unable_df[unable_df['Is_Peptide'] == True]
            if not peptide_unable.empty:
                for _, row in peptide_unable.iterrows():
                    print(f"  ID {row['ID']}: {row['Atoms']} atoms")
        else:
            print("\nAll molecules were successfully drawn!")
