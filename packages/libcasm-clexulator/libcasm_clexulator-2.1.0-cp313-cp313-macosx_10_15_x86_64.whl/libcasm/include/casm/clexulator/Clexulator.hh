#ifndef CASM_clexulator_Clexulator
#define CASM_clexulator_Clexulator
#include <cstddef>

#include "casm/casm_io/Log.hh"
#include "casm/clexulator/BaseClexulator.hh"
#include "casm/clexulator/ConfigDoFValues.hh"
#include "casm/clexulator/NeighborList.hh"
#include "casm/crystallography/UnitCellCoord.hh"
#include "casm/global/filesystem.hh"
#include "casm/misc/cloneable_ptr.hh"

namespace CASM {
class RuntimeLibrary;

namespace clexulator {

/// \brief Evaluates correlations
///
/// CASM generates code for very efficient calculation of basis functions via
/// the print_clexulator function. This source code may be compiled, linked,
/// and used at runtime via Clexulator.
///
/// Notes:
/// - There could be undefined behavior if data within a ConfigDoFValues object
///   is changed between calls to Clexulator. For example, if
///   local_dof_values[type] is erased and then re-inserted pointers to the
///   values matrix for that type may (will?) fail.
///
class Clexulator {
 public:
  typedef clexulator::BaseClexulator::size_type size_type;

  Clexulator() {}

  /// \brief Construct a Clexulator
  Clexulator(std::string _name,
             std::unique_ptr<clexulator::BaseClexulator> _clex,
             std::shared_ptr<RuntimeLibrary> _lib);

  ~Clexulator();

  /// \brief Is runtime library loaded?
  bool initialized() const { return m_lib.get() != nullptr; }

  /// \brief Name
  std::string name() const { return m_name; }

  /// \brief Neighbor list size
  size_type nlist_size() const { return m_clex->nlist_size(); }

  /// \brief Number of correlations
  size_type corr_size() const { return m_clex->corr_size(); }

  /// \brief Valid range for `neighbor_ind` argument to calc_point_corr
  ///
  /// - For periodic clex, this is the number of sublattices.
  /// - For local clex, this is the neighbor list size.
  size_type n_point_corr() const { return m_clex->n_point_corr(); }

  /// \brief Obtain const reference to abstract ClexParamPack object
  ClexParamPack const &param_pack() const { return m_clex->param_pack(); }

  /// \brief Obtain reference to abstract ClexParamPack object
  ClexParamPack &param_pack() { return m_clex->param_pack(); }

  /// \brief Obtain ClexParamKey for a particular parameter
  ClexParamKey const &param_key(std::string const &_param_name) const {
    return m_clex->param_key(_param_name);
  }

  /// \brief The UnitCell involved in calculating the basis functions,
  /// relative origin UnitCell
  const std::set<xtal::UnitCell> &neighborhood() const {
    return m_clex->neighborhood();
  }

  /// \brief The UnitCell involved in calculating the basis functions
  /// for a particular orbit, relative origin UnitCell
  const std::set<xtal::UnitCell> &neighborhood(
      size_type linear_orbit_index) const {
    return m_clex->neighborhood(linear_orbit_index);
  }

  /// \brief The UnitCellCoord involved in calculating the basis functions,
  /// relative origin UnitCell
  std::set<xtal::UnitCellCoord> site_neighborhood() const {
    std::set<xtal::UnitCellCoord> result;
    for (Index i = 0; i < corr_size(); ++i) {
      std::set<xtal::UnitCellCoord> const &tmp = this->site_neighborhood(i);
      result.insert(tmp.begin(), tmp.end());
    }
    return result;
  }

  /// \brief The UnitCellCoord involved in calculating the basis functions
  /// for a particular orbit, relative origin UnitCell
  const std::set<xtal::UnitCellCoord> &site_neighborhood(
      size_type linear_orbit_index) const {
    return m_clex->site_neighborhood(linear_orbit_index);
  }

