// Note:
// - Requires environment variable CASM_PREFIX to specify `global` and
// `crystallography` CASM libraries install location
//   - CASM_PREFIX is recognized by
//   `RuntimeLibrary::default_casm_includedir()`
//     and `RuntimeLibrary::default_casm_libdir()`
// - To avoid re-compiling the Clexulator each time, tests are organized as
// member functions and then all called from a single TEST_F
//

#include "casm/clexulator/ClusterExpansion.hh"

#include "TestClexulatorBase.hh"
#include "TestConfiguration.hh"
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
class OccZrOClexTest : public test::TestClexulatorBase {
 protected:
  OccZrOClexTest()
      : TestClexulatorBase("ZrO_Clexulator", "default",
                           "OccClexulatorZrOTest_2") {
    // can uncomment for debugging:
    tmpdir.do_not_remove_on_destruction();
  }

  clexulator::SparseCoefficients coefficients;
  std::unique_ptr<clexulator::ClusterExpansion> clex;

  std::vector<clexulator::SparseCoefficients> multicoeffs;
  std::unique_ptr<clexulator::MultiClusterExpansion> multiclex;

  void ReadEciJson_tests() {
    fs::path eci_path =
        test::data_dir("clexulator") / "OccClexulatorZrOTest_2" / "eci.json";
    jsonParser json(eci_path);
    InputParser<clexulator::SparseCoefficients> parser(json);
    EXPECT_TRUE(parser.valid());
    EXPECT_EQ(parser.value->index.size(), 33);
    EXPECT_EQ(parser.value->value.size(), 33);

    coefficients = *parser.value;
  }

  void ReadCoeffJson_tests() {
    fs::path eci_path =
        test::data_dir("clexulator") / "OccClexulatorZrOTest_2" / "coeff.json";
    jsonParser json(eci_path);
    InputParser<clexulator::SparseCoefficients> parser(json);
    EXPECT_TRUE(parser.valid());
    EXPECT_EQ(parser.value->index.size(), 33);
    EXPECT_EQ(parser.value->value.size(), 33);

    coefficients = *parser.value;
  }
  void ReadMultiCoeffJson_tests() {
    multicoeffs.clear();

    {
      fs::path eci_path = test::data_dir("clexulator") /
                          "OccClexulatorZrOTest_2" / "coeff_0.json";
      jsonParser json(eci_path);
      InputParser<clexulator::SparseCoefficients> parser(json);
      EXPECT_TRUE(parser.valid());
      EXPECT_EQ(parser.value->index.size(), 1);
      EXPECT_EQ(parser.value->value.size(), 1);
      multicoeffs.push_back(*parser.value);
    }

    {
      fs::path eci_path = test::data_dir("clexulator") /
                          "OccClexulatorZrOTest_2" / "coeff_1.json";
      jsonParser json(eci_path);
      InputParser<clexulator::SparseCoefficients> parser(json);
      EXPECT_TRUE(parser.valid());
      EXPECT_EQ(parser.value->index.size(), 2);
      EXPECT_EQ(parser.value->value.size(), 2);
      multicoeffs.push_back(*parser.value);
    }
  }

  /// Explicitly pass the `parse_eci_json` function
  void ReadEciExplicitJson_tests() {
    fs::path eci_path =
        test::data_dir("clexulator") / "OccClexulatorZrOTest_2" / "eci.json";
    jsonParser json(eci_path);
    InputParser<clexulator::SparseCoefficients> parser(parse_eci_json, json);
    EXPECT_TRUE(parser.valid());
    EXPECT_EQ(parser.value->index.size(), 33);
    EXPECT_EQ(parser.value->value.size(), 33);

    coefficients = *parser.value;
  }

  void MakeClexulator_tests() {
    // Check constructed clexulator
    EXPECT_EQ(clexulator->name(), clexulator_name);
    EXPECT_EQ(clexulator->nlist_size(), 225);
    EXPECT_EQ(clexulator->corr_size(), 74);
    EXPECT_EQ(clexulator->n_point_corr(), 2);
    EXPECT_EQ(clexulator->neighborhood().size(), 107);
  }

