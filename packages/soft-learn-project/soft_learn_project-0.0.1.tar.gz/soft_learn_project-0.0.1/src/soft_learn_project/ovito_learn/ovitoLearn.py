
import ovito.data
import ovito.pipeline
import ovito.pipeline
from ovito.data import DataCollection
from ovito.traits import Color
from traits.api import Range
import ovito.modifiers
import ovito.vis
import ovito.io
import numpy as np
import ovito.io.ase
import ovito.io.lammps
import os


class OvitoLearn():
  def __init__(self) -> None:
    """https://docs.ovito.org/python/introduction/installation.html#using-pip
    这是学习网址 有空学学

    这里主要是学习ovito python 模块
    对于ovito 的可视化软件 通过 brew install ovito 可以很容易升级安装
    """
    pass

  def string_install(self):
    string = """ 官网: https://www.ovito.org/#download
    1. ovito 软件的安装: 
    直接从官网下载然后安装.
    或者, 通过 brew install ovito 可以很容易升级安装, 当然也可以通过conda 环境安装 # for mac 
    或者, sudo apt install ovito # for ubuntu 
    conda install -c conda-forge ovito=3.10.6  # 不是 vovito 的python包 

    2. ovito python 模块的安装
    # 这样安装能用vovito 包, 但不能用ovito 软件
    conda install --strict-channel-priority -c https://conda.ovito.org -c conda-forge ovito=3.10.6
    """
    print(string)
    return None

  def ex_modify_global(frame: int, data: DataCollection):
    data.attributes["TotalEnergy"] = np.sum(data.particles["Energy"])

  def ex_modify_peratoms(frame: int, data: DataCollection):
    momenta = data.particles.velocities * data.particles.masses[:, np.newaxis]
    data.particles_.create_property(
        'Momentum', data=momenta, components=['X', 'Y', 'Z'])

  def ex2(self):
    # Create the data collection containing a Particles object:
    data = ovito.data.DataCollection()
    particles = data.create_particles()

    # XYZ coordinates of the three atoms to create:
    pos = [(1.0, 1.5, 0.3),
           (7.0, 4.2, 6.0),
           (5.0, 9.2, 8.0)]

    # Create the particle position property:
    pos_prop = particles.create_property('Position', data=pos)
    # Create the particle type property and insert two atom types:
    type_prop = particles.create_property('Particle Type')
    type_prop.types.append(ovito.data.ParticleType(
        id=1, name='Cu', color=(0.0, 1.0, 0.0)))
    type_prop.types.append(ovito.data.ParticleType(
        id=2, name='Ni', color=(0.0, 0.5, 1.0)))
    type_prop[0] = 1  # First atom is Cu
    type_prop[1] = 2  # Second atom is Ni
    type_prop[2] = 2  # Third atom is Ni

    # Create a user-defined particle property with some data:
    my_data = [3.141, -1.2, 0.23]
    my_prop = particles.create_property('My property', data=my_data)
    # Create the simulation box:
    cell = ovito.data.SimulationCell(pbc=(False, False, False))
    cell[...] = [[10, 0, 0, 0],
                 [0, 10, 0, 0],
                 [0, 0, 10, 0]]
    cell.vis.line_width = 0.1
    data.objects.append(cell)

    # Create 3 bonds between particles:
    bond_topology = [[0, 1], [1, 2], [2, 0]]
    bonds = particles.create_bonds()
    bonds.create_property('Topology', data=bond_topology)

    # Create a pipeline, set the source and insert it into the scene:
    pipeline = ovito.pipeline.Pipeline(
        source=ovito.pipeline.StaticSource(data=data))

    self.add_pipline_to_scene(pipeline)
    vp = self.view()
    return vp

  def ex_add_scale_bar_ex(self):
    """https://docs.ovito.org/python/introduction/examples/overlays/scale_bar.html
    https://docs.ovito.org/python/introduction/examples/overlays/data_plot.html
    """
    from ovito.qt_compat import QtCore, QtGui
    from ovito.vis import ViewportOverlayInterface

    class ScaleBarOverlay(ViewportOverlayInterface):

      # Adjustable user parameters:

      # World-space length of the scale bar:
      length = Range(value=4.0, low=0.0, label='Length (nm)')

      # Screen-space height of the scale bar:
      height = Range(value=0.05, low=0.0, high=0.2, label='Height')

      # Bar color:
      bar_color = Color(default=(0.0, 0.0, 0.0), label='Bar color')

      # Text color:
      text_color = Color(default=(1.0, 1.0, 1.0), label='Text color')

      def render(self, canvas: ViewportOverlayInterface.Canvas, data: DataCollection, **kwargs):

        # Compute the center coordinates of the simulation cell.
        center = data.cell @ (0.5, 0.5, 0.5, 1.0)

        # Compute length of bar in screen space - as a fraction of the canvas height.
        screen_length = canvas.project_length(center, self.length)

        # Convert from nanometers to simulation units of length (Angstroms) and
        # convert from vertical to horizontal canvas coordinates by multiplying with the h/w aspect ratio.
        screen_length *= 10 * canvas.logical_size[1] / canvas.logical_size[0]

        # Create a 1-by-1 pixel image for drawing the bar rectangle.
        image = QtGui.QImage(1, 1, canvas.preferred_qimage_format)
        image.fill(QtGui.QColor.fromRgbF(*self.bar_color))

        # Draw the bar rectangle.
        canvas.draw_image(image, pos=(0.01, 0.01), size=(
            screen_length, self.height), anchor="south west")

        # Draw the text label.
        canvas.draw_text(f"{self.length:.3} nm",
                         pos=(0.01 + 0.5*screen_length,
                              0.01 + 0.5*self.height),
                         font_size=self.height,
                         anchor="center",
                         color=self.text_color)

  def ex_Highlight_a_particle(self):
    """https://docs.ovito.org/python/introduction/examples/overlays/highlight_particle.html
    """
    from ovito.vis import ViewportOverlayInterface
    from ovito.qt_compat import QtCore, QtGui

    class HighlightParticleOverlay(ViewportOverlayInterface):

        # Adjustable user parameter that selects which particle to highlight:
      particle_index = Range(value=0, low=0, label='Particle index')

      def render(self, canvas: ViewportOverlayInterface.Canvas, data: DataCollection, **kwargs):

        # Determine world-space radius of the particle.
        radius = 0.0
        if 'Radius' in data.particles:
          radius = data.particles['Radius'][self.particle_index]
        if radius <= 0 and data.particles.particle_types is not None:
          particle_type = data.particles.particle_types[self.particle_index]
          radius = data.particles.particle_types.type_by_id(
              particle_type).radius
        if radius <= 0:
          radius = data.particles.vis.radius

        # Project center of the particle to screen space.
        positions = data.particles.positions
        xy = canvas.project_location(positions[self.particle_index])
        if xy is None:
          return

        # Calculate screen-space size of the particle as a fraction of the canvas height.
        screen_radius = canvas.project_length(
            positions[self.particle_index], radius)

        # Convert everything to logical pixel coordinates used by the QPainter.
        x = xy[0] * canvas.logical_size[0]
        y = (1 - xy[1]) * canvas.logical_size[1]
        screen_radius *= canvas.logical_size[1]

        # Start drawing using a QPainter.
        with canvas.qt_painter() as painter:
          # Draw a dashed circle around the particle.
          pen = QtGui.QPen(QtCore.Qt.DashLine)
          pen.setWidth(3)
          pen.setColor(QtGui.QColor(0, 0, 255))
          painter.setPen(pen)
          painter.drawEllipse(QtCore.QPointF(
              x, y), screen_radius, screen_radius)

          # Draw an arrow pointing at the particle.
          arrow_shape = QtGui.QPolygonF()
          arrow_shape.append(QtCore.QPointF(0, 0))
          arrow_shape.append(QtCore.QPointF(10, 10))
          arrow_shape.append(QtCore.QPointF(10, 5))
          arrow_shape.append(QtCore.QPointF(40, 5))
          arrow_shape.append(QtCore.QPointF(40, -5))
          arrow_shape.append(QtCore.QPointF(10, -5))
          arrow_shape.append(QtCore.QPointF(10, -10))
          painter.setPen(QtGui.QPen())
          painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
          painter.translate(QtCore.QPointF(x, y))
          painter.rotate(-45.0)
          painter.translate(QtCore.QPointF(screen_radius, 0))
          painter.scale(2, 2)
          painter.drawPolygon(arrow_shape)
    pass


