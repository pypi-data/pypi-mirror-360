#include "casm/clexulator/OrderParameter.hh"

#include "casm/clexulator/ConfigDoFValues.hh"
#include "casm/clexulator/ConfigDoFValuesTools_impl.hh"
#include "casm/clexulator/DoFSpace.hh"
#include "casm/crystallography/BasicStructure.hh"
#include "casm/crystallography/SuperlatticeEnumerator.hh"
#include "gtest/gtest.h"
#include "teststructures.hh"

// // Uncommment what generating a symmetry adapated subspace:
// #include "casm/symmetry/IrrepDecomposition.hh"
// #include "casm/symmetry/IrrepDecompositionImpl.hh"

using namespace CASM;
using namespace test;

namespace {

Eigen::Matrix3l _fcc_conventional_transf_mat() {
  Eigen::Matrix3l transf_mat;
  transf_mat << -1, 1, 1, 1, -1, 1, 1, 1, -1;
  return transf_mat;
}

/// \brief Round entries that are within tol of being integer to that integer
/// value
void print_pretty(const Eigen::MatrixXd &M) {
  double tol = 1e-10;
  Eigen::MatrixXd Mp(M);
  std::cout << "Eigen::MatrixXd basis;\n";
  std::cout << "basis.resize(" << M.rows() << "," << M.cols() << ");\n";
  for (int j = 0; j < M.cols(); j++) {
    std::cout << "basis.col(" << j << ") << ";
    for (int i = 0; i < M.rows(); i++) {
      if (std::abs(std::round(M(i, j)) - M(i, j)) < tol) {
        Mp(i, j) = std::round(M(i, j));
      }
      std::cout << Mp(i, j);
      if (i != M.rows() - 1)
        std::cout << ",";
      else
        std::cout << ";\n";
    }
  }
}

}  // namespace

// reminder: prim_dof_values = dof_space.basis * normal_coordinate

class OrderParameterTest : public testing::Test {
 protected:
  std::shared_ptr<xtal::BasicStructure const> prim;
  std::map<DoFKey, xtal::DoFSet> global_dof_info;
  std::map<DoFKey, std::vector<xtal::SiteDoFSet>> local_dof_info;
  Eigen::Matrix3l transformation_matrix_to_super;
  xtal::UnitCellCoordIndexConverter index_converter;
  clexulator::ConfigDoFValues dof_values;

  OrderParameterTest()
      : prim(std::make_shared<xtal::BasicStructure const>(
            test::FCC_ternary_GLstrain_disp_prim())),
        global_dof_info(clexulator::make_global_dof_info(*prim)),
        local_dof_info(clexulator::make_local_dof_info(*prim)),
        transformation_matrix_to_super(_fcc_conventional_transf_mat()),
        index_converter(transformation_matrix_to_super, prim->basis().size()),
        dof_values(clexulator::make_default_config_dof_values(
            prim->basis().size(), transformation_matrix_to_super.determinant(),
            global_dof_info, local_dof_info)) {}
};

TEST_F(OrderParameterTest, Test1_GLstrain) {
  // Construct the GLstrain DoF space.
  DoFKey dof_key = "GLstrain";
  clexulator::DoFSpace dof_space =
      clexulator::make_global_dof_space(dof_key, prim);
  EXPECT_EQ(dof_space.basis.rows(), 6);

  clexulator::OrderParameter order_f(dof_space);
  order_f.update(transformation_matrix_to_super, index_converter, &dof_values);

  // test 1: initial value
  {
    Eigen::VectorXd y, expected;
    y = order_f.value();
    expected = Eigen::VectorXd::Zero(6);
    EXPECT_TRUE(almost_equal(y, expected))
        << "\ny: " << y.transpose() << "\nexpected: " << expected.transpose()
        << std::endl;
  }

  // test 2: value after modification
  {
    Eigen::VectorXd y, expected;
    expected = Eigen::VectorXd::Zero(6);
    expected(1) = 0.1;
    dof_values.global_dof_values.at("GLstrain") = expected;
    y = order_f.value();
    EXPECT_TRUE(almost_equal(y, expected))
        << "\ny: " << y.transpose() << "\nexpected: " << expected.transpose()
        << std::endl;
  }

  // test 3: global delta
  {
    Eigen::VectorXd old_x, new_x, dy, expected;
    old_x = dof_values.global_dof_values.at("GLstrain");
    new_x.resize(6);
    new_x << 0.1, 0.0, 0.0, 0.0, 0.0, 0.0;
    expected = new_x - old_x;
    dy = order_f.global_delta_value(new_x);
    EXPECT_TRUE(almost_equal(dy, expected))
        << "\nold_x: " << old_x.transpose() << "\nnew_x: " << new_x.transpose()
        << "\ndy: " << dy.transpose() << "\nexpected: " << expected.transpose()
        << std::endl;
  }

  // test 4: global delta (single component)
  {
    Eigen::VectorXd old_x, dy, expected;
    old_x = dof_values.global_dof_values.at("GLstrain");
    int dof_component = 0;
    double new_xi = 0.1;
    expected = Eigen::VectorXd::Zero(6);
    expected(dof_component) = new_xi - old_x(dof_component);
    dy = order_f.global_delta_value(dof_component, new_xi);
    EXPECT_TRUE(almost_equal(dy, expected))
        << "\nold_x: " << old_x.transpose()
        << "\ndof_component: " << dof_component << "\nnew_xi: " << new_xi
        << "\ndy: " << dy.transpose() << "\nexpected: " << expected.transpose()
        << std::endl;
  }
}

