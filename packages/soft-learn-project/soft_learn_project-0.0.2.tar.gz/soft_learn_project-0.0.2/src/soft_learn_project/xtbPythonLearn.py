import os


class XtbPythonLearn():
  def __init__(self,) -> None:
    """https://xtb-python.readthedocs.io/en/latest/ase-calculator.html
    https://xtb-python.readthedocs.io/en/latest/general-api.html#single-point-calculator
    """
    super().__init__()
    pass

  def install(self):
    """https://xtb-python.readthedocs.io/en/latest/installation.html
    conda install xtb-python
    conda search xtb-python --channel conda-forge
    conda install qcelemental ase
    conda config --add channels conda-forge
    conda install cffi numpy meson ninja
    ---
    from xtb.qcschema.harness import run_qcschema # 需要
    conda install -c conda-forge QCElemental
    """
    pass

  def get_calc(self,
               directory='.',
               method='GFN2-xTB',
               **kwargs):
    """GFN0-xTB|GFN1-xTB|GFN2-xTB|GFNFF|IPEAxTB
    """
    import xtb.ase.calculator
    if not os.path.exists(directory):
      os.makedirs(name=directory,)
    calc = xtb.ase.calculator.XTB(method=method,
                                  directory=directory,
                                  **kwargs)
    return calc

  def example_1(self):
    """Keyword	Default	Description
    method	“GFN2-xTB”	Underlying method for energy and forces
    accuracy	1.0	Numerical accuracy of the calculation
    electronic_temperature	300.0	Electronic temperatur for TB methods
    max_iterations	250	Iterations for self-consistent evaluation
    solvent	“none”	GBSA implicit solvent model
    cache_api	True	Reuse generate API objects (recommended)
    """
    import ase.build
    import xtb.ase.calculator
    atoms = ase.build.molecule('H2O')
    atoms.calc = xtb.ase.calculator.XTB(method="GFN2-xTB")
    atoms.get_potential_energy()
    -137.9677758730299
    atoms.get_forces()
    return None

  def example_2(self):
    from xtb.qcschema.harness import run_qcschema
    import qcelemental as qcel
    atomic_input = qcel.models.AtomicInput(
        molecule=qcel.models.Molecule(
            symbols=["O", "H", "H"],
            geometry=[
                0.00000000000000,  0.00000000000000, -0.73578586109551,
                1.44183152868459,  0.00000000000000,  0.36789293054775,
                -1.44183152868459,  0.00000000000000,  0.36789293054775
            ],
        ),
        driver="energy",
        model={
            "method": "GFN2-xTB",
        },
        keywords={
            "accuracy": 1.0,
            "max_iterations": 50,
        },
    )

    atomic_result = run_qcschema(atomic_input)
    atomic_result.return_result
    return None
