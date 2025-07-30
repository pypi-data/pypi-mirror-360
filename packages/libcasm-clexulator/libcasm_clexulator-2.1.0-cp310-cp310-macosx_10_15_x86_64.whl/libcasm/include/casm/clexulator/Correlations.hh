#ifndef CASM_clexulator_Correlations
#define CASM_clexulator_Correlations

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

// --- Correlations ---

/// \brief Manages correlations calculations
///
/// This is a bit higher level than direct use of Clexulator. It manages use of
/// the SuperNeighborList, and handles the looping and temporaries used in
/// typical calculations.
///
/// Notes:
/// - If the pointed-to ConfigDoFValues are modified, then Correlations member
/// functions can be called again to calculate and return correlations
/// - As with direct use of Clexulator, the ConfigDoFValues object being used
/// as input may be modified between calls, but the pointers to the underlying
/// global and local DoF value vectors & matrices must remain valid (i.e. they
/// must not be erased) or a new ConfigDoFValues object should be used.
class Correlations {
 public:
  /// \brief Constructor - calculate select correlation elements
  Correlations(
      std::shared_ptr<SuperNeighborList const> const &supercell_neighbor_list,
      std::shared_ptr<Clexulator const> const &clexulator,
      std::vector<unsigned int> const &correlation_indices,
      ConfigDoFValues const *_dof_values = nullptr);

  /// \brief Constructor - calculate all correlation elements
  Correlations(
      std::shared_ptr<SuperNeighborList const> const &supercell_neighbor_list,
      std::shared_ptr<Clexulator const> const &clexulator,
      ConfigDoFValues const *_dof_values = nullptr);

  /// \brief Set internal pointer to DoF values - must be consistent with
  ///     supercell_neighbor_list
  void set(ConfigDoFValues const *_dof_values);

  /// \brief Get internal pointer to DoF values
  ConfigDoFValues const *get() const;

  /// \brief Get the neighborhood of sites where a change in DoF value requires
  ///     an update of the correlation values
  std::set<xtal::UnitCellCoord> required_update_neighborhood() const;

  // --- Correlations ---

  /// \brief Number of correlations
  Index corr_size() const;

  /// \brief The elements of the correlations vector that will be calculated.
  std::vector<unsigned int> const &correlation_indices() const;

  /// \brief Calculate and return per_unitcell correlations
  Eigen::VectorXd const &per_unitcell(
      Eigen::VectorXd const &per_supercell_correlations);

  /// \brief Calculate and return per_supercell correlations
  Eigen::VectorXd const &per_supercell();

  /// \brief Calculate and return the contribution from a particular unit cell
  Eigen::VectorXd const &contribution(Index linear_unitcell_index);

  // --- Point correlations ---

  /// \brief Check if point correlations valid at specified point
  bool has_point(Index linear_site_index) const;

  /// \brief Calculate and return correlations at specified point
  Eigen::VectorXd const &point(Index linear_site_index,
                               bool skip_if_unnecessary_for_occ_delta = false);

  /// \brief Calculate and return all point correlations, as a matrix
  Eigen::MatrixXd all_points(bool include_all_sites = true);

  /// \brief Return the site index corresponding to each row of the matrix
  /// returned by `all_points`
  std::vector<Index> all_points_site_indices(bool include_all_sites = true);

  // --- Delta correlations ---

  // --- Occupation ---

  /// \brief Calculate and return change in (per_supercell) correlations due to
  /// an occupation change
  Eigen::VectorXd const &occ_delta(
      Index linear_site_index, int new_occ,
      Eigen::VectorXd const &reference_point_correlations);

  /// \brief Calculate and return change in (per_supercell) correlations due to
  /// multiple occupation changes
  Eigen::VectorXd const &occ_delta(std::vector<Index> const &linear_site_index,
                                   std::vector<int> const &new_occ);

  // --- Local continuous ---

  /// \brief Calculate and return change in (per_supercell) correlations due to
  /// a local continuous DoF change
  Eigen::VectorXd const &local_delta(
      DoFKey const &key, Index linear_site_index,
      Eigen::VectorXd const &new_value,
      Eigen::VectorXd const &reference_point_correlations);

  // --- Global continuous ---

  /// \brief Calculate and return change in (per_supercell) correlations due to
  /// a global continuous DoF change
  Eigen::VectorXd const &global_delta(
      DoFKey const &key, Eigen::VectorXd const &new_value,
      Eigen::VectorXd const &reference_per_supercell_correlations);

  // --- Gradients of correlations
  /// \brief Calculates and returns gradients of correlations with respect
  /// to DoF corresponding to key
  /// Returns a M x N matrix, where M represents the number of correlations,
  /// and N represents the dimensions of the degrees of freedom corresponding to
  /// key. For example, if key is Hstrain, N will be 6. If key is disp, and
  /// there are 3 sites in the configuration, N will be 9 (x, y, z displacements
  /// for each site). Each row of the matrix corresponds to gradients of all M
  /// correlations with respect to one of the dimensions of degrees of freedom
  /// corresponding to key
  Eigen::MatrixXd const grad_correlations(DoFKey const &key);

 private:
  /// Holds all correlation indices
  std::vector<unsigned int> m_correlation_indices;

  unsigned int const *m_corr_indices_begin;
  unsigned int const *m_corr_indices_end;

  /// Holds temporary correlations used in calculations internally
  Eigen::VectorXd m_tcorr;

  /// Holds last point correlation results
  Eigen::VectorXd m_point_corr;

  /// Holds last per_supercell correlation results
  Eigen::VectorXd m_per_supercell_corr;

  /// Holds last per_unitcell correlation results
  Eigen::VectorXd m_per_unitcell_corr;

  /// Holds last delta correlation results
  Eigen::VectorXd m_delta_corr;

  /// Holds temporary data for occ_delta method
  std::vector<int> m_curr_occ;

  /// DoF values to use
  ConfigDoFValues const *m_dof_values;

  /// SuperNeighborList to use
  std::shared_ptr<SuperNeighborList const> m_supercell_neighbor_list;

  /// Clexulator to use
  std::shared_ptr<Clexulator const> m_clexulator;

  /// Number of total correlations
  Index m_corr_size;
};

/// \brief Return the vector [0, 1, 2, ... n-1]
std::vector<unsigned int> all_correlation_indices(Index n);

}  // namespace clexulator
}  // namespace CASM

#endif
