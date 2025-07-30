import unittest
import numpy as np

from src.stads.stads_helpers import (compute_local_moments_of_image, compute_local_temporal_variance, compute_optical_flow,
                                     compute_pdf_from_gradients_image)


class TestImageProcessingFunctions(unittest.TestCase):

    def setUp(self):
        self.image = np.random.rand(100, 100).astype(np.float32)
        self.image_uint8 = (255 * self.image).astype(np.uint8)
        self.frame1 = np.random.rand(100, 100).astype(np.float32)
        self.frame2 = np.random.rand(100, 100).astype(np.float32)
        self.windowSize = 5

    def test_compute_local_moments_of_image(self):
        meanMap, gradientMap, varianceMap = compute_local_moments_of_image(self.image, self.windowSize)
        self.assertEqual(meanMap.shape, self.image.shape)
        self.assertEqual(gradientMap.shape, self.image.shape)
        self.assertEqual(varianceMap.shape, self.image.shape)
        self.assertTrue(np.all(gradientMap >= 0) and np.all(gradientMap <= 255))

    def test_compute_local_temporal_variance(self):
        varianceMap = compute_local_temporal_variance(self.frame1, self.frame2, self.windowSize)
        self.assertEqual(varianceMap.shape, self.image.shape)
        self.assertTrue(np.all(varianceMap >= 0))

    def test_compute_optical_flow(self):
        # Using uint8 images for OpenCV optical flow
        frame1_uint8 = (self.frame1 * 255).astype(np.uint8)
        frame2_uint8 = (self.frame2 * 255).astype(np.uint8)
        magnitude = compute_optical_flow(frame1_uint8, frame2_uint8, self.windowSize)
        self.assertEqual(magnitude.shape, self.image.shape)
        self.assertTrue(np.all(magnitude >= 0))

    def test_compute_pdf_from_gradients_image(self):
        gradients = np.random.rand(100, 100).astype(np.float32)
        pdf = compute_pdf_from_gradients_image(gradients)
        self.assertEqual(pdf.shape, gradients.shape)
        self.assertTrue(np.isclose(np.sum(pdf), 1.0) or np.all(pdf == 0.0))

    def test_zero_gradients_pdf(self):
        gradients = np.zeros((100, 100), dtype=np.float32)
        pdf = compute_pdf_from_gradients_image(gradients)
        self.assertTrue(np.all(pdf == 0))

    def test_compute_local_moments_on_constant_image(self):
        constant_image = np.ones((10, 10), dtype=np.float32)
        meanMap, gradientMap, varianceMap = compute_local_moments_of_image(constant_image, self.windowSize)
        self.assertTrue(np.allclose(meanMap, 1.0))
        self.assertTrue(np.all(gradientMap == 0))
        self.assertTrue(np.allclose(varianceMap, 0.0))

    def test_compute_local_moments_on_small_image(self):
        small_image = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.float32)
        meanMap, gradientMap, varianceMap = compute_local_moments_of_image(small_image, windowSize=2)
        self.assertEqual(meanMap.shape, small_image.shape)
        self.assertEqual(gradientMap.shape, small_image.shape)
        self.assertEqual(varianceMap.shape, small_image.shape)

    def test_pdf_normalization_error_correction(self):
        gradients = np.ones((10, 10), dtype=np.float32)
        pdf = compute_pdf_from_gradients_image(gradients)
        self.assertAlmostEqual(np.sum(pdf), 1.0, places=6)

    def test_pdf_on_negative_gradients(self):
        gradients = -np.ones((10, 10), dtype=np.float32)
        pdf = compute_pdf_from_gradients_image(gradients)
        self.assertTrue(np.all(pdf == 0.0))

    def test_temporal_variance_on_identical_frames(self):
        identical = np.random.rand(100, 100).astype(np.float32)
        variance = compute_local_temporal_variance(identical, identical, self.windowSize)
        self.assertTrue(np.allclose(variance, 0.0))

    def test_optical_flow_on_identical_frames(self):
        identical = (np.random.rand(100, 100) * 255).astype(np.uint8)
        magnitude = compute_optical_flow(identical, identical, self.windowSize)
        self.assertLess(np.mean(magnitude), 0.1, "Optical flow on identical images should be close to zero")

    def test_optical_flow_none_input(self):
        with self.assertRaises(ValueError):
            compute_optical_flow(None, self.frame2, self.windowSize)

    def test_pdf_on_sparse_gradient_image(self):
        gradients = np.zeros((10, 10), dtype=np.float32)
        gradients[5, 5] = 10.0
        pdf = compute_pdf_from_gradients_image(gradients)
        expected = np.zeros_like(gradients)
        expected[5, 5] = 1.0
        self.assertTrue(np.allclose(pdf, expected))

    def test_gradient_map_clipping(self):
        high_gradient = np.ones((100, 100), dtype=np.float32) * 1000
        _, gradientMap, _ = compute_local_moments_of_image(high_gradient, self.windowSize)
        self.assertTrue(np.all((gradientMap >= 0) & (gradientMap <= 255)))


if __name__ == '__main__':
    unittest.main()

