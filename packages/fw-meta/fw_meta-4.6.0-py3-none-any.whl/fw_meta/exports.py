"""Flywheel export filtering and path templating based on metadata."""

import enum
import re
import typing as t

import fw_utils
from pydantic import BaseModel, Field, PrivateAttr, model_validator

from .aliases import ALIASES

__all__ = ["ExportFilter", "ExportTemplate", "ExportRule"]


class ClassificationFilter(fw_utils.SetFilter):
    """File classification filter."""

    def match(self, value) -> bool:
        """Return True if the given value is among the classifications."""
        # get field path (export:file.classification, smart-copy:classification)
        ns, _, key = self.field.lower().partition("classification")
        classification = fw_utils.get_field(value, ns + _) or {}
        # filtering on a specific classification key
        # eg.: file.classification.Intent=Structural
        if key := key.lstrip("."):
            values = {k.lower(): v for k, v in classification.items()}.get(key, [])
        # filtering on any classification value
        # eg.: file.classification=Structural
        else:
            values = [v for vs in classification.values() for v in vs]
        return super().match(values)


# TODO analysis fields?
EXPORT_FILTERS = {
    "project._id": fw_utils.StringFilter,
    "project.label": fw_utils.StringFilter,
    "project.created": fw_utils.TimeFilter,
    "project.modified": fw_utils.TimeFilter,
    "subject._id": fw_utils.StringFilter,
    "subject.label": fw_utils.StringFilter,
    "subject.created": fw_utils.TimeFilter,
    "subject.modified": fw_utils.TimeFilter,
    "subject.firstname": fw_utils.StringFilter,
    "subject.lastname": fw_utils.StringFilter,
    "subject.sex": fw_utils.StringFilter,
    "subject.mlset": fw_utils.StringFilter,
    "subject.info.*": fw_utils.AutoFilter,
    "subject.tags": fw_utils.SetFilter,
    "session._id": fw_utils.StringFilter,
    "session.uid": fw_utils.StringFilter,
    "session.label": fw_utils.StringFilter,
    "session.created": fw_utils.TimeFilter,
    "session.modified": fw_utils.TimeFilter,
    "session.age": fw_utils.NumberFilter,
    "session.weight": fw_utils.NumberFilter,
    "session.operator": fw_utils.StringFilter,
    "session.timestamp": fw_utils.TimeFilter,
    "session.info.*": fw_utils.AutoFilter,
    "session.tags": fw_utils.SetFilter,
    "acquisition._id": fw_utils.StringFilter,
    "acquisition.uid": fw_utils.StringFilter,
    "acquisition.label": fw_utils.StringFilter,
    "acquisition.created": fw_utils.TimeFilter,
    "acquisition.modified": fw_utils.TimeFilter,
    "acquisition.timestamp": fw_utils.TimeFilter,
    "acquisition.info.*": fw_utils.AutoFilter,
    "acquisition.tags": fw_utils.SetFilter,
    "file.name": fw_utils.StringFilter,
    "file.created": fw_utils.TimeFilter,
    "file.modified": fw_utils.TimeFilter,
    "file.type": fw_utils.StringFilter,
    "file.modality": fw_utils.StringFilter,
    "file.size": fw_utils.SizeFilter,
    "file.info.*": fw_utils.AutoFilter,
    "file.tags": fw_utils.SetFilter,
    "file.classification": ClassificationFilter,
    "file.classification.*": ClassificationFilter,
}


def validate_export_filter_field(field: str) -> str:
    """Return validated/canonic export filter field name for the field shorthand."""
    return fw_utils.parse_field_name(
        field, aliases=ALIASES, allowed=list(EXPORT_FILTERS)
    )


class ExportFilter(fw_utils.IncludeExcludeFilter):
    """Export include/exclude filter with field validation and filter types."""

    def __init__(
        self,
        include: t.List[str] = None,
        exclude: t.List[str] = None,
    ) -> None:
        """Init filter with field name validators and filter types."""
        super().__init__(
            EXPORT_FILTERS,
            include=include,
            exclude=exclude,
            validate=validate_export_filter_field,
        )


