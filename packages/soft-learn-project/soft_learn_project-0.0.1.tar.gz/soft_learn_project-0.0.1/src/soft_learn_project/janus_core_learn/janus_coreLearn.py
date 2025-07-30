import janus_core.calculations.single_point
import janus_core.calculations.geom_opt
import janus_core.calculations.md
import ase
import ase.build
import matplotlib.pyplot as plt
import numpy as np
import ase.io
import janus_core.calculations.eos
import janus_core.helpers.stats
import os
import importlib.resources


class Base():
  def __init__(self,):
    self.model_mace_mp = importlib.resources.files('soft_learn_project.mace_learn.data').joinpath(
        'mace-mpa-0-medium.model')
    # --下面的以后再改
    self.model_chgnet = '/Users/wangjinlong/job/soft_learn/py_package_learn/chgnet_learn/package/chgnet-main/chgnet/pretrained/0.3.0/chgnet_0.3.0_e29f68s314m37.pth.tar'
    self.model_m3gnet = '/Users/wangjinlong/job/soft_learn/py_package_learn/matgl_learn/package/matgl-main/pretrained_models/CHGNet-MatPES-PBE-2025.2.10-2.7M-PES/model.pt'
    self.model_mace_omat = '/Users/wangjinlong/job/soft_learn/py_package_learn/mace_learn/mace-foundations/MACE-matpes-pbe-omat-ft.model'
    self.sevenn_mf_ompa = '/Users/wangjinlong/job/soft_learn/py_package_learn/sevenn_learn/package/SevenNet-main/sevenn/pretrained_potentials/SevenNet_MF_0/checkpoint_sevennet_mf_0.pth'
    pass

  def train(self, data):
    self.model.train()
    self.optimizer.zero_grad()

  def get_calc_MLIP(self, arch='mace_mp',
                    device='cpu',
                    **kwargs):
    import janus_core.helpers.mlip_calculators
    if arch == 'mace_mp':
      model = importlib.resources.files('soft_learn_project.mace_learn.data').joinpath(
          'mace-mpa-0-medium.model')
    elif arch == 'mace_omat':
      model = self.model_mace_omat
    elif arch == 'chgnet':
      model = self.model_chgnet
    elif arch == 'm3gnet':
      model = self.model_m3gnet
    elif arch == 'sevennet':
      model = self.sevenn_mf_ompa
    else:
      raise ValueError('arch not supported')
    calc = janus_core.helpers.mlip_calculators.choose_calculator(
        arch=arch,
        model=model,
        device=device,
        **kwargs
    )
    return calc

  def sp_universal(self, atoms: ase.Atoms,
                   file_prefix=None,
                   **kwargs):
    """ 给出 带计算器的原子 atoms.calc = xxx 就可以进行计算
    kwargs:
      file_prefix: str, optional 
      write_results: bool, optional  If True, the calculation results will be written to the specified file prefix.
    """
    if file_prefix is not None:
      kwargs.update({'write_results': True})
      if not os.path.exists(os.path.dirname(file_prefix)):
        os.makedirs(os.path.dirname(file_prefix), exist_ok=True)
      elif os.path.exists(file_prefix+'-results.extxyz'):
        struct = ase.io.read(file_prefix+'-results.extxyz', '-1')
        return struct

    sp = janus_core.calculations.single_point.SinglePoint(
        struct=atoms,
        file_prefix=file_prefix,
        **kwargs
    )
    sp.run()
    sturct = sp.struct
    return sturct

  def geom_opt_universal(self, atoms: ase.Atoms,
                         file_prefix=None,
                         fmax=0.05,
                         **kwargs,
                         ):
    """给出 带计算器的原子 atoms.calc = xxx 就可以进行计算
    kwargs
    1. filter_func=None, 只优化位置 或 filter_kwargs={"constant_volume": True}
    2. file_prefix='xxx/tmp', 保存优化结果, write_traj=True, write_results=True
    """
    if file_prefix is not None:
      kwargs.update({'write_traj': True, 'write_results': True})
      if not os.path.exists(os.path.dirname(file_prefix)):
        os.makedirs(os.path.dirname(file_prefix), exist_ok=True)
      elif os.path.exists(file_prefix+'-opt.extxyz'):
        struct = ase.io.read(file_prefix+'-opt.extxyz', '-1')
        return struct

    geom_opt = janus_core.calculations.geom_opt.GeomOpt(
        struct=atoms,
        fmax=fmax,
        file_prefix=file_prefix,
        **kwargs,
    )
    geom_opt.run()
    struct = geom_opt.struct
    return struct

  # ---
  def get_kwargs_arch_model(self,
                            arch="mace_mp",
                            model=None,
                            **kwargs):
    """
    model 路径: /Users/wangjinlong/job/soft_learn/py_package_learn/mace_learn/mace-foundations
    MACE-OFF23_medium.model
    MACE-OFF24_medium.model
    MACE-matpes-pbe-omat-ft.model
    MACE-matpes-r2scan-omat-ft.model
    mace-mp-0_small.model
    mace-mpa-0-medium.model
    mace-omat-0-medium.model
    """
    if arch == 'mace_mp':
      if model is None:
        kwargs.update({'model': self.model_mace_mp})
      else:
        kwargs.update({'model': model})
    kwargs.update({'arch': arch})
    return kwargs

  def sp_MLIP(self, atoms: ase.Atoms,
              arch="mace_mp",
              model=None,
              device='cpu',
              calc_kwargs={"default_dtype": 'float64'},
              **kwargs):
    """kwargs:
      model: str, optional
      file_prefix: str, optional 
      write_results: bool, optional  If True, the calculation results will be written to the specified file prefix.
    """
    kwargs = self.get_kwargs_arch_model(arch=arch, model=model, **kwargs)
    if 'file_prefix' in kwargs.keys():
      kwargs.update({'write_results': True})
      v_file_prefix = kwargs['file_prefix']
      if not os.path.exists(os.path.dirname(v_file_prefix)):
        os.makedirs(os.path.dirname(v_file_prefix), exist_ok=True)
      elif os.path.exists(v_file_prefix+'-results.extxyz'):
        struct = ase.io.read(v_file_prefix+'-results.extxyz', '-1')
        return struct

    sp = janus_core.calculations.single_point.SinglePoint(
        # struct=atoms.copy(),
        struct=atoms,
        device=device,
        calc_kwargs=calc_kwargs,
        **kwargs
    )
    sp.run()
    sturct = sp.struct
    return sturct

  def geom_opt_MLIP(self, atoms: ase.Atoms,
                    arch='mace_mp',  # chgnet, mace_mp, m3gnet, chgnet,
                    model=None,
                    calc_kwargs={"default_dtype": "float64"},
                    fmax=0.05,
                    **kwargs,
                    ):
    """kwargs
    1. filter_func=None, 只优化位置 或 filter_kwargs={"constant_volume": True}
    2. file_prefix='xxx/tmp', 保存优化结果, write_traj=True, write_results=True
    ---
    arch='chgnet', 可以不用 model 参数
    Setting `filter_kwargs = {"hydrostatic_strain": True}` allows the cell lengths to be changed, in addition to atomic positions, but cell angles remain fixed:
    ---
    Calculations can also be run at a fixed pressure and volume, by setting `filter_kwargs = {"scalar_pressure": x, "constant_volume": True}`
    """
    kwargs = self.get_kwargs_arch_model(arch=arch, model=model, **kwargs)
    if 'file_prefix' in kwargs.keys():
      kwargs.update({'write_traj': True, 'write_results': True})
      v_file_prefix = kwargs['file_prefix']
      if not os.path.exists(os.path.dirname(v_file_prefix)):
        os.makedirs(os.path.dirname(v_file_prefix), exist_ok=True)
      elif os.path.exists(v_file_prefix+'-opt.extxyz'):
        struct = ase.io.read(v_file_prefix+'-opt.extxyz', '-1')
        return struct
    geom_opt = janus_core.calculations.geom_opt.GeomOpt(
        struct=atoms,
        device='cpu',
        calc_kwargs=calc_kwargs,
        fmax=fmax,
        **kwargs,
    )

    geom_opt.run()
    return geom_opt.struct

  def sp_m3gnet(self, atoms: ase.Atoms):
    """模型路径: /Users/wangjinlong/job/soft_learn/py_package_learn/matgl_learn/package/matgl-main/pretrained_models/
    CHGNet-MPtrj-2023.12.1-2.7M-PES
    CHGNet-MPtrj-2024.2.13-11M-PES
    CHGNet-MatPES-PBE-2025.2.10-2.7M-PES
    CHGNet-MatPES-r2SCAN-2025.2.10-2.7M-PES
    M3GNet-MP-2021.2.8-PES
    M3GNet-MatPES-PBE-v2025.1-PES
    M3GNet-MatPES-r2SCAN-v2025.1-PES
    """
    sp = janus_core.calculations.single_point.SinglePoint(
        struct=atoms,
        arch="m3gnet",
        device='cpu',
        calc_kwargs={
            'model_paths': '/Users/wangjinlong/job/soft_learn/py_package_learn/matgl_learn/package/matgl-main/pretrained_models/CHGNet-MatPES-PBE-2025.2.10-2.7M-PES/model.pt',
            'default_dtype': 'float64'},
    )
    sp.run()
    return sp

  def sp_chgnet(self, atoms: ase.Atoms):
    """模型路径: /Users/wangjinlong/job/soft_learn/py_package_learn/chgnet_learn/package/chgnet-main/chgnet/pretrained/0.3.0/
    """
    sp = janus_core.calculations.single_point.SinglePoint(struct=atoms,
                                                          arch="chgnet",
                                                          device='cpu',
                                                          model='/Users/wangjinlong/job/soft_learn/py_package_learn/chgnet_learn/package/chgnet-main/chgnet/pretrained/0.3.0/chgnet_0.3.0_e29f68s314m37.pth.tar',
                                                          )
    sp.run()
    return sp

  def geom_opt_method2(self, atoms: ase.Atoms, fmax=0.05, ):
    sp_mace = janus_core.calculations.single_point.SinglePoint(
        struct=atoms,
        arch="mace_mp",
        device="cpu",
        model="/Users/wangjinlong/job/soft_learn/py_package_learn/mace_learn/mace-foundations/mace-mpa-0-medium.model",
        calc_kwargs={"default_dtype": "float64"},
        properties="energy",
    )

    geom_opt = janus_core.calculations.geom_opt.GeomOpt(
        struct=sp_mace.struct,
        fmax=fmax,
        filter_func=None,
    )
    geom_opt.run()
    return geom_opt

  def geom_opt_example(self, atoms: ase.Atoms,
                       model='/Users/wangjinlong/job/soft_learn/py_package_learn/mace_learn/mace-foundations/mace-mpa-0-medium.model',):
    """Calculations can also be run at a fixed pressure and volume, by setting `filter_kwargs = {"scalar_pressure": x, "constant_volume": True}`

    By default, both the cell lengths and angles will be optimized, in addition to the atomic positions.

    We can also set the optimizer function and filter function used, either by passing the function itself (e.g. `FIRE`) or passing the name of the ASE function (e.g. `"ExpCellFilter"`):
    """
    import ase.optimize
    geom = self.geom_opt_universal(atoms=atoms.copy(),
                                   filter_func="ExpCellFilter",
                                   filter_kwargs={"scalar_pressure": 0.05,
                                                  "constant_volume": True},
                                   optimizer=ase.optimize.FIRE,
                                   )
    # --- 不优化晶格, 只优化位置 或 filter_kwargs={"constant_volume": True}
    geom = self.geom_opt_universal(struct=atoms,
                                   filter_func=None,
                                   )
    # --- 只优化x,y方向 不优化z方向
    geom = self.geom_opt_universal(atoms.copy(),
                                   filter_func="FrechetCellFilter",  # 默认就是这个可以不设置
                                   filter_kwargs={'mask': [1, 1, 0, 0, 0, 0]},
                                   )

    pass

  def ex(self):
    """尽管janus-core只直接支持入门中列出的MLIP计算器，但是任何有效的ASE计算器都可以附加到一个结构，包括当前不受支持的MLIP计算器。
    然后可以将此结构传递给janus-core计算，该计算可以像往常一样运行。
    例如，使用（ASE内置）Lennard Jones势能计算器执行几何优化：
    """
    import ase.calculators.lj
    struct = ase.io.read("tests/data/NaCl-deformed.cif")
    struct.calc = ase.calculators.lj.LennardJones()
    geom_opt = janus_core.calculations.geom_opt.GeomOpt(
        struct=struct,
        fmax=0.001,
    )
    geom_opt.run()


