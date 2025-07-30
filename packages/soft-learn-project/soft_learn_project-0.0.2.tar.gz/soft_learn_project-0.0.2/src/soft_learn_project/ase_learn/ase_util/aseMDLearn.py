import numpy as np
import pandas as pd
import ase.lattice.cubic
import ase.md.verlet
import ase.optimize
import ase.calculators.emt
import ase.calculators
import ase.optimize
import ase.io
import ase
import ase.lattice
import ase.md
import ase.units
import ase.visualize
import os
import ase.calculators.calculator
import ase.md.velocitydistribution
import ase.md.verlet
import ase.md.md
import ase.md.langevin
import ase.md.nose_hoover_chain
import ase.md.bussi
import ase.md.andersen
import ase.md.nvtberendsen
import ase.md.nptberendsen
import ase.md.npt
import ase.md.analysis


class MDBase():
  def __init__(self):
    """xx"""
    super().__init__()
    pass

  def get_press(self, atoms: ase.Atoms):
    # ASE 获取压力的方法（单位是 GPa）
    stress = atoms.get_stress(voigt=False)  # shape (3, 3)，单位为 eV/Å³
    pressure_eVA3 = -np.trace(stress) / 3   # 取负号是因为压缩为正压
    pressure_GPa = pressure_eVA3 * 160.21766208  # eV/Å³ → GPa
    pressure_Pa = pressure_GPa * ase.units.GPa
    # pressure_atm = pressure_GPa * 9.86923
    return pressure_Pa

  def get_df_thermo(self, atoms: ase.Atoms,
                    call_times=1,
                    loginterval=100,
                    timestep=5,
                    thermo_name_list=['step', 'time', 'temperature',
                                      'pe[eV]', 'ke', 'lx', 'ly', 'lz', 'vol', 'press'],
                    decimals=3,):
    """thermo_name_list: steps|time|temperature|pe|ke|lx|ly|lz|vol|press 可选的热力学量
    """
    steps = (call_times - 1) * loginterval
    time = steps * timestep
    pe = atoms.get_potential_energy()
    ke = atoms.get_kinetic_energy()
    temperature_K = atoms.get_temperature()
    # temperature_K = ke_patom / (3/2 * ase.units.kB) # 或者这个
    lx = atoms.get_cell()[0, 0]
    ly = atoms.get_cell()[1, 1]
    lz = atoms.get_cell()[2, 2]
    vol = atoms.get_volume()
    press = self.get_press(atoms=atoms)
    data = {'steps': steps,
            'time[ps]': time/1e+3,
            'temperature_K[K]': temperature_K,
            'pe[eV]': pe,
            'ke[eV]': ke,
            'lx[A]': lx,
            'ly[A]': ly,
            'lz[A]': lz,
            'vol[A^3]': vol,
            'press[GPa]': press,
            }
    df = pd.DataFrame([data])
    # 取出部分列, 并按照顺序
    # regex = '|'.join(thermo_name_list) if len(
    #     thermo_name_list) > 1 else thermo_name_list
    # df_filter = df.filter(regex=regex, axis=1)
    # 再按目标顺序重排列
    column_ordered = []
    for name in thermo_name_list:
      for column in df.columns:
        if name in column:
          column_ordered.append(column)
    df = df[column_ordered]
    df = df.round(decimals=decimals)
    return df

  def get_df_from_csv(self,
                      directory='.',
                      fname_csv='md.log'):
    df = pd.read_csv(os.path.join(directory, fname_csv))
    return df

  def md_attach_custom_function(self, atoms: ase.Atoms,
                                dyn: ase.md.md.MolecularDynamics,
                                timestep=5,
                                loginterval=10,
                                thermo_name_list=[
                                    'step', 'time', 'temperature', 'pe[eV]', 'ke', 'lx', 'ly', 'lz', 'vol', 'press'],
                                decimals=3,
                                fname_log='md.log',
                                is_append_log=False,):
    """构建并在 md_obj 中加入自定义的 attach 函数
    thermo_name_list: steps|time|temperature|pe|ke|lx|ly|lz|vol|press 可选的热力学量
    """
    df = self.get_df_thermo(atoms=atoms,
                            call_times=1,
                            loginterval=loginterval,
                            timestep=timestep,
                            thermo_name_list=thermo_name_list,)
    mode = 'a' if is_append_log else 'w'
    df.head(0).to_csv(fname_log,
                      mode=mode,
                      index=False)
    # with open(fname_log, mode=mode) as f:
    #   print(*df.columns, file=f)

    def md_function():
      md_function.calls += 1
      df = self.get_df_thermo(atoms=atoms,
                              call_times=md_function.calls,
                              loginterval=loginterval,
                              timestep=timestep,
                              thermo_name_list=thermo_name_list,
                              decimals=decimals,)
      df.to_csv(fname_log, mode='a',
                header=False, index=False)
      # with open(fname_log, mode='a') as f:
      #   string = df.to_string(header=False,
      #                         index=False)
      #   print(string, file=f)

    md_function.calls = 0
    dyn.attach(function=md_function, interval=loginterval)
    return dyn

  def md_attach_temperature(self,
                            dyn: ase.md.nptberendsen.NPTBerendsen,
                            T_start=300,
                            T_end=1000,
                            run_steps=1000,
                            ):
    """定义升温过程：线性升温函数
    用于体系升温
    """

    def temperature_ramp():
      current_step = dyn.get_number_of_steps()
      temperature = T_start + (T_end - T_start) * current_step / run_steps
      dyn.set_temperature(temperature_K=temperature)

    # 每一步都更新温度
    dyn.attach(function=temperature_ramp, interval=1)
    return dyn

  def md_attach_custom_check_volume_ratio(self,
                                          initial_volume: float,
                                          atoms: ase.Atoms,
                                          dyn: ase.md.md.MolecularDynamics,
                                          volume_ratio_stop=1.119,
                                          fname_traj='ase.traj',
                                          ):
    """检查当满足某个条件时, 中断md 模拟
    * 这里设置的是体积比
    """
    def check_volume_ratio():
      current_volume = atoms.get_volume()
      volume_ratio = current_volume / initial_volume

      if volume_ratio > volume_ratio_stop:
        atoms.write(filename=fname_traj,)
        dyn.close()
        raise RuntimeError(f"体积比达到 {volume_ratio}, 停止模拟。")

    dyn.attach(function=check_volume_ratio, interval=1)
    return dyn

  def md_attach_logger(self, atoms: ase.Atoms,
                       dyn: ase.md.md.MolecularDynamics,
                       interval=10,
                       logfile='mdx.log',
                       header=True,
                       stress=False,
                       peratom=True,
                       ):
    """加入md日志, 通常在 md_obj 加入日志就够了
    """
    md_logger = ase.md.MDLogger(dyn=dyn,
                                atoms=atoms,
                                logfile=logfile,
                                header=header,
                                stress=stress,
                                peratom=peratom,
                                mode="a")
    dyn.attach(function=md_logger,
               interval=interval)
    return dyn

  def md_attach_traj(self, atoms: ase.Atoms,
                     dyn: ase.md.md.MolecularDynamics,
                     fname_traj='ase.traj',
                     interval=10,):
    """加入 md 轨迹, 通常在 md_obj 加入轨迹就够了
    """
    traj = ase.io.Trajectory(filename=fname_traj,
                             mode='w',
                             atoms=atoms)
    dyn.attach(function=traj, interval=interval)
    return dyn

  def get_md_control_velocitydistribution_MaxwellBZ(self,
                                                    atoms: ase.Atoms,
                                                    temperature_K=1200,
                                                    force_temp=False,):
    """Set the momenta corresponding to T=1200K"""
    ase.md.velocitydistribution.MaxwellBoltzmannDistribution(
        atoms=atoms,
        temperature_K=temperature_K,
        force_temp=force_temp,)
    return None

  def get_md_control_velocitydistribution_PhononHarmonics(
          self,
          atoms: ase.Atoms,
          temperature_K=1200,
          force_constants=None,):
    """This will displace atomic positions and set the velocities so as to produce a random, phononically correct state with the requested temperature.
    ---
    ase.md.velocitydistribution.phonon_harmonics ??
    """
    ase.md.velocitydistribution.PhononHarmonics(
        atoms=atoms,
        force_constants=force_constants,
        temperature_K=temperature_K,
    )
    return None

  def get_md_control_Stationary(self, atoms: ase.Atoms):
    """zero linear momentum
    """
    ase.md.velocitydistribution.Stationary(atoms)  # zero linear momentum
    return None

  def get_md_control_ZeroRotation(self, atoms: ase.Atoms,
                                  preserve_temperature=True):
    """zero angular momentum
    """
    ase.md.velocitydistribution.ZeroRotation(atoms=atoms,
                                             preserve_temperature=preserve_temperature)
    return None

  def get_md_obj_VelocityVerlet(self,
                                atoms: ase.Atoms,
                                timestep=5,
                                is_save_log=True,
                                logfile='md.log',
                                is_save_traj=True,
                                trajectory='md.traj',
                                loginterval=10,
                                ):
    """NVE系综中的分子动力学模拟将使用Velocity Verlet动力学
    - 如果时间步长很小或很大，那么在Velocity Verlet动力学中，能量守恒的缺乏是最明显的，否则能量应该是守恒的。
    """
    logfile = logfile if is_save_log else None  # 可以为 '-'
    trajectory = trajectory if is_save_traj else None
    dyn = ase.md.verlet.VelocityVerlet(atoms=atoms,
                                       timestep=timestep * ase.units.fs,
                                       trajectory=trajectory,
                                       logfile=logfile,
                                       loginterval=loginterval,
                                       )
    return dyn

  def get_md_obj_Langevin(self,
                          atoms: ase.Atoms,
                          timestep=5,
                          temperature_K=300,
                          friction=0.002,
                          is_save_log=True,
                          logfile='md.log',
                          is_save_traj=True,
                          trajectory='md.traj',
                          loginterval=10,
                          ):
    """control the temperature of an MD simulation
    * friction 典型范围为0.001-0.1 fs−1 （1 - 100 ps−1）。
    """
    logfile = logfile if is_save_log else None  # 可以为 '-'
    trajectory = trajectory if is_save_traj else None
    dyn = ase.md.langevin.Langevin(atoms=atoms,
                                   timestep=timestep * ase.units.fs,
                                   temperature_K=temperature_K,
                                   friction=friction,
                                   fixcm=True,
                                   # ---
                                   trajectory=trajectory,
                                   logfile=logfile,
                                   loginterval=loginterval,
                                   )
    return dyn

  def get_md_obj_NoseHooverChainNVT(self,
                                    atoms: ase.Atoms,
                                    timestep=5,
                                    temperature_K=300,
                                    tdamp=100,
                                    is_save_log=True,
                                    logfile='md.log',
                                    is_save_traj=True,
                                    trajectory='md.traj',
                                    loginterval=10,):
    """ tdamp: 初始测试建议使用 tdamp=0.2 ps；
    配合 loginterval 输出温度信息，看温度是否振荡剧烈；
    如果温度剧烈波动或系统震荡，可以逐步增大 tdamp。
    """
    logfile = logfile if is_save_log else None  # 可以为 '-'
    trajectory = trajectory if is_save_traj else None
    dyn = ase.md.nose_hoover_chain.NoseHooverChainNVT(
        atoms=atoms,
        timestep=timestep * ase.units.fs,
        temperature_K=temperature_K,
        # 以ASE时间单位表示的恒温器的特征时间标度。通常，它被设置为100倍的时间步长。
        tdamp=timestep * ase.units.fs * tdamp,
        tchain=3,
        tloop=1,
        # ---
        trajectory=trajectory,
        logfile=logfile,
        loginterval=loginterval,
    )
    return dyn

  def get_md_obj_Bussi(self,
                       atoms: ase.Atoms,
                       timestep=5,
                       temperature_K=300,
                       taut=0.1,
                       is_save_log=True,
                       logfile='md.log',
                       is_save_traj=True,
                       trajectory='md.traj',
                       loginterval=10,):
    """系统类型	推荐 taut 值	说明
    小体系（<100原子）	0.01 ~ 0.1 ps	调节快，防止波动过大
    中等体系（~几百原子）	0.1 ~ 1.0 ps	稳定性和响应速度折中
    大体系（>1000原子）	1.0 ps 或更大（最多 10）	更慢调节，避免扰动自然演化
    """
    logfile = logfile if is_save_log else None  # 可以为 '-'
    trajectory = trajectory if is_save_traj else None
    dyn = ase.md.bussi.Bussi(
        atoms=atoms,
        timestep=timestep * ase.units.fs,
        temperature_K=temperature_K,
        taut=taut * ase.units.fs * 1000,
        rng=None,
        # ---
        trajectory=trajectory,
        logfile=logfile,
        loginterval=loginterval,
    )
    return dyn

  def get_md_obj_Andersen(self,
                          atoms: ase.Atoms,
                          timestep=5,
                          temperature_K=300,
                          andersen_prob=0.01,
                          is_save_log=True,
                          logfile='md.log',
                          is_save_traj=True,
                          trajectory='md.traj',
                          loginterval=10,):
    """andersen_prob: 碰撞概率。这个概率的典型值的顺序是1e-4到1e-1。
    """
    logfile = logfile if is_save_log else None  # 可以为 '-'
    trajectory = trajectory if is_save_traj else None
    dyn = ase.md.andersen.Andersen(
        atoms=atoms,
        timestep=timestep * ase.units.fs,
        temperature_K=temperature_K,
        andersen_prob=andersen_prob,
        fixcm=True,
        # ---
        trajectory=trajectory,
        logfile=logfile,
        loginterval=loginterval,
    )
    return dyn

  def get_md_obj_NVTBerendsen(self,
                              atoms: ase.Atoms,
                              timestep=5,
                              temperature_K=300,
                              taut=0.1,
                              is_save_log=True,
                              logfile='md.log',
                              is_save_traj=True,
                              trajectory='md.traj',
                              loginterval=10,):
    """taut=0.5*1000*units.fs
    """

    logfile = logfile if is_save_log else None  # 可以为 '-'
    trajectory = trajectory if is_save_traj else None
    dyn = ase.md.nvtberendsen.NVTBerendsen(
        atoms=atoms,
        timestep=timestep * ase.units.fs,
        temperature_K=temperature_K,
        taut=taut*1000*ase.units.fs,
        fixcm=True,
        # ---
        trajectory=trajectory,
        logfile=logfile,
        loginterval=loginterval,
    )
    return dyn

  def get_md_obj_NVE(self,
                     atoms: ase.Atoms,
                     timestep=5,
                     is_save_log=True,
                     logfile='md.log',
                     is_save_traj=True,
                     trajectory='md.traj',
                     loginterval=10,):
    """VelocityVerlet是唯一实现NVE集成的动态。它需要两个参数，原子和时间步长。选择太大的时间步长会立即变得很明显，因为能量会随着时间的推移而增加，通常非常迅速。
    """
    dyn = self.get_md_obj_VelocityVerlet(
        atoms=atoms,
        timestep=timestep,
        is_save_log=is_save_log,
        logfile=logfile,
        is_save_traj=is_save_traj,
        trajectory=trajectory,
        loginterval=loginterval,
    )
    return dyn

  def get_md_obj_NVT(self):
    """Constant NVT simulations (the canonical ensemble)
    * 推荐的算法 Langevin dynamics | Nosé-Hoover chain |Bussi dynamics
    * 不推荐的算法 Andersen dynamics|Berendsen NVT dynamics
    """
    pass

  def get_md_obj_NPTBerendsen(self,
                              atoms: ase.Atoms,
                              timestep=5,
                              temperature_K=300,
                              pressure_au=0,
                              mask=(1, 1, 1),
                              compressibility_au=0.01,
                              taut=100,
                              taup=10,
                              is_save_log=True,
                              logfile='md.log',
                              is_save_traj=True,
                              trajectory='md.traj',
                              loginterval=10,):
    """这是一个变化的Berendsen NVT动力学加上一个气压调节器。在每个时间步长之后，重新调整单元格的大小，使压力/应力接近所需的压力。它以两种形式存在，一种是保留细胞的形状，另一种是允许变化的。缺点：与正确的NPT系综相比，总能量和压力的波动都受到抑制。对于大型系统，预计这不会很严重。
    compressibility_au=0.01,  较好的参数
    taut=100,
    taup=10, 1-10
    * pressure_au: The desired pressure, in atomic units 
    pressure_au,  # ✅ 目标压力（原子单位），金属通常为 0.0 (eV/Å^3).
    taut,         # ✅ 温度耦合时间常数（以 fs 为单位）
    tau,          # ✅ 压力耦合时间常数（以 fs 为单位）
    compressibility_au=None, # ✅ 系统压缩率，金属很小，可查材料数据库
    ---
    * 模拟室温的气体分子 Room temperature simulation (300K, 0.1 fs time step, atmospheric pressure)
    dyn = NPTBerendsen(atoms, 
                   timestep=0.1 * units.fs, temperature_K=300,
                   taut=100 * units.fs, pressure_au=1.01325 * units.bar,
                   taup=1000 * units.fs, compressibility_au=4.57e-5 / units.bar)
    """
    logfile = logfile if is_save_log else None  # 可以为 '-'
    trajectory = trajectory if is_save_traj else None
    dyn = ase.md.nptberendsen.Inhomogeneous_NPTBerendsen(
        atoms=atoms,
        timestep=timestep * ase.units.fs,
        temperature_K=temperature_K,
        pressure_au=pressure_au,
        taut=taut * ase.units.fs,
        taup=taup * ase.units.fs,
        fixcm=True,
        compressibility_au=compressibility_au,
        mask=mask,
        # ---
        append_trajectory=False,
        trajectory=trajectory,
        logfile=logfile,
        loginterval=loginterval,
    )
    return dyn

  def get_md_obj_NPT_NH_HR(self,
                           atoms: ase.Atoms,
                           timestep=5,
                           temperature_K=300,
                           externalstress=0,
                           ttime=500,
                           pfactor=50,
                           mask=(1, 1, 1),
                           is_save_log=True,
                           logfile='md.log',
                           is_save_traj=True,
                           trajectory='md.traj',
                           loginterval=10,):
    """根据Melchionna等人的说法，NPT动态的实现结合了nos<s:1> - hoover恒温器和Parinello-Rahman气压调节器，见下文。不推荐!动力学往往是不稳定的，特别是当开始的温度或压力与期望的不同时。这种波动似乎经常是错误的。
    Nosé-Hoover-Parinello-Rahman
    ttime	0.1 ~ 1.0	ps	温度热浴响应时间，决定控温速度，推荐 0.1~0.5 ps
    pfactor	10 ~ 100	eV·ps²	压力调节阻尼项，与体系大小相关，越大越“软”，推荐 50 左右起步
    ---
    *  结合Nose-Hoover和Parrinello-Rahman动力学，形成NPT（或N、应力、T）系综。
    * externalstress: The external stress in eV/A^3. Either a symmetric 3x3 tensor, a 6-vector representing the same, or a scalar representing the pressure. Note that the stress is positive in tension whereas the pressure is positive in compression: giving a scalar p is equivalent to giving the tensor (-p, -p, -p, 0, 0, 0).
    * ttime 和 pfactor 是非常关键的，过小的值可能会导致T / p不稳定和/或错误的波动，过大的值会导致振荡而缓慢死亡。对于具有15000-200000个原子的大块铜来说，较好的特征时间值似乎是ttime为25fs， ptime（用于计算pfactor）为75fs。但这还没有经过很好的测试，监测温度和应力/压力波动是很重要的。
    * pfactor: A constant in the barostat differential equation. If a characteristic barostat timescale of ptime is desired, set pfactor to ptime^2 * B (where ptime is in units matching eV, Å, u; and B is the Bulk Modulus, given in eV/Å^3). Set to None to disable the barostat. Typical metallic bulk moduli are of the order of 100 GPa or 0.6 eV/A^3.
    * mask: 可选参数。由三个整数（0或1）组成的元组，表示系统是否可以沿着三个笛卡尔轴改变大小。设置为（1,1,1）或None以允许完全灵活的计算框。设置为（1,1,0）来禁止沿z轴等方向的伸长。掩模也可以指定为一个对称的3x3数组，指示哪些应变值可能会改变。
    """
    logfile = logfile if is_save_log else None  # 可以为 '-'
    trajectory = trajectory if is_save_traj else None
    dyn = ase.md.npt.NPT(
        atoms=atoms,
        timestep=timestep * ase.units.fs,
        temperature_K=temperature_K,
        externalstress=externalstress,
        ttime=ttime*ase.units.fs,
        pfactor=pfactor,
        mask=mask,
        # ---
        trajectory=trajectory,
        logfile=logfile,
        loginterval=loginterval,
        append_trajectory=False,
    )
    return dyn

  def get_md_obj_NPT(self):
    """恒定压力（对于固体，恒定应力）通常通过在上述NVT算法中添加一个恒压器来获得。ASE目前缺乏一个好的NPT算法。以下两个可用。
    * 推荐 Berendsen NPT dynamics
    * 不推荐 Parrinello-Rahman
    """
    return None

  def get_md_analysis_DiffusionCoefficient(self,
                                           traj: ase.io.Trajectory,
                                           timestep,
                                           atom_indices,
                                           molecule,
                                           ):
    """Post-simulation Analysis
    ---
    This class calculates the Diffusion Coefficient for the given Trajectory using the Einstein Equation:
    * atom_indices: 要显式计算扩散系数的原子的索引
    * timestep: 模拟的时间步长 * 间隔 
    * molecule (Boolean) – Indicate if we are studying a molecule instead of atoms, therefore use centre of mass in calculations
    """
    DiffusionCoefficient = ase.md.analysis.DiffusionCoefficient(
        traj=traj,
        timestep=timestep,
        atom_indices=atom_indices,
        molecule=molecule,
    )
    return DiffusionCoefficient


