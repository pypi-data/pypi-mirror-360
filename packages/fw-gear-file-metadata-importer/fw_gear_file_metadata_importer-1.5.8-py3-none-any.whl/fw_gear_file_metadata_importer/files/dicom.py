"""Dicom parsing module."""

import logging
import os
import re
import sys
import typing as t
import warnings
import zipfile
from pathlib import Path
from typing import NamedTuple

import numpy
from fw_file.dicom import DICOM, DICOMCollection, get_config
from fw_file.dicom.dicom import get_value
from fw_meta import MetaData
from pydicom.datadict import dictionary_VR, tag_for_keyword
from pydicom.multival import MultiValue

from ..geometry import (
    compute_affine,
    compute_axis_from_origins,
    compute_normal,
    compute_slice_locations_from_origins,
    compute_slice_spacing_from_locations,
    is_uniform,
    split_by_location,
    split_by_orientation,
)
from ..transform import Matrix3DTransform
from ..util import AnyPath, load_p15e_tags_from_file, remove_empty_values, validate_file

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from nibabel.nicom import csareader

CONFIG = get_config()
CONFIG.read_only = True
CONFIG.reading_validation_mode = 1

log = logging.getLogger(__name__)

DENY_TAGS = {
    "PixelData",
    # TODO: Check why Pixel Data is in the list. Could it be in Siemens CSA?
    "Pixel Data",
    "ContourData",
    "EncryptedAttributesSequence",
    "OriginalAttributesSequence",
    "SpectroscopyData",
    "MrPhoenixProtocol",  # From Siemens CSA
    "MrEvaProtocol",  # From Siemens CSA
    "FileMetaInformationVersion",  # OB in file_meta
    "EncapsulatedDocument",
}

DENY_VRS = {
    "OB",  # Don't save any byte objects
    "OB_OW",  # ...
    "OW",  # ...
    "UN",  # Undefined VR
    "UT",  # Unlimited text VR.
}

# TODO: extend that set
ARRAY_TAGS = {
    "AcquisitionNumber",
    "AcquisitionTime",
    "DiffusionBValue",
    "DiffusionGradientOrientation",
    "EchoTime",
    "ImageOrientationPatient",
    "ImagePositionPatient",
    "ImageType",
    "InstanceNumber",
    "SliceLocation",
}

# Private Dicom tag to keep, in the format (PrivateCreatorName, 0099xx10)
PRIVATE_TAGS = set()

# matches either hexadecimal, keyword or private tag notation
# e.g. "00100020" or "PatientID" or "GEMS_PARM_01, 0043xx01"
VALID_KEY = re.compile(
    r"^[\dA-Fa-f]{8}$|^[A-Za-z]+$|^\w+,\s*[0-9A-Fa-f]{4}[xX]{2}[0-9A-Fa-f]{2}$"
)


class DICOMFindings(NamedTuple):
    """Class to store findings on dicom file and report on them."""

    # True is file is zero_byte, false otherwise.
    zero_byte: bool
    # True is file can be decoded without Exception, false otherwise
    decoding: bool
    # List of tracking events (changes made to the raw data elements during decoding)
    tracking: list

    def is_valid(self):
        """Returns True if file is not zero bite and can be decoded, else False."""
        if not self.zero_byte and self.decoding:
            return True
        return False

    def __repr__(self):
        """Returns string representation of DICOMFindings object."""
        return (
            f"{self.__class__.__name__}:"
            f"\n\t0-byte: {self.zero_byte}\n\tdecoding: {self.decoding}"
        )


