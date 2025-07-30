"""EEG parsing module."""

import datetime
import math
import typing as t
import zipfile

import numpy as np
from fw_file.eeg import BDF, EDF, EEGLAB, BrainVision
from fw_meta import MetaData

from ..util import AnyPath


def process_brainvision(file_path: AnyPath) -> t.Tuple[t.Dict, MetaData, t.Dict]:
    """Process `file_path` and returns a `FileEntry` and its corresponding meta.

    Args:
        file_path (Path-like): Path to BrainVision archive.

    Returns:
        dict: Dictionary of file attributes to update.
        dict: Dictionary containing the file meta.
        dict: Dictionary containing the qc metrics.

    """
    if zipfile.is_zipfile(file_path):
        bv = BrainVision.from_zip(file_path)
    else:
        raise RuntimeError(
            "Input must be a zipped archive containing all three BrainVision files."
        )
    return _process(bv.file_format, bv.get_meta(), bv.fields)


def process_edf(file_path: AnyPath) -> t.Tuple[t.Dict, MetaData, t.Dict]:
    """Process `file_path` and returns a `FileEntry` and its corresponding meta.

    Args:
        file_path (Path-like): Path to EDF/EDF+ input-file.

    Returns:
        dict: Dictionary of file attributes to update.
        dict: Dictionary containing the file meta.
        dict: Dictionary containing the qc metrics.

    """
    edf = EDF(file_path)
    return _process(edf.file_format, edf.get_meta(), edf.fields)


def process_bdf(file_path: AnyPath) -> t.Tuple[t.Dict, MetaData, t.Dict]:
    """Process `file_path` and returns a `FileEntry` and its corresponding meta.

    Args:
        file_path (Path-like): Path to BDF/BDF+ input-file.

    Returns:
        dict: Dictionary of file attributes to update.
        dict: Dictionary containing the file meta.
        dict: Dictionary containing the qc metrics.

    """
    bdf = BDF(file_path)
    return _process(bdf.file_format, bdf.get_meta(), bdf.fields)


def process_eeglab(file_path: AnyPath) -> t.Tuple[t.Dict, MetaData, t.Dict]:
    """Process `file_path` and returns a `FileEntry` and its corresponding meta.

    Args:
        file_path (Path-like): Path to EEGLAB input-file or archive.

    Returns:
        dict: Dictionary of file attributes to update.
        dict: Dictionary containing the file meta.
        dict: Dictionary containing the qc metrics.

    """
    if zipfile.is_zipfile(file_path):
        elb = EEGLAB.from_zip(file_path)
    else:
        elb = EEGLAB(file_path)
    return _process(elb.file_format, elb.get_meta(), elb.fields)


def _process(
    format: str, meta: MetaData, fields: dict
) -> t.Tuple[t.Dict, MetaData, t.Dict]:
    header = {key: value for (key, value) in fields.items() if value}
    header = _clean_metadata_dict(header)
    fe = {"modality": "EEG", "info": {"header": {format: header}}}
    qc = {}
    return fe, meta, qc


def _clean_metadata_dict(d):
    if isinstance(d, dict):
        return {k: _clean_metadata_dict(v) for k, v in d.items()}
    elif isinstance(d, (list, np.ndarray)):
        d = list(d)
        return [_clean_metadata_dict(v) for v in d]
    elif isinstance(d, (int, float)) and math.isnan(d):
        return None
    elif isinstance(d, (datetime.datetime, datetime.date)):
        return d.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return d
