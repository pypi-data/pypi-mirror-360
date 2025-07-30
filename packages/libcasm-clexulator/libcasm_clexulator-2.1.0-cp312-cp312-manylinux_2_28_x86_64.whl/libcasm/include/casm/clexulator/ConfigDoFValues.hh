#ifndef CASM_clexulator_ConfigDoFValues
#define CASM_clexulator_ConfigDoFValues
#include <map>
#include <string>

#include "casm/global/eigen.hh"

namespace CASM {
namespace clexulator {

/// \brief Data structure holding configuration DoF values
///
/// Notes:
/// - Site DoF values are organized in blocks by sublattice, and ordered within
///   a sublattice block by unit cell index
/// - For use by Clexulator, DoF values should be expressed in terms of the
///   `prim basis`.
/// - For input / output, conversion to structure, etc. the DoF values should be
///   expressed in terms of the `standard basis`.
/// - See `ConfigDoF` for full documentation on layout.
///
/// Conversion between (single) `occupation` and `multi_occupation`:
/// - If using multi_occupation, the single occupation occupant indcies *must*
///   be determined from the multi occupation index definitions in order for
///   the `update_single_occupation` and update_multi_occupation` functions
///   to work correctly.
///
/// Example, for a particular sublattice b:
/// - dof_type=0: chemical dof: "A", "B", "C" -> 0, 1, 2
/// - dof_type=1: magspin dof: -1, +1 -> 0, 1
/// - dof_type=2: orientation dof: x, y, z -> 0, 1, 2
/// - discrete_dof_dim[b] = {3, 2, 3}
///
/// (single) occupation:
/// - [ ... single occupation indices in {0, 1, 2, ..., 17, 18} ... ];
///
/// multi_occupation:
/// - [[ ... chemical dof occupation indices in {0, 1, 2} ...    ],
///    [ ... magspin dof occupation indices in {0, 1} ...        ],
///    [ ... orientation dof occupation indices in {0, 1, 2} ... ]];
///
/// occupation_shape_factors: [6, 3, 1]
/// multi occupation indices (column l in ConfigDoFValues::multi_occupation) =
///    [chemical_occ_index, magspin_occ_index, orientation_occ_index]
/// single occupation index (element l in ConfigDoFValues::occupation) =
///    6*chemical_occ_index + 3*magspin_occ_index + 1*orientation_occ_index
///
struct ConfigDoFValues {
  /// \brief Occupation values (shape=(N_sites,1))
  Eigen::VectorXi occupation;

  /// \brief Occupation values, by dof type (shape=(N_discrete_dof, N_sites))
  Eigen::MatrixXi multi_occupation;

  /// \brief Local continuous DoF values
  ///
  /// For use by clexulator, expected shape is (max(DoFSet::dim()), N_sites)
  /// - The number of rows is the maximum of the individual sublattice DoFSet
  /// dimensions.
  ///
  /// For the standard basis, the expected shape is (standard_dim, N_sites)
  std::map<std::string, Eigen::MatrixXd> local_dof_values;

  /// \brief Global continuous DoF values
  ///
  /// For use by clexulator, expected shape is (DoFSet::dim(), 1)
  ///
  /// For the standard basis, the expected shape is (standard_dim, 1)
  std::map<std::string, Eigen::VectorXd> global_dof_values;
};

}  // namespace clexulator
}  // namespace CASM

#endif
