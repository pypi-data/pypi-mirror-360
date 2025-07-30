import re
from tkinter import N, NO
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import ase
import ase.calculators.vasp
import ase.io
import ase.thermochemistry
import ase.neighborlist
import copy
from vasp_learn import dataBase, base
from py_package_learn.functools_learn import functoolsLearn


class Tjt_台阶图_old(metaclass=functoolsLearn.AutoDecorateMeta):
  def __init__(self) -> None:
    self.DataBase = dataBase.DataBase()
    pass

  # 用到的方法
  def get_rawdata_ORR(self, is_sol_eff=False, is_amend=True):
    """用到的方法 计算 O2的gibbs 自由能时 用这个, 而计算吸附能还是用计算的
    获得O2的 gibbs energy 仅仅用于画自由能变图
    标准氢电极中实验满足 2*gibbs_energy_H2O - 2*gibbs_energy_H2 - gibbs_energy_O2 = -4.92
    而O2的gibbs 能计算不准确, 因此使用计算式获得 gibbs_energy_O2 = 2*gibbs_energy_H2O - 2 * gibbs_energy_H2 + 4.92

    Returns:
        _type_: _description_
    """
    rawdata = {}
    for key in ["O2", "H2", "H2O"]:
      key_dbname = (
          f"{key}-sol_eff-vibration" if is_sol_eff else f"{key}-vibration"
      )
      e = self.DataBase.db.get(f"name={key_dbname}").gibbs_energy
      rawdata.update({key: e})

    if is_amend:  # 是否使用4.92 来修正
      rawdata["O2"] = 2 * rawdata["H2O"] - 2 * rawdata["H2"] + 4.92
    return rawdata

  def get_formular_list(self, substrate="CoN4", is_O2=True):
    """这个是对于 OER 在 CoN4 衬底上的特定反应
    formular_list=['1*CoN4 + 2*H2O',
                    '1*OH_CoN4 + 1*H2O + 1/2 *H2',
                    '1*O_CoN4 + 1*H2O + 2/2*H2',
                    '1*O2H_CoN4 +3/2 * H2',
                    '1*O2_CoN4 + 4/2 * H2',
                    '1*CoN4 + 1*O2 + 2*H2',]
    Returns:
        _type_: _description_
    """
    # 电化学反应过程状态的吉布斯能计算式
    if is_O2:
      formular_list = [
          f"1*{substrate} + 2*H2O",
          f"1*OH_{substrate} + 1*H2O + 1/2 *H2",
          f"1*O_{substrate} + 1*H2O + 2/2*H2",
          f"1*O2H_{substrate} +3/2 * H2",
          f"1*O2_{substrate} + 4/2 * H2",
          f"1*{substrate} + 1*O2 + 2*H2",
      ]
    else:
      formular_list = [
          f"1*{substrate} + 2*H2O",
          f"1*OH_{substrate} + 1*H2O + 1/2 *H2",
          f"1*O_{substrate} + 1*H2O + 2/2*H2",
          f"1*O2H_{substrate} +3/2 * H2",
          # f'1*O2_{substrate} + 4/2 * H2',
          f"1*{substrate} + 1*O2 + 2*H2",
      ]
    return formular_list

  def get_label_list(self, formular_list, replace_str="CoN4"):
    label_list = []
    for formular in formular_list:
      label = "*" + formular.split("+")[0].split("*")[1].strip().replace(
          replace_str, ""
      )
      if label.endswith("_"):
        label = label.replace("_", "")
      label_list.append(label)
    # 处理数字为角标
    label_list_new = []
    for label in label_list:
      label: str
      try:
        search = re.search(r"\d", label).group()
        label_new = label.replace(f"{search}", f"$_{search}$")
      except:
        label_new = label
      label_list_new.append(label_new)
    return label_list_new

  def get_key_name(self, formular_list):
    """从公式列表中获取 所有的关键词集合 用于之后获取 rawdata

    Args:
        formular_list (_type_): _description_

    Returns:
        _type_: _description_
    """
    key_name = set()
    for formular in formular_list:
      for formular_part in formular.split("+"):
        key_name.add(formular_part.split("*")[-1].strip())
    return key_name

  def get_rawdata(
      self, key_name, name_substrate="CoN4", is_sol_eff=False, is_amend=True
  ):
    """合并计算的数据, 获得的是自由能: gibbs energy / helmholtz_energy

    Args:
        key_name (_type_): _description_
        name_substrate (str, optional): _description_. Defaults to 'CoN4'.

    Returns:
        _type_: _description_
    """

    rawdata = {}
    for key in key_name:
      key_dbname = (
          f"{key}-sol_eff-vibration" if is_sol_eff else f"{key}-vibration"
      )
      if key == name_substrate:
        try:  # 对于特殊的衬底是有吸附物之后的衬底, 因此有振动
          e = self.DataBase.db.get(f"name={key_dbname}").helmholtz_energy
        except:  # 衬底没有振动
          key_dbname = key_dbname.replace("-vibration", "")
          e = self.DataBase.db.get(f"name={key_dbname}").energy
      else:
        try:
          e = self.DataBase.db.get(f"name={key_dbname}").helmholtz_energy
        except:
          e = self.DataBase.db.get(f"name={key_dbname}").gibbs_energy
      rawdata.update({key: e})
    rawdata_ORR = self.get_rawdata_ORR(
        is_sol_eff=is_sol_eff, is_amend=is_amend)
    rawdata.update(rawdata_ORR)

    return rawdata

  def cacl_formula(self, formular, rawdate):
    """formular, e.g.: '1*OH_P_N3_graphene + 1*H2O + 1/2 *H2',

    Args:
        formular (_type_): _description_
        rawdate (_type_): 公式中每一项的 Gibbs 自由能

    Returns:
        _type_: _description_
    """
    name_list = []
    coeff_list = []
    for i in formular.split("+"):
      if "*" in i.strip():
        k = i.split("*")
        coe, name = eval(k[0].strip()), k[1].strip()
      else:
        coe = 1
        name = i.strip()
      coeff_list.append(coe)
      name_list.append(name)

    value_list = [rawdate[name] for name in name_list]
    coeff_array = np.array(coeff_list)
    value_array = np.array(value_list)
    result = (coeff_array * value_array).sum()
    return result

  def get_result_array(self, formular_list, rawdata):
    """此时的能量数组为 U = 0 时的结果

    Args:
        formular_list (_type_): _description_
        rawdata (_type_): _description_

    Returns:
        _type_: _description_
    """
    result_list = []
    for formular in formular_list:
      result = self.cacl_formula(formular=formular, rawdate=rawdata)
      result_list.append(result)
    result_array = np.array(result_list)
    result_array -= result_array[0]
    return result_array

  def get_result_array_with_eU(self, result_array, start_index=1, eU=1.23):
    """对于OER 反应
    增加电压, 对于H2O 的解离 每去掉一个H 和 e+ 能量就少1.23 eV

    Args:
        result_array (_type_): _description_
        start_index (int, optional): _description_. Defaults to 1.

    Returns:
        _type_: _description_
    """

    result_array = copy.deepcopy(result_array)
    delta_U = 0
    for index in range(result_array.__len__()):
      if index >= start_index:
        delta_U += eU
        if delta_U > eU * 4:
          delta_U = eU * 4
        result_array[index] -= delta_U

    return result_array

  def get_plot_data(
      self,
      substrate="B_N_sub",
      eU=1.23,
      reverse=False,
      show_O2=True,
      is_sol_eff=False,
      is_amend=True,
      is_O2=True,
  ):
    formular_list = self.get_formular_list(substrate=substrate,
                                           is_O2=is_O2)
    key_name = self.get_key_name(formular_list=formular_list)
    rawdata = self.get_rawdata(
        key_name=key_name,
        name_substrate=substrate,
        is_sol_eff=is_sol_eff,
        is_amend=is_amend,
    )
    label_list = self.get_label_list(
        formular_list=formular_list, replace_str=substrate
    )
    result_array = self.get_result_array(
        formular_list=formular_list, rawdata=rawdata
    )
    result_array_with_eU = self.get_result_array_with_eU(
        result_array=result_array, start_index=1, eU=eU
    )

    data_plot = list(result_array_with_eU)
    # 避免第一个和最后一个是非常小的负数
    data_plot[0] = abs(data_plot[0]) if abs(
        data_plot[0]) < 1e-5 else data_plot[0]
    data_plot[-1] = (
        abs(data_plot[-1]) if abs(data_plot[-1]) < 1e-5 else data_plot[-1]
    )

    if reverse:
      data_plot.reverse()
      label_list.reverse()

    if not show_O2:  # 如果不显示O2 的数据
      index = label_list.index("*O$_2$")
      data_plot.pop(index)
      label_list.pop(index)

    data = {f"data_plot": data_plot,
            f"label_list": label_list, "label": substrate}
    return data


