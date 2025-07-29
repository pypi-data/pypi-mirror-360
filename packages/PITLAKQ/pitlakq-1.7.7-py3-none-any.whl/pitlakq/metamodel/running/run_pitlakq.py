#!/usr/local/bin/python
# coding: utf-8

###############################################################################
# PITLAKQ
# The Pit Lake Hydrodynamic and Water Quality Model
# http://www.pitlakq.com/
# Author: Mike Mueller
# mmueller@hydrocomputing.com
#
# Copyright (c) 2012, Mike Mueller
# All rights reserved.
#
# This software is BSD-licensed.
# See the file license.txt for license.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###############################################################################

from __future__ import absolute_import
from __future__ import print_function

from argparse import ArgumentParser
import calendar
import datetime
import sys
import textwrap
import time
import warnings

import datetime
import numpy

from pitlakq.metamodel.configuration.getconfig import get_config, get_mode
from pitlakq.metamodel.configuration.initialize import initialize_pitlakq
from pitlakq.metamodel.configuration.version import version
from pitlakq.commontools.tools import keep_old_files
from pitlakq.commontools.timing.timetools import get_days_in_month
from pitlakq.commontools.tools import duration_display
import pitlakq.metamodel.balance.balance as total_balance
import pitlakq.metamodel.balance.specie_balance as specie_balance
from pitlakq.metamodel.running import introspection
from pitlakq.metamodel.running import pitlakq_scripter
import pitlakq.metamodel.running.db as db
from pitlakq.preprocessing import create_project
import pitlakq.submodels.lake.lake as lake

# Give py2exe some help.
import pitlakq.metamodel.running.importhelper


numpy.seterr(all='raise')

warnings.simplefilter('error', UserWarning)


