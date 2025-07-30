#include <cstddef>

#include "casm/clexulator/BaseClexulator.hh"
#include "casm/clexulator/BasicClexParamPack.hh"
#include "casm/global/eigen.hh"

/****** PROJECT SPECIFICATIONS ******

         ****** prim.json ******

{
  "basis" : [
    {
      "coordinate" : [ 0.000000000000, 0.000000000000, 0.000000000000 ],
      "occupants" : [ "Zr" ]
    },
    {
      "coordinate" : [ 0.666666666667, 0.333333333333, 0.500000000000 ],
      "occupants" : [ "Zr" ]
    },
    {
      "coordinate" : [ 0.333333333333, 0.666666666667, 0.250000000000 ],
      "occupants" : [ "Va", "O" ]
    },
    {
      "coordinate" : [ 0.333333333333, 0.666666666667, 0.750000000000 ],
      "occupants" : [ "Va", "O" ]
    }
  ],
  "coordinate_mode" : "Fractional",
  "lattice_vectors" : [
    [ 3.233986860000, 0.000000000000, 0.000000000000 ],
    [ -1.616993430000, 2.800714770000, 0.000000000000 ],
    [ 0.000000000000, 0.000000000000, 5.168678340000 ]
  ],
  "title" : "ZrO"
}

        ****** bspecs.json ******

{
  "basis_function_specs" : {
    "dof_specs" : {
      "occ" : {
        "site_basis_functions" : "OCCUPATION"
      }
    },
    "dofs" : [ "occ" ],
    "global_max_poly_order" : -1,
    "param_pack_type" : "DEFAULT"
  },
  "cluster_specs" : {
    "method" : "periodic_max_length",
    "params" : {
      "generating_group" : [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
15, 16, 17, 18, 19, 20, 21, 22, 23 ], "orbit_branch_specs" : { "0" : {
          "max_length" : 0.000000000000
        },
        "1" : {
          "max_length" : 0.000000000000
        },
        "2" : {
          "max_length" : 6.010000000000
        },
        "3" : {
          "max_length" : 4.140000000000
        },
        "4" : {
          "max_length" : 4.140000000000
        }
      }
    }
  }
}

**/

/// \brief Returns a clexulator::BaseClexulator* owning a
/// OccClexulatorZrOTest_Clexulator_default
extern "C" CASM::clexulator::BaseClexulator *
make_OccClexulatorZrOTest_Clexulator_default();

