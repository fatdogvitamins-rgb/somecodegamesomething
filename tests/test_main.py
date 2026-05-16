import unittest

from main import spin_entity


class FakeEntity:
    def __init__(self):
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0


class SpinEntityTests(unittest.TestCase):
    def test_spin_entity_rotates_each_axis(self):
        cube = FakeEntity()

        spin_entity(cube, 2)

        self.assertEqual(cube.rotation_x, 2)
        self.assertEqual(cube.rotation_y, 2)
        self.assertEqual(cube.rotation_z, 2)


if __name__ == "__main__":
    unittest.main()
