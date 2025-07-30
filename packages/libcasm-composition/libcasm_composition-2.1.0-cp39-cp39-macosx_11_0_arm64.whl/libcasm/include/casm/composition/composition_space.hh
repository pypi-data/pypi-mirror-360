#ifndef CASM_composition_composition_space
#define CASM_composition_composition_space

#include <map>
#include <set>
#include <string>
#include <vector>

#include "casm/global/definitions.hh"
#include "casm/global/eigen.hh"

namespace CASM {
namespace composition {

/// \brief Make the possible standard choices of origin and end member
///     compositions given the allowed occupation on each sublattice of a
///     crystal.
std::vector<Eigen::MatrixXd> make_standard_origin_and_end_members(
    std::vector<std::string> const &components,
    std::vector<std::vector<std::string> > const &allowed_occs, double tol);

/// \brief Find independent chemical subsystems
std::map<std::set<Index>, std::map<std::set<Index>, Index> >
make_chemical_subsystems(
    std::vector<std::string> const &components,
    std::vector<std::vector<std::string> > const &allowed_occs);

/// \brief Determine the extreme integer compositions possible for a chemical
///     subsystem.
Eigen::MatrixXi make_subsystem_end_members(
    std::set<Index> const &subsystem_components,
    std::map<std::set<Index>, Index> const &sublattice_type_multiplicity,
    Index dim);

/// \brief Make a column matrix of extreme integer compositions possible given
///     the allowed occupation on each sublattice of a crystal.
Eigen::MatrixXi make_end_members(
    std::vector<std::string> const &components,
    std::vector<std::vector<std::string> > const &allowed_occs);

/// \brief Check if choice of origin and end members results in only
///     positive parameteric composition parameters for all provided end members
bool is_positive_parametric_space(
    Eigen::MatrixXd const &test_origin_and_end_members,
    Eigen::MatrixXd const &end_members_column_matrix, double tol);

}  // namespace composition
}  // namespace CASM

#endif
