#include "casm/clexulator/io/json/DoFSpace_json_io.hh"

#include <optional>

#include "casm/casm_io/json/InputParser_impl.hh"
#include "casm/casm_io/json/jsonParser.hh"
#include "casm/casm_io/json/optional.hh"
#include "casm/clexulator/DoFSpace.hh"
#include "casm/crystallography/BasicStructureTools.hh"
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

class DoFSpaceJsonIOTest : public testing::Test {
 protected:
  std::shared_ptr<xtal::BasicStructure const> prim;
  Eigen::Matrix3l transformation_matrix_to_super;

  DoFSpaceJsonIOTest()
      : prim(make_shared_prim(test::FCC_ternary_GLstrain_disp_prim())),
        transformation_matrix_to_super(_fcc_conventional_transf_mat()) {}
};

TEST_F(DoFSpaceJsonIOTest, Test1_GLstrain) {
  // Construct the GLstrain DoF space.
  DoFKey dof_key = "GLstrain";
  clexulator::DoFSpace dof_space =
      clexulator::make_global_dof_space(dof_key, prim);

  jsonParser json;
  to_json(dof_space, json);
  std::cout << json << std::endl;
}

TEST_F(DoFSpaceJsonIOTest, Test2_occ) {
  // Construct the occ DoF space.
  DoFKey dof_key = "occ";
  clexulator::DoFSpace dof_space = clexulator::make_local_dof_space(
      dof_key, prim, transformation_matrix_to_super);

  jsonParser json;
  to_json(dof_space, json);
  std::cout << json << std::endl;
}

TEST_F(DoFSpaceJsonIOTest, Test3_disp) {
  // Construct the disp DoF space.
  DoFKey dof_key = "disp";
  clexulator::DoFSpace dof_space = clexulator::make_local_dof_space(
      dof_key, prim, transformation_matrix_to_super);

  jsonParser json;
  to_json(dof_space, json);
  std::cout << json << std::endl;
}

TEST_F(DoFSpaceJsonIOTest, Test3_disp_ExcludeHomogeneousModeSpace) {
  // Construct the disp DoF space.
  DoFKey dof_key = "disp";
  clexulator::DoFSpace dof_space_0 = clexulator::make_local_dof_space(
      dof_key, prim, transformation_matrix_to_super);

  Eigen::MatrixXd homogeneous_mode_space =
      clexulator::make_homogeneous_mode_space(dof_space_0);
  EXPECT_EQ(homogeneous_mode_space.rows(), dof_space_0.dim);
  EXPECT_EQ(homogeneous_mode_space.cols(), 3);

  clexulator::DoFSpace dof_space_1 =
      clexulator::exclude_homogeneous_mode_space(dof_space_0);
  EXPECT_EQ(dof_space_1.dim, dof_space_0.dim);
  EXPECT_EQ(dof_space_1.subspace_dim, dof_space_0.subspace_dim - 3);

  jsonParser json;
  to_json(dof_space_1, json);
  std::cout << json << std::endl;
}
