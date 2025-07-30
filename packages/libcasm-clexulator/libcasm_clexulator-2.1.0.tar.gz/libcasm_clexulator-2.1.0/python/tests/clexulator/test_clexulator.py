import numpy as np
import pytest

from libcasm.clexulator import (
    Clexulator,
    LocalClexulator,
    PrimNeighborList,
    make_clexulator,
    make_local_clexulator,
)

from .functions import make_source


def test_constructor():
    clexulator = Clexulator()
    assert isinstance(clexulator, Clexulator)


@pytest.mark.slow
@pytest.mark.very_slow
def test_make_clexulator_1(session_shared_datadir):
    source = make_source(
        session_shared_datadir,
        "OccClexulatorZrOTest",
        "OccClexulatorZrOTest",
        "default",
    )

    prim_neighbor_list = PrimNeighborList()
    clexulator = make_clexulator(source, prim_neighbor_list)
    assert isinstance(clexulator, Clexulator)
    assert clexulator.n_functions() == 74
    assert clexulator.n_point_corr() == 2
    assert clexulator.n_sublattices() == 4
    assert clexulator.nlist_size() == 225
    assert clexulator.sublat_indices() == set([2, 3])
    assert (
        clexulator.weight_matrix()
        == np.array(
            [
                [2, -1, 0],
                [-1, 2, 0],
                [0, 0, 5],
            ],
            dtype="int",
        )
    ).all()


@pytest.mark.slow
@pytest.mark.very_slow
def test_make_local_clexulator(session_shared_datadir):
    source = make_source(
        session_shared_datadir, "LocalOccClexulatorZrOTest", "ZrO", "hop0"
    )

    prim_neighbor_list = PrimNeighborList()
    hop0_clexulator = make_local_clexulator(source, prim_neighbor_list)
    assert isinstance(hop0_clexulator, LocalClexulator)
    assert hop0_clexulator.n_equivalents() == 2
    assert hop0_clexulator.n_functions() == 6


@pytest.mark.slow
@pytest.mark.very_slow
def test_make_periodic_and_local_clexulator(session_shared_datadir):
    prim_neighbor_list = PrimNeighborList()

    source = make_source(
        session_shared_datadir,
        "OccClexulatorZrOTest",
        "OccClexulatorZrOTest",
        "default",
    )
    clexulator = make_clexulator(source, prim_neighbor_list)
    assert isinstance(clexulator, Clexulator)
    assert clexulator.n_functions() == 74

    source = make_source(
        session_shared_datadir, "LocalOccClexulatorZrOTest", "ZrO", "hop0"
    )
    hop0_clexulator = make_local_clexulator(source, prim_neighbor_list)
    assert isinstance(hop0_clexulator, LocalClexulator)
    assert hop0_clexulator.n_equivalents() == 2
    assert hop0_clexulator.n_functions() == 6

    source = make_source(
        session_shared_datadir, "LocalOccClexulatorZrOTest", "ZrO", "hop1"
    )
    hop1_clexulator = make_local_clexulator(source, prim_neighbor_list)
    assert isinstance(hop1_clexulator, LocalClexulator)
    assert hop1_clexulator.n_equivalents() == 6
    assert hop1_clexulator.n_functions() == 8
