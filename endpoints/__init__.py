# Standard library imports
import os
from datetime import datetime
from requests import post
from requests import get

# Third party imports
from flask import Flask
from flask import request
from flask import g
from flask_restx import Namespace
from flask_restx import Resource as _Resource
from flask_restx.fields import DateTime
from flask_restx.fields import Float
from flask_restx.fields import Integer
from flask_restx.fields import List
from flask_restx.fields import Nested
from flask_restx.fields import String
from flask_restx.fields import Boolean
from flask_restx.fields import Raw

# Local application imports
import models


class Resource(_Resource):
    dispatch_requests = []

    def __init__(self, api=None, *args, **kwargs):
        super(Resource, self).__init__(api, args, kwargs)

    def dispatch_request(self, *args, **kwargs):

        tmp = request.args.to_dict()

        if request.method == "GET":
            request.args = tmp

            [
                tmp.update({k: v.split(",")})
                for k, v in tmp.items()
                if k.endswith("__in")
            ]

            [
                tmp.update({k: v.split(",")})
                for k, v in tmp.items()
                if k.startswith("$sort")
            ]

        if (
            request.method == "POST"
            and request.headers.get("Content-Type", "") == "application/json"
        ):
            json = request.get_json()

            for key, value in json.items():
                if isinstance(value, dict) and key in routes:
                    if "id" in value:
                        json[key] = value["id"]

                    else:
                        item = post(
                            "http://localhost:5000/api/{}".format(key), json=value
                        )
                        json[key] = item.json()["id"]

        for method in self.dispatch_requests:
            method(self, args, kwargs)

        return super(Resource, self).dispatch_request(*args, **kwargs)


api = Namespace("api", description="")
book_base = api.model("book_base", models.Book.base())
book_reference = api.model("book_reference", models.Book.reference())
book_full = api.model("book", models.Book.model(api))
text_base = api.model("text_base", models.Text.base())
text_reference = api.model("text_reference", models.Text.reference())
text_full = api.model("text", models.Text.model(api))


@api.route("/book")
class BookController(Resource):
    @api.marshal_list_with(api.models.get("book"), skip_none=True)
    def get(self):
        return models.Book.qry(request.args)

    @api.marshal_with(api.models.get("book"), skip_none=True)
    def post(self):
        return models.Book.post(request.get_json())

    @api.marshal_with(api.models.get("book"), skip_none=True)
    def put(self):
        return models.Book.put(request.get_json())

    @api.marshal_with(api.models.get("book"), skip_none=True)
    def patch(self):
        return models.Book.patch(request.get_json())


@api.route("/book/<book_id>")
class BaseBookController(Resource):
    @api.marshal_with(api.models.get("book"), skip_none=True)
    def get(self, book_id):
        return models.Book.objects.get(id=book_id).to_json()

    @api.marshal_with(api.models.get("book"), skip_none=True)
    def put(self, book_id):
        return models.Book.put({"id": book_id, **request.get_json()})

    @api.marshal_with(api.models.get("book"), skip_none=True)
    def patch(self, book_id):
        return models.Book.patch({"id": book_id, **request.get_json()})

    def delete(self, book_id):
        return models.Book.get(id=book_id).delete()


@api.route("/text")
class TextController(Resource):
    @api.marshal_list_with(api.models.get("text"), skip_none=True)
    def get(self):
        return models.Text.qry(request.args)

    @api.marshal_with(api.models.get("text"), skip_none=True)
    def post(self):
        return models.Text.post(request.get_json())

    @api.marshal_with(api.models.get("text"), skip_none=True)
    def put(self):
        return models.Text.put(request.get_json())

    @api.marshal_with(api.models.get("text"), skip_none=True)
    def patch(self):
        return models.Text.patch(request.get_json())


@api.route("/text/<text_id>")
class BaseTextController(Resource):
    @api.marshal_with(api.models.get("text"), skip_none=True)
    def get(self, text_id):
        return models.Text.objects.get(id=text_id).to_json()

    @api.marshal_with(api.models.get("text"), skip_none=True)
    def put(self, text_id):
        return models.Text.put({"id": text_id, **request.get_json()})

    @api.marshal_with(api.models.get("text"), skip_none=True)
    def patch(self, text_id):
        return models.Text.patch({"id": text_id, **request.get_json()})

    def delete(self, text_id):
        return models.Text.get(id=text_id).delete()


routes = list(set([x.urls[0].split("/")[1] for x in api.resources]))
