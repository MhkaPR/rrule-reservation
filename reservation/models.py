from datetime import datetime, timedelta

from dateutil.rrule import (
    rrule,
    DAILY, WEEKLY, MONTHLY, YEARLY,
    MO, TU, WE, TH, FR, SA, SU,
)
from django.db import models

from utils.models import TimeStampedModel

BYDAY_MAP = {
    "MO": MO, "TU": TU, "WE": WE, "TH": TH, "FR": FR, "SA": SA, "SU": SU,
}

class Event(TimeStampedModel):
    class Freq(models.IntegerChoices):
        DAILY = 1, "Daily"
        WEEKLY = 2, "Weekly"
        MONTHLY = 3, "Monthly"
        YEARLY = 4, "Yearly"

    _FREQ_TO_RRULE = {
        Freq.DAILY: DAILY,
        Freq.WEEKLY: WEEKLY,
        Freq.MONTHLY: MONTHLY,
        Freq.YEARLY: YEARLY,
    }

    title = models.CharField(max_length=255)

    start = models.DateTimeField()
    end = models.DateTimeField()

    recurrence_freq = models.PositiveSmallIntegerField(
        choices=Freq.choices,
        null=True,
        blank=True,
    )
    recurrence_interval = models.PositiveSmallIntegerField(default=1)
    recurrence_byday = models.CharField(max_length=50, blank=True)
    recurrence_until = models.DateTimeField(null=True, blank=True)
    recurrence_count = models.PositiveIntegerField(null=True, blank=True)

    exdates = models.JSONField(default=list, blank=True)


    class Meta:
        ordering = ("start",)
        indexes = [
            models.Index(fields=["start", "end"]),
            models.Index(fields=["recurrence_freq"]),
        ]

    def __str__(self) -> str:
        return self.title

    @property
    def duration(self) -> timedelta:
        return self.end - self.start

    @property
    def is_recurring(self) -> bool:
        return self.recurrence_freq is not None

    def build_rrule(self):
        if not self.is_recurring:
            return None

        byweekday = None
        if self.recurrence_byday:
            try:
                byweekday = [
                    BYDAY_MAP[word.strip().upper()]
                    for word in self.recurrence_byday.split(",")
                    if word.strip()
                ]
            except KeyError as exc:
                raise ValueError(
                    f"Invalid recurrence_byday word: {exc.args[0]!r}"
                ) from exc

        return rrule(
            freq=self._FREQ_TO_RRULE[self.recurrence_freq],
            dtstart=self.start,
            interval=self.recurrence_interval or 1,
            byweekday=byweekday,
            until=self.recurrence_until,
            count=self.recurrence_count,
        )

    def occurrences_between(self, start: datetime, end: datetime):
        if not self.is_recurring:
            if self.start < end and self.end > start:
                yield self.start
            return

        exdates = {datetime.fromisoformat(d) for d in (self.exdates or [])}
        rule = self.build_rrule()
        for dtstart in rule.between(start - self.duration, end, inc=True):
            if dtstart in exdates:
                continue
            yield dtstart