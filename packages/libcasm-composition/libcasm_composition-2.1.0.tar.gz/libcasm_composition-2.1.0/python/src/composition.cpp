#include <pybind11/eigen.h>
#include <pybind11/iostream.h>
#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <fstream>

// nlohmann::json binding
#define JSON_USE_IMPLICIT_CONVERSIONS 0
#include "pybind11_json/pybind11_json.hpp"

// CASM
#include "casm/casm_io/container/json_io.hh"
#include "casm/casm_io/json/InputParser_impl.hh"
#include "casm/casm_io/json/jsonParser.hh"
#include "casm/composition/CompositionCalculator.hh"
#include "casm/composition/CompositionConverter.hh"
#include "casm/composition/composition_space.hh"
#include "casm/composition/io/json/CompositionConverter_json_io.hh"

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;

/// CASM - Python binding code
namespace CASMpy {

using namespace CASM;

// TODO: rename and move to composition/io/json
jsonParser &calculator_to_json(composition::CompositionCalculator const &m,
                               jsonParser &json) {
  json = jsonParser::object();
  json["components"] = m.components();
  json["allowed_occs"] = m.allowed_occs();

  // only include vacancy names if there are any not in the defaults
  bool custom_vacancy_names = false;
  std::set<std::string> default_names = {"Va", "VA", "va"};
  for (auto const &name : m.vacancy_names()) {
    if (default_names.find(name) == default_names.end()) {
      custom_vacancy_names = true;
      break;
    }
  }
  if (custom_vacancy_names) {
    json["vacancy_names"] = m.vacancy_names();
  }
  return json;
}

}  // namespace CASMpy

PYBIND11_DECLARE_HOLDER_TYPE(T, std::shared_ptr<T>);

