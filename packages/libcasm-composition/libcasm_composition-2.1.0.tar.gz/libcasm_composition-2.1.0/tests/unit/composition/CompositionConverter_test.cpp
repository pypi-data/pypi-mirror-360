#include "casm/composition/CompositionConverter.hh"

#include "casm/casm_io/container/stream_io.hh"
#include "casm/misc/CASM_Eigen_math.hh"
#include "gtest/gtest.h"

using namespace CASM;

TEST(CompositionConverterTest, Test1) {
  using namespace CASM::composition;

  // std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}};
  std::vector<std::string> components = {"A", "B"};

  // composition axes origin composition
  Eigen::VectorXd origin(2);
  origin << 0, 1;

  // composition end member compositions, as columns
  Eigen::MatrixXd end_members(2, 1);
  end_members.col(0) << 1, 0;

  CompositionConverter comp_converter(components, origin, end_members);

  // composition conversions
  EXPECT_EQ(comp_converter.param_formula(), "a(0.5+0.5A-0.5B)");
  EXPECT_EQ(comp_converter.mol_formula(), "A(a)B(1-a)");

  Eigen::VectorXd comp_n(2);
  Eigen::VectorXd expected(1);

  comp_n = origin;
  expected << 0.0;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));

  comp_n = end_members.col(0);
  expected << 1.0;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));

  comp_n << 0.5, 0.5;
  expected << 0.5;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));

  comp_n << 0.25, 0.75;
  expected << 0.25;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));

  // chemical potential conversions
  std::stringstream ss;
  display_param_chem_pot(ss, comp_converter);
  EXPECT_EQ(ss.str(), "param_chem_pot(a) = chem_pot(A) - chem_pot(B) \n");

  Eigen::VectorXd param_chem_pot;
  Eigen::VectorXd chem_pot(2);
  chem_pot << -2.0, 2.0;  // dG/dn_A, dG/dn_B
  expected << -4.0;       // dG/da
  param_chem_pot = comp_converter.param_chem_pot(chem_pot);
  EXPECT_EQ(param_chem_pot.size(), 1);
  EXPECT_TRUE(almost_equal(param_chem_pot, expected));

  chem_pot << -4.0, 0.0;  // dG/dn_A, dG/dn_B
  expected << -4.0;       // dG/da
  param_chem_pot = comp_converter.param_chem_pot(chem_pot);
  EXPECT_EQ(param_chem_pot.size(), 1);
  EXPECT_TRUE(almost_equal(param_chem_pot, expected));
}

TEST(CompositionConverterTest, Test2) {
  using namespace CASM::composition;

  // std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}, {"A",
  // "B"}};
  std::vector<std::string> components = {"A", "B"};

  // composition axes origin composition
  Eigen::VectorXd origin(2);
  origin << 0, 2;

  // composition end member compositions, as columns
  Eigen::MatrixXd end_members(2, 1);
  end_members.col(0) << 2, 0;

  CompositionConverter comp_converter(components, origin, end_members);

  // composition conversions
  EXPECT_EQ(comp_converter.param_formula(), "a(0.5+0.25A-0.25B)");
  EXPECT_EQ(comp_converter.mol_formula(), "A(2a)B(2-2a)");

  Eigen::VectorXd comp_n(2);
  Eigen::VectorXd expected(1);

  comp_n = origin;
  expected << 0.0;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));

  comp_n = end_members.col(0);
  expected << 1.0;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));

  comp_n << 1.0, 1.0;
  expected << 0.5;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));

  comp_n << 0.5, 1.5;
  expected << 0.25;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));

  // chemical potential conversions
  std::stringstream ss;
  display_param_chem_pot(ss, comp_converter);
  EXPECT_EQ(ss.str(), "param_chem_pot(a) = 2*chem_pot(A) -2*chem_pot(B) \n");

  Eigen::VectorXd param_chem_pot;
  Eigen::VectorXd chem_pot(2);
  chem_pot << -2.0, 2.0;  // dG/dn_A, dG/dn_B
  expected << -8.0;       // dG/da
  param_chem_pot = comp_converter.param_chem_pot(chem_pot);
  EXPECT_EQ(param_chem_pot.size(), 1);
  EXPECT_TRUE(almost_equal(param_chem_pot, expected));

  chem_pot << -4.0, 0.0;  // dG/dn_A, dG/dn_B
  expected << -8.0;       // dG/da
  param_chem_pot = comp_converter.param_chem_pot(chem_pot);
  EXPECT_EQ(param_chem_pot.size(), 1);
  EXPECT_TRUE(almost_equal(param_chem_pot, expected));
}

