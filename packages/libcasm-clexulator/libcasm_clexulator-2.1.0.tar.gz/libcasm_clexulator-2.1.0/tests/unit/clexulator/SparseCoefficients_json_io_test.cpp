#include "casm/clexulator/io/json/SparseCoefficients_json_io.hh"

#include "autotools.hh"
#include "casm/casm_io/json/InputParser_impl.hh"
#include "casm/clexulator/SparseCoefficients.hh"
#include "gtest/gtest.h"
#include "testdir.hh"

using namespace CASM;

namespace test {

TEST(ParseSparseCoefficients, ParseECIJsonTest) {
  // read example eci.json file and check
  fs::path eci_path =
      test::data_dir("clexulator") / "OccClexulatorZrOTest_2" / "eci.json";
  jsonParser json(eci_path);
  InputParser<clexulator::SparseCoefficients> parser(parse_eci_json, json);
  EXPECT_TRUE(parser.valid());
  EXPECT_EQ(parser.value->index.size(), 33);
  EXPECT_EQ(parser.value->value.size(), 33);
}

TEST(ParseSparseCoefficients, ParseCoeffJson) {
  fs::path coeff_path =
      test::data_dir("clexulator") / "OccClexulatorZrOTest_2" / "coeff.json";
  jsonParser json(coeff_path);
  InputParser<clexulator::SparseCoefficients> parser(json);
  EXPECT_TRUE(parser.valid());
  EXPECT_EQ(parser.value->index.size(), 33);
  EXPECT_EQ(parser.value->value.size(), 33);
}

TEST(ParseSparseCoefficients, ParseECIJsonTestAutomatic) {
  fs::path eci_path =
      test::data_dir("clexulator") / "OccClexulatorZrOTest_2" / "eci.json";
  jsonParser json(eci_path);
  InputParser<clexulator::SparseCoefficients> parser(json);

  EXPECT_TRUE(parser.valid());
  EXPECT_EQ(parser.value->index.size(), 33);
  EXPECT_EQ(parser.value->value.size(), 33);
}

TEST(ParseSparseCoefficients, ToJsonTest) {
  clexulator::SparseCoefficients coeff;
  coeff.index = std::vector<unsigned int>{0, 1, 2, 5, 6};
  coeff.value = std::vector<double>{1.0, 1.0, 1.0, 1.0, 1.0};

  jsonParser json;
  to_json(coeff, json);

  EXPECT_TRUE(json.is_array());
  EXPECT_EQ(coeff.index.size(), json.size());
}

}  // namespace test
