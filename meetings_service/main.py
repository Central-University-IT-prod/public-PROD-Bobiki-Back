import logging
import os

import flask
import flask_restful

from meeting_api.free_time import FreeTimeResource
from meeting_api.meetings import (
    AllMeetingsResource,
    MeetingResource,
    MeetingWithIdResource,
)
from orm_manager import db_session
from products_api.documents import DocumentsResource
from products_api.products import ProductsResource
from users_api.get_current_user import CurrentUserResource

logger = logging.getLogger()
app = flask.Flask(__name__)
api = flask_restful.Api(app, prefix="/api/v1")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

api.add_resource(CurrentUserResource, "/current_user")
api.add_resource(ProductsResource, "/products")
api.add_resource(DocumentsResource, "/products/<int:product_id>/documents")
api.add_resource(FreeTimeResource, "/meetings/free_time/<string:date>/<int:length>")
api.add_resource(MeetingResource, "/meetings/create", "/meetings/<int:meeting_id>")
api.add_resource(MeetingWithIdResource, "/user/meetings/<int:meeting_id>")
api.add_resource(AllMeetingsResource, "/user/meetings/all")


@app.errorhandler(404)
def not_found(error):
    return flask.make_response(flask.jsonify({"error": "Not found"}), 404)


@app.before_request
def log_the_request():
    if flask.request.headers.get("Content-Type") == "application/json":
        logger.info(flask.request.json)
    logger.info(flask.request)


@app.after_request
def log_the_response(response):
    logger.info(response)
    logger.info(response.json)
    return response


if __name__ == "__main__":
    from waitress import serve

    db_session.global_init()
    port = os.getenv("SERVER_PORT", 8080)
    host = os.getenv("SERVER_HOST", "0.0.0.0")

    serve(app, host=host, port=port)
