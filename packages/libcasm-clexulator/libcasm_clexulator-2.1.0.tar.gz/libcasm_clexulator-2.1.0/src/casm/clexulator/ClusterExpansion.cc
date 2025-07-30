#include "casm/clexulator/ClusterExpansion.hh"

#include "casm/clexulator/Clexulator.hh"

namespace CASM {
namespace clexulator {

ClusterExpansion::ClusterExpansion(
    std::shared_ptr<SuperNeighborList const> const &_supercell_neighbor_list,
    std::shared_ptr<Clexulator const> const &_clexulator,
    SparseCoefficients const &_coefficients, ConfigDoFValues const *_dof_values)
    : m_correlations(_supercell_neighbor_list, _clexulator, _coefficients.index,
                     _dof_values),
      m_coefficients(_coefficients) {}

/// \brief Reset pointer to configuration currently being calculated
void ClusterExpansion::set(ConfigDoFValues const *dof_values) {
  return m_correlations.set(dof_values);
}

/// \brief Pointer to configuration currently being calculated
ConfigDoFValues const *ClusterExpansion::get() const {
  return m_correlations.get();
}

/// \brief Get internal Correlations calculator
Correlations &ClusterExpansion::correlations() { return m_correlations; }

/// \brief Get internal Correlations calculator
Correlations const &ClusterExpansion::correlations() const {
  return m_correlations;
}

/// \brief Get internal SparseCoefficients
SparseCoefficients &ClusterExpansion::coefficients() { return m_coefficients; }

/// \brief Get internal SparseCoefficients
SparseCoefficients const &ClusterExpansion::coefficients() const {
  return m_coefficients;
}

double ClusterExpansion::per_unitcell() {
  auto const &e = m_correlations.per_supercell();
  return m_coefficients * m_correlations.per_unitcell(e);
}

double ClusterExpansion::per_supercell() {
  return m_coefficients * m_correlations.per_supercell();
}

/// \brief Calculate change in cluster expansion value due to a single
///     occupation change
double ClusterExpansion::occ_delta_value(Index linear_site_index, int new_occ) {
  bool skip_if_unnecessary_for_occ_delta = true;
  auto const &p = m_correlations.point(linear_site_index,
                                       skip_if_unnecessary_for_occ_delta);
  return m_coefficients *
         m_correlations.occ_delta(linear_site_index, new_occ, p);
}

/// \brief Calculate change in cluster expansion value due to a series of
///     occupation changes
double ClusterExpansion::occ_delta_value(
    std::vector<Index> const &linear_site_index,
    std::vector<int> const &new_occ) {
  return m_coefficients * m_correlations.occ_delta(linear_site_index, new_occ);
}

double ClusterExpansion::local_delta_value(DoFKey const &key,
                                           Index linear_site_index,
                                           Eigen::VectorXd const &new_value) {
  auto const &p = m_correlations.point(linear_site_index);
  return m_coefficients *
         m_correlations.local_delta(key, linear_site_index, new_value, p);
}

double ClusterExpansion::global_delta_value(DoFKey const &key,
                                            Eigen::VectorXd const &new_value) {
  auto const &e = m_correlations.per_supercell();
  return m_coefficients * m_correlations.global_delta(key, new_value, e);
}

std::set<xtal::UnitCellCoord> ClusterExpansion::required_update_neighborhood()
    const {
  return m_correlations.required_update_neighborhood();
}

// ---

namespace {

std::vector<unsigned int> make_all_indices(
    std::vector<SparseCoefficients> const &coefficients) {
  std::set<unsigned int> _indices;
  for (auto const &c : coefficients) {
    for (unsigned int index : c.index) {
      _indices.insert(index);
    }
  }
  return std::vector<unsigned int>(_indices.begin(), _indices.end());
}

}  // namespace

MultiClusterExpansion::MultiClusterExpansion(
    std::shared_ptr<SuperNeighborList const> const &_supercell_neighbor_list,
    std::shared_ptr<Clexulator const> const &_clexulator,
    std::vector<SparseCoefficients> const &_coefficients,
    ConfigDoFValues const *_dof_values)
    : m_correlations(_supercell_neighbor_list, _clexulator,
                     make_all_indices(_coefficients), _dof_values),
      m_coefficients(_coefficients) {
  m_values.resize(m_coefficients.size());
}

/// \brief Reset pointer to configuration currently being calculated
void MultiClusterExpansion::set(ConfigDoFValues const *dof_values) {
  return m_correlations.set(dof_values);
}

/// \brief Pointer to configuration currently being calculated
ConfigDoFValues const *MultiClusterExpansion::get() const {
  return m_correlations.get();
}

/// \brief Get internal Correlations calculator
Correlations &MultiClusterExpansion::correlations() { return m_correlations; }

/// \brief Get internal Correlations calculator
Correlations const &MultiClusterExpansion::correlations() const {
  return m_correlations;
}

/// \brief Get internal SparseCoefficients
std::vector<SparseCoefficients> &MultiClusterExpansion::coefficients() {
  return m_coefficients;
}

/// \brief Get internal SparseCoefficients
std::vector<SparseCoefficients> const &MultiClusterExpansion::coefficients()
    const {
  return m_coefficients;
}

Eigen::VectorXd const &MultiClusterExpansion::per_unitcell() {
  auto const &e = m_correlations.per_supercell();
  return _calc(m_correlations.per_unitcell(e));
}

Eigen::VectorXd const &MultiClusterExpansion::per_supercell() {
  return _calc(m_correlations.per_supercell());
}

/// \brief Calculate change in cluster expansion value due to a single
///     occupation change
Eigen::VectorXd const &MultiClusterExpansion::occ_delta_value(
    Index linear_site_index, int new_occ) {
  bool skip_if_unnecessary_for_occ_delta = true;
  auto const &p = m_correlations.point(linear_site_index,
                                       skip_if_unnecessary_for_occ_delta);
  return _calc(m_correlations.occ_delta(linear_site_index, new_occ, p));
}

/// \brief Calculate change in cluster expansion value due to a series of
///     occupation changes
Eigen::VectorXd const &MultiClusterExpansion::occ_delta_value(
    std::vector<Index> const &linear_site_index,
    std::vector<int> const &new_occ) {
  return _calc(m_correlations.occ_delta(linear_site_index, new_occ));
}

Eigen::VectorXd const &MultiClusterExpansion::local_delta_value(
    DoFKey const &key, Index linear_site_index,
    Eigen::VectorXd const &new_value) {
  auto const &p = m_correlations.point(linear_site_index);
  return _calc(
      m_correlations.local_delta(key, linear_site_index, new_value, p));
}

Eigen::VectorXd const &MultiClusterExpansion::global_delta_value(
    DoFKey const &key, Eigen::VectorXd const &new_value) {
  auto const &e = m_correlations.per_supercell();
  return _calc(m_correlations.global_delta(key, new_value, e));
}

std::set<xtal::UnitCellCoord>
MultiClusterExpansion::required_update_neighborhood() const {
  return m_correlations.required_update_neighborhood();
}

Eigen::VectorXd const &MultiClusterExpansion::_calc(
    Eigen::VectorXd const &corr) {
  for (int i = 0; i < m_coefficients.size(); ++i) {
    m_values(i) = m_coefficients[i] * corr;
  }
  return m_values;
}

}  // namespace clexulator
}  // namespace CASM
