# Standard library imports
import os

# Third party imports
from flask import Flask
from flask import request
from flask_cors import CORS
from flask_restx import Api
from mongoengine import DoesNotExist
from bson.objectid import ObjectId

# Local application imports
from endpoints import api as _api
from extensions import api_list
import models.triggers


app = Flask("api")
app.config["PROPAGATE_EXCEPTIONS"] = False
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)
api.add_namespace(_api)

for item in os.listdir("endpoints"):
    if item.endswith(".py") and not item == "__init__.py":
        imprt = __import__("endpoints.{}".format(item.split(".py")[0]))
        api.add_namespace(getattr(imprt, item.split(".py")[0]).api)

for extension in api_list:
    api.add_namespace(extension)


@api.errorhandler(DoesNotExist)
def handle_no_result_exception(error):
    if ObjectId.is_valid(request.path.split("/")[-1]):
        return {
            "message": "{} with id {} not found".format(
                request.path.split("/")[-2], request.path.split("/")[-1]
            )
        }, 404

    return {"message": str(error)}, 404


@api.errorhandler
def default_error_handler(error):
    return {"message": str(error)}, getattr(error, "code", 500)
