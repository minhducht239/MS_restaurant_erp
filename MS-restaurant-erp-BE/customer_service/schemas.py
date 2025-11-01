from marshmallow import Schema, fields

class CustomerSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    phone = fields.Str()
    created_at = fields.DateTime()