from marshmallow import fields

from app import ma


class MessageResponseSchema(ma.Schema):
    message = fields.Str()
