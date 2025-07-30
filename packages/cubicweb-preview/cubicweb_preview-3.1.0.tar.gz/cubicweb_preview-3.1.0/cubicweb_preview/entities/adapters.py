"""cube-specific forms/views/actions/components

:organization: SecondWeb
:copyright: 2007-2010 SECOND WEB S.A.S. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.secondweb.fr/ -- mailto:contact@secondweb.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""

import os.path as osp
from cubicweb.predicates import objectify_predicate
from cubicweb.entities.adapters import IDownloadableAdapter


@objectify_predicate
def previewable_downloadable_adapter(
    cls, req, rset=None, row=0, col=0, entity=None, do_not_select_me=False, **kwargs
):
    if do_not_select_me:
        return 0
    eid = None
    if entity is not None:
        eid = entity.eid
    elif rset:
        eid = rset[row][col]
    if hasattr(req, "data") and eid in req.data.get("preview_entities", ()):
        return 999
    return 0


class PreviewIDownloadable(IDownloadableAdapter):
    __select__ = previewable_downloadable_adapter()

    def __init__(self, *args, **kwargs):
        super(PreviewIDownloadable, self).__init__(*args, **kwargs)
        adapter = self._cw.vreg["adapters"].select(
            self.__regid__, self._cw, entity=self.entity, do_not_select_me=True
        )
        self.entity._cw_adapters_cache["IDownloadable"] = self
        self._wrapped_adapter = adapter
        self.download_content_type = adapter.download_content_type
        self.download_file_name = adapter.download_file_name
        self.download_data = adapter.download_data
        self.download_encoding = adapter.download_encoding

    def download_url(self, **kwargs):
        prev_ents = self._cw.data.get("preview_entities", {})
        eid = int(self.entity.eid)
        if eid in prev_ents:
            return osp.join(
                self._cw.vreg.config["preview-urlpath"], osp.basename(prev_ents[eid])
            )
        else:
            return self._wrapped_adapter.download_url(**kwargs)
