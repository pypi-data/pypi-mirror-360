"""cube-specific forms/views/actions/components

:organization: SecondWeb
:copyright: 2007-2010 SECOND WEB S.A.S. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.secondweb.fr/ -- mailto:contact@secondweb.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""

from cubicweb import _

from cubicweb.predicates import objectify_predicate
from cubicweb_web.views.basetemplates import TheMainTemplate


@objectify_predicate
def preview_form(cls, req, rset=None, **kwargs):
    if req.form.get("__preview_mode") == "newtab":
        return 1
    return 0


class PreviewTemplate(TheMainTemplate):
    """a very lightweight main template showing only
    the previewed entity, for the 'newtab' mode
    """

    __select__ = TheMainTemplate.__select__ & preview_form()
    preview_msg = _(
        "This is a preview. Do not try to follow links or trigger actions as both may fail."
    )

    def call(self, view):
        self.set_request_content_type()
        self.template_header(self.content_type, view)
        self._cw.add_js("cubicweb.edition.js")
        w = self.w
        w('<div id="pageContent">')
        w("<p>%s</p>" % self._cw._(self.preview_msg))
        w('<div id="contentmain">\n')
        view.render(w=w)
        w("</div></div>\n")
        self.template_footer(view)

    def template_body_header(self, view=None):
        pass

    def template_footer(self, view=None):
        pass
