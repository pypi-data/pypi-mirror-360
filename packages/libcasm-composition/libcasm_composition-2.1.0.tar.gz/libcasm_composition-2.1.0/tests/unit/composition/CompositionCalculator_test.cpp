#include "casm/composition/CompositionCalculator.hh"

#include "casm/casm_io/container/stream_io.hh"
#include "casm/misc/CASM_Eigen_math.hh"
#include "gtest/gtest.h"

using namespace CASM;

class CompositionCalculatorTest : public testing::Test {
 protected:
  CompositionCalculatorTest() {}

  void initialize(std::vector<std::string> const &_components,
                  std::vector<std::vector<std::string>> const &_allowed_occs,
                  Index volume) {
    components = _components;
    allowed_occs = _allowed_occs;
    calculator_ptr = std::make_unique<composition::CompositionCalculator>(
        components, allowed_occs);
    n_sublat = allowed_occs.size();
    occupation = Eigen::VectorXi::Zero(n_sublat * volume);
    expected_int.resize(components.size());
    expected_double.resize(components.size());
  }

  std::vector<std::string> components;
  std::vector<std::vector<std::string>> allowed_occs;
  std::unique_ptr<composition::CompositionCalculator> calculator_ptr;
  Index n_sublat;
  Eigen::VectorXi occupation;
  Eigen::VectorXi num_each_component;
  Eigen::VectorXi expected_int;
  Eigen::VectorXd mean_num_each_component;
  Eigen::VectorXd expected_double;
  Eigen::VectorXd species_frac;
};

TEST_F(CompositionCalculatorTest, Test0a) {
  using namespace CASM::composition;

  std::vector<std::string> components = {"A", "B"};
  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}};
  Index volume = 10;
  initialize(components, allowed_occs, volume);

  EXPECT_EQ(get_occupant(occupation, 0, allowed_occs), "A");
  set_occupant(occupation, 0, "B", allowed_occs);
  EXPECT_EQ(get_occupant(occupation, 0, allowed_occs), "B");
}

TEST_F(CompositionCalculatorTest, Test0b) {
  using namespace CASM::composition;

  std::vector<std::string> components = {"A", "B"};
  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}, {"B", "A"}};
  Index volume = 10;
  initialize(components, allowed_occs, volume);

  EXPECT_EQ(get_occupant(occupation, 0, allowed_occs), "A");
  EXPECT_EQ(get_occupant(occupation, 10, allowed_occs), "B");

  set_occupant(occupation, 0, "B", allowed_occs);
  EXPECT_EQ(get_occupant(occupation, 0, allowed_occs), "B");

  set_occupant(occupation, 10, "A", allowed_occs);
  EXPECT_EQ(get_occupant(occupation, 10, allowed_occs), "A");
}

TEST_F(CompositionCalculatorTest, Test0c) {
  using namespace CASM::composition;

  std::vector<std::vector<std::string>> allowed_occs = {
      {"Zr"}, {"Zr"}, {"Va", "O"}, {"Va", "O"}};
  std::vector<std::string> components = {"Zr", "Va", "O"};
  Index volume = 10;
  initialize(components, allowed_occs, volume);

  EXPECT_EQ(get_occupant(occupation, 0, allowed_occs), "Zr");
  EXPECT_EQ(get_occupant(occupation, 10, allowed_occs), "Zr");
  EXPECT_EQ(get_occupant(occupation, 20, allowed_occs), "Va");
  EXPECT_EQ(get_occupant(occupation, 30, allowed_occs), "Va");
  set_occupant(occupation, 20, "O", allowed_occs);
  EXPECT_EQ(get_occupant(occupation, 20, allowed_occs), "O");
}

TEST_F(CompositionCalculatorTest, Test1) {
  using namespace CASM::composition;

  std::vector<std::string> components = {"A", "B"};
  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}};
  Index volume = 10;
  initialize(components, allowed_occs, volume);

  // occupation = zeros
  {
    num_each_component = calculator_ptr->num_each_component(occupation);
    expected_int << 10, 0;
    EXPECT_TRUE(num_each_component == expected_int);

    mean_num_each_component =
        calculator_ptr->mean_num_each_component(occupation);
    expected_double << 1.0, 0.0;
    EXPECT_TRUE(almost_equal(mean_num_each_component, expected_double));
  }

  occupation[0] = 1;
  {
    num_each_component = calculator_ptr->num_each_component(occupation);
    expected_int << 9, 1;
    EXPECT_TRUE(num_each_component == expected_int);

    mean_num_each_component =
        calculator_ptr->mean_num_each_component(occupation);
    expected_double << 0.9, 0.1;
    EXPECT_TRUE(almost_equal(mean_num_each_component, expected_double));
  }
}

