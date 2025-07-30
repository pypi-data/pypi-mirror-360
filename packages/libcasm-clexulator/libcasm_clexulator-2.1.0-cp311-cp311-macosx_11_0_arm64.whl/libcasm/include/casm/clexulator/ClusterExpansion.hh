#ifndef CASM_clexulator_ClusterExpansion
#define CASM_clexulator_ClusterExpansion

#include <map>
#include <memory>
#include <set>

#include "casm/clexulator/Correlations.hh"
#include "casm/clexulator/SparseCoefficients.hh"
#include "casm/crystallography/UnitCellCoord.hh"

namespace CASM {
namespace clexulator {

/// \brief A cluster expansion calculator
class ClusterExpansion {
 public:
  ClusterExpansion(
      std::shared_ptr<SuperNeighborList const> const &_supercell_neighbor_list,
      std::shared_ptr<Clexulator const> const &_clexulator,
      SparseCoefficients const &_coefficients,
      ConfigDoFValues const *_dof_values = nullptr);

  /// \brief Reset pointer to configuration currently being calculated
  void set(ConfigDoFValues const *dof_values);

  /// \brief Pointer to configuration currently being calculated
  ConfigDoFValues const *get() const;

  /// \brief Get internal Correlations calculator
  Correlations &correlations();

  /// \brief Get internal Correlations calculator
  Correlations const &correlations() const;

  /// \brief Get internal SparseCoefficients
  SparseCoefficients &coefficients();

  /// \brief Get internal SparseCoefficients
  SparseCoefficients const &coefficients() const;

  double per_unitcell();

  double per_supercell();

  /// \brief Calculate change in cluster expansion value due to a single
  ///     occupation change
  double occ_delta_value(Index linear_site_index, int new_occ);

  /// \brief Calculate change in cluster expansion value due to a series of
  ///     occupation changes
  double occ_delta_value(std::vector<Index> const &linear_site_index,
                         std::vector<int> const &new_occ);

  double local_delta_value(DoFKey const &key, Index linear_site_index,
                           Eigen::VectorXd const &new_value);

  double global_delta_value(DoFKey const &key,
                            Eigen::VectorXd const &new_value);

  std::set<xtal::UnitCellCoord> required_update_neighborhood() const;

 private:
  /// \brief Used to evaluate correlations
  Correlations m_correlations;

  /// \brief Non-zero expansion coefficients
  SparseCoefficients m_coefficients;
};

/// \brief A calculator for multiple cluster expansions sharing the same basis
class MultiClusterExpansion {
 public:
  MultiClusterExpansion(
      std::shared_ptr<SuperNeighborList const> const &_supercell_neighbor_list,
      std::shared_ptr<Clexulator const> const &_clexulator,
      std::vector<SparseCoefficients> const &_coefficients,
      ConfigDoFValues const *_dof_values = nullptr);

  /// \brief Reset pointer to configuration currently being calculated
  void set(ConfigDoFValues const *dof_values);

  /// \brief Pointer to configuration currently being calculated
  ConfigDoFValues const *get() const;

  /// \brief Get internal Correlations calculator
  Correlations &correlations();

  /// \brief Get internal Correlations calculator
  Correlations const &correlations() const;

  /// \brief Get internal SparseCoefficients
  std::vector<SparseCoefficients> &coefficients();

  /// \brief Get internal SparseCoefficients
  std::vector<SparseCoefficients> const &coefficients() const;

  Eigen::VectorXd const &per_unitcell();

  Eigen::VectorXd const &per_supercell();

  /// \brief Calculate change in cluster expansion value due to a single
  ///     occupation change
  Eigen::VectorXd const &occ_delta_value(Index linear_site_index, int new_occ);

  /// \brief Calculate change in cluster expansion value due to a series of
  ///     occupation changes
  Eigen::VectorXd const &occ_delta_value(
      std::vector<Index> const &linear_site_index,
      std::vector<int> const &new_occ);

  Eigen::VectorXd const &local_delta_value(DoFKey const &key,
                                           Index linear_site_index,
                                           Eigen::VectorXd const &new_value);

  Eigen::VectorXd const &global_delta_value(DoFKey const &key,
                                            Eigen::VectorXd const &new_value);

  std::set<xtal::UnitCellCoord> required_update_neighborhood() const;

 private:
  Eigen::VectorXd const &_calc(Eigen::VectorXd const &corr);

  /// \brief Used to evaluate local correlations
  Correlations m_correlations;

  /// \brief Non-zero expansion coefficients
  std::vector<SparseCoefficients> m_coefficients;

  /// \brief Results
  Eigen::VectorXd m_values;
};

}  // namespace clexulator
}  // namespace CASM

#endif
