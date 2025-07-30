#
# Copyright (c) 2024-2025 ABXR Labs, Inc.
# Released under the MIT License. See LICENSE file for details.
#

from loguru import logger
from androguard.core.apk import APK
from androguard.util import set_log

set_log("WARNING")

def get_package_name(apk_path):
    try:
        apk = APK(apk_path)
        return apk.get_package()
    except Exception as e:
        return None

