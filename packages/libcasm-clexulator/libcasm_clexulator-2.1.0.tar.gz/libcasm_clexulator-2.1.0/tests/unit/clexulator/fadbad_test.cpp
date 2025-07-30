#include "casm/clexulator/external/fadbad/badiff.h"
#include "casm/clexulator/external/fadbad/fadiff.h"
#include "casm/misc/CASM_math.hh"
#include "gtest/gtest.h"

using namespace CASM;

namespace test {
template <typename T>
T func(T const &x, T const &y) {
  // f(x,y) = 3.0*x^2 + 4.0*y^3 + 5.0*x*y
  // df_dx = 6*x + 5*y
  // df_dy = 12*y^2 + 5*x
  // df_dxdx = 6
  // df_dxdy = 5
  // df_dydx = 5
  // df_dydy = 24*y
  //
  // x=5, y=2
  // value = 3.0*5.*5. + 4*2*2*2 + 5*5*2= 157.0
  // df_dx_value = 6.0*5 + 5.0*2 = 40.0
  // df_dy_value = 12.0*2^2 + 5*5 = 73.0
  // df_dxdx_value = 6.0
  // df_dxdy_value = 5.0
  // df_dydx_value = 5.0
  // df_dydy_value = 24.0*y = 48.0

  return 3.0 * x * x + 4.0 * y * y * y + 5.0 * x * y;
}
}  // namespace test

TEST(FadbadTest, TestForward) {
  // Declare variables
  fadbad::F<double> x, y;
  fadbad::F<double> f;

  x = 5;
  x.diff(0, 2);  // 0=indep_var_index for x, 2=N_indep_var
  y = 2;
  y.diff(1, 2);  // 1=indep_var_index for y, 2=N_indep_var

  // first evaluate the function:
  f = test::func(x, y);
  double f_value = f.x();  // value of function

  // getting derivatives:
  // (dependent_var).d(indep_var_index)
  double df_dx_value = f.d(0);  // 0=indep_var_index for x
  double df_dy_value = f.d(1);  // 1=indep_var_index for y

  double tol = 1e-10;
  EXPECT_TRUE(almost_equal(f_value, 157.0, tol));
  EXPECT_TRUE(almost_equal(df_dx_value, 40.0, tol));
  EXPECT_TRUE(almost_equal(df_dy_value, 73.0, tol));
}

TEST(FadbadTest, TestBackward) {
  // Declare variables
  fadbad::B<double> x, y;
  fadbad::B<double> f;

  x = 5;
  y = 2;

  // first evaluate the function:
  f = test::func(x, y);
  f.diff(0, 1);            // 0=dep_var_index for f, 1=N_dep_var
  double f_value = f.x();  // value of function

  // getting derivatives:
  // (independent_var).d(dep_var_index)
  double df_dx_value = x.d(0);  // 0=dep_var_index for f
  double df_dy_value = y.d(0);  // 1=dep_var_index for f

  // f(x,y) = 3.0*x^2 + 4.0*y^3
  // x=5, y=2
  // value = 3.0*5.*5. + 4*2*2*2 = 107.0
  // df_dx_value = 6.0*5
  // df_dy_value = 12.0*2^2

  double tol = 1e-10;
  EXPECT_TRUE(almost_equal(f_value, 157.0, tol));
  EXPECT_TRUE(almost_equal(df_dx_value, 40.0, tol));
  EXPECT_TRUE(almost_equal(df_dy_value, 73.0, tol));
}

TEST(FadbadTest, TestHess) {
  // Declare variables
  fadbad::B<fadbad::F<double>> x, y;
  fadbad::B<fadbad::F<double>> f;

  // first evaluate the function:
  x = 5;
  y = 2;

  // pre-eval
  // call on each independent parameter before function evaluation
  x.val().diff(0, 2);  // 0=indep_var_index for x, 2=N_indep_var
  y.val().diff(1, 2);  // 1=indep_var_index for y, 2=N_indep_var

  f = test::func(x, y);

  // post-eval
  // call on each dependent parameter (B<double>) after function evaluation
  f.diff(0, 1);  // 0=dep_var_index for f, 1=N_dep_var

  double f_value = f.x().x();  // value of function

  // f(x,y) = 3.0*x^2 + 4.0*y^3
  // x=5, y=2
  // value = 3.0*5.*5. + 4*2*2*2 = 107.0
  // df_dx_value = 6.0*5
  // df_dy_value = 12.0*2^2

  // df_dxdx_value = 6.0
  // df_dxdy_value = 0.0
  // df_dydx_value = 0.0
  // df_dydy_value = 48.0

  double tol = 1e-10;
  EXPECT_TRUE(almost_equal(f_value, 157.0, tol));

  {
    // getting second derivatives only:
    // (independent_var).d(dependent_index).d(independent_var)
    double df_dxdx_value =
        x.d(0).d(0);  // 0=dep_var_index for f, 0=indep_var_index for x
    double df_dxdy_value =
        x.d(0).d(1);  // 0=dep_var_index for f, 1=indep_var_index for y
    double df_dydx_value =
        y.d(0).d(0);  // 0=dep_var_index for f, 0=indep_var_index for x
    double df_dydy_value =
        y.d(0).d(1);  // 0=dep_var_index for f, 1=indep_var_index for y

    EXPECT_TRUE(almost_equal(df_dxdx_value, 6.0, tol));
    EXPECT_TRUE(almost_equal(df_dxdy_value, 5.0, tol));
    EXPECT_TRUE(almost_equal(df_dydx_value, 5.0, tol));
    EXPECT_TRUE(almost_equal(df_dydy_value, 48.0, tol));
  }

  {
    // getting first & second derivatives:
    fadbad::F<double> df_dx, df_dy;

    df_dx = x.d(0);                  // 0=dep_var_index for f
    df_dy = y.d(0);                  // 1=dep_var_index for f
    double df_dx_value = df_dx.x();  // is this right?
    double df_dy_value = df_dy.x();  // is this right?

    EXPECT_TRUE(almost_equal(df_dx_value, 40.0, tol));
    EXPECT_TRUE(almost_equal(df_dy_value, 73.0, tol));

    double df_dxdx_value = df_dx.d(0);  // 0=indep_var_index for x
    double df_dxdy_value = df_dx.d(1);  // 1=indep_var_index for y
    double df_dydx_value = df_dy.d(0);  // 0=indep_var_index for x
    double df_dydy_value = df_dy.d(1);  // 1=indep_var_index for y

    EXPECT_TRUE(almost_equal(df_dxdx_value, 6.0, tol));
    EXPECT_TRUE(almost_equal(df_dxdy_value, 5.0, tol));
    EXPECT_TRUE(almost_equal(df_dydx_value, 5.0, tol));
    EXPECT_TRUE(almost_equal(df_dydy_value, 48.0, tol));
  }
}
