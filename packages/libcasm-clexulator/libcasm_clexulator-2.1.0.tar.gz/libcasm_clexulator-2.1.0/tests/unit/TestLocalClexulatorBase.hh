#ifndef CASM_unittest_TestLocalClexulatorBase
#define CASM_unittest_TestLocalClexulatorBase

#include <filesystem>

#include "autotools.hh"
#include "casm/casm_io/container/json_io.hh"
#include "casm/casm_io/json/jsonFile.hh"
#include "casm/casm_io/json/jsonParser.hh"
#include "casm/clexulator/BaseClexulator.hh"
#include "casm/clexulator/Clexulator.hh"
#include "casm/crystallography/BasicStructure.hh"
#include "casm/crystallography/io/BasicStructureIO.hh"
#include "casm/global/filesystem.hh"
#include "casm/system/RuntimeLibrary.hh"
#include "gtest/gtest.h"
#include "testdir.hh"

namespace test {

class TestLocalClexulatorBase : public testing::Test {
 protected:
  /// \brief Constructor
  ///
  /// \param _clexulator_basename Ex: ZrO_Clexulator (excludes basis set name)
  /// \param _test_subdir Where to read test data from
  /// \param _bset_names Names for each local basis set (i.e. `{"hop0",
  ///     "hop1"}`)
  TestLocalClexulatorBase(std::string _clexulator_basename,
                          std::vector<std::string> const &_bset_names,
                          std::string _test_subdir)
      : clexulator_basename(_clexulator_basename),
        bset_names(_bset_names),
        test_data_dir(test::data_dir("clexulator") / _test_subdir),
        meta(test_data_dir / "meta.json"),
        prim(std::make_shared<xtal::BasicStructure const>(
            read_prim(meta["prim"], TOL))),
        prim_neighbor_list(),
        compile_opt(
            RuntimeLibrary::default_cxx().first + " " +
            RuntimeLibrary::default_cxxflags().first + " " +
            include_path(RuntimeLibrary::default_casm_includedir().first) +
            " " + include_path(autotools::abs_includedir())),
        so_opt(RuntimeLibrary::default_cxx().first + " " +
               RuntimeLibrary::default_soflags().first + " " +
               link_path(RuntimeLibrary::default_casm_libdir().first) + " " +
               link_path(autotools::abs_libdir()) + " " + "-lcasm_clexulator "),
        tmpdir(),
        clexulator() {
    make_clexulator();
  }

  /// \brief Constructor
  ///
  /// \param _clexulator_basename Ex: ZrO_Clexulator (excludes basis set name)
  /// \param _test_subdir Where to read test data from
  /// \param _bset_names Names for each local basis set (i.e. `{"hop0",
  ///     "hop1"}`)
  TestLocalClexulatorBase(std::string _clexulator_basename,
                          std::vector<std::string> const &_bset_names,
                          std::string _test_subdir, bool wait)
      : clexulator_basename(_clexulator_basename),
        bset_names(_bset_names),
        test_data_dir(test::data_dir("clexulator") / _test_subdir),
        meta(test_data_dir / "meta.json"),
        prim(std::make_shared<xtal::BasicStructure const>(
            read_prim(meta["prim"], TOL))),
        prim_neighbor_list(),
        compile_opt(
            RuntimeLibrary::default_cxx().first + " " +
            RuntimeLibrary::default_cxxflags().first + " " +
            include_path(RuntimeLibrary::default_casm_includedir().first) +
            " " + include_path(autotools::abs_includedir())),
        so_opt(RuntimeLibrary::default_cxx().first + " " +
               RuntimeLibrary::default_soflags().first + " " +
               link_path(RuntimeLibrary::default_casm_libdir().first) + " " +
               link_path(autotools::abs_libdir()) + " " + "-lcasm_clexulator "),
        tmpdir(),
        clexulator() {}

  std::string clexulator_basename;

  // i.e. {"hop0", "hop1"} to read local clexulators from "bset.hop0",
  // "bset.hop1", etc.
  std::vector<std::string> bset_names;

  fs::path test_data_dir;
  jsonFile meta;
  std::shared_ptr<xtal::BasicStructure const> prim;
  std::shared_ptr<clexulator::PrimNeighborList> prim_neighbor_list;

  // configure with (in order of priority):
  // - CASM_CXX, CXX, default="c++"
  // - CASM_CXXFLAGS, default="-O3 -Wall -fPIC --std=c++17"
  // - CASM_SOFLAGS, default="-shared"

  std::string compile_opt;
  std::string so_opt;
  TmpDir tmpdir;

  // clexulator[bset_name] ->
  //     std::shared_ptr<std::vector<clexulator::Clexulator> const>
  std::map<std::string,
           std::shared_ptr<std::vector<clexulator::Clexulator> const> >
      clexulator;

  void make_clexulator() {
    // copy files to tmpdir for use
    for (std::string const &bset_name : bset_names) {
      copy_local_clexulator(test_data_dir / "basis_sets",
                            tmpdir.path() / "basis_sets", bset_name,
                            clexulator_basename);
    }

    // make Clexulator
    typedef std::vector<clexulator::Clexulator> clexvec;
    for (std::string const &bset_name : bset_names) {
      clexulator[bset_name] =
          std::make_shared<clexvec const>(clexulator::make_local_clexulator(
              clexulator_basename + "_" + bset_name,
              tmpdir.path() / "basis_sets" / ("bset." + bset_name),
              prim_neighbor_list, compile_opt, so_opt));
    }
  }

  void copy_local_clexulator(fs::path src_basis_sets_dir,
                             fs::path dest_basis_sets_dir,
                             std::string bset_name,
                             std::string clexulator_basename) {
    fs::path src_dir = src_basis_sets_dir / (std::string("bset.") + bset_name);
    fs::path dest_dir =
        dest_basis_sets_dir / (std::string("bset.") + bset_name);
    std::cout << "dest_dir: " << dest_dir << std::endl;

    fs::copy_options copy_options = fs::copy_options::skip_existing;

    // equivalents
    Index i = 0;
    fs::path equiv_dir = fs::path(std::to_string(i));
    while (fs::exists(src_dir / equiv_dir)) {
      std::string src_filename = clexulator_basename + "_" + bset_name + "_" +
                                 std::to_string(i) + ".cc";
      if (!fs::exists(src_dir / equiv_dir / src_filename)) {
        break;
      }
      fs::create_directories(dest_dir / equiv_dir);
      fs::copy_file(src_dir / equiv_dir / src_filename,
                    dest_dir / equiv_dir / src_filename, copy_options);
      ++i;
      equiv_dir = fs::path(std::to_string(i));
    }

    // prototype
    std::string src_filename;
    src_filename = clexulator_basename + "_" + bset_name + ".cc";
    std::cout << "f: " << src_dir / src_filename << std::endl;
    if (fs::exists(src_dir / src_filename)) {
      fs::copy_file(src_dir / src_filename, dest_dir / src_filename,
                    copy_options);
    }

    src_filename = "equivalents_info.json";
    if (fs::exists(src_dir / src_filename)) {
      fs::copy_file(src_dir / src_filename, dest_dir / src_filename,
                    copy_options);
    }
  }
};

}  // namespace test

#endif
