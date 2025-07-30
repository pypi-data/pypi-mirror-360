#include "casm/clexulator/Correlations.hh"

#include "casm/clexulator/ClexParamPack.hh"
#include "casm/clexulator/Clexulator.hh"
#include "casm/clexulator/NeighborList.hh"
#include "casm/crystallography/AnisoValTraits.hh"

namespace CASM {

namespace clexulator {

/// \brief Constructor - calculate select correlation elements
///
/// \param supercell_neighbor_list Pointer to the neighbor list used as input
///     to the Clexulator
/// \param clexulator Pointer to the Clexulator used to calculate correlations
/// \param correlation_indices Specifies the elements of the correlations
///     vector that will be calculated. Correlation vectors will always be the
///     size specified by clexulator->corr_size(), but elements not specified
///     by `correlation_indices` will have undefined value.
/// \param _dof_values Pointer to the ConfigDoFValues to be used as input for
///     calculating correlations. As with direct use of Clexulator, the
///     ConfigDoFValues object being used as input may be modified between
///     calls, but the pointers to the underlying global and local DoF value
///     vectors and matrices must remain valid (i.e. they must not be erased)
///     or a new Correlations object should be used. May be constructed with
///     nullptr, then set later via `Correlations::set`.
Correlations::Correlations(
    std::shared_ptr<SuperNeighborList const> const &supercell_neighbor_list,
    std::shared_ptr<Clexulator const> const &clexulator,
    std::vector<unsigned int> const &correlation_indices,
    ConfigDoFValues const *_dof_values)
    : m_correlation_indices(correlation_indices),
      m_dof_values(_dof_values),
      m_supercell_neighbor_list(supercell_neighbor_list),
      m_clexulator(clexulator),
      m_corr_size(m_clexulator->corr_size()) {
  if (m_supercell_neighbor_list == nullptr) {
    throw std::runtime_error(
        "Error constructing Correlations: supercell_neighbor_list == nullptr");
  }

  if (m_clexulator == nullptr) {
    throw std::runtime_error(
        "Error constructing Correlations: clexulator == nullptr");
  }

  // construct m_all_correlation_indices
  m_corr_indices_begin = m_correlation_indices.data();
  m_corr_indices_end = m_corr_indices_begin + m_correlation_indices.size();
}

/// \brief Constructor - calculate all correlation elements
///
/// \param supercell_neighbor_list Pointer to the neighbor list used as input
///     to the Clexulator
/// \param clexulator Pointer to the Clexulator used to calculate correlations
/// \param _dof_values Pointer to the ConfigDoFValues to be used as input for
///     calculating correlations. As with direct use of Clexulator, the
///     ConfigDoFValues object being used as input may be modified between
///     calls, but the pointers to the underlying global and local DoF value
///     vectors and matrices must remain valid (i.e. they must not be erased)
///     or a new Correlations object should be used. May be constructed with
///     nullptr, then set later via `Correlations::set`.
///
/// Note:
/// - This overload constructs an instance that will calculate all correlation
/// vector elements.
Correlations::Correlations(
    std::shared_ptr<SuperNeighborList const> const &supercell_neighbor_list,
    std::shared_ptr<Clexulator const> const &clexulator,
    ConfigDoFValues const *_dof_values)
    : Correlations(supercell_neighbor_list, clexulator,
                   all_correlation_indices(clexulator->corr_size()),
                   _dof_values) {}

/// \brief Reset internal pointer to DoF values - must have the same supercell
///
/// \param _dof_values Pointer to the ConfigDoFValues to be used as input for
///     calculating correlations. As with direct use of Clexulator, the
///     ConfigDoFValues object being used as input may be modified between
///     calls, but the pointers to the underlying global and local DoF value
///     vectors and matrices must remain valid (i.e. they must not be erased)
///     or a new Correlations object should be used.
///
void Correlations::set(ConfigDoFValues const *_dof_values) {
  if (_dof_values == nullptr) {
    throw std::runtime_error(
        "Error in Correlations::set: _dof_values == nullptr");
  }
  m_dof_values = _dof_values;
}

/// \brief Get internal pointer to DoF values
ConfigDoFValues const *Correlations::get() const { return m_dof_values; }

/// \brief Get the neighborhood of sites where a change in DoF value requires
///     an update of the correlation values
std::set<xtal::UnitCellCoord> Correlations::required_update_neighborhood()
    const {
  return m_clexulator->site_neighborhood(m_corr_indices_begin,
                                         m_corr_indices_end);
}

/// \brief Number of correlations
Index Correlations::corr_size() const { return m_corr_size; }

/// \brief The elements of the correlations vector that will be calculated.
std::vector<unsigned int> const &Correlations::correlation_indices() const {
  return m_correlation_indices;
}

/// \brief Calculate and return per_unitcell correlations
///
/// \param per_supercell_correlations Extensive correlations, to be normalized
///     by the number of unit cells in the supercell.
///
/// Notes:
/// - Result is a vector of size clexulator->corr_size().
/// - Constructor specifies which vector elements are defined.
/// - Result is a reference to an internal Eigen::VectorXd. The reference is
///   valid until the next time this method is called.
Eigen::VectorXd const &Correlations::per_unitcell(
    Eigen::VectorXd const &per_supercell_correlations) {
  if (m_per_unitcell_corr.size() != m_corr_size) {
    m_per_unitcell_corr.resize(m_corr_size);
    m_per_unitcell_corr.setZero();
  }
  double n_unitcells = (double)m_supercell_neighbor_list->n_unitcells();
  for (auto it = m_corr_indices_begin; it != m_corr_indices_end; ++it) {
    *(m_per_unitcell_corr.data() + *it) =
        *(per_supercell_correlations.data() + *it) / n_unitcells;
  }
  return m_per_unitcell_corr;
}

/// \brief Calculate and return per_supercell correlations
///
/// \returns The basis function values summed over the entire configuration
///
/// Notes:
/// - Result is a vector of size clexulator->corr_size().
/// - Constructor specifies which vector elements are defined.
/// - Result is a reference to an internal Eigen::VectorXd. The reference is
///   valid until the next time this method is called.
Eigen::VectorXd const &Correlations::per_supercell() {
  if (m_per_supercell_corr.size() != m_corr_size) {
    m_per_supercell_corr.resize(m_corr_size);
    m_per_supercell_corr.setZero();
  }
  if (m_tcorr.size() != m_corr_size) {
    m_tcorr.resize(m_corr_size);
    m_tcorr.setZero();
  }
  int n_unitcells = m_supercell_neighbor_list->n_unitcells();

  for (auto it = m_corr_indices_begin; it != m_corr_indices_end; ++it) {
    *(m_per_supercell_corr.data() + *it) = 0.0;
  }

  for (int unitcell_index = 0; unitcell_index < n_unitcells; unitcell_index++) {
    // Fill up contributions
    m_clexulator->calc_restricted_global_corr_contribution(
        *m_dof_values, m_supercell_neighbor_list->sites(unitcell_index).data(),
        m_tcorr.data(), m_corr_indices_begin, m_corr_indices_end);

    for (auto it = m_corr_indices_begin; it != m_corr_indices_end; ++it) {
      *(m_per_supercell_corr.data() + *it) += *(m_tcorr.data() + *it);
    }
  }
  return m_per_supercell_corr;
}

/// \brief Calculate and return the contribution from a particular
/// unit cell
///
/// \param linear_unitcell_index Linear unit cell index (as defined by a
///     UnitCellIndexConverter) to calculate correlation contributions from
///
/// Notes:
/// - Result is a vector of size clexulator->corr_size().
/// - Constructor specifies which vector elements are defined.
/// - Result is a reference to an internal Eigen::VectorXd. The reference is
///   valid until the next time this method is called.
Eigen::VectorXd const &Correlations::contribution(Index linear_unitcell_index) {
  if (m_tcorr.size() != m_corr_size) {
    m_tcorr.resize(m_corr_size);
    m_tcorr.setZero();
  }
  int n_unitcells = m_supercell_neighbor_list->n_unitcells();

  if (linear_unitcell_index >= n_unitcells) {
    std::stringstream msg;
    msg << "Error in Correlations::contribution(Index): "
        << "linear_unitcell_index out of range (" << linear_unitcell_index
        << " >= " << n_unitcells << ")";
    throw std::runtime_error(msg.str());
  }

  auto const &unitcell_nlist =
      m_supercell_neighbor_list->sites(linear_unitcell_index);
  m_clexulator->calc_restricted_global_corr_contribution(
      *m_dof_values, unitcell_nlist.data(), m_tcorr.data(),
      m_corr_indices_begin, m_corr_indices_end);
  return m_tcorr;
}

/// \brief Check if point correlations valid at specified point
///
/// \param linear_unitcell_index Linear site index (as defined by a
///     UnitCellCoordIndexConverter)
///
/// \return True if there are point correlations associated with the given site
bool Correlations::has_point(Index linear_site_index) const {
  if (linear_site_index < 0 ||
      linear_site_index >= m_supercell_neighbor_list->n_sites()) {
    std::stringstream msg;
    msg << "Error in Correlations::has_point: "
        << "invalid linear_site_index.";
    throw std::runtime_error(msg.str());
  }

  Index neighbor_index =
      m_supercell_neighbor_list->neighbor_index(linear_site_index);

  if (neighbor_index == -1) {
    return false;
  }
  return true;
}

/// \brief Calculate and return correlations contributions from specified site
///
/// \param linear_site_index Linear site index (as defined by a
///     UnitCellCoordIndexConverter) to calculate point correlations for.
/// \param skip_if_unnecessary_for_occ_delta If true, skip calculating point
///     correlations if they are not necessary for calculating `occ_delta`.
///     This will be the case if the supercell is not too small
///     (`supercell_neighbor_list->overlap() == false`).
///
/// \return Sum of all basis functions that include DoF from the specified site.
///
/// Notes:
/// - Result is a vector of size clexulator->corr_size().
/// - Constructor specifies which vector elements are defined.
/// - Result is a reference to an internal Eigen::VectorXd. The reference is
///   valid until any this method is called again.
Eigen::VectorXd const &Correlations::point(
    Index linear_site_index, bool skip_if_unnecessary_for_occ_delta) {
  if (m_point_corr.size() != m_corr_size) {
    m_point_corr.resize(m_corr_size);
    m_point_corr.setZero();
  }

  if (!m_supercell_neighbor_list->overlaps() &&
      skip_if_unnecessary_for_occ_delta) {
    return m_point_corr;
  }

  if (linear_site_index < 0 ||
      linear_site_index >= m_supercell_neighbor_list->n_sites()) {
    std::stringstream msg;
    msg << "Error in Correlations::point: "
        << "invalid linear_site_index.";
    throw std::runtime_error(msg.str());
  }

  Index unitcell_index =
      m_supercell_neighbor_list->unitcell_index(linear_site_index);
  Index neighbor_index =
      m_supercell_neighbor_list->neighbor_index(linear_site_index);

  if (neighbor_index == -1) {
    std::stringstream msg;
    msg << "Error in Correlations::point: invalid linear_site_index."
        << "No point correlations associated with the site.";
    throw std::runtime_error(msg.str());
  }

  auto const &unitcell_nlist = m_supercell_neighbor_list->sites(unitcell_index);
  m_clexulator->calc_restricted_point_corr(
      *m_dof_values, unitcell_nlist.data(), neighbor_index, m_point_corr.data(),
      m_corr_indices_begin, m_corr_indices_end);
  return m_point_corr;
}

/// \brief Calculate and return all point correlations, as a matrix
///
/// \param include_all_sites If true, include a row for every site, even if
/// there are no point correlations associated with that site (in which case
/// the row is all zeros). If false, only include rows are only included for
/// sites from sublattices included in `PrimNeighborList::sublat_indices()`
/// (rows are still ordered according to increasing site index).
Eigen::MatrixXd Correlations::all_points(bool include_all_sites) {
  Index n_unitcells = m_supercell_neighbor_list->n_unitcells();
  Index n_sites = m_supercell_neighbor_list->n_sites();
  Index n_rows =
      include_all_sites ? n_sites : n_unitcells * m_clexulator->n_point_corr();
  Eigen::MatrixXd corr = Eigen::MatrixXd::Zero(n_rows, m_corr_size);
  Index row_index = 0;
  for (Index l = 0; l < n_sites; l++) {
    if (m_supercell_neighbor_list->neighbor_index(l) == -1) {
      if (include_all_sites) {
        ++row_index;
      } else {
        continue;
      }
    } else {
      corr.row(row_index) = point(l);
      ++row_index;
    }
  }
  return corr;
}

/// \brief Return the site index corresponding to each row of the matrix
/// returned by `all_points` or `restricted_all_points`
std::vector<Index> Correlations::all_points_site_indices(
    bool include_all_sites) {
  std::vector<Index> site_indices;
  Index n_sites = m_supercell_neighbor_list->n_sites();
  for (Index l = 0; l < n_sites; l++) {
    if (m_supercell_neighbor_list->neighbor_index(l) == -1 &&
        !include_all_sites) {
      continue;
    }
    site_indices.push_back(l);
  }
  return site_indices;
}

/// \brief Calculate and return change in (per_supercell) correlations due to an
/// occupation change
///
/// \param linear_site_index Linear site index (as defined by a
///     UnitCellCoordIndexConverter) to calculate point correlations for.
/// \param new_occ Occupation value to calculate the change in correlations for.
/// \param reference_point_correlations The point correlations of the specified
///     site before the change in occupation value. This value is not needed
///     and ignored if the supercell is large enough (`supercell_neighbor_list-
///     >overlap == false`).
///
/// \returns Change in per_supercell correlations, relative to
///     `reference_point_correlations`
///
/// Notes:
/// - Result is a vector of size clexulator->corr_size().
/// - Constructor specifies which vector elements are defined.
/// - Result is a reference to an internal Eigen::VectorXd. The reference is
///   valid until any of this, `local_delta`, or `global_delta` is called.
Eigen::VectorXd const &Correlations::occ_delta(
    Index linear_site_index, int new_occ,
    Eigen::VectorXd const &reference_point_correlations) {
  if (m_delta_corr.size() != m_corr_size) {
    m_delta_corr.resize(m_corr_size);
    m_delta_corr.setZero();
  }
  Index unitcell_index =
      m_supercell_neighbor_list->unitcell_index(linear_site_index);
  int neighbor_index =
      m_supercell_neighbor_list->neighbor_index(linear_site_index);

  auto const &nlist_sites = m_supercell_neighbor_list->sites(unitcell_index);
  long int const *nlist_begin = nlist_sites.data();

  if (!m_supercell_neighbor_list->overlaps()) {
    int curr_occ = m_dof_values->occupation[linear_site_index];
    m_clexulator->calc_restricted_delta_point_corr(
        *m_dof_values, nlist_begin, neighbor_index, curr_occ, new_occ,
        m_delta_corr.data(), m_corr_indices_begin, m_corr_indices_end);
    return m_delta_corr;
  } else {
    // Get current value
    Eigen::VectorXi const &values = m_dof_values->occupation;
    int curr_occ = values[linear_site_index];

    // Apply change (at the end we will unapply)
    Eigen::VectorXi &mutable_values = const_cast<Eigen::VectorXi &>(values);
    mutable_values[linear_site_index] = new_occ;

    // Calculate final point corr
    m_clexulator->calc_restricted_point_corr(
        *m_dof_values, nlist_begin, neighbor_index, m_delta_corr.data(),
        m_corr_indices_begin, m_corr_indices_end);

    // dcorr = final - initial
    Eigen::VectorXd const &before = reference_point_correlations;
    for (auto it = m_corr_indices_begin; it != m_corr_indices_end; ++it) {
      *(m_delta_corr.data() + *it) -= *(before.data() + *it);
    }

    // Unapply change
    mutable_values[linear_site_index] = curr_occ;
    return m_delta_corr;
  }
}

/// \brief Calculate and return change in (per_supercell) correlations due to
/// multiple occupation changes
Eigen::VectorXd const &Correlations::occ_delta(
    std::vector<Index> const &linear_site_index,
    std::vector<int> const &new_occ) {
  if (m_delta_corr.size() != m_corr_size) {
    m_delta_corr.resize(m_corr_size);
    m_delta_corr.setZero();
  }
  if (m_tcorr.size() != m_corr_size) {
    m_tcorr.resize(m_corr_size);
    m_tcorr.setZero();
  }
  if (m_curr_occ.size() < linear_site_index.size()) {
    m_curr_occ.resize(linear_site_index.size());
  }

  Eigen::VectorXi const &values = m_dof_values->occupation;
  Eigen::VectorXi &mutable_values = const_cast<Eigen::VectorXi &>(values);

  // Initialize delta corr to 0.0
  for (auto it = m_corr_indices_begin; it != m_corr_indices_end; ++it) {
    *(m_delta_corr.data() + *it) = 0.0;
  }

  // For each occupation change...
  for (Index i = 0; i < linear_site_index.size(); ++i) {
    // Remember original occupant
    Index l = linear_site_index[i];
    int curr_occ = values[l];
    m_curr_occ[i] = curr_occ;

    // Get neighbor list info
    Index unitcell_index = m_supercell_neighbor_list->unitcell_index(l);
    int neighbor_index = m_supercell_neighbor_list->neighbor_index(l);
    auto const &nlist_sites = m_supercell_neighbor_list->sites(unitcell_index);
    long int const *nlist_begin = nlist_sites.data();

    // If no neighborhood overlap, use delta point functions
    if (!m_supercell_neighbor_list->overlaps()) {
      // Calculate delta point corr
      m_clexulator->calc_restricted_delta_point_corr(
          *m_dof_values, nlist_begin, neighbor_index, curr_occ, new_occ[i],
          m_tcorr.data(), m_corr_indices_begin, m_corr_indices_end);

      // Increment by delta point corr
      for (auto it = m_corr_indices_begin; it != m_corr_indices_end; ++it) {
        *(m_delta_corr.data() + *it) += *(m_tcorr.data() + *it);
      }

      // Apply change (at the end we will unapply)
      mutable_values[l] = new_occ[i];
    } else {
      // Else neighborhood overlaps, so calculate initial / final point corr

      // Calculate initial point corr
      m_clexulator->calc_restricted_point_corr(
          *m_dof_values, nlist_begin, neighbor_index, m_tcorr.data(),
          m_corr_indices_begin, m_corr_indices_end);

      // Decrement by initial point corr
      for (auto it = m_corr_indices_begin; it != m_corr_indices_end; ++it) {
        *(m_delta_corr.data() + *it) -= *(m_tcorr.data() + *it);
      }

      // Apply change (at the end we will unapply)
      mutable_values[l] = new_occ[i];

      // Calculate final point corr
      m_clexulator->calc_restricted_point_corr(
          *m_dof_values, nlist_begin, neighbor_index, m_tcorr.data(),
          m_corr_indices_begin, m_corr_indices_end);

      // Increment by final point corr
      for (auto it = m_corr_indices_begin; it != m_corr_indices_end; ++it) {
        *(m_delta_corr.data() + *it) += *(m_tcorr.data() + *it);
      }
    }
  }
  // Unapply changes
  for (Index i = 0; i < linear_site_index.size(); ++i) {
    mutable_values[linear_site_index[i]] = m_curr_occ[i];
  }
  return m_delta_corr;
}

/// \brief Calculate and return change in (per_supercell) correlations due to a
/// local continuous DoF change
///
/// \param key Specifies the type of DoF
/// \param linear_site_index Linear site index (as defined by a
///     UnitCellCoordIndexConverter) where the change occurs.
/// \param new_value Final value to calculate the change in correlations for.
/// \param reference_point_correlations The point correlations of the specified
///     site before the change in value.
///
/// \returns Change in per_supercell correlations, relative to
///     `reference_point_correlations`
///
/// Notes:
/// - Result is a vector of size clexulator->corr_size().
/// - Constructor specifies which vector elements are defined.
/// - Result is a reference to an internal Eigen::VectorXd. The reference is
///   valid until any of this, `local_delta`, or `global_delta` is called.
Eigen::VectorXd const &Correlations::local_delta(
    DoFKey const &key, Index linear_site_index,
    Eigen::VectorXd const &new_value,
    Eigen::VectorXd const &reference_point_correlations) {
  if (m_delta_corr.size() != m_corr_size) {
    m_delta_corr.resize(m_corr_size);
    m_delta_corr.setZero();
  }
  Index unitcell_index =
      m_supercell_neighbor_list->unitcell_index(linear_site_index);
  int neighbor_index =
      m_supercell_neighbor_list->neighbor_index(linear_site_index);

  auto const &nlist_sites = m_supercell_neighbor_list->sites(unitcell_index);
  long int const *nlist_begin = nlist_sites.data();

  // Get current value
  Eigen::MatrixXd const &values = m_dof_values->local_dof_values.at(key);
  Eigen::VectorXd curr_value = values.col(linear_site_index);

  // Apply change (at the end we will unapply)
  Eigen::MatrixXd &mutable_values = const_cast<Eigen::MatrixXd &>(values);
  mutable_values.col(linear_site_index) = new_value;

  // Calculate after
  m_clexulator->calc_restricted_point_corr(
      *m_dof_values, nlist_begin, neighbor_index, m_delta_corr.data(),
      m_corr_indices_begin, m_corr_indices_end);

  // dcorr = after - before
  Eigen::VectorXd const &before = reference_point_correlations;
  for (auto it = m_corr_indices_begin; it != m_corr_indices_end; ++it) {
    *(m_delta_corr.data() + *it) -= *(before.data() + *it);
  }

  // Unapply change
  mutable_values.col(linear_site_index) = curr_value;
  return m_delta_corr;
}

/// \brief Calculate and return change in (per_supercell) correlations due to a
/// global continuous DoF change
///
/// \param key Specifies the type of DoF
/// \param new_value Final value to calculate the change in correlations for.
/// \param reference_per_supercell_correlations The per_supercell correlations
/// of before
///     the change in value.
///
/// \returns Change in per_supercell correlations, relative to
///     `reference_point_correlations`
///
/// Notes:
/// - Result is a vector of size clexulator->corr_size().
/// - Constructor specifies which vector elements are defined.
/// - Result is a reference to an internal Eigen::VectorXd. The reference is
///   valid until any of this, `local_delta`, or `global_delta` is called.

Eigen::VectorXd const &Correlations::global_delta(
    DoFKey const &key, Eigen::VectorXd const &new_value,
    Eigen::VectorXd const &reference_per_supercell_correlations) {
  if (m_tcorr.size() != m_corr_size) {
    m_tcorr.resize(m_corr_size);
    m_tcorr.setZero();
  }
  if (m_delta_corr.size() != m_corr_size) {
    m_delta_corr.resize(m_corr_size);
    m_delta_corr.setZero();
  }

  // Get current value
  Eigen::VectorXd const &value = m_dof_values->global_dof_values.at(key);
  Eigen::VectorXd curr_value = value;

  // Apply change (at the end we will unapply)
  Eigen::VectorXd &mutable_value = const_cast<Eigen::VectorXd &>(value);
  mutable_value = new_value;

  // Calculate per_supercell correlations after change (store in m_delta_corr)
  // ----
  int n_unitcells = m_supercell_neighbor_list->n_unitcells();

  for (auto it = m_corr_indices_begin; it != m_corr_indices_end; ++it) {
    *(m_delta_corr.data() + *it) = 0.0;
  }

  for (int unitcell_index = 0; unitcell_index < n_unitcells; unitcell_index++) {
    // Fill up contributions
    m_clexulator->calc_restricted_global_corr_contribution(
        *m_dof_values, m_supercell_neighbor_list->sites(unitcell_index).data(),
        m_tcorr.data(), m_corr_indices_begin, m_corr_indices_end);

    for (auto it = m_corr_indices_begin; it != m_corr_indices_end; ++it) {
      *(m_delta_corr.data() + *it) += *(m_tcorr.data() + *it);
    }
  }
  // ----

  // dcorr = after - before
  Eigen::VectorXd const &before = reference_per_supercell_correlations;
  for (auto it = m_corr_indices_begin; it != m_corr_indices_end; ++it) {
    *(m_delta_corr.data() + *it) -= *(before.data() + *it);
  }

  // Unapply change
  mutable_value = curr_value;
  return m_delta_corr;
}

std::vector<unsigned int> all_correlation_indices(Index n) {
  std::vector<unsigned int> corr_indices;
  for (unsigned int i = 0; i < n; ++i) {
    corr_indices.push_back(i);
  }
  return corr_indices;
}

/// Gradients of Correlations

Eigen::MatrixXd const Correlations::grad_correlations(DoFKey const &key) {
  ClexParamKey paramkey;
  clexulator::ClexParamKey corr_key(m_clexulator->param_pack().key("corr"));
  clexulator::ClexParamKey dof_key;

  if (key == "occ") {
    paramkey =
        m_clexulator->param_pack().key("diff/corr/" + key + "_site_func");
    dof_key = m_clexulator->param_pack().key("occ_site_func");
  } else {
    paramkey = m_clexulator->param_pack().key("diff/corr/" + key + "_var");
    dof_key = m_clexulator->param_pack().key(key + "_var");
  }

  std::string em_corr, em_dof;
  em_corr = m_clexulator->param_pack().eval_mode(corr_key);
  em_dof = m_clexulator->param_pack().eval_mode(dof_key);

  // this const_cast is not great...
  // but it seems like the only place passing const Clexulator is a problem and
  // it is not actually changing clexulator before/after this function

  const_cast<Clexulator &>(*m_clexulator)
      .param_pack()
      .set_eval_mode(corr_key, "DIFF");
  const_cast<Clexulator &>(*m_clexulator)
      .param_pack()
      .set_eval_mode(dof_key, "DIFF");

  Eigen::MatrixXd gcorr;
  Index scel_vol = m_supercell_neighbor_list->n_unitcells();
  if (AnisoValTraits(key).global()) {
    Eigen::MatrixXd gcorr_func = m_dof_values->global_dof_values.at(key);
    gcorr.setZero(gcorr_func.size(), m_clexulator->corr_size());
    // Holds contribution to global correlations from a particular Neighborhood

    // std::vector<double> corr(clexulator.corr_size(), 0.0);
    for (int v = 0; v < scel_vol; v++) {
      // Fill up contributions
      m_clexulator->calc_global_corr_contribution(
          *m_dof_values, m_supercell_neighbor_list->sites(v).data());

      for (Index c = 0; c < m_clexulator->corr_size(); ++c)
        gcorr.col(c) += m_clexulator->param_pack().read(paramkey(c));
    }
  } else {
    Eigen::MatrixXd gcorr_func;
    gcorr.setZero(m_dof_values->local_dof_values.at(key).size(),
                  m_clexulator->corr_size());
    // Holds contribution to global correlations from a particular Neighborhood
    Index l;
    for (int v = 0; v < scel_vol; v++) {
      // Fill up contributions
      m_clexulator->calc_global_corr_contribution(
          *m_dof_values, m_supercell_neighbor_list->sites(v).data());

      for (Index c = 0; c < m_clexulator->corr_size(); ++c) {
        gcorr_func = m_clexulator->param_pack().read(paramkey(c));

        for (Index n = 0; n < m_clexulator->nlist_size(); ++n) {
          l = m_supercell_neighbor_list->sites(v)[n];
          // for(Index i=0; i<gcorr_func.cols(); ++i){
          gcorr.block(l * gcorr_func.rows(), c, gcorr_func.rows(), 1) +=
              gcorr_func.col(n);
          // std::cout << "Block: (" << l * gcorr_func.rows() << ", " << c << ",
          // " << gcorr_func.rows() << ", " << 1 << ") += " <<
          // gcorr_func.col(n).transpose() << "\n";
          //}
        }
      }
    }
  }
  const_cast<Clexulator &>(*m_clexulator)
      .param_pack()
      .set_eval_mode(corr_key, em_corr);
  const_cast<Clexulator &>(*m_clexulator)
      .param_pack()
      .set_eval_mode(dof_key, em_dof);

  return gcorr;
}

}  // namespace clexulator
}  // namespace CASM