class Tjt_台阶图(metaclass=functoolsLearn.AutoDecorateMeta):
  def __init__(self, font_size=12) -> None:
    r""" 学习网页: https://www.bilibili.com/video/BV1PJ411A7jw?spm_id_from=333.788.recommend_more_video.-1&vd_source=5ec84b7f759de5474190c5f84b86a564
    超详细电催化台阶图计算步骤，细节拉满【电催化课程1】
    https://www.bilibili.com/video/BV1Q7411k7NU/?spm_id_from=333.788.recommend_more_video.-1&vd_source=5ec84b7f759de5474190c5f84b86a564

    一般来说，**有效的 ORR 催化剂** 需要具有较低的过电位 \( \eta \)，即 \( E_{\text{max-diff}} \) 不能太大。根据 ORR 计算公式：  

    \[
    \eta = 1.23V - E_{\text{max-diff}}
    \]

    要保证催化剂在**实际工作电位**（如 0.9V 左右）下具有较好的催化活性，经验上要求：  

    \[
    E_{\text{max-diff}} \leq 0.9V
    \]

    ### **具体分类**  
    - **优异的催化剂**：\( E_{\text{max-diff}} \leq 0.45 \) eV（对应 \(\eta \leq 0.78V\)）  
      - 例如 Pt(111) 的 \( E_{\text{max-diff}} \approx 0.91 \) eV，对应 \(\eta \approx 0.32V\)，已经是很好的催化剂。  
    - **可以接受的催化剂**：\( 0.45 \text{ eV} \leq E_{\text{max-diff}} \leq 0.9 \) eV（对应 \(\eta \approx 0.3 - 0.78V\)）  
      - 这些催化剂可能比 Pt 差一些，但仍然可以用于 ORR。  
    - **催化性能较差**：\( E_{\text{max-diff}} > 0.9 \) eV（对应 \(\eta > 0.3V\)）  
      - 过电位太高，意味着反应动力学较慢，催化活性较差，通常不被认为是高效的 ORR 催化剂。  

    ### **结论**
    如果 \(E_{\text{max-diff}} \leq 0.9\) eV，说明材料可能是有效的催化剂；如果 \(E_{\text{max-diff}}\) 远高于 0.9 eV，则过电位过高，不适合作为高效 ORR 催化剂。
    ---
    可以跟理想的催化剂进行对比, 理想的催化剂就是每个H还原的电子步, 能量都降低1.23 eV (fazio2014boron).
    *O2的形成不取决于所施加的电势.
    注意，在第一个还原步骤之前，有一个能量成本(0.46 eV)来吸附O2，然而，这并不取决于所施加的电势. Note that there is an energy cost(0.46 eV) to adsorb O2, preceding the first reduction step, which, however, is not dependent on the applied potential..

    计算时要保证slab 的目录名或者说dbname 和 adsorbate + slab 中 slab的名字一致, 才可以用下面的方法

    工作电位: 电催化剂的工作电位是指在催化剂促进的电化学反应中，保持所有中间反应都是放热的最高电极电位。换句话说，工作电位是使得整个电化学反应过程中的所有元素反应都是放热的最高电极电位。在电催化过程中，中间反应的能量变化是至关重要的，因为这些中间反应的能量变化将直接影响电极过程的效率和可行性。
    工作电位的概念是在实际电催化过程中特别重要的，因为在工作电位下，所有涉及的中间反应都是放热的，这意味着整个电化学反应过程是能量有利的，有利于推动反应向前进行，从而提高反应速率和效率。因此，工作电位通常被视为评估电催化剂性能的重要指标之一。

    在氧还原反应（ORR）中，工作电位越高并不一定表示催化剂越好。事实上，对于氧还原反应而言，催化剂的性能评价不仅仅取决于工作电位的高低，还取决于许多其他因素，包括活性、选择性、稳定性等。

    虽然较高的工作电位可能意味着更有利的电催化过程，但这并不一定意味着催化剂具有更高的活性或更好的性能。有时候，某些催化剂可能具有较高的工作电位，但其活性较低，导致氧还原反应的速率较慢或产生较低的电流密度。另外，催化剂的选择性和稳定性也是评价催化剂性能的重要因素。

    因此，在评价氧还原反应催化剂时，除了考虑工作电位外，还需要综合考虑其他因素，如活性、选择性和稳定性等。最终的目标是找到在工作条件下具有良好电化学性能和长期稳定性的催化剂。
    抗中毒性：某些反应物或中间产物可能会中毒催化剂表面的活性位点，从而降低催化剂的活性。因此，抗中毒性也是评价催化剂的一个重要指标。
    活性：催化剂的活性指的是其促进氧还原反应的能力。具有较高活性的催化剂可以在较低的过电位下实现较高的反应速率和电流密度，这意味着它们可以更有效地促进氧还原反应，从而提高电化学设备的性能。在电化学领域，活性通常与过电位相关联，但是活性与过电位的关系并不总是线性的，而是取决于具体的反应和催化剂。一般来说，对于氧还原反应（ORR）而言，较低的过电位确实通常意味着更高的活性，因为它意味着在更低的电压下实现了更高的反应速率。过电位是指在电化学反应中需要施加的电压超过了理论的电极电压（即在不受电极限制时需要的电压）。因此，较低的过电位意味着可以在更低的电压下实现更快的反应速率，这通常意味着更高的催化活性。
    选择性：催化剂的选择性指的是其在氧还原反应中产生特定产物的能力。对于氧还原反应而言，主要关注的是产生水的选择性。高选择性的催化剂能够有效地将氧气还原成水，而不会生成其他副产物，从而提高反应的纯度和效率。

    稳定性：催化剂的稳定性指的是其在长时间运行过程中的性能保持能力。稳定性较好的催化剂可以在长期使用过程中保持其活性和选择性，而不会发生失活或性能下降，从而延长催化剂的使用寿命。
    """

    self.DataBase = dataBase.DataBase()
    self.energydata = {}
    from py_package_learn.matplotlib_learn import matplotlibLearn
    self.matplotlibLearnFeatures = matplotlibLearn.Features(
        font_size=font_size)
    pass

  def get_delta_GpH(self, pH):
    """pH值或者说酸碱环境对 吉布斯自由能的影响
    下面只使用自由能 表示 吉布斯自由能
    'Origin of the overpotential for oxygen reduction at a fuel-cell cathode': norskov2004origin
    Args:
        pH (_type_): _description_

    Returns:
        _type_: _description_
    """
    # G(pH) )-kT ln[H+]) kT ln 10 × pH.
    from scipy import constants

    k_B = constants.k  # k_B
    T = 298.15
    # k_B*T*np.log(10) *pH /e # 不要忘记转化为eV
    # constants.k * 298.15/constants.e * np.log(10) = 0.05915934968478234
    delta_GpH = k_B * T * np.log(10) / constants.e * pH
    delta_GpH = 0.05915934968478234 * pH
    return delta_GpH

  def zsd_知识点(self):
    delta_G_酸性 = self.get_delta_G(ph=0)
    delta_G_碱性 = self.get_delta_G(pH=14)

  def get_delta_G(self, pH=0):
    """gibbs_energy 考虑 酸性和碱性环境
    酸性条件下, pH = 0
    https://www.bilibili.com/video/BV1PJ411A7jw?spm_id_from=333.788.recommend_more_video.-1&vd_source=5ec84b7f759de5474190c5f84b86a564

    Args:
        pH (int, optional): _description_. Defaults to 0.

    Returns:
        _type_: _description_
    """
    # 标准氢电极中
    # 2*gibbs_energy_H2O - 2*gibbs_energy_H2 - gibbs_energy_O2  # 应该=-4.92
    # 由上式可以计算 O2 的gibbs_energy
    gibbs_energy_H2O = -14.097652417444566
    gibbs_energy_H2 = -6.738036452984931
    gibbs_energy_O2 = 2 * gibbs_energy_H2O - 2 * gibbs_energy_H2 + 4.92
    # 考虑pH
    delta_G = 2 * gibbs_energy_H2O - (
        4 * (0.5 * gibbs_energy_H2 - 0.0592 * pH) + gibbs_energy_O2
    )
    return delta_G

  # 常用的方法
  def get_eU_array(self, eU=1.23,
                   is_consider_O2=True,
                   is_ORR=True):

    v_list = [eU * 0, 1 * eU, 2 * eU, 3 * eU, 4 * eU]
    if is_consider_O2:
      v_list.insert(1, eU * 0,)
    eU_array = np.array(v_list)  # 对于ORR
    if not is_ORR:  # 对于 OER
      eU_array = eU_array[::-1]-4.92
    return eU_array

  def get_formular_list(self,
                        dbname_slab="CoN4",
                        ORR=True,
                        HER=False,
                        is_consider_O2=True):
    """这个是对于 OER 在 CoN4 衬底上的特定反应
    formular_list=['1*CoN4 + 2*H2O',
                    '1*OH_CoN4 + 1*H2O + 1/2 *H2',
                    '1*O_CoN4 + 1*H2O + 2/2*H2',
                    '1*O2H_CoN4 +3/2 * H2',
                    '1*O2_CoN4 + 4/2 * H2',
                    '1*CoN4 + 1*O2 + 2*H2',]
    Returns:
        _type_: _description_
    """

    # 电化学反应过程状态的吉布斯能计算式
    formular_list_OER = [
        f"1*{dbname_slab} + 4/2*H2O",
        f"1*OH_{dbname_slab} + 2/2*H2O + 1/2*H2",
        f"1*O_{dbname_slab} + 2/2*H2O + 2/2*H2",
        f"1*O2H_{dbname_slab} + 3/2*H2",
        # f"1*O2_{dbname_slab} + 4/2*H2", # -1 这个位置
        f"1*{dbname_slab} + 2/2*O2 + 4/2*H2",
    ]
    if is_consider_O2:
      formular_list_OER.insert(-1, f"1*O2_{dbname_slab} + 4/2*H2")
    else:
      pass
    if ORR:
      formular_list_OER.reverse()
      return formular_list_OER
    elif HER:
      formular_list = [
          f"1*{dbname_slab} + 2/2*H2",
          f"1*H_{dbname_slab} + 1/2*H2",
          f"1*{dbname_slab} + 2/2*H2",
      ]
      return formular_list
    else:
      return formular_list_OER

  def parse_formular(self,
                     formular="O2H_graphene72atoms + 3/2*H2",):
    """_summary_

    Args:
        formular (str, optional): _description_. Defaults to 'O2H_graphene72atoms + 5/2*H2'.

    Returns: coeff_list, dbname_list
        _type_: _description_
    """

    dbname_list = []
    coeff_list = []
    for i in formular.split("+"):
      if "*" in i.strip():
        k = i.split("*")
        coe, name = eval(k[0].strip()), k[1].strip()
      else:
        coe = 1
        name = i.strip()
      coeff_list.append(coe)  # [1, 2.5]
      dbname_list.append(name)  # ['O2H_graphene72atoms', 'H2']

    return coeff_list, dbname_list

  def get_energy_system(self,
                        formular="O2H_graphene72atoms + 3/2*H2",
                        energy_name="energy|free_energy",
                        is_sol_eff=True,
                        is_ammend_O2=True,):
    """计算系统的总能量

    Args:
        system_str (str, optional): _description_. Defaults to 'O2H_graphene72atoms + 5/2*H2'.
        energy_name (str, optional): 'energy' or 'free_energy'. Defaults to 'energy'.
        is_sol_eff (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """

    coeff_list, dbname_list = self.parse_formular(formular=formular)
    # 获取能量列表
    energy_list = []
    for dbname in dbname_list:
      if dbname in self.energydata.keys():
        energy = self.energydata[dbname]
      else:
        energy = self.DataBase.get_energy(dbname=dbname,
                                          directory=None,
                                          energy_name=energy_name,
                                          is_sol_eff=is_sol_eff,
                                          is_ammend_O2=is_ammend_O2,
                                          )
        self.energydata.update({dbname: energy})
      energy_list.append(energy)
    # 计算系统的总能量
    energy_system = (np.array(coeff_list) * np.array(energy_list)).sum()
    return energy_system

  def get_energy_array(self,
                       formular_list,
                       energy_name="free_energy",
                       is_sol_eff=True,
                       is_ammend_O2=True,
                       ):
    # 此时的能量数组为 U = 0 时的结果
    energy_array = np.array([])
    for formular in formular_list:
      energy = self.get_energy_system(
          formular=formular,
          energy_name=energy_name,
          is_sol_eff=is_sol_eff,
          is_ammend_O2=is_ammend_O2,
      )
      energy_array = np.append(energy_array, energy)
    energy_array -= energy_array[0]

    return energy_array

  def get_energy_array_with_eU(
      self,
      energy_array,
      is_consider_O2=True,
      eU=1.23,
      is_ORR=True,
  ):
    """对于OER 反应
    增加电压, 对于H2O 的解离 每去掉一个H 和 e+ 能量就少1.23 eV

    Args:
        result_array (_type_): _description_
        start_index (int, optional): _description_. Defaults to 1.

    Returns:
        _type_: _description_
    """

    eU_array = self.get_eU_array(eU=eU,
                                 is_consider_O2=is_consider_O2,
                                 is_ORR=is_ORR)[: len(energy_array)]
    energy_array_with_eU = energy_array + eU_array
    # 使得显示为-0.0 的结果变为0.0
    for index in np.arange(len(energy_array_with_eU)):
      if abs(energy_array_with_eU[index]) < 1e-4:
        energy_array_with_eU[index] = 0.0
      return energy_array_with_eU.round(3)

  def get_label(self,
                formular="1*O2H_graphene72atoms + 5/2*H2",
                dbname_slab="graphene72atoms",
                ):
    label = ("*"
             + formular.split("+")[0]
             .split("*")[1]
             .replace(dbname_slab, "")
             .replace("_", "")
             .strip().replace('O2H', 'OOH').replace('O2', 'O$_2$')
             )
    return label

  def get_label_list(self, formular_list,
                     dbname_slab="graphene72atoms"):
    """label_list = ['*','*O2','*O2H','*O','*OH','*']

    Args:
        formular_list (_type_): _description_
        dbname_slab (str, optional): _description_. Defaults to 'graphene72atoms'.

    Returns:
        _type_: _description_
    """

    label_list = []
    for formular in formular_list:
      label = self.get_label(formular=formular,
                             dbname_slab=dbname_slab)
      label_list.append(label)
    return label_list

  def get_overpotential(self, result_array_with_eU_list,):
    """过电势越低说明是越好的催化剂

    Args:
        result_array_with_eU_list (_type_): _description_

    Returns: overpotential_list
        _type_: _description_
    """

    overpotential_list = []
    for result_array_with_eU in result_array_with_eU_list:
      overpotential_arr = np.diff(result_array_with_eU)
      overpotential = overpotential_arr.max()
      # print(overpotential_arr, overpotential_arr.max())
      overpotential_list.append(overpotential)
    return overpotential_list

  def get_plot_data(self,
                    dbname_slab_list,
                    line_label_list=None,
                    energy_name="free_energy",
                    is_sol_eff=True,
                    is_ammend_O2=True,
                    eU=1.23,
                    ORR=True,
                    is_consider_O2=True,
                    HER=False,
                    ):
    """获取画图数据

    Args:
        dbname_slab (_type_): _description_
        energy_name (str, optional): _description_. Defaults to 'free_energy'.
        is_sol_eff (bool, optional): _description_. Defaults to True.
        is_ammend_O2 (bool, optional): _description_. Defaults to True.
        eU (float, optional): _description_. Defaults to 1.23.
        line_label (_type_, optional): _description_. Defaults to None.

    Returns: plot_data_dict_list
        _type_: _description_
    """

    plot_data_dict_list = []
    line_label_list = dbname_slab_list if line_label_list is None else line_label_list
    for dbname_slab, line_label in zip(dbname_slab_list, line_label_list):
      formular_list = self.get_formular_list(dbname_slab=dbname_slab,
                                             ORR=ORR,
                                             HER=HER,
                                             is_consider_O2=is_consider_O2,
                                             )
      energy_array = self.get_energy_array(
          formular_list,
          energy_name=energy_name,
          is_sol_eff=is_sol_eff,
          is_ammend_O2=is_ammend_O2,
      )
      energy_array_with_eU = self.get_energy_array_with_eU(
          energy_array=energy_array, eU=eU,
          is_consider_O2=is_consider_O2,
          is_ORR=ORR,
      )

      label_list = self.get_label_list(
          formular_list=formular_list, dbname_slab=dbname_slab
      )
      overpotential = self.get_overpotential(
          result_array_with_eU_list=[energy_array_with_eU]
      )[0]
      plot_data = {"energy_array_with_eU": energy_array_with_eU,
                   "label_list": label_list,
                   "line_label": line_label,
                   "overpotential": overpotential, }
      plot_data_dict_list.append(plot_data)
    return plot_data_dict_list

  def get_overpotential_wrapper(self,
                                dbname_slab_list,
                                is_consider_O2=True):
    """更简便的获得 overpotential_list

    Args:
        dbname_slab_list (_type_): _description_

    Returns:
        _type_: _description_
    """
    plot_data_dict_list = self.get_plot_data(dbname_slab_list=dbname_slab_list,
                                             is_consider_O2=is_consider_O2)

    energy_array_with_eU_list = []
    for plot_data in plot_data_dict_list:
      energy_array_with_eU = plot_data['energy_array_with_eU']
      energy_array_with_eU_list.append(energy_array_with_eU)
    overpotential_list = self.get_overpotential(
        result_array_with_eU_list=energy_array_with_eU_list)

    return np.array(overpotential_list)

  def plot(self,
           energy_array,
           label_list,
           line_label="graphene72atoms",
           fig=None,
           ax=None,
           color="k",
           va="bottom",
           ylim=None,
           legend_loc='best',  # 0
           legend_fontsize='small',
           is_save=False,
           fname="tjt_台阶图.pdf",
           dpi='figure',
           ):

    # data_plot
    data_plot = np.array([[v, v] for v in energy_array])
    data_plot = data_plot.flatten()
    data_plot = list(data_plot)

    # 绘图
    if (fig is None) and (ax is None):
      fig = plt.figure()
      ax = fig.add_subplot()

    for i in range(int(len(data_plot) / 2)):
      ax.plot(
          [2 * i, 2 * i + 1],
          [data_plot[2 * i], data_plot[2 * i + 1]],
          color=color,
          alpha=0.8,
      )  # 将相同数值的点用实线连接
      # 文本
      # ax.text(x=2*i+0.5, y=data_plot[2*i],
      #         s=label_list[i], ha='center', va='bottom')
      # bbox=dict(facecolor='white', alpha=0.5)
      ax.text(
          x=2 * i + 0.5,
          y=data_plot[2 * i],
          s=data_plot[2 * i].round(2),
          ha="center",
          va=va,
          color=color,
          alpha=0.7,
      )
    ax.plot(data_plot, ":", color=color, label=line_label, alpha=0.8)

    # ax.set_xticks([])
    ax.set_xticks([2 * idx + 0.5 for idx in range(int(len(data_plot) / 2))])
    ax.set_xticklabels(label_list)
    ax.set_xlabel("Reaction Pathway")
    ax.set_ylabel(r"$\Delta G \,(eV)$")
    legend = ax.legend(loc=legend_loc, fontsize=legend_fontsize)
    legend.get_frame().set_alpha(0.5)
    if ylim:
      ax.set_ylim(*ylim)
    if is_save:
      fig.savefig(fname, dpi=dpi)
      print(f'文件保存-> {fname}')
    return fig, ax

  def plot_lines_wrapper(self,
                         dbname_slab_list=['N6_graphene_config1',
                                           'N3_graphene',],
                         line_label_list=None,
                         energy_name="free_energy",
                         is_sol_eff=True,
                         is_ammend_O2=True,
                         eU=1.23,
                         ORR=True,
                         is_consider_O2=True,
                         HER=False,
                         label_list=None,
                         fig=None,
                         ax=None,
                         is_save=False,
                         fname='xxx/fig_orr.pdf',
                         legend_loc='lower left',
                         legend_fontsize='small'):
    """
    * 如果不提供 line_label_list 则使用 dbname_slab_list 作为图 label
    * is_amend: 是否修正O2的 gibbs 能量
    * is_sol_eff: 是否考虑溶剂化效应
    * 如果O2的氢化是速率决定步 那么溶剂化效应影响较大, 如果O的氢化为速率决定步, 溶剂化效应* 对吉布斯能变没什么影响, 单步加H也不影响, 以后就不研究单步加氢了对ORR的吉布斯能具体值有影响, 但对两个反应的吉布斯变没有影响
    ---
    * label_list 可以自定义为: ['*', '*O, *O', '*O, *OH', 'O', 'OH', '*']
    """

    if os.path.exists(fname) and is_save:
      print(f"{fname} 已经存在")
      return fname

    if (fig is None) and (ax is None):
      fig = plt.figure()
      ax = fig.add_subplot()

    plot_data_dict_list = self.get_plot_data(
        dbname_slab_list=dbname_slab_list,
        line_label_list=line_label_list,
        energy_name=energy_name,
        is_sol_eff=is_sol_eff,
        is_ammend_O2=is_ammend_O2,
        eU=eU,
        ORR=ORR,
        is_consider_O2=is_consider_O2,
        HER=HER,)

    for plot_data_dict, line_color in zip(plot_data_dict_list, self.matplotlibLearnFeatures.color_list):
      energy_array = plot_data_dict['energy_array_with_eU']
      if label_list is None:
        label_list = plot_data_dict['label_list']
      overpotential = round(plot_data_dict['overpotential'], 2)
      if line_label_list is None:
        line_label = plot_data_dict['line_label'] + \
            fr" ($\eta$={overpotential} eV)"
        pass
      else:
        line_label = line_label_list[0]
      self.plot(energy_array=energy_array,
                label_list=label_list,
                line_label=line_label,
                ax=ax,
                fig=fig,
                color=line_color,
                legend_loc=legend_loc,
                legend_fontsize=legend_fontsize,
                is_save=is_save,
                fname=fname,)
    return fname

  def plot_custom(self,
                  formular_list,
                  dbname_slab,
                  eU=1.23,
                  is_consider_O2=True,
                  label_list=None,
                  line_label=None,
                  energy_name="energy|free_energy",
                  is_sol_eff=False,
                  is_ammend_O2=True,
                  is_ORR=True,
                  line_color='black',
                  fig=None,
                  ax=None,
                  save=False,
                  fname='xxx/fig_orr.pdg',
                  legend_loc='best',
                  legend_fontsize=None,
                  ):
    """
    eU=1.23 可以是一个自定义列表, 而不用 [0,0,1.23,1.23*2,1.23*3,1.23*4]
    # 如果O2的氢化是速率决定步 那么溶剂化效应影响较大, 如果O的氢化为速率决定步, 溶剂化效应对吉布斯能变没什么影响, 单步加H也不影响, 
    ## 以后就不研究单步加氢了对ORR的吉布斯能具体值有影响, 但对两个反应的吉布斯变没有影响
    Args:
        formular_list (_type_): _description_
        dbname_slab (_type_): _description_
        eU (float, optional): _description_. Defaults to 1.23.
        energy_name (str, optional): _description_. Defaults to 'energy|free_energy'.
        is_sol_eff (bool, optional): _description_. Defaults to True.
        is_ammend_O2 (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """
    # 获取画图数据

    energy_array = self.get_energy_array(
        formular_list,
        energy_name=energy_name,
        is_sol_eff=is_sol_eff,
        is_ammend_O2=is_ammend_O2,
    )

    if isinstance(eU, list):  # 自定义 eU 列表
      energy_array_with_eU = energy_array + eU
    else:
      eU_array = self.get_eU_array(eU=eU,
                                   is_consider_O2=is_consider_O2,
                                   is_ORR=is_ORR)
      energy_array_with_eU = energy_array + eU_array[: len(energy_array)]

    if label_list is None:
      label_list = self.get_label_list(
          formular_list=formular_list, dbname_slab=dbname_slab
      )
    overpotential = round(self.get_overpotential(
        result_array_with_eU_list=[energy_array_with_eU])[0], 2)
    line_label = dbname_slab if line_label is None else line_label
    line_label += fr' ($\eta$={overpotential} V)'

    fig, ax = self.plot(
        energy_array=energy_array_with_eU,
        label_list=label_list,
        line_label=line_label,
        fig=fig,
        ax=ax,
        is_save=save,
        fname=fname,
        color=line_color,
        legend_loc=legend_loc,
        legend_fontsize=legend_fontsize,
    )
    return fig, ax

  def plot_custom_wrapper(self,
                          dbname_slab="O2_P_N3_graphene",
                          formular_index_list=[0, 1, 2, 3, 4, 5],
                          check=True,
                          eU=1.23,
                          is_consider_O2=True,
                          energy_name="energy|free_energy",
                          is_sol_eff=False,
                          is_ammend_O2=True,
                          is_ORR=True,
                          fig=None,
                          ax=None,
                          line_label=None,
                          line_color='black',
                          save=False,
                          fname='xxx/xx.pdf',
                          is_consideer_O2=True,
                          ):
    """可以画 不要O2吸附的 吉布斯能变图
    formular_index_list=[0, 2, 3, 4, 5] 即可

    Args:
        dbname_slab (str, optional): _description_. Defaults to "O2_P_N3_graphene".
        formular_index_list (list, optional): _description_. Defaults to [0, 1, 2, 3, 4, 5].
        check (bool, optional): _description_. Defaults to True.
        eU (float, optional): _description_. Defaults to 1.23.
        energy_name (str, optional): _description_. Defaults to "energy|free_energy".
        is_sol_eff (bool, optional): _description_. Defaults to False.
        is_ammend_O2 (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """
    formular_list = self.get_formular_list(dbname_slab=dbname_slab,
                                           is_consideer_O2=is_consideer_O2,)
    eU_array = self.get_eU_array(eU=eU,
                                 is_consider_O2=is_consider_O2,
                                 is_ORR=is_ORR)
    used_formular_list = []
    used_eU_array = []
    for index in formular_index_list:
      formular = formular_list[index]
      used_formular_list.append(formular)
      used_eU_array.append(eU_array[index])
    if check:
      print("当前check is True, 确认后设置为 False")
      return used_formular_list

    label_list = self.get_label_list(
        formular_list=used_formular_list,
        dbname_slab=dbname_slab
    )

    fig, ax = self.plot_custom(formular_list=used_formular_list,
                               dbname_slab=dbname_slab,
                               eU=used_eU_array,
                               label_list=label_list,
                               line_color=line_color,
                               line_label=line_label,
                               energy_name=energy_name,
                               is_sol_eff=is_sol_eff,
                               is_ammend_O2=is_ammend_O2,
                               fig=fig,
                               ax=ax,
                               save=save,
                               fname=fname,
                               )
    return fig, ax

  def plot_perfect_ORR(self, fig=None, ax=None, color='black',
                       is_consider_O2=True,
                       is_ORR=True):
    energy_array = -self.get_eU_array(eU=1.23,
                                      is_consider_O2=is_consider_O2,
                                      is_ORR=is_ORR) + 4.92
    fig, ax = self.plot(
        energy_array=energy_array,
        label_list=["*", "*O$_2$", "*OOH", "*O", "*OH", "*"],
        line_label="perfect",
        fig=fig,
        ax=ax,
        color=color,
        is_save=False,
    )
    return fig, ax

  def plot_lines_custom(self,
                        energy_array_list,
                        line_label_list=None,
                        xlabel_list=['*', '*O$_2$', '*OOH', '*O', '*OH', '*'],
                        fig=None,
                        ax=None,
                        save=False,
                        fname='xxx/fig_orr.pdf',
                        legend_loc='lower left',
                        legend_fontsize='small'):
    """给定数组画这个数组的 orr 图
    eg: energy_array_list=np.array([[ 0.  ,  0.21,  0.46, -0.52, -0.62,  0.  ],[ 0.  ,  0.73,  1.01, -0.78, -0.11,  0.  ]])

    Args:
        energy_array_list (_type_): _description_
        line_label_list (_type_, optional): _description_. Defaults to None.
        xlabel_list (list, optional): _description_. Defaults to ['*','*O2','*OOH','*O','*OH','*'].
        fig (_type_, optional): _description_. Defaults to None.
        ax (_type_, optional): _description_. Defaults to None.
        save (bool, optional): _description_. Defaults to False.
        fname (str, optional): _description_. Defaults to 'xxx/fig_orr.pdf'.
        legend_loc (str, optional): _description_. Defaults to 'lower left'.
        legend_fontsize (str, optional): _description_. Defaults to 'small'.

    Returns:
        _type_: _description_
    """

    if line_label_list is None:
      line_label_list = [f'line{i+1}' for i in range(len(energy_array_list))]
    for energy_array, line_label, line_color in zip(energy_array_list, line_label_list, self.matplotlibLearnFeatures.color_list):
      fig, ax = self.plot(energy_array=energy_array,
                          line_label=line_label,
                          label_list=xlabel_list,
                          ax=ax,
                          fig=fig,
                          color=line_color,
                          legend_loc=legend_loc,
                          legend_fontsize=legend_fontsize,
                          is_save=save,
                          fname=fname,)
    return fig, ax


