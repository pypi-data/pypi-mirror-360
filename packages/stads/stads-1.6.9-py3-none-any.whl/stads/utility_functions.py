import math
import numpy as np


def compute_sample_size(imageShape, sparsityPercent):
    return int(imageShape[0] * imageShape[1] * sparsityPercent / 100)


def find_corners(imageToSample):
    xCornerCoordinates = np.array([0, 0, len(imageToSample) - 1, len(imageToSample) - 1])
    yCornerCoordinates = np.array([0, len(imageToSample) - 1, 0, len(imageToSample) - 1])
    cornerPixelIntensities = np.array(
        [imageToSample[ yCornerCoordinates[i], xCornerCoordinates[i]] for i in range(len(xCornerCoordinates))])
    return np.array([yCornerCoordinates, xCornerCoordinates, cornerPixelIntensities]).astype(int)


def add_corners_to_samples(cornersToAdd, randomSparseFeatures):
    randomSparseFeatures = np.concatenate((randomSparseFeatures, cornersToAdd), axis=1)
    return randomSparseFeatures


def remove_duplicate_points(randomSparseFeatures):
    return np.unique(randomSparseFeatures, axis=1)


def calculate_number_of_pyramid_levels(imageSize):
    imageSizeY, imageSizeX = imageSize
    if imageSizeX <= 0 or imageSizeY <= 0:
        raise ValueError("illegal image size")
    numberOfPyramidLevels = 1
    pyramidResolution = 2
    while pyramidResolution < imageSizeX and pyramidResolution < imageSizeY:
        numberOfPyramidLevels = numberOfPyramidLevels + 1
        pyramidResolution = pyramidResolution * 2
    return numberOfPyramidLevels

def next_smaller_power_of_two( number ):
    if number <= 2:
        return 2
    return 2**int(math.log2( number-1 ))


def intersection_of_rectangles(a, b):
    upperLeft, lowerRight = a
    ay0, ax0 = upperLeft
    ay1, ax1  = lowerRight

    upperLeft, lowerRight = b
    by0, bx0 = upperLeft
    by1, bx1 = lowerRight

    x0 = max(ax0, bx0)
    x1 = min(ax1, bx1)
    y0 = max(ay0, by0)
    y1 = min(ay1, by1)

    if x0 > x1 or y0 > y1:
        return None

    return np.array([[y0, x0], [y1, x1]])


def calculate_number_of_samples_from_bucket(areaOfBucket, sparsityPercent):
    if sparsityPercent < 0.0 or sparsityPercent > 100.0:
        raise ValueError("invalid sparsity")
    if areaOfBucket <= 0:
        raise ValueError("invalid bucket")
    return int(sparsityPercent * areaOfBucket / 100)


def calculate_area_of_bucket(bucket):
    upper_left, lower_right = bucket
    y0, x0 = upper_left
    y1, x1 = lower_right
    width = x1 - x0 + 1
    height = y1 - y0 + 1
    return width * height


def calculate_area_fractions_of_buckets(children, parentBucket):
    if not math.isclose(np.sum([calculate_area_of_bucket(child) for child in children]), calculate_area_of_bucket(parentBucket)):
        raise ValueError("Areas don't add up")
    areaFractionOfBucket = []
    for childBucket in children:
        area = calculate_area_of_bucket(childBucket) / calculate_area_of_bucket(parentBucket)
        areaFractionOfBucket.append(area)
    return np.array(areaFractionOfBucket)
