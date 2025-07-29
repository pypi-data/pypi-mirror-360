"""
Extract and show contour for depth and time slot.
"""
from __future__ import print_function

import datetime
import os
import time
import sys

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy
import netCDF4

# suppress has-no-member message for numpy
# pylint: disable-msg=W0142
# pylint: disable-msg=E1101


LANGUAGE = 'English' # 'German'

MAX_DAYS_OFF = 10
MEASURED_TIME_WIDTH = 5
MEASURED_TIME_THICKENESS = 1
LABELS = {}
NAMES = {}
XAXIS = {'show_first': True,
         'show_last': True,
         'rotation': 30,
         'font_size': 8,
         # None: show all years
         # list with years: show only these, e.g. [2005, 2010, 2015]
         'years': None,
         # None: show only first month of the year
         # list with month: show only these, possible values: range(1, 13)
         'months': None,
         #'months': range(1, 13),
         # None: show only first day of the month
         # list with days: show only these, possible values: range(1, 32)
         'days': None,
         #'days': range(1, 32),
         # distance between x axis and bottom of plot
         # prevents that label is outside of screen
         'bottom': 0.12}
PROJECT = {'description': '',
           'font_size': 6,
           'position': (0.02, 0.005),
           'show_date': True,
           'show_file_name': True}


def configure_language():
    """Use the appropriate language for all labels.
    """
    names_german = {'t2': 'Temperatur in C',
                    'u': 'Geschwindigkeit in m/s',
                    'vactive': 'Aktives Volumen im m3',
                    'cl': 'Chloridkonzentration in mg/l',
                    'na': 'Natrium in mg/l',
                    'tra': 'Tracer in mg/l',
                    'dox': 'geloester Sauerstoff in mg/l',
                    'ca': 'Kalzium in mg/l',
                    'fe': 'Eisen(II) in mg/l',
                    'fe3': 'Eisen(III) in mg/l',
                    'mg': 'Magnesium in mg/l',
                    'al': 'Aluminium in mg/L',
                    'ph': 'pH-Wert',
                    'so4': 'Sulfat in mg/l',
                    'po4': 'Phosphat in mg/l',
                    'iceth': 'Eisdicke in m'}

    names_english = {'t2': 'Temperature in C',
                     'rho': 'Density kg/m3',
                     'u': 'Velocity in m/s',
                     'vactive': 'Active Volume im m3',
                     'cl': 'Chlorid in mg/L',
                     'ka': 'Potassium in mg/L',
                     'na': 'Sodium in mg/L',
                     'tra': 'Tracer in mg/L',
                     'dox': 'Dissolved Oxygen in mg/L',
                     'ca': 'Calcium in mg/L',
                     'fe': 'Iron(II) in mg/L',
                     'fe3': 'Iron(III) in mg/L',
                     'mg': 'Magnesium in mg/L',
                     'mn': 'Maganese in mg/L',
                     'al': 'Aluminum in mg/L',
                     'ph': 'pH-value',
                     'so4': 'Sulphate in mg/L',
                     'po4': 'Phosphate in mg/L',
                     'cd': 'Cadmium in mg/L',
                     'pb': 'Lead in mg/L',
                     'zn': 'Zinc in mg/L',
                     'ars': 'Arsenic in mg/L',
                     'co': 'Cobalt in mg/L',
                     'hg': 'Mercury in mg/L',
                     'arg': 'Silver in mg/L',
                     'cr': 'Chromium in mg/L',
                     'cu': 'Copper in mg/L',
                     'mo': 'Molybdenum in mg/L',
                     'ni': 'Nickel in mg/L',
                     'se': 'Selenium in mg/L',
                     'tl': 'Thallium in mg/L',
                     'ur': 'Uranium in mg/L',
                     'sb': 'Antimony in mg/L',
                     'ba': 'Barium in mg/L',
                     'be': 'Beryllium in mg/L',
                     'bi': 'Bismuth in mg/L',
                     'bor': 'Boron in mg/L',
                     'sr': 'Strontium in mg/L',
                     'sn': 'Tin in mg/L',
                     'ti': 'Titanium in mg/L',
                     'van': 'Vanadium in mg/L',
                     'iceth': 'Ice Thickness in m',
                     'tds': 'Total Dissolved Solids in mg/L',
                     'feoh3': 'Fe(OH)3 in mg/L',
                     'algae': 'Algae in mg/L'
                     }

    NAMES.update({'German': names_german,
                  'English': names_english}[LANGUAGE])

    labels_german = {}
    labels_german['time_unit'] = 'Tagen'
    labels_german['subtitles'] = {'measured': 'Messwerte',
                                  'modelled': 'Modellergebnisse'}
    labels_german['title_species'] = '%s'
    labels_german['title_point'] = ' fuer das Segment %d '
    labels_german['title_deepest_point'] = ' fuer den tiefsten Punkt '
    labels_german['title_date'] = 'von %s bis %s'
    labels_german['date_format'] = '%d.%m.%Y'
    labels_german['ylabel'] = 'm NHN'
    labels_german['xlabel'] = 'Datum'

    labels_english = {}
    labels_english['time_unit'] = 'days'
    labels_english['subtitles'] = {'measured': 'Measured Values',
                                  'modelled': 'Modelling Results'}
    labels_english['title_species'] = '%s'
    labels_english['title_point'] = ' for Segment %d '
    labels_english['title_deepest_point'] = ' for the Deepest Point '
    labels_english['title_date'] = 'from %s to %s'
    labels_english['date_format'] = '%m/%Y'
    labels_english['ylabel'] = 'm ASL' #'m Depth'  # 'm AHD'
    labels_english['xlabel'] = 'Date'

    LABELS.update({'German': labels_german,
                   'English': labels_english}[LANGUAGE])


