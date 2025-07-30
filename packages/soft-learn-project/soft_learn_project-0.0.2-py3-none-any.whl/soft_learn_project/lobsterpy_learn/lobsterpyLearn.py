import lobsterpy
import lobsterpy.structuregraph
import pymatgen
from matplotlib import style
from pathlib import Path
import warnings
import pymatgen.io
import pymatgen.io.lobster
import os
import ase.io
import ase.calculators.vasp
import numpy as np
import matplotlib.pyplot as plt
import re
# os 这两行是为了避免出现空白窗口, 是否有其他副作用目前未知
os.environ['ETS_TOOLKIT'] = 'null'
os.environ['QT_API'] = 'pyside6'  # 或 'pyqt5'，具体看你安装的库
warnings.filterwarnings('ignore')


class LobsterpyLearn():
  def __init__(self) -> None:
    """
    lobsterpy 是一个用于分析和可视化电子结构的 Python 包，特别用于处理和分析由 LOBSTER（a software for calculating and analyzing local orbital bonding in molecular and solid-state systems）产生的数据。LOBSTER 是一种计算化学工具，主要用于分析分子和固体系统中的局部轨道键合特征，能够帮助研究者理解材料中的电子结构和化学键合特性。

    学习文档: https://jageo.github.io/LobsterPy/installation/index.html

    lobsterpy 主要功能：
    数据读取和解析： lobsterpy 可以读取 LOBSTER 输出的数据文件，并将其转换为 Python 数据结构，方便进一步处理和分析。

    COHP（Chemical Orbital Hamilton Population）分析： lobsterpy 支持对 COHP 结果的处理，COHP 是描述化学键合强度的一个重要工具，lobsterpy 可以提取并可视化 COHP 曲线。

    局部轨道分析： lobsterpy 提供了对局部轨道和原子轨道间键合的分析功能，允许用户更好地理解系统中的电子分布和相互作用。

    数据可视化： lobsterpy 提供了多种图形化工具，可以将计算结果以图形方式呈现，帮助研究者更加直观地理解电子结构特性。

    集成其他工具： lobsterpy 还支持与其他计算化学软件（如 VASP）结合使用，进一步增强其分析功能。
    """
    pass

  def install():
    string = """安装 lobsterpy：
    你可以通过以下方式安装 lobsterpy：
    pip install lobsterpy
    pip install lobsterpy[featurizer] # 带有特性的安装
    conda install -c conda-forge lobsterpy
    * 某些功能的实现还需要一些包
    conda install pygraphviz 
    conda install mendeleev
    """
    print(string)
    return None

  def cite_info(self):
    string = """How to cite?
    A. A. Naik, K. Ueltzen, C. Ertural, A. J. Jackson, J. George, Journal of Open Source Software 2024, 9, 6286. https://joss.theoj.org/papers/10.21105/joss.06286.

    J. George, G. Petretto, A. Naik, M. Esters, A. J. Jackson, R. Nelson, R. Dronskowski, G.-M. Rignanese, G. Hautier, ChemPlusChem 2022, 87, e202200123. https://doi.org/10.1002/cplu.202200123 (Information on the methodology of the automatic analysis)

    Please cite pymatgen, Lobster, and ChemEnv correctly as well.
    """
    print(string)
    return None

  def get_analyse(self,
                  directory='/Users/wangjinlong/job/soft_learn/py_package_learn/lobsterpy_learn/LobsterPy/tests/test_data/CdF_comp_range',
                  surfix='.gz'):
    import lobsterpy.cohp.analyze
    analyse = lobsterpy.cohp.analyze.Analysis(
        path_to_poscar=os.path.join(directory, "POSCAR"+surfix),
        path_to_icohplist=os.path.join(
            directory, directory, "ICOHPLIST.lobster" + surfix),
        path_to_cohpcar=os.path.join(
            directory, directory, "COHPCAR.lobster"+surfix),
        path_to_charge=os.path.join(
            directory, directory, "CHARGE.lobster"+surfix),
        which_bonds="cation-anion",
    )
    return analyse

  def get_describe(self, analyse):
    import lobsterpy.cohp.describe
    # Initialize Description object and to get text description of the analysis
    describe = lobsterpy.cohp.describe.Description(analysis_object=analyse)
    describe.write_description()
    # describe.plot_cohps(ylim=[-10, 2], xlim=[-4, 4])
    return describe

  def get_static_plots(self,
                       describe,
                       ylim=[-10, 2], xlim=[-4, 4]):
    # Get static plots for detected relevant bonds
    describe.plot_cohps(ylim=ylim, xlim=xlim)
    return None

  def get_interactive_plots(self,
                            describe):
    # analyse = self.get_analyse(directory='/Users/wangjinlong/job/soft_learn/py_package_learn/lobsterpy_learn/LobsterPy/tests/test_data/CdF_comp_range')
    # describe = self.get_describe(analyse=analyse)

    # Get interactive plots of relevant bonds,
    # Setting label_resolved arg to True will plot each COHP curve separately, alongside summed COHP for the bonds.
    fig = describe.plot_interactive_cohps(label_resolved=True,
                                          hide=True)
    fig.show(renderer='notebook')
    return None

  def get_analysis_results(self,
                           analyse):
    """analyze: lobsterpy.cohp.analyze
    """

    s = r"""# Dict summarizing the automatic analysis results
    result_dict = analyse.condensed_bonding_analysis
    # Dict with bonds identified
    analyse.final_dict_bonds
    # Dict with ions and their co-ordination environments
    analyse.final_dict_ions
    """
    print(s)
    # Dict summarizing the automatic analysis results
    result_dict = analyse.condensed_bonding_analysis
    # Dict with bonds identified
    analyse.final_dict_bonds
    # Dict with ions and their co-ordination environments
    analyse.final_dict_ions
    return result_dict

  def get_analyse_cobicar(self,
                          directory='/Users/wangjinlong/job/soft_learn/py_package_learn/lobsterpy_learn/LobsterPy/tests/test_data/CdF_comp_range'):
    import lobsterpy.cohp.analyze
    # You can also perform automatic analysis using COBICAR(ICOBILIST.lobster) or COOPCAR(ICOOPLIST.lobster). You would need to set are_cobis/are_coops to True depending on the type of file you decide to analyze when you initialize the Analysis object. Change the default noise_cutoff value to 0.001 or lower, as ICOOP and ICOBI typically have smaller values and different units than ICOHP. Below is an example code snippet.
    analyse = lobsterpy.cohp.analyze.Analysis(
        path_to_poscar=os.path.join(directory, "POSCAR.gz"),
        path_to_icohplist=os.path.join(directory, "ICOBILIST.lobster.gz"),
        path_to_cohpcar=os.path.join(directory, "COBICAR.lobster.gz"),
        path_to_charge=os.path.join(directory, "CHARGE.lobster.gz"),
        which_bonds="cation-anion",
        are_cobis=True,
        noise_cutoff=0.001,
    )
    return analyse

  def get_analyse_orbital(self,
                          directory='/Users/wangjinlong/job/soft_learn/py_package_learn/lobsterpy_learn/LobsterPy/tests/test_data/CdF_comp_range'):
    import lobsterpy.cohp.analyze
    # Advanced usage : Analysis, Description
    # LobsterPy now also allows for automatic orbital-wise analysis and plotting of COHPs, COBIs, and COOPs. To switch on orbital-wise analysis, one must set orbital_resolved arg to True. By default, orbitals contributing 5% or more relative to summed ICOHPs are considered in the analysis. One can change this default threshold using the orbital_cutoff argument. Here, we will set this cutoff value to 3%.
    analyse = lobsterpy.cohp.analyze.Analysis(
        path_to_poscar=os.path.join(directory, "POSCAR.gz"),
        path_to_icohplist=os.path.join(directory, "ICOHPLIST.lobster.gz"),
        path_to_cohpcar=os.path.join(directory, "COHPCAR.lobster.gz"),
        path_to_charge=os.path.join(directory, "CHARGE.lobster.gz"),
        which_bonds="cation-anion",
        orbital_resolved=True,
        orbital_cutoff=0.03,
    )
    """只有在初始化analysis对象时，将 orbital_resolved 参数设为True时，才能从轨道解析分析中获得绘图。如果不这样做，您将遇到错误。此外，只有交互式绘图仪才能绘制轨道解析分析的结果，因为静态绘图仪的可读性不高。在任何情况下，如果需要，您都可以生成静态图。

    Returns:
        _type_: _description_
    """
    # Access the dict summarizing the results including orbital-wise analysis data
    analyse.condensed_bonding_analysis
    # In the above output, you will now see a key named orbital_data associated with each relevant bond identified. The orbital_summary_stats key contains the orbitals that contribute the most to the bonding and antibonding interactions, and values are reported there in percent.
    return analyse

  def get_interactive_plots_orbital(self,
                                    analyse):
    import lobsterpy.cohp.describe
    # Initialize the Description object
    describe = lobsterpy.cohp.describe.Description(analysis_object=analyse)
    describe.write_description()
    # Automatic interactive plots
    fig = describe.plot_interactive_cohps(
        orbital_resolved=True, ylim=[-15, 5], hide=True)
    fig.show(renderer='notebook')
    return None

  def get_calculation_quality_description(self,
                                          directory='/Users/wangjinlong/job/soft_learn/py_package_learn/lobsterpy_learn/LobsterPy/tests/test_data/K3Sb'):
    """Get LOBSTER calculation quality and description

    Args:
        directory (str, optional): _description_. Defaults to '/Users/wangjinlong/job/soft_learn/py_package_learn/lobsterpy_learn/LobsterPy/tests/test_data/K3Sb'.

    Returns:
        _type_: _description_
    """
    import lobsterpy.cohp.describe
    import lobsterpy.cohp.analyze
    # directory = Path("LobsterPy") / "tests" / "test_data" / "K3Sb"
    calc_quality_K3Sb = lobsterpy.cohp.analyze.Analysis.get_lobster_calc_quality_summary(
        path_to_poscar=os.path.join(directory, "POSCAR.gz"),
        path_to_charge=os.path.join(directory, "CHARGE.lobster.gz"),
        path_to_lobsterin=os.path.join(directory, "lobsterin.gz"),
        path_to_lobsterout=os.path.join(directory, "lobsterout.gz"),
        # if POTCAR exists, then provide path_to_potcar and set this to None
        potcar_symbols=["K_sv", "Sb"],
        path_to_bandoverlaps=os.path.join(
            directory, "bandOverlaps.lobster.gz"),
        dos_comparison=True,  # set to false to disable DOS comparisons
        bva_comp=True,  # set to false to disable LOBSTER charge classification comparisons with BVA method
        path_to_doscar=os.path.join(directory, "DOSCAR.LSO.lobster.gz"),
        e_range=[-20, 0],
        path_to_vasprun=os.path.join(directory, "vasprun.xml.gz"),
        n_bins=256,
    )
    # Get a text description from calculation quality summary dictionary
    calc_quality_k3sb_des = lobsterpy.cohp.describe.Description.get_calc_quality_description(
        calc_quality_K3Sb
    )
    lobsterpy.cohp.describe.Description.write_calc_quality_description(
        calc_quality_k3sb_des)
    return None

  def using_plotting_utilities_e1(self):
    import lobsterpy.plotting
    analyse = self.get_analyse()
    # Using PlainCohpPlotter to get static plots of relevant bonds from Analysis object

    # Use the LobsterPy style sheet for the generated plots
    style.use(lobsterpy.plotting.get_style_list()[0])

    cohp_plot_static = lobsterpy.plotting.PlainCohpPlotter(
        are_cobis=False, are_coops=False)
    for plot_label, label_list in analyse.get_site_bond_resolved_labels().items():
      cohp = analyse.chemenv.completecohp.get_summed_cohp_by_label_list(
          label_list=label_list)
      cohp_plot_static.add_cohp(plot_label, cohp)
    cohp_plot_static.get_plot(ylim=[-15, 2])

  def using_plotting_utilities_e2(self):
    import lobsterpy.plotting
    analyse = self.get_analyse_orbital()
    # Using PlainCohpPlotter to get static plots of relevant orbitals COHPs from Analysis object
    style.use('default')  # Complete reset the matplotlib figure style
    # use one of the existing matplotlib style sheet
    style.use('seaborn-v0_8-ticks')

    cohp_plot_static = lobsterpy.plotting.PlainCohpPlotter()
    for plot_label, orb_data in analyse.get_site_orbital_resolved_labels().items():
      for orb, plot_data in orb_data.items():
        mapped_bond_labels = [
            item for item in plot_data["bond_labels"] for _ in range(len(plot_data["relevant_sub_orbitals"]))
        ]
        cohp = analyse.chemenv.completecohp.get_summed_cohp_by_label_and_orbital_list(label_list=mapped_bond_labels,
                                                                                      orbital_list=plot_data["relevant_sub_orbitals"] *
                                                                                      len(plot_data["bond_labels"]))
        cohp_plot_static.add_cohp(orb, cohp)
    cohp_plot_static.get_plot(ylim=[-15, 2])

    pass

  def using_plotting_utilities_e3_interactive(self):
    import lobsterpy.plotting
    analyse = self.get_analyse_orbital()
    # Using interactive plotter to add relevant cohps
    interactive_cohp_plot = lobsterpy.plotting.InteractiveCohpPlotter()
    interactive_cohp_plot.add_all_relevant_cohps(
        analyse=analyse, label_resolved=False, orbital_resolved=True, suffix='')
    fig = interactive_cohp_plot.get_plot(ylim=[-15, 2])
    fig.show(renderer='notebook')
    return None

  def get_dos(self,
              directory='/Users/wangjinlong/job/soft_learn/py_package_learn/lobsterpy_learn/LobsterPy/tests/test_data/NaCl_comp_range'):
    import pymatgen.io.lobster
    # directory = Path("LobsterPy") / "tests" / "test_data" / "NaCl_comp_range"
    dos = pymatgen.io.lobster.Doscar(
        doscar=os.path.join(directory, 'DOSCAR.lobster.gz'),
        structure_file=os.path.join(directory, 'POSCAR.gz'),
    )
    return dos

  def get_dos_plotter(self,
                      summed=True,
                      stack=False,
                      sigma=None):
    import lobsterpy.plotting
    # 设置图形风格
    # Plot total, element and spd dos
    style.use('default')  # Complete reset the matplotlib figure style
    # Use the LobsterPy style sheet for the generated plots
    style.use(lobsterpy.plotting.get_style_list()[0])

    dos_plotter = lobsterpy.plotting.PlainDosPlotter(summed=summed,
                                                     stack=stack,
                                                     sigma=sigma)
    return dos_plotter

  def plot_dos(self,
               dos,
               dos_plotter):
    """dos: pymatgen.io.lobster.Doscar,
    dos_plotter: lobsterpy.plotting.PlainDosPlotter
    """
    import lobsterpy.plotting
    dos: pymatgen.io.lobster.Doscar
    dos_plotter: lobsterpy.plotting.PlainDosPlotter
    # 总DOS
    # dos_plotter.add_dos(dos=dos.completedos, label='Total DOS')
    # 元素 DOS
    # dos_plotter.add_dos_dict(
    #     dos_dict=dos.completedos.get_element_dos())  # Add element dos
    # PDOS
    # dos_plotter.add_dos_dict(
    #     dos_dict=dos.completedos.get_spd_dos())  # add spd dos

    # LPDOS
    # Plotting DOS at particular site and orbital
    # 可以画局域投影 LPDOS
    # dos_plotter = PlainDosPlotter(summed=True, stack=False, sigma=0.03)
    dos_plotter.add_site_orbital_dos(dos=dos.completedos,
                                     site_index=0,  # 画哪一个原子的
                                     orbital='3s')
    # 绘图
    dos_plotter.get_plot(xlim=[-10, 3])
    pass

  def plot_lpdos(self,
                 dos,
                 dos_plotter,
                 site_index=0,  # 画哪一个原子的
                 orbital='3s',
                 xlim=[-10, 3]):
    """dos: pymatgen.io.lobster.Doscar,
    dos_plotter: lobsterpy.plotting.PlainDosPlotter,
    """
    import pymatgen.io.lobster
    import lobsterpy.plotting
    dos: pymatgen.io.lobster.Doscar
    dos_plotter: lobsterpy.plotting.PlainDosPlotter

    # Plotting DOS at particular site and orbital
    dos_plotter.add_site_orbital_dos(dos=dos.completedos,
                                     site_index=site_index,
                                     orbital=orbital)
    # 绘图
    dos_plotter.get_plot(xlim=xlim,)
    pass

  def plot_lpdos_wrapper(self,
                         directory='/Users/wangjinlong/job/soft_learn/py_package_learn/lobsterpy_learn/LobsterPy/tests/test_data/NaCl_comp_range',
                         summed=True,
                         stack=False,
                         sigma=0.03,
                         site_index=0,
                         orbital='3s',
                         xlim=[-10, 3],
                         ):
    """Plot DOS from Lobster
    py4vasp 直接从vasp计算数据中也能画DOS, 这里只是提供了一种从lobster 计算结果中画 DOS 的方法
    """
    dos = self.get_dos(directory=directory)
    dos_plotter = self.get_dos_plotter(summed=summed,
                                       stack=stack,
                                       sigma=sigma)
    self.plot_lpdos(dos=dos,
                    dos_plotter=dos_plotter,
                    site_index=site_index,
                    orbital=orbital,
                    xlim=xlim)
    pass

  def get_structure_graph(self,
                          directory='/Users/wangjinlong/job/soft_learn/py_package_learn/lobsterpy_learn/LobsterPy/tests/test_data/NaCl_comp_range'):
    """Generate structure graph objects with LOBSTER data
    - 需要 pygrahviz

    """
    import lobsterpy.structuregraph.graph
    # Below code snippet will generate a networkx graph object with ICOHP, ICOOP, and ICOBI data as edge properties and charges as node properties.

    # (Change this cell block type to Code or copy it from here when executing locally)
    graph_NaCl_all = lobsterpy.structuregraph.graph.LobsterGraph(
        path_to_poscar=os.path.join(directory, "POSCAR.gz",),
        path_to_charge=os.path.join(directory, "CHARGE.lobster.gz",),
        path_to_cohpcar=os.path.join(directory, "COHPCAR.lobster.gz",),
        path_to_icohplist=os.path.join(directory, "ICOHPLIST.lobster.gz",),
        add_additional_data_sg=True,
        path_to_icooplist=os.path.join(directory, "ICOOPLIST.lobster.gz",),
        path_to_icobilist=os.path.join(directory, "ICOBILIST.lobster.gz",),
        path_to_madelung=os.path.join(
            directory, "MadelungEnergies.lobster.gz",),
        which_bonds="all",
        start=None,
    )
    graph_NaCl_all.sg.graph.nodes.data()  # view node data
    graph_NaCl_all.sg.graph.edges.data()  # view edge data
    return graph_NaCl_all

  # for ML
  def get_Coxx_features4ml(self,
                           directory='/Users/wangjinlong/job/soft_learn/py_package_learn/lobsterpy_learn/LobsterPy/tests/test_data/Featurizer_test_data/Lobster_calcs'):
    """* Featurizer usage examples (Generates features from LOBSTER data for ML studies)

    - To use the batch featurizers, the path to the parent directory containing LOBSTER calculation outputs needs to be provided. For example, your directory structure needs to be like this:

    - parent_dir/lobster_calc_output_dir_for_compound_1/ parent_dir/lobster_calc_output_dir_for_compound_2/ parent_dir/lobster_calc_output_dir_for_compound_3/

    - the lobster_calc_output_dir_for_compound_* directory should contain all your LOBSTER outputs and POSCAR file.

    - In such a case path_to_lobster_calcs="parent_dir" needs to be set
    """
    from lobsterpy.featurize.batch import (BatchCoxxFingerprint, BatchDosFeaturizer,
                                           BatchSummaryFeaturizer, BatchStructureGraphs)
    fp_cohp_bonding = BatchCoxxFingerprint(
        path_to_lobster_calcs=directory,
        e_range=[-15, 0],
        feature_type="bonding",
        normalize=True,  # affects only the fingerprint similarity matrix computation
        tanimoto=True,  # affects only the fingerprint similarity matrix computation
        n_jobs=3,
        # changing this to cobi/coop will result in reading cobicar/coopcar file
        fingerprint_for='cohp'
    )
    # Access the fingerprints dataframe
    fp_cohp_bonding.fingerprint_df
    # Get the fingerprints similarity matrix
    fp_cohp_bonding.get_similarity_matrix_df()

    pass

  def get_dos_features4ml(self,
                          directory='/Users/wangjinlong/job/soft_learn/py_package_learn/lobsterpy_learn/LobsterPy/tests/test_data/Featurizer_test_data/Lobster_calcs'):
    """BatchDosFeaturizer provides a convenient way to extract LOBSTER DOS moment features and fingerprints in the form of pandas dataframe from the LOBSTER calculation directory. The extracted features consist of the following:

    Element and PDOS center, width, skewness, kurtosis, and edges

    PDOS or total DOS fingerprint objects
    """

    # Initialize batch DOS featurizer (Change this cell block type to Code and remove formatting when executing locally)
    import lobsterpy.featurize.batch
    batch_dos = lobsterpy.featurize.batch.BatchDosFeaturizer(
        path_to_lobster_calcs=directory,  # path to parent lobster calcs
        use_lso_dos=True,  # will enforce using DOSCAR.LSO.lobster
        # set to false to not have element moments dos features
        add_element_dos_moments=True,
        e_range=None,  # setting this to none results in features computed for the entire energy range
        # fingerprint type (s,p,d,f, summed_pdos)
        fingerprint_type="summed_pdos",
        n_bins=256,
        n_jobs=3,)
    # get the DOS moments df
    df = batch_dos.get_df()
    # get the DOS fingerprints df
    df = batch_dos.get_fingerprints_df()
    return df

  def get_summary_features4ml(self,
                              directory='/Users/wangjinlong/job/soft_learn/py_package_learn/lobsterpy_learn/LobsterPy/tests/test_data/Featurizer_test_data/Lobster_calcs'):
    """BatchSummaryFeaturizer
    BatchSummaryFeaturizer provides a convenient way to extract summary stats as pandas dataframe from the LOBSTER calculation directory. The summary stats consist of the following:

    ICOHP, bonding, antibonding percent (mean, min, max, standard deviation) of relevant bonds from LobsterPy analysis (Orbital-wise analysis stats data can also be included: Optional)

    Weighted ICOHP ( ICOOP/ ICOBI: Optional)

    COHP center, width, skewness, kurtosis, edge (COOP/ COBI: Optional)

    Ionicity and Madelung energies for the structure based on Mulliken and Loewdin charges
    """

    import lobsterpy.featurize.batch
    # Initialize batch summary featurizer (Change this cell block type to Code and remove formatting when executing locally)
    summary_features = lobsterpy.featurize.batch.BatchSummaryFeaturizer(
        path_to_lobster_calcs=directory,
        bonds="all",
        include_cobi_data=False,
        include_coop_data=False,
        e_range=[-15, 0],
        n_jobs=3,
    )
    # get summary stats features
    df = summary_features.get_df()
    return df

  def get_BatchStructureGraphs(self,
                               directory='/Users/wangjinlong/job/soft_learn/py_package_learn/lobsterpy_learn/LobsterPy/tests/test_data/Featurizer_test_data/Lobster_calcs'):
    """
    BatchStructureGraphs
    BatchStructureGraphs provides a convenient way to generate structure graph objects with LOBSTER data in the form of pandas dataframe from a set of the LOBSTER calculation directories.
    """
    import lobsterpy.featurize.batch
    # Initialize batch structure graphs featurizer (Change this cell block type to Code and remove formatting when executing locally)
    batch_sg = lobsterpy.featurize.batch.BatchStructureGraphs(path_to_lobster_calcs=directory,
                                                              add_additional_data_sg=True,
                                                              which_bonds='all',
                                                              n_jobs=3,
                                                              start=None)
    # get the structure graphs df
    df = batch_sg.get_df()
    return df

  def example(self):
    import lobsterpy.cohp.describe
    import lobsterpy.cohp.analyze
    # Change directory to your Lobster computations (Change this cell block type to Code and remove formatting when executing locally)
    directory = Path("LobsterPy") / "tests" / "test_data" / "CdF_comp_range"

    # Initialize Analysis object
    analyse = lobsterpy.cohp.analyze.Analysis(
        path_to_poscar=directory / "POSCAR.gz",
        path_to_icohplist=directory / "ICOHPLIST.lobster.gz",
        path_to_cohpcar=directory / "COHPCAR.lobster.gz",
        path_to_charge=directory / "CHARGE.lobster.gz",
        which_bonds="cation-anion",
    )
    # Initialize Description object and to get text description of the analysis
    describe = lobsterpy.cohp.describe.Description(analysis_object=analyse)
    describe.write_description()
    # Get static plots for detected relevant bonds
    describe.plot_cohps(ylim=[-10, 2], xlim=[-4, 4])
    pass

  # CLI 命令行工具
  def creating_input_files(self):
    """Creating input files
    为此，在INCAR集合中，ISYM = -1（完全网格/对称性关闭）或ISYM = 0（半网格/时间反转）。为了确保WAVECAR被写入，设置LWAVE = . true。对于pCOHP分析，在局部基础上需要有和轨道一样多的能带。

    """
    # 使用LobsterPy，这些复杂的细节可以用一个命令处理。我们需要标准的VASP输入文件，即计算目录中的INCAR、KPOINTS、POTCAR和POSCAR。有了这些文件后，需要运行以下命令：
    string = 'lobsterpy create-inputs'  # 产生
    string = 'lobsterpy create-inputs --file-incar-out <path/to/incar>/INCAR --file-lobsterin <path/to/lobsterin>/lobsterin'
    # 指定目录产生文件
    # 产生 INCAR-0     lobsterin-0
    string = 'lobsterpy create-inputs --file-incar-out lobster/INCAR --file-lobsterin lobster/lobsterin'
    # 别忘记改名为 lobsterin
    pass

  def lobster_submission_script(self,
                                ntasks=4,
                                nodes=1,
                                fname='xxx/qsub.pbs',
                                path_lobster_bin='/Users/wangjinlong/job/soft_learn/lobster_learn/lobster-5.0.0/OSX/lobster-5.0.0-OSX'
                                ):
    string = f"""
    #!/bin/bash -l
    #SBATCH -J lob_job
    #SBATCH --no-requeue
    #SBATCH --export=NONE
    #SBATCH --get-user-env
    #SBATCH -D ./
    #SBATCH --ntasks={ntasks}
    #SBATCH --time=04:00:00
    #SBATCH --nodes={nodes}
    #SBATCH --output=lobsterjob.out.%j
    #SBATCH --error=lobsterjob.err.%j

    export OMP_NUM_THREADS=48
    
    {path_lobster_bin}
    """
    with open(fname, mode='w') as f:
      line_list = string.split(sep='\n')
      for line in line_list:
        f.write(line.strip()+'\n')
    return None


