from datetime import date, timedelta


def first_of_this_month() -> str:
    return date.today().replace(day=1).isoformat()


def tomorrow() -> str:
    return (date.today() + timedelta(days=1)).isoformat()
