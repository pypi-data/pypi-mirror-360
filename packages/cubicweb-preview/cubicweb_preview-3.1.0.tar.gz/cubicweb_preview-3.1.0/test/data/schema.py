from yams.buildobjs import RelationDefinition


class illustrated_by(RelationDefinition):
    subject = "Card"
    object = "File"
    cardinality = "1*"
