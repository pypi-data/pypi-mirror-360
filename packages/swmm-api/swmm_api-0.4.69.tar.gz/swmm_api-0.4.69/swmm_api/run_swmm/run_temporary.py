import shutil
import tempfile
from pathlib import Path

from .run_pyswmm import swmm5_run_progress
from .run_swmm_toolkit import swmm5_run_owa
from .run_epaswmm import swmm5_run_epa
from .run import swmm5_run
from ._run_helpers import get_result_filenames
from .._io_helpers import CONFIG
from ..input_file._type_converter import is_nan, is_placeholder, is_not_set
from ..input_file.sections import TimeseriesFile
from ..output_file import SwmmOutput
from ..report_file import SwmmReport, read_lid_report
from ..input_file import SEC, SwmmInput
from ..input_file.section_lists import GEO_SECTIONS, GUI_SECTIONS


class SwmmResults:
    """Object to load results."""
    def __init__(self, inp, fn_inp):
        self.inp = inp
        self._rpt = None
        self._out = None
        self._lid_rpts = None

        self._parent_path = fn_inp.parent
        self._fn_inp = fn_inp
        self._fn_rpt, self._fn_out = get_result_filenames(fn_inp)

    @property
    def rpt(self):
        """Report file object."""
        if self._rpt is None:
            self._rpt = SwmmReport(self._fn_rpt)
        return self._rpt

    @property
    def out(self):
        """Output file object."""
        if self._out is None:
            with SwmmOutput(self._fn_out) as out:
                out.to_numpy()
            self._out = out
        return self._out

    @property
    def lid_rpt_dict(self):
        """if LID report file exists, read file and save it in a dict with the key (SC label, LID label)"""
        if self._lid_rpts is None:
            self._lid_rpts = {}
            # get list of LID report files in inp data
            if SEC.LID_USAGE in self.inp:
                for lid_usage in self.inp.LID_USAGE.values():
                    if is_not_set(lid_usage.fn_lid_report):
                        continue  # no name defined -> no file will be written
                    pth = Path(lid_usage.fn_lid_report)

                    self._lid_rpts[(lid_usage.subcatchment, lid_usage.lid)] = read_lid_report(self._parent_path / pth)
        return self._lid_rpts


