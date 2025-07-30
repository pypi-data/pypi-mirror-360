from typing import Optional, Tuple, Union

import numpy as np

import libcasm.clexulator._clexulator as _clex
import libcasm.xtal as xtal


class ClusterExpansionInfo:
    """ClusterExpansion related data"""

    def __init__(
        self,
        prim_neighbor_list: _clex.PrimNeighborList,
        supercell_neighbor_list: _clex.SuperNeighborList,
        clexulator: Union[_clex.Clexulator, _clex.LocalClexulator],
        config_dof_values: _clex.ConfigDoFValues,
    ):
        """Constructor

        Parameters
        ----------
        prim_neighbor_list: :class:`~libcasm.clexulator.PrimNeighborList`
            The :class:`~libcasm.clexulator.PrimNeighborList` used to order unit cells
            in the neighbor list.
        supercell_neighbor_list: :class:`~libcasm.clexulator.SuperNeighborList`
            The :class:`~libcasm.clexulator.SuperNeighborList` used to find neighbors
            in a particular supercell when evaluating cluster basis functions.
        clexulator: :class:`~libcasm.clexulator.Clexulator`
            The :class:`~libcasm.clexulator.Clexulator` used to evaluate cluster basis
            functions.
        config_dof_values: :class:`~libcasm.clexulator.ConfigDoFValues`
            The :class:`~libcasm.clexulator.ConfigDoFValues` that the cluster expansion
            will evaluate.
        """

        self.prim_neighbor_list = prim_neighbor_list
        """:class:`~libcasm.clexulator.PrimNeighborList`: The 
        :class:`~libcasm.clexulator.PrimNeighborList` used to order unit cells in the 
        neighbor list.
        """

        self.supercell_neighbor_list = supercell_neighbor_list
        """:class:`~libcasm.clexulator.SuperNeighborList`: The 
        :class:`~libcasm.clexulator.SuperNeighborList` used to find neighbors in a 
        particular supercell when evaluating cluster basis functions.
        """

        self.clexulator = clexulator
        """Union[:class:`~libcasm.clexulator.Clexulator`, 
        :class:`~libcasm.clexulator.LocalClexulator`]: The 
        :class:`~libcasm.clexulator.Clexulator` or 
        :class:`~libcasm.clexulator.LocalClexulator` used to evaluate cluster basis 
        functions.
        """

        self.config_dof_values = config_dof_values
        """:class:`~libcasm.clexulator.ConfigDoFValues`: The 
        :class:`~libcasm.clexulator.ConfigDoFValues` that the cluster expansion will 
        evaluate.
        """


