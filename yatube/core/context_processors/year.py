import datetime


def year(request):
    a = datetime.date.today().year
    return {
        "year": a
    }
