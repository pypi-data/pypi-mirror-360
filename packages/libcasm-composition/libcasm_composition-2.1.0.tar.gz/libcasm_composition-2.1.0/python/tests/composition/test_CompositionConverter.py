import numpy as np

from libcasm.composition import (
    CompositionConverter,
    make_exchange_chemical_potential,
    pretty_json,
)


def test_CompositionConverter_1():
    # allowed_occs = [["A", "B"]]
    components = ["A", "B"]

    origin_and_end_members = np.array(
        [
            [0, 1],  # origin
            [1, 0],  # end member, 'a'
        ]
    ).transpose()

    comp_converter = CompositionConverter(components, origin_and_end_members)

    # composition conversions
    assert comp_converter.param_formula() == "a(0.5+0.5A-0.5B)"
    assert comp_converter.mol_formula() == "A(a)B(1-a)"

    n = origin_and_end_members[:, 0]
    x_expected = np.array([0.0])
    assert np.allclose(comp_converter.param_composition(n), x_expected)

    n = origin_and_end_members[:, 1]
    x_expected = np.array([1.0])
    assert np.allclose(comp_converter.param_composition(n), x_expected)

    n = np.array([0.5, 0.5])
    x_expected = np.array([0.5])
    assert np.allclose(comp_converter.param_composition(n), x_expected)

    n = np.array([0.25, 0.75])
    x_expected = np.array([0.25])
    assert np.allclose(comp_converter.param_composition(n), x_expected)

    # EXPECT_EQ(ss.str(), "param_chem_pot(a) = chem_pot(A) - chem_pot(B) \n");
    assert (
        comp_converter.param_chem_pot_formula(0)
        == "param_chem_pot(a) = chem_pot(A) - chem_pot(B) "
    )

    chem_pot = np.array([-2.0, 2.0])  # dG/dn_A, dG/dn_B
    param_chem_pot_expected = np.array([-4.0])  # dG/da
    param_chem_pot = comp_converter.param_chem_pot(chem_pot)
    assert len(param_chem_pot) == 1
    assert np.allclose(param_chem_pot, param_chem_pot_expected)

    chem_pot = np.array([-4.0, 0.0])  # dG/dn_A, dG/dn_B
    param_chem_pot_expected = np.array([-4.0])  # dG/da
    param_chem_pot = comp_converter.param_chem_pot(chem_pot)
    assert len(param_chem_pot) == 1
    assert np.allclose(param_chem_pot, param_chem_pot_expected)


def test_CompositionConverter_2():
    # allowed_occs = [["A", "B"], ["C", "D"]]
    components = ["A", "B", "C", "D"]

    origin_and_end_members = np.array(
        [
            [1, 0, 1, 0],  # origin
            [1, 0, 0, 1],  # end member, 'a'
            [0, 1, 1, 0],  # end member, 'b'
        ]
    ).transpose()

    comp_converter = CompositionConverter(components, origin_and_end_members)

    # composition conversions
    assert comp_converter.param_formula() == "a(0.5-0.5C+0.5D)b(0.5-0.5A+0.5B)"
    assert comp_converter.mol_formula() == "A(1-b)B(b)C(1-a)D(a)"

    n = origin_and_end_members[:, 0]
    x_expected = np.array([0.0, 0.0])
    assert np.allclose(comp_converter.param_composition(n), x_expected)

    n = origin_and_end_members[:, 1]
    x_expected = np.array([1.0, 0.0])
    assert np.allclose(comp_converter.param_composition(n), x_expected)

    n = origin_and_end_members[:, 2]
    x_expected = np.array([0.0, 1.0])
    assert np.allclose(comp_converter.param_composition(n), x_expected)

    n = np.array([0.5, 0.5, 1.0, 0.0])
    x_expected = np.array([0.0, 0.5])
    assert np.allclose(comp_converter.param_composition(n), x_expected)

    n = np.array([0.0, 1.0, 0.5, 0.5])
    x_expected = np.array([0.5, 1.0])
    assert np.allclose(comp_converter.param_composition(n), x_expected)


