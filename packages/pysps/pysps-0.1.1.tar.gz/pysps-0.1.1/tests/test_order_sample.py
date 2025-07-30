import numpy as np
from pysps import OrderSample, InclusionProb, PoissonSample


def test_no_sample():
    samp = OrderSample(InclusionProb([1, 2, 3], 0))

    assert samp.units.size == 0
    assert samp.take_all.size == 0
    assert samp.take_some.size == 0
    assert samp.weights.size == 0

    samp = PoissonSample(InclusionProb([1, 2, 3], 0))

    assert samp.units.size == 0
    assert samp.take_all.size == 0
    assert samp.take_some.size == 0
    assert samp.weights.size == 0


def test_ta_units():
    samp = OrderSample(InclusionProb([4, 1, 3, 10, 4], 3))

    assert samp.units[samp.take_all] == np.array([3])
    assert samp.weights[samp.take_all] == np.array([1])
    assert np.all(samp.weights[samp.take_some] > 1)

    samp = PoissonSample(InclusionProb([4, 1, 3, 10, 4], 3))

    assert samp.units[samp.take_all] == np.array([3])
    assert samp.weights[samp.take_all] == np.array([1])
    assert np.all(samp.weights[samp.take_some] > 1)


def test_prn():
    prn = [0.1, 0.2, 0.3, 0.5]
    x = [1, 2, 3, 4]

    samp1 = OrderSample(InclusionProb(x, 2), prn=prn)
    samp2 = OrderSample(InclusionProb(x, 2), prn=prn)

    assert np.all(samp1.units == samp2.units)

    samp1 = PoissonSample(InclusionProb(x, 2), prn=prn)
    samp2 = PoissonSample(InclusionProb(x, 2), prn=prn)

    assert np.all(samp1.units == samp2.units)


def test_ties():
    x = [4, 1, 3, 2, 4]
    pi = InclusionProb(x, 3)
    samp = OrderSample(pi, pi.values)

    assert np.all(samp.units == np.arange(3))


def test_all_ta():
    x = [0, 3, 2, 1]
    pi = InclusionProb(x, 3)
    samp = OrderSample(pi)

    assert np.all(samp.take_all == [0, 1, 2])
    assert np.all(samp.units == samp.take_all + 1)
    assert np.all(samp.weights == 1)
    assert samp.take_some.size == 0

    samp = PoissonSample(pi)

    assert np.all(samp.take_all == [0, 1, 2])
    assert np.all(samp.units == samp.take_all + 1)
    assert np.all(samp.weights == 1)
    assert samp.take_some.size == 0


def test_sample_size():
    x = [1, 2, 3, 4, 5]
    pi = InclusionProb(x, 3)
    assert len(OrderSample(pi)) == 3


def test_sort_method():
    x = [1, 2, 3, 4, 5, 6]
    prn = [0.1, 0.3, 0.2, 0.6, 0.7, 0.5]

    samp1 = OrderSample(InclusionProb(x, 3))
    samp2 = OrderSample(InclusionProb(x, 3), sort_method="stable")

    np.all(samp1.units == samp2.units)