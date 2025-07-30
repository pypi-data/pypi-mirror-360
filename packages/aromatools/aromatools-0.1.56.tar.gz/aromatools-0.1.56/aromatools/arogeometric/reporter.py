import pandas as pd
from aromatools.arogeometric.arogeometric import build_graph, compute_index, get_3Dgraph

class AtomsReporter:
    def __init__(self, mol, index_type: str, name: str):
        self.index_type = index_type.upper()
        self.name = name
        atoms_list = []
        for atom in mol:
            symbol = atom.symbol.capitalize()
            if symbol == 'H':
                continue
            x, y, z = atom.position
            atoms_list.append((symbol, x, y, z))
        self._graph = build_graph(atoms_list)
        rings, ring_indices_list, df_index = compute_index(self._graph, atoms_list, self.index_type)
        self._df = df_index
        ring_idx_dict = dict(ring_indices_list)
        self._fig = get_3Dgraph(self._graph, atoms_list, rings, ring_idx_dict, title=self.name)

    def df(self) -> pd.DataFrame:
        return self._df

    def fig(self):
        return self._fig
