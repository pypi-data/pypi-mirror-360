import emmet.core
import mp_api
import mp_api.client
import emmet.core.summary
from emmet.core.thermo import ThermoType
import pandas as pd


class MpApiLearn():
  def __init__(self) -> None:
    """学习文档 https://docs.materialsproject.org/downloading-data/using-the-api/getting-started

    使用提供的Python客户端通过API访问Materials Project数据。请参阅网站上的API页面，以获取此处提供的一些信息的额外参考
    """
    self.init()
    pass

  def install(self):
    string = """ * 安装 
    conda install mp-api
    pip install mp_api
    - 或者:
    git clone https://github.com/materialsproject/api
    cd api
    pip install -e 
    """
    print(string)
    return None

  def init(self):
    # 1. 注册账号: https://next-gen.materialsproject.org/dashboard
    # 2. 获取秘钥: 为了使用客户端，需要API密钥。这是提供给每个材料项目帐户的唯一密钥。您的API密钥可以在您的个人资料仪表板页面或登录后的主API页面上找到。
    self.my_API_Key = 'aKB0GGIGwkraQwvSLIkYLfvxOMtnjaKQ'

  def get_mpr(self):
    """获取mpr对象"""
    # mp_api.client.MPRester() # 这个出错
    # with mp_api.client.MPRester(api_key=self.my_API_Key) as mpr:
    #   return mpr
    from py_package_learn.pymatgen_learn import pymatgenLearn
    mpr = pymatgenLearn.PymatgenLearn().get_mpr()
    return mpr

  def learn(self):
    mpr = self.get_mpr()
    # 大多数材料属性数据可作为特定材料的汇总数据。要使用Materials Project id查询汇总数据，应使用以下搜索方法：
    docs = mpr.materials.summary.search(
        material_ids=["mp-149", "mp-13", "mp-22526"]
    )

    example_doc = docs[0]
    mpid = example_doc.material_id
    formula = example_doc.formula_pretty
    # A list of available property fields can be obtained by examining one of these objects, or from the MPRester with:
    list_of_available_fields = mpr.materials.summary.available_fields

    with mp_api.client.MPRester(
            "your_api_key_here", monty_decode=False, use_document_model=False) as mpr:
      docs = mpr.materials.summary.search()
      # save docs to file .？
      # 输出列表，并将列表保存为csv文件
      test = pd.DataFrame(docs)  # 转csv内容
      test.to_csv('./a.csv', encoding='gbk')

    docs = mpr.materials.summary.search(
        elements=["Si", "O"], band_gap=(0.5, 1.0),
        fields=["material_id", "band_gap", "volume"]
    )
    example_doc = docs[0]
    mpid = example_doc.material_id       # a Materials Project ID
    formula = example_doc.formula_pretty  # a formula
    volume = example_doc.volume          # a volume
    example_doc.formula_pretty

    docs = mpr.materials.summary.search(
        has_props=["dielectric", "dos"], fields=["material_id"]
    )
    # 获得用于计算的初始结构
    docs = mpr.materials.search(
        elements=["Si", "O"], num_sites=(0, 10),
        fields=["initial_structures"]
    )
    example_doc = docs[0]
    initial_structures = example_doc.initial_structures

  def example(self):
    mpr = self.get_mpr()
    # Structure data for silicon (mp-149)
    docs = mpr.materials.summary.search(
        material_ids=["mp-149"], fields=["structure"])
    structure = docs[0].structure
    # -- Shortcut for a single Materials Project ID:
    structure = mpr.get_structure_by_material_id("mp-149")
    # Find all Materials Project IDs for entries with dielectric data
    docs = mpr.materials.summary.search(
        has_props=[emmet.core.summary.HasProps.dielectric], fields=[
            "material_id"]
    )
    mpids = [doc.material_id for doc in docs]

    # Calculation (task) IDs and types for silicon (mp-149)
    docs = mpr.materials.search(material_ids=["mp-149"], fields=["calc_types"])
    task_ids = docs[0].calc_types.keys()
    task_types = docs[0].calc_types.values()
    # -- Shortcut for a single Materials Project ID:
    task_ids = mpr.get_task_ids_associated_with_material_id("mp-149")
    # Band gaps for all materials containing only Si and O
    docs = mpr.materials.summary.search(
        chemsys="Si-O", fields=["material_id", "band_gap"]
    )
    mpid_bgap_dict = {doc.material_id: doc.band_gap for doc in docs}
    # Chemical formulas for all materials containing at least Si and O
    docs = mpr.materials.summary.search(
        elements=["Si", "O"], fields=["material_id", "band_gap", "formula_pretty"]
    )
    mpid_formula_dict = {
        doc.material_id: doc.formula_pretty for doc in docs
    }
    # Material IDs for all ternary oxides with the form ABC3
    docs = mpr.materials.summary.search(
        chemsys="O-*-*", formula="ABC3",
        fields=["material_id"]
    )
    mpids = [doc.material_id for doc in docs]
    # Stable materials (on the GGA/GGA+U hull) with large band gaps (>3eV)
    docs = mpr.materials.summary.search(
        band_gap=(3, None), is_stable=True, fields=["material_id"]
    )
    stable_mpids = [doc.material_id for doc in docs]
    # Band structures for silicon (mp-149)
    from emmet.core.electronic_structure import BSPathType
    # -- line-mode, Setyawan-Curtarolo (default):
    bs_sc = mpr.get_bandstructure_by_material_id("mp-149")

    # -- line-mode, Hinuma et al.:
    bs_hin = mpr.get_bandstructure_by_material_id(
        "mp-149", path_type=BSPathType.hinuma)

    # -- line-mode, Latimer-Munro:
    bs_hin = mpr.get_bandstructure_by_material_id(
        "mp-149", path_type=BSPathType.latimer_munro)

    # -- uniform:
    bs_uniform = mpr.get_bandstructure_by_material_id(
        "mp-149", line_mode=False)
    # Density of states for silicon (mp-149)
    dos = mpr.get_dos_by_material_id("mp-149")
    # Charge density for silicon (mp-149)
    chgcar = mpr.get_charge_density_from_material_id("mp-149")
    # Phase diagram for the Li-Fe-O chemical system
    # -- GGA/GGA+U/R2SCAN mixed phase diagram
    pd = mpr.materials.thermo.get_phase_diagram_from_chemsys(
        chemsys="Li-Fe-O",
        thermo_type=ThermoType.GGA_GGA_U_R2SCAN)
