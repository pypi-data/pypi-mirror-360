import unittest
import numpy as np
import numpy.testing as npt
from src.stads.random_sampler import RandomSampler


class TestRandomSampler(unittest.TestCase):

    def test_basic_sampling_shape(self):
        sampler = RandomSampler((20, 20), "linear", 45)
        sampledPoints = sampler.get_coordinates()
        self.assertEqual(len(sampledPoints[0]), 180)

    def test_zero_samples(self):
        sampler = RandomSampler((100, 100), "linear", 0)
        sampledPoints = sampler.get_coordinates()
        npt.assert_array_equal(sampledPoints, np.empty((2, 0), dtype=np.int64))

    def test_maximum_samples_equal_to_pixels(self):
        height, width = 16, 16
        sampler = RandomSampler((height, width), "linear", 100)
        sampledPoints = sampler.get_coordinates()
        self.assertEqual(len(sampledPoints[0]), height * width)

    def test_invalid_negative_sample_count(self):
        with self.assertRaises(ValueError):
            RandomSampler((128, 128),"linear",  -5)

    def test_invalid_zero_shape(self):
        with self.assertRaises(ValueError):
            RandomSampler((0, 128), "linear", 10)
        with self.assertRaises(ValueError):
            RandomSampler((128, 0), "linear", 10)

    def test_invalid_over_sample(self):
        with self.assertRaises(ValueError):
            RandomSampler((10, 10), "linear", 101)


    def test_consistency_of_shape_parameter(self):
        # test several sizes
        for shape in [(1, 1), (5, 10), (40, 15), (1024, 1024)]:
            sampler = RandomSampler(shape, "linear", 10)
            sampledPoints = sampler.get_coordinates()
            for y, x in zip(sampledPoints[0], sampledPoints[1]):
                self.assertTrue(0 <= y < shape[0])
                self.assertTrue(0 <= x < shape[1])

    def test_sample_return_type(self):
        sampler = RandomSampler((100, 100), "linear", 5)
        sampledPoints = sampler.get_coordinates()

        self.assertIsInstance(sampledPoints, tuple)
        self.assertEqual(len(sampledPoints), 2)
        self.assertTrue(all(isinstance(arr, np.ndarray) for arr in sampledPoints))
        self.assertEqual(len(sampledPoints[0]), len(sampledPoints[1]))

    def test_duplicate_sampled_points_not_allowed(self):
        sampler = RandomSampler((10, 10), "linear", 50)
        yCoords, xCoords = sampler.get_coordinates()
        coords = list(zip(yCoords, xCoords))
        self.assertEqual(len(coords), len(set(coords)))


    def test_run_returns_image_with_correct_shape(self):
        imageShape = (1080,1080)
        sampler = RandomSampler(imageShape, "linear", 20)
        result,_,_ = sampler.run()
        self.assertEqual(result[0].shape, imageShape)

    def test_invalid_interpolation_method(self):
        with self.assertRaises(ValueError):
            RandomSampler((20, 20), "invalid_method", 10)

    def test_get_coordinates_returns_unique_points(self):
        sampler = RandomSampler((1080,1080), "linear", 25)
        yCoords, xCoords = sampler.get_coordinates()
        coords = list(zip(yCoords, xCoords))
        self.assertEqual(len(coords), len(set(coords)))


if __name__ == '__main__':
    unittest.main()
