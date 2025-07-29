"""Get depth profile of a model variable."""


from matplotlib import pyplot as plt
import netCDF4


class DepthProfile:
    """Depth profile of one variable at specific location and time."""

    def __init__(self,
                 nc_file_name,
                 date,
                 date_by='day',
                 location=5,
                 variable_name='t2',
                 ):
        # pylint: disable-msg=too-many-arguments
        self.nc_file = netCDF4.Dataset(  # pylint: disable-msg=no-member
            nc_file_name, mode='r', format='NETCDF3_CLASSIC')
        self.date = date
        self.date_by = date_by
        self.location = location
        self.variable_name = variable_name
        self.time_step = self.find_time_step()
        self.values = self.get_variable_profile()

    def find_time_step(self):
        """Find time step for given date.

        Depending on the value of `date_by` the date will be resolved
        by day, minute, or second.
        """
        date_match = {
            'day': 3,
            'hour': 4,
            'minute': 5,
            'second': 6,
        }
        match_numbers = date_match[self.date_by]
        time_steps = self.nc_file.variables['timesteps']
        steps = self.nc_file.dimensions['time']
        for step in range(len(steps)):
            current_date = time_steps[step]
            if (tuple(current_date)[:match_numbers] ==
                    self.date.timetuple()[:match_numbers]):
                return step
        raise ValueError(f'date {self.date} not found')

    def get_variable_profile(self):
        """Get values for variable."""
        vars_ = self.nc_file.variables
        values = vars_[self.variable_name][self.time_step, :, self.location]
        cell_bottoms = vars_['zu'][:]
        cell_heights = vars_['hactive'][self.time_step, :, self.location]
        return {'depths': cell_bottoms + cell_heights / 2,
                self.variable_name: values}

    def plot_depth_profile(self, value_text=''):
        """Plot a depth profile"""
        _, ax = plt.subplots()  # pylint: disable-msg=invalid-name
        ax.plot(self.values[self.variable_name], self.values['depths'])
        title_value_text = 'for ' + value_text if value_text else ''
        ax.set_title(
            f'Depth profile {title_value_text} at location {self.location} '
            f'at time {self.date}')
        if value_text:
            ax.set_xlabel(value_text)
        ax.set_ylabel = 'depth in m'
        plt.show()

    def save_values(self, file_name=None, sep=','):
        """Save value for depth profile to a file"""
        if not file_name:
            file_name = f'{self.variable_name}_{self.date}.txt'
        with open(file_name, 'w', encoding='utf-8') as fobj:
            fobj.write(f'depths{sep}{self.variable_name}\n')
            for depth, value in zip(self.values['depths'],
                                    self.values[self.variable_name]):
                fobj.write(f'{depth}{sep}{value}\n')


def main(
        nc_file_name,
        date,
        variable_name,
        location=5,
        date_by='day',
        save=True,
        show=True,
        save_file_name=None,
        variable_text=None,
        ):
    """
    nc_file_name - name the NetCDF output file
    date - date for which values will be displayed
          `datetime.date` or `datetime.datetime` object
    variable_name - name of variable to show
    location - model section
    date_by - time resolution, if saved daily only `day` makes sense
    save - save result to a text file
    show - show plot
    save_file_name - file name for saving, default is a combination of
                    variable name and date
    variable_text - text for plot title, defaults to variable name
    """
    # pylint: disable-msg=too-many-arguments
    depth_profile = DepthProfile(
        nc_file_name=nc_file_name,
        date=date,
        variable_name=variable_name,
        date_by=date_by,
        location=location,
    )
    if save:
        depth_profile.save_values(file_name=save_file_name)
    if not variable_text:
        variable_text = variable_name
    if show:
        depth_profile.plot_depth_profile(value_text=variable_text)
