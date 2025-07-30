#include "casm/clexulator/LocalClusterExpansion.hh"

namespace CASM {
namespace clexulator {

LocalClusterExpansion::LocalClusterExpansion(
    std::shared_ptr<SuperNeighborList const> const &_supercell_neighbor_list,
    std::shared_ptr<std::vector<Clexulator> const> const &_clexulator,
    SparseCoefficients const &_coefficients, ConfigDoFValues const *_dof_values)
    : m_correlations(_supercell_neighbor_list, _clexulator, _coefficients.index,
                     _dof_values),
      m_coefficients(_coefficients) {}

/// \brief Reset pointer to configuration currently being calculated
void LocalClusterExpansion::set(ConfigDoFValues const *dof_values) {
  return m_correlations.set(dof_values);
}

/// \brief Pointer to configuration currently being calculated
ConfigDoFValues const *LocalClusterExpansion::get() const {
  return m_correlations.get();
}

/// \brief Get internal LocalCorrelations calculator
LocalCorrelations &LocalClusterExpansion::correlations() {
  return m_correlations;
}

/// \brief Get internal LocalCorrelations calculator
LocalCorrelations const &LocalClusterExpansion::correlations() const {
  return m_correlations;
}

/// \brief Get internal SparseCoefficients
SparseCoefficients &LocalClusterExpansion::coefficients() {
  return m_coefficients;
}

/// \brief Get internal SparseCoefficients
SparseCoefficients const &LocalClusterExpansion::coefficients() const {
  return m_coefficients;
}

/// \brief Value at particular unit cell and phenomenal cluster
double LocalClusterExpansion::value(Index unitcell_index,
                                    Index equivalent_index) {
  return m_coefficients *
         m_correlations.local(unitcell_index, equivalent_index);
}

/// \brief Return the coordinates of sites (relative to the origin unit cell)
///     where a change in DoF values requires this calculators values to be
///     re-calculated.
std::set<xtal::UnitCellCoord>
LocalClusterExpansion::required_update_neighborhood(
    Index equivalent_index) const {
  return m_correlations.required_update_neighborhood(equivalent_index);
}

// ---

namespace {

std::vector<unsigned int> make_all_indices(
    std::vector<SparseCoefficients> const &coefficients) {
  std::set<unsigned int> all_indices;
  for (auto const &c : coefficients) {
    for (unsigned int index : c.index) {
      all_indices.insert(index);
    }
  }
  return std::vector<unsigned int>(all_indices.begin(), all_indices.end());
}

}  // namespace

MultiLocalClusterExpansion::MultiLocalClusterExpansion(
    std::shared_ptr<SuperNeighborList const> const &_supercell_neighbor_list,
    std::shared_ptr<std::vector<Clexulator> const> const &_clexulator,
    std::vector<SparseCoefficients> const &_coefficients,
    ConfigDoFValues const *_dof_values)
    : m_correlations(_supercell_neighbor_list, _clexulator,
                     make_all_indices(_coefficients), _dof_values),
      m_coefficients(_coefficients) {
  m_values.resize(m_coefficients.size());
}

/// \brief Reset pointer to configuration currently being calculated
void MultiLocalClusterExpansion::set(ConfigDoFValues const *dof_values) {
  return m_correlations.set(dof_values);
}

/// \brief Pointer to configuration currently being calculated
ConfigDoFValues const *MultiLocalClusterExpansion::get() const {
  return m_correlations.get();
}

/// \brief Get internal LocalCorrelations calculator
LocalCorrelations &MultiLocalClusterExpansion::correlations() {
  return m_correlations;
}

/// \brief Get internal LocalCorrelations calculator
LocalCorrelations const &MultiLocalClusterExpansion::correlations() const {
  return m_correlations;
}

/// \brief Get internal SparseCoefficients
std::vector<SparseCoefficients> &MultiLocalClusterExpansion::coefficients() {
  return m_coefficients;
}

/// \brief Get internal SparseCoefficients
std::vector<SparseCoefficients> const &
MultiLocalClusterExpansion::coefficients() const {
  return m_coefficients;
}

/// \brief Values at particular unit cell and phenomenal cluster
///
/// The clex_index-th value in the result corresponds to the clex_index-th
/// coefficients
Eigen::VectorXd const &MultiLocalClusterExpansion::values(
    Index unitcell_index, Index equivalent_index) {
  auto const &corr = m_correlations.local(unitcell_index, equivalent_index);
  for (int i = 0; i < m_coefficients.size(); ++i) {
    m_values(i) = m_coefficients[i] * corr;
  }
  return m_values;
}

/// \brief Return the coordinates of sites (relative to the origin unit cell)
///     where a change in DoF values requires this calculators values to be
///     re-calculated.
std::set<xtal::UnitCellCoord>
MultiLocalClusterExpansion::required_update_neighborhood(
    Index equivalent_index) const {
  return m_correlations.required_update_neighborhood(equivalent_index);
}

}  // namespace clexulator
}  // namespace CASM
