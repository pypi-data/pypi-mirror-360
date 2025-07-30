"""Philips parsing module."""

import decimal
import logging
import typing as t
import zipfile

from fw_file.philips import PARFile
from fw_meta import MetaData
from fw_utils import AnyPath

from fw_gear_file_metadata_importer.util import decode

log = logging.getLogger(__name__)


def process(file_path: AnyPath) -> t.Tuple[t.Dict, MetaData, t.Dict]:
    """Process `file_path` and returns a `FileEntry` and its corresponding meta.

    Args:
        file_path (Path-like): Path to input-file.

    Returns:
        dict: Dictionary of file attributes to update.
        dict: Dictionary containing the file meta.
        dict: Dictionary containing the qc metrics.

    """
    if zipfile.is_zipfile(file_path):
        par_file = PARFile.from_zip(file_path)
    else:
        par_file = PARFile(file_path)

    # Populate header by getting values of iterated header keys.
    par_header = dict()
    for key in par_file.fields:
        # filter keys that are not integer
        #
        if isinstance(key, str):
            # Convert from numpy list to value
            val = par_file[key]  # .tolist()

            if isinstance(val, decimal.Decimal):
                val = float(val)

            # Account for list including float values
            if isinstance(val, list) and len(val) > 1:
                for i, v in enumerate(val):
                    if not isinstance(v, str):
                        val[i] = float(v)

            # If still bytes try to decode, else use hex string.
            if isinstance(val, bytes):
                val = decode(val)

            par_header[key] = val
        else:
            log.debug(f"Skipping key {key} with type {type(key)}")

    if "modality" in par_header:
        fe = {
            "modality": par_header["modality"],
            "info": {"header": {"par": par_header}},
        }
    else:
        fe = {"modality": "MR", "info": {"header": {"par": par_header}}}

    qc = {}
    return fe, par_file.get_meta(), qc
