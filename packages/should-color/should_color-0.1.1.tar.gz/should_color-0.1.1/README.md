should-color
===================

[![github](https://img.shields.io/badge/github-Techcable/should-color.py-master)](https://github.com/Techcable/should-color.py)
[![pypi](https://img.shields.io/pypi/v/should-color)](https://pypi.org/project/should-color)
![types](https://img.shields.io/pypi/types/should-color)

Determine if terminal output should be colored, respecting [`NO_COLOR`] and [`CLICOLOR`] environment variables.

On Unix, ANSI colors are enabled if the output is [`isatty`]. On Windows, ANSI colors are assumed to be unsupported unless or [`colorama`] is installed and enabled.

[`isatty`]: https://docs.python.org/3/library/io.html#io.IOBase.isatty
[`NO_COLOR`]: https://no-color.org/
[`CLICOLOR`]: https://bixense.com/clicolors/
[`colorama`]: https://pypi.org/project/colorama/

## Example Usage
```python
import sys
from should_color import should_color, apply_ansi_style

should_color(sys.stdout)
should_color(sys.stderr)
should_color('stdout')  # same as should_color(sys.stdout)
should_color('stderr')  # same as should_color(sys.stdout)
print(
    apply_ansi_style(
        "ERROR:",
        color="red",
        bold=True,
        # implicitly checks should_color('stdout'),
        # both these options are the implicit defaults if unspecified
        enabled='auto',
        file='stdout',
    ),
    "Fatal problem",
)
```

## License
Licensed under either the [Apache 2.0 License](./LICENSE-APACHE.txt) or [MIT License](./LICENSE-MIT.txt) at your option.

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in this project by you, as defined in the Apache-2.0 license, shall be dual licensed as above, without any additional terms or conditions. 
