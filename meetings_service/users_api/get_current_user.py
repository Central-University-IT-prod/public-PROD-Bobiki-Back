import logging

from flask import jsonify
from flask_restful import Resource

from auth.current_user import get_current_user

logger = logging.getLogger()


class CurrentUserResource(Resource):
    def get(self):
        user = get_current_user()
        logger.debug(f"Successfully get current user: {user.id}")
        return jsonify(
            {
                "id": user.id,
                "name": user.name,
                "surname": user.surname,
                "middle_name": user.middle_name,
                "phone_number": user.phone_number,
            }
        )