  void check_per_unitcell(double expected_value) {
    Eigen::VectorXd corr_per_supercell = clex->correlations().per_supercell();
    Eigen::VectorXd corr_per_unitcell =
        clex->correlations().per_unitcell(corr_per_supercell);
    double sum = 0.0;
    for (Index i = 0; i < coefficients.index.size(); ++i) {
      Index coeff_index = coefficients.index[i];
      double coeff_value = coefficients.value[i];
      double contrib = corr_per_unitcell(coeff_index) * coeff_value;
      sum += contrib;
      // std::cout << coeff_index << ": " << corr_per_unitcell(coeff_index) << "
      // "
      // << coeff_value << " " << contrib << " " << sum << std::endl;
    }
    double per_unitcell = clex->per_unitcell();
    // std::cout << "value: " << per_unitcell << std::endl;
    EXPECT_TRUE(CASM::almost_equal(per_unitcell, sum));
    EXPECT_TRUE(CASM::almost_equal(per_unitcell, expected_value));
  };

  void MakeClex_tests() {
    // Check correlations (checks running without errors, not values)
    Eigen::Matrix3l T = Eigen::Matrix3l::Identity() * 2;
    test::TestConfiguration config(prim, T, *prim_neighbor_list);

    // Make a copy of DoF values to test calculating on different DoF values
    clexulator::ConfigDoFValues dof_values_2 = config.dof_values;

    clex = notstd::make_unique<clexulator::ClusterExpansion>(
        config.supercell_neighbor_list, clexulator, coefficients);

    // Expected value, from single point occupant:
    double ZrO_point_mult = 2.0;
    double volume = T.determinant();
    Index point_index = CASM::find_index(coefficients.index, 1);
    double expected_point_corr = 1.0 / ZrO_point_mult / volume;
    double expected_value =
        expected_point_corr * coefficients.value[point_index];

    // original DoF values
    clex->set(&config.dof_values);
    check_per_unitcell(0.0);

    config.dof_values.occupation(16) = 1;
    check_per_unitcell(expected_value);

    // copied DoF values
    clex->set(&dof_values_2);
    check_per_unitcell(0.0);

    dof_values_2.occupation(16) = 1;
    check_per_unitcell(expected_value);
  }

  void MakeMultiClex_tests() {
    // Check correlations (checks running without errors, not values)
    Eigen::Matrix3l T = Eigen::Matrix3l::Identity() * 2;
    test::TestConfiguration config(prim, T, *prim_neighbor_list);

    multiclex = notstd::make_unique<clexulator::MultiClusterExpansion>(
        config.supercell_neighbor_list, clexulator, multicoeffs);
    EXPECT_EQ(multiclex->coefficients().size(), 2);

    multiclex->set(&config.dof_values);
    // default config
    {
      Eigen::VectorXd const &values = multiclex->per_unitcell();
      EXPECT_EQ(values.size(), 2);
      EXPECT_TRUE(CASM::almost_equal(values(0), 1.0));
      EXPECT_TRUE(CASM::almost_equal(values(1), 1.0));
    }

    // all Va-O sites filled with O
    for (Index l = 16; l < 32; ++l) {
      config.dof_values.occupation(l) = 1;
    }
    {
      Eigen::VectorXd const &values = multiclex->per_unitcell();
      EXPECT_EQ(values.size(), 2);
      EXPECT_TRUE(CASM::almost_equal(values(0), 1.0));
      EXPECT_TRUE(CASM::almost_equal(values(1), 2.0));
    }
  }
};

TEST_F(OccZrOClexTest, Tests) {
  // only compile once...
  MakeClexulator_tests();

  {
    ReadEciJson_tests();
    MakeClex_tests();
  }

  {
    ReadCoeffJson_tests();
    MakeClex_tests();
  }

  {
    ReadEciExplicitJson_tests();
    MakeClex_tests();
  }

  {
    ReadMultiCoeffJson_tests();
    MakeMultiClex_tests();
  }
}

}  // namespace test
