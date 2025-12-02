from marshmallow import Schema, fields, validate

class CustomerSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(allow_none=True)
    phone = fields.Str(required=True, validate=validate.Regexp(r'^[0-9]{10,11}$'))
    loyalty_points = fields.Int(dump_default=0, validate=validate.Range(min=0))
    total_spent = fields.Float(dump_default=0.0, validate=validate.Range(min=0))
    last_visit = fields.Date(allow_none=True)
    visit_count = fields.Int(dump_default=1, validate=validate.Range(min=0))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class CustomerFilterSchema(Schema):
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    limit = fields.Int(load_default=10, validate=validate.Range(min=1, max=100))
    search = fields.Str(allow_none=True)
    loyalty_points_min = fields.Int(allow_none=True, validate=validate.Range(min=0))
    loyalty_points_max = fields.Int(allow_none=True, validate=validate.Range(min=0))
    total_spent_min = fields.Float(allow_none=True, validate=validate.Range(min=0))
    total_spent_max = fields.Float(allow_none=True, validate=validate.Range(min=0))
    created_at_after = fields.Date(allow_none=True)
    created_at_before = fields.Date(allow_none=True)
    ordering = fields.Str(allow_none=True)