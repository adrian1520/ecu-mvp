import numpy as np

def is_axis(seq):
    diffs = np.diff(seq)
    return np.all(diffs >= 0)

def evaluate_matrix(matrix):
    std = np.std(matrix)
    if std == 0:
        return 0
    return min(std / 1000, 1)

def detect_16x16_maps(arr):
    candidates = []
    length = len(arr)
    stride = 16 + 16 + 256

    for i in range(0, length - stride, 2):
        axis_x = arr[i:i+16]
        axis_y = arr[i+16:i+32]
        matrix = arr[i+32:i+32+256]

        if is_axis(axis_x) and is_axis(axis_y):
            score = evaluate_matrix(matrix)
            if score > 0.5:
                candidates.append({
                    "offset": i*2,
                    "size_x": 16,
                    "size_y": 16,
                    "confidence": float(score)
                })
    return candidates