"""Flywheel metadata field aliases."""

import typing as t

ALIASES: t.Dict[str, str] = {
    r"\.id$": "._id",
    r"^grp?(?=\.|$)": "group",
    r"^pro?j?(?=\.|$)": "project",
    r"^su(bj?)?(?=\\.|$)": "subject",
    r"^se(ss?)?(?=\.|$)": "session",
    r"^acq?(?=\.|$)": "acquisition",
    r"^group$": "group._id",
    r"^project$": "project.label",
    r"^subject$": "subject.label",
    r"^session$": "session.label",
    r"^acquisition$": "acquisition.label",
    r"^timestamp$": "acquisition.timestamp",
    r".(time|ts)$": ".timestamp",
    r"^file$": "file.name",
    r"^info(?=\.|$)": "file.info",
    r"^classification(?=\.|$)": "file.classification",
}
