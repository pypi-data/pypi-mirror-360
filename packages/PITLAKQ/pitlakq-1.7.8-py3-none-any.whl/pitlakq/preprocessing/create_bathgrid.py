"""
Create bathymetry grid data with linear interpolation.

"""

from pathlib import Path
import os
import shutil

from matplotlib import cm
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import griddata

from pitlakq.metamodel.configuration.getconfig import read_dot_pitlakq


def _create_output_path(project_path):
    """Create output path."""
    output_path = Path(project_path, 'preprocessing', 'output')
    output_path.mkdir(exist_ok=True)
    output_path = Path(project_path, 'preprocessing', 'tmp')
    output_path.mkdir(exist_ok=True)



def make_grid(file_name, num_x, num_y):
    """
    Create grid with linear interpolation.

    :param file_name: file name for file with lake bottom data
    :param num_x: number of interpolation points in x direction
    :param num_y: number of interpolation points in y direction
    :return: dict with these items
       grid: 2D array with gridded z values
       start_x: start coordinate for interpolation in x direction
       start_y: start coordinate for interpolation in y direction
       end_x: end coordinate for interpolation in x direction
       end_y: end coordinate for interpolation in y direction
    """
    bath = pd.read_csv(file_name, delim_whitespace=True)
    start_x, end_x = bath.x.min(), bath.x.max()
    start_y, end_y = bath.y.min(), bath.y.max()

    points = bath[['x', 'y']].values
    values = bath.z.values
    grid_x, grid_y = np.mgrid[start_x:end_x:num_x*1j, start_y:end_y:num_y*1j]
    grid = griddata(points, values, (grid_x, grid_y), method='linear')
    res = {'grid': grid,
           'grid_x': grid_x,
           'grid_y': grid_y,
           'start_x': start_x,
           'end_x': end_x,
           'start_y': start_y,
           'end_y': end_y}
    return res


def save_surfer_ascii(file_name, grid, num_x, num_y, start_x, start_y, end_x,
                      end_y):
    """
    Write Surfer Ascii file from 2D array of gridded values.

    :param file_name: file name for grid
    :param grid: 2D array with gridded z values
    :param num_x: number of interpolation points in x direction
    :param num_y: number of interpolation points in y direction
    :param start_x: start coordinate for interpolation in x direction
    :param start_y: start coordinate for interpolation in y direction
    :param end_x: end coordinate for interpolation in x direction
    :param end_y: end coordinate for interpolation in y direction
    :return: None
    """
    # pylint: disable=too-many-arguments
    n_values = 10
    with open(file_name, 'w') as fobj:
        fobj.write('DSAA\n')
        fobj.write(f'{num_x} {num_y}\n')
        fobj.write(f'{start_x} {end_x}\n')
        fobj.write(f'{start_y} {end_y}\n')
        fobj.write(f'{np.min(grid)} {np.max(grid)}\n')
        for line in grid:
            start = 0
            end = n_values
            while True:
                data = line[start:end]
                if not data.size:
                    break
                str_data = ' '.join(f'{x:10.8f}' for x in data)
                fobj.write(f'{str_data}\n')
                start = end
                end = start + n_values
            fobj.write('\n')


def main(project_name, bath_data_file_name, num_x, num_y,
         grd_file_name='bath_asci.grd', copy_to_input=False):
    """
    Create Surfer ascii grid file from measured bottom elevation data.

    :param project_name: project name
    :param bath_data_file_name: name of file with lake bottom data
    :param num_x: number of interpolation points in x direction
    :param num_y: number of interpolation points in y direction
    :param grd_file_name: name out surfer ascii grid file
    :return: None
    """
    dot_pitlakq = list(read_dot_pitlakq())[0]
    project_path = os.path.join(dot_pitlakq['model_path'], project_name)
    bath_file = os.path.join(project_path, 'preprocessing', 'input',
                             bath_data_file_name)
    _create_output_path(project_path)
    grd_file = os.path.join(project_path, 'preprocessing', 'output',
                            grd_file_name)
    res = make_grid(bath_file, num_x, num_y)
    save_surfer_ascii(grd_file, grid=res['grid'].T, num_x=num_x, num_y=num_y,
                      start_x=res['start_x'], start_y=res['start_y'],
                      end_x=res['end_x'], end_y=res['end_y'])
    if copy_to_input:
        input_grd_file = os.path.join(
            project_path, 'preprocessing', 'input', grd_file_name)
        shutil.copy(grd_file, input_grd_file)



def show_points(project_name, bath_data_file_name='bath_data.txt',
                plot_file_name='lake_bottom_points.png', show_plot=True):
    """
    Show the location of the measured bathymetry points.
    :param project_name: project name
    :param bath_data_file_name: name of file with lake bottom data
    :param plot_file_name: name of result plot file, None for no file
    :param show_plot: show plot interactively
    :return: None
    """
    dot_pitlakq = list(read_dot_pitlakq())[0]
    project_path = os.path.join(dot_pitlakq['model_path'], project_name)
    bath_file = os.path.join(project_path, 'preprocessing', 'input',
                             bath_data_file_name)

    bath_data = pd.read_csv(bath_file, delim_whitespace=True)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    bath_data.plot(x='x', y='y', kind='scatter', ax=ax)
    if plot_file_name:
        _create_output_path(project_path)
        plot_file = os.path.join(project_path, 'preprocessing', 'output',
                                 plot_file_name)
        plt.savefig(plot_file, dpi=150)
    if show_plot:
        plt.show()


def show_contours(project_name, num_x, num_y, spacing=10,
                  bath_data_file_name='bath_data.txt',
                  plot_file_name='lake_contour.png',
                  show_plot=True, **kwargs):
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals
    """
    Show contour map of gridded data.
    :param project_name: project name
    :param num_x: number of interpolation points in x direction
    :param num_y: number of interpolation points in y direction
    :param spacing: spacing between contour lines
    :param bath_data_file_name: name of file with lake bottom data
    :param plot_file_name: name of file to save figure
    :param show_plot: show the plot interactively
    :param kwargs: keyword arguments for `plt.contour` and `plt.contourf`
    :return:
    """
    dot_pitlakq = list(read_dot_pitlakq())[0]
    project_path = os.path.join(dot_pitlakq['model_path'], project_name)
    bath_file = os.path.join(project_path, 'preprocessing', 'input',
                             bath_data_file_name)
    res = make_grid(file_name=bath_file, num_x=num_x, num_y=num_y)
    grid_x, grid_y, grid = res['grid_x'], res['grid_y'], res['grid']
    fig = plt.figure()
    ax = fig.add_subplot(111)
    cont = ax.contourf(grid_x, grid_y, grid, spacing,
                       cmap=cm.rainbow,  # pylint: disable=no-member
                       **kwargs)
    fig.colorbar(cont)
    ax.contour(grid_x, grid_y, grid, spacing, colors='k', linewidths=0.5,
               **kwargs)
    ax.set_aspect('equal')
    plt.xticks(rotation=90)
    fig.tight_layout()

    if plot_file_name:
        _create_output_path(project_path)
        plot_file = os.path.join(project_path, 'preprocessing', 'output',
                                 plot_file_name)
        fig.savefig(plot_file, dpi=150)
    if show_plot:
        plt.show()


if __name__ == '__main__':
    main('pitlakq_tut', 'bath_data.txt', num_x=100, num_y=51, copy_to_input=False)
    show_points('pitlakq_tut', show_plot=False)
    show_contours('pitlakq_tut', num_x=100, num_y=51, show_plot=False)
