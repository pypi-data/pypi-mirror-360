#include <cstddef>
#include "casm/clexulator/BaseClexulator.hh"
#include "casm/global/eigen.hh"
#include "casm/clexulator/BasicClexParamPack.hh"




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
    "method" : "local_max_length",
    "params" : {
      "generating_group" : [ 0, 3, 4, 9, 10, 11, 12, 13, 14, 15, 21, 22 ],
      "orbit_branch_specs" : {
        "0" : {
          "cutoff_radius" : 0.000000000000,
          "max_length" : 0.000000000000
        },
        "1" : {
          "cutoff_radius" : 4.010000000000,
          "max_length" : 0.000000000000
        },
        "2" : {
          "cutoff_radius" : 4.010000000000,
          "max_length" : 4.010000000000
        }
      },
      "phenomenal" : {
        "max_length" : 2.584339170000,
        "min_length" : 2.584339170000,
        "sites" : [
          [ 3, 0, 0, 0 ],
          [ 2, 0, 0, 1 ]
        ]
      }
    }
  }
}

**/


/// \brief Returns a clexulator::BaseClexulator* owning a ZrO_Clexulator_hop0_1
extern "C" CASM::clexulator::BaseClexulator *make_ZrO_Clexulator_hop0_1();

namespace CASM {
namespace clexulator {

  /****** GENERATED CLEXPARAMPACK DEFINITION ******/


  typedef BasicClexParamPack ParamPack;


  /****** GENERATED CLEXULATOR DEFINITION ******/

  class ZrO_Clexulator_hop0_1 : public clexulator::BaseClexulator {

  public:

    ZrO_Clexulator_hop0_1();

    ~ZrO_Clexulator_hop0_1();

    ClexParamPack const &param_pack() const override {
      return m_params;
    }

    ClexParamPack &param_pack() override {
      return m_params;
    }


    template<typename Scalar>
    Scalar eval_bfunc_0_0() const;

    template<typename Scalar>
    Scalar eval_bfunc_1_0() const;

