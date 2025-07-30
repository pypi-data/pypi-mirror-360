#include "casm/clexulator/ConfigDoFValues.hh"
#include "casm/clexulator/ConfigDoFValuesTools_impl.hh"
#include "casm/clexulator/DoFSpace.hh"
#include "casm/clexulator/OrderParameter.hh"
#include "casm/crystallography/BasicStructureTools.hh"
#include "casm/crystallography/CanonicalForm.hh"
#include "casm/crystallography/SuperlatticeEnumerator.hh"
#include "gtest/gtest.h"
#include "teststructures.hh"

using namespace CASM;
using namespace test;

namespace {

Eigen::Matrix3l _fcc_conventional_transf_mat() {
  Eigen::Matrix3l transf_mat;
  transf_mat << -1, 1, 1, 1, -1, 1, 1, 1, -1;
  return transf_mat;
}

std::shared_ptr<xtal::BasicStructure const> make_shared_prim(
    xtal::BasicStructure const &prim) {
  return std::make_shared<xtal::BasicStructure const>(prim);
}

}  // namespace

class FCCBinaryDoFSpaceValuesTest : public testing::Test {
 protected:
  std::shared_ptr<xtal::BasicStructure const> prim;
  Eigen::Matrix3l transformation_matrix_to_super;

  FCCBinaryDoFSpaceValuesTest()
      : prim(make_shared_prim(test::FCC_binary_prim())),
        transformation_matrix_to_super(_fcc_conventional_transf_mat()) {}
};

TEST_F(FCCBinaryDoFSpaceValuesTest, Test1) {
  // Construct the occupation DoF space.
  DoFKey dof_key = "occ";
  clexulator::DoFSpace dof_space = clexulator::make_local_dof_space(
      dof_key, prim, transformation_matrix_to_super);
  EXPECT_EQ(dof_space.axis_info.site_index.value(),
            std::vector<Index>({0, 0, 1, 1, 2, 2, 3, 3}));
  EXPECT_EQ(dof_space.axis_info.dof_component.value(),
            std::vector<Index>({0, 1, 0, 1, 0, 1, 0, 1}));
  EXPECT_EQ(dof_space.dim, 2 * 4);
  EXPECT_EQ(dof_space.dim, dof_space.basis.rows());
}

TEST_F(FCCBinaryDoFSpaceValuesTest, Test2) {
  // Construct the occupation DoF space.
  DoFKey dof_key = "occ";
  clexulator::DoFSpace dof_space = clexulator::make_local_dof_space(
      dof_key, prim, transformation_matrix_to_super);

  // Construct ConfigDoFValues
  Index N_sublat = prim->basis().size();
  Index N_volume = transformation_matrix_to_super.determinant();
  std::map<DoFKey, xtal::DoFSet> global_dof_info =
      clexulator::make_global_dof_info(*prim);
  std::map<DoFKey, std::vector<xtal::SiteDoFSet>> local_dof_info =
      clexulator::make_local_dof_info(*prim);
  clexulator::ConfigDoFValues dof_values =
      clexulator::make_default_config_dof_values(
          N_sublat, N_volume, global_dof_info, local_dof_info);
  EXPECT_EQ(dof_values.occupation.size(), 4);
  EXPECT_EQ(dof_values.local_dof_values.size(), 0);
  EXPECT_EQ(dof_values.global_dof_values.size(), 0);

  Eigen::VectorXd v;
  Eigen::VectorXd v_expected(8);
  Eigen::VectorXi occ_expected(4);

  occ_expected << 0, 0, 0, 0;
  EXPECT_TRUE(CASM::almost_equal(dof_values.occupation, occ_expected));

  v = clexulator::get_dof_vector_value(
      dof_values, transformation_matrix_to_super, dof_space);
  v_expected << 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0;
  EXPECT_EQ(v.size(), 8);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  dof_values.occupation << 1, 0, 0, 0;
  v = clexulator::get_dof_vector_value(
      dof_values, transformation_matrix_to_super, dof_space);
  v_expected << 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0;
  EXPECT_EQ(v.size(), 8);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  dof_values.occupation << 0, 1, 0, 0;
  v = clexulator::get_dof_vector_value(
      dof_values, transformation_matrix_to_super, dof_space);
  v_expected << 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0;
  EXPECT_EQ(v.size(), 8);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  dof_values.occupation << 1, 1, 1, 1;
  v = clexulator::get_dof_vector_value(
      dof_values, transformation_matrix_to_super, dof_space);
  v_expected << 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0;
  EXPECT_EQ(v.size(), 8);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));
}

