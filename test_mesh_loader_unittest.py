from pathlib import Path
import unittest

from mesh_loader import BinarySTLMeshWriter, iter_binary_stl_mesh_triangles


class TestMeshLoader(unittest.TestCase):
    def setUp(self) -> None:
        self.TEST_STL_FILEPATH = Path(__file__).parent / "test.stl"

    def test_import_export_roundtrip(self):
        vertices1 = []
        with BinarySTLMeshWriter(self.TEST_STL_FILEPATH) as writer:
            for tri in iter_binary_stl_mesh_triangles(
                Path(__file__).parent / "suzanne.stl"
            ):
                tri_verts = tuple(tuple(value for value in vertex) for vertex in tri)
                vertices1.extend(tri_verts)
                writer.write_triangle(tri_verts)

        vertices2 = []
        for tri in iter_binary_stl_mesh_triangles(self.TEST_STL_FILEPATH):
            vertices2.extend(tuple(tuple(value for value in vertex) for vertex in tri))

        self.assertEqual(vertices1, vertices2)

    def tearDown(self) -> None:
        self.TEST_STL_FILEPATH.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
