from db_models.models import Courier


def do_intersect(intervals: list) -> bool:
    intervals.sort(key=lambda x: x[0])

    for i in range(1, len(intervals)):
        if intervals[i - 1][1] >= intervals[i][0]:
            return True

    return False


def check_courier_availability(courier: "Courier", start, end) -> bool:
    for meeting in courier.meetings:
        if do_intersect([(start, end), (meeting.start_datetime, meeting.end_datetime)]):
            return False
    return True
