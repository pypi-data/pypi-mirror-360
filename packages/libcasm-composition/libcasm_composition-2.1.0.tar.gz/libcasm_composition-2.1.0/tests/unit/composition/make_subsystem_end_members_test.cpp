#include "casm/casm_io/container/stream_io.hh"
#include "casm/composition/composition_space.hh"
#include "casm/misc/CASM_Eigen_math.hh"
#include "gtest/gtest.h"
#include "testfunctions.hh"

using namespace CASM;

TEST(MakeSubsystemEndMembersTest, Test1) {
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
  Index dim = components.size();

  std::map<IndexSet, std::map<SublatType, Multiplicity>> expected_subsystems;
  expected_subsystems[subsystem_0] = SublatTypeMap({{sublat_type_0, 1}});

  Eigen::MatrixXi subsystem_end_members = make_subsystem_end_members(
      subsystem_0, expected_subsystems[subsystem_0], dim);

  Eigen::MatrixXi expected_end_members(2, 2);
  expected_end_members.col(0) << 1, 0;
  expected_end_members.col(1) << 0, 1;

  EXPECT_TRUE(
      test::is_column_permutation(subsystem_end_members, expected_end_members));
}

TEST(MakeSubsystemEndMembersTest, Test2) {
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
  Index dim = components.size();

  std::map<IndexSet, std::map<SublatType, Multiplicity>> expected_subsystems;
  expected_subsystems[subsystem_0] = SublatTypeMap({{sublat_type_0, 1}});

  Eigen::MatrixXi subsystem_end_members = make_subsystem_end_members(
      subsystem_0, expected_subsystems[subsystem_0], dim);

  Eigen::MatrixXi expected_end_members(2, 2);
  expected_end_members.col(0) << 1, 0;
  expected_end_members.col(1) << 0, 1;

  EXPECT_TRUE(
      test::is_column_permutation(subsystem_end_members, expected_end_members));
}

TEST(MakeSubsystemEndMembersTest, Test3) {
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
  Index dim = components.size();

  std::map<IndexSet, std::map<SublatType, Multiplicity>> expected_subsystems;
  expected_subsystems[subsystem_0] = SublatTypeMap({{sublat_type_0, 2}});

  Eigen::MatrixXi subsystem_end_members = make_subsystem_end_members(
      subsystem_0, expected_subsystems[subsystem_0], dim);

  Eigen::MatrixXi expected_end_members(2, 2);
  expected_end_members.col(0) << 2, 0;
  expected_end_members.col(1) << 0, 2;

  EXPECT_TRUE(
      test::is_column_permutation(subsystem_end_members, expected_end_members));
}

TEST(MakeSubsystemEndMembersTest, Test4) {
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
  Index dim = components.size();

  std::map<IndexSet, std::map<SublatType, Multiplicity>> expected_subsystems;
  expected_subsystems[subsystem_0] = SublatTypeMap(
      {{sublat_type_0, 1}, {sublat_type_1, 1}, {sublat_type_2, 1}});

  Eigen::MatrixXi subsystem_end_members = make_subsystem_end_members(
      subsystem_0, expected_subsystems[subsystem_0], dim);

  // std::cout << "subsystem_end_members:\n" <<
  // subsystem_end_members.transpose() << std::endl;

  Eigen::MatrixXi expected_end_members(4, 8);
  expected_end_members.col(0) << 1, 0, 2, 0;
  expected_end_members.col(1) << 0, 2, 1, 0;
  expected_end_members.col(2) << 0, 1, 2, 0;
  expected_end_members.col(3) << 0, 2, 0, 1;
  expected_end_members.col(4) << 1, 1, 1, 0;
  expected_end_members.col(5) << 1, 1, 0, 1;
  expected_end_members.col(6) << 1, 0, 1, 1;
  expected_end_members.col(7) << 0, 1, 1, 1;

  EXPECT_TRUE(
      test::is_column_permutation(subsystem_end_members, expected_end_members));
}

TEST(MakeSubsystemEndMembersTest, Test5) {
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
  Index dim = components.size();

  std::map<IndexSet, std::map<SublatType, Multiplicity>> expected_subsystems;
  expected_subsystems[subsystem_0] = SublatTypeMap({{sublat_type_0, 1}});
  expected_subsystems[subsystem_1] = SublatTypeMap({{sublat_type_1, 1}});

  // - subsystem 0
  {
    Eigen::MatrixXi subsystem_end_members = make_subsystem_end_members(
        subsystem_0, expected_subsystems[subsystem_0], dim);

    // std::cout << "subsystem_end_members:\n" <<
    // subsystem_end_members.transpose() << std::endl;

    Eigen::MatrixXi expected_end_members(4, 2);
    expected_end_members.col(0) << 1, 0, 0, 0;
    expected_end_members.col(1) << 0, 1, 0, 0;

    EXPECT_TRUE(test::is_column_permutation(subsystem_end_members,
                                            expected_end_members));
  }

  // - subsystem 1
  {
    Eigen::MatrixXi subsystem_end_members = make_subsystem_end_members(
        subsystem_1, expected_subsystems[subsystem_1], dim);

    // std::cout << "subsystem_end_members:\n" <<
    // subsystem_end_members.transpose() << std::endl;

    Eigen::MatrixXi expected_end_members(4, 2);
    expected_end_members.col(0) << 0, 0, 1, 0;
    expected_end_members.col(1) << 0, 0, 0, 1;

    EXPECT_TRUE(test::is_column_permutation(subsystem_end_members,
                                            expected_end_members));
  }
}

TEST(MakeSubsystemEndMembersTest, Test6) {
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
  Index dim = components.size();

  std::map<IndexSet, std::map<SublatType, Multiplicity>> expected_subsystems;
  expected_subsystems[subsystem_0] =
      SublatTypeMap({{sublat_type_0, 1}, {sublat_type_1, 1}});

  Eigen::MatrixXi subsystem_end_members = make_subsystem_end_members(
      subsystem_0, expected_subsystems[subsystem_0], dim);

  // std::cout << "subsystem_end_members:\n" <<
  // subsystem_end_members.transpose() << std::endl;

  Eigen::MatrixXi expected_end_members(4, 7);
  expected_end_members.col(0) << 2, 0, 0, 0;
  expected_end_members.col(1) << 0, 2, 0, 0;
  expected_end_members.col(2) << 1, 0, 1, 0;
  expected_end_members.col(3) << 0, 1, 1, 0;
  expected_end_members.col(4) << 1, 0, 0, 1;
  expected_end_members.col(5) << 0, 1, 0, 1;
  expected_end_members.col(6) << 0, 0, 1, 1;

  EXPECT_TRUE(
      test::is_column_permutation(subsystem_end_members, expected_end_members));
}
