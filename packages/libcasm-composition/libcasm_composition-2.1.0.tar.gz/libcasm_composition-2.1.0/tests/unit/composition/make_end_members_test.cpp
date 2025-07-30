#include "casm/casm_io/container/stream_io.hh"
#include "casm/composition/composition_space.hh"
#include "casm/misc/CASM_Eigen_math.hh"
#include "gtest/gtest.h"
#include "testfunctions.hh"

using namespace CASM;

TEST(MakeEndMembersTest, Test1) {
  using namespace CASM::composition;

  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}};
  std::vector<std::string> components = {"A", "B"};

  Eigen::MatrixXi end_members = make_end_members(components, allowed_occs);

  Eigen::MatrixXi expected_end_members(2, 2);
  expected_end_members.col(0) << 1, 0;
  expected_end_members.col(1) << 0, 1;

  EXPECT_TRUE(test::is_column_permutation(end_members, expected_end_members));
}

TEST(MakeEndMembersTest, Test2) {
  using namespace CASM::composition;

  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}};
  std::vector<std::string> components = {"B", "A"};

  Eigen::MatrixXi end_members = make_end_members(components, allowed_occs);

  Eigen::MatrixXi expected_end_members(2, 2);
  expected_end_members.col(0) << 1, 0;
  expected_end_members.col(1) << 0, 1;

  EXPECT_TRUE(test::is_column_permutation(end_members, expected_end_members));
}

TEST(MakeEndMembersTest, Test3) {
  using namespace CASM::composition;

  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}, {"B", "A"}};
  std::vector<std::string> components = {"A", "B"};

  Eigen::MatrixXi end_members = make_end_members(components, allowed_occs);

  Eigen::MatrixXi expected_end_members(2, 2);
  expected_end_members.col(0) << 2, 0;
  expected_end_members.col(1) << 0, 2;

  EXPECT_TRUE(test::is_column_permutation(end_members, expected_end_members));
}

TEST(MakeEndMembersTest, Test4) {
  using namespace CASM::composition;

  std::vector<std::vector<std::string>> allowed_occs = {
      {"A", "B"}, {"B", "C"}, {"C", "D"}};
  std::vector<std::string> components = {"A", "B", "C", "D"};

  Eigen::MatrixXi end_members = make_end_members(components, allowed_occs);

  Eigen::MatrixXi expected_end_members(4, 8);
  expected_end_members.col(0) << 1, 0, 2, 0;
  expected_end_members.col(1) << 0, 2, 1, 0;
  expected_end_members.col(2) << 0, 1, 2, 0;
  expected_end_members.col(3) << 0, 2, 0, 1;
  expected_end_members.col(4) << 1, 1, 1, 0;
  expected_end_members.col(5) << 1, 1, 0, 1;
  expected_end_members.col(6) << 1, 0, 1, 1;
  expected_end_members.col(7) << 0, 1, 1, 1;

  EXPECT_TRUE(test::is_column_permutation(end_members, expected_end_members));
}

TEST(MakeEndMembersTest, Test5) {
  using namespace CASM::composition;

  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}, {"C", "D"}};
  std::vector<std::string> components = {"A", "B", "C", "D"};

  Eigen::MatrixXi end_members = make_end_members(components, allowed_occs);

  Eigen::MatrixXi expected_end_members(4, 4);
  expected_end_members.col(0) << 1, 0, 1, 0;
  expected_end_members.col(1) << 0, 1, 1, 0;
  expected_end_members.col(2) << 1, 0, 0, 1;
  expected_end_members.col(3) << 0, 1, 0, 1;

  EXPECT_TRUE(test::is_column_permutation(end_members, expected_end_members));
}

TEST(MakeEndMembersTest, Test6) {
  using namespace CASM::composition;

  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B", "C"},
                                                        {"A", "B", "D"}};
  std::vector<std::string> components = {"A", "B", "C", "D"};

  Eigen::MatrixXi end_members = make_end_members(components, allowed_occs);

  Eigen::MatrixXi expected_end_members(4, 7);
  expected_end_members.col(0) << 2, 0, 0, 0;
  expected_end_members.col(1) << 0, 2, 0, 0;
  expected_end_members.col(2) << 1, 0, 1, 0;
  expected_end_members.col(3) << 0, 1, 1, 0;
  expected_end_members.col(4) << 1, 0, 0, 1;
  expected_end_members.col(5) << 0, 1, 0, 1;
  expected_end_members.col(6) << 0, 0, 1, 1;

  EXPECT_TRUE(test::is_column_permutation(end_members, expected_end_members));
}