class Contour(object):
    """Extract and show depth-time-contour.
    """
    def __init__(self, output_file_name, location, species,
                 target_path, time_slot=(None, None), show_graph=True,
                 show_ice=True, is_deepest=False, no_show_below=-9999999,
                 lower_border=-9999999, show_water_level=False,
                 upper_border=99999999, ph_limit=8):
        configure_language()
        self.output_file_name = output_file_name
        self.location = location
        self.species = species
        self.target_path = target_path
        self.time_slot = list(time_slot)
        self.show_graph = show_graph
        self.show_ice = show_ice
        self.is_deepest = is_deepest
        self.no_show_below = no_show_below
        self.show_water_level = show_water_level
        self.lower_border = lower_border
        self.upper_border = upper_border
        self.ph_limit = ph_limit
        self.data = {}
        self.ice_thickness = None
        self.ice_location = 0
        self.time_unit = LABELS['time_unit']
        self._active_time_steps = None
        self._active_data_points = 0
        self._tick_locations = None
        self._tick_labels = None
        self._figures = {}
        self._check_names()

    def _check_names(self):
        """Make sure that all species do have axis labels.
        """
        for specie in self.species:
            name = specie['name']
            try:
                NAMES[name]
            except KeyError:
                print('Found no entry for {0}.'.format(name))
                print('Please provide a name for the axis label.')
                sys.exit(1)

    def read_data(self):
        """Read netCDF data.
        """
        # pylint:disable-msg=W0201
        loc = self.location - 1
        fobj = netCDF4.Dataset(self.output_file_name, 'r',
                               format='NETCDF3_CLASSIC')
        self.time_steps = fobj.variables['timesteps']
        start_index, end_index = self._find_time_indices()
        self.start_index = start_index
        self._active_time_steps = self.time_steps[start_index:end_index]
        self.zcoord = self._make_zcoords(
            layer_bottoms=fobj.variables['zu'][:])
        self.xcoord = numpy.arange(start_index, end_index)
        vactive = fobj.variables['vactive'][start_index:end_index, :, loc]
        inactive_below = 0
        for coord in self.zcoord[::-1]:
            if coord < self.no_show_below:
                inactive_below += 1
            else:
                break
        if inactive_below:
            vactive[:, -inactive_below:] = False
        cutoff_below = 0
        for coord in self.zcoord[::-1]:
            if coord < self.lower_border:
                cutoff_below  += 1
            else:
                break
        if cutoff_below:
            vactive = vactive [:, :-cutoff_below]
            self.zcoord = self.zcoord[:-cutoff_below]
        self.vactive = vactive
        mask = numpy.where(vactive > 0, False, True)
        mask[:, -1] = False
        self._active_data_points = numpy.sum(mask)
        water_level = fobj.variables['elws'][start_index:end_index, loc]
        upper_border = self.upper_border
        water_level[water_level>upper_border] = upper_border
        self.water_level = water_level
        get_active = []
        for mask_step in mask:
            value = numpy.where(mask_step == False)[0][0]
            get_active.append(value + 1)
            mask_step[value - 1] = False
        for specie in self.species:
            if cutoff_below:
                value = fobj.variables[specie['name']][
                    start_index:end_index, :-cutoff_below, loc]
            else:
                value = fobj.variables[specie['name']][
                    start_index:end_index, :, loc]
            for index, get_a in enumerate(get_active):
                for n in range(1, 3):
                    value[index, get_a - n] = value[index, get_a]
            if specie['name'] == 'ph':
                value[value > self.ph_limit] = self.ph_limit
            value[:, -1] = value[:, -2]
            value = numpy.ma.masked_array(value, mask=mask)
            value[:, -1] = value[:, -2]
            self.data[specie['name']] = value.transpose()
        if self.show_ice:
            self.ice_thickness = fobj.variables['iceth'][start_index:end_index,
                                                         loc]
            self.ice_location = max(self.water_level) + 1.0
        fobj.close()

    @staticmethod
    def _make_zcoords(layer_bottoms):
        zcoord = layer_bottoms.copy()
        bottom = None
        top = layer_bottoms[0]
        for bottom_index, entry in enumerate(zcoord[::-1]):
            if  isinstance(entry, numpy.float64):
                bottom = entry
                break
        centers = (layer_bottoms[:-1] - layer_bottoms[1:]) / 2
        zcoord[:-1] = layer_bottoms[1:] + centers
        zcoord[-2] = layer_bottoms[-2]
        zcoord[1:] = zcoord[:-1]
        zcoord[0] = top + (layer_bottoms[0] - layer_bottoms[1]) * 5
        zcoord[-bottom_index:] = bottom
        return zcoord

    def _find_time_indices(self):
        """Find indices for start and end time.
        """
        time_indices = [0, len(self.time_steps[:]) - 1]
        start = self.time_slot[0]
        end = self.time_slot[1]
        if start:
            time_indices[0], _ = self._find_time(start)
        else:
            self.time_slot[0] = (datetime.datetime(
                *self.time_steps[time_indices[0]][:6]))
        if end:
            time_indices[1], _ = self._find_time(end)
        else:
            self.time_slot[1] = (datetime.datetime(
                *self.time_steps[time_indices[1]][:6]))
        self._time_indices = time_indices
        return time_indices

    def _find_time(self, time_):
        """Find right time.
        """
        min_diff = datetime.timedelta(int(1e5))
        index = 0
        for i, time_step in enumerate(self.time_steps[:]):
            diff = abs(datetime.datetime(*time_step[:6]) - time_)
            if diff < min_diff:
                index = i
                min_diff = diff
        if min_diff.days > MAX_DAYS_OFF:
            raise ValueError('date not found diff: %d days' % min_diff.days)
        return index, min_diff

    def show(self):
        """Show all graphs.
        """
        for specie in self.species:
            name = specie['name']
            print(name)
            if name not in self._figures:
                fig = self._draw(specie)
                self._figures[name] = fig
            fig = self._figures[name]
            if not 'inline' in matplotlib.get_backend():
                fig.show()
        plt.show()

    def save_figure(self):
        """Draw figures for all species.
        """
        for specie in self.species:
            name = specie['name']
            file_name = os.path.join(self.target_path, '%s.png' % name)
            print('saving %s' % name)
            if name not in self._figures:
                fig = self._draw(specie)
                self._figures[name] = fig
            fig = self._figures[name]
            fig.savefig(file_name)

    def _draw(self, specie):
        """Draw one graph.
        """
        if specie['name'] == 'ph':
            cmap = plt.cm.jet_r
        else:
            cmap = plt.cm.jet
        fig = plt.figure(figsize=(16, 8))
        levels = specie.get('levels', 'auto')
        name = specie['name']
        zcoord = self.zcoord
        data = {'modelled': self.data[name]}
        titles = LABELS['subtitles']
        set_label = {'measured': False, 'modelled': True}
        if 'measurement' in specie:
            if levels == 'auto':
                msg = ('Auto scaling not allowed when measured values are'
                       ' given. Please specify level range or do NOT provide'
                       ' measured values.')
                print('#' * 72)
                print(msg)
                print('#' * 72)
                raise ValueError(msg)
            all_axies = {'measured': fig.add_subplot(211),
                         'modelled': fig.add_subplot(212)}
            data['measured'] = self._get_measured(specie['measurement'])
        else:
            all_axies = {'modelled': fig.add_subplot(111)}
        if self.is_deepest:
            title_point = LABELS['title_deepest_point']
        else:
            title_point = LABELS['title_point'] % self.location
        title = (LABELS['title_species'] % NAMES[name] +
                 title_point + LABELS['title_date']
                   % (self.time_slot[0].strftime(LABELS['date_format']),
                      self.time_slot[1].strftime(LABELS['date_format'])))
        fig.text(0.5, 0.95, title, horizontalalignment='center',
                 fontproperties=FontProperties(size=14))
        if name == 'u':
            zcoord = self.zcoord[::-1][:]
        for axis_name in all_axies:
            cont = self._draw_subplot(all_axies[axis_name], titles[axis_name],
                                      data[axis_name], zcoord, levels, cmap,
                                      set_label[axis_name])
        plt.subplots_adjust(bottom=XAXIS['bottom'], right=0.8, top=0.9)
        cax = plt.axes([0.85, 0.1, 0.03, 0.8])
        plt.colorbar(cont, cax=cax)
        plt.grid(True)
        return fig

    def _draw_subplot(self, axis, title, data, zcoord, levels, cmap,
                      set_label=True):
        """Draw one subplot.
        """
        # Fill values of inactive cells above the water level
        # with values from last active cell below.
        # This avoids ugly artifacts due equidistant grid in `contourf`.
        if self.show_water_level:
            for time_index in range(data.shape[-1]):
                data_col = data[:, time_index]
                # iterating from below
                below_value = False
                replace = False
                for col_index in range(len(data_col) - 1, -1, -1):
                    entry = data_col[col_index]
                    if not isinstance(entry, numpy.float64):
                        if replace and entry.mask == True:
                            data[col_index, time_index] = below_value
                    else:
                        replace = True
                        below_value = entry

        axis.set_title(title)
        if levels == 'auto':
            cont = axis.contourf(self.xcoord, zcoord, data, cmap=cmap)
        else:
            cont = axis.contourf(self.xcoord, zcoord, data, levels, cmap=cmap)
        axis.fill_between(self.xcoord, self.water_level, self.zcoord[0],
                          facecolor='white', color='white')
        if self.show_water_level:
            axis.plot(self.xcoord, self.water_level)
        if self.show_ice:
            x = self.xcoord[numpy.where(self.ice_thickness > 0.02, True,
                                        False)]
            axis.plot(x, [self.ice_location] * len(x), 'bs')
        axis.set_ylabel(LABELS['ylabel'])
        if set_label:
            axis.set_xlabel(LABELS['xlabel'])
        axis.xaxis.set_major_locator(self.major_locator)
        if set_label:
            axis.xaxis.set_major_formatter(self.major_formatter)
        else:
            axis.xaxis.set_major_formatter(plt.FixedFormatter([]))
        axis.xaxis.set_tick_params(
            rotation=XAXIS['rotation'],
            labelsize=XAXIS['font_size'])
        text = PROJECT['description']
        if PROJECT['show_date']:
            text += '\nPlot creation date: ' + time.ctime()
            text += ' | Output file date: '
            text += time.asctime(time.localtime(
                                 os.path.getmtime(self.output_file_name)))
            text += ' | Number of time steps: %d' % (
                len(self._active_time_steps))
            text += ' | Number of data points: %d' % (
                self._active_data_points)
        if PROJECT['show_file_name']:
            text += '\n' + os.path.abspath(self.output_file_name)
        xpos, ypos = PROJECT['position']
        plt.figtext(xpos, ypos, text,
                    fontproperties=FontProperties(size=PROJECT['font_size']))
        return cont

    @property
    def major_locator(self):
        """Find tick locations.
        """
        if not self._tick_locations:
            locations = []
            first_date = datetime.datetime(*self._active_time_steps[0])
            last_date = datetime.datetime(*self._active_time_steps[-1])
            date_strings = []
            if XAXIS['years']:
                years = set(XAXIS['years'])
            else:
                years = set(range(first_date.year, last_date.year + 1))
            if XAXIS['months']:
                months = set(XAXIS['months'])
            else:
                months = set([1])
            if XAXIS['days']:
                days = set(XAXIS['days'])
            else:
                days = set([1])
            if XAXIS['show_first']:
                locations.append(0)
                date_strings.append(first_date.strftime(LABELS['date_format']))
            seen = set()
            for loc, date_array in enumerate(self._active_time_steps[1:]):
                loc += self.start_index
                date = datetime.datetime(*date_array)
                if (
                    #(date.day in days) and
                    #(date.month in months) and
                    #date.day == 1 and
                    #date.month == 1 and
                    (date.year not in seen) and
                    (date.year in years)):
                    seen.add(date.year)
                    locations.append(loc)
                    date_strings.append(date.strftime(LABELS['date_format']))
            if XAXIS['show_last']:
                locations.append(loc)
                date_strings.append(last_date.strftime(LABELS['date_format']))
            self._tick_locations = plt.FixedLocator(locations)
            self._tick_labels = plt.FixedFormatter(date_strings)
        return self._tick_locations

    @property
    def major_formatter(self):
        """Format the tick lables.
        """
        # XXX ???
        # if not self._tick_labels:
        #    self.major_locator
        return self._tick_labels

    def save(self):
        """Save data to file.
        """
        for specie in self.species:
            name = specie['name']
            fname = '%s.txt' % (name,)
            fobj = open(os.path.join(self.target_path, fname), 'w')
            fobj.write('%10s\t %10s\t %10s\n' % ('time', 'coord', 'value'))
            for coord, value in zip(self.zcoord, self.data[name]):
                for time_ in range(value.shape[0]):
                    fobj.write('%10.2f\t %10.2f\t %10.5f\n' % (time_, coord,
                                                               value[time_]))
            fobj.close()
            print('saved: %s' % fname)

    def _get_measured(self, file_name):
        """Get measured data. Return as masked array.
        """
        time_indices = {}
        z_indices = {}

        def make_date(text):
            """Convert text to date.
            """
            return datetime.datetime(*time.strptime(text, '%d.%m.%Y')[:3])

        def find_z_index(value):
            """Find closest index for depth.
            Assume 0.5 m steps, i.e. 0.5, 1.5, 2.5 etc.
            """
            value = int(value) + 0.5
            try:
                index = int(numpy.nonzero(self.zcoord == value)[0])
            except TypeError:
                print('ignoring value outside model grid')
                print('level:', value)
                return
            return z_indices.setdefault(value, index)
        convert = {'date': make_date, 'depth': float, 'conc': float}
        fobj = open(file_name)
        header = next(fobj).split()
        data = {}
        for head in header:
            data[head] = []
        for line in fobj:
            line_data = line.split()
            if line_data:
                for index, head in enumerate(header):
                    try:
                        data[head].append(convert[head](line_data[index]))
                    except ValueError:
                        print(line)
                        raise
        fobj.close()
        result_array = numpy.zeros(self.vactive.shape, dtype=numpy.float64)
        for date, depth, conc in zip(data['date'], data['depth'],
                                     data['conc']):
            try:
                time_index = time_indices.setdefault(date,
                                                     self._find_time(date)[0])
            except ValueError:
                continue
            z_index = find_z_index(depth)
            if not z_index:
                continue
            result_array[time_index - MEASURED_TIME_WIDTH:
                         time_index + MEASURED_TIME_WIDTH,
                         z_index - MEASURED_TIME_THICKENESS:
                         z_index + MEASURED_TIME_THICKENESS] = conc
        mask = numpy.where(result_array > 0, False, True)
        result_array = numpy.ma.masked_array(result_array, mask=mask)
        return result_array.transpose()

def main(nc_out, species, location, tar=os.getcwd(), time_slot=(None, None),
         show_ice=False, save=False, show=True, no_show_below=-9999999,
         lower_border=-9999999, show_water_level=True,
         upper_border=999999999):
    """Make depth_time plot.
    """
    contour = Contour(nc_out, location, species, tar, time_slot=time_slot,
                      show_ice=show_ice, no_show_below=no_show_below,
                      lower_border=lower_border,
                      show_water_level=show_water_level,
                      upper_border=upper_border)
    contour.read_data()
    if show:
        contour.show()
    if save:
        contour.save_figure()
