import pathlib


def make_source(dir, subdir, title, bsetname):
    return str(
        pathlib.Path(dir)
        / subdir
        / "basis_sets"
        / ("bset." + bsetname)
        / (title + "_Clexulator_" + bsetname + ".cc")
    )
