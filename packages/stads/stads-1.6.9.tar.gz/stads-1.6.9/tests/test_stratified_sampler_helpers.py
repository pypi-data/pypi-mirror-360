import random
import unittest

import numpy as np

from src.stads.stratified_sampler_helpers import select_index, direct_child_buckets, deterministic_sample_counts, \
    non_deterministic_sample_counts, random_rejection_sampling
from src.stads.utility_functions import intersection_of_rectangles, calculate_number_of_samples_from_bucket, \
    calculate_area_fractions_of_buckets


class TestBucketIntersection(unittest.TestCase):

    def test_calculate_number_of_samples(self):
        self.assertEqual(calculate_number_of_samples_from_bucket(50, 50), 25)
        self.assertEqual(calculate_number_of_samples_from_bucket(1024 ** 2, 25), 262144)
        with self.assertRaises(ValueError):
            calculate_number_of_samples_from_bucket(50, 320)
            calculate_number_of_samples_from_bucket(0, 0)

    def test_intersection_of_rectangle(self):
        self.assertTrue(np.array_equal(intersection_of_rectangles(((0, 0), (10, 5)), ((0, 0), (7, 7))), ((0, 0), (7, 5))))
        self.assertTrue(np.array_equal(intersection_of_rectangles(((0, 0), (10, 5)), ((8, 0), (15, 7))), ((8, 0), (10, 5))))
        self.assertIsNone(intersection_of_rectangles(((0, 0), (10, 5)), ((0, 8), (7, 15))))
        self.assertIsNone(intersection_of_rectangles(((0, 0), (10, 5)), ((8, 8), (15, 15))))

    def test_direct_child_buckets(self):
        buckets = direct_child_buckets(((0, 0), (10, 5)))
        self.assertTrue(any(np.array_equal(bucket, ((0, 0), (7, 5))) for bucket in buckets))
        self.assertTrue(any(np.array_equal(bucket, ((8, 0), (10, 5))) for bucket in buckets))

        buckets = direct_child_buckets(((8, 4), (10, 5)))
        self.assertTrue(any(np.array_equal(bucket, ((8, 4), (9, 5))) for bucket in buckets))
        self.assertTrue(any(np.array_equal(bucket, ((10, 4), (10, 5))) for bucket in buckets))


    def test_area_fractions_of_buckets(self):
        area_fractions = calculate_area_fractions_of_buckets(
            (((0, 0), (7, 7)), ((8, 0), (15, 7)), ((0, 8), (7, 15)), ((8, 8), (15, 15))), ((0, 0), (15, 15)))
        self.assertAlmostEqual(area_fractions[0], 0.25)
        self.assertAlmostEqual(area_fractions[1], 0.25)
        self.assertAlmostEqual(area_fractions[2], 0.25)
        self.assertAlmostEqual(area_fractions[3], 0.25)

        area_fractions = calculate_area_fractions_of_buckets((((0, 0), (7, 7)), ((8, 0), (15, 7))), ((0, 0), (15, 7)))
        self.assertAlmostEqual(area_fractions[0], 0.5)
        self.assertAlmostEqual(area_fractions[1], 0.5)

        for i in range(10):
            x = random.randint(0, 100)
            y = random.randint(0, 100)
            width = random.randint(0, 100)
            height = random.randint(0, 100)
            parent = ((x, y), (x + width, y + height))
            area_fractions = calculate_area_fractions_of_buckets(direct_child_buckets(parent), parent)
            self.assertAlmostEqual(sum(area_fractions), 1.0)


    def test_deterministic_sample_counts_homogeneous(self):
        n_samples = deterministic_sample_counts((0.25, 0.25, 0.25, 0.25), 20)
        self.assertAlmostEqual(n_samples[0], 5.0)
        self.assertAlmostEqual(n_samples[1], 5.0)
        self.assertAlmostEqual(n_samples[2], 5.0)
        self.assertAlmostEqual(n_samples[3], 5.0)

        n_samples = deterministic_sample_counts((0.25, 0.25, 0.25, 0.25), 23)
        self.assertAlmostEqual(n_samples[0], 5.0)
        self.assertAlmostEqual(n_samples[1], 5.0)
        self.assertAlmostEqual(n_samples[2], 5.0)
        self.assertAlmostEqual(n_samples[3], 5.0)

    def test_number_of_deterministic_samples_non_homogeneous(self):
        n_samples = deterministic_sample_counts((0.8, 0.2), 20)
        self.assertEqual(n_samples[0], int(20 * 0.8))
        self.assertEqual(n_samples[1], int(20 * 0.2))


    def test_non_deterministic_sample_counts(self):
        n_samples = non_deterministic_sample_counts([1.0], 10)
        self.assertEqual(n_samples[0], 10)

        n_samples = non_deterministic_sample_counts([0.3, 0.3, 0.4], 0)
        self.assertEqual(n_samples[0], 0.0)
        self.assertEqual(n_samples[1], 0.0)
        self.assertEqual(n_samples[2], 0.0)

        probabilities = [1 / 1000] * 1000
        n_samples = non_deterministic_sample_counts(probabilities, 1000)
        self.assertEqual(sum(n_samples), 1000)
        self.assertTrue(all(x <= 2 for x in n_samples))

        with self.assertRaises(ValueError):
            non_deterministic_sample_counts([0.3, 0.3, 0.2], 34)
            non_deterministic_sample_counts([0.0, 0.0, 0.0], 34)
            non_deterministic_sample_counts([0.0], 46)

    def test_select_index(self):
        probabilities = [0.1, 0.8, 0.05, 0.05]
        self.assertEqual(select_index(probabilities, 0.08), 0)
        self.assertEqual(select_index(probabilities, 0.5), 1)
        self.assertEqual(select_index(probabilities, 0.99), 3)

        probabilities = [1.0]
        self.assertEqual(select_index(probabilities, 0.0), 0)
        self.assertEqual(select_index(probabilities, 0.2), 0)
        self.assertEqual(select_index(probabilities, 0.8), 0)
        self.assertEqual(select_index(probabilities, 1.0), 0)


