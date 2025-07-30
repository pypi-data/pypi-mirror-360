"""Flywheel import metadata extraction fields and utilities."""

# check out the core-api input validation regexes for field loading context:
# https://gitlab.com/flywheel-io/product/backend/core-api/-/blob/master/core/models/regex.py
import enum
import json
import re
import string
import typing as t
from collections import defaultdict
from pathlib import Path

import fw_utils
from dateutil.tz import gettz
from fw_utils import AttrDict, Pattern, Template, get_field, parse_field_name
from pydantic import BaseModel, Field, PrivateAttr, model_validator

from .aliases import ALIASES

__all__ = ["MetaData", "MetaExtractor", "extract_meta"]
Mappings = t.Union[str, t.List[t.Union[t.Tuple[str, str], str]], t.Dict[str, str]]


# RULES


class StrEnum(str, enum.Enum):
    """String enum."""

    def __str__(self) -> str:
        """Return string representation of a level."""
        return self.name  # pragma: no cover


class ImportLevel(StrEnum):
    """Flywheel hierarchy levels with files."""

    project = "project"
    subject = "subject"
    session = "session"
    acquisition = "acquisition"


LEVELS = list(ImportLevel)
IMPORT_FILTERS = {
    "path": fw_utils.StringFilter,
    "name": fw_utils.StringFilter,
    "dir": fw_utils.StringFilter,
    "depth": fw_utils.NumberFilter,
    "size": fw_utils.SizeFilter,
    "ctime": fw_utils.TimeFilter,
    "mtime": fw_utils.TimeFilter,
}
IMPORT_FILTER_ALIASES = {
    r"^filepath$": "path",
    r"^filename$": "name",
    r"^dirname$": "dir",
    r"^created$": "ctime",
    r"^modified$": "mtime",
}


def validate_import_filter_field(field: str) -> str:
    """Return validated/canonic import filter field name for the field shorthand."""
    return fw_utils.parse_field_name(
        field, aliases=IMPORT_FILTER_ALIASES, allowed=list(IMPORT_FILTERS)
    )


class ImportFilter(fw_utils.IncludeExcludeFilter):
    """Import include/exclude filter with field validation and filter types."""

    def __init__(
        self,
        include: t.List[str] = None,
        exclude: t.List[str] = None,
    ) -> None:
        """Init filter with field name validators and filter types."""
        super().__init__(
            IMPORT_FILTERS,
            include=include,
            exclude=exclude,
            validate=validate_import_filter_field,
        )


