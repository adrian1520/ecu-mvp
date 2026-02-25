import numpy as np


def is_axis(seq: np.ndarray) -> bool:
    """
    Sprawdza czy sekwencja może być osią:
    - dokładnie 16 elementów
    - wartości niemalejące
    - nie wszystkie wartości identyczne
    """
    if len(seq) != 16:
        return False

    # oś nie może być stała
    if np.all(seq == seq[0]):
        return False

    diffs = np.diff(seq)

    return np.all(diffs >= 0)


def evaluate_matrix(matrix: np.ndarray) -> float:
    """
    Prosty scoring:
    - odrzuca macierze stałe
    - normalizuje odchylenie standardowe
    """
    if len(matrix) != 256:
        return 0.0

    # macierz nie może być stała
    if np.all(matrix == matrix[0]):
        return 0.0

    std = np.std(matrix)

    score = std / 1000.0

    # ograniczenie do zakresu 0–1
    if score < 0:
        return 0.0
    if score > 1:
        return 1.0

    return float(score)


def detect_16x16_maps(arr: np.ndarray):
    """
    Wyszukiwanie struktur:
    [16 axis_x]
    [16 axis_y]
    [256 matrix]
    """
    candidates = []

    stride = 16 + 16 + 256
    length = len(arr)

    # zabezpieczenie przed zbyt krótkim wsadem
    if length < stride:
        return candidates

    for i in range(0, length - stride):
        axis_x = arr[i : i + 16]
        axis_y = arr[i + 16 : i + 32]
        matrix = arr[i + 32 : i + 288]

        if is_axis(axis_x) and is_axis(axis_y):
            score = evaluate_matrix(matrix)

            if score > 0.5:
                candidates.append(
                    {
                        "offset": int(i * 2),  # int16 → 2 bajty
                        "size_x": 16,
                        "size_y": 16,
                        "confidence": float(score),
                    }
                )

    return candidates