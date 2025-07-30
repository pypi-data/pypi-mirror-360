#include "casm/casm_io/container/stream_io.hh"
#include "casm/composition/CompositionConverter.hh"
#include "casm/composition/composition_space.hh"
#include "casm/misc/CASM_Eigen_math.hh"
#include "gtest/gtest.h"
#include "testfunctions.hh"

using namespace CASM;

TEST(MakeStandardOriginAndEndMembersTest, Test1) {
  using namespace CASM::composition;

  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}};
  std::vector<std::string> components = {"A", "B"};
  double tol = 1e-14;

  std::vector<Eigen::MatrixXd> standard_origin_and_end_members =
      make_standard_origin_and_end_members(components, allowed_occs, tol);

  std::vector<Eigen::MatrixXd> expected;
  {
    Eigen::MatrixXd M(2, 2);
    M.col(0) << 1.0, 0.0;
    M.col(1) << 0.0, 1.0;
    expected.push_back(M);
  }
  {
    Eigen::MatrixXd M(2, 2);
    M.col(0) << 0.0, 1.0;
    M.col(1) << 1.0, 0.0;
    expected.push_back(M);
  }

  std::set<Index> found;
  for (Index i = 0; i < standard_origin_and_end_members.size(); ++i) {
    Eigen::MatrixXd const &A = standard_origin_and_end_members[i];
    for (Index j = 0; j < expected.size(); ++j) {
      Eigen::MatrixXd const &B = expected[j];
      if (almost_equal(A.col(0), B.col(0)) &&
          test::is_column_permutation(A, B)) {
        found.insert(j);
        break;
      }
    }
  }
  EXPECT_EQ(found.size(), standard_origin_and_end_members.size());
}

TEST(MakeStandardOriginAndEndMembersTest, Test2) {
  using namespace CASM::composition;

  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}};
  std::vector<std::string> components = {"B", "A"};
  double tol = 1e-14;

  std::vector<Eigen::MatrixXd> standard_origin_and_end_members =
      make_standard_origin_and_end_members(components, allowed_occs, tol);

  std::vector<Eigen::MatrixXd> expected;
  {
    Eigen::MatrixXd M(2, 2);
    M.col(0) << 1.0, 0.0;
    M.col(1) << 0.0, 1.0;
    expected.push_back(M);
  }
  {
    Eigen::MatrixXd M(2, 2);
    M.col(0) << 0.0, 1.0;
    M.col(1) << 1.0, 0.0;
    expected.push_back(M);
  }

  std::set<Index> found;
  for (Index i = 0; i < standard_origin_and_end_members.size(); ++i) {
    Eigen::MatrixXd const &A = standard_origin_and_end_members[i];
    for (Index j = 0; j < expected.size(); ++j) {
      Eigen::MatrixXd const &B = expected[j];
      if (almost_equal(A.col(0), B.col(0)) &&
          test::is_column_permutation(A, B)) {
        found.insert(j);
        break;
      }
    }
  }
  EXPECT_EQ(found.size(), standard_origin_and_end_members.size());
}

TEST(MakeStandardOriginAndEndMembersTest, Test3) {
  using namespace CASM::composition;

  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}, {"B", "A"}};
  std::vector<std::string> components = {"A", "B"};
  double tol = 1e-14;

  std::vector<Eigen::MatrixXd> standard_origin_and_end_members =
      make_standard_origin_and_end_members(components, allowed_occs, tol);

  std::vector<Eigen::MatrixXd> expected;
  {
    Eigen::MatrixXd M(2, 2);
    M.col(0) << 2.0, 0.0;
    M.col(1) << 0.0, 2.0;
    expected.push_back(M);
  }
  {
    Eigen::MatrixXd M(2, 2);
    M.col(0) << 0.0, 2.0;
    M.col(1) << 2.0, 0.0;
    expected.push_back(M);
  }

  std::set<Index> found;
  for (Index i = 0; i < standard_origin_and_end_members.size(); ++i) {
    Eigen::MatrixXd const &A = standard_origin_and_end_members[i];
    for (Index j = 0; j < expected.size(); ++j) {
      Eigen::MatrixXd const &B = expected[j];
      if (almost_equal(A.col(0), B.col(0)) &&
          test::is_column_permutation(A, B)) {
        found.insert(j);
        break;
      }
    }
  }
  EXPECT_EQ(found.size(), standard_origin_and_end_members.size());
}

