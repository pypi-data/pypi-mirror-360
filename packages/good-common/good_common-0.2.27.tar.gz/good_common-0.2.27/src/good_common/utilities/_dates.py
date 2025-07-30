import datetime
import typing
from zoneinfo import ZoneInfo

from dateutil import parser

from ._functional import try_chain


def any_datetime_to_tz(
    value: datetime.datetime, tz: str | ZoneInfo
) -> datetime.datetime:
    if isinstance(tz, str):
        tz = ZoneInfo(tz)
    if value.tzinfo is None:
        return value.replace(tzinfo=datetime.UTC).astimezone(tz)
    return value.astimezone(tz)


def any_datetime_to_utc(value: datetime.datetime) -> datetime.datetime:
    return any_datetime_to_tz(value, "UTC")


def to_start_of_day(value: datetime.date | datetime.datetime) -> datetime.datetime:
    if isinstance(value, datetime.date):
        value = datetime.datetime(value.year, value.month, value.day, 0, 0, 0, 0)
    return value.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=value.tzinfo)


def to_end_of_day(
    value: datetime.date | datetime.datetime, tomorrow: bool = False
) -> datetime.datetime:
    if isinstance(value, datetime.date):
        value = datetime.datetime(value.year, value.month, value.day, 0, 0, 0, 0)
    if tomorrow:
        return to_start_of_day(value + datetime.timedelta(days=1))
    return value.replace(hour=23, minute=59, second=59, microsecond=999999)


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc)


def now_tz(tz):
    return datetime.datetime.now(ZoneInfo(tz))


def now_pt():
    return now_tz("US/Pacific")


def date_pt(year, month, day):
    return datetime.datetime(
        year, month, day, 0, 0, 0, 0, tzinfo=ZoneInfo("US/Pacific")
    )


def to_pt(date: datetime.date | datetime.datetime):
    if isinstance(date, datetime.date):
        date = datetime.datetime(date.year, date.month, date.day, 0, 0, 0, 0)
    return any_datetime_to_tz(date, "US/Pacific")


def date_utc(year, month, day):
    return datetime.datetime(year, month, day, 0, 0, 0, 0, tzinfo=datetime.UTC)


def date_et(year, month, day):
    return datetime.datetime(
        year, month, day, 0, 0, 0, 0, tzinfo=ZoneInfo("US/Eastern")
    )


def to_et(date: datetime.date | datetime.datetime):
    if isinstance(date, datetime.date):
        date = datetime.datetime(date.year, date.month, date.day, 0, 0, 0, 0)
    return any_datetime_to_tz(date, "US/Eastern")


def now_et():
    return now_tz("US/Eastern")


def strptime(format: str) -> typing.Callable[..., datetime.datetime]:
    def _strptime(value):
        return datetime.datetime.strptime(value, format)

    return _strptime


def parse_timestamp(
    timestamp: typing.Any,
    *formats,
    raise_error=False,
    timezone=datetime.UTC,
    as_date=False,
) -> typing.Optional[datetime.datetime]:
    if not timestamp:
        return None

    if isinstance(timestamp, datetime.datetime):
        return timestamp

    if isinstance(timestamp, datetime.date):
        if as_date:
            return timestamp
        return datetime.datetime(
            timestamp.year, timestamp.month, timestamp.day, tzinfo=timezone
        )
        # return timestamp

    chain_fns = []

    if len(formats) > 0:
        for fmt in formats:
            chain_fns.append(strptime(fmt))

    chain_fns += [
        strptime("%Y-%m-%dT%H:%M:%S.%fZ"),
        strptime("%Y-%m-%d"),
        lambda x: parser.parse(x),
    ]

    output = try_chain(chain_fns, fail=raise_error)(timestamp)
    if output:
        output.replace(tzinfo=timezone)
        return output.date() if as_date else output
    return None


def parse_date(
    date: typing.Any, *formats, raise_error=False
) -> typing.Optional[datetime.date]:
    return parse_timestamp(
        date,
        *formats,
        raise_error=raise_error,
        as_date=True,
    )
