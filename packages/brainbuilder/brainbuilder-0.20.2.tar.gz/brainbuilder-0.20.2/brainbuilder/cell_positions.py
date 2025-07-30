# SPDX-License-Identifier: Apache-2.0
"""Algorithms to create cell positions."""

import logging

import numpy as np

from brainbuilder import poisson_disc_sampling

L = logging.getLogger(__name__)


def _assert_cubic_voxels(voxel_data):
    """Helper function that verifies whether the voxels of given voxel data are
    cubic.
    """
    a, b, c = np.abs(voxel_data.voxel_dimensions)
    assert np.isclose(a, b) and np.isclose(a, c)


def _get_cell_count(density, density_factor):
    """Helper function that counts the number of cells per voxel and the total
    number of cells.
    """
    # voxel volume is in um^3
    cell_count_per_voxel = density.raw * density_factor * density.voxel_volume / 1e9
    cell_count = int(np.round(np.sum(cell_count_per_voxel)))

    return cell_count_per_voxel, cell_count


def _get_seed(cell_count_per_voxel, voxel_data):
    """Helper function to calculate seed for Poisson disc sampling. The seed
    is set in a low-density area, to try to avoid that the algorithm gets
    stuck in the high-density areas. Other pitfalls of the Poisson disc
    sampling algorithm are illustrated on
    http://devmag.org.za/2009/05/03/poisson-disk-sampling/.
    """
    assert np.all(cell_count_per_voxel >= 0)
    positives = np.ma.masked_values(cell_count_per_voxel, 0)
    idcs = np.unravel_index(np.argmin(positives), cell_count_per_voxel.shape)
    return voxel_data.indices_to_positions(idcs) + voxel_data.voxel_dimensions / 2.0


def get_bbox_indices_nonzero_entries(data):
    """Calculate bounding box of indices of non-zero entries of a given
    three-dimensional numpy.array.
    """
    idx = np.nonzero(data)
    return np.array(
        [
            [np.min(idx[0]), np.min(idx[1]), np.min(idx[2])],
            [np.max(idx[0]), np.max(idx[1]), np.max(idx[2])],
        ]
    )


def get_bbox_nonzero_entries(data, bbox, voxel_dimensions):
    """Calculate bounding box of non-zero entries of a given three-dimensional
    numpy.array.

    Args:
        data: three-dimensional numpy.array
        bbox: original bbox
        voxel_dimensions: numpy.array with voxel size in each dimension
    """
    bbox_idx_nonzero = get_bbox_indices_nonzero_entries(data)
    bbox_nonzero = bbox[0, :] + bbox_idx_nonzero * voxel_dimensions
    bbox_nonzero[1, :] += voxel_dimensions
    return bbox_nonzero


def _create_cell_positions_uniform(density, density_factor):
    """Create cell positions given cell density volumetric data (using uniform distribution).

    Within voxels, samples are created according to a uniform distribution.

    The total cell count is calculated based on cell density values.

    Args:
        density(VoxelData): cell density (count / mm^3)
        density_factor(float): reduce / increase density proportionally for all
            voxels. Default is 1.0.

    Returns:
        numpy.array: array of positions of shape (cell_count, 3) where each row
        represents a cell and the columns correspond to (x, y, z).
    """
    cell_count_per_voxel, cell_count = _get_cell_count(density, density_factor)

    if cell_count == 0:
        L.warning("Density resulted in zero cell counts.")
        return np.empty((0, 3), dtype=np.float32)

    voxel_ijk = np.nonzero(cell_count_per_voxel > 0)
    voxel_idx = np.arange(len(voxel_ijk[0]))

    probs = 1.0 * cell_count_per_voxel[voxel_ijk] / np.sum(cell_count_per_voxel)
    chosen = np.random.choice(voxel_idx, cell_count, replace=True, p=probs)
    chosen_idx = np.stack(voxel_ijk).transpose()[chosen]

    # get random positions within chosen voxels
    return density.indices_to_positions(chosen_idx + np.random.random(np.shape(chosen_idx)))


def _create_cell_positions_poisson_disc(density, density_factor):
    """Create cell positions given cell density volumetric data (using poisson disc sampling).

    The upper limit of the total cell count is calculated based on cell density
    values. The minimum distance between points is based on the expected number
    of positions in each voxel. In case of a homogeneous cell density, the
    resulting set of points is equidistributed.

    Args:
        density(VoxelData): cell density (count / mm^3)
        density_factor(float): reduce / increase density proportionally for all
            voxels. Default is 1.0.

    Returns:
        numpy.array: array of positions of shape (nb_points, 3) where each row
        represents a cell and the columns correspond to (x, y, z).

        The upper limit of nb_points is the total cell count as extracted from
        the density volumetric data.
    """
    # pylint: disable=assignment-from-no-return
    cell_count_per_voxel, cell_count = _get_cell_count(density, density_factor)

    if cell_count == 0:
        L.warning("Density resulted in zero cell counts.")
        return np.empty((0, 3), dtype=np.float32)

    _assert_cubic_voxels(density)
    voxel_size = np.abs(density.voxel_dimensions[0])

    cell_cnt_masked = np.ma.masked_values(cell_count_per_voxel, 0)
    tmp = np.divide(voxel_size, np.power(cell_cnt_masked, 1.0 / density.ndim))
    too_large_distance = 2 * np.max(np.abs(density.bbox[1, :] - density.bbox[0, :]))
    local_distance = 0.84 * tmp.filled(too_large_distance)  # pylint: disable=no-member
    min_distance = np.min(local_distance)

    def _min_distance_func(point=None):
        """Helper function that makes the connection between input densities
        and distances between generated cell positions.
        """
        if point is None:
            # minimum distance, used for the spatial index
            return min_distance
        else:
            voxel = density.positions_to_indices(point)
            return local_distance[tuple(voxel)]

    seed = _get_seed(cell_count_per_voxel, density)
    bbox_nonzero = get_bbox_nonzero_entries(
        cell_count_per_voxel, density.bbox, density.voxel_dimensions
    )
    points = poisson_disc_sampling.generate_points(
        bbox_nonzero, cell_count, _min_distance_func, seed
    )
    return np.array(points)


def create_cell_positions(density, density_factor=1.0, method="basic", seed=None):
    """Given cell density volumetric data, create cell positions.

    Total cell count is calculated based on cell density values.

    Args:
        density(VoxelData): cell density (count / mm^3)
        density_factor(float): reduce / increase density proportionally for all
            voxels. Default is 1.0.
        method(str): algorithm used for cell position creation.
            Default is ``basic`` and the possible values are:

            - ``basic``: generated positions may collide or form clusters
            - ``poisson_disc``: positions are created with poisson disc sampling algorithm
              where minimum distance between points is modulated based on density values

        seed(int): (optional) the numpy random seed to be used.
            Defaults to None, in which case the seed is not set and the outcome
            cannot be predicted.

    Returns:
        numpy.array: array of positions of shape (cell_count, 3) where each row represents
        a cell and the columns correspond to (x, y, z).
    """
    if np.count_nonzero(density.raw < 0) != 0:
        raise ValueError("Found negative densities, aborting")

    if seed is not None:
        np.random.seed(seed)  # make the output reproducible

    position_generators = {
        "basic": _create_cell_positions_uniform,
        "poisson_disc": _create_cell_positions_poisson_disc,
    }

    return position_generators[method](density, density_factor)
