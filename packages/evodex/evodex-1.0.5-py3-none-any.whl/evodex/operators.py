import rdkit
from rdkit import Chem
from rdkit.Chem import AllChem, Draw
from rdkit.Chem import rdChemReactions
from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')

# Function to check if an atom is sp3 hybridized
def _is_sp3(atom):
    for bond in atom.GetBonds():
        if bond.GetBondType() != Chem.BondType.SINGLE:
            return False
    return True

# Function to remove stereochemistry from a molecule
def _remove_stereochemistry(molecule):
    for atom in molecule.GetAtoms():
        atom.SetChiralTag(Chem.rdchem.ChiralType.CHI_UNSPECIFIED)
    for bond in molecule.GetBonds():
        bond.SetStereo(Chem.rdchem.BondStereo.STEREONONE)
    return molecule

# Function to process a molecule and identify static hydrogen atom indices
def _process_static_hydrogens(molecule, center_atom_indices):
    static_hydrogen_indices = set()
    for atom in molecule.GetAtoms():
        if atom.GetAtomicNum() != 1 and atom.GetAtomicNum() != 85:
            continue
        if atom.GetAtomMapNum() == 0:
            continue
        if atom.GetIdx() not in center_atom_indices:
            static_hydrogen_indices.add(atom.GetIdx())
    return static_hydrogen_indices

# Function to process a molecule and identify center atom indices
def _extract_center_atom_indices(molecule, center_atom_maps):
    center_atom_indices = set()
    for atom in molecule.GetAtoms():
        atom_map = atom.GetAtomMapNum()
        if atom_map in center_atom_maps:
            center_atom_indices.add(atom.GetIdx())
    return center_atom_indices

# Function to process a molecule and identify sigma atom indices
def _process_sigma_molecule(molecule, center_atom_indices):
    sigma_indices = set()
    for atom in molecule.GetAtoms():
        atom_idx = atom.GetIdx()
        for neighbor in atom.GetNeighbors():
            neighbor_idx = neighbor.GetIdx()
            if neighbor_idx in center_atom_indices:
                sigma_indices.add(atom_idx)
    return sigma_indices

# Helper function to check if an atom is SP2 or SP hybridized
def _is_sp_or_sp2(atom):
    for bond in atom.GetBonds():
        if bond.GetBondType() in [Chem.rdchem.BondType.DOUBLE, Chem.rdchem.BondType.TRIPLE]:
            return True
    return False

def _grow_pi_shell(reaction, current_pi_indices):
    new_pi_indices = ([], [])
    flagged_atom_maps = set()

    # Helper function to process a molecule
    def process_molecule(molecule, current_indices):
        pi_set = set()
        for atom_idx in current_indices:
            atom = molecule.GetAtomWithIdx(atom_idx)
            if not _is_sp_or_sp2(atom):
                continue
            pi_set.add(atom_idx)
            for neighbor in atom.GetNeighbors():
                if _is_sp_or_sp2(neighbor):
                    pi_set.add(neighbor.GetIdx())
            if atom.GetAtomMapNum() > 0:
                flagged_atom_maps.add(atom.GetAtomMapNum())
        return pi_set

    # Process reactants
    for i in range(reaction.GetNumReactantTemplates()):
        molecule = reaction.GetReactantTemplate(i)
        pi_set = process_molecule(molecule, current_pi_indices[0][i])
        new_pi_indices[0].append(pi_set)

    # Process products
    for i in range(reaction.GetNumProductTemplates()):
        molecule = reaction.GetProductTemplate(i)
        pi_set = process_molecule(molecule, current_pi_indices[1][i])
        new_pi_indices[1].append(pi_set)

    # Include flagged atoms based on atom map values
    def include_flagged_atoms(molecule, pi_set):
        for atom in molecule.GetAtoms():
            if atom.GetAtomMapNum() in flagged_atom_maps:
                pi_set.add(atom.GetIdx())

    for i in range(reaction.GetNumReactantTemplates()):
        molecule = reaction.GetReactantTemplate(i)
        include_flagged_atoms(molecule, new_pi_indices[0][i])

    for i in range(reaction.GetNumProductTemplates()):
        molecule = reaction.GetProductTemplate(i)
        include_flagged_atoms(molecule, new_pi_indices[1][i])

    # Check if the new pi indices are the same as the current ones
    if sorted([sorted(list(s)) for s in new_pi_indices[0]]) == sorted([sorted(list(s)) for s in current_pi_indices[0]]) and \
       sorted([sorted(list(s)) for s in new_pi_indices[1]]) == sorted([sorted(list(s)) for s in current_pi_indices[1]]):
        return new_pi_indices
    else:
        return _grow_pi_shell(reaction, new_pi_indices)

