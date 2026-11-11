from marshmallow import Schema, fields

class TenderOutSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    status = fields.Str()
    budget = fields.Float()
    deadline_date = fields.DateTime()
    created_at = fields.DateTime(dump_only=True)

TenderOut = TenderOutSchema