class NEB():
  def __init__(self,):
    pass

  def get_neb_images(self, initial, final, nimages=7, ):
    import pymatgen.io.ase
    start = pymatgen.io.ase.AseAtomsAdaptor.get_structure(
        initial)
    end = pymatgen.io.ase.AseAtomsAdaptor.get_structure(
        final)
    images_p = start.interpolate(end_structure=end,
                                 nimages=nimages+1,
                                 pbc=False,
                                 interpolate_lattices=False,
                                 autosort_tol=0.5)
    images = [p.to_ase_atoms() for p in images_p]
    return images

  def get_neb_instance_old(self, images,
                           arch='mace_mp',
                           model="/Users/wangjinlong/job/soft_learn/py_package_learn/mace_learn/mace-foundations/20231210mace128L0_energy_epoch249model",):
    """用的是 mace
    """
    import ase.mep
    # Set calculators:
    for image in images:
      sp = janus_core.calculations.single_point.SinglePoint(
          struct=image,
          arch=arch,
          model=model,
          device='cpu',
      )
    neb_instance = ase.mep.NEB(images=images,
                               climb=True,
                               allow_shared_calculator=True)
    return neb_instance

  def get_neb_instance(self, images,
                       calc_func):
    import ase.mep
    for image in images:
      image.calc = calc_func()
    neb_instance = ase.mep.NEB(images=images,
                               climb=True,
                               allow_shared_calculator=True)
    return neb_instance

  def neb_calc(self, neb_instance, fmax=0.05,
               is_save_traj=False,
               is_save_log=False,
               logfile='-'):
    # do the neb optimize:
    import ase.optimize
    trajectory = 'neb.traj' if is_save_traj else None
    logfile = 'neb.log' if is_save_log else logfile
    opt = ase.optimize.LBFGS(neb_instance,
                             trajectory=trajectory,
                             logfile=logfile,
                             )
    opt.run(fmax=fmax)
    return neb_instance

  def neb_analysis(self, neb_instance,
                   is_plot_fig=True,):
    import ase.mep
    # view the final path
    nebtools = ase.mep.NEBTools(neb_instance.images)
    if is_plot_fig:
      # Get the calculated barrier and the energy change of the reaction.
      Ef, dE = nebtools.get_barrier()
      # Get the barrier without any interpolation between highest images.
      Ef, dE = nebtools.get_barrier(fit=False)
      # Get the actual maximum force at this point in the simulation.
      max_force = nebtools.get_fmax()
      # Create a figure like that coming from ASE-GUI.
      fig_b = nebtools.plot_band()
      # print(f"能垒Ef: {Ef}")
      # view(neb_instance.images)
    return nebtools

  def run_neb_wrapper(self, initial, final, calc_func,
                      nimages=3, fmax=0.05,
                      is_save_log=False,
                      is_save_traj=False,
                      logfile=None,
                      is_plot_fig=True,):
    images = self.get_neb_images(initial, final, nimages=nimages)
    neb_instance = self.get_neb_instance(
        images, calc_func=calc_func)
    neb_instance = self.neb_calc(neb_instance=neb_instance, fmax=fmax,
                                 is_save_log=is_save_log,
                                 is_save_traj=is_save_traj,
                                 logfile=logfile)
    nebtools = self.neb_analysis(neb_instance=neb_instance,
                                 is_plot_fig=is_plot_fig)
    Ef, dE = nebtools.get_barrier()
    return nebtools

  def generate_snapshot(self, images: list):
    """Generate a snapshot from images and return an ase atoms."""
    import pymatgen.io.ase
    import pymatgen.core
    import itertools
    image_structs = list(
        map(pymatgen.io.ase.AseAtomsAdaptor().get_structure, images))
    sites = set()
    lattice = image_structs[0].lattice
    for site in itertools.chain(*(struct for struct in image_structs)):
      sites.add(pymatgen.core.PeriodicSite(
          site.species, site.frac_coords, lattice))
    neb_path = pymatgen.core.Structure.from_sites(sorted(sites))
    return neb_path.to_ase_atoms()


