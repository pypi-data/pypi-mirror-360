import sys
from typing import Optional, TextIO, Union

import numpy as np
from tabulate import tabulate

import libcasm.casmglobal

from ._composition import (
    CompositionCalculator,
    CompositionConverter,
    make_standard_origin_and_end_members,
)


def make_normalized_origin_and_end_members(
    origin_and_end_members: np.ndarray,
    tol: float = libcasm.casmglobal.TOL,
) -> np.ndarray:
    R"""Normalize compositions so that one unit along a parametric composition
    axis corresponds to a change of one site per unit cell in the occupation.

    See :class:`CompositionConverter` for details on definitions.

    Parameters
    ----------
    origin_and_end_members: np.ndarray
        A matrix with the origin, :math:`\vec{n}_0`, as the first column and
        end member compositions, :math:`\vec{n}_0 + \vec{q}_i` as the
        remaining columns.
    tol: float = :data:`~libcasm.casmglobal.TOL`
        Tolerance for comparison. Used to find composition axes such that the
        parametric composition parameters are non-negative.

    Returns
    -------
    normalized_origin_and_end_members: np.ndarray
        A modified `origin_and_end_members` matrix. The origin (first column) is not
        modified. The end member compositions (subsequent columns) are modified so
        that a unit distance along each composition axis corresponds to a change of
        one site per unit cell in the occupation.
    """
    M = origin_and_end_members
    origin = M[:, 0]
    for i in range(1, M.shape[1]):
        if not np.isclose(np.sum(M[:, i] - origin), 0.0, atol=tol):
            raise ValueError(
                "Invalid origin_and_end_members: "
                f"sum of column {i} sum does not match sum of origin (column 0)."
            )
        if np.allclose(M[:, i], M[:, 0], atol=tol):
            raise ValueError(
                "Invalid origin_and_end_members: "
                f"column {i} is the same as the origin (column 0)."
            )
        delta = M[:, i] - origin
        inc_sum = 0.0
        dec_sum = 0.0
        for dx_i in delta:
            if dx_i > tol:
                inc_sum += dx_i
            elif dx_i < -tol:
                dec_sum += dx_i

        M[:, i] = origin + delta / inc_sum
    return M


def make_standard_axes(
    allowed_occs: list[list[str]],
    components: Union[str, list[str], None] = None,
    vacancy_names: Optional[set[str]] = None,
    normalize: bool = True,
    tol: float = libcasm.casmglobal.TOL,
) -> tuple[CompositionCalculator, list[CompositionConverter]]:
    """Make standard composition axes for a set of components

    Parameters
    ----------
    allowed_occs: Optional[list[list[str]]]
        For each sublattice, a vector of components allowed to occupy the sublattice.
        The order in which components are listed on each sublattice determines the
        `occupation_index` in occupation vectors correpsonding to that component
        species.
    components: Union[str, list[str], None] = None
        The requested component order in the composition vectors. If None, the
        components are listed in the order found in `allowed_occs`. If the string
        "sorted", the components are sorted alphabetically. If a list, the components
        are listed in the order given in the list.
    vacancy_names: Optional[set[str]] = None
        Set of component names that should be recognized as vacancies. An exception is
        raised if more than one component is a vacancy.
    normalize: bool = True
        If True, normalize the composition axes so that going one unit along the
        composition axis corresponds to a change of one site per unit cell in the
        occupation. If False, one unit along the composition axis corresponds to a
        change from the origin to an extreme end member composition.
    tol: float = :data:`~libcasm.casmglobal.TOL`
        Tolerance for comparison. Used to find composition axes such that the
        parametric composition parameters are non-negative.

    Returns
    -------
    calculator: :class:`CompositionCalculator`
        A composition calculator object
    standard_axes: list[:class:`CompositionConverter`]
        List of :class:`CompositionConverter` for the standard composition axes
    """

    ## Determine defaults

    # components
    unique_components = []
    for sublattice in allowed_occs:
        for x in sublattice:
            if x not in unique_components:
                unique_components.append(x)

    invalid_value_error = ValueError(
        f"Invalid value for `components`: {components}. "
        f"May be None, or a list of "
        f"components, or 'sorted' to sort components alphabetically."
    )

    if components is None:
        components = unique_components
    elif isinstance(components, str):
        if components == "sorted":
            components = sorted(unique_components)
        else:
            raise invalid_value_error
    elif isinstance(components, list):
        if sorted(components) != sorted(unique_components):
            raise ValueError(
                f"Given `components` ({components}) do not match the components "
                f"found in `allowed_occs`: ({unique_components})"
            )
    else:
        raise invalid_value_error

    # vacancy_names
    if vacancy_names is None:
        vacancy_names = set(["va", "Va", "VA"])

    _standard_origin_and_end_members = make_standard_origin_and_end_members(
        components=components,
        allowed_occs=allowed_occs,
        tol=tol,
    )
    if normalize:
        _standard_origin_and_end_members = [
            make_normalized_origin_and_end_members(axes)
            for axes in _standard_origin_and_end_members
        ]

    calculator = CompositionCalculator(
        components=components,
        allowed_occs=allowed_occs,
        vacancy_names=vacancy_names,
    )
    standard_axes = [
        CompositionConverter(
            components=components,
            origin_and_end_members=axes,
            vacancy_names=vacancy_names,
        )
        for axes in _standard_origin_and_end_members
    ]
    return (calculator, standard_axes)


