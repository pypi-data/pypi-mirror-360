#ifndef CASM_clexulator_ConfigDoFValuesTools
#define CASM_clexulator_ConfigDoFValuesTools
#include <algorithm>
#include <vector>

#include "casm/clexulator/ConfigDoFValues.hh"
#include "casm/crystallography/DoFDecl.hh"
#include "casm/global/definitions.hh"

namespace CASM {

namespace xtal {
class BasicStructure;
class DoFSet;
class SiteDoFSet;
}  // namespace xtal

namespace clexulator {

// Note: DoFSetType template parameter requires: dim(), basis(), inv_basis()

/// Returns the block of DoF values from one sublattice
template <typename Derived>
Eigen::Block<Derived> sublattice_block(Eigen::MatrixBase<Derived> &M,
                                       Index sublattice_index, Index N_volume);

/// Returns the block of DoF values from one sublattice
template <typename Derived>
const Eigen::Block<const Derived> sublattice_block(
    Eigen::MatrixBase<Derived> const &M, Index sublattice_index,
    Index N_volume);

/// \brief Determine local continuous DoF matrix row dimension
///
/// For local continuous DoF values stored in a matrix, the expected matrix
/// shape is (matrix_dim x number of sites), where matrix_dim is the maximum
/// of the individual sublattice DoFSet dimensions.
///
/// \param dof_info Vector of DoFSetType, which must have a `DoFSetType::dim()`
/// member
template <typename DoFSetType>
Index max_dim(std::vector<DoFSetType> const &dof_info);

/// Convert local DoF values from prim basis to standard basis
template <typename DoFSetType>
Eigen::MatrixXd local_to_standard_values(
    Eigen::MatrixXd const &dof_values, Index N_sublat, Index N_volume,
    std::vector<DoFSetType> const &dof_info);

/// Convert local DoF values from standard basis to prim basis
template <typename DoFSetType>
Eigen::MatrixXd local_from_standard_values(
    Eigen::MatrixXd const &standard_values, Index N_sublat, Index N_volume,
    std::vector<DoFSetType> const &dof_info);

/// Convert global DoF values from prim basis to standard basis
template <typename DoFSetType>
Eigen::VectorXd global_to_standard_values(Eigen::VectorXd const &dof_values,
                                          DoFSetType const &dof_info);

/// Convert global DoF values from standard basis to prim basis
template <typename DoFSetType>
Eigen::VectorXd global_from_standard_values(
    Eigen::VectorXd const &standard_values, DoFSetType const &dof_info);

// ConfigDoFValues factory functions

std::map<DoFKey, xtal::DoFSet> make_global_dof_info(
    xtal::BasicStructure const &basic_structure);

std::map<DoFKey, std::vector<xtal::SiteDoFSet>> make_local_dof_info(
    xtal::BasicStructure const &basic_structure);

/// \brief Make ConfigDoFValues, expressed in the standard basis, initialized
/// with value zero
template <typename GlobalDoFSetType, typename LocalDoFSetType>
ConfigDoFValues make_default_standard_config_dof_values(
    Index N_sublat, Index N_volume,
    std::map<DoFKey, GlobalDoFSetType> const &global_dof_info,
    std::map<DoFKey, std::vector<LocalDoFSetType>> const &local_dof_info);

/// \brief Make ConfigDoFValues, expressed in the prim basis, initialized
/// with value zero
template <typename GlobalDoFSetType, typename LocalDoFSetType>
ConfigDoFValues make_default_config_dof_values(
    Index N_sublat, Index N_volume,
    std::map<DoFKey, GlobalDoFSetType> const &global_dof_info,
    std::map<DoFKey, std::vector<LocalDoFSetType>> const &local_dof_info);

/// Convert ConfigDoFValues expressed in prim basis to standard basis
template <typename GlobalDoFSetType, typename LocalDoFSetType>
ConfigDoFValues to_standard_values(
    ConfigDoFValues const &dof_values, Index N_sublat, Index N_volume,
    std::map<DoFKey, GlobalDoFSetType> const &global_dof_info,
    std::map<DoFKey, std::vector<LocalDoFSetType>> const &local_dof_info);

/// Convert ConfigDoFValues expressed in standard basis to prim basis
template <typename GlobalDoFSetType, typename LocalDoFSetType>
ConfigDoFValues from_standard_values(
    ConfigDoFValues const &standard_values, Index N_sublat, Index N_volume,
    std::map<DoFKey, GlobalDoFSetType> const &global_dof_info,
    std::map<DoFKey, std::vector<LocalDoFSetType>> const &local_dof_info);

/// \brief Calculate the shape factors needed for updates between
///     ConfigDoFValues::occupation and ConfigDoFValues::multi_occupation
std::vector<std::vector<int>> make_occupation_shape_factors(
    std::vector<std::vector<int>> const &discrete_dof_dim);

/// \brief Make the default ConfigDoFValues::multi_occupation matrix
void make_default_multi_occupation(
    ConfigDoFValues &dof_values, Index N_sublat, Index N_volume,
    std::vector<std::vector<int>> const &discrete_dof_dim);

/// \brief Update ConfigDoFValues::occupation to be consistent with
///     ConfigDoFValues::multi_occupation, on a single site
void update_single_occupation(ConfigDoFValues &dof_values, Index N_sublat,
                              Index N_volume,
                              std::vector<int> const &occupation_shape_factors,
                              Index linear_site_index);

/// \brief Update ConfigDoFValues::occupation to be consistent with
///     ConfigDoFValues::multi_occupation
void update_single_occupation(ConfigDoFValues &dof_values, Index N_sublat,
                              Index N_volume,
                              std::vector<int> const &occupation_shape_factors);

/// \brief Update ConfigDoFValues::multi_occupation to be consistent with
///     ConfigDoFValues::occupation, on a single site
void update_multi_occupation(ConfigDoFValues &dof_values, Index N_sublat,
                             Index N_volume,
                             std::vector<int> const &occupation_shape_factors,
                             Index linear_site_index);

/// \brief Update ConfigDoFValues::multi_occupation to be consistent with
///     ConfigDoFValues::occupation
void update_multi_occupation(ConfigDoFValues &dof_values, Index N_sublat,
                             Index N_volume,
                             std::vector<int> const &occupation_shape_factors);

// --- Inline & template definitions ---

/// Returns the block of DoF values from one sublattice
template <typename Derived>
Eigen::Block<Derived> sublattice_block(Eigen::MatrixBase<Derived> &M,
                                       Index sublattice_index, Index N_volume) {
  return Eigen::Block<Derived>(M.derived(), 0, sublattice_index * N_volume,
                               M.rows(), N_volume);
}

/// Returns the block of DoF values from one sublattice
template <typename Derived>
const Eigen::Block<Derived const> sublattice_block(
    Eigen::MatrixBase<Derived> const &M, Index sublattice_index,
    Index N_volume) {
  return Eigen::Block<Derived const>(
      M.derived(), 0, sublattice_index * N_volume, M.rows(), N_volume);
}

/// \brief Determine local continuous DoF matrix row dimension
///
/// For local continuous DoF values stored in a matrix, the expected matrix
/// shape is (matrix_dim x number of sites), where matrix_dim is the maximum
/// of the individual sublattice DoFSet dimensions.
///
/// \param dof_info Vector of DoFSetType, which must have a `DoFSetType::dim()`
/// member
template <typename DoFSetType>
Index max_dim(std::vector<DoFSetType> const &dof_info) {
  Index dim = 0;
  for (auto const &info : dof_info) {
    dim = std::max(dim, info.dim());
  }
  return dim;
}

/// Convert local DoF values from prim basis to standard basis
template <typename DoFSetType>
Eigen::MatrixXd local_to_standard_values(
    Eigen::MatrixXd const &dof_values, Index N_sublat, Index N_volume,
    std::vector<DoFSetType> const &dof_info) {
  Index N_sites = N_volume * N_sublat;
  Index rows = dof_info.front().basis().rows();
  if (dof_values.rows() != max_dim(dof_info) || dof_values.cols() != N_sites) {
    std::stringstream msg;
    msg << "Invalid dof values input size in "
           "local_to_standard_values: "
        << "Expected rows=" << max_dim(dof_info)
        << ", received rows=" << dof_values.rows()
        << ", expected cols=" << N_sites
        << ", received cols=" << dof_values.cols();
    throw std::runtime_error(msg.str());
  }
  Eigen::MatrixXd standard_values = Eigen::MatrixXd::Zero(rows, N_sites);
  for (Index b = 0; b < N_sublat; ++b) {
    if (dof_info[b].dim() == 0) {
      continue;
    }
    standard_values.block(0, b * N_volume, rows, N_volume) =
        dof_info[b].basis() *
        sublattice_block(dof_values, b, N_volume).topRows(dof_info[b].dim());
  }
  return standard_values;
}

/// Convert local DoF values from standard basis to prim basis
template <typename DoFSetType>
Eigen::MatrixXd local_from_standard_values(
    Eigen::MatrixXd const &standard_values, Index N_sublat, Index N_volume,
    std::vector<DoFSetType> const &dof_info) {
  Index N_sites = N_volume * N_sublat;
  if (standard_values.rows() != dof_info.front().basis().rows() ||
      standard_values.cols() != N_sites) {
    std::stringstream msg;
    msg << "Invalid standard values input size in "
           "local_from_standard_value: "
        << "Expected rows=" << dof_info.front().basis().rows()
        << ", received rows=" << standard_values.rows()
        << ", expected cols=" << N_sites
        << ", received cols=" << standard_values.cols();
    throw std::runtime_error(msg.str());
  }
  Eigen::MatrixXd result = Eigen::MatrixXd::Zero(max_dim(dof_info), N_sites);
  for (Index b = 0; b < N_sublat; ++b) {
    if (dof_info[b].dim() == 0) {
      continue;
    }
    sublattice_block(result, b, N_volume).topRows(dof_info[b].dim()) =
        dof_info[b].inv_basis() *
        sublattice_block(standard_values, b, N_volume);
  }
  return result;
}

/// Convert global DoF values from prim basis to standard basis
template <typename DoFSetType>
Eigen::VectorXd global_to_standard_values(Eigen::VectorXd const &dof_values,
                                          DoFSetType const &dof_info) {
  return dof_info.basis() * dof_values;
}

/// Convert global DoF values from standard basis to prim basis
template <typename DoFSetType>
Eigen::VectorXd global_from_standard_values(
    Eigen::VectorXd const &standard_values, DoFSetType const &dof_info) {
  if (standard_values.size() != dof_info.basis().rows()) {
    std::stringstream msg;
    msg << "Invalid standard values input size in "
           "global_dof_values_from_standard_basis: "
        << "Expected size=" << dof_info.basis().rows()
        << ", received size=" << standard_values.size();
    throw std::runtime_error(msg.str());
  }
  return dof_info.inv_basis() * standard_values;
}

/// \brief Make ConfigDoFValues, expressed in the standard basis, initialized
/// with value zero
template <typename GlobalDoFSetType, typename LocalDoFSetType>
ConfigDoFValues make_default_standard_config_dof_values(
    Index N_sublat, Index N_volume,
    std::map<DoFKey, GlobalDoFSetType> const &global_dof_info,
    std::map<DoFKey, std::vector<LocalDoFSetType>> const &local_dof_info) {
  Index N_sites = N_volume * N_sublat;
  ConfigDoFValues standard_values;
  standard_values.occupation = Eigen::VectorXi::Zero(N_sites);

  for (auto const &pair : local_dof_info) {
    std::string const &dof_type = pair.first;
    auto const &dof_info = pair.second;
    Index standard_dim = dof_info.front().basis().rows();
    standard_values.local_dof_values.emplace(
        dof_type, Eigen::MatrixXd::Zero(standard_dim, N_sites));
  }

  for (auto const &pair : global_dof_info) {
    std::string const &dof_type = pair.first;
    auto const &dof_info = pair.second;
    Index standard_dim = dof_info.basis().rows();
    standard_values.global_dof_values.emplace(
        dof_type, Eigen::VectorXd::Zero(standard_dim));
  }

  return standard_values;
}

/// \brief Make ConfigDoFValues, expressed in the prim basis, initialized
/// with value zero
template <typename GlobalDoFSetType, typename LocalDoFSetType>
ConfigDoFValues make_default_config_dof_values(
    Index N_sublat, Index N_volume,
    std::map<DoFKey, GlobalDoFSetType> const &global_dof_info,
    std::map<DoFKey, std::vector<LocalDoFSetType>> const &local_dof_info) {
  Index N_sites = N_volume * N_sublat;
  ConfigDoFValues dof_values;
  dof_values.occupation = Eigen::VectorXi::Zero(N_sites);

  for (auto const &pair : local_dof_info) {
    std::string const &dof_type = pair.first;
    auto const &dof_info = pair.second;
    dof_values.local_dof_values.emplace(
        dof_type, Eigen::MatrixXd::Zero(max_dim(dof_info), N_sites));
  }

  for (auto const &pair : global_dof_info) {
    std::string const &dof_type = pair.first;
    auto const &dof_info = pair.second;
    dof_values.global_dof_values.emplace(dof_type,
                                         Eigen::VectorXd::Zero(dof_info.dim()));
  }

  return dof_values;
}

/// Convert ConfigDoFValues expressed in prim basis to standard basis
template <typename GlobalDoFSetType, typename LocalDoFSetType>
ConfigDoFValues to_standard_values(
    ConfigDoFValues const &dof_values, Index N_sublat, Index N_volume,
    std::map<DoFKey, GlobalDoFSetType> const &global_dof_info,
    std::map<DoFKey, std::vector<LocalDoFSetType>> const &local_dof_info) {
  ConfigDoFValues standard_values;
  standard_values.occupation = dof_values.occupation;

  for (auto const &pair : dof_values.local_dof_values) {
    std::string const &dof_type = pair.first;
    Eigen::MatrixXd const &values = pair.second;
    auto it = local_dof_info.find(dof_type);
    if (it == local_dof_info.end()) {
      std::stringstream msg;
      msg << "Error in clexulator::to_standard_values: Incompatible local DoF";
      throw std::runtime_error(msg.str());
    }
    auto const &dof_info = it->second;
    standard_values.local_dof_values.emplace(
        dof_type,
        local_to_standard_values(values, N_sublat, N_volume, dof_info));
  }

  for (auto const &pair : dof_values.global_dof_values) {
    std::string const &dof_type = pair.first;
    Eigen::VectorXd const &values = pair.second;
    auto it = global_dof_info.find(dof_type);
    if (it == global_dof_info.end()) {
      std::stringstream msg;
      msg << "Error in clexulator::to_standard_values: Incompatible local DoF";
      throw std::runtime_error(msg.str());
    }
    auto const &dof_info = it->second;
    standard_values.global_dof_values.emplace(
        dof_type, global_to_standard_values(values, dof_info));
  }

  return standard_values;
}

/// Convert ConfigDoFValues expressed in standard basis to prim basis
template <typename GlobalDoFSetType, typename LocalDoFSetType>
ConfigDoFValues from_standard_values(
    ConfigDoFValues const &standard_values, Index N_sublat, Index N_volume,
    std::map<DoFKey, GlobalDoFSetType> const &global_dof_info,
    std::map<DoFKey, std::vector<LocalDoFSetType>> const &local_dof_info) {
  ConfigDoFValues dof_values;
  dof_values.occupation = standard_values.occupation;

  for (auto const &pair : standard_values.local_dof_values) {
    std::string const &dof_type = pair.first;
    Eigen::MatrixXd const &values = pair.second;
    auto it = local_dof_info.find(dof_type);
    if (it == local_dof_info.end()) {
      std::stringstream msg;
      msg << "Error in clexulator::to_standard_values: Incompatible local DoF";
      throw std::runtime_error(msg.str());
    }
    auto const &dof_info = it->second;
    dof_values.local_dof_values.emplace(
        dof_type,
        local_from_standard_values(values, N_sublat, N_volume, dof_info));
  }

  for (auto const &pair : standard_values.global_dof_values) {
    std::string const &dof_type = pair.first;
    Eigen::VectorXd const &values = pair.second;
    auto it = global_dof_info.find(dof_type);
    if (it == global_dof_info.end()) {
      std::stringstream msg;
      msg << "Error in clexulator::to_standard_values: Incompatible local DoF";
      throw std::runtime_error(msg.str());
    }
    auto const &dof_info = it->second;
    dof_values.global_dof_values.emplace(
        dof_type, global_from_standard_values(values, dof_info));
  }

  return dof_values;
}

/// \brief Calculate the shape factors needed for updates between
///     ConfigDoFValues::occupation and ConfigDoFValues::multi_occupation
///
/// \param discrete_dof_dim The value
///     `discrete_dof_dim[sublattice_index][dof_type_index]` is the number
///     of allowed discrete values for the `dof_type_index`-th discrete
///     DoF on the `sublattice_index`-th sublattice.
/// \return occupation_shape_factors The values in
///     `occupation_shape_factors[sublattice_index]` are used to convert
///     between single and multi occupation indices for the discrete dof,
///     on the `sublattice_index`-th sublattice, where a column in
///     `ConfigDofValues::multi_occupation` is like "rolled" indices
///     (i.e. [0,0], [0,1], [0,2], [1,0], ...), and corresponds to a
///     value in `ConfigDoFValues::occupation` which is like an
///     "unrolled" index (i.e. 0, 1, 2, 3, ...).
inline std::vector<std::vector<int>> make_occupation_shape_factors(
    std::vector<std::vector<int>> const &discrete_dof_dim) {
  // Ex: (for a particular sublattice, b)

  std::vector<std::vector<int>> occupation_shape_factors;
  for (auto const &discrete_dof_dim_on_b : discrete_dof_dim) {
    std::vector<int> _occupation_shape_factors;
    for (int i = 0; i < discrete_dof_dim_on_b.size(); ++i) {
      int factor = 1;
      for (int j = i + 1; j < discrete_dof_dim_on_b.size(); ++j) {
        factor *= discrete_dof_dim_on_b[j];
      }
      _occupation_shape_factors.push_back(factor);
    }
    occupation_shape_factors.push_back(_occupation_shape_factors);
  }
  return occupation_shape_factors;
}

/// \brief Update ConfigDoFValues::occupation to be consistent with
///     ConfigDoFValues::multi_occupation, on a single site
inline void update_single_occupation(
    ConfigDoFValues &dof_values, Index N_sublat, Index N_volume,
    std::vector<std::vector<int>> const &occupation_shape_factors,
    Index linear_site_index) {
  Index b = linear_site_index / N_volume;
  dof_values.occupation(linear_site_index) = 0;
  for (int i = 0; i < occupation_shape_factors[b].size(); ++i) {
    dof_values.occupation(linear_site_index) +=
        occupation_shape_factors[b][i] *
        dof_values.multi_occupation(i, linear_site_index);
  }
}

/// \brief Make the default ConfigDoFValues::multi_occupation matrix
inline void make_default_multi_occupation(
    ConfigDoFValues &dof_values, Index N_sublat, Index N_volume,
    std::vector<std::vector<int>> const &discrete_dof_dim) {
  Index N_sites = N_sublat * N_volume;
  dof_values.multi_occupation.resize(discrete_dof_dim.size(), N_sites);
  dof_values.multi_occupation.setZero();
}

/// \brief Update ConfigDoFValues::occupation to be consistent with
///     ConfigDoFValues::multi_occupation
inline void update_single_occupation(
    ConfigDoFValues &dof_values, Index N_sublat, Index N_volume,
    std::vector<std::vector<int>> const &occupation_shape_factors) {
  Index N_sites = N_sublat * N_volume;
  for (Index l = 0; l < N_sites; ++l) {
    update_single_occupation(dof_values, N_sublat, N_volume,
                             occupation_shape_factors, l);
  }
}

/// \brief Update ConfigDoFValues::multi_occupation to be consistent with
///     ConfigDoFValues::occupation, on a single site
inline void update_multi_occupation(
    ConfigDoFValues &dof_values, Index N_sublat, Index N_volume,
    std::vector<std::vector<int>> const &occupation_shape_factors,
    Index linear_site_index) {
  Index b = linear_site_index / N_volume;
  int remaining = dof_values.occupation(linear_site_index);
  for (int i = 0; i < occupation_shape_factors[b].size(); ++i) {
    dof_values.multi_occupation(i, linear_site_index) = 0;
    while (occupation_shape_factors[b][i] <= remaining) {
      dof_values.multi_occupation(i, linear_site_index) += 1;
      remaining -= occupation_shape_factors[b][i];
    }
  }
}

/// \brief Update ConfigDoFValues::multi_occupation to be consistent with
///     ConfigDoFValues::occupation
inline void update_multi_occupation(
    ConfigDoFValues &dof_values, Index N_sublat, Index N_volume,
    std::vector<std::vector<int>> const &occupation_shape_factors) {
  Index N_sites = N_sublat * N_volume;
  for (Index l = 0; l < N_sites; ++l) {
    update_multi_occupation(dof_values, N_sublat, N_volume,
                            occupation_shape_factors, l);
  }
}

}  // namespace clexulator
}  // namespace CASM

#endif
