#include <iostream>
#include <map>
#include <set>

#include "casm/global/definitions.hh"
#include "casm/misc/CASM_Eigen_math.hh"

namespace test {
using CASM::Index;

template <typename Derived>
inline bool is_column_permutation(Eigen::MatrixBase<Derived> const &A,
                                  Eigen::MatrixBase<Derived> const &B) {
  if (A.cols() != B.cols()) {
    return false;
  }
  std::set<Index> found;
  for (Index i = 0; i < A.cols(); ++i) {
    for (Index j = 0; j < B.cols(); ++j) {
      if (almost_equal(A.col(i), B.col(j))) {
        found.insert(j);
        break;
      }
    }
  }
  return found.size() == A.cols();
}

inline void print(
    std::map<std::set<Index>, Index> const &sublattice_type_multiplicity) {
  std::cout << "sublattice_type_multiplicity.size(): "
            << sublattice_type_multiplicity.size() << std::endl;
  std::cout << "sublattice_type_multiplicity: ";
  for (auto const &value : sublattice_type_multiplicity) {
    std::cout << "--" << std::endl;
    std::cout << "sublattice_type: ";
    for (auto const &component_index : value.first) {
      std::cout << component_index << " ";
    }
    std::cout << std::endl;
    std::cout << "multiplicity: " << value.second << std::endl;
  }
  std::cout << std::endl << std::endl;
}

inline void print(
    std::set<Index> const &subsystem_components,
    std::map<std::set<Index>, Index> const &sublattice_type_multiplicity) {
  std::cout << "subsystem_components: ";
  for (auto const &component_index : subsystem_components) {
    std::cout << component_index << " ";
  }
  std::cout << std::endl;

  print(sublattice_type_multiplicity);
}

}  // namespace test