class ImportRule(BaseModel):
    """Import rule defining what to import and how."""

    level: ImportLevel = Field(
        ImportLevel.acquisition,
        title="Flywheel container hierarchy level to import files to",
        examples=[],
    )
    include: t.Optional[t.List[str]] = Field(
        None,
        title=(
            "Include filters - if given, "
            "only include files matching at least one include filter"
        ),
        examples=["path=~.dcm"],
    )
    exclude: t.Optional[t.List[str]] = Field(
        None,
        title=(
            "Exclude filters - if given, "
            "exclude files matching any of the exclude filters"
        ),
        examples=["path=~meta.json"],
    )
    type: t.Optional[str] = Field(
        None,
        title=(
            "Data type to import matching files with - if given, "
            "allows extracting additional metadata for known types"
        ),
        examples=["dicom"],
    )
    zip: t.Optional[t.Literal[True]] = Field(
        None,
        title="Import multiple grouped files zipped together",
    )
    zip_single: t.Optional[bool] = Field(
        None,
        title="Create zip archive even if only a single file is matched",
    )
    group_by: t.Optional[str] = Field(
        None,
        title="Group and process files together based on a shared prefix",
        examples=["dir"],
        json_schema_extra={
            "readOnly": True,  # hide in input schemas for now
        },
    )
    mappings: Mappings = Field(
        title="Metadata mapping patterns",
        examples=[
            ("path", "{sub}/{ses}/{acq}/{file}"),
            ("path", "{file.info.original_path}"),
        ],
    )
    defaults: t.Optional[Mappings] = Field(
        None,
        title="Metadata fallback defaults",
        examples=[{"session.label": "control"}],
        json_schema_extra={
            "readOnly": True,  # hide in input schemas for now
        },
    )
    overrides: t.Optional[Mappings] = Field(
        None,
        title="Metadata manual overrides",
        examples=[{"subject.label": "ex1000"}],
        json_schema_extra={
            "readOnly": True,  # hide in input schemas for now
        },
    )
    dicom_instance_name: t.Optional[str] = Field(
        None,
        title="Single DICOM instance file name to use",
        examples=["{SOPInstanceUID}.{Modality}.dcm"],
    )
    dicom_group_by: t.Optional[list[str]] = Field(
        None,
        title="DICOM tags to group by",
        examples=[["StudyInsatnceUID", "SeriesInstanceUID"]],
    )
    dicom_split_localizer: t.Optional[bool] = Field(
        None,
        title="Split embedded localizer DICOM images into separate archive",
    )

    _filter: ImportFilter = PrivateAttr(None)
    _group_by: "ImportTemplate" = PrivateAttr(None)
    _extractor: "MetaExtractor" = PrivateAttr(None)

    @model_validator(mode="before")
    @classmethod
    def validate_rule(cls, values: dict) -> dict:
        """Validate the filters and the mappings given the level constraint."""
        ImportLevel(values.setdefault("level", "acquisition"))
        # validate filters
        filt = ImportFilter(
            include=values.get("includes") or values.get("include"),
            exclude=values.get("excludes") or values.get("exclude"),
        )
        values["include"] = [str(i) for i in filt.include]
        values["exclude"] = [str(e) for e in filt.exclude]
        # TODO use path globs in group_by for more flexibility, eg.:
        # - ** = group by parent dir = current functionality
        # - */* = group by the top 2 levels
        # - **/foo = group by the closest parent dir named foo (also filters)
        # when available, then it may be exposed as a feature
        # default to group_by=dir if type=dicom and/or zip=true
        if values.get("group_by") is None:
            if values.get("type") == "dicom" or values.get("zip"):
                values["group_by"] = "dir"
        # if group_by is set, ensure it's a valid template
        if values.get("group_by"):
            assert ImportTemplate(values["group_by"])
        # validate patterns
        extractor = MetaExtractor(
            mappings=values.get("mappings") or values.get("mapping"),
            defaults=values.get("defaults") or values.get("default"),
            overrides=values.get("overrides") or values.get("override"),
        )
        # check that untyped rules only reference known stat fields
        if not values.get("type"):
            allowed = set(IMPORT_FILTERS)
            if invalid := extractor.src_fields - allowed:  # pragma: no cover
                invalid_str = ",".join(invalid)
                allowed_str = "|".join(allowed)
                msg = f"invalid mapping field: {invalid_str} (allowed: {allowed_str})"
                raise ValueError(msg)
        values["mappings"] = [(str(t), str(p)) for t, p in extractor.mappings]
        values["defaults"] = extractor.defaults
        values["overrides"] = extractor.overrides
        return values

    def group(self, stat) -> t.Optional[str]:
        """Return the file's prefix group based on the group_by template."""
        if not self.group_by:
            return None  # pragma: no cover
        if not self._group_by:
            self._group_by = ImportTemplate(self.group_by)
        return self._group_by.format(stat)

    def match(self, stat) -> bool:
        """Return True if the file matches the rule's include/exclude filters."""
        if not self._filter:
            self._filter = ImportFilter(include=self.include, exclude=self.exclude)
        return self._filter.match(stat)

    def extract(self, *stat_and_meta) -> t.Optional["MetaData"]:
        """Return extracted metadata if the object matches the filters."""
        file = FieldGetter(*stat_and_meta)
        if not self.match(file):
            return None  # pragma: no cover
        meta = self.extractor.extract(file)
        if self.type:
            meta.setdefault("file.type", self.type)
        # TODO consider saving the import and the storage/path on info
        # TODO consider suffixing [.type].zip to file.name here
        return meta

    @property
    def extractor(self) -> "MetaExtractor":
        """Return initialized meta extractor instance."""
        if not self._extractor:
            self._extractor = MetaExtractor(
                mappings=self.mappings,
                defaults=self.defaults,
                overrides=self.overrides,
                level=self.level,
            )
        return self._extractor

    @property
    def dst_fields(self) -> t.Set[str]:
        """Return metadata fields that are present in the rule."""
        return self.extractor.dst_fields


