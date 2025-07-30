"""new-python-project tests.

© Reuben Thomas <rrt@sc3d.org> 2025

Released under the GPL version 3, or (at your option) any later version.
"""

import subprocess
from contextlib import chdir
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from nancy import main
from pytest import CaptureFixture, LogCaptureFixture
from testutils import failing_cli_test, passing_cli_test


tests_dir = Path(__file__).parent.resolve() / "test-files"


# CLI tests
def test_help_option_should_produce_output(capsys: CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as e:
        main(["--help"])
    assert e.type is SystemExit
    assert e.value.code == 0
    assert capsys.readouterr().out.find("A simple templating system.") != -1


def test_invalid_command_line_argument_causes_an_error(
    capsys: CaptureFixture[str],
    caplog: LogCaptureFixture,
) -> None:
    failing_cli_test(capsys, caplog, ["--foo", "a"], "unrecognized arguments: --foo")


def test_project_creation(capsys: CaptureFixture[str]) -> None:
    with TemporaryDirectory(delete=False) as tempdir:
        with chdir(tempdir):
            passing_cli_test(
                capsys, ["--noprompt", "foo", str(Path(tests_dir) / "foo.toml")]
            )
            with chdir("foo"):
                subprocess.check_call(["tox"])
