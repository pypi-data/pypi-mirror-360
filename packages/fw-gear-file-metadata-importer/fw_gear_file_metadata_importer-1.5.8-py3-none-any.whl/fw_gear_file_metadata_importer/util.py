"""Util module."""

# <!-- markdown-link-check-disable -->
import copy
import csv
import logging
import os
import re
import typing as t
from pathlib import Path
from zipfile import ZipFile

from flywheel_gear_toolkit import GearToolkitContext
from fw_meta import MetaData
from pydicom.tag import BaseTag

AnyPath = t.Union[str, Path]
location = Path(__file__).parents[0]

log = logging.getLogger(__name__)

# From https://gitlab.com/flywheel-io/product/backend/core-api/-/blob/master/core/models/file_types.py
FILETYPES = {
    "dicom": [".dcm", ".dcm.zip", ".dicom.zip", ".dicom"],
    "nifti": [".nii.gz", ".nii", ".nifti"],
    "ParaVision": [".pv5.zip", ".pv6.zip"],
    "parrec": [".par", ".rec", ".PAR", ".REC"],  # TODO .lower()?
    "eeg header": [".vhdr"],
    "archive": [".zip"],
}
# Adding additional file types
FILETYPES.update(
    {"ptd": [".ptd"], "edf": [".edf"], "bdf": [".bdf"], "eeglab": [".set"]}
)


def get_startswith_lstrip_dict(dict_: t.Dict, startswith: str) -> t.Dict:
    """Returns dictionary filtered with keys starting with startswith."""
    res = {}
    for k, v in dict_.items():
        if k.startswith(startswith):
            res[k.split(f"{startswith}.")[1]] = v
    return res


def validate_file(filepath: AnyPath) -> t.List[str]:
    """Returns a list of validation errors if any."""
    errors = []
    errors += validate_file_size(filepath)
    return errors


def validate_file_size(filepath: AnyPath) -> t.List[str]:
    """Returns a list of validation errors related to file size."""
    errors = []
    if not os.path.getsize(filepath) > 1:
        errors.append("File is empty: {}".format(filepath))
    return errors


def sanitize_modality(modality: str) -> str:
    """Remove invalid characters in modality.

    Args:
        modality (str): Modality string.

    Returns:
        str: Sanitized modality string.
    """
    reg = re.compile(r"[^ 0-9a-zA-Z_-]+")
    modality_sanitized = reg.sub("-", modality)
    if modality_sanitized != modality:
        log.info(f"Sanitizing modality {modality} -> {modality_sanitized}")
    return modality_sanitized


def create_metadata(
    context: GearToolkitContext, fe: t.Dict, meta: MetaData, qc: t.Dict
):
    """Populate .metadata.json.

    Args:
        context (GearToolkitContext): The gear context.
        fe (dict): A dictionary containing the file attributes to update.
        meta (MetaData): A MetaData containing the file "metadata"
            (parents container info)
        qc (dict): QC information
    """
    file_input = context.get_input("input-file")

    # Add qc information
    context.metadata.add_qc_result(
        file_input,
        "metadata-extraction",
        # TODO: Add FAIL?
        state="PASS",
        data=qc,
    )
    context.metadata.update_file(file_input, info=fe.get("info", {}))
    if fe.get("modality"):
        modality = sanitize_modality(fe.get("modality"))
        context.metadata.update_file(file_input, modality=modality)

    # parent containers update
    # TODO revisit that age cannot be passed
    if "session.age" in meta:
        _ = meta.pop("session.age")
    context.metadata.update_container(
        "session", **get_startswith_lstrip_dict(meta, "session")
    )
    context.metadata.update_container(
        "subject", **get_startswith_lstrip_dict(meta, "subject")
    )
    context.metadata.update_container(
        "acquisition", **get_startswith_lstrip_dict(meta, "acquisition")
    )

    # https://flywheelio.atlassian.net/browse/GEAR-868
    # Subject needs to be updated on session in old-core
    # These two lines make this gear compatible with 15.x.x and 14.x.x
    sub = context.metadata._metadata.pop("subject")
    context.metadata._metadata.get("session").update({"subject": sub})


def remove_empty_values(d: t.Dict, recurse=True) -> t.Dict:
    """Removes empty value in dictionary.

    Args:
        d (dict): A dictionary.
        recurse (bool): If true, recurse nested dictionary.

    Returns:
        dict: A filtered dictionary.
    """
    d_copy = copy.deepcopy(d)
    for k, v in d.items():
        if isinstance(v, dict) and recurse:
            d_copy[k] = remove_empty_values(v, recurse=recurse)
        if isinstance(v, BaseTag):
            continue
        if v == "" or v is None or v in ([], {}):
            d_copy.pop(k)
    return d_copy


def decode(val: bytes):
    """Decode decoded val or hex repr if cannot be decoded."""
    try:
        val = val.decode("utf-8")
    except UnicodeDecodeError:
        log.debug(f"Cannot decode bytes {val}.  Replacing with hex")
        val = val.hex()
    return val


def archived_filetype(fpath: AnyPath) -> t.Optional[str]:
    """Return filetype of underlying files.

    Args:
        fpath (AnyPath): Filepath of archive (must be .zip)

    Returns:
        str: Filetype of underlying files in archive
    """
    if Path(fpath).suffix != ".zip":
        return None

    with ZipFile(fpath) as z:
        files = z.namelist()

    # Set to store the filetype of every file in archive
    filetypes = set()
    for f in files:
        for ft, suffixes in FILETYPES.items():
            if any([f.endswith(suffix) for suffix in suffixes]):
                filetypes.add(ft)

    # If multiple different filetypes in archive, filetype is ambiguous
    # return None
    if len(filetypes) != 1:
        return None
    # Otherwise return the singular underlying filetype in this archive
    return filetypes.pop()


def format_address(raw_address: str) -> str:
    """Attempts to standardize dicom attribute addresses to: ####xx## format.
    Dicom attribute addresses may come in different forms, e.g.:
     - (2001,1023)
     - 20011012
     - 2001, 1023
     - ( 2001, 1023 )
     etc.

     This attempts to standardize them by stripping parenthesis and white spaces from
     the ends of the string,removing any commas and whitespaces, and replacing the 5th
     and 6th address characters with "x"'s, following the format defined here:
     https://dicom.nema.org/medical/dicom/current/output/html/part15.html#chapter_E

    """
    # Remove leading and trailing white spaces and parenthesis
    address = raw_address.strip(" ()")
    # Remove comma and ensure no whitespaces mid-string
    address = address.replace(",", "").replace(" ", "")
    # Ensure final four indexes start with "xx"
    address = address[:4] + "xx" + address[6:]
    return address


def load_p15e_tags_from_file() -> t.Set[str]:
    """Loads list of P15E compliant dicom attributes from the "private_tags.csv" file."""

    p15e_private_tags = set()
    csv_path = os.path.join(location, "P15E_private_tags.csv")
    with open(csv_path, encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            p15e_private_tags.add(
                (row["Private Creator"], format_address(row["Data Element"]))
            )

    return p15e_private_tags
