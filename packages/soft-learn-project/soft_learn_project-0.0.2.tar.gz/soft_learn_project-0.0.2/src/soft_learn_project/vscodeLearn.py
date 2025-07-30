class VscodeLearn():
  def __init__(self) -> None:
    """设置搜索: 'windows: Auto Detect color scheme', 并勾选即可以获得类名的颜色为浅蓝色
    """
    pass
  def install(self):
    string = """ vscode 安装
    下载所需要的版本
    安装: sudo dpkg -i code_1.95.1-1730354713_arm64.deb 
    打开vscode -> 终端新建x.py -> 用vscode 打开, 根据提示安装插件
    打开vscode -> 终端新建x.ipynb -> 用vscode 打开, 根据提示安装插件 jupyter  ipykernel 
    选择内核: 找到 py39
    直接进入py39 环境: 终端vim ~/.bashrc -> 最后一行加上 conda activate py39  -> 保存退出-> source ~/.bashrc
    关闭 vscode -> 重新打开
    """
    print(string)
    return None
  
  def shut_keys(self):
    string = """ 常用快捷键
    shift+command + P, reload windows 
    """
    print(string)
    return None
  
  def settings_dot_json(self):
    """我的 settings.json 设置 
{   
    // 设置主题颜色
    "workbench.colorTheme": "Visual Studio Light",
    "files.autoSave": "onFocusChange",
    "git.openRepositoryInParentFolders": "never",
    "jupyter.widgetScriptSources": [
        "jsdelivr.com",
        "unpkg.com"
    ],
    // 使代码显示颜色
    "typescript.preferGoToSourceDefinition": true,  
    "window.autoDetectColorScheme": true,
    // 设置代码缩进为2 空格
    "python.defaultInterpreterPath": "/Users/wangjinlong/opt/anaconda3/envs/py3918/bin/python",
    "editor.tabSize": 2,   
    "editor.autoIndent": "brackets",
    "editor.defaultFormatter": "ms-python.autopep8",
    "autopep8.args": [
        "--indent-size=2"
    ],
    "terminal.integrated.inheritEnv": false,
    "notebook.lineNumbers": "on",
    // 代码自动换行
    "editor.wordWrap": "bounded",

    // 终端设置 terminal 
    "terminal.integrated.defaultProfile.osx": "zsh",  // 设定终端为zsh, 否则出问题
    "terminal.integrated.profiles.osx": {
                "zsh": {"path": "/bin/zsh","args": ["-l"]}
        },
}
    """
    pass

  def change_interpreter(self,):
    # py 文件改变解释器
    s1 = '打开py 文件后右下角状态栏会显示当前使用的解释器, 点击后可以改变'
    s2 = '代开配置文件搜索 python path, 可以修改默认的解释器'
    # ipynb 的解释器
    s3 = '打开ipynb 文件后 右上角标题栏显示内核, 点击后修改'
    pass

  def paste_fig(self,):
    # vscode 中的jupyter-lab 直接粘贴剪贴板图片
    s1 = '在设置中搜索paste images'
    s22 = '启用ipynb>experimental > paste iamges: enables'
    s3 = '还需要启用editor>experimental > paste iamges: enables'

  def good_插件(self,):
    """
    """
    # 1. 安装这两个插件
    # * TODO: TODO Highlight 插件
    # * Todo Tree 插件
    # 2. 使用
    # * 在平时的使用过程中，先在需要标记的地方写上  TODO: 记得一定是大写的TODO，并且是英文状态下的冒号。当写完之后，TODO:会以高亮的方式显示。在左侧会出现待办事项的图标，非常方便用于以后的查找
    pass

  def color_scheme(self):
    # 设置搜索: 'windows: Auto Detect color scheme', 并勾选即可以获得类名的颜色为浅蓝色
    pass