TEST(MakeStandardOriginAndEndMembersTest, Test4) {
  using namespace CASM::composition;

  std::vector<std::vector<std::string>> allowed_occs = {
      {"A", "B"}, {"B", "C"}, {"C", "D"}};
  std::vector<std::string> components = {"A", "B", "C", "D"};
  double tol = 1e-14;

  std::vector<Eigen::MatrixXd> standard_origin_and_end_members =
      make_standard_origin_and_end_members(components, allowed_occs, tol);

  // for (auto const &M : standard_origin_and_end_members) {
  //   std::cout << M << std::endl << std::endl;
  // }

  std::vector<Eigen::MatrixXd> expected;
  {
    Eigen::MatrixXd M(4, 4);
    M.row(0) << 0, 1, 0, 0;
    M.row(1) << 2, 1, 2, 1;
    M.row(2) << 1, 1, 0, 2;
    M.row(3) << 0, 0, 1, 0;
    expected.push_back(M);
  }
  {
    Eigen::MatrixXd M(4, 4);
    M.row(0) << 1, 1, 0, 1;
    M.row(1) << 1, 1, 2, 0;
    M.row(2) << 1, 0, 1, 2;
    M.row(3) << 0, 1, 0, 0;
    expected.push_back(M);
  }
  {
    Eigen::MatrixXd M(4, 4);
    M.row(0) << 1, 1, 1, 0;
    M.row(1) << 0, 0, 1, 1;
    M.row(2) << 2, 1, 1, 2;
    M.row(3) << 0, 1, 0, 0;
    expected.push_back(M);
  }
  {
    Eigen::MatrixXd M(4, 4);
    M.row(0) << 1, 1, 1, 0;
    M.row(1) << 1, 0, 1, 2;
    M.row(2) << 0, 1, 1, 0;
    M.row(3) << 1, 1, 0, 1;
    expected.push_back(M);
  }
  {
    Eigen::MatrixXd M(4, 4);
    M.row(0) << 0, 0, 0, 1;
    M.row(1) << 1, 1, 2, 0;
    M.row(2) << 2, 1, 1, 2;
    M.row(3) << 0, 1, 0, 0;
    expected.push_back(M);
  }
  {
    Eigen::MatrixXd M(4, 4);
    M.row(0) << 0, 0, 1, 0;
    M.row(1) << 2, 1, 1, 2;
    M.row(2) << 0, 1, 0, 1;
    M.row(3) << 1, 1, 1, 0;
    expected.push_back(M);
  }
  {
    Eigen::MatrixXd M(4, 4);
    M.row(0) << 0, 1, 0, 0;
    M.row(1) << 1, 0, 2, 1;
    M.row(2) << 1, 1, 0, 2;
    M.row(3) << 1, 1, 1, 0;
    expected.push_back(M);
  }
  {
    Eigen::MatrixXd M(4, 4);
    M.row(0) << 1, 0, 1, 1;
    M.row(1) << 0, 1, 1, 0;
    M.row(2) << 1, 1, 0, 2;
    M.row(3) << 1, 1, 1, 0;
    expected.push_back(M);
  }

  std::set<Index> found;
  for (Index i = 0; i < standard_origin_and_end_members.size(); ++i) {
    Eigen::MatrixXd const &A = standard_origin_and_end_members[i];
    for (Index j = 0; j < expected.size(); ++j) {
      Eigen::MatrixXd const &B = expected[j];
      if (almost_equal(A.col(0), B.col(0)) &&
          test::is_column_permutation(A, B)) {
        found.insert(j);
        break;
      }
    }
  }
  EXPECT_EQ(found.size(), standard_origin_and_end_members.size());
}

