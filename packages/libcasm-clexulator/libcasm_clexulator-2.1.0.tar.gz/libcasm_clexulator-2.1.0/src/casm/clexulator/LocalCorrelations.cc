#include "casm/clexulator/LocalCorrelations.hh"

#include "casm/clexulator/Clexulator.hh"
#include "casm/clexulator/NeighborList.hh"

namespace CASM {

namespace clexulator {

/// \brief Constructor - calculate select correlation elements
///
/// \param supercell_neighbor_list Pointer to the neighbor list used as input
///     to the Clexulator
/// \param clexulator Pointer to a vector of Clexulator used to calculate
///     correlations for equivalent local phenomenal clusters
/// \param correlation_indices Specifies the elements of the correlations
///     vector that will be calculated. Correlation vectors will always be the
///     size specified by clexulator->corr_size(), but elements not specified
///     by `correlation_indices` will have undefined value.
/// \param dof_values Pointer to the ConfigDoFValues to be used as input for
///     calculating correlations. As with direct use of Clexulator, the
///     ConfigDoFValues object being used as input may be modified between
///     calls, but the pointers to the underlying global and local DoF value
///     vectors and matrices must remain valid (i.e. they must not be erased)
///     or a new LocalCorrelations object should be used.
LocalCorrelations::LocalCorrelations(
    std::shared_ptr<SuperNeighborList const> const &supercell_neighbor_list,
    std::shared_ptr<std::vector<Clexulator> const> const &clexulator,
    std::vector<unsigned int> const &correlation_indices,
    ConfigDoFValues const *_dof_values)
    : m_correlation_indices(correlation_indices),
      m_dof_values(_dof_values),
      m_supercell_neighbor_list(supercell_neighbor_list),
      m_clexulator(clexulator) {
  if (m_supercell_neighbor_list == nullptr) {
    throw std::runtime_error(
        "Error constructing LocalCorrelations: supercell_neighbor_list == "
        "nullptr");
  }

  if (m_clexulator == nullptr) {
    throw std::runtime_error(
        "Error constructing LocalCorrelations: clexulator == nullptr");
  }
  if (m_clexulator->size() == 0) {
    throw std::runtime_error(
        "Error constructing LocalCorrelations: clexulator->size() == 0");
  }
  for (Index i = 0; i < m_clexulator->size(); ++i) {
    if (i + 1 != m_clexulator->size()) {
      if ((*m_clexulator)[i].corr_size() !=
          (*m_clexulator)[i + 1].corr_size()) {
        throw std::runtime_error(
            "Error constructing LocalCorrelations: clexulators are not "
            "equivalent (as checked by corr_size)");
      }
    }
  }

  int n = (*m_clexulator)[0].corr_size();
  m_corr_indices_begin = m_correlation_indices.data();
  m_corr_indices_end = m_corr_indices_begin + m_correlation_indices.size();

  m_local_corr.resize(n);
  m_local_corr.setZero();
}

/// \brief Constructor - calculate all correlation elements
///
/// \param supercell_neighbor_list Pointer to the neighbor list used as input
///     to the Clexulator
/// \param clexulator Pointer to a vector of Clexulator used to calculate
///     correlations for equivalent local phenomenal clusters
/// \param dof_values Pointer to the ConfigDoFValues to be used as input for
///     calculating correlations. As with direct use of Clexulator, the
///     ConfigDoFValues object being used as input may be modified between
///     calls, but the pointers to the underlying global and local DoF value
///     vectors and matrices must remain valid (i.e. they must not be erased)
///     or a new LocalCorrelations object should be used.
LocalCorrelations::LocalCorrelations(
    std::shared_ptr<SuperNeighborList const> const &supercell_neighbor_list,
    std::shared_ptr<std::vector<Clexulator> const> const &clexulator,
    ConfigDoFValues const *_dof_values)
    : LocalCorrelations(supercell_neighbor_list, clexulator,
                        all_correlation_indices(clexulator), _dof_values) {}

/// \brief Reset internal pointer to DoF values - must have the same supercell
void LocalCorrelations::set(ConfigDoFValues const *_dof_values) {
  if (_dof_values == nullptr) {
    throw std::runtime_error(
        "Error in Correlations::reset: _dof_values == nullptr");
  }
  m_dof_values = _dof_values;
}

/// \brief Get internal pointer to DoF values
ConfigDoFValues const *LocalCorrelations::get() const { return m_dof_values; }

/// \brief Return the coordinates of sites (relative to the origin unit cell)
///     where a change in DoF values requires this calculators values to be
///     re-calculated.
std::set<xtal::UnitCellCoord> LocalCorrelations::required_update_neighborhood(
    Index equivalent_index) const {
  return (*m_clexulator)[equivalent_index].site_neighborhood(
      m_corr_indices_begin, m_corr_indices_end);
}

/// \brief Number of correlations
Index LocalCorrelations::corr_size() const {
  if (m_clexulator->size() == 0) {
    throw std::runtime_error("Error: empty local clexulator vector");
  }
  return m_clexulator->begin()->corr_size();
}

/// \brief The elements of the correlations vector that will be calculated.
std::vector<unsigned int> const &LocalCorrelations::correlation_indices()
    const {
  return m_correlation_indices;
}

/// \brief Calculate and return local correlations
///
/// \param unitcell_index Linear unitcell index associated with the phenomenal
///     cluster about which local correlations are to be calculated
/// \param equivalent_index Index into the input vector of Clexulator,
///     specifies which of the equivalent phenomenal clusters associated with
///     the given unit cell to calculate local correlations about.
///
/// Notes:
/// - Result is a vector of size clexulator->corr_size().
/// - Constructor specifies which vector elements are defined.
/// - Result is a reference to an internal Eigen::VectorXd. The reference is
///   valid until the next time this method is called.
Eigen::VectorXd const &LocalCorrelations::local(Index unitcell_index,
                                                Index equivalent_index) {
  int n_unitcells = m_supercell_neighbor_list->n_unitcells();

  if (unitcell_index < 0 || unitcell_index >= n_unitcells) {
    std::stringstream msg;
    msg << "Error in LocalCorrelations: "
        << "unitcell_index (" << unitcell_index << ") out of range [0,"
        << n_unitcells << ").";
    throw std::runtime_error(msg.str());
  }
  if (equivalent_index < 0 || equivalent_index >= m_clexulator->size()) {
    std::stringstream msg;
    msg << "Error in LocalCorrelations: "
        << "equivalent_index (" << equivalent_index << ") out of range [0,"
        << m_clexulator->size() << ").";
    throw std::runtime_error(msg.str());
  }

  auto const &unitcell_nlist = m_supercell_neighbor_list->sites(unitcell_index);
  (*m_clexulator)[equivalent_index].calc_restricted_global_corr_contribution(
      *m_dof_values, unitcell_nlist.data(), m_local_corr.data(),
      m_corr_indices_begin, m_corr_indices_end);
  return m_local_corr;
}

/// \brief Return the vector [0, 1, 2, ... corr_size-1]
std::vector<unsigned int> all_correlation_indices(
    std::shared_ptr<std::vector<Clexulator> const> const &clexulator) {
  if (clexulator->size() == 0) {
    throw std::runtime_error("Error: empty local clexulator vector");
  }
  Index n = clexulator->begin()->corr_size();

  std::vector<unsigned int> corr_indices;
  for (unsigned int i = 0; i < n; ++i) {
    corr_indices.push_back(i);
  }
  return corr_indices;
}

}  // namespace clexulator
}  // namespace CASM