class DealDataThermo:
  def __init__(self) -> None:
    pass

  def get_vib_data_vasp_method(self, directory="xxx/vibration"):
    """

    vib_data = mycalc.features.deal_data.get_vib_data_vasp_method(
    directory='/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/BN_codoping_sub/O2_B_N1_graphene/vibration')
    vib_data.write_jmol(filename='/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/BN_codoping_sub/O2_B_N1_graphene/vibration/vib.xyz')
    打开jmol.jar  打开 vib.xyz 可以查看

    Args:
        directory (_type_): 频率计算的目录

    Returns:
        _type_: _description_
    """
    # 分析
    calc = ase.calculators.vasp.Vasp(directory=directory, restart=True)
    # vib_freq = calc.read_vib_freq()  # meV  # print(f'实频和虚频为 {vib_freq} meV')
    # retrieving a VibrationsData object
    # 如果出现问题那么需要升级ase: pip install --upgrade git+https://gitlab.com/ase/ase.git@master
    vib_data = calc.get_vibrations()
    # print(vib_data.tabulate())
    return vib_data

  def get_thermochemistry_gas(
      self,
      directory_relax,
      potentialenergy=None,
      symmetrynumber=2,
      spin=0,
      ignore_imag_modes=True,
      geometry="linear",
  ):
    """potentialenergy 给定势能可以考虑溶剂化效应
    geometry: 'monatomic', 'linear', or 'nonlinear'

    Args:
        directory_relax (_type_): _description_
        potentialenergy (_type_, optional): _description_. Defaults to None.
        symmetrynumber (int, optional): _description_. Defaults to 2.
        spin (int, optional): _description_. Defaults to 0.
        ignore_imag_modes (bool, optional): _description_. Defaults to True.
        geometry (str, optional): _description_. Defaults to 'linear'.

    Returns:
        _type_: _description_
    """
    atoms = ase.io.read(os.path.join(directory_relax, "OUTCAR"))
    if potentialenergy is None:
      potentialenergy = atoms.get_potential_energy()
    directory_vib = os.path.join(directory_relax, "vibration")
    vib_data = self.get_vib_data_vasp_method(directory=directory_vib)

    thermo = ase.thermochemistry.IdealGasThermo(
        atoms=atoms,
        potentialenergy=potentialenergy,
        vib_energies=vib_data.get_energies(),
        geometry=geometry,
        symmetrynumber=symmetrynumber,
        spin=spin,
        ignore_imag_modes=ignore_imag_modes,
    )
    return thermo

  def get_thermodata_gas(
      self,
      directory_relax,
      potentialenergy=None,
      temperature=298.15,
      pressure=101325,
      verbose=False,
      symmetrynumber=2,
      spin=0,
      ignore_imag_modes=True,
      geometry="linear",
  ):
    """给定 potentialenergy 可以考虑溶剂化效应
    对于H2O 压力要设置为 3500

    Args:
        directory_relax (_type_): _description_
        temperature (int, optional): _description_. Defaults to 298.15.
        pressure (int, optional): _description_. Defaults to 101325.
        verbose (bool, optional): _description_. Defaults to False.
        symmetrynumber (int, optional): _description_. Defaults to 2.
        spin (int, optional): _description_. Defaults to 0.
        ignore_imag_modes (bool, optional): _description_. Defaults to True.
        geometry (str, optional): _description_. Defaults to 'linear'.

    Returns:
        _type_: _description_
    """
    thermo = self.get_thermochemistry_gas(
        directory_relax=directory_relax,
        potentialenergy=potentialenergy,
        symmetrynumber=symmetrynumber,
        spin=spin,
        ignore_imag_modes=ignore_imag_modes,
        geometry=geometry,
    )
    entropy = thermo.get_entropy(
        temperature=temperature, pressure=pressure, verbose=verbose
    )
    zpe = thermo.get_ZPE_correction()
    gibbs_energy = thermo.get_gibbs_energy(
        temperature=temperature, pressure=pressure, verbose=verbose
    )
    thermodata = {
        "entropy": entropy,
        "zpe": zpe,
        "gibbs_energy": gibbs_energy,
        "temperature": temperature,
        "pressure": pressure,
    }
    return thermodata

  def get_thermochemistry_adsorbate_on_slab(
      self,
      directory_relax,
      potentialenergy=None,
      ignore_imag_modes=True,
  ):
    """考虑溶剂化效应时, 需要给定溶剂化后的势能 potentialenergy

    Args:
        directory_relax (_type_): _description_
        potentialenergy (_type_, optional): _description_. Defaults to None.
        ignore_imag_modes (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """
    atoms = ase.io.read(os.path.join(directory_relax, "OUTCAR"))
    if potentialenergy is None:
      potentialenergy = atoms.get_potential_energy()
    directory_vib = os.path.join(directory_relax, "vibration")
    vib_data = self.get_vib_data_vasp_method(directory=directory_vib)

    thermo = ase.thermochemistry.HarmonicThermo(
        vib_energies=vib_data.get_energies(),
        potentialenergy=potentialenergy,
        ignore_imag_modes=ignore_imag_modes,
    )
    return thermo

  def get_thermodata_adsorbate_on_slab(self,
                                       directory_relax,
                                       potentialenergy=None,
                                       temperature=298.15,
                                       verbose=False,
                                       ignore_imag_modes=True,
                                       ):
    """考虑溶剂化效应时, 需要给定溶剂化后的势能 potentialenergy

    Args:
        directory_relax (_type_): _description_
        potentialenergy (_type_, optional): _description_. Defaults to None.
        temperature (int, optional): _description_. Defaults to 298.15.
        verbose (bool, optional): _description_. Defaults to False.
        ignore_imag_modes (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """

    thermo = self.get_thermochemistry_adsorbate_on_slab(
        directory_relax=directory_relax,
        potentialenergy=potentialenergy,
        ignore_imag_modes=ignore_imag_modes,
    )
    zpe = thermo.get_ZPE_correction()
    entropy = thermo.get_entropy(temperature=temperature, verbose=verbose)
    helmholtz_energy = thermo.get_helmholtz_energy(
        temperature=temperature, verbose=verbose
    )

    thermodata = {
        "entropy": entropy,
        "zpe": zpe,
        "helmholtz_energy": helmholtz_energy,
        "temperature": temperature,
    }
    return thermodata

  def get_thermodata_gas_sol_eff_wrapper(
      self,
      directory_relax,
      pressure=101325,
      temperature=298.15,
      symmetrynumber=1,
      spin=0,
      geometry='linear',
  ):
    thermodata = self.get_thermodata_gas(
        directory_relax=directory_relax,
        potentialenergy=None,
        pressure=pressure,
        temperature=temperature,
        symmetrynumber=symmetrynumber,
        spin=spin,
        geometry=geometry,
    )
    try:
      # sol_eff
      atoms = ase.io.read(os.path.join(directory_relax, "sol_eff", "OUTCAR"))
      energy_sol_eff = atoms.get_potential_energy()
      thermodata_sol_eff = self.get_thermodata_gas(
          directory_relax=directory_relax,
          potentialenergy=energy_sol_eff,
          pressure=pressure,
          temperature=temperature,
          symmetrynumber=symmetrynumber,
          spin=spin,
          geometry=geometry,
      )
      thermodata.update(
          {
              "energy_sol_eff": energy_sol_eff,
              "gibbs_energy_sol_eff": thermodata_sol_eff["gibbs_energy"],
          }
      )
    except:
      pass
    return thermodata

  def get_thermodata_adsorbate_on_slab_sol_eff_wrapper(self,
                                                       directory_relax,
                                                       temperature=298.15,
                                                       ):
    thermodata = self.get_thermodata_adsorbate_on_slab(
        directory_relax=directory_relax,
        potentialenergy=None,
        temperature=temperature,
        ignore_imag_modes=True,
        verbose=False,
    )
    try:
      # sol_eff
      atoms = ase.io.read(os.path.join(directory_relax, "sol_eff", "OUTCAR"))
      energy_sol_eff = atoms.get_potential_energy()
      thermodata_sol_eff = self.get_thermodata_adsorbate_on_slab(
          directory_relax=directory_relax,
          potentialenergy=energy_sol_eff,
          temperature=temperature,
          ignore_imag_modes=True,
          verbose=False,
      )
      thermodata.update(
          {
              "energy_sol_eff": energy_sol_eff,
              "helmholtz_energy_sol_eff": thermodata_sol_eff["helmholtz_energy"],
          }
      )
    except:
      pass
    return thermodata


