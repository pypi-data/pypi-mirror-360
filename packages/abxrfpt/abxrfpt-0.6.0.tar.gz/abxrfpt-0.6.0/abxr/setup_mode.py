#!/usr/bin/env python3
#
# Copyright (c) 2024 ABXR Labs, Inc.
# Proprietary and confidential. All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
#


from abxr.display import display
from abxr.version import version

def main():
    display.write([ "ArborXR", "Field Provisioning", f"Version: {version}", "Setup Mode"])

if __name__ == "__main__":
    main()