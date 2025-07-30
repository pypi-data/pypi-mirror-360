from pathlib import Path

from orca_studio import OrcaOutput

opt_output = Path(__file__).parent / "test_calculations/opt/opt.out"
opt = OrcaOutput(opt_output)


def test_charge():
    assert opt.charge == 0, "Wrong charge"


def test_mult():
    assert opt.mult == 1, "Wrong mult"


def test_fspe():
    assert opt.fspe_eh == -56.512842645369, "Wrong FSPE"


def test_run_time():
    assert opt.run_time_h == 0.00


def test_xyz():
    xyz = "\n".join(
        [
            "4",
            "",
            "N      0.066254    0.066254    0.066254",
            "H     -0.071486   -0.071486    1.076718",
            "H     -0.071486    1.076718   -0.071486",
            "H      1.076718   -0.071486   -0.071486",
        ]
    )
    assert opt.xyz == xyz, "Wrong xyz"
