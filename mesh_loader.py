from typing import BinaryIO
from pathlib import Path
from struct import Struct
import os

import numpy as np


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


def read_float32(file: BinaryIO):
    return FLOAT32_STRUCT.unpack(read_bytes(file, 4))[0]


def write_float32(file: BinaryIO, value: float):
    write_bytes(file, FLOAT32_STRUCT.pack(value))


def read_uint16(file: BinaryIO):
    return UINT16_STRUCT.unpack(read_bytes(file, 2))[0]


def write_zeros(file: BinaryIO, n: int):
    write_bytes(file, b"0" * n)


def read_stl_mesh(filepath: Path | str):
    with open(filepath, "rb") as file:
        file.seek(80, os.SEEK_CUR)  # Skip header

        num_tris = read_uint32(file)
        tris = np.empty((num_tris, 3, 3), dtype=np.float32)

        for tri_index in range(num_tris):
            file.seek(4 * 3, os.SEEK_CUR)  # Skip normal vector
            for i in range(3):
                for j in range(3):
                    tris[tri_index][i][j] = read_float32(file)
            file.seek(2, os.SEEK_CUR)  # Skip "attribute byte count"

        return tris


def write_stl_mesh(filepath: Path | str, tris: np.ndarray):
    with open(filepath, "wb") as file:
        write_zeros(file, 80)  # Write header

        num_tris = len(tris)
        write_uint32(file, num_tris)

        for tri_index in range(num_tris):
            write_zeros(file, 4 * 3)  # Write normal vector
            for i in range(3):
                for j in range(3):
                    write_float32(file, tris[tri_index][i][j])

            write_zeros(file, 2)  # Write "attribute byte count"
