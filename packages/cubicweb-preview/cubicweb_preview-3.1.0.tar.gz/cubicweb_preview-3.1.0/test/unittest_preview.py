# -*- encoding: utf-8 -*-

from io import BytesIO
import re

from cubicweb import Binary
from cubicweb_web.devtools.testlib import WebCWTC

from cubicweb_preview.utils import preview_dir_cleanup


class PreviewEditControllerTC(WebCWTC):
    def setup_database(self):
        super(PreviewEditControllerTC, self).setup_database()
        with open(self.datapath("small.png"), "rb") as fobj:
            self.small_png = fobj.read()
        with self.admin_access.client_cnx() as cnx:
            self.image_eid = cnx.create_entity(
                "File",
                data_name="small.png",
                data_format="image/png",
                data=Binary(self.small_png),
            ).eid
            self.card_eid = cnx.create_entity("Card", title="Initial card").eid
            cnx.execute(
                "SET C illustrated_by I WHERE C eid %(c)s, I eid %(i)s",
                {"c": self.card_eid, "i": self.image_eid},
            )
            cnx.commit()
        preview_dir_cleanup(self.config)

    def tearDown(self):
        preview_dir_cleanup(self.config)
        super(PreviewEditControllerTC, self).tearDown()

    def entity_count(self, cnx, etype):
        return cnx.execute("Any COUNT(X) WHERE X is %s" % etype)[0][0]

    def _main_form(self, maineid, preview_mode="newtab"):
        return {
            "__form_id": "edition",
            "__errorurl": "",
            "__domid": "entityForm",
            "__maineid": str(maineid),
            "__message": "Entity created",
            "__action_preview": "preview",
            "__preview_mode": preview_mode,
        }

    def _card_form(self, eid, title="New card"):
        add_eid = lambda key: key + ":%s" % eid  # noqa: E731
        return {
            "eid": str(eid),
            add_eid("__type"): "Card",
            add_eid("_cw_entity_fields"): "title-subject,__type",
            add_eid("title-subject"): title,
        }

    def _image_form(self, eid):
        add_eid = lambda key: key + ":%s" % eid  # noqa: E731
        form = {
            "eid": str(eid),
            add_eid("__type"): "File",
            add_eid("_cw_entity_fields"): (
                "title-subject,data-subject," "__type,description-subject"
            ),
            add_eid("title-subject"): "Initial image",
            add_eid("data-subject"): ("small.png", BytesIO(self.small_png)),
            add_eid("data_name-subject"): "small.png",
            add_eid("data_format-subject"): "image/png",
            add_eid("data_encoding-subject"): "",
            add_eid("description_format-subject"): "text/html",
        }
        return form

    def illustrated_card_form(
        self, eid="A", image_eid="B", title="New card", params={}
    ):
        form = self._main_form(eid)
        form.update(self._card_form(eid, title))
        form.update(self._image_form(image_eid))
        form["eid"] = [str(eid), str(image_eid)]
        form["_cw_entity_fields:%s" % eid] += ",illustrated_by-subject"
        form["illustrated_by-subject:%s" % eid] = str(image_eid)
        form["_cw_entity_fields:%s" % image_eid] += ",illustrated_by-object"
        form["illustrated_by-object:%s" % image_eid] = str(eid)
        form.update(params)
        return form

    def image_form(self, eid="A", params={}):
        form = self._main_form(eid)
        form.update(self._image_form(eid))
        form.update(params)
        return form

    def publish(self, req, form):
        req.form.update(form)
        controller = self.vreg["controllers"].select(
            "validateform", req=req, appli=self.app
        )
        ret = controller.publish()
        return ret

    def test_creation(self):
        with self.admin_access.web_request() as req:
            image_nb = self.entity_count(req, "File")
            form = self.image_form()
            result = self.publish(req, form)
            self.assertIn(b"/static\\/preview", result)
            self.assertIn(
                b"window.parent.rePostFormForPreview('entityForm', html)", result
            )
        with self.admin_access.web_request() as req:
            form = self.image_form()
            form["__preview_html"] = "<html>poop</html>"
            result = self.publish(req, form)
            self.assertEqual(result, b"<html>poop</html>")
            self.assertEqual(image_nb, self.entity_count(req, "File"))
        with self.admin_access.web_request() as req:
            form = self.image_form(params={"__preview_mode": "inline"})
            result = self.publish(req, form)
            self.assertIn(
                b"window.parent.handleInlinePreview('entityForm', html)", result
            )
            self.assertEqual(image_nb, self.entity_count(req, "File"))

    def test_edition(self):
        with self.admin_access.web_request() as req:
            image_nb = self.entity_count(req, "File")
            params = {"title-subject:%s" % self.image_eid: "New image"}
            result = self.publish(req, self.image_form(self.image_eid, params))
            self.assertIn(b"New image", result)
            self.assertIn(b"/static\\/preview", result)
            self.assertEqual(image_nb, self.entity_count(req, "File"))

    def test_local_filename(self):
        with self.admin_access.web_request() as req:
            add_eid = lambda key: "%s:%s" % (key, self.image_eid)  # noqa: E731
            params = {
                add_eid("title-subject"): "New image",
                add_eid("data-subject"): (
                    "autre bannière.png",
                    BytesIO("é content".encode(req.encoding)),
                ),
                add_eid("data_name-subject"): "autre bannière.png",
            }
            result = self.publish(req, self.image_form(self.image_eid, params))
            self.assertIn(b"New image", result)
            self.assertIn(b"/static\\/preview", result)
            static_urls = re.findall(
                r'/static[\\/]+preview[\\/]+([^"]+)', result.decode(req.encoding)
            )
            self.assertNotIn(
                None, [re.match("^[0-9a-zA-Z.-_]+$", s) for s in static_urls]
            )

    def test_related_edited(self):
        """tests the necessity of entity.clear_related_cache()
        be careful when you modify this test: it reproduces precise
        conditions where this call is needed (and thus must crash if
        it is commented out)"""
        with self.admin_access.web_request() as req:
            image_nb = self.entity_count(req, "File")
            params = {"title-subject:%s" % self.image_eid: "New image"}
            result = self.publish(
                req,
                self.illustrated_card_form(
                    self.card_eid, self.image_eid, params=params
                ),
            )
            self.assertIn(b"New card", result)
            self.assertIn(b"/static\\/preview", result)
            self.assertEqual(image_nb, self.entity_count(req, "File"))

    def test_related_edited_with_validation_error(self):
        """tests the preview controller behaves properly when there is
        a validation error due to invalid form data"""
        with self.admin_access.web_request() as req:
            image_nb = self.entity_count(req, "File")  # noqa: F841
            params = {"title-subject:%s" % self.image_eid: "New image"}
            result = self.publish(
                req,
                self.illustrated_card_form(
                    self.card_eid,
                    self.image_eid,
                    title="A too long title " * 20,  # >256 to generate the error
                    params=params,
                ),
            )
            self.assertNotIn("New card", result)
            self.assertIn("value should have maximum size of 256", result)

    def test_inline_result_class(self):
        with self.admin_access.web_request() as req:
            image_nb = self.entity_count(req, "File")  # noqa: F841
            form = self.image_form(params={"__preview_mode": "inline"})
            result = self.publish(req, form)
            self.assertIsInstance(result, bytes)

    def test_newtab_result_class(self):
        with self.admin_access.web_request() as req:
            image_nb = self.entity_count(req, "File")  # noqa: F841
            form = self.image_form(params={"__preview_mode": "newtab"})
            result = self.publish(req, form)
            self.assertIsInstance(result, bytes)


if __name__ == "__main__":
    import unittest

    unittest.main()
