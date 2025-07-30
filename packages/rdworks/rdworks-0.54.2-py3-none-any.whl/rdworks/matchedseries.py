import os
import pathlib
import copy
import operator
from collections import defaultdict
from typing import List, Tuple, Union, Iterator

from rdkit import Chem, Geometry
from rdkit.Chem import Draw, AllChem, rdMMPA

from .mol import Mol, rd_descriptor, rd_descriptor_f
from .mollibr import MolLibr


class MatchedSeries:
    def __init__(self, 
                 mollibr:MolLibr,
                 sort_props:Union[List,str,None]=None,
                 core_min:int=5, core_max:int=30, size_min:int=3) -> None :
        """Initialize.

        Documented here: [MMS with rdkit](https://iwatobipen.wordpress.com/2016/02/01/create-matched-molecular-series-with-rdkit/),
        [Mishima-syk](https://github.com/Mishima-syk/py4chemoinformatics/blob/master/ch07_graph.asciidoc), 
        and [rdkit docs](http://rdkit.org/docs/source/rdkit.Chem.rdMMPA.html).            

        Examples:
            >>> import rdworks
            >>> libr = rdworks.read_smi('test.smi')
            >>> series = rdworks.MatchedSeries(libr)
        
        Args:
            mollibr (MolLibr): a library of molecules.
            sort_props (Union[List,str,None], optional): how to sort molecules within a series. Defaults to None.
            core_min (int, optional): min number of atoms for a core. Defaults to 5.
            core_max (int, optional): max number of atoms for a core. Defaults to 30.
            size_min (int, optional): min number of molecules for a series. Defaults to 3.

        Raises:
            TypeError: if `mollibr` is not rdworks.MolLibr object.
        """
        if isinstance(mollibr, MolLibr):
            self.mollibr = copy.deepcopy(mollibr) # a copy of MolLibr
        else:
            raise TypeError('MatchedSeries() expects rdworks.MolLibr object')
        if isinstance(sort_props, list):
            self.sort_props = sort_props
        elif isinstance(sort_props, str):
            self.sort_props = [ sort_props ]
        else:
            self.sort_props = [ 'HAC' ]
        self.core_min = core_min
        self.core_max = core_max
        self.size_min = size_min # minimum numer of R-groups in a series
        # for consistent drawing
        self.template_pattern = None
        self.template_coord2D = None
        self.series = self.libr_to_series() 
        
        
    def __str__(self) -> str:
        """Returns a string representation of object.

        Returns:
            str: string representation.
        """
        return f"<rdworks.MatchedSeries({self.count()})>"
    

    def __iter__(self) -> Iterator:
        """Yields an iterator of molecules.

        Yields:
            Iterator: iterator of molecules.
        """
        return iter(self.series)
    
    
    def __next__(self) -> Tuple:
        """Next series.

        Returns:
            Tuple: (scaffold_SMILES, [(r-group_SMILES, rdworks.Mol, *sort_props_values)
        """
        return next(self.series)
    

    def __getitem__(self, index:Union[int,slice]) -> Tuple:
        """Operator `[]`.

        Args:
            index (Union[int,slice]): index or indexes.

        Raises:
            ValueError: if series is empty or index is out of range.

        Returns:
            Tuple: (scaffold_SMILES, [(r-group_SMILES, rdworks.Mol, *sort_props_values)
        """
        if self.count() == 0:
            raise ValueError(f"MatchedSeries is empty")
        try:
            return self.series[index]
        except:
            raise ValueError(f"index should be 0..{self.count()-1}")
        

    def count(self) -> int:
        """Returns the count of series.

        Returns:
            int: count of series.
        """
        return len(self.series)
    

    def libr_to_series(self) -> List[Tuple]:
        """Returns a list of molecular series.

        Raises:
            RuntimeError: if a molecular cut cannot be defined.

        Returns:
            List[Tuple]: 
                [
                (scaffold_SMILES, [(r-group_SMILES, rdworks.Mol, *sort_props_values), ...,]),  
                ...,
                ]
        """
        series = defaultdict(list)
        for mol in self.mollibr:
            # make a single cut
            list_of_frag = rdMMPA.FragmentMol(mol.rdmol, maxCuts=1, resultsAsMols=False)
            # note: default parameters: maxCuts=3, maxCutBonds=20, resultsAsMols=True
            for _, cut in list_of_frag:
                try:
                    frag_smiles_1, frag_smiles_2 = cut.split('.')
                except:
                    raise RuntimeError(f'{mol.name} fragment_tuple= {cut}')
                n1 = Chem.MolFromSmiles(frag_smiles_1).GetNumHeavyAtoms()
                n2 = Chem.MolFromSmiles(frag_smiles_2).GetNumHeavyAtoms()
                # split scaffold core and rgroup symmetrically
                if n1 >= self.core_min and n1 <= self.core_max and n1 > n2: 
                    # frag_1 is the scaffold and frag_2 is the rgroup
                    series[frag_smiles_1].append((frag_smiles_2, mol))
                if n2 >= self.core_min and n2 <= self.core_max and n2 > n1: 
                    # frag_2 is the scaffold and frag_1 is the rgroup
                    series[frag_smiles_2].append((frag_smiles_1, mol))    
        # convert dict to list and remove size < self.size_min
        series = [(k,v) for k,v in series.items() if len(v) >= self.size_min]
        # sort by size (from the largest to the smallest)
        series = sorted(series, key=lambda x: len(x[1]), reverse=True)
        # sort by self.sort_props
        series_r_group_sorted = []
        for (scaffold_smi, r_group_) in series:
            r_group = []
            for (r_smi, mol) in r_group_:
                values = []
                for p in self.sort_props:
                    try:
                        v = mol.props[p]
                    except:
                        if p in rd_descriptor_f:
                            v = rd_descriptor_f[p](mol.rdmol) # calc. on the fly
                            mol.props.update({p:v})
                        else:
                            v = None
                    values.append(v)
                r_group.append((r_smi, mol, *values)) # unpack values i.e. a=[2,3] b=(1,*a) == (1,2,3)
            r_group = sorted(r_group, key=operator.itemgetter(slice(2, 2+len(self.sort_props))))
            series_r_group_sorted.append((scaffold_smi, r_group))
        return series_r_group_sorted
    

    def template(self, SMARTS:str, rdmol:Chem.Mol) -> None:
        """Sets drawing layout template.

        Args:
            SMARTS (str): SMARTS for template pattern.
            rdmol (Chem.Mol): template molecule.
        """
        
        self.template_pattern = Chem.MolFromSmarts(SMARTS)
        matched = rdmol.GetSubstructMatch(self.template_pattern)
        coords = [rdmol.GetConformer().GetAtomPosition(x) for x in matched]
        self.template_coords2D = [Geometry.Point2D(pt.x, pt.y) for pt in coords]


    def depict(self, smiles:str) -> Chem.Mol:
        """Draws a molecule according to self.template in a consistent way.

        Args:
            smiles (str): input molecule.

        Returns:
            Chem.Mol: 2D coordinated Chem.Mol for depiction.
        """
        rdmol_2d = Chem.MolFromSmiles(smiles)
        try:
            matched = rdmol_2d.GetSubstructMatch(self.template_pattern)
            coordDict = {}
            for i, coord in enumerate(self.template_coords2D):
                coordDict[matched[i]] = coord
            AllChem.Compute2DCoords(rdmol_2d, coordMap=coordDict)
        except:
            pass
        return rdmol_2d


    def report(self,
               workdir:os.PathLike=pathlib.Path("."),
               prefix:str="mmseries",
               mols_per_row:int=8,
               width:int=200,
               height:int=200,
               max_mols:int=200, 
               use_svg:bool=True) -> None:
        """Plots individual series and an overview of series.

        Args:
            workdir (os.PathLike, optional): working directory. Defaults to pathlib.Path(".").
            prefix (str, optional): prefix of output files. Defaults to "mmseries".
            mols_per_row (int, optional): number of molecules per row. Defaults to 8.
            width (int, optional): width. Defaults to 200.
            height (int, optional): height. Defaults to 200.
            max_mols (int, optional): max number of molecules. Defaults to 200.
            use_svg (bool, optional): whether to use SVG format. Defaults to True.
        """
        scaffold_mols = []
        scaffold_legends = []
        for idx, (scaffold_smiles, list_tuples_r_groups) in enumerate(self.series, start=1):
            num = len(list_tuples_r_groups)
            scaffold_mols.append(Chem.MolFromSmiles(scaffold_smiles))
            scaffold_legends.append(f'Series #{idx} (n={num})')
            r_group_mols = []
            r_group_legends = []
            for (r_group_smiles, m, *values) in list_tuples_r_groups:
                # (r-group_SMILES, rdworks.Mol, *sort_props_values)
                values = list(map(str, values))
                r_group_mols.append(Chem.MolFromSmiles(r_group_smiles))
                r_group_legends.append(f'{m.name}\n{",".join(values)}')
            
            # plot individual series
            with open(workdir / f"{prefix}-{idx:03d}-count-{num:03d}.svg", "w") as svg:
                mols = scaffold_mols[-1:] + r_group_mols
                legends = scaffold_legends[-1:] + r_group_legends
                img = Draw.MolsToGridImage(mols,
                    molsPerRow=mols_per_row,
                    subImgSize=(width, height),
                    legends=legends,
                    useSVG=use_svg)
                svg.write(img)

        # plot overview
        with open(workdir / f"{prefix}-overview.svg", "w") as svg:
            img = Draw.MolsToGridImage(scaffold_mols, 
                molsPerRow=mols_per_row, 
                subImgSize=(width, height),
                legends=scaffold_legends,
                useSVG=use_svg)
            svg.write(img)
