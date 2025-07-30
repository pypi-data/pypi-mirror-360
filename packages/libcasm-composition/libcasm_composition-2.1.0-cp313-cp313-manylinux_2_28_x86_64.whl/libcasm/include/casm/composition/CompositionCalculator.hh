#ifndef CASM_composition_CompositionCalculator
#define CASM_composition_CompositionCalculator

#include <set>
#include <string>
#include <vector>

#include "casm/global/definitions.hh"
#include "casm/global/eigen.hh"

namespace CASM {
namespace composition {

/// \brief Calculate composition from occupation vectors
///
/// Note:
/// - Occupation vectors, `occupation`, are vectors of integer indicating which
///   component is on each site in a periodic crystal, according to:
///
///       occupant_name == allowed_occs[b][occupation[site_index]],
///
///   where:
///   - allowed_occs (`std::vector<std::vector<std::string>>`): For each
///     sublattice, a vector of the names of components allowed to occupy the
///     sublattice.
///     - Note: the number of sublattices, `n_sublat == allowed_occs.size()`
///     - Note: `occupation.size() == n_sublat * volume`, `volume` being the
///       number of unit cells in the supercell
///   - the sublattice index, `b`, associated with a particular site,
///     `site_index` in the occupation vector, can be determined from:
///     - `b = site_index / volume`
///     - `volume = occupation.size() / allowed_occs.size()`
/// - This definition is consistent with the occupation vector begin organized
///   in sublattice blocks:
///
///       [sublat 0 ---> | sublat 1 ---> | .... ]
///
/// - The supercell shape and the order of unit cells within a sublattice block
///   does not matter for the purposes of CompositionCalculator.
class CompositionCalculator {
 public:
  /// \brief Constructor
  CompositionCalculator(
      std::vector<std::string> const &_components,
      std::vector<std::vector<std::string>> const &_allowed_occs,
      std::set<std::string> const &_vacancy_names =
          std::set<std::string>({"Va", "VA", "va"}));

  /// \brief The order of components in composition vector results
  std::vector<std::string> components() const;

  /// \brief The names of allowed occupants for each sublattice
  std::vector<std::vector<std::string>> allowed_occs() const;

  /// \brief The names of vacancy components
  std::set<std::string> vacancy_names() const;

  /// \brief The number of sublattices
  Index n_sublat() const;

  /// \brief Returns the composition as number per primitive cell, in the order
  ///     of components
  Eigen::VectorXd mean_num_each_component(
      Eigen::VectorXi const &occupation) const;

  /// \brief Returns the composition as total number, in the order of components
  Eigen::VectorXi num_each_component(Eigen::VectorXi const &occupation) const;

  /// \brief Returns the composition as species fraction, with [Va] = 0.0, in
  ///     the order of components
  Eigen::VectorXd species_frac(Eigen::VectorXi const &occupation) const;

  /// \brief Returns the composition as number per primitive cell, in the order
  ///     of components, on a particular sublattice
  Eigen::VectorXd mean_num_each_component(Eigen::VectorXi const &occupation,
                                          Index sublattice_index) const;

  /// \brief Returns the composition as total number, in the order of
  ///     components, on a particular sublattice
  Eigen::VectorXi num_each_component(Eigen::VectorXi const &occupation,
                                     Index sublattice_index) const;

  /// \brief Returns the composition as species fraction, with [Va] = 0.0, in
  ///     the order of components, on a particular sublattice
  Eigen::VectorXd species_frac(Eigen::VectorXi const &occupation,
                               Index sublattice_index) const;

 private:
  // Names of components corresponding to each position in
  // the result. Must be consistent with occ_to_component_index_converter.
  // Vacancy components are detected using `xtal::is_vacancy`.
  std::vector<std::string> m_components;

  // Lookup table for sublattice index and occupant index to component index.
  std::vector<std::vector<Index>> m_occ_to_component_index_converter;

  // Whether one of the components is a vacancy, as detected by
  // `xtal::is_vacancy`
  bool m_vacancy_allowed;

  // Index in components of vacancies
  Index m_vacancy_index;
};

/// \brief Make a lookup table for sublattice index and occupant index to
///     component index.
std::vector<std::vector<Index>> make_occ_index_to_component_index_converter(
    std::vector<std::string> const &components,
    std::vector<std::vector<std::string>> const &allowed_occs);

/// \brief Get the name of the occupant species on a particular site
std::string const &get_occupant(
    Eigen::VectorXi const &occupation, Index site_index,
    std::vector<std::vector<std::string>> const &allowed_occs);

/// \brief Set the occupation value on a particular site
void set_occupant(Eigen::VectorXi &occupation, Index site_index,
                  std::string const &occupant_name,
                  std::vector<std::vector<std::string>> const &allowed_occs);

}  // namespace composition
}  // namespace CASM

#endif