namespace CASM {
namespace clexulator {

/****** GENERATED CLEXPARAMPACK DEFINITION ******/

typedef BasicClexParamPack ParamPack;

/****** GENERATED CLEXULATOR DEFINITION ******/

class OccClexulatorZrOTest_Clexulator_default
    : public clexulator::BaseClexulator {
 public:
  OccClexulatorZrOTest_Clexulator_default();

  ~OccClexulatorZrOTest_Clexulator_default();

  ClexParamPack const &param_pack() const override { return m_params; }

  ClexParamPack &param_pack() override { return m_params; }

  template <typename Scalar>
  Scalar eval_bfunc_0_0() const;

  template <typename Scalar>
  Scalar eval_bfunc_1_0() const;

  template <typename Scalar>
  Scalar site_eval_bfunc_1_0_at_0() const;
  template <typename Scalar>
  Scalar site_eval_bfunc_1_0_at_1() const;

  template <typename Scalar>
  Scalar site_deval_bfunc_1_0_at_0(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar site_deval_bfunc_1_0_at_1(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar eval_bfunc_2_0() const;

  template <typename Scalar>
  Scalar site_eval_bfunc_2_0_at_0() const;
  template <typename Scalar>
  Scalar site_eval_bfunc_2_0_at_1() const;

  template <typename Scalar>
  Scalar site_deval_bfunc_2_0_at_0(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar site_deval_bfunc_2_0_at_1(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar eval_bfunc_3_0() const;

  template <typename Scalar>
  Scalar site_eval_bfunc_3_0_at_0() const;
  template <typename Scalar>
  Scalar site_eval_bfunc_3_0_at_1() const;

  template <typename Scalar>
  Scalar site_deval_bfunc_3_0_at_0(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar site_deval_bfunc_3_0_at_1(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar eval_bfunc_4_0() const;

  template <typename Scalar>
  Scalar site_eval_bfunc_4_0_at_0() const;
  template <typename Scalar>
  Scalar site_eval_bfunc_4_0_at_1() const;

  template <typename Scalar>
  Scalar site_deval_bfunc_4_0_at_0(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar site_deval_bfunc_4_0_at_1(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar eval_bfunc_5_0() const;

  template <typename Scalar>
  Scalar site_eval_bfunc_5_0_at_0() const;
  template <typename Scalar>
  Scalar site_eval_bfunc_5_0_at_1() const;

  template <typename Scalar>
  Scalar site_deval_bfunc_5_0_at_0(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar site_deval_bfunc_5_0_at_1(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar eval_bfunc_6_0() const;

  template <typename Scalar>
  Scalar site_eval_bfunc_6_0_at_0() const;
  template <typename Scalar>
  Scalar site_eval_bfunc_6_0_at_1() const;

  template <typename Scalar>
  Scalar site_deval_bfunc_6_0_at_0(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar site_deval_bfunc_6_0_at_1(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar eval_bfunc_7_0() const;

  template <typename Scalar>
  Scalar site_eval_bfunc_7_0_at_0() const;
  template <typename Scalar>
  Scalar site_eval_bfunc_7_0_at_1() const;

  template <typename Scalar>
  Scalar site_deval_bfunc_7_0_at_0(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar site_deval_bfunc_7_0_at_1(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar eval_bfunc_8_0() const;

  template <typename Scalar>
  Scalar site_eval_bfunc_8_0_at_0() const;
  template <typename Scalar>
  Scalar site_eval_bfunc_8_0_at_1() const;

  template <typename Scalar>
  Scalar site_deval_bfunc_8_0_at_0(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar site_deval_bfunc_8_0_at_1(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar eval_bfunc_9_0() const;

  template <typename Scalar>
  Scalar site_eval_bfunc_9_0_at_0() const;
  template <typename Scalar>
  Scalar site_eval_bfunc_9_0_at_1() const;

  template <typename Scalar>
  Scalar site_deval_bfunc_9_0_at_0(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar site_deval_bfunc_9_0_at_1(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar eval_bfunc_10_0() const;

  template <typename Scalar>
  Scalar site_eval_bfunc_10_0_at_0() const;
  template <typename Scalar>
  Scalar site_eval_bfunc_10_0_at_1() const;

  template <typename Scalar>
  Scalar site_deval_bfunc_10_0_at_0(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar site_deval_bfunc_10_0_at_1(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar eval_bfunc_11_0() const;

  template <typename Scalar>
  Scalar site_eval_bfunc_11_0_at_0() const;
  template <typename Scalar>
  Scalar site_eval_bfunc_11_0_at_1() const;

  template <typename Scalar>
  Scalar site_deval_bfunc_11_0_at_0(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar site_deval_bfunc_11_0_at_1(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar eval_bfunc_12_0() const;

  template <typename Scalar>
  Scalar site_eval_bfunc_12_0_at_0() const;
  template <typename Scalar>
  Scalar site_eval_bfunc_12_0_at_1() const;

  template <typename Scalar>
  Scalar site_deval_bfunc_12_0_at_0(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar site_deval_bfunc_12_0_at_1(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar eval_bfunc_13_0() const;

  template <typename Scalar>
  Scalar site_eval_bfunc_13_0_at_0() const;
  template <typename Scalar>
  Scalar site_eval_bfunc_13_0_at_1() const;

  template <typename Scalar>
  Scalar site_deval_bfunc_13_0_at_0(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar site_deval_bfunc_13_0_at_1(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar eval_bfunc_14_0() const;

  template <typename Scalar>
  Scalar site_eval_bfunc_14_0_at_0() const;
  template <typename Scalar>
  Scalar site_eval_bfunc_14_0_at_1() const;

  template <typename Scalar>
  Scalar site_deval_bfunc_14_0_at_0(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar site_deval_bfunc_14_0_at_1(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar eval_bfunc_15_0() const;

  template <typename Scalar>
  Scalar site_eval_bfunc_15_0_at_0() const;
  template <typename Scalar>
  Scalar site_eval_bfunc_15_0_at_1() const;

  template <typename Scalar>
  Scalar site_deval_bfunc_15_0_at_0(int occ_i, int occ_f) const;

  template <typename Scalar>
  Scalar site_deval_bfunc_15_0_at_1(int occ_i, int occ_f) const;

 private:
  // ParamPack object, which stores temporary data for calculations
  mutable ParamPack m_params;

  // typedef for method pointers of scalar type double
  typedef double (
      OccClexulatorZrOTest_Clexulator_default::*BasisFuncPtr_0)() const;

  // typedef for method pointers
  typedef double (
      OccClexulatorZrOTest_Clexulator_default::*DeltaBasisFuncPtr_0)(int,
                                                                     int) const;

  // array of pointers to member functions for calculating basis functions of
  // scalar type double
  BasisFuncPtr_0 m_orbit_func_table_0[16];

  // array of pointers to member functions for calculating flower functions of
  // scalar type double
  BasisFuncPtr_0 m_flower_func_table_0[2][16];

  // array of pointers to member functions for calculating DELTA flower
  // functions of scalar type double
  DeltaBasisFuncPtr_0 m_delta_func_table_0[2][16];

  // Occupation Function tables for basis sites in asymmetric unit 1:
  //   - basis site 2:
  double m_occ_func_2_0[2];

  //   - basis site 3:
  double m_occ_func_3_0[2];

  // ClexParamPack allocation for evaluated correlations
  ParamPack::Key m_corr_param_key;
  // ClexParamPack allocation for DoF occ
  ParamPack::Key m_occ_site_func_param_key;

  /// \brief Clone the OccClexulatorZrOTest_Clexulator_default
  BaseClexulator *_clone() const override {
    return new OccClexulatorZrOTest_Clexulator_default(*this);
  }

  /// \brief Calculate contribution to global correlations from one unit cell
  /// Result is recorded in ClexParamPack
  void _calc_global_corr_contribution() const override;

  /// \brief Calculate contribution to global correlations from one unit cell
  /// /// Result is recorded in double array starting at corr_begin
  void _calc_global_corr_contribution(double *corr_begin) const override;

  /// \brief Calculate contribution to select global correlations from one unit
  /// cell into ClexParamPack Result is recorded in ClexParamPack
  void _calc_restricted_global_corr_contribution(
      size_type const *ind_list_begin,
      size_type const *ind_list_end) const override;

  /// \brief Calculate contribution to select global correlations from one unit
  /// cell Result is recorded in double array starting at corr_begin
  void _calc_restricted_global_corr_contribution(
      double *corr_begin, size_type const *ind_list_begin,
      size_type const *ind_list_end) const override;

  /// \brief Calculate point correlations about neighbor site 'nlist_ind'
  /// For global clexulators, 'nlist_ind' only ranges over sites in the cell
  /// For local clexulators, 'nlist_ind' ranges over all sites in the
  /// neighborhood Result is recorded in ClexParamPack
  void _calc_point_corr(int nlist_ind) const override;

  /// \brief Calculate point correlations about neighbor site 'nlist_ind'
  /// For global clexulators, 'nlist_ind' only ranges over sites in the cell
  /// For local clexulators, 'nlist_ind' ranges over all sites in the
  /// neighborhood Result is recorded in double array starting at corr_begin
  void _calc_point_corr(int nlist_ind, double *corr_begin) const override;

  /// \brief Calculate select point correlations about neighbor site 'nlist_ind'
  /// For global clexulators, 'nlist_ind' only ranges over sites in the cell
  /// For local clexulators, 'nlist_ind' ranges over all sites in the
  /// neighborhood Result is recorded in ClexParamPack
  void _calc_restricted_point_corr(
      int nlist_ind, size_type const *ind_list_begin,
      size_type const *ind_list_end) const override;

  /// \brief Calculate select point correlations about neighbor site 'nlist_ind'
  /// For global clexulators, 'nlist_ind' only ranges over sites in the cell
  /// For local clexulators, 'nlist_ind' ranges over all sites in the
  /// neighborhood Result is recorded in double array starting at corr_begin
  void _calc_restricted_point_corr(
      int nlist_ind, double *corr_begin, size_type const *ind_list_begin,
      size_type const *ind_list_end) const override;

  /// \brief Calculate the change in point correlations due to changing an
  /// occupant at neighbor site 'nlist_ind' For global clexulators, 'nlist_ind'
  /// only ranges over sites in the cell For local clexulators, 'nlist_ind'
  /// ranges over all sites in the neighborhood Result is recorded in
  /// ClexParamPack
  void _calc_delta_point_corr(int nlist_ind, int occ_i,
                              int occ_f) const override;

  /// \brief Calculate the change in point correlations due to changing an
  /// occupant at neighbor site 'nlist_ind' For global clexulators, 'nlist_ind'
  /// only ranges over sites in the cell For local clexulators, 'nlist_ind'
  /// ranges over all sites in the neighborhood Result is recorded in double
  /// array starting at corr_begin
  void _calc_delta_point_corr(int nlist_ind, int occ_i, int occ_f,
                              double *corr_begin) const override;

  /// \brief Calculate the change in select point correlations due to changing
  /// an occupant at neighbor site 'nlist_ind' For global clexulators,
  /// 'nlist_ind' only ranges over sites in the cell For local clexulators,
  /// 'nlist_ind' ranges over all sites in the neighborhood Result is recorded
  /// in ClexParamPack
  void _calc_restricted_delta_point_corr(
      int nlist_ind, int occ_i, int occ_f, size_type const *ind_list_begin,
      size_type const *ind_list_end) const override;

  /// \brief Calculate the change in select point correlations due to changing
  /// an occupant at neighbor site 'nlist_ind' For global clexulators,
  /// 'nlist_ind' only ranges over sites in the cell For local clexulators,
  /// 'nlist_ind' ranges over all sites in the neighborhood Result is recorded
  /// in double array starting at corr_begin
  void _calc_restricted_delta_point_corr(
      int nlist_ind, int occ_i, int occ_f, double *corr_begin,
      size_type const *ind_list_begin,
      size_type const *ind_list_end) const override;

  template <typename Scalar>
  void _global_prepare() const;

  template <typename Scalar>
  void _point_prepare(int nlist_ind) const;

  // Occupation Function evaluators and accessors for basis site 2:
  double const &eval_occ_func_2_0(const int &nlist_ind) const {
    return m_occ_func_2_0[_occ(nlist_ind)];
  }

  double const &occ_func_2_0(const int &nlist_ind) const {
    return m_params.read(m_occ_site_func_param_key, 0, nlist_ind);
  }

  // Occupation Function evaluators and accessors for basis site 3:
  double const &eval_occ_func_3_0(const int &nlist_ind) const {
    return m_occ_func_3_0[_occ(nlist_ind)];
  }

  double const &occ_func_3_0(const int &nlist_ind) const {
    return m_params.read(m_occ_site_func_param_key, 0, nlist_ind);
  }

  // default functions for basis function evaluation
  template <typename Scalar>
  Scalar zero_func() const {
    return Scalar(0.0);
  }

  template <typename Scalar>
  Scalar zero_func(int, int) const {
    return Scalar(0.0);
  }
};

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OccClexulatorZrOTest_Clexulator_default::
    OccClexulatorZrOTest_Clexulator_default()
    : BaseClexulator(53, 16, 2) {
  m_occ_func_2_0[0] = -0.0000000000, m_occ_func_2_0[1] = 1.0000000000;

  m_occ_func_3_0[0] = -0.0000000000, m_occ_func_3_0[1] = 1.0000000000;

  m_occ_site_func_param_key = m_params.allocate("occ_site_func", 1, 53, true);

  m_corr_param_key = m_params.allocate("corr", corr_size(), 1, false);

  m_orbit_func_table_0[0] =
      &OccClexulatorZrOTest_Clexulator_default::eval_bfunc_0_0<double>;
  m_orbit_func_table_0[1] =
      &OccClexulatorZrOTest_Clexulator_default::eval_bfunc_1_0<double>;
  m_orbit_func_table_0[2] =
      &OccClexulatorZrOTest_Clexulator_default::eval_bfunc_2_0<double>;
  m_orbit_func_table_0[3] =
      &OccClexulatorZrOTest_Clexulator_default::eval_bfunc_3_0<double>;
  m_orbit_func_table_0[4] =
      &OccClexulatorZrOTest_Clexulator_default::eval_bfunc_4_0<double>;
  m_orbit_func_table_0[5] =
      &OccClexulatorZrOTest_Clexulator_default::eval_bfunc_5_0<double>;
  m_orbit_func_table_0[6] =
      &OccClexulatorZrOTest_Clexulator_default::eval_bfunc_6_0<double>;
  m_orbit_func_table_0[7] =
      &OccClexulatorZrOTest_Clexulator_default::eval_bfunc_7_0<double>;
  m_orbit_func_table_0[8] =
      &OccClexulatorZrOTest_Clexulator_default::eval_bfunc_8_0<double>;
  m_orbit_func_table_0[9] =
      &OccClexulatorZrOTest_Clexulator_default::eval_bfunc_9_0<double>;
  m_orbit_func_table_0[10] =
      &OccClexulatorZrOTest_Clexulator_default::eval_bfunc_10_0<double>;
  m_orbit_func_table_0[11] =
      &OccClexulatorZrOTest_Clexulator_default::eval_bfunc_11_0<double>;
  m_orbit_func_table_0[12] =
      &OccClexulatorZrOTest_Clexulator_default::eval_bfunc_12_0<double>;
  m_orbit_func_table_0[13] =
      &OccClexulatorZrOTest_Clexulator_default::eval_bfunc_13_0<double>;
  m_orbit_func_table_0[14] =
      &OccClexulatorZrOTest_Clexulator_default::eval_bfunc_14_0<double>;
  m_orbit_func_table_0[15] =
      &OccClexulatorZrOTest_Clexulator_default::eval_bfunc_15_0<double>;

  m_flower_func_table_0[0][0] =
      &OccClexulatorZrOTest_Clexulator_default::zero_func<double>;
  m_flower_func_table_0[0][1] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_1_0_at_0<
          double>;
  m_flower_func_table_0[0][2] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_2_0_at_0<
          double>;
  m_flower_func_table_0[0][3] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_3_0_at_0<
          double>;
  m_flower_func_table_0[0][4] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_4_0_at_0<
          double>;
  m_flower_func_table_0[0][5] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_5_0_at_0<
          double>;
  m_flower_func_table_0[0][6] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_6_0_at_0<
          double>;
  m_flower_func_table_0[0][7] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_7_0_at_0<
          double>;
  m_flower_func_table_0[0][8] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_8_0_at_0<
          double>;
  m_flower_func_table_0[0][9] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_9_0_at_0<
          double>;
  m_flower_func_table_0[0][10] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_10_0_at_0<
          double>;
  m_flower_func_table_0[0][11] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_11_0_at_0<
          double>;
  m_flower_func_table_0[0][12] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_12_0_at_0<
          double>;
  m_flower_func_table_0[0][13] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_13_0_at_0<
          double>;
  m_flower_func_table_0[0][14] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_14_0_at_0<
          double>;
  m_flower_func_table_0[0][15] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_15_0_at_0<
          double>;

  m_flower_func_table_0[1][0] =
      &OccClexulatorZrOTest_Clexulator_default::zero_func<double>;
  m_flower_func_table_0[1][1] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_1_0_at_1<
          double>;
  m_flower_func_table_0[1][2] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_2_0_at_1<
          double>;
  m_flower_func_table_0[1][3] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_3_0_at_1<
          double>;
  m_flower_func_table_0[1][4] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_4_0_at_1<
          double>;
  m_flower_func_table_0[1][5] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_5_0_at_1<
          double>;
  m_flower_func_table_0[1][6] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_6_0_at_1<
          double>;
  m_flower_func_table_0[1][7] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_7_0_at_1<
          double>;
  m_flower_func_table_0[1][8] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_8_0_at_1<
          double>;
  m_flower_func_table_0[1][9] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_9_0_at_1<
          double>;
  m_flower_func_table_0[1][10] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_10_0_at_1<
          double>;
  m_flower_func_table_0[1][11] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_11_0_at_1<
          double>;
  m_flower_func_table_0[1][12] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_12_0_at_1<
          double>;
  m_flower_func_table_0[1][13] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_13_0_at_1<
          double>;
  m_flower_func_table_0[1][14] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_14_0_at_1<
          double>;
  m_flower_func_table_0[1][15] =
      &OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_15_0_at_1<
          double>;

  m_delta_func_table_0[0][0] =
      &OccClexulatorZrOTest_Clexulator_default::zero_func<double>;
  m_delta_func_table_0[0][1] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_1_0_at_0<
          double>;
  m_delta_func_table_0[0][2] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_2_0_at_0<
          double>;
  m_delta_func_table_0[0][3] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_3_0_at_0<
          double>;
  m_delta_func_table_0[0][4] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_4_0_at_0<
          double>;
  m_delta_func_table_0[0][5] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_5_0_at_0<
          double>;
  m_delta_func_table_0[0][6] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_6_0_at_0<
          double>;
  m_delta_func_table_0[0][7] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_7_0_at_0<
          double>;
  m_delta_func_table_0[0][8] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_8_0_at_0<
          double>;
  m_delta_func_table_0[0][9] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_9_0_at_0<
          double>;
  m_delta_func_table_0[0][10] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_10_0_at_0<
          double>;
  m_delta_func_table_0[0][11] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_11_0_at_0<
          double>;
  m_delta_func_table_0[0][12] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_12_0_at_0<
          double>;
  m_delta_func_table_0[0][13] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_13_0_at_0<
          double>;
  m_delta_func_table_0[0][14] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_14_0_at_0<
          double>;
  m_delta_func_table_0[0][15] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_15_0_at_0<
          double>;

  m_delta_func_table_0[1][0] =
      &OccClexulatorZrOTest_Clexulator_default::zero_func<double>;
  m_delta_func_table_0[1][1] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_1_0_at_1<
          double>;
  m_delta_func_table_0[1][2] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_2_0_at_1<
          double>;
  m_delta_func_table_0[1][3] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_3_0_at_1<
          double>;
  m_delta_func_table_0[1][4] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_4_0_at_1<
          double>;
  m_delta_func_table_0[1][5] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_5_0_at_1<
          double>;
  m_delta_func_table_0[1][6] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_6_0_at_1<
          double>;
  m_delta_func_table_0[1][7] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_7_0_at_1<
          double>;
  m_delta_func_table_0[1][8] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_8_0_at_1<
          double>;
  m_delta_func_table_0[1][9] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_9_0_at_1<
          double>;
  m_delta_func_table_0[1][10] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_10_0_at_1<
          double>;
  m_delta_func_table_0[1][11] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_11_0_at_1<
          double>;
  m_delta_func_table_0[1][12] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_12_0_at_1<
          double>;
  m_delta_func_table_0[1][13] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_13_0_at_1<
          double>;
  m_delta_func_table_0[1][14] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_14_0_at_1<
          double>;
  m_delta_func_table_0[1][15] =
      &OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_15_0_at_1<
          double>;

  m_weight_matrix.row(0) << 2, -1, 0;
  m_weight_matrix.row(1) << -1, 2, 0;
  m_weight_matrix.row(2) << 0, 0, 5;

  m_sublat_indices = std::set<int>{2, 3};

  m_n_sublattices = 4;

  m_neighborhood = std::set<xtal::UnitCell>{
      xtal::UnitCell(-2, -1, 0),  xtal::UnitCell(-1, -2, 0),
      xtal::UnitCell(-1, -1, -1), xtal::UnitCell(-1, -1, 0),
      xtal::UnitCell(-1, -1, 1),  xtal::UnitCell(-1, 0, -1),
      xtal::UnitCell(-1, 0, 0),   xtal::UnitCell(-1, 0, 1),
      xtal::UnitCell(-1, 1, 0),   xtal::UnitCell(0, -1, -1),
      xtal::UnitCell(0, -1, 0),   xtal::UnitCell(0, -1, 1),
      xtal::UnitCell(0, 0, -1),   xtal::UnitCell(0, 0, 0),
      xtal::UnitCell(0, 0, 1),    xtal::UnitCell(0, 1, -1),
      xtal::UnitCell(0, 1, 0),    xtal::UnitCell(0, 1, 1),
      xtal::UnitCell(1, -1, 0),   xtal::UnitCell(1, 0, -1),
      xtal::UnitCell(1, 0, 0),    xtal::UnitCell(1, 0, 1),
      xtal::UnitCell(1, 1, -1),   xtal::UnitCell(1, 1, 0),
      xtal::UnitCell(1, 1, 1),    xtal::UnitCell(1, 2, 0),
      xtal::UnitCell(2, 1, 0)};

  m_orbit_neighborhood.resize(corr_size());
  m_orbit_site_neighborhood.resize(corr_size());
  m_orbit_neighborhood[1] = std::set<xtal::UnitCell>{xtal::UnitCell(0, 0, 0)};

  m_orbit_site_neighborhood[1] = std::set<xtal::UnitCellCoord>{
      xtal::UnitCellCoord(2, 0, 0, 0), xtal::UnitCellCoord(3, 0, 0, 0)};

  m_orbit_neighborhood[2] = std::set<xtal::UnitCell>{xtal::UnitCell(0, 0, -1),
                                                     xtal::UnitCell(0, 0, 0),
                                                     xtal::UnitCell(0, 0, 1)};

  m_orbit_site_neighborhood[2] = std::set<xtal::UnitCellCoord>{
      xtal::UnitCellCoord(3, 0, 0, -1), xtal::UnitCellCoord(2, 0, 0, 0),
      xtal::UnitCellCoord(3, 0, 0, 0), xtal::UnitCellCoord(2, 0, 0, 1)};

  m_orbit_neighborhood[3] = std::set<xtal::UnitCell>{
      xtal::UnitCell(-1, -1, 0), xtal::UnitCell(-1, 0, 0),
      xtal::UnitCell(0, -1, 0),  xtal::UnitCell(0, 0, 0),
      xtal::UnitCell(0, 1, 0),   xtal::UnitCell(1, 0, 0),
      xtal::UnitCell(1, 1, 0)};

  m_orbit_site_neighborhood[3] = std::set<xtal::UnitCellCoord>{
      xtal::UnitCellCoord(2, -1, -1, 0), xtal::UnitCellCoord(3, -1, -1, 0),
      xtal::UnitCellCoord(2, -1, 0, 0),  xtal::UnitCellCoord(3, -1, 0, 0),
      xtal::UnitCellCoord(2, 0, -1, 0),  xtal::UnitCellCoord(3, 0, -1, 0),
      xtal::UnitCellCoord(2, 0, 0, 0),   xtal::UnitCellCoord(3, 0, 0, 0),
      xtal::UnitCellCoord(2, 0, 1, 0),   xtal::UnitCellCoord(3, 0, 1, 0),
      xtal::UnitCellCoord(2, 1, 0, 0),   xtal::UnitCellCoord(3, 1, 0, 0),
      xtal::UnitCellCoord(2, 1, 1, 0),   xtal::UnitCellCoord(3, 1, 1, 0)};

  m_orbit_neighborhood[4] = std::set<xtal::UnitCell>{
      xtal::UnitCell(-1, -1, -1), xtal::UnitCell(-1, -1, 0),
      xtal::UnitCell(-1, -1, 1),  xtal::UnitCell(-1, 0, -1),
      xtal::UnitCell(-1, 0, 0),   xtal::UnitCell(-1, 0, 1),
      xtal::UnitCell(0, -1, -1),  xtal::UnitCell(0, -1, 0),
      xtal::UnitCell(0, -1, 1),   xtal::UnitCell(0, 0, 0),
      xtal::UnitCell(0, 1, -1),   xtal::UnitCell(0, 1, 0),
      xtal::UnitCell(0, 1, 1),    xtal::UnitCell(1, 0, -1),
      xtal::UnitCell(1, 0, 0),    xtal::UnitCell(1, 0, 1),
      xtal::UnitCell(1, 1, -1),   xtal::UnitCell(1, 1, 0),
      xtal::UnitCell(1, 1, 1)};

  m_orbit_site_neighborhood[4] = std::set<xtal::UnitCellCoord>{
      xtal::UnitCellCoord(3, -1, -1, -1), xtal::UnitCellCoord(2, -1, -1, 0),
      xtal::UnitCellCoord(3, -1, -1, 0),  xtal::UnitCellCoord(2, -1, -1, 1),
      xtal::UnitCellCoord(3, -1, 0, -1),  xtal::UnitCellCoord(2, -1, 0, 0),
      xtal::UnitCellCoord(3, -1, 0, 0),   xtal::UnitCellCoord(2, -1, 0, 1),
      xtal::UnitCellCoord(3, 0, -1, -1),  xtal::UnitCellCoord(2, 0, -1, 0),
      xtal::UnitCellCoord(3, 0, -1, 0),   xtal::UnitCellCoord(2, 0, -1, 1),
      xtal::UnitCellCoord(2, 0, 0, 0),    xtal::UnitCellCoord(3, 0, 0, 0),
      xtal::UnitCellCoord(3, 0, 1, -1),   xtal::UnitCellCoord(2, 0, 1, 0),
      xtal::UnitCellCoord(3, 0, 1, 0),    xtal::UnitCellCoord(2, 0, 1, 1),
      xtal::UnitCellCoord(3, 1, 0, -1),   xtal::UnitCellCoord(2, 1, 0, 0),
      xtal::UnitCellCoord(3, 1, 0, 0),    xtal::UnitCellCoord(2, 1, 0, 1),
      xtal::UnitCellCoord(3, 1, 1, -1),   xtal::UnitCellCoord(2, 1, 1, 0),
      xtal::UnitCellCoord(3, 1, 1, 0),    xtal::UnitCellCoord(2, 1, 1, 1)};

  m_orbit_neighborhood[5] = std::set<xtal::UnitCell>{xtal::UnitCell(0, 0, -1),
                                                     xtal::UnitCell(0, 0, 0),
                                                     xtal::UnitCell(0, 0, 1)};

  m_orbit_site_neighborhood[5] = std::set<xtal::UnitCellCoord>{
      xtal::UnitCellCoord(2, 0, 0, -1), xtal::UnitCellCoord(3, 0, 0, -1),
      xtal::UnitCellCoord(2, 0, 0, 0),  xtal::UnitCellCoord(3, 0, 0, 0),
      xtal::UnitCellCoord(2, 0, 0, 1),  xtal::UnitCellCoord(3, 0, 0, 1)};

  m_orbit_neighborhood[6] = std::set<xtal::UnitCell>{
      xtal::UnitCell(-2, -1, 0), xtal::UnitCell(-1, -2, 0),
      xtal::UnitCell(-1, 1, 0),  xtal::UnitCell(0, 0, 0),
      xtal::UnitCell(1, -1, 0),  xtal::UnitCell(1, 2, 0),
      xtal::UnitCell(2, 1, 0)};

  m_orbit_site_neighborhood[6] = std::set<xtal::UnitCellCoord>{
      xtal::UnitCellCoord(2, -2, -1, 0), xtal::UnitCellCoord(3, -2, -1, 0),
      xtal::UnitCellCoord(2, -1, -2, 0), xtal::UnitCellCoord(3, -1, -2, 0),
      xtal::UnitCellCoord(2, -1, 1, 0),  xtal::UnitCellCoord(3, -1, 1, 0),
      xtal::UnitCellCoord(2, 0, 0, 0),   xtal::UnitCellCoord(3, 0, 0, 0),
      xtal::UnitCellCoord(2, 1, -1, 0),  xtal::UnitCellCoord(3, 1, -1, 0),
      xtal::UnitCellCoord(2, 1, 2, 0),   xtal::UnitCellCoord(3, 1, 2, 0),
      xtal::UnitCellCoord(2, 2, 1, 0),   xtal::UnitCellCoord(3, 2, 1, 0)};

  m_orbit_neighborhood[7] = std::set<xtal::UnitCell>{
      xtal::UnitCell(-1, -1, 0), xtal::UnitCell(-1, 0, 0),
      xtal::UnitCell(0, -1, 0),  xtal::UnitCell(0, 0, 0),
      xtal::UnitCell(0, 1, 0),   xtal::UnitCell(1, 0, 0),
      xtal::UnitCell(1, 1, 0)};

  m_orbit_site_neighborhood[7] = std::set<xtal::UnitCellCoord>{
      xtal::UnitCellCoord(2, -1, -1, 0), xtal::UnitCellCoord(3, -1, -1, 0),
      xtal::UnitCellCoord(2, -1, 0, 0),  xtal::UnitCellCoord(3, -1, 0, 0),
      xtal::UnitCellCoord(2, 0, -1, 0),  xtal::UnitCellCoord(3, 0, -1, 0),
      xtal::UnitCellCoord(2, 0, 0, 0),   xtal::UnitCellCoord(3, 0, 0, 0),
      xtal::UnitCellCoord(2, 0, 1, 0),   xtal::UnitCellCoord(3, 0, 1, 0),
      xtal::UnitCellCoord(2, 1, 0, 0),   xtal::UnitCellCoord(3, 1, 0, 0),
      xtal::UnitCellCoord(2, 1, 1, 0),   xtal::UnitCellCoord(3, 1, 1, 0)};

  m_orbit_neighborhood[8] = std::set<xtal::UnitCell>{
      xtal::UnitCell(-1, -1, -1), xtal::UnitCell(-1, -1, 0),
      xtal::UnitCell(-1, -1, 1),  xtal::UnitCell(-1, 0, -1),
      xtal::UnitCell(-1, 0, 0),   xtal::UnitCell(-1, 0, 1),
      xtal::UnitCell(0, -1, -1),  xtal::UnitCell(0, -1, 0),
      xtal::UnitCell(0, -1, 1),   xtal::UnitCell(0, 0, -1),
      xtal::UnitCell(0, 0, 0),    xtal::UnitCell(0, 0, 1),
      xtal::UnitCell(0, 1, -1),   xtal::UnitCell(0, 1, 0),
      xtal::UnitCell(0, 1, 1),    xtal::UnitCell(1, 0, -1),
      xtal::UnitCell(1, 0, 0),    xtal::UnitCell(1, 0, 1),
      xtal::UnitCell(1, 1, -1),   xtal::UnitCell(1, 1, 0),
      xtal::UnitCell(1, 1, 1)};

  m_orbit_site_neighborhood[8] = std::set<xtal::UnitCellCoord>{
      xtal::UnitCellCoord(3, -1, -1, -1), xtal::UnitCellCoord(2, -1, -1, 0),
      xtal::UnitCellCoord(3, -1, -1, 0),  xtal::UnitCellCoord(2, -1, -1, 1),
      xtal::UnitCellCoord(3, -1, 0, -1),  xtal::UnitCellCoord(2, -1, 0, 0),
      xtal::UnitCellCoord(3, -1, 0, 0),   xtal::UnitCellCoord(2, -1, 0, 1),
      xtal::UnitCellCoord(3, 0, -1, -1),  xtal::UnitCellCoord(2, 0, -1, 0),
      xtal::UnitCellCoord(3, 0, -1, 0),   xtal::UnitCellCoord(2, 0, -1, 1),
      xtal::UnitCellCoord(3, 0, 0, -1),   xtal::UnitCellCoord(2, 0, 0, 0),
      xtal::UnitCellCoord(3, 0, 0, 0),    xtal::UnitCellCoord(2, 0, 0, 1),
      xtal::UnitCellCoord(3, 0, 1, -1),   xtal::UnitCellCoord(2, 0, 1, 0),
      xtal::UnitCellCoord(3, 0, 1, 0),    xtal::UnitCellCoord(2, 0, 1, 1),
      xtal::UnitCellCoord(3, 1, 0, -1),   xtal::UnitCellCoord(2, 1, 0, 0),
      xtal::UnitCellCoord(3, 1, 0, 0),    xtal::UnitCellCoord(2, 1, 0, 1),
      xtal::UnitCellCoord(3, 1, 1, -1),   xtal::UnitCellCoord(2, 1, 1, 0),
      xtal::UnitCellCoord(3, 1, 1, 0),    xtal::UnitCellCoord(2, 1, 1, 1)};

  m_orbit_neighborhood[9] = std::set<xtal::UnitCell>{
      xtal::UnitCell(-1, -1, -1), xtal::UnitCell(-1, -1, 0),
      xtal::UnitCell(-1, -1, 1),  xtal::UnitCell(-1, 0, -1),
      xtal::UnitCell(-1, 0, 0),   xtal::UnitCell(-1, 0, 1),
      xtal::UnitCell(0, -1, -1),  xtal::UnitCell(0, -1, 0),
      xtal::UnitCell(0, -1, 1),   xtal::UnitCell(0, 0, 0),
      xtal::UnitCell(0, 1, -1),   xtal::UnitCell(0, 1, 0),
      xtal::UnitCell(0, 1, 1),    xtal::UnitCell(1, 0, -1),
      xtal::UnitCell(1, 0, 0),    xtal::UnitCell(1, 0, 1),
      xtal::UnitCell(1, 1, -1),   xtal::UnitCell(1, 1, 0),
      xtal::UnitCell(1, 1, 1)};

  m_orbit_site_neighborhood[9] = std::set<xtal::UnitCellCoord>{
      xtal::UnitCellCoord(3, -1, -1, -1), xtal::UnitCellCoord(2, -1, -1, 0),
      xtal::UnitCellCoord(3, -1, -1, 0),  xtal::UnitCellCoord(2, -1, -1, 1),
      xtal::UnitCellCoord(3, -1, 0, -1),  xtal::UnitCellCoord(2, -1, 0, 0),
      xtal::UnitCellCoord(3, -1, 0, 0),   xtal::UnitCellCoord(2, -1, 0, 1),
      xtal::UnitCellCoord(3, 0, -1, -1),  xtal::UnitCellCoord(2, 0, -1, 0),
      xtal::UnitCellCoord(3, 0, -1, 0),   xtal::UnitCellCoord(2, 0, -1, 1),
      xtal::UnitCellCoord(2, 0, 0, 0),    xtal::UnitCellCoord(3, 0, 0, 0),
      xtal::UnitCellCoord(3, 0, 1, -1),   xtal::UnitCellCoord(2, 0, 1, 0),
      xtal::UnitCellCoord(3, 0, 1, 0),    xtal::UnitCellCoord(2, 0, 1, 1),
      xtal::UnitCellCoord(3, 1, 0, -1),   xtal::UnitCellCoord(2, 1, 0, 0),
      xtal::UnitCellCoord(3, 1, 0, 0),    xtal::UnitCellCoord(2, 1, 0, 1),
      xtal::UnitCellCoord(3, 1, 1, -1),   xtal::UnitCellCoord(2, 1, 1, 0),
      xtal::UnitCellCoord(3, 1, 1, 0),    xtal::UnitCellCoord(2, 1, 1, 1)};

  m_orbit_neighborhood[10] = std::set<xtal::UnitCell>{
      xtal::UnitCell(-1, -1, -1), xtal::UnitCell(-1, -1, 0),
      xtal::UnitCell(-1, -1, 1),  xtal::UnitCell(-1, 0, -1),
      xtal::UnitCell(-1, 0, 0),   xtal::UnitCell(-1, 0, 1),
      xtal::UnitCell(0, -1, -1),  xtal::UnitCell(0, -1, 0),
      xtal::UnitCell(0, -1, 1),   xtal::UnitCell(0, 0, 0),
      xtal::UnitCell(0, 1, -1),   xtal::UnitCell(0, 1, 0),
      xtal::UnitCell(0, 1, 1),    xtal::UnitCell(1, 0, -1),
      xtal::UnitCell(1, 0, 0),    xtal::UnitCell(1, 0, 1),
      xtal::UnitCell(1, 1, -1),   xtal::UnitCell(1, 1, 0),
      xtal::UnitCell(1, 1, 1)};

  m_orbit_site_neighborhood[10] = std::set<xtal::UnitCellCoord>{
      xtal::UnitCellCoord(3, -1, -1, -1), xtal::UnitCellCoord(2, -1, -1, 0),
      xtal::UnitCellCoord(3, -1, -1, 0),  xtal::UnitCellCoord(2, -1, -1, 1),
      xtal::UnitCellCoord(3, -1, 0, -1),  xtal::UnitCellCoord(2, -1, 0, 0),
      xtal::UnitCellCoord(3, -1, 0, 0),   xtal::UnitCellCoord(2, -1, 0, 1),
      xtal::UnitCellCoord(3, 0, -1, -1),  xtal::UnitCellCoord(2, 0, -1, 0),
      xtal::UnitCellCoord(3, 0, -1, 0),   xtal::UnitCellCoord(2, 0, -1, 1),
      xtal::UnitCellCoord(2, 0, 0, 0),    xtal::UnitCellCoord(3, 0, 0, 0),
      xtal::UnitCellCoord(3, 0, 1, -1),   xtal::UnitCellCoord(2, 0, 1, 0),
      xtal::UnitCellCoord(3, 0, 1, 0),    xtal::UnitCellCoord(2, 0, 1, 1),
      xtal::UnitCellCoord(3, 1, 0, -1),   xtal::UnitCellCoord(2, 1, 0, 0),
      xtal::UnitCellCoord(3, 1, 0, 0),    xtal::UnitCellCoord(2, 1, 0, 1),
      xtal::UnitCellCoord(3, 1, 1, -1),   xtal::UnitCellCoord(2, 1, 1, 0),
      xtal::UnitCellCoord(3, 1, 1, 0),    xtal::UnitCellCoord(2, 1, 1, 1)};

  m_orbit_neighborhood[11] = std::set<xtal::UnitCell>{
      xtal::UnitCell(-1, -1, -1), xtal::UnitCell(-1, -1, 0),
      xtal::UnitCell(-1, -1, 1),  xtal::UnitCell(-1, 0, -1),
      xtal::UnitCell(-1, 0, 0),   xtal::UnitCell(-1, 0, 1),
      xtal::UnitCell(0, -1, -1),  xtal::UnitCell(0, -1, 0),
      xtal::UnitCell(0, -1, 1),   xtal::UnitCell(0, 0, -1),
      xtal::UnitCell(0, 0, 0),    xtal::UnitCell(0, 0, 1),
      xtal::UnitCell(0, 1, -1),   xtal::UnitCell(0, 1, 0),
      xtal::UnitCell(0, 1, 1),    xtal::UnitCell(1, 0, -1),
      xtal::UnitCell(1, 0, 0),    xtal::UnitCell(1, 0, 1),
      xtal::UnitCell(1, 1, -1),   xtal::UnitCell(1, 1, 0),
      xtal::UnitCell(1, 1, 1)};

  m_orbit_site_neighborhood[11] = std::set<xtal::UnitCellCoord>{
      xtal::UnitCellCoord(3, -1, -1, -1), xtal::UnitCellCoord(2, -1, -1, 0),
      xtal::UnitCellCoord(3, -1, -1, 0),  xtal::UnitCellCoord(2, -1, -1, 1),
      xtal::UnitCellCoord(3, -1, 0, -1),  xtal::UnitCellCoord(2, -1, 0, 0),
      xtal::UnitCellCoord(3, -1, 0, 0),   xtal::UnitCellCoord(2, -1, 0, 1),
      xtal::UnitCellCoord(3, 0, -1, -1),  xtal::UnitCellCoord(2, 0, -1, 0),
      xtal::UnitCellCoord(3, 0, -1, 0),   xtal::UnitCellCoord(2, 0, -1, 1),
      xtal::UnitCellCoord(3, 0, 0, -1),   xtal::UnitCellCoord(2, 0, 0, 0),
      xtal::UnitCellCoord(3, 0, 0, 0),    xtal::UnitCellCoord(2, 0, 0, 1),
      xtal::UnitCellCoord(3, 0, 1, -1),   xtal::UnitCellCoord(2, 0, 1, 0),
      xtal::UnitCellCoord(3, 0, 1, 0),    xtal::UnitCellCoord(2, 0, 1, 1),
      xtal::UnitCellCoord(3, 1, 0, -1),   xtal::UnitCellCoord(2, 1, 0, 0),
      xtal::UnitCellCoord(3, 1, 0, 0),    xtal::UnitCellCoord(2, 1, 0, 1),
      xtal::UnitCellCoord(3, 1, 1, -1),   xtal::UnitCellCoord(2, 1, 1, 0),
      xtal::UnitCellCoord(3, 1, 1, 0),    xtal::UnitCellCoord(2, 1, 1, 1)};

  m_orbit_neighborhood[12] = std::set<xtal::UnitCell>{
      xtal::UnitCell(-1, -1, -1), xtal::UnitCell(-1, -1, 0),
      xtal::UnitCell(-1, -1, 1),  xtal::UnitCell(-1, 0, -1),
      xtal::UnitCell(-1, 0, 0),   xtal::UnitCell(-1, 0, 1),
      xtal::UnitCell(0, -1, -1),  xtal::UnitCell(0, -1, 0),
      xtal::UnitCell(0, -1, 1),   xtal::UnitCell(0, 0, -1),
      xtal::UnitCell(0, 0, 0),    xtal::UnitCell(0, 0, 1),
      xtal::UnitCell(0, 1, -1),   xtal::UnitCell(0, 1, 0),
      xtal::UnitCell(0, 1, 1),    xtal::UnitCell(1, 0, -1),
      xtal::UnitCell(1, 0, 0),    xtal::UnitCell(1, 0, 1),
      xtal::UnitCell(1, 1, -1),   xtal::UnitCell(1, 1, 0),
      xtal::UnitCell(1, 1, 1)};

  m_orbit_site_neighborhood[12] = std::set<xtal::UnitCellCoord>{
      xtal::UnitCellCoord(3, -1, -1, -1), xtal::UnitCellCoord(2, -1, -1, 0),
      xtal::UnitCellCoord(3, -1, -1, 0),  xtal::UnitCellCoord(2, -1, -1, 1),
      xtal::UnitCellCoord(3, -1, 0, -1),  xtal::UnitCellCoord(2, -1, 0, 0),
      xtal::UnitCellCoord(3, -1, 0, 0),   xtal::UnitCellCoord(2, -1, 0, 1),
      xtal::UnitCellCoord(3, 0, -1, -1),  xtal::UnitCellCoord(2, 0, -1, 0),
      xtal::UnitCellCoord(3, 0, -1, 0),   xtal::UnitCellCoord(2, 0, -1, 1),
      xtal::UnitCellCoord(3, 0, 0, -1),   xtal::UnitCellCoord(2, 0, 0, 0),
      xtal::UnitCellCoord(3, 0, 0, 0),    xtal::UnitCellCoord(2, 0, 0, 1),
      xtal::UnitCellCoord(3, 0, 1, -1),   xtal::UnitCellCoord(2, 0, 1, 0),
      xtal::UnitCellCoord(3, 0, 1, 0),    xtal::UnitCellCoord(2, 0, 1, 1),
      xtal::UnitCellCoord(3, 1, 0, -1),   xtal::UnitCellCoord(2, 1, 0, 0),
      xtal::UnitCellCoord(3, 1, 0, 0),    xtal::UnitCellCoord(2, 1, 0, 1),
      xtal::UnitCellCoord(3, 1, 1, -1),   xtal::UnitCellCoord(2, 1, 1, 0),
      xtal::UnitCellCoord(3, 1, 1, 0),    xtal::UnitCellCoord(2, 1, 1, 1)};

  m_orbit_neighborhood[13] = std::set<xtal::UnitCell>{
      xtal::UnitCell(-1, -1, -1), xtal::UnitCell(-1, -1, 0),
      xtal::UnitCell(-1, -1, 1),  xtal::UnitCell(-1, 0, -1),
      xtal::UnitCell(-1, 0, 0),   xtal::UnitCell(-1, 0, 1),
      xtal::UnitCell(0, -1, -1),  xtal::UnitCell(0, -1, 0),
      xtal::UnitCell(0, -1, 1),   xtal::UnitCell(0, 0, -1),
      xtal::UnitCell(0, 0, 0),    xtal::UnitCell(0, 0, 1),
      xtal::UnitCell(0, 1, -1),   xtal::UnitCell(0, 1, 0),
      xtal::UnitCell(0, 1, 1),    xtal::UnitCell(1, 0, -1),
      xtal::UnitCell(1, 0, 0),    xtal::UnitCell(1, 0, 1),
      xtal::UnitCell(1, 1, -1),   xtal::UnitCell(1, 1, 0),
      xtal::UnitCell(1, 1, 1)};

  m_orbit_site_neighborhood[13] = std::set<xtal::UnitCellCoord>{
      xtal::UnitCellCoord(3, -1, -1, -1), xtal::UnitCellCoord(2, -1, -1, 0),
      xtal::UnitCellCoord(3, -1, -1, 0),  xtal::UnitCellCoord(2, -1, -1, 1),
      xtal::UnitCellCoord(3, -1, 0, -1),  xtal::UnitCellCoord(2, -1, 0, 0),
      xtal::UnitCellCoord(3, -1, 0, 0),   xtal::UnitCellCoord(2, -1, 0, 1),
      xtal::UnitCellCoord(3, 0, -1, -1),  xtal::UnitCellCoord(2, 0, -1, 0),
      xtal::UnitCellCoord(3, 0, -1, 0),   xtal::UnitCellCoord(2, 0, -1, 1),
      xtal::UnitCellCoord(3, 0, 0, -1),   xtal::UnitCellCoord(2, 0, 0, 0),
      xtal::UnitCellCoord(3, 0, 0, 0),    xtal::UnitCellCoord(2, 0, 0, 1),
      xtal::UnitCellCoord(3, 0, 1, -1),   xtal::UnitCellCoord(2, 0, 1, 0),
      xtal::UnitCellCoord(3, 0, 1, 0),    xtal::UnitCellCoord(2, 0, 1, 1),
      xtal::UnitCellCoord(3, 1, 0, -1),   xtal::UnitCellCoord(2, 1, 0, 0),
      xtal::UnitCellCoord(3, 1, 0, 0),    xtal::UnitCellCoord(2, 1, 0, 1),
      xtal::UnitCellCoord(3, 1, 1, -1),   xtal::UnitCellCoord(2, 1, 1, 0),
      xtal::UnitCellCoord(3, 1, 1, 0),    xtal::UnitCellCoord(2, 1, 1, 1)};

  m_orbit_neighborhood[14] = std::set<xtal::UnitCell>{
      xtal::UnitCell(-1, -1, -1), xtal::UnitCell(-1, -1, 0),
      xtal::UnitCell(-1, -1, 1),  xtal::UnitCell(-1, 0, -1),
      xtal::UnitCell(-1, 0, 0),   xtal::UnitCell(-1, 0, 1),
      xtal::UnitCell(0, -1, -1),  xtal::UnitCell(0, -1, 0),
      xtal::UnitCell(0, -1, 1),   xtal::UnitCell(0, 0, -1),
      xtal::UnitCell(0, 0, 0),    xtal::UnitCell(0, 0, 1),
      xtal::UnitCell(0, 1, -1),   xtal::UnitCell(0, 1, 0),
      xtal::UnitCell(0, 1, 1),    xtal::UnitCell(1, 0, -1),
      xtal::UnitCell(1, 0, 0),    xtal::UnitCell(1, 0, 1),
      xtal::UnitCell(1, 1, -1),   xtal::UnitCell(1, 1, 0),
      xtal::UnitCell(1, 1, 1)};

  m_orbit_site_neighborhood[14] = std::set<xtal::UnitCellCoord>{
      xtal::UnitCellCoord(3, -1, -1, -1), xtal::UnitCellCoord(2, -1, -1, 0),
      xtal::UnitCellCoord(3, -1, -1, 0),  xtal::UnitCellCoord(2, -1, -1, 1),
      xtal::UnitCellCoord(3, -1, 0, -1),  xtal::UnitCellCoord(2, -1, 0, 0),
      xtal::UnitCellCoord(3, -1, 0, 0),   xtal::UnitCellCoord(2, -1, 0, 1),
      xtal::UnitCellCoord(3, 0, -1, -1),  xtal::UnitCellCoord(2, 0, -1, 0),
      xtal::UnitCellCoord(3, 0, -1, 0),   xtal::UnitCellCoord(2, 0, -1, 1),
      xtal::UnitCellCoord(3, 0, 0, -1),   xtal::UnitCellCoord(2, 0, 0, 0),
      xtal::UnitCellCoord(3, 0, 0, 0),    xtal::UnitCellCoord(2, 0, 0, 1),
      xtal::UnitCellCoord(3, 0, 1, -1),   xtal::UnitCellCoord(2, 0, 1, 0),
      xtal::UnitCellCoord(3, 0, 1, 0),    xtal::UnitCellCoord(2, 0, 1, 1),
      xtal::UnitCellCoord(3, 1, 0, -1),   xtal::UnitCellCoord(2, 1, 0, 0),
      xtal::UnitCellCoord(3, 1, 0, 0),    xtal::UnitCellCoord(2, 1, 0, 1),
      xtal::UnitCellCoord(3, 1, 1, -1),   xtal::UnitCellCoord(2, 1, 1, 0),
      xtal::UnitCellCoord(3, 1, 1, 0),    xtal::UnitCellCoord(2, 1, 1, 1)};

  m_orbit_neighborhood[15] = std::set<xtal::UnitCell>{
      xtal::UnitCell(-1, -1, -1), xtal::UnitCell(-1, -1, 0),
      xtal::UnitCell(-1, -1, 1),  xtal::UnitCell(-1, 0, -1),
      xtal::UnitCell(-1, 0, 0),   xtal::UnitCell(-1, 0, 1),
      xtal::UnitCell(0, -1, -1),  xtal::UnitCell(0, -1, 0),
      xtal::UnitCell(0, -1, 1),   xtal::UnitCell(0, 0, -1),
      xtal::UnitCell(0, 0, 0),    xtal::UnitCell(0, 0, 1),
      xtal::UnitCell(0, 1, -1),   xtal::UnitCell(0, 1, 0),
      xtal::UnitCell(0, 1, 1),    xtal::UnitCell(1, 0, -1),
      xtal::UnitCell(1, 0, 0),    xtal::UnitCell(1, 0, 1),
      xtal::UnitCell(1, 1, -1),   xtal::UnitCell(1, 1, 0),
      xtal::UnitCell(1, 1, 1)};

  m_orbit_site_neighborhood[15] = std::set<xtal::UnitCellCoord>{
      xtal::UnitCellCoord(3, -1, -1, -1), xtal::UnitCellCoord(2, -1, -1, 0),
      xtal::UnitCellCoord(3, -1, -1, 0),  xtal::UnitCellCoord(2, -1, -1, 1),
      xtal::UnitCellCoord(3, -1, 0, -1),  xtal::UnitCellCoord(2, -1, 0, 0),
      xtal::UnitCellCoord(3, -1, 0, 0),   xtal::UnitCellCoord(2, -1, 0, 1),
      xtal::UnitCellCoord(3, 0, -1, -1),  xtal::UnitCellCoord(2, 0, -1, 0),
      xtal::UnitCellCoord(3, 0, -1, 0),   xtal::UnitCellCoord(2, 0, -1, 1),
      xtal::UnitCellCoord(3, 0, 0, -1),   xtal::UnitCellCoord(2, 0, 0, 0),
      xtal::UnitCellCoord(3, 0, 0, 0),    xtal::UnitCellCoord(2, 0, 0, 1),
      xtal::UnitCellCoord(3, 0, 1, -1),   xtal::UnitCellCoord(2, 0, 1, 0),
      xtal::UnitCellCoord(3, 0, 1, 0),    xtal::UnitCellCoord(2, 0, 1, 1),
      xtal::UnitCellCoord(3, 1, 0, -1),   xtal::UnitCellCoord(2, 1, 0, 0),
      xtal::UnitCellCoord(3, 1, 0, 0),    xtal::UnitCellCoord(2, 1, 0, 1),
      xtal::UnitCellCoord(3, 1, 1, -1),   xtal::UnitCellCoord(2, 1, 1, 0),
      xtal::UnitCellCoord(3, 1, 1, 0),    xtal::UnitCellCoord(2, 1, 1, 1)};
}

OccClexulatorZrOTest_Clexulator_default::
    ~OccClexulatorZrOTest_Clexulator_default() {
  // nothing here for now
}

/// \brief Calculate contribution to global correlations from one unit cell
void OccClexulatorZrOTest_Clexulator_default::_calc_global_corr_contribution(
    double *corr_begin) const {
  _calc_global_corr_contribution();
  for (size_type i = 0; i < corr_size(); i++) {
    *(corr_begin + i) =
        ParamPack::Val<double>::get(m_params, m_corr_param_key, i);
  }
}

/// \brief Calculate contribution to global correlations from one unit cell
void OccClexulatorZrOTest_Clexulator_default::_calc_global_corr_contribution()
    const {
  m_params.pre_eval();
  {
    _global_prepare<double>();
    for (size_type i = 0; i < corr_size(); i++) {
      ParamPack::Val<double>::set(m_params, m_corr_param_key, i,
                                  (this->*m_orbit_func_table_0[i])());
    }
  }
  m_params.post_eval();
}

/// \brief Calculate contribution to select global correlations from one unit
/// cell
void OccClexulatorZrOTest_Clexulator_default::
    _calc_restricted_global_corr_contribution(
        double *corr_begin, size_type const *ind_list_begin,
        size_type const *ind_list_end) const {
  _calc_restricted_global_corr_contribution(ind_list_begin, ind_list_end);
  for (; ind_list_begin < ind_list_end; ind_list_begin++) {
    *(corr_begin + *ind_list_begin) = ParamPack::Val<double>::get(
        m_params, m_corr_param_key, *ind_list_begin);
  }
}

/// \brief Calculate contribution to select global correlations from one unit
/// cell
void OccClexulatorZrOTest_Clexulator_default::
    _calc_restricted_global_corr_contribution(
        size_type const *ind_list_begin, size_type const *ind_list_end) const {
  m_params.pre_eval();
  {
    _global_prepare<double>();
    for (; ind_list_begin < ind_list_end; ind_list_begin++) {
      ParamPack::Val<double>::set(
          m_params, m_corr_param_key, *ind_list_begin,
          (this->*m_orbit_func_table_0[*ind_list_begin])());
    }
  }
  m_params.post_eval();
}

/// \brief Calculate point correlations about basis site 'nlist_ind'
void OccClexulatorZrOTest_Clexulator_default::_calc_point_corr(
    int nlist_ind, double *corr_begin) const {
  _calc_point_corr(nlist_ind);
  for (size_type i = 0; i < corr_size(); i++) {
    *(corr_begin + i) =
        ParamPack::Val<double>::get(m_params, m_corr_param_key, i);
  }
}

/// \brief Calculate point correlations about basis site 'nlist_ind'
void OccClexulatorZrOTest_Clexulator_default::_calc_point_corr(
    int nlist_ind) const {
  m_params.pre_eval();
  {
    _point_prepare<double>(nlist_ind);
    for (size_type i = 0; i < corr_size(); i++) {
      ParamPack::Val<double>::set(
          m_params, m_corr_param_key, i,
          (this->*m_flower_func_table_0[nlist_ind][i])());
    }
  }
  m_params.post_eval();
}

/// \brief Calculate select point correlations about basis site 'nlist_ind'
void OccClexulatorZrOTest_Clexulator_default::_calc_restricted_point_corr(
    int nlist_ind, double *corr_begin, size_type const *ind_list_begin,
    size_type const *ind_list_end) const {
  _calc_restricted_point_corr(nlist_ind, ind_list_begin, ind_list_end);
  for (; ind_list_begin < ind_list_end; ind_list_begin++) {
    *(corr_begin + *ind_list_begin) = ParamPack::Val<double>::get(
        m_params, m_corr_param_key, *ind_list_begin);
  }
}

/// \brief Calculate select point correlations about basis site 'nlist_ind'
void OccClexulatorZrOTest_Clexulator_default::_calc_restricted_point_corr(
    int nlist_ind, size_type const *ind_list_begin,
    size_type const *ind_list_end) const {
  m_params.pre_eval();
  {
    _point_prepare<double>(nlist_ind);
    for (; ind_list_begin < ind_list_end; ind_list_begin++) {
      ParamPack::Val<double>::set(
          m_params, m_corr_param_key, *ind_list_begin,
          (this->*m_flower_func_table_0[nlist_ind][*ind_list_begin])());
    }
  }
  m_params.post_eval();
}

/// \brief Calculate the change in point correlations due to changing an
/// occupant
void OccClexulatorZrOTest_Clexulator_default::_calc_delta_point_corr(
    int nlist_ind, int occ_i, int occ_f, double *corr_begin) const {
  _calc_delta_point_corr(nlist_ind, occ_i, occ_f);
  for (size_type i = 0; i < corr_size(); i++) {
    *(corr_begin + i) =
        ParamPack::Val<double>::get(m_params, m_corr_param_key, i);
  }
}

/// \brief Calculate the change in point correlations due to changing an
/// occupant
void OccClexulatorZrOTest_Clexulator_default::_calc_delta_point_corr(
    int nlist_ind, int occ_i, int occ_f) const {
  m_params.pre_eval();
  {
    _point_prepare<double>(nlist_ind);
    for (size_type i = 0; i < corr_size(); i++) {
      ParamPack::Val<double>::set(
          m_params, m_corr_param_key, i,
          (this->*m_delta_func_table_0[nlist_ind][i])(occ_i, occ_f));
    }
  }
  m_params.post_eval();
}

/// \brief Calculate the change in select point correlations due to changing an
/// occupant
void OccClexulatorZrOTest_Clexulator_default::_calc_restricted_delta_point_corr(
    int nlist_ind, int occ_i, int occ_f, double *corr_begin,
    size_type const *ind_list_begin, size_type const *ind_list_end) const {
  _calc_restricted_delta_point_corr(nlist_ind, occ_i, occ_f, ind_list_begin,
                                    ind_list_end);
  for (; ind_list_begin < ind_list_end; ind_list_begin++) {
    *(corr_begin + *ind_list_begin) = ParamPack::Val<double>::get(
        m_params, m_corr_param_key, *ind_list_begin);
  }
}

/// \brief Calculate the change in select point correlations due to changing an
/// occupant
void OccClexulatorZrOTest_Clexulator_default::_calc_restricted_delta_point_corr(
    int nlist_ind, int occ_i, int occ_f, size_type const *ind_list_begin,
    size_type const *ind_list_end) const {
  m_params.pre_eval();
  {
    _point_prepare<double>(nlist_ind);
    for (; ind_list_begin < ind_list_end; ind_list_begin++) {
      ParamPack::Val<double>::set(
          m_params, m_corr_param_key, *ind_list_begin,
          (this->*m_delta_func_table_0[nlist_ind][*ind_list_begin])(occ_i,
                                                                    occ_f));
    }
  }
  m_params.post_eval();
}

template <typename Scalar>
void OccClexulatorZrOTest_Clexulator_default::_point_prepare(
    int nlist_ind) const {
  switch (nlist_ind) {
    case 0:
      if (m_params.eval_mode(m_occ_site_func_param_key) != ParamPack::READ) {
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 0,
                                    eval_occ_func_2_0(0));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 2,
                                    eval_occ_func_2_0(2));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 4,
                                    eval_occ_func_2_0(4));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 6,
                                    eval_occ_func_2_0(6));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 8,
                                    eval_occ_func_2_0(8));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 10,
                                    eval_occ_func_2_0(10));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 12,
                                    eval_occ_func_2_0(12));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 14,
                                    eval_occ_func_2_0(14));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 16,
                                    eval_occ_func_2_0(16));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 18,
                                    eval_occ_func_2_0(18));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 20,
                                    eval_occ_func_2_0(20));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 22,
                                    eval_occ_func_2_0(22));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 24,
                                    eval_occ_func_2_0(24));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 26,
                                    eval_occ_func_2_0(26));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 28,
                                    eval_occ_func_2_0(28));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 1,
                                    eval_occ_func_3_0(1));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 3,
                                    eval_occ_func_3_0(3));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 5,
                                    eval_occ_func_3_0(5));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 7,
                                    eval_occ_func_3_0(7));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 9,
                                    eval_occ_func_3_0(9));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 11,
                                    eval_occ_func_3_0(11));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 13,
                                    eval_occ_func_3_0(13));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 15,
                                    eval_occ_func_3_0(15));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 31,
                                    eval_occ_func_3_0(31));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 35,
                                    eval_occ_func_3_0(35));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 39,
                                    eval_occ_func_3_0(39));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 43,
                                    eval_occ_func_3_0(43));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 47,
                                    eval_occ_func_3_0(47));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 51,
                                    eval_occ_func_3_0(51));
      }
      break;
    case 1:
      if (m_params.eval_mode(m_occ_site_func_param_key) != ParamPack::READ) {
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 0,
                                    eval_occ_func_2_0(0));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 2,
                                    eval_occ_func_2_0(2));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 4,
                                    eval_occ_func_2_0(4));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 6,
                                    eval_occ_func_2_0(6));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 8,
                                    eval_occ_func_2_0(8));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 10,
                                    eval_occ_func_2_0(10));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 12,
                                    eval_occ_func_2_0(12));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 16,
                                    eval_occ_func_2_0(16));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 32,
                                    eval_occ_func_2_0(32));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 36,
                                    eval_occ_func_2_0(36));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 40,
                                    eval_occ_func_2_0(40));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 44,
                                    eval_occ_func_2_0(44));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 48,
                                    eval_occ_func_2_0(48));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 52,
                                    eval_occ_func_2_0(52));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 1,
                                    eval_occ_func_3_0(1));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 3,
                                    eval_occ_func_3_0(3));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 5,
                                    eval_occ_func_3_0(5));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 7,
                                    eval_occ_func_3_0(7));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 9,
                                    eval_occ_func_3_0(9));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 11,
                                    eval_occ_func_3_0(11));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 13,
                                    eval_occ_func_3_0(13));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 15,
                                    eval_occ_func_3_0(15));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 17,
                                    eval_occ_func_3_0(17));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 19,
                                    eval_occ_func_3_0(19));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 21,
                                    eval_occ_func_3_0(21));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 23,
                                    eval_occ_func_3_0(23));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 25,
                                    eval_occ_func_3_0(25));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 27,
                                    eval_occ_func_3_0(27));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 29,
                                    eval_occ_func_3_0(29));
      }
      break;
  }
}
template <typename Scalar>
void OccClexulatorZrOTest_Clexulator_default::_global_prepare() const {
  if (m_params.eval_mode(m_occ_site_func_param_key) != ParamPack::READ) {
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 0,
                                eval_occ_func_2_0(0));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 2,
                                eval_occ_func_2_0(2));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 4,
                                eval_occ_func_2_0(4));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 6,
                                eval_occ_func_2_0(6));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 8,
                                eval_occ_func_2_0(8));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 10,
                                eval_occ_func_2_0(10));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 12,
                                eval_occ_func_2_0(12));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 14,
                                eval_occ_func_2_0(14));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 16,
                                eval_occ_func_2_0(16));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 18,
                                eval_occ_func_2_0(18));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 20,
                                eval_occ_func_2_0(20));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 22,
                                eval_occ_func_2_0(22));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 24,
                                eval_occ_func_2_0(24));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 26,
                                eval_occ_func_2_0(26));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 28,
                                eval_occ_func_2_0(28));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 32,
                                eval_occ_func_2_0(32));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 36,
                                eval_occ_func_2_0(36));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 40,
                                eval_occ_func_2_0(40));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 44,
                                eval_occ_func_2_0(44));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 48,
                                eval_occ_func_2_0(48));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 52,
                                eval_occ_func_2_0(52));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 1,
                                eval_occ_func_3_0(1));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 3,
                                eval_occ_func_3_0(3));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 5,
                                eval_occ_func_3_0(5));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 7,
                                eval_occ_func_3_0(7));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 9,
                                eval_occ_func_3_0(9));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 11,
                                eval_occ_func_3_0(11));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 13,
                                eval_occ_func_3_0(13));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 15,
                                eval_occ_func_3_0(15));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 17,
                                eval_occ_func_3_0(17));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 19,
                                eval_occ_func_3_0(19));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 21,
                                eval_occ_func_3_0(21));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 23,
                                eval_occ_func_3_0(23));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 25,
                                eval_occ_func_3_0(25));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 27,
                                eval_occ_func_3_0(27));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 29,
                                eval_occ_func_3_0(29));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 31,
                                eval_occ_func_3_0(31));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 35,
                                eval_occ_func_3_0(35));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 39,
                                eval_occ_func_3_0(39));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 43,
                                eval_occ_func_3_0(43));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 47,
                                eval_occ_func_3_0(47));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 51,
                                eval_occ_func_3_0(51));
  }
}

