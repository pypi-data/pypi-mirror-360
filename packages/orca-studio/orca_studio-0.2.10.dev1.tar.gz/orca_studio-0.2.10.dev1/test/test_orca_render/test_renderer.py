import marimo

__generated_with = "0.13.14"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    from pathlib import Path

    from orca_render.renderer import Renderer
    return Path, Renderer


@app.cell
def _(Path, Renderer):
    file = Path("/home/freddy/Documents/orca_studio/test/test_calculations/opt/opt.out")
    r = Renderer(file)
    return file, r


@app.cell
def _(r):
    r.show()
    return


@app.cell
def _(file, r):
    r.add_isosurface(cube_file=file.with_name("opt.mo17a.cube"), name="mo17")
    return


@app.cell
def _(r):
    r.fig
    return


@app.cell
def _(file, r):
    r.add_isosurface(cube_file=file.with_name("opt.mo24a.cube"), name="mo24")
    return


@app.cell
def _(r):
    r.show()
    return


@app.cell
def _(r):
    r.remove_isosurface("mo17")
    return


@app.cell
def _(r):
    r.show()
    return


if __name__ == "__main__":
    app.run()