// Test basis change and get_normal_coordinate
TEST_F(FCCBinaryDoFSpaceValuesTest, Test3) {
  // Construct the occupation DoF space.
  DoFKey dof_key = "occ";
  std::set<Index> site_indices = {0, 1, 2, 3};
  Eigen::MatrixXd basis = Eigen::MatrixXd::Identity(8, 8);
  // flip meaning of first two values
  basis(0, 0) = 0.0;
  basis(1, 1) = 0.0;
  basis(1, 0) = 1.0;
  basis(0, 1) = 1.0;
  clexulator::DoFSpace dof_space = clexulator::make_local_dof_space(
      dof_key, prim, transformation_matrix_to_super, site_indices, basis);

  // Construct ConfigDoFValues
  Index N_sublat = prim->basis().size();
  Index N_volume = transformation_matrix_to_super.determinant();
  std::map<DoFKey, xtal::DoFSet> global_dof_info =
      clexulator::make_global_dof_info(*prim);
  std::map<DoFKey, std::vector<xtal::SiteDoFSet>> local_dof_info =
      clexulator::make_local_dof_info(*prim);
  clexulator::ConfigDoFValues dof_values =
      clexulator::make_default_config_dof_values(
          N_sublat, N_volume, global_dof_info, local_dof_info);
  EXPECT_EQ(dof_values.occupation.size(), 4);
  EXPECT_EQ(dof_values.local_dof_values.size(), 0);
  EXPECT_EQ(dof_values.global_dof_values.size(), 0);

  Eigen::VectorXd v;
  Eigen::VectorXd v_expected(8);
  Eigen::VectorXi occ_expected(4);

  occ_expected << 0, 0, 0, 0;
  EXPECT_TRUE(CASM::almost_equal(dof_values.occupation, occ_expected));

  v = clexulator::get_dof_vector_value(
      dof_values, transformation_matrix_to_super, dof_space);
  v_expected << 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0;
  EXPECT_EQ(v.size(), 8);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  v = clexulator::get_normal_coordinate(
      dof_values, transformation_matrix_to_super, dof_space);
  v_expected << 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0;
  EXPECT_EQ(v.size(), 8);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));
}

// Test get_normal_coordinate_at and get_normal_coordinate
TEST_F(FCCBinaryDoFSpaceValuesTest, Test4) {
  // Construct the occupation DoF space.
  DoFKey dof_key = "occ";
  Eigen::Matrix3l T_dof_space = Eigen::Matrix3l::Identity();
  clexulator::DoFSpace dof_space =
      clexulator::make_local_dof_space(dof_key, prim, T_dof_space);

  // Construct ConfigDoFValues
  Eigen::Matrix3l T_config = transformation_matrix_to_super;
  Index N_sublat = prim->basis().size();
  Index N_volume = T_config.determinant();
  std::map<DoFKey, xtal::DoFSet> global_dof_info =
      clexulator::make_global_dof_info(*prim);
  std::map<DoFKey, std::vector<xtal::SiteDoFSet>> local_dof_info =
      clexulator::make_local_dof_info(*prim);
  clexulator::ConfigDoFValues dof_values =
      clexulator::make_default_config_dof_values(
          N_sublat, N_volume, global_dof_info, local_dof_info);
  EXPECT_EQ(dof_values.occupation.size(), 4);
  EXPECT_EQ(dof_values.local_dof_values.size(), 0);
  EXPECT_EQ(dof_values.global_dof_values.size(), 0);

  xtal::UnitCellIndexConverter unitcell_index_converter(T_config);
  xtal::UnitCellCoordIndexConverter unitcellcoord_index_converter(T_config,
                                                                  N_sublat);
  clexulator::DoFSpaceIndexConverter dof_space_index_converter(
      unitcellcoord_index_converter, dof_space);

  Eigen::VectorXd v;
  Eigen::VectorXd v_expected(2);
  Eigen::VectorXi &occupation = dof_values.occupation;
  occupation << 1, 0, 0, 0;

  v = clexulator::get_normal_coordinate_at(dof_values, dof_space,
                                           dof_space_index_converter,
                                           unitcell_index_converter(0));
  v_expected << 0.0, 1.0;
  EXPECT_EQ(v.size(), 2);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  v = clexulator::get_normal_coordinate_at(dof_values, dof_space,
                                           dof_space_index_converter,
                                           unitcell_index_converter(1));
  v_expected << 1.0, 0.0;
  EXPECT_EQ(v.size(), 2);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  v = clexulator::get_normal_coordinate_at(dof_values, dof_space,
                                           dof_space_index_converter,
                                           unitcell_index_converter(2));
  v_expected << 1.0, 0.0;
  EXPECT_EQ(v.size(), 2);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  v = clexulator::get_normal_coordinate_at(dof_values, dof_space,
                                           dof_space_index_converter,
                                           unitcell_index_converter(3));
  v_expected << 1.0, 0.0;
  EXPECT_EQ(v.size(), 2);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  v = clexulator::get_mean_normal_coordinate(dof_values, T_config, dof_space);
  v_expected << 0.75, 0.25;
  EXPECT_EQ(v.size(), 2);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  // compare to OrderParameter result
  clexulator::OrderParameter order_parameter(dof_space);
  v = order_parameter(T_config, unitcellcoord_index_converter, &dof_values);
  EXPECT_EQ(v.size(), 2);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));
}