class MD(Base):
  def __init__(self,):
    """/Users/wangjinlong/job/soft_learn/py_package_learn/janus_core_learn/package/janus-tutorials-main/md.ipynb
    ---
    查看帮助文档: janus md --help  显示所有的可用参数
    """
    super().__init__()
    pass

  def get_paras_mlip(self,
                     arch='mace_mp',  # chgnet, mace_mp, m3gnet, chgnet,
                     model='/Users/wangjinlong/job/soft_learn/py_package_learn/mace_learn/mace-foundations/mace-mpa-0-medium.model',
                     device='cpu',
                     calc_kwargs={"default_dtype": "float64"},
                     ):
    """
    ╭─ MLIP calculator ─────────────────────────────────────────────╮
    │ *  --arch               [mace|mace_mp|mac  MLIP architecture  │
    │                         e_off|m3gnet|chgn  to use for         │
    │                         et|alignn|sevenne  calculations.      │
    │                         t|nequip|dpa3|orb  [required]         │
    │                         |mattersim|grace]                     │
    │    --device             [cpu|cuda|mps|xpu  Device to run      │
    │                         ]                  calculations on.   │
    │                                            [default: cpu]     │
    │    --model              TEXT               MLIP model name,   │
    │                                            or path to model.  │
    │                                            [default: None]    │
    │    --model-path         TEXT               Deprecated. Please │
    │                                            use --model        │
    │                                            [default: None]    │
    │    --calc-kwargs        DICT               Keyword arguments  │
    │                                            to pass to         │
    │                                            selected           │
    │                                            calculator. Must   │
    │                                            be passed as a     │
    │                                            dictionary wrapped │
    │                                            in quotes, e.g.    │
    │                                            "{'key': value}".  │
    │                                            [default: None]    │
    ╰───────────────────────────────────────────────────────────────╯
    """
    paras = {
        "arch": arch,
        "device": device,
        "model": model,
        "calc_kwargs": calc_kwargs,
    }
    return paras

  def get_paras_calculation(self,
                            ensemble='npt',
                            steps=1000,
                            timestep=1,
                            temp=300,
                            equil_steps=0,
                            minimize=False,
                            minimize_every=-1,
                            minimize_kwargs=None,
                            remove_rot=False,
                            rescale_velocities=False,
                            rescale_every=10,
                            post_process_kwargs=None,
                            correlation_kwargs=None,
                            seed=None):
    """
    ╭─ Calculation ─────────────────────────────────────────────────╮
    │ *  --ensemble                      [nph|npt|nv  Name of       │
    │                                    e|nvt|nvt-n  thermodynamic │
    │                                    h|nvt-csvr|  ensemble.     │
    │                                    npt-mtk]     [required]    │
    │ *  --struct                        PATH         Path of       │
    │                                                 structure to  │
    │                                                 simulate.     │
    │                                                 [required]    │
    │    --steps                         INTEGER      Number of     │
    │                                                 steps in MD   │
    │                                                 simulation.   │
    │                                                 [default: 0]  │
    │    --timestep                      FLOAT        Timestep for  │
    │                                                 integrator,   │
    │                                                 in fs.        │
    │                                                 [default:     │
    │                                                 1.0]          │
    │    --temp                          FLOAT        Temperature,  │
    │                                                 in K.         │
    │                                                 [default:     │
    │                                                 300.0]        │
    │    --equil-steps                    INTEGER      Maximum       │
    │                                                 number of     │
    │                                                 steps at      │
    │                                                 which to      │
    │                                                 perform       │
    │                                                 optimization  │
    │                                                 and reset     │
    │                                                 [default: 0]  │
    │    --minimize      --no-minimi…                 Whether to    │
    │                                                 minimize      │
    │                                                 structure     │
    │                                                 during        │
    │                                                 equilibratio… │
    │                                                 [default:     │
    │                                                 no-minimize]  │
    │    --minimize_every            INTEGER          Frequency of  │
    │                                                 minimization… │
    │                                                 Default       │
    │                                                 disables      │
    │                                                 minimization  │
    │                                                 after         │
    │                                                 beginning     │
    │                                                 dynamics.     │
    │                                                 [default: -1] │
    │    --minimize_kwargs               DICT         Keyword       │
    │                                                 arguments to  │
    │                                                 pass to       │
    │                                                 optimizer.    │
    │                                                 Must be       │
    │                                                 passed as a   │
    │                                                 dictionary    │
    │                                                 wrapped in    │
    │                                                 quotes, e.g.  │
    │                                                 "{'key':      │
    │                                                 value}".      │
    │                                                 [default:     │
    │                                                 None]         │
    │    --rescale_velocities    --no-rescal…         Whether to    │
    │                                                 rescale       │
    │                                                 velocities    │
    │                                                 during        │
    │                                                 equilibratio… │
    │                                                 [default:     │
    │                                                 no-rescale-v… │
    │    --remove-rot    --no-remove…                 Whether to    │
    │                                                 remove        │
    │                                                 rotation      │
    │                                                 during        │
    │                                                 equilibratio… │
    │                                                 [default:     │
    │                                                 no-remove-ro… │
    │    --rescale_every                 INTEGER      Frequency to  │
    │                                                 rescale       │
    │                                                 velocities    │
    │                                                 during        │
    │                                                 equilibratio… │
    │                                                 [default: 10] │
    │    --post_process_kwargs           DICT         Keyword       │
    │                                                 arguments to  │
    │                                                 pass to       │
    │                                                 post-process… │
    │                                                 Must be       │
    │                                                 passed as a   │
    │                                                 dictionary    │
    │                                                 wrapped in    │
    │                                                 quotes, e.g.  │
    │                                                 "{'key':      │
    │                                                 value}".      │
    │                                                 [default:     │
    │                                                 None]         │
    │    --correlation_kwargs            DICT         Keyword       │
    │                                                 arguments to  │
    │                                                 pass to md    │
    │                                                 for           │
    │                                                 on-the-fly    │
    │                                                 correlations. │
    │                                                 Must be       │
    │                                                 passed as a   │
    │                                                 list of       │
    │                                                 dictionaries  │
    │                                                 wrapped in    │
    │                                                 quotes, e.g.  │
    │                                                 "[{'key' :    │
    │                                                 values}]".    │
    │                                                 [default:     │
    │                                                 None]         │
    │    --seed                          INTEGER      Random seed   │
    │                                                 for           │
    │                                                 numpy.random  │
    │                                                 and random    │
    │                                                 functions.    │
    │                                                 [default:     │
    │                                                 None]         │
    ╰───────────────────────────────────────────────────────────────╯
    """
    paras = {
        "ensemble": ensemble,
        "steps": steps,
        "timestep": timestep,
        "temp": temp,
        "equil_steps": equil_steps,
        "minimize": minimize,
        "minimize_every": minimize_every,
        "minimize_kwargs": minimize_kwargs,
        "remove_rot": remove_rot,
        "rescale_velocities": rescale_velocities,
        "rescale_every": rescale_every,
        "post_process_kwargs": post_process_kwargs,
        "correlation_kwargs": correlation_kwargs,
        "seed": seed,
    }
    return paras

  def get_paras_ensemble(self,
                         bulk_modulus=2.0,
                         pressure=0.0,
                         friction=0.005,
                         taut=100.0,
                         **kwargs):
    """
    ╭─ Ensemble configuration ──────────────────────────────────────╮
    │ --thermostat-time            FLOAT    Thermostat time for     │
    │                                       NPT, NPT-MTK or NVT     │
    │                                       Nosé-Hoover simulation, │
    │                                       in fs. Default is 50 fs │
    │                                       for NPT and NVT         │
    │                                       Nosé-Hoover, or 100 fs  │
    │                                       for NPT-MTK.            │
    │                                       [default: None]         │
    │ --barostat-time              FLOAT    Barostat time for NPT,  │
    │                                       NPT-MTK or NPH          │
    │                                       simulation, in fs.      │
    │                                       Default is 75 fs for    │
    │                                       NPT and NPH, or 1000 fs │
    │                                       for NPT-MTK.            │
    │                                       [default: None]         │
    │ --bulk_modulus               FLOAT    Bulk modulus for NPT or │
    │                                       NPH simulation, in GPa. │
    │                                       [default: 2.0]          │
    │ --pressure                   FLOAT    Pressure for NPT or NPH │
    │                                       simulation, in GPa.     │
    │                                       [default: 0.0]          │
    │ --friction                   FLOAT    Friction coefficient    │
    │                                       for NVT simulation, in  │
    │                                       fs^-1.                  │
    │                                       [default: 0.005]        │
    │ --taut                       FLOAT    Temperature coupling    │
    │                                       time constant for NVT   │
    │                                       CSVR simulation, in fs. │
    │                                       [default: 100.0]        │
    │ --thermostat_chain           INTEGER  Number of variables in  │
    │                                       thermostat chain for    │
    │                                       NPT MTK simulation.     │
    │                                       [default: 3]            │
    │ --barostat_chain             INTEGER  Number of variables in  │
    │                                       barostat chain for NPT  │
    │                                       MTK simulation.         │
    │                                       [default: 3]            │
    │ --thermostat_substeps        INTEGER  Number of sub-steps in  │
    │                                       thermostat integration  │
    │                                       for NPT MTK simulation. │
    │                                       [default: 1]            │
    │ --barostat_substeps          INTEGER  Number of sub-steps in  │
    │                                       barostat integration    │
    │                                       for NPT MTK simulation. │
    │                                       [default: 1]            │
    │ --ensemble_kwargs            DICT     Keyword arguments to    │
    │                                       pass to ensemble        │
    │                                       initialization. Must be │
    │                                       passed as a dictionary  │
    │                                       wrapped in quotes, e.g. │
    │                                       "{'key': value}".       │
    │                                       [default: None]         │
    ╰───────────────────────────────────────────────────────────────╯
    """
    paras = {
        "bulk_modulus": bulk_modulus,
        "pressure": pressure,
        "friction": friction,
        "taut": taut,
        **kwargs,
    }
    return paras

  def get_paras_temp_ramp(self,
                          temp_start=None,
                          temp_end=None,
                          temp_step=None,
                          temp_time=None):
    """
    ╭─ Heating/cooling ramp ────────────────────────────────────────╮
    │ --temp_start        FLOAT  Temperature to start heating, in   │
    │                            K.                                 │
    │                            [default: None]                    │
    │ --temp_end          FLOAT  Maximum temperature for heating,   │
    │                            in K.                              │
    │                            [default: None]                    │
    │ --temp_step         FLOAT  Size of temperature steps when     │
    │                            heating, in K.                     │
    │                            [default: None]                    │
    │ --temp_time         FLOAT  Time between heating steps, in fs. │
    │                            [default: None]                    │
    ╰───────────────────────────────────────────────────────────────╯
    """
    paras = {
        "temp_start": temp_start,
        "temp_end": temp_end,
        "temp_step": temp_step,
        "temp_time": temp_time,
    }
    return paras

  def get_paras_restart(self,
                        restart=False,
                        restart_every=1000,
                        rotate_restart=False,
                        restarts_to_keep=4,
                        **kwargs,
                        ):
    """
    ╭─ Restart settings ────────────────────────────────────────────╮
    │ --restart          --no-restart               Whether         │
    │                                               restarting      │
    │                                               dynamics.       │
    │                                               [default:       │
    │                                               no-restart]     │
    │ --restart_auto     --no-restart-…             Whether to      │
    │                                               infer restart   │
    │                                               file if         │
    │                                               restarting      │
    │                                               dynamics.       │
    │                                               [default:       │
    │                                               restart-auto]   │
    │ --restart_stem                       PATH     Stem for        │
    │                                               restart file    │
    │                                               name. Default   │
    │                                               inferred from   │
    │                                               `file_prefix`.  │
    │                                               [default: None] │
    │ --restart_every                      INTEGER  Frequency of    │
    │                                               steps to save   │
    │                                               restart info.   │
    │                                               [default: 1000] │
    │ --rotate_restart    --no-rotate-r…            Whether to      │
    │                                               rotate restart  │
    │                                               files.          │
    │                                               [default:       │
    │                                               no-rotate-rest… │
    │ --restarts_to_keep                   INTEGER  Restart files   │
    │                                               to keep if      │
    │                                               rotating.       │
    │                                               [default: 4]    │
    ╰───────────────────────────────────────────────────────────────╯
    """
    paras = {
        "restart": restart,
        "restart_every": restart_every,
        "rotate_restart": rotate_restart,
        "restarts_to_keep": restarts_to_keep,
        **kwargs,
    }
    return paras

  def get_paras_io(self,
                   file_prefix=None,
                   read_kwargs=None,
                   write_kwargs=None):
    """
    ╭─ Structure I/O ───────────────────────────────────────────────╮
    │ --file_prefix         PATH  Prefix for output files,          │
    │                             including directories. Default    │
    │                             directory is ./janus_results, and │
    │                             default filename prefix is        │
    │                             inferred from the input stucture  │
    │                             filename.                         │
    │                             [default: None]                   │
    │ --read_kwargs         DICT  Keyword arguments to pass to      │
    │                             ase.io.read. Must be passed as a  │
    │                             dictionary wrapped in quotes,     │
    │                             e.g. "{'key': value}". By         │
    │                             default, read_kwargs['index'] =   │
    │                             -1, so only the last structure is │
    │                             read.                             │
    │                             [default: None]                   │
    │ --write_kwargs        DICT  Keyword arguments to pass to      │
    │                             ase.io.write when saving any      │
    │                             structures. Must be passed as a   │
    │                             dictionary wrapped in quotes,     │
    │                             e.g. "{'key': value}".            │
    │                             [default: None]                   │
    ╰───────────────────────────────────────────────────────────────╯
    """
    paras = {
        "file_prefix": file_prefix,
        "read_kwargs": read_kwargs,
        "write_kwargs": write_kwargs,
    }
    return paras

  def get_paras_output(self,
                       final_file=None,
                       stats_file=None,
                       stats_every=100,
                       traj_file=None,
                       traj_append=False,
                       traj_start=0,
                       traj_every=100,
                       ):
    """
    ╭─ Output files ────────────────────────────────────────────────╮
    │ --final_file                        PATH     File to save     │
    │                                              final            │
    │                                              configuration at │
    │                                              each temperature │
    │                                              of similation.   │
    │                                              Default inferred │
    │                                              from             │
    │                                              `file_prefix`.   │
    │                                              [default: None]  │
    │ --stats_file                        PATH     File to save     │
    │                                              thermodynamical  │
    │                                              statistics.      │
    │                                              Default inferred │
    │                                              from             │
    │                                              `file_prefix`.   │
    │                                              [default: None]  │
    │ --stats_every                       INTEGER  Frequency to     │
    │                                              output           │
    │                                              statistics.      │
    │                                              [default: 100]   │
    │ --traj_file                         PATH     File to save     │
    │                                              trajectory.      │
    │                                              Default inferred │
    │                                              from             │
    │                                              `file_prefix`.   │
    │                                              [default: None]  │
    │ --traj_append    --no-traj-appe…             Whether to       │
    │                                              append           │
    │                                              trajectory.      │
    │                                              [default:        │
    │                                              no-traj-append]  │
    │ --traj_start                        INTEGER  Step to start    │
    │                                              saving           │
    │                                              trajectory.      │
    │                                              [default: 0]     │
    │ --traj_every                        INTEGER  Frequency of     │
    │                                              steps to save    │
    │                                              trajectory.      │
    │                                              [default: 100]   │
    ╰───────────────────────────────────────────────────────────────╯
    """
    paras = {
        "final_file": final_file,
        "stats_file": stats_file,
        "stats_every": stats_every,
        "traj_file": traj_file,
        "traj_append": traj_append,
        "traj_start": traj_start,
        "traj_every": traj_every,
    }
    return paras

  def get_paras_log(self,
                    log=None,
                    tracker=False,
                    summary=None,
                    progress_bar=True,
                    update_progress_every=None,
                    ):
    """_summary_
    ╭─ Logging/summary ─────────────────────────────────────────────╮
    │ --log                                PATH     Path to save    │
    │                                               logs to.        │
    │                                               Default is      │
    │                                               inferred from   │
    │                                               `file_prefix`   │
    │                                               [default: None] │
    │ --tracker          --no-tracker               Whether to save │
    │                                               carbon          │
    │                                               emissions of    │
    │                                               calculation     │
    │                                               [default:       │
    │                                               tracker]        │
    │ --summary                            PATH     Path to save    │
    │                                               summary of      │
    │                                               inputs,         │
    │                                               start/end time, │
    │                                               and carbon      │
    │                                               emissions.      │
    │                                               Default is      │
    │                                               inferred from   │
    │                                               `file_prefix`.  │
    │                                               [default: None] │
    │ --progress_bar     --no-progress…             Whether to show │
    │                                               progress bar.   │
    │                                               [default:       │
    │                                               progress-bar]   │
    │ --update_progress_every              INTEGER  Number of       │
    │                                               timesteps       │
    │                                               between         │
    │                                               progress bar    │
    │                                               updates.        │
    │                                               Default is      │
    │                                               steps / 100,    │
    │                                               rounded up.     │
    │                                               [default: None] │
    ╰───────────────────────────────────────────────────────────────╯
    """
    paras = {
        "log": log,
        "tracker": tracker,
        "summary": summary,
        "progress_bar": progress_bar,
        "update_progress_every": update_progress_every,
    }
    return paras

  def get_paras_my_universal(self, struct: ase.Atoms,
                             arch="mace_mp",
                             device="cpu",
                             model="/Users/wangjinlong/job/soft_learn/py_package_learn/mace_learn/mace-foundations/mace-mpa-0-medium.model",
                             calc_kwargs={"default_dtype": "float64"},
                             ensemble='npt',
                             steps=1000,
                             timestep=1,
                             temp=300,
                             remove_rot=True,
                             rescale_velocities=True,
                             rescale_every=10,
                             post_process_kwargs=None,
                             correlation_kwargs=None,
                             seed=None,
                             restart=False,
                             restart_every=1000,
                             rotate_restart=False,
                             restarts_to_keep=4,
                             file_prefix=None,
                             stats_every=100,
                             traj_start=0,
                             traj_every=100,
                             **kwargs,
                             ):
    paras_1 = self.get_paras_mlip(arch=arch,
                                  model=model,
                                  device=device,
                                  calc_kwargs=calc_kwargs,)
    paras_2 = self.get_paras_calculation(ensemble=ensemble,
                                         steps=steps,
                                         timestep=timestep,
                                         temp=temp,
                                         remove_rot=remove_rot,
                                         rescale_velocities=rescale_velocities,
                                         rescale_every=rescale_every,
                                         post_process_kwargs=post_process_kwargs,
                                         correlation_kwargs=correlation_kwargs,
                                         seed=seed)
    paras_3 = self.get_paras_restart(restart=restart,
                                     restart_every=restart_every,
                                     rotate_restart=rotate_restart,
                                     restarts_to_keep=restarts_to_keep,)
    paras_4 = self.get_paras_io(file_prefix=file_prefix,)
    paras_5 = self.get_paras_output(traj_start=traj_start,
                                    traj_every=traj_every,
                                    stats_every=stats_every,)
    paras = {'struct': struct,
             **paras_1,
             **paras_2,
             **paras_3,
             **paras_4,
             **paras_5,
             **kwargs,
             }
    return paras

  def npt_calc(self, atoms,
               directory='/Users/wangjinlong/my_server/my/W_Re_potential/database_for_WReHe_gpaw/tmp',
               timestep=3,
               temp=3000,
               steps=100,
               stats_every=10,
               traj_every=10,
               restart_every=None,
               restart=False,
               **kwargs,
               ):
    if restart_every is None:
      restart_every = steps
    paras = self.get_paras_my_universal(struct=atoms,
                                        ensemble='npt',
                                        timestep=timestep,
                                        temp=temp,
                                        steps=steps,
                                        stats_every=stats_every,
                                        traj_every=traj_every,
                                        restart_every=restart_every,
                                        restart=restart,
                                        **kwargs,
                                        )
    cwd = os.getcwd()
    os.chdir(path=directory)
    npt = janus_core.calculations.md.NPT(**paras,)
    npt.run()
    os.chdir(cwd)
    return npt

  def NVT_example(self, atoms: ase.Atoms):
    nvt = janus_core.calculations.md.NVT(
        struct=atoms,
        arch="mace_mp",
        device="cpu",
        model=self.model_mace_mp,
        calc_kwargs={"default_dtype": "float64"},
        temp_start=300.0,
        temp_end=200.0,
        temp_step=20,
        temp_time=5,
        stats_every=2,
    )
    return nvt

  def coling(self):
    from ase.io import read

    from janus_core.calculations.md import NVE, NVT
    from janus_core.processing import post_process
    from janus_core.helpers.stats import Stats
    NaCl = ase.build.bulk('NaCl', 'rocksalt', a=5.63, cubic=True)
    NaCl = NaCl * (2, 2, 2)
    cooling = janus_core.calculations.md.NVT(
        struct=NaCl.copy(),
        arch="mace_mp",
        device="cpu",
        model=self.model_mace_mp,
        calc_kwargs={
            "default_dtype": "float64"},
        temp_start=300.0,
        temp_end=200.0,
        temp_step=20,
        temp_time=5,
        stats_every=2,
    )
    cooling.run()

  def analysis_stats_dat(self,
                         fname="/Users/wangjinlong/job/soft_learn/py_package_learn/janus_core_learn/package/janus-tutorials-main/janus_results/Cl32Na32-nvt-T300.0-T200.0-stats.dat",
                         xdata_index=2,
                         ydata_index=5):

    data = janus_core.helpers.stats.Stats(source=fname)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(data[xdata_index], data[ydata_index],
            label=data.labels[ydata_index],
            marker='o')
    ax.set_xlabel(
        xlabel=f'{data.labels[xdata_index]} ({data.units[xdata_index]})')
    ax.set_ylabel(
        ylabel=f'{data.labels[ydata_index]} ({data.units[ydata_index]})')
    ax.legend()
    plt.show()
    # df = pd.DataFrame(data=data.labels, columns=["labels"])
    return data

  def analysis_stats_dat_double_y(self,
                                  fname="/Users/wangjinlong/job/soft_learn/py_package_learn/janus_core_learn/package/janus-tutorials-main/janus_results/Cl32Na32-nvt-T300.0-T200.0-stats.dat",
                                  xdata_index=2,
                                  ydata_index1=5,
                                  ydata_index2=6,
                                  markersize=6,
                                  y1_lim=None,
                                  y2_lim=None,
                                  is_save=False,
                                  fname_pdf='xx/tmp.pdf'):

    data = janus_core.helpers.stats.Stats(source=fname)
    from soft_learn_project.matplotlib_learn import matplotlibLearn
    matplotlibLearn.Features().TwoDimension.double_y_axies(
        x=data[xdata_index],
        y1=data[ydata_index1],
        y2=data[ydata_index2],
        x_label=f'{data.labels[xdata_index]} ({data.units[xdata_index]})',
        ax_y1label=f'{data.labels[ydata_index1]} ({data.units[ydata_index1]})',
        ax_y2label=f'{data.labels[ydata_index2]} ({data.units[ydata_index2]})',
        line_y1label=f'{data.labels[ydata_index1]}',
        line_y2label=f'{data.labels[ydata_index2]}',
        markersize=markersize,
        y1_lim=y1_lim,
        y2_lim=y2_lim,
        is_save=is_save,
        fname=fname_pdf,
    )
    return data

  def calc_rdf(self, atoms: ase.Atoms):
    md = janus_core.calculations.md.NVE(
        struct=atoms,
        temp=300,
        stats_every=5,
        steps=50,
        post_process_kwargs={
            "rdf_compute": True,
            "rdf_rmax": 5,
            "rdf_bins": 200
        },
    )
    md.run()
    rdf = np.loadtxt("janus_results/Cl32Na32-nve-T300-rdf.dat")
    bins, counts = zip(*rdf)
    plt.plot(bins, counts)
    plt.ylabel("RDF")
    plt.xlabel("Distance / Å")
    plt.show()

  def get_rdf(self):
    import janus_core.processing.post_process
    data = ase.io.read("data/precomputed_NaCl-traj.xyz", index=":")
    rdf = janus_core.processing.post_process.compute_rdf(
        data, rmax=5.0, nbins=200)
    plt.plot(rdf[0], rdf[1])
    plt.ylabel("RDF")
    plt.xlabel("Distance / Å")
    plt.show()

    pass


