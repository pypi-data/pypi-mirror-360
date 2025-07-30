"""This module is an implementation in progress of the decision tree method for pKa prediction.

Crippen, J. Chem. Inf. Model., Vol. 48, No. 10, 2008, 2042-2053.

The SMARTS patterns and pKa values were taken from the supporting information of the paper.
These "MOE SMARTS" were converted to generic SMARTS which relied on use of some recursive SMARTS patterns.  
The first data row then describes nodes 1, and then the tree expands out based on decisions of SMARTS-matching:
    if node 2 is yes to pattern [#8,#16,#34,#52,#84;H]C(=O) - giving pKa 3.68 and range 5.96
    node 3 is no to the same pattern - giving pKa 7.21 and range 17.32
Then nodes 4,5 are under 2 and 6,7 are under 3, etc, etc until the leaf nodes are reached
"""


import importlib.resources
from collections import namedtuple
from typing import Union

from rdkit import Chem
from rdkit.Chem import AllChem

datadir = importlib.resources.files('rdworks.predefined')
DecisionTreeNode = namedtuple('DecisionTree', ('node', 'parent', 'child', 'FP', 'SMARTS', 'YN', 'pKa', 'pKa_range'))
decision_tree = []
with open(datadir / "pKa_decision_tree.ext", "r") as f: 
    for line in f:
        if (not line) or line.startswith('#'):
            continue
        decision_tree.append(DecisionTreeNode(line.strip().split()))
        

def decision_tree_pKa(rdmol:Chem.Mol) -> Union[float, None]:
    pKa = None
    for _ in decision_tree:
        patt = Chem.MolFromSmarts(_.SMARTS) # make an RDKit query molecule
        match = rdmol.HasSubstructMatch(patt) # check if we have a match for our test molecule
        # pKa = float(values[6])
        # pKa_range = float(values[7])
    return pKa