def update_array_tag(custom_tags: t.Dict[str, bool]):  # noqa: PLR0912
    """Update PRIVATE_TAGS and ARRAY_TAGS list.

    Args:
        custom_tags (dict): Dictionary of type with key/value of type tag: bool.
            If bool=True, tag is added to PRIVATE_TAGS and ARRAY_TAGS. If bool=False,
            tag is removed from PRIVATE_TAGS and ARRAY_TAGS.
    """
    if custom_tags:
        # validate key/value
        for k, v in custom_tags.items():
            if not VALID_KEY.match(k):
                log.error(
                    "Invalid key defined in project.info.context.header.dicom: %s\n"
                    "Valid key format is hexadecimal (e.g. '00100020'), "
                    "keyword (e.g. 'PatientID') or "
                    "private tag notation (e.g. 'GEMS_PARM_01, 0043xx01'). "
                    "Please check your project context.",
                    k,
                )
                sys.exit(1)
            if isinstance(v, str):
                if v.strip().lower() == "false":
                    custom_tags[k] = False
                elif v.strip().lower() == "true":
                    custom_tags[k] = True
                else:
                    log.error(
                        "Invalid value defined in project.info.context.header.dicom "
                        "for key %s. Valid value is boolean, 'True' or 'False'",
                        k,
                    )
                    sys.exit(1)

        for k, bool_val in custom_tags.items():
            is_private = False

            if "," in k:  # key pattern is "PrivateCreatorName, GGGGxxEE"
                k = tuple(p.strip() for p in k.split(","))
                is_private = True

            if bool_val:
                if is_private and k not in PRIVATE_TAGS:
                    PRIVATE_TAGS.add(k)
                if k not in ARRAY_TAGS:
                    ARRAY_TAGS.add(k)
            else:
                if k in PRIVATE_TAGS:
                    PRIVATE_TAGS.remove(k)
                if k in ARRAY_TAGS:
                    ARRAY_TAGS.remove(k)
                if k not in DENY_TAGS:
                    DENY_TAGS.add(k)


def inspect_file(file_: DICOM) -> DICOMFindings:
    """Returns the DICOMFindings for the input DICOM instance."""
    zero_byte = False if os.path.getsize(file_.filepath) > 1 else True
    try:
        file_.decode()  # NB: file_.read_context gets populated during decoding.
        decoding = True
    except Exception:  # pragma: no cover
        log.error(
            "Exception attempting to decode, please ensure dicom-fixer has run",
            exc_info=True,
        )
        decoding = False

    # store tracking events
    file_.read_context.trim()
    tracking_events = [de.export() for de in file_.read_context.data_elements]
    return DICOMFindings(zero_byte, decoding, tracking_events)


def inspect_collection(collection: DICOMCollection) -> t.List:
    """Return list of findings for each Dicom in collection.

    Args:
        collection: DICOMCollection object

    Returns:
        list: findings found during inspection
    """
    # Report on progress every ~10%
    coll_len = len(collection)
    decis = int(coll_len / 10) or 1
    log.info(f"Inspecting {coll_len} files in collection")
    findings = []
    for i, file_ in enumerate(collection):
        if i % decis == 0:
            log.info(f"{i}/{coll_len} ({100 * i / coll_len:.2f}%)")
        findings.append(inspect_file(file_))
    return findings


def get_dicom_header(dcm: DICOM, deny: bool = True) -> dict:
    """Returns a dictionary representation of the dicom header of the DICOM instance.

    Args:
        dcm (DICOM): The DICOM instance.
        deny: Deny by VR type as well as file name.

    Returns:
        dict: A dictionary representation of the dicom header.
    """
    header = {}

    header.update(get_preamble_dicom_header(dcm, deny))
    header.update(get_core_dicom_header(dcm, deny))
    header = remove_empty_values(header)

    return header


def is_keyword_denied(kw: t.Any, deny=True) -> bool:
    """Helper function to decide whether or not to deny a keyword from being kept.

    Args:
        kw: Input keyword
        deny (bool): Deny by VR type as well as specific keys.

    Returns:
        bool: True if value should be removed, False otherwise.
    """
    if kw in DENY_TAGS:
        return True
    if deny and isinstance(kw, str):
        tag = tag_for_keyword(kw)
        if not tag:
            return True
        return dictionary_VR(tag) in DENY_VRS
    return False


