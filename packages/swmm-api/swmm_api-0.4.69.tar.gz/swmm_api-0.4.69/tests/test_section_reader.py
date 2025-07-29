import pytest
from swmm_api import SwmmInput, CONFIG
from swmm_api.input_file import SEC
from swmm_api.input_file.section_types import SECTION_TYPES
from swmm_api.input_file.sections import OptionSection


# Fixture to create a SwmmInput object with a specific section
@pytest.fixture
def swmm_input_with_section(request):
    section = request.param
    content = ';...'  # Placeholder for an empty section in SWMM format
    return SwmmInput.read_text(f'[{section.upper()}]\n{content}\n'), section, content


# Dynamically parameterize the test with all section types
@pytest.mark.parametrize('swmm_input_with_section', SECTION_TYPES, indirect=True)
def test_section(swmm_input_with_section):
    inp, section, content = swmm_input_with_section

    if section == SEC.TITLE:
        # Title section is treated as a string
        assert inp._data.get(section) == content
        assert inp[section].to_inp_lines() == content
    elif section == SEC.OPTIONS:
        # Options section is always converted to an OptionSection object
        assert inp._data.get(section) == OptionSection()
        assert inp[section].to_inp_lines() == CONFIG.comment_empty_section
    else:
        # Other sections are treated as plain content
        assert inp._data.get(section) == content
        assert inp[section].to_inp_lines() == CONFIG.comment_empty_section