class TestStratifiedSamplerInternals(unittest.TestCase):

    def test_random_rejection_sampling_basic(self):
        bucket = ((0, 0), (2, 2))  # 9 points
        result = random_rejection_sampling(bucket, 5)
        self.assertEqual(len(result), 5)
        for y, x in result:
            self.assertTrue(0 <= y <= 2)
            self.assertTrue(0 <= x <= 2)

    def test_random_rejection_sampling_full(self):
        bucket = ((0, 0), (1, 1))  # 4 points
        result = random_rejection_sampling(bucket, 4)
        self.assertEqual(len(result), 4)

    def test_random_rejection_sampling_error_on_oversample(self):
        bucket = ((0, 0), (1, 1))  # 4 points
        with self.assertRaises(ValueError):
            random_rejection_sampling(bucket, 5)

    def test_deterministic_sample_counts_exact_fraction(self):
        area_fractions = [0.25, 0.25, 0.25, 0.25]
        result = deterministic_sample_counts(area_fractions, 8)
        np.testing.assert_array_equal(result, [2, 2, 2, 2])

    def test_deterministic_sample_counts_zero_fraction(self):
        area_fractions = [0.0, 1.0]
        result = deterministic_sample_counts(area_fractions, 10)
        np.testing.assert_array_equal(result, [0, 10])

    def test_non_deterministic_sample_counts_distribution(self):
        area_fractions = [0.4, 0.4, 0.2]
        total = 100
        result = non_deterministic_sample_counts(area_fractions, total)
        self.assertEqual(sum(result), total)
        self.assertEqual(len(result), 3)

    def test_non_deterministic_sample_counts_sum_check(self):
        area_fractions = [0.3, 0.3, 0.3]
        with self.assertRaises(ValueError):
            non_deterministic_sample_counts(area_fractions, 10)

    def test_direct_child_buckets_leaf(self):
        bucket = ((0, 0), (0, 0))
        result = direct_child_buckets(bucket)
        np.testing.assert_array_equal(result, [bucket])

    def test_direct_child_buckets_produces_children(self):
        bucket = ((0, 0), (7, 7))  # Should subdivide
        children = direct_child_buckets(bucket)
        self.assertGreater(len(children), 1)

    def test_select_index_edge_values(self):
        probs = [0.1, 0.2, 0.3, 0.4]
        self.assertEqual(select_index(probs, 0.05), 0)
        self.assertEqual(select_index(probs, 0.15), 1)
        self.assertEqual(select_index(probs, 0.95), 3)

    def test_select_index_upper_bound(self):
        probs = [0.25, 0.25, 0.25, 0.25]
        self.assertEqual(select_index(probs, 0.999), 3)


if __name__ == '__main__':
    unittest.main(argv=[''], verbosity=2, exit=False)