PYBIND11_MODULE(_composition, m) {
  using namespace CASMpy;

  m.doc() = R"pbdoc(
        libcasm.composition
        -------------------

        The libcasm.composition module is a Python interface to the composition
        classes and methods in the CASM::composition namespace of the CASM C++
        libraries. This includes:

        - Methods for constructing standard composition axes
        - Methods for converting between mol and parametric composition
        - Methods for calculating the composition of configurations,
          including sublattice compositions

    )pbdoc";

  py::class_<composition::CompositionCalculator>(m, "CompositionCalculator",
                                                 R"pbdoc(
      Calculate composition from occupation vectors

      Notes
      -----

      Occupation vectors, ``occupation``, are vectors of integer indicating which
      component is on each site in a periodic crystal, according to:

      .. code-block:: Python

          occupant_name == allowed_occs[b][occupation[site_index]],

      where:

      - allowed_occs (``list[list[str]]``): For each sublattice, a vector of
        the names of components allowed to occupy th sublattice.

        - Note: the number of sublattices, ``n_sublat == len(allowed_occs)``
        - Note: ``len(occupation) == n_sublat * volume``, ``volume`` being the
          number of unit cells in the supercell

      - the sublattice index, ``b``, associated with a particular site,
        ``site_index`` in the occupation vector, can be determined from:

        - ``b = site_index / volume``
        - ``volume = len(occupation) / len(allowed_occs)``

      - This definition is consistent with the occupation vector being organized
        in sublattice blocks:

        ::

            [sublat 0 ---> | sublat 1 ---> | .... ]

      - The supercell shape and the order of unit cells within a sublattice block
        does not matter for the purposes of CompositionCalculator.

      )pbdoc")
      .def(py::init<std::vector<std::string> const &,
                    std::vector<std::vector<std::string>> const &,
                    std::set<std::string> const &>(),
           "Construct a CompositionCalculator", py::arg("components"),
           py::arg("allowed_occs"),
           py::arg("vacancy_names") = std::set<std::string>({"Va", "VA", "va"}),
           R"pbdoc(

      Parameters
      ----------
      components : list[str]
          The requested component order in the composition vectors.
      allowed_occs : list[list[str]]
          For each sublattice, a vector of components allowed to occupy
          the sublattice.
      vacancy_names : set[str]
          Set of component names that should be recognized as vacancies.
          An exception is raised if more than one component is a vacancy.
      )pbdoc")
      .def("components", &composition::CompositionCalculator::components,
           R"pbdoc(
           list[str]: The order of components in composition vector results.
           )pbdoc")
      .def("allowed_occs", &composition::CompositionCalculator::allowed_occs,
           R"pbdoc(
           list[list[str]]: The names of allowed occupants for each sublattice.
           )pbdoc")
      .def("vacancy_names", &composition::CompositionCalculator::vacancy_names,
           R"pbdoc(
           set[str]: The names of vacancy components.
           )pbdoc")
      .def("n_sublat", &composition::CompositionCalculator::n_sublat,
           "int: The number of sublattices.")
      .def(
          "mean_num_each_component",
          [](composition::CompositionCalculator const &m,
             Eigen::VectorXi const &occupation,
             std::optional<Index> sublattice_index) {
            if (sublattice_index.has_value()) {
              return m.mean_num_each_component(occupation, *sublattice_index);
            } else {
              return m.mean_num_each_component(occupation);
            }
          },
          py::arg("occupation"), py::arg("sublattice_index") = std::nullopt,
          R"pbdoc(
          Composition as number per primitive cell

          Parameters
          ----------
          occupation : numpy.ndarray[numpy.int64[m, 1]]
              The site occupation values, as indices into the allowed occupants
              on the corresponding basis site.
          sublattice_index : Optional[int] = None
              If not None, returns the composition on the specified sublattice in
              range [0, n_sublattice).

          Returns
          -------
          comp_n: numpy.ndarray[numpy.float64[n_components, 1]]
              The composition of each component, as number per primitve cell.

          )pbdoc")
      .def(
          "num_each_component",
          [](composition::CompositionCalculator const &m,
             Eigen::VectorXi const &occupation,
             std::optional<Index> sublattice_index) {
            if (sublattice_index.has_value()) {
              return m.num_each_component(occupation, *sublattice_index);
            } else {
              return m.num_each_component(occupation);
            }
          },
          py::arg("occupation"), py::arg("sublattice_index") = std::nullopt,
          R"pbdoc(
          Composition as total number

          Parameters
          ----------
          occupation : numpy.ndarray[numpy.int64[m, 1]]
              The site occupation values, as indices into the allowed occupants
              on the corresponding basis site.
          sublattice_index : Optional[int] = None
              If not None, returns the composition on the specified sublattice in
              range [0, n_sublattice).

          Returns
          -------
          total_n: numpy.ndarray[numpy.float64[n_components, 1]]
              The total number of each component.
          )pbdoc")
      .def(
          "species_frac",
          [](composition::CompositionCalculator const &m,
             Eigen::VectorXi const &occupation,
             std::optional<Index> sublattice_index) {
            if (sublattice_index.has_value()) {
              return m.species_frac(occupation, *sublattice_index);
            } else {
              return m.species_frac(occupation);
            }
          },
          py::arg("occupation"), py::arg("sublattice_index") = std::nullopt,
          R"pbdoc(
          Composition as species fraction, with [Va] = 0.0

          Parameters
          ----------
          occupation : numpy.ndarray[numpy.int64[m, 1]]
              The site occupation values, as indices into the allowed occupants
              on the corresponding basis site.
          sublattice_index : Optional[int] = None
              If not None, returns the composition on the specified sublattice in
              range [0, n_sublattice).

          Returns
          -------
          species_frac: numpy.ndarray[numpy.float64[n_components, 1]]
              Composition as species fraction, with [Va] = 0.0.
          )pbdoc")
      .def_static(
          "from_dict",
          [](const nlohmann::json &data) {
            // print errors and warnings to sys.stdout
            py::scoped_ostream_redirect redirect;

            jsonParser json{data};
            std::vector<std::string> components;
            from_json(components, json["components"]);
            std::vector<std::vector<std::string>> allowed_occs;
            from_json(allowed_occs, json["allowed_occs"]);
            std::set<std::string> vacancy_names;
            if (json.contains("vacancy_names")) {
              from_json(vacancy_names, json["vacancy_names"]);
            } else {
              vacancy_names = std::set<std::string>({"Va", "VA", "va"});
            }
            return composition::CompositionCalculator(components, allowed_occs,
                                                      vacancy_names);
          },
          R"pbdoc(
          Construct a CompositionCalculator from a Python dict

          Parameters
          ----------
          data: dict
              A Python dict representing the CompositionCalculator.

          Returns
          -------
          calculator: CompositionCalculator
              A CompositionCalculator constructed from the dict.
          )pbdoc",
          py::arg("data"))
      .def(
          "to_dict",
          [](composition::CompositionCalculator const &m) {
            std::stringstream ss;
            jsonParser json;
            calculator_to_json(m, json);
            return static_cast<nlohmann::json>(json);
          },
          R"pbdoc(
          Represent a CompositionCalculator as a Python dict

          Returns
          -------
          data: dict
              A Python dict representing the CompositionCalculator.
          )pbdoc")
      .def("__repr__", [](composition::CompositionCalculator const &m) {
        std::stringstream ss;
        jsonParser json;
        calculator_to_json(m, json);
        ss << json;
        return ss.str();
      });

  m.def("get_occupant", &composition::get_occupant, py::arg("occupation"),
        py::arg("site_index"), py::arg("allowed_occs"),
        R"pbdoc(
    Get the name of the occupant species on a particular site

    Parameters
    ----------
    occupation : numpy.ndarray[numpy.int64[m, 1]]
        The site occupation values, as indices into the allowed occupants
        on the corresponding basis site.
    site_index : int
        Linear index into the occupation vector.
    allowed_occs : list[list[str]]
        For each sublattice, a vector of components allowed to occupy
        the sublattice.

    Returns
    -------
    occupant_name: str
        The name of the occupant species on the specified site.
    )pbdoc");

  m.def("set_occupant", &composition::set_occupant, py::arg("occupation"),
        py::arg("site_index"), py::arg("occupant_name"),
        py::arg("allowed_occs"), R"pbdoc(
    Set by name the species on a particular site

    Parameters
    ----------
    occupation : numpy.ndarray[numpy.int64[m, 1]]
        The site occupation values, as indices into the allowed occupants
        on the corresponding basis site.
    site_index : int
        Linear index into the occupation vector.
    occupant_name: str
        The name of the occupant species on the specified site.
    allowed_occs : list[list[str]]
        For each sublattice, a vector of components allowed to occupy
        the sublattice.

    )pbdoc");

  m.def("make_standard_origin_and_end_members",
        &composition::make_standard_origin_and_end_members,
        py::arg("components"), py::arg("allowed_occs"), py::arg("tol") = TOL,
        R"pbdoc(
    Make the possible standard choices of origin and end member compositions

    Given the allowed occupation on each sublattice of a crystal, this method
    constructs a list of possible choice of composition axes, specified by
    the number composition per unit cell at the origin and end members.

    The method iterates over possible choices and checks:

    1. Does the current choice of K end members span the full space?
    2. Try each of the chosen K end members as the origin, and let remaining
       define composition axes. Does this result in only positive parametric
       composition parameters?

    If (1) and (2) are satisfied, that choice of origin and end members are
    included in the results.

    Parameters
    ----------
    components : list[str]
        The requested component order in the composition vectors.
    allowed_occs : list[list[str]]
        For each sublattice, a vector of components allowed to occupy
        the sublattice.
    tol : float = :data:`~libcasm.casmglobal.TOL`
        Tolerance for comparison. Used to find composition axes such
        that the parametric composition parameters are non-negative.

    Returns
    -------
    standard_origin_and_end_members: list[numpy.ndarray[numpy.float64[n_components, n_composition_axes+1]]]
        A list of matrices representing origin and end member compositions
        for the set of standard composition axes. The composition of
        the origin is the first column of each matrix, and the subsequent columns
        are the compositions of the end members. Rows are ordered according to
        the order requested by ``components``.

        These "end member compositions" are the extreme compositions allowed
        by `allowed_occs`.

    )pbdoc");

  //
  m.def(
      "make_chemical_subsystems",
      [](std::vector<std::string> const &components,
         std::vector<std::vector<std::string>> const &allowed_occs)
          -> py::tuple {
        auto result =
            composition::make_chemical_subsystems(components, allowed_occs);

        std::vector<std::set<Index>> chemical_subsystems;
        std::vector<std::vector<std::set<Index>>> sublattice_types;
        std::vector<std::vector<Index>> sublattice_type_multiplicities;

        for (auto const &x : result) {
          chemical_subsystems.push_back(x.first);
          std::vector<std::set<Index>> _types;
          std::vector<Index> _mults;
          for (auto const &y : x.second) {
            _types.push_back(y.first);
            _mults.push_back(y.second);
          }
          sublattice_types.push_back(_types);
          sublattice_type_multiplicities.push_back(_mults);
        }

        return py::make_tuple(chemical_subsystems, sublattice_types,
                              sublattice_type_multiplicities);
      },
      py::arg("components"), py::arg("allowed_occs"), R"pbdoc(
    Find independent chemical subsystems

    The method returns the independent chemical subsystems comprising
    the overall chemical system. An independent chemical subsystem
    is a set of chemical components that share at least one sublattice.
    A "sublattice type" is a set of indices into the components vector
    specifying the components allowed on the sublattice.

    Example:

    .. code-block:: Python

        components = ["A", "B", "C", "D", "E", "F"]
        allowed_occs = [
            ["A", "B"], # -> sublattice type = {0, 1} (component indices)
            ["B", "A"], # -> sublattice type = {0, 1} (sorted)
            ["A", "C"], # -> sublattice type = {0, 2}
            ["D", "E"], # -> sublattice type = {3, 4}
            ["E", "F"]  # -> sublattice type = {4, 5}
          ]
        chemical_subsystems, sublattice_types, sublattice_type_multiplicities = make_chemical_subsystems(
            components,
            allowed_occs,
        )

        # chemical subsystem 0: {"A", "B", "C"} ->
        # - component indices: {0, 1, 2}
        # - comprised of:
        #   - sublattice type: {0, 1}, multiplicity 2
        #   - sublattice type: {0, 2}, multiplicity 1
        # chemical subsystem 1: {"D, "E", "F"}  ->
        # - component indices: {3, 4, 5}
        # - comprised of:
        #    - sublattice type: {3, 4}, multiplicity 1
        #    - sublattice type: {4, 5}, multiplicity 1
        #
        # chemical_subsystems == [
        #     set([0, 1, 2]),
        #     set([3, 4, 5]),
        # ]
        #
        # sublattice_types == [
        #     [set([0, 1]), set([0, 2])],
        #     [set([3, 4]), set([3, 5])],
        # ]
        #
        # sublattice_type_multiplicities == [
        #     [2, 1],
        #     [1, 1],
        # ]

    Parameters
    ----------
    components : list[str]
        The requested component order in the composition vectors.
    allowed_occs : list[list[str]]
        For each sublattice, a vector of components allowed to occupy
        the sublattice.

    Returns
    -------
    (chemical_subsystems, sublattice_types, sublattice_type_multiplicities):

        chemical_subsystems: list[set[int]]
            A list of sets of indices of chemical components that share at
            least one sublattice.

        sublattice_types: list[list[set[int]]
            Lists of sets of indices of chemical components allowed on a sublattice. This is organized by chemical subsystem, so ``sublattice_types[system_index][sublattice_type_index]`` is a ``set[int]`` of allowed occs on a particular type of sublattice.

        sublattice_type_multiplicities: list[list[int]]
            The multiplicity of each type of sublattice.

    )pbdoc");

  m.def("make_end_members", &composition::make_end_members,
        py::arg("components"), py::arg("allowed_occs"), R"pbdoc(
    Make end member compositions

    This method makes a column matrix of extreme integer compositions
    possible given the allowed occupation on each sublattice of a crystal.

    Parameters
    ----------
    components : list[str]
        The requested component order in the composition vectors.
    allowed_occs : list[list[str]]
        For each sublattice, a vector of components allowed to occupy
        the sublattice.

    Returns
    -------
    end_members: numpy.ndarray[numpy.float64[n_components, m]]
        A matrix whose columns are the extreme integer compositions
        possible. The number of rows will equal ``len(components)``,
        the number of columns depends on the composition space
        determined from ``allowed_occs``.

    )pbdoc");

  py::class_<composition::CompositionConverter>(m, "CompositionConverter",
                                                R"pbdoc(
      Convert between number of species per unit cell and parametric composition

      This class handles conversions of the form:

      .. math::

          \vec{n} = \vec{n}_0 + \mathbf{Q} \vec{x}

          \vec{x} = \mathbf{R}^{\mathsf{T}} (\vec{n} - \vec{n}_0)

      where:

      - :math:`\vec{n}`: The mol composition as number of each component species
        per unit cell, a vector of length :math:`s`.
      - :math:`\vec{x}`: The parametric composition, a vector of length :math:`k`,
        giving the composition along each composition axis when referenced to the
        origin composition.
      - :math:`\vec{n}_0`: The origin in composition space, a vector of length
        :math:`s`, as the number of each component species per unit cell.
      - :math:`s`: The number of component species (``n_components``).
      - :math:`k`: The number of independent composition axes (``k``).
      - :math:`Q`: Matrix of shape=(:math:`s`, :math:`k`), with columns representing
        the change in composition per unit cell along each independent composition axis.
      - :math:`R`: Matrix of shape=(:math:`s`, :math:`k`), with columns forming the
        dual-spanning basis of Q, such that
        :math:`\mathbf{R}^{\mathsf{T}}\mathbf{Q} = \mathbf{Q}^{\mathsf{T}}\mathbf{R} = \mathbf{I}`.

      The "parametric composition axes" are the columns of :math:`Q`,
      :math:`\vec{q}_i`. Due to preservation of the number of sites per
      unit cell, :math:`\sum_{i} Q_{ij} = 0` (vacancies are included as a
      component). If :math:`\sum_{i} |Q_{ij}| = 2`, the parametric composition
      axis can be said to be normalized in the sense that a unit distance along
      that axis corresponds to a change in occupation of one site per unit cell.

      Notes:

      - The term "endmember" usually refers to the extreme compositions in a
        solid solution. In the context of CompositionConverter, the term
        "end member composition" is used to mean the composition one unit
        distance along a parametric composition axis,
        :math:`\vec{n}_0 + \vec{q}_i`.
      - When printing formulas, the characters "a", "b", "c", etc. are used to
        represent the parametric compositions, :math:`x_1`, :math:`x_2`,
        :math:`x_3`, etc.
      - When referring to parametric composition axes, the characters "a", "b",
        "c", etc. are used to represent the parametric composition axes,
        :math:`\vec{q}_1`, :math:`\vec{q}_2`, :math:`\vec{q}_3`, etc.

      )pbdoc")
      .def(py::init<std::vector<std::string> const &, Eigen::MatrixXd,
                    std::set<std::string> const &>(),
           "Construct a CompositionConverter", py::arg("components"),
           py::arg("origin_and_end_members"),
           py::arg("vacancy_names") = std::set<std::string>({"Va", "VA", "va"}),
           R"pbdoc(

      Parameters
      ----------
      components : list[str]
          The requested component order in the composition vectors.
      origin_and_end_members: numpy.ndarray[numpy.float64[n_components, n_composition_axes+1]]
          A matrix representing the origin and end member compositions
          for the choice of composition axes. The composition of the origin,
          :math:`\vec{n}_0`, is the first column of each matrix, and the
          subsequent columns are the "end member compositions" one unit
          distance along a parametric composition axis,
          :math:`\vec{n}_0 + \vec{q}_i`. Rows are ordered according to
          the order requested by ``components``.
      vacancy_names : set[str]
          Set of component names that should be recognized as vacancies.
          An exception is raised if more than one component is a vacancy.
      )pbdoc")
      .def_static(
          "from_dict",
          [](const nlohmann::json &data) {
            // print errors and warnings to sys.stdout
            py::scoped_ostream_redirect redirect;

            jsonParser json{data};
            InputParser<composition::CompositionConverter> parser(json);
            std::runtime_error error_if_invalid{
                "Error constructing CompositionConverter from dict"};
            report_and_throw_if_invalid(parser, CASM::log(), error_if_invalid);
            return *parser.value;
          },
          R"pbdoc(
          Construct a CompositionConverter from a Python dict. The `Composition Axes reference <https://prisms-center.github.io/CASMcode_docs/formats/casm/clex/CompositionAxes/>`_ documents the expected format.
          )pbdoc")
      .def(
          "to_dict",
          [](composition::CompositionConverter const &m) {
            jsonParser json;
            to_json(m, json);
            return static_cast<nlohmann::json>(json);
          },
          R"pbdoc(
          Represent a CompositionConverter as a Python dict. The `Composition Axes reference <https://prisms-center.github.io/CASMcode_docs/formats/casm/clex/CompositionAxes/>`_ documents the format.
          )pbdoc")
      .def("__repr__",
           [](composition::CompositionConverter const &m) {
             std::stringstream ss;
             jsonParser json;
             to_json(m, json);
             ss << json;
             return ss.str();
           })
      .def("components", &composition::CompositionConverter::components,
           R"pbdoc(
           The order of components in mol composition vectors.
           )pbdoc")
      .def("independent_compositions",
           &composition::CompositionConverter::independent_compositions,
           R"pbdoc(
           The dimensionality of the composition space, :math:`k`. This is the number of parametric composition axes.
           )pbdoc")
      .def("axes", &composition::CompositionConverter::axes,
           R"pbdoc(
           A list ``["a", "b", ...]`` of size :math:`k`.
           )pbdoc")
      .def("origin", &composition::CompositionConverter::origin,
           R"pbdoc(
           The mol composition of the parameteric composition axes origin.
           )pbdoc")
      .def(
          "end_member", &composition::CompositionConverter::end_member,
          py::arg("i"),
          "The mol composition of the i-th parameteric composition end member.")
      .def(
          "matrixR",
          [](composition::CompositionConverter const &m) {
            return m.dparam_dmol();
          },
          R"pbdoc(
          Return the matrix :math:`R^{\mathsf{T}}`.
          )pbdoc")
      .def("matrixQ", &composition::CompositionConverter::dmol_dparam,
           R"pbdoc(
           Return the matrix  :math:`Q`.
           )pbdoc")
      .def("param_composition",
           &composition::CompositionConverter::param_composition, py::arg("n"),
           R"pbdoc(
           Convert number per unit cell, :math:`\vec{n}`, to parametric composition, :math:`\vec{x}`.
           )pbdoc")
      .def("mol_composition",
           &composition::CompositionConverter::mol_composition, py::arg("x"),
           R"pbdoc(
           Convert parametric composition, :math:`\vec{x}`, to number per unit cell, :math:`\vec{n}`.
           )pbdoc")
      .def("dparam_composition",
           &composition::CompositionConverter::dparam_composition,
           py::arg("dn"),
           R"pbdoc(
           Convert a change in number per unit cell, :math:`d\vec{n}`, to change in parametric composition, :math:`d\vec{x}`.
           )pbdoc")
      .def("dmol_composition",
           &composition::CompositionConverter::dmol_composition, py::arg("dx"),
           R"pbdoc(
           Convert a change in parametric composition, :math:`d\vec{x}`, to a change in number per unit cell, :math:`d\vec{n}`.
           )pbdoc")
      .def("param_chem_pot", &composition::CompositionConverter::param_chem_pot,
           py::arg("chem_pot"),
           R"pbdoc(
           Convert :math:`dG/dn` to :math:`dG/dx`.
           )pbdoc")
      .def("mol_formula", &composition::CompositionConverter::mol_formula,
           R"pbdoc(
           Return formula for :math:`\vec{n}` in terms of :math:`\vec{x}` (ex: \"A(a)B(1-a)\").
           )pbdoc")
      .def("param_formula", &composition::CompositionConverter::param_formula,
           R"pbdoc(
           Return formula for :math:`\vec{x}` in terms of :math:`\vec{n}` (ex: \"a(0.5+0.5A-0.5B)\").
           )pbdoc")
      .def("origin_formula", &composition::CompositionConverter::origin_formula,
           R"pbdoc(
           Return formula for the origin composition, :math:`\vec{n}_0`.
           )pbdoc")
      .def("end_member_formula",
           &composition::CompositionConverter::end_member_formula, py::arg("i"),
           R"pbdoc(
           Return formula for the i-th end member, :math:`\vec{n}_0 + \vec{q}_i`.
           )pbdoc")
      .def("param_component_formula",
           &composition::CompositionConverter::comp_formula, py::arg("i"),
           R"pbdoc(
           Return formula for the i-th parametric composition component, :math:`x_i`, in terms of :math:`\vec{n}`.
           )pbdoc")
      .def("mol_component_formula",
           &composition::CompositionConverter::comp_n_formula, py::arg("i"),
           R"pbdoc(
           Return formula for the i-th mol composition component, :math:`n_i`, in terms of :math:`\vec{x}`.
           )pbdoc")
      .def(
          "param_chem_pot_formula",
          [](composition::CompositionConverter const &m, int i,
             bool include_va) {
            if (include_va) {
              return m.param_chem_pot_formula_with_va(i);
            } else {
              return m.param_chem_pot_formula(i);
            }
          },
          py::arg("i"), py::arg("include_va") = false,
          R"pbdoc(
           Return formula for the parametric composition conjugate potential in terms
           of the chemical potentials.

           Parameters
           ----------
           i: int
               The parametric composition axis index, starting from 0.
           include_va: bool = False
               If True, include chem_pot(Va) in output. If False (default),
               assume chem_pot(Va) is 0.
           )pbdoc");

  m.def("make_composition_space", &composition::composition_space,
        py::arg("components"), py::arg("allowed_occs"),
        py::arg("vacancy_names") = std::set<std::string>({"Va", "VA", "va"}),
        py::arg("tol") = TOL,
        R"pbdoc(
      Return the species fraction space as a column vector matrix

      Parameters
      ----------
      components : list[str]
          The requested component order in the composition vectors.
      allowed_occs : list[list[str]]
          For each sublattice, a vector of components allowed to occupy the sublattice.
      vacancy_names : set[str]
          Set of component names that should be recognized as vacancies. An exception is raised if more than one component is a vacancy.
      tol : double = :data:`~libcasm.casmglobal.TOL`
          Floating point tolerance.

      Returns
      -------
      composition_space : numpy.ndarray[numpy.float64[n_components, n_composition_axes]]
          The species fraction space, as a column vector matrix. Each column corresponds to an orthogonal vector in species fraction space. Each row corresponds to a component, according to `components`.
      )pbdoc");

  m.def("make_null_composition_space", &composition::null_composition_space,
        py::arg("components"), py::arg("allowed_occs"),
        py::arg("vacancy_names") = std::set<std::string>({"Va", "VA", "va"}),
        py::arg("tol") = TOL,
        R"pbdoc(
      Return the null space of the species fraction space as a column vector matrix

      Parameters
      ----------
      components : list[str]
          The requested component order in the composition vectors.
      allowed_occs : list[list[str]]
          For each sublattice, a vector of components allowed to occupy the sublattice.
      vacancy_names : set[str]
          Set of component names that should be recognized as vacancies. An exception is raised if more than one component is a vacancy.
      tol : double = :data:`~libcasm.casmglobal.TOL`
          Floating point tolerance.

      Returns
      -------
      null_composition_space : numpy.ndarray[numpy.float64[n_components, n_composition_axes]]
          The null space of the species fraction space, as a column vector matrix. Each column corresponds to an orthogonal vector in species fraction space. Each row corresponds to a component, according to `components`.
      )pbdoc");

  m.def("make_exchange_chemical_potential",
        &composition::make_exchange_chemical_potential,
        py::arg("param_chem_pot"), py::arg("composition_converter"),
        R"pbdoc(
      Make the exchange chemical potential matrix

      Parameters
      ----------
      param_chem_pot : numpy.ndarray[numpy.float64[n_composition_axes, 1]]
          The parametric chemical potential, :math:`\vec{\tilde{\mu}} = \mathbf{Q}^{\mathsf{T}}\vec{\mu}`, which is conjugate to the parametric composition :math:`\vec{x}`.
      composition_converter : ~libcasm.composition.CompositionConverter
          A CompositionConverter instance.

      Returns
      -------
      exchange_chemical_potential : numpy.ndarray[numpy.float64[n_components, n_components]]
          The matrix, :math:`M`, with values :math:`M_{ij} = \mu_i - \mu_j`, at the given parametric chemical potential.
      )pbdoc");

  m.def(
      "pretty_json",
      [](const nlohmann::json &data) -> std::string {
        jsonParser json{data};
        std::stringstream ss;
        ss << json << std::endl;
        return ss.str();
      },
      "Pretty-print JSON to string.", py::arg("data"));

#ifdef VERSION_INFO
  m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
  m.attr("__version__") = "dev";
#endif
}