# Function to augment pi atom indices with conjugated atoms
# JCA Note:  I'm not sure this step is needed, though ChatGPT thinks it is.
def _augment_pi_indices(molecule, pi_atom_indices):
    for atom in molecule.GetAtoms():
        atom_idx = atom.GetIdx()
        if atom_idx in pi_atom_indices:
            for neighbor in atom.GetNeighbors():
                if _is_sp_or_sp2(neighbor):
                    pi_atom_indices.add(neighbor.GetIdx())
    return pi_atom_indices

# Function to process a molecule and identify unmapped hydrogen and heavy atom indices
def _process_unmapped_atoms(molecule):
    unmapped_hydrogen_indices = set()
    unmapped_heavy_indices = set()
    for atom in molecule.GetAtoms():
        atom_map = atom.GetAtomMapNum()
        if atom_map != 0:
            continue
        atomic_number = atom.GetAtomicNum()
        if atomic_number == 1 or atomic_number == 85:
            unmapped_hydrogen_indices.add(atom.GetIdx())
        else:
            unmapped_heavy_indices.add(atom.GetIdx())
    return unmapped_hydrogen_indices, unmapped_heavy_indices

# Main function to process the reaction
def extract_operator(smirks: str, include_stereochemistry: bool = False, include_sigma: bool = True, include_pi: bool = True, include_unmapped_hydrogens: bool = True, include_unmapped_heavy_atoms: bool = True, include_static_hydrogens: bool = False):

    # ==================================================================
    #                   REACTION STEREOCHEMISTRY AND PREP
    # ==================================================================

    # Parse the reaction SMARTS
    reaction = rdChemReactions.ReactionFromSmarts(smirks)

    # Remove stereochemistry if requested
    if not include_stereochemistry:
        # print("Removing Stereochemistry")

        # Create a new reaction object
        new_reaction = rdChemReactions.ChemicalReaction()

        # Process reactants
        for i in range(reaction.GetNumReactantTemplates()):
            reactant = reaction.GetReactantTemplate(i)
            reactant = _remove_stereochemistry(reactant)
            new_reaction.AddReactantTemplate(reactant)

        # Process products
        for i in range(reaction.GetNumProductTemplates()):
            product = reaction.GetProductTemplate(i)
            product = _remove_stereochemistry(product)
            new_reaction.AddProductTemplate(product)

        smirks = rdChemReactions.ReactionToSmarts(new_reaction)
        reaction = rdChemReactions.ReactionFromSmarts(smirks)

    # Do some cleanup and internal calculation
    reaction.Initialize()

    # ==================================================================
    #                       LABEL AND COLLECT ATOMS SETS
    # ==================================================================

    # ---------------------- POPULATE CENTER ATOMS ---------------------
    # Identify reacting mapped atoms using our custom method
    reacting_atoms = _identify_changed_mapped_atoms(reaction)
    
    # Identify the atom maps of the reacting mapped atoms
    center_atom_maps = set()
    for i, atom_indices in enumerate(reacting_atoms):
        reactant = reaction.GetReactantTemplate(i)
        for atom_idx in atom_indices:
            atom = reactant.GetAtomWithIdx(atom_idx)
            atom_map = atom.GetAtomMapNum()
            center_atom_maps.add(atom_map)

    # Create a tuple of lists of sets called center_atom_indices
    center_atom_indices = ([], [])

    # Iterate through reactants and add to the first list in the tuple
    for i in range(reaction.GetNumReactantTemplates()):
        reactant = reaction.GetReactantTemplate(i)
        center_atom_indices[0].append(_extract_center_atom_indices(reactant, center_atom_maps))

    # Iterate through products and add to the second list in the tuple
    for i in range(reaction.GetNumProductTemplates()):
        product = reaction.GetProductTemplate(i)
        center_atom_indices[1].append(_extract_center_atom_indices(product, center_atom_maps))

    # Augment center_atom_indices with unmapped-and-adjacent atoms for reactants
    for i in range(reaction.GetNumReactantTemplates()):
        reactant = reaction.GetReactantTemplate(i)
        for atom_idx in reacting_atoms[i]:
            atom = reactant.GetAtomWithIdx(atom_idx)
            for neighbor in atom.GetNeighbors():
                if neighbor.GetAtomMapNum() == 0:
                    center_atom_indices[0][i].add(neighbor.GetIdx())

    # Augment center_atom_indices with unmapped-and-adjacent atoms for products
    for i in range(reaction.GetNumProductTemplates()):
        product = reaction.GetProductTemplate(i)
        for atom in product.GetAtoms():
            atom_map = atom.GetAtomMapNum()
            if atom_map in center_atom_maps:
                for neighbor in atom.GetNeighbors():
                    if neighbor.GetAtomMapNum() == 0:
                        center_atom_indices[1][i].add(neighbor.GetIdx())

    # Print the final center_atom_indices for reactants and products
    # print("Final Center Atom Indices Reactants:", [list(indices) for indices in center_atom_indices[0]])
    # print("Final Center Atom Indices Products:", [list(indices) for indices in center_atom_indices[1]])

    # ic(center_atom_indices)

    # ---------------------- POPULATE SIGMA-BONDED ATOMS ---------------------
    # Create a tuple of lists of sets called sigma_atom_indices
    sigma_atom_indices = ([], [])

    # Iterate through reactants and add to the first list in the tuple
    for i in range(reaction.GetNumReactantTemplates()):
        reactant = reaction.GetReactantTemplate(i)
        sigma_atom_indices[0].append(_process_sigma_molecule(reactant, center_atom_indices[0][i]))

    # Iterate through products and add to the second list in the tuple
    for i in range(reaction.GetNumProductTemplates()):
        product = reaction.GetProductTemplate(i)
        sigma_atom_indices[1].append(_process_sigma_molecule(product, center_atom_indices[1][i]))

    # Print the final sigma_atom_indices for reactants and products
    # print("Sigma Atom Indices Reactants:", [list(indices) for indices in sigma_atom_indices[0]])
    # print("Sigma Atom Indices Products:", [list(indices) for indices in sigma_atom_indices[1]])

    # ---------------------- POPULATE PI-BONDED ATOMS ---------------------
    # Grow the pi shell until it no longer changes
    pi_atom_indices = _grow_pi_shell(reaction, center_atom_indices)

    # Display the pi_atom_indices
    # print("Pi Atom Indices:", pi_atom_indices)

    # Process reactants and products to augment pi_atom_indices
    for i in range(reaction.GetNumReactantTemplates()):
        reactant = reaction.GetReactantTemplate(i)
        pi_atom_indices[0][i] = _augment_pi_indices(reactant, pi_atom_indices[0][i])

    for i in range(reaction.GetNumProductTemplates()):
        product = reaction.GetProductTemplate(i)
        pi_atom_indices[1][i] = _augment_pi_indices(product, pi_atom_indices[1][i])

    # Print the final pi_atom_indices for reactants and products
    # print("Final Pi Atom Indices Reactants:", [list(indices) for indices in pi_atom_indices[0]])
    # print("Final Pi Atom Indices Products:", [list(indices) for indices in pi_atom_indices[1]])

    # ---------------------- POPULATE UNMAPPED ATOMS ---------------------
    # Initialize unmapped_hydrogen_indices and unmapped_heavy_indices with the same structure as pi_atom_indices
    unmapped_hydrogen_indices = ([], [])
    unmapped_heavy_indices = ([], [])

    # Iterate through reactants and add to the first list in the tuples
    for i in range(reaction.GetNumReactantTemplates()):
        reactant = reaction.GetReactantTemplate(i)
        hydrogen_indices, heavy_indices = _process_unmapped_atoms(reactant)
        unmapped_hydrogen_indices[0].append(hydrogen_indices)
        unmapped_heavy_indices[0].append(heavy_indices)

    # Iterate through products and add to the second list in the tuples
    for i in range(reaction.GetNumProductTemplates()):
        product = reaction.GetProductTemplate(i)
        hydrogen_indices, heavy_indices = _process_unmapped_atoms(product)
        unmapped_hydrogen_indices[1].append(hydrogen_indices)
        unmapped_heavy_indices[1].append(heavy_indices)

    # Display the final unmapped_hydrogen_indices and unmapped_heavy_indices
    # ic(unmapped_hydrogen_indices)
    # ic(unmapped_heavy_indices)

    # ---------------------- POPULATE STATIC HYDROGENS ---------------------
    # Initialize static_hydrogen_indices with the same structure as other indices lists
    static_hydrogen_indices = ([], [])

    # Iterate through reactants and add to the first list in the tuples
    for i in range(reaction.GetNumReactantTemplates()):
        reactant = reaction.GetReactantTemplate(i)
        static_hydrogens = _process_static_hydrogens(reactant, center_atom_indices[0][i])
        static_hydrogen_indices[0].append(static_hydrogens)

    # Iterate through products and add to the second list in the tuples
    for i in range(reaction.GetNumProductTemplates()):
        product = reaction.GetProductTemplate(i)
        static_hydrogens = _process_static_hydrogens(product, center_atom_indices[1][i])
        static_hydrogen_indices[1].append(static_hydrogens)

    # Display the final static_hydrogen_indices
    # ic(static_hydrogen_indices)

    # ==================================================================
    #                       EXTRACT THE OPERATOR
    # ==================================================================

    # Start by duplicating center_atom_indices as keep_atom_indices
    keep_atom_indices = ([], [])

    for i in range(len(center_atom_indices[0])):
        keep_atom_indices[0].append(set(center_atom_indices[0][i]))

    for i in range(len(center_atom_indices[1])):
        keep_atom_indices[1].append(set(center_atom_indices[1][i]))

    # Add or remove indices according to the logic
    if include_sigma:
        for i in range(len(sigma_atom_indices[0])):
            keep_atom_indices[0][i].update(sigma_atom_indices[0][i])
        for i in range(len(sigma_atom_indices[1])):
            keep_atom_indices[1][i].update(sigma_atom_indices[1][i])

    if include_pi:
        for i in range(len(pi_atom_indices[0])):
            keep_atom_indices[0][i].update(pi_atom_indices[0][i])
        for i in range(len(pi_atom_indices[1])):
            keep_atom_indices[1][i].update(pi_atom_indices[1][i])

    if include_unmapped_hydrogens:
        for i in range(len(unmapped_hydrogen_indices[0])):
            keep_atom_indices[0][i].update(unmapped_hydrogen_indices[0][i])
        for i in range(len(unmapped_hydrogen_indices[1])):
            keep_atom_indices[1][i].update(unmapped_hydrogen_indices[1][i])

    if include_unmapped_heavy_atoms:
        for i in range(len(unmapped_heavy_indices[0])):
            keep_atom_indices[0][i].update(unmapped_heavy_indices[0][i])
        for i in range(len(unmapped_heavy_indices[1])):
            keep_atom_indices[1][i].update(unmapped_heavy_indices[1][i])

    if not include_static_hydrogens:
        for i in range(len(static_hydrogen_indices[0])):
            keep_atom_indices[0][i].difference_update(static_hydrogen_indices[0][i])
        for i in range(len(static_hydrogen_indices[1])):
            keep_atom_indices[1][i].difference_update(static_hydrogen_indices[1][i])

    # Create remove_bond_indices and remove_atom_indices
    remove_bond_indices = ([], [])
    remove_atom_indices = ([], [])

    # Process reactants
    for i in range(reaction.GetNumReactantTemplates()):
        reactant = reaction.GetReactantTemplate(i)
        bond_indices_set = set()
        atom_indices_set = set()
        for atom in reactant.GetAtoms():
            if atom.GetIdx() not in keep_atom_indices[0][i]:
                atom_indices_set.add(atom.GetIdx())
                for bond in atom.GetBonds():
                    bond_indices_set.add(bond.GetIdx())
        remove_bond_indices[0].append(bond_indices_set)
        remove_atom_indices[0].append(atom_indices_set)

    # Process products
    for i in range(reaction.GetNumProductTemplates()):
        product = reaction.GetProductTemplate(i)
        bond_indices_set = set()
        atom_indices_set = set()
        for atom in product.GetAtoms():
            if atom.GetIdx() not in keep_atom_indices[1][i]:
                atom_indices_set.add(atom.GetIdx())
                for bond in atom.GetBonds():
                    bond_indices_set.add(bond.GetIdx())
        remove_bond_indices[1].append(bond_indices_set)
        remove_atom_indices[1].append(atom_indices_set)

    # Remove bonds and atoms from the reaction
    new_reaction = rdChemReactions.ChemicalReaction()

    # Process reactants
    for i in range(reaction.GetNumReactantTemplates()):
        reactant = reaction.GetReactantTemplate(i)
        editable_reactant = Chem.EditableMol(reactant)
        for bond_idx in remove_bond_indices[0][i]:
            bond = reactant.GetBondWithIdx(bond_idx)
            editable_reactant.RemoveBond(bond.GetBeginAtomIdx(), bond.GetEndAtomIdx())
        for atom_idx in sorted(remove_atom_indices[0][i], reverse=True):
            editable_reactant.RemoveAtom(atom_idx)
        new_reaction.AddReactantTemplate(editable_reactant.GetMol())

    # Process products
    for i in range(reaction.GetNumProductTemplates()):
        product = reaction.GetProductTemplate(i)
        editable_product = Chem.EditableMol(product)
        for bond_idx in remove_bond_indices[1][i]:
            bond = product.GetBondWithIdx(bond_idx)
            editable_product.RemoveBond(bond.GetBeginAtomIdx(), bond.GetEndAtomIdx())
        for atom_idx in sorted(remove_atom_indices[1][i], reverse=True):
            editable_product.RemoveAtom(atom_idx)
        new_reaction.AddProductTemplate(editable_product.GetMol())

    # Convert to SMIRKS
    smirks = rdChemReactions.ReactionToSmarts(new_reaction)
    return smirks


