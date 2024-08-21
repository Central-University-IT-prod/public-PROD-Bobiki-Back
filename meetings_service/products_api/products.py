import logging

from flask import jsonify
from flask_restful import Resource

from db_models.models import Product
from orm_manager import db_session

logger = logging.getLogger(__name__)


class ProductsResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        products = db_sess.query(Product).all()
        logger.debug("Selected all products successfully")
        db_sess.close()
        return jsonify(
            {
                "products": [
                    {
                        "id": product.id,
                        "name": product.name,
                        "time": product.time,
                    }
                    for product in products
                ]
            }
        )