// Basis functions for empty cluster:
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::eval_bfunc_0_0() const {
  return 1;
}

/**** Basis functions for orbit 1****
0.3333333 0.6666667 0.2500000 Va  O

****/
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::eval_bfunc_1_0() const {
  return (occ_func_2_0(0) + occ_func_2_0(1)) / 2.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_1_0_at_0()
    const {
  return (occ_func_2_0(0)) / 2.;
}
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_1_0_at_1()
    const {
  return (occ_func_2_0(1)) / 2.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_1_0_at_0(
    int occ_i, int occ_f) const {
  return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (1) / 2.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_1_0_at_1(
    int occ_i, int occ_f) const {
  return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (1) / 2.;
}

/**** Basis functions for orbit 2****
0.3333333 0.6666667 0.2500000 Va  O

0.3333333 0.6666667 0.7500000 Va  O

****/
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::eval_bfunc_2_0() const {
  return (occ_func_2_0(0) * occ_func_3_0(1) +
          occ_func_2_0(1) * occ_func_3_0(16)) /
         2.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_2_0_at_0()
    const {
  return (occ_func_2_0(0) * occ_func_3_0(1) +
          occ_func_2_0(15) * occ_func_3_0(0)) /
         2.;
}
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_2_0_at_1()
    const {
  return (occ_func_2_0(0) * occ_func_3_0(1) +
          occ_func_2_0(1) * occ_func_3_0(16)) /
         2.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_2_0_at_0(
    int occ_i, int occ_f) const {
  return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) *
         (occ_func_3_0(1) + occ_func_2_0(15)) / 2.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_2_0_at_1(
    int occ_i, int occ_f) const {
  return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) *
         (occ_func_2_0(0) + occ_func_3_0(16)) / 2.;
}

/**** Basis functions for orbit 3****
0.3333333 0.6666667 0.2500000 Va  O

0.3333333 1.6666667 0.2500000 Va  O

****/
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::eval_bfunc_3_0() const {
  return (occ_func_2_0(0) * occ_func_2_0(8) +
          occ_func_2_0(11) * occ_func_2_0(1) +
          occ_func_2_0(1) * occ_func_2_0(13) +
          occ_func_2_0(12) * occ_func_2_0(0) +
          occ_func_2_0(0) * occ_func_2_0(10) +
          occ_func_2_0(9) * occ_func_2_0(1)) /
         6.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_3_0_at_0()
    const {
  return (occ_func_2_0(0) * occ_func_2_0(8) +
          occ_func_2_0(6) * occ_func_2_0(0) +
          occ_func_2_0(12) * occ_func_2_0(0) +
          occ_func_2_0(0) * occ_func_2_0(2) +
          occ_func_2_0(0) * occ_func_2_0(10) +
          occ_func_2_0(4) * occ_func_2_0(0)) /
         6.;
}
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_3_0_at_1()
    const {
  return (occ_func_2_0(11) * occ_func_2_0(1) +
          occ_func_2_0(1) * occ_func_2_0(5) +
          occ_func_2_0(1) * occ_func_2_0(13) +
          occ_func_2_0(3) * occ_func_2_0(1) +
          occ_func_2_0(9) * occ_func_2_0(1) +
          occ_func_2_0(1) * occ_func_2_0(7)) /
         6.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_3_0_at_0(
    int occ_i, int occ_f) const {
  return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) *
         (occ_func_2_0(8) + occ_func_2_0(6) + occ_func_2_0(12) +
          occ_func_2_0(2) + occ_func_2_0(10) + occ_func_2_0(4)) /
         6.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_3_0_at_1(
    int occ_i, int occ_f) const {
  return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) *
         (occ_func_2_0(11) + occ_func_2_0(5) + occ_func_2_0(13) +
          occ_func_2_0(3) + occ_func_2_0(9) + occ_func_2_0(7)) /
         6.;
}

/**** Basis functions for orbit 4****
0.3333333 0.6666667 0.2500000 Va  O

1.3333333 1.6666667 -0.2500000 Va  O

****/
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::eval_bfunc_4_0() const {
  return (occ_func_2_0(0) * occ_func_3_0(51) +
          occ_func_2_0(1) * occ_func_3_0(8) +
          occ_func_2_0(1) * occ_func_3_0(10) +
          occ_func_2_0(48) * occ_func_3_0(1) +
          occ_func_2_0(44) * occ_func_3_0(1) +
          occ_func_2_0(0) * occ_func_3_0(13) +
          occ_func_2_0(0) * occ_func_3_0(47) +
          occ_func_2_0(0) * occ_func_3_0(43) +
          occ_func_2_0(52) * occ_func_3_0(1) +
          occ_func_2_0(1) * occ_func_3_0(12) +
          occ_func_2_0(9) * occ_func_3_0(0) +
          occ_func_2_0(11) * occ_func_3_0(0)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_4_0_at_0()
    const {
  return (occ_func_2_0(0) * occ_func_3_0(51) +
          occ_func_2_0(7) * occ_func_3_0(0) +
          occ_func_2_0(5) * occ_func_3_0(0) +
          occ_func_2_0(0) * occ_func_3_0(35) +
          occ_func_2_0(0) * occ_func_3_0(39) +
          occ_func_2_0(0) * occ_func_3_0(13) +
          occ_func_2_0(0) * occ_func_3_0(47) +
          occ_func_2_0(0) * occ_func_3_0(43) +
          occ_func_2_0(0) * occ_func_3_0(31) +
          occ_func_2_0(3) * occ_func_3_0(0) +
          occ_func_2_0(9) * occ_func_3_0(0) +
          occ_func_2_0(11) * occ_func_3_0(0)) /
         12.;
}
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_4_0_at_1()
    const {
  return (occ_func_2_0(32) * occ_func_3_0(1) +
          occ_func_2_0(1) * occ_func_3_0(8) +
          occ_func_2_0(1) * occ_func_3_0(10) +
          occ_func_2_0(48) * occ_func_3_0(1) +
          occ_func_2_0(44) * occ_func_3_0(1) +
          occ_func_2_0(2) * occ_func_3_0(1) +
          occ_func_2_0(36) * occ_func_3_0(1) +
          occ_func_2_0(40) * occ_func_3_0(1) +
          occ_func_2_0(52) * occ_func_3_0(1) +
          occ_func_2_0(1) * occ_func_3_0(12) +
          occ_func_2_0(1) * occ_func_3_0(6) +
          occ_func_2_0(1) * occ_func_3_0(4)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_4_0_at_0(
    int occ_i, int occ_f) const {
  return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) *
         (occ_func_3_0(51) + occ_func_2_0(7) + occ_func_2_0(5) +
          occ_func_3_0(35) + occ_func_3_0(39) + occ_func_3_0(13) +
          occ_func_3_0(47) + occ_func_3_0(43) + occ_func_3_0(31) +
          occ_func_2_0(3) + occ_func_2_0(9) + occ_func_2_0(11)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_4_0_at_1(
    int occ_i, int occ_f) const {
  return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) *
         (occ_func_2_0(32) + occ_func_3_0(8) + occ_func_3_0(10) +
          occ_func_2_0(48) + occ_func_2_0(44) + occ_func_2_0(2) +
          occ_func_2_0(36) + occ_func_2_0(40) + occ_func_2_0(52) +
          occ_func_3_0(12) + occ_func_3_0(6) + occ_func_3_0(4)) /
         12.;
}

/**** Basis functions for orbit 5****
0.3333333 0.6666667 0.2500000 Va  O

0.3333333 0.6666667 1.2500000 Va  O

****/
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::eval_bfunc_5_0() const {
  return (occ_func_2_0(0) * occ_func_2_0(16) +
          occ_func_2_0(1) * occ_func_2_0(17)) /
         2.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_5_0_at_0()
    const {
  return (occ_func_2_0(0) * occ_func_2_0(16) +
          occ_func_2_0(14) * occ_func_2_0(0)) /
         2.;
}
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_5_0_at_1()
    const {
  return (occ_func_2_0(1) * occ_func_2_0(17) +
          occ_func_2_0(15) * occ_func_2_0(1)) /
         2.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_5_0_at_0(
    int occ_i, int occ_f) const {
  return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) *
         (occ_func_2_0(16) + occ_func_2_0(14)) / 2.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_5_0_at_1(
    int occ_i, int occ_f) const {
  return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) *
         (occ_func_2_0(17) + occ_func_2_0(15)) / 2.;
}

/**** Basis functions for orbit 6****
0.3333333 0.6666667 0.2500000 Va  O

2.3333333 1.6666667 0.2500000 Va  O

****/
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::eval_bfunc_6_0() const {
  return (occ_func_2_0(0) * occ_func_2_0(28) +
          occ_func_2_0(1) * occ_func_2_0(27) +
          occ_func_2_0(1) * occ_func_2_0(25) +
          occ_func_2_0(24) * occ_func_2_0(0) +
          occ_func_2_0(26) * occ_func_2_0(0) +
          occ_func_2_0(29) * occ_func_2_0(1)) /
         6.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_6_0_at_0()
    const {
  return (occ_func_2_0(0) * occ_func_2_0(28) +
          occ_func_2_0(18) * occ_func_2_0(0) +
          occ_func_2_0(24) * occ_func_2_0(0) +
          occ_func_2_0(0) * occ_func_2_0(22) +
          occ_func_2_0(26) * occ_func_2_0(0) +
          occ_func_2_0(0) * occ_func_2_0(20)) /
         6.;
}
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_6_0_at_1()
    const {
  return (occ_func_2_0(1) * occ_func_2_0(27) +
          occ_func_2_0(21) * occ_func_2_0(1) +
          occ_func_2_0(1) * occ_func_2_0(25) +
          occ_func_2_0(23) * occ_func_2_0(1) +
          occ_func_2_0(29) * occ_func_2_0(1) +
          occ_func_2_0(1) * occ_func_2_0(19)) /
         6.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_6_0_at_0(
    int occ_i, int occ_f) const {
  return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) *
         (occ_func_2_0(28) + occ_func_2_0(18) + occ_func_2_0(24) +
          occ_func_2_0(22) + occ_func_2_0(26) + occ_func_2_0(20)) /
         6.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_6_0_at_1(
    int occ_i, int occ_f) const {
  return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) *
         (occ_func_2_0(27) + occ_func_2_0(21) + occ_func_2_0(25) +
          occ_func_2_0(23) + occ_func_2_0(29) + occ_func_2_0(19)) /
         6.;
}

/**** Basis functions for orbit 7****
0.3333333 0.6666667 0.2500000 Va  O

0.3333333 1.6666667 0.2500000 Va  O

1.3333333 1.6666667 0.2500000 Va  O

****/
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::eval_bfunc_7_0() const {
  return (occ_func_2_0(0) * occ_func_2_0(8) * occ_func_2_0(12) +
          occ_func_2_0(11) * occ_func_2_0(1) * occ_func_2_0(13) +
          occ_func_2_0(10) * occ_func_2_0(12) * occ_func_2_0(0) +
          occ_func_2_0(13) * occ_func_2_0(9) * occ_func_2_0(1)) /
         4.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_7_0_at_0()
    const {
  return (occ_func_2_0(0) * occ_func_2_0(8) * occ_func_2_0(12) +
          occ_func_2_0(6) * occ_func_2_0(0) * occ_func_2_0(10) +
          occ_func_2_0(2) * occ_func_2_0(4) * occ_func_2_0(0) +
          occ_func_2_0(10) * occ_func_2_0(12) * occ_func_2_0(0) +
          occ_func_2_0(0) * occ_func_2_0(8) * occ_func_2_0(4) +
          occ_func_2_0(6) * occ_func_2_0(0) * occ_func_2_0(2)) /
         4.;
}
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_7_0_at_1()
    const {
  return (occ_func_2_0(11) * occ_func_2_0(1) * occ_func_2_0(13) +
          occ_func_2_0(1) * occ_func_2_0(5) * occ_func_2_0(9) +
          occ_func_2_0(7) * occ_func_2_0(3) * occ_func_2_0(1) +
          occ_func_2_0(13) * occ_func_2_0(9) * occ_func_2_0(1) +
          occ_func_2_0(11) * occ_func_2_0(1) * occ_func_2_0(7) +
          occ_func_2_0(1) * occ_func_2_0(5) * occ_func_2_0(3)) /
         4.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_7_0_at_0(
    int occ_i, int occ_f) const {
  return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) *
         (occ_func_2_0(8) * occ_func_2_0(12) +
          occ_func_2_0(6) * occ_func_2_0(10) +
          occ_func_2_0(2) * occ_func_2_0(4) +
          occ_func_2_0(10) * occ_func_2_0(12) +
          occ_func_2_0(8) * occ_func_2_0(4) +
          occ_func_2_0(6) * occ_func_2_0(2)) /
         4.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_7_0_at_1(
    int occ_i, int occ_f) const {
  return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) *
         (occ_func_2_0(11) * occ_func_2_0(13) +
          occ_func_2_0(5) * occ_func_2_0(9) +
          occ_func_2_0(7) * occ_func_2_0(3) +
          occ_func_2_0(13) * occ_func_2_0(9) +
          occ_func_2_0(11) * occ_func_2_0(7) +
          occ_func_2_0(5) * occ_func_2_0(3)) /
         4.;
}

/**** Basis functions for orbit 8****
0.3333333 0.6666667 0.2500000 Va  O

0.3333333 0.6666667 0.7500000 Va  O

0.3333333 1.6666667 0.2500000 Va  O

****/
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::eval_bfunc_8_0() const {
  return (occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(8) +
          occ_func_2_0(11) * occ_func_3_0(48) * occ_func_2_0(1) +
          occ_func_2_0(1) * occ_func_3_0(16) * occ_func_2_0(13) +
          occ_func_2_0(12) * occ_func_3_0(13) * occ_func_2_0(0) +
          occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(10) +
          occ_func_2_0(16) * occ_func_3_0(1) * occ_func_2_0(44) +
          occ_func_2_0(12) * occ_func_3_0(51) * occ_func_2_0(0) +
          occ_func_2_0(16) * occ_func_3_0(1) * occ_func_2_0(48) +
          occ_func_2_0(9) * occ_func_3_0(44) * occ_func_2_0(1) +
          occ_func_2_0(11) * occ_func_3_0(10) * occ_func_2_0(1) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(13) +
          occ_func_2_0(9) * occ_func_3_0(8) * occ_func_2_0(1) +
          occ_func_2_0(8) * occ_func_3_0(9) * occ_func_2_0(0) +
          occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(12) +
          occ_func_2_0(10) * occ_func_3_0(11) * occ_func_2_0(0) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(9) +
          occ_func_2_0(1) * occ_func_3_0(16) * occ_func_2_0(11) +
          occ_func_2_0(13) * occ_func_3_0(52) * occ_func_2_0(1) +
          occ_func_2_0(1) * occ_func_3_0(16) * occ_func_2_0(9) +
          occ_func_2_0(16) * occ_func_3_0(1) * occ_func_2_0(52) +
          occ_func_2_0(10) * occ_func_3_0(47) * occ_func_2_0(0) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(11) +
          occ_func_2_0(13) * occ_func_3_0(12) * occ_func_2_0(1) +
          occ_func_2_0(8) * occ_func_3_0(43) * occ_func_2_0(0)) /
         24.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_8_0_at_0()
    const {
  return (occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(8) +
          occ_func_2_0(6) * occ_func_3_0(7) * occ_func_2_0(0) +
          occ_func_2_0(15) * occ_func_3_0(0) * occ_func_2_0(35) +
          occ_func_2_0(15) * occ_func_3_0(0) * occ_func_2_0(51) +
          occ_func_2_0(12) * occ_func_3_0(13) * occ_func_2_0(0) +
          occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(2) +
          occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(10) +
          occ_func_2_0(4) * occ_func_3_0(5) * occ_func_2_0(0) +
          occ_func_2_0(0) * occ_func_3_0(15) * occ_func_2_0(8) +
          occ_func_2_0(6) * occ_func_3_0(39) * occ_func_2_0(0) +
          occ_func_2_0(12) * occ_func_3_0(51) * occ_func_2_0(0) +
          occ_func_2_0(0) * occ_func_3_0(15) * occ_func_2_0(2) +
          occ_func_2_0(0) * occ_func_3_0(15) * occ_func_2_0(10) +
          occ_func_2_0(4) * occ_func_3_0(35) * occ_func_2_0(0) +
          occ_func_2_0(15) * occ_func_3_0(0) * occ_func_2_0(39) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(5) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(13) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(7) +
          occ_func_2_0(8) * occ_func_3_0(9) * occ_func_2_0(0) +
          occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(6) +
          occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(12) +
          occ_func_2_0(2) * occ_func_3_0(3) * occ_func_2_0(0) +
          occ_func_2_0(10) * occ_func_3_0(11) * occ_func_2_0(0) +
          occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(4) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(9) +
          occ_func_2_0(15) * occ_func_3_0(0) * occ_func_2_0(47) +
          occ_func_2_0(15) * occ_func_3_0(0) * occ_func_2_0(31) +
          occ_func_2_0(15) * occ_func_3_0(0) * occ_func_2_0(43) +
          occ_func_2_0(0) * occ_func_3_0(15) * occ_func_2_0(12) +
          occ_func_2_0(2) * occ_func_3_0(31) * occ_func_2_0(0) +
          occ_func_2_0(10) * occ_func_3_0(47) * occ_func_2_0(0) +
          occ_func_2_0(0) * occ_func_3_0(15) * occ_func_2_0(4) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(11) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(3) +
          occ_func_2_0(8) * occ_func_3_0(43) * occ_func_2_0(0) +
          occ_func_2_0(0) * occ_func_3_0(15) * occ_func_2_0(6)) /
         24.;
}
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_8_0_at_1()
    const {
  return (occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(8) +
          occ_func_2_0(11) * occ_func_3_0(48) * occ_func_2_0(1) +
          occ_func_2_0(1) * occ_func_3_0(16) * occ_func_2_0(5) +
          occ_func_2_0(1) * occ_func_3_0(16) * occ_func_2_0(13) +
          occ_func_2_0(3) * occ_func_3_0(32) * occ_func_2_0(1) +
          occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(2) +
          occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(10) +
          occ_func_2_0(16) * occ_func_3_0(1) * occ_func_2_0(44) +
          occ_func_2_0(16) * occ_func_3_0(1) * occ_func_2_0(32) +
          occ_func_2_0(16) * occ_func_3_0(1) * occ_func_2_0(48) +
          occ_func_2_0(9) * occ_func_3_0(44) * occ_func_2_0(1) +
          occ_func_2_0(1) * occ_func_3_0(16) * occ_func_2_0(7) +
          occ_func_2_0(11) * occ_func_3_0(10) * occ_func_2_0(1) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(5) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(13) +
          occ_func_2_0(3) * occ_func_3_0(2) * occ_func_2_0(1) +
          occ_func_2_0(9) * occ_func_3_0(8) * occ_func_2_0(1) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(7) +
          occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(6) +
          occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(12) +
          occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(4) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(9) +
          occ_func_2_0(7) * occ_func_3_0(6) * occ_func_2_0(1) +
          occ_func_2_0(1) * occ_func_3_0(16) * occ_func_2_0(11) +
          occ_func_2_0(5) * occ_func_3_0(36) * occ_func_2_0(1) +
          occ_func_2_0(13) * occ_func_3_0(52) * occ_func_2_0(1) +
          occ_func_2_0(1) * occ_func_3_0(16) * occ_func_2_0(3) +
          occ_func_2_0(1) * occ_func_3_0(16) * occ_func_2_0(9) +
          occ_func_2_0(7) * occ_func_3_0(40) * occ_func_2_0(1) +
          occ_func_2_0(16) * occ_func_3_0(1) * occ_func_2_0(52) +
          occ_func_2_0(16) * occ_func_3_0(1) * occ_func_2_0(36) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(11) +
          occ_func_2_0(5) * occ_func_3_0(4) * occ_func_2_0(1) +
          occ_func_2_0(13) * occ_func_3_0(12) * occ_func_2_0(1) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(3) +
          occ_func_2_0(16) * occ_func_3_0(1) * occ_func_2_0(40)) /
         24.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_8_0_at_0(
    int occ_i, int occ_f) const {
  return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) *
         (occ_func_3_0(1) * occ_func_2_0(8) +
          occ_func_2_0(6) * occ_func_3_0(7) +
          occ_func_2_0(15) * occ_func_2_0(35) +
          occ_func_2_0(15) * occ_func_2_0(51) +
          occ_func_2_0(12) * occ_func_3_0(13) +
          occ_func_3_0(1) * occ_func_2_0(2) +
          occ_func_3_0(1) * occ_func_2_0(10) +
          occ_func_2_0(4) * occ_func_3_0(5) +
          occ_func_3_0(15) * occ_func_2_0(8) +
          occ_func_2_0(6) * occ_func_3_0(39) +
          occ_func_2_0(12) * occ_func_3_0(51) +
          occ_func_3_0(15) * occ_func_2_0(2) +
          occ_func_3_0(15) * occ_func_2_0(10) +
          occ_func_2_0(4) * occ_func_3_0(35) +
          occ_func_2_0(15) * occ_func_2_0(39) +
          occ_func_2_0(1) * occ_func_2_0(5) +
          occ_func_2_0(1) * occ_func_2_0(13) +
          occ_func_2_0(1) * occ_func_2_0(7) +
          occ_func_2_0(8) * occ_func_3_0(9) +
          occ_func_3_0(1) * occ_func_2_0(6) +
          occ_func_3_0(1) * occ_func_2_0(12) +
          occ_func_2_0(2) * occ_func_3_0(3) +
          occ_func_2_0(10) * occ_func_3_0(11) +
          occ_func_3_0(1) * occ_func_2_0(4) +
          occ_func_2_0(1) * occ_func_2_0(9) +
          occ_func_2_0(15) * occ_func_2_0(47) +
          occ_func_2_0(15) * occ_func_2_0(31) +
          occ_func_2_0(15) * occ_func_2_0(43) +
          occ_func_3_0(15) * occ_func_2_0(12) +
          occ_func_2_0(2) * occ_func_3_0(31) +
          occ_func_2_0(10) * occ_func_3_0(47) +
          occ_func_3_0(15) * occ_func_2_0(4) +
          occ_func_2_0(1) * occ_func_2_0(11) +
          occ_func_2_0(1) * occ_func_2_0(3) +
          occ_func_2_0(8) * occ_func_3_0(43) +
          occ_func_3_0(15) * occ_func_2_0(6)) /
         24.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_8_0_at_1(
    int occ_i, int occ_f) const {
  return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) *
         (occ_func_2_0(0) * occ_func_2_0(8) +
          occ_func_2_0(11) * occ_func_3_0(48) +
          occ_func_3_0(16) * occ_func_2_0(5) +
          occ_func_3_0(16) * occ_func_2_0(13) +
          occ_func_2_0(3) * occ_func_3_0(32) +
          occ_func_2_0(0) * occ_func_2_0(2) +
          occ_func_2_0(0) * occ_func_2_0(10) +
          occ_func_2_0(16) * occ_func_2_0(44) +
          occ_func_2_0(16) * occ_func_2_0(32) +
          occ_func_2_0(16) * occ_func_2_0(48) +
          occ_func_2_0(9) * occ_func_3_0(44) +
          occ_func_3_0(16) * occ_func_2_0(7) +
          occ_func_2_0(11) * occ_func_3_0(10) +
          occ_func_3_0(0) * occ_func_2_0(5) +
          occ_func_3_0(0) * occ_func_2_0(13) +
          occ_func_2_0(3) * occ_func_3_0(2) +
          occ_func_2_0(9) * occ_func_3_0(8) +
          occ_func_3_0(0) * occ_func_2_0(7) +
          occ_func_2_0(0) * occ_func_2_0(6) +
          occ_func_2_0(0) * occ_func_2_0(12) +
          occ_func_2_0(0) * occ_func_2_0(4) +
          occ_func_3_0(0) * occ_func_2_0(9) +
          occ_func_2_0(7) * occ_func_3_0(6) +
          occ_func_3_0(16) * occ_func_2_0(11) +
          occ_func_2_0(5) * occ_func_3_0(36) +
          occ_func_2_0(13) * occ_func_3_0(52) +
          occ_func_3_0(16) * occ_func_2_0(3) +
          occ_func_3_0(16) * occ_func_2_0(9) +
          occ_func_2_0(7) * occ_func_3_0(40) +
          occ_func_2_0(16) * occ_func_2_0(52) +
          occ_func_2_0(16) * occ_func_2_0(36) +
          occ_func_3_0(0) * occ_func_2_0(11) +
          occ_func_2_0(5) * occ_func_3_0(4) +
          occ_func_2_0(13) * occ_func_3_0(12) +
          occ_func_3_0(0) * occ_func_2_0(3) +
          occ_func_2_0(16) * occ_func_2_0(40)) /
         24.;
}

/**** Basis functions for orbit 9****
0.3333333 0.6666667 0.2500000 Va  O

0.3333333 1.6666667 0.2500000 Va  O

1.3333333 1.6666667 -0.2500000 Va  O

****/
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::eval_bfunc_9_0() const {
  return (occ_func_2_0(0) * occ_func_2_0(8) * occ_func_3_0(51) +
          occ_func_2_0(11) * occ_func_2_0(1) * occ_func_3_0(12) +
          occ_func_2_0(1) * occ_func_2_0(13) * occ_func_3_0(10) +
          occ_func_2_0(12) * occ_func_2_0(0) * occ_func_3_0(43) +
          occ_func_2_0(44) * occ_func_2_0(52) * occ_func_3_0(1) +
          occ_func_2_0(10) * occ_func_2_0(12) * occ_func_3_0(1) +
          occ_func_2_0(12) * occ_func_2_0(0) * occ_func_3_0(11) +
          occ_func_2_0(0) * occ_func_2_0(10) * occ_func_3_0(13) +
          occ_func_2_0(13) * occ_func_2_0(11) * occ_func_3_0(0) +
          occ_func_2_0(51) * occ_func_2_0(43) * occ_func_3_0(0) +
          occ_func_2_0(1) * occ_func_2_0(13) * occ_func_3_0(44) +
          occ_func_2_0(9) * occ_func_2_0(1) * occ_func_3_0(52)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_9_0_at_0()
    const {
  return (occ_func_2_0(0) * occ_func_2_0(8) * occ_func_3_0(51) +
          occ_func_2_0(6) * occ_func_2_0(0) * occ_func_3_0(47) +
          occ_func_2_0(7) * occ_func_2_0(3) * occ_func_3_0(0) +
          occ_func_2_0(5) * occ_func_2_0(9) * occ_func_3_0(0) +
          occ_func_2_0(12) * occ_func_2_0(0) * occ_func_3_0(43) +
          occ_func_2_0(0) * occ_func_2_0(2) * occ_func_3_0(35) +
          occ_func_2_0(0) * occ_func_2_0(10) * occ_func_3_0(39) +
          occ_func_2_0(4) * occ_func_2_0(0) * occ_func_3_0(31) +
          occ_func_2_0(0) * occ_func_2_0(8) * occ_func_3_0(5) +
          occ_func_2_0(6) * occ_func_2_0(0) * occ_func_3_0(3) +
          occ_func_2_0(12) * occ_func_2_0(0) * occ_func_3_0(11) +
          occ_func_2_0(0) * occ_func_2_0(2) * occ_func_3_0(7) +
          occ_func_2_0(0) * occ_func_2_0(10) * occ_func_3_0(13) +
          occ_func_2_0(4) * occ_func_2_0(0) * occ_func_3_0(9) +
          occ_func_2_0(13) * occ_func_2_0(11) * occ_func_3_0(0) +
          occ_func_2_0(51) * occ_func_2_0(43) * occ_func_3_0(0) +
          occ_func_2_0(39) * occ_func_2_0(47) * occ_func_3_0(0) +
          occ_func_2_0(35) * occ_func_2_0(31) * occ_func_3_0(0)) /
         12.;
}
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_9_0_at_1()
    const {
  return (occ_func_2_0(32) * occ_func_2_0(36) * occ_func_3_0(1) +
          occ_func_2_0(11) * occ_func_2_0(1) * occ_func_3_0(12) +
          occ_func_2_0(1) * occ_func_2_0(5) * occ_func_3_0(8) +
          occ_func_2_0(1) * occ_func_2_0(13) * occ_func_3_0(10) +
          occ_func_2_0(3) * occ_func_2_0(1) * occ_func_3_0(6) +
          occ_func_2_0(48) * occ_func_2_0(40) * occ_func_3_0(1) +
          occ_func_2_0(44) * occ_func_2_0(52) * occ_func_3_0(1) +
          occ_func_2_0(10) * occ_func_2_0(12) * occ_func_3_0(1) +
          occ_func_2_0(8) * occ_func_2_0(4) * occ_func_3_0(1) +
          occ_func_2_0(2) * occ_func_2_0(6) * occ_func_3_0(1) +
          occ_func_2_0(9) * occ_func_2_0(1) * occ_func_3_0(4) +
          occ_func_2_0(1) * occ_func_2_0(7) * occ_func_3_0(2) +
          occ_func_2_0(11) * occ_func_2_0(1) * occ_func_3_0(40) +
          occ_func_2_0(1) * occ_func_2_0(5) * occ_func_3_0(32) +
          occ_func_2_0(1) * occ_func_2_0(13) * occ_func_3_0(44) +
          occ_func_2_0(3) * occ_func_2_0(1) * occ_func_3_0(36) +
          occ_func_2_0(9) * occ_func_2_0(1) * occ_func_3_0(52) +
          occ_func_2_0(1) * occ_func_2_0(7) * occ_func_3_0(48)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_9_0_at_0(
    int occ_i, int occ_f) const {
  return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) *
         (occ_func_2_0(8) * occ_func_3_0(51) +
          occ_func_2_0(6) * occ_func_3_0(47) +
          occ_func_2_0(7) * occ_func_2_0(3) +
          occ_func_2_0(5) * occ_func_2_0(9) +
          occ_func_2_0(12) * occ_func_3_0(43) +
          occ_func_2_0(2) * occ_func_3_0(35) +
          occ_func_2_0(10) * occ_func_3_0(39) +
          occ_func_2_0(4) * occ_func_3_0(31) +
          occ_func_2_0(8) * occ_func_3_0(5) +
          occ_func_2_0(6) * occ_func_3_0(3) +
          occ_func_2_0(12) * occ_func_3_0(11) +
          occ_func_2_0(2) * occ_func_3_0(7) +
          occ_func_2_0(10) * occ_func_3_0(13) +
          occ_func_2_0(4) * occ_func_3_0(9) +
          occ_func_2_0(13) * occ_func_2_0(11) +
          occ_func_2_0(51) * occ_func_2_0(43) +
          occ_func_2_0(39) * occ_func_2_0(47) +
          occ_func_2_0(35) * occ_func_2_0(31)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_9_0_at_1(
    int occ_i, int occ_f) const {
  return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) *
         (occ_func_2_0(32) * occ_func_2_0(36) +
          occ_func_2_0(11) * occ_func_3_0(12) +
          occ_func_2_0(5) * occ_func_3_0(8) +
          occ_func_2_0(13) * occ_func_3_0(10) +
          occ_func_2_0(3) * occ_func_3_0(6) +
          occ_func_2_0(48) * occ_func_2_0(40) +
          occ_func_2_0(44) * occ_func_2_0(52) +
          occ_func_2_0(10) * occ_func_2_0(12) +
          occ_func_2_0(8) * occ_func_2_0(4) +
          occ_func_2_0(2) * occ_func_2_0(6) +
          occ_func_2_0(9) * occ_func_3_0(4) +
          occ_func_2_0(7) * occ_func_3_0(2) +
          occ_func_2_0(11) * occ_func_3_0(40) +
          occ_func_2_0(5) * occ_func_3_0(32) +
          occ_func_2_0(13) * occ_func_3_0(44) +
          occ_func_2_0(3) * occ_func_3_0(36) +
          occ_func_2_0(9) * occ_func_3_0(52) +
          occ_func_2_0(7) * occ_func_3_0(48)) /
         12.;
}

/**** Basis functions for orbit 10****
0.3333333 0.6666667 0.2500000 Va  O

0.3333333 1.6666667 0.2500000 Va  O

1.3333333 1.6666667 0.7500000 Va  O

****/
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::eval_bfunc_10_0() const {
  return (occ_func_2_0(0) * occ_func_2_0(8) * occ_func_3_0(13) +
          occ_func_2_0(11) * occ_func_2_0(1) * occ_func_3_0(52) +
          occ_func_2_0(1) * occ_func_2_0(13) * occ_func_3_0(48) +
          occ_func_2_0(12) * occ_func_2_0(0) * occ_func_3_0(9) +
          occ_func_2_0(8) * occ_func_2_0(12) * occ_func_3_0(1) +
          occ_func_2_0(48) * occ_func_2_0(52) * occ_func_3_0(1) +
          occ_func_2_0(12) * occ_func_2_0(0) * occ_func_3_0(47) +
          occ_func_2_0(0) * occ_func_2_0(10) * occ_func_3_0(51) +
          occ_func_2_0(51) * occ_func_2_0(47) * occ_func_3_0(0) +
          occ_func_2_0(13) * occ_func_2_0(9) * occ_func_3_0(0) +
          occ_func_2_0(1) * occ_func_2_0(13) * occ_func_3_0(8) +
          occ_func_2_0(9) * occ_func_2_0(1) * occ_func_3_0(12)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_10_0_at_0()
    const {
  return (occ_func_2_0(0) * occ_func_2_0(8) * occ_func_3_0(13) +
          occ_func_2_0(6) * occ_func_2_0(0) * occ_func_3_0(11) +
          occ_func_2_0(39) * occ_func_2_0(31) * occ_func_3_0(0) +
          occ_func_2_0(35) * occ_func_2_0(43) * occ_func_3_0(0) +
          occ_func_2_0(12) * occ_func_2_0(0) * occ_func_3_0(9) +
          occ_func_2_0(0) * occ_func_2_0(2) * occ_func_3_0(5) +
          occ_func_2_0(0) * occ_func_2_0(10) * occ_func_3_0(7) +
          occ_func_2_0(4) * occ_func_2_0(0) * occ_func_3_0(3) +
          occ_func_2_0(0) * occ_func_2_0(8) * occ_func_3_0(35) +
          occ_func_2_0(6) * occ_func_2_0(0) * occ_func_3_0(31) +
          occ_func_2_0(12) * occ_func_2_0(0) * occ_func_3_0(47) +
          occ_func_2_0(0) * occ_func_2_0(2) * occ_func_3_0(39) +
          occ_func_2_0(0) * occ_func_2_0(10) * occ_func_3_0(51) +
          occ_func_2_0(4) * occ_func_2_0(0) * occ_func_3_0(43) +
          occ_func_2_0(51) * occ_func_2_0(47) * occ_func_3_0(0) +
          occ_func_2_0(13) * occ_func_2_0(9) * occ_func_3_0(0) +
          occ_func_2_0(7) * occ_func_2_0(11) * occ_func_3_0(0) +
          occ_func_2_0(5) * occ_func_2_0(3) * occ_func_3_0(0)) /
         12.;
}
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_10_0_at_1()
    const {
  return (occ_func_2_0(2) * occ_func_2_0(4) * occ_func_3_0(1) +
          occ_func_2_0(11) * occ_func_2_0(1) * occ_func_3_0(52) +
          occ_func_2_0(1) * occ_func_2_0(5) * occ_func_3_0(44) +
          occ_func_2_0(1) * occ_func_2_0(13) * occ_func_3_0(48) +
          occ_func_2_0(3) * occ_func_2_0(1) * occ_func_3_0(40) +
          occ_func_2_0(10) * occ_func_2_0(6) * occ_func_3_0(1) +
          occ_func_2_0(8) * occ_func_2_0(12) * occ_func_3_0(1) +
          occ_func_2_0(48) * occ_func_2_0(52) * occ_func_3_0(1) +
          occ_func_2_0(44) * occ_func_2_0(36) * occ_func_3_0(1) +
          occ_func_2_0(32) * occ_func_2_0(40) * occ_func_3_0(1) +
          occ_func_2_0(9) * occ_func_2_0(1) * occ_func_3_0(36) +
          occ_func_2_0(1) * occ_func_2_0(7) * occ_func_3_0(32) +
          occ_func_2_0(11) * occ_func_2_0(1) * occ_func_3_0(6) +
          occ_func_2_0(1) * occ_func_2_0(5) * occ_func_3_0(2) +
          occ_func_2_0(1) * occ_func_2_0(13) * occ_func_3_0(8) +
          occ_func_2_0(3) * occ_func_2_0(1) * occ_func_3_0(4) +
          occ_func_2_0(9) * occ_func_2_0(1) * occ_func_3_0(12) +
          occ_func_2_0(1) * occ_func_2_0(7) * occ_func_3_0(10)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_10_0_at_0(
    int occ_i, int occ_f) const {
  return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) *
         (occ_func_2_0(8) * occ_func_3_0(13) +
          occ_func_2_0(6) * occ_func_3_0(11) +
          occ_func_2_0(39) * occ_func_2_0(31) +
          occ_func_2_0(35) * occ_func_2_0(43) +
          occ_func_2_0(12) * occ_func_3_0(9) +
          occ_func_2_0(2) * occ_func_3_0(5) +
          occ_func_2_0(10) * occ_func_3_0(7) +
          occ_func_2_0(4) * occ_func_3_0(3) +
          occ_func_2_0(8) * occ_func_3_0(35) +
          occ_func_2_0(6) * occ_func_3_0(31) +
          occ_func_2_0(12) * occ_func_3_0(47) +
          occ_func_2_0(2) * occ_func_3_0(39) +
          occ_func_2_0(10) * occ_func_3_0(51) +
          occ_func_2_0(4) * occ_func_3_0(43) +
          occ_func_2_0(51) * occ_func_2_0(47) +
          occ_func_2_0(13) * occ_func_2_0(9) +
          occ_func_2_0(7) * occ_func_2_0(11) +
          occ_func_2_0(5) * occ_func_2_0(3)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_10_0_at_1(
    int occ_i, int occ_f) const {
  return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) *
         (occ_func_2_0(2) * occ_func_2_0(4) +
          occ_func_2_0(11) * occ_func_3_0(52) +
          occ_func_2_0(5) * occ_func_3_0(44) +
          occ_func_2_0(13) * occ_func_3_0(48) +
          occ_func_2_0(3) * occ_func_3_0(40) +
          occ_func_2_0(10) * occ_func_2_0(6) +
          occ_func_2_0(8) * occ_func_2_0(12) +
          occ_func_2_0(48) * occ_func_2_0(52) +
          occ_func_2_0(44) * occ_func_2_0(36) +
          occ_func_2_0(32) * occ_func_2_0(40) +
          occ_func_2_0(9) * occ_func_3_0(36) +
          occ_func_2_0(7) * occ_func_3_0(32) +
          occ_func_2_0(11) * occ_func_3_0(6) +
          occ_func_2_0(5) * occ_func_3_0(2) +
          occ_func_2_0(13) * occ_func_3_0(8) +
          occ_func_2_0(3) * occ_func_3_0(4) +
          occ_func_2_0(9) * occ_func_3_0(12) +
          occ_func_2_0(7) * occ_func_3_0(10)) /
         12.;
}

/**** Basis functions for orbit 11****
0.3333333 0.6666667 0.2500000 Va  O

0.3333333 0.6666667 0.7500000 Va  O

1.3333333 1.6666667 0.2500000 Va  O

1.3333333 1.6666667 0.7500000 Va  O

****/
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::eval_bfunc_11_0() const {
  return (occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(12) *
              occ_func_3_0(13) +
          occ_func_2_0(1) * occ_func_3_0(16) * occ_func_2_0(9) *
              occ_func_3_0(44) +
          occ_func_2_0(1) * occ_func_3_0(16) * occ_func_2_0(11) *
              occ_func_3_0(48) +
          occ_func_2_0(10) * occ_func_3_0(11) * occ_func_2_0(0) *
              occ_func_3_0(1) +
          occ_func_2_0(8) * occ_func_3_0(9) * occ_func_2_0(0) *
              occ_func_3_0(1) +
          occ_func_2_0(16) * occ_func_3_0(1) * occ_func_2_0(52) *
              occ_func_3_0(13)) /
         6.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_11_0_at_0()
    const {
  return (occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(12) *
              occ_func_3_0(13) +
          occ_func_2_0(2) * occ_func_3_0(3) * occ_func_2_0(0) *
              occ_func_3_0(1) +
          occ_func_2_0(15) * occ_func_3_0(0) * occ_func_2_0(43) *
              occ_func_3_0(8) +
          occ_func_2_0(39) * occ_func_3_0(6) * occ_func_2_0(15) *
              occ_func_3_0(0) +
          occ_func_2_0(15) * occ_func_3_0(0) * occ_func_2_0(47) *
              occ_func_3_0(10) +
          occ_func_2_0(35) * occ_func_3_0(4) * occ_func_2_0(15) *
              occ_func_3_0(0) +
          occ_func_2_0(10) * occ_func_3_0(11) * occ_func_2_0(0) *
              occ_func_3_0(1) +
          occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(4) *
              occ_func_3_0(5) +
          occ_func_2_0(8) * occ_func_3_0(9) * occ_func_2_0(0) *
              occ_func_3_0(1) +
          occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(6) *
              occ_func_3_0(7) +
          occ_func_2_0(0) * occ_func_3_0(15) * occ_func_2_0(12) *
              occ_func_3_0(51) +
          occ_func_2_0(2) * occ_func_3_0(31) * occ_func_2_0(0) *
              occ_func_3_0(15)) /
         6.;
}
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_11_0_at_1()
    const {
  return (occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(12) *
              occ_func_3_0(13) +
          occ_func_2_0(2) * occ_func_3_0(3) * occ_func_2_0(0) *
              occ_func_3_0(1) +
          occ_func_2_0(1) * occ_func_3_0(16) * occ_func_2_0(9) *
              occ_func_3_0(44) +
          occ_func_2_0(7) * occ_func_3_0(40) * occ_func_2_0(1) *
              occ_func_3_0(16) +
          occ_func_2_0(1) * occ_func_3_0(16) * occ_func_2_0(11) *
              occ_func_3_0(48) +
          occ_func_2_0(5) * occ_func_3_0(36) * occ_func_2_0(1) *
              occ_func_3_0(16) +
          occ_func_2_0(10) * occ_func_3_0(11) * occ_func_2_0(0) *
              occ_func_3_0(1) +
          occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(4) *
              occ_func_3_0(5) +
          occ_func_2_0(8) * occ_func_3_0(9) * occ_func_2_0(0) *
              occ_func_3_0(1) +
          occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(6) *
              occ_func_3_0(7) +
          occ_func_2_0(16) * occ_func_3_0(1) * occ_func_2_0(52) *
              occ_func_3_0(13) +
          occ_func_2_0(32) * occ_func_3_0(3) * occ_func_2_0(16) *
              occ_func_3_0(1)) /
         6.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_11_0_at_0(
    int occ_i, int occ_f) const {
  return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) *
         (occ_func_3_0(1) * occ_func_2_0(12) * occ_func_3_0(13) +
          occ_func_2_0(2) * occ_func_3_0(3) * occ_func_3_0(1) +
          occ_func_2_0(15) * occ_func_2_0(43) * occ_func_3_0(8) +
          occ_func_2_0(39) * occ_func_3_0(6) * occ_func_2_0(15) +
          occ_func_2_0(15) * occ_func_2_0(47) * occ_func_3_0(10) +
          occ_func_2_0(35) * occ_func_3_0(4) * occ_func_2_0(15) +
          occ_func_2_0(10) * occ_func_3_0(11) * occ_func_3_0(1) +
          occ_func_3_0(1) * occ_func_2_0(4) * occ_func_3_0(5) +
          occ_func_2_0(8) * occ_func_3_0(9) * occ_func_3_0(1) +
          occ_func_3_0(1) * occ_func_2_0(6) * occ_func_3_0(7) +
          occ_func_3_0(15) * occ_func_2_0(12) * occ_func_3_0(51) +
          occ_func_2_0(2) * occ_func_3_0(31) * occ_func_3_0(15)) /
         6.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_11_0_at_1(
    int occ_i, int occ_f) const {
  return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) *
         (occ_func_2_0(0) * occ_func_2_0(12) * occ_func_3_0(13) +
          occ_func_2_0(2) * occ_func_3_0(3) * occ_func_2_0(0) +
          occ_func_3_0(16) * occ_func_2_0(9) * occ_func_3_0(44) +
          occ_func_2_0(7) * occ_func_3_0(40) * occ_func_3_0(16) +
          occ_func_3_0(16) * occ_func_2_0(11) * occ_func_3_0(48) +
          occ_func_2_0(5) * occ_func_3_0(36) * occ_func_3_0(16) +
          occ_func_2_0(10) * occ_func_3_0(11) * occ_func_2_0(0) +
          occ_func_2_0(0) * occ_func_2_0(4) * occ_func_3_0(5) +
          occ_func_2_0(8) * occ_func_3_0(9) * occ_func_2_0(0) +
          occ_func_2_0(0) * occ_func_2_0(6) * occ_func_3_0(7) +
          occ_func_2_0(16) * occ_func_2_0(52) * occ_func_3_0(13) +
          occ_func_2_0(32) * occ_func_3_0(3) * occ_func_2_0(16)) /
         6.;
}

/**** Basis functions for orbit 12****
0.3333333 0.6666667 0.2500000 Va  O

0.3333333 0.6666667 0.7500000 Va  O

1.3333333 0.6666667 0.2500000 Va  O

1.3333333 1.6666667 0.2500000 Va  O

****/
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::eval_bfunc_12_0() const {
  return (occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(10) *
              occ_func_2_0(12) +
          occ_func_2_0(1) * occ_func_3_0(16) * occ_func_2_0(13) *
              occ_func_2_0(9) +
          occ_func_2_0(9) * occ_func_3_0(44) * occ_func_2_0(1) *
              occ_func_2_0(13) +
          occ_func_2_0(10) * occ_func_3_0(11) * occ_func_2_0(12) *
              occ_func_2_0(0) +
          occ_func_2_0(12) * occ_func_3_0(13) * occ_func_2_0(0) *
              occ_func_2_0(10) +
          occ_func_2_0(12) * occ_func_3_0(51) * occ_func_2_0(0) *
              occ_func_2_0(8) +
          occ_func_2_0(8) * occ_func_3_0(43) * occ_func_2_0(12) *
              occ_func_2_0(0) +
          occ_func_2_0(16) * occ_func_3_0(1) * occ_func_2_0(44) *
              occ_func_2_0(52) +
          occ_func_2_0(13) * occ_func_3_0(52) * occ_func_2_0(9) *
              occ_func_2_0(1) +
          occ_func_2_0(13) * occ_func_3_0(12) * occ_func_2_0(11) *
              occ_func_2_0(1) +
          occ_func_2_0(11) * occ_func_3_0(10) * occ_func_2_0(1) *
              occ_func_2_0(13) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(13) *
              occ_func_2_0(11)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_12_0_at_0()
    const {
  return (occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(10) *
              occ_func_2_0(12) +
          occ_func_2_0(4) * occ_func_3_0(5) * occ_func_2_0(0) *
              occ_func_2_0(8) +
          occ_func_2_0(2) * occ_func_3_0(3) * occ_func_2_0(6) *
              occ_func_2_0(0) +
          occ_func_2_0(15) * occ_func_3_0(0) * occ_func_2_0(51) *
              occ_func_2_0(43) +
          occ_func_2_0(15) * occ_func_3_0(0) * occ_func_2_0(39) *
              occ_func_2_0(47) +
          occ_func_2_0(10) * occ_func_3_0(11) * occ_func_2_0(12) *
              occ_func_2_0(0) +
          occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(8) *
              occ_func_2_0(4) +
          occ_func_2_0(6) * occ_func_3_0(7) * occ_func_2_0(0) *
              occ_func_2_0(2) +
          occ_func_2_0(12) * occ_func_3_0(13) * occ_func_2_0(0) *
              occ_func_2_0(10) +
          occ_func_2_0(8) * occ_func_3_0(9) * occ_func_2_0(4) *
              occ_func_2_0(0) +
          occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(2) *
              occ_func_2_0(6) +
          occ_func_2_0(12) * occ_func_3_0(51) * occ_func_2_0(0) *
              occ_func_2_0(8) +
          occ_func_2_0(10) * occ_func_3_0(47) * occ_func_2_0(6) *
              occ_func_2_0(0) +
          occ_func_2_0(0) * occ_func_3_0(15) * occ_func_2_0(2) *
              occ_func_2_0(4) +
          occ_func_2_0(8) * occ_func_3_0(43) * occ_func_2_0(12) *
              occ_func_2_0(0) +
          occ_func_2_0(0) * occ_func_3_0(15) * occ_func_2_0(10) *
              occ_func_2_0(6) +
          occ_func_2_0(4) * occ_func_3_0(35) * occ_func_2_0(0) *
              occ_func_2_0(2) +
          occ_func_2_0(0) * occ_func_3_0(15) * occ_func_2_0(8) *
              occ_func_2_0(12) +
          occ_func_2_0(6) * occ_func_3_0(39) * occ_func_2_0(0) *
              occ_func_2_0(10) +
          occ_func_2_0(2) * occ_func_3_0(31) * occ_func_2_0(4) *
              occ_func_2_0(0) +
          occ_func_2_0(15) * occ_func_3_0(0) * occ_func_2_0(35) *
              occ_func_2_0(31) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(7) *
              occ_func_2_0(3) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(5) *
              occ_func_2_0(9) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(13) *
              occ_func_2_0(11)) /
         12.;
}
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_12_0_at_1()
    const {
  return (occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(10) *
              occ_func_2_0(12) +
          occ_func_2_0(1) * occ_func_3_0(16) * occ_func_2_0(13) *
              occ_func_2_0(9) +
          occ_func_2_0(7) * occ_func_3_0(40) * occ_func_2_0(11) *
              occ_func_2_0(1) +
          occ_func_2_0(3) * occ_func_3_0(32) * occ_func_2_0(1) *
              occ_func_2_0(5) +
          occ_func_2_0(9) * occ_func_3_0(44) * occ_func_2_0(1) *
              occ_func_2_0(13) +
          occ_func_2_0(1) * occ_func_3_0(16) * occ_func_2_0(7) *
              occ_func_2_0(11) +
          occ_func_2_0(5) * occ_func_3_0(36) * occ_func_2_0(3) *
              occ_func_2_0(1) +
          occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(8) *
              occ_func_2_0(4) +
          occ_func_2_0(0) * occ_func_3_0(1) * occ_func_2_0(2) *
              occ_func_2_0(6) +
          occ_func_2_0(16) * occ_func_3_0(1) * occ_func_2_0(32) *
              occ_func_2_0(36) +
          occ_func_2_0(16) * occ_func_3_0(1) * occ_func_2_0(48) *
              occ_func_2_0(40) +
          occ_func_2_0(16) * occ_func_3_0(1) * occ_func_2_0(44) *
              occ_func_2_0(52) +
          occ_func_2_0(13) * occ_func_3_0(52) * occ_func_2_0(9) *
              occ_func_2_0(1) +
          occ_func_2_0(11) * occ_func_3_0(48) * occ_func_2_0(1) *
              occ_func_2_0(7) +
          occ_func_2_0(1) * occ_func_3_0(16) * occ_func_2_0(5) *
              occ_func_2_0(3) +
          occ_func_2_0(13) * occ_func_3_0(12) * occ_func_2_0(11) *
              occ_func_2_0(1) +
          occ_func_2_0(9) * occ_func_3_0(8) * occ_func_2_0(1) *
              occ_func_2_0(5) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(7) *
              occ_func_2_0(3) +
          occ_func_2_0(11) * occ_func_3_0(10) * occ_func_2_0(1) *
              occ_func_2_0(13) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(5) *
              occ_func_2_0(9) +
          occ_func_2_0(7) * occ_func_3_0(6) * occ_func_2_0(3) *
              occ_func_2_0(1) +
          occ_func_2_0(1) * occ_func_3_0(0) * occ_func_2_0(13) *
              occ_func_2_0(11) +
          occ_func_2_0(5) * occ_func_3_0(4) * occ_func_2_0(9) *
              occ_func_2_0(1) +
          occ_func_2_0(3) * occ_func_3_0(2) * occ_func_2_0(1) *
              occ_func_2_0(7)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_12_0_at_0(
    int occ_i, int occ_f) const {
  return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) *
         (occ_func_3_0(1) * occ_func_2_0(10) * occ_func_2_0(12) +
          occ_func_2_0(4) * occ_func_3_0(5) * occ_func_2_0(8) +
          occ_func_2_0(2) * occ_func_3_0(3) * occ_func_2_0(6) +
          occ_func_2_0(15) * occ_func_2_0(51) * occ_func_2_0(43) +
          occ_func_2_0(15) * occ_func_2_0(39) * occ_func_2_0(47) +
          occ_func_2_0(10) * occ_func_3_0(11) * occ_func_2_0(12) +
          occ_func_3_0(1) * occ_func_2_0(8) * occ_func_2_0(4) +
          occ_func_2_0(6) * occ_func_3_0(7) * occ_func_2_0(2) +
          occ_func_2_0(12) * occ_func_3_0(13) * occ_func_2_0(10) +
          occ_func_2_0(8) * occ_func_3_0(9) * occ_func_2_0(4) +
          occ_func_3_0(1) * occ_func_2_0(2) * occ_func_2_0(6) +
          occ_func_2_0(12) * occ_func_3_0(51) * occ_func_2_0(8) +
          occ_func_2_0(10) * occ_func_3_0(47) * occ_func_2_0(6) +
          occ_func_3_0(15) * occ_func_2_0(2) * occ_func_2_0(4) +
          occ_func_2_0(8) * occ_func_3_0(43) * occ_func_2_0(12) +
          occ_func_3_0(15) * occ_func_2_0(10) * occ_func_2_0(6) +
          occ_func_2_0(4) * occ_func_3_0(35) * occ_func_2_0(2) +
          occ_func_3_0(15) * occ_func_2_0(8) * occ_func_2_0(12) +
          occ_func_2_0(6) * occ_func_3_0(39) * occ_func_2_0(10) +
          occ_func_2_0(2) * occ_func_3_0(31) * occ_func_2_0(4) +
          occ_func_2_0(15) * occ_func_2_0(35) * occ_func_2_0(31) +
          occ_func_2_0(1) * occ_func_2_0(7) * occ_func_2_0(3) +
          occ_func_2_0(1) * occ_func_2_0(5) * occ_func_2_0(9) +
          occ_func_2_0(1) * occ_func_2_0(13) * occ_func_2_0(11)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_12_0_at_1(
    int occ_i, int occ_f) const {
  return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) *
         (occ_func_2_0(0) * occ_func_2_0(10) * occ_func_2_0(12) +
          occ_func_3_0(16) * occ_func_2_0(13) * occ_func_2_0(9) +
          occ_func_2_0(7) * occ_func_3_0(40) * occ_func_2_0(11) +
          occ_func_2_0(3) * occ_func_3_0(32) * occ_func_2_0(5) +
          occ_func_2_0(9) * occ_func_3_0(44) * occ_func_2_0(13) +
          occ_func_3_0(16) * occ_func_2_0(7) * occ_func_2_0(11) +
          occ_func_2_0(5) * occ_func_3_0(36) * occ_func_2_0(3) +
          occ_func_2_0(0) * occ_func_2_0(8) * occ_func_2_0(4) +
          occ_func_2_0(0) * occ_func_2_0(2) * occ_func_2_0(6) +
          occ_func_2_0(16) * occ_func_2_0(32) * occ_func_2_0(36) +
          occ_func_2_0(16) * occ_func_2_0(48) * occ_func_2_0(40) +
          occ_func_2_0(16) * occ_func_2_0(44) * occ_func_2_0(52) +
          occ_func_2_0(13) * occ_func_3_0(52) * occ_func_2_0(9) +
          occ_func_2_0(11) * occ_func_3_0(48) * occ_func_2_0(7) +
          occ_func_3_0(16) * occ_func_2_0(5) * occ_func_2_0(3) +
          occ_func_2_0(13) * occ_func_3_0(12) * occ_func_2_0(11) +
          occ_func_2_0(9) * occ_func_3_0(8) * occ_func_2_0(5) +
          occ_func_3_0(0) * occ_func_2_0(7) * occ_func_2_0(3) +
          occ_func_2_0(11) * occ_func_3_0(10) * occ_func_2_0(13) +
          occ_func_3_0(0) * occ_func_2_0(5) * occ_func_2_0(9) +
          occ_func_2_0(7) * occ_func_3_0(6) * occ_func_2_0(3) +
          occ_func_3_0(0) * occ_func_2_0(13) * occ_func_2_0(11) +
          occ_func_2_0(5) * occ_func_3_0(4) * occ_func_2_0(9) +
          occ_func_2_0(3) * occ_func_3_0(2) * occ_func_2_0(7)) /
         12.;
}

/**** Basis functions for orbit 13****
0.3333333 0.6666667 0.2500000 Va  O

0.3333333 1.6666667 0.2500000 Va  O

1.3333333 1.6666667 0.2500000 Va  O

1.3333333 1.6666667 0.7500000 Va  O

****/
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::eval_bfunc_13_0() const {
  return (occ_func_2_0(0) * occ_func_2_0(8) * occ_func_2_0(12) *
              occ_func_3_0(13) +
          occ_func_2_0(11) * occ_func_2_0(1) * occ_func_2_0(13) *
              occ_func_3_0(52) +
          occ_func_2_0(1) * occ_func_2_0(13) * occ_func_2_0(11) *
              occ_func_3_0(48) +
          occ_func_2_0(12) * occ_func_2_0(0) * occ_func_2_0(8) *
              occ_func_3_0(9) +
          occ_func_2_0(8) * occ_func_2_0(12) * occ_func_2_0(0) *
              occ_func_3_0(1) +
          occ_func_2_0(48) * occ_func_2_0(52) * occ_func_2_0(16) *
              occ_func_3_0(1) +
          occ_func_2_0(12) * occ_func_2_0(0) * occ_func_2_0(10) *
              occ_func_3_0(47) +
          occ_func_2_0(0) * occ_func_2_0(10) * occ_func_2_0(12) *
              occ_func_3_0(51) +
          occ_func_2_0(13) * occ_func_2_0(11) * occ_func_2_0(1) *
              occ_func_3_0(16) +
          occ_func_2_0(13) * occ_func_2_0(9) * occ_func_2_0(1) *
              occ_func_3_0(0) +
          occ_func_2_0(1) * occ_func_2_0(13) * occ_func_2_0(9) *
              occ_func_3_0(8) +
          occ_func_2_0(9) * occ_func_2_0(1) * occ_func_2_0(13) *
              occ_func_3_0(12)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_13_0_at_0()
    const {
  return (occ_func_2_0(0) * occ_func_2_0(8) * occ_func_2_0(12) *
              occ_func_3_0(13) +
          occ_func_2_0(6) * occ_func_2_0(0) * occ_func_2_0(10) *
              occ_func_3_0(11) +
          occ_func_2_0(2) * occ_func_2_0(4) * occ_func_2_0(0) *
              occ_func_3_0(1) +
          occ_func_2_0(39) * occ_func_2_0(31) * occ_func_2_0(15) *
              occ_func_3_0(0) +
          occ_func_2_0(35) * occ_func_2_0(43) * occ_func_2_0(15) *
              occ_func_3_0(0) +
          occ_func_2_0(12) * occ_func_2_0(0) * occ_func_2_0(8) *
              occ_func_3_0(9) +
          occ_func_2_0(10) * occ_func_2_0(6) * occ_func_2_0(0) *
              occ_func_3_0(1) +
          occ_func_2_0(0) * occ_func_2_0(2) * occ_func_2_0(4) *
              occ_func_3_0(5) +
          occ_func_2_0(8) * occ_func_2_0(12) * occ_func_2_0(0) *
              occ_func_3_0(1) +
          occ_func_2_0(0) * occ_func_2_0(10) * occ_func_2_0(6) *
              occ_func_3_0(7) +
          occ_func_2_0(4) * occ_func_2_0(0) * occ_func_2_0(2) *
              occ_func_3_0(3) +
          occ_func_2_0(10) * occ_func_2_0(12) * occ_func_2_0(0) *
              occ_func_3_0(15) +
          occ_func_2_0(0) * occ_func_2_0(8) * occ_func_2_0(4) *
              occ_func_3_0(35) +
          occ_func_2_0(6) * occ_func_2_0(0) * occ_func_2_0(2) *
              occ_func_3_0(31) +
          occ_func_2_0(12) * occ_func_2_0(0) * occ_func_2_0(10) *
              occ_func_3_0(47) +
          occ_func_2_0(8) * occ_func_2_0(4) * occ_func_2_0(0) *
              occ_func_3_0(15) +
          occ_func_2_0(0) * occ_func_2_0(2) * occ_func_2_0(6) *
              occ_func_3_0(39) +
          occ_func_2_0(0) * occ_func_2_0(10) * occ_func_2_0(12) *
              occ_func_3_0(51) +
          occ_func_2_0(4) * occ_func_2_0(0) * occ_func_2_0(8) *
              occ_func_3_0(43) +
          occ_func_2_0(2) * occ_func_2_0(6) * occ_func_2_0(0) *
              occ_func_3_0(15) +
          occ_func_2_0(51) * occ_func_2_0(47) * occ_func_2_0(15) *
              occ_func_3_0(0) +
          occ_func_2_0(13) * occ_func_2_0(9) * occ_func_2_0(1) *
              occ_func_3_0(0) +
          occ_func_2_0(7) * occ_func_2_0(11) * occ_func_2_0(1) *
              occ_func_3_0(0) +
          occ_func_2_0(5) * occ_func_2_0(3) * occ_func_2_0(1) *
              occ_func_3_0(0)) /
         12.;
}
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_13_0_at_1()
    const {
  return (occ_func_2_0(2) * occ_func_2_0(4) * occ_func_2_0(0) *
              occ_func_3_0(1) +
          occ_func_2_0(11) * occ_func_2_0(1) * occ_func_2_0(13) *
              occ_func_3_0(52) +
          occ_func_2_0(1) * occ_func_2_0(5) * occ_func_2_0(9) *
              occ_func_3_0(44) +
          occ_func_2_0(7) * occ_func_2_0(3) * occ_func_2_0(1) *
              occ_func_3_0(16) +
          occ_func_2_0(1) * occ_func_2_0(13) * occ_func_2_0(11) *
              occ_func_3_0(48) +
          occ_func_2_0(5) * occ_func_2_0(9) * occ_func_2_0(1) *
              occ_func_3_0(16) +
          occ_func_2_0(3) * occ_func_2_0(1) * occ_func_2_0(7) *
              occ_func_3_0(40) +
          occ_func_2_0(10) * occ_func_2_0(6) * occ_func_2_0(0) *
              occ_func_3_0(1) +
          occ_func_2_0(8) * occ_func_2_0(12) * occ_func_2_0(0) *
              occ_func_3_0(1) +
          occ_func_2_0(48) * occ_func_2_0(52) * occ_func_2_0(16) *
              occ_func_3_0(1) +
          occ_func_2_0(44) * occ_func_2_0(36) * occ_func_2_0(16) *
              occ_func_3_0(1) +
          occ_func_2_0(32) * occ_func_2_0(40) * occ_func_2_0(16) *
              occ_func_3_0(1) +
          occ_func_2_0(13) * occ_func_2_0(11) * occ_func_2_0(1) *
              occ_func_3_0(16) +
          occ_func_2_0(9) * occ_func_2_0(1) * occ_func_2_0(5) *
              occ_func_3_0(36) +
          occ_func_2_0(1) * occ_func_2_0(7) * occ_func_2_0(3) *
              occ_func_3_0(32) +
          occ_func_2_0(13) * occ_func_2_0(9) * occ_func_2_0(1) *
              occ_func_3_0(0) +
          occ_func_2_0(11) * occ_func_2_0(1) * occ_func_2_0(7) *
              occ_func_3_0(6) +
          occ_func_2_0(1) * occ_func_2_0(5) * occ_func_2_0(3) *
              occ_func_3_0(2) +
          occ_func_2_0(1) * occ_func_2_0(13) * occ_func_2_0(9) *
              occ_func_3_0(8) +
          occ_func_2_0(7) * occ_func_2_0(11) * occ_func_2_0(1) *
              occ_func_3_0(0) +
          occ_func_2_0(3) * occ_func_2_0(1) * occ_func_2_0(5) *
              occ_func_3_0(4) +
          occ_func_2_0(9) * occ_func_2_0(1) * occ_func_2_0(13) *
              occ_func_3_0(12) +
          occ_func_2_0(1) * occ_func_2_0(7) * occ_func_2_0(11) *
              occ_func_3_0(10) +
          occ_func_2_0(5) * occ_func_2_0(3) * occ_func_2_0(1) *
              occ_func_3_0(0)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_13_0_at_0(
    int occ_i, int occ_f) const {
  return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) *
         (occ_func_2_0(8) * occ_func_2_0(12) * occ_func_3_0(13) +
          occ_func_2_0(6) * occ_func_2_0(10) * occ_func_3_0(11) +
          occ_func_2_0(2) * occ_func_2_0(4) * occ_func_3_0(1) +
          occ_func_2_0(39) * occ_func_2_0(31) * occ_func_2_0(15) +
          occ_func_2_0(35) * occ_func_2_0(43) * occ_func_2_0(15) +
          occ_func_2_0(12) * occ_func_2_0(8) * occ_func_3_0(9) +
          occ_func_2_0(10) * occ_func_2_0(6) * occ_func_3_0(1) +
          occ_func_2_0(2) * occ_func_2_0(4) * occ_func_3_0(5) +
          occ_func_2_0(8) * occ_func_2_0(12) * occ_func_3_0(1) +
          occ_func_2_0(10) * occ_func_2_0(6) * occ_func_3_0(7) +
          occ_func_2_0(4) * occ_func_2_0(2) * occ_func_3_0(3) +
          occ_func_2_0(10) * occ_func_2_0(12) * occ_func_3_0(15) +
          occ_func_2_0(8) * occ_func_2_0(4) * occ_func_3_0(35) +
          occ_func_2_0(6) * occ_func_2_0(2) * occ_func_3_0(31) +
          occ_func_2_0(12) * occ_func_2_0(10) * occ_func_3_0(47) +
          occ_func_2_0(8) * occ_func_2_0(4) * occ_func_3_0(15) +
          occ_func_2_0(2) * occ_func_2_0(6) * occ_func_3_0(39) +
          occ_func_2_0(10) * occ_func_2_0(12) * occ_func_3_0(51) +
          occ_func_2_0(4) * occ_func_2_0(8) * occ_func_3_0(43) +
          occ_func_2_0(2) * occ_func_2_0(6) * occ_func_3_0(15) +
          occ_func_2_0(51) * occ_func_2_0(47) * occ_func_2_0(15) +
          occ_func_2_0(13) * occ_func_2_0(9) * occ_func_2_0(1) +
          occ_func_2_0(7) * occ_func_2_0(11) * occ_func_2_0(1) +
          occ_func_2_0(5) * occ_func_2_0(3) * occ_func_2_0(1)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_13_0_at_1(
    int occ_i, int occ_f) const {
  return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) *
         (occ_func_2_0(2) * occ_func_2_0(4) * occ_func_2_0(0) +
          occ_func_2_0(11) * occ_func_2_0(13) * occ_func_3_0(52) +
          occ_func_2_0(5) * occ_func_2_0(9) * occ_func_3_0(44) +
          occ_func_2_0(7) * occ_func_2_0(3) * occ_func_3_0(16) +
          occ_func_2_0(13) * occ_func_2_0(11) * occ_func_3_0(48) +
          occ_func_2_0(5) * occ_func_2_0(9) * occ_func_3_0(16) +
          occ_func_2_0(3) * occ_func_2_0(7) * occ_func_3_0(40) +
          occ_func_2_0(10) * occ_func_2_0(6) * occ_func_2_0(0) +
          occ_func_2_0(8) * occ_func_2_0(12) * occ_func_2_0(0) +
          occ_func_2_0(48) * occ_func_2_0(52) * occ_func_2_0(16) +
          occ_func_2_0(44) * occ_func_2_0(36) * occ_func_2_0(16) +
          occ_func_2_0(32) * occ_func_2_0(40) * occ_func_2_0(16) +
          occ_func_2_0(13) * occ_func_2_0(11) * occ_func_3_0(16) +
          occ_func_2_0(9) * occ_func_2_0(5) * occ_func_3_0(36) +
          occ_func_2_0(7) * occ_func_2_0(3) * occ_func_3_0(32) +
          occ_func_2_0(13) * occ_func_2_0(9) * occ_func_3_0(0) +
          occ_func_2_0(11) * occ_func_2_0(7) * occ_func_3_0(6) +
          occ_func_2_0(5) * occ_func_2_0(3) * occ_func_3_0(2) +
          occ_func_2_0(13) * occ_func_2_0(9) * occ_func_3_0(8) +
          occ_func_2_0(7) * occ_func_2_0(11) * occ_func_3_0(0) +
          occ_func_2_0(3) * occ_func_2_0(5) * occ_func_3_0(4) +
          occ_func_2_0(9) * occ_func_2_0(13) * occ_func_3_0(12) +
          occ_func_2_0(7) * occ_func_2_0(11) * occ_func_3_0(10) +
          occ_func_2_0(5) * occ_func_2_0(3) * occ_func_3_0(0)) /
         12.;
}

/**** Basis functions for orbit 14****
0.3333333 0.6666667 0.2500000 Va  O

0.3333333 1.6666667 -0.2500000 Va  O

0.3333333 1.6666667 0.2500000 Va  O

1.3333333 1.6666667 -0.2500000 Va  O

****/
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::eval_bfunc_14_0() const {
  return (occ_func_2_0(0) * occ_func_3_0(43) * occ_func_2_0(8) *
              occ_func_3_0(51) +
          occ_func_2_0(11) * occ_func_3_0(0) * occ_func_2_0(1) *
              occ_func_3_0(12) +
          occ_func_2_0(1) * occ_func_3_0(12) * occ_func_2_0(13) *
              occ_func_3_0(10) +
          occ_func_2_0(52) * occ_func_3_0(1) * occ_func_2_0(16) *
              occ_func_3_0(9) +
          occ_func_2_0(44) * occ_func_3_0(13) * occ_func_2_0(52) *
              occ_func_3_0(1) +
          occ_func_2_0(0) * occ_func_3_0(11) * occ_func_2_0(10) *
              occ_func_3_0(13) +
          occ_func_2_0(44) * occ_func_3_0(1) * occ_func_2_0(16) *
              occ_func_3_0(13) +
          occ_func_2_0(0) * occ_func_3_0(51) * occ_func_2_0(12) *
              occ_func_3_0(43) +
          occ_func_2_0(52) * occ_func_3_0(9) * occ_func_2_0(44) *
              occ_func_3_0(1) +
          occ_func_2_0(1) * occ_func_3_0(10) * occ_func_2_0(11) *
              occ_func_3_0(12) +
          occ_func_2_0(13) * occ_func_3_0(0) * occ_func_2_0(1) *
              occ_func_3_0(10) +
          occ_func_2_0(11) * occ_func_3_0(12) * occ_func_2_0(13) *
              occ_func_3_0(0)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_14_0_at_0()
    const {
  return (occ_func_2_0(0) * occ_func_3_0(43) * occ_func_2_0(8) *
              occ_func_3_0(51) +
          occ_func_2_0(6) * occ_func_3_0(15) * occ_func_2_0(0) *
              occ_func_3_0(47) +
          occ_func_2_0(11) * occ_func_3_0(0) * occ_func_2_0(1) *
              occ_func_3_0(12) +
          occ_func_2_0(7) * occ_func_3_0(2) * occ_func_2_0(3) *
              occ_func_3_0(0) +
          occ_func_2_0(5) * occ_func_3_0(8) * occ_func_2_0(9) *
              occ_func_3_0(0) +
          occ_func_2_0(3) * occ_func_3_0(0) * occ_func_2_0(1) *
              occ_func_3_0(6) +
          occ_func_2_0(12) * occ_func_3_0(15) * occ_func_2_0(0) *
              occ_func_3_0(43) +
          occ_func_2_0(0) * occ_func_3_0(31) * occ_func_2_0(2) *
              occ_func_3_0(35) +
          occ_func_2_0(0) * occ_func_3_0(47) * occ_func_2_0(10) *
              occ_func_3_0(39) +
          occ_func_2_0(4) * occ_func_3_0(15) * occ_func_2_0(0) *
              occ_func_3_0(31) +
          occ_func_2_0(0) * occ_func_3_0(11) * occ_func_2_0(10) *
              occ_func_3_0(13) +
          occ_func_2_0(4) * occ_func_3_0(1) * occ_func_2_0(0) *
              occ_func_3_0(9) +
          occ_func_2_0(8) * occ_func_3_0(15) * occ_func_2_0(0) *
              occ_func_3_0(51) +
          occ_func_2_0(0) * occ_func_3_0(39) * occ_func_2_0(6) *
              occ_func_3_0(47) +
          occ_func_2_0(0) * occ_func_3_0(51) * occ_func_2_0(12) *
              occ_func_3_0(43) +
          occ_func_2_0(2) * occ_func_3_0(15) * occ_func_2_0(0) *
              occ_func_3_0(35) +
          occ_func_2_0(10) * occ_func_3_0(15) * occ_func_2_0(0) *
              occ_func_3_0(39) +
          occ_func_2_0(0) * occ_func_3_0(35) * occ_func_2_0(4) *
              occ_func_3_0(31) +
          occ_func_2_0(5) * occ_func_3_0(0) * occ_func_2_0(1) *
              occ_func_3_0(8) +
          occ_func_2_0(3) * occ_func_3_0(6) * occ_func_2_0(7) *
              occ_func_3_0(0) +
          occ_func_2_0(13) * occ_func_3_0(0) * occ_func_2_0(1) *
              occ_func_3_0(10) +
          occ_func_2_0(9) * occ_func_3_0(4) * occ_func_2_0(5) *
              occ_func_3_0(0) +
          occ_func_2_0(11) * occ_func_3_0(12) * occ_func_2_0(13) *
              occ_func_3_0(0) +
          occ_func_2_0(7) * occ_func_3_0(0) * occ_func_2_0(1) *
              occ_func_3_0(2)) /
         12.;
}
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_14_0_at_1()
    const {
  return (occ_func_2_0(40) * occ_func_3_0(1) * occ_func_2_0(16) *
              occ_func_3_0(11) +
          occ_func_2_0(32) * occ_func_3_0(5) * occ_func_2_0(36) *
              occ_func_3_0(1) +
          occ_func_2_0(11) * occ_func_3_0(0) * occ_func_2_0(1) *
              occ_func_3_0(12) +
          occ_func_2_0(1) * occ_func_3_0(4) * occ_func_2_0(5) *
              occ_func_3_0(8) +
          occ_func_2_0(1) * occ_func_3_0(12) * occ_func_2_0(13) *
              occ_func_3_0(10) +
          occ_func_2_0(3) * occ_func_3_0(0) * occ_func_2_0(1) *
              occ_func_3_0(6) +
          occ_func_2_0(52) * occ_func_3_0(1) * occ_func_2_0(16) *
              occ_func_3_0(9) +
          occ_func_2_0(48) * occ_func_3_0(7) * occ_func_2_0(40) *
              occ_func_3_0(1) +
          occ_func_2_0(44) * occ_func_3_0(13) * occ_func_2_0(52) *
              occ_func_3_0(1) +
          occ_func_2_0(36) * occ_func_3_0(1) * occ_func_2_0(16) *
              occ_func_3_0(3) +
          occ_func_2_0(4) * occ_func_3_0(1) * occ_func_2_0(0) *
              occ_func_3_0(9) +
          occ_func_2_0(2) * occ_func_3_0(7) * occ_func_2_0(6) *
              occ_func_3_0(1) +
          occ_func_2_0(44) * occ_func_3_0(1) * occ_func_2_0(16) *
              occ_func_3_0(13) +
          occ_func_2_0(36) * occ_func_3_0(3) * occ_func_2_0(32) *
              occ_func_3_0(1) +
          occ_func_2_0(40) * occ_func_3_0(11) * occ_func_2_0(48) *
              occ_func_3_0(1) +
          occ_func_2_0(32) * occ_func_3_0(1) * occ_func_2_0(16) *
              occ_func_3_0(5) +
          occ_func_2_0(52) * occ_func_3_0(9) * occ_func_2_0(44) *
              occ_func_3_0(1) +
          occ_func_2_0(48) * occ_func_3_0(1) * occ_func_2_0(16) *
              occ_func_3_0(7) +
          occ_func_2_0(1) * occ_func_3_0(10) * occ_func_2_0(11) *
              occ_func_3_0(12) +
          occ_func_2_0(5) * occ_func_3_0(0) * occ_func_2_0(1) *
              occ_func_3_0(8) +
          occ_func_2_0(13) * occ_func_3_0(0) * occ_func_2_0(1) *
              occ_func_3_0(10) +
          occ_func_2_0(1) * occ_func_3_0(2) * occ_func_2_0(3) *
              occ_func_3_0(6) +
          occ_func_2_0(1) * occ_func_3_0(8) * occ_func_2_0(9) *
              occ_func_3_0(4) +
          occ_func_2_0(7) * occ_func_3_0(0) * occ_func_2_0(1) *
              occ_func_3_0(2)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_14_0_at_0(
    int occ_i, int occ_f) const {
  return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) *
         (occ_func_3_0(43) * occ_func_2_0(8) * occ_func_3_0(51) +
          occ_func_2_0(6) * occ_func_3_0(15) * occ_func_3_0(47) +
          occ_func_2_0(11) * occ_func_2_0(1) * occ_func_3_0(12) +
          occ_func_2_0(7) * occ_func_3_0(2) * occ_func_2_0(3) +
          occ_func_2_0(5) * occ_func_3_0(8) * occ_func_2_0(9) +
          occ_func_2_0(3) * occ_func_2_0(1) * occ_func_3_0(6) +
          occ_func_2_0(12) * occ_func_3_0(15) * occ_func_3_0(43) +
          occ_func_3_0(31) * occ_func_2_0(2) * occ_func_3_0(35) +
          occ_func_3_0(47) * occ_func_2_0(10) * occ_func_3_0(39) +
          occ_func_2_0(4) * occ_func_3_0(15) * occ_func_3_0(31) +
          occ_func_3_0(11) * occ_func_2_0(10) * occ_func_3_0(13) +
          occ_func_2_0(4) * occ_func_3_0(1) * occ_func_3_0(9) +
          occ_func_2_0(8) * occ_func_3_0(15) * occ_func_3_0(51) +
          occ_func_3_0(39) * occ_func_2_0(6) * occ_func_3_0(47) +
          occ_func_3_0(51) * occ_func_2_0(12) * occ_func_3_0(43) +
          occ_func_2_0(2) * occ_func_3_0(15) * occ_func_3_0(35) +
          occ_func_2_0(10) * occ_func_3_0(15) * occ_func_3_0(39) +
          occ_func_3_0(35) * occ_func_2_0(4) * occ_func_3_0(31) +
          occ_func_2_0(5) * occ_func_2_0(1) * occ_func_3_0(8) +
          occ_func_2_0(3) * occ_func_3_0(6) * occ_func_2_0(7) +
          occ_func_2_0(13) * occ_func_2_0(1) * occ_func_3_0(10) +
          occ_func_2_0(9) * occ_func_3_0(4) * occ_func_2_0(5) +
          occ_func_2_0(11) * occ_func_3_0(12) * occ_func_2_0(13) +
          occ_func_2_0(7) * occ_func_2_0(1) * occ_func_3_0(2)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_14_0_at_1(
    int occ_i, int occ_f) const {
  return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) *
         (occ_func_2_0(40) * occ_func_2_0(16) * occ_func_3_0(11) +
          occ_func_2_0(32) * occ_func_3_0(5) * occ_func_2_0(36) +
          occ_func_2_0(11) * occ_func_3_0(0) * occ_func_3_0(12) +
          occ_func_3_0(4) * occ_func_2_0(5) * occ_func_3_0(8) +
          occ_func_3_0(12) * occ_func_2_0(13) * occ_func_3_0(10) +
          occ_func_2_0(3) * occ_func_3_0(0) * occ_func_3_0(6) +
          occ_func_2_0(52) * occ_func_2_0(16) * occ_func_3_0(9) +
          occ_func_2_0(48) * occ_func_3_0(7) * occ_func_2_0(40) +
          occ_func_2_0(44) * occ_func_3_0(13) * occ_func_2_0(52) +
          occ_func_2_0(36) * occ_func_2_0(16) * occ_func_3_0(3) +
          occ_func_2_0(4) * occ_func_2_0(0) * occ_func_3_0(9) +
          occ_func_2_0(2) * occ_func_3_0(7) * occ_func_2_0(6) +
          occ_func_2_0(44) * occ_func_2_0(16) * occ_func_3_0(13) +
          occ_func_2_0(36) * occ_func_3_0(3) * occ_func_2_0(32) +
          occ_func_2_0(40) * occ_func_3_0(11) * occ_func_2_0(48) +
          occ_func_2_0(32) * occ_func_2_0(16) * occ_func_3_0(5) +
          occ_func_2_0(52) * occ_func_3_0(9) * occ_func_2_0(44) +
          occ_func_2_0(48) * occ_func_2_0(16) * occ_func_3_0(7) +
          occ_func_3_0(10) * occ_func_2_0(11) * occ_func_3_0(12) +
          occ_func_2_0(5) * occ_func_3_0(0) * occ_func_3_0(8) +
          occ_func_2_0(13) * occ_func_3_0(0) * occ_func_3_0(10) +
          occ_func_3_0(2) * occ_func_2_0(3) * occ_func_3_0(6) +
          occ_func_3_0(8) * occ_func_2_0(9) * occ_func_3_0(4) +
          occ_func_2_0(7) * occ_func_3_0(0) * occ_func_3_0(2)) /
         12.;
}

/**** Basis functions for orbit 15****
0.3333333 0.6666667 0.2500000 Va  O

0.3333333 1.6666667 0.2500000 Va  O

0.3333333 1.6666667 0.7500000 Va  O

1.3333333 1.6666667 0.7500000 Va  O

****/
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::eval_bfunc_15_0() const {
  return (occ_func_2_0(0) * occ_func_2_0(8) * occ_func_3_0(9) *
              occ_func_3_0(13) +
          occ_func_2_0(11) * occ_func_2_0(1) * occ_func_3_0(16) *
              occ_func_3_0(52) +
          occ_func_2_0(1) * occ_func_2_0(13) * occ_func_3_0(52) *
              occ_func_3_0(48) +
          occ_func_2_0(12) * occ_func_2_0(0) * occ_func_3_0(1) *
              occ_func_3_0(9) +
          occ_func_2_0(8) * occ_func_2_0(12) * occ_func_3_0(13) *
              occ_func_3_0(1) +
          occ_func_2_0(0) * occ_func_2_0(10) * occ_func_3_0(47) *
              occ_func_3_0(51) +
          occ_func_2_0(8) * occ_func_2_0(0) * occ_func_3_0(1) *
              occ_func_3_0(13) +
          occ_func_2_0(0) * occ_func_2_0(12) * occ_func_3_0(13) *
              occ_func_3_0(9) +
          occ_func_2_0(12) * occ_func_2_0(8) * occ_func_3_0(9) *
              occ_func_3_0(1) +
          occ_func_2_0(1) * occ_func_2_0(11) * occ_func_3_0(48) *
              occ_func_3_0(52) +
          occ_func_2_0(13) * occ_func_2_0(1) * occ_func_3_0(16) *
              occ_func_3_0(48) +
          occ_func_2_0(47) * occ_func_2_0(51) * occ_func_3_0(12) *
              occ_func_3_0(0)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_15_0_at_0()
    const {
  return (occ_func_2_0(0) * occ_func_2_0(8) * occ_func_3_0(9) *
              occ_func_3_0(13) +
          occ_func_2_0(6) * occ_func_2_0(0) * occ_func_3_0(1) *
              occ_func_3_0(11) +
          occ_func_2_0(47) * occ_func_2_0(15) * occ_func_3_0(0) *
              occ_func_3_0(12) +
          occ_func_2_0(39) * occ_func_2_0(31) * occ_func_3_0(2) *
              occ_func_3_0(0) +
          occ_func_2_0(35) * occ_func_2_0(43) * occ_func_3_0(8) *
              occ_func_3_0(0) +
          occ_func_2_0(31) * occ_func_2_0(15) * occ_func_3_0(0) *
              occ_func_3_0(6) +
          occ_func_2_0(12) * occ_func_2_0(0) * occ_func_3_0(1) *
              occ_func_3_0(9) +
          occ_func_2_0(0) * occ_func_2_0(2) * occ_func_3_0(3) *
              occ_func_3_0(5) +
          occ_func_2_0(0) * occ_func_2_0(10) * occ_func_3_0(11) *
              occ_func_3_0(7) +
          occ_func_2_0(4) * occ_func_2_0(0) * occ_func_3_0(1) *
              occ_func_3_0(3) +
          occ_func_2_0(0) * occ_func_2_0(10) * occ_func_3_0(47) *
              occ_func_3_0(51) +
          occ_func_2_0(4) * occ_func_2_0(0) * occ_func_3_0(15) *
              occ_func_3_0(43) +
          occ_func_2_0(8) * occ_func_2_0(0) * occ_func_3_0(1) *
              occ_func_3_0(13) +
          occ_func_2_0(0) * occ_func_2_0(6) * occ_func_3_0(7) *
              occ_func_3_0(11) +
          occ_func_2_0(0) * occ_func_2_0(12) * occ_func_3_0(13) *
              occ_func_3_0(9) +
          occ_func_2_0(2) * occ_func_2_0(0) * occ_func_3_0(1) *
              occ_func_3_0(5) +
          occ_func_2_0(10) * occ_func_2_0(0) * occ_func_3_0(1) *
              occ_func_3_0(7) +
          occ_func_2_0(0) * occ_func_2_0(4) * occ_func_3_0(5) *
              occ_func_3_0(3) +
          occ_func_2_0(35) * occ_func_2_0(15) * occ_func_3_0(0) *
              occ_func_3_0(8) +
          occ_func_2_0(31) * occ_func_2_0(39) * occ_func_3_0(6) *
              occ_func_3_0(0) +
          occ_func_2_0(51) * occ_func_2_0(15) * occ_func_3_0(0) *
              occ_func_3_0(10) +
          occ_func_2_0(43) * occ_func_2_0(35) * occ_func_3_0(4) *
              occ_func_3_0(0) +
          occ_func_2_0(47) * occ_func_2_0(51) * occ_func_3_0(12) *
              occ_func_3_0(0) +
          occ_func_2_0(39) * occ_func_2_0(15) * occ_func_3_0(0) *
              occ_func_3_0(2)) /
         12.;
}
template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_eval_bfunc_15_0_at_1()
    const {
  return (occ_func_2_0(6) * occ_func_2_0(0) * occ_func_3_0(1) *
              occ_func_3_0(11) +
          occ_func_2_0(2) * occ_func_2_0(4) * occ_func_3_0(5) *
              occ_func_3_0(1) +
          occ_func_2_0(11) * occ_func_2_0(1) * occ_func_3_0(16) *
              occ_func_3_0(52) +
          occ_func_2_0(1) * occ_func_2_0(5) * occ_func_3_0(36) *
              occ_func_3_0(44) +
          occ_func_2_0(1) * occ_func_2_0(13) * occ_func_3_0(52) *
              occ_func_3_0(48) +
          occ_func_2_0(3) * occ_func_2_0(1) * occ_func_3_0(16) *
              occ_func_3_0(40) +
          occ_func_2_0(12) * occ_func_2_0(0) * occ_func_3_0(1) *
              occ_func_3_0(9) +
          occ_func_2_0(10) * occ_func_2_0(6) * occ_func_3_0(7) *
              occ_func_3_0(1) +
          occ_func_2_0(8) * occ_func_2_0(12) * occ_func_3_0(13) *
              occ_func_3_0(1) +
          occ_func_2_0(4) * occ_func_2_0(0) * occ_func_3_0(1) *
              occ_func_3_0(3) +
          occ_func_2_0(36) * occ_func_2_0(16) * occ_func_3_0(1) *
              occ_func_3_0(9) +
          occ_func_2_0(32) * occ_func_2_0(40) * occ_func_3_0(7) *
              occ_func_3_0(1) +
          occ_func_2_0(8) * occ_func_2_0(0) * occ_func_3_0(1) *
              occ_func_3_0(13) +
          occ_func_2_0(4) * occ_func_2_0(2) * occ_func_3_0(3) *
              occ_func_3_0(1) +
          occ_func_2_0(6) * occ_func_2_0(10) * occ_func_3_0(11) *
              occ_func_3_0(1) +
          occ_func_2_0(2) * occ_func_2_0(0) * occ_func_3_0(1) *
              occ_func_3_0(5) +
          occ_func_2_0(12) * occ_func_2_0(8) * occ_func_3_0(9) *
              occ_func_3_0(1) +
          occ_func_2_0(10) * occ_func_2_0(0) * occ_func_3_0(1) *
              occ_func_3_0(7) +
          occ_func_2_0(1) * occ_func_2_0(11) * occ_func_3_0(48) *
              occ_func_3_0(52) +
          occ_func_2_0(5) * occ_func_2_0(1) * occ_func_3_0(16) *
              occ_func_3_0(44) +
          occ_func_2_0(13) * occ_func_2_0(1) * occ_func_3_0(16) *
              occ_func_3_0(48) +
          occ_func_2_0(1) * occ_func_2_0(3) * occ_func_3_0(32) *
              occ_func_3_0(40) +
          occ_func_2_0(1) * occ_func_2_0(9) * occ_func_3_0(44) *
              occ_func_3_0(36) +
          occ_func_2_0(7) * occ_func_2_0(1) * occ_func_3_0(16) *
              occ_func_3_0(32)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_15_0_at_0(
    int occ_i, int occ_f) const {
  return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) *
         (occ_func_2_0(8) * occ_func_3_0(9) * occ_func_3_0(13) +
          occ_func_2_0(6) * occ_func_3_0(1) * occ_func_3_0(11) +
          occ_func_2_0(47) * occ_func_2_0(15) * occ_func_3_0(12) +
          occ_func_2_0(39) * occ_func_2_0(31) * occ_func_3_0(2) +
          occ_func_2_0(35) * occ_func_2_0(43) * occ_func_3_0(8) +
          occ_func_2_0(31) * occ_func_2_0(15) * occ_func_3_0(6) +
          occ_func_2_0(12) * occ_func_3_0(1) * occ_func_3_0(9) +
          occ_func_2_0(2) * occ_func_3_0(3) * occ_func_3_0(5) +
          occ_func_2_0(10) * occ_func_3_0(11) * occ_func_3_0(7) +
          occ_func_2_0(4) * occ_func_3_0(1) * occ_func_3_0(3) +
          occ_func_2_0(10) * occ_func_3_0(47) * occ_func_3_0(51) +
          occ_func_2_0(4) * occ_func_3_0(15) * occ_func_3_0(43) +
          occ_func_2_0(8) * occ_func_3_0(1) * occ_func_3_0(13) +
          occ_func_2_0(6) * occ_func_3_0(7) * occ_func_3_0(11) +
          occ_func_2_0(12) * occ_func_3_0(13) * occ_func_3_0(9) +
          occ_func_2_0(2) * occ_func_3_0(1) * occ_func_3_0(5) +
          occ_func_2_0(10) * occ_func_3_0(1) * occ_func_3_0(7) +
          occ_func_2_0(4) * occ_func_3_0(5) * occ_func_3_0(3) +
          occ_func_2_0(35) * occ_func_2_0(15) * occ_func_3_0(8) +
          occ_func_2_0(31) * occ_func_2_0(39) * occ_func_3_0(6) +
          occ_func_2_0(51) * occ_func_2_0(15) * occ_func_3_0(10) +
          occ_func_2_0(43) * occ_func_2_0(35) * occ_func_3_0(4) +
          occ_func_2_0(47) * occ_func_2_0(51) * occ_func_3_0(12) +
          occ_func_2_0(39) * occ_func_2_0(15) * occ_func_3_0(2)) /
         12.;
}

template <typename Scalar>
Scalar OccClexulatorZrOTest_Clexulator_default::site_deval_bfunc_15_0_at_1(
    int occ_i, int occ_f) const {
  return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) *
         (occ_func_2_0(6) * occ_func_2_0(0) * occ_func_3_0(11) +
          occ_func_2_0(2) * occ_func_2_0(4) * occ_func_3_0(5) +
          occ_func_2_0(11) * occ_func_3_0(16) * occ_func_3_0(52) +
          occ_func_2_0(5) * occ_func_3_0(36) * occ_func_3_0(44) +
          occ_func_2_0(13) * occ_func_3_0(52) * occ_func_3_0(48) +
          occ_func_2_0(3) * occ_func_3_0(16) * occ_func_3_0(40) +
          occ_func_2_0(12) * occ_func_2_0(0) * occ_func_3_0(9) +
          occ_func_2_0(10) * occ_func_2_0(6) * occ_func_3_0(7) +
          occ_func_2_0(8) * occ_func_2_0(12) * occ_func_3_0(13) +
          occ_func_2_0(4) * occ_func_2_0(0) * occ_func_3_0(3) +
          occ_func_2_0(36) * occ_func_2_0(16) * occ_func_3_0(9) +
          occ_func_2_0(32) * occ_func_2_0(40) * occ_func_3_0(7) +
          occ_func_2_0(8) * occ_func_2_0(0) * occ_func_3_0(13) +
          occ_func_2_0(4) * occ_func_2_0(2) * occ_func_3_0(3) +
          occ_func_2_0(6) * occ_func_2_0(10) * occ_func_3_0(11) +
          occ_func_2_0(2) * occ_func_2_0(0) * occ_func_3_0(5) +
          occ_func_2_0(12) * occ_func_2_0(8) * occ_func_3_0(9) +
          occ_func_2_0(10) * occ_func_2_0(0) * occ_func_3_0(7) +
          occ_func_2_0(11) * occ_func_3_0(48) * occ_func_3_0(52) +
          occ_func_2_0(5) * occ_func_3_0(16) * occ_func_3_0(44) +
          occ_func_2_0(13) * occ_func_3_0(16) * occ_func_3_0(48) +
          occ_func_2_0(3) * occ_func_3_0(32) * occ_func_3_0(40) +
          occ_func_2_0(9) * occ_func_3_0(44) * occ_func_3_0(36) +
          occ_func_2_0(7) * occ_func_3_0(16) * occ_func_3_0(32)) /
         12.;
}

}  // namespace clexulator
}  // namespace CASM

extern "C" {
/// \brief Returns a clexulator::BaseClexulator* owning a
/// OccClexulatorZrOTest_Clexulator_default
CASM::clexulator::BaseClexulator *
make_OccClexulatorZrOTest_Clexulator_default() {
  return new CASM::clexulator::OccClexulatorZrOTest_Clexulator_default();
}
}
