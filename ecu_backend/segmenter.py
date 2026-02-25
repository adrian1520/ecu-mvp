def find_calibration_region(data: bytes):
    start = next(i for i, b in enumerate(data) if b != 0xFF)
    end = len(data) - next(i for i, b in enumerate(reversed(data)) if b != 0xFF)
    return start, end
