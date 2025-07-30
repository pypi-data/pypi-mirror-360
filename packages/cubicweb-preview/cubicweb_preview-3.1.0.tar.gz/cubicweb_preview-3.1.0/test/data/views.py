from cubicweb.predicates import is_instance
from cubicweb_web.views.primary import PrimaryView


class CardPrimaryView(PrimaryView):
    __select__ = PrimaryView.__select__ & is_instance("Card")

    def cell_call(self, row, col):
        super(CardPrimaryView, self).cell_call(row, col)
        card = self.cw_rset.get_entity(row, col)
        self.wview("primary", card.related("illustrated_by"))
