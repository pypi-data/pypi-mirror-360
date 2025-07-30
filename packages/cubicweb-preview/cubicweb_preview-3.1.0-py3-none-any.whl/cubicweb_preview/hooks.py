"""cube-specific rql server side hooks

:organization: SecondWeb
:copyright: 2007-2010 SECOND WEB S.A.S. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.secondweb.fr/ -- mailto:contact@secondweb.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""

import os

from cubicweb_preview.utils import preview_dir, preview_dir_cleanup

from cubicweb.server.hook import Hook


class PreviewDirCheckHook(Hook):
    __regid__ = "preview_dir_check"
    events = ("server_startup",)

    def __call__(self):
        if self.repo.config.name != "all-in-one":
            return
        directory = preview_dir(self.repo.config)
        if not os.path.isdir(directory):
            try:
                os.makedirs(directory)
            except Exception:
                self.critical(
                    "could not find preview directory "
                    "(check preview-dir option which present value is %r)",
                    self.config["preview-dir"],
                )
                raise
        if not os.access(directory, os.W_OK):
            raise ValueError(
                "directory %r is not writable " "(check preview-dir option)" % directory
            )
        # XXX hack to work around 1193301
        pdcfunc = preview_dir_cleanup

        def regular_preview_dir_cleanup(config):
            try:
                self.info("starting preview directory cleanup...")
                pdcfunc(config)
            except Exception as ex:
                self.error("preview directory cleanup error occured : %s", ex)

        cleanup_time = self.repo.config["preview-dir-cleanup-time"]
        if cleanup_time:
            self.repo.looping_task(
                cleanup_time, regular_preview_dir_cleanup, self.repo.config
            )