# Helper function to identify changed mapped atoms between reactants and products
# Returns (reactants, products) tuple of lists of sets of atom indices (matching original GetReactingAtoms behavior)
def _identify_changed_mapped_atoms(reaction):
    def get_atom_signature(atom):
        signature = {
            'neighbors': set(),
            'chirality': atom.GetChiralTag().name
        }
        for bond in atom.GetBonds():
            neighbor = bond.GetOtherAtom(atom)
            neighbor_atomic_num = neighbor.GetAtomicNum()
            neighbor_atom_map = neighbor.GetAtomMapNum()
            # bond_order = bond.GetBondTypeAsDouble()
            signature['neighbors'].add((neighbor_atomic_num, neighbor_atom_map))
        return signature

    def build_signature_dict(molecule):
        signature_dict = {}
        for atom in molecule.GetAtoms():
            atom_map = atom.GetAtomMapNum()
            if atom_map > 0:
                signature_dict[atom_map] = get_atom_signature(atom)
        return signature_dict

    # Build signature dicts
    reactant_signatures = {}
    for i in range(reaction.GetNumReactantTemplates()):
        molecule = reaction.GetReactantTemplate(i)
        sigs = build_signature_dict(molecule)
        reactant_signatures.update(sigs)

    product_signatures = {}
    for i in range(reaction.GetNumProductTemplates()):
        molecule = reaction.GetProductTemplate(i)
        sigs = build_signature_dict(molecule)
        product_signatures.update(sigs)

    # Compare signatures
    changed_atom_maps = set()
    all_atom_maps = set(reactant_signatures.keys()).union(product_signatures.keys())
    for atom_map in all_atom_maps:
        react_sig = reactant_signatures.get(atom_map)
        prod_sig = product_signatures.get(atom_map)
        if react_sig != prod_sig:
            # print(f"Changed atom map: {atom_map}")
            # print(f"  Reactant signature: {react_sig}")
            # print(f"  Product signature:  {prod_sig}")
            changed_atom_maps.add(atom_map)

    # Now return reacting_atoms = (reactants, products), in the same format as before
    reacting_atoms = ([], [])

    # Reactants
    for i in range(reaction.GetNumReactantTemplates()):
        molecule = reaction.GetReactantTemplate(i)
        index_set = set()
        for atom in molecule.GetAtoms():
            # print(f"Reactant {i}: Atom index {atom.GetIdx()} has atom map {atom.GetAtomMapNum()}")
            if atom.GetAtomMapNum() in changed_atom_maps:
                index_set.add(atom.GetIdx())
        reacting_atoms[0].append(index_set)

    # Products
    for i in range(reaction.GetNumProductTemplates()):
        molecule = reaction.GetProductTemplate(i)
        index_set = set()
        for atom in molecule.GetAtoms():
            # print(f"Product {i}: Atom index {atom.GetIdx()} has atom map {atom.GetAtomMapNum()}")
            if atom.GetAtomMapNum() in changed_atom_maps:
                index_set.add(atom.GetIdx())
        reacting_atoms[1].append(index_set)

    # print(reacting_atoms)

    return reacting_atoms[0]