EXPORT_FIELDS = [
    field for field in EXPORT_FILTERS if not re.match(r"\.(tags|classification)", field)
]


def validate_export_field(field: str) -> str:
    """Return validated/canonic export field name for the field shorthand."""
    return fw_utils.parse_field_name(field, aliases=ALIASES, allowed=EXPORT_FIELDS)


class ExportTemplate(fw_utils.Template):
    """Export template for formatting Flywheel metadata as path strings."""

    def __init__(self, template: str) -> None:
        """Init template with field name validators."""
        super().__init__(template, validate=validate_export_field)


class StrEnum(str, enum.Enum):
    """String enum."""

    def __str__(self) -> str:
        """Return string representation of a level."""
        return self.name  # pragma: no cover


class ExportLevel(StrEnum):
    """Flywheel hierarchy levels with files."""

    project = "project"
    subject = "subject"
    session = "session"
    acquisition = "acquisition"


class UnzipPath(StrEnum):
    """Unzipped member path / file naming strategy."""

    original = "original"
    underscore = "underscore"
    basename = "basename"


LEVELS = list(ExportLevel)
LEVEL_PATH = {
    ExportLevel.project: "{project}/{file}",
    ExportLevel.subject: "{project}/{subject}/{file}",
    ExportLevel.session: "{project}/{subject}/{session}/{file}",
    ExportLevel.acquisition: "{project}/{subject}/{session}/{acquisition}/{file}",
}


class ExportRule(BaseModel):
    """Export rule defining what to export and how."""

    level: ExportLevel = Field(
        ExportLevel.acquisition,
        title="Flywheel hierarchy level to export files from",
    )

    include: t.Optional[t.List[str]] = Field(
        None,
        examples=["type=dicom"],
        title=(
            "Include filters - if given, "
            "only include files matching at least one include filter"
        ),
    )

    exclude: t.Optional[t.List[str]] = Field(
        None,
        examples=["session.label=~test"],
        title=(
            "Exclude filters - if given, "
            "exclude files matching any of the exclude filters"
        ),
    )

    path: t.Optional[str] = Field(
        None,
        examples=[LEVEL_PATH[ExportLevel.acquisition]],
        title="Export path template",
    )

    unzip: bool = Field(
        True,
        title="Extract zipped files when exporting",
    )

    unzip_path: UnzipPath = Field(
        UnzipPath.basename,
        title="Unzipped member naming strategy",
    )

    metadata: bool = Field(
        False,
        title="Toggle to enable exporting metadata JSON alongside files",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_rule(cls, values: dict) -> dict:
        """Validate the filters and the path template given the level constraint."""
        level = ExportLevel(values.setdefault("level", "acquisition"))

        def check_level(field: str) -> bool:
            """Return True IFF the field is at or above the rule level."""
            if field.startswith("file."):
                return True
            field_level = ExportLevel(field.split(".")[0])
            if LEVELS.index(field_level) > LEVELS.index(level):
                raise ValueError(f"invalid field {field} for level {level}")
            return True

        include, exclude = values.get("include"), values.get("exclude")
        filt = ExportFilter(include=include, exclude=exclude)
        values["include"] = [str(i) for i in filt.include if check_level(i.field)]
        values["exclude"] = [str(e) for e in filt.exclude if check_level(e.field)]

        path = values.get("path") or LEVEL_PATH[level]
        template = ExportTemplate(path)
        for field in template.fields:
            check_level(field)
        values["path"] = str(template)

        return values

    _filter: ExportFilter = PrivateAttr(None)
    _template: ExportTemplate = PrivateAttr(None)

    def match(self, value) -> bool:
        """Return True if the values passes the include/exclude filters."""
        if self._filter is None:
            self._filter = ExportFilter(include=self.include, exclude=self.exclude)
        return self._filter.match(value)

    def format(self, value) -> t.Optional[str]:
        """Format the export rule's path template with the given context."""
        if not self.match(value):
            return None  # pragma: no cover
        if self._template is None:
            assert self.path
            self._template = ExportTemplate(self.path)
        return self._template.format(value)