class Pitlakq(object):
    """Main class of PITLAKQ.

    The main time loop lives here.
    All submodels will be initiated here.
    """

    def __init__(self,
                 config,
                 start,
                 gw_time_step,
                 lake_time_step,
                 pcg_names,
                 lake_active_const_names,
                 lake_active_minerals_names,
                 rates,
                 mineral_rates,
                 gw_lake_exchange_species='intersection'):
        self.start_time = time.time()
        self.config = config
        self.config.silent = False
        self.db_open = False
        self.open_message_file()
        self.open_db()
        self.start = start
        self.gw_time_step = gw_time_step
        self.lake_time_step = lake_time_step
        self.pcg_names = pcg_names
        self.lake_active_const_names = lake_active_const_names
        self.lake_active_minerals_names = lake_active_minerals_names
        self.rates = rates
        self.mineral_rates = mineral_rates
        self.gw_lake_exchange_species = gw_lake_exchange_species
        self.init_sub_models()
        self.last_until = 0
        self.modmst_time_corrector = 0

    def open_db(self):
        """Open the ZODB database and set `db_open` True.
        """
        self.db = db.SharedDB()
        self.db.open(self.config.database)
        self.db_open = True

    def open_message_file(self):
        """Open a file for log messages.

        All screen output from this module is also written
        to a file. Screen output from CE-QUAL-W2
        and PCGEOFIM can not be captured (?) but can
        be found in their own log files.
        """

        class Tee(object):
            """Branching stdout to a file _and_ the screen.
            """

            def __init__(self, name, mode):
                self.file = open(name, mode)
                self.stdout = sys.stdout
                sys.stdout = self

            def __del__(self):
                sys.stdout = self.stdout
                self.file.close()

            def write(self, data):
                """Write for the file and stdout.
                """
                self.file.write(data)
                self.stdout.write(data)

            def flush(self):
                self.file.flush()
                self.stdout.flush()

        keep_old_files(self.config.message_file_name, 10)
        Tee(self.config.message_file_name, 'w')

    def make_exchange(self):
        """Create the gw exchange object.
        """
        self.ex = gw_lake_exchange.gw_lake_exchange(self.config,
                                                    self.exchange_species,
                                                    self.gw)
        if not self.config.reduced:
            self.ex.get_rabe_info()
            self.ex.make_mapping()
            self.ex.make_area_sum()
            self.ex.get_pcg_geometry()
            self.ex.make_bottom()
            self.ex.make_three_to_one()

    def do_next_exchange(self, delta_t):
        """Perform next gw/lake exchange step.
        """
        self.ex.make_new_mapping(self.date)
        self.ex.put_q(self.date)
        if self.config.gw_migration:
            self.ex.put_conc(self.date)
            self.ex.get_conc(delta_t)
        elif self.config.use_fixed_gw_conc:
            self.ex.put_conc(self.date)

    def find_exchange_species(self):
        """Sort out which species will be exchanged between gw and lake.
        """
        exchange_species_names = []
        if self.gw_lake_exchange_species == 'intersection':
            for name in self.pcg_names.keys():
                for specie in self.pcg_names[name]['conc']:
                    if specie in self.lake_active_const_names:
                        exchange_species_names.append(specie)
        else:
            for specie in self.gw_lake_exchange_species:
                specie_in_both = False
                for name in self.pcg_names.keys():
                    if (specie in self.lake_active_const_names and
                        specie in self.pcg_names[name]['conc']):
                        exchange_species_names.append(specie)
                        specie_in_both = True
                if not specie_in_both:
                    msg = """Specie %s is supposed to be exchanged between
                    lake and groundwater, but is not a specie of lake AND
                    groundwater.

                    Please take specie out of exchange list or make it a specie
                    of lake AND groundwater""" % specie
                    print(textwrap.dedent(msg))
                    self.gw.done()
                    sys.exit()
        if self.config.precalc_gw_conc:
            self.exchange_species = exchange_species_names
        else:
            self.exchange_species = self.gw.find_species_location(
                                            exchange_species_names)

    def init_sub_models(self):
        """Initialize all used sub models.
        """
        self.dual_porosity = self.config.dual_porosity_coupling
        self.gw_lake_coupling = self.config.gw_lake_coupling
        if self.gw_lake_coupling:
            if self.config.gw_model == 'modmst':
                self.config.distributed_gw_temperature = True
            elif not hasattr(self.config, 'distributed_gw_temperature'):
                self.distributed_gw_temperature = False
        begin = datetime.datetime(*self.config.start.timetuple()[:6])
        # gw may start earlier than lake but not later
        gw_begin = datetime.datetime(*self.config.gw_start.timetuple()[:6])
        self.date = begin
        if self.config.lake_calculations:
            if not self.config.silent:
                print('init lake ')
            self.lake = lake.Lake(self.config,
                                  self.lake_active_const_names,
                                  self.lake_active_minerals_names,
                                  self.rates,
                                  self.mineral_rates,
                                  begin)
        step = get_days_in_month(begin) * self.gw_time_step
        if self.config.restart:
            days_in_month = get_days_in_month(begin +
                                              datetime.timedelta(days=1))
            step = days_in_month * self.gw_time_step
            end_first_period = begin + datetime.timedelta(days=step)
        else:
            end_first_period = begin + datetime.timedelta(days=step-1)
        if self.gw_lake_coupling or self.config.gw_calculations:
            if not self.config.silent and not self.config.use_saved_gw_q:
                print('init gw')
            if self.config.gw_model == 'pcg':
                from pitlakq.submodels.gw import gw
                self.gw = gw.GwModel(self.config, self.pcg_names, gw_begin,
                                     end_first_period)
                if not self.config.use_saved_gw_q:
                    self.gw.do_pcg_init_run()
                    self.gw.read_binary_output()
            elif self.config.gw_model == 'modmst':
                from pitlakq.numericalmodels.existingmodels.modmst import \
                     modmst
                print('modmst active')
                self.modmst = modmst.Modmst(self.config)
            else:
                print(72*'#')
                print('gw models has to be pcg or modmst')
                print('model %s not supported' % self.config.gw_model)
                print(72*'#')
                sys.exit(1)
        if self.dual_porosity:
            if self.config.gw_model != 'pcg':
                print('dual porosity supported for gw model pcg only')
                sys.exit(1)
            self.gw.init_dual_porosity()
            self.gw.dual_porosity.update(end_first_period.ticks() -
                                         self.date.ticks())
        if self.gw_lake_coupling and self.config.lake_calculations:
            if self.config.gw_model == 'pcg':
                self.find_exchange_species()
                self.make_exchange()
                self.do_next_exchange(step*86400)
        if self.gw_lake_coupling or self.config.gw_calculations:
            if self.config.gw_model == 'pcg':
                if not self.config.use_saved_gw_q:
                    self.gw.write_binary_output()
                    self.gw.init_pcg_output()
                    self.gw.write_pcg_out(end_first_period)
            elif self.config.gw_model == 'modmst':
                self.modmst_done = next(self.modmst)
                end_first_period = begin + datetime.timedelta(
                    days=self.modmst.dt)
            else:
                print(72*'#')
                print('gw models has to be pcg or modmst')
                print('model %s not supported' % self.config.gw_model)
                print(72*'#')
                sys.exit(1)
        self.date = end_first_period
        if self.config.precalc_gw:
            import pitlakq.submodels.gw.precalc_gw_in_out as precalc_gw_in_out
            if self.config.precalc_gw_conc:
                self.find_exchange_species()
            else:
                self.exchange_species = None
            self.pre_gw = precalc_gw_in_out.PrecalcGwInOut(
                self.config,
                self.config.precal_gw_q_file_name,
                self.config.precal_gw_key_file_name,
                self.config.precal_gw_distrib_file_name,
                self.exchange_species)
            self.config.pre_gw = self.pre_gw
            self.config.pitlakq_date = self.date
        if self.config.gwh:
            assert self.config.precalc_gw is False
            assert self.gw_lake_coupling is False
            assert self.config.gw_calculations is False
            from pitlakq.submodels.gw import gwh
            self.gwh = gwh.GroundwaterLakeLevel(self.config)
            self.gwh.read_data()
        if self.config.loading:
            from pitlakq.submodels.loading.loading import Loading
            self.lake.loading = Loading(self.config)
            self.lake.loading_step = datetime.timedelta(
                days=self.config.loading_step)
            self.lake.last_loading_date = datetime.datetime(1, 1, 1)
        self.balance = total_balance.TotalBalance(self.config)
        self.specie_balance = specie_balance.SpecieBalance(self.config)

    def run(self, gw_time_step, lake_time_step, first, last):
        """Run the main time loop.
        """
        if first and self.config.precalc_gw:
            self.pre_gw.set_qs(self.date)
            if self.config.precalc_gw_conc:
                self.pre_gw.set_conc()
        if first and self.config.gwh:
            self.gwh.set_q()
        if self.config.lake_calculations:
            self.lake.w2.year = self.lake.year = self.date.year
            is_leap_year = calendar.isleap(self.date.year)
            self.lake.w2.is_leap_year = self.lake.is_leap_year = is_leap_year
            if self.gw_lake_coupling and self.config.gw_model == 'pcg':
                self.lake.w2.read_pcg_result()
        if self.config.lake_calculations:
            jday = self.lake.w2.jday_converter.make_jday_from_date(self.date)
            until = jday + 1
            self.last_until = until
            print('run time:', duration_display(time.time() - self.start_time))
            print('until:', until)
            self.lake.run(until,
                          lake_time_step,
                          self.config.w2_output_step)
            if self.config.lake_calculations:
                self.balance.check_w2_balance(self.date)
                self.specie_balance.write_balance(self.date)
                self.config.w2.offset_balance = False
        if not self.config.silent:
            print()
            print(self.date.strftime('%d. %B %Y'))
        days_in_month = get_days_in_month(self.date +
                                          datetime.timedelta(days=1))
        step = days_in_month * self.gw_time_step
        if self.config.gw_lake_coupling and self.config.gw_model == 'modmst':
            step = self.modmst.dt
        next_time_step = self.date + datetime.timedelta(days=step)
        # rerun of pcg
        if (first and self.gw_lake_coupling and self.config.gw_model == 'pcg'
            and self.config.rerun_pcg):
            if not self.config.silent:
                print('rerun of pcg')
            old_step = get_days_in_month(self.date) * self.gw_time_step
            if (self.gw_lake_coupling or self.config.gw_calculations
                and not self.config.use_saved_gw_q):
                self.gw.run(self.date, rerun=1)
                self.gw.read_binary_output()
            if self.dual_porosity:
                self.gw.set_dual_porosity_values()
                self.gw.dual_porosity.update(old_step * 86400)
            if (self.gw_lake_coupling or self.config.gw_calculations
                and not self.config.use_saved_gw_q):
                self.gw.write_binary_output()
                self.gw.write_pcg_out(self.date)
        # pcg next time step
        if not last:
            if self.gw_lake_coupling or self.config.gw_calculations:
                if self.config.gw_model == 'pcg':
                    if not self.config.use_saved_gw_q:
                        self.gw.run(next_time_step)
                        self.gw.read_binary_output()
                elif self.config.gw_model == 'modmst':
                    self.modmst_done = next(self.modmst)
                else:
                    print(72*'#')
                    print('gw models has to be pcg or modmst')
                    print('model %s not supported' % self.config.gw_model)
                    print(72*'#')
                    sys.exit(1)
            if self.gw_lake_coupling:
                if self.config.gw_model == 'pcg':
                    self.do_next_exchange(step * 86400)
            if self.config.precalc_gw:
                self.pre_gw.set_qs(self.date)
                if self.config.precalc_gw_conc:
                    self.pre_gw.set_conc()
            if self.config.gwh:
                self.gwh.set_q()
            if self.config.gw_model == 'pcg':
                if self.dual_porosity:
                    self.gw.set_dual_porosity_values()
                    self.gw.dual_porosity.update(step * 86400)
                if (not self.config.use_saved_gw_q and
                    (self.gw_lake_coupling or self.config.gw_calculations)):
                    self.gw.write_binary_output()
                    self.gw.write_pcg_out(next_time_step)
            self.date += datetime.timedelta(days=step)

    def cleanup(self):
        """Cleanup and close database.
        """
        if self.db_open:
            self.close_db_conncetion()
        if (self.gw_lake_coupling and not self.config.use_saved_gw_q and
            self.config.gw_model == 'pcg'):
            self.gw.done()
            self.gw.pcg_out.close()
        if self.config.lake_calculations:
            self.lake.cleanup()
        if (self.config.dual_porosity_coupling and
            self.config.gw_model == 'pcg'):
            self.gw.dual_porosity.write_mobile_conc()
        if not self.config.reduced:
            sys.exit()

    def close_db_conncetion(self):
        """Close the ZODB.
        """
        self.db.close()
        self.db_open = False


