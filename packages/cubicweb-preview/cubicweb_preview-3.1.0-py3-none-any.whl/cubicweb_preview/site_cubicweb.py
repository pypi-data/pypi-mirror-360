"""cube-specific options

:organization: SecondWeb
:copyright: 2007-2010 SECOND WEB S.A.S. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.secondweb.fr/ -- mailto:contact@secondweb.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""

options = (
    (
        "preview-dir",
        {
            "type": "string",
            "default": "preview",
            "help": (
                "directory where to store the preview downloadable content (images, files, ...); "
                "if relative, use static_dir as a base directory."
            ),
            "group": "preview",
            "level": 2,
        },
    ),
    (
        "preview-urlpath",
        {
            "type": "string",
            "default": "/static/preview/",
            "help": "url path where to access the preview directory for downloadable content",
            "group": "preview",
            "level": 2,
        },
    ),
    (
        "preview-dir-cleanup-time",
        {
            "type": "int",
            "default": 120,
            "help": (
                "number of seconds between two preview directory cleanups; "
                "unset or set to 0 if you do not want cleanup"
            ),
            "group": "preview",
            "level": 2,
        },
    ),
)
