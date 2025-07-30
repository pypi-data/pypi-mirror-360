"""Module to define imaging 3D geometry and related transforms."""

from builtins import len

import numpy
from numpy import ndarray


class Transform:
    """Interface for forward and backward transform of 3D points and vectors."""

    # Forward transform of 3D coord
    def __init__(self):
        """Initializes Transform."""
        pass

    def transform_point(self, coord):
        """Forward transform of 3D coord."""
        return coord

    # Forward transform of 3D vector
    def transform_vector(self, vec):
        """Forward transform of 3D vector."""
        return vec

    # Backward transform of 3D coord
    def inverse_transform_point(self, coord):
        """Backward transform of 3D coord."""
        return coord

    # Backward transform of 3D vector
    def inverse_transform_vector(self, vec):
        """Backward transform of 3D vector."""
        return vec

    def transform_points(self, points):
        """Forward transform of 3D points."""
        return points

    def inverse_transform_points(self, points):
        """Backward transform of 3D points."""
        return points


def apply_transform_to_point(matrix, coord):
    """Apply matrix multiplication to a single 2D or 3D coord and adjust dimensionality.

    :param matrix: 4x4 or 3x3 matrix
    :param coord: 3D grid coordinate
    :type coord: numpy.array or list
    :return: 3D coordinate from multiplication of matrix x coord
    """
    dim = len(coord)
    if dim == 2:
        # 0 is added for slice axis, 1 is added for matrix multiplication
        coord = numpy.asarray((coord[0], coord[1], 0, 1))
    elif dim == 3:
        # 1 is added for matrix multiplication
        coord = numpy.asarray((coord[0], coord[1], coord[2], 1))
    # Apply matrix multiplication and return the 3D coord
    return numpy.matmul(matrix, coord)[0:3]


def apply_transform_to_points(matrix, points):
    """Apply matrix multiplication of matrix x points and adjust dimensionality.

    :param matrix: 4x4 or 3x3 matrix
    :param points: numpy ndarray of shape(n,2) or (n,3) for 2D and 3D respectively
    :return: ndarray of shape [n,3] representing matrix X points (same shape as points)
    """
    if not isinstance(points, ndarray):
        points = numpy.asarray(points, dtype=float)
    shape = points.shape
    mshape = matrix.shape
    d = shape[1]
    if d == 2:
        # Pad zeros to make 3D
        zeros = numpy.zeros((shape[0], 1))
        points = numpy.concatenate((points, zeros), axis=1)
        d = 3
    if mshape[1] > d:
        # Pad ones to match mshape
        ones = numpy.ones((shape[0], mshape[1] - d))
        points = numpy.concatenate((points, ones), axis=1)

    # Matrix multiplication requires transposition
    result = numpy.matmul(matrix, points.swapaxes(0, 1)).swapaxes(0, 1)
    if result.shape[1] > shape[1]:
        # Restore dimensionality of input coordinate array
        result = result[:, 0:d]
    return result


class Matrix3DTransform(Transform):
    """A transform class for 3D points and vectors using a 4x4 transformation matrix."""

    # matrix must be a 4x4 numpy array
    def __init__(self, matrix):
        """Initializes Matrix3DTransform object."""
        self.matrix = matrix
        self.inverseMatrix = numpy.linalg.inv(matrix)

    def transform_points(self, points):
        """Apply this transform in the forward direction to an array of points.

        :param points: numpy ndarray of shape(n,2) or (n,3) for 2D and 3D respectively
        :return: ndarray of shape [n,3] after transformation in the forward direction
        """
        return apply_transform_to_points(self.matrix, points)

    def inverse_transform_points(self, points):
        """Apply this transform in the reverse direction to an array of points.

        :param points: numpy ndarray of shape(n,2) or (n,3) for 2D and 3D respectively
        :return: ndarray of shape [n,3] after transformation in the reverse direction
        """
        return apply_transform_to_points(self.inverseMatrix, points)

    # Transform point in forward direction
    def transform_point(self, coord):
        """Apply this transform in the forward direction to a single coordinate.

        :param coord: 2D or 3D coordinate that can be a tuple or numpy array
        :return: ndarray of shape [n,3] after transformation in the forward direction
        """
        return apply_transform_to_point(self.matrix, coord)

    # Transform point in reverse direction
    def inverse_transform_point(self, coord):
        """Apply this transform in the reverse direction to a single coordinate.

        :param coord: 2D or 3D coordinate that can be a tuple or numpy array
        :return: ndarray of shape [n,3] after transformation in the forward direction
        """
        return apply_transform_to_point(self.inverseMatrix, coord)

    # Transform vector in forward direction
    def transform_vector(self, vec3D):
        """Apply this transform in the forward direction to a vector.

        :param vec3D: 3D coordinate representing a vector
        :return: 3D numpy array after forward transformation of the vector
        """
        origin_transformed = self.transform_point((0, 0, 0))
        tip_transformed = self.transform_point(vec3D)
        return numpy.subtract(tip_transformed, origin_transformed)

    # Transform vector in reverse direction
    def inverse_transform_vector(self, vec3D):
        """Apply this transform in the reverse direction to a vector.

        :param vec3D: 3D coordinate representing a vector
        :return: 3D numpy array after reverse transformation of the vector
        """
        origin_transformed = self.inverse_transform_point((0, 0, 0))
        tip_transformed = self.inverse_transform_point(vec3D)
        return numpy.subtract(tip_transformed, origin_transformed)