class FCCTernaryDoFSpaceValuesTest : public testing::Test {
 protected:
  std::shared_ptr<xtal::BasicStructure const> prim;
  Eigen::Matrix3l transformation_matrix_to_super;

  FCCTernaryDoFSpaceValuesTest()
      : prim(make_shared_prim(test::FCC_ternary_prim())),
        transformation_matrix_to_super(_fcc_conventional_transf_mat()) {}
};

TEST_F(FCCTernaryDoFSpaceValuesTest, Test1) {
  // Construct the occupation DoF space.
  DoFKey dof_key = "occ";
  clexulator::DoFSpace dof_space = clexulator::make_local_dof_space(
      dof_key, prim, transformation_matrix_to_super);
  EXPECT_EQ(dof_space.axis_info.site_index.value(),
            std::vector<Index>({0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3}));
  EXPECT_EQ(dof_space.axis_info.dof_component.value(),
            std::vector<Index>({0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2}));
  EXPECT_EQ(dof_space.dim, 3 * 4);
  EXPECT_EQ(dof_space.dim, dof_space.basis.rows());
}

TEST_F(FCCTernaryDoFSpaceValuesTest, Test2) {
  // Construct the occupation DoF space.
  DoFKey dof_key = "occ";
  clexulator::DoFSpace dof_space = clexulator::make_local_dof_space(
      dof_key, prim, transformation_matrix_to_super);

  // Construct ConfigDoFValues
  Index N_sublat = prim->basis().size();
  Index N_volume = transformation_matrix_to_super.determinant();
  std::map<DoFKey, xtal::DoFSet> global_dof_info =
      clexulator::make_global_dof_info(*prim);
  std::map<DoFKey, std::vector<xtal::SiteDoFSet>> local_dof_info =
      clexulator::make_local_dof_info(*prim);
  clexulator::ConfigDoFValues dof_values =
      clexulator::make_default_config_dof_values(
          N_sublat, N_volume, global_dof_info, local_dof_info);
  EXPECT_EQ(dof_values.occupation.size(), 4);
  EXPECT_EQ(dof_values.local_dof_values.size(), 0);
  EXPECT_EQ(dof_values.global_dof_values.size(), 0);

  Eigen::VectorXd v;
  Eigen::VectorXd v_expected(12);
  Eigen::VectorXi occ_expected(4);

  occ_expected << 0, 0, 0, 0;
  EXPECT_TRUE(CASM::almost_equal(dof_values.occupation, occ_expected));

  v = clexulator::get_dof_vector_value(
      dof_values, transformation_matrix_to_super, dof_space);
  v_expected << 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0;
  EXPECT_EQ(v.size(), 12);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  dof_values.occupation << 1, 0, 0, 0;
  v = clexulator::get_dof_vector_value(
      dof_values, transformation_matrix_to_super, dof_space);
  v_expected << 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0;
  EXPECT_EQ(v.size(), 12);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  dof_values.occupation << 2, 0, 0, 0;
  v = clexulator::get_dof_vector_value(
      dof_values, transformation_matrix_to_super, dof_space);
  v_expected << 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0;
  EXPECT_EQ(v.size(), 12);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  dof_values.occupation << 0, 1, 2, 0;
  v = clexulator::get_dof_vector_value(
      dof_values, transformation_matrix_to_super, dof_space);
  v_expected << 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0;
  EXPECT_EQ(v.size(), 12);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  dof_values.occupation << 1, 1, 2, 2;
  v = clexulator::get_dof_vector_value(
      dof_values, transformation_matrix_to_super, dof_space);
  v_expected << 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0;
  EXPECT_EQ(v.size(), 12);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  dof_values.occupation << 2, 2, 2, 2;
  v = clexulator::get_dof_vector_value(
      dof_values, transformation_matrix_to_super, dof_space);
  v_expected << 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0;
  EXPECT_EQ(v.size(), 12);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));
}

