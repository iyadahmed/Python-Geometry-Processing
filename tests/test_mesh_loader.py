from pathlib import Path

from geoproc.mesh_loader import BinarySTLMeshWriter, iter_binary_stl_mesh_triangles


def test_import_export_roundtrip():
    TEST_STL_FILEPATH = Path(__file__).parent / "test_import_export_roundtrip.stl"

    try:
        vertices1 = []
        with BinarySTLMeshWriter(TEST_STL_FILEPATH) as writer:
            for tri in iter_binary_stl_mesh_triangles(
                Path(__file__).parent / "suzanne.stl"
            ):
                tri_verts = tuple(tuple(value for value in vertex) for vertex in tri)
                vertices1.extend(tri_verts)
                writer.write_triangle(tri_verts)

        vertices2 = []
        for tri in iter_binary_stl_mesh_triangles(TEST_STL_FILEPATH):
            vertices2.extend(tuple(tuple(value for value in vertex) for vertex in tri))

        assert vertices1 == vertices2

    finally:
        TEST_STL_FILEPATH.unlink(missing_ok=True)
