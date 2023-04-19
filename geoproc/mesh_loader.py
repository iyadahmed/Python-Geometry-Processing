from typing import BinaryIO, Tuple
from pathlib import Path
from struct import Struct
import os


FLOAT32_STRUCT = Struct("<f")
UINT16_STRUCT = Struct("<H")


def read_bytes(file: BinaryIO, n: int):
    data = file.read(n)
    assert len(data) == n
    return data


def write_bytes(file: BinaryIO, data: bytes):
    assert file.write(data) == len(data)


def read_uint32(file: BinaryIO):
    data = read_bytes(file, 4)
    return int.from_bytes(data, "little", signed=False)


def write_uint32(file: BinaryIO, value: int):
    data = value.to_bytes(4, "little", signed=False)
    write_bytes(file, data)


def read_float32(file: BinaryIO) -> float:
    return FLOAT32_STRUCT.unpack(read_bytes(file, 4))[0]


def write_float32(file: BinaryIO, value: float):
    write_bytes(file, FLOAT32_STRUCT.pack(value))


def read_uint16(file: BinaryIO):
    return UINT16_STRUCT.unpack(read_bytes(file, 2))[0]


def write_zeros(file: BinaryIO, n: int):
    write_bytes(file, b"0" * n)


def iter_binary_stl_mesh_triangles(filepath: Path | str):
    with open(filepath, "rb") as file:
        file.seek(80, os.SEEK_CUR)  # Skip header

        num_tris = read_uint32(file)

        for _ in range(num_tris):
            file.seek(4 * 3, os.SEEK_CUR)  # Skip normal vector
            yield ((read_float32(file) for i in range(3)) for j in range(3))
            file.seek(2, os.SEEK_CUR)  # Skip "attribute byte count"


class BinarySTLMeshWriter:
    def __init__(self, filepath: Path | str):
        self._num_tris = 0
        self._file = open(filepath, "wb")

        write_zeros(self._file, 80)  # Write header

        # Write number of triangles, we should update it later
        write_uint32(self._file, 0)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self._file.seek(80, os.SEEK_SET)
        write_uint32(self._file, self._num_tris)
        self._file.close()

    def write_triangle(
        self,
        vertices: Tuple[
            Tuple[float, float, float],
            Tuple[float, float, float],
            Tuple[float, float, float],
        ],
    ):
        write_zeros(self._file, 4 * 3)  # Write normal vector

        # Write vertices
        for vertex in vertices:
            for value in vertex:
                write_float32(self._file, value)

        write_zeros(self._file, 2)  # Write "attribute byte count"

        self._num_tris += 1
