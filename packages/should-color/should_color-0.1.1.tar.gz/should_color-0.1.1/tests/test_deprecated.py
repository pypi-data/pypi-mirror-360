import pytest

import should_color


def test_implicit_file_deprecated():
    with pytest.deprecated_call():
        should_color.should_color()
    with pytest.deprecated_call():
        should_color.apply_ansi_style(
            "text",
            bold=True,
        )