class FCCTernaryGLstrainDispDoFSpaceValuesTest : public testing::Test {
 protected:
  std::shared_ptr<xtal::BasicStructure const> prim;
  Eigen::Matrix3l transformation_matrix_to_super;

  FCCTernaryGLstrainDispDoFSpaceValuesTest()
      : prim(make_shared_prim(test::FCC_ternary_GLstrain_disp_prim())),
        transformation_matrix_to_super(_fcc_conventional_transf_mat()) {}
};

TEST_F(FCCTernaryGLstrainDispDoFSpaceValuesTest, Test1) {
  // Construct the disp DoF space.
  DoFKey dof_key = "disp";
  clexulator::DoFSpace dof_space = clexulator::make_local_dof_space(
      dof_key, prim, transformation_matrix_to_super);
  EXPECT_EQ(dof_space.axis_info.site_index.value(),
            std::vector<Index>({0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3}));
  EXPECT_EQ(dof_space.axis_info.dof_component.value(),
            std::vector<Index>({0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2}));
  EXPECT_EQ(dof_space.dim, 3 * 4);
  EXPECT_EQ(dof_space.dim, dof_space.basis.rows());
}

TEST_F(FCCTernaryGLstrainDispDoFSpaceValuesTest, Test1b) {
  // Construct the disp DoF space.
  DoFKey dof_key = "disp";
  clexulator::DoFSpace dof_space = clexulator::make_local_dof_space(
      dof_key, prim, transformation_matrix_to_super);

  // Construct ConfigDoFValues
  Index N_sublat = prim->basis().size();
  Index N_volume = transformation_matrix_to_super.determinant();
  std::map<DoFKey, xtal::DoFSet> global_dof_info =
      clexulator::make_global_dof_info(*prim);
  std::map<DoFKey, std::vector<xtal::SiteDoFSet>> local_dof_info =
      clexulator::make_local_dof_info(*prim);
  clexulator::ConfigDoFValues dof_values =
      clexulator::make_default_config_dof_values(
          N_sublat, N_volume, global_dof_info, local_dof_info);
  EXPECT_EQ(dof_values.occupation.size(), 4);
  EXPECT_EQ(dof_values.local_dof_values.size(), 1);
  EXPECT_EQ(dof_values.global_dof_values.size(), 1);

  Eigen::VectorXd v;
  Eigen::VectorXd v_expected(12);
  Eigen::MatrixXd &disp_dof_values = dof_values.local_dof_values.at(dof_key);
  Eigen::MatrixXd disp_expected(3, 4);

  disp_expected.setZero();
  EXPECT_TRUE(CASM::almost_equal(disp_dof_values, disp_expected));

  v = clexulator::get_dof_vector_value(
      dof_values, transformation_matrix_to_super, dof_space);
  v_expected << 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0;
  EXPECT_EQ(v.size(), 12);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  disp_dof_values.col(0) << 1.0, 0.0, 0.0;
  v = clexulator::get_dof_vector_value(
      dof_values, transformation_matrix_to_super, dof_space);
  v_expected << 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0;
  EXPECT_EQ(v.size(), 12);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  disp_dof_values.col(1) << 0.0, 1.0, 0.0;
  v = clexulator::get_dof_vector_value(
      dof_values, transformation_matrix_to_super, dof_space);
  v_expected << 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0;
  EXPECT_EQ(v.size(), 12);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));
}

