from __future__ import annotations
from datetime import datetime, timedelta
from uuid import UUID
from enum import Enum, StrEnum
from typing import Annotated, Optional, List, Union, get_origin, get_args

import isodate
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

# Enums for TaskWarrior-specific fields
class TaskStatus(str, Enum):
    """Task status as defined by TaskWarrior."""
    PENDING = "pending"
    COMPLETED = "completed"
    DELETED = "deleted"
    WAITING = "waiting"
    RECURRING = "recurring"

class Priority(str, Enum):
    """Task priority levels in TaskWarrior."""
    HIGH = "H"
    MEDIUM = "M"
    LOW = "L"
    NONE = ""

class RecurrencePeriod(str, Enum):
    """Supported recurrence periods for tasks."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    QUARTERLY = "quarterly"
    SEMIANNUALLY = "semiannually"

# Pydantic Models
class Task(BaseModel):
    """Represents a TaskWarrior task.
    Required Fields: description
    When defining a task fill the fields you want to use, ignore the others.
    Date representation:
        - datetime
        - NamedDate. Examples: 'tomorrow', 'eoy' for End of Month, '22th' for the next 22th of month, 'Monday' for the next monday.
        - Timedelta Period like `[±]P[DD]DT[HH]H[MM]M[SS]S` (ISO 8601 format for timedelta)
        - NamedDate [+-] Timedelta Period. Example 'tomorrow + PT8H' for tomorrow at 8am.
        - datatime + Timedelta Period."""

    description: Annotated[str, Field(..., description="Task description (required).")]
    priority: Annotated[
        Optional[Priority],
        Field(default=None, description="Priority of the task (H, M, L, or empty).")
    ]
    due: Annotated[
        Optional[Union[datetime, timedelta, str, NamedDate]],
        Field(default=None, description="Due date and time for the task.")
    ]

    tags: Annotated[
        Optional[List[str]],
        Field(default_factory=list, description="List of tags associated with the task.")
    ]
    project: Annotated[
        Optional[str],
        Field(default=None, description="Project the task belongs to.")
    ]
    depends: Annotated[
        Optional[List[UUID]],
        Field(default_factory=list, description="List of UUIDs of tasks this task depends on.")
    ]
    recur: Annotated[
        Optional[RecurrencePeriod],
        Field(default=None, description="Recurrence period for recurring tasks. When a reccutent task is created a parent template is automatically created. A recurrent task must be defined with a due date and a recurrence period")
    ]
    scheduled: Annotated[
        Optional[Union[datetime, timedelta, str, NamedDate]],
        Field(default=None, description="Schedule the earlier time the task can be done. Masked when using the `ready` filter")
    ]
    wait: Annotated[
        Optional[Union[datetime, timedelta, str, NamedDate]],
        Field(default=None, description="The task is hidden until the date.")
    ]
    until: Annotated[
        Optional[Union[datetime, timedelta, str, NamedDate]],
        Field(default=None, description="Expiration date for recurring tasks.")
    ]
    #annotations: List[Annotation ({'entry': datetime, 'description': str}] = Field(default_factory=list, description="List of annotations for the task.")
    context: Annotated[
        Optional[str],
        Field(default=None, description="Context filter for the task.")
    ]
#    udas: Dict[str, Any] = Field(default_factory=dict) #TODO: Review UDA usage

    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        json_schema_extra={
            'examples': [
                {
                    'description': 'a task'
                },
                {
                    'description': 'a due task in two weeks for Lambda project',
                    'due': 'P2W',
                    'project': 'Lambda',
                    'tags': ['demo']
                },
                {
                    'description': 'pay the rent (each end of month)',
                    'recurr': 'monthly',
                    'due': 'eom',
                    'priority': 'H'
                }
            ]
        }
    )

    @field_validator("description")
    @classmethod
    def description_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v):
        return [tag.strip() for tag in v if tag.strip()]

    @field_validator('*', mode='before')
    @classmethod
    def modify_date_format(cls, v, info):
        """Date converter"""
        # Get the field's type annotation
        field_type = cls.model_fields[info.field_name].annotation

        # Helper function to check if datetime is in the type (handles Union, Optional)
        def contains_datetime_or_timedelta(t):
            origin = get_origin(t)
            if origin in (Union, Optional):
                return any(contains_datetime_or_timedelta(arg) for arg in get_args(t))
            return t in (datetime, timedelta)

        # Check if the field involves datetime and the input is a string
        if contains_datetime_or_timedelta(field_type):# and isinstance(v, str):
            #        if (field_type == datetime or field_type == Union[datetime, timedelta]) and isinstance(v, str):
            if isinstance(v, (datetime, timedelta)):
                return v
            # Try parsing as datetime (format: yyyymmddThhmmssZ)
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                # Try parsing as duration (example format: P21DT1H10M49S)
                try:
                    isodate.parse_duration(v)
                except isodate.ISO8601Error:
                    return v
        return v


class TWTask(Task):
    index: Annotated[
        Optional[int],
        Field(default=None, alias='id', description="READONLY Task index of a task in the working set, which can change when tasks are completed or deleted.")
    ]
    uuid: Annotated[
        Optional[UUID],
        Field(default=None, description="Unique identifier for the task. Cannot be set when adding task")
    ]
    entry: Annotated[
        Optional[datetime],
        Field(default=None, description="Task creation date and time.")
    ]
    start: Annotated[
        Optional[datetime],
        Field(default=None, description="Task started date and time.")
    ]
    end: Annotated[
        Optional[datetime],
        Field(default=None, description="Task done date and time.")
    ]
    modified: Annotated[
        Optional[datetime],
        Field(default=None, description="Last modification date and time.")
    ]
    status: Annotated[
        Optional[TaskStatus],
        Field(default=None, description="Current status of the task.")
    ]
    parent: Annotated[
        Optional[UUID],
        Field(default=None, description="UUID of the template task for a recurrent task")
    ]
    urgency: Annotated[
            Optional[float],
            Field(default=None, description="Urgency score computed by TaskWarrior.")
    ]

    @field_serializer('uuid')
    def serialize_uuid(self, uuid: UUID, _info):
        return str(uuid)


class NamedDate(StrEnum):
    """
    Enum for Taskwarrior named dates.
    - now: 'Current local date and time.'
    - today: 'Current local date, with time 00:00:00.'
    - sod: 'Current local date, with time 00:00:00. Same as today.'
    - eod: 'Current local date, with time 23:59:59.'
    - yesterday: 'Local date for yesterday, with time 00:00:00.'
    - tomorrow: 'Local date for tomorrow, with time 00:00:00.'
    - monday: 'Local date for the specified day, after today, with time 00:00:00.'
    - tuesday: 'Local date for the specified day, after today, with time 00:00:00.'
    - wednesday: 'Local date for the specified day, after today, with time 00:00:00.'
    - thursday: 'Local date for the specified day, after today, with time 00:00:00.'
    - friday: 'Local date for the specified day, after today, with time 00:00:00.'
    - saturday: 'Local date for the specified day, after today, with time 00:00:00.'
    - sunday: 'Local date for the specified day, after today, with time 00:00:00.'
    - january: 'Local date for the specified month, 1st day, with time 00:00:00.'
    - february: 'Local date for the specified month, 1st day, with time 00:00:00.'
    - march: 'Local date for the specified month, 1st day, with time 00:00:00.'
    - april: 'Local date for the specified month, 1st day, with time 00:00:00.'
    - may: 'Local date for the specified month, 1st day, with time 00:00:00.'
    - june: 'Local date for the specified month, 1st day, with time 00:00:00.'
    - july: 'Local date for the specified month, 1st day, with time 00:00:00.'
    - august: 'Local date for the specified month, 1st day, with time 00:00:00.'
    - september: 'Local date for the specified month, 1st day, with time 00:00:00.'
    - october: 'Local date for the specified month, 1st day, with time 00:00:00.'
    - november: 'Local date for the specified month, 1st day, with time 00:00:00.'
    - december: 'Local date for the specified month, 1st day, with time 00:00:00.'
    - later: 'Local 9999-12-30, with time 00:00:00. A date far away, with a meaning to GTD users.'
    - someday: 'Local 9999-12-30, with time 00:00:00. A date far away, with a meaning to GTD users.'
    - soy: 'Start Of Year. Local date for the current year, January 1st, with time 00:00:00.'
    - eoy: 'End Of Year.,Local date for the current year, December 31st, with time 23:59:59.'
    - soq: 'Local date for the current quarter (January, April, July, October), 1st, with time 00:00:00.'
    - eoq: 'Local date for the end of the current quarter (March, June, September, December), last day of the month, with time 23:59:59.'
    - som: 'Local date for the 1st day of the current month, with time 00:00:00.'
    - eom: 'Local date for the last day of the current month, with time 23:59:59.'
    - sow: 'Local date for the start of the current week, Monday with time 00:00:00.'
    - eow: 'Local date for the end of the current week, Sunday night, with time 23:59:59.'
    - soww: 'Local date for the start of the work week, Monday, with time 00:00:00.'
    - eoww: 'Local date for the end of the work week, Friday night, with time 23:59:59.'
    - all ordinal days of month, from 1st to 31st with time 00:00:00. e.g, '1st', '2nd', '3rd', ..., '11th', '12th', .., '30th', '31st'
    - goodfriday: 'Local date for the next Good Friday, with time 00:00:00.'
    - easter: 'Local date for the next Easter Sunday, with time 00:00:00.'
    - eastermonday: 'Local date for the next Easter Monday, with time 00:00:00.'
    - ascension: 'Local date for the next Ascension (39 days after Easter Sunday), with time 00:00:00.'
    - pentecost: 'Local date for the next Pentecost (40 days after Easter Sunday), with time 00:00:00.'
    - midsommar: 'Local date for the Saturday after June 20th, with time 00:00:00. Swedish.'
    - midsommarafton: 'Local date for the Friday after June 19th, with time 00:00:00. Swedish.'
    """
    NOW = 'now'
    TODAY = 'today'
    SOD = 'sod'
    EOD = 'eod'
    YESTERDAY = 'yesterday'
    TOMORROW = 'tomorrow'
    MONDAY = 'monday'
    TUESDAY = 'tuesday'
    WEDNESDAY = 'wednesday'
    THURSDAY = 'thursday'
    FRIDAY = 'friday'
    SATURDAY = 'saturday'
    SUNDAY = 'sunday'
    JANUARY = 'january'
    FEBRUARY = 'february'
    MARCH = 'march'
    APRIL = 'april'
    MAY = 'may'
    JUNE = 'june'
    JULY = 'july'
    AUGUST = 'august'
    SEPTEMBER = 'september'
    OCTOBER = 'october'
    NOVEMBER = 'november'
    DECEMBER = 'december'
    LATER = 'later'
    SOMEDAY = 'someday'
    SOY = 'soy'
    EOY = 'eoy'
    SOQ = 'soq'
    EOQ = 'eoq'
    SOM = 'som'
    EOM = 'eom'
    SOW = 'sow'
    EOW = 'eow'
    SOWW = 'soww'
    EOWW = 'eoww'
    _1st = '1st'
    _2nd = '2nd'
    _3rd = '3rd'
    _4th = '4th'
    _5th = '5th'
    _6th = '6th'
    _7th = '7th'
    _8th = '8th'
    _9th = '9th'
    _10th = '10th'
    _11th = '11th'
    _12th = '12th'
    _13th = '13th'
    _14th = '14th'
    _15th = '15th'
    _16th = '16th'
    _17th = '17th'
    _18th = '18th'
    _19th = '19th'
    _20th = '20th'
    _21st = '21st'
    _22nd = '22nd'
    _23rd = '23rd'
    _24th = '24th'
    _25th = '25th'
    _26th = '26th'
    _27th = '27th'
    _28th = '28th'
    _29th = '29th'
    _30th = '30th'
    _31st = '31st'
    GOODFRIDAY = 'goodfriday'
    EASTER = 'easter'
    EASTERMONDAY = 'eastermonday'
    ASCENSION = 'ascension'
    PENTECOST = 'pentecost'
    MIDSOMMAR = 'midsommar'
    MIDSOMMARAFTON = 'midsommarafton'

