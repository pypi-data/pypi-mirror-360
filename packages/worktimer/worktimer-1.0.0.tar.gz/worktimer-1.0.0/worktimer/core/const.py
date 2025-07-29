"""
Application-wide constants
"""

import os

from worktimer.core import util


PATH_APP = util.get_app_dir()
PATH_CONFIG = os.path.join(PATH_APP, "config.json")
PATH_DB = os.path.join(PATH_APP, "worktimer.db")
