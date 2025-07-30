from libcasm.composition import (
    make_standard_axes,
    print_axes_summary,
    print_axes_table,
)


def test_make_standard_axes_1():
    allowed_occs = [["Zr"], ["Zr"], ["Va", "O"], ["Va", "O"]]
    components = ["Zr", "Va", "O"]  # None  # "sorted"
    include_va = False  # include "chem_pot(Va)" in summary?

    calculator, standard_axes = make_standard_axes(
        allowed_occs=allowed_occs,
        components=components,
        normalize=True,
    )

    # TODO: more detailed tests

    import io
    from contextlib import redirect_stdout

    string_io = io.StringIO()
    with redirect_stdout(string_io):
        print(calculator)
        print()

        print_axes_table(possible_axes=standard_axes)
        print()

        for i, axes in enumerate(standard_axes):
            print(f"--- {i} ---")
            print_axes_summary(axes, include_va=include_va)
            print()
    out = string_io.getvalue()
    assert "KEY" in out

    # Check output:
    # print(out)
    # assert False
