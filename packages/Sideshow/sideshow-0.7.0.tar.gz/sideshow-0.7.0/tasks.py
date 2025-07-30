# -*- coding: utf-8; -*-
"""
Tasks for Sideshow
"""

import os
import shutil

from invoke import task


@task
def release(c, skip_tests=False):
    """
    Release a new version of Sideshow
    """
    if not skip_tests:
        c.run('pytest')

    # rebuild pkg
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('Sideshow.egg-info'):
        shutil.rmtree('Sideshow.egg-info')
    c.run('python -m build --sdist')

    # upload
    c.run('twine upload dist/*')
