"""cube-specific utils

:organization: SecondWeb
:copyright: 2007-2010 SECOND WEB S.A.S. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.secondweb.fr/ -- mailto:contact@secondweb.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""

import os
import os.path as osp
from time import time


def preview_dir(config):
    directory = config["preview-dir"]
    if not osp.isabs(directory):
        directory = osp.join(config.static_directory, directory)
    return directory


def preview_dir_cleanup(config):
    cleanup_time = config["preview-dir-cleanup-time"]
    directory = preview_dir(config)
    for fname in os.listdir(directory):
        fullname = osp.join(directory, fname)
        if time() - os.stat(fullname).st_mtime > cleanup_time:
            os.unlink(fullname)
