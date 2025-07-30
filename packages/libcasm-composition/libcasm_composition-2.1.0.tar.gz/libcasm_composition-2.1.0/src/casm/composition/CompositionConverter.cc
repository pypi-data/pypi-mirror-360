#include "casm/composition/CompositionConverter.hh"

#include <iomanip>

#include "casm/composition/composition_space.hh"
#include "casm/misc/CASM_Eigen_math.hh"

namespace CASM {
namespace composition {

/// \brief Construct a CompositionConverter
///
/// \param _components The order of species in the composition vectors.
/// \param _origin Origin for parametric composition space axess
/// \param _end_members Column vector matrix of end members for parameteric
///     composition space axes. End members are the points in composition space
///     corresponding to unit length along one parametric composition axis.
///
/// - The origin vector and columns in `_end_members` give points in
///   composition space as species number per unit cell
/// - The length of `_origin` and number of rows in `_end_members` should match
///   the size of `_components`.
///
CompositionConverter::CompositionConverter(
    std::vector<std::string> const &_components, Eigen::VectorXd _origin,
    Eigen::MatrixXd _end_members, std::set<std::string> const &_vacancy_names)
    : m_components(_components),
      m_origin(_origin),
      m_end_members(_end_members),
      m_vacancy_names(_vacancy_names) {
  _check_size(_origin);

  _check_size(_end_members);

  _calc_conversion_matrices();
}

/// \brief Construct a CompositionConverter
///
/// \param _components The order of species in the composition vectors.
/// \param _origin Origin for parametric composition space axess
/// \param _origin_and_end_members Column vector matrix of the origin
///     (first column) and end members for parameteric composition space
///     axes. End members are the points in composition space corresponding
///     to unit length along one parametric composition axis.
///
/// - The origin vector (first column) and columns in `_end_members` give points
/// in
///   composition space as species number per unit cell
/// - The number of rows in `_origin_and_end_members` should match
///   the size of `_components`.
///
CompositionConverter::CompositionConverter(
    std::vector<std::string> const &_components,
    Eigen::MatrixXd _origin_and_end_members,
    std::set<std::string> const &_vacancy_names)
    : CompositionConverter(
          _components, _origin_and_end_members.col(0),
          _origin_and_end_members.rightCols(_origin_and_end_members.cols() - 1),
          _vacancy_names) {}

/// \brief The dimensionality of the composition space
///
/// Examples:
/// - ZrOa: 1
/// - AaB(1-a): 1
/// - AaBbC(1-a-b): 2
CompositionConverter::size_type CompositionConverter::independent_compositions()
    const {
  return m_to_x.rows();
}

/// \brief Composition variable names: "a", "b", ...
std::string CompositionConverter::comp_var(size_type i) {
  return std::string(1, (char)(i + (int)'a'));
}

/// \brief The order of components in mol composition vectors
std::vector<std::string> CompositionConverter::components() const {
  return m_components;
}

/// \brief Vector of "a", "b", ... of size `independent_compositions()`
std::vector<std::string> CompositionConverter::axes() const {
  std::vector<std::string> _axes;
  for (Index i = 0; i < independent_compositions(); ++i) {
    _axes.push_back(comp_var(i));
  }
  return _axes;
}

/// \brief The mol composition of the parameteric composition axes origin
///
/// - Matches order from components()
///
Eigen::VectorXd CompositionConverter::origin() const { return m_origin; }

/// \brief The mol composition of the parameteric composition axes end members
///
/// - Matches order from components()
///
Eigen::VectorXd CompositionConverter::end_member(size_type i) const {
  if (i >= m_end_members.cols()) {
    throw std::runtime_error(
        std::string("Error: Requested end member index is too large."));
  }
  return m_end_members.col(i);
}

/// \brief Return the matrix Mij = dx_i/dn_j
Eigen::MatrixXd CompositionConverter::dparam_dmol() const { return m_to_x; }

/// \brief Return the matrix Mij = dn_i/dx_j
Eigen::MatrixXd CompositionConverter::dmol_dparam() const { return m_to_n; }

/// \brief Convert number of atoms per prim, 'n' to parametric composition 'x'
///
/// \param n mol composition, matches order from components()
///
Eigen::VectorXd CompositionConverter::param_composition(
    Eigen::VectorXd const &n) const {
  return m_to_x * (n - m_origin);
}

/// \brief Convert change in number of atoms per prim, 'dn' to change in
/// parametric composition 'dx'
///
/// \param dn mol composition, matches order from components()
///
Eigen::VectorXd CompositionConverter::dparam_composition(
    Eigen::VectorXd const &dn) const {
  return m_to_x * dn;
}

/// \brief Convert parametric composition, 'x', to number of atoms per prim, 'n'
///
/// - Matches order from components()
///
Eigen::VectorXd CompositionConverter::mol_composition(
    Eigen::VectorXd const &x) const {
  return m_origin + m_to_n * x;
}

/// \brief Convert change in parametric composition, 'dx', to change in number
/// of atoms per prim, 'dn'
///
/// - Matches order from components()
///
Eigen::VectorXd CompositionConverter::dmol_composition(
    Eigen::VectorXd const &dx) const {
  return m_to_n * dx;
}

/// \brief Convert chemical potential, 'chem_pot', to parametric chemical
/// potential, 'param_chem_pot'
///
/// Notes:
/// - To be consistent with `param_chem_pot_formula`, it is required that
///   chem_pot(Va) == 0
Eigen::VectorXd CompositionConverter::param_chem_pot(
    Eigen::VectorXd const &chem_pot) const {
  return m_to_n.transpose() * chem_pot;
}

/// \brief Return formula for x->n
std::string CompositionConverter::mol_formula() const {
  // n = origin + m_to_n * x

  std::stringstream tstr;

  // for each molecule:
  for (int i = 0; i < m_components.size(); i++) {
    bool first_char = true;

    // print mol name 'A('
    tstr << m_components[i] << "(";

    // constant term from origin
    // print 'x' if x != 0
    if (!almost_zero(m_origin(i))) {
      first_char = false;
      tstr << m_origin(i);
    }

    // terms from m_to_n columns
    for (int j = 0; j < m_to_n.cols(); j++) {
      // print nothing if x == 0
      if (almost_zero(m_to_n(i, j))) {
        continue;
      }

      // print '+' if x>0 mid-expression
      if (!first_char && m_to_n(i, j) > 0) tstr << '+';
      // print '-' if x<0
      else if (m_to_n(i, j) < 0)
        tstr << '-';
      // print absolute value of x if |x|!=1
      if (!almost_equal(std::abs(m_to_n(i, j)), 1.0))
        tstr << std::abs(m_to_n(i, j));
      // print variable ('a','b',etc...)
      tstr << comp_var(j);

      first_char = false;
    }

    // close ')'
    tstr << ")";
  }

  return tstr.str();
}

/// \brief Return formula for n->x
std::string CompositionConverter::param_formula() const {
  // x_i = m_to_x*(n - origin) = m_to_x*n - m_to_x*origin

  std::stringstream tstr;

  Eigen::VectorXd v = -m_to_x * m_origin;

  // for each independent composition:
  for (int i = 0; i < independent_compositions(); i++) {
    bool first_char = true;

    // print mol name 'a('
    tstr << comp_var(i) << "(";

    // constant term from origin
    // print 'x' if x != 0
    if (!almost_zero(v(i))) {
      first_char = false;
      tstr << v(i);
    }

    // terms from m_to_x columns
    for (int j = 0; j < m_to_x.cols(); j++) {
      double coeff = m_to_x(i, j);

      // print nothing if n == 0
      if (almost_zero(coeff)) {
        continue;
      }

      // print 'A' or '+A' if n == 1
      if (almost_zero(coeff - 1)) {
        if (!first_char) {
          tstr << '+';
        }
        tstr << m_components[j];
      }

      // print '-A' if n == -1
      else if (almost_zero(coeff + 1)) {
        tstr << '-' << m_components[j];
      }

      // print 'nA' or '+nA' if n > 0
      else if (coeff > 0) {
        if (!first_char) {
          tstr << '+';
        }
        tstr << coeff << m_components[j];
      }

      // print '-nA' if n < 0
      else {
        tstr << coeff << m_components[j];
      }

      first_char = false;
    }

    // close ')'
    tstr << ")";
  }

  return tstr.str();
}

/// \brief Return formula for comp(i) in terms of comp_n(A), comp_n(B), ...
std::string CompositionConverter::comp_formula(size_type i) const {
  // comp(i) = m_to_x(i,j)*(comp_n(j) - m_origin(j)) + ...
  if (i >= independent_compositions()) {
    throw std::runtime_error(
        std::string("Error: Requested parametric component is too large."));
  }

  std::stringstream ss;

  auto comp_x_str = [&]() { return "comp(" + comp_var(i) + ")"; };

  auto comp_n_str = [&](int j) { return "comp_n(" + m_components[j] + ")"; };

  auto delta_str = [&](int j) {
    std::stringstream tss;
    // print '(comp_n(J) - m_origin(j))' if m_origin(j) != 0
    if (!almost_zero(m_origin(j))) {
      tss << "(" << comp_n_str(j) << " - " << m_origin(j) << ")";
    }
    // print 'comp_n(J)'
    else {
      tss << comp_n_str(j);
    }
    return tss.str();
  };

  ss << comp_x_str() << " = ";
  bool first_term = true;
  for (int j = 0; j < m_to_x.cols(); ++j) {
    double coeff = m_to_x(i, j);

    // print nothing if coeff == 0
    if (almost_zero(coeff)) {
      continue;
    }

    // if coeff < 0
    if (coeff < 0) {
      if (!first_term) {
        ss << " - " << -coeff << "*" << delta_str(j);
      } else {
        ss << coeff << "*" << delta_str(j);
      }
    }

    // if coeff > 0
    else {
      if (!first_term) {
        ss << " + " << coeff << "*" << delta_str(j);
      } else {
        ss << coeff << "*" << delta_str(j);
      }
    }
    ss << " ";

    first_term = false;
  }

  return ss.str();
}

/// \brief Return formula for comp_n(component(i)) in terms of comp(a), comp(b),
/// ...
std::string CompositionConverter::comp_n_formula(size_type i) const {
  // comp_n(i) = m_origin(j) + m_to_n(i,j)*comp(j) + ...
  if (i >= m_components.size()) {
    throw std::runtime_error(
        std::string("Error: Requested component index is too large."));
  }
  std::stringstream ss;

  auto comp_x_str = [&](int j) { return "comp(" + comp_var(j) + ")"; };

  auto comp_n_str = [&](int j) { return "comp_n(" + m_components[j] + ")"; };

  ss << comp_n_str(i) << " = ";
  bool first_term = true;
  // print nothing if coeff == 0
  if (!almost_zero(m_origin(i))) {
    ss << m_origin(i);
    first_term = false;
  }

  for (int j = 0; j < m_to_n.cols(); ++j) {
    double coeff = m_to_n(i, j);

    // print nothing if coeff == 0
    if (almost_zero(coeff)) {
      continue;
    }

    // if coeff < 0
    if (coeff < 0) {
      if (!first_term) {
        ss << " - " << -coeff << "*" << comp_x_str(j);
      } else {
        ss << coeff << "*" << comp_x_str(j);
      }
    }

    // if coeff > 0
    else {
      if (!first_term) {
        ss << " + " << coeff << "*" << comp_x_str(j);
      } else {
        ss << coeff << "*" << comp_x_str(j);
      }
    }
    ss << " ";

    first_term = false;
  }

  return ss.str();
}

/// \brief Return formula for param_chem_pot(i) in terms of chem_pot(A),
/// chem_pot(B), ...
///
/// Ex: param_chem_pot(a) = c0*chem_pot(A) + c1*chem_pot(B) + ...
///
/// Assumes chem_pot(Va) == 0
std::string CompositionConverter::param_chem_pot_formula(size_type i) const {
  bool include_va = false;
  return _param_chem_pot_formula(i, include_va);
}

/// \brief Return formula for param_chem_pot(i) in terms of chem_pot(A),
/// chem_pot(B), ..., including chem_pot(Va)
///
/// Ex: param_chem_pot(a) = c0*chem_pot(A) + c1*chem_pot(B) + ...
///
std::string CompositionConverter::param_chem_pot_formula_with_va(
    size_type i) const {
  bool include_va = true;
  return _param_chem_pot_formula(i, include_va);
}

/// \brief Return formula for param_chem_pot(i) in terms of chem_pot(A),
/// chem_pot(B), ...
///
/// Ex: param_chem_pot(a) = c0*chem_pot(A) + c1*chem_pot(B) + ...
///
/// If include_va == false, Assumes chem_pot(Va) == 0
std::string CompositionConverter::_param_chem_pot_formula(
    size_type i, bool include_va) const {
  // param_chem_pot = m_to_n.transpose() * chem_pot;

  // n = m_origin + m_to_n * x
  // x = m_to_x*(n - origin)

  // dn = m_to_n * dx  ( dn_i/dx_j = m_to_n(i,j) )
  // dx = m_to_x * dn  ( dx_i/dn_j = m_to_x(i,j) )

  // defintion of chem_pot: dG = chem_pot.trans * dn
  // defintion of param_chem_pot: dG = param_chem_pot.trans * dx

  // dG = chem_pot.trans * dn = chem_pot.trans * m_to_n * dx
  // -> param_chem_pot.trans = chem_pot.trans * m_to_n
  // -> param_chem_pot = m_to_n.trans * chem_pot
  if (i >= independent_compositions()) {
    throw std::runtime_error(std::string(
        "Error: Requested parametric chemical potential index is too large."));
  }

  std::stringstream ss;

  auto print_chem_pot = [&](int j) {
    return "chem_pot(" + m_components[j] + ") ";
  };

  ss << "param_chem_pot(" << comp_var(i) << ") = ";
  Eigen::MatrixXd Mt = m_to_n.transpose();
  bool first_term = true;
  for (int j = 0; j < Mt.cols(); ++j) {
    double coeff = Mt(i, j);

    // print nothing if n == 0

    if (almost_zero(coeff) ||
        (!include_va && m_vacancy_names.count(m_components[j]))) {
      continue;
    }

    // print 'A' or '+A' if n == 1
    if (almost_zero(coeff - 1)) {
      if (!first_term) {
        ss << "+ ";
      }
      ss << print_chem_pot(j);
    }

    // print '-A' if n == -1
    else if (almost_zero(coeff + 1)) {
      if (first_term) {
        ss << "-" << print_chem_pot(j);
      } else {
        ss << "- " << print_chem_pot(j);
      }
    }

    // print 'nA' or '+nA' if n > 0
    else if (coeff > 0) {
      if (!first_term) {
        ss << "+ ";
      }
      ss << coeff << "*" << print_chem_pot(j);
    }

    // print '-nA' if n < 0
    else {
      ss << coeff << "*" << print_chem_pot(j);
    }

    first_term = false;
  }

  return ss.str();
}

/// \brief Return formula for origin
std::string CompositionConverter::origin_formula() const {
  return _n_formula(m_origin);
}

/// \brief Return formula for end member
std::string CompositionConverter::end_member_formula(size_type i) const {
  if (i >= m_end_members.cols()) {
    throw std::runtime_error(
        std::string("Error: Requested end member index is too large."));
  }
  return _n_formula(m_end_members.col(i));
}

/// \brief Check that origin and end member vectors have same size as the number
/// of components
void CompositionConverter::_check_size(Eigen::MatrixXd const &mat) const {
  if (m_components.size() != mat.rows()) {
    throw std::runtime_error(
        std::string("Error in CompositionConverter: origin or end member "
                    "vector size does not match components size."));
  }
}

/// \brief Calculate conversion matrices m_to_n and m_to_x
void CompositionConverter::_calc_conversion_matrices() {
  // calculate m_to_n and m_to_x:
  //
  // n = origin + m_to_n*x
  // x = m_to_x*(n - origin)

  // end_members.col(i) corresponds to x such that x[i] = 1, x[j!=i] = 0,
  //  -> end_members.col(i) = origin + m_to_n.col(i)

  int c = m_end_members.cols();

  m_to_n = m_end_members.leftCols(c).colwise() - m_origin;

  // x = m_to_x*(n - origin)
  //   -> x = m_to_x*(origin + m_to_n*x - origin)
  //   -> x = m_to_x*m_to_n*x

  // m_to_x is left pseudoinverse of m_to_n, which must have full column rank,
  // because it describes the composition space:
  //
  // I = A+ * A, (A+ is the left pseudoinverse)
  // if A has full column rank, (A.t * A) is invertible, so
  //   A+ = (A.t * A).inv * A.t
  m_to_x = (m_to_n.transpose() * m_to_n).inverse() * m_to_n.transpose();
}

/// \brief Return formula for 'n'
std::string CompositionConverter::_n_formula(Eigen::VectorXd const &vec) const {
  std::stringstream tstr;

  // for each molecule:
  for (int i = 0; i < vec.size(); i++) {
    // print 'A' if x == 1
    if (almost_zero(vec(i) - 1)) {
      tstr << m_components[i];
    }
    // print 'A(x)' if x != 0
    else if (!almost_zero(vec(i))) {
      tstr << m_components[i] << "(" << vec(i) << ")";
    }
  }

  return tstr.str();
}

/// \brief Generate CompositionConverter for standard composition axes
std::vector<CompositionConverter> make_standard_composition_converter(
    std::vector<std::string> const &components,
    std::vector<std::vector<std::string> > const &allowed_occs,
    std::set<std::string> vacancy_names, double tol) {
  std::vector<CompositionConverter> result;
  std::vector<Eigen::MatrixXd> standard_origin_and_end_members =
      make_standard_origin_and_end_members(components, allowed_occs, tol);
  for (auto const &M : standard_origin_and_end_members) {
    Index n = M.cols() - 1;
    result.emplace_back(components, M.col(0), M.rightCols(n), vacancy_names);
  }
  return result;
}

/// \brief Pretty-print map of name/CompositionConverter pairs
///
/// \param stream Output stream
/// \param map Map of name/CompositionConverter pairs
/// \param name Name for this set of composition axes
///
void display_composition_axes(
    std::ostream &stream,
    std::map<std::string, CompositionConverter> const &map) {
  if (map.size() == 0) {
    return;
  }

  auto comp_var = CompositionConverter::comp_var;

  stream << std::setw(10) << "KEY"
         << " ";
  stream << std::setw(10) << "ORIGIN"
         << " ";
  for (int i = 0; i < map.begin()->second.independent_compositions(); i++) {
    stream << std::setw(10) << comp_var(i) << " ";
  }
  stream << "    ";
  stream << "GENERAL FORMULA";
  stream << std::endl;

  stream << std::setw(10) << "  ---"
         << " ";
  stream << std::setw(10) << "  ---"
         << " ";
  for (int i = 0; i < map.begin()->second.independent_compositions(); i++) {
    stream << std::setw(10) << "  ---"
           << " ";
  }
  stream << "    ";
  stream << "---" << std::endl;

  for (auto it = map.cbegin(); it != map.cend(); ++it) {
    stream << std::setw(10) << it->first << " ";
    stream << std::setw(10) << it->second.origin_formula() << " ";
    for (int i = 0; i < it->second.independent_compositions(); ++i) {
      stream << std::setw(10) << it->second.end_member_formula(i) << " ";
    }
    stream << "    ";
    stream << std::setw(10) << it->second.mol_formula() << "\n";
  }
}

/// \brief Pretty-print comp in terms of comp_n
///
/// Example:
/// \code
/// comp(a) = c00*(comp_n(A) - 1) + c01*comp_n(B) + ...
/// comp(b) = c00*comp_n(A) + c01*(comp_n(B) - 2) + ...
/// ...
/// \endcode
void display_comp(std::ostream &stream, CompositionConverter const &f,
                  int indent) {
  for (int i = 0; i < f.independent_compositions(); ++i) {
    stream << std::string(indent, ' ') << f.comp_formula(i) << "\n";
  }
}

/// \brief Pretty-print comp in terms of comp_n
///
/// Example:
/// \code
/// comp_n(A) = nAo + c00*comp(a) + c01*comp(b) + ...
/// comp_n(B) = nBo + c10*comp(a) + c11*comp(b) + ...
/// ...
/// \endcode
void display_comp_n(std::ostream &stream, CompositionConverter const &f,
                    int indent) {
  for (int i = 0; i < f.components().size(); ++i) {
    stream << std::string(indent, ' ') << f.comp_n_formula(i) << "\n";
  }
}

/// \brief Pretty-print param_chem_pot in terms of chem_pot
///
/// Example:
/// \code
/// param_chem_pot(a) = c00*chem_pot(A) + c01*chem_pot(B) + ...
/// param_chem_pot(b) = c10*chem_pot(A) + c11*chem_pot(B) + ...
/// ...
/// \endcode
void display_param_chem_pot(std::ostream &stream, CompositionConverter const &f,
                            int indent) {
  for (int i = 0; i < f.independent_compositions(); ++i) {
    stream << std::string(indent, ' ') << f.param_chem_pot_formula(i) << "\n";
  }
}

namespace {

/// \brief Non-orthogonal composition space
Eigen::MatrixXd _composition_space(
    std::vector<std::string> const &components,
    std::vector<std::vector<std::string> > const &allowed_occs,
    std::set<std::string> vacancy_names, double tol) {
  bool has_Va = false;
  Index Va_index = components.size();
  for (Index j = 0; j < components.size(); ++j) {
    if (vacancy_names.count(components[j])) {
      has_Va = true;
      Va_index = j;
      break;
    }
  }

  // convert to species frac
  Eigen::MatrixXd E = make_end_members(components, allowed_occs).cast<double>();
  if (has_Va) {
    E.row(Va_index) = Eigen::VectorXd::Zero(E.cols());
  }
  for (int i = 0; i < E.cols(); i++) {
    E.col(i) /= E.col(i).sum();
  }

  // convert to species frac space
  Eigen::MatrixXd M(E.rows(), E.cols() - 1);
  for (int i = 0; i < M.cols(); ++i) {
    M.col(i) = E.col(i + 1) - E.col(0);
  }
  return M;
}

}  // namespace

/// \brief Return the species fraction space
///
/// \param components The requested component order in the composition vectors
///     (i.e. rows in the resulting matrix).
/// \param allowed_occs For each sublattice, a vector of components allowed to
///     occupy the sublattice.
/// \param vacancy_names Set of component names that should be recognized as
///     vacancies.
/// \param tol tolerance for checking rank (default 1e-14)
///
/// \returns The species fraction space, as a column vector matrix
///
/// - Each column corresponds to an orthogonal vector in species fraction space
/// - Each row corresponds to a component, according to `component`
Eigen::MatrixXd composition_space(
    std::vector<std::string> const &components,
    std::vector<std::vector<std::string> > const &allowed_occs,
    std::set<std::string> vacancy_names, double tol) {
  auto Qr = _composition_space(components, allowed_occs, vacancy_names, tol)
                .fullPivHouseholderQr();
  Qr.setThreshold(tol);
  auto Q = Qr.matrixQ();
  return Q.leftCols(Qr.rank());
}

/// \brief Return the null of the species fraction space
///
/// \param components The requested component order in the composition vectors
///     (i.e. rows in the resulting matrix).
/// \param allowed_occs For each sublattice, a vector of components allowed to
///     occupy the sublattice.
/// \param vacancy_names Set of component names that should be recognized as
///     vacancies.
/// \param tol tolerance for checking rank (default 1e-14)
///
/// \returns The null space of the species fraction space, as a column vector
///     matrix
///
/// - Each column corresponds to an orthogonal vector in atom fraction space
/// - Each row corresponds to a Molecule, ordered as from
/// BasicStructure::struc_molecule
Eigen::MatrixXd null_composition_space(
    std::vector<std::string> const &components,
    std::vector<std::vector<std::string> > const &allowed_occs,
    std::set<std::string> vacancy_names, double tol) {
  auto Qr = _composition_space(components, allowed_occs, vacancy_names, tol)
                .fullPivHouseholderQr();
  Qr.setThreshold(tol);
  auto Q = Qr.matrixQ();
  return Q.rightCols(Q.cols() - Qr.rank());
}

/// \brief Make the exchange chemical potential matrix
///
/// \param param_chem_pot The parametric chemical potential, \f$\vec{\xi}\f$,
///     which is conjugate to the parametric composition \f$x\f$, and satisfies
///     \f$ \vec{\xi}^{\mathsf{T}} \vec{x} = \vec{\mu}^{\mathsf{T}} \vec{n}\f$.
/// \param composition_converter CompositionConverter instance
///
/// \returns Matrix, \f$M\f$, with values \f$M(i,j) = \mu_i - \mu_j\f$.
///
Eigen::MatrixXd make_exchange_chemical_potential(
    Eigen::VectorXd param_chem_pot,
    CompositionConverter const &composition_converter) {
  int Ncomp = composition_converter.components().size();
  Eigen::MatrixXd exchange_chem_pot = Eigen::MatrixXd(Ncomp, Ncomp);
  for (int index_new = 0; index_new < Ncomp; ++index_new) {
    for (int index_curr = 0; index_curr < Ncomp; ++index_curr) {
      Eigen::VectorXl dn = Eigen::VectorXl::Zero(Ncomp);
      dn(index_new) += 1;
      dn(index_curr) -= 1;
      exchange_chem_pot(index_new, index_curr) =
          param_chem_pot.transpose() * composition_converter.dparam_dmol() *
          dn.cast<double>();
    }
  }
  return exchange_chem_pot;
}

}  // namespace composition
}  // namespace CASM