  /// \brief The UnitCellCoord involved in calculating the basis functions
  /// for a selection of orbits, relative origin UnitCell
  std::set<xtal::UnitCellCoord> site_neighborhood(
      unsigned int const *linear_orbit_index_begin,
      unsigned int const *linear_orbit_index_end) const {
    std::set<xtal::UnitCellCoord> result;
    auto it = linear_orbit_index_begin;
    for (; it != linear_orbit_index_end; ++it) {
      std::set<xtal::UnitCellCoord> const &tmp = this->site_neighborhood(*it);
      result.insert(tmp.begin(), tmp.end());
    }
    return result;
  }

  /// \brief The weight matrix used for ordering the neighbor list
  const PrimNeighborList::Matrix3Type &weight_matrix() const {
    return m_clex->weight_matrix();
  }

  /// \brief Return sublat_indices
  const std::set<int> &sublat_indices() const {
    return m_clex->sublat_indices();
  }

  /// \brief Return n_sublattices
  size_type n_sublattices() const { return m_clex->n_sublattices(); }

  /// \brief Set the pointer to DoF values
  ///
  /// Notes:
  /// - There is a small overhead that could be avoided by setting this
  ///   manually only when the configuration being calculated is changed, but
  ///   currently for safety this is called by the `calc_X` methods everytime
  ///   and no savings are possible.
  ///
  void set_configdofvalues(ConfigDoFValues const &configdofvalues) const {
    m_clex->set_configdofvalues(configdofvalues);
  }

  /// \brief Calculate basis functions associated with one unit cell,
  ///     normalized by the number of basis functions
  ///
  /// Notes:
  /// - For periodic cluster expansions, this is the contribution of one unit
  ///   cell to the global correlations. The global correlations are the sum of
  ///   this value over all unit cells, normalized by the number of unit cells.
  /// - For local cluster expansions, this is the local correlations.
  ///
  /// \param dof_values ConfigDoFValues, the input configuration
  /// \param nlist_begin Pointer to beginning of the neighbor list. For
  ///     periodic cluster expansions, this is the neighbor list of the unit
  ///     cell. For local cluster expansions, this is the neighbor list of the
  ///     unit cell that the phenomenal cluster is associated with.
  /// \param corr_begin Pointer to beginning of data structure where
  /// correlations are written
  ///
  /// Call using:
  /// \code
  /// // xtal::UnitCellIndexConverter can help get unitcell_index
  /// Index unitcell_index = ...;
  /// SuperNeighborList supercell_neighbor_list = ...;
  ///
  /// long int const *nlist_begin =
  ///     supercell_neighbor_list.sites(unitcell_index);
  /// Eigen::VectorXd corr;
  /// corr.resize(myclexulator.corr_size());
  /// corr.setZero();
  /// myclexulator.calc_global_corr_contribution(
  ///     my_configdof, nlist_begin, corr.data());
  /// \endcode
  ///
  void calc_global_corr_contribution(ConfigDoFValues const &dof_values,
                                     long int const *nlist_begin,
                                     double *corr_begin) const {
    m_clex->set_configdofvalues(dof_values);
    m_clex->set_nlist(nlist_begin);
    m_clex->calc_global_corr_contribution(corr_begin);
  }

