#
# Copyright (c) 2024 ABXR Labs, Inc.
# Proprietary and confidential. All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
#

from setuptools import setup

setup(
    name = 'abxrfpt',
    version = '0.6.0',
    packages = ['abxr'],
    entry_points = {
        'console_scripts': [
            'abxr-provision = abxr.provision:main',
            'abxr-display-setup-mode = abxr.setup_mode:main',
        ]
    },
    install_requires = [
        'androguard',
        'pyudev',
        'adafruit-circuitpython-ssd1306',
        'setuptools'
    ],
    include_package_data=True,
)
