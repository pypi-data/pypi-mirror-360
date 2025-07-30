import numpy as np
from pysps import InclusionProb, becomes_ta


def test_no_sample():
    pi = InclusionProb([0], 0)

    assert pi.n == 0
    assert pi.take_all.size == 0
    assert pi.take_some.size == 0
    assert pi.values == np.array([0.0])

    x = [1, 2, 3]
    pi = InclusionProb(x, 0)
    
    assert pi.n == 0
    assert pi.take_all.size == 0
    assert np.all(pi.take_some == np.array([0, 1, 2], dtype=np.int64))
    assert np.all(pi.values == np.array([0.0, 0.0, 0.0]))


def test_sums_to_n():
    x = [1, 2, 3, 4, 5]

    pi = InclusionProb(x, 1)
    assert np.isclose(pi.values.sum(), pi.n)

    pi = InclusionProb(x, 3)
    assert np.isclose(pi.values.sum(), pi.n)

    pi = InclusionProb(x, 5)
    assert np.isclose(pi.values.sum(), pi.n)


def test_fixed_point():
    x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    pi = InclusionProb(x, 5)
    assert np.allclose(pi.values, InclusionProb(pi.values, pi.n).values)

    x = [0, 4, 1, 4, 5]
    pi = InclusionProb(x, 3, alpha=0.15)
    assert np.allclose(pi.values, InclusionProb(pi.values, pi.n).values)


def test_with_sampling():
    pi = InclusionProb(np.arange(21), 12)

    assert np.allclose(
        pi.values,
        np.concatenate([np.arange(17) / 136 * 8, [1, 1, 1, 1]])
    )
    assert np.all(pi.take_all == [17, 18, 19, 20])
    assert np.all(pi.take_some == np.arange(1, 17))

    x = np.array([100, 25, 94, 23, 55, 6, 80, 65, 48, 76,
                  31, 99, 45, 39, 28, 18, 54, 78, 4, 33])
    
    pi = InclusionProb(x, 10)
    assert np.allclose(
        pi.values,
        np.concatenate([[1], x[1:] / np.sum(x[1:]) * 9])
    )

    pi = InclusionProb(x, 10, alpha=0)
    assert np.isclose(pi.values, x / np.sum(x) * 10).all()


def test_increasing_alpha():
    x = np.array([0, 4, 1, 4, 5])

    pi = InclusionProb(x, 3, alpha=0.1)
    assert np.allclose(pi.values, np.concatenate([x[:4]/ 9 * 2, [1]]))

    pi = InclusionProb(x, 3, alpha=0.15)
    assert np.allclose(pi.values, np.concatenate([[0], [1], x[2:4] / 5, [1]]))

    pi = InclusionProb(x, 3, alpha=0.2)
    assert np.allclose(pi.values, np.array([0, 1, 0, 1, 1]))


def test_cutoff():
    x = np.arange(1, 21)
    pi1 = InclusionProb(x[x < 18], 9)
    pi2 = InclusionProb(x, 12, cutoff=18)

    assert np.allclose(pi1.values[:17], pi2.values[:17])

    pi1 = InclusionProb(x[x < 18], 9, alpha=0.1)
    pi2 = InclusionProb(x, 12, cutoff=18, alpha=0.1)

    assert np.allclose(pi1.values[:17], pi2.values[:17])


def test_becomes_ta():
    x = [6, 4, 3, 4, 2, 1, 4, 2, 2, 1, 2]
    bta = becomes_ta(x, alpha=0.4, cutoff=6)
    
    assert np.all(bta[1:] == np.array([5, 7, 6, 8, 11, 6, 9, 9, 11, 10]))
    assert np.isnan(bta[0])

def test_sort_method():
    x = np.array([1, 2, 2, 4, 2, 4, 5, 5, 5])

    pi1 = InclusionProb(x, 6, alpha=0.8)
    pi2 = InclusionProb(x, 6, alpha=0.8, sort_method="partial")

    assert set(x[pi1.take_all]) == set(x[pi2.take_all])

    pi1 = InclusionProb(x, 6, alpha=0.5)
    pi2 = InclusionProb(x, 6, alpha=0.5, sort_method="partial")

    assert np.all(pi1.values == pi2.values)
