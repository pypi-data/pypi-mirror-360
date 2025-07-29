"""
Detect if ANSI colors should be used, respecting environment variables.

The primary function of this library is the `should_color` function.

The `apply_ansi_style` function is also very useful.
It conditionally applies ANSI styling to text whenever `should_color` returns True.
It supports keyword argument like `color="red", bold=True` so you don't have to remember the raw codes.
"""

from __future__ import annotations

import os
import sys

from ._version import __version__

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import (
        IO,
        AnyStr,
        Literal,
        Sequence,
        TextIO,
        Union,
    )

    from typing_extensions import TypeAlias, assert_type

    KnownStream: TypeAlias = Literal["stdout", "stderr"]
    SimpleColor: TypeAlias = Literal["black", "red", "green", "yellow", "blue", "purple"]
    EnabledSpec: TypeAlias = Union[bool, Literal["always", "never", "auto"]]
else:
    # fallback
    def cast(tp, x, /):  # noqa
        return x


def should_color(
    file: KnownStream | IO[str] | IO[bytes],
    *,
    enabled: EnabledSpec = "auto",
) -> bool:
    """
    Determine if ANSI colors should be used when printing to the specified stream.

    If no stream is specified, this checks the standard output.

    This respects [`NO_COLOR`] and [`CLICOLOR`] environment variables.
    If these are net set, this will return `True` if the specified file [`isatty`]
    and the platform supports colors (isn't old windows).

    On windows, if colorama is installed, this will implicitly call `just_fix_windows_console`.
    See [`platform_supports_colors`] for details.

    The `enabled="always"` flag can be used to forcibly enable colors, returning `True` unconditionally.
    Similarly, `enabled="never"` will forcibly disable colors, unconditionally returning `False`.
    By default, `enabled="auto"` and the stream will be checked for support as expected.
    This flag is purely for convenience.
    Using 'should_color(file) or force_enabled' would have the same effect.

    [`NO_COLOR`]: https://no-color.org/)
    [`CLICLOR`]: https://no-color.org/)
    [`isatty`]: https://docs.python.org/3/library/io.html#io.IOBase.isatty
    """
    if isinstance(file, str):
        if file == "stdout":
            file = sys.stdout
        elif file == "stderr":
            file = sys.stderr
        else:
            raise ValueError(f"Invalid `file`: {file!r}")
        if TYPE_CHECKING:
            assert isinstance(file, TextIO)  # needed because sys.stderr has type `Any`
    if enabled == "auto":
        pass  # default behavior
    elif isinstance(enabled, bool):
        return enabled
    elif enabled == "always":
        return True
    elif enabled == "never":
        return False
    elif not isinstance(enabled, bool):
        raise ValueError(f"Unexpected value for `enabled`: {enabled!r}")
    if TYPE_CHECKING:
        assert_type(file, Union[IO[bytes], IO[str]])
    if os.getenv("NO_COLOR"):
        return False
    elif os.getenv("CLICOLOR_FORCE"):
        return True
    else:
        return file.isatty() and platform_supports_colors()


def _build_ansi_code(
    parts: Sequence[str | int],
    /,
) -> str:
    if not parts:
        raise ValueError("empty parts")
    return f"\x1b[{';'.join(map(str, parts))}m"


_COLOR_OFFSETS: dict[str, int] = {
    "black": 0,
    "red": 1,
    "green": 2,
    "yellow": 3,
    "blue": 4,
    "purple": 5,
    "cyan": 6,
    "white": 7,
}


def apply_ansi_style(
    text: str,
    /,
    *,
    color: SimpleColor | None = None,
    bold: bool = False,
    underline: bool = False,
    file: KnownStream | IO[AnyStr],
    enabled: EnabledSpec = "auto",
) -> str:
    """
    Conditionally apply ANSI styling to the specified text.

    When `enabled="auto"` (the default), this only applies formatting when `should_color(file)` returns true.
    To force coloring, set `enabled="always"`.

    :param text: The text to style.
    :param file: The file that is being output to, for determining `enabled="auto"`.
    :param enabled: Whether the styling should be enabled.
            Using "auto" (the default) calls `should_color(file)`.
    :param bold: Whether the text should be bolded.
    :param underline: Whether the text should be underlined.
    :param color: The color to apply to the text, or `None` if the color should not be changed.
    :return: The text with appropriate styling applied.
    """
    if not should_color(enabled=enabled, file=file):
        return text
    begin_style = []
    if bold:
        begin_style.append(1)
    if underline:
        begin_style.append(4)
    if color is not None:
        try:
            color_offset = _COLOR_OFFSETS[color]
        except KeyError:
            raise ValueError(f"Invalid `color`: {color!r}") from None
        begin_style.append(30 + color_offset)
    if not begin_style:
        return text  # no styling to apply
    reset_code = _build_ansi_code([0])
    assert reset_code == "\x1b[0m", reset_code
    return f"{_build_ansi_code(begin_style)}{text}{reset_code}"


def apply_bold(
    text: str,
    /,
    *,
    file: KnownStream | IO[AnyStr],
    enabled: EnabledSpec = "auto",
) -> str:
    """
    Apply bold ANSI styling to the specified text.

    This is a convenience wrapper for [`apply_ansi_style`] which only sets `bold=True`.
    All available options have the same meaning as [`apply_ansi_style`].
    """
    return apply_ansi_style(
        text,
        file=file,
        enabled=enabled,
        bold=True,
    )


_cached_supports_colors: bool | None = None


def platform_supports_colors() -> bool:
    """
    Return true if the platform supports ANSI colors in terminals.

    This is always true on Unix systems, but on Windows it requires one of the following:
    - Microsoft Terminal being used (as determined by `WT_SESSION` environment variable)
    - The `CLICOLOR` or `ANSICON` environment variables are set, explicitly indicating support
    - The `ANSICON` environment variable is set, indicating terminal ANSI support
    - If [`colorama>=0.4.6`](https://github.com/tartley/colorama) is installed,
       this will implicitly invoke `just_fix_windows_console` to enable colors.

    If none of these apply, this will conservatively return `False` on Windows.
    """
    global _cached_supports_colors
    if sys.platform != "win32":
        return True  # using unix
    if _cached_supports_colors is not None:
        return _cached_supports_colors
    if os.getenv("CLICOLOR") or os.getenv("ANSICON") or os.getenv("WT_SESSION"):
        # environment indicates support
        _cached_supports_colors = True
        return True
    try:
        import colorama  # noqa: PLC0415

        getattr(colorama, "just_fix_windows_console")  # noqa: B009
    except (ImportError, AttributeError):
        _cached_supports_colors = False
        return False  # unsupported
    else:
        colorama.just_fix_windows_console()
        _cached_supports_colors = True
        return True


__all__ = (
    "EnabledSpec",
    "KnownStream",
    "SimpleColor",
    "__version__",
    "apply_ansi_style",
    "apply_bold",
    "platform_supports_colors",
    "should_color",
)
