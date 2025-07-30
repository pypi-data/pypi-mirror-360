import numpy as np

from libcasm.composition import make_standard_origin_and_end_members


def is_column_permutation(A, B):
    if A.shape != B.shape:
        return False

    found = set()
    for i in range(A.shape[1]):
        for j in range(B.shape[1]):
            if np.allclose(A[:, i], A[:, j]):
                found.add(j)
                break

    return len(found) == A.shape[1]


def test_make_standard_origin_and_end_members_1():
    allowed_occs = [["A", "B"]]
    components = ["A", "B"]

    standard_origin_and_end_members = make_standard_origin_and_end_members(
        components, allowed_occs
    )
    print(standard_origin_and_end_members)

    expected = [
        np.array([[1.0, 0.0], [0.0, 1.0]]).transpose(),
        np.array([[0.0, 1.0], [1.0, 0.0]]).transpose(),
    ]

    found = set()
    for i, A in enumerate(standard_origin_and_end_members):
        for j, B in enumerate(expected):
            if np.allclose(A[:, 0], B[:, 0]) and is_column_permutation(A, B):
                found.add(j)
                break

    assert len(found) == len(expected)


def test_make_standard_origin_and_end_members_2():
    allowed_occs = [["A", "B"], ["B", "A"]]
    components = ["A", "B"]

    standard_origin_and_end_members = make_standard_origin_and_end_members(
        components, allowed_occs
    )
    print(standard_origin_and_end_members)

    expected = [
        np.array([[2.0, 0.0], [0.0, 2.0]]).transpose(),
        np.array([[0.0, 2.0], [2.0, 0.0]]).transpose(),
    ]

    found = set()
    for i, A in enumerate(standard_origin_and_end_members):
        for j, B in enumerate(expected):
            if np.allclose(A[:, 0], B[:, 0]) and is_column_permutation(A, B):
                found.add(j)
                break

    assert len(found) == len(expected)


def test_make_standard_origin_and_end_members_3():
    allowed_occs = [["A", "B"], ["B", "C"], ["C", "D"]]
    components = ["A", "B", "C", "D"]

    standard_origin_and_end_members = make_standard_origin_and_end_members(
        components, allowed_occs
    )
    print(standard_origin_and_end_members)

    expected = [
        np.array(
            [
                [0, 1, 0, 0],
                [2, 1, 2, 1],
                [1, 1, 0, 2],
                [0, 0, 1, 0],
            ]
        ),
        np.array(
            [
                [1, 1, 0, 1],
                [1, 1, 2, 0],
                [1, 0, 1, 2],
                [0, 1, 0, 0],
            ]
        ),
        np.array(
            [
                [1, 1, 1, 0],
                [0, 0, 1, 1],
                [2, 1, 1, 2],
                [0, 1, 0, 0],
            ]
        ),
        np.array(
            [
                [1, 1, 1, 0],
                [1, 0, 1, 2],
                [0, 1, 1, 0],
                [1, 1, 0, 1],
            ]
        ),
        np.array(
            [
                [0, 0, 0, 1],
                [1, 1, 2, 0],
                [2, 1, 1, 2],
                [0, 1, 0, 0],
            ]
        ),
        np.array(
            [
                [0, 0, 1, 0],
                [2, 1, 1, 2],
                [0, 1, 0, 1],
                [1, 1, 1, 0],
            ]
        ),
        np.array(
            [
                [0, 1, 0, 0],
                [1, 0, 2, 1],
                [1, 1, 0, 2],
                [1, 1, 1, 0],
            ]
        ),
        np.array(
            [
                [1, 0, 1, 1],
                [0, 1, 1, 0],
                [1, 1, 0, 2],
                [1, 1, 1, 0],
            ]
        ),
    ]

    found = set()
    for i, A in enumerate(standard_origin_and_end_members):
        for j, B in enumerate(expected):
            if np.allclose(A[:, 0], B[:, 0]) and is_column_permutation(A, B):
                found.add(j)
                break

    assert len(found) == len(expected)
