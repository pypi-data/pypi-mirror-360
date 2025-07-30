"""new-python-project: Launcher.

© Reuben Thomas <rrt@sc3d.org> 2025.

Released under the GPL version 3, or (at your option) any later version.
"""

import re
import sys

from new_python_project import main


sys.argv[0] = re.sub(r"__main__.py$", "new_python_project", sys.argv[0])
main()
