# 材料模拟环境

## 安装

主要基于ase, janus-core 包

- 安装:
    常规:
        pip install soft_learn_project
        pip install git+<https://gitee.com/wangjl580/soft_learn_project.git> # 安装最新版本
    推荐:
        git clone <https://gitee.com/wangjl580/soft_learn_project.git>
        cd soft_learn_project
        pip install -e . # 安装当前目录的代码

## 用法

- 示例:

```python
from soft_learn_project.ase_learn import aseLearn
al = aseLearn.AseLearn()
# 使用不同的计算器
# calc = al.CalcModule.get_calc_lammps(
#     directory='/Users/wangjinlong/job/tmp/t1', )
# calc = al.CalcModule.get_calc_vasp(
#     directory='/Users/wangjinlong/job/tmp/t1', 
#     kpts=(3,3,3))
# calc = al.CalcModule.get_calc_gpaw(
#     directory='/Users/wangjinlong/job/tmp/t1',
#     kpts=(3,3,3))
calc = al.CalcModule.get_calc_MLIP(  
    directory='/Users/wangjinlong/job/tmp/t1', )
atoms = al.Model.get_atoms_normal_crsytal(name='W', cubic=True)

al.calc_lattice_constant(atoms=atoms,
                         calc=calc,
                         is_recalc=True
                         )
```

最新的源码: <https://gitee.com/wangjl580/soft_learn_project/tree/main>

## 说明

可以用于vasp, lammps, gpaw, MLIP 等计算器
    对于vasp 需要安装 vasp 可执行文件
        1. 从 <https://www.vasp.at/> 下载 vasp 编译
    对于 lammps 需要安装 lammps的 python 包, 使 import lammps 可以使用,
        1. git clone <https://gitlab.com/lammps/lammps.git>
        2. cd lammps
        3. cd src
        4. make mac_mpi mode=shlib -j8
        5. make install-python