class Features():
  def __init__(self, ) -> None:
    """https://docs.ovito.org/python/introduction/introduction.html
    这是学习网址 暂时学到够用就行
    以后可能需要学习: ovito.modifiers.ClusterAnalysisModifier file:///Applications/Ovito.app/Contents/Resources/doc/manual/html/python/modules/ovito_modifiers.html#ovito.modifiers.CombineDatasetsModifier
    """
    self.OvitoLearn = OvitoLearn()
    pass

  def get_atoms_ovito2ase(self, fname='input/simulation.dump'):
    # Create an OVITO data pipeline from an external file:
    pipeline = ovito.io.import_file(fname)
    # Evaluate pipeline to obtain a DataCollection:
    data = pipeline.compute()
    # Convert it to an ASE Atoms object:
    ase_atoms = ovito.io.ase.ovito_to_ase(data)
    return ase_atoms

  def get_pipeline(self, atoms=None,
                   dbname=None,
                   fname=None):
    """fname='/Users/wangjinlong/my_server/my/myORR_B/adsorbate_slab/Nn_graphene/N3_graphene/O_N3_graphene/O_N3_graphene.xyz'
    atoms|dbname|fname: 三者给一个

    Args:
        atoms (_type_, optional): _description_. Defaults to None.
        dbname (str, optional): _description_. Defaults to 'N3_graphene'.
        fname (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    if fname is not None:  # 通过xyz文件获取 pipeline
      pipeline = ovito.io.import_file(fname)
      return pipeline
    elif dbname is not None:  # 通过 dbname 获取
      from vasp_learn import dataBase
      atoms = dataBase.DataBase().get_atoms_list(dbname=dbname)[-1]
    elif atoms is not None:  # 通过 atoms 获取
      pass
    else:
      print('请给定atoms 或者 dbname!')
    data = ovito.io.ase.ase_to_ovito(atoms=atoms)
    pipeline = ovito.pipeline.Pipeline(
        source=ovito.pipeline.StaticSource(data=data))
    return pipeline

  def clean_scene(self,):
    """确保只添加当前的pipline 到 scence 中

    Args:
        pipeline (_type_): _description_
    """
    for existing_pipeline in list(ovito.scene.pipelines):
      existing_pipeline.remove_from_scene()

      # Add the desired pipeline to the scene
      # pipeline.add_to_scene()

  def get_vp(self,
             camera_dir=(-0.01, 2, -1),
             ):
    """获得 Viewport 对象, 设置相机的方向

    Args:
        camera_dir (tuple, optional): _description_. Defaults to (-0.01, 2, -1).

    Returns:
        _type_: _description_
    """
    vp = ovito.vis.Viewport()
    vp.type = ovito.vis.Viewport.Type.Ortho
    # vp.camera_pos = (-100, -150, 150)
    vp.camera_dir = camera_dir
    # vp.fov = math.radians(60.0) #?
    vp.zoom_all()

    return vp

  def render_image(slef, vp: ovito.vis.Viewport,
                   size=(1000, 800),
                   render='TR',
                   fname='output.jpg',):
    """渲染图片

    Args:
        slef (_type_): _description_
        vp (ovito.vis.Viewport): _description_
        size (tuple, optional): _description_. Defaults to (1000, 800).
        save (bool, optional): _description_. Defaults to False.
        render (str, optional): _description_. Defaults to 'TR'.
        fname (str, optional): _description_. Defaults to 'output.jpg'.

    Returns:
        _type_: _description_
    """

    if render == 'TR':
      renderer = ovito.vis.TachyonRenderer()
    elif render == 'OSPRay':
      renderer = ovito.vis.OSPRayRenderer()

    vp.render_image(size=size, renderer=renderer, filename=fname,
                    background=(1, 1, 1), )
    print(f'图片保存 -> {os.path.abspath(fname)}')
    return vp

  def vis_particle(self, pipeline: ovito.pipeline.Pipeline,
                   scaling=0.5, radius=1.2):
    """这种方法比 modifier_particle_property 更容易

    Args:
        pipeline (ovito.pipeline.Pipeline): _description_
        scaling (int, optional): _description_. Defaults to 1.
        radius (float, optional): _description_. Defaults to 1.2.
    """
    vis_element = pipeline.compute().particles.vis
    vis_element.shape = ovito.vis.ParticlesVis.Shape.Sphere
    vis_element.scaling = 1
    vis_element.radius = radius

  def modifier_particle_property(self, uniform_radius=0.5,
                                 radius_scale=None):
    # tobe delete
    class ParticlePropertyModifier():
      def __init__(self, uniform_radius, radius_scale) -> None:
        self.uniform_radius = uniform_radius
        self.radius_scale = radius_scale

      def modifier(self, frame, data: ovito.data.DataCollection,):
        """
        下面可以设置 半径的尺度因子, 但设置具体的值不管用
        pipeline.compute().particles.vis.scaling = 0.5  # 效果不好, 原子之间的差异有点大 
        # 下面这种方式只能用于modifier 并应用在管道上 才管用
        data = pipeline.compute()
        data.particles_.particle_types_.type_by_id_(1).name = "Cu"
        data.particles_.particle_types_.type_by_id_(1).radius = 0.5
        data.particles_.particle_types_.type_by_id_(id=3).radius = 0.3
        data.particles_.particle_types_.types_[2].color = (1,0,0)
        """

        num_types = data.particles_.particle_types_.types_.__len__()  # 本身是个列表
        for n in range(1, num_types+1):
          if self.radius_scale:
            data.particles_.particle_types_.type_by_id_(
                n).radius *= self.radius_scale
          elif self.uniform_radius:
            data.particles_.particle_types_.type_by_id_(
                n).radius = self.uniform_radius

    modifier = ParticlePropertyModifier(
        uniform_radius=uniform_radius, radius_scale=radius_scale).modifier
    return modifier

  def get_particle_radius_dict_default(self):
    from py_package_learn.ase_learn import aseLearn
    import ase.data
    particle_radius_dict_default = {chemical_symbol: aseLearn.Base().get_atomic_covalent_radii(
        atomic_symbel=chemical_symbol) for chemical_symbol in ase.data.chemical_symbols}
    return particle_radius_dict_default

  def my_modifier_AssignParticleRadius(
          self,
          particle_radius_dict={'C': 0.2, 'N': 0.1}):
    class AssignParticleRadius(ovito.pipeline.ModifierInterface):
      def __init__(self, particle_radius_dict={'C': 0.2, 'N': 0.1}) -> None:
        super().__init__()
        self.particle_radius_dict = particle_radius_dict

      def modify(self, data, **kwargs):
        for particle_type in data.particles_.particle_types_.types_:
          # particle_type.radius = self.particle_radius_dict[particle_type.name]
          particle_type.radius = self.particle_radius_dict.get(
              particle_type.name, 0.5)  # 默认值为 0.1

    # 我自己设置的默认半径
    particle_radius_dict_default = self.get_particle_radius_dict_default()
    particle_radius_dict_default.update(particle_radius_dict)
    particle_radius_dict = particle_radius_dict_default
    # ---
    modifier = AssignParticleRadius(particle_radius_dict=particle_radius_dict)
    return modifier

  def deal_bond_pairwise_dict_for_my_modifier_create_bonds(self,
                                                           bond_pairwise_dict: dict = {'O-O': 2.5, 'O-H': 1.5}):
    """将 {'O-O': 2.5, 'O-H': 1.5} 的形式变成 
    type_a_list = ['O','O']
    type_a_list = ['O','H']
    cutoff_pairwise_list = [2.5 1,5] 
    的形式, 用于 my_modifier_create_bonds 的使用

    Args:
        bond_pairwise_dict (dict, optional): _description_. Defaults to {'O-O': 2.5, 'O-H': 1.5}.

    Returns:
        _type_: _description_
    """

    # 我的默认设置
    bond_pairwise_dict_default = {'O-O': 2.5, 'O-H': 1.5,
                                  'C-C': 2, 'Br-C': 2.2,
                                  'Cl-C': 2.2, 'F-C': 2.2,
                                  'Br-O': 2.3, 'C-O': 2, }
    bond_pairwise_dict_default.update(bond_pairwise_dict)
    bond_pairwise_dict = bond_pairwise_dict_default
    # --
    type_a_list = []
    type_b_list = []
    cutoff_pairwise_list = []
    for bond_pair in list(bond_pairwise_dict.keys()):
      type_ab = bond_pair.split('-')
      type_a_list.append(type_ab[0])
      type_b_list.append(type_ab[1])
      cutoff_pairwise_list.append(bond_pairwise_dict.get(bond_pair))

    return zip(type_a_list, type_b_list, cutoff_pairwise_list)

  def my_modifier_create_bonds(self,
                               cutoff_bond=2.2,
                               bond_width=0.2,
                               bond_mode='Uniform|pairwise',
                               bond_pairwise_dict={'O-O': 2.5, 'O-H': 1.5,
                                                   'C-C': 2, 'Br-C': 2.2,
                                                   'Cl-C': 2.2, 'F-C': 2.2,
                                                   'C-O': 2, },):

    modifier = ovito.modifiers.CreateBondsModifier(enabled=True,
                                                   cutoff=cutoff_bond,)
    if bond_mode.lower() == 'uniform':
      modifier.mode = ovito.modifiers.CreateBondsModifier.Mode.Uniform
    elif bond_mode.lower() == 'pairwise':
      modifier.mode = ovito.modifiers.CreateBondsModifier.Mode.Pairwise
      for type_a, type_b, cutoff_pairwise in self.deal_bond_pairwise_dict_for_my_modifier_create_bonds(bond_pairwise_dict=bond_pairwise_dict):
        modifier.set_pairwise_cutoff(type_a=type_a, type_b=type_b,
                                     cutoff=cutoff_pairwise)
    modifier.vis.width = bond_width
    return modifier

  def modifier_color_coding(self, property='initial_magmoms',
                            color_graident='Jet|Hot|BlueWhiteRed',
                            start_value=None,
                            end_value=None,
                            ):
    """根据属性指定颜色, 属性名可以看 O_N3_graphene.xyz 中的列名 

    Args:
        property (str, optional): _description_. Defaults to 'initial_magmoms'.
        color_graident (str, optional): _description_. Defaults to 'BlueWhiteRed'.

    Returns:
        _type_: _description_
    """

    if color_graident == 'Jet':
      color_graident = ovito.modifiers.ColorCodingModifier.Jet()
    elif color_graident == 'Hot':
      color_graident = ovito.modifiers.ColorCodingModifier.Hot()
    else:
      color_graident = ovito.modifiers.ColorCodingModifier.BlueWhiteRed()

    modifier = ovito.modifiers.ColorCodingModifier(
        property=property,
        gradient=color_graident,
    )

    if start_value is None or end_value is None:
      modifier.auto_adjust_range = True
    else:
      modifier.start_value = start_value
      modifier.end_value = end_value

    return modifier

  def modifier_assign_color_wrapper(self, color=(0.2, 0.5, 1.0)):
    # Define our custom modifier class, which assigns a uniform color
    # to all particles, similar to the built-in AssignColorModifier.
    class AssignColor(ovito.pipeline.ModifierInterface):
      def __init__(self) -> None:
        super().__init__()
        self.color = color

      def modify(self, data, **kwargs):
        color_property = data.particles_.create_property('Color')
        color_property[:] = self.color

    modifier = AssignColor()
    # Insert the user-defined modifier into the data pipeline.
    'pipeline.modifiers.append(modifier)'
    return modifier

  def modifier_forece_vector(frame, data: ovito.data.DataCollection):
    """显示原子受力的箭头

    Args:
        frame (_type_): _description_
        data (ovito.data.DataCollection): _description_
    """
    vector_vis: ovito.vis.VectorVis = data.particles_.forces.vis
    vector_vis.enabled = True  # This activates the display of arrow glyphs
    vector_vis.color = (1, 0, 0)
    vector_vis.scaling = 20
    vector_vis.width = 0.03

  def modifier_calculate_displacements(self):
    """显示原子位移的箭头
    """
    modifier = ovito.modifiers.CalculateDisplacementsModifier()
    modifier.vis.enabled = True  # This activates the display of displacement vectors
    modifier.vis.flat_shading = False
    return modifier

  def modifier_own_arrow(self, frame, data: ovito.data.DataCollection, vector_vis=ovito.vis.VectorVis(alignment=ovito.vis.VectorVis.Alignment.Center, color=(1.0, 0.0, 0.4))):
    """自定义一个矢量属性箭头

    Args:
        frame (_type_): _description_
        data (ovito.data.DataCollection): _description_
        vector_vis (_type_, optional): _description_. Defaults to ovito.vis.VectorVis(alignment=ovito.vis.VectorVis.Alignment.Center, color=(1.0, 0.0, 0.4)).
    """
    # Add a new vector property to the particles:
    vector_data = np.random.random_sample(size=(data.particles.count, 3))
    property = data.particles_.create_property(
        'My Vector Property', data=vector_data)

    # Attach the visual element to the output property:
    property.vis = vector_vis

  def overlay_coordinate_tripod(self, size=0.1):
    """所有的overlay 用的时候是 vp.overlays.append(overlay)
    """
    from ovito.qt_compat import QtCore
    # Create the overlay.
    tripod = ovito.vis.CoordinateTripodOverlay()
    tripod.size = size
    tripod.alignment = QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignBottom
    return tripod

  def overlay_color_legend(self, modifier,
                           legend_size=0.3,
                           label_size=0.8,
                           title='atomic chagres',
                           font_size=0.1,
                           offset_x=0,
                           offset_y=0,
                           format_string='%.2f eV',):
    """所有的overlay 用的时候是 vp.overlays.append(overlay)
    需要配合 modifier_color_coding 来使用
    modifier = self.modifier_color_coding()
    创建颜色图例叠加层并配置其属性

    left = QtCore.Qt.AlignmentFlag.AlignLeft
    bottom = QtCore.Qt.AlignmentFlag.AlignBottom
    right = QtCore.Qt.AlignmentFlag.AlignRight
    top = QtCore.Qt.AlignmentFlag.AlignTop

    Args:
        modifier (_type_): _description_
        legend_size (float, optional): _description_. Defaults to 0.3.
        label_size (float, optional): _description_. Defaults to 0.6.
        title (str, optional): _description_. Defaults to 'ok'.
        font_size (float, optional): _description_. Defaults to 0.1.
        offset_x (int, optional): _description_. Defaults to 0.
        offset_y (int, optional): _description_. Defaults to 0.
        format_string (str, optional): _description_. Defaults to '%.2f eV'.

    Returns:
        _type_: _description_
    """

    from ovito.qt_compat import QtCore
    color_legend = ovito.vis.ColorLegendOverlay()
    color_legend.modifier = modifier
    color_legend.alignment = QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignBottom
    color_legend.orientation = QtCore.Qt.Orientation.Horizontal
    color_legend.legend_size = legend_size
    color_legend.offset_x = offset_x
    color_legend.offset_y = offset_y
    color_legend.title = title
    color_legend.font_size = font_size
    color_legend.label_size = label_size
    color_legend.format_string = format_string
    return color_legend

  def overlay_text_label(self, text="text",
                         font_size=0.2,
                         offset_x=0,
                         offset_y=0,
                         text_color=(1, 0, 0)):
    """用的时候 在vp.render_image 之前 vp.overlays.append(overlay)
    """
    overlay = ovito.vis.TextLabelOverlay(text=text,
                                         font_size=font_size,
                                         offset_x=offset_x,
                                         offset_y=offset_y,
                                         text_color=text_color,)
    # 动态计算某些属性的时候需要开启以下
    # Specify the source of dynamically computed attributes.
    # overlay.pipeline = pipeline
    return overlay

  def overlay_PythonViewportOverlay(self, text='C',
                                    pos=(0.5, 0.5),
                                    font_size=0.03,
                                    color=(1, 0, 0)):
    class MyOverlay(ovito.vis.ViewportOverlayInterface):
      def render(self, canvas: ovito.vis.ViewportOverlayInterface.Canvas, **kwargs):
        # 这是canvas 的中心, 原子的坐标位置还是很难确定
        canvas.draw_text(text=text, pos=pos,
                         font_size=font_size,
                         color=color,)
    overlay = ovito.vis.PythonViewportOverlay(delegate=MyOverlay())
    return overlay

  def cell_vis(self,
               data: ovito.data.DataCollection,
               line_width=1,
               rendering_color=(0.0, 0.0, 0.8),
               ):

    # cell_vis = pipeline.source.data.cell.vis
    cell_vis = data.cell.vis
    cell_vis.line_width = line_width
    cell_vis.rendering_color = rendering_color

  def get_bond_pairwise_dict(self, atoms):
    import itertools
    from vasp_learn import base
    elements = list(set(atoms.get_chemical_symbols()))
    # 使用 itertools.combinations 生成所有两个元素的组合
    combinations = itertools.combinations(elements, 2)
    # 添加同元素对
    combinations = list(combinations) + \
        [(element, element) for element in elements]
    bond_pairwise_dict = {}
    for a, b in combinations:
      r_a = base.Base().get_atomic_covalent_radii(atomic_symbel=a)
      r_b = base.Base().get_atomic_covalent_radii(atomic_symbel=b)
      bond = (r_a+r_b)*1.25
      bond_pairwise_dict.update({f'{a}-{b}': bond})
    return bond_pairwise_dict

  def atoms_structure(self,
                      atoms=None,
                      directory=None,
                      dbname=None,
                      rotate=False,
                      rotate_dict={'a': 180, 'v': 'x'},
                      particle_radius_dict={'H': 0.2,
                                            'C': 0.5,
                                            'N': 0.5,
                                            'Br': 0.5,
                                            'O': 0.4,
                                            'Cl': 0.5,
                                            'P': 0.5,
                                            'Si': 0.5},
                      cutoff_bond=2,
                      bond_width=0.2,
                      bond_mode='pairwise',
                      bond_pairwise_dict=None,
                      cell_line_width=0.03,
                      cell_line_rendering_color=(0, 0, 0),
                      camera_dir=(-0.01, 2, -1),
                      text2overlay_dict_list=[],
                      text_font_size=0.03,
                      text_color=(0, 0, 0),
                      fname_format='jpg',
                      fname_out=None,
                      fname_surfix='',
                      ):
    r"""提供 directory | dbname | atoms, dbname, directory
    使用 dbname 读取速度较慢 这需要从数据库检索, 数据库越大检索越慢
    ---
    - cutoff_mode='None|pairwise'
    - bond_pairwise_dict="None|{'O-O': 2.5, 'O-H': 1.5,'C-C': 2, 'Br-C': 2.2, 'Cl-C': 2.2, 'F-C': 2.2,'C-O': 2, }"
    - text2overlay_dict_list=[{'text': 'O', 'pos': (0.49, 0.51)},
                                                {'text': 'N', 'pos': (
                                                    0.49, 0.44)},
                                                {'text': 'N', 'pos': (
                                                    0.44, 0.55)},
                                                {'text': 'N', 'pos': (0.54, 0.55)},],
    """

    from vasp_learn import dataBase
    import ase.io
    # 获得原子对象
    if atoms and dbname and directory:
      # print('还需要提供 dbname 和 directory ')
      pass
    elif directory:
      dbname = os.path.basename(os.path.abspath(directory))
      atoms = ase.io.read(os.path.join(directory, 'OUTCAR'))
    elif dbname:
      atoms = dataBase.DataBase().db.get_atoms(name=dbname)
      directory = dataBase.DataBase().get_directory(dbname=dbname)
    else:
      print(f'参数不足, dbname: {dbname}, atoms: {atoms}, directory: {directory}')
      return

    if fname_out is None:
      new_name = dbname+str(fname_surfix) + f'.{fname_format}'
      fname_out = os.path.join(directory, new_name)

    if os.path.exists(fname_out):
      # print(f'文件存在-> {fname_out}')
      return fname_out
    # 旋转原子
    if rotate:
      atoms.rotate(a=rotate_dict['a'],
                   v=rotate_dict['v'], rotate_cell=True)
    # 设置 原子大小和成键
    pipeline = self.get_pipeline(atoms=atoms, dbname=None, fname=None)
    m1 = self.my_modifier_AssignParticleRadius(
        particle_radius_dict=particle_radius_dict)
    bond_pairwise_dict = self.get_bond_pairwise_dict(
        atoms=atoms) if bond_pairwise_dict is None else bond_pairwise_dict
    m2 = self.my_modifier_create_bonds(cutoff_bond=cutoff_bond,
                                       bond_width=bond_width,
                                       bond_mode=bond_mode,
                                       bond_pairwise_dict=bond_pairwise_dict,
                                       )
    pipeline.modifiers.extend([m1, m2,])

    # 加入场景
    self.clean_scene()
    pipeline.add_to_scene()
    vp = self.get_vp(camera_dir=camera_dir)

    # cell
    self.cell_vis(data=pipeline.compute(),
                  line_width=cell_line_width,
                  rendering_color=cell_line_rendering_color)

    # 加入坐标轴图层
    overlay_tripod = self.overlay_coordinate_tripod(size=0.1)
    vp.overlays.append(overlay_tripod)

    # 加入文本图层overlay_text
    if text2overlay_dict_list:
      overlay_text_list = []
      for text_dict in text2overlay_dict_list:
        text = text_dict['text']
        pos = text_dict['pos']
        overlay_text = self.overlay_PythonViewportOverlay(text=text,
                                                          pos=pos,
                                                          font_size=text_font_size,
                                                          color=text_color)
        overlay_text_list.append(overlay_text)
      vp.overlays.extend(overlay_text_list)

    # 保存图片
    self.render_image(vp=vp, fname=fname_out,
                      size=(1000, 800))
    return fname_out

  def wrapper_atoms_structure(self,
                              directory=None,
                              dbname=None,
                              particle_radius_dict={'H': 0.2,
                                                    'C': 0.5,
                                                    'N': 0.5,
                                                    'Br': 0.5,
                                                    'O': 0.4,
                                                    'Cl': 0.5,
                                                    'P': 0.5,
                                                    'Si': 0.5},
                              ):
    """直接画出斜视图, 顶视图和侧视图"""
    fname_out_list = []
    camera_dir_list = [(-0.01, 2, -1), (0, 0, -1), (0, 1, 0)]
    fname_surfix_list = ['_oblique_view', '_top_view', '_side_view']
    for camera_dir, fname_surfix in zip(camera_dir_list,
                                        fname_surfix_list):
      fname_out = self.atoms_structure(
          directory=directory,
          dbname=dbname,
          camera_dir=camera_dir,
          fname_surfix=fname_surfix,
          particle_radius_dict=particle_radius_dict,
      )
      fname_out_list.append(fname_out)
    return fname_out_list

  def property_distribution(self,
                            atoms,
                            particle_radius_dict={'H': 0.2,
                                                  'C': 0.5,
                                                  'Br': 0.7,
                                                  'O': 0.4,
                                                  'Cl': 0.5,
                                                  'N': 0.5},
                            cutoff_bond=2,
                            bond_width=0.2,
                            bond_mode='uniform|pairwise',
                            bond_pairwise_dict="None|{'O-O': 2.5, 'O-H': 1.5,'C-C': 2, 'Br-C': 2.2, 'Cl-C': 2.2, 'F-C': 2.2,'C-O': 2, }",
                            cell_line_width=0.03,
                            cell_line_rendering_color=(0, 0, 0),
                            camera_dir=(0, 0, 0),
                            property_name='initial_charges|initial_magmoms',
                            color_legend_title='Atomic Charge',
                            format_string='%.2f e',
                            property_value_range=[None, None],
                            text2overlay_dict_list=[{'text': 'O', 'pos': (0.49, 0.51)},
                                                    {'text': 'N', 'pos': (
                                                        0.49, 0.44)},
                                                    {'text': 'N', 'pos': (
                                                        0.44, 0.55)},
                                                    {'text': 'N', 'pos': (0.54, 0.55)},],
                            text2overlay_color=(0, 0, 0),
                            text2overlay_fontsize=0.03,
                            is_save=True,
                            fname_out='xxx/yy.jpg',
                            fig_size=(1000, 800),
                            ):
    """* 自定义属性绘图, 可以绘制原子电荷的增量, e.g.:
    arr = atoms2[:72].get_initial_charges() - atoms1.get_initial_charges()
    atoms1.set_initial_charges(charges=arr)
    ---
    - atoms: 包含电荷和磁矩分布的原子对象
    - property_name: 不知道是什么的话, 把atoms对象保存为.xyz 查看属性名
    """

    # 设置 原子大小和成键
    pipeline = self.get_pipeline(atoms=atoms, dbname=None, fname=None,)
    m1 = self.my_modifier_AssignParticleRadius(
        particle_radius_dict=particle_radius_dict)
    bond_pairwise_dict = self.get_bond_pairwise_dict(
        atoms=atoms) if bond_pairwise_dict is None else bond_pairwise_dict
    m2 = self.my_modifier_create_bonds(cutoff_bond=cutoff_bond,
                                       bond_width=bond_width,
                                       bond_mode=bond_mode,
                                       bond_pairwise_dict=bond_pairwise_dict)
    pipeline.modifiers.extend([m1, m2,])

    # cell
    self.cell_vis(data=pipeline.compute(),
                  line_width=cell_line_width,
                  rendering_color=cell_line_rendering_color)

    # 加入场景
    self.clean_scene()
    pipeline.add_to_scene()
    vp = self.get_vp(camera_dir=camera_dir)

    # 加入坐标轴图层
    overlay_tripod = self.overlay_coordinate_tripod(size=0.1)
    vp.overlays.append(overlay_tripod)

    # 加入colorlegend图层 color coding and color legend
    start_value, end_value = property_value_range
    m_color_coding = self.modifier_color_coding(property=property_name,
                                                start_value=start_value,
                                                end_value=end_value,)
    pipeline.modifiers.append(m_color_coding)
    overlay_color_legend = self.overlay_color_legend(modifier=m_color_coding,
                                                     title=color_legend_title,
                                                     label_size=0.8,
                                                     format_string=format_string)
    vp.overlays.append(overlay_color_legend)

    # 加入文本图层overlay_text, 如 C, N, O 等元素符号
    if text2overlay_dict_list:
      overlay_text_list = []
      for text_dict in text2overlay_dict_list:
        text = text_dict['text']
        pos = text_dict['pos']
        overlay_text = self.overlay_PythonViewportOverlay(text=text,
                                                          pos=pos,
                                                          font_size=text2overlay_fontsize,
                                                          color=text2overlay_color)
        overlay_text_list.append(overlay_text)
      vp.overlays.extend(overlay_text_list)

    # 保存图片
    if is_save:
      self.render_image(vp=vp, fname=fname_out,
                        size=fig_size)
      return fname_out
    else:
      return vp

  def wrapper_property_distribution(
      self,
      dbname='O_N3_graphene',
      particle_radius_dict={'H': 0.2,
                            'C': 0.5,
                            'Br': 0.7,
                            'O': 0.4,
                            'Cl': 0.5,
                            'N': 0.5},
      cutoff_bond=2,
      bond_width=0.2,
      bond_mode='pairwise',
      bond_pairwise_dict=None,
      cell_line_width=0.03,
      cell_line_rendering_color=(0, 0, 0),
      camera_dir=(0, 0, 0),
      property_name='initial_charges|initial_magmoms',
      property_value_range=[None, None],
      text2overlay_dict_list=[{'text': 'O', 'pos': (0.49, 0.51)},
                              {'text': 'N', 'pos': (
                                  0.49, 0.44)},
                              {'text': 'N', 'pos': (
                                  0.44, 0.55)},
                              {'text': 'N', 'pos': (0.54, 0.55)},],
      text2overlay_color=(0, 0, 0),
      text2overlay_fontsize=0.03,
      is_save=True,
      fig_size=(1000, 800),
      fname_out=None,
  ):
    """bond_mode='uniform|pairwise',
      bond_pairwise_dict="None|{'O-O': 2.5, 'O-H': 1.5,'C-C': 2, 'Br-C': 2.2, 'Cl-C': 2.2, 'F-C': 2.2,'C-O': 2, }",
    """
    # format_string 的设置 for self.overlay_color_legend
    if property_name == 'initial_charges':
      color_legend_title = 'Atomic Charges'
      format_string = '%.2f e'
    elif property_name == 'initial_magmoms':
      color_legend_title = 'Atomic Magnetic Moments'
      format_string = '%.2f μB'
    else:
      print('property_name 设置不对: initial_charges|initial_magmoms')
      return

    from vasp_learn import dataBase
    import ase.io
    directory_relax = dataBase.DataBase().get_directory(dbname=dbname)
    directory = os.path.join(directory_relax, 'single_point')
    if fname_out is None:
      fname_out = os.path.join(directory, f'{dbname}_{property_name}.jpg')

    # 获得原子对象 包含 电荷和磁矩分布的
    atoms = dataBase.DataBase().get_atoms_with_infos(dbname=dbname)
    ase.io.write(filename=os.path.join(directory, dbname+'.xyz'),
                 images=atoms)

    self.property_distribution(atoms=atoms,
                               particle_radius_dict=particle_radius_dict,
                               cutoff_bond=cutoff_bond,
                               bond_width=bond_width,
                               bond_mode=bond_mode,
                               bond_pairwise_dict=bond_pairwise_dict,
                               cell_line_width=cell_line_width,
                               cell_line_rendering_color=cell_line_rendering_color,
                               camera_dir=camera_dir,
                               property_name=property_name,
                               color_legend_title=color_legend_title,
                               format_string=format_string,
                               property_value_range=property_value_range,
                               text2overlay_dict_list=text2overlay_dict_list,
                               text2overlay_color=text2overlay_color,
                               text2overlay_fontsize=text2overlay_fontsize,
                               is_save=is_save,
                               fname_out=fname_out,
                               fig_size=fig_size,
                               )
    return fname_out

  def wrapper_structure_ab_md(self, dbname='Si_P_2V_Gra',
                              particle_radius_dict={
                                  'P': 0.5, 'Si': 0.5, 'C': 0.5},
                              fname_format='jpg',
                              ):

    from vasp_learn import dataBase
    fname_list = []
    for n, fname_surfix in zip([0, -1],
                               ['initial', 'final']):
      atoms = dataBase.DataBase().get_atoms_list(
          dbname=dbname, is_md=True, is_view=False)[n]
      directory = os.path.join(
          dataBase.DataBase().get_directory(dbname=dbname), 'ab_md')
      fname = self.atoms_structure(
          atoms=atoms,
          dbname=dbname,
          directory=directory,
          particle_radius_dict=particle_radius_dict,
          camera_dir=(-0.01, 2, -1),
          fname_out=os.path.join(
              directory,
              f'ab_md_{dbname}_{fname_surfix}.{fname_format}',),
      )
      fname_list.append(fname)
    return fname_list

  def example_test(self, modifier_list=[]):
    self.clean_scene()
    pipeline = self.get_pipeline(dbname='N3_graphene')
    pipeline.add_to_scene()

    # 获得修饰器实例
    m1 = self.my_modifier_AssignParticleRadius(
        particle_radius_dict={'C': 0.1, 'N': 0.5})
    m2 = self.my_modifier_create_bonds()
    # 将修饰器添加到管道中
    pipeline.modifiers.extend([m1, m2])

    for modifier in modifier_list:
      pipeline.modifiers.append(modifier)
    vp = self.get_vp()
    return vp