# METADATA EXTRACTOR


class MetaData(dict):
    """Flywheel metadata dict with sorted/validated keys and attr access."""

    def __init__(self, *args, **kw) -> None:
        """Initialize a new MetaData dict."""
        super().__init__()
        self.update(*args, **kw)

    def update(self, *args, **kw) -> None:
        """Update MetaData dict from another dict or kwargs."""
        for field, value in dict(*args, **kw).items():
            self[field] = value

    def setdefault(self, field, value):
        """Set metadata field (or alias) value if not set yet."""
        field, value = load_field_tuple(field, value)
        if value in ("", None):
            return  # pragma: no cover
        if field not in self:
            self[field] = value
        return self[field]

    def __contains__(self, field) -> bool:
        """Return whether a field (or alias) is in the meta dict."""
        return super().__contains__(validate_import_field(field)[0])

    def __getitem__(self, field):
        """Get metadata field (or alias) value."""
        return super().__getitem__(validate_import_field(field)[0])

    def __setitem__(self, field, value) -> None:
        """Set canonized field names to validated values."""
        field, value = load_field_tuple(field, value)
        if value in ("", None):
            return  # pragma: no cover
        if field in ("session.timestamp", "acquisition.timestamp"):
            tz_key = field.replace("timestamp", "timezone")
            tz_val = getattr(value.tzinfo, "key", value.tzname())
            super().__setitem__(tz_key, tz_val)
            value = value.isoformat(timespec="milliseconds")
        super().__setitem__(field, value)

    def __getattr__(self, name: str):
        """Return dictionary keys as attributes."""
        return getattr(self.dict, name)

    def __iter__(self):
        """Return dict key iterator respecting the hierarchy/field order."""
        return iter(sorted(super().keys(), key=self.sort_key))

    @staticmethod
    def sort_key(field: str):
        """Return sorting key to order meta fields by hierarchy/importance."""
        return IMPORT_FIELD_NUM[field], field

    def keys(self):
        """Return dict keys, sorted."""
        return list(self)

    def values(self):
        """Return dict values, sorted."""
        return [self[k] for k in self]

    def items(self):
        """Return key, value pairs, sorted."""
        return iter((k, self[k]) for k in self)

    @property
    def dict(self) -> AttrDict:
        """Return inflated metadata dict ready for Flywheel uploads."""
        return AttrDict.from_flat(self)

    @property
    def json(self) -> bytes:
        """Return JSON dump of the inflated/nested metadata."""
        return json.dumps(self.dict, separators=(",", ":")).encode()