  /// \brief Calculate basis functions associated with one unit cell,
  ///     normalized by the number of basis functions,
  ///     writing results to parameter pack
  ///
  /// Notes:
  /// - This overload writes values to the ParamPack, but not to a correlations
  ///   vector
  /// - For periodic cluster expansions, this is the contribution of one unit
  ///   cell to the global correlations. The global correlations are the sum of
  ///   this value over all unit cells, normalized by the number of unit cells.
  /// - For local cluster expansions, this is the local correlations.
  ///
  /// \param dof_values ConfigDoFValues, the input configuration
  /// \param nlist_begin Pointer to beginning of the neighbor list. For
  ///     periodic cluster expansions, this is the neighbor list of the unit
  ///     cell. For local cluster expansions, this is the neighbor list of the
  ///     unit cell that the phenomenal cluster is associated with.
  ///
  /// Call using:
  /// \code
  /// // xtal::UnitCellIndexConverter can help get unitcell_index
  /// Index unitcell_index = ...;
  /// SuperNeighborList supercell_neighbor_list = ...;
  ///
  /// long int const *nlist_begin =
  ///     supercell_neighbor_list.sites(unitcell_index);
  /// myclexulator.calc_global_corr_contribution(my_configdof, nlist_begin);
  /// \endcode
  ///
  void calc_global_corr_contribution(ConfigDoFValues const &dof_values,
                                     long int const *nlist_begin) const {
    m_clex->set_configdofvalues(dof_values);
    m_clex->set_nlist(nlist_begin);
    m_clex->calc_global_corr_contribution();
  }

  /// \brief Calculate basis functions associated with one unit cell,
  ///     normalized by the number of basis functions
  ///
  /// Notes:
  /// - For periodic cluster expansions, this is the contribution of one unit
  ///   cell to the global correlations. The global correlations are the sum of
  ///   this value over all unit cells, normalized by the number of unit cells.
  /// - For local cluster expansions, this is the local correlations.
  ///
  /// \param dof_values ConfigDoFValues, the input configuration
  /// \param nlist_begin Pointer to beginning of the neighbor list. For
  ///     periodic cluster expansions, this is the neighbor list of the unit
  ///     cell. For local cluster expansions, this is the neighbor list of the
  ///     unit cell that the phenomenal cluster is associated with.
  /// \param corr_begin Pointer to beginning of data structure where
  ///     correlations are written
  /// \param corr_ind_begin,corr_ind_end Pointers to range indicating which
  ///     correlations should be calculated
  ///
  /// Call using:
  /// \code
  /// // xtal::UnitCellIndexConverter can help get unitcell_index
  /// Index unitcell_index = ...;
  /// SuperNeighborList supercell_neighbor_list = ...;
  ///
  /// long int const *nlist_begin =
  ///     supercell_neighbor_list.sites(unitcell_index);
  /// Eigen::VectorXd corr;
  /// corr.resize(myclexulator.corr_size());
  /// corr.setZero();
  /// // Get contribution to correlations 0, 2, 4, and 6
  /// std::vector<unsigned int> corr_ind = {0, 2, 4, 6};
  /// unsigned int const *corr_ind_begin = corr_ind.begin();
  /// unsigned int const *corr_ind_end = corr_ind.begin();
  /// myclexulator.calc_restricted_global_corr_contribution(
  ///     my_configdof, nlist_begin, corr.data(),
  ///     corr_ind_begin, corr_ind_end);
  /// \endcode
  ///
  void calc_restricted_global_corr_contribution(
      ConfigDoFValues const &dof_values, long int const *nlist_begin,
      double *corr_begin, size_type const *corr_ind_begin,
      size_type const *corr_ind_end) const {
    m_clex->set_configdofvalues(dof_values);
    m_clex->set_nlist(nlist_begin);
    m_clex->calc_restricted_global_corr_contribution(corr_begin, corr_ind_begin,
                                                     corr_ind_end);
  }

