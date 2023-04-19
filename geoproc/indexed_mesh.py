from dataclasses import dataclass
from pathlib import Path
from typing import Hashable

from geoproc.mesh_loader import iter_binary_stl_mesh_triangles


class IndexHashMap:
    def __init__(self) -> None:
        self._map: dict[Hashable, int] = dict()

    def insert(self, key: Hashable):
        return self._map.setdefault(key, len(self._map.keys()))

    def computeInverseMap(self):
        return dict(zip(self._map.values(), self._map.keys()))


@dataclass
class IndexedMesh:
    tris: set[frozenset[int]]
    verts: dict[int, frozenset[float]]


def create_indexed_mesh_from_stl_mesh_file(filepath: Path | str):
    unique_verts = IndexHashMap()
    unique_tris: set[frozenset[int]] = set()

    for tri in iter_binary_stl_mesh_triangles(filepath):
        utri = frozenset(unique_verts.insert(frozenset(vertex_pos)) for vertex_pos in tri)
        unique_tris.add(utri)

    return IndexedMesh(unique_tris, unique_verts.computeInverseMap())