TEST_F(OrderParameterTest, Test1_GLstrain_SymAdapted) {
  // Construct the GLstrain DoF space.
  DoFKey dof_key = "GLstrain";
  Eigen::MatrixXd basis;
  basis.resize(6, 6);
  basis.col(0) << 0.57735, 0.57735, 0.57735, 0.0, 0.0, 0.0;
  basis.col(1) << -0.408248, -0.408248, 0.816497, 0.0, 0.0, 0.0;
  basis.col(2) << 0.707107, -0.707107, 0.0, 0.0, 0.0, 0.0;
  basis.col(3) << 0.0, 0.0, 0.0, 1.0, 0.0, 0.0;
  basis.col(4) << 0.0, 0.0, 0.0, 0.0, 1.0, 0.0;
  basis.col(5) << 0.0, 0.0, 0.0, 0.0, 0.0, 1.0;
  clexulator::DoFSpace dof_space =
      clexulator::make_global_dof_space(dof_key, prim, basis);
  EXPECT_EQ(dof_space.basis.rows(), 6);

  clexulator::OrderParameter order_f(dof_space);
  order_f.update(transformation_matrix_to_super, index_converter, &dof_values);

  // test 1: initial value
  {
    Eigen::VectorXd y, expected;
    y = order_f.value();
    expected = Eigen::VectorXd::Zero(6);
    EXPECT_TRUE(almost_equal(y, expected))
        << "\ny: " << y.transpose() << "\nexpected: " << expected.transpose()
        << std::endl;
  }

  // test 2: value after modification
  {
    // x = basis * y
    Eigen::VectorXd x, y;
    x = Eigen::VectorXd::Zero(6);
    x(0) = 0.1;
    dof_values.global_dof_values.at("GLstrain") = x;
    y = order_f.value();
    EXPECT_TRUE(almost_equal(x, basis * y))
        << "\nx: " << x.transpose() << "\ny: " << y.transpose()
        << "\nbasis * y: " << (basis * y).transpose() << std::endl;
  }

  // test 3: global delta
  {
    // x = basis * y
    Eigen::VectorXd old_x, new_x, dy, expected;
    old_x = dof_values.global_dof_values.at("GLstrain");
    new_x.resize(6);
    new_x << 0.1, 0.0, 0.0, 0.0, 0.0, 0.0;
    dy = order_f.global_delta_value(new_x);
    EXPECT_TRUE(almost_equal(new_x - old_x, basis * dy))
        << "\nold_x: " << old_x.transpose() << "\nnew_x: " << new_x.transpose()
        << "\ndx: " << (new_x - old_x).transpose() << "\ndy: " << dy.transpose()
        << "\nbasis * dy: " << (basis * dy).transpose() << std::endl;
  }

  // test 4: global delta (single component)
  {
    Eigen::VectorXd old_x, new_x, dy;
    old_x = dof_values.global_dof_values.at("GLstrain");
    int dof_component = 0;
    double new_xi = 0.1;
    new_x = old_x;
    new_x(dof_component) = new_xi;
    dy = order_f.global_delta_value(dof_component, new_xi);
    EXPECT_TRUE(almost_equal(dy, basis * dy))
        << "\nold_x: " << old_x.transpose() << "\nnew_x: " << new_x.transpose()
        << "\ndx: " << (new_x - old_x).transpose() << "\ndy: " << dy.transpose()
        << "\nbasis * dy: " << (basis * dy).transpose() << std::endl;
  }
}