  /// \brief Calculate point correlations about one site
  ///
  /// \param dof_values ConfigDoFValues, the input configuration
  /// \param nlist_begin Pointer to beginning of the neighbor list. For
  ///     periodic cluster expansions, this is the neighbor list of the unit
  ///     cell containing the site. For local cluster expansions, this is the
  ///     neighbor list of the unit cell that the phenomenal cluster is
  ///     associated with.
  /// \param neighbor_ind Index in the neighbor list of the site about which to
  ///     calculate correlations. This can be obtained from the linear site
  ///     index and the supercell neighbor list using:
  ///         `supercell_neighbor_list->neighbor_index(linear_site_index)`,
  ///     which have value -1 if the site is not in the neighbor list.
  /// \param corr_begin Pointer to beginning of data structure where
  ///     correlations are written
  ///
  /// Call using:
  /// \code
  /// // xtal::UnitCellCoordIndexConverter can help get linear_site_index
  /// Index linear_site_index = ...;
  /// SuperNeighborList supercell_neighbor_list = ...;
  ///
  /// Index unitcell_index =
  ///     supercell_neighbor_list.unitcell_index(linear_site_index);
  /// long int const *nlist_begin =
  ///     supercell_neighbor_list.sites(unitcell_index);
  /// int neighbor_ind =
  ///     supercell_neighbor_list.neighbor_index(linear_site_index);
  /// Eigen::VectorXd corr;
  /// corr.resize(myclexulator.corr_size());
  /// corr.setZero();
  /// myclexulator.calc_point_corr(
  ///     my_configdof, nlist_begin, neighbor_ind, corr.data());
  /// \endcode
  ///
  void calc_point_corr(ConfigDoFValues const &dof_values,
                       long int const *nlist_begin, int neighbor_ind,
                       double *corr_begin) const {
    m_clex->set_configdofvalues(dof_values);
    m_clex->set_nlist(nlist_begin);
    m_clex->calc_point_corr(neighbor_ind, corr_begin);
  }

  /// \brief Calculate select point correlations one site
  ///
  /// \param dof_values ConfigDoFValues, the input configuration
  /// \param nlist_begin Pointer to beginning of the neighbor list. For
  ///     periodic cluster expansions, this is the neighbor list of the unit
  ///     cell containing the site. For local cluster expansions, this is the
  ///     neighbor list of the unit cell that the phenomenal cluster is
  ///     associated with.
  /// \param neighbor_ind Index in the neighbor list of the site about which to
  ///     calculate correlations. This can be obtained from the linear site
  ///     index and the supercell neighbor list using:
  ///         `supercell_neighbor_list->neighbor_index(linear_site_index)`,
  ///     which have value -1 if the site is not in the neighbor list.
  /// \param corr_begin Pointer to beginning of data structure where
  ///     correlations are written
  /// \param corr_ind_begin,corr_ind_end Pointers to range indicating which
  ///     correlations should be calculated
  ///
  /// Call using:
  /// \code
  /// // xtal::UnitCellCoordIndexConverter can help get linear_site_index
  /// Index linear_site_index = ...;
  /// SuperNeighborList supercell_neighbor_list = ...;
  ///
  /// Index unitcell_index =
  ///     supercell_neighbor_list.unitcell_index(linear_site_index);
  /// long int const *nlist_begin =
  ///     supercell_neighbor_list.sites(unitcell_index);
  /// int neighbor_ind =
  ///     supercell_neighbor_list.neighbor_index(linear_site_index);
  /// Eigen::VectorXd corr;
  /// corr.resize(myclexulator.corr_size());
  /// corr.setZero();
  /// // Get contribution to correlations 0, 2, 4, and 6
  /// std::vector<unsigned int> corr_ind = {0, 2, 4, 6};
  /// unsigned int const *corr_ind_begin = corr_ind.begin();
  /// unsigned int const *corr_ind_end = corr_ind.begin();
  /// myclexulator.calc_restricted_point_corr(
  ///     my_configdof, nlist_begin, neighbor_ind, corr.data(),
  ///     corr_ind_begin, corr_ind_end);
  /// \endcode
  ///
  void calc_restricted_point_corr(ConfigDoFValues const &dof_values,
                                  long int const *nlist_begin, int neighbor_ind,
                                  double *corr_begin,
                                  size_type const *corr_ind_begin,
                                  size_type const *corr_ind_end) const {
    m_clex->set_configdofvalues(dof_values);
    m_clex->set_nlist(nlist_begin);
    m_clex->calc_restricted_point_corr(neighbor_ind, corr_begin, corr_ind_begin,
                                       corr_ind_end);
  }