// Test basis change and get_normal_coordinate
TEST_F(FCCTernaryGLstrainDispDoFSpaceValuesTest, Test1c) {
  // Construct the occupation DoF space.
  DoFKey dof_key = "disp";
  std::set<Index> site_indices = {0, 1, 2, 3};
  Eigen::MatrixXd basis = Eigen::MatrixXd::Identity(12, 12);
  // flip meaning of first three and second three values
  basis.block(0, 0, 3, 3) = Eigen::MatrixXd::Zero(3, 3);
  basis.block(3, 3, 3, 3) = Eigen::MatrixXd::Zero(3, 3);
  basis.block(0, 3, 3, 3) = Eigen::MatrixXd::Identity(3, 3);
  basis.block(3, 0, 3, 3) = Eigen::MatrixXd::Identity(3, 3);

  clexulator::DoFSpace dof_space = clexulator::make_local_dof_space(
      dof_key, prim, transformation_matrix_to_super, site_indices, basis);

  // Construct ConfigDoFValues
  Index N_sublat = prim->basis().size();
  Index N_volume = transformation_matrix_to_super.determinant();
  std::map<DoFKey, xtal::DoFSet> global_dof_info =
      clexulator::make_global_dof_info(*prim);
  std::map<DoFKey, std::vector<xtal::SiteDoFSet>> local_dof_info =
      clexulator::make_local_dof_info(*prim);
  clexulator::ConfigDoFValues dof_values =
      clexulator::make_default_config_dof_values(
          N_sublat, N_volume, global_dof_info, local_dof_info);
  EXPECT_EQ(dof_values.occupation.size(), 4);
  EXPECT_EQ(dof_values.local_dof_values.size(), 1);
  EXPECT_EQ(dof_values.global_dof_values.size(), 1);

  Eigen::VectorXd v;
  Eigen::VectorXd v_expected(12);
  Eigen::MatrixXd &disp_dof_values = dof_values.local_dof_values.at(dof_key);
  Eigen::MatrixXd disp_expected(3, 4);

  disp_expected.setZero();
  EXPECT_TRUE(CASM::almost_equal(disp_dof_values, disp_expected));

  disp_dof_values.col(0) << 1.0, 0.0, 0.0;
  v = clexulator::get_dof_vector_value(
      dof_values, transformation_matrix_to_super, dof_space);
  v_expected << 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0;
  EXPECT_EQ(v.size(), 12);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  v = clexulator::get_normal_coordinate(
      dof_values, transformation_matrix_to_super, dof_space);
  v_expected << 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0;
  EXPECT_EQ(v.size(), 12);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));
}

// Test get_mean_normal_coordinate_at and get_mean_normal_coordinate
TEST_F(FCCTernaryGLstrainDispDoFSpaceValuesTest, Test1d) {
  // Construct the occupation DoF space.
  DoFKey dof_key = "disp";
  Eigen::Matrix3l T_dof_space = Eigen::Matrix3l::Identity();
  clexulator::DoFSpace dof_space =
      clexulator::make_local_dof_space(dof_key, prim, T_dof_space);

  // Construct ConfigDoFValues
  Eigen::Matrix3l T_config = transformation_matrix_to_super;
  Index N_sublat = prim->basis().size();
  Index N_volume = T_config.determinant();
  std::map<DoFKey, xtal::DoFSet> global_dof_info =
      clexulator::make_global_dof_info(*prim);
  std::map<DoFKey, std::vector<xtal::SiteDoFSet>> local_dof_info =
      clexulator::make_local_dof_info(*prim);
  clexulator::ConfigDoFValues dof_values =
      clexulator::make_default_config_dof_values(
          N_sublat, N_volume, global_dof_info, local_dof_info);
  EXPECT_EQ(dof_values.occupation.size(), 4);
  EXPECT_EQ(dof_values.local_dof_values.size(), 1);
  EXPECT_EQ(dof_values.global_dof_values.size(), 1);

  xtal::UnitCellIndexConverter unitcell_index_converter(T_config);
  xtal::UnitCellCoordIndexConverter unitcellcoord_index_converter(T_config,
                                                                  N_sublat);
  clexulator::DoFSpaceIndexConverter dof_space_index_converter(
      unitcellcoord_index_converter, dof_space);

  Eigen::VectorXd v;
  Eigen::VectorXd v_expected(3);
  Eigen::MatrixXd &disp_dof_values = dof_values.local_dof_values.at(dof_key);
  Eigen::MatrixXd disp_expected(3, 4);

  disp_expected.setZero();
  EXPECT_TRUE(CASM::almost_equal(disp_dof_values, disp_expected));

  disp_dof_values.col(0) << 1.0, 0.0, 0.0;

  v = clexulator::get_normal_coordinate_at(dof_values, dof_space,
                                           dof_space_index_converter,
                                           unitcell_index_converter(0));
  v_expected << 1.0, 0.0, 0.0;
  EXPECT_EQ(v.size(), 3);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  v = clexulator::get_normal_coordinate_at(dof_values, dof_space,
                                           dof_space_index_converter,
                                           unitcell_index_converter(1));
  v_expected << 0.0, 0.0, 0.0;
  EXPECT_EQ(v.size(), 3);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  v = clexulator::get_normal_coordinate_at(dof_values, dof_space,
                                           dof_space_index_converter,
                                           unitcell_index_converter(2));
  v_expected << 0.0, 0.0, 0.0;
  EXPECT_EQ(v.size(), 3);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  v = clexulator::get_normal_coordinate_at(dof_values, dof_space,
                                           dof_space_index_converter,
                                           unitcell_index_converter(3));
  v_expected << 0.0, 0.0, 0.0;
  EXPECT_EQ(v.size(), 3);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  v = clexulator::get_mean_normal_coordinate(dof_values, T_config, dof_space);
  v_expected << 0.25, 0.0, 0.0;
  EXPECT_EQ(v.size(), 3);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  // compare to OrderParameter result
  clexulator::OrderParameter order_parameter(dof_space);
  v = order_parameter(T_config, unitcellcoord_index_converter, &dof_values);
  EXPECT_EQ(v.size(), 3);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));
}

