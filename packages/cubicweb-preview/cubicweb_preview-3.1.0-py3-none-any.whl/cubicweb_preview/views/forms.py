"""cube-specific forms/views/actions/components

:organization: SecondWeb
:copyright: 2007-2010 SECOND WEB S.A.S. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.secondweb.fr/ -- mailto:contact@secondweb.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""

from cubicweb import _

from cubicweb_web.formwidgets import Button


PreviewButton = Button(
    (_("button_preview"), "PREVIEW_ICON"),
    attrs={"klass": "validateButton preview_button btn btn-default"},
    onclick=(
        "postForm('__action_preview', 'button_preview', "
        "$(this).closest('form').attr('id'))"
    ),
)


class PreviewFormMixin(object):
    """mix this with all forms you want to have a preview with"""

    preview_vid = None
    preview_rql = None
    preview_mode = "newtab"  # 'inline'/'newtab'
    cwtarget = "eformframe"

    def __init__(self, *args, **kwargs):
        super(PreviewFormMixin, self).__init__(*args, **kwargs)
        if PreviewButton not in self.form_buttons:
            # XXX handle reledit ... (we do not want preview button there)
            fname = self._cw.form.get("fname")
            if fname != "reledit_form":
                self.form_buttons = self.form_buttons[:]
                self.form_buttons.append(PreviewButton)
        if self.preview_vid is not None:
            self.add_hidden("__preview_vid", self.preview_vid)
        if self.preview_rql is not None:
            self.add_hidden("__preview_rql", self.preview_rql)
        if self.formtype == "main":
            self.add_hidden("__preview_mode", self.preview_mode)

    def render(self, *args, **kwargs):
        self._cw.add_js("cubes.preview.js")
        return super(PreviewFormMixin, self).render(*args, **kwargs)


def registration_callback(vreg):
    if "bootstrap" in vreg.config.cubes():
        PreviewButton.icon = "glyphicon glyphicon-search"
    vreg.register_all(globals().values(), __name__)