  /// \brief Calculate the change in point correlations due to changing an
  /// occupant
  ///
  /// \param dof_values ConfigDoFValues, the input configuration
  /// \param nlist_begin Pointer to beginning of the neighbor list. For
  ///     periodic cluster expansions, this is the neighbor list of the unit
  ///     cell containing the site. For local cluster expansions, this is the
  ///     neighbor list of the unit cell that the phenomenal cluster is
  ///     associated with.
  /// \param neighbor_ind Index in the neighbor list of the site about which to
  ///     calculate correlations. This can be obtained from the linear site
  ///     index and the supercell neighbor list using:
  ///         `supercell_neighbor_list->neighbor_index(linear_site_index)`,
  ///     which have value -1 if the site is not in the neighbor list.
  /// \param occ_i,occ_f Initial and final occupant variable
  /// \param corr_begin Pointer to beginning of data structure where difference
  ///     in correlations are written
  ///
  /// Call using:
  /// \code
  /// // xtal::UnitCellCoordIndexConverter can help get linear_site_index
  /// Index linear_site_index = ...;
  /// SuperNeighborList supercell_neighbor_list = ...;
  ///
  /// Index unitcell_index =
  ///     supercell_neighbor_list.unitcell_index(linear_site_index);
  /// long int const *nlist_begin =
  ///     supercell_neighbor_list.sites(unitcell_index);
  /// int neighbor_ind =
  ///     supercell_neighbor_list.neighbor_index(linear_site_index);
  /// Eigen::VectorXd corr;
  /// corr.resize(myclexulator.corr_size());
  /// corr.setZero();
  /// myclexulator.calc_delta_point_corr(
  ///     my_configdof, nlist_begin, neighbor_ind, occ_i, occ_f, corr.data());
  /// \endcode
  ///
  void calc_delta_point_corr(ConfigDoFValues const &dof_values,
                             long int const *nlist_begin, int neighbor_ind,
                             int occ_i, int occ_f, double *corr_begin) const {
    m_clex->set_configdofvalues(dof_values);
    m_clex->set_nlist(nlist_begin);
    m_clex->calc_delta_point_corr(neighbor_ind, occ_i, occ_f, corr_begin);
  }

  /// \brief Similar to calc_delta_point_corr, using
  ///     ConfigDoFValues::multi_occupation
  void calc_multi_occ_delta_point_corr(ConfigDoFValues const &dof_values,
                                       long int const *nlist_begin,
                                       int neighbor_ind, int discrete_dof_index,
                                       int occ_i, int occ_f,
                                       double *corr_begin) const {
    m_clex->set_configdofvalues(dof_values);
    m_clex->set_nlist(nlist_begin);
    m_clex->calc_multi_occ_delta_point_corr(neighbor_ind, discrete_dof_index,
                                            occ_i, occ_f, corr_begin);
  }

