
from .A5_chem_utils import ChemDict, LRUCache, ChemRegex

class ChemicalFeatureGenerator:
    
    def __init__(self, fp_size=2048, radius=2):
  
        self.fp_size = fp_size
        self.radius = radius
        
        self._init_atom_table()
        
        self.bond_types = {
            '-': 1,  # 单键
            '=': 2,  # 双键
            '#': 3,  # 三键
            ':': 4,  # 芳香键
            '/': 5,  # 立体化学键（顺式）
            '\\': 6, # 立体化学键（反式）
            '.': 7   # 配位键
        }
        
        self.ring_cache = {}
        self.feature_cache = LRUCache(maxsize=10000)(self._calculate_hash_indices)
        self.hash_seeds = [3, 7, 11, 17, 23, 29, 37, 43]  
        
        self.atom_regex = ChemRegex(r"""
            ^\[
            (?:([A-Z][a-z]*)      # 元素
            |(\*))                # 通配符
            (?:@([A-Z]+))?        # 手性标记
            (?:H(\d*))?           # 氢原子数
            (?:([+-])             # 电荷符号
            (\d*))?               # 电荷数
            (?::(\d+))?           # 原子映射编号
            \]$
        """, ChemRegex.VERBOSE)
        self.simple_atom_regex = ChemRegex(r'^([A-Z][a-z]?)(.*)$')
        self.charge_regex = ChemRegex(r'^([+-])(\d*)$')
        self.anychar_regex = ChemRegex(r'^(.)(.*)$')

    def _init_atom_table(self):
        elements = ['C', 'N', 'O', 'S', 'P', 'F', 'Cl', 'Br', 'I', 'B', 'Si', '*']
        charges = [-2, -1, 0, 1, 2]
        hybridizations = ['SP3', 'SP2', 'SP', 'SP3D', 'UNKNOWN']
        chiral_types = ['TH', 'AL', 'SP', 'DB', 'OH', 'NONE']
        
        self.atom_table = {}
        index = 0
        for elem in elements:
            for charge in charges:
                for hybrid in hybridizations:
                    for chiral in chiral_types:
                        self.atom_table[(elem, charge, hybrid, chiral)] = index
                        index += 1

    def generate_morgan_fingerprint(self, smiles):
  
        try:
            self.current_smiles = smiles
            
            normalized_smiles = self._normalize_smiles(smiles)
            
            atoms, bonds, rings = self._parse_smiles(normalized_smiles)
            
            fp = [0.0] * self.fp_size
            self._process_atomic_features(atoms, fp)
            self._process_bond_features(bonds, atoms, fp)
            self._process_ring_features(rings, atoms, fp)
            self._process_stereo_features(bonds, fp)
            self._process_charge_features(atoms, fp)
            self._process_global_features(atoms, bonds, rings, fp)
            
            return fp
        except ValueError as e:
            error_str = str(e)
         
            return [0.0] * self.fp_size
        except Exception as e:
            error_str = str(e)
          
            return [0.0] * self.fp_size

    def _normalize_smiles(self, smiles):

        normalized = []
        i = 0
        while i < len(smiles):
            c = smiles[i]
            if c == 'c':
                normalized.append('C')
                if (i+1 < len(smiles) and smiles[i+1].isdigit()) or \
                   (i > 0 and smiles[i-1] in ['(', '%']):
                    normalized.append('H')
            elif c == 'n':
                normalized.append('N')
            elif c == 'o':
                normalized.append('O')
            elif c == 's':
                normalized.append('S')
            elif c == '%':
                normalized.append('%')
                i += 1
                while i < len(smiles) and smiles[i].isdigit():
                    normalized.append(smiles[i])
                    i += 1
                continue
            else:
                normalized.append(c)
            i += 1
        return ''.join(normalized)
    
    def _parse_smiles(self, smiles):
        atoms = []
        bonds = []
        ring_marks = ChemDict()
        branch_stack = []
        current_atom = None
        i = 0
        
        while i < len(smiles):
            char = smiles[i]
            
            if char == '%':
                ring_num, i = self._parse_multi_digit_number(smiles, i+1)
                if current_atom is not None:
                    self._process_ring_marker(ring_num, current_atom, ring_marks, bonds, atoms)
                continue
                
            if char == '[':
                atom, i = self._parse_complex_atom(smiles, i)
                atoms.append(atom)
                current_atom = len(atoms) - 1
                
                if branch_stack and branch_stack[-1] is not None:
                    prev_atom = branch_stack[-1]
                    self._create_bond_pair(prev_atom, current_atom, 1, bonds)
                    atoms[prev_atom]['bonds'].append(current_atom)
                    atoms[current_atom]['bonds'].append(prev_atom)
                    
            elif char.isalpha():
                atom, i = self._parse_simple_atom(smiles, i)
                atoms.append(atom)
                current_atom = len(atoms) - 1
                
                if branch_stack and branch_stack[-1] is not None:
                    prev_atom = branch_stack[-1]
                    self._create_bond_pair(prev_atom, current_atom, 1, bonds)
                    atoms[prev_atom]['bonds'].append(current_atom)
                    atoms[current_atom]['bonds'].append(prev_atom)
                    
            elif char in self.bond_types:
                bond_type = self.bond_types[char]
                i += 1  
                
                if current_atom is None or i >= len(smiles):
                    continue
                    
                next_char = smiles[i]
                
                if next_char == '[':
                    
                    atom, new_i = self._parse_complex_atom(smiles, i)
                    atoms.append(atom)
                    next_atom = len(atoms) - 1
                    self._create_bond_pair(current_atom, next_atom, bond_type, bonds)
                    atoms[current_atom]['bonds'].append(next_atom)
                    atoms[next_atom]['bonds'].append(current_atom)
                    i = new_i
                    current_atom = next_atom
                    
                elif next_char.isalpha():
                    atom, new_i = self._parse_simple_atom(smiles, i)
                    atoms.append(atom)
                    next_atom = len(atoms) - 1
                    self._create_bond_pair(current_atom, next_atom, bond_type, bonds)
                    atoms[current_atom]['bonds'].append(next_atom)
                    atoms[next_atom]['bonds'].append(current_atom)
                    i = new_i
                    current_atom = next_atom
                    
                elif next_char == '(':
                    continue
                    
            elif char.isdigit():
                if current_atom is not None:
                    self._process_ring_marker(int(char), current_atom, ring_marks, bonds, atoms)
                i += 1
                
            elif char == '(':
                branch_stack.append(current_atom)
                i += 1
                
            elif char == ')':
                if branch_stack:
                    current_atom = branch_stack.pop()
                i += 1
                
            else:
                i += 1  
        
        self._post_parse_validation(atoms, bonds)
        return atoms, bonds, ring_marks
    
    def _process_ring_marker(self, ring_id, current_atom, ring_marks, bonds, atoms):
        if ring_id in ring_marks:
            prev_data = ring_marks[ring_id]
            prev_atom = prev_data['atom']
            bond_type = prev_data.get('bond_type', 1)
            
            self._create_bond_pair(current_atom, prev_atom, bond_type, bonds)
            atoms[current_atom]['bonds'].append(prev_atom)
            atoms[prev_atom]['bonds'].append(current_atom)
            del ring_marks[ring_id]
        else:
            ring_marks[ring_id] = {
                'atom': current_atom,
                'bond_type': 1,  
                'stereo': 0
            }

    def _post_parse_validation(self, atoms, bonds):

        for bond in bonds:
            if bond['from'] >= len(atoms) or bond['to'] >= len(atoms):
                raise ValueError
        
    def _get_max_bonds(self, element):
        max_bonds = {
            'C': 4, 'N': 3, 'O': 2, 'S': 2,
            'P': 3, 'F': 1, 'Cl': 1, 'Br': 1,
            'I': 1, 'B': 3, 'Si': 4, '*': 0,
            'H': 1
        }
        return max_bonds.get(element.upper(), 0)

    def _parse_complex_atom(self, smiles, start):
        end = smiles.find(']', start)
        if end == -1:
            raise ValueError
        
        content = smiles[start+1:end]
        match = self.atom_regex.match(content)
        
        element = None
        chirality = 'NONE'
        h_count = 0
        charge = 0
        atom_map = None
        
        if match:
            elem, wildcard, chiral, h_count_str, charge_sign, charge_num, atom_map_num = match.groups()
            
            element = wildcard if wildcard else elem
            if not element:
                raise ValueError
            
            if chiral:
                chirality = chiral
            
            if h_count_str is not None:
                try:
                    h_count = int(h_count_str) if h_count_str else 1
                except ValueError:
                    h_count = 0
            
            if charge_sign:
                try:
                    charge = 1 if charge_sign == '+' else -1
                    if charge_num:
                        charge *= int(charge_num)
                except ValueError:
                    charge = 0
            
            if atom_map_num:
                try:
                    atom_map = int(atom_map_num)
                except ValueError:
                    atom_map = None
        else:
            try:
                relaxed_match = ChemRegex(r'^([A-Z][a-z]*)(.*)$').match(content)
                if not relaxed_match:
                    element = 'C'
                else:
                    element, rest = relaxed_match.groups()
                    
                    charge_match = ChemRegex(r'([+-])(\d*)').search(rest)
                    if charge_match:
                        try:
                            charge_sign, charge_num = charge_match.groups()
                            charge = 1 if charge_sign == '+' else -1
                            if charge_num:
                                charge *= int(charge_num)
                        except ValueError:
                            charge = 0
            except Exception:
                element = 'C'
        
        if h_count == 0 and element in ['C', 'N', 'O', 'S', 'P']:
            h_count = self._estimate_hydrogens(element, False)
        
        return {
            'element': element.upper() if element else 'C',
            'charge': charge,
            'h_count': h_count,
            'chirality': chirality,
            'bonds': [],
            'aromatic': False,
            'atom_map': atom_map
        }, end + 1
    
    def _parse_simple_atom(self, smiles, start):
        element, rest = self.parse_relaxed_atom(smiles[start:])
        
        aromatic = False
        if element.islower():
            element = element.upper()
            aromatic = True
        
        hydrogens = self._estimate_hydrogens(element, aromatic)
        
        return {
            'element': element,
            'charge': 0,
            'h_count': hydrogens,
            'chirality': 'NONE',
            'bonds': [],
            'aromatic': aromatic,
            'atom_map': None
        }, start + len(element) + len(rest)

    def _process_atomic_features(self, atoms, fp):
        for atom in atoms:
            features = [
                f"element_{atom['element']}",
                f"charge_{atom['charge']}",
                f"hcount_{atom['h_count']}",
                f"chiral_{atom['chirality']}",
                f"valence_{len(atom['bonds'])}"
            ]
            
            if atom['aromatic']:
                features.append("aromatic_atom")
                features.append(f"aromatic_{atom['element']}")
            
            neighbors = [atoms[i]['element'] for i in atom['bonds']]
            if neighbors:
                features.append(f"neighbors_{'_'.join(sorted(neighbors))}")
                features.append(f"neighbor_count_{len(neighbors)}")
            
            if atom['element'] in ['C', 'N', 'O', 'S']:
                features.append(f"heteroatom_{atom['element']}")
            
            self._hash_features(features, fp)

    def _process_bond_features(self, bonds, atoms, fp):
        for bond in bonds:
            a1 = atoms[bond['from']]
            a2 = atoms[bond['to']]
            
            features = [
                f"bond_type_{bond['type']}",
                f"bond_{a1['element']}-{a2['element']}",
                f"bond_order_{bond['type']}",
                f"stereo_{bond.get('stereo', 0)}"
            ]
            
            if bond['type'] in [5, 6]:
                features.append("stereo_bond")
                features.append(f"stereo_{a1['element']}-{a2['element']}")
            
            if a1['aromatic'] and a2['aromatic']:
                features.append("aromatic_bond")
            
            a1_neighbors = len(a1['bonds'])
            a2_neighbors = len(a2['bonds'])
            features.append(f"bond_topology_{a1_neighbors}-{a2_neighbors}")
            
            self._hash_features(features, fp)

    def _process_ring_features(self, rings, atoms, fp):
        for ring_id, ring_data in rings.items():
            cache_key = hash((ring_id, frozenset(ring_data.items())))
            if cache_key in self.ring_cache:
                features = self.ring_cache[cache_key]
            else:
                features = self._detect_ring_properties(ring_data, atoms)
                self.ring_cache[cache_key] = features
            self._hash_features(features, fp)

    def _process_stereo_features(self, bonds, fp):
        stereo_bonds = [b for b in bonds if b['type'] in (5, 6)]
        if stereo_bonds:
            self._hash_features(["stereo_chemistry_present"], fp)

    def _process_charge_features(self, atoms, fp):
        for atom in atoms:
            if atom['charge'] != 0:
                self._hash_features([f"charge_{atom['charge']}"], fp)

    def _process_global_features(self, atoms, bonds, rings, fp):
        features = [
            f"mol_num_atoms_{len(atoms)}",
            f"mol_num_bonds_{len(bonds)//2}",
            f"mol_num_rings_{len(rings)}",
            f"mol_weight_{sum(self._get_atomic_weight(a['element']) for a in atoms):.1f}"
        ]
        self._hash_features(features, fp)

    def _hash_features(self, features, fp):
        for feature in features:
            if not feature:
                continue
            norm_feature = feature.strip().upper()
            indices = self.feature_cache(norm_feature)
            for idx in indices:
                fp[idx] = 1.0  

    @LRUCache(maxsize=10000)
    def _calculate_hash_indices(self, feature):
        indices = []
        for seed in self.hash_seeds:
            hash_val = self._rotating_hash(feature, seed)
            indices.append(hash_val % self.fp_size)
        return indices

    def _rotating_hash(self, s, seed):
        hash_val = 0x89ABCDEF
        s = str(s)
        for i, c in enumerate(s):
            hash_val = ((hash_val << 13) | (hash_val >> 19)) ^ (ord(c) * seed * (i+1))
            hash_val &= 0xFFFFFFFF 
        return hash_val

    def _parse_multi_digit_number(self, smiles, start):
        num_str = []
        i = start
        while i < len(smiles) and smiles[i].isdigit():
            num_str.append(smiles[i])
            i += 1
        try:
            return int(''.join(num_str)) if num_str else 0, i
        except ValueError:
            return 0, i

    def _create_bond_pair(self, a1, a2, bond_type, bonds):
        bonds.append({'from': a1, 'to': a2, 'type': bond_type})
        bonds.append({'from': a2, 'to': a1, 'type': bond_type})

    def _connect_branch(self, branch_stack, current_atom, bonds):
        if branch_stack:
            prev_atom = branch_stack[-1]
            self._create_bond_pair(prev_atom, current_atom, 1, bonds)

    def _detect_ring_properties(self, ring_data, atoms):
        members = self._find_ring_members(ring_data['atom'], atoms)
        features = []
        
        ring_size = len(members)
        features.append(f"ring_size_{ring_size}")
        
        elements = sorted({atoms[i]['element'] for i in members})
        features.append(f"ring_composition_{'_'.join(elements)}")
        
        if all(atoms[i].get('aromatic', False) for i in members):
            features.append("aromatic_ring")
            features.append(f"aromatic_ring_size_{ring_size}")
            features.append(f"aromatic_ring_composition_{'_'.join(elements)}")
        
        bond_types = {}  
        for i in range(ring_size):
            a1 = members[i]
            a2 = members[(i+1)%ring_size]
            for bond in self._get_bonds_between(a1, a2, atoms):
                bond_type = bond['type']
                bond_types[bond_type] = bond_types.get(bond_type, 0) + 1
        for bt, count in bond_types.items():
            features.append(f"ring_bondtype_{bt}_count_{count}")
        
        ring_degrees = [len(atoms[i]['bonds']) for i in members]
        features.append(f"ring_degrees_{'_'.join(map(str, sorted(ring_degrees)))}")
        
        if any(atoms[i]['chirality'] != 'NONE' for i in members):
            features.append("chiral_ring")
        
        return features

    def _find_ring_members(self, start_atom, atoms):
        visited = {}
        stack = [(start_atom, -1, [])] 
        
        while stack:
            current, parent, path = stack.pop()
            if current in visited:
                if current == start_atom and len(path) >= 3:
                    return path
                continue
            
            visited[current] = parent
            new_path = path + [current]
            
            for neighbor in atoms[current]['bonds']:
                if neighbor != parent:
                    stack.append((neighbor, current, new_path))
        
        return [start_atom]

    def _get_bonds_between(self, a1, a2, atoms):
        bonds = []
        for atom_idx, atom in enumerate(atoms):
            if atom_idx == a1:
                if a2 in atom['bonds']:
                    for bond_idx, bond in enumerate(atom['bonds']):
                        if bond == a2:
                            bonds.append({'from': a1, 'to': a2, 'type': 1})
        return bonds

    def _get_atomic_weight(self, element):
        weights = {
            'C': 12.01, 'N': 14.01, 'O': 16.00, 'S': 32.07,
            'P': 30.97, 'F': 19.00, 'Cl': 35.45, 'Br': 79.90,
            'I': 126.90, 'B': 10.81, 'Si': 28.09, '*': 0.00,
            'H': 1.01 
        }
        return weights.get(element.upper(), 0.00)

    def _estimate_hydrogens(self, element, aromatic):
        valence = {
            'C': 4, 'N': 3, 'O': 2, 'S': 2,
            'P': 3, 'F': 1, 'Cl': 1, 'Br': 1,
            'I': 1, 'B': 3, 'Si': 4, '*': 0,
            'H': 1 
        }
        base = valence.get(element.upper(), 0)
        return max(0, base - 1) if aromatic else base

    def parse_atom(self, atom_str):
        if not (atom_str.startswith('[') and atom_str.endswith(']')):
            return None
        content = atom_str[1:-1]
        element = ''
        i = 0
        while i < len(content) and (content[i].isalpha() or content[i] == '*'):
            element += content[i]
            i += 1
        chiral = None
        if i < len(content) and content[i] == '@':
            chiral = ''
            i += 1
            while i < len(content) and content[i].isalpha():
                chiral += content[i]
                i += 1
        hydrogens = None
        if i < len(content) and content[i] == 'H':
            i += 1
            hnum = ''
            while i < len(content) and content[i].isdigit():
                hnum += content[i]
                i += 1
            hydrogens = int(hnum) if hnum else 1
        charge = None
        if i < len(content) and content[i] in '+-':
            sign = content[i]
            i += 1
            cnum = ''
            while i < len(content) and content[i].isdigit():
                cnum += content[i]
                i += 1
            charge = int(sign + (cnum if cnum else '1'))
        mapping = None
        if i < len(content) and content[i] == ':':
            i += 1
            mnum = ''
            while i < len(content) and content[i].isdigit():
                mnum += content[i]
                i += 1
            mapping = int(mnum) if mnum else None
        return element, chiral, hydrogens, charge, mapping

    def parse_relaxed_atom(self, atom_str):
        if not atom_str:
            return None, ""
        match = self.simple_atom_regex.match(atom_str)
        if match:
            element, rest = match.groups()
            return element, rest
        match = self.anychar_regex.match(atom_str)
        if match:
            element, rest = match.groups()
            return element, rest
        return "", atom_str

    def parse_charge(self, charge_str):
        if not charge_str:
            return None, 0
        match = self.charge_regex.match(charge_str)
        if match:
            sign, num = match.groups()
            value = int(num) if num else 1
            return sign, value
        return None, 0
