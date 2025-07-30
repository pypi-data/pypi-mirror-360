===================
General description
===================

Preview cube adds the ability to preview the effect of a form submission.

The main idea is :

* submit the form data to a special controller, that will
  insert / update data in the database transaction, as normal

* generate the preview

* rollback the database changes to leave the database unchanged

The only exceptions to this rules are downloadable entities, like images : when
an html page (as a preview example view) that contains newly created / updated
images is rendered, the actual image content is queried by users' browser a
while after the above-mentionned database rollback was performed. The solution
adopted in this cube is to save such contents on the disk, and keep it for some
time (that can be set using the preview-time option) so that it can be previewed
and clean it up afterwards.

=====
Usage
=====

Simplest usage concerns automatic entity forms, where you generally want to
preview the just created or updated entity : in this case, import
PreviewFormMixin from cubicweb_preview.utils and make your form inherit it :
you're done. For example, to apply it to all AutomaticEntityForm forms, use::

 from cubicweb.selectors import yes
 from cubicweb_web.views.autoform import AutomaticEntityForm
 from cubicweb_preview.views.forms import PreviewFormMixin

 class PreviewAutomaticEntityForm(PreviewFormMixin, AutomaticEntityForm):
     __select__ = AutomaticEntityForm.__select__ & yes()

You can of course customize the preview, using PreviewFormMixin preview_vid
and preview_rql attributes, that will be used by the controller to create a
result set (using preview_rql, if not None) and apply a view (which name is
preview_vid value, default to "index") to it.

Below is an example for a CubicWeb instance using the file and preview cubes,
that can be used to preview the list of all images when you add or edit one :
we request all images through the preview_rql setting and display them using
the primary view ::

  from cubicweb.selectors import is_instance
  from cubicweb_web.views.autoform import AutomaticEntityForm
  from cubicweb_preview.views.forms import PreviewFormMixin

  class ImageForm(PreviewFormMixin, AutomaticEntityForm):
     __select__ = AutomaticEntityForm.__select__ & is_instance('Image')
     preview_vid = 'primary'
     preview_rql = 'Any X WHERE X is Image'
     preview_mode = 'inline'

Note that the previously created images are stored in the database while the
previewed one is temporarily stored on disk. By default, the previewed image
will be kept for one hour on disk, which can be set using the preview-store-time
option.

The `preview_mode` attribute accepts `newtab` (the default, opening
the preview in a new browser windows/tab within a custom template), or
`inline` (will show the preview below the form).

