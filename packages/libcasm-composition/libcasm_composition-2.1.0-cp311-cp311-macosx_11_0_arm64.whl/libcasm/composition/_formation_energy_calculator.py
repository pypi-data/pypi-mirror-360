import numpy as np

from ._composition import pretty_json


class FormationEnergyCalculator:
    R"""Calculate formation energies given a choice of reference states.

    For a :math:`k`-dimensional composition space,
    :math:`k+1` reference states are required to determine the
    parameters :math:`h_0, h_1, \dots, h_k` needed to calculate
    energy references according to:

    .. math::

        \newcommand{\config}{{\mathbb{C}}}
        e(\config_i) = h_0 + \sum_{j=1}^{k} h_i x_j(\config_i),

    where :math:`e(\config_i)` is the reference energy of configuration
    :math:`i`, and :math:`x_j(\config_i)` is the :math:`j`-th element of the
    composition of configuration :math:`i`.

    """

    def __init__(
        self,
        composition_ref: np.ndarray,
        energy_ref: np.ndarray,
    ):
        """

        .. rubric:: Constructor

        Parameters
        ----------
        composition_ref: np.ndarray[np.float[k, k+1]]
            The compositions of the :math:`k+1` reference states
            as column vectors of a shape=(k,k+1) matrix.
        energy_ref: np.ndarray[np.float[k]]
            The reference state energies, normalized per primitive cell.
        """
        if len(energy_ref.shape) != 1:
            raise ValueError("energy_ref must be a 1D array")
        if len(composition_ref.shape) != 2:
            raise ValueError("composition_ref must be a 2D array")
        k = composition_ref.shape[0]
        rank = np.linalg.matrix_rank(composition_ref)
        if not rank == k:
            raise ValueError(
                f"composition_ref must have rank equal to number of rows ({k}), "
                f"but found rank={rank}"
            )
        if not composition_ref.shape == (k, k + 1):
            raise ValueError(f"composition_ref must have shape ({k}, {k+1})")
        if not energy_ref.shape == (k + 1,):
            raise ValueError(f"energy_ref must have shape ({k+1},)")

        self.independent_compositions = k
        """int: The number of independent composition axes."""

        self.composition_ref = composition_ref
        """np.ndarray: The compositions of the :math:`k+1` reference states
        as column vectors of a shape=(k,k+1) matrix."""

        self.energy_ref = energy_ref
        """np.ndarray: The reference state energies, normalized per primitive cell, as
        a 1D array of shape=(k,)."""

        # \vec{e} = h_0 + [x_1, x_2, ..., x_k].T @ h_{1:k}
        #
        # [ e_1    ]   [ 1, ... (\vec{x}_1).T ...    ]    [ h_0 ]
        # [ e_2    ] = [ 1, ... (\vec{x}_2).T ...    ]  @ [ h_1 ]
        # [ ...    ]   [ 1,     ...                  ]    [ ... ]
        # [ e_{k+1}]   [ 1, ... (\vec{x}_{k+1}).T ...]    [ h_k ]

        X = np.hstack((np.ones((k + 1, 1)), composition_ref.transpose()))
        self.h = np.linalg.solve(X, energy_ref)
        R"""np.ndarray: The parameters :math:`h_0, h_1, \dots, h_k` needed to calculate
        energy references."""

    def reference_energy(
        self,
        composition: np.ndarray,
    ) -> np.ndarray:
        """Calculate the reference energy at a composition.

        Parameters
        ----------
        composition: np.ndarray
            The composition of one or more structures. This may be a 1d
            array of shape=(k,) representing a single structure, or a 2d array of
            shape=(k,n) representing :math:`n` structures, where :math:`k` is the
            number of independent composition axes. If a 1d array is provided, the
            result in a scalar. If a 2d array is provided, the result is a 1d array of
            shape=(n,).

        Returns
        -------
        reference_energy: np.ndarray
            The reference energy at the input composition(s).
        """
        return self.h[0] + self.h[1:] @ composition

    def formation_energy(
        self,
        composition: np.ndarray,
        energy: np.ndarray,
    ) -> np.ndarray:
        """Calculate the formation energy of a configuration.

        Parameters
        ----------
        composition: np.ndarray
            The composition of 1 or more structures. This may be a 1d array of
            shape=(k,) representing a single structure, where :math:`k` is
            the number of independent composition axes, or a 2d array of shape=(k,n)
            with the composition of :math:`n` structures as columns.
        energy: Union[float, np.ndarray]
            The energy of 1 or more structures. This may be a scalar
            with the energy of a single structure, or a 1d array of shape=(n,)
            with the energy of :math:`n` structures.

        Returns
        -------
        formation_energy: np.ndarray
            The formation energy of the configuration(s).
        """
        if isinstance(energy, float):
            if composition.shape != (self.independent_compositions,):
                raise ValueError(
                    "If energy is a scalar, composition must be a 1D array "
                    f"with shape ({self.independent_compositions},)"
                )
        else:
            if energy.shape != (self.independent_compositions,):
                raise ValueError(
                    "If energy is an array, "
                    f"it must have shape ({self.independent_compositions},)"
                )
            if composition.shape[0] != self.independent_compositions:
                raise ValueError(
                    "If energy is an array,"
                    "composition must be a 2d array with shape "
                    f"({self.independent_compositions}, n)"
                )
        return energy - self.reference_energy(composition)

    def to_dict(self):
        """Represent the FormationEnergyCalculator as a Python dict

        Returns
        -------
        data: dict
            The FormationEnergyCalculator as a Python dict. Note that the
            composition_ref is transposed to keep reference state compositions in
            a single list.

            Example:

            .. code-block:: Python

                {
                    "composition_ref": [
                        [0.0, 0.0], # Reference state 1 composition
                        [0.0, 1.0], # Reference state 2 composition
                        [1.0, 0.0], # Reference state 3 composition
                    ],
                    "energy_ref": [
                        2.0, # Reference state 1 energy
                        1.0, # Reference state 2 energy
                        0.0, # Reference state 3 energy
                    ]
                }
        """
        return {
            "composition_ref": self.composition_ref.transpose().tolist(),
            "energy_ref": self.energy_ref.tolist(),
        }

    @staticmethod
    def from_dict(data: dict):
        """Create a FormationEnergyCalculator from a Python dict

        Parameters
        ----------
        data: dict
            The FormationEnergyCalculator as a Python dict. Note that the
            composition ref is expected to be transposed to keep reference state
            compositions in a single list. See :func:`to_dict` for the expected
            format.

        Returns
        -------
        calculator: FormationEnergyCalculator
            The FormationEnergyCalculator object
        """
        return FormationEnergyCalculator(
            composition_ref=np.array(data["composition_ref"]).transpose(),
            energy_ref=np.array(data["energy_ref"]),
        )

    def __repr__(self):
        return pretty_json(self.to_dict())
