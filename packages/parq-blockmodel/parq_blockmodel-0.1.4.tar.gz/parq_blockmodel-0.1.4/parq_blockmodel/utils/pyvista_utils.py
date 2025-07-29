from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

import pandas as pd
import numpy as np
from scipy.stats import mode

from parq_blockmodel import RegularGeometry

if TYPE_CHECKING:
    import pyvista as pv


def df_to_pv_image_data(df: pd.DataFrame,
                        geometry: RegularGeometry,
                        fill_value=np.nan) -> 'pv.ImageData':
    """
    Convert a DataFrame to a PyVista ImageData object for a dense regular grid.

    Args:
        df: DataFrame with MultiIndex (x, y, z) or columns x, y, z.
        geometry: RegularGeometry instance (provides shape, spacing, origin).
        fill_value: Value to use for missing cells.

    Returns:
        pv.ImageData: PyVista ImageData object with cell data.
    """

    # Ensure index is MultiIndex (x, y, z)
    if not isinstance(df.index, pd.MultiIndex):
        df = df.set_index(['x', 'y', 'z'])

    # Create dense index and reindex
    dense_index = geometry.to_multi_index()
    dense_df = df.reindex(dense_index)
    shape = geometry.shape

    grid: pv.ImageData = geometry.to_pyvista()

    for attr in df.columns:
        arr = dense_df[attr].to_numpy().reshape(shape, order='C').ravel(order='F')
        arr = np.where(np.isnan(arr), fill_value, arr)
        grid.cell_data[attr] = arr

    return grid


def df_to_pv_structured_grid(df: pd.DataFrame,
                             block_size: Optional[tuple[float, float, float]] = None,
                             validate_block_size: bool = True
                             ) -> 'pv.StructuredGrid':
    """Convert a DataFrame into a PyVista StructuredGrid.

    This function is for the full grid dense block model.

    The DataFrame should have a MultiIndex of coordinates (x, y, z) and data columns.
    The grid is created assuming uniform block sizes in the x, y, z directions.
    The grid points are calculated based on the centroids of the blocks, and the data is added to the cell
    data of the grid.

    Args:
        df: pd.DataFrame with a MultiIndex of coordinates (x, y, z) and data columns.
        block_size: tuple of floats (dx, dy, dz), optional.  Not used if geometry is provided.
        validate_block_size: bool, optional.  Not needed if geometry is provided.

    Returns:
        pv.StructuredGrid: A PyVista StructuredGrid object.
    """
    import pyvista as pv

    # ensure the dataframe is sorted by z, y, x, since Pyvista uses 'F' order.
    df = df.sort_index(level=['z', 'y', 'x'])

    # Get the unique x, y, z coordinates (centroids)
    x_centroids = df.index.get_level_values('x').unique()
    y_centroids = df.index.get_level_values('y').unique()
    z_centroids = df.index.get_level_values('z').unique()

    if block_size is None:
        # Calculate the cell size (assuming all cells are of equal size)
        dx = np.diff(x_centroids)[0]
        dy = np.diff(y_centroids)[0]
        dz = np.diff(z_centroids)[0]
    else:
        dx, dy, dz = block_size[0], block_size[1], block_size[2]

    if validate_block_size:
        # Check all diffs are the same (within tolerance)
        tol = 1e-8
        if (np.any(np.abs(np.diff(x_centroids) - dx) > tol) or
                np.any(np.abs(np.diff(y_centroids) - dy) > tol) or
                np.any(np.abs(np.diff(z_centroids) - dz) > tol)):
            raise ValueError("Block sizes are not uniform in the structured grid.")

    # Calculate the grid points
    x_points = np.concatenate([x_centroids - dx / 2, x_centroids[-1:] + dx / 2])
    y_points = np.concatenate([y_centroids - dy / 2, y_centroids[-1:] + dy / 2])
    z_points = np.concatenate([z_centroids - dz / 2, z_centroids[-1:] + dz / 2])

    # Create the 3D grid of points
    x, y, z = np.meshgrid(x_points, y_points, z_points, indexing='ij')

    # Create a StructuredGrid object
    grid = pv.StructuredGrid(x, y, z)

    # Add the data from the DataFrame to the grid
    for column in df.columns:
        grid.cell_data[column] = df[column].values

    return grid