class MetaExtractor:
    """Meta Extractor."""

    def __init__(
        self,
        *,
        mappings: Mappings = None,
        defaults: Mappings = None,
        overrides: Mappings = None,
        level: ImportLevel = ImportLevel.acquisition,
    ) -> None:
        """Validate, compile and cache metadata extraction templates & patterns."""
        self.level = str(level)
        self.src_fields: t.Set[str] = set()
        self.dst_fields: t.Set[str] = set()
        self.mappings = []
        for mapping in parse_metadata_mappings(mappings or []):
            src_tpl, dst_pat = validate_metadata_mapping(mapping)
            for field in sorted(src_tpl.fields):
                if not field.startswith("!"):
                    self.src_fields.add(field)
                elif field[1:] not in self.dst_fields:  # pragma: no cover
                    msg = f"cannot reference {field} before assignment"
                    raise ValueError(msg)
            self.dst_fields.update(dst_pat.fields)
            self.mappings.append((src_tpl, dst_pat))

        # NOTE use case for defaults and overrides came from reapers
        # imports are tied to a project, so CLI doesn't expose them
        # TODO gather current use cases and reimplement defaults/overrides:
        # - D mapping-based extractions and literals *after* type/path-defaults
        # - D !metaref capability *after* type/path-defaults
        # - O for incrementally / minimally changing previous behavior
        # early proposal:
        # - support templates/patterns in defaults (literals vs validation?)
        # - drop overrides for simplicity (use-case not strong enough)
        self.defaults = dict(
            load_field_tuple(field, default)
            for field, default in parse_metadata_mappings(defaults or [])
        )
        # validate override fields and literal values
        self.overrides = dict(
            load_field_tuple(field, override)
            for field, override in parse_metadata_mappings(overrides or [])
        )

    def extract(self, obj) -> MetaData:
        """Extract metadata from given object's attrs or keys."""
        meta = MetaData()

        def get(field):
            if field.startswith("!"):
                return get_field(meta, field[1:])
            return get_field(obj, field)

        # apply user-defined metadata mappings
        for template, pattern in self.mappings:
            ctx = {field: get(field) for field in template.fields}
            # skip if data doesn't have a value for any of the template fields
            if any(value in ("", None) for value in ctx.values()):
                continue
            # format the template, then parse with the pattern
            for field, value in pattern.match(template.format(ctx)).to_flat().items():
                # setdefault allows using multiple patterns as fallback
                meta.setdefault(field, value)
        # apply type-defaults (eg. {'acquisition.label': <SeriesDescription>})
        get_meta = get("get_meta")  # fw-file integration
        type_meta = get_meta() if get_meta else {}
        for field, type_default in type_meta.items():
            if field == "file.name":
                continue  # pragma: no cover
            meta.setdefault(field, type_default)
        # apply path-defaults (eg. {'acquisition.label': <parent dir name>})
        path = get("path") or ""
        path_fields = ["acquisition", "session", "subject", "project"]
        path_fields = path_fields[path_fields.index(self.level) : -1]
        path_values = list(reversed(path.split("/")))[1:]
        for field, path_default in zip(path_fields, path_values):
            meta.setdefault(field, path_default)
        # NOTE defaults and overrides are not officially exposed
        # apply user-defaults (eg. {'project.label': 'Default Project'})
        for field, user_default in self.defaults.items():
            meta.setdefault(field, user_default)
        # apply user-overrides (eg. {'project.label': 'Override Project'})
        for field, user_override in self.overrides.items():
            meta[field] = user_override
        # consider adding single/zipped/member name candidates
        # pop file.name -> == singe name candidate
        # finally return the meta
        return meta


def extract_meta(
    obj,
    *,
    mappings: Mappings = None,
    defaults: Mappings = None,
    overrides: Mappings = None,
    level: ImportLevel = ImportLevel.acquisition,
) -> MetaData:
    """Extract Flywheel metadata from a dict like object."""
    # NOTE using the class enables validation and caching
    meta_extractor = MetaExtractor(
        mappings=mappings,
        defaults=defaults,
        overrides=overrides,
        level=level,
    )
    return meta_extractor.extract(obj)


def load_group_id(value: str) -> t.Optional[str]:
    """Normalize to lowercase and return validated value (or None)."""
    group_id = value.lower()
    if re.match(r"^[0-9a-z][0-9a-z.@_-]{0,62}[0-9a-z]$", group_id):
        return group_id
    return None


def load_cont_id(value: str) -> t.Optional[str]:
    """Normalize to lowercase and return validated value (or None)."""
    cont_id = value.lower()
    if re.match(r"^[0-9a-f]{24}$", cont_id):
        return cont_id
    return None


def load_cont_label(value: str) -> str:
    """Sanitize for path compatibility and truncate to 64 chars for CoreAPI."""
    return sanitize_label(value)[:64]


def load_acq_label(value: str) -> str:
    """Sanitize for path compatibility and truncate to 128 chars for CoreAPI."""
    return sanitize_label(value)[:128]


def load_file_name(value: t.Union[str, Path]) -> str:
    """Sanitize for path compatibility."""
    return sanitize_label(str(value))


def sanitize_label(value: str) -> str:
    """Sanitize and truncate labels for filesystem dir/filename compatibility."""
    # replace '*' with 'star' (to retain eg. DICOM MR T2* domain context)
    value = re.sub(r"\*", r"star", value)
    # replace any occurrences of (one or more) invalid chars w/ an underscore
    unprintable = [chr(c) for c in range(128) if chr(c) not in string.printable]
    invalid_chars = "*/:<>?\\|\t\n\r\x0b\x0c" + "".join(unprintable)
    value = re.sub(rf"[{re.escape(invalid_chars):s}]+", "_", value)
    # finally, truncate to 255 chars and return
    return value[:255]