TEST(CompositionConverterTest, Test3) {
  using namespace CASM::composition;

  // std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}, {"C",
  // "D"}};
  std::vector<std::string> components = {"A", "B", "C", "D"};

  // composition axes origin composition
  Eigen::VectorXd origin(4);
  origin << 1, 0, 1, 0;

  // composition end member compositions, as columns
  Eigen::MatrixXd end_members(4, 2);
  end_members.col(0) << 1, 0, 0, 1;
  end_members.col(1) << 0, 1, 1, 0;

  CompositionConverter comp_converter(components, origin, end_members);

  EXPECT_EQ(comp_converter.param_formula(), "a(0.5-0.5C+0.5D)b(0.5-0.5A+0.5B)");
  EXPECT_EQ(comp_converter.mol_formula(), "A(1-b)B(b)C(1-a)D(a)");

  Eigen::VectorXd comp_n(4);
  Eigen::VectorXd expected(2);

  comp_n = origin;
  expected << 0.0, 0.0;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));

  comp_n = end_members.col(0);
  expected << 1.0, 0.0;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));
  comp_n = end_members.col(1);
  expected << 0.0, 1.0;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));

  comp_n << 0.5, 0.5, 1.0, 0.0;
  expected << 0.0, 0.5;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));

  comp_n << 0.0, 1.0, 0.5, 0.5;
  expected << 0.5, 1.0;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));
}

TEST(CompositionConverterTest, Test4) {
  using namespace CASM::composition;

  // std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}, {"B",
  // "C"}, {"C", "D"}};
  std::vector<std::string> components = {"A", "B", "C", "D"};

  // composition axes origin composition
  Eigen::VectorXd origin(4);
  origin << 0, 2, 1, 0;

  // composition end member compositions, as columns
  Eigen::MatrixXd end_members(4, 3);
  end_members.col(0) << 1, 1, 1, 0;
  end_members.col(1) << 0, 2, 0, 1;
  end_members.col(2) << 0, 1, 2, 0;

  CompositionConverter comp_converter(components, origin, end_members);

  EXPECT_EQ(comp_converter.param_formula(),
            "a(0.75+0.75A-0.25B-0.25C-0.25D)b(0.75-0.25A-0.25B-0.25C+0.75D)c(0."
            "5-0.5A-0.5B+0.5C+0.5D)");
  EXPECT_EQ(comp_converter.mol_formula(), "A(a)B(2-a-c)C(1-b+c)D(b)");

  Eigen::VectorXd comp_n(4);
  Eigen::VectorXd expected(3);

  comp_n = origin;
  expected << 0.0, 0.0, 0.0;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));

  comp_n = end_members.col(0);
  expected << 1.0, 0.0, 0.0;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));
  comp_n = end_members.col(1);
  expected << 0.0, 1.0, 0.0;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));
  comp_n = end_members.col(2);
  expected << 0.0, 0.0, 1.0;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));

  comp_n << 0.5, 1.0, 1.0, 0.5;
  expected << 0.5, 0.5, 0.5;
  // std::cout << "param_comp: "
  //           << comp_converter.param_composition(comp_n).transpose()
  //           << std::endl;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));

  comp_n << 1.0, 0.5, 0.5, 1.0;
  expected << 1.0, 1.0, 0.5;
  // std::cout << "param_comp: "
  //           << comp_converter.param_composition(comp_n).transpose()
  //           << std::endl;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));
}

TEST(CompositionConverterTest, Test5) {
  using namespace CASM::composition;

  // std::vector<std::vector<std::string>> allowed_occs = {{"Zr"}, {"Zr"},
  // {"Va", "O"}, {"Va", "O"}};
  std::vector<std::string> components = {"Zr", "Va", "O"};

  // composition axes origin composition
  Eigen::VectorXd origin(3);
  origin << 2, 2, 0;

  // composition end member compositions, as columns
  Eigen::MatrixXd end_members(3, 1);
  end_members.col(0) << 2, 0, 2;

  CompositionConverter comp_converter(components, origin, end_members);

  // composition conversions
  EXPECT_EQ(comp_converter.param_formula(), "a(0.5-0.25Va+0.25O)");
  EXPECT_EQ(comp_converter.mol_formula(), "Zr(2)Va(2-2a)O(2a)");

  Eigen::VectorXd comp_n(3);
  Eigen::VectorXd expected(1);

  comp_n = origin;
  expected << 0.0;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));

  comp_n = end_members.col(0);
  expected << 1.0;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));

  comp_n << 2.0, 1.5, 0.5;
  expected << 0.25;
  EXPECT_TRUE(almost_equal(comp_converter.param_composition(comp_n), expected));

  // chemical potential conversions
  Eigen::VectorXd param_chem_pot;
  Eigen::VectorXd chem_pot(3);
  chem_pot << 0.0, 0.0, 2.0;  // dG/dn_Zr=<does not apply>, dG/dn_Va=0, dG/dn_O
  expected << 4.0;            // dG/da
  param_chem_pot = comp_converter.param_chem_pot(chem_pot);
  EXPECT_EQ(param_chem_pot.size(), 1);
  EXPECT_TRUE(almost_equal(param_chem_pot, expected));

  std::stringstream ss;
  display_param_chem_pot(ss, comp_converter);
  EXPECT_EQ(ss.str(), "param_chem_pot(a) = 2*chem_pot(O) \n");
}
