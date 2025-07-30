#include "casm/composition/composition_space.hh"

#include "casm/casm_io/container/stream_io.hh"
#include "casm/misc/CASM_math.hh"

namespace CASM {
namespace composition {

namespace {

/// \brief Sort composition vectors by sum of squares and return as columns of
///     a matrix
Eigen::MatrixXi _sort_and_hstack(
    std::vector<Eigen::VectorXi> const &compositions) {
  // Sort according to sum of squares
  std::map<Index, std::vector<Eigen::VectorXi> > sorted_compositions;
  for (auto const &v : compositions) {
    sorted_compositions[v.squaredNorm()].push_back(v);
  }

  // Store compositions as columns an Eigen::MatrixXi
  Eigen::MatrixXi end_members;
  end_members.resize(compositions[0].size(), compositions.size());
  Index l = 0;
  auto it = sorted_compositions.rbegin();
  auto end = sorted_compositions.rend();
  for (; it != end; ++it) {
    for (auto const &el : it->second) {
      end_members.col(l) = el;
      ++l;
    }
  }
  return end_members;
}

}  // namespace

/// \brief Make the possible standard choices of origin and end member
///     compositions given the allowed occupation on each sublattice of a
///     crystal.
///
/// \param components The requested component order in the composition vectors
///     (i.e. row order in the resulting matrices).
/// \param allowed_occs For each sublattice, a vector of components allowed to
///     occupy the sublattice.
/// \param tol Tolerance for comparison. Used to find composition axes such
///     that the parametric composition parameters are non-negative.
///
/// \returns A vector of matrices representing origin and end member
/// compositions for the set of standard composition axes. The composition of
/// the origin is the first column of each matrix, and the subsequent columns
/// are the compositions of the end members. Rows are ordered according to
/// order requested by `components`.
///
/// Example input:
/// - `components = {"A", "B"}`, then the output matrices have the `"A"`
/// composition in the first row and the `"B"` composition in the second row.
/// - `allowed_occ[1] == {"A", "B", "D"}` indicates components `"A"`, `"B"`,
/// and `"D"` are allowed on the sublattice with index `1`.
///
std::vector<Eigen::MatrixXd> make_standard_origin_and_end_members(
    std::vector<std::string> const &components,
    std::vector<std::vector<std::string> > const &allowed_occs, double tol) {
  // Calculate extreme integer composition end members for given space
  Eigen::MatrixXd end_members_column_matrix =
      make_end_members(components, allowed_occs).cast<double>();

  // Eigen object to rank revealing QR decompositions of end member matrices
  Eigen::FullPivHouseholderQR<Eigen::MatrixXd> qr;

  // Calculate the rank of the space (# of composition axes = rank-1)
  Index rank_of_space = qr.compute(end_members_column_matrix).rank();
  Index n_components = end_members_column_matrix.rows();

  // Count over K-combinations of end members, for each K-combination, select
  // one as origin and construct axes from the rest
  Index K = rank_of_space;
  Index N = end_members_column_matrix.cols();  // N: total number end members
  Index ncomb = nchoosek(N, K);

  // Loop over combinations of possible end members,
  // testing for "standard" axes, by checking for each K-combination:
  // 1) does current choice of K end members span full space?
  // 2) try each of the chosen K end members as the origin, and let
  //    remaining define composition axes... does this result in only positive
  //    parametric composition parameters?
  // If (1) and (2) are satisfied, save that choice of origin and end members.
  std::vector<Eigen::MatrixXd> standard_origin_and_end_members;
  for (Index c = 0; c < ncomb; ++c) {
    // Indices of current combination is stored in 'combo' vector
    std::vector<Index> combo;
    combo = index_to_kcombination(c, K);

    // Test end member column matrix shape=(n_components x rank_of_space)
    Eigen::MatrixXd tmembers_column_matrix(n_components, rank_of_space);
    for (Index i = 0; i < K; ++i) {
      tmembers_column_matrix.col(i) = end_members_column_matrix.col(combo[i]);
    }

    // include cutoff parameter?
    // if (c > 100000 && standard_axes.size() > 0) break;

    // assure choice of origin and end members spans the full space
    if (qr.compute(tmembers_column_matrix).rank() < K) continue;

    // try each chosen end member as the origin
    for (Index origin_index = 0; origin_index < K; ++origin_index) {
      // store choice of origin (in col 0) and end members (in remaining K-1
      // cols)
      Eigen::MatrixXd test_origin_and_end_members(n_components, K);
      {
        Index end_member_index = 0;
        for (Index j = 0; j < K; ++j) {
          if (j != origin_index) {
            test_origin_and_end_members.col(1 + end_member_index) =
                tmembers_column_matrix.col(j);
            ++end_member_index;
          } else {
            test_origin_and_end_members.col(0) = tmembers_column_matrix.col(j);
          }
        }
      }

      // Check if choice of parametric composition axes results in only
      // positive parameteric composition parameters for all provided end
      // members
      if (is_positive_parametric_space(test_origin_and_end_members,
                                       end_members_column_matrix, tol)) {
        standard_origin_and_end_members.push_back(test_origin_and_end_members);
      }
    }
  }
  return standard_origin_and_end_members;
}

/// \brief Find independent chemical subsystems
///
/// \param components The requested component order in the composition vectors.
/// \param allowed_occs For each sublattice, a vector of components allowed to
///     occupy the sublattice.
///
/// \returns A map of chemical subsystem component indices to a map of
///     {sublattice types, multiplicity} comprising the chemical subsystem. An
///     independent chemical subsystem is a set of chemical components that
///     share at least one sublattice. A "sublattice type" is a set of indices
///     into the components vector specifying the components allowed on the
///     sublattice. Example:
///
///         components = ["A", "B", "C", "D", "E", "F"]
///         allowed_occs = [
///           ["A", "B"], // -> sublattice type = {0, 1} (component indices)
///           ["B", "A"], // -> sublattice type = {0, 1} (sorted)
///           ["A", "C"], // -> sublattice type = {0, 2}
///           ["D", "E"], // -> sublattice type = {3, 4}
///           ["E", "F"]  // -> sublattice type = {4, 5}
///         ] ->
///         chemical subsystem 0: {"A", "B", "C"} ->
///         - component indices: {0, 1, 2}
///         - comprised of:
///           - sublattice type: {0, 1}, multiplicity 2
///           - sublattice type: {0, 2}, multiplicity 1
///         chemical subsystem 1: {"D, "E", "F"}  ->
///         - component indices: {3, 4, 5}
///           - sublattice type: {3, 4}, multiplicity 1
///           - sublattice type: {4, 5}, multiplicity 1
///         result: {
///           {0, 1, 2}: {
///             {0, 1}: 2,
///             {0, 2}: 1
///           },
///           {3, 4, 5}: {
///             {3, 4}: 1,
///             {3, 5}: 1
///           }
///         }
///
std::map<std::set<Index>, std::map<std::set<Index>, Index> >
make_chemical_subsystems(
    std::vector<std::string> const &components,
    std::vector<std::vector<std::string> > const &allowed_occs) {
  // Find the multiplicity of unique "types" of sublattices, by converting
  // component names to indices into the `components` vector. Sublattice type
  // depends only on which occupants are allowed on the sublattice, not the
  // order they are listed.  For example:
  //   components = ["A", "B", "C"]
  //   allowed_occs = [
  //     ["A", "B"], -> "type" = [0, 1] (sorted indices into `components`)
  //     ["B", "A"], -> "type" = [0, 1]
  //     ["A", "C"]  -> "type" = [0, 2]
  //   ]

  std::map<std::set<Index>, Index> sublattice_type_multiplicity;
  for (auto const &_sublat_allowed_occs : allowed_occs) {
    std::set<Index> _sublat_component_indices;
    for (auto const &component_name : _sublat_allowed_occs) {
      auto it = std::find(components.begin(), components.end(), component_name);
      if (it == components.end()) {
        throw std::runtime_error(
            "Error in make_chemical_subsystems: components and allowed_occs "
            "are inconsistent");
      }
      _sublat_component_indices.insert(std::distance(components.begin(), it));
    }
    auto it = sublattice_type_multiplicity.find(_sublat_component_indices);
    if (it != sublattice_type_multiplicity.end()) {
      ++(it->second);
    } else {
      sublattice_type_multiplicity.emplace(_sublat_component_indices, 1);
    }
  }

  // Problem definition & setup:
  // 1. The total chemical system is a graph with chemical components as nodes.
  // 2. Each sublattice type is a fully connected subgraph.
  // 3. An independent chemical subsystem is a connected subgraph.

  // Finding independent chemical subsystems:
  // Use a "flooding algorithm" to start at one node (i.e. one chemical
  // component) and traverse edges (i.e. visit components that are in the same
  // subsystem because they are allowed to occupy a common sublattice type),
  // until all components in that subsystem are found.

  // Result:
  // key: a chemical subsystem, represented as indices of the components in the
  //     subsystem
  // value: the sublattice types comprising the chemical subsystem; as a map of
  //     sublattice types w/ multiplicities ;
  std::map<std::set<Index>, std::map<std::set<Index>, Index> > result;

  // Indices of components that have already been added to a chemical subsystem
  std::set<Index> visited;

  for (int starting_component = 0; starting_component < components.size();
       ++starting_component) {
    if (visited.count(starting_component)) continue;

    // Indices of components in the current subsystem
    std::set<Index> current_subsystem({starting_component});

    // Queue of indices of occupants to be visited for the current subsystem
    std::set<Index> to_be_visited({starting_component});

    // Will hold the sublattices comprising the current subsystem
    std::map<std::set<Index>, Index>
        sublattice_types_comprising_the_current_subsystem;

    while (!to_be_visited.empty()) {
      auto it = to_be_visited.begin();
      Index current_component = *it;
      to_be_visited.erase(it);
      if (!visited.count(current_component)) {
        visited.insert(current_component);

        // Loop over sublattice types (with multiplicity)
        for (auto const &value : sublattice_type_multiplicity) {
          auto const &_sublat_component_indices = value.first;
          auto begin = std::begin(_sublat_component_indices);
          auto end = std::end(_sublat_component_indices);

          // If `current_component` is allowed on `value` sublattice type, add
          // its allowed components to the `to_be_visited` queue and to the set
          // of connected nodes. Add the sublattice to the current subsystem
          if (_sublat_component_indices.count(current_component)) {
            current_subsystem.insert(begin, end);
            to_be_visited.insert(begin, end);
            sublattice_types_comprising_the_current_subsystem.insert(value);
          }
        }
      }
    }

    result.emplace(current_subsystem,
                   sublattice_types_comprising_the_current_subsystem);
  }

  return result;
}

/// \brief Determine the extreme integer compositions possible for a chemical
///     subsystem.
///
/// \param subsystem_components The indices of the chemical components
///     comprising a chemical subsystem. (Key from result of
///     `make_chemical_subsystems`.)
/// \param sublattice_type_multiplicity The sublattice types comprising the
///     chemical subsystem (as set of component indices allowed on the
///     sublattice type), and their multiplicities. (Value from result of
///     `make_chemical_subsystems`.)
/// \param dim Total number of allowed components in the full chemical system.
///     (i.e. `components.size()`).
///
/// \returns The extreme integer compositions possible for the subsystem, as
///    columns of a matrix.
/// \returns A matrix whose columns are the extreme integer compositions
///     possible in the chemical subspace. The number of rows will equal `dim`,
///     the number of columns depends on the composition space.
///
Eigen::MatrixXi make_subsystem_end_members(
    std::set<Index> const &subsystem_components,
    std::map<std::set<Index>, Index> const &sublattice_type_multiplicity,
    Index dim) {
  std::vector<Index> subsystem_components_vec(subsystem_components.begin(),
                                              subsystem_components.end());

  // Count over k-combinations of subsystem components, where k is number of
  // sublattices
  Index k = sublattice_type_multiplicity.size();
  Index n = subsystem_components_vec.size();
  Index ncomb = nchoosek(n, k);

  std::vector<Eigen::VectorXi> result;
  for (Index ic = 0; ic < ncomb; ++ic) {
    // Combination is stored in 'combo' vector
    std::vector<Index> tcombo = index_to_kcombination(ic, k);

    std::vector<Index> combo(tcombo.rbegin(), tcombo.rend());

    // Consider each permutation of the k-combination elements, which specifies
    // the 'direction' in which to maximize the composition
    std::vector<Index> priority;
    for (Index c : combo) priority.push_back(subsystem_components_vec[c]);

    do {
      // Maximize composition in direction specified by the current 'priority'
      Eigen::VectorXi tend(Eigen::VectorXi::Zero(dim));
      bool success = false;
      for (auto const &sublat : sublattice_type_multiplicity) {
        success = false;
        for (Index i : priority) {
          if (sublat.first.count(i)) {
            tend[i] +=
                sublat.second;  // increment by multiplicity of the sublattice
            success = true;
            break;
          }
        }
        if (!success) break;
      }

      // Keep unique extrema
      if (success) {
        auto it = std::find(result.begin(), result.end(), tend);
        if (it == result.end()) {
          result.push_back(tend);
        }
      }

    } while (next_permutation(
        priority.begin(),
        priority.end()));  // repeat the above for all permutations of priority
  }

  return _sort_and_hstack(result);
}

/// \brief Make a column matrix of extreme integer compositions possible given
///     the allowed occupation on each sublattice of a crystal.
///
/// \param components The requested component order (i.e. row order in the
///     resulting matrix) in the composition vectors.
/// \param allowed_occs For each sublattice, a vector of components allowed to
///     occupy the sublattice.
///
/// \returns A matrix whose columns are the extreme integer compositions
///     possible. The number of rows will equal `components.size()`, the number
///     of columns depends on the composition space determined from
///     `allowed_occs`.
Eigen::MatrixXi make_end_members(
    std::vector<std::string> const &components,
    std::vector<std::vector<std::string> > const &allowed_occs) {
  // 1. find chemical subsystems
  // 2. find extreme integer compositions of each subsystem
  // 3. combine all possible subsystem extreme compositions to generate
  //    extreme compositions for the overall system

  std::map<std::set<Index>, std::map<std::set<Index>, Index> >
      chemical_subsystems = make_chemical_subsystems(components, allowed_occs);

  std::vector<Eigen::VectorXi> extreme_compositions(
      1, Eigen::VectorXi::Zero(components.size()));

  for (auto const &subsystem : chemical_subsystems) {
    Eigen::MatrixXi subsystem_end_members = make_subsystem_end_members(
        subsystem.first, subsystem.second, components.size());

    // combine current subsystem extreme compositions with previous results
    std::vector<Eigen::VectorXi> tmp;
    tmp.reserve(extreme_compositions.size() * subsystem_end_members.cols());
    for (auto const &v1 : extreme_compositions) {
      for (Index j = 0; j < subsystem_end_members.cols(); ++j) {
        tmp.push_back(v1 + subsystem_end_members.col(j));
      }
    }
    std::swap(extreme_compositions, tmp);
  }

  return _sort_and_hstack(extreme_compositions);
}

/// \brief Check if choice of origin and end members results in only
///     positive parameteric composition parameters for all provided end members
///
/// \param test_origin_and_end_members Column vector matrix, with column 0
///     being the origin composition, and remaining columns begin end member
///     compositions. Expected to have same rank as end_members_column_matrix.
/// \param end_members_column_matrix Column vector matrix, whose columns are
///     the extreme integer compositions of a given space.
/// \param tol Tolerance for comparison
///
/// \returns True, if all columns of `end_members_column_matrix` have zero-
///     valued or positive parametric composition given the choice of
///     `test_origin_and_end_members`, up to specified tolerance
bool is_positive_parametric_space(
    Eigen::MatrixXd const &test_origin_and_end_members,
    Eigen::MatrixXd const &end_members_column_matrix, double tol) {
  // construct test composition axes matrix and `to_x_matrix` pseudoinverse:
  // - test_axes.col(i) = end_member(i) - origin
  // - n = origin + test_axes*x,
  // - x = to_x_matrix * (n - origin),
  //   - x=parametric composition, n=component composition
  Index K = test_origin_and_end_members.cols();
  if (K <= 1) {
    throw std::runtime_error("Error in is_positive_parametric_space: K <= 1");
  }
  Eigen::VectorXd origin = test_origin_and_end_members.col(0);
  Eigen::MatrixXd test_axes =
      test_origin_and_end_members.rightCols(K - 1).colwise() - origin;

  // from above equations for n & x,
  // to_x_matrix is left pseudoinverse of test_axes:
  // - x = to_x_matrix * test_axes * x
  //
  // I = A+ * A, (A+ is the left pseudoinverse)
  // if A has full column rank, (A.t * A) is invertible, so
  //   A+ = (A.t * A).inv * A.t
  Eigen::MatrixXd to_x_matrix =
      (test_axes.transpose() * test_axes).inverse() * test_axes.transpose();

  Eigen::VectorXd test_x;
  for (Index j = 0; j < end_members_column_matrix.cols(); ++j) {
    Eigen::VectorXd test_n = end_members_column_matrix.col(j);
    test_x = to_x_matrix * (test_n - origin);
    for (Index i = 0; i < test_x.size(); ++i) {
      if (test_x(i) < -tol) {
        return false;
      }
    }
  }
  return true;
}

}  // namespace composition
}  // namespace CASM