TEST_F(CompositionCalculatorTest, Test2) {
  using namespace CASM::composition;

  std::vector<std::string> components = {"A", "B"};
  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}, {"A", "B"}};
  Index volume = 10;
  initialize(components, allowed_occs, volume);

  // occupation = zeros
  {
    num_each_component = calculator_ptr->num_each_component(occupation);
    expected_int << 20, 0;
    EXPECT_TRUE(num_each_component == expected_int);

    mean_num_each_component =
        calculator_ptr->mean_num_each_component(occupation);
    expected_double << 2.0, 0.0;
    EXPECT_TRUE(almost_equal(mean_num_each_component, expected_double));
  }

  occupation[0] = 1;
  {
    num_each_component = calculator_ptr->num_each_component(occupation);
    expected_int << 19, 1;
    EXPECT_TRUE(num_each_component == expected_int);

    mean_num_each_component =
        calculator_ptr->mean_num_each_component(occupation);
    expected_double << 1.9, 0.1;
    EXPECT_TRUE(almost_equal(mean_num_each_component, expected_double));
  }
}

TEST_F(CompositionCalculatorTest, Test2b) {
  using namespace CASM::composition;

  std::vector<std::string> components = {"A", "B"};
  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}, {"B", "A"}};
  Index volume = 10;
  initialize(components, allowed_occs, volume);

  // occupation = zeros
  {
    num_each_component = calculator_ptr->num_each_component(occupation);
    expected_int << 10, 10;
    EXPECT_TRUE(num_each_component == expected_int);

    mean_num_each_component =
        calculator_ptr->mean_num_each_component(occupation);
    expected_double << 1.0, 1.0;
    EXPECT_TRUE(almost_equal(mean_num_each_component, expected_double));
  }

  occupation[0] = 1;
  {
    num_each_component = calculator_ptr->num_each_component(occupation);
    expected_int << 9, 11;
    EXPECT_TRUE(num_each_component == expected_int);

    mean_num_each_component =
        calculator_ptr->mean_num_each_component(occupation);
    expected_double << 0.9, 1.1;
    EXPECT_TRUE(almost_equal(mean_num_each_component, expected_double));
  }
}

TEST_F(CompositionCalculatorTest, Test3) {
  using namespace CASM::composition;

  std::vector<std::string> components = {"A", "B", "C", "D"};
  std::vector<std::vector<std::string>> allowed_occs = {{"A", "B"}, {"C", "D"}};
  Index volume = 10;
  initialize(components, allowed_occs, volume);

  // occupation = zeros
  {
    num_each_component = calculator_ptr->num_each_component(occupation);
    expected_int << 10, 0, 10, 0;
    EXPECT_TRUE(num_each_component == expected_int);

    mean_num_each_component =
        calculator_ptr->mean_num_each_component(occupation);
    expected_double << 1.0, 0.0, 1.0, 0.0;
    EXPECT_TRUE(almost_equal(mean_num_each_component, expected_double));
  }

  occupation[0] = 1;
  {
    num_each_component = calculator_ptr->num_each_component(occupation);
    expected_int << 9, 1, 10, 0;
    EXPECT_TRUE(num_each_component == expected_int);

    mean_num_each_component =
        calculator_ptr->mean_num_each_component(occupation);
    expected_double << 0.9, 0.1, 1.0, 0.0;
    EXPECT_TRUE(almost_equal(mean_num_each_component, expected_double));
  }
}

TEST_F(CompositionCalculatorTest, Test4) {
  using namespace CASM::composition;

  std::vector<std::vector<std::string>> allowed_occs = {
      {"Zr"}, {"Zr"}, {"Va", "O"}, {"Va", "O"}};
  std::vector<std::string> components = {"Zr", "Va", "O"};
  Index volume = 10;
  initialize(components, allowed_occs, volume);

  // occupation = zeros
  {
    num_each_component = calculator_ptr->num_each_component(occupation);
    expected_int << 20, 20, 0;
    EXPECT_TRUE(num_each_component == expected_int);

    mean_num_each_component =
        calculator_ptr->mean_num_each_component(occupation);
    expected_double << 2.0, 2.0, 0.0;
    EXPECT_TRUE(almost_equal(mean_num_each_component, expected_double));

    species_frac = calculator_ptr->species_frac(occupation);
    expected_double << 1.0, 0.0, 0.0;
    EXPECT_TRUE(almost_equal(species_frac, expected_double));
  }

  occupation[20] = 1;
  {
    num_each_component = calculator_ptr->num_each_component(occupation);
    expected_int << 20, 19, 1;
    EXPECT_TRUE(num_each_component == expected_int);

    mean_num_each_component =
        calculator_ptr->mean_num_each_component(occupation);
    expected_double << 2.0, 1.9, 0.1;
    EXPECT_TRUE(almost_equal(mean_num_each_component, expected_double));

    species_frac = calculator_ptr->species_frac(occupation);
    expected_double << 20.0 / 21.0, 0.0, 1.0 / 21.0;
    EXPECT_TRUE(almost_equal(species_frac, expected_double));
  }
}
