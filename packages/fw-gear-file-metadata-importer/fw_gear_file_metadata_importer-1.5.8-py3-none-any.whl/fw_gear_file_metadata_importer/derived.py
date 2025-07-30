"""derived module to host source for derived metadata."""

import typing as t


def compute_scan_coverage(z_array: t.List[float]) -> t.Tuple[float, float, float]:
    """Computes ScanCoverage and Min/Max of Slice location.

    Args:
        z_array (list): An array of slice locations.

    Returns:
        tuple: A tuple containing the scan coverage, max slice location, and min slice
            location.
    """
    max_slice_location = max(z_array)
    min_slice_location = min(z_array)
    scan_coverage = abs(max_slice_location - min_slice_location)
    return scan_coverage, max_slice_location, min_slice_location