def get_preamble_dicom_header(dcm: DICOM, deny=True) -> t.Dict:
    """Returns a representation of the dicom header preamble of the DICOM instance.

    Args:
        dcm (DICOM): The DICOM instance.
        deny (bool): Deny by VR type as well as file name.

    Returns:
        dict: A dictionary representation of the dicom preamble header.
    """
    header = {}

    for kw in dcm.dataset.file_meta.dir():
        if is_keyword_denied(kw, deny):
            continue
        header[kw] = get_value(dcm.dataset.file_meta[kw].value, dcm.read_context)
    return header


def get_core_dicom_header(dcm: DICOM, deny=True) -> t.Dict:
    """Returns a dictionary representation of the dicom header but the preamble.

    Args:
        dcm (DICOM): The DICOM instance.
        deny (bool): Deny by VR type as well as file name.

    Returns:
        dict: A dictionary representation of the dicom header.
    """
    header = {}

    for kw in dcm.dir() + list(PRIVATE_TAGS):
        if is_keyword_denied(kw, deny):
            log.debug(f"Skipping {kw} - marked as deny.")
            continue
        # some keyword may be repeating group and none unique
        if tag_for_keyword(kw) is None and kw not in PRIVATE_TAGS:
            log.debug(f"Skipping {kw} - none unique.")
            continue
        try:
            elem = dcm.get_dataelem(kw)
            if elem.is_private and isinstance(kw, tuple):
                header_kw = ",".join(kw)
            else:
                header_kw = kw
            if kw == "PerFrameFunctionalGroupsSequence":
                # For large multiframe DICOMs, storing all pffgs can cause problems.
                # To prevent that, we're only storing the first frame's sequence.
                header[header_kw] = get_core_dicom_header(dcm[kw][0])
            elif elem.VR == "SQ":
                header[header_kw] = []
                for i, ds in enumerate(dcm[kw]):
                    header[header_kw].append(get_core_dicom_header(ds))
            else:
                header[header_kw] = dcm[kw]
        except KeyError:  # private tag
            continue

    return header


def get_siemens_csa_header(dcm: DICOM) -> t.Dict:
    """Returns a dict containing the Siemens CSA header for image and series.

    More on Siemens CSA header at https://nipy.org/nibabel/dicom/siemens_csa.html.

    Args:
        dcm (DICOM): The DICOM instance.

    Returns:
        dict: A dictionary containing the CSA header.

    """
    csa_header = {"image": {}, "series": {}}
    csa_header_image = csareader.get_csa_header(dcm.dataset.raw, csa_type="image")
    if csa_header_image:
        csa_header_image_tags = csa_header_image.get("tags", {})
        for k, v in csa_header_image_tags.items():
            if (v["items"] is not None and not v["items"] == []) and k not in DENY_TAGS:
                csa_header["image"][k] = v["items"]

    csa_header_series = csareader.get_csa_header(dcm.dataset.raw, csa_type="series")
    if csa_header_series:
        csa_header_series_tags = csa_header_series.get("tags", {})
        for k, v in csa_header_series_tags.items():
            if (v["items"] is not None and not v["items"] == []) and k not in DENY_TAGS:
                csa_header["series"][k] = v["items"]

    return csa_header