TEST(MakeStandardOriginAndEndMembersTest, Test5) {
  using namespace CASM::composition;

  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}, {"C", "D"}};
  std::vector<std::string> components = {"A", "B", "C", "D"};
  double tol = 1e-14;

  std::vector<Eigen::MatrixXd> standard_origin_and_end_members =
      make_standard_origin_and_end_members(components, allowed_occs, tol);

  // for (auto const &M : standard_origin_and_end_members) {
  //   std::cout << M << std::endl << std::endl;
  // }

  std::vector<Eigen::MatrixXd> expected;
  {
    Eigen::MatrixXd M(4, 3);
    M.row(0) << 1, 0, 1;
    M.row(1) << 0, 1, 0;
    M.row(2) << 1, 1, 0;
    M.row(3) << 0, 0, 1;
    expected.push_back(M);
  }
  {
    Eigen::MatrixXd M(4, 3);
    M.row(0) << 1, 0, 1;
    M.row(1) << 0, 1, 0;
    M.row(2) << 0, 0, 1;
    M.row(3) << 1, 1, 0;
    expected.push_back(M);
  }
  {
    Eigen::MatrixXd M(4, 3);
    M.row(0) << 0, 0, 1;
    M.row(1) << 1, 1, 0;
    M.row(2) << 1, 0, 1;
    M.row(3) << 0, 1, 0;
    expected.push_back(M);
  }
  {
    Eigen::MatrixXd M(4, 3);
    M.row(0) << 0, 0, 1;
    M.row(1) << 1, 1, 0;
    M.row(2) << 0, 1, 0;
    M.row(3) << 1, 0, 1;
    expected.push_back(M);
  }

  std::set<Index> found;
  for (Index i = 0; i < standard_origin_and_end_members.size(); ++i) {
    Eigen::MatrixXd const &A = standard_origin_and_end_members[i];
    for (Index j = 0; j < expected.size(); ++j) {
      Eigen::MatrixXd const &B = expected[j];
      if (almost_equal(A.col(0), B.col(0)) &&
          test::is_column_permutation(A, B)) {
        found.insert(j);
        break;
      }
    }
  }
  EXPECT_EQ(found.size(), standard_origin_and_end_members.size());
}

TEST(MakeStandardOriginAndEndMembersTest, Test6) {
  using namespace CASM::composition;

  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B", "C"},
                                                        {"A", "B", "D"}};
  std::vector<std::string> components = {"A", "B", "C", "D"};
  double tol = 1e-14;

  std::vector<Eigen::MatrixXd> standard_origin_and_end_members =
      make_standard_origin_and_end_members(components, allowed_occs, tol);

  // for (auto const &M : standard_origin_and_end_members) {
  //   std::cout << M << std::endl << std::endl;
  // }

  std::vector<Eigen::MatrixXd> expected;
  {
    Eigen::MatrixXd M(4, 4);
    M.row(0) << 2, 1, 1, 0;
    M.row(1) << 0, 0, 0, 2;
    M.row(2) << 0, 0, 1, 0;
    M.row(3) << 0, 1, 0, 0;
    expected.push_back(M);
  }
  {
    Eigen::MatrixXd M(4, 4);
    M.row(0) << 0, 0, 0, 2;
    M.row(1) << 2, 1, 1, 0;
    M.row(2) << 0, 0, 1, 0;
    M.row(3) << 0, 1, 0, 0;
    expected.push_back(M);
  }
  {
    Eigen::MatrixXd M(4, 4);
    M.row(0) << 1, 0, 0, 2;
    M.row(1) << 0, 0, 1, 0;
    M.row(2) << 1, 1, 1, 0;
    M.row(3) << 0, 1, 0, 0;
    expected.push_back(M);
  }
  {
    Eigen::MatrixXd M(4, 4);
    M.row(0) << 0, 0, 1, 0;
    M.row(1) << 1, 0, 0, 2;
    M.row(2) << 1, 1, 1, 0;
    M.row(3) << 0, 1, 0, 0;
    expected.push_back(M);
  }
  {
    Eigen::MatrixXd M(4, 4);
    M.row(0) << 1, 0, 0, 2;
    M.row(1) << 0, 0, 1, 0;
    M.row(2) << 0, 1, 0, 0;
    M.row(3) << 1, 1, 1, 0;
    expected.push_back(M);
  }
  {
    Eigen::MatrixXd M(4, 4);
    M.row(0) << 0, 0, 1, 0;
    M.row(1) << 1, 0, 0, 2;
    M.row(2) << 0, 1, 0, 0;
    M.row(3) << 1, 1, 1, 0;
    expected.push_back(M);
  }

  std::set<Index> found;
  for (Index i = 0; i < standard_origin_and_end_members.size(); ++i) {
    Eigen::MatrixXd const &A = standard_origin_and_end_members[i];
    for (Index j = 0; j < expected.size(); ++j) {
      Eigen::MatrixXd const &B = expected[j];
      if (almost_equal(A.col(0), B.col(0)) &&
          test::is_column_permutation(A, B)) {
        found.insert(j);
        break;
      }
    }
  }
  EXPECT_EQ(found.size(), standard_origin_and_end_members.size());
}