class EOS(Base):
  def __init__(self,):
    """/Users/wangjinlong/job/soft_learn/py_package_learn/janus_core_learn/package/janus-tutorials-main/eos.ipynb
    """
    super().__init__()
    pass

  def calc_eos(self, atoms: ase.Atoms,
               arch="mace_mp",
               model="/Users/wangjinlong/job/soft_learn/py_package_learn/mace_learn/mace-foundations/mace-mpa-0-medium.model",
               is_show=False):
    eos = janus_core.calculations.eos.EoS(
        struct=atoms.copy(),
        arch=arch,
        device="cpu",
        model=model,
        calc_kwargs={"default_dtype": "float64"},
        minimize_kwargs={"filter_func": None},
    )
    eos_result = eos.run()
    if is_show:
      eos_result["eos"].plot(show=True)
    return eos_result

  def get_plot_data(self,
                    eos_result: janus_core.calculations.eos.EoSResults):

    plot_data = eos_result["eos"].getplotdata()
    return plot_data

  def get_alpha_quartz(self):
    alpha_quartz = ase.Atoms(symbols=(*["Si"]*3, *["O"]*6),
                             scaled_positions=[[0.469700, 0.000000, 0.000000],
                                               [0.000000, 0.469700, 0.666667],
                                               [0.530300, 0.530300, 0.333333],

                                               [0.413500, 0.266900, 0.119100],
                                               [0.266900, 0.413500, 0.547567],
                                               [0.733100, 0.146600, 0.785767],

                                               [0.586500, 0.853400, 0.214233],
                                               [0.853400, 0.586500, 0.452433],
                                               [0.146600, 0.733100, 0.880900]],

                             cell=[[4.916000, 0.000000, 0.000000],
                                   [-2.45800, 4.257381, 0.000000],
                                   [0.000000, 0.000000, 5.405400]],
                             pbc=True,
                             )
    return alpha_quartz

  def get_beta_quartz(self):
    beta_quartz = ase.io.read(
        "/Users/wangjinlong/job/soft_learn/py_package_learn/janus_core_learn/package/janus-tutorials-main/data/beta_quartz.cif")
    return beta_quartz

  def calc_eos_example1(self, is_show=False):
    alpha_quartz = self.get_alpha_quartz()
    eos = janus_core.calculations.eos.EoS(
        struct=alpha_quartz.copy(),
        arch="mace_mp",
        device="cpu",
        model=self.model_mace_mp,
        calc_kwargs={"default_dtype": "float64"},
        minimize_kwargs={"filter_func": None},
        min_volume=0.75,
        max_volume=1.25,
        n_volumes=20,
    )
    eos_result = eos.run()
    if is_show:
      eos_result["eos"].plot(show=True)
    return eos_result

  def calc_eos_example2(self, is_show=False):
    beta_quartz = self.get_beta_quartz()
    eos = janus_core.calculations.eos.EoS(
        struct=beta_quartz.copy(),
        arch="mace_mp",
        device="cpu",
        model=self.model_mace_mp,
        calc_kwargs={"default_dtype": "float64"},
        minimize_kwargs={"filter_func": None},
        min_volume=0.75,
        max_volume=1.25,
        n_volumes=20,
    )
    eos_result = eos.run()
    if is_show:
      eos_result["eos"].plot(show=True)
    return eos_result

  def combine_eos(self):
    # Combining plots for α-quartz and β-quartz:
    import matplotlib.pyplot as plt
    ax = plt.gca()
    eos_r1 = self.calc_eos_example1(is_show=False)
    eos_r2 = self.calc_eos_example2(is_show=False)

    data_alpha = eos_r1["eos"].getplotdata()
    data_beta = eos_r2["eos"].getplotdata()

    ax.plot(data_alpha[4], data_alpha[5], ls='-', color='C3', label="α-quartz")
    ax.plot(data_alpha[6], data_alpha[7], ls='',
            marker='x', color='C4', mfc='C4')

    ax.plot(data_beta[4], data_beta[5], ls='-', color='C0', label="β-quartz")
    ax.plot(data_beta[6], data_beta[7], ls='',
            marker='x', color='C2', mfc='C2')

    ax.set_xlabel('volume [Å$^3$]')
    ax.set_ylabel('energy [eV]')
    ax.legend()

    plt.show()
    pass

  def compare_three_results(self):
    # Comparing MACE to CHGNET and MGNET
    alpha_quartz = self.get_alpha_quartz()

    mace_eos = janus_core.calculations.eos.EoS(
        struct=alpha_quartz.copy(),
        arch="mace_mp",
        device="cpu",
        model=self.model_mace_mp,
        minimize_kwargs={"filter_func": None}
    ).run()
    m3gnet_eos = janus_core.calculations.eos.EoS(
        struct=alpha_quartz.copy(),
        arch="m3gnet",
        device="cpu",
        model=self.model_m3gnet,
        minimize_kwargs={"filter_func": None}
    ).run()
    # m3gnet_eos["eos"].plot(show=True)
    chgnet_eos = janus_core.calculations.eos.EoS(
        struct=alpha_quartz.copy(),
        arch="chgnet",
        device="cpu",
        model=self.model_chgnet,
        minimize_kwargs={"filter_func": None}
    ).run()

    print(f"MACE energy [eV]: {mace_eos['e_0']}")
    print(f"M3GNET energy [eV]: {m3gnet_eos['e_0']}")
    print(f"CHGNET energy [eV]: {chgnet_eos['e_0']}")

    print()

    print(f"MACE volume [Å^3]: {mace_eos['v_0']}")
    print(f"M3GNET volume [Å^3]: {m3gnet_eos['v_0']}")
    print(f"CHGNET volume [Å^3]: {chgnet_eos['v_0']}")

    print()

    print(f"MACE bulk_modulus [GPa]: {mace_eos['bulk_modulus']}")
    print(f"M3GNET bulk_modulus [GPa]: {m3gnet_eos['bulk_modulus']}")
    print(f"CHGNET bulk_modulus [GPa]: {chgnet_eos['bulk_modulus']}")

    pass