def get_dicom_array_header(collection: DICOMCollection) -> dict:
    """Returns array of DICOM tags for tag in ARRAY_TAGS.

    Args:
        collection: DICOMCollection object

    Returns:
        dict: array_header dictionary
    """
    primary = collection[0].dataset

    def get_frame_item_value(item, t):
        # Try frame item level
        value = item.get(t)
        if value is None:
            # Next try sequences in frame item
            for seq_name in per_item_seqs:
                seq = item.get(seq_name)
                if seq is not None and len(seq) > 0:
                    value = seq[0].get(t)
                    if value is not None:
                        break
        if value is None:
            # Finally try against root level if not present per frame
            value = primary.get(t)
        if isinstance(value, MultiValue):
            value = numpy.array(value).tolist()
        return value

    """Returns array of dicom tags for tag in ARRAY_TAGS."""
    array_header = {}
    n = len(collection)
    is_multiframe = (n == 1) and "NumberOfFrames" in collection[0].dataset
    if not is_multiframe:
        for at in ARRAY_TAGS:
            arr = collection.bulk_get(at)
            if any(arr):
                array_header[at] = arr
    else:
        n_frames = primary.get("NumberOfFrames")
        pffgs = primary.get("PerFrameFunctionalGroupsSequence")
        per_item_seqs = [
            "PlanePositionSequence",
            "PlaneOrientationSequence",
            "PixelMeasuresSequence",
        ]
        if (n_frames > 0) and (pffgs is not None) and (len(pffgs) == n_frames):
            for at in ARRAY_TAGS:
                value_list = []
                any_value_not_null = False

                for frame_item in pffgs:
                    value = get_frame_item_value(frame_item, at)
                    value_list.append(value)
                    if value is not None:
                        any_value_not_null = True
                if any_value_not_null:
                    array_header[at] = value_list
    return array_header


def get_file_info_header(
    dcm: DICOM,
    collection: t.Optional[DICOMCollection] = None,
    siemens_csa: bool = False,
    deny: bool = True,
) -> t.Dict:
    """Returns a dictionary representing the header of the DICOM instance.

    Args:
        dcm (DICOM): The DICOM instance.
        collection (DICOMCollection or None): A DICOMCollection instance.
        siemens_csa (bool): If true, extracts the Siemens CSA header and stores under
            "csa" key.
        deny: Deny by VR type as well as file name.

    Returns:
        dict: A dictionary containing the header information.
    """
    header = dict()
    header["dicom"] = get_dicom_header(dcm, deny)
    if collection:
        header["dicom_array"] = get_dicom_array_header(collection)
    if siemens_csa:
        manufacturer = header["dicom"].get("Manufacturer")
        if (
            manufacturer
            and isinstance(manufacturer, str)
            and manufacturer.lower().strip() != "siemens"
        ):
            log.info("Manufacturer is not Siemens - skipping CSA parsing")
            return header
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                header["csa"] = get_siemens_csa_header(dcm)
    return header


def get_file_qc(dcm: DICOM, file_path: t.Optional[AnyPath] = None) -> t.Dict:
    """Returns the tracking trace of dcm.

    Args:
        dcm (DICOM): The DICOM instance.
        file_path (Path-like): Optional file path

    Returns:
        dict: Dictionary containing trace of updated data elements.
    """
    qc = {"filename": Path(file_path or dcm.filepath).parts[-1], "trace": []}
    if dcm.read_context:
        dcm.read_context.trim()
        for raw_elem in dcm.read_context.data_elements:
            de_trace = raw_elem.export()
            for event in de_trace["events"]:
                qc["trace"].append(f"Tag {de_trace['original'].tag} {event}")
    return qc


