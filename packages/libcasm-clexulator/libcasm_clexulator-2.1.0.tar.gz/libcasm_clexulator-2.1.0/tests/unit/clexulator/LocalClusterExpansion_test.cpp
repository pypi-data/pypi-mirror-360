// Note:
// - Requires environment variable CASM_PREFIX to specify `global` and
// `crystallography` CASM libraries install location
//   - CASM_PREFIX is recognized by
//   `RuntimeLibrary::default_casm_includedir()`
//     and `RuntimeLibrary::default_casm_libdir()`
// - To avoid re-compiling the Clexulator each time, tests are organized as
// member functions and then all called from a single TEST_F
//

#include "casm/clexulator/LocalClusterExpansion.hh"

#include "TestConfiguration.hh"
#include "TestLocalClexulatorBase.hh"
#include "casm/casm_io/json/InputParser_impl.hh"
#include "casm/clexulator/ConfigDoFValues.hh"
#include "casm/clexulator/ConfigDoFValuesTools_impl.hh"
#include "casm/clexulator/Correlations.hh"
#include "casm/clexulator/io/json/SparseCoefficients_json_io.hh"
#include "casm/misc/algorithm.hh"

using namespace CASM;

namespace test {

// Test using data/OccClexulatorZrOTest, which is currently
// generated as part of the OccClexulatorZrOTest in the main CASMcode repo
//
class OccZrOLocalClexTest : public test::TestLocalClexulatorBase {
 protected:
  OccZrOLocalClexTest()
      : TestLocalClexulatorBase("ZrO_Clexulator", {"hop0", "hop1"},
                                "LocalOccClexulatorZrOTest") {
    // can uncomment for debugging:
    tmpdir.do_not_remove_on_destruction();
  }

  clexulator::SparseCoefficients coefficients;
  std::unique_ptr<clexulator::LocalClusterExpansion> clex;

  std::vector<clexulator::SparseCoefficients> multicoeffs;
  std::unique_ptr<clexulator::MultiLocalClusterExpansion> multiclex;

  void ReadCoeffJson_tests() {
    fs::path eci_path = test::data_dir("clexulator") /
                        "LocalOccClexulatorZrOTest" / "basis_sets" /
                        "bset.hop0" / "coeff.json";
    jsonParser json(eci_path);
    InputParser<clexulator::SparseCoefficients> parser(json);
    EXPECT_TRUE(parser.valid());
    EXPECT_EQ(parser.value->index.size(), 1);
    EXPECT_EQ(parser.value->value.size(), 1);

    coefficients = *parser.value;
  }
  void ReadMultiCoeffJson_tests() {
    multicoeffs.clear();

    {
      fs::path eci_path = test::data_dir("clexulator") /
                          "LocalOccClexulatorZrOTest" / "basis_sets" /
                          "bset.hop0" / "coeff_0.json";
      jsonParser json(eci_path);
      InputParser<clexulator::SparseCoefficients> parser(json);
      EXPECT_TRUE(parser.valid());
      EXPECT_EQ(parser.value->index.size(), 1);
      EXPECT_EQ(parser.value->value.size(), 1);
      multicoeffs.push_back(*parser.value);
    }

    {
      fs::path eci_path = test::data_dir("clexulator") /
                          "LocalOccClexulatorZrOTest" / "basis_sets" /
                          "bset.hop0" / "coeff_1.json";
      jsonParser json(eci_path);
      InputParser<clexulator::SparseCoefficients> parser(json);
      EXPECT_TRUE(parser.valid());
      EXPECT_EQ(parser.value->index.size(), 2);
      EXPECT_EQ(parser.value->value.size(), 2);
      multicoeffs.push_back(*parser.value);
    }
  }

  void MakeClex_tests() {
    // Check correlations (checks running without errors, not values)
    Eigen::Matrix3l T = Eigen::Matrix3l::Identity() * 2;
    test::TestConfiguration config(prim, T, *prim_neighbor_list);

    clex = notstd::make_unique<clexulator::LocalClusterExpansion>(
        config.supercell_neighbor_list, clexulator.at("hop0"), coefficients);

    clex->set(&config.dof_values);
    // default config
    {
      double value;
      Index unitcell_index = 0;
      value = clex->value(0 /*equivalent_index*/, unitcell_index);
      EXPECT_TRUE(CASM::almost_equal(value, 1.0));
      value = clex->value(1 /*equivalent_index*/, unitcell_index);
      EXPECT_TRUE(CASM::almost_equal(value, 1.0));
    }

    // all Va-O sites filled with O
    for (Index l = 16; l < 32; ++l) {
      config.dof_values.occupation(l) = 1;
    }
    {
      double value;
      Index unitcell_index = 0;
      value = clex->value(0 /*equivalent_index*/, unitcell_index);
      EXPECT_TRUE(CASM::almost_equal(value, 1.0));
      value = clex->value(1 /*equivalent_index*/, unitcell_index);
      EXPECT_TRUE(CASM::almost_equal(value, 1.0));
    }
  }

  void MakeMultiClex_tests() {
    // Check correlations (checks running without errors, not values)
    Eigen::Matrix3l T = Eigen::Matrix3l::Identity() * 2;
    test::TestConfiguration config(prim, T, *prim_neighbor_list);

    multiclex = notstd::make_unique<clexulator::MultiLocalClusterExpansion>(
        config.supercell_neighbor_list, clexulator.at("hop0"), multicoeffs);
    EXPECT_EQ(multiclex->coefficients().size(), 2);

    multiclex->set(&config.dof_values);
    // default config
    {
      Eigen::VectorXd values;
      Index unitcell_index = 0;
      values = multiclex->values(0 /*equivalent_index*/, unitcell_index);
      EXPECT_TRUE(CASM::almost_equal(values(0), 1.0));
      EXPECT_TRUE(CASM::almost_equal(values(1), 1.0));
      values = multiclex->values(1 /*equivalent_index*/, unitcell_index);
      EXPECT_TRUE(CASM::almost_equal(values(0), 1.0));
      EXPECT_TRUE(CASM::almost_equal(values(1), 1.0));
    }

    // all Va-O sites filled with O
    for (Index l = 16; l < 32; ++l) {
      config.dof_values.occupation(l) = 1;
    }
    {
      Eigen::VectorXd values;
      Index unitcell_index = 0;
      values = multiclex->values(0 /*equivalent_index*/, unitcell_index);
      EXPECT_TRUE(CASM::almost_equal(values(0), 1.0));
      EXPECT_TRUE(CASM::almost_equal(values(1), 2.0));
      values = multiclex->values(1 /*equivalent_index*/, unitcell_index);
      EXPECT_TRUE(CASM::almost_equal(values(0), 1.0));
      EXPECT_TRUE(CASM::almost_equal(values(1), 2.0));
    }
  }
};

TEST_F(OccZrOLocalClexTest, Tests) {
  // only compile once...
  // MakeClexulator_tests();

  {
    ReadCoeffJson_tests();
    MakeClex_tests();
  }

  {
    ReadMultiCoeffJson_tests();
    MakeMultiClex_tests();
  }
}

}  // namespace test
