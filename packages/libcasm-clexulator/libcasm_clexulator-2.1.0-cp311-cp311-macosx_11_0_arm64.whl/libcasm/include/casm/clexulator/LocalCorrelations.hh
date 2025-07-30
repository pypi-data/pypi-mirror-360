#ifndef CASM_clexulator_LocalCorrelations
#define CASM_clexulator_LocalCorrelations

#include <memory>
#include <set>
#include <vector>

#include "casm/crystallography/DoFDecl.hh"
#include "casm/global/definitions.hh"
#include "casm/global/eigen.hh"

namespace CASM {
namespace xtal {
class UnitCellCoord;
}

namespace clexulator {

struct ConfigDoFValues;
class Clexulator;
class SuperNeighborList;

// --- LocalCorrelations ---

/// \brief Manages local correlations calculations
///
class LocalCorrelations {
 public:
  /// \brief Constructor - calculate select correlation elements
  LocalCorrelations(
      std::shared_ptr<SuperNeighborList const> const &supercell_neighbor_list,
      std::shared_ptr<std::vector<Clexulator> const> const &clexulator,
      std::vector<unsigned int> const &correlation_indices,
      ConfigDoFValues const *_dof_values = nullptr);

  /// \brief Constructor - calculate all correlation elements
  LocalCorrelations(
      std::shared_ptr<SuperNeighborList const> const &supercell_neighbor_list,
      std::shared_ptr<std::vector<Clexulator> const> const &clexulator,
      ConfigDoFValues const *_dof_values = nullptr);

  /// \brief Reset internal pointer to DoF values - must have the same supercell
  void set(ConfigDoFValues const *_dof_values);

  /// \brief Get internal pointer to DoF values
  ConfigDoFValues const *get() const;

  /// \brief Return the coordinates of sites (relative to the origin unit cell)
  ///     where a change in DoF values requires this calculators values to be
  ///     re-calculated.
  std::set<xtal::UnitCellCoord> required_update_neighborhood(
      Index equivalent_index) const;

  /// \brief Number of correlations
  Index corr_size() const;

  /// \brief The elements of the correlations vector that will be calculated.
  std::vector<unsigned int> const &correlation_indices() const;

  /// \brief Calculate and return local correlations
  Eigen::VectorXd const &local(Index unitcell_index, Index equivalent_index);

 private:
  /// Holds all correlation indices
  std::vector<unsigned int> m_correlation_indices;

  unsigned int const *m_corr_indices_begin;
  unsigned int const *m_corr_indices_end;

  /// Holds last local correlation results
  Eigen::VectorXd m_local_corr;

  /// DoF values to use
  ConfigDoFValues const *m_dof_values;

  /// SuperNeighborList to use
  std::shared_ptr<SuperNeighborList const> m_supercell_neighbor_list;

  /// Clexulators to use (one for each symmetrically equivalent phenomenal
  /// cluster per unit cell)
  std::shared_ptr<std::vector<Clexulator> const> m_clexulator;
};

/// \brief Return the vector [0, 1, 2, ... corr_size-1]
std::vector<unsigned int> all_correlation_indices(
    std::shared_ptr<std::vector<Clexulator> const> const &clexulator);

}  // namespace clexulator
}  // namespace CASM

#endif
