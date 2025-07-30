
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors

def calculate_mol_weight(smiles):
    mol = Chem.MolFromSmiles(smiles)
    if mol is not None:
        return Descriptors.MolWt(mol)
    else:
        return None

def process_molecules(input_file, output_file):
    data = pd.read_csv(input_file)

    results = []

    for index, row in data.iterrows():
        smiles = row["SMILES"]
        mol_weight = calculate_mol_weight(smiles)
        if mol_weight is not None:
            results.append({"SMILES": smiles, "Molecular Weight": mol_weight})

    results_df = pd.DataFrame(results)

    results_df.to_csv(output_file, index=False)

