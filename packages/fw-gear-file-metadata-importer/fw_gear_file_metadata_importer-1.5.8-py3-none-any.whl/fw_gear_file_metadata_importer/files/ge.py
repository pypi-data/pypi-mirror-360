"""PFILE parsing module."""

import gzip
import logging
import os
import shutil
import sys
import tempfile
import typing as t
import zipfile
from os import listdir
from os.path import isfile, join
from pathlib import Path

from fw_file.ge import PFile
from fw_meta import MetaData

from ..util import AnyPath, decode

log = logging.getLogger(__name__)


def pfile_extract_files(input_zfile, tmp_path: AnyPath) -> Path:
    """Returns the list of file in the zip folder.

    If input_zfile is a zip archive.

    Args:
        input_zfile (AnyPath): Path-like object to input file.
        tmp_path (AnyPath): A temporary folder path.

    Returns:
        Path: Path to the extracted pfile.
    """
    tmp_path = Path(tmp_path)

    fname = os.path.basename(input_zfile)
    fname = os.path.splitext(fname)[0]

    outzip_dir = tmp_path

    try:
        with zipfile.ZipFile(input_zfile) as zfile:
            infiles = zfile.namelist()
            zfile.extract(infiles[0], path=outzip_dir, pwd=None)

        # List files within pfile dir
        pfiledir = os.path.join(outzip_dir, fname)
        gfile = [f for f in listdir(pfiledir) if isfile(join(pfiledir, f))]

        # Get path to the gz file
        gzfile = os.path.join(outzip_dir, fname, gfile[0])

        # Get base name of the pfile that will be extracted
        gfname = os.path.splitext(gfile[0])[0]

        # Extract the pfile in  outzip_dir
        with gzip.open(gzfile, "rb") as f_in:
            with open(os.path.join(outzip_dir, fname, gfname), "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

    except (IOError, zipfile.BadZipfile) as exception:
        log.error("Unable to open ZIP file: %s" % (repr(exception)))
        sys.exit(1)

    return os.path.join(outzip_dir, fname, gfname)


def process(file_path: AnyPath) -> t.Tuple[t.Dict, MetaData, t.Dict]:
    """Process `file_path` and returns a `FileEntry` and its corresponding meta.

    Args:
        file_path (Path-like): Path to input-file.

    Returns:
        dict: Dictionary of file attributes to update.
        dict: Dictionary containing the file meta.
        dict: Dictionary containing the qc metrics.

    """
    pfile_header = {}
    meta = MetaData()

    if file_path:
        with tempfile.TemporaryDirectory() as tmp_path:
            pfile_path = pfile_extract_files(file_path, tmp_path)
            p_file = PFile(pfile_path)
            meta = p_file.get_meta()
            # Populate header by getting values of iterated header keys.
            for key, val in p_file.items():
                if isinstance(val, bytes):
                    val = decode(val)
                pfile_header[key] = val

    fe = {"info": {"header": {"pfile": pfile_header}}}
    qc = {}
    return fe, meta, qc
