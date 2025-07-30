import numpy as np

import libcasm.clexulator as clex


def test_SparseCoefficients_1():
    index = [0, 2]
    value = [1.1, -0.3]

    coeff = clex.SparseCoefficients(
        index=index,
        value=value,
    )

    assert isinstance(coeff, clex.SparseCoefficients)
    assert coeff.index == index
    assert np.allclose(value, value)


def test_SparseCoefficients_mul():
    index = [0, 2]
    value = [1.1, -0.3]

    coeff = clex.SparseCoefficients(
        index=index,
        value=value,
    )
    assert isinstance(coeff, clex.SparseCoefficients)

    corr = np.array([0.1, 0.1, 0.1, 0.1])
    assert np.isclose(coeff * corr, 0.08)

    corr = np.array([0.0, 0.1, 0.1, 0.1])
    assert np.isclose(coeff * corr, -0.03)


def test_SparseCoefficients_tofrom_data_1():
    """Read CASM v2 format"""
    index = [0, 2]
    value = [1.1, -0.3]

    data = [
        [index[0], value[0]],
        [index[1], value[1]],
    ]

    coeff = clex.SparseCoefficients.from_data(data)

    assert isinstance(coeff, clex.SparseCoefficients)
    assert coeff.index == index
    assert np.allclose(value, value)

    _data = coeff.to_data()
    assert np.allclose(_data[0], data[0])
    assert np.allclose(_data[1], data[1])


def test_SparseCoefficients_tofrom_data_2():
    """Read CASM v1 format"""
    index = [0, 2]
    value = [1.1, -0.3]

    data = {
        "orbits": [
            {
                "cluster_functions": [
                    {
                        "linear_function_index": 0,
                        "eci": 1.1,
                    }
                ]
            },
            {
                "cluster_functions": [
                    {
                        "linear_function_index": 1,
                    }
                ]
            },
            {
                "cluster_functions": [
                    {
                        "linear_function_index": 2,
                        "eci": -0.3,
                    }
                ]
            },
        ]
    }

    coeff = clex.SparseCoefficients.from_data(data)

    assert isinstance(coeff, clex.SparseCoefficients)
    assert coeff.index == index
    assert np.allclose(value, value)

    _data = coeff.to_data()
    assert np.allclose(_data[0], [index[0], value[0]])
    assert np.allclose(_data[1], [index[1], value[1]])
