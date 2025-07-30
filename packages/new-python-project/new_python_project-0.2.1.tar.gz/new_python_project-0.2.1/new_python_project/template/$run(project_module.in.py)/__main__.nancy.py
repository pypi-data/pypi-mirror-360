"""$run(project_name.in.py): Launcher.

© $run(author.in.py) <$run(email.in.py)> $run(year.in.py).

Released under the GPL version 3, or (at your option) any later version.
"""

import re
import sys

from $run(project_module.in.py) import main


sys.argv[0] = re.sub(r"__main__.py$", "$run(project_module.in.py)", sys.argv[0])
main()
