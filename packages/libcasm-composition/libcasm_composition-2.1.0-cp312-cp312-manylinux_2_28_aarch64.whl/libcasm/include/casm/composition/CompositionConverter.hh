#ifndef CASM_composition_CompositionConverter
#define CASM_composition_CompositionConverter

#include <iostream>
#include <map>
#include <set>
#include <vector>

#include "casm/global/definitions.hh"
#include "casm/global/eigen.hh"

namespace CASM {
namespace composition {

/// \brief Convert between number of species per unit cell and parametric
/// composition
///
/// \ingroup Clex
///
class CompositionConverter {
 public:
  typedef unsigned int size_type;

  /// \brief Construct a CompositionConverter
  CompositionConverter(std::vector<std::string> const &_components,
                       Eigen::VectorXd _origin, Eigen::MatrixXd _end_members,
                       std::set<std::string> const &_vacancy_names =
                           std::set<std::string>({"Va", "VA", "va"}));

  /// \brief Construct a CompositionConverter
  CompositionConverter(std::vector<std::string> const &_components,
                       Eigen::MatrixXd _origin_and_end_members,
                       std::set<std::string> const &_vacancy_names =
                           std::set<std::string>({"Va", "VA", "va"}));

  /// \brief The dimensionality of the composition space
  size_type independent_compositions() const;

  /// \brief Composition variable names: "a", "b", ...
  static std::string comp_var(size_type i);

  /// \brief The order of components in mol composition vectors
  std::vector<std::string> components() const;

  /// \brief Vector of "a", "b", ... of size `independent_compositions()`
  std::vector<std::string> axes() const;

  /// \brief The mol composition of the parameteric composition axes origin
  Eigen::VectorXd origin() const;

  /// \brief The mol composition of the parameteric composition axes end members
  Eigen::VectorXd end_member(size_type i) const;

  /// \brief Return the matrix Mij = dx_i/dn_j
  Eigen::MatrixXd dparam_dmol() const;

  /// \brief Return the matrix Mij = dn_i/dx_j
  Eigen::MatrixXd dmol_dparam() const;

  /// \brief Convert number of mol per prim, 'n' to parametric composition 'x'
  Eigen::VectorXd param_composition(Eigen::VectorXd const &n) const;

  /// \brief Convert change in number of atoms per prim, 'dn' to change in
  /// parametric composition 'dx'
  Eigen::VectorXd dparam_composition(Eigen::VectorXd const &dn) const;

  /// \brief Convert parametric composition, 'x', to number of mol per prim, 'n'
  Eigen::VectorXd mol_composition(Eigen::VectorXd const &x) const;

  /// \brief Convert change in parametric composition, 'dx', to change in number
  /// of mol per prim, 'dn'
  Eigen::VectorXd dmol_composition(Eigen::VectorXd const &dx) const;

  /// \brief Convert dG/dn to dG/dx
  Eigen::VectorXd param_chem_pot(Eigen::VectorXd const &chem_pot) const;

  /// \brief Return formula for x->n
  std::string mol_formula() const;

  /// \brief Return formula for n->x
  std::string param_formula() const;

  /// \brief Return formula for origin
  std::string origin_formula() const;

  /// \brief Return formula for end member
  std::string end_member_formula(size_type i) const;

  /// \brief Return formula for comp(i) in terms of comp_n(A), comp_n(B), ...
  std::string comp_formula(size_type i) const;

  /// \brief Return formula for comp_n(components()[i]) in terms of comp(a),
  /// comp(b), ...
  std::string comp_n_formula(size_type i) const;

  /// \brief Return formula for param_chem_pot(i) in terms of chem_pot(A),
  /// chem_pot(B), ..., assuming chem_pot(Va) == 0
  std::string param_chem_pot_formula(size_type i) const;