    template<typename Scalar>
    Scalar site_eval_bfunc_1_0_at_15() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_1_0_at_16() const;
    template<typename Scalar>
    Scalar site_deval_bfunc_1_0_at_15(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_1_0_at_16(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar eval_bfunc_2_0() const;

    template<typename Scalar>
    Scalar site_eval_bfunc_2_0_at_2() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_2_0_at_3() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_2_0_at_4() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_2_0_at_5() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_2_0_at_6() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_2_0_at_7() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_2_0_at_8() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_2_0_at_9() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_2_0_at_10() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_2_0_at_11() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_2_0_at_12() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_2_0_at_13() const;

    template<typename Scalar>
    Scalar site_deval_bfunc_2_0_at_2(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_2_0_at_3(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_2_0_at_4(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_2_0_at_5(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_2_0_at_6(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_2_0_at_7(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_2_0_at_8(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_2_0_at_9(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_2_0_at_10(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_2_0_at_11(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_2_0_at_12(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_2_0_at_13(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar eval_bfunc_3_0() const;

    template<typename Scalar>
    Scalar site_eval_bfunc_3_0_at_2() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_3_0_at_3() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_3_0_at_4() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_3_0_at_5() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_3_0_at_6() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_3_0_at_7() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_3_0_at_8() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_3_0_at_9() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_3_0_at_10() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_3_0_at_11() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_3_0_at_12() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_3_0_at_13() const;

    template<typename Scalar>
    Scalar site_deval_bfunc_3_0_at_2(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_3_0_at_3(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_3_0_at_4(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_3_0_at_5(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_3_0_at_6(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_3_0_at_7(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_3_0_at_8(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_3_0_at_9(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_3_0_at_10(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_3_0_at_11(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_3_0_at_12(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_3_0_at_13(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar eval_bfunc_4_0() const;

    template<typename Scalar>
    Scalar site_eval_bfunc_4_0_at_2() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_4_0_at_3() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_4_0_at_4() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_4_0_at_5() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_4_0_at_6() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_4_0_at_7() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_4_0_at_8() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_4_0_at_9() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_4_0_at_10() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_4_0_at_11() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_4_0_at_12() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_4_0_at_13() const;

    template<typename Scalar>
    Scalar site_deval_bfunc_4_0_at_2(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_4_0_at_3(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_4_0_at_4(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_4_0_at_5(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_4_0_at_6(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_4_0_at_7(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_4_0_at_8(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_4_0_at_9(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_4_0_at_10(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_4_0_at_11(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_4_0_at_12(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_4_0_at_13(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar eval_bfunc_5_0() const;

    template<typename Scalar>
    Scalar site_eval_bfunc_5_0_at_2() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_5_0_at_3() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_5_0_at_4() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_5_0_at_5() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_5_0_at_6() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_5_0_at_7() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_5_0_at_8() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_5_0_at_9() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_5_0_at_10() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_5_0_at_11() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_5_0_at_12() const;
    template<typename Scalar>
    Scalar site_eval_bfunc_5_0_at_13() const;

    template<typename Scalar>
    Scalar site_deval_bfunc_5_0_at_2(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_5_0_at_3(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_5_0_at_4(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_5_0_at_5(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_5_0_at_6(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_5_0_at_7(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_5_0_at_8(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_5_0_at_9(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_5_0_at_10(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_5_0_at_11(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_5_0_at_12(int occ_i, int occ_f) const;

    template<typename Scalar>
    Scalar site_deval_bfunc_5_0_at_13(int occ_i, int occ_f) const;


  private:

    // ParamPack object, which stores temporary data for calculations
    mutable ParamPack m_params;

    // typedef for method pointers of scalar type double
    typedef double (ZrO_Clexulator_hop0_1::*BasisFuncPtr_0)() const;

    // typedef for method pointers
    typedef double (ZrO_Clexulator_hop0_1::*DeltaBasisFuncPtr_0)(int, int) const;

    // array of pointers to member functions for calculating basis functions of scalar type double
    BasisFuncPtr_0 m_orbit_func_table_0[6];

    // array of pointers to member functions for calculating flower functions of scalar type double
    BasisFuncPtr_0 m_flower_func_table_0[17][6];

    // array of pointers to member functions for calculating DELTA flower functions of scalar type double
    DeltaBasisFuncPtr_0 m_delta_func_table_0[17][6];

    // Occupation Function tables for basis sites in asymmetric unit 1:
    //   - basis site 2:
    double m_occ_func_2_0[2];

    //   - basis site 3:
    double m_occ_func_3_0[2];

    //ClexParamPack allocation for evaluated correlations 
    ParamPack::Key m_corr_param_key;
    //ClexParamPack allocation for DoF occ
    ParamPack::Key m_occ_site_func_param_key;

    /// \brief Clone the ZrO_Clexulator_hop0_1
    BaseClexulator *_clone() const override {
      return new ZrO_Clexulator_hop0_1(*this);
    }

    /// \brief Calculate contribution to global correlations from one unit cell
    /// Result is recorded in ClexParamPack
    void _calc_global_corr_contribution() const override;

    /// \brief Calculate contribution to global correlations from one unit cell     /// Result is recorded in double array starting at corr_begin
    void _calc_global_corr_contribution(double *corr_begin) const override;

    /// \brief Calculate contribution to select global correlations from one unit cell into ClexParamPack
    /// Result is recorded in ClexParamPack
    void _calc_restricted_global_corr_contribution(size_type const *ind_list_begin, size_type const *ind_list_end) const override;

    /// \brief Calculate contribution to select global correlations from one unit cell
    /// Result is recorded in double array starting at corr_begin
    void _calc_restricted_global_corr_contribution(double *corr_begin, size_type const *ind_list_begin, size_type const *ind_list_end) const override;

    /// \brief Calculate point correlations about neighbor site 'nlist_ind'
    /// For global clexulators, 'nlist_ind' only ranges over sites in the cell
    /// For local clexulators, 'nlist_ind' ranges over all sites in the neighborhood
    /// Result is recorded in ClexParamPack
    void _calc_point_corr(int nlist_ind) const override;

    /// \brief Calculate point correlations about neighbor site 'nlist_ind'
    /// For global clexulators, 'nlist_ind' only ranges over sites in the cell
    /// For local clexulators, 'nlist_ind' ranges over all sites in the neighborhood
    /// Result is recorded in double array starting at corr_begin
    void _calc_point_corr(int nlist_ind, double *corr_begin) const override;

    /// \brief Calculate select point correlations about neighbor site 'nlist_ind'
    /// For global clexulators, 'nlist_ind' only ranges over sites in the cell
    /// For local clexulators, 'nlist_ind' ranges over all sites in the neighborhood
    /// Result is recorded in ClexParamPack
    void _calc_restricted_point_corr(int nlist_ind, size_type const *ind_list_begin, size_type const *ind_list_end) const override;

    /// \brief Calculate select point correlations about neighbor site 'nlist_ind'
    /// For global clexulators, 'nlist_ind' only ranges over sites in the cell
    /// For local clexulators, 'nlist_ind' ranges over all sites in the neighborhood
    /// Result is recorded in double array starting at corr_begin
    void _calc_restricted_point_corr(int nlist_ind, double *corr_begin, size_type const *ind_list_begin, size_type const *ind_list_end) const override;

    /// \brief Calculate the change in point correlations due to changing an occupant at neighbor site 'nlist_ind'
    /// For global clexulators, 'nlist_ind' only ranges over sites in the cell
    /// For local clexulators, 'nlist_ind' ranges over all sites in the neighborhood
    /// Result is recorded in ClexParamPack
    void _calc_delta_point_corr(int nlist_ind, int occ_i, int occ_f) const override;

    /// \brief Calculate the change in point correlations due to changing an occupant at neighbor site 'nlist_ind'
    /// For global clexulators, 'nlist_ind' only ranges over sites in the cell
    /// For local clexulators, 'nlist_ind' ranges over all sites in the neighborhood
    /// Result is recorded in double array starting at corr_begin
    void _calc_delta_point_corr(int nlist_ind, int occ_i, int occ_f, double *corr_begin) const override;

    /// \brief Calculate the change in select point correlations due to changing an occupant at neighbor site 'nlist_ind'
    /// For global clexulators, 'nlist_ind' only ranges over sites in the cell
    /// For local clexulators, 'nlist_ind' ranges over all sites in the neighborhood
    /// Result is recorded in ClexParamPack
    void _calc_restricted_delta_point_corr(int nlist_ind, int occ_i, int occ_f, size_type const *ind_list_begin, size_type const *ind_list_end) const override;

    /// \brief Calculate the change in select point correlations due to changing an occupant at neighbor site 'nlist_ind'
    /// For global clexulators, 'nlist_ind' only ranges over sites in the cell
    /// For local clexulators, 'nlist_ind' ranges over all sites in the neighborhood
    /// Result is recorded in double array starting at corr_begin
    void _calc_restricted_delta_point_corr(int nlist_ind, int occ_i, int occ_f, double *corr_begin, size_type const *ind_list_begin, size_type const *ind_list_end) const override;

    template<typename Scalar>
    void _global_prepare() const;

    template<typename Scalar>
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

    //default functions for basis function evaluation
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

  ZrO_Clexulator_hop0_1::ZrO_Clexulator_hop0_1() :
    BaseClexulator(17, 6, 17) {
    m_occ_func_2_0[0] = -0.0000000000, m_occ_func_2_0[1] = 1.0000000000;

    m_occ_func_3_0[0] = -0.0000000000, m_occ_func_3_0[1] = 1.0000000000;

    m_occ_site_func_param_key = m_params.allocate("occ_site_func", 1, 17, true);

    m_corr_param_key = m_params.allocate("corr", corr_size(), 1, false);

    m_orbit_func_table_0[0] = &ZrO_Clexulator_hop0_1::eval_bfunc_0_0<double>;
    m_orbit_func_table_0[1] = &ZrO_Clexulator_hop0_1::eval_bfunc_1_0<double>;
    m_orbit_func_table_0[2] = &ZrO_Clexulator_hop0_1::eval_bfunc_2_0<double>;
    m_orbit_func_table_0[3] = &ZrO_Clexulator_hop0_1::eval_bfunc_3_0<double>;
    m_orbit_func_table_0[4] = &ZrO_Clexulator_hop0_1::eval_bfunc_4_0<double>;
    m_orbit_func_table_0[5] = &ZrO_Clexulator_hop0_1::eval_bfunc_5_0<double>;


    m_flower_func_table_0[0][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[0][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[0][2] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[0][3] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[0][4] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[0][5] = &ZrO_Clexulator_hop0_1::zero_func<double>;


    m_flower_func_table_0[1][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[1][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[1][2] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[1][3] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[1][4] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[1][5] = &ZrO_Clexulator_hop0_1::zero_func<double>;


    m_flower_func_table_0[2][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[2][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[2][2] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_2<double>;
    m_flower_func_table_0[2][3] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_2<double>;
    m_flower_func_table_0[2][4] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_2<double>;
    m_flower_func_table_0[2][5] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_2<double>;


    m_flower_func_table_0[3][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[3][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[3][2] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_3<double>;
    m_flower_func_table_0[3][3] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_3<double>;
    m_flower_func_table_0[3][4] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_3<double>;
    m_flower_func_table_0[3][5] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_3<double>;


    m_flower_func_table_0[4][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[4][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[4][2] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_4<double>;
    m_flower_func_table_0[4][3] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_4<double>;
    m_flower_func_table_0[4][4] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_4<double>;
    m_flower_func_table_0[4][5] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_4<double>;


    m_flower_func_table_0[5][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[5][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[5][2] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_5<double>;
    m_flower_func_table_0[5][3] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_5<double>;
    m_flower_func_table_0[5][4] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_5<double>;
    m_flower_func_table_0[5][5] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_5<double>;


    m_flower_func_table_0[6][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[6][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[6][2] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_6<double>;
    m_flower_func_table_0[6][3] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_6<double>;
    m_flower_func_table_0[6][4] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_6<double>;
    m_flower_func_table_0[6][5] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_6<double>;


    m_flower_func_table_0[7][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[7][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[7][2] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_7<double>;
    m_flower_func_table_0[7][3] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_7<double>;
    m_flower_func_table_0[7][4] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_7<double>;
    m_flower_func_table_0[7][5] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_7<double>;


    m_flower_func_table_0[8][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[8][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[8][2] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_8<double>;
    m_flower_func_table_0[8][3] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_8<double>;
    m_flower_func_table_0[8][4] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_8<double>;
    m_flower_func_table_0[8][5] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_8<double>;


    m_flower_func_table_0[9][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[9][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[9][2] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_9<double>;
    m_flower_func_table_0[9][3] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_9<double>;
    m_flower_func_table_0[9][4] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_9<double>;
    m_flower_func_table_0[9][5] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_9<double>;


    m_flower_func_table_0[10][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[10][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[10][2] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_10<double>;
    m_flower_func_table_0[10][3] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_10<double>;
    m_flower_func_table_0[10][4] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_10<double>;
    m_flower_func_table_0[10][5] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_10<double>;


    m_flower_func_table_0[11][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[11][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[11][2] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_11<double>;
    m_flower_func_table_0[11][3] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_11<double>;
    m_flower_func_table_0[11][4] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_11<double>;
    m_flower_func_table_0[11][5] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_11<double>;


    m_flower_func_table_0[12][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[12][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[12][2] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_12<double>;
    m_flower_func_table_0[12][3] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_12<double>;
    m_flower_func_table_0[12][4] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_12<double>;
    m_flower_func_table_0[12][5] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_12<double>;


    m_flower_func_table_0[13][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[13][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[13][2] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_13<double>;
    m_flower_func_table_0[13][3] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_13<double>;
    m_flower_func_table_0[13][4] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_13<double>;
    m_flower_func_table_0[13][5] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_13<double>;


    m_flower_func_table_0[14][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[14][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[14][2] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[14][3] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[14][4] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[14][5] = &ZrO_Clexulator_hop0_1::zero_func<double>;


    m_flower_func_table_0[15][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[15][1] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_1_0_at_15<double>;
    m_flower_func_table_0[15][2] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[15][3] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[15][4] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[15][5] = &ZrO_Clexulator_hop0_1::zero_func<double>;


    m_flower_func_table_0[16][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[16][1] = &ZrO_Clexulator_hop0_1::site_eval_bfunc_1_0_at_16<double>;
    m_flower_func_table_0[16][2] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[16][3] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[16][4] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_flower_func_table_0[16][5] = &ZrO_Clexulator_hop0_1::zero_func<double>;


    m_delta_func_table_0[0][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[0][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[0][2] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[0][3] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[0][4] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[0][5] = &ZrO_Clexulator_hop0_1::zero_func<double>;


    m_delta_func_table_0[1][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[1][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[1][2] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[1][3] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[1][4] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[1][5] = &ZrO_Clexulator_hop0_1::zero_func<double>;


    m_delta_func_table_0[2][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[2][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[2][2] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_2<double>;
    m_delta_func_table_0[2][3] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_2<double>;
    m_delta_func_table_0[2][4] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_2<double>;
    m_delta_func_table_0[2][5] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_2<double>;


    m_delta_func_table_0[3][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[3][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[3][2] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_3<double>;
    m_delta_func_table_0[3][3] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_3<double>;
    m_delta_func_table_0[3][4] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_3<double>;
    m_delta_func_table_0[3][5] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_3<double>;


    m_delta_func_table_0[4][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[4][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[4][2] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_4<double>;
    m_delta_func_table_0[4][3] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_4<double>;
    m_delta_func_table_0[4][4] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_4<double>;
    m_delta_func_table_0[4][5] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_4<double>;


    m_delta_func_table_0[5][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[5][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[5][2] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_5<double>;
    m_delta_func_table_0[5][3] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_5<double>;
    m_delta_func_table_0[5][4] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_5<double>;
    m_delta_func_table_0[5][5] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_5<double>;


    m_delta_func_table_0[6][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[6][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[6][2] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_6<double>;
    m_delta_func_table_0[6][3] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_6<double>;
    m_delta_func_table_0[6][4] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_6<double>;
    m_delta_func_table_0[6][5] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_6<double>;


    m_delta_func_table_0[7][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[7][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[7][2] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_7<double>;
    m_delta_func_table_0[7][3] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_7<double>;
    m_delta_func_table_0[7][4] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_7<double>;
    m_delta_func_table_0[7][5] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_7<double>;


    m_delta_func_table_0[8][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[8][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[8][2] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_8<double>;
    m_delta_func_table_0[8][3] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_8<double>;
    m_delta_func_table_0[8][4] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_8<double>;
    m_delta_func_table_0[8][5] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_8<double>;


    m_delta_func_table_0[9][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[9][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[9][2] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_9<double>;
    m_delta_func_table_0[9][3] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_9<double>;
    m_delta_func_table_0[9][4] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_9<double>;
    m_delta_func_table_0[9][5] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_9<double>;


    m_delta_func_table_0[10][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[10][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[10][2] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_10<double>;
    m_delta_func_table_0[10][3] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_10<double>;
    m_delta_func_table_0[10][4] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_10<double>;
    m_delta_func_table_0[10][5] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_10<double>;


    m_delta_func_table_0[11][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[11][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[11][2] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_11<double>;
    m_delta_func_table_0[11][3] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_11<double>;
    m_delta_func_table_0[11][4] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_11<double>;
    m_delta_func_table_0[11][5] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_11<double>;


    m_delta_func_table_0[12][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[12][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[12][2] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_12<double>;
    m_delta_func_table_0[12][3] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_12<double>;
    m_delta_func_table_0[12][4] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_12<double>;
    m_delta_func_table_0[12][5] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_12<double>;


    m_delta_func_table_0[13][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[13][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[13][2] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_13<double>;
    m_delta_func_table_0[13][3] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_13<double>;
    m_delta_func_table_0[13][4] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_13<double>;
    m_delta_func_table_0[13][5] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_13<double>;


    m_delta_func_table_0[14][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[14][1] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[14][2] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[14][3] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[14][4] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[14][5] = &ZrO_Clexulator_hop0_1::zero_func<double>;


    m_delta_func_table_0[15][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[15][1] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_1_0_at_15<double>;
    m_delta_func_table_0[15][2] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[15][3] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[15][4] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[15][5] = &ZrO_Clexulator_hop0_1::zero_func<double>;


    m_delta_func_table_0[16][0] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[16][1] = &ZrO_Clexulator_hop0_1::site_deval_bfunc_1_0_at_16<double>;
    m_delta_func_table_0[16][2] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[16][3] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[16][4] = &ZrO_Clexulator_hop0_1::zero_func<double>;
    m_delta_func_table_0[16][5] = &ZrO_Clexulator_hop0_1::zero_func<double>;


    m_weight_matrix.row(0) << 2, -1, 0;
    m_weight_matrix.row(1) << -1, 2, 0;
    m_weight_matrix.row(2) << 0, 0, 5;

    m_sublat_indices = std::set<int>{2, 3};

    m_n_sublattices = 4;

    m_neighborhood = std::set<xtal::UnitCell> {
      xtal::UnitCell(-1, -1, 0),
      xtal::UnitCell(-1, 0, 0),
      xtal::UnitCell(0, -1, 0),
      xtal::UnitCell(0, 0, -1),
      xtal::UnitCell(0, 0, 1),
      xtal::UnitCell(0, 1, 0),
      xtal::UnitCell(1, 0, 0),
      xtal::UnitCell(1, 1, 0)
    };


    m_orbit_neighborhood.resize(corr_size());
    m_orbit_site_neighborhood.resize(corr_size());
    m_orbit_neighborhood[1] = std::set<xtal::UnitCell> {
      xtal::UnitCell(0, 0, -1),
      xtal::UnitCell(0, 0, 1)
    };

    m_orbit_site_neighborhood[1] = std::set<xtal::UnitCellCoord> {
      xtal::UnitCellCoord(3, 0, 0, -1),
      xtal::UnitCellCoord(2, 0, 0, 1)
    };

    m_orbit_neighborhood[2] = std::set<xtal::UnitCell> {
      xtal::UnitCell(-1, -1, 0),
      xtal::UnitCell(-1, 0, 0),
      xtal::UnitCell(0, -1, 0),
      xtal::UnitCell(0, 1, 0),
      xtal::UnitCell(1, 0, 0),
      xtal::UnitCell(1, 1, 0)
    };

    m_orbit_site_neighborhood[2] = std::set<xtal::UnitCellCoord> {
      xtal::UnitCellCoord(2, -1, -1, 0),
      xtal::UnitCellCoord(3, -1, -1, 0),
      xtal::UnitCellCoord(2, -1, 0, 0),
      xtal::UnitCellCoord(3, -1, 0, 0),
      xtal::UnitCellCoord(2, 0, -1, 0),
      xtal::UnitCellCoord(3, 0, -1, 0),
      xtal::UnitCellCoord(2, 0, 1, 0),
      xtal::UnitCellCoord(3, 0, 1, 0),
      xtal::UnitCellCoord(2, 1, 0, 0),
      xtal::UnitCellCoord(3, 1, 0, 0),
      xtal::UnitCellCoord(2, 1, 1, 0),
      xtal::UnitCellCoord(3, 1, 1, 0)
    };

    m_orbit_neighborhood[3] = std::set<xtal::UnitCell> {
      xtal::UnitCell(-1, -1, 0),
      xtal::UnitCell(-1, 0, 0),
      xtal::UnitCell(0, -1, 0),
      xtal::UnitCell(0, 1, 0),
      xtal::UnitCell(1, 0, 0),
      xtal::UnitCell(1, 1, 0)
    };

    m_orbit_site_neighborhood[3] = std::set<xtal::UnitCellCoord> {
      xtal::UnitCellCoord(2, -1, -1, 0),
      xtal::UnitCellCoord(3, -1, -1, 0),
      xtal::UnitCellCoord(2, -1, 0, 0),
      xtal::UnitCellCoord(3, -1, 0, 0),
      xtal::UnitCellCoord(2, 0, -1, 0),
      xtal::UnitCellCoord(3, 0, -1, 0),
      xtal::UnitCellCoord(2, 0, 1, 0),
      xtal::UnitCellCoord(3, 0, 1, 0),
      xtal::UnitCellCoord(2, 1, 0, 0),
      xtal::UnitCellCoord(3, 1, 0, 0),
      xtal::UnitCellCoord(2, 1, 1, 0),
      xtal::UnitCellCoord(3, 1, 1, 0)
    };

    m_orbit_neighborhood[4] = std::set<xtal::UnitCell> {
      xtal::UnitCell(-1, -1, 0),
      xtal::UnitCell(-1, 0, 0),
      xtal::UnitCell(0, -1, 0),
      xtal::UnitCell(0, 1, 0),
      xtal::UnitCell(1, 0, 0),
      xtal::UnitCell(1, 1, 0)
    };

    m_orbit_site_neighborhood[4] = std::set<xtal::UnitCellCoord> {
      xtal::UnitCellCoord(2, -1, -1, 0),
      xtal::UnitCellCoord(3, -1, -1, 0),
      xtal::UnitCellCoord(2, -1, 0, 0),
      xtal::UnitCellCoord(3, -1, 0, 0),
      xtal::UnitCellCoord(2, 0, -1, 0),
      xtal::UnitCellCoord(3, 0, -1, 0),
      xtal::UnitCellCoord(2, 0, 1, 0),
      xtal::UnitCellCoord(3, 0, 1, 0),
      xtal::UnitCellCoord(2, 1, 0, 0),
      xtal::UnitCellCoord(3, 1, 0, 0),
      xtal::UnitCellCoord(2, 1, 1, 0),
      xtal::UnitCellCoord(3, 1, 1, 0)
    };

    m_orbit_neighborhood[5] = std::set<xtal::UnitCell> {
      xtal::UnitCell(-1, -1, 0),
      xtal::UnitCell(-1, 0, 0),
      xtal::UnitCell(0, -1, 0),
      xtal::UnitCell(0, 1, 0),
      xtal::UnitCell(1, 0, 0),
      xtal::UnitCell(1, 1, 0)
    };

    m_orbit_site_neighborhood[5] = std::set<xtal::UnitCellCoord> {
      xtal::UnitCellCoord(2, -1, -1, 0),
      xtal::UnitCellCoord(3, -1, -1, 0),
      xtal::UnitCellCoord(2, -1, 0, 0),
      xtal::UnitCellCoord(3, -1, 0, 0),
      xtal::UnitCellCoord(2, 0, -1, 0),
      xtal::UnitCellCoord(3, 0, -1, 0),
      xtal::UnitCellCoord(2, 0, 1, 0),
      xtal::UnitCellCoord(3, 0, 1, 0),
      xtal::UnitCellCoord(2, 1, 0, 0),
      xtal::UnitCellCoord(3, 1, 0, 0),
      xtal::UnitCellCoord(2, 1, 1, 0),
      xtal::UnitCellCoord(3, 1, 1, 0)
    };

  }


  ZrO_Clexulator_hop0_1::~ZrO_Clexulator_hop0_1() {
    //nothing here for now
  }

  /// \brief Calculate contribution to global correlations from one unit cell
  void ZrO_Clexulator_hop0_1::_calc_global_corr_contribution(double *corr_begin) const {
    _calc_global_corr_contribution();
    for(size_type i = 0; i < corr_size(); i++) {
      *(corr_begin + i) = ParamPack::Val<double>::get(m_params, m_corr_param_key, i);
    }
  }

  /// \brief Calculate contribution to global correlations from one unit cell
  void ZrO_Clexulator_hop0_1::_calc_global_corr_contribution() const {
    m_params.pre_eval();
    {
      _global_prepare<double>();
      for(size_type i = 0; i < corr_size(); i++) {
        ParamPack::Val<double>::set(m_params, m_corr_param_key, i, (this->*m_orbit_func_table_0[i])());
      }
    }
    m_params.post_eval();
  }

  /// \brief Calculate contribution to select global correlations from one unit cell
  void ZrO_Clexulator_hop0_1::_calc_restricted_global_corr_contribution(double *corr_begin, size_type const *ind_list_begin, size_type const *ind_list_end) const {
    _calc_restricted_global_corr_contribution(ind_list_begin, ind_list_end);
    for(; ind_list_begin < ind_list_end; ind_list_begin++) {
      *(corr_begin + *ind_list_begin) = ParamPack::Val<double>::get(m_params, m_corr_param_key, *ind_list_begin);
    }
  }

  /// \brief Calculate contribution to select global correlations from one unit cell
  void ZrO_Clexulator_hop0_1::_calc_restricted_global_corr_contribution(size_type const *ind_list_begin, size_type const *ind_list_end) const {
    m_params.pre_eval();
    {
      _global_prepare<double>();
      for(; ind_list_begin < ind_list_end; ind_list_begin++) {
        ParamPack::Val<double>::set(m_params, m_corr_param_key, *ind_list_begin, (this->*m_orbit_func_table_0[*ind_list_begin])());
      }
    }
    m_params.post_eval();
  }

  /// \brief Calculate point correlations about basis site 'nlist_ind'
  void ZrO_Clexulator_hop0_1::_calc_point_corr(int nlist_ind, double *corr_begin) const {
    _calc_point_corr(nlist_ind);
    for(size_type i = 0; i < corr_size(); i++) {
      *(corr_begin + i) = ParamPack::Val<double>::get(m_params, m_corr_param_key, i);
    }
  }

  /// \brief Calculate point correlations about basis site 'nlist_ind'
  void ZrO_Clexulator_hop0_1::_calc_point_corr(int nlist_ind) const {
    m_params.pre_eval();
    {
      _point_prepare<double>(nlist_ind);
      for(size_type i = 0; i < corr_size(); i++) {
        ParamPack::Val<double>::set(m_params, m_corr_param_key, i, (this->*m_flower_func_table_0[nlist_ind][i])());
      }
    }
    m_params.post_eval();
  }

  /// \brief Calculate select point correlations about basis site 'nlist_ind'
  void ZrO_Clexulator_hop0_1::_calc_restricted_point_corr(int nlist_ind, double *corr_begin, size_type const *ind_list_begin, size_type const *ind_list_end) const {
    _calc_restricted_point_corr(nlist_ind, ind_list_begin, ind_list_end);
    for(; ind_list_begin < ind_list_end; ind_list_begin++) {
      *(corr_begin + *ind_list_begin) = ParamPack::Val<double>::get(m_params, m_corr_param_key, *ind_list_begin);
    }
  }

  /// \brief Calculate select point correlations about basis site 'nlist_ind'
  void ZrO_Clexulator_hop0_1::_calc_restricted_point_corr(int nlist_ind, size_type const *ind_list_begin, size_type const *ind_list_end) const {
    m_params.pre_eval();
    {
      _point_prepare<double>(nlist_ind);
      for(; ind_list_begin < ind_list_end; ind_list_begin++) {
        ParamPack::Val<double>::set(m_params, m_corr_param_key, *ind_list_begin, (this->*m_flower_func_table_0[nlist_ind][*ind_list_begin])());
      }
    }
    m_params.post_eval();
  }

  /// \brief Calculate the change in point correlations due to changing an occupant
  void ZrO_Clexulator_hop0_1::_calc_delta_point_corr(int nlist_ind, int occ_i, int occ_f, double *corr_begin) const {
    _calc_delta_point_corr(nlist_ind, occ_i, occ_f);
    for(size_type i = 0; i < corr_size(); i++) {
      *(corr_begin + i) = ParamPack::Val<double>::get(m_params, m_corr_param_key, i);
    }
  }

  /// \brief Calculate the change in point correlations due to changing an occupant
  void ZrO_Clexulator_hop0_1::_calc_delta_point_corr(int nlist_ind, int occ_i, int occ_f) const {
    m_params.pre_eval();
    {
      _point_prepare<double>(nlist_ind);
     for(size_type i = 0; i < corr_size(); i++) {
        ParamPack::Val<double>::set(m_params, m_corr_param_key, i, (this->*m_delta_func_table_0[nlist_ind][i])(occ_i, occ_f));
      }
    }
    m_params.post_eval();
  }

  /// \brief Calculate the change in select point correlations due to changing an occupant
  void ZrO_Clexulator_hop0_1::_calc_restricted_delta_point_corr(int nlist_ind, int occ_i, int occ_f, double *corr_begin, size_type const *ind_list_begin, size_type const *ind_list_end) const {
    _calc_restricted_delta_point_corr(nlist_ind, occ_i, occ_f, ind_list_begin, ind_list_end);
    for(; ind_list_begin < ind_list_end; ind_list_begin++) {
      *(corr_begin + *ind_list_begin) = ParamPack::Val<double>::get(m_params, m_corr_param_key, *ind_list_begin);
    }
  }

  /// \brief Calculate the change in select point correlations due to changing an occupant
  void ZrO_Clexulator_hop0_1::_calc_restricted_delta_point_corr(int nlist_ind, int occ_i, int occ_f, size_type const *ind_list_begin, size_type const *ind_list_end) const {
    m_params.pre_eval();
    {
      _point_prepare<double>(nlist_ind);
      for(; ind_list_begin < ind_list_end; ind_list_begin++) {
        ParamPack::Val<double>::set(m_params, m_corr_param_key, *ind_list_begin, (this->*m_delta_func_table_0[nlist_ind][*ind_list_begin])(occ_i, occ_f));
      }
    }
    m_params.post_eval();
  }


  template<typename Scalar>
  void ZrO_Clexulator_hop0_1::_point_prepare(int nlist_ind) const {
    switch(nlist_ind) {
    case 2:
      if(m_params.eval_mode(m_occ_site_func_param_key) != ParamPack::READ) {
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 2, eval_occ_func_2_0(2));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 4, eval_occ_func_2_0(4));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 6, eval_occ_func_2_0(6));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 3, eval_occ_func_3_0(3));
      }
      break;
    case 3:
      if(m_params.eval_mode(m_occ_site_func_param_key) != ParamPack::READ) {
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 2, eval_occ_func_2_0(2));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 3, eval_occ_func_3_0(3));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 5, eval_occ_func_3_0(5));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 7, eval_occ_func_3_0(7));
      }
      break;
    case 4:
      if(m_params.eval_mode(m_occ_site_func_param_key) != ParamPack::READ) {
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 2, eval_occ_func_2_0(2));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 4, eval_occ_func_2_0(4));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 8, eval_occ_func_2_0(8));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 5, eval_occ_func_3_0(5));
      }
      break;
    case 5:
      if(m_params.eval_mode(m_occ_site_func_param_key) != ParamPack::READ) {
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 4, eval_occ_func_2_0(4));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 3, eval_occ_func_3_0(3));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 5, eval_occ_func_3_0(5));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 9, eval_occ_func_3_0(9));
      }
      break;
    case 6:
      if(m_params.eval_mode(m_occ_site_func_param_key) != ParamPack::READ) {
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 2, eval_occ_func_2_0(2));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 6, eval_occ_func_2_0(6));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 10, eval_occ_func_2_0(10));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 7, eval_occ_func_3_0(7));
      }
      break;
    case 7:
      if(m_params.eval_mode(m_occ_site_func_param_key) != ParamPack::READ) {
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 6, eval_occ_func_2_0(6));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 3, eval_occ_func_3_0(3));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 7, eval_occ_func_3_0(7));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 11, eval_occ_func_3_0(11));
      }
      break;
    case 15:
      if(m_params.eval_mode(m_occ_site_func_param_key) != ParamPack::READ) {
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 15, eval_occ_func_3_0(15));
      }
      break;
    case 16:
      if(m_params.eval_mode(m_occ_site_func_param_key) != ParamPack::READ) {
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 16, eval_occ_func_2_0(16));
      }
      break;
    case 8:
      if(m_params.eval_mode(m_occ_site_func_param_key) != ParamPack::READ) {
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 4, eval_occ_func_2_0(4));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 8, eval_occ_func_2_0(8));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 12, eval_occ_func_2_0(12));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 9, eval_occ_func_3_0(9));
      }
      break;
    case 9:
      if(m_params.eval_mode(m_occ_site_func_param_key) != ParamPack::READ) {
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 8, eval_occ_func_2_0(8));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 5, eval_occ_func_3_0(5));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 9, eval_occ_func_3_0(9));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 13, eval_occ_func_3_0(13));
      }
      break;
    case 10:
      if(m_params.eval_mode(m_occ_site_func_param_key) != ParamPack::READ) {
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 6, eval_occ_func_2_0(6));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 10, eval_occ_func_2_0(10));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 12, eval_occ_func_2_0(12));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 11, eval_occ_func_3_0(11));
      }
      break;
    case 11:
      if(m_params.eval_mode(m_occ_site_func_param_key) != ParamPack::READ) {
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 10, eval_occ_func_2_0(10));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 7, eval_occ_func_3_0(7));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 11, eval_occ_func_3_0(11));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 13, eval_occ_func_3_0(13));
      }
      break;
    case 12:
      if(m_params.eval_mode(m_occ_site_func_param_key) != ParamPack::READ) {
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 8, eval_occ_func_2_0(8));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 10, eval_occ_func_2_0(10));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 12, eval_occ_func_2_0(12));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 13, eval_occ_func_3_0(13));
      }
      break;
    case 13:
      if(m_params.eval_mode(m_occ_site_func_param_key) != ParamPack::READ) {
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 12, eval_occ_func_2_0(12));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 9, eval_occ_func_3_0(9));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 11, eval_occ_func_3_0(11));
        ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 13, eval_occ_func_3_0(13));
      }
      break;
    }
  }
  template<typename Scalar>
  void ZrO_Clexulator_hop0_1::_global_prepare() const {
  if(m_params.eval_mode(m_occ_site_func_param_key) != ParamPack::READ) {
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 2, eval_occ_func_2_0(2));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 4, eval_occ_func_2_0(4));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 6, eval_occ_func_2_0(6));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 8, eval_occ_func_2_0(8));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 10, eval_occ_func_2_0(10));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 12, eval_occ_func_2_0(12));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 16, eval_occ_func_2_0(16));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 3, eval_occ_func_3_0(3));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 5, eval_occ_func_3_0(5));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 7, eval_occ_func_3_0(7));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 9, eval_occ_func_3_0(9));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 11, eval_occ_func_3_0(11));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 13, eval_occ_func_3_0(13));
    ParamPack::Val<Scalar>::set(m_params, m_occ_site_func_param_key, 0, 15, eval_occ_func_3_0(15));
  }
  }

  // Basis functions for empty cluster:
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::eval_bfunc_0_0() const {
    return 1;
  }

  /**** Basis functions for orbit 1****
0.3333333 0.6666667 -0.2500000 Va  O  

  ****/
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::eval_bfunc_1_0() const {
    return (occ_func_2_0(15) + occ_func_2_0(16)) / 2.;
  }

  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_1_0_at_15() const {
    return (occ_func_2_0(15)) / 2.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_1_0_at_16() const {
    return (occ_func_2_0(16)) / 2.;
  }
    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_1_0_at_15(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (1) / 2.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_1_0_at_16(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (1) / 2.;
  }

  /**** Basis functions for orbit 2****
-0.6666667 0.6666667 0.2500000 Va  O  

  ****/
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::eval_bfunc_2_0() const {
    return (occ_func_3_0(4) + occ_func_3_0(6) + occ_func_3_0(12) + occ_func_3_0(11) + occ_func_3_0(3) + occ_func_3_0(9) + occ_func_3_0(8) + occ_func_3_0(2) + occ_func_3_0(10) + occ_func_3_0(5) + occ_func_3_0(13) + occ_func_3_0(7)) / 12.;
  }

  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_2() const {
    return (occ_func_3_0(2)) / 12.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_3() const {
    return (occ_func_3_0(3)) / 12.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_4() const {
    return (occ_func_3_0(4)) / 12.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_5() const {
    return (occ_func_3_0(5)) / 12.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_6() const {
    return (occ_func_3_0(6)) / 12.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_7() const {
    return (occ_func_3_0(7)) / 12.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_8() const {
    return (occ_func_3_0(8)) / 12.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_9() const {
    return (occ_func_3_0(9)) / 12.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_10() const {
    return (occ_func_3_0(10)) / 12.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_11() const {
    return (occ_func_3_0(11)) / 12.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_12() const {
    return (occ_func_3_0(12)) / 12.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_2_0_at_13() const {
    return (occ_func_3_0(13)) / 12.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_2(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (1) / 12.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_3(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (1) / 12.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_4(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (1) / 12.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_5(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (1) / 12.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_6(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (1) / 12.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_7(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (1) / 12.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_8(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (1) / 12.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_9(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (1) / 12.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_10(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (1) / 12.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_11(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (1) / 12.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_12(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (1) / 12.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_2_0_at_13(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (1) / 12.;
  }

  /**** Basis functions for orbit 3****
-0.6666667 0.6666667 0.2500000 Va  O  

-0.6666667 0.6666667 0.7500000 Va  O  

  ****/
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::eval_bfunc_3_0() const {
    return (occ_func_3_0(4) * occ_func_2_0(5) + occ_func_3_0(6) * occ_func_2_0(7) + occ_func_3_0(12) * occ_func_2_0(13) + occ_func_3_0(11) * occ_func_2_0(10) + occ_func_3_0(3) * occ_func_2_0(2) + occ_func_3_0(9) * occ_func_2_0(8)) / 6.;
  }

  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_2() const {
    return (occ_func_3_0(3) * occ_func_2_0(2)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_3() const {
    return (occ_func_3_0(3) * occ_func_2_0(2)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_4() const {
    return (occ_func_3_0(4) * occ_func_2_0(5)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_5() const {
    return (occ_func_3_0(4) * occ_func_2_0(5)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_6() const {
    return (occ_func_3_0(6) * occ_func_2_0(7)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_7() const {
    return (occ_func_3_0(6) * occ_func_2_0(7)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_8() const {
    return (occ_func_3_0(9) * occ_func_2_0(8)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_9() const {
    return (occ_func_3_0(9) * occ_func_2_0(8)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_10() const {
    return (occ_func_3_0(11) * occ_func_2_0(10)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_11() const {
    return (occ_func_3_0(11) * occ_func_2_0(10)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_12() const {
    return (occ_func_3_0(12) * occ_func_2_0(13)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_3_0_at_13() const {
    return (occ_func_3_0(12) * occ_func_2_0(13)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_2(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (occ_func_3_0(3)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_3(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (occ_func_2_0(2)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_4(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (occ_func_2_0(5)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_5(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (occ_func_3_0(4)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_6(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (occ_func_2_0(7)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_7(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (occ_func_3_0(6)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_8(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (occ_func_3_0(9)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_9(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (occ_func_2_0(8)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_10(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (occ_func_3_0(11)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_11(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (occ_func_2_0(10)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_12(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (occ_func_2_0(13)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_3_0_at_13(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (occ_func_3_0(12)) / 6.;
  }

  /**** Basis functions for orbit 4****
-0.6666667 0.6666667 0.2500000 Va  O  

0.3333333 1.6666667 0.2500000 Va  O  

  ****/
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::eval_bfunc_4_0() const {
    return (occ_func_3_0(4) * occ_func_3_0(8) + occ_func_3_0(6) * occ_func_3_0(2) + occ_func_3_0(12) * occ_func_3_0(10) + occ_func_3_0(11) * occ_func_3_0(13) + occ_func_3_0(3) * occ_func_3_0(7) + occ_func_3_0(9) * occ_func_3_0(5)) / 6.;
  }

  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_2() const {
    return (occ_func_3_0(6) * occ_func_3_0(2)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_3() const {
    return (occ_func_3_0(3) * occ_func_3_0(7)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_4() const {
    return (occ_func_3_0(4) * occ_func_3_0(8)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_5() const {
    return (occ_func_3_0(9) * occ_func_3_0(5)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_6() const {
    return (occ_func_3_0(6) * occ_func_3_0(2)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_7() const {
    return (occ_func_3_0(3) * occ_func_3_0(7)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_8() const {
    return (occ_func_3_0(4) * occ_func_3_0(8)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_9() const {
    return (occ_func_3_0(9) * occ_func_3_0(5)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_10() const {
    return (occ_func_3_0(12) * occ_func_3_0(10)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_11() const {
    return (occ_func_3_0(11) * occ_func_3_0(13)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_12() const {
    return (occ_func_3_0(12) * occ_func_3_0(10)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_4_0_at_13() const {
    return (occ_func_3_0(11) * occ_func_3_0(13)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_2(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (occ_func_3_0(6)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_3(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (occ_func_3_0(7)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_4(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (occ_func_3_0(8)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_5(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (occ_func_3_0(9)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_6(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (occ_func_3_0(2)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_7(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (occ_func_3_0(3)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_8(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (occ_func_3_0(4)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_9(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (occ_func_3_0(5)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_10(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (occ_func_3_0(12)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_11(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (occ_func_3_0(13)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_12(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (occ_func_3_0(10)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_4_0_at_13(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (occ_func_3_0(11)) / 6.;
  }

  /**** Basis functions for orbit 5****
0.3333333 -0.3333333 0.2500000 Va  O  

1.3333333 0.6666667 0.2500000 Va  O  

  ****/
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::eval_bfunc_5_0() const {
    return (occ_func_3_0(6) * occ_func_3_0(10) + occ_func_3_0(12) * occ_func_3_0(8) + occ_func_3_0(4) * occ_func_3_0(2) + occ_func_3_0(3) * occ_func_3_0(5) + occ_func_3_0(9) * occ_func_3_0(13) + occ_func_3_0(11) * occ_func_3_0(7)) / 6.;
  }

  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_2() const {
    return (occ_func_3_0(4) * occ_func_3_0(2)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_3() const {
    return (occ_func_3_0(3) * occ_func_3_0(5)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_4() const {
    return (occ_func_3_0(4) * occ_func_3_0(2)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_5() const {
    return (occ_func_3_0(3) * occ_func_3_0(5)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_6() const {
    return (occ_func_3_0(6) * occ_func_3_0(10)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_7() const {
    return (occ_func_3_0(11) * occ_func_3_0(7)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_8() const {
    return (occ_func_3_0(12) * occ_func_3_0(8)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_9() const {
    return (occ_func_3_0(9) * occ_func_3_0(13)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_10() const {
    return (occ_func_3_0(6) * occ_func_3_0(10)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_11() const {
    return (occ_func_3_0(11) * occ_func_3_0(7)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_12() const {
    return (occ_func_3_0(12) * occ_func_3_0(8)) / 6.;
  }
  template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_eval_bfunc_5_0_at_13() const {
    return (occ_func_3_0(9) * occ_func_3_0(13)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_2(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (occ_func_3_0(4)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_3(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (occ_func_3_0(5)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_4(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (occ_func_3_0(2)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_5(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (occ_func_3_0(3)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_6(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (occ_func_3_0(10)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_7(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (occ_func_3_0(11)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_8(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (occ_func_3_0(12)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_9(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (occ_func_3_0(13)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_10(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (occ_func_3_0(6)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_11(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (occ_func_3_0(7)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_12(int occ_i, int occ_f) const {
    return (m_occ_func_2_0[occ_f] - m_occ_func_2_0[occ_i]) * (occ_func_3_0(8)) / 6.;
  }

    template<typename Scalar>
  Scalar ZrO_Clexulator_hop0_1::site_deval_bfunc_5_0_at_13(int occ_i, int occ_f) const {
    return (m_occ_func_3_0[occ_f] - m_occ_func_3_0[occ_i]) * (occ_func_3_0(9)) / 6.;
  }

} // namespace clexulator
} // namespace CASM


extern "C" {
  /// \brief Returns a clexulator::BaseClexulator* owning a ZrO_Clexulator_hop0_1
  CASM::clexulator::BaseClexulator *make_ZrO_Clexulator_hop0_1() {
    return new CASM::clexulator::ZrO_Clexulator_hop0_1();
  }

}