class DealDataEnergy:
  def __init__(self) -> None:
    self.DataBase = dataBase.DataBase()
    pass

  # 稳定性, Ef 形成能和 Eb 结合能(杂质原子与衬底的结合能)
  def get_df_isolated_atom(self, symbol_list=['B', 'C', 'N']):
    """获得孤立原子的能量

    Args:
        symbol_list (list, optional): _description_. Defaults to ['B','C','N'].

    Returns:
        _type_: _description_
    """
    for symbol in symbol_list:
      energy = self.DataBase.get_atoms_list(
          dbname=f'{symbol}_atom',)[-1].get_potential_energy()
      df = pd.DataFrame({'energy_isolated_atom': energy}, index=[symbol])
    return df

  def get_df_isolated_atom_wrapper(self, symbol_list=None,
                                   fname='/Users/wangjinlong/my_server/my/myORR_B/isolated_atoms/energy_isolated_atoms.csv'):
    if not os.path.exists(fname):
      df = self.get_df_isolated_atom(symbol_list=['C'])
      df.to_csv(fname)
    else:
      df = pd.read_csv(fname, index_col=0)

    if symbol_list is not None:
      for symbol in symbol_list:
        if symbol in df.index:
          pass
        else:
          df_new = self.get_df_isolated_atom(symbol_list=[symbol])
          df = pd.concat([df, df_new], axis=0)
          df = df.sort_index().round(3)
          df.to_csv(fname)
    return df if symbol_list is None else df.loc[symbol_list]

  def get_df_chemical_potentials(self,
                                 rawdata={
                                     "C": "graphene72atoms",
                                     "B": "B_alpha-rhombohedral",
                                     "N": "N2",
                                     "P": "P_black_phosphorus",  # 获取黑磷晶体中P的化学势
                                     "Br": "Br2",
                                     "Pt": "Pt_bulk",
                                     'Al': 'Al_bulk',
                                     'As': 'As_rhombohedral',
                                     'Cu': 'Cu_bulk',
                                     'Fe': 'Fe_bulk',
                                     'I': 'I_crystal',
                                     'Se': 'Se_crystal',
                                     'Si': 'Si_bulk',
                                     'Te': 'Te_crystal',
                                     'W': 'W_bulk',
                                     'Br': 'Br2',
                                     'Cl': 'Cl2',
                                     'F': 'F2',
                                     'O': 'O2',
                                     "S": "S2",  # 根据S2气体计算化学势,
                                 }):

    index_list = list(rawdata.keys())
    from_source_list = list(rawdata.values())
    E_patom_list = []
    for element, db_name in rawdata.items():
      atoms: ase.Atoms = self.DataBase.db.get(f"name={db_name}").toatoms()
      E_patom = atoms.get_potential_energy() / atoms.get_global_number_of_atoms()
      E_patom_list.append(E_patom)
    df = pd.DataFrame(data={'chemical_potential': E_patom_list,
                            'from_source': from_source_list},
                      index=index_list)
    return df

  def get_df_chemical_potentials_wrapper(self,
                                         rawdata_dict=None,
                                         fname='/Users/wangjinlong/my_server/my/myORR_B/chemical_potential.csv',
                                         is_all=True,
                                         is_update=True):
    """
    rawdata_dict = {'Ag': 'Ag_bulk'}

    Args:
        rawdata_dict (_type_, optional): _description_. Defaults to { 'Ag': 'Ag_bulk'}.
        fname (str, optional): _description_. Defaults to '/Users/wangjinlong/my_server/my/myORR_B/chemical_potential.csv'.

    Returns:
        _type_: _description_
    """
    if os.path.exists(fname):
      df = pd.read_csv(fname, index_col=0)
    else:
      df = self.get_df_chemical_potentials()
      df.to_csv(fname)

    # 如果给出 rawdata_dict 则更新 df
    if rawdata_dict:
      for key in rawdata_dict.keys():
        df_new = self.get_df_chemical_potentials(rawdata=rawdata_dict)
        df: pd.DataFrame = pd.concat([df, df_new])
        if is_update:
          df.update(df_new)
        df = df.sort_index().drop_duplicates()
        df.to_csv(fname)

    return df if is_all else df.loc[rawdata_dict.keys()]

  def convert_chemical_formula2expression(self, chemical_formula):
    pattern = r"[A-Z][a-z]*"  # 抽取元素
    ele_list = re.findall(pattern=pattern, string=chemical_formula)
    ele_num_list = []
    for ele in ele_list:
      ele_num = re.findall(rf"{ele}(\d+)", string=chemical_formula)
      if not ele_num:
        ele_num = "1"
      ele_num_list.extend(ele_num)

    expr_list = []
    for ele, num in zip(ele_list, ele_num_list):
      expr_part = [ele + "*" + num]
      expr_list.extend(expr_part)
    expression = "+".join(expr_list)

    return expression

  def get_E_f(self, db_name_of_atoms="B_N1_graphene"):
    """slab 的形成能
    计算公式: B_N1graphene 的能量 - 所有原子化学势的和

    Args:
        db_name_of_atoms (str, optional): _description_. Defaults to 'B_N1graphene'.

    Returns:
        _type_: _description_
    """

    df = self.get_df_chemical_potentials_wrapper()
    data = df['chemical_potential'].to_dict()

    atoms: ase.Atoms = self.DataBase.db.get(
        name=db_name_of_atoms).toatoms()
    expr = self.convert_chemical_formula2expression(
        chemical_formula=atoms.get_chemical_formula()
    )
    chemical_potentials = eval(expr, None, data)

    # print(f'形成能expr: {expr}')
    formation_energy = atoms.get_potential_energy() - chemical_potentials

    return formation_energy

  def get_df_Ef(self, dbname_list):
    Ef_list = []
    for dbname in dbname_list:
      Ef = self.get_E_f(db_name_of_atoms=dbname)
      Ef_list.append(Ef)
    data = {r"E$_f$": Ef_list}
    df = pd.DataFrame(data, index=dbname_list)
    return df

  def get_df_Ef_wrapper(
      self,
      dbname_slab_list=["graphene72atoms"],
      fname="/Users/wangjinlong/my_server/my/myORR_B/slab/Ef_slab.csv",
      is_all=False,
      is_update=False,
  ):
    """计算公式: B_N1graphene 的能量 - 所有原子化学势的和

    Args:
        dbname_slab_list (list, optional): _description_. Defaults to ["graphene72atoms"].
        fname (str, optional): _description_. Defaults to "/Users/wangjinlong/my_server/my/myORR_B/slab/Ef_slab.csv".
        is_all (bool, optional): _description_. Defaults to False.
        is_update (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    if os.path.exists(fname):
      df_total = pd.read_csv(fname, index_col=0)
      for dbname_slab in dbname_slab_list:
        if dbname_slab in list(df_total.index):
          if is_update:
            df = self.get_df_Ef(dbname_list=[dbname_slab])
            df_total.update(df)
          pass
        else:
          df = self.get_df_Ef(dbname_list=[dbname_slab])
          df_total = pd.concat([df_total, df])
    else:
      df_total = self.get_df_Ef(dbname_list=dbname_slab_list)
    df_total = df_total.round(3).sort_index()
    df_total.to_csv(fname)
    df_out = df_total.loc[dbname_slab_list]
    return df_total if is_all else df_out

  def get_E_f2(self, db_name_of_atoms="P_N0_graphene"):
    """考虑了slab 的形成能
    计算公式: E_slab 的能量 - E_defect_graphene - 其它杂质原子化学势的和

    Args:
        db_name_of_atoms (str, optional): _description_. Defaults to 'P_N0_graphene'.

    Returns:
        _type_: _description_
    """

    df = self.get_df_chemical_potentials_wrapper()
    data = df['chemical_potential'].to_dict()

    atoms: ase.Atoms = self.DataBase.db.get(
        f"name={db_name_of_atoms}").toatoms()
    expr = self.convert_chemical_formula2expression(
        chemical_formula=atoms.get_chemical_formula()
    )
    expr_impurities = "+".join(
        [item for item in expr.split("+") if "C" not in item]
    )
    # 杂质原子的化学势
    impurities_chemical_potentials_sum = eval(expr_impurities, data)
    # 获得 E_defect_graphene 的能量
    expr_C = [item for item in expr.split("+") if "C" in item][0].split("*")
    expr_C.reverse()
    expr_C = "".join(expr_C)  # e.g. 71C
    E_defect_graphene = self.DataBase.db.get(
        f"name=defect_graphene_{expr_C}"
    ).energy

    formation_energy = (
        atoms.get_potential_energy()
        - E_defect_graphene
        - impurities_chemical_potentials_sum
    )
    return formation_energy

  def get_E_coh_patom(self, dbname="P2_N4_CoN4_like"):
    r"""_summary_

    Args:
        db_name_of_atoms (str, optional): _description_. Defaults to 'P2_N4_CoN4_like'.

    Returns:
        _type_: _description_
    """
    # 获取原子对象
    atoms = self.DataBase.db.get(name=dbname).toatoms()
    # 获取表达式 如 'C*66+N*4+P*2'
    expr = self.convert_chemical_formula2expression(
        chemical_formula=atoms.get_chemical_formula()
    )

    # 获得 数据字典 data_dict
    symbol_list = list(set(atoms.get_chemical_symbols()))
    df = self.get_df_isolated_atom_wrapper(symbol_list=symbol_list)
    data_dict = df['energy_isolated_atom'].to_dict()

    # 计算
    n_atoms = atoms.get_global_number_of_atoms()
    E_coh_patom = eval(expr, None, data_dict) / n_atoms
    return E_coh_patom

  def get_Eb_slab_new(self,
                      slab_plus_impurite='',
                      slab='',
                      impurite_list=[''],
                      ):
    """有多个掺杂原子时就要用这个
    """
    E_slab_plus_impurite = self.DataBase.get_energy(
        dbname=slab_plus_impurite,)
    E_slab = self.DataBase.get_energy(dbname=slab,)
    E_impurite_all = 0
    for impurite in impurite_list:
      df = self.get_df_chemical_potentials_wrapper()
      E_impurite = df['chemical_potential'].loc[impurite]
      E_impurite_all += E_impurite
    Eb = E_slab_plus_impurite - E_slab - E_impurite_all
    return Eb

  def get_df_Eb_slab_new(self,
                         slab_plus_impurite_list=['Si_P_2V_Gra',
                                                  'Si_P_3V_Gra_1',
                                                  'Si_P_4V_Gra',
                                                  ],
                         slab_list=['DVG',
                                    'defect_graphene_69C',
                                    'defect_graphene_68C_type2',
                                    ],
                         impurite_lists=[['Si', 'P']]*3,
                         ):
    Eb_list = []
    for slab_plus_impurite, slab, impurite_list in zip(
        slab_plus_impurite_list,
        slab_list,
        impurite_lists,
    ):
      Eb = self.get_Eb_slab_new(
          slab_plus_impurite=slab_plus_impurite,
          slab=slab,
          impurite_list=impurite_list,)
      Eb_list.append(Eb)
    df = pd.DataFrame(data=Eb_list, index=slab_plus_impurite_list,
                      columns=[r'E$_b$'])
    return df

  def get_Eb_slab(self,
                  adsorbate='As',
                  dbname_slab='MVG',
                  dbname_adsorbate_on_slab=None,
                  is_chemical_potentials=True,
                  ):
    """计算杂质原子与衬底的结合能

    Args:
        adsorbate (str, optional): _description_. Defaults to 'As'.
        dbname_slab (str, optional): _description_. Defaults to 'MVG'.
        dbname_adsorbate_on_slab (_type_, optional): _description_. Defaults to None.
        is_chemical_potentials (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """

    dbname_adsorbate_on_slab = f'{adsorbate}_{dbname_slab}' if dbname_adsorbate_on_slab is None else dbname_adsorbate_on_slab
    # 杂质原子的能量
    if is_chemical_potentials:
      df = self.get_df_chemical_potentials_wrapper()
      energy_adsorbate = df['chemical_potential'].loc[adsorbate]
    else:
      df = self.get_df_isolated_atom_wrapper()
      energy_adsorbate = df['energy_isolated_atom'].loc[adsorbate]
    # 衬底和 adsorbate_on_slab 的能量
    energy_slab = self.DataBase.get_energy(dbname=dbname_slab)
    energy_adsorbate_on_slab = self.DataBase.get_energy(
        dbname=dbname_adsorbate_on_slab)
    E_b = energy_adsorbate_on_slab - energy_adsorbate - energy_slab
    return E_b

  def get_df_E_b_slab(self, dbname_slab_list=['As_MVG']):
    """计算杂质原子与衬底的结合能

    Args:
        dbname_slab_list (list, optional): _description_. Defaults to ['As_MVG'].

    Returns:
        _type_: _description_
    """
    E_b_list = []
    for dbname_slab in dbname_slab_list:
      adsorbate = dbname_slab.split('_')[0]
      dbname = '_'.join(dbname_slab.split('_')[1:])  # 掺杂之前的构型
      E_b = self.get_Eb_slab(adsorbate=adsorbate,
                             dbname_slab=dbname,
                             dbname_adsorbate_on_slab=dbname_slab,
                             is_chemical_potentials=True)
      E_b_list.append(E_b)
    df = pd.DataFrame({'E_b': E_b_list}, index=dbname_slab_list)
    return df

  # 吸附能
  def get_E_ads(
      self,
      dbname_adsorbate="OH",
      dbname_slab="B_C_sub",
      dbname_adsorbate_on_slab=None,
      is_sol_eff=False,
  ):
    """计算吸附能
    要注意 是否考虑溶剂化效应如果要考虑 则 dbname_adsorbate='OH_sol_eff', dbname_adsorbate_on_slab='OH_B_C_sub'
    E_{add} = E_{adsorbate+sub} - E_{adsorbate} - E_{sub}

    Args:
        dbname_adsorbate (str, optional): _description_. Defaults to 'OH'.
        db_atoms_name_slab (str, optional): _description_. Defaults to 'B_C_sub'.
        dbname_adsorbate_on_slab (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """

    if dbname_adsorbate_on_slab is None:
      dbname_adsorbate_on_slab = f"{dbname_adsorbate}_{dbname_slab}"
    energy_list = []
    for dbname in [
        dbname_adsorbate,
        dbname_slab,
        dbname_adsorbate_on_slab,
    ]:
      print(f'{dbname} -> get_energy ...')
      energy = self.DataBase.get_energy(
          dbname=dbname,
          is_sol_eff=is_sol_eff,
          energy_name="energy",
          is_ammend_O2=False,
      )
      energy_list.append(energy)
    E_ads = energy_list[2] - energy_list[0] - energy_list[1]

    return E_ads

  def get_df_E_ads_with_multiple_confs(self,
                                       adsorbate='O2',
                                       slab='Si_P_2V_Gra',
                                       adsorbate_on_slab_list=[
                                           'O2_Si_P_2V_Gra_P_top',
                                           'O2_Si_P_2V_Gra_P_top_sideon'],
                                       df_index_list=None):
    """获取具有多个吸附构型的吸附能 
    """

    Eads_list = []
    for adsorbate_on_slab in adsorbate_on_slab_list:
      Eads = self.get_E_ads(
          dbname_adsorbate=adsorbate,
          dbname_slab=slab,
          dbname_adsorbate_on_slab=adsorbate_on_slab,
          is_sol_eff=False,
      )
      Eads_list.append(Eads)
    if df_index_list is None:
      df_index_list = adsorbate_on_slab_list
    df = pd.DataFrame(data=Eads_list, index=df_index_list,
                      columns=[adsorbate]).round(decimals=3)

    return df

  def get_df_E_ads(
      self,
      dbname_slab="P_N0_graphene",
      adsorbate_list=["O2", "O2H", "O", "OH"],
      is_sol_eff=False,
  ):
    """
    - O2H 吸附能最好在 -1.8 附近,
    - O2 吸附能最好在 -0.3 ~ -0.6 eV 附近, 
    - O 的吸附能最好在  -3.6 eV 附近
    - OH 的吸附能最好在 -2.4 eV 
    """

    data = {}
    for adsorbate in adsorbate_list:
      dbname_adsorbate_on_slab = f"{adsorbate}_{dbname_slab}"
      E_ads = self.get_E_ads(
          dbname_adsorbate=adsorbate,
          dbname_slab=dbname_slab,
          dbname_adsorbate_on_slab=dbname_adsorbate_on_slab,
          is_sol_eff=is_sol_eff,
      )
      data.update({adsorbate: [E_ads]})
    df = pd.DataFrame(data, index=[dbname_slab])
    return df

  def get_df_E_ads_wrapper(self,
                           dbname_slab_list=["P_N0_graphene"],
                           adsorbate_list=["O2", "O2H", "O", "OH"],
                           is_sol_eff=False,
                           fname="/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/E_ads.csv",
                           update_data=False,
                           is_dropna=False,
                           is_all=False,
                           ):
    """
    根据以上计算结果, 我们认为 
    - O2H 吸附能最好是 -1.7 +- 0.6 eV  ? -1.9 eV
    - O 的吸附能最好在是-3.4 +- 0.7 eV, O 的吸附能如果小于OH很有可能是吸附位不对
    - OH 的吸附能最好在 -2.4 +- 0.5 0.6 eV 
    - O2 吸附能最好在 -0.67  +- 0.?  eV 
    - 如果O2H的吸附能过小那么*O2的氢化很有可能是速率决定步, O和OH的吸附能过大, 则很有可能是O和OH的氢化是速率决定步. 

    Args:
        dbname_slab_list (list, optional): _description_. Defaults to ["P_N0_graphene"].
        adsorbate_list (list, optional): _description_. Defaults to ["O2", "O2H", "O", "OH"].
        is_sol_eff (bool, optional): _description_. Defaults to False.
        fname (str, optional): _description_. Defaults to "/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/E_ads.csv".
        update_data (bool, optional): _description_. Defaults to False.
        is_dropna (bool, optional): _description_. Defaults to False.
        is_all (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """

    if is_sol_eff:
      fname = fname.replace(".csv", "_sol_eff.csv")

    if os.path.exists(fname):
      df_total = pd.read_csv(fname, index_col=0).drop_duplicates()
      for dbname_slab in dbname_slab_list:
        # 如果存在之前的数据, 更新
        if dbname_slab in list(df_total.index):
          if update_data:
            df = self.get_df_E_ads(
                dbname_slab=dbname_slab,
                adsorbate_list=adsorbate_list,
                is_sol_eff=is_sol_eff,
            )
            df_total.update(df)
          else:
            pass
        else:
          df = self.get_df_E_ads(
              dbname_slab=dbname_slab,
              adsorbate_list=adsorbate_list,
              is_sol_eff=is_sol_eff,
          )
          df_total = pd.concat([df_total, df])
          df_total = df_total.drop_duplicates()
    else:
      df_total = self.get_df_E_ads(
          dbname_slab=dbname_slab_list[0],
          adsorbate_list=adsorbate_list,
          is_sol_eff=is_sol_eff,)

    if is_dropna:
      df_total.dropna(inplace=True)
    df_total = df_total.round(3).sort_index()
    df_total.to_csv(fname)

    return df_total if is_all else df_total.loc[dbname_slab_list]

  def wrapper_merge_df_apply(self,
                             df1: pd.DataFrame,
                             df2: pd.DataFrame):
    """df1: df_Eads_sol_eff, df2: df_Eads_diff
    合并两个行列名都相同的 df 到一个df 
    - slab            O2H               O             OH
    - B_O_Gra  -2.479 (0.03)  -4.982 (-0.14)  -4.28 (-0.02)
    - B_P_Gra  -1.345 (0.28)   -4.021 (0.35)  -2.827 (0.27)
    - B_S_Gra  -2.262 (-0.2)  -4.932 (-0.11)  -4.13 (-0.02)

    Args:
        df1 (pd.DataFrame): _description_
        df2 (pd.DataFrame): _description_

    Returns:
        _type_: _description_
    """

    df = df1.apply(lambda x: x.astype(str)
                   + " ("
                   + df2[x.name].astype(str)
                   + ")",
                   axis=0,)
    return df

  def get_df_E_ads_with_sol_eff_diff(self,
                                     dbname_slab_list=['Si_MVG',
                                                       'Si_P_2V_Gra_Si_top',
                                                       'P_MVG',
                                                       'Si_P_2V_Gra_P_top',
                                                       ],
                                     is_difference_value=True,
                                     update_data=True):
    df1 = self.get_df_E_ads_wrapper(
        dbname_slab_list=dbname_slab_list,
        is_sol_eff=False,
        update_data=update_data
    )
    df2 = self.get_df_E_ads_wrapper(
        dbname_slab_list=dbname_slab_list,
        is_sol_eff=True,
        update_data=update_data
    )
    if is_difference_value:
      df2 = df2-df1
    df = self.wrapper_merge_df_apply(
        df1=df1, df2=df2.round(3)
    )
    return df

  def get_df_Eads_compare_Eads_opt(self,
                                   df_Eads: pd.DataFrame,
                                   decimals=2,
                                   only_diff=False,
                                   data={'O2': [-0.55],
                                         'O2H': [-1.81],
                                         'O': [-3.33],
                                         'OH': [-2.42]},
                                   ):
    """获得 与最优吸附能的差值, 更完整的请使用 get_df_Eads_compare_opt_diff_diff
    'O2': [-0.55],
    'O2H': [-1.81],
    'O': [-3.33],
    'OH': [-2.42]

    Args:
        df_Eads (_type_): _description_
        decimals (int, optional): _description_. Defaults to 2.

    Returns:
        _type_: _description_
    """

    df_Eads_opt = pd.DataFrame(data=data, index=['E_opt_ads'])
    df_diff: pd.DataFrame = df_Eads - df_Eads_opt.values
    df = DealData().wrapper_merge_df_apply(df_Eads.round(decimals),
                                           df_diff.round(decimals))
    return df_diff.round(decimals=decimals) if only_diff else df

  def get_df_Eads_compare_opt_diff_diff(self, dbname_slab_list,
                                        is_sol_eff=True,
                                        is_consider_O2=True):
    """获得吸附物O2,O2H,O,OH 的吸附能与最优吸附能的差, 以及相邻两列的差, 相邻两列的差的最大的步骤就是速率决速步, 该最大值可以预测为过电位. 

    Args:
        dbname_slab_list (_type_): _description_

    Returns:
        _type_: _description_
    """

    df_Eads_se = self.get_df_E_ads_wrapper(
        dbname_slab_list=dbname_slab_list,
        is_sol_eff=is_sol_eff)
    # 与最优吸附能的差值
    df_diff: pd.DataFrame = self.get_df_Eads_compare_Eads_opt(
        df_Eads=df_Eads_se,
        only_diff=True)
    df_diff.columns = [r'O$_2$', 'OOH', 'O', 'OH']
    df_diff['0'] = [0]*len(df_diff)  # 右侧增加一列 0
    df_delta = df_diff.diff(axis=1)  # 相邻两列的差值
    if is_consider_O2:
      df_delta = df_delta.iloc[:, -4:]  # 取最右四列
      df_delta.columns = [fr'$\Delta E_{i}$' for i in range(1, 5)]
      df_delta[r'$\Delta E_{max}$'] = df_delta.max(axis=1)  # 增加一列最大值
      df = pd.concat([df_diff.iloc[:, :4], df_delta], axis=1)  # 合并起来
    else:
      df_delta = df_delta.iloc[:, -3:]  # 取最右三列
      df_delta.columns = [fr'$\Delta E_{i}$' for i in range(1, 4)]
      df_delta[r'$\Delta E_{max}$'] = df_delta.max(axis=1)  # 增加一列最大值
      df = pd.concat([df_diff.iloc[:, 1:4], df_delta], axis=1)  # 合并起来
    return df.round(2)

  def get_model_Eads_Chg_Mag(self,
                             features_array=np.random.normal(size=(3, 2)),
                             adsorbate_name='O|OH|O2H'):
    """根据衬底活性位原子的磁矩和电荷量 预测 吸附物的吸附能的模型, 可以大致判断衬底ORR活性的好坏

    Args:
        features_array (_type_, optional): _description_. Defaults to np.random.normal(size=(3, 2)).
        adsorbate_name (str, optional): _description_. Defaults to 'O|OH|O2H'.

    Returns:
        _type_: _description_
    """

    if adsorbate_name == 'O':
      a, b, c = [-12.63609335, -1.11681538, -2.63760832]
      # old np.array([13.33, -1.4, -2.15])
    elif adsorbate_name == 'OH':
      a, b, c = [-13.04542244, -1.73438186, -0.77060173]
      # old np.array([-6.07, -1.88, -0.15])
    elif adsorbate_name == 'O2H':
      a, b, c = [-2.0273443, -1.41475109, 0.21142448]
      # old np.array([-5.28, -1.58, 0.54])
    elif adsorbate_name == 'O2':
      a, b, c = [-4.50667321, -0.63427271,  0.3217048]
    else:
      print(f'缺少参数 adsorbate_name.')
      return
    x = features_array[:, 0]
    y = features_array[:, 1]

    return a*x+b*y + c

  def get_df_Eads_predict_from_model(self, df):
    data = {}
    for name in ['O2', 'O2H', 'O', 'OH']:
      v = self.get_model_Eads_Chg_Mag(
          features_array=df[['magnetic_moments', 'charges']].values,
          adsorbate_name=name)
      data.update({name: v})
    df = pd.DataFrame(data=data, index=df.index).round(3)
    return df

  # 溶解势
  def get_dissoluion_potential_old(self,
                                   delta_G=1,
                                   z=2,
                                   ):
    """这是根据 chat gpt 查的
    G_ion:金属离子的自由能, G_solid:固体金属的自由能
    计算Gibbs自由能变 ΔG = G_ion - G_solid
    计算金属原子在电化学环境中脱离骨架并溶解到电解质中的电位(Udiss，dissolution potential):
    U_diss = -delta_G/zF
    法拉第常数 F=96485C/mol, z 是金属离子的电荷数
    """
    delta_G_kJ_mol = self.transfer_eV2kJ_mol(v_eV=delta_G)  # kJ/mol
    print(f"{delta_G} eV-> {delta_G_kJ_mol} kJ/mol")
    # 金属离子的电荷数 n
    from scipy import constants

    faraday_constanct = constants.physical_constants["Faraday constant"][0]
    # *1e+3 是变成 J/mol
    U_diss = -delta_G_kJ_mol * 1e3 / (z * faraday_constanct)
    return U_diss

  def get_df_standard_dissolution_potential(self):
    r"""标准溶解势的数据来自一本书: lide2004crc, 用来计算 A金属在B衬底上相对于SHE的溶解势 an estimate of the potential versus SHE at which such a dissolution process

    The experimentally determined standard potentials for pure metals is given in Appendix A.
    $U^0_A$

    The standard dissolution potentials (pH 0) for the pure metals considered in this study (lide2004crc). 

    Returns: df 
        _type_: _description_
    """

    import pandas as pd
    Metal = 'Fe Co Ni Cu Ru Rh Pd Ag Os Ir Pt Au'.split()
    Number_of_electrons_transferred = '2 2 2 2 2 2 2 1 2 3 2 3'.split()
    Standard_dissolution_potential = '-0.45 -0.28 -0.26 0.34 0.46 0.60 0.95 0.80 - 1.16 1.18 1.50'.split()
    df = pd.DataFrame(data={'Number of electrons transferred': Number_of_electrons_transferred,
                      'Standard dissolution potential':
                            Standard_dissolution_potential}, index=Metal, )

    # 假设你想要将不能转换的值设置为NaN
    df[['Number of electrons transferred', 'Standard dissolution potential']] = df[[
        'Number of electrons transferred', 'Standard dissolution potential']].apply(pd.to_numeric, errors='coerce')
    # df.replace(to_replace="-", value=np.nan, inplace=True)

    return df

  def get_dissolution_potential_of_A_on_B(self,
                                          element_A='Fe',
                                          element_B='Au',
                                          dbame_slab_B_B=None,
                                          dbame_slab_A_B=None,
                                          shift_dissolution_potential=True,
                                          ):
    """根据文献 greeley2007electrochemical, 计算A@B (A在B衬底上的溶解势) 溶解势, 计算公式: n*e*U_A = E_B/B - E_A/B + mu_A - mu_B + n*e * U_A0

    正的电极电势值越大，金属还原能力越强，越不容易被氧化。
    负的电极电势值越小（数值越大），金属氧化能力越强，越容易被氧化

    金属的标准电极电势（或标准溶解电势）指的是在标准条件下（298 K，1 M 浓度的溶液，1 atm 压力）金属相对于标准氢电极（SHE）的电极电势。这个电势的正负表示金属的还原或氧化倾向：

    正的标准电极电势：如果金属的标准电极电势是正的，这意味着该金属在标准条件下更倾向于还原（接受电子）。在电化学系列中，这类金属通常被认为是贵金属，例如金（Au）、铂（Pt）等。这些金属比较难被氧化，具有较高的抗腐蚀性。

    负的标准电极电势：如果金属的标准电极电势是负的，这意味着该金属在标准条件下更倾向于氧化（失去电子）。这种金属更容易被氧化（例如与酸反应产生氢气）。常见的有负标准电极电势的金属有锌（Zn）、铁（Fe）、铝（Al）等。这些金属容易被腐蚀和氧化。

    标准电极电势的正负值是金属活性的一种量度，能够帮助预测在电化学反应中的行为：

    正的电极电势值越大，金属还原能力越强，越不容易被氧化。
    负的电极电势值越小（数值越大），金属氧化能力越强，越容易被氧化。
    举例来说，金的标准电极电势为 +1.50 V，相对来说不容易被氧化，而锌的标准电极电势为 -0.76 V，相对来说更容易被氧化。

    Args:
        element_A (str, optional): _description_. Defaults to 'Fe'.
        element_B (str, optional): _description_. Defaults to 'Au'.
        dbame_slab_B_B (_type_, optional): _description_. Defaults to None.
        dbame_slab_A_B (_type_, optional): _description_. Defaults to None.
        shift_dissolution_potential (bool, optional): _description_. Defaults to True.

    Returns: 
        _type_: _description_
    """

    # 获得E_B/B 和 E_A/B slab的能量
    if (dbame_slab_B_B is None) and (dbame_slab_A_B is None):
      dbame_slab_B_B = f'{element_B}_{element_B}111_2x2'
      dbame_slab_A_B = f'{element_A}_{element_B}111_2x2'

    E_B_B = self.DataBase.get_energy(dbname=dbame_slab_B_B)
    E_A_B = self.DataBase.get_energy(dbname=dbame_slab_A_B)
    # 获得A, B 元素的化学势
    df_chemical_potential = self.get_df_chemical_potentials_wrapper()
    chemical_potential_A = df_chemical_potential.chemical_potential[element_A]
    chemical_potential_B = df_chemical_potential.chemical_potential[element_B]
    # 获得标准溶解势和转移的电子数
    df_sdp = self.get_df_standard_dissolution_potential()
    n_ele_A = df_sdp['Number of electrons transferred'].loc[element_A]
    U_A0 = df_sdp['Standard dissolution potential'].loc[element_A]

    # 计算公式
    # 溶质A的溶解电位
    U_A = (E_B_B - E_A_B + chemical_potential_A -
           chemical_potential_B + n_ele_A * U_A0)/n_ele_A
    # 溶质A的溶解电位的变化
    delta_U_A = U_A - U_A0
    if shift_dissolution_potential:
      return delta_U_A
    else:
      return U_A


class DealDataBader(metaclass=functoolsLearn.AutoDecorateMeta):
  def __init__(self) -> None:
    self.Base = base.Base()
    self.DataBase = dataBase.DataBase()
    from bader_learn import baderLearn
    self.baderLearn = baderLearn
    pass

  # bader
  def bader_analysis(self,
                     dbname=None,
                     directory_relax=None,
                     recalc=False,
                     cube_or_chg="chg",
                     is_hpc=False):
    """
      为了明确判断哪个 O 更容易氢化，你可以进行如下计算：
      计算 Si-OH-P 和 Si-OH-C 体系的能量：
      对于每种体系，构建模型并优化结构。
      计算每种结构的吸附能或自由能 
      1. 比较两者的能量差，能量更低的就是更稳定的氢化路径。
      2. 用 Bader 电荷分析、Löwdin 电荷分析或电子密度差（charge density difference）来判断每个 O 原子的电子富集程度。 如果某个 O 原子具有更高的电负性或更大的负电荷，则更可能与 H⁺ 相互作用。
      3. 较弱的键（如 Si-O-C）通常更容易被氢化。 
      如果 O 原子与石墨烯的 C 原子结合，这个键可能相对较弱，尤其是如果 C 是 sp² 杂化态的 C。 能量计算（DFT 计算） 是验证这一点的最直接方式。 
    """
    directory_relax, dbname = self.DataBase.choice_directory_dname(
        dbname=dbname,
        directory=directory_relax)
    directory_sp = os.path.join(directory_relax, 'single_point')
    atoms = self.baderLearn.BaderLearn().bader_analysis(
        directory=directory_sp,
        recalc=recalc,
        cube_or_chg=cube_or_chg,
        is_hpc=is_hpc,
    )
    return atoms

  def get_atomic_charge_arr(self,
                            dbname,
                            index_list=None,
                            symbol_list=None,
                            is_neighbor=False,):
    """_summary_
    """

    atoms = self.bader_analysis(dbname=dbname, directory_relax=None)

    if is_neighbor:
      index_list = self.Base.get_neighbor_index_list_wrapper(
          atoms=atoms, index_list=index_list, symbol_list=symbol_list
      )
    else:
      index_list, symbol_list = self.Base.get_index_list_and_symbol_list(
          atoms=atoms, symbol_list=symbol_list, index_list=index_list
      )

    # 或者
    charge_arr = atoms.get_initial_charges()[index_list]
    return charge_arr

  def get_df_bader_analysis_charge_of_adsorbate(
      self,
      dbname_slab_list=["P_N0_graphene"],
      adsorbate_list=["O2", "O2H", "O", "OH"],
      symbol_list=["O", "H"],
  ):
    """获取吸附物的电荷

    Args:
        dbname_slab_list (list, optional): _description_. Defaults to ["P_N0_graphene"].
        adsorbate_list (list, optional): _description_. Defaults to ["O2", "O2H", "O", "OH"].
        symbol_list (list, optional): _description_. Defaults to ["O", "H"].

    Returns:
        _type_: _description_
    """
    merged_df = pd.DataFrame()
    for dbname_slab in dbname_slab_list:
      data = {}
      for adsorbate in adsorbate_list:
        dbname_adsorbate_on_slab = f"{adsorbate}_{dbname_slab}"
        charge_adsorbate = self.get_atomic_charge_arr(
            dbname=dbname_adsorbate_on_slab, symbol_list=symbol_list
        ).sum()
        data.update({adsorbate: [charge_adsorbate]})

      df = pd.DataFrame(data, index=[dbname_slab])
      merged_df = pd.concat([merged_df, df])
    merged_df.sort_index(inplace=True)
    return merged_df

  def get_df_bader_analysis_charge_of_adsorbate_wrapper(
      self,
      dbname_slab_list=["P_N0_graphene"],
      adsorbate_list=["O2", "O2H", "O", "OH"],
      symbol_list=["O", "H"],
      is_all=False,
      fname="/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/charge_of_adsorbate.csv",
  ):
    """获取吸附物的电荷"""
    if os.path.exists(fname):
      df_total = pd.read_csv(fname, index_col=0)
      for dbname_slab in dbname_slab_list:
        if dbname_slab in list(df_total.index):
          pass
        else:
          df = self.get_df_bader_analysis_charge_of_adsorbate(
              dbname_slab_list=[dbname_slab],
              adsorbate_list=adsorbate_list,
              symbol_list=symbol_list,
          )
          df_total = pd.concat([df_total, df])
    else:
      df_total = self.get_df_bader_analysis_charge_of_adsorbate(
          dbname_slab_list=dbname_slab_list,
          adsorbate_list=adsorbate_list,
          symbol_list=symbol_list,
      )

    df_total = df_total.round(3).sort_index()
    df_total.to_csv(fname)

    return df_total if is_all else df_total.loc[dbname_slab_list]

  # magmom
  def get_atomic_magnetic_moment_arr(self,
                                     dbname,
                                     index_list=None,
                                     symbol_list=None,
                                     is_neighbor=False
                                     ):
    atoms = self.bader_analysis(dbname=dbname,)
    magnetic_moments = atoms.get_initial_magnetic_moments()
    if is_neighbor:
      index_list = self.Base.get_neighbor_index_list_wrapper(
          atoms=atoms, index_list=index_list, symbol_list=symbol_list
      )
    else:
      index_list, symbol_list = self.Base.get_index_list_and_symbol_list(
          atoms=atoms, symbol_list=symbol_list, index_list=index_list
      )

    magnetic_moments_arr = magnetic_moments[index_list]
    return magnetic_moments_arr

  def get_df_active_site_info(self,
                              dbname,
                              symbol=None,
                              index=None,
                              df_index=None,):
    """获取活性位的电荷和磁矩
    """

    if symbol is not None:
      symbol_list = [symbol]
      index_list = None
    elif index is not None:
      index_list = [index]
      symbol_list = None
    else:
      print('请给一个非None: symbol|index')
      return

    directory_relax = self.DataBase.get_directory(dbname=dbname)
    directory_sp = os.path.join(directory_relax, 'single_point')
    charges = self.get_atomic_charge_arr(dbname=dbname,
                                         symbol_list=symbol_list,
                                         index_list=index_list)[0]
    magnetic_moments = self.get_atomic_magnetic_moment_arr(dbname=dbname,
                                                           symbol_list=symbol_list,
                                                           index_list=index_list)[0]
    # 获得数据
    data = {'magnetic_moments': [magnetic_moments],
            'charges': [charges]}

    df_index = dbname if df_index is None else df_index
    df = pd.DataFrame(data=data, index=[df_index])
    return df

  def get_df_active_site_info_wrapper(self,
                                      dbname_slab_list=None,
                                      index_list=None,
                                      symbol_list=None,
                                      df_index_list=None,
                                      update=False,
                                      fname='/Users/wangjinlong/my_server/my/myORR_B/slab/active_site_info.csv',):
    """活性位的带电量和磁矩信息
    """

    if not os.path.exists(fname):
      print('error')
      return None
    else:
      df = pd.read_csv(fname, index_col=0)

    index_list = [None] * \
        len(dbname_slab_list) if index_list is None else index_list
    symbol_list = [None] * \
        len(dbname_slab_list) if symbol_list is None else symbol_list
    df_index_list = dbname_slab_list if df_index_list is None else df_index_list
    for dbname_slab, index, symbol, df_index in zip(dbname_slab_list,
                                                    index_list,
                                                    symbol_list,
                                                    df_index_list,
                                                    ):
      if df_index in df.index:
        pass
      elif update:
        df_single = self.get_df_active_site_info(dbname=dbname_slab,
                                                 symbol=symbol,
                                                 index=index,
                                                 df_index=df_index)
        df.update(df_single)
      else:
        df_single = self.get_df_active_site_info(dbname=dbname_slab,
                                                 symbol=symbol,
                                                 index=index,
                                                 df_index=df_index)
        df = pd.concat([df, df_single])
        df.sort_index().drop_duplicates().to_csv(fname)
    df_out: pd.DataFrame = df.loc[df_index_list]
    df_out.columns = [r'Mag ($\mu B$)', r'Chg ($e$)']
    return df_out


class DealDataAbmd:
  def __init__(self) -> None:
    self.DataBase = dataBase.DataBase()
    from py_package_learn.matplotlib_learn import matplotlibLearn
    self.matplotlibFeatures = matplotlibLearn.Features()
    pass

  # ab_md
  def get_energy_py4vasp(self, dbname=None, directory=None):
    """
    - directory 应该是 xxx/ab_md

    Args:
        dbname (_type_, optional): _description_. Defaults to None.
        directory (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """

    directory, dbname = self.DataBase.choice_directory_dname(dbname=dbname,
                                                             directory=directory)
    directory = os.path.join(directory, 'ab_md')
    from py_package_learn.py4vasp_learn import py4vaspLearn
    energy = py4vaspLearn.Py4vaspLearn().get_energy(directory=directory)
    return energy

  def get_fig_ab_md(self,
                    df,
                    n_begin=800,
                    n_end=1000,
                    y1_column='total_energy.y',
                    y2_column='temperature.y',
                    y1_lim=None,
                    y2_lim=None,
                    lable_fontdict=None,
                    markersize=2,
                    is_save=False,
                    fname="xxx/ab_md.pdf",
                    ):
    """ab_md 画图
    n_begin 和 n_end 可以为None, 表示取所有的数据
    ---
    lable_fontdict={'family': 'serif',
                         'style': 'italic',
                         'weight': 'bold',
                         'size': 14,
                         'color': 'blue'
                     }
    """

    xdata = np.arange(n_begin, n_end)
    toten = df[y1_column][n_begin:n_end]
    temp = df[y2_column][n_begin:n_end]
    fig, ax = self.matplotlibFeatures.TwoDimension.double_y_axies(
        x=xdata,
        y1=toten,
        y2=temp,
        x_label="Step",
        ax_y1label="Total Energy (eV)",
        ax_y2label="Temperature (K)",
        line_y1label="Total Energy",
        line_y2label="Temperature",
        lable_fontdict=lable_fontdict,
        markersize=markersize,
        y1_lim=y1_lim,
        y2_lim=y2_lim,
        is_save=is_save,
        fname=fname,)

    return fig, ax

  def get_fig_ab_md_wrapper(self, dbname,
                            n_begin=0,
                            n_end=10000,
                            y1_lim=None,
                            y2_lim=None,
                            lable_fontdict=None,
                            markersize=2,
                            is_save=False,):
    """ab_md 画图
    n_begin 和 n_end 可以为None, 表示取所有的数据
    """

    pardir = self.DataBase.db.get(name=dbname).directory
    fname = os.path.join(pardir, 'ab_md', f'ab_md_{dbname}.pdf')
    if os.path.exists(fname):
      print(f'文件存在-> {fname}')
      pass
    else:
      energy = self.get_energy_py4vasp(dbname=dbname,)
      df = energy.to_frame('total_energy, temperature')
      fig, ax = self.get_fig_ab_md(df=df,
                                   n_begin=n_begin,
                                   n_end=n_end,
                                   y1_column='total_energy.y',
                                   y2_column='temperature.y',
                                   y1_lim=y1_lim,
                                   y2_lim=y2_lim,
                                   lable_fontdict=lable_fontdict,
                                   markersize=markersize,
                                   is_save=is_save,
                                   fname=fname)
    return fname


class DealDataDos:
  def __init__(self) -> None:
    self.DataBase = dataBase.DataBase()
    # 画 dos
    from py_package_learn.py4vasp_learn import py4vaspLearn
    self.py4vaspLearn = py4vaspLearn
    pass

  # dos
  def get_df_pdos(self, dbname='O_N_dope_graphene',
                  directory=None,
                  selection=None,):
    """selection: None表示total dos, or 'p(O)','C(p),O(p)','72(p)', 'total(O)','O(total),P(up),S(down)','O(total),P(total), 'total(P(d)),total(P(p))', '71(s,pd),70(s,p,d)', 'total(71(s,p),70(s,p))'
    * 注意, 如果selection 中是原子索引 '70,39' 的时候需要 多加1 才可以, selection 中好像是以1开始的

    """

    if dbname:
      directory_relax = self.DataBase.get_directory(dbname=dbname)
      directory = os.path.join(directory_relax, 'single_point')
    elif directory:
      pass

    df_pdos = self.py4vaspLearn.Py4vaspLearn().get_df_dos(
        directory=directory,
        selection=selection,)
    return df_pdos

  def plot_pdos_wrapper(self, dbname='O_N_dope_graphene',
                        directory=None,
                        selection=None,
                        xlim_list=[None, None],
                        ylim_list=[None, None],
                        index_column_y_list=[-2, -1],
                        name_column_y_list=None,
                        name_line_label_list=None,
                        line_color_list=None,
                        linestyle_list=None,
                        save=False,
                        fname="dos.pdf",
                        fig=None, ax=None):
    """* 画pdos, 对于 spin_dos 需要先获取 df 再plot_df_dos 
    * selection: None表示total dos, or 'p(O)','C(p),O(p)','72(p)', 'total(O)','O(total),P(up),S(down)','O(total),P(total), total(P(d)),total(P(p))

    - 提供 dbname | directory  ->single_point 目录
    """

    if dbname:
      directory_relax = self.DataBase.get_directory(dbname=dbname)
      directory = os.path.join(directory_relax, 'single_point')
    elif directory:
      print(f'dos 数据所在目录为: {directory}')
      pass

    df, fname, fig, ax = self.py4vaspLearn.Py4vaspLearn().plot_pdos_wrapper(
        directory=directory,
        selection=selection,
        xlim_list=xlim_list,
        ylim_list=ylim_list,
        name_column_y_list=name_column_y_list,
        index_column_y_list=index_column_y_list,
        name_line_label_list=name_line_label_list,
        line_color_list=line_color_list,
        linestyle_list=linestyle_list,
        save=save,
        fname=fname,
        fig=fig,
        ax=ax)

    return df, fname, fig, ax

  def plot_pdos_example(self):
    """画 n行1列的 DOS图 用于参考

    Returns:
        _type_: _description_
    """

    df = self.plot_pdos_wrapper(
        directory="xxx/single_point",
        selection="O(total),P(total)",
        name_column_y_list=["O_total", "P_total"],
    )

    return df

  def get_homo_lumo_gap(self, directory_relax, criteria=1e-3):
    """在 DFT 框架内，VASP 并不直接计算 HOMO (Highest Occupied Molecular Orbital) 和 LUMO (Lowest Unoccupied Molecular Orbital)，这些概念通常更常见于分子体系的量子化学计算。然而，对于周期性固体系统，可以通过类似的概念来理解电子结构，例如费米能级、导带底（CBM）和价带顶（VBM）。

    尽管 VASP 主要用于固态材料，计算周期性体系的电子结构，但对于分子或有限体系，也可以通过以下方法近似得到 HOMO 和 LUMO：

    1. 电子结构计算：进行自洽场计算（SCF），得到体系的轨道能量。
    2. 带结构分析：分析能带结构图，确定费米能级及其周围的态密度。
    3. 态密度 (DOS) 计算：通过态密度分析，确定 HOMO 和 LUMO 的位置。

    这种方法适用于分子或有限体系的近似计算，但对于严格的分子轨道计算，使用量子化学软件（如 Gaussian 或 Orca）可能更合适。这些软件专为分子体系设计，可以直接计算 HOMO 和 LUMO。
    取自旋向上和自旋向下的 HOMO-LUMO 能隙中的最小值作为最终的 HOMO-LUMO 能隙。
    通过这种方法，可以准确计算自旋极化体系中的 HOMO-LUMO 能隙。这个能隙反映了体系的电子激发能量，通常用于分析材料的电子性质和光学性质。
    """

    fname = os.path.join(directory_relax, "single_point/vasprun.xml")
    from pymatgen.io.vasp import Vasprun
    from pymatgen.electronic_structure.core import Spin

    # 读取 vasprun.xml 文件
    vasprun = Vasprun(fname, parse_projected_eigen=True)
    dos = vasprun.complete_dos

    # 提取自旋向上和自旋向下的总态密度（total density of states）
    tdos_up = dos.densities[Spin.up]
    tdos_down = dos.densities[Spin.down]

    # 提取能量值，并相对于费米能级进行调整
    energies = dos.energies - dos.efermi

    # 确定 HOMO 和 LUMO
    # 自旋向上
    homo_index_up = max(
        [
            i
            for i in range(len(energies))
            if tdos_up[i] > criteria and energies[i] <= 0
        ]
    )
    lumo_index_up = min(
        [
            i
            for i in range(len(energies))
            if tdos_up[i] > criteria and energies[i] > 0
        ]
    )

    # 自旋向下
    homo_index_down = max(
        [
            i
            for i in range(len(energies))
            if tdos_down[i] > criteria and energies[i] <= 0
        ]
    )
    lumo_index_down = min(
        [
            i
            for i in range(len(energies))
            if tdos_down[i] > criteria and energies[i] > 0
        ]
    )

    # 获取 HOMO 和 LUMO 能量值
    homo_energy_up = energies[homo_index_up]
    lumo_energy_up = energies[lumo_index_up]
    homo_energy_down = energies[homo_index_down]
    lumo_energy_down = energies[lumo_index_down]

    print(f"Spin-up HOMO energy: {homo_energy_up} eV")
    print(f"Spin-up LUMO energy: {lumo_energy_up} eV")
    print(f"Spin-down HOMO energy: {homo_energy_down} eV")
    print(f"Spin-down LUMO energy: {lumo_energy_down} eV")

    # 计算 HOMO-LUMO 能隙
    homo_lumo_gap_up = lumo_energy_up - homo_energy_up
    homo_lumo_gap_down = lumo_energy_down - homo_energy_down

    print(f"Spin-up HOMO-LUMO gap: {homo_lumo_gap_up} eV")
    print(f"Spin-down HOMO-LUMO gap: {homo_lumo_gap_down} eV")

    # 选择较小的能量差作为 HOMO-LUMO 能隙
    homo_lumo_gap = min(homo_lumo_gap_up, homo_lumo_gap_down)

    print(f"HOMO-LUMO gap: {homo_lumo_gap} eV")

    pass


class DealDataChg:
  def __init__(self) -> None:
    self.Base = base.Base()
    self.DataBase = dataBase.DataBase()
    pass

  # chgcar cdd
  def get_charge_density_difference_analysis(
      self,
      check=True,
      directory="adsorbate_TM_B2C3N/N2_Mn_B2C3N",
      atoms2_position_z_downlim=None,
      atom2_symbol_list=["O", "H"],
  ):
    """设置atoms2_position_z_downlim 和/或 atom2_symbol_list=['O','H']
    要注意保证三个计算中的参数 NGX NGY NGZ 是一致的
    计算好之后用VESTA 处理, edit-> edit data -> Volumetric data -> import data 注意减去

    # 其结果和atoms.get_magnetic_moments() 中的原子磁矩是一样的
    atoms = ase.io.read(os.path.join(directory, 'OUTCAR'))
    initial_magnetic_moments = atoms.get_magnetic_moments()

    # 一些脚本 处理电荷密度的脚本
    chgavg.pl
    usage: chgavg.pl CHGCAR1 CHGCAR2
    output: CHGCAR_avg
    Generates an average CHGCAR.
    chgsum.pl
    usage: chgsum.pl (CHGCAR1) (CHGCAR2) (fact1) (fact2)
    output: CHGCAR_sum
    The values in CHGCAR_sum are (CHGCAR1*fact1+CHGCAR2+fact2). By default, fact1=fact2=1.0, so that the output is the sum of the input charge density files
    chgdiff.pl
    usage: chgdiff.pl (CHGCAR1) (CHGCAR2)
    output: CHGCAR_diff
    Generates a CHGCAR difference.
    chgparavg.pl
    usage: chgparavg.pl PARCHG1 PARCHG2
    output: PARCHG_avg
    Generates an average PARCHG.
    chg2cube.pl
    usage: chg2cube.pl CHGCAR
    output: CHGCAR.cube
    Converts a CHGCAR file to the CUBE format.

    Args:
        check (bool, optional): _description_. Defaults to True.
        directory (str, optional): _description_. Defaults to 'adsorbate_TM_B2C3N/N2_Mn_B2C3N'.

    Returns: atoms, atoms1, atoms2|None
        _type_: _description_
    """
    # charge_density_difference_analysis
    calc = ase.calculators.vasp.Vasp(directory=directory, restart=True)
    atoms1 = calc.get_atoms()
    atoms2_index_list = self.Base.get_atoms_index_list(
        atoms=atoms1,
        position_z_downlim=atoms2_position_z_downlim,
        atom_symbol_list=atom2_symbol_list,
    )
    atoms3_index_list = [
        atom.index for atom in atoms1 if atom.index not in atoms2_index_list
    ]
    atoms2 = atoms1[atoms2_index_list]
    atoms3 = atoms1[atoms3_index_list]

    if check:
      print(f"请确认差分电荷密度的三部分! 之后设置check=False!")
      return atoms1, atoms2, atoms3

    directory = os.path.join(directory, "cdd")
    # 要注意保证三个计算中的参数 NGX NGY NGZ 是一致的

    # TODO: 以后处理
    def calc_part(atoms):
      from vasp_learn import calculation

      calculation.Calculations().calc_single_point(
          atoms=atoms,
          directory=os.path.join(
              directory,
              atoms.get_chemical_formula() + "_part",
          ),
          kpts=atoms1.calc.kpts,
      )
      return atoms

    atoms2 = calc_part(atoms=atoms2)
    atoms3 = calc_part(atoms=atoms3)

    self.Base.get_chg_diff(
        atoms1=atoms1, atoms2=atoms2, atoms3=atoms3, directory=directory
    )

  def get_spin_polarization_density(self, directory_sp,
                                    data_name='total|diff',
                                    ):
    """自旋磁化密度和

    Args:
        directory_relax (_type_): _description_
    """
    from py_package_learn.pymatgen_learn import pymatgenLearn
    chgdiff = pymatgenLearn.PymatgenLearn().get_cube_from_CHG_wrapper(
        directory_sp=directory_sp,
        data_name=data_name,)
    return chgdiff


class DealDataStructure:
  def __init__(self) -> None:
    self.DataBase = dataBase.DataBase()

  def ovito_fig(self):
    """使用 x86_py310 或者 x86_py39环境 
    **提供dbname 或者 atoms, directory**
    - cutoff_mode: 可以选择 pairwise 
    """
    from py_package_learn.ovito_learn import ovitoLearn
    ovitoFeatures = ovitoLearn.Features()
    return ovitoFeatures

  def old_save_atoms2png(self,
                         directory,
                         atoms,
                         fname="config.png",
                         rotation="0x,0y,0z",
                         ):
    """deprecated
    """

    filename = os.path.join(directory, fname)
    ase.io.write(filename=filename,
                 images=atoms,
                 rotation=rotation,
                 )
    print(f"文件已保存为同目录下 {fname} 文件")

    return filename

  def old_plot_atoms(self,
                     atoms,
                     is_save=False,
                     rotation=("0x, 0y, 0z"),
                     radii=0.5,
                     fname="xxx/atoms.png",
                     dpi=300,
                     ):
    """deprecated
    这个不能显示 bonds, 以后学学 ovito 模块
    临时使用 view(atoms) ->  tools -> render scence  -> jmol 好看点

    Args:
        atoms (_type_): _description_
        is_save (bool, optional): _description_. Defaults to False.
        rotation (tuple, optional): _description_. Defaults to ('0x, 0y, 0z').
        radii (float, optional): _description_. Defaults to 0.5.
        fname (str, optional): _description_. Defaults to 'xxx/atoms.png'.
        dpi (int, optional): _description_. Defaults to 300.
    """
    import ase.visualize.plot

    # 创建一个图像对象
    fig, ax = plt.subplots()
    ax: plt.Axes
    # 使用 ASE 的 plot_atoms 函数绘制原子结构
    ase.visualize.plot.plot_atoms(
        atoms,
        ax,
        show_unit_cell=2,
        rotation=rotation,
        radii=radii,
    )
    ax.set_axis_off()
    if is_save:
      # 保存图片，并设置 DPI（分辨率）
      fig.savefig(fname=fname, dpi=dpi)
    # 显示图片（可选）
    # plt.show()
    print(
        "这个不能显示 bonds, 以后学学 ovito 模块, 临时使用 view(atoms) ->  tools -> render scence  -> jmol 好看点"
    )

  def old_plot_atoms_label(self, atoms: ase.Atoms):
    """deprecated
    图不好看
    """
    from mpl_toolkits.mplot3d import Axes3D

    # 创建一个 3D 图形对象
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax: Axes3D
    # 提取原子坐标
    positions = atoms.get_positions()
    symbols = atoms.get_chemical_symbols()

    # 绘制原子
    ax.scatter(positions[:, 0], positions[:, 1],
               positions[:, 2], s=100, color='b')

    # 显示原子符号
    for position, symbol in zip(positions, symbols):
      ax.text(position[0], position[1], position[2],
              symbol, color='r', fontsize=12, ha='center')

    # 设置坐标轴标签
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Atomic Structure with Element Symbols')

    # 设置视角
    ax.view_init(elev=90, azim=0)
    ax.set_axis_off()
    # 显示和保存图像
    plt.show()


class DealDataUnitTransform():
  def __init__(self) -> None:
    """单位转换
    """
    pass

  def kcal_per_mol_2_eV(self, kcal_mol=25.83):
    """1 eV=23.0605 kcal/mol

    Returns:
        _type_: _description_
    """
    coeff = 23.0605
    V_eV = kcal_mol/coeff
    return V_eV

  def kj_per_mol_eV(self, kj_mol=72.77):
    """1eV=96.485kJ/mol
    """
    V_eV = kj_mol/96.485
    return V_eV


class DealData(DealDataThermo, DealDataAbmd,
               DealDataChg, DealDataEnergy,
               DealDataBader, DealDataDos,
               metaclass=functoolsLearn.AutoDecorateMeta,):
  def __init__(self) -> None:
    super().__init__()
    self.Base = base.Base()
    self.DataBase = dataBase.DataBase()
    self.DealDataTjt_台阶图 = Tjt_台阶图()
    self.DealDataThermo = DealDataThermo()
    self.DealDataAbmd = DealDataAbmd()
    self.DealDataBader = DealDataBader()
    from bader_learn import baderLearn
    self.baderLearn = baderLearn
    self.DealDataEnergy = DealDataEnergy()
    self.DealDataChg = DealDataChg()
    self.DealDataDos = DealDataDos()
    self.DealDataStructure = DealDataStructure()
    from py_package_learn.matplotlib_learn import matplotlibLearn
    self.matplotlibFeatures = matplotlibLearn.Features()
    self.DealDataUnitTransform = DealDataUnitTransform()
    # lobster cohp
    from lobster_learn import lobsterLearn
    self.LobsterLearn = lobsterLearn.LobsterLearn()
    # os 这两行是为了避免出现空白窗口, 是否有其他副作用目前未知
    os.environ['ETS_TOOLKIT'] = 'null'
    os.environ['QT_API'] = 'pyside6'  # 或 'pyqt5'，具体看你安装的库
    from py_package_learn.lobsterpy_learn import lobsterpyLearn
    self.lobsterpyLearn = lobsterpyLearn
    # 保存 pyobj
    from py_package_learn.pickle_learn import pickleLearn
    self.pickleLearn = pickleLearn
    #  pymatgenLearn
    from py_package_learn.pymatgen_learn import pymatgenLearn
    self.pymatgenLearn = pymatgenLearn

  def get_df_atomic_electronegativity(self, symbol_list=['B', 'As', ],
                                      index_list=['B_MVG', 'As_MVG',],):

    electronegativity_list = []
    for symbol in symbol_list:
      electronegativity = self.Base.get_atomic_electronegativity(
          atomic_symbel=symbol)
      electronegativity_list.append(electronegativity)
    df = pd.DataFrame(
        data={'electronegativity': electronegativity_list}, index=index_list)
    return df

    # wrapper
  def get_energy(self, directory):
    """不从db 中读取而是从目录中读取数据

    Args:
        directory (_type_): _description_

    Returns:
        _type_: _description_
    """
    calc = ase.calculators.vasp.Vasp(directory=directory,
                                     restart=True)
    energy = calc.get_potential_energy()
    return energy

  def wrapper_get_df_E_ads_and_charge_of_adsorbate(
      self,
      dbname_slab_list=["P_N1_graphene"],
      adsorbate_list=["O2", "O2H", "O", "OH"],
      is_sol_eff=False,
      symbol_list=["O", "H"],
      decimals=2,
  ):

    df_E_ads = self.get_df_E_ads_wrapper(
        dbname_slab_list=dbname_slab_list,
        adsorbate_list=adsorbate_list,
        is_sol_eff=is_sol_eff,
        is_all=False,
    )
    df_E_ads = df_E_ads.round(decimals=decimals)
    df_charge_of_adsorbate = self.get_df_bader_analysis_charge_of_adsorbate_wrapper(
        dbname_slab_list=dbname_slab_list,
        adsorbate_list=adsorbate_list,
        symbol_list=symbol_list,
        is_all=False,
    )
    df_charge_of_adsorbate = df_charge_of_adsorbate.round(decimals=decimals)
    df = df_E_ads.apply(
        lambda x: x.astype(str)
        + " ("
        + df_charge_of_adsorbate[x.name].astype(str)
        + ")",
        axis=0,
    )

    return df

  def wrapper_get_df_Eads_with_diff_active_info(
          self,
          dbname_slab_list=['Si_MVG', 'P_MVG',
                            'Si_P_2V_Gra_Si_top',
                            'Si_P_2V_Gra_P_top'],
          acvite_site_symbol_list=['Si', 'P', 'Si', 'P'],
          acvite_site_index_list=None,
  ):
    """获取df: 包含Eads 与溶剂化效应后的差, 活性位信息
    * acvite_site_symbol_list|acvite_site_index_list, 提供一个
    """

    df_Eads = self.get_df_E_ads_wrapper(
        dbname_slab_list=dbname_slab_list,
    )
    df_Eads_se = self.get_df_E_ads_wrapper(
        dbname_slab_list=dbname_slab_list,
        is_sol_eff=True
    )
    df_Eads_diff = df_Eads_se - df_Eads
    # 获取吸附能以及与溶剂化效应后的差值
    df_Eads_with_diff = self.wrapper_merge_df_apply(df1=df_Eads.round(2),
                                                    df2=df_Eads_diff.round(2)
                                                    )
    # 获取活性位的信息
    df_active_info = self.get_df_active_site_info_wrapper(
        dbname_slab_list=dbname_slab_list,
        symbol_list=acvite_site_symbol_list,
        index_list=acvite_site_index_list
    ).round(3)
    df_Eads_with_diff_active_info = pd.concat(
        [df_Eads_with_diff, df_active_info], axis=1)
    return df_Eads_with_diff_active_info
  # 以下考虑弃用

  def get_gibbs_energy(
      self, potential_energy=0, zpe=0, T=298.15, enetropy=0, U=-0.77, Gph=0
  ):
    n = 1
    e = 1
    GU_correction_of_voltage = -n * e * U
    gibbs_energy = (
        potential_energy + zpe - T * enetropy + Gph + GU_correction_of_voltage
    )
    return gibbs_energy

  def get_df_gas_thermodata(self,
                            dbname_list=["H2O", "H2", "O2",
                                         "O2H", "O", "OH",],):
    data = {}
    for dbname in dbname_list:
      row = self.DataBase.db.get(f"name={dbname}")
      energy = row.energy
      row = self.DataBase.db.get(f"name={dbname}-sol_eff")
      energy_sol = row.energy
      if dbname == "O":
        zpe = None
        entropy = None
        free_energy = None
        free_energy_sol = None
      else:
        row = self.DataBase.db.get(f"name={dbname}-vibration")
        zpe = row.zpe
        entropy = row.entropy
        free_energy = row.gibbs_energy
        row = self.DataBase.db.get(f"name={dbname}-sol_eff-vibration")
        free_energy_sol = row.gibbs_energy
      data.update(
          {
              dbname: {
                  "E": energy,
                  "E_sol": energy_sol,
                  "ZPE": zpe,
                  "S": entropy,
                  "G": free_energy,
                  "G_sol": free_energy_sol,
              }
          }
      )
    df = pd.DataFrame(
        data=data,
    ).transpose()
    return df

  def get_df_substrate_thermodata(
      self,
      dbname_list=["B_N1_graphene"],
  ):
    data = {}
    for dbname in dbname_list:
      row = self.DataBase.db.get(f"name={dbname}")
      energy = row.energy
      row = self.DataBase.db.get(f"name={dbname}-sol_eff")
      energy_sol = row.energy

      zpe = None
      entropy = None
      free_energy = None
      free_energy_sol = None

      data.update(
          {
              dbname: {
                  "E": energy,
                  "E_sol": energy_sol,
                  "ZPE": zpe,
                  "S": entropy,
                  "G": free_energy,
                  "G_sol": free_energy_sol,
              }
          }
      )
    df = pd.DataFrame(
        data=data,
    ).transpose()
    return df

  def get_df_adsorbate_substrate_thermodata(
      self,
      adsorbate_list=[
          "O2",
          "O2H",
          "O",
          "OH",
      ],
      substrate_list=["B_N1_graphene"],
  ):
    data = {}
    for substrate in substrate_list:
      for adsorbate in adsorbate_list:
        dbname = f"{adsorbate}_{substrate}"
        row = self.DataBase.db.get(f"name={dbname}")
        energy = row.energy
        row = self.DataBase.db.get(f"name={dbname}-sol_eff")
        energy_sol = row.energy
        # 振动数据
        row = self.DataBase.db.get(f"name={dbname}-vibration")
        zpe = row.zpe
        entropy = row.entropy
        free_energy = row.helmholtz_energy
        row = self.DataBase.db.get(f"name={dbname}-sol_eff-vibration")
        free_energy_sol = row.helmholtz_energy

        data.update(
            {
                dbname: {
                    "E": energy,
                    "E_sol": energy_sol,
                    "ZPE": zpe,
                    "S": entropy,
                    "G": free_energy,
                    "G_sol": free_energy_sol,
                }
            }
        )
    df = pd.DataFrame(
        data=data,
    ).transpose()
    return df

  # 用于手稿
  def get_pyobj(self, directory,
                fobj_name,
                pyobj,
                ):
    """ 获取保存的pyboj 避免重新生成 好像没啥用
    """

    fname = os.path.join(directory, fobj_name)
    if os.path.exists(fname):
      print(f'fobj_name -> {fname}')
      pyobj = self.pickleLearn.PickleLearn().load_pyobj(fname=fname)
    else:
      self.pickleLearn.PickleLearn().dump_pyobj(pyobj=pyobj, fname=fname)

    return pyobj

  def get_df_fig_top_side_view_for_manuscript(self, directory,
                                              fobj_name,
                                              dbname_list=['O2H_Si_P_2V_Gra_Si_top',
                                                           'O2H_Si_P_2V_Gra_P_top'],
                                              df_index_list=['O2H@Si-P-2V-Gra Si top',
                                                             'O2H@Si-P-2V-Gra P top'],
                                              is_save=True,
                                              ):
    """获取图片df (包含顶视图和侧视图), 用于
    self.PylatexFeatures.Doc.figure_list_with_top_front_view(
        fnames_list=df_fig_O2_Si_P_2V_Gra['fig'].array,
        sub_caption_list=df_fig_O2_Si_P_2V_Gra.index.array,...)  的参数

    Args:
        directory (_type_): _description_
        fobj_name (_type_): _description_
        dbname_list (list, optional): _description_. Defaults to ['O2H_Si_P_2V_Gra_Si_top', 'O2H_Si_P_2V_Gra_P_top'].
        df_index_list (list, optional): _description_. Defaults to ['O2H@Si-P-2V-Gra Si top', 'O2H@Si-P-2V-Gra P top'].

    Returns:
        _type_: _description_
    """

    fname = os.path.join(directory, fobj_name)
    if os.path.exists(fname):
      df = self.pickleLearn.PickleLearn().load_pyobj(fname=fname)
    else:
      fig_list = []
      for adsorbate_on_slab in dbname_list:
        directory = self.DataBase.get_directory(
            dbname=adsorbate_on_slab)
        fname_list = self.DealDataStructure.ovito_fig(
        ).wrapper_atoms_structure(directory=directory)
        fig_list.append(fname_list[1:])  # 顶视图和侧视图
      df = pd.DataFrame(data={'fig': fig_list}, index=df_index_list)
      if is_save:
        df.to_pickle(fname)

    return df

  def get_df_Eads_for_manuscript(
      self,
      directory,
      fobj_name,
      adsorbate='O',
      slab='Si_P_2V_Gra',
      adsorbate_on_slab_list=['O_Si_P_2V_Gra_P_top',
                              'O_Si_P_2V_Gra_SiP_bridge',
                              'O_Si_P_2V_Gra_Si_top',
                              ],
      df_index_list=['Si-P-2V-Gra P top',
                     'Si-P-2V-Gra SiP bridge',
                     'Si-P-2V-Gra Si top',
                     ],
      is_save_obj=True,
  ):
    """获取df, 用于
    table = self.PylatexFeatures.Doc.table_tabu(df=df, ...)
    """
    fname = os.path.join(directory, fobj_name)
    if os.path.exists(fname):
      df = self.pickleLearn.PickleLearn().load_pyobj(fname=fname)
    else:
      df = self.get_df_E_ads_with_multiple_confs(
          adsorbate=adsorbate,
          slab=slab,
          adsorbate_on_slab_list=adsorbate_on_slab_list,
          df_index_list=df_index_list,
      )
      if is_save_obj:
        self.pickleLearn.PickleLearn().dump_pyobj(df, fname=fname)
    return df

  # other

  def calculate_C_v(self, Omega=1,
                    omega_list=[1, 2, 3],
                    T=298.15,
                    ):
    """使用振动频率计算材料的热容
    公式: k_B/Omega*np.sum((hbar*omega/(k_B*T))**2 *
                    np.exp(hbar*omega/(k_B*T)) *
                    (np.exp(hbar*omega/(k_B*T))-1)**(-2))
    Omega 是晶胞中的原子数,
    omega_list 是频率列表, 以Hz为单位？
    """
    from scipy import constants
    import numpy as np

    k_B = constants.Boltzmann
    hbar = constants.hbar
    omega = np.array(omega_list)
    C_v = (
        k_B
        / Omega
        * np.sum(
            (hbar * omega / (k_B * T)) ** 2
            * np.exp(hbar * omega / (k_B * T))
            * (np.exp(hbar * omega / (k_B * T)) - 1) ** (-2)
        )
    )
    return C_v

  def get_phi(self, element='B'):
    # Φ ¼ðEx=ECÞ ´ ðAx=ACÞ
    def get_Ex_Ea(element='C'):
      E_X = self.Base.get_atomic_electronegativity(atomic_symbel=element)
      A_X = self.Base.get_atomic_electron_affinity(element=element)
      return E_X, A_X
    E_C, A_C = get_Ex_Ea(element='C')
    E_X, A_X = get_Ex_Ea(element=element)
    phi = E_X/E_C * A_X/A_C
    return phi

  # write_annotation
  def write_annotation(self, directory, string, fname="anotation.md"):
    """给计算目录添加注释

    Args:
        directory (_type_): _description_
        string (str, optional): _description_. Defaults to 'x'.
        fname (str, optional): _description_. Defaults to 'anotation.md'.
    """
    fname = os.path.join(directory, fname)
    with open(file=fname, mode="a+") as f:
      f.write(string + "\n")
    pass

  def read_annotation(self, directory, fname="anotation.md"):
    """读取计算目录添加注释

    Args:
        directory (_type_): _description_
        fname (str, optional): _description_. Defaults to 'anotation.md'.
    """
    fname = os.path.join(directory, fname)
    with open(file=fname) as f:
      anotation = f.read()
    print(anotation)

  def merge_pdfs_horizontally(self, pdf_paths, output_path):
    """把多个pdf图片 水平合并至一个pdf图片
    merge_pdfs_horizontally(['slab1.pdf', 'slab2.pdf',
                        'slab3.pdf'], 'slabs.pdf')
    Args:
        pdf_paths (_type_): _description_
        output_path (_type_): _description_
    """
    from py_package_learn.pymupdf_learn import pymupdfLearn

    pymupdfLearn.Features().merge_pdfs_horizontally(
        pdf_paths=pdf_paths, output_path=output_path
    )
    pass

  def transfer_eV2kJ_mol(self, v_eV=1):
    """把 eV 的能量单位转换为 kJ/mol 单位

    Args:
        v_eV (int, optional): _description_. Defaults to 1.

    Returns:
        _type_: _description_
    """

    from scipy import constants

    elementary_charge = constants.elementary_charge
    # k = 1.602176634e-19 * 1e-3 * 6.02214076e23 = 96.485
    k = elementary_charge * 1e-3 * constants.Avogadro
    kJ_mol = v_eV * k
    return kJ_mol

  def get_phonon_energy(self):
    """计算Gibbs自由能变 ΔG = G_ion - G_solid
    铜的溶解势为 0.34 V, z=2, 那么根据 U_diss = -delta_G/zF, ΔG=-0.68 eV
    电子能量部分
    固体金属铜的自由能: G_solid = F_el + F_ph
    电子自由能(F_el)：可以从 VASP 输出文件中提取。声子自由能(F_ph)：由 Phonopy 计算得到。
    以后有空再问 gpt
    G_ion 好像就是 nelect=9 然后考虑溶剂化效应, 体系的总能量, 我以后验证下
    """

    pass

  def pdf_page_to_image(self, fname_pdf="xx.pdf", page_number=0):
    from py_package_learn.pymupdf_learn import pymupdfLearn

    image = pymupdfLearn.Features().pdf_page_to_image(
        fname_pdf=fname_pdf, page_number=page_number
    )
    return image

  def get_minimum_energy(self,
                         d_list,
                         directory_for_save='/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/X_graphene/Br_DVG/final'):
    """从两个不同的吸附构型中选择能量最低的构型

    Args:
        d_list (_type_): _description_
        directory_for_save (str, optional): _description_. Defaults to '/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/X_graphene/Br_DVG/final'.
    """
    energy_list = []
    for d in d_list:
      energy = self.DataBase.get_energy_from_dir(
          directory=d,)
      energy_list.append(energy)
    e_arr = np.array(energy_list)
    directory = d_list[e_arr.argmin()]
    directory_for_save = directory_for_save + os.path.basename(directory)
    # shutil.copytree(directory, directory_for_save, dirs_exist_ok=True)
    print(directory)
