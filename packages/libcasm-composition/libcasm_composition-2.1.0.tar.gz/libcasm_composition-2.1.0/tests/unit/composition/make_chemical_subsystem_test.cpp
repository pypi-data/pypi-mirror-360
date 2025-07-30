#include "casm/casm_io/container/stream_io.hh"
#include "casm/composition/composition_space.hh"
#include "gtest/gtest.h"
#include "testfunctions.hh"

using namespace CASM;

TEST(MakeChemicalSubsystemsTest, Test1) {
  using namespace CASM::composition;

  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}};

  std::vector<std::string> components = {"A", "B"};

  typedef Index Multiplicity;
  typedef std::set<Index> IndexSet;
  typedef std::set<Index> SublatType;
  typedef std::map<SublatType, Multiplicity> SublatTypeMap;
  std::map<IndexSet, std::map<SublatType, Multiplicity>> chemical_subsystems =
      make_chemical_subsystems(components, allowed_occs);

  IndexSet sublat_type_0({0, 1});  // A, B
  IndexSet subsystem_0({0, 1});    // A, B

  std::map<IndexSet, std::map<SublatType, Multiplicity>> expected;
  expected[subsystem_0] = SublatTypeMap({{sublat_type_0, 1}});

  EXPECT_EQ(chemical_subsystems, expected);
}

TEST(MakeChemicalSubsystemsTest, Test2) {
  using namespace CASM::composition;

  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}};

  std::vector<std::string> components = {"B", "A"};

  typedef Index Multiplicity;
  typedef std::set<Index> IndexSet;
  typedef std::set<Index> SublatType;
  typedef std::map<SublatType, Multiplicity> SublatTypeMap;
  std::map<IndexSet, std::map<SublatType, Multiplicity>> chemical_subsystems =
      make_chemical_subsystems(components, allowed_occs);

  IndexSet sublat_type_0({0, 1});  // A, B
  IndexSet subsystem_0({0, 1});    // A, B

  std::map<IndexSet, std::map<SublatType, Multiplicity>> expected;
  expected[subsystem_0] = SublatTypeMap({{sublat_type_0, 1}});

  EXPECT_EQ(chemical_subsystems, expected);
}

TEST(MakeChemicalSubsystemsTest, Test3) {
  using namespace CASM::composition;

  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}, {"B", "A"}};

  std::vector<std::string> components = {"A", "B"};

  typedef Index Multiplicity;
  typedef std::set<Index> IndexSet;
  typedef std::set<Index> SublatType;
  typedef std::map<SublatType, Multiplicity> SublatTypeMap;
  std::map<IndexSet, std::map<SublatType, Multiplicity>> chemical_subsystems =
      make_chemical_subsystems(components, allowed_occs);

  IndexSet sublat_type_0({0, 1});  // A, B
  IndexSet subsystem_0({0, 1});    // A, B

  std::map<IndexSet, std::map<SublatType, Multiplicity>> expected;
  expected[subsystem_0] = SublatTypeMap({{sublat_type_0, 2}});

  EXPECT_EQ(chemical_subsystems, expected);
}

TEST(MakeChemicalSubsystemsTest, Test4) {
  using namespace CASM::composition;

  std::vector<std::vector<std::string>> allowed_occs = {
      {"A", "B"}, {"B", "C"}, {"C", "D"}};

  std::vector<std::string> components = {"A", "B", "C", "D"};

  typedef Index Multiplicity;
  typedef std::set<Index> IndexSet;
  typedef std::set<Index> SublatType;
  typedef std::map<SublatType, Multiplicity> SublatTypeMap;
  std::map<IndexSet, std::map<SublatType, Multiplicity>> chemical_subsystems =
      make_chemical_subsystems(components, allowed_occs);

  IndexSet sublat_type_0({0, 1});      // A, B
  IndexSet sublat_type_1({1, 2});      // B, C
  IndexSet sublat_type_2({2, 3});      // C, D
  IndexSet subsystem_0({0, 1, 2, 3});  // A, B, C, D

  std::map<IndexSet, std::map<SublatType, Multiplicity>> expected;
  expected[subsystem_0] = SublatTypeMap(
      {{sublat_type_0, 1}, {sublat_type_1, 1}, {sublat_type_2, 1}});

  EXPECT_EQ(chemical_subsystems, expected);
}

TEST(MakeChemicalSubsystemsTest, Test5) {
  using namespace CASM::composition;

  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}, {"C", "D"}};

  std::vector<std::string> components = {"A", "B", "C", "D"};

  typedef Index Multiplicity;
  typedef std::set<Index> IndexSet;
  typedef std::set<Index> SublatType;
  typedef std::map<SublatType, Multiplicity> SublatTypeMap;
  std::map<IndexSet, std::map<SublatType, Multiplicity>> chemical_subsystems =
      make_chemical_subsystems(components, allowed_occs);

  IndexSet sublat_type_0({0, 1});  // A, B
  IndexSet sublat_type_1({2, 3});  // C, D
  IndexSet subsystem_0({0, 1});    // A, B, C, D
  IndexSet subsystem_1({2, 3});    // A, B, C, D

  std::map<IndexSet, std::map<SublatType, Multiplicity>> expected;
  expected[subsystem_0] = SublatTypeMap({{sublat_type_0, 1}});
  expected[subsystem_1] = SublatTypeMap({{sublat_type_1, 1}});

  EXPECT_EQ(chemical_subsystems, expected);
}

TEST(MakeChemicalSubsystemsTest, Test6) {
  using namespace CASM::composition;

  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B", "C"},
                                                        {"A", "B", "D"}};

  std::vector<std::string> components = {"A", "B", "C", "D"};

  typedef Index Multiplicity;
  typedef std::set<Index> IndexSet;
  typedef std::set<Index> SublatType;
  typedef std::map<SublatType, Multiplicity> SublatTypeMap;
  std::map<IndexSet, std::map<SublatType, Multiplicity>> chemical_subsystems =
      make_chemical_subsystems(components, allowed_occs);

  IndexSet sublat_type_0({0, 1, 2});   // A, B, C
  IndexSet sublat_type_1({0, 1, 3});   // A, B, D
  IndexSet subsystem_0({0, 1, 2, 3});  // A, B, C, D

  std::map<IndexSet, std::map<SublatType, Multiplicity>> expected;
  expected[subsystem_0] =
      SublatTypeMap({{sublat_type_0, 1}, {sublat_type_1, 1}});

  EXPECT_EQ(chemical_subsystems, expected);
}