class swmm5_run_temporary:
    """
    Run SWMM with an input file in a temporary directory.

    Attributes:
        inp (swmm_api.SwmmInput): SWMM input-file data.
        cleanup (bool): if temporary folder should be deleted after with-statement.
        pth_temp (Path): temporary folder path.

    Examples::

        >> with swmm5_run_temporary(inp) as res:
        >>     res  # type: swmm_api.run_summ.run_temporary.SwmmResults
        >>     res.out  # type: SwmmOutput
        >>     res.rpt  # type: SwmmReport
        >>     res.inp  # type: SwmmInput
        >>     res.lid_rpt  # type: dict[tuple(str, str), pandas.DataFrame]
    """
    def __init__(self, inp: SwmmInput, cleanup=True, run=None, label='temp', set_saved_files_relative=False, base_path=None, **kwargs):
        """
        Run SWMM with an input file in a temporary directory.

        Args:
            inp (swmm_api.SwmmInput): SWMM input-file data.
            cleanup (bool): if temporary folder should be deleted after with-statement.
            run (function): function for running SWMM. The function should only have one positional argument: input_file_name. default from CONFIG.
            label (str): name for temporary files.
            set_saved_files_relative (bool): if all saved files should be set as relative path to be saved in the temporary folder.
            base_path (str or pathlib.Path): path where the files used (linked with relative paths) in the inp file are stored. default=current working directory.
        """
        self.inp = inp
        self.cleanup = cleanup
        self.pth_temp = Path(tempfile.mkdtemp())

        self.fn_inp = self.pth_temp / f'{label}.inp'

        inp.delete_sections(GEO_SECTIONS + GUI_SECTIONS + [SEC.TAGS])

        # ---
        # files used
        if base_path is None:
            pth_current = Path.cwd()
        else:
            pth_current = Path(base_path)

        # where to look:
        # when relative - look in current dir
        def _handle_files(fn):
            if Path(fn).is_file() and Path(fn).is_absolute():
                # print(Path(fn), 'is file')
                ...
            elif (pth_current / fn).is_file():
                # rename to pasted
                fn = str(pth_current / fn)
            else:
                # print('UNKONWN:', fn)
                ...
            # print(fn)
            return fn

        # RAINGAGES with file
        if SEC.RAINGAGES in self.inp:
            for rg in inp.RAINGAGES.values():
                if rg.source.upper() == 'FILE':
                    rg.filename = _handle_files(rg.filename)

        # TIMESERIES FILE
        if SEC.TIMESERIES in self.inp:
            for ts in inp.TIMESERIES.values():
                if isinstance(ts, TimeseriesFile):
                    # or isinstance(ts, TimeseriesFile)
                    ts.filename = _handle_files(ts.filename)

        # EVAPORATION
        if (SEC.EVAPORATION in self.inp) and 'FILE' in inp.EVAPORATION:
            inp.EVAPORATION['FILE'] = _handle_files(inp.EVAPORATION['FILE'])

        # TEMPERATURE
        if (SEC.TEMPERATURE in self.inp) and 'FILE' in inp.TEMPERATURE:
            inp.TEMPERATURE['FILE'] = _handle_files(inp.TEMPERATURE['FILE'])

        # BACKDROP
        if (SEC.BACKDROP in self.inp) and 'FILE' in inp.BACKDROP:
            inp.BACKDROP['FILE'] = _handle_files(inp.BACKDROP['FILE'])

        # FILES
        if (SEC.FILES in self.inp) and inp.FILES:
            for k, v in inp.FILES.items():
                inp.FILES[k] = _handle_files(v)

        # ---
        if set_saved_files_relative:
            # Remove write hotstart file when in relative path?
            # Maybe someone uses this file. Users have to check for their own.
            if SEC.FILES in inp:
                for key in inp.FILES:
                    if key.upper().startswith(inp.FILES.KEYS.SAVE):
                        # print('Are you using the saved file?')
                        pth = Path(inp.FILES[key])
                        # print(key, pth)
                        inp.FILES[key] = pth.name

            # Rename LID report to relative path.
            # Using a relative path will save the LID report into the temporary folder and will be deleted after the with-statement.
            # Using an absolute path will save the LID report into the given folder and will not be deleted.
            if SEC.LID_USAGE in inp:
                for lid_usage in inp.LID_USAGE.values():
                    if is_nan(lid_usage.fn_lid_report):
                        continue  # no name defined -> no file will be written
                    lid_usage.fn_lid_report = f'lid_rpt_{lid_usage.subcatchment}_{lid_usage.lid}.txt'

        inp.write_file(self.fn_inp, fast=True, encoding=CONFIG.encoding)

        if _ := 0:  # this code is not for running but to keep the imports, which are needed to enable the "eval" function below.
            swmm5_run_progress
            swmm5_run_owa
            swmm5_run

        if run is None:
            if isinstance(CONFIG.default_temp_run, str):
                run = eval(CONFIG.default_temp_run)
            else:
                run = CONFIG.default_temp_run  # type: function
        run(self.fn_inp, **kwargs)

    def __enter__(self):
        """Entering the with statement. Read the results if available."""
        return SwmmResults(self.inp, self.fn_inp)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the with statement. Delete the temporary folder with all its files if cleanup=True."""
        if self.cleanup:
            shutil.rmtree(self.pth_temp)


def dummy_run(inp, skip_rpt=False, skip_out=False):
    inp.delete_sections(GEO_SECTIONS + GUI_SECTIONS + [SEC.TAGS])
    with swmm5_run_temporary(inp) as res:
        if skip_rpt:
            rpt = None
        else:
            rpt = res.rpt
        if skip_out:
            out = None
        else:
            out = res.out
    return rpt, out


def swmm_test_run(inp: SwmmInput, logging_func=print):
    """
    Check if inp file is run-able.

    This function modifies the inp-Data to make a 30 sec short simulation with only one reporting step and two routing steps.
    After the simulation is finished the TITLE section of the inp-file and the errors and warnings from the report-file are printed.

    To make the test run faster, metadata sections like geo-data, GUI and tags are deleted.

    Args:
        inp (swmm_api.SwmmInput): SWMM input-file data.
        logging_func (function): logging function (like logging.debug). default is print.
    """
    # GEO_SECTIONS = [COORDINATES, VERTICES, POLYGONS]
    # GUI_SECTIONS = [MAP, SYMBOLS, LABELS, BACKDROP, PROFILES]
    logging_func('delete report, tags, coordinates, poylgons, vertices, map, symbols, labels, backdrop, and profile sections')
    inp.delete_sections([SEC.REPORT])

    logging_func('setting threads=1 and simulations run duration to 30 seconds')
    inp.OPTIONS['THREADS'] = 1

    from datetime import timedelta
    dur = timedelta(seconds=30)
    inp.OPTIONS.set_simulation_duration(dur)

    inp.OPTIONS['ROUTING_STEP'] = 15
    inp.OPTIONS['WET_STEP'] = 15
    inp.OPTIONS['REPORT_STEP'] = dur
    inp.OPTIONS['MINIMUM_STEP'] = 15

    with swmm5_run_temporary(inp) as res:
        rpt = res.rpt
        if rpt_errors := rpt.get_errors():
            logging_func(rpt._pretty_dict(rpt_errors))
        else:
            logging_func('No Errors')

        if rpt_warnings := rpt.get_warnings():
            logging_func(rpt._pretty_dict(rpt_warnings))
        else:
            logging_func('No Warnings')

        if 'Version+Title' in rpt._raw_parts:
            logging_func(rpt._raw_parts['Version+Title'])