TEST_F(OrderParameterTest, Test2_disp) {
  // Construct the disp DoF space.
  DoFKey dof_key = "disp";
  clexulator::DoFSpace dof_space = clexulator::make_local_dof_space(
      dof_key, prim, transformation_matrix_to_super);
  EXPECT_EQ(dof_space.basis.rows(), 4 * 3);

  clexulator::OrderParameter order_f(dof_space);
  order_f.update(transformation_matrix_to_super, index_converter, &dof_values);

  // test 1: initial value
  {
    Eigen::VectorXd y, expected;
    y = order_f.value();
    expected = Eigen::VectorXd::Zero(12);
    EXPECT_TRUE(almost_equal(y, expected))
        << "\ny: " << y.transpose() << "\nexpected: " << expected.transpose()
        << std::endl;
  }

  // test 2a: value after modification
  {
    Eigen::MatrixXd x;
    Eigen::VectorXd y, expected;
    x = Eigen::MatrixXd::Zero(3, 4);
    x(0, 0) = 0.1;
    dof_values.local_dof_values.at("disp") = x;
    expected = Eigen::VectorXd::Zero(12);
    expected(0) = 0.1;
    y = order_f.value();
    EXPECT_TRUE(almost_equal(y, expected))
        << "\nx: " << x.transpose() << "\ny: " << y.transpose()
        << "\nexpected: " << expected.transpose() << std::endl;
  }

  // test 2b: value after modification
  {
    Eigen::MatrixXd x;
    Eigen::VectorXd y, expected;
    x = Eigen::MatrixXd::Zero(3, 4);
    x(0, 1) = 0.1;
    dof_values.local_dof_values.at("disp") = x;
    expected = Eigen::VectorXd::Zero(12);
    expected(3) = 0.1;
    y = order_f.value();
    EXPECT_TRUE(almost_equal(y, expected))
        << "\nx: " << x.transpose() << "\ny: " << y.transpose()
        << "\nexpected: " << expected.transpose() << std::endl;
  }

  // test 3: local delta
  {
    // x = basis * y
    Eigen::VectorXd old_xi, new_xi, dy, expected;
    Index site_index = 1;
    Index dof_component = 1;
    double new_value = 0.1;
    dof_values.local_dof_values.at("disp") = Eigen::MatrixXd::Zero(3, 4);
    old_xi = dof_values.local_dof_values.at("disp").col(site_index);
    new_xi = old_xi;
    new_xi(dof_component) = new_value;
    dy = order_f.local_delta_value(site_index, new_xi);
    expected = Eigen::VectorXd::Zero(12);
    expected(dof_space.axis_info.basis_row_index
                 .value()[site_index][dof_component]) = new_value;
    EXPECT_TRUE(almost_equal(dy, expected))
        << "\nsite_index: " << site_index
        << "\ndof_component: " << dof_component << "\nnew_value: " << new_value
        << "\nold_xi: " << old_xi.transpose()
        << "\nnew_xi: " << new_xi.transpose() << "\ndy: " << dy.transpose()
        << "\nexpected: " << expected.transpose() << std::endl;
  }

  // test 4: local delta (single component)
  {
    // x = basis * y
    Eigen::VectorXd old_xi, new_xi, dy, expected;
    Index site_index = 1;
    Index dof_component = 1;
    double new_value = 0.1;
    dof_values.local_dof_values.at("disp") = Eigen::MatrixXd::Zero(3, 4);
    old_xi = dof_values.local_dof_values.at("disp").col(site_index);
    dy = order_f.local_delta_value(site_index, dof_component, new_value);
    expected = Eigen::VectorXd::Zero(12);
    expected(dof_space.axis_info.basis_row_index
                 .value()[site_index][dof_component]) = new_value;
    EXPECT_TRUE(almost_equal(dy, expected))
        << "\nsite_index: " << site_index
        << "\ndof_component: " << dof_component << "\nnew_value: " << new_value
        << "\nold_xi: " << old_xi.transpose() << "\ndy: " << dy.transpose()
        << "\nexpected: " << expected.transpose() << std::endl;
  }
}

