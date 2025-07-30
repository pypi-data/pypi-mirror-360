# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import importlib.util
import subprocess
import sys
from typing import List


def install_and_import_packages(packages: List[str]):
    try:
        # Find missing packages
        missing_packages = [
            pkg for pkg in packages if importlib.util.find_spec(pkg) is None]

        # Install missing packages if any
        if missing_packages:
            print(
                f"Installing missing packages: {', '.join(missing_packages)}")
            subprocess.check_call([sys.executable, "-m", "pip",
                                   "install"] + missing_packages)
        else:
            print("All required packages are already installed.")
    except Exception as ex:
        raise ImportError(f"Error while installing {packages}.Details:{ex}")
