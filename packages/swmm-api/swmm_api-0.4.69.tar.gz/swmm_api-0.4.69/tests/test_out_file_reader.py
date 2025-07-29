import pytest
import pandas.testing as pdt
from swmm_api import SwmmOutput
from swmm_api.output_file import OBJECTS, VARIABLES

SELECTED_PART = dict(kind=OBJECTS.NODE, label=None, variable=VARIABLES.NODE.HEAD,
                     show_progress=False)


@pytest.fixture(scope="module")
def swmm_output():
    """Fixture to load the SWMM output file once for all tests."""
    return SwmmOutput('../examples/epaswmm5_apps_manual/Example6-Final.out')


@pytest.fixture(scope="module")
def time_bounds(swmm_output):
    """Fixture to provide start and end time indices."""
    start_i, end_i = 123, 982
    return swmm_output.index[start_i], swmm_output.index[end_i]


def test_times(swmm_output, time_bounds):
    start, end = time_bounds
    sliced_index = swmm_output.index[123:983]
    assert sliced_index[0] == start
    assert sliced_index[-1] == end


def prepare_data(swmm_output, preliminary):
    if preliminary:
        swmm_output.to_numpy()
    else:
        swmm_output._data = None


@pytest.mark.parametrize("slim, preliminary", [(True, False), (False, False), (False, True)])
@pytest.mark.parametrize("start, end", [
    (False, False),  # Both start and end are None
    (True, False),  # start is time_bounds[0], end is None
    (False, True),  # start is None, end is time_bounds[1]
    (True, True)  # Both start and end are from time_bounds
])
def test_get_part(swmm_output, time_bounds, slim, preliminary, start, end):
    prepare_data(swmm_output, preliminary)
    start = time_bounds[0] if start else None
    end = time_bounds[1] if end else None
    d = swmm_output.get_part(**SELECTED_PART, slim=slim, start=start, end=end)
    assert d.index[0] == (start if start else swmm_output.index[0])
    assert d.index[-1] == (end if end else swmm_output.index[-1])


@pytest.mark.parametrize("preliminary", [False, True])
@pytest.mark.parametrize("start, end", [
    (False, False),  # Both start and end are None
    (True, False),  # start is time_bounds[0], end is None
    (False, True),  # start is None, end is time_bounds[1]
    (True, True)  # Both start and end are from time_bounds
])
def test_comparison(swmm_output, time_bounds, preliminary, start, end):
    prepare_data(swmm_output, preliminary)
    start = time_bounds[0] if start else None
    end = time_bounds[1] if end else None
    d1 = swmm_output.get_part(**SELECTED_PART, slim=False, start=start, end=end)
    d2 = swmm_output.get_part(**SELECTED_PART, slim=True, start=start, end=end)
    pdt.assert_frame_equal(d1, d2)