TEST_F(OrderParameterTest, Test2_disp_SymAdapted) {
  // Construct the disp DoF space.
  DoFKey dof_key = "disp";
  Eigen::MatrixXd basis;
  basis.resize(12, 12);
  basis.col(0) << 0.5, 0, -0, 0.5, 0, -0, 0.5, 0, -0, 0.5, 0, 0;
  basis.col(1) << 0, 0.5, -0, 0, 0.5, -0, 0, 0.5, 0, 0, 0.5, -0;
  basis.col(2) << 0, 0, 0.5, -0, 0, 0.5, 0, 0, 0.5, 0, 0, 0.5;
  basis.col(3) << 0.5, 0, -0, -0.5, -0, -0, 0.5, 0, -0, -0.5, -0, -0;
  basis.col(4) << 0, 0.5, -0, 0, 0.5, 0, -0, -0.5, 0, -0, -0.5, 0;
  basis.col(5) << 0, 0, 0.5, -0, 0, -0.5, -0, -0, -0.5, 0, 0, 0.5;
  basis.col(6) << 0.707107, 0, -0, 0, -0, 0, -0.707107, 0, 0, 0, 0, 0;
  basis.col(7) << 0, 0.707107, -0, -0, -0.707107, 0, -0, -0, -0, 0, -0, 0;
  basis.col(8) << -0, 0, 0.707107, 0, 0, -0, -0, -0, -0, -0, 0, -0.707107;
  basis.col(9) << 0, -0, 0, 0.707107, 0, -0, 0, 0, 0, -0.707107, -0, 0;
  basis.col(10) << 0, 0, -0, 0, 0, 0.707107, -0, -0, -0.707107, 0, -0, -0;
  basis.col(11) << -0, 0, 0, 0, 0, -0, 0, 0.707107, -0, 0, -0.707107, 0;
  clexulator::DoFSpace dof_space = clexulator::make_local_dof_space(
      dof_key, prim, transformation_matrix_to_super, std::nullopt, basis);
  EXPECT_EQ(dof_space.basis.rows(), 4 * 3);

  clexulator::OrderParameter order_f(dof_space);
  order_f.update(transformation_matrix_to_super, index_converter, &dof_values);

  // test 1: initial value
  {
    Eigen::VectorXd y, expected;
    y = order_f.value();
    expected = Eigen::VectorXd::Zero(12);
    EXPECT_TRUE(almost_equal(y, expected))
        << "\ny: " << y.transpose() << "\nexpected: " << expected.transpose()
        << std::endl;
  }

  // test 2a: value after modification
  {
    // x = basis * y
    Eigen::MatrixXd x;
    Eigen::VectorXd y, expected;
    x = Eigen::MatrixXd::Zero(3, 4);
    x(0, 0) = 0.1;
    dof_values.local_dof_values.at("disp") = x;
    expected = Eigen::VectorXd::Zero(12);
    expected(0) = 0.1;
    y = order_f.value();
    EXPECT_TRUE(almost_equal(expected, basis * y))
        << "\nx: " << x.transpose() << "\ny: " << y.transpose()
        << "\nexpected: " << expected.transpose() << std::endl;
  }

  // test 2b: value after modification
  {
    Eigen::MatrixXd x;
    Eigen::VectorXd y, expected;
    x = Eigen::MatrixXd::Zero(3, 4);
    x(0, 1) = 0.1;
    dof_values.local_dof_values.at("disp") = x;
    expected = Eigen::VectorXd::Zero(12);
    expected(3) = 0.1;
    y = order_f.value();
    EXPECT_TRUE(almost_equal(expected, basis * y))
        << "\nx: " << x.transpose() << "\ny: " << y.transpose()
        << "\nexpected: " << expected.transpose() << std::endl;
  }

  // test 3: local delta
  {
    // x = basis * y
    Eigen::VectorXd old_xi, new_xi, dy, expected;
    Index site_index = 1;
    Index dof_component = 1;
    double new_value = 0.1;
    dof_values.local_dof_values.at("disp") = Eigen::MatrixXd::Zero(3, 4);
    old_xi = dof_values.local_dof_values.at("disp").col(site_index);
    new_xi = old_xi;
    new_xi(dof_component) = new_value;
    dy = order_f.local_delta_value(site_index, new_xi);
    expected = Eigen::VectorXd::Zero(12);
    expected(dof_space.axis_info.basis_row_index
                 .value()[site_index][dof_component]) = new_value;
    EXPECT_TRUE(almost_equal(expected, basis * dy))
        << "\nsite_index: " << site_index
        << "\ndof_component: " << dof_component << "\nnew_value: " << new_value
        << "\nold_xi: " << old_xi.transpose()
        << "\nnew_xi: " << new_xi.transpose() << "\ndy: " << dy.transpose()
        << "\nexpected: " << expected.transpose() << std::endl;
  }

  // test 4: global delta (single component)
  {
    // x = basis * y
    Eigen::VectorXd old_xi, new_xi, dy, expected;
    Index site_index = 1;
    Index dof_component = 1;
    double new_value = 0.1;
    dof_values.local_dof_values.at("disp") = Eigen::MatrixXd::Zero(3, 4);
    old_xi = dof_values.local_dof_values.at("disp").col(site_index);
    dy = order_f.local_delta_value(site_index, dof_component, new_value);
    expected = Eigen::VectorXd::Zero(12);
    expected(dof_space.axis_info.basis_row_index
                 .value()[site_index][dof_component]) = new_value;
    EXPECT_TRUE(almost_equal(expected, basis * dy))
        << "\nsite_index: " << site_index
        << "\ndof_component: " << dof_component << "\nnew_value: " << new_value
        << "\nold_xi: " << old_xi.transpose() << "\ndy: " << dy.transpose()
        << "\nexpected: " << expected.transpose() << std::endl;
  }
}