class MD(MDBase):
  def __init__(self):
    super().__init__()
    pass

  def example_nve(self, size=3,
                  temperature_K=300,):
    """molecular dynamics with constant energy
    """
    # 注意这里是周期性的
    atoms = ase.lattice.cubic.FaceCenteredCubic(
        directions=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        symbol='Cu',
        size=(size, size, size),
        pbc=True)
    calc = ase.calculators.emt.EMT()
    atoms.calc = calc

    # Set the momenta corresponding
    self.get_md_control_velocitydistribution_MaxwellBZ(
        atoms=atoms,
        temperature_K=temperature_K,
    )
    dyn = self.get_md_obj_VelocityVerlet(atoms=atoms,
                                         timestep=5,
                                         loginterval=100,
                                         is_save_traj=True,
                                         )
    dyn.run(steps=200)
    return dyn

  def example_nvt(self, size=5, friction=0.01,
                  temperature_K=1500,):
    """control the temperature of an MD simulation
    """
    # 注意这里是非周期性的
    atoms = ase.lattice.cubic.FaceCenteredCubic(
        directions=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        symbol='Cu',
        size=(size, size, size),
        pbc=False)
    calc = ase.calculators.emt.EMT()
    atoms.calc = calc

    dyn = self.get_md_obj_Langevin(atoms=atoms,
                                   temperature_K=temperature_K,
                                   timestep=5,
                                   loginterval=100,
                                   friction=friction)
    dyn.run(steps=5000)
    return None

  def example_nanoparticle(self, size=2):
    """Demonstrates molecular dynamics for isolated particles."""
    # Set up a nanoparticle
    import aseLearn
    atoms: ase.Atoms = aseLearn.Model().get_atoms_nanapartile_fcc_cubic(
        symbols='Cu',
        size=size)
    atoms.calc = ase.calculators.emt.EMT()

    # Do a quick relaxation of the cluster
    qn = ase.optimize.QuasiNewton(atoms)
    qn.run(0.001, 10)

    # Set the momenta corresponding to T=1200K
    self.get_md_control_velocitydistribution_MaxwellBZ(
        atoms=atoms,
        temperature_K=1200,)
    self.get_md_control_Stationary(atoms=atoms,)
    self.get_md_control_ZeroRotation(atoms=atoms,)

    dyn = self.get_md_obj_VelocityVerlet(atoms=atoms,
                                         timestep=5,
                                         loginterval=100)
    dyn.run(2000)
    return None

  def md_NPT(self,
             atoms: ase.Atoms,
             calc: ase.calculators.calculator.Calculator,
             temperature_K=3690,
             pressure_au=0.0,
             compressibility_au=0.001,
             taut=100,
             taup=1,
             timestep=5,
             run_steps=1000,
             loginterval=None,
             num_logs=10,
             mask=(1, 1, 1),
             is_save_log=True,
             thermo_name_list=[
                 'step', 'time',  'pe[eV]', 'ke', 'vol', 'temperature', 'press', 'lx'],
             df_decimals=3,
             fname_log='md_equilibrate.log',
             is_append_log=False,
             is_save_traj=True,
             fname_traj='md_equilibrate.traj',):
    """ compressibility_au=0.01,taut=100,taup=5, 300 步收敛, 算500步间隔50,取后五个体积求平均
    compressibility_au= 0.001, taup=1 (0.5-5)
    或者 compressibility_au= 0.01, taup=10 (5-50)
    """
    atoms.calc = calc
    self.get_md_control_velocitydistribution_MaxwellBZ(
        atoms=atoms,
        temperature_K=temperature_K,
    )
    self.get_md_control_Stationary(atoms=atoms)
    self.get_md_control_ZeroRotation(atoms=atoms)

    if loginterval is None:
      loginterval = int(run_steps/num_logs)  # 10 个记录
    dyn = self.get_md_obj_NPTBerendsen(atoms=atoms,
                                       timestep=timestep,
                                       temperature_K=temperature_K,
                                       pressure_au=pressure_au,
                                       mask=mask,
                                       compressibility_au=compressibility_au,
                                       taut=taut,
                                       taup=taup,
                                       loginterval=loginterval,
                                       is_save_log=False,
                                       is_save_traj=is_save_traj,
                                       trajectory=fname_traj,
                                       )
    # 自定义输出日志
    if is_save_log:
      dyn = self.md_attach_custom_function(atoms=atoms,
                                           dyn=dyn,
                                           fname_log=fname_log,
                                           loginterval=loginterval,
                                           thermo_name_list=thermo_name_list,
                                           decimals=df_decimals,
                                           is_append_log=is_append_log,
                                           )
    dyn.run(steps=run_steps)
    return dyn

  def md_NPT_analysis(self, directory='.',
                      fname_csv='md_equilibrate.log',
                      fname_traj='md_equilibrate.traj',):
    df = self.get_df_from_csv(directory=directory,
                              fname_csv=fname_csv)
    df.plot(x='steps',
            y=['lx[A]',
               # 'vol[A^3]'
               ], marker='o',)
    from .aseLearn import Model
    atoms: ase.Atoms = Model().get_atoms_from_traj(
        directory=directory,
        fname_traj=fname_traj,
        index=':')
    ase.visualize.view(atoms)
    return None

  def md_NPT_uptemp(self,
                    atoms: ase.Atoms,
                    calc: ase.calculators.calculator.Calculator,
                    T_start=1000,
                    T_end=2000,
                    timestep=5,
                    pressure_au=0.0,
                    mask=(1, 1, 1),
                    compressibility_au=0.001,
                    taut=100,
                    taup=1,
                    run_steps=2000,
                    loginterval=100,
                    is_save_log=True,
                    thermo_name_list=['step', 'time', 'temperature',
                                      'pe[eV]', 'ke',  'vol',
                                      'lx', 'press',],
                    df_decimals=3,
                    fname_log='md_uptemp.log',
                    is_save_traj=True,
                    fname_traj='md_uptemp.traj',
                    ):
    """ 效果不好: 读取atoms 后 其温度还是0, 相当于从0K开始, 建议使用 self.md_NPT_euilibreate_and_uptemp()
    ---
    以后可以试试将温度平衡后的atoms 保存再读取试试
    ---
    atoms: 是温度平衡后读取 traj中的 atoms, 里面包含了原子的速度
    compressibility_au= 0.001, taup=1 (0.1-10)
    或者 compressibility_au= 0.01, taup=10 # good 
    """
    atoms.calc = calc
    self.get_md_control_Stationary(atoms=atoms)
    self.get_md_control_ZeroRotation(atoms=atoms)
    dyn = self.get_md_obj_NPTBerendsen(atoms=atoms,
                                       timestep=timestep,
                                       temperature_K=T_start,
                                       pressure_au=pressure_au,
                                       mask=mask,
                                       compressibility_au=compressibility_au,
                                       taut=taut,
                                       taup=taup,
                                       is_save_log=False,
                                       logfile=fname_log,
                                       is_save_traj=is_save_traj,
                                       trajectory=fname_traj,
                                       loginterval=loginterval,)
    if is_save_log:
      # 自定义输出日志
      dyn = self.md_attach_custom_function(atoms=atoms,
                                           dyn=dyn,
                                           fname_log=fname_log,
                                           loginterval=loginterval,
                                           thermo_name_list=thermo_name_list,
                                           decimals=df_decimals,
                                           is_append_log=False,
                                           )
    # 升温
    dyn = self.md_attach_temperature(dyn=dyn,
                                     T_start=T_start,
                                     T_end=T_end,
                                     run_steps=run_steps,
                                     )
    return dyn

  def md_NPT_euilibreate_and_uptemp(self,
                                    atoms: ase.Atoms,
                                    calc: ase.calculators.calculator.Calculator,
                                    T_start=3690,
                                    T_end=5300,
                                    run_steps_equilibrate=1000,
                                    run_md_perK=10,
                                    run_steps_uptemp=None,
                                    pressure_au=0.0,
                                    compressibility_au=0.001,
                                    taut=100,
                                    taup=1,
                                    timestep=5,
                                    loginterval=None,
                                    mask=(1, 1, 1),
                                    is_save_log=True,
                                    thermo_name_list=['step', 'time', 'temperature',
                                                      'pe[eV]', 'ke',  'vol',
                                                      'lx', 'press',],
                                    df_decimals=3,
                                    fname_log_equilibrate='md_equilibrate.log',
                                    fname_log_uptemp='md_uptemp.log',
                                    is_save_traj=True,
                                    fname_traj_equilibrate='md_equilibrate.traj',
                                    fname_traj_uptemp='md_uptemp.traj',
                                    ):
    """
    compressibility_au= 0.001, taup=1 (0.1-10)
    或者 compressibility_au= 0.01, taup=10 # good 
    """
    # 1.温度平衡
    dyn = self.md_NPT(atoms=atoms,
                      calc=calc,
                      run_steps=run_steps_equilibrate,
                      temperature_K=T_start,
                      pressure_au=pressure_au,
                      compressibility_au=compressibility_au,
                      taut=taut,
                      taup=taup,
                      timestep=timestep,
                      loginterval=loginterval,
                      mask=mask,
                      is_save_log=is_save_log,
                      thermo_name_list=thermo_name_list,
                      df_decimals=df_decimals,
                      fname_log=fname_log_equilibrate,
                      is_append_log=False,
                      is_save_traj=is_save_traj,
                      fname_traj=fname_traj_equilibrate,
                      )

    # 2. 升高温度
    if run_steps_uptemp is None:
      run_steps_uptemp = int(run_md_perK * abs(T_end - T_start))
      print(f'run_steps is None, set to {run_steps_uptemp}')
    if loginterval is None:
      loginterval = int(run_steps_uptemp/50)
    dyn = self.md_NPT_uptemp(atoms=atoms,
                             calc=calc,
                             T_start=T_start,
                             T_end=T_end,
                             timestep=timestep,
                             pressure_au=pressure_au,
                             mask=mask,
                             compressibility_au=compressibility_au,
                             taut=taut,
                             taup=taup,
                             run_steps=run_steps_uptemp,
                             loginterval=loginterval,
                             is_save_log=is_save_log,
                             thermo_name_list=thermo_name_list,
                             df_decimals=df_decimals,
                             fname_log=fname_log_uptemp,
                             is_save_traj=is_save_traj,
                             fname_traj=fname_traj_uptemp,
                             )

    dyn.run(steps=run_steps_uptemp)
    return dyn

  def get_melt_T_md_NPT_euilibreate_and_uptemp(
      self,
      atoms: ase.Atoms,
      calc: ase.calculators.calculator.Calculator,
      volume_ratio_stop=1.119,
      T_start=3690,
      T_end=5300,
      run_steps_equilibrate=1000,
      run_md_perK=10,
      run_steps_uptemp=None,
      pressure_au=0.0,
      compressibility_au=0.001,
      taut=100,
      taup=1,
      timestep=5,
      loginterval=None,
      mask=(1, 1, 1),
      is_save_log=True,
      thermo_name_list=['step', 'time', 'temperature',
                        'pe[eV]', 'ke',  'vol',
                        'lx', 'press',],
      df_decimals=3,
      fname_log_equilibrate='md_equilibrate.log',
      fname_log_uptemp='md_uptemp.log',
      is_save_traj=True,
      fname_traj_equilibrate='md_equilibrate.traj',
      fname_traj_uptemp='md_uptemp.traj',
  ):

    initial_volume = atoms.get_volume()
    # 1.温度平衡
    dyn = self.md_NPT(atoms=atoms,
                      calc=calc,
                      run_steps=run_steps_equilibrate,
                      temperature_K=T_start,
                      pressure_au=pressure_au,
                      compressibility_au=compressibility_au,
                      taut=taut,
                      taup=taup,
                      timestep=timestep,
                      loginterval=loginterval,
                      mask=mask,
                      is_save_log=is_save_log,
                      thermo_name_list=thermo_name_list,
                      df_decimals=df_decimals,
                      fname_log=fname_log_equilibrate,
                      is_append_log=False,
                      is_save_traj=is_save_traj,
                      fname_traj=fname_traj_equilibrate,
                      )

    # 2. 升高温度
    if run_steps_uptemp is None:
      run_steps_uptemp = int(run_md_perK * abs(T_end - T_start))
      print(f'run_steps is None, set to {run_steps_uptemp}')
    if loginterval is None:
      loginterval = int(run_steps_uptemp/50)
    dyn = self.md_NPT_uptemp(atoms=atoms,
                             calc=calc,
                             T_start=T_start,
                             T_end=T_end,
                             timestep=timestep,
                             pressure_au=pressure_au,
                             mask=mask,
                             compressibility_au=compressibility_au,
                             taut=taut,
                             taup=taup,
                             run_steps=run_steps_uptemp,
                             loginterval=loginterval,
                             is_save_log=is_save_log,
                             thermo_name_list=thermo_name_list,
                             df_decimals=df_decimals,
                             fname_log=fname_log_uptemp,
                             is_save_traj=is_save_traj,
                             fname_traj=fname_traj_uptemp,
                             )
    # 加入判断
    dyn = self.md_attach_custom_check_volume_ratio(
        initial_volume=initial_volume,
        atoms=atoms,
        dyn=dyn,
        volume_ratio_stop=volume_ratio_stop,
        fname_traj=fname_traj_uptemp,
    )
    try:
      dyn.run(steps=run_steps_uptemp)
    except RuntimeError as e:
      print(str(e))
    T_melt = atoms.get_temperature()
    print(f'T_melt is {T_melt}')
    return dyn
