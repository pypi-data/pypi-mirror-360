# import actual context
import os
import sys

# Vendoring: add vendor directory to module search path
parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, "_vendor")
if os.path.exists(vendor_dir):
    for vendor_path in os.listdir(vendor_dir):
        sys.path.append(os.path.join(vendor_dir, vendor_path))

from plugp100.responses import *
from plugp100.api.requests import *
from plugp100.api import *
from plugp100.common import *

__version__ = "5.1.5"
