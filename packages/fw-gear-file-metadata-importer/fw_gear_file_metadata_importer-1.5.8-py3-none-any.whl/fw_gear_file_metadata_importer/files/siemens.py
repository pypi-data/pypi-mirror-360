"""Siemens PTD (Dicom based) parsing module."""

import logging
import typing as t
from pathlib import Path

from fw_file.siemens import PTDFile
from fw_meta import MetaData

from . import dicom

AnyPath = t.Union[str, Path]

log = logging.getLogger(__name__)


def process_ptd(
    file_path, siemens_csa: bool = False
) -> t.Tuple[t.Dict, MetaData, t.Dict]:
    """Process `file_path` and returns a `FileEntry` and its corresponding meta.

    Args:
        file_path (Path-like): Path to input-file.
        siemens_csa (bool): If True, extracts Siemens CSA header (Default: False).

    Returns:
        dict: Dictionary of file attributes to update.
        dict: Dictionary containing the file meta.
        dict: Dictionary containing the qc metrics.

    """
    # Extract dicom header
    ptd_file = PTDFile(file_path)
    header = dicom.get_file_info_header(ptd_file.dcm, None, siemens_csa=siemens_csa)
    # Extract PTD preamble
    try:
        ptd_preamble = ptd_file.preamble.decode("utf-8")
        header.update({"ptd": ptd_preamble})
    except UnicodeDecodeError:
        log.warning("Could not decode ptd preamble.  Not saving.")

    qc = dicom.get_file_qc(ptd_file.dcm, ptd_file.filepath)
    fe = {"modality": ptd_file.dcm.get("Modality"), "info": {"header": header}}
    return fe, ptd_file.dcm.get_meta(), qc