def make_cluster_expansion(
    coefficients: Union[_clex.SparseCoefficients, list[_clex.SparseCoefficients]],
    supercell_neighbor_list: Optional[_clex.SuperNeighborList] = None,
    clexulator: Union[_clex.Clexulator, _clex.LocalClexulator] = None,
    config_dof_values: Optional[_clex.ConfigDoFValues] = None,
    prim_neighbor_list: Optional[_clex.PrimNeighborList] = None,
    transformation_matrix_to_super: Optional[np.ndarray] = None,
    xtal_prim: Optional[xtal.Prim] = None,
    cluster_expansion_type: Optional[str] = "periodic",
    clexulator_source: Optional[str] = None,
    compile_options: Optional[str] = None,
    so_options: Optional[str] = None,
) -> Tuple[_clex.ClusterExpansion, ClusterExpansionInfo]:
    """Factory function for constructing cluster expansion calculators

    .. rubric:: Basic usage, evaluating a periodic cluster expansion

    For basic usage, it is convenient to let
    :func:`~libcasm.clexulator.make_cluster_expansion` construct the clexulator and
    neighbor lists used by the cluster expansion, and the
    :class:`~libcasm.clexulator.ConfigDoFValues` instance which is evaluated by the
    cluster expansion. For example:

    .. code-block:: Python

        # construct a ClusterExpansion calculator
        cluster_expansion, info = make_cluster_expansion(
            xtal_prim=xtal_prim, # libcasm.xtal.Prim
            clexulator_source=clexulator_source, # str, path to clexulator source code
            coefficients=coefficients, # libcasm.clexulator.SparseCoefficients
            transformation_matrix_to_super=transformation_matrix_to_super, # np.ndarray
        )

    For more details, see the section
    :ref:`Evaluating a cluster expansion <cluster-expansion-index>`

    In this case, the method returns the tuple `(cluster_expansion, info)`, where
    `cluster_expansion` is a periodic cluster expansion calculator of type
    :class:`~libcasm.clexulator.ClusterExpansion`, and `info` is an instance of
    :class:`~libcasm.clexulator.ClusterExpansionInfo`, that can be used to access the
    neighbor lists and :class:`~libcasm.clexulator.ConfigDoFValues` instance that were
    generated.

    .. rubric:: Evaluating local cluster expansions

    To evaluate local cluster expansions with a `cluster_expansion` of type
    :class:`~libcasm.clexulator.LocalClusterExpansion`, the `cluster_expansion_type`
    should be set to `"local"`.

    .. rubric:: Evaluating multiple cluster expansions using the same basis set

    When multiple periodic or local cluster expansions use the same basis set with
    different expansion coefficients, the calculator types
    :class:`~libcasm.clexulator.MultiClusterExpansion` and
    :class:`~libcasm.clexulator.MultiLocalClusterExpansion` can be used to simplify
    evaluating them all with a single evaluation of the basis functions. These can be
    constructed by setting `cluster_expansion_type` to `"multi_periodic"` or
    `"multi_local"`, respectively, and using `cofficients` to provide a list of
    :class:`~libcasm.clexulator.SparseCoefficients` instead of a single instance.

    .. rubric:: Evaluating multiple cluster expansions in the same supercell

    If multiple periodic or local cluster expansions will be used in the same
    supercell, it is necessary to set them all to evaluate the same
    :class:`~libcasm.clexulator.ConfigDoFValues` instance and preferrable to re-use
    neighbor lists. For this use case, the data from the output `info` can be used as
    input parameters to construct additional periodic or local cluster expansions in
    repeated uses of :func:`~libcasm.clexulator.make_cluster_expansion`. For example:

    .. code-block:: Python

        formation_energy_cluster_expansion, info = make_cluster_expansion(
            coefficients=formation_energy_coefficients,
            clexulator_source=formation_energy_clexulator_source,
            xtal_prim=xtal_prim,
            transformation_matrix_to_super=transformation_matrix_to_super,
        )
        prim_neighbor_list=info.prim_neighbor_list
        supercell_neighbor_list=info.supercell_neighbor_list
        config_dof_values = info.config_dof_values
        hop_1_cluster_expansion, _ = make_cluster_expansion(
            coefficients=[hop_1_kra_coefficients, hop_1_freq_coefficients],
            clexulator_sourcesource=hop_1_clexulator_source,
            prim_neighbor_list=prim_neighbor_list,
            supercell_neighbor_list=supercell_neighbor_list,
            config_dof_values=config_dof_values,
            cluster_expansion_type="multi_local",
        )


    Parameters
    ----------
    coefficients: Union[:class:`~libcasm.clexulator.SparseCoefficients`, \
    list[:class:`~libcasm.clexulator.SparseCoefficients`]]
        Cluster expansion coefficients to use. May be a single
        :class:`~libcasm.clexulator.SparseCoefficients` instance for evaluating a
        single cluster expansion (`cluster_expansion_type` equal to `"periodic"` or
        `"local"`), or a list of :class:`~libcasm.clexulator.SparseCoefficients`
        instances for constructing multiple cluster expansions that use the same
        cluster basis fucntions (`cluster_expansion_type` equal to `"multi_periodic"`
        or `"multi_local"`).
    supercell_neighbor_list: \
        Optional[:class:`~libcasm.clexulator.SuperNeighborList`]=None
        The SuperNeighborList to use. If None, a new instance will be constructed with
        the `transformation_matrix_to_super` parameter.
    clexulator: Union[:class:`~libcasm.clexulator.Clexulator`, \
        :class:`~libcasm.clexulator.LocalClexulator`]=None
        The :class:`~libcasm.clexulator.Clexulator` used to evaluate basis functions.
        If None, a new instance will be constructed using the `prim_neighbor_list`,
        `clexulator_source`, `compile_options`, and `so_options` parameters.
    config_dof_values: Optional[:class:`~libcasm.clexulator.ConfigDoFValues`]=None
        The :class:`~libcasm.clexulator.ConfigDoFValues` to be evaluated. If None, a
        new instance will be constructed with the `xtal_prim` parameter.
    prim_neighbor_list: Optional[:class:`~libcasm.clexulator.PrimNeighborList`]=None
        The PrimNeighborList to use if necessary to construct `supercell_neighbor_list`
        or `clexulator`. If None, a new instance will be constructed.
    transformation_matrix_to_super: Optional[np.ndarray]=None
        The supercell definining transformation matrix to use if necessary to construct
        `supercell_neighbor_list`.
    xtal_prim: Optional[:class:`~libcasm.xtal.Prim`]=None
        The :class:`~libcasm.xtal.Prim`, defining the crystal structure and allowed
        degrees of freedom (DoF), used if necessary to construct `config_dof_values`.
    cluster_expansion_type: Optional[str] = "periodic"
        Specify the type of cluster expansion calculator to construct. One of the
        following:

        - `"periodic"`: Construct a :class:`~libcasm.clexulator.ClusterExpansion`
        - `"local"`: Construct a :class:`~libcasm.clexulator.LocalClusterExpansion`
        - `"multi_periodic"`: Construct a
          :class:`~libcasm.clexulator.MultiClusterExpansion`
        - `"multi_local"`: Construct a
          :class:`~libcasm.clexulator.MultiLocalClusterExpansion`

    clexulator_source: Optional[str]=None
        The location of the clexulator source code file, used if necessary to construct
        `clexulator`. For local cluster expansions, this is the location of the
        prototype source code file.
    compile_options: Optional[str] = None
        An optional parameter, forwarded to :func:`~libcasm.clexulator.make_clexulator`
        or :func:`~libcasm.clexulator.make_local_clexulator`, that is used if necessary
        to construct `clexulator`.
    so_options: Optional[str] = None
        An optional parameter, forwarded to :func:`~libcasm.clexulator.make_clexulator`
        or :func:`~libcasm.clexulator.make_local_clexulator`, that is used if necessary
        to construct `clexulator`.

    Returns
    -------
    (cluster_expansion, info): Tuple

        cluster_expansion:
            The constructed cluster expansion calculator, of type specified by the
            `cluster_expansion_type` parameter.

        info: :class:`~libcasm.clexulator.ClusterExpansionInfo`
            Contains the `prim_neighbor_list`, `supercell_neighbor_list`, `clexulator`,
            and `config_dof_values` used to construct `cluster_expansion`.
    """
    if supercell_neighbor_list is None:
        if prim_neighbor_list is None:
            if xtal_prim is None:
                raise Exception(
                    "Error in make_cluster_expansion: xtal_prim is None and "
                    "prim_neighbor_list is None"
                )
            prim_neighbor_list = _clex.make_default_prim_neighbor_list(xtal_prim)
        if transformation_matrix_to_super is None:
            raise Exception(
                "Error in make_cluster_expansion: supercell_neighbor_list is None and "
                "transformation_matrix_to_super is None"
            )
        supercell_neighbor_list = _clex.SuperNeighborList(
            transformation_matrix_to_super, prim_neighbor_list
        )
    if clexulator is None:
        if prim_neighbor_list is None:
            if xtal_prim is None:
                raise Exception(
                    "Error in make_cluster_expansion: xtal_prim is None and "
                    "prim_neighbor_list is None"
                )
            prim_neighbor_list = _clex.make_default_prim_neighbor_list(xtal_prim)
        if cluster_expansion_type in ["periodic", "multi_periodic"]:
            clexulator = _clex.make_clexulator(
                source=clexulator_source,
                prim_neighbor_list=prim_neighbor_list,
                compile_options=compile_options,
                so_options=so_options,
            )
        elif cluster_expansion_type in ["periodic", "multi_periodic"]:
            clexulator = _clex.make_local_clexulator(
                source=clexulator_source,
                prim_neighbor_list=prim_neighbor_list,
                compile_options=compile_options,
                so_options=so_options,
            )
        else:
            raise Exception(
                "Error in make_cluster_expansion: cluster_expansion_type not recognized"
            )
    if config_dof_values is None:
        if xtal_prim is None:
            raise Exception(
                "Error in make_cluster_expansion: config_dof_values is None and "
                "xtal_prim is None"
            )
        config_dof_values = _clex.make_default_config_dof_values(
            xtal_prim=xtal_prim, n_unitcells=supercell_neighbor_list.n_unitcells()
        )
    if cluster_expansion_type == "periodic":
        cluster_expansion = _clex.ClusterExpansion(
            supercell_neighbor_list=supercell_neighbor_list,
            clexulator=clexulator,
            coefficients=coefficients,
            config_dof_values=config_dof_values,
        )
    elif cluster_expansion_type == "local":
        cluster_expansion = _clex.LocalClusterExpansion(
            supercell_neighbor_list=supercell_neighbor_list,
            clexulator=clexulator,
            coefficients=coefficients,
            config_dof_values=config_dof_values,
        )
    elif cluster_expansion_type == "multi_periodic":
        cluster_expansion = _clex.MultiClusterExpansion(
            supercell_neighbor_list=supercell_neighbor_list,
            clexulator=clexulator,
            coefficients=coefficients,
            config_dof_values=config_dof_values,
        )
    elif cluster_expansion_type == "multi_local":
        cluster_expansion = _clex.MultiLocalClusterExpansion(
            supercell_neighbor_list=supercell_neighbor_list,
            clexulator=clexulator,
            coefficients=coefficients,
            config_dof_values=config_dof_values,
        )
    else:
        raise Exception(
            "Error in make_cluster_expansion: cluster_expansion_type not recognized"
        )
    info = ClusterExpansionInfo(
        prim_neighbor_list=prim_neighbor_list,
        supercell_neighbor_list=supercell_neighbor_list,
        clexulator=clexulator,
        config_dof_values=config_dof_values,
    )
    return (cluster_expansion, info)