class Phonons(Base):
  def __init__(self,):
    """/Users/wangjinlong/job/soft_learn/py_package_learn/janus_core_learn/package/janus-tutorials-main/phonons.ipynb
    """
    super().__init__()

  def get_NaCl(self):
    NaCl = ase.build.bulk('NaCl', 'rocksalt', a=5.63, cubic=True)
    return NaCl

  def phonon_calc_salt(self):
    """phonon calculations on salt """
    import janus_core.calculations.phonons
    NaCl = self.get_NaCl()
    # Note: Set `filter_func = None` for geometry optimization via `minimize_kwargs`, so cell is fixed
    phonons_mace = janus_core.calculations.phonons.Phonons(
        struct=NaCl.copy(),
        arch="mace_mp",
        device="cpu",
        model=self.model_mace_mp,
        calc_kwargs={"default_dtype": "float64"},
        supercell=[2, 2, 2],
        displacement=0.01,
        temp_step=10.0,
        temp_min=0.0,
        temp_max=1000.0,
        minimize=False,
        force_consts_to_hdf5=True,
        plot_to_file=True,
        symmetrize=False,
        write_full=True,
        minimize_kwargs={"filter_func": None},
        write_results=True,
    )
    # Optimize structure and calculate force constants using phonopy.
    # This will save phonopy to `Cl4Na4-phonopy.yml`, and additionally save force constants to `Cl4Na4-force_constants.hdf5`:
    phonons_mace.calc_force_constants()
    # Calculate and plot band structure, writing results to `Cl4Na4-auto_bands.yml`, and saving the figure as `Cl4Na4-auto_bands.svg`:
    phonons_mace.calc_bands(write_bands=True)
    # Calculate thermal properties, saving the heat capacity, enthalpy, and entropy, to `Cl4Na4-thermal.dat`:
    phonons_mace.calc_thermal_props(write_thermal=True)
    return phonons_mace

  def phonon_calc_with_opt_cell(self):
    """honon calcualtions with optimization of cell
    The same calculations can be run with cell lengths, but not angles, optimized.

    Note: Set `"filter_kwargs" = {"hydrostatic_strain": True}` for geometry optimization via `minimize_kwargs`, so cell angles are fixed, but lengths can change
    """
    import janus_core.calculations.phonons
    NaCl = self.get_NaCl()
    phonons_mace_lengths_only = janus_core.calculations.phonons.Phonons(
        struct=NaCl.copy(),
        arch="mace_mp",
        device="cpu",
        model=self.model_mace_mp,
        calc_kwargs={"default_dtype": "float64"},
        supercell=[2, 2, 2],
        displacement=0.01,
        temp_step=10.0,
        temp_min=0.0,
        temp_max=1000.0,
        minimize=True,
        force_consts_to_hdf5=True,
        plot_to_file=True,
        symmetrize=False,
        write_full=True,
        minimize_kwargs={"filter_kwargs": {"hydrostatic_strain": True}},
        write_results=True,
    )
    phonons_mace_lengths_only.calc_bands(write_bands=True)
    # Confirm changes to cell lengths:
    print(phonons_mace_lengths_only.struct.cell.cellpar())
    return phonons_mace_lengths_only

  def phonon_calc_with_pressure(self):
    """Phonon calculations with pressure
    Calculations can also be run at a fixed pressure, as well as optmising both the cell lengths and angles.

    Note: Set `"filter_kwargs" = {"scalar_pressure": x}` for geometry optimization via `minimize_kwargs` to set the pressure. Without setting `hydrostatic_strain =  True`, both the cell lengths and angles will be optimized 
    """
    import janus_core.calculations.phonons
    NaCl = self.get_NaCl()
    phonons_mace_pressure = janus_core.calculations.phonons.Phonons(
        struct=NaCl.copy(),
        arch="mace_mp",
        device="cpu",
        model=self.model_mace_mp,
        calc_kwargs={"default_dtype": "float64"},
        supercell=[2, 2, 2],
        displacement=0.01,
        temp_step=10.0,
        temp_min=0.0,
        temp_max=1000.0,
        minimize=True,
        force_consts_to_hdf5=True,
        plot_to_file=True,
        symmetrize=False,
        write_full=True,
        minimize_kwargs={"filter_kwargs": {"scalar_pressure": 0.1}},
        write_results=True,
    )
    phonons_mace_pressure.calc_bands(write_bands=True)
    print(phonons_mace_pressure.struct.cell.cellpar())
    # save to files:
    phonons_mace_pressure.write_bands(plot_file="NaCl_pressure.svg")
    return phonons_mace_pressure

  def phonon_calc(self):
    import janus_core.calculations.phonons
    NaCl = self.get_NaCl()
    phonons_m3gnet = janus_core.calculations.phonons.Phonons(
        struct=NaCl.copy(),
        arch="m3gnet",
        device="cpu",
        model=self.model_m3gnet,
        supercell=[2, 2, 2],
        displacement=0.01,
        temp_step=10.0,
        temp_min=0.0,
        temp_max=1000.0,
        minimize=True,
        force_consts_to_hdf5=True,
        plot_to_file=True,
        symmetrize=False,
        write_full=True,
        minimize_kwargs={"filter_func": None},
        write_results=True,
    )
    phonons_m3gnet.write_bands(plot_file="m3gnet.svg")
    return phonons_m3gnet