def _print_table(
    data: list[dict],
    columns: list[str],
    headers: list[str],
    out: Optional[TextIO] = None,
):
    """Print table from data in a list of dict

    Parameters
    ----------
    data: list[dict]
        Data to print
    columns: list[str]
        Keys of data to print, in order
    headers: list[str]
        Header strings
    out: Optional[stream] = None
        Output stream. Defaults to `sys.stdout`.
    """
    tabulate_in = []
    if out is None:
        out = sys.stdout
    for record in data:
        tabulate_in.append([record[col] for col in columns])
    out.write(tabulate(tabulate_in, headers=headers))
    out.write("\n")


def print_axes_table(
    possible_axes: Union[list[CompositionConverter], dict[str, CompositionConverter]],
    out: Optional[TextIO] = None,
):
    """Print a formatted summary of several composition axes

    Example output:

    .. code-block:: Python

        KEY     ORIGIN          a     GENERAL FORMULA
        ---        ---        ---     ---
          0          B          A     A(a)B(1-a)
          1          A          B     A(1-a)B(a)


    Parameters
    ----------
    possible_axes: list[CompositionConverter] | dict[str, CompositionConverter]
        A list or dict containing composition axes. If a list, the printed
        keys are the indices in the list. If a dict, the printed keys are the
        dict keys.
    out: Optional[TextIO] = None
        Output stream. Defaults to `sys.stdout`

    """
    if isinstance(possible_axes, list):
        possible_axes = {str(i): v for i, v in enumerate(possible_axes)}

    columns = ["KEY", "ORIGIN"]
    for key, value in possible_axes.items():
        for label in value.axes():
            columns.append(label)
        break
    columns.append("GENERAL FORMULA")

    data = []
    for key, value in possible_axes.items():
        _data = {
            "KEY": key,
            "ORIGIN": value.origin_formula(),
            "GENERAL FORMULA": value.mol_formula(),
        }
        for i, label in enumerate(value.axes()):
            _data[label] = value.end_member_formula(i)
        data.append(_data)

    _print_table(data=data, columns=columns, headers=columns, out=out)


def print_axes_summary(
    composition_converter: CompositionConverter,
    include_va: bool = False,
    out: Optional[TextIO] = None,
):
    """Print a formatted summary of the composition formulas for a
    particular choice of axes

    Example output:

    .. code-block:: Python

        Parametric composition:
          comp(a) = 0.5*comp_n(A)  - 0.5*(comp_n(B) - 1)

        Composition:
          comp_n(A) = 1*comp(a)
          comp_n(B) = 1 - 1*comp(a)

        Parametric chemical potentials:
          param_chem_pot(a) = chem_pot(A) - chem_pot(B)

    Parameters
    ----------
    composition_converter: CompositionConverter
        The CompositionConverter object with the composition axes
    include_va: bool = False
        If True, include "chem_pot(Va)" in the summary; If False (default) assume
        that the vacancy chemical potential is zero.
    out: Optional[TextIO] = None
        Output stream. Defaults to `sys.stdout`

    """

    if out is None:
        out = sys.stdout

    axes = composition_converter

    out.write("Parametric composition:\n")
    for i in range(axes.independent_compositions()):
        out.write(f"  {axes.param_component_formula(i)}\n")
    out.write("\n")
    out.write("Composition:\n")
    for i in range(len(axes.components())):
        out.write(f"  {axes.mol_component_formula(i)}\n")
    out.write("\n")
    out.write("Parametric chemical potentials:\n")
    for i in range(axes.independent_compositions()):
        out.write(f"  {axes.param_chem_pot_formula(i, include_va=include_va)}\n")
