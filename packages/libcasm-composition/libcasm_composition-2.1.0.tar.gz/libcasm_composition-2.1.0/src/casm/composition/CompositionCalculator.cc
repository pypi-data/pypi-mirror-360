#include "casm/composition/CompositionCalculator.hh"

namespace CASM {
namespace composition {

/// \brief Constructor
///
/// \param _components The requested component order in the composition vectors.
/// \param _allowed_occs For each sublattice, a vector of components allowed to
///     occupy the sublattice.
/// \param _vacancy_names Set of component names that should be recognized as
///     vacancies. An error is throw if more than one component is a vacancy.
CompositionCalculator::CompositionCalculator(
    std::vector<std::string> const &_components,
    std::vector<std::vector<std::string>> const &_allowed_occs,
    std::set<std::string> const &_vacancy_names)
    : m_components(_components),
      m_occ_to_component_index_converter(
          make_occ_index_to_component_index_converter(_components,
                                                      _allowed_occs)),
      m_vacancy_allowed(false) {
  for (int i = 0; i < m_components.size(); ++i) {
    if (_vacancy_names.count(m_components[i])) {
      if (m_vacancy_allowed) {
        throw std::runtime_error(
            "Error in CompositionCalculator: components contains multiple "
            "vacancy species");
      }
      m_vacancy_allowed = true;
      m_vacancy_index = i;
    }
  }
}

/// \brief The order of components in composition vector results
std::vector<std::string> CompositionCalculator::components() const {
  return m_components;
}

/// \brief The names of allowed occupants for each sublattice
std::vector<std::vector<std::string>> CompositionCalculator::allowed_occs()
    const {
  std::vector<std::vector<std::string>> _allowed_occs;
  for (Index b = 0; b < m_occ_to_component_index_converter.size(); ++b) {
    std::vector<std::string> sublat_occs;
    for (Index occ_index = 0;
         occ_index < m_occ_to_component_index_converter[b].size();
         ++occ_index) {
      sublat_occs.push_back(
          m_components[m_occ_to_component_index_converter[b][occ_index]]);
    }
    _allowed_occs.push_back(sublat_occs);
  }
  return _allowed_occs;
}

/// \brief The names of vacancy components
std::set<std::string> CompositionCalculator::vacancy_names() const {
  std::set<std::string> _vacancy_names;
  if (m_vacancy_allowed) {
    _vacancy_names.insert(m_components[m_vacancy_index]);
  }
  return _vacancy_names;
}

/// \brief The number of sublattices
Index CompositionCalculator::n_sublat() const {
  return m_occ_to_component_index_converter.size();
}

/// \brief Returns the composition as number per primitive cell, in the order
///     of components
///
/// \param occupation A vector of integer indicating which component is on each
///     site, according to `species == allowed_occs[b][occupation[i]]`, where
///     the sublattice index, `b`, can be determined from `b = i / volume` and
///     `volume = occupation.size() / allowed_occs.size()`.
///
/// \returns The composition, as number per primitive cell, in the order of
///     `components`.
Eigen::VectorXd CompositionCalculator::mean_num_each_component(
    Eigen::VectorXi const &occupation) const {
  Index n_sites = occupation.size();
  Index n_sublat = m_occ_to_component_index_converter.size();
  Index volume = n_sites / n_sublat;
  return num_each_component(occupation).cast<double>() / volume;
}

/// \brief Returns the composition as total number, in the order of components
///
/// \param occupation A vector of integer indicating which component is on each
///     site, according to `species == allowed_occs[b][occupation[i]]`, where
///     the sublattice index, `b`, can be determined from `b = i / volume` and
///     `volume = occupation.size() / allowed_occs.size()`.
///
/// \returns The composition, as total number, in the order of `components`.
Eigen::VectorXi CompositionCalculator::num_each_component(
    Eigen::VectorXi const &occupation) const {
  Index n_sites = occupation.size();
  Index n_sublat = m_occ_to_component_index_converter.size();
  Index volume = n_sites / n_sublat;
  Index n_component = m_components.size();

  // initialize
  Eigen::VectorXi result = Eigen::VectorXi::Zero(n_component);

  // count the number of each component
  for (Index b = 0; b < n_sublat; ++b) {
    auto const &sublat_index_converter = m_occ_to_component_index_converter[b];
    Index l_init = b * volume;
    for (Index i = 0; i < volume; ++i) {
      result[sublat_index_converter[occupation[l_init + i]]] += 1;
    }
  }
  return result;
}

/// \brief Returns the composition as species fraction, with [Va] = 0.0, in
///        the order of components
///
/// \param occupation A vector of integer indicating which component is on each
///     site, according to `species == allowed_occs[b][occupation[i]]`, where
///     the sublattice index, `b`, can be determined from `b = i / volume` and
///     `volume = occupation.size() / allowed_occs.size()`.
///
/// \returns The composition, as total number, in the order of `components`.
Eigen::VectorXd CompositionCalculator::species_frac(
    Eigen::VectorXi const &occupation) const {
  Eigen::VectorXd result = this->mean_num_each_component(occupation);
  if (m_vacancy_allowed) {
    result(m_vacancy_index) = 0.0;
  }
  double sum = result.sum();
  result /= sum;
  return result;
}

/// \brief Returns the composition as number per primitive cell, in the order
///     of components, on a particular sublattice
///
/// \param occupation A vector of integer indicating which component is on each
///     site, according to `species == allowed_occs[b][occupation[i]]`, where
///     the sublattice index, `b`, can be determined from `b = i / volume` and
///     `volume = occupation.size() / allowed_occs.size()`.
///
/// \returns The composition, as number per primitive cell, in the order of
///     `components`, on a particular sublattice.
Eigen::VectorXd CompositionCalculator::mean_num_each_component(
    Eigen::VectorXi const &occupation, Index sublattice_index) const {
  Index n_sites = occupation.size();
  Index n_sublat = m_occ_to_component_index_converter.size();
  Index volume = n_sites / n_sublat;
  return num_each_component(occupation, sublattice_index).cast<double>() /
         volume;
}

/// \brief Returns the composition as total number, in the order of components,
///     on a particular sublattice
///
/// \param occupation A vector of integer indicating which component is on each
///     site, according to `species == allowed_occs[b][occupation[i]]`, where
///     the sublattice index, `b`, can be determined from `b = i / volume` and
///     `volume = occupation.size() / allowed_occs.size()`.
///
/// \returns The composition, as total number, in the order of `components`, on
///     a particular sublattice.
Eigen::VectorXi CompositionCalculator::num_each_component(
    Eigen::VectorXi const &occupation, Index sublattice_index) const {
  Index n_sites = occupation.size();
  Index n_sublat = m_occ_to_component_index_converter.size();
  Index volume = n_sites / n_sublat;
  Index n_component = m_components.size();

  // initialize
  Eigen::VectorXi result = Eigen::VectorXi::Zero(n_component);

  // count the number of each component
  Index b = sublattice_index;
  Index l_init = b * volume;
  auto const &sublat_index_converter = m_occ_to_component_index_converter[b];
  for (Index i = 0; i < volume; ++i) {
    result[sublat_index_converter[occupation[l_init + i]]] += 1;
  }
  return result;
}

/// \brief Returns the composition as species fraction, with [Va] = 0.0, in
///        the order of components, on a particular sublattice
///
/// \param occupation A vector of integer indicating which component is on each
///     site, according to `species == allowed_occs[b][occupation[i]]`, where
///     the sublattice index, `b`, can be determined from `b = i / volume` and
///     `volume = occupation.size() / allowed_occs.size()`.
///
/// \returns The composition, as total number, in the order of `components`, on
///     a particular sublattice.
Eigen::VectorXd CompositionCalculator::species_frac(
    Eigen::VectorXi const &occupation, Index sublattice_index) const {
  Eigen::VectorXd result =
      this->mean_num_each_component(occupation, sublattice_index);
  if (m_vacancy_allowed) {
    result(m_vacancy_index) = 0.0;
  }
  double sum = result.sum();
  result /= sum;
  return result;
}

/// \brief Make a lookup table for sublattice index and occupant index to
///     component index.
///
/// \param components The requested component order in composition vectors.
/// \param allowed_occs For each sublattice, a vector of components allowed to
///     occupy the sublattice.
///
/// \returns Lookup table, `converter`, satisfying:
///     component_index = converter[sublattice_index][occ_index]
///     components[component_index] == allowed_occs[sublattice_index][occ_index]
std::vector<std::vector<Index>> make_occ_index_to_component_index_converter(
    std::vector<std::string> const &components,
    std::vector<std::vector<std::string>> const &allowed_occs) {
  std::vector<std::vector<Index>> converter;
  converter.resize(allowed_occs.size());

  for (Index b = 0; b < allowed_occs.size(); ++b) {
    for (Index occ_index = 0; occ_index < allowed_occs[b].size(); ++occ_index) {
      auto const &component_name = allowed_occs[b][occ_index];
      auto it = std::find(components.begin(), components.end(), component_name);
      Index component_index = std::distance(components.begin(), it);
      converter[b].push_back(component_index);
    }
  }
  return converter;
}

/// \brief Get the name of the occupant species on a particular site
///
/// \param occupation A vector of integer indicating which component is on each
///     site, according to `species == allowed_occs[b][occupation[i]]`, where
///     the sublattice index, `b`, can be determined from `b = i / volume` and
///     `volume = occupation.size() / allowed_occs.size()`.
/// \param site_index Index into `occupation`.
/// \param allowed_occs For each sublattice, a vector of components allowed to
///     occupy the sublattice.
///
/// \returns Name of species corresponding to value of `occupation[i]`, as
///     determined from `allowed_occs`.
std::string const &get_occupant(
    Eigen::VectorXi const &occupation, Index site_index,
    std::vector<std::vector<std::string>> const &allowed_occs) {
  Index n_sites = occupation.size();
  Index n_sublat = allowed_occs.size();
  Index volume = n_sites / n_sublat;
  return allowed_occs[site_index / volume][occupation[site_index]];
}

/// \brief Set the occupation value on a particular site
///
/// \param occupation A vector of integer indicating which component is on each
///     site, according to `species == allowed_occs[b][occupation[i]]`, where
///     the sublattice index, `b`, can be determined from `b = i / volume` and
///     `volume = occupation.size() / allowed_occs.size()`.
/// \param site_index Index into `occupation`.
/// \param occupant_name The value of `occupation[site_index]` will be set to
///     specify that the species with name `occupant_name` is occupying the
///     site.
/// \param allowed_occs For each sublattice, a vector of components allowed to
///     occupy the sublattice.
void set_occupant(Eigen::VectorXi &occupation, Index site_index,
                  std::string const &occupant_name,
                  std::vector<std::vector<std::string>> const &allowed_occs) {
  Index n_sites = occupation.size();
  Index n_sublat = allowed_occs.size();
  Index volume = n_sites / n_sublat;
  Index sublattice_index = site_index / volume;
  auto const &sublat_occs = allowed_occs[sublattice_index];
  auto it = std::find(sublat_occs.begin(), sublat_occs.end(), occupant_name);
  occupation[site_index] = std::distance(sublat_occs.begin(), it);
}

}  // namespace composition
}  // namespace CASM
