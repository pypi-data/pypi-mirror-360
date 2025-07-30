#include "autotools.hh"
#include "casm/clexulator/ConfigDoFValuesTools_impl.hh"
#include "casm/system/RuntimeLibrary.hh"
#include "gtest/gtest.h"
#include "testdir.hh"
#include "teststructures.hh"

using namespace CASM;

TEST(ConfigDoFValuesToolsTest, MakeDefaultStandardConfigDoFValuesTest1) {
  xtal::BasicStructure prim(test::FCC_ternary_prim());

  Index N_sublat = prim.basis().size();
  Index N_volume = 4;
  std::map<DoFKey, xtal::DoFSet> global_dof_info =
      clexulator::make_global_dof_info(prim);
  std::map<DoFKey, std::vector<xtal::SiteDoFSet>> local_dof_info =
      clexulator::make_local_dof_info(prim);

  clexulator::ConfigDoFValues dof_values =
      clexulator::make_default_standard_config_dof_values(
          N_sublat, N_volume, global_dof_info, local_dof_info);

  EXPECT_EQ(dof_values.occupation.size(), N_sublat * N_volume);
  EXPECT_EQ(dof_values.local_dof_values.size(), 0);
  EXPECT_EQ(dof_values.global_dof_values.size(), 0);
}
