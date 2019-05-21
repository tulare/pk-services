# -*- encoding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import setuptools

with open('LICENSE') as f:
    license = f.read()

# Get version without import module
exec(compile(open('src/pk_services/version.py').read(),
             'pk_services/version.py', 'exec'))

setuptools.setup(
    version = __version__,
    license=license,
    package_dir = {
        '' : str('src')
    },
)
