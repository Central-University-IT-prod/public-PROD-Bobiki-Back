import logging
from datetime import datetime, timedelta
from random import shuffle

from flask import jsonify, make_response, request
from flask_restful import Resource
from sqlalchemy import exc
from sqlalchemy.orm import Session

from auth.current_user import get_current_user
from db_models.models import AdditionalUser, Courier, Meeting, Product, User
from orm_manager import db_session
from validators.exc import ValidationError
from validators.validate_datetimes import check_courier_availability
from validators.validate_place import validate_place
from validators.validate_products import validate_product

logger = logging.getLogger()


def calculate_end_datatime(start_datetime: datetime, products: list["Product"]):
    duration = sum(product.time for product in products)
    return start_datetime + timedelta(minutes=duration)


def find_courier(start_datetime: datetime, end_datetime: datetime):
    couriers = db_session.create_session().query(Courier).all()
    shuffle(couriers)
    for courier in couriers:
        if check_courier_availability(courier, start_datetime, end_datetime):
            return courier


def update_meeting_products(meeting_id: int, products: list[dict], session: "Session"):
    meeting = session.get(Meeting, meeting_id)

    for product in products:
        if not validate_product(product["name"]):
            logger.warning(f"Product {product['name']} not found")
            raise ValidationError("Product not found")

    products = [
        session.query(Product).filter(Product.name == product["name"]).first()
        for product in products
    ]
    end_datetime = calculate_end_datatime(meeting.start_datetime, products)

    courier = find_courier(meeting.start_datetime, end_datetime)
    if not courier:
        logger.warning("Courier not found")
        raise ValidationError("Courier not found")
    courier = session.get(Courier, courier.id)

    meeting.products = products
    meeting.end_datetime = end_datetime
    meeting.courier = courier

    session.flush()


def update_meeting_start_datetime(
    meeting_id: int, start_datetime: str, session: "Session"
):
    meeting = session.get(Meeting, meeting_id)

    start_datetime = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M")
    end_datetime = calculate_end_datatime(start_datetime, meeting.products)

    courier = find_courier(start_datetime, end_datetime)
    if not courier:
        logger.warning("Courier not found")
        raise ValidationError("Courier not found")
    courier = session.get(Courier, courier.id)

    meeting.start_datetime = start_datetime
    meeting.end_datetime = end_datetime
    meeting.courier = courier

    session.flush()


def update_meeting_additional_users(
    meeting_id: int, additional_users: list[dict], session: "Session"
):
    meeting = session.get(Meeting, meeting_id)

    old_user = (
        session.query(AdditionalUser)
        .filter(AdditionalUser.meeting_id == meeting_id)
        .all()
    )
    for user in old_user:
        session.delete(user)

    meeting.additional_users = [
        AdditionalUser(**additional_user, meeting_id=meeting.id)
        for additional_user in additional_users
    ]
    session.flush()


def update_meeting_place(meeting_id: int, place: str, session: "Session"):
    meeting = session.get(Meeting, meeting_id)

    if not validate_place(place):
        logger.warning("Invalid place")
        raise ValidationError("Invalid place")

    meeting.location = place
    session.flush()


class MeetingWithIdResource(Resource):
    def get(self, meeting_id: int):
        session = db_session.create_session()
        meeting = session.get(Meeting, meeting_id)
        if not meeting:
            session.close()
            return make_response(jsonify({"status": "Meeting not found"}), 400)

        response_data = {
            "user": {
                "id": meeting.user.id,
                "name": meeting.user.name,
                "surname": meeting.user.surname,
                "middle_name": meeting.user.middle_name,
                "phone_number": meeting.user.phone_number,
            },
            "meeting": {
                "id": meeting.id,
                "start_datetime": datetime.strftime(
                    meeting.start_datetime, "%Y-%m-%d %H:%M"
                ),
                "end_datetime": datetime.strftime(
                    meeting.end_datetime, "%Y-%m-%d %H:%M"
                ),
                "place": meeting.location,
            },
            "courier": {
                "name": meeting.courier.name,
                "surname": meeting.courier.surname,
                "middle_name": meeting.courier.middle_name,
                "phone_number": meeting.courier.phone_number,
            },
            "additional_users": [],
            "products": [],
        }
        for product in meeting.products:
            response_data["products"].append(
                {"id": product.id, "name": product.name, "time": product.time}
            )
        for user in meeting.additional_users:
            response_data["additional_users"].append(
                {
                    "id": user.id,
                    "name": user.name,
                    "surname": user.surname,
                    "middle_name": user.middle_name,
                    "role": user.role,
                    "passport_data": user.passport_data,
                    "phone_number": user.phone_number,
                }
            )
        logger.info(f"Successfully get user meeting with id {meeting.id}")
        session.close()
        return jsonify(response_data)


