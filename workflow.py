import numpy as np
from segmenter import find_calibration_region
from detector import detect_16x16_maps

def run_workflow(file_bytes: bytes):
    start, end = find_calibration_region(file_bytes)
    calib = file_bytes[start:end]
    arr = np.frombuffer(calib, dtype='<i2')

    maps = detect_16x16_maps(arr)

    return {
        "calibration_start": start,
        "calibration_size": end-start,
        "map_candidates": maps
    }