TEST_F(FCCTernaryGLstrainDispDoFSpaceValuesTest, Test2a) {
  // Construct the GLstrain DoF space.
  DoFKey dof_key = "GLstrain";
  clexulator::DoFSpace dof_space =
      clexulator::make_global_dof_space(dof_key, prim);
  EXPECT_EQ(dof_space.axis_info.site_index.has_value(), false);
  EXPECT_EQ(dof_space.axis_info.dof_component.has_value(), false);
  EXPECT_EQ(dof_space.dim, 6);
  EXPECT_EQ(dof_space.dim, dof_space.basis.rows());
}

TEST_F(FCCTernaryGLstrainDispDoFSpaceValuesTest, Test2b) {
  // Construct the GLstrain DoF space.
  DoFKey dof_key = "GLstrain";
  clexulator::DoFSpace dof_space =
      clexulator::make_global_dof_space(dof_key, prim);

  // Construct ConfigDoFValues
  Index N_sublat = prim->basis().size();
  Index N_volume = transformation_matrix_to_super.determinant();
  std::map<DoFKey, xtal::DoFSet> global_dof_info =
      clexulator::make_global_dof_info(*prim);
  std::map<DoFKey, std::vector<xtal::SiteDoFSet>> local_dof_info =
      clexulator::make_local_dof_info(*prim);
  clexulator::ConfigDoFValues dof_values =
      clexulator::make_default_config_dof_values(
          N_sublat, N_volume, global_dof_info, local_dof_info);
  EXPECT_EQ(dof_values.occupation.size(), 4);
  EXPECT_EQ(dof_values.local_dof_values.size(), 1);
  EXPECT_EQ(dof_values.global_dof_values.size(), 1);

  Eigen::VectorXd v;
  Eigen::VectorXd v_expected(6);
  Eigen::VectorXd &GLstrain_dof_values =
      dof_values.global_dof_values.at(dof_key);
  Eigen::VectorXd GLstrain_expected(6);

  GLstrain_expected.setZero();
  EXPECT_TRUE(CASM::almost_equal(GLstrain_dof_values, GLstrain_expected));

  v = clexulator::get_dof_vector_value(
      dof_values, transformation_matrix_to_super, dof_space);
  v_expected << 0.0, 0.0, 0.0, 0.0, 0.0, 0.0;
  EXPECT_EQ(v.size(), 6);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  GLstrain_dof_values << 1.0, 0.0, 0.0, 0.0, 0.0, 0.0;
  v = clexulator::get_dof_vector_value(
      dof_values, transformation_matrix_to_super, dof_space);
  v_expected << 1.0, 0.0, 0.0, 0.0, 0.0, 0.0;
  EXPECT_EQ(v.size(), 6);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));

  GLstrain_dof_values << 0.0, 0.0, 1.0, 0.0, 0.0, 0.0;
  v = clexulator::get_dof_vector_value(
      dof_values, transformation_matrix_to_super, dof_space);
  v_expected << 0.0, 0.0, 1.0, 0.0, 0.0, 0.0;
  EXPECT_EQ(v.size(), 6);
  EXPECT_TRUE(CASM::almost_equal(v, v_expected));
}