class JanuscoreLearn(Base):
  def __init__(self,):
    r"""
    https://github.com/stfc/janus-core?tab=readme-ov-file#getting-started

    --- 教学目录
    /Users/wangjinlong/job/soft_learn/py_package_learn/janus_core_learn/package/janus-core-main/docs/source/tutorials/python  
    ---
    janus-core 是一个用于材料科学模拟的 Python 库，特别适用于集成和管理多种机器学习势能模型（MLIPs），如 MACE、CHGNet、M3GNet 和 ORB 等。

    🔧 janus-core 的主要功能
    统一接口：为不同的 ML 势能模型提供统一的 Python 接口，简化了模型的调用和管理。

    ASE 集成：与 Atomic Simulation Environment (ASE) 集成，支持结构优化、分子动力学模拟等任务。

    命令行工具：提供命令行工具，方便在终端中运行模拟任务。

    可扩展性：支持添加新的 ML 势能模型，方便用户根据需求扩展功能。
    """
    # self.config = config
    # self.model = modules.MACE(**self.config)
    # self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
    # self.criterion = torch.nn.MSELoss()
    super().__init__()
    self.Base = Base()
    self.NEB = NEB()
    self.MD = MD()
    self.EOS = EOS()
    self.Phonons = Phonons()
    pass

  def install(self):
    """
    uv pip install "janus-core[m3gnet,chgnet,sevennet]" -i https://pypi.tuna.tsinghua.edu.cn/simple
    pip install janus-core
    python3 -m pip install "janus-core[all]"
    # ase 
    python3 -m pip install git+https://gitlab.com/ase/ase.git

    """
    pass
