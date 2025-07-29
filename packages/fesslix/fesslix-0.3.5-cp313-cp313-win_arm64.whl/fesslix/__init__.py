"""Top-level module for Fesslix.

"""

# Fesslix - Stochastic Analysis
# Copyright (C) 2010-2025 Wolfgang Betz
#
# Fesslix is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Fesslix is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Fesslix.  If not, see <http://www.gnu.org/licenses/>. 

#==================================================================
# Expose core-interface of Fesslix
#==================================================================

from .core import *  # Expose all core functions at the top level
#from . import core   ## Loads the main-module of Fesslix

#==================================================================
# Expose metadata
#==================================================================

__all__ = (
    "__title__",
    "__summary__",
    "__uri__",
    "__version__",
    "__license__",
    "__copyright__",
)

__copyright__ = "Copyright (C) 2010-2025 Wolfgang Betz"

try:
    from importlib.metadata import metadata as _metadata  # Python 3.8+
except ImportError:
    from importlib_metadata import metadata as _metadata  # Python <3.8, requires 'importlib-metadata' package
_meta = _metadata("fesslix")

__title__ = _meta["name"]
__summary__ = _meta["description"]
__uri__ = next(
    entry.split(", ")[1]
    for entry in _meta.get_all("Project-URL", ())
    if entry.startswith("Homepage")
)
__version__ = _meta["version"]
__license__ = _meta["license"]


#==================================================================
# Attempt to load configuration
#==================================================================
set_exe_dir(__path__[0])

import yaml

try:
    # Load YAML configuration from a file
    with open("fesslix.yaml", "r") as fs:
        process_config( yaml.safe_load(fs) )
except KeyboardInterrupt:
    raise
except FileNotFoundError:
    pass
except yaml.YAMLError as e:
    print(f"Error [Fesslix::__init__::yaml_01]: Failed to parse YAML file: {e}")
except Exception as e:
    print(f"Error [Fesslix::__init__::yaml_02]: {e}")



