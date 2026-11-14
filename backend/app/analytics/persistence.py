"""Provisional daily demo cadence; not a clinical or NASA threshold."""

from datetime import timedelta


MAX_DAILY_GAP = timedelta(hours=48)


def persistence_reasons(recent, barriers):
    """Explain why the three reserved observations cannot show continuity.

    Timestamps are already UTC. We do not aggregate repeated daily readings
    or invent a timestamp for a rejected row whose time is unknown.
    """
    reasons = []
    for (previous, _), (following, _) in zip(recent, recent[1:]):
        if following.date() - previous.date() != timedelta(days=1):
            reasons.append("Persistence requires three consecutive UTC dates")
            break

    if any(
        not timedelta(0) < following - previous <= MAX_DAILY_GAP
        for (previous, _), (following, _) in zip(recent, recent[1:])
    ):
        reasons.append("Persistence requires gaps no greater than 48 hours")

    if any(when is None for when in barriers):
        reasons.append("A rejected same-series observation has no usable timestamp")
    if any(
        when is not None and recent[0][0] <= when <= recent[-1][0]
        for when in barriers
    ):
        reasons.append("Missing or invalid observations interrupt persistence")

    return reasons