def test_CompositionConverter_3():
    # allowed_occs = [["A", "B"], ["B", "C"], ["C", "D"]]
    components = ["A", "B", "C", "D"]

    origin_and_end_members = np.array(
        [
            [0, 2, 1, 0],  # origin
            [1, 1, 1, 0],  # end member, 'a'
            [0, 2, 0, 1],  # end member, 'b'
            [0, 1, 2, 0],  # end member, 'c'
        ]
    ).transpose()

    comp_converter = CompositionConverter(components, origin_and_end_members)

    # composition conversions
    assert (
        comp_converter.param_formula() == "a(0.75+0.75A-0.25B-0.25C-0.25D)"
        "b(0.75-0.25A-0.25B-0.25C+0.75D)"
        "c(0.5-0.5A-0.5B+0.5C+0.5D)"
    )
    assert comp_converter.mol_formula() == "A(a)B(2-a-c)C(1-b+c)D(b)"

    n = origin_and_end_members[:, 0]
    x_expected = np.array([0.0, 0.0, 0.0])
    assert np.allclose(comp_converter.param_composition(n), x_expected)

    n = origin_and_end_members[:, 1]
    x_expected = np.array([1.0, 0.0, 0.0])
    assert np.allclose(comp_converter.param_composition(n), x_expected)

    n = origin_and_end_members[:, 2]
    x_expected = np.array([0.0, 1.0, 0.0])
    assert np.allclose(comp_converter.param_composition(n), x_expected)

    n = origin_and_end_members[:, 3]
    x_expected = np.array([0.0, 0.0, 1.0])
    assert np.allclose(comp_converter.param_composition(n), x_expected)

    n = np.array([0.5, 1.0, 1.0, 0.5])
    x_expected = np.array([0.5, 0.5, 0.5])
    assert np.allclose(comp_converter.param_composition(n), x_expected)

    n = np.array([1.0, 0.5, 0.5, 1.0])
    x_expected = np.array([1.0, 1.0, 0.5])
    assert np.allclose(comp_converter.param_composition(n), x_expected)


def test_CompositionConverter_4():
    # allowed_occs = [["Zr"], ["Zr"], ["Va", "O"], ["Va", "O"]]
    components = ["Zr", "Va", "O"]

    origin_and_end_members = np.array(
        [
            [2, 2, 0],  # origin
            [2, 0, 2],  # end member, 'a'
        ]
    ).transpose()

    comp_converter = CompositionConverter(components, origin_and_end_members)

    # composition conversions
    assert comp_converter.param_formula() == "a(0.5-0.25Va+0.25O)"
    assert comp_converter.mol_formula() == "Zr(2)Va(2-2a)O(2a)"

    n = origin_and_end_members[:, 0]
    x_expected = np.array([0.0])
    assert np.allclose(comp_converter.param_composition(n), x_expected)

    n = origin_and_end_members[:, 1]
    x_expected = np.array([1.0])
    assert np.allclose(comp_converter.param_composition(n), x_expected)

    n = np.array([2.0, 1.5, 0.5])
    x_expected = np.array([0.25])
    assert np.allclose(comp_converter.param_composition(n), x_expected)

    chem_pot = np.array(
        [0.0, 0.0, 2.0]
    )  # dG/dn_Zr=<does not apply>, dG/dn_Va=0, dG/dn_O
    param_chem_pot_expected = np.array([4.0])  # dG/da
    param_chem_pot = comp_converter.param_chem_pot(chem_pot)
    assert len(param_chem_pot) == 1
    assert np.allclose(param_chem_pot, param_chem_pot_expected)


def test_make_exchange_chemical_potential():
    # allowed_occs = [["Zr"], ["Zr"], ["Va", "O"], ["Va", "O"]]
    components = ["Zr", "Va", "O"]

    origin_and_end_members = np.array(
        [
            [2, 2, 0],  # origin
            [2, 1, 1],  # end member, 'a'
        ]
    ).transpose()

    comp_converter = CompositionConverter(components, origin_and_end_members)

    exchange_chemical_potential = make_exchange_chemical_potential(
        np.array([1.0]), comp_converter
    )
    print(exchange_chemical_potential)

    # note, row/col 1 are not allowed
    expected = np.array(
        [
            [0.0, 0.5, -0.5],
            [-0.5, 0.0, -1.0],
            [0.5, 1.0, 0.0],
        ]
    )
    assert np.allclose(exchange_chemical_potential, expected)


def test_CompositionConverter_io():
    # allowed_occs = [["A", "B"], ["B", "C"], ["C", "D"]]
    components = ["A", "B", "C", "D"]

    origin_and_end_members = np.array(
        [
            [0, 2, 1, 0],  # origin
            [1, 1, 1, 0],  # end member, 'a'
            [0, 2, 0, 1],  # end member, 'b'
            [0, 1, 2, 0],  # end member, 'c'
        ]
    ).transpose()

    f = CompositionConverter(components, origin_and_end_members)

    assert isinstance(f, CompositionConverter)

    data = f.to_dict()
    print(pretty_json(data))
    assert isinstance(data, dict)
    assert "mol_formula" in data

    f_in = CompositionConverter.from_dict(data)
    assert np.allclose(f_in.matrixQ(), f.matrixQ())
    assert "mol_formula" in data

    import io
    from contextlib import redirect_stdout

    string_io = io.StringIO()
    with redirect_stdout(string_io):
        print(f)
    out = string_io.getvalue()
    assert "mol_formula" in out
