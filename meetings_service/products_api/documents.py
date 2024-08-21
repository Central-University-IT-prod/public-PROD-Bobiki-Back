import logging

from flask import jsonify
from flask_restful import Resource

from auth.current_user import get_current_user
from db_models.models import Product
from orm_manager import db_session

logger = logging.getLogger(__name__)


class DocumentsResource(Resource):
    def get(self, product_id):
        user = get_current_user()
        db_sess = db_session.create_session()
        products = db_sess.get(Product, product_id)

        docs = [doc for doc in products.documents]
        if user.business_type != "LLC":
            docs = [doc for doc in docs if doc.for_LLC is False]
        logger.debug(f"Successfully get documents for product {product_id}")
        db_sess.close()
        return jsonify(
            {"product": products.name},
            {"documents": [doc.name for doc in docs]},
        )
