from db_models.models import Product
from orm_manager import db_session


def validate_product(product_name: str) -> bool:
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.name == product_name).first()
    if product is None:
        return False
    return True