def df_to_pv_unstructured_grid(df: pd.DataFrame, block_size: tuple[float, float, float],
                               validate_block_size: bool = True) -> 'pv.UnstructuredGrid':
    """Convert a DataFrame into a PyVista UnstructuredGrid.

    This function is for the unstructured grid block model, which is typically used for sparse or
    irregular block models.

    The DataFrame should have a MultiIndex of coordinates (x, y, z) and block sizes (dx, dy, dz).
    The grid is created based on the centroids of the blocks, and the data is added to the cell
    data of the grid.
    The block sizes (dx, dy, dz) can be provided or estimated from the DataFrame.


    Args:
        df: pd.DataFrame with a MultiIndex of coordinates (x, y, z) and block sizes (dx, dy, dz).
        block_size: tuple of floats, optional
        validate_block_size: bool, optional

    Returns:
        pv.UnstructuredGrid: A PyVista UnstructuredGrid object.
    """

    import pyvista as pv

    # ensure the dataframe is sorted by z, y, x, since Pyvista uses 'F' order.
    blocks = df.reset_index().sort_values(['z', 'y', 'x'])

    # Get the x, y, z coordinates and cell dimensions
    # if no dims are passed, estimate them
    if 'dx' not in blocks.columns:
        dx, dy, dz = block_size[0], block_size[1], block_size[2]
        blocks['dx'] = dx
        blocks['dy'] = dy
        blocks['dz'] = dz

    if validate_block_size:
        tol = 1e-8
        if blocks[['dx', 'dy', 'dz']].std().max() > tol:
            raise ValueError("Block sizes are not uniform in the unstructured grid.")

    x, y, z, dx, dy, dz = (blocks[col].values for col in blocks.columns if col in ['x', 'y', 'z', 'dx', 'dy', 'dz'])
    blocks.set_index(['x', 'y', 'z', 'dx', 'dy', 'dz'], inplace=True)
    # Create the cell points/vertices
    # REF: https://github.com/OpenGeoVis/PVGeo/blob/main/PVGeo/filters/voxelize.py

    n_cells = len(x)

    # Generate cell nodes for all points in data set
    # - Bottom
    c_n1 = np.stack(((x - dx / 2), (y - dy / 2), (z - dz / 2)), axis=1)
    c_n2 = np.stack(((x + dx / 2), (y - dy / 2), (z - dz / 2)), axis=1)
    c_n3 = np.stack(((x - dx / 2), (y + dy / 2), (z - dz / 2)), axis=1)
    c_n4 = np.stack(((x + dx / 2), (y + dy / 2), (z - dz / 2)), axis=1)
    # - Top
    c_n5 = np.stack(((x - dx / 2), (y - dy / 2), (z + dz / 2)), axis=1)
    c_n6 = np.stack(((x + dx / 2), (y - dy / 2), (z + dz / 2)), axis=1)
    c_n7 = np.stack(((x - dx / 2), (y + dy / 2), (z + dz / 2)), axis=1)
    c_n8 = np.stack(((x + dx / 2), (y + dy / 2), (z + dz / 2)), axis=1)

    # - Concatenate
    # nodes = np.concatenate((c_n1, c_n2, c_n3, c_n4, c_n5, c_n6, c_n7, c_n8), axis=0)
    nodes = np.hstack((c_n1, c_n2, c_n3, c_n4, c_n5, c_n6, c_n7, c_n8)).ravel().reshape(n_cells * 8, 3)

    # create the cells
    # REF: https://docs/pyvista.org/examples/00-load/create-unstructured-surface.html
    cells_hex = np.arange(n_cells * 8).reshape(n_cells, 8)

    grid = pv.UnstructuredGrid({pv.CellType.VOXEL: cells_hex}, nodes)

    # add the attributes (column) data
    for col in blocks.columns:
        grid.cell_data[col] = blocks[col].values

    return grid


def calculate_spacing(grid: pv.UnstructuredGrid) -> tuple[float, float, float]:
    """
    Calculate the spacing of an UnstructuredGrid by finding the mode of unique differences.

    Args:
        grid (pv.UnstructuredGrid): The input PyVista UnstructuredGrid.

    Returns:
        tuple[float, float, float]: The spacing in x, y, and z directions.
    """
    # Extract unique x, y, z coordinates
    x_coords = np.unique(grid.points[:, 0])
    y_coords = np.unique(grid.points[:, 1])
    z_coords = np.unique(grid.points[:, 2])

    # Calculate differences and find the mode
    dx = mode(np.diff(x_coords)).mode
    dy = mode(np.diff(y_coords)).mode
    dz = mode(np.diff(z_coords)).mode

    return dx, dy, dz