  /// \brief Calculate the change in select point correlations due to changing
  /// an occupant
  ///
  /// \param dof_values ConfigDoFValues, the input configuration
  /// \param nlist_begin Pointer to beginning of the neighbor list. For
  ///     periodic cluster expansions, this is the neighbor list of the unit
  ///     cell containing the site. For local cluster expansions, this is the
  ///     neighbor list of the unit cell that the phenomenal cluster is
  ///     associated with.
  /// \param neighbor_ind Index in the neighbor list of the site about which to
  ///     calculate correlations. This can be obtained from the linear site
  ///     index and the supercell neighbor list using:
  ///         `supercell_neighbor_list->neighbor_index(linear_site_index)`,
  ///     which have value -1 if the site is not in the neighbor list.
  /// \param occ_i,occ_f Initial and final occupant variable
  /// \param corr_begin Pointer to beginning of data structure where difference
  ///     in correlations are written
  /// \param corr_ind_begin,corr_ind_end Pointers to range indicating which
  ///     correlations should be calculated
  ///
  /// Call using:
  /// \code
  /// // xtal::UnitCellCoordIndexConverter can help get linear_site_index
  /// Index linear_site_index = ...;
  /// SuperNeighborList supercell_neighbor_list = ...;
  ///
  /// Index unitcell_index =
  ///     supercell_neighbor_list.unitcell_index(linear_site_index);
  /// long int const *nlist_begin =
  ///     supercell_neighbor_list.sites(unitcell_index);
  /// int neighbor_ind =
  ///     supercell_neighbor_list.neighbor_index(linear_site_index);
  /// Eigen::VectorXd corr;
  /// corr.resize(myclexulator.corr_size());
  /// corr.setZero();
  /// // Get contribution to correlations 0, 2, 4, and 6
  /// std::vector<unsigned int> corr_ind = {0, 2, 4, 6};
  /// unsigned int const *corr_ind_begin = corr_ind.begin();
  /// unsigned int const *corr_ind_end = corr_ind.begin();
  /// myclexulator.calc_restricted_delta_point_corr(
  ///     my_configdof, nlist_begin, neighbor_ind, occ_i, occ_f, corr.data(),
  ///     corr_ind_begin, corr_ind_end);
  /// \endcode
  ///
  void calc_restricted_delta_point_corr(ConfigDoFValues const &dof_values,
                                        long int const *nlist_begin,
                                        int neighbor_ind, int occ_i, int occ_f,
                                        double *corr_begin,
                                        size_type const *corr_ind_begin,
                                        size_type const *corr_ind_end) const {
    m_clex->set_configdofvalues(dof_values);
    m_clex->set_nlist(nlist_begin);
    m_clex->calc_restricted_delta_point_corr(
        neighbor_ind, occ_i, occ_f, corr_begin, corr_ind_begin, corr_ind_end);
  }

  /// \brief Similar to calc_restricted_delta_point_corr, using
  ///     ConfigDoFValues::multi_occupation
  void calc_multi_occ_restricted_delta_point_corr(
      ConfigDoFValues const &dof_values, long int const *nlist_begin,
      int neighbor_ind, int discrete_dof_index, int occ_i, int occ_f,
      double *corr_begin, size_type const *corr_ind_begin,
      size_type const *corr_ind_end) const {
    m_clex->set_configdofvalues(dof_values);
    m_clex->set_nlist(nlist_begin);
    m_clex->calc_multi_occ_restricted_delta_point_corr(
        neighbor_ind, discrete_dof_index, occ_i, occ_f, corr_begin,
        corr_ind_begin, corr_ind_end);
  }

 private:
  std::string m_name;
  notstd::cloneable_ptr<clexulator::BaseClexulator> m_clex;
  std::shared_ptr<RuntimeLibrary> m_lib;
};

struct LocalClexulatorWrapper {
  LocalClexulatorWrapper() {}
  LocalClexulatorWrapper(
      std::shared_ptr<std::vector<clexulator::Clexulator>> _local_clexulator)
      : local_clexulator(_local_clexulator) {}

  std::shared_ptr<std::vector<clexulator::Clexulator>> local_clexulator;
};

/// \brief Default log for compilation info output
///
/// Initially this writes to `std::cout`, but it can be reset.
///
/// \relates Log
inline Log &compile_log() {
  static Log log{std::cout};
  return log;
}

/// \brief Clexulator factory function
Clexulator make_clexulator(std::string name, fs::path dirpath,
                           std::shared_ptr<PrimNeighborList> &nlist,
                           std::string compile_options, std::string so_options);

/// \brief Local Clexulator factory function
std::vector<Clexulator> make_local_clexulator(
    std::string clexulator_name, fs::path dirpath,
    std::shared_ptr<PrimNeighborList> &nlist, std::string compile_options,
    std::string so_options);

}  // namespace clexulator
}  // namespace CASM

#endif
