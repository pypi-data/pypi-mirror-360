import os
import numpy as np
import cv2
import logging
from scipy.optimize import curve_fit

from . import evaluation
from .image_processing import generate_scan_pattern_from_pdf
from .interpolator import ImageInterpolator
from .monitor import visualize_microscope_image
from .stads_helpers import compute_local_moments_of_image, compute_pdf_from_gradients_image, \
    compute_local_temporal_variance, compute_optical_flow
from .microscope import Microscope
from .random_sampler import RandomSampler
from .stratified_sampler import StratifiedSampler

logging.basicConfig(level=logging.INFO)


def linear_func(x, a, b):
    return a * x + b


class AdaptiveSampler:
    def __init__(self, initialSampling, interpolMethod, sparsityPercent, numberOfFrames,
                 groundTruthName="dendrites_one", withTemporal=True):

        self.windowSize = 8

        self.initialSampling = initialSampling
        self.interpolMethod = interpolMethod
        self.sparsityPercent = sparsityPercent
        self.numberOfFrames = numberOfFrames
        self.withTemporal = withTemporal

        self.sampledFrames = [None] * self.numberOfFrames
        self.microscope = Microscope(groundTruthName)
        self.imageShape = self.microscope.imageShape

        self.reconstructedFrames = []
        self.gradientsMaps = []
        self.yCoords, self.xCoords = self.initialize_sampling()

        self.flowMap = np.zeros(self.imageShape)
        self.temporalVarianceMap = np.ones(self.imageShape)
        self.spatialVarianceMap = np.ones(self.imageShape)

        self.psnrs = []
        self.ssims = []

        self.farnebackParameters = {
            "pyr_scale": 0.5,
            "levels": 5,
            "window_size": self.windowSize,
            "iterations": 5,
            "poly_n": 7,
            "poly_sigma": 1.0,
            "flags": 0
        }

    def initialize_sampling(self):
        if self.initialSampling == 'uniform':
            randomSampler = RandomSampler(self.interpolMethod, self.sparsityPercent)
            return randomSampler.get_coordinates()
        elif self.initialSampling == 'stratified':
            stratifiedSampler = StratifiedSampler(self.interpolMethod, self.sparsityPercent)
            return stratifiedSampler.get_coordinates()
        else:
            raise ValueError("Invalid initial sampling method. Choose 'uniform' or 'stratified'.")

    def get_samples(self, frameNumber=0):
        sampledImage = self.microscope.sample_image(self.yCoords, self.xCoords, frameNumber)
        pixelIntensities = sampledImage[self.yCoords, self.xCoords]
        self.sampledFrames[frameNumber] = sampledImage
        return pixelIntensities

    def interpolate_sparse_image(self, pixelIntensities):
        knownPoints = np.column_stack((self.xCoords, self.yCoords))
        imageInterpolator = ImageInterpolator(self.imageShape, knownPoints, pixelIntensities, self.interpolMethod)
        reconstructedImage = imageInterpolator.interpolate_image()
        reconstructedImage = np.clip(reconstructedImage, 0, 255).astype(np.uint8)
        return reconstructedImage

    def update_reconstructed_frames(self, reconstructedImage):
        self.reconstructedFrames.append(reconstructedImage)

    def update_gradients_maps(self, gradientsMap):
        self.gradientsMaps.append(gradientsMap)

    def compute_pmf_based_on_spatiotemporal_stats(self, samplingMap):
        samplingVarianceMap = compute_pdf_from_gradients_image(samplingMap)
        flowDensityMap = compute_pdf_from_gradients_image(self.flowMap)
        return compute_pdf_from_gradients_image(0.5 * (samplingVarianceMap + flowDensityMap))

    def update_scan_pattern(self, pdf):
        self.yCoords, self.xCoords = generate_scan_pattern_from_pdf(pdf, self.sparsityPercent)

    def update_flow_map(self, frameNumber=1):

        prev = self.gradientsMaps[frameNumber - 1]
        curr = self.gradientsMaps[frameNumber]

        flow = cv2.calcOpticalFlowFarneback(prev, curr, None,
                                            self.farnebackParameters["pyr_scale"],
                                            self.farnebackParameters["levels"],
                                            self.farnebackParameters["window_size"],
                                            self.farnebackParameters["iterations"],
                                            self.farnebackParameters["poly_n"],
                                            self.farnebackParameters["poly_sigma"],
                                            self.farnebackParameters["flags"])
        magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        self.flowMap = magnitude

    def update_temporal_variance_map(self, frameNumber=0):
        self.temporalVarianceMap = compute_local_temporal_variance(
            self.reconstructedFrames[frameNumber - 1], self.reconstructedFrames[frameNumber], self.windowSize)

    def compute_spatiotemporal_variance_map(self, spatialVarianceMap):
        return spatialVarianceMap + self.temporalVarianceMap

    def recalibrate_flow_parameters(self):
        """
        Recalibrate optical flow parameter poly_sigma using curve fitting on temporal variance means.
        """
        frame_indices = np.arange(len(self.reconstructedFrames))
        if len(frame_indices) < 6:
            # Not enough frames for fitting
            return

        temporal_var_means = []
        for i in frame_indices:
            if i == 0:
                temporal_var_means.append(np.mean(self.temporalVarianceMap))
            else:
                tv_map = compute_local_temporal_variance(
                    self.reconstructedFrames[i - 1], self.reconstructedFrames[i], self.windowSize)
                temporal_var_means.append(np.mean(tv_map))

        temporal_var_means = np.array(temporal_var_means)

        try:
            popt, _ = curve_fit(linear_func, frame_indices, temporal_var_means)
            a, b = popt
            current_frame = frame_indices[-1]
            fitted_value = linear_func(current_frame, a, b)
            new_poly_sigma = min(max(0.5, fitted_value), 2.0)  # clamp to [0.5, 2.0]

            old_poly_sigma = self.farnebackParameters["poly_sigma"]
            self.farnebackParameters["poly_sigma"] = new_poly_sigma

            print(f"[Recalibrate] Old poly_sigma: {old_poly_sigma:.3f}, New poly_sigma: {new_poly_sigma:.3f}")

        except Exception as e:
            logging.warning(f"Curve fitting failed: {e}")

    def generate_scan_pattern_for_next_frame(self, frameNumber):
        pixelIntensities = self.get_samples(frameNumber)
        reconstructedImage = self.interpolate_sparse_image(pixelIntensities)
        self.update_reconstructed_frames(reconstructedImage)

        if frameNumber < self.numberOfFrames - 1:
            meanMap, gradientMap, spatialVariance = compute_local_moments_of_image(reconstructedImage, self.windowSize)
            self.update_gradients_maps(gradientMap)
            self.spatialVarianceMap = spatialVariance
            spatiotemporalVariance = self.compute_spatiotemporal_variance_map(self.spatialVarianceMap)

            if self.withTemporal and frameNumber > 0:
                self.update_flow_map(frameNumber)
                self.update_temporal_variance_map(frameNumber)

                # Recalibrate parameters after 5 frames
                if frameNumber >= 5:
                    self.recalibrate_flow_parameters()

            pdf = self.compute_pmf_based_on_spatiotemporal_stats(spatiotemporalVariance)
            self.update_scan_pattern(pdf)

    def run(self):
        for frameNumber in range(self.numberOfFrames):
            self.generate_scan_pattern_for_next_frame(frameNumber)

            psnr = evaluation.calculate_psnr(self.microscope.groundTruthVideo[frameNumber],
                                             self.reconstructedFrames[frameNumber])
            ssim = evaluation.calculate_ssim(self.reconstructedFrames[frameNumber],
                                             self.microscope.groundTruthVideo[frameNumber])
            self.psnrs.append(psnr)
            self.ssims.append(ssim)

        return np.array(self.reconstructedFrames), self.psnrs, self.ssims

    def coordinates_to_mask(self, yCoords, xCoords):
        mask = np.zeros(self.imageShape, dtype=np.uint8)
        mask[yCoords, xCoords] = 255
        return mask

    def generate_masks(self):
        spatial_pdf = compute_pdf_from_gradients_image(self.spatialVarianceMap)
        spatiotemporal_pdf = compute_pdf_from_gradients_image(
            self.compute_spatiotemporal_variance_map(self.spatialVarianceMap)
        )
        flow_pdf = compute_pdf_from_gradients_image(self.flowMap)

        y1, x1 = generate_scan_pattern_from_pdf(spatial_pdf, self.sparsityPercent)
        y2, x2 = generate_scan_pattern_from_pdf(spatiotemporal_pdf, self.sparsityPercent)
        y3, x3 = generate_scan_pattern_from_pdf(flow_pdf, self.sparsityPercent)

        spatialMask = self.coordinates_to_mask(y1, x1)
        spatiotemporalMask = self.coordinates_to_mask(y2, x2)
        flowMask = self.coordinates_to_mask(y3, x3)

        return spatialMask, spatiotemporalMask, flowMask

    def show_figures(self, frameNumber=4):
        if frameNumber >= len(self.reconstructedFrames):
            raise IndexError("Frame number exceeds number of reconstructed frames.")

        sampled = self.sampledFrames[frameNumber]
        reconstructed = self.reconstructedFrames[frameNumber]

        print(f"Displaying results for frame {frameNumber}")
        print(f"PSNR: {self.psnrs[frameNumber]:.2f}, SSIM: {self.ssims[frameNumber]:.4f}")
        visualize_microscope_image(sampled, imageTitle="Sampled Image (Adaptive Sampling)")
        visualize_microscope_image(reconstructed, imageTitle="Reconstructed Image")

        spatial_mask, spatiotemporal_mask, flow_mask = self.generate_masks()
        visualize_microscope_image(spatial_mask, imageTitle="Spatial Variance Mask")
        visualize_microscope_image(spatiotemporal_mask, imageTitle="Spatiotemporal Variance Mask")
        visualize_microscope_image(flow_mask, imageTitle="Flow Mask")

    def save_figures(self, frameNumber=4, save_path="plots"):
        if frameNumber >= len(self.reconstructedFrames):
            raise IndexError("Frame number exceeds number of reconstructed frames.")

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        sampled = self.sampledFrames[frameNumber]
        reconstructed = self.reconstructedFrames[frameNumber]

        visualize_microscope_image(sampled, imageTitle="Sampled Image (Adaptive Sampling)",
                                   savePlot=True, savePath=os.path.join(save_path, f"frame_{frameNumber}_sampled.png"))
        visualize_microscope_image(reconstructed, imageTitle="Reconstructed Image",
                                   savePlot=True,
                                   savePath=os.path.join(save_path, f"frame_{frameNumber}_reconstructed.png"))

        spatial_mask, spatiotemporal_mask, flow_mask = self.generate_masks()
        visualize_microscope_image(spatial_mask, imageTitle="Spatial Variance Mask",
                                   savePlot=True,
                                   savePath=os.path.join(save_path, f"frame_{frameNumber}_spatial_mask.png"))
        visualize_microscope_image(spatiotemporal_mask, imageTitle="Spatiotemporal Variance Mask",
                                   savePlot=True,
                                   savePath=os.path.join(save_path, f"frame_{frameNumber}_spatiotemporal_mask.png"))
        visualize_microscope_image(flow_mask, imageTitle="Flow Mask",
                                   savePlot=True,
                                   savePath=os.path.join(save_path, f"frame_{frameNumber}_flow_mask.png"))