  /// \brief Return formula for param_chem_pot(i) in terms of chem_pot(A),
  /// chem_pot(B), ..., including chem_pot(Va)
  std::string param_chem_pot_formula_with_va(size_type i) const;

 private:
  /// \brief Return formula for param_chem_pot(i) in terms of chem_pot(A),
  /// chem_pot(B), ...
  ///
  /// Ex: param_chem_pot(a) = c0*chem_pot(A) + c1*chem_pot(B) + ...
  ///
  /// If include_va == false, Assumes chem_pot(Va) == 0
  std::string _param_chem_pot_formula(size_type i, bool include_va) const;

  /// \brief Check that origin and end member vectors have same size as the
  /// number of components
  void _check_size(Eigen::MatrixXd const &vec) const;

  /// \brief Calculate conversion matrices m_to_n and m_to_x
  void _calc_conversion_matrices();

  /// \brief Return formula for 'n'
  std::string _n_formula(Eigen::VectorXd const &vec) const;

  /// \brief List of all allowed components names in the prim, position in
  /// vector is reference
  ///  for origin and end_members
  std::vector<std::string> m_components;

  /// \brief Vector, size == m_components.size(), specifying the
  /// num_mols_per_prim of each
  ///  component at the origin in parametric composition space
  Eigen::VectorXd m_origin;

  /// \brief Column vector matrix, rows == m_components.size(), cols == rank of
  /// parametric composition space
  /// - Specifies the number mol per prim of end member in parametric
  /// composition space
  Eigen::MatrixXd m_end_members;

  /// \brief Conversion matrix: n = origin + m_to_n*x
  /// - where x is parametric composition, and n is number of mol per prim
  Eigen::MatrixXd m_to_n;

  /// \brief Conversion matrix: x = m_to_x*(n - origin)
  /// - where x is parametric composition, and n is number of mol per prim
  Eigen::MatrixXd m_to_x;

  /// \brief Component names recognized as vacancies
  std::set<std::string> m_vacancy_names;
};

/// \brief Generate CompositionConverter for standard composition axes
std::vector<CompositionConverter> make_standard_composition_converter(
    std::vector<std::string> const &components,
    std::vector<std::vector<std::string> > const &allowed_occs,
    std::set<std::string> vacancy_names = std::set<std::string>({"Va", "VA",
                                                                 "va"}),
    double tol = 1e-14);

/// \brief Pretty-print map of name/CompositionConverter pairs
void display_composition_axes(
    std::ostream &stream,
    std::map<std::string, CompositionConverter> const &map);

/// \brief Pretty-print comp in terms of comp_n
void display_comp(std::ostream &stream, CompositionConverter const &f,
                  int indent = 0);

/// \brief Pretty-print comp_n in terms of comp
void display_comp_n(std::ostream &stream, CompositionConverter const &f,
                    int indent = 0);

/// \brief Pretty-print param_chem_pot in terms of chem_pot
void display_param_chem_pot(std::ostream &stream, CompositionConverter const &f,
                            int indent = 0);

/// \brief Return the species fraction space as column vector matrix
Eigen::MatrixXd composition_space(
    std::vector<std::string> const &components,
    std::vector<std::vector<std::string> > const &allowed_occs,
    std::set<std::string> vacancy_names = std::set<std::string>({"Va", "VA",
                                                                 "va"}),
    double tol = 1e-14);

/// \brief Return the null species fraction space as column vector matrix
Eigen::MatrixXd null_composition_space(
    std::vector<std::string> const &components,
    std::vector<std::vector<std::string> > const &allowed_occs,
    std::set<std::string> vacancy_names = std::set<std::string>({"Va", "VA",
                                                                 "va"}),
    double tol = 1e-14);

/// \brief Make the exchange chemical potential matrix
Eigen::MatrixXd make_exchange_chemical_potential(
    Eigen::VectorXd param_chem_pot,
    CompositionConverter const &composition_converter);

}  // namespace composition
}  // namespace CASM

#endif
