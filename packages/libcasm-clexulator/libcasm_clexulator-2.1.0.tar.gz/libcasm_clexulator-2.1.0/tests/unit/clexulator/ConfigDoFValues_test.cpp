#include "casm/clexulator/ConfigDoFValues.hh"

#include "autotools.hh"
#include "casm/system/RuntimeLibrary.hh"
#include "gtest/gtest.h"
#include "testdir.hh"
#include "testfunctions.hh"
#include "teststructures.hh"

using namespace CASM;

TEST(MakeConfigDoFValues, Test1) {
  clexulator::ConfigDoFValues dof_values;
  EXPECT_EQ(dof_values.occupation.size(), 0);
  EXPECT_EQ(dof_values.local_dof_values.size(), 0);
  EXPECT_EQ(dof_values.global_dof_values.size(), 0);
}

TEST(MakeConfigDoFValues, Test2) {
  xtal::BasicStructure prim(test::FCC_ternary_GLstrain_disp_prim());
  Index N_sublat = prim.basis().size();
  Index N_volume = 4;
  clexulator::ConfigDoFValues dof_values =
      test::make_dof_values(prim, N_volume);

  EXPECT_EQ(dof_values.occupation.size(), N_sublat * N_volume);

  EXPECT_EQ(dof_values.local_dof_values.size(), 1);
  EXPECT_EQ(dof_values.local_dof_values.count("disp"), 1);
  EXPECT_EQ(dof_values.local_dof_values.at("disp").cols(), 4);
  EXPECT_EQ(dof_values.local_dof_values.at("disp").rows(), 3);

  EXPECT_EQ(dof_values.global_dof_values.size(), 1);
  EXPECT_EQ(dof_values.global_dof_values.count("GLstrain"), 1);
  EXPECT_EQ(dof_values.global_dof_values.at("GLstrain").cols(), 1);
  EXPECT_EQ(dof_values.global_dof_values.at("GLstrain").rows(), 6);
}