def load_subj_sex(value: str) -> t.Optional[str]:
    """Normalize to lowercase and return validated value (or None)."""
    subj_sex = value.lower()
    subj_sex_map = {"m": "male", "f": "female", "o": "other"}  # dicom
    subj_sex = subj_sex_map.get(subj_sex, subj_sex)
    if re.match(r"^male|female|other|unknown$", subj_sex):
        return subj_sex
    return None


def load_subj_type(value: str) -> t.Optional[str]:  # pragma: no cover
    """Return validated subject type (or None)."""
    subj_type = value.lower()
    if re.match(r"^human|animal|phantom$", subj_type):
        return subj_type
    return None


# TODO
# def load_subj_race(value: str) -> t.Optional[str]:
#     """Return validated subject race (or None)."""
#     r"American Indian or Alaska Native|Asian"
#     r"|Native Hawaiian or Other Pacific Islander|Black or African American|White"
#     r"|More Than One Race|Unknown or Not Reported"


# def load_subj_ethnicity(value: str) -> t.Optional[str]:
#     """Return validated subject ethnicity."""
#     r"Not Hispanic or Latino|Hispanic or Latino|Unknown or Not Reported"


def load_sess_age(value: t.Union[str, int, float]) -> t.Optional[int]:
    """Return as a validated integer (or None)."""
    # NOTE add unit conversion here if/when needed later [target: seconds]
    try:
        return int(value)
    except ValueError:
        return None


def load_sess_weight(value: t.Union[str, int, float]) -> t.Optional[float]:
    """Return as a validated float (or None)."""
    # NOTE add unit conversion here if/when needed later [target: kilograms]
    try:
        return float(value)
    except ValueError:
        return None


def load_tags(value: t.Union[str, list]) -> list:
    """Return list of strings split by comma."""
    if isinstance(value, str):
        return value.split(",") if value else []
    return value


def load_timezone(value: str) -> t.Optional[str]:  # pragma: no cover
    """Return timezone string if it's a valid IANA timezone name."""
    if gettz(value):
        return value
    return None


def load_any(value):
    """Return value as-is."""
    return value  # pragma: no cover


def load_field_tuple(field: str, value) -> t.Tuple[str, t.Any]:
    """Return validated field name and value as a tuple."""
    field, _ = validate_import_field(field)
    if value is not None:
        value = IMPORT_FIELD_LOADERS.get(field, load_any)(value)
    return field, value


IMPORT_FIELD_LOADERS: t.Dict[str, t.Callable] = {
    # TODO consider moving routing id under project
    "external_routing_id": load_any,
    "group._id": load_group_id,
    "group.label": load_cont_label,
    "project._id": load_cont_id,
    "project.label": load_cont_label,
    # TODO consider supporting project info updates in uploader
    # TODO validate and raise on empty info key (project.info.)
    "project.info.*": load_any,
    "subject._id": load_cont_id,
    "subject.routing_field": load_any,
    "subject.label": load_cont_label,
    "subject.firstname": load_any,
    "subject.lastname": load_any,
    "subject.sex": load_subj_sex,
    "subject.type": load_subj_type,
    # "subject.race": load_subj_race,
    # "subject.ethnicity": load_subj_ethnicity,
    "subject.species": load_any,
    "subject.strain": load_any,
    "subject.tags": load_tags,
    "subject.info.*": load_any,
    "session._id": load_cont_id,
    "session.uid": load_any,
    "session.routing_field": load_any,
    "session.label": load_cont_label,
    "session.age": load_sess_age,
    "session.weight": load_sess_weight,
    "session.operator": load_any,
    "session.timestamp": Pattern.load_timestamp,
    "session.timezone": load_timezone,  # auto-populated from timestamp
    "session.tags": load_tags,
    "session.info.*": load_any,
    "acquisition._id": load_cont_id,
    "acquisition.uid": load_any,
    "acquisition.routing_field": load_any,
    "acquisition.label": load_acq_label,
    "acquisition.timestamp": Pattern.load_timestamp,
    "acquisition.timezone": load_timezone,  # auto-populated from timestamp
    "acquisition.tags": load_tags,
    "acquisition.info.*": load_any,
    "file.name": load_file_name,
    "file.type": load_any,
    "file.tags": load_tags,
    "file.info.*": load_any,
    "file.path": str,
    "file.provider_id": str,
    "file.reference": bool,
    "file.size": int,
    "file.client_hash": str,
    "file.zip_member_count": int,
}
LABEL_RE = r"[^/]+"
LABEL_FIELDS = {
    "group._id",
    "group.label",
    "project.label",
    "subject.label",
    "session.label",
    "acquisition.label",
    "file.name",
}
IMPORT_FIELDS = list(IMPORT_FIELD_LOADERS)
IMPORT_FIELD_INDEX = {field: index for index, field in enumerate(IMPORT_FIELDS)}
IMPORT_FIELD_NUM = defaultdict(lambda: len(IMPORT_FIELDS), IMPORT_FIELD_INDEX)