def get_cmd_line():
    """Read commandline parameters.
    """
    mode, _ = get_mode()
    parser = ArgumentParser(prog='pitlakq')
    parser.add_argument("-v", "--version", action="store_true",
                      dest="version",
                      help="show version info and exit")

    subparsers = parser.add_subparsers()
    parser_init = subparsers.add_parser('init',
        help="initialize PITLAKQ and create `.pitlakq`")
    parser_init.set_defaults(func=initialize_pitlakq)
    parser_run = subparsers.add_parser(
        'run',
        description='run a project',
        help='start the calculation of a model')
    parser_run.add_argument('project_name', type=str,
                            help='name of project to be calculated')

    def run_project(args):
        """Run a project.
        """
        run(args.project_name)

    parser_run.set_defaults(func=run_project)
    parser_create = subparsers.add_parser(
        'create',
        description='create a new project',
        help='creates a new project folder with empty sub folders')
    parser_create.add_argument('project_name', type=str,
                                help='name of project to be created')

    def create(args):
        """Create a new project.
        """
        create_project.main(args.project_name)

    parser_create.set_defaults(func=create)

    if  mode == 'deployment mode':
        # This only makes sense when running as exe.
        # When Python and pitakq is installed it is much easier to
        # run a script directly.
        parser_script = subparsers.add_parser(
            'script',
            description='run a Python script',
            help='runs a Python script with all modules of pitlakq available')
        parser_script.add_argument('script_name', type=str,
                                    help='name of Python script to be run')

        def run_script(args):
            """Run a script.
            """
            pitlakq_scripter.main(args.script_name)

        parser_script.set_defaults(func=run_script)

    parser_introspect = subparsers.add_parser(
        'introspect',
        description='find out internals',
        help='find out internals of PITLAKQ or your projects')
    parser_introspect.add_argument("-w", "--w2-names", dest="w2_names",
                                    action="store_true", help="show w2 names")
    parser_introspect.add_argument("-p", "--projects", dest='projects',
                                   action="store_true",
                                   help='show all projects')


    def introspect(args):
        """Do introspection.
        """
        if args.w2_names:
            introspection.show_w2_names()
        elif args.projects:
            introspection.show_projects()
        else:
            parser_introspect.print_help()

    parser_introspect.set_defaults(func=introspect)

    return parser


