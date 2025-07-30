"""$run(project_name.in.py): Main module.

© $run(author.in.py) <$run(email.in.py)> $run(year.in.py).

Released under the GPL version 3, or (at your option) any later version.
"""

import argparse
import importlib.metadata
import sys
import warnings

from .warnings_util import simple_warning


VERSION = importlib.metadata.version("$run(project_module.in.py)")


def main(argv: list[str] = sys.argv[1:]) -> None:
    # Command-line arguments
    parser = argparse.ArgumentParser(
        description="$run(description.in.py)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"""%(prog)s {VERSION}
© $run(year.in.py) $run(author.in.py) <$run(email.in.py)>
$run(project_home_page.in.py)
Distributed under the GNU General Public License version 3, or (at
your option) any later version. There is no warranty.""",
    )
    parser.add_argument(
        "--greeting",
        help="specify the greeting to use",
    )
    warnings.showwarning = simple_warning(parser.prog)
    args = parser.parse_args(argv)

    print(f"{args.greeting or 'Hello'} from $run(project_name.in.py)!")
