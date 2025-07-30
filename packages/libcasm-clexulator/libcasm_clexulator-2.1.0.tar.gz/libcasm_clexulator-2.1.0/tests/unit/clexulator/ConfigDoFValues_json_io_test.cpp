#include "casm/clexulator/io/json/ConfigDoFValues_json_io.hh"

#include <filesystem>

#include "autotools.hh"
#include "casm/casm_io/json/jsonParser.hh"
#include "casm/clexulator/ConfigDoFValuesTools_impl.hh"
#include "gtest/gtest.h"
#include "testfunctions.hh"
#include "teststructures.hh"

using namespace CASM;

TEST(ParseConfigDoFValues, Test1) {
  xtal::BasicStructure prim(test::FCC_ternary_prim());
  Index N_sublat = prim.basis().size();
  Index N_volume = 4;
  clexulator::ConfigDoFValues dof_values =
      test::make_dof_values(prim, N_volume);

  jsonParser json;
  to_json(dof_values, json);

  EXPECT_TRUE(json.is_obj());
  EXPECT_EQ(json.size(), 1);
  EXPECT_TRUE(json.contains("occ"));
  EXPECT_TRUE(json["occ"].is_array());
  EXPECT_EQ(json["occ"].size(), N_sublat * N_volume);

  EXPECT_TRUE(!json.contains("local_dofs"));
  EXPECT_TRUE(!json.contains("global_dofs"));
}

TEST(ParseConfigDoFValues, Test2) {
  xtal::BasicStructure prim(test::FCC_ternary_GLstrain_disp_prim());
  Index N_sublat = prim.basis().size();
  Index N_volume = 4;
  clexulator::ConfigDoFValues dof_values =
      test::make_dof_values(prim, N_volume);

  jsonParser json;
  to_json(dof_values, json);

  EXPECT_TRUE(json.is_obj());
  EXPECT_EQ(json.size(), 3);
  EXPECT_TRUE(json.contains("occ"));
  EXPECT_TRUE(json["occ"].is_array());
  EXPECT_EQ(json["occ"].size(), N_sublat * N_volume);

  EXPECT_TRUE(json.find_at(fs::path("local_dofs/disp/values")) != json.end());

  EXPECT_TRUE(json.find_at(fs::path("global_dofs/GLstrain/values")) !=
              json.end());
}
