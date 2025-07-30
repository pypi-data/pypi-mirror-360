// Note:
// - Requires environment variable CASM_PREFIX to specify `global` and
// `crystallography` CASM libraries install location
//   - CASM_PREFIX is recognized by
//   `RuntimeLibrary::default_casm_includedir()`
//     and `RuntimeLibrary::default_casm_libdir()`
// - To avoid re-compiling the Clexulator each time, tests are organized as
// member functions and then all called from a single TEST_F
//

#include "TestConfiguration.hh"
#include "TestLocalClexulatorBase.hh"
#include "casm/clexulator/ConfigDoFValues.hh"
#include "casm/clexulator/ConfigDoFValuesTools_impl.hh"
#include "casm/clexulator/LocalCorrelations.hh"

using namespace CASM;

namespace test {

namespace {

void run_local_correlations_checks(
    TestConfiguration &config,
    std::shared_ptr<std::vector<clexulator::Clexulator> const> &clexulator,
    std::vector<unsigned int> const &corr_indices);

}  // namespace

// Test using data/LocalOccClexulatorZrOTest, which is currently
// generated as part of the LocalOccClexulatorZrOTest in the main CASMcode repo
//
class LocalOccClexulatorZrOTest : public test::TestLocalClexulatorBase {
 protected:
  LocalOccClexulatorZrOTest()
      : TestLocalClexulatorBase("ZrO_Clexulator", {"hop0", "hop1"},
                                "LocalOccClexulatorZrOTest") {
    // can uncomment for debugging:
    // tmpdir.do_not_remove_on_destruction();
  }

  void MakeClexulator_tests() {
    // Check constructed clexulator
    EXPECT_EQ(this->clexulator.size(), 2);

    std::map<std::string, int> expected_local_clexulator_size = {{"hop0", 2},
                                                                 {"hop1", 6}};

    std::map<std::string, std::vector<std::vector<int>>> expected;

    expected["hop0"] = std::vector<std::vector<int>>({
        {53, 6, 53, 14},
        {17, 6, 17, 8},
    });
    expected["hop1"] = std::vector<std::vector<int>>({
        {66, 8, 66, 12},
        {61, 8, 61, 12},
        {63, 8, 63, 12},
        {64, 8, 64, 12},
        {62, 8, 62, 12},
        {65, 8, 65, 12},
    });

    // loop over different basis sets
    for (auto const &bset_name : bset_names) {
      EXPECT_EQ(this->clexulator[bset_name]->size(),
                expected_local_clexulator_size[bset_name]);

      // loop over clexulator for equivalent phenomenal clusters
      Index i = 0;
      for (auto &equiv_clexulator : *this->clexulator[bset_name]) {
        EXPECT_EQ(
            equiv_clexulator.name(),
            clexulator_basename + "_" + bset_name + "_" + std::to_string(i));
        EXPECT_EQ(equiv_clexulator.nlist_size(), expected[bset_name][i][0]);
        EXPECT_EQ(equiv_clexulator.corr_size(), expected[bset_name][i][1]);
        EXPECT_EQ(equiv_clexulator.n_point_corr(), expected[bset_name][i][2]);
        EXPECT_EQ(equiv_clexulator.neighborhood().size(),
                  expected[bset_name][i][3]);
        ++i;
      }
    }
  }

  void UseClexulator_tests() {
    // Check correlations (checks running without errors, not values)
    test::TestConfiguration config(prim, Eigen::Matrix3l::Identity() * 2,
                                   *prim_neighbor_list);

    // basis functions to evaluate for restricted calculations
    std::map<std::string, std::vector<unsigned int>> corr_indices;
    corr_indices["hop0"] = std::vector<unsigned int>({0, 1, 2, 3, 4});
    corr_indices["hop1"] = std::vector<unsigned int>({0, 1, 2, 3, 4});

    for (auto const &bset_name : bset_names) {
      auto const &indices = corr_indices.at(bset_name);
      run_local_correlations_checks(config, this->clexulator[bset_name],
                                    indices);
    }
  }
};

TEST_F(LocalOccClexulatorZrOTest, Tests) {
  MakeClexulator_tests();
  UseClexulator_tests();
}

namespace {

/// \param config TestConfiguration object used as input
/// \param clexulator Clexulators to test
/// \param begin,end Iterators over basis function indices to evaluate for
///     restricted correlations calculations
/// \param expected_has_point `expected_has_point[b]` is the expected result
///     for `Correlations::has_point(l)`, where `b` is the sublattice index for
///     site index `l`.
void run_local_correlations_checks(
    TestConfiguration &config,
    std::shared_ptr<std::vector<clexulator::Clexulator> const> &clexulator,
    std::vector<unsigned int> const &corr_indices) {
  clexulator::LocalCorrelations correlations(config.supercell_neighbor_list,
                                             clexulator, corr_indices,
                                             &config.dof_values);

  Index n_corr = (*clexulator)[0].corr_size();

  // -- local correlation checks --
  EXPECT_EQ(correlations.local(0, 0).size(), n_corr);
}

}  // namespace

}  // namespace test