TEST_F(OrderParameterTest, Test3_occ) {
  // Construct the occ DoF space.
  DoFKey dof_key = "occ";
  clexulator::DoFSpace dof_space = clexulator::make_local_dof_space(
      dof_key, prim, transformation_matrix_to_super);
  EXPECT_EQ(dof_space.basis.rows(), 4 * 3);

  clexulator::OrderParameter order_f(dof_space);
  order_f.update(transformation_matrix_to_super, index_converter, &dof_values);

  // test 1: initial value
  {
    Eigen::VectorXd y, expected;
    y = order_f.value();
    expected.resize(12);
    expected << 1., 0., 0., 1., 0., 0., 1., 0., 0., 1., 0., 0.;
    EXPECT_TRUE(almost_equal(y, expected))
        << "\ny: " << y.transpose() << "\nexpected: " << expected.transpose()
        << std::endl;
  }

  // test 2a: value after modification
  {
    Eigen::VectorXd y, expected;
    dof_values.occupation(0) = 1;
    expected.resize(12);
    expected << 0., 1., 0., 1., 0., 0., 1., 0., 0., 1., 0., 0.;
    y = order_f.value();
    EXPECT_TRUE(almost_equal(y, expected))
        << "\ny: " << y.transpose() << "\nexpected: " << expected.transpose()
        << std::endl;
  }

  // test 2b: value after modification
  {
    Eigen::VectorXd y, expected;
    dof_values.occupation(0) = 2;
    expected.resize(12);
    expected << 0., 0., 1., 1., 0., 0., 1., 0., 0., 1., 0., 0.;
    y = order_f.value();
    EXPECT_TRUE(almost_equal(y, expected))
        << "\ny: " << y.transpose() << "\nexpected: " << expected.transpose()
        << std::endl;
  }

  // test 3: occ delta
  {
    // x = basis * y
    Eigen::VectorXd dy, expected;
    Index site_index = 1;
    int new_occ = 1;
    dof_values.occupation = Eigen::VectorXi::Zero(4);
    dy = order_f.occ_delta_value(site_index, new_occ);
    expected = Eigen::VectorXd::Zero(12);
    expected << 0., 0., 0., -1., 1., 0., 0., 0., 0., 0., 0., 0.;
    EXPECT_TRUE(almost_equal(dy, expected))
        << "\nsite_index: " << site_index << "\nnew_occ: " << new_occ
        << "\ndy: " << dy.transpose() << "\nexpected: " << expected.transpose()
        << std::endl;
  }
}
