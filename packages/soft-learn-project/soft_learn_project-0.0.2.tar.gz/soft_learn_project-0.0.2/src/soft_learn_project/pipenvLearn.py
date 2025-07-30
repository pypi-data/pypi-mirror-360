class PipenvLearn:
  def __init__(self):
    """https://packaging.python.org/en/latest/tutorials/managing-dependencies/
      Pipenv 是一个 Python 项目的依赖管理工具。如果你熟悉 Node.js 的 npm 或 Ruby 的 bundler，它在精神上与这些工具类似。虽然 pip 个人使用通常已经足够，但 Pipenv 适用于协作项目，因为它是一个更高层次的工具，可以简化常见用例中的依赖管理。
    """
    pass

  def install(self):
    """
      python3 -m pip install --user pipenv
    """
    pass

  def usage(self):
    """  pipenv --help  # 查看帮助
    为你的项目安装包¶
      cd myproject
      pipenv install requests
      激活环境
        run pipenv shell.
      运行环境中的命令
        pipenv run
      touch main.py # 输入以下内容
        '''
        import requests
        response = requests.get('https://httpbin.org/ip')
        print('Your IP is {0}'.format(response.json()['origin']))
        '''
      然后你可以使用 `pipenv run` 运行这个脚本：
        pipenv run python main.py
      你应该会得到类似以下的输出：
      Your IP is 8.8.8.8
    """
    pass