def validate_import_field(field: str) -> t.Tuple[str, str]:
    """Return canonic import field name and it's value regex for a short name."""
    field = parse_field_name(field, aliases=ALIASES, allowed=IMPORT_FIELDS)
    if field in LABEL_FIELDS:
        return field, LABEL_RE
    return field, ""


def validate_import_template_field(field: str) -> str:
    """Return canonic import field name if !prefixed, otherwise value as-is."""
    if field.startswith("!"):
        field, _ = validate_import_field(field[1:])
        return f"!{field}"
    # TODO validate that only path/dir/name[/ext? /type?] is used if not parsed
    return field


class ImportTemplate(Template):
    """Import template for formatting data or !metadata fields."""

    def __init__(self, template: str) -> None:
        """Init template with !field name validators."""
        super().__init__(template, validate=validate_import_template_field)


class ImportPattern(Pattern):
    """Import pattern for extracting metadata fields from strings."""

    def __init__(self, pattern: str) -> None:
        """Init pattern with field name validators and value loaders."""
        super().__init__(
            pattern,
            validate=validate_import_field,
            loaders=IMPORT_FIELD_LOADERS,
        )


# HELPERS


def parse_metadata_mappings(mappings: Mappings) -> t.Iterable[t.Tuple[str, str]]:
    """Parse and yield metadata mappings as a tuple."""
    if isinstance(mappings, str):
        mappings = [mappings]
    elif isinstance(mappings, dict):
        mappings = list(mappings.items())
    for mapping in mappings:
        if isinstance(mapping, str):
            yield mapping.split("=", maxsplit=1)  # type: ignore
        else:
            yield mapping


def validate_metadata_mapping(
    mapping: t.Tuple[str, str],
) -> t.Tuple["ImportTemplate", "ImportPattern"]:  # pragma: no cover
    """Return validated (ImportTemplate, ImportPattern) tuple from 2 strings."""
    # attempt left-to-right first, then reversed for input flexibility
    error: t.Optional[ValueError] = None
    for template, pattern in [mapping, reversed(mapping)]:
        try:
            return ImportTemplate(template), ImportPattern(pattern)
        except ValueError as exc:
            error = error or exc
    # always raise the left-to-right error for consistency
    assert error
    raise error


class FieldGetter:
    """Wrapper class dispatching attr/key access to multiple objects in order."""

    def __init__(self, *objects) -> None:
        """Init FieldGetter instance with one or more objects."""
        assert objects, "at least one object required"
        self._objects = objects

    def __getattr__(self, field):
        """Return the first object's attr that has it or raise AttributeError."""
        error: t.Optional[AttributeError] = None
        for obj in self._objects:
            try:
                return getattr(obj, field)
            except AttributeError as exc:
                error = exc
        assert error
        raise error

    def __getitem__(self, field):
        """Return the first object's key that has it or raise KeyError."""
        error: t.Optional[KeyError] = None
        for obj in self._objects:
            try:
                return obj[field]
            except KeyError as exc:
                error = exc
        assert error
        raise error
