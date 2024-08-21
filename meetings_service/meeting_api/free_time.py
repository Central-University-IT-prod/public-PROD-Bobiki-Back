import datetime
import logging

from flask import jsonify
from flask_restful import Resource

from db_models.models import Courier
from orm_manager import db_session

logger = logging.getLogger()


def do_intersect(intervals: list) -> bool:
    intervals.sort(key=lambda x: x[0])

    for i in range(1, len(intervals)):
        if intervals[i - 1][1] >= intervals[i][0]:
            return True

    return False


def check_courier_availability(courier: Courier, start, end) -> bool:
    for meeting in courier.meetings:
        if do_intersect([(start, end), (meeting.start_datetime, meeting.end_datetime)]):
            return False
    return True


class FreeTimeResource(Resource):
    def get(self, date, length):
        db_sess = db_session.create_session()
        couriers = db_sess.query(Courier).all()

        free_slots = []

        for i in range(23):
            start = (
                datetime.datetime.strptime(date, "%Y-%m-%d")
                + datetime.timedelta(hours=8)
                + datetime.timedelta(minutes=i * 30)
            )
            end = start + datetime.timedelta(minutes=int(length))
            for courier in couriers:
                if (
                    check_courier_availability(courier, start, end)
                    and start not in free_slots
                ):
                    free_slots.append(
                        datetime.datetime.strftime(start, "%Y-%m-%d %H:%M")
                    )

        free_slots = sorted(set(free_slots))
        logger.debug(f"Successfully get free time in {date}")
        db_sess.close()
        return jsonify({"free_slots": free_slots})
