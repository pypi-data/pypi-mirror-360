
from rdworks.stereoisomers import enumerate_stereoisomers, enumerate_ring_bond_stereoisomers
from rdworks.mol import Mol
from rdworks.mollibr import MolLibr

from rdkit import Chem
from rdkit.Chem.MolStandardize import rdMolStandardize


def complete_stereoisomers(molecular_input: str | Chem.Mol | Mol, 
                           name: str | None = None, 
                           std: bool = False, 
                           override: bool = False, 
                           **kwargs) -> MolLibr:
    """Completes stereoisomers and returns a rdworks.MolLibr.

    Args:
        molecular_input (Union[Mol, str, Chem.Mol]): input molecule.
        name (Optional[str], optional): name of the molecule. Defaults to None.
        std (bool, optional): whether to standardize the input. Defaults to False.
        override (bool, optional): whether to override input stereoisomers. Defaults to False.

    Raises:
        TypeError: if `molecular_input` is not rdworks.Mol, SMILES, or rdkit.Chem.Mol object.

    Returns:
        MolLibr: a library of complete stereoisomers.
    """
    if isinstance(molecular_input, Mol):
        if name:
            mol = molecular_input.rename(name)
        else:
            mol = molecular_input
    elif isinstance(molecular_input, str) or isinstance(molecular_input, Chem.Mol):
        mol = Mol(molecular_input, name, std)
    else:
        raise TypeError('complete_stereoisomers() expects rdworks.Mol, SMILES or rdkit.Chem.Mol object')
    
    ring_bond_stereo_info = mol.get_ring_bond_stereo()
    
    if override:
        mol = mol.remove_stereo()
    
    rdmols = enumerate_stereoisomers(mol.rdmol)
    # ring bond stereo is not properly enumerated
    # cis/trans information is lost if stereochemistry is removed,
    # which cannot be enumerated by EnumerateStereoisomers() function
    # so enumerate_ring_bond_stereoisomers() is introduced
    if len(ring_bond_stereo_info) > 0:
        ring_cis_trans = []
        for rdmol in rdmols:
            ring_cis_trans += enumerate_ring_bond_stereoisomers(rdmol,
                                                     ring_bond_stereo_info,
                                                     override=override)
        if len(ring_cis_trans) > 0:
            rdmols = ring_cis_trans
    
    if len(rdmols) > 1:
        libr = MolLibr(rdmols).unique().rename(mol.name, sep='.').compute(**kwargs)
    else:
        libr = MolLibr(rdmols).rename(mol.name).compute(**kwargs)
    
    for _ in libr:
        _.props.update(mol.props)
    
    return libr



def complete_tautomers(mol: Mol, **kwargs) -> MolLibr:
    """Returns a library of enumerated tautomers.

    Args:
        mol (Mol): input molecule.

    Returns:
        MolLibr: a library of enumerated tautomers.
    """
    enumerator = rdMolStandardize.TautomerEnumerator()
    rdmols = list(enumerator.Enumerate(mol.rdmol))
    
    if len(rdmols) > 1: 
        return MolLibr(rdmols).unique().rename(mol.name, sep='.').compute(**kwargs)
    
    return MolLibr(rdmols).compute(**kwargs)