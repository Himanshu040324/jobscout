"""Closed vocabularies shared across modules."""

from enum import StrEnum


class Seniority(StrEnum):
    INTERN = "intern"
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"


class Recommendation(StrEnum):
    STRONG = "strong"
    MAYBE = "maybe"
    SKIP = "skip"


class AtsType(StrEnum):
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    ASHBY = "ashby"
    WORKABLE = "workable"
    SMARTRECRUITERS = "smartrecruiters"
