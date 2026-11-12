from marshmallow import Schema, fields, validate

class TenderOutSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    status = fields.Str()
    budget = fields.Float()
    deadline_date = fields.DateTime()
    created_at = fields.DateTime(dump_only=True)

TenderOut = TenderOutSchema

class BidIn(Schema):
    amount = fields.Float(required=True, validate=validate.Range(min=0.01))
    proposal = fields.Str(load_default=None)

class BidOut(Schema):
    id = fields.Int(dump_only=True)
    tender_id = fields.Int(dump_only=True)
    bidder_id = fields.Int(dump_only=True)
    amount = fields.Float(dump_only=True)
    proposal = fields.Str(dump_only=True)
    status = fields.Str(dump_only=True)
    submitted_at = fields.DateTime(dump_only=True)

class ReviewIn(Schema):
    status = fields.Str(required=True, validate=validate.OneOf(["accepted", "rejected"]))