def preprocess_input(
    input_file: AnyPath,
) -> t.Tuple[DICOM, t.Union[DICOMCollection, None]]:
    """Returns a DICOM and optionally a DICOMCollection if input_file is a zip.

    If input_file is a zip archive, returns one a representative zip member.

    Args:
        input_file (AnyPath): Path-like object to input file.

    Returns:
        DICOM: A representative DICOM File instance.
        DICOMCollection or None: A Collection or None if input_file is not a zip
            archive.
    """
    if not isinstance(input_file, Path):
        input_file = Path(input_file)

    # validate input_file
    validation_errors = validate_file(input_file)
    if validation_errors:
        log.error(f"Errors found validating input file: {validation_errors}")
        sys.exit(1)

    if zipfile.is_zipfile(input_file):
        log.info(f"Loading dicoms from archive at {input_file}")
        collection = DICOMCollection.from_zip(input_file, force=True)
        try:
            log.info("Attempting to sort dicoms by InstanceNumber")
            collection.sort(key=lambda x: x.get("InstanceNumber"))
        except TypeError:  # InstanceNumber not found, not sorting
            log.info("InstanceNumber missing from collection - skipping sorting.")
            pass
        except ValueError as e:
            log.error(f"Cannot extra meta, reason: {e.args[0]}")
            sys.exit(1)
        collection_findings = inspect_collection(collection)
        file_ = None
        for i, dicom_findings in enumerate(collection_findings):
            if dicom_findings.is_valid():
                file_ = collection[i]
                break

        if not file_:
            log.error(f"Unable to find a valid Dicom file in archive: {input_file}.")
            sys.exit(1)
    else:
        collection = None
        file_ = DICOM(input_file, force=True)
        dicom_findings = inspect_file(file_)
        if not dicom_findings.is_valid():
            log.error(f"Input file is invalid: {input_file}\n{dicom_findings}")
            sys.exit(1)

    return file_, collection


def get_derived_metadata(  # noqa: PLR0915
    file_: DICOM, collection: DICOMCollection, header
) -> t.Tuple[dict, list]:
    """Add derived metadata under 'derived' key. Only applies to DICOMs with the image plane module.

    Args:
        file_ (DICOM): A DICOM instance.
        collection (DICOMCollection): A DICOMCollection instance.
        header (dict): Dictionary computed from get_dicom_array_header

    Returns:
        Tuple[dict, list]: A tuple containing the derived metadata and a list of errors.
    """

    derived = {}
    errors = []

    # Gets tag value from header or collection
    def get_tag_value(header: dict, tag: str):
        """Gets a tag value from the header.

        Args:
            header (): Header with 'dicom_array' and 'dicom' members
            tag (): Name of value to retrieve

        Returns: Value retrieved from dicom_array and then dicom
        """
        dicom_array = header.get("dicom_array")
        value = dicom_array.get(tag)
        if value is None:
            dicom_values = header.get("dicom")
            value = dicom_values.get(tag)
        return value

    ipps = get_tag_value(header, "ImagePositionPatient")
    iops = get_tag_value(header, "ImageOrientationPatient")
    pixel_spacing = get_tag_value(header, "PixelSpacing")
    if not all([ipps, iops, pixel_spacing]):
        # These tags are required in ImagePlane IOD.
        # Skip derived metadata for DCMs that don't have the ImagePlane IOD
        log.info(
            "Dicom does not include the ImagePlane IOD. Skipping derived metadata."
        )
        return derived, errors

    error = validate_geometry(ipps, iops, collection)
    if not error:
        orientation = iops[0]
        # Compute axis connecting slice positions
        slice_axis = compute_axis_from_origins(ipps)
        if slice_axis is None:
            slice_axis = compute_normal(orientation)
        # Compute scalar locations of 3D positions along axis
        slice_locations = compute_slice_locations_from_origins(ipps, slice_axis)
        s_max, s_min = slice_locations.max(), slice_locations.min()
        derived["MaxSliceLocation"] = s_max
        derived["MinSliceLocation"] = s_min
        derived["ScanCoverage"] = abs(s_max - s_min)
        if not get_tag_value(header, "SliceLocation"):
            derived["SliceLocation"] = slice_locations.tolist()
        derived["SliceAxis"] = slice_axis.tolist()

        # Add phase information based on geometry
        phase_count, indexes = split_by_orientation(iops)
        if phase_count == 1 and is_uniform(iops) and (slice_locations is not None):
            phase_count, indexes = split_by_location(slice_locations)
        derived["PhaseCount"] = phase_count
        if phase_count > 1:
            derived["PhaseIndexes"] = indexes.tolist()

        slice_spacing = compute_slice_spacing_from_locations(slice_locations)
        if (slice_spacing) and (slice_spacing > 0.1) and is_uniform(iops):
            derived["SpacingBetweenSlices"] = slice_spacing
            if is_uniform(pixel_spacing):
                # We now have all sufficient conditions to compute affine transform
                axes = [orientation[0:3], orientation[3:6], slice_axis]
                spacing = [pixel_spacing[0], pixel_spacing[1], slice_spacing]
                origin = ipps[0]
                affine = compute_affine(axes=axes, origin=origin, spacing=spacing)
                derived["affine"] = affine.tolist()

                # Compute 3D fov
                n_cols = file_.get("columns")
                n_rows = file_.get("rows")
                n_slices = len(collection)
                transform = Matrix3DTransform(affine)
                p1 = transform.transform_point([n_cols - 1, n_rows - 1, n_slices - 1])
                fov = numpy.abs(p1 - origin).round(decimals=1)
                derived["fov"] = fov.tolist()
    else:
        log.warning(
            "Error found when computing scan coverage. "
            "Check file.info.qc.derived for details."
        )
        errors.append(error)

    return derived, errors