def main():
    """Start the program.
    """
    parser = get_cmd_line()
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        if args.version:
            print('PITLAKQ version: %s' % version)
        else:
            parser.print_help()


def run(project_name):
    """Run pitlakq.
    """
    prg_start = time.time()
    config = get_config(project_name)
    try:
        model = Pitlakq(config,
                        config.start,
                        config.gw_time_step,
                        config.lake_time_step,
                        config.pcg_names,
                        config.lake_active_const_names,
                        config.lake_active_minerals_names,
                        config.rates,
                        config.mineral_rates)
        last = False
        if config.gw_model == 'modmst':
            config.number_of_gw_time_steps = 99999
        for step in range(config.number_of_gw_time_steps):
            first = False
            if step == config.number_of_gw_time_steps - 1:
                last = True
            if step == 0:
                first = True
            model.run(config.gw_time_step, config.lake_time_step, first,
                        last)
            if (model.config.gw_lake_coupling and
                model.config.gw_model == 'modmst' and model.modmst_done):
                break
        prg_end = time.time()
        model.cleanup()
        if not config.silent:
            print('runtime: %s' % str(
                datetime.timedelta(seconds=prg_end - prg_start)))
    except:
        if 'model' in dir():
            try:
                if model.db_open:
                    model.close_db_conncetion()
            except AttributeError:
                pass
            if hasattr(model, 'gw'):
                model.gw.done()
                if hasattr(model.gw, 'pcg_out'):
                    model.gw.pcg_out.close()
        if not config.silent:
            prg_end = time.time()
            print()
            print('runtime: %s' % str(
                datetime.timedelta(seconds=prg_end - prg_start)))
        raise


if __name__ == '__main__':

    main()