class LobsterLearn():
  def __init__(self) -> None:
    r"""当前画图只能是 ISPIN=1 的结果
    引用 \cite{dronskowski1993crystal,deringer2011crystal, nelson2020lobster}
    https://zhuanlan.zhihu.com/p/470592188
    COHP将能带结构能量划分为轨道成对的相互作用, 从化学上来讲, 它是一对相邻原子之间的“键加权”态密度。COHP图显示了成键和反键态对能带结构能量的贡献。ICOHP是基于特定能量窗口范围内对COHP进行积分, ICOHP费米能级以下的值可以理解为原子对之间成键电子数目, 在一定程度上可以体现出键的强度, 它的单位为eV或者kJ/mol。

    COOP 是一个关于能量的函数, 其正值表示对体系能量有降低贡献的轨道重叠（即成键）, 其负值表示对体系能量有升高贡献的轨道重叠（即反键）。
    """
    # 提前在环境变量中设置好 LOSBTER_COMMAND。

    os.environ['LOBSTER_COMMAND'] = f'/Users/wangjinlong/job/soft_learn/lobster_learn/lobster-5.0.0/OSX/lobster-5.0.0-OSX'
    from py_package_learn.matplotlib_learn import matplotlibLearn
    self.MatplotlibFeatures = matplotlibLearn.Features()
    pass

  def steps(self):
    """
    1. 使用默认版本的VASP, 不使用Gamma版本
    2. 使用PAW赝势文件
    3. 删除原有的波函数文件
    4. 做静态计算, NSW = 0,  ISIF = 0
    5. 关闭对称性, ISYM = -1 or 0
    6. NBANDS设置总价电子数更高, 只要查看OUTCAR里面的NBANDS多少, 在INCAR里面,  NBANDS 关键词设置成1.5倍NBANDS
    """
    pass

  def get_wavcar_只用于参考(self, dname='MgO'):
    """获取波函数
    这里选取 6mm 点群的氢化亚铜（CuH）作为例子。首先去 Materials Project 获取结构[4], 然后读取, 建立 VASP 计算器对象（argument里给出计算参数）, 使用 BFGS 优化器进行几何优化：
    """

    import ase.build
    import ase.calculators.vasp
    import ase.optimize
    # atoms = ase.io.read('CuH_mp-24093_computed.cif')
    atoms = ase.build.bulk(name='MgO', crystalstructure="rocksalt", a=4.2)

    calc = ase.calculators.vasp.Vasp(gga='PE', ivdw=11,
                                     nelm=300,
                                     lreal='Auto',
                                     isym=0,
                                     algo='F',
                                     prec='Accurate',
                                     ismear=0,
                                     sigma=0.05,
                                     encut=400,
                                     ediff=1e-6,
                                     gamma=True,
                                     kpts=[2, 2, 2],
                                     setups='recommended',
                                     directory=dname)

    atoms.calc = calc
    ase.optimize.BFGS(atoms).run(fmax=0.01)
    return atoms

  def get_wavecar(self, atoms: ase.Atoms,
                  directory='xxx/lobster',
                  nbands=296,
                  only_write_inputs=False,
                  recalc=False,
                  **kwargs):
    """进行单点计算获取 wavecar
    注意这些设置 ISIF = 0,  关闭对称性, ISYM = -1 or 0

    Args:
        atoms (_type_): _description_
        dname (str, optional): _description_. Defaults to 'Cu'.

    Returns:
        _type_: _description_
    """

    incar_sets_dict = {'isif': 0, 'isym': 0,
                       'ismear': 0, 'nbands': nbands,
                       'ispin': 1,
                       }
    from vasp_learn import calculation
    calculation.Calculations().calc_universal(atoms=atoms,
                                              incar_sets_dict=incar_sets_dict,
                                              directory=directory,
                                              recalc=recalc,
                                              only_write_inputs=only_write_inputs,
                                              **kwargs,)

  def write_labels(self, atoms: ase.Atoms,
                   dname='xxx/lobster',
                   atoms_index_list='None|[[71,72]]',):
    """获取成键原子对
    这里可以直接使用 ase.io.pov 模块里的 get_bondpairs 函数。该函数原理是计算所有原子间距离, 然后遍历与共价半径之和比较, 低于阈值的即认为成键。此后只取原子序号信息, 并且将重复的成键原子对筛除：

    Args:
        atoms (_type_): _description_
        dname (str, optional): _description_. Defaults to 'MgO'.
        atoms_index_list: 只分析两个原子之间的 COHP
    """
    import ase.io.pov
    bondpairs_raw = ase.io.pov.get_bondpairs(atoms)
    bondpairs = []
    for bp in bondpairs_raw:
      tmp = list(bp[:2])
      tmp.sort()
      if tmp not in bondpairs and tmp[0] != tmp[1]:
        bondpairs.append(tmp)
    # 如果给出列表(如[68,69]), 则只分析两个原子之间的 COHP
    if atoms_index_list:
      bondpairs = atoms_index_list

    # 写一个文本文件, 保存成键原子对的序号和元素符号信息：
    with open(f'{dname}/labels', 'w') as f:
      for bp in bondpairs:
        f.write(
            f'{atoms.get_chemical_symbols()[bp[0]]}[{bp[0]}]-{atoms.get_chemical_symbols()[bp[1]]}[{bp[1]}]\n')

  def write_lobsterin(self, dname='MgO'):
    """写 lobsterin 输入文件
    在 python 里直接写 lobsterin 文件。定义能量范围（以费米能级为零点）, 基组（直接使用根据vasp拟合的基组以及默认的基函数）, 使用 Gaussian smearing 的话要给出展宽, 最后将前一节中获得的成键原子对逐行写入（此处要给原子序号加1, 因为python中数组下标是从0开始的）：

    Args:
        dname (str, optional): _description_. Defaults to 'MgO'.
    """
    with open(os.path.join(dname, 'labels')) as f:
      content = f.read()
    result = np.array(re.findall(r'\[(\d+)\]', content), dtype=int)
    bondpairs = [result[i:i+2] for i in range(0, len(result), 2)]

    with open(f'{dname}/lobsterin', 'w') as f:
      f.write('COHPstartEnergy  -10\n')
      f.write('COHPendEnergy  5\n')
      f.write('usebasisset pbeVaspFit2015\n')
      f.write('useRecommendedBasisFunctions\n')
      f.write('gaussianSmearingWidth 0.1\n')  # gaussianSmearingWidth 0.05\n
      for bp in bondpairs:
        f.write(f'cohpbetween atom {bp[0]+1} and atom {bp[1]+1}\n')

  def run_lobster(self, dname='xxx/lobster'):
    """进入 dname 执行 $LOBSTER_COMMAND

    Args:
        dname (str, optional): _description_. Defaults to 'MgO'.
    """
    from py_package_learn.subprocess_learn import subprocessLearn
    subprocessLearn.SubprocessLearn().CLI_popen(
        directory=dname,
        args=[os.environ['LOBSTER_COMMAND']]
    )
    return None

  def read_COHP(self, fn):
    raw = open(fn).readlines()
    raw = [l for l in raw if 'No' not in l][3:]
    raw = [[eval(i) for i in l.split()] for l in raw]
    return np.array(raw)

  def get_data(self, dname='MgO'):
    """读取输出并作图
    lobster 运行结束后, 会在当前目录中写诸多输出文件, 其中比较有用的如下：

    CHARGE.lobster：基于原子重叠布居的 Mulliken 电荷和 Loewdin 电荷
    * COHPCAR.lobster：每一对定义的原子对的 COHP、ICOHP, 作为能量的函数
    DOSCAR.lobster：包含轨道投影信息的态密度, 和 DOSCAR 格式一致
    ICOHPLIST.lobster：每一对定义的原子对的 COHP 积分到费米能级的数值
    这里我们用 python 读取 COHP 相关输出以及前节写好的 labels, 自动画图：

    Args:
        dname (str, optional): _description_. Defaults to 'MgO'.

    Returns: data_cohp, labels_cohp, icohp_ef
        _type_: _description_
    """

    data_cohp = self.read_COHP(f'{dname}/COHPCAR.lobster')
    labels_cohp = [l.strip() for l in open(f'{dname}/labels').readlines()]
    # 从 ICOHPLIST.lobster 文件中获取最后一列
    icohp_ef = [eval(l.split()[-1])
                for l in open(f'{dname}/ICOHPLIST.lobster').readlines()[1:]]

    return data_cohp, labels_cohp, icohp_ef

  # -- 以前考虑的只是 ispin=1 通过改变 plot 函数中的 数据列 画ispin=2 的其它结果
  def calc_lobster(self, atoms,
                   atoms_index_list=[[72, 73]],
                   directory='xxx/lobster',
                   recalc=False,):
    """只是执行 lobster 处理数据, 需要 WAVECAR

    Args:
        atoms (_type_): _description_
        atoms_index_list (list, optional): _description_. Defaults to [72, 73].
        directory (str, optional): _description_. Defaults to 'xxx/lobster'.
    """

    if not os.path.exists(os.path.join(directory, 'COHPCAR.lobster')) or recalc:
      self.write_labels(atoms=atoms, dname=directory,
                        atoms_index_list=atoms_index_list)
      self.write_lobsterin(dname=directory)
      self.run_lobster(dname=directory)
    else:
      print(f'{directory}->lobster 计算完成!')
    return None

  def plot(self,
           dbname=None,
           directory_relax=None,
           xlim=[-20, 20],
           ylim=[-12, 10],
           xlim_icohp=None,
           legend_loc='best',
           is_icohp=True,
           line_label_list=None,
           dname='lobster'):
    from vasp_learn import dataBase
    directory_relax, dbname = dataBase.DataBase().choice_directory_dname(
        directory=directory_relax,
        dbname=dbname)
    directory = os.path.join(directory_relax, dname)

    fname_list = []
    # ---
    data_cohp, labels_cohp, icohp_ef = self.get_data(dname=directory)
    if line_label_list is None:
      line_label_list = labels_cohp
    for i in range(len(labels_cohp)):  # range(int((len(data_cohp[0])-3)/2)):
      fig = plt.figure(figsize=[2.4, 4.8])
      ax = fig.add_subplot()
      ax.plot(-data_cohp[:, i*2+3], data_cohp[:, 0],
              color='k', label=line_label_list[i])
      ax.legend(loc=legend_loc)
      ax.fill_betweenx(data_cohp[:, 0],
                       -data_cohp[:, i*2+3], 0,
                       where=-data_cohp[:, i*2+3] >= 0,
                       facecolor='green', alpha=0.5)
      ax.fill_betweenx(data_cohp[:, 0],
                       -data_cohp[:, i*2+3], 0,
                       where=-data_cohp[:, i*2+3] <= 0,
                       facecolor='red', alpha=0.5)
      ax.set_xlim(xlim)
      ax.set_ylim(ylim)
      ax.set_xlabel('-COHP (eV)', color='k', fontsize='large')
      ax.set_ylabel('$E-E_F$ (eV)', fontsize='large')
      ax.tick_params(axis='x', colors="k")
      # markers
      ax.axvline(0, color='k', linestyle=':', alpha=0.5)
      ax.axhline(0, color='k', linestyle='--', alpha=0.5)

      # 使用 ax.annotate 添加文本到右上角
      xlim = ax.get_xlim()
      ylim = ax.get_ylim()
      ax.annotate(text=f'-ICOHP:',
                  xy=(xlim[1], ylim[1]),  # 右上角坐标
                  xytext=(-10, -40),      # 向左下方偏移10个单位
                  textcoords='offset points',  # 使用偏移量作为坐标系统 单位是点数（points），1 个点等于 1/72 英寸（约 0.353 毫米）。
                  ha='right',             # 水平右对齐
                  va='bottom',               # 垂直顶部对齐
                  color='gray',)
      ax.annotate(text=f'{-icohp_ef[i]:.3f}',
                  xy=(xlim[1], ylim[1]),  # 右上角坐标
                  xytext=(-10, -40),      # 向左下方偏移10个单位
                  textcoords='offset points',  # 使用偏移量作为坐标系统 单位是点数（points），1 个点等于 1/72 英寸（约 0.353 毫米）。
                  ha='right',             # 水平右对齐
                  va='top',               # 垂直顶部对齐
                  color='gray',)

      if is_icohp:  # 画图 ICOHP
        ax2 = ax.twiny()
        ax2.plot(-data_cohp[:, i*2+4], data_cohp[:, 0], color='grey')
        ax2.set_ylim(ylim)
        ax2.set_xlim(xlim_icohp)
        ax2.set_xlabel('-ICOHP (eV)', color='grey', fontsize='large')
        ax2.xaxis.tick_top()
        ax2.xaxis.set_label_position('top')
        ax2.tick_params(axis='x', colors="grey")
        # ax2.annotate(labels_cohp[i], xy=(1.45, 5.5), ha='right', va='top',
        #  bbox=dict(boxstyle='round', fc='w', alpha=0.5))
        # ax2.annotate(f'{-icohp_ef[i]:.3f}', xy=(1.45, -0.05),
        #          ha='right', va='top', color='grey')

      fname = os.path.join(directory, f'cohp_{i+1}.pdf')
      self.MatplotlibFeatures.savefig(fig=fig,
                                      fname=fname)
      fname_list.append(fname)
      plt.close()

    return fname_list

  def wrapper_lobster_part1_run_vasp(self,
                                     dbname=None,
                                     directory_relax=None,
                                     only_write_inputs=True,
                                     incar_pars_dict={},
                                     directory_lobster=None,
                                     dname='lobster',
                                     ):
    """ * 步骤
    - 1. 先only_write_inputs=True 获得 lobster目录的 VASP 计算输入
    - 2. 上传的到服务器进行vasp 计算
    ---
    """
    # 获取 wavecar
    from vasp_learn import dataBase
    directory_relax, dbname = dataBase.DataBase().choice_directory_dname(
        directory=directory_relax,
        dbname=dbname)
    calc = ase.calculators.vasp.Vasp(directory=directory_relax, restart=True)
    kpts = calc.kpts
    nbands = int(calc.nbands * 1.6)
    if directory_lobster is None:
      directory_lobster = os.path.join(directory_relax, dname)
    atoms = ase.io.read(os.path.join(directory_relax, 'OUTCAR'))

    self.get_wavecar(atoms=atoms,
                     directory=directory_lobster,
                     nbands=nbands,
                     kpts=kpts,
                     only_write_inputs=only_write_inputs,
                     **incar_pars_dict)

    # 上传到服务器
    from sci_scripts import rsync_hfeshell_合肥超算
    rsync_hfeshell_合肥超算.ssh_Rsync().rsync(
        local_dir_list=[directory_lobster],
        upload=True,
        rsync_pars='',
    )

    return None

  def wrapper_lobster_part2_run_lobster(self,
                                        dbname=None,
                                        atom_index_list=[[72, 71], [72, 70]],
                                        recalc=False,
                                        directory_lobster=None,
                                        dname='lobster',
                                        xlim=[-20, 20],
                                        ylim=[-12, 10],
                                        line_label_list=None,
                                        ):
    """ # 服务器上算好后, 下载WAVECAR, 计算 lobster 和 分析 
    * 步骤
    - 1. 先only_write_inputs=True 获得 lobster目录的 VASP 计算输入
    - 2. 上传的到服务器进行vasp 计算
    - 3. 下载 WAVECAR 
    - 4. only_write_inputs=False 进行 lobster 计算
    - 5. plot 绘图
    ---
    使用 lobsterpyLearn 分析也是可以的 
    ll = mypaper_SiP_codope.CalculationsVasp.DealData.lobsterpyLearn.LobsterpyLearn()
    ana = ll.get_analyse(
        directory='/Users/wangjinlong/my_server/my/myORR_B/slab/SiTe_codope/Si_Te_2V_Gra/lobster',
        surfix='')
    des = ll.get_describe(ana)
    ll.get_static_plots(des)

    ---
    * 单点计算获取wavecar 并且执行lobster 数据分析
    * 改变原子索引后需要 recalc=True

    注意! 这里的atoms 要从目录中的 POSCAR或者CONTCAR读取
    atoms = ase.io.read(filename=os.path.join(directory, 'CONTCAR'))
    不能这样读取: row = ob.db_all.get('name=O_B_N0graphene') atoms = row.toatoms() calc.atoms 也不行
    """

    from vasp_learn import dataBase
    directory_relax = dataBase.DataBase().get_directory(dbname=dbname)
    calc = ase.calculators.vasp.Vasp(directory=directory_relax, restart=True)
    atoms = calc.atoms

    if directory_lobster is None:
      directory_lobster = os.path.join(directory_relax, dname)
    # 下载WAVECAR
    fwavecar = os.path.join(directory_lobster, 'WAVECAR')
    if os.path.exists(fwavecar) and (os.path.getsize(fwavecar) > 0):
      pass
    else:
      from sci_scripts import rsync_hfeshell_合肥超算
      rsync_hfeshell_合肥超算.ssh_Rsync().rsync(
          exclude_key_list=[],
          local_dir_list=[directory_lobster],
          download=True,
          rsync_pars='',
      )

    # 计算lobster
    self.calc_lobster(atoms=atoms,
                      atoms_index_list=atom_index_list,
                      directory=directory_lobster,
                      recalc=recalc)
    # 画图
    fname_list = self.plot(dbname=dbname,
                           directory_relax=None,
                           xlim=xlim,
                           ylim=ylim,
                           line_label_list=line_label_list,
                           dname=dname)
    return fname_list
