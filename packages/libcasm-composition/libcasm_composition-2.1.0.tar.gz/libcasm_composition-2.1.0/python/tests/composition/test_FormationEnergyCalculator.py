import numpy as np

from libcasm.composition import FormationEnergyCalculator


def test_FormationEnergyCalculator_1():
    energy_ref = np.array(
        [
            1.0,  # Reference state 1 energy
            0.0,  # Reference state 2 energy
            2.0,  # Reference state 3 energy
        ]
    )
    comp_ref = np.array(
        [
            [0.0, 0.0],  # Reference state 1 composition
            [1.0, 0.0],  # Reference state 2 composition
            [0.0, 1.0],  # Reference state 3 composition
        ]
    ).transpose()  # <-- comps as columns

    f = FormationEnergyCalculator(
        composition_ref=comp_ref,
        energy_ref=energy_ref,
    )

    assert f.independent_compositions == 2

    x = np.array([0.0, 0.0])
    assert np.allclose(
        f.reference_energy(x),
        1.0,
    )

    x = np.array([0.5, 0.5])
    assert np.allclose(
        f.reference_energy(x),
        1.0,
    )

    assert np.allclose(
        f.reference_energy(comp_ref),
        energy_ref,
    )

    x = np.array([0.9, 0.1])
    assert np.allclose(
        f.reference_energy(x),
        0.2,
    )
    e = 0.3
    assert np.allclose(
        f.formation_energy(energy=e, composition=x),
        0.1,
    )

    X = np.array(
        [
            [0.9, 0.1],
            [0.1, 0.9],
        ]
    )
    assert np.allclose(
        f.reference_energy(X),
        np.array([0.2, 1.8]),
    )
    e = np.array([0.3, 1.7])
    assert np.allclose(
        f.formation_energy(energy=e, composition=X),
        np.array([0.1, -0.1]),
    )


def test_FormationEnergyCalculator_io():
    energy_ref = np.array(
        [
            1.0,  # Reference state 1 energy
            0.0,  # Reference state 2 energy
            2.0,  # Reference state 3 energy
        ]
    )
    comp_ref = np.array(
        [
            [0.0, 0.0],  # Reference state 1 composition
            [1.0, 0.0],  # Reference state 2 composition
            [0.0, 1.0],  # Reference state 3 composition
        ]
    ).transpose()  # <-- comps as columns

    f = FormationEnergyCalculator(
        composition_ref=comp_ref,
        energy_ref=energy_ref,
    )
    assert isinstance(f, FormationEnergyCalculator)
    assert f.independent_compositions == 2

    data = f.to_dict()
    assert isinstance(data, dict)
    assert "composition_ref" in data
    assert np.allclose(
        np.array(data["composition_ref"]).transpose(),
        comp_ref,
    )
    assert "energy_ref" in data
    assert np.allclose(
        np.array(data["energy_ref"]),
        energy_ref,
    )

    f_in = FormationEnergyCalculator.from_dict(data)
    assert np.allclose(
        f_in.composition_ref,
        f.composition_ref,
    )
    assert np.allclose(
        f_in.energy_ref,
        f.energy_ref,
    )

    import io
    from contextlib import redirect_stdout

    string_io = io.StringIO()
    with redirect_stdout(string_io):
        print(f)
    out = string_io.getvalue()
    assert "composition_ref" in out
    assert "energy_ref" in out