def validate_geometry(
    ipps: t.List, iops: t.List, collection: DICOMCollection
) -> t.Optional[str]:
    """Return a string containing the error found or None if none found.

    Args:
        iops ():
        ipps (list): A list of ImagePositionPatient values.
        iops (list): A list of ImageOrientationPatient values.
        collection (DICOMCollection): A DICOMCollection instance.

    Returns:
        str: The error or None if no error.
    """
    error = None
    if ipps is None:
        return f"ImagePositionPatient missing for file {collection[0].filepath}"
    if iops is None:
        return f"ImageOrientationPatient missing for file {collection[0].filepath}"
    if len(ipps) != len(iops):
        return (
            "ImageOrientationPatient and ImagePositionPatient do not have same "
            "length for {collection[0].filepath}"
        )

    def validate_vector(ivo, tag, expected_length):
        for i, iv in enumerate(ivo):
            if iv is None:
                return f"{tag} missing for file {collection[i].filepath}"
            if len(iv) != expected_length:
                return (
                    f"{tag} for file {collection[i].filepath}"
                    f" has incorrect length ({len(iv)})"
                )
            elif not isinstance(iv[2], float):
                return (
                    f"{tag}[2] for file {collection[i].filepath}"
                    f" has incorrect type ({type(iv[2]).__name__})"
                )

    error = validate_vector(ipps, "ImagePositionPatient", 3)
    if not error:
        error = validate_vector(iops, "ImageOrientationPatient", 6)
    return error


def process(
    input_path: AnyPath, siemens_csa: bool = False, derived: bool = False
) -> t.Tuple[t.Dict, MetaData, t.Dict]:
    """Process `file_path` and returns a `FileEntry` and its corresponding meta.

    Args:
        input_path (Path-like): Path to input-file.
        siemens_csa (bool): If True, extracts Siemens CSA header (Default: False).
        derived (bool): If True, calculates derived metadata.

    Returns:
        dict: Dictionary of file attributes to update.
        dict: Dictionary containing the file meta.
        dict: Dictionary containing the qc metrics.
    """
    file_, collection = preprocess_input(input_path)
    log.info("Getting file header")
    header = get_file_info_header(file_, collection, siemens_csa=siemens_csa)
    log.info("Getting file QC info")
    qc = get_file_qc(file_)
    if derived and collection:
        log.info("Calculating derived metadata")
        derived_data, errors = get_derived_metadata(file_, collection, header)
        if derived_data:
            header.update({"derived": derived_data})
        if errors:
            qc["derived"] = errors

    fe = {"modality": file_.get("Modality"), "info": {"header": header}}
    return fe, file_.get_meta(), qc


def add_p15e_tags():
    """Adds the p15E tags to the default import list."""
    global PRIVATE_TAGS  # noqa: PLW0602
    [PRIVATE_TAGS.add(tag) for tag in load_p15e_tags_from_file()]
