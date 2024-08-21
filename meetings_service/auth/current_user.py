from db_models.models import User
from orm_manager import db_session


def get_current_user():
    db_sess = db_session.create_session()
    user = db_sess.get(User, 1)
    db_sess.close()
    return user