class AllMeetingsResource(Resource):
    def get(self):
        user = get_current_user()
        session = db_session.create_session()
        meetings = session.query(Meeting).filter_by(user_id=user.id).all()

        response_data = {}
        for meeting in meetings:
            response_data[meeting.id] = {
                "user": {
                    "id": meeting.user.id,
                    "name": meeting.user.name,
                    "surname": meeting.user.surname,
                    "middle_name": meeting.user.middle_name,
                    "phone_number": meeting.user.phone_number,
                },
                "meeting": {
                    "id": meeting.id,
                    "start_datetime": datetime.strftime(
                        meeting.start_datetime, "%Y-%m-%d %H:%M"
                    ),
                    "end_datetime": datetime.strftime(
                        meeting.end_datetime, "%Y-%m-%d %H:%M"
                    ),
                    "place": meeting.location,
                },
                "courier": {
                    "name": meeting.courier.name,
                    "surname": meeting.courier.surname,
                    "middle_name": meeting.courier.middle_name,
                    "phone_number": meeting.courier.phone_number,
                },
                "additional_users": [
                    {
                        "id": user.id,
                        "name": user.name,
                        "surname": user.surname,
                        "middle_name": user.middle_name,
                        "role": user.role,
                        "passport_data": user.passport_data,
                        "phone_number": user.phone_number,
                    }
                    for user in meeting.additional_users
                ],
                "products": [
                    {"id": product.id, "name": product.name, "time": product.time}
                    for product in meeting.products
                ],
            }
        logger.info(f"Successfully get all user {user.id} meetings")
        session.close()
        return jsonify(response_data)


class MeetingResource(Resource):
    def post(self):
        data = request.get_json()
        session = db_session.create_session()

        start_datetime = data["meeting"]["start_datetime"]
        start_datetime = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M")
        products = [
            session.query(Product).filter(Product.name == product["name"]).first()
            for product in data["products"]
        ]
        end_datetime = calculate_end_datatime(start_datetime, products)

        place = data["meeting"]["place"]
        if not validate_place(place):
            logger.warning(f"Invalid place: {place}")
            session.close()
            return make_response(jsonify({"status": "Invalid place"}), 400)

        user = (
            session.query(User)
            .filter(
                User.name == data["user"]["name"]
                and User.surname == data["user"]["surname"]
                and User.middle_name == data["user"]["middle_name"]
            )
            .first()
        )
        if user is None:
            session.close()
            logger.warning(f"User not found: {data['user']}")
            return make_response(jsonify({"status": "User not found"}), 400)
        courier = find_courier(start_datetime, end_datetime)
        if courier is None:
            session.close()
            logger.warning(f"Courier not found: {data['user']}")
            return make_response(jsonify({"status": "Courier not found"}), 400)

        new_meeting = Meeting(
            user_id=user.id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            location=place,
            courier_id=courier.id,
        )
        session.add(new_meeting)
        try:
            session.flush()
        except exc.SQLAlchemyError as err:
            logger.warning(f"Error create new meeting: {err}")
            session.close()
            return make_response(jsonify({"status": "Fail create"}), 500)
        except:
            session.close()
            return make_response(jsonify({"status": "Fail create. Unknown error"}), 500)

        for additional_user in data["additional_users"]:
            new_additional_user = AdditionalUser(
                **additional_user,
                meeting_id=new_meeting.id,
            )
            session.add(new_additional_user)

        for product in products:
            new_meeting.products.append(product)

        try:
            logger.info(f"Successfully created new meeting, user {user.id}")
            session.commit()
        except exc.SQLAlchemyError as err:
            logger.warning(f"Error creating meeting: {err}")
            session.close()
            return make_response(jsonify({"status": "Error while adding to DB"}), 500)
        except:
            session.close()
            return make_response(jsonify({"status": "Unknown error"}), 500)
        session.close()
        return jsonify({"status": "success create"})

    def patch(self, meeting_id: int):
        data = request.get_json()
        session = db_session.create_session()
        meeting = session.get(Meeting, meeting_id)
        if not meeting:
            session.close()
            return make_response(jsonify({"status": "Meeting not found"}), 400)

        try:
            if "additional_users" in data:
                update_meeting_additional_users(
                    meeting.id, data["additional_users"], session
                )
            if "start_datetime" in data:
                update_meeting_start_datetime(
                    meeting.id, data["start_datetime"], session
                )
            if "products" in data:
                update_meeting_products(meeting.id, data["products"], session)
            if "place" in data:
                update_meeting_place(meeting.id, data["place"], session)
            session.commit()
        except exc.SQLAlchemyError as err:
            logger.warning(
                f"Error edit user, user_id: {meeting.user.id}; meeting, meeting_id: {meeting_id}; err: {err}"
            )
            session.close()
            return make_response(jsonify({"status": "Fail to edit"}), 500)
        except ValidationError as err:
            logger.warning(f"Error update data, err: {err}")
            session.close()
            return make_response(jsonify({"status": "Invalid data"}), 400)
        except:
            session.close()
            return make_response(jsonify({"status": "Unknown error"}), 500)
        logger.info(f"Successfully edited user {meeting.user.id} meeting {meeting.id}")
        session.close()
        return jsonify({"status": "success edit"})

    def delete(self, meeting_id: int):
        session = db_session.create_session()
        meeting = session.get(Meeting, meeting_id)
        if not meeting:
            session.close()
            return make_response(jsonify({"status": "Meeting not found"}), 400)
        session.delete(meeting)
        session.commit()
        logger.info(f"Successfully deleted user {meeting.user.id} meeting {meeting.id}")
        session.close()
        return jsonify({"status": "success delete"})
