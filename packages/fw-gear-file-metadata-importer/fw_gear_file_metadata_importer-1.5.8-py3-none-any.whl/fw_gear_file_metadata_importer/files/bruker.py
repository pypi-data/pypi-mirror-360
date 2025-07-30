"""Bruker Paravision parsing module."""

import logging
import sys
import tempfile
import typing as t
import zipfile
from pathlib import Path

from fw_file.bruker import ParaVision
from fw_meta import MetaData

from ..util import AnyPath, decode

log = logging.getLogger(__name__)


def paravis_extract_files(
    input_zfile: AnyPath, tmp_path: AnyPath
) -> t.Tuple[Path, Path]:
    """Returns the list of file in the zip folder.

    If input_file is a zip archive.

    Args:
        input_zfile (AnyPath): Path-like object to input file.
        tmp_path (AnyPath): A temporary folder path.

    Returns:
        tuple: Tuple containing the acqp and method file paths.
    """
    tmp_path = Path(tmp_path)
    acqp_path = None
    method_path = None

    try:
        with zipfile.ZipFile(input_zfile) as zfile:
            infiles = zfile.namelist()

            acqp = [s for s in infiles if "acqp" in s and "._acqp" not in s]
            if acqp:
                zfile.extract(acqp[0], path=tmp_path, pwd=None)
                acqp_path = tmp_path / acqp[0]

            method = [s for s in infiles if "method" in s and "._method" not in s]
            if method:
                zfile.extract(method[0], path=tmp_path, pwd=None)
                method_path = tmp_path / method[0]

    except (IOError, zipfile.BadZipfile) as exception:
        log.error("Unable to open ZIP file: %s" % (repr(exception)))
        sys.exit(1)

    return acqp_path, method_path


def process(file_path: t.Union[AnyPath, None]) -> t.Tuple[t.Dict, MetaData, t.Dict]:
    """Extract and process files, then merge dictionaries.

    Args:
        file_path (Path-like): Path to input-file.

    Returns:
        dict: Dictionary of file attributes to update.
        dict: Dictionary containing the file meta.
        dict: Dictionary containing the qc metrics.
    """
    with tempfile.TemporaryDirectory() as tmp_path:
        acqp_path, method_path = paravis_extract_files(file_path, tmp_path)
        fe_acqp, meta_acqp, qc_acqp = process_file(acqp_path)
        fe_method, meta_method, qc_method = process_file(method_path)
    fe = fe_merge(fe_acqp, fe_method)
    meta = meta_acqp | meta_method
    qc = qc_acqp | qc_method
    return fe, meta, qc


def process_file(
    file_path: t.Union[AnyPath, None],
) -> t.Tuple[t.Dict, MetaData, t.Dict]:
    """Process `file_path` and returns a `FileEntry` and its corresponding meta.

    Args:
        file_path (Path-like): Path to input-file.

    Returns:
        dict: Dictionary of file attributes to update.
        dict: Dictionary containing the file meta.
        dict: Dictionary containing the qc metrics.
    """
    paravision_header = {}
    meta = MetaData()
    if file_path:
        paravision_file = ParaVision(file_path)
        meta = paravision_file.get_meta()
        # Populate header by getting values of iterated header keys.
        for key, val in paravision_file.items():
            if isinstance(val, bytes):
                val = decode(val)
            paravision_header[key] = val

    fe = {"info": {"header": {"paravision": paravision_header}}}
    qc = {}

    return fe, meta, qc


def fe_merge(fe_acqp: t.Dict, fe_method: t.Dict) -> t.Dict:
    """Merge the "fe" of acqp and method dictionaries to a single "fe" dictionary."""
    fe = {"info": {"header": {"paravision": {"acqp": {}, "method": {}}}}}
    try:
        if fe_acqp:
            fe["info"]["header"]["paravision"]["acqp"] = fe_acqp["info"]["header"][
                "paravision"
            ]

        if fe_method:
            fe["info"]["header"]["paravision"]["method"] = fe_method["info"]["header"][
                "paravision"
            ]

    except KeyError:
        log.warning("Cannot find acqp/method metadata or are not dictionaries")

    return fe
