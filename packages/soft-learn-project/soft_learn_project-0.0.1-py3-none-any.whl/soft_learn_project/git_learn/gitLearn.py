class GitLearn():
  def __init__(self) -> None:
    """Git 代码版本管理
    来自 mf_莫烦_git_learn
    https://www.bilibili.com/video/BV1MU4y1Y7h5/?spm_id_from=333.337.search-card.all.click&vd_source=5ec84b7f759de5474190c5f84b86a564  # 黑马
    ---
    码云: gitee: https://gitee.com/wangjl580/md_pot

    """
    pass

  def install(self):
    """安装
    1. conda install git  # 在环境中安装
    2. brew install git  # 系统中安装
    """
    pass

  def authenticate_GitHub(self):
    string = """ 1. 需要的话先安装 gh, brew install gh
    # 看到的提示信息表示 GitHub CLI（gh 命令行工具）需要先进行身份验证，才能执行像添加 SSH 密钥到 GitHub 账户这样的操作。
    2. $gh auth login 
    - Title for your SSH key: Personal Laptop # 自己随便起的名字
    - How would you like to authenticate GitHub CLI? Login with a web browser
    这样就把公钥上传到 https://github.com/settings/keys 里面了 
    之后就可以 使用 git clone git@github.com:materialsproject/fireworks.git 进行同步了
    """
    print(string)
    return None

  def step1_环境配置(self):
    """
    1. 进入需要文件管理的目录
    2. 为了更好地使用 git, 我们同时也记录每一个施加修改的人. 这样人和修改能够对应上. 所以我们在 git 中添加用户名 user.name 和 用户 email user.email
      * git config --global user.name "wjl"
      * git config --global user.email "<396292346@qq.com>"
    """
    pass

  def step2_获取本地仓库(self):
    """
    1. 进入某个目录, 该目录称为工作区 
    初始化
    git init  # 可以看到.git 目录生成
    git status # 查看版本库的状态 或者 git status -s  # 查看状态 简单的形式
    2. 增删改 文件  touch test.py  所有文件都处于未跟踪状态, 未暂存
    git add test.py  # 加入暂存区, 工作区-> 暂存区
    git add . # 加入所有
    git status
    3. 提交, 暂存区 -> 本地仓库
      1. git commit -m "create test.py"   -m 自定义这次改变的信息  
      2. git commit -am 'change 3 in dev'  # -a 表示直接加入并提交分支
      3. git commit --amend --no-edit  # 不增加 注释 提交
      git status 
    4. 查看提交的位置
    git log 
    git log --oneline --graph  # 这个命令常用
    --- 
    5. 版本回退  git log 查看 commit-id
    git reset --hard commit-id # 回退到指定的版本, 30 天后找不回
    git reflog # 查看操作记录 找到要回到 commit-id 
    git reset --hard commit-id  # 再回到某个版本  
    # 另一种
    git checkout 某个commit号  # 你切换到了一个旧commit
    # 查看/对比文件...
    git checkout main      # 切回当前主分支（恢复最新版本）
    # 对于单个文件
      1. git checkout 0c04910 -- 1.py   # 针对1.py

    6. 版本管理设置
    touch .gitignore  # 创建文件 
    vim .gitignore  # 编辑文件, 输入 *.a 表示所有的a文件都不加入版本管理
    # 不希望目录加入版本管理
    vim .gitignore  # 编辑文件, 输入 /dir/ 表示不加入版本管理
    git add .gitignore
    git commit -m "add .gitignore"
    """
    pass

  def step3_分支(self):
    """
    1. 查看分支
    git branch 
    git log --oneline --graph # 也能查看分支
    2. 创建分支（开发多版本）
    git branch 分支名
    3. 切换分支
    git checkout 分支名
    git checkout -b 分支名  # 创建并切换
    4. 合并分支 一般都是合并到主分支 main 
    git checkout main # 先切换回main
    git merge 分支名 
    如果有冲突则修改冲突, 解决冲突文件, 然后重新提交 `git commit -m 'solved confilct`
    # 合并分支的另一种方式
      1. 首先处于 main 分支
      2. git rebase dev ?
      3. 修改冲突, git add 1.py,  git rebase --continue  # 这种方式
    5. 删除分支
    git branch -d 分支名  # 删除分支
    ---
    你在开发时，通常是这样的流程：
    git checkout -b feature-A  # 开发新功能
    # 做一堆修改
    git commit -m "完成feature-A"
    做完后你希望把 feature-A 合并回主分支 main，让主分支也拥有这个新功能：
    git checkout main
    git merge feature-A
    --- 练习
    git branch wjl 
    git log --oneline --graph # 也能查看分支
    git add .
    git commit -m "add .ignore file"
    git branch wjl 
    git log --oneline --graph # HEAD -> wjl  head 表示当前所处的分支
    git checkout wj 
    git checkout main
    git merge wjl 
    """
    pass

  def step4_remote(self):
    """
    1. 配置
      1. ssh-keygen -t rsa # 生成秘钥
      2. cat ~/.ssh/id_rsa.pub  # 复制公钥 粘贴到 https://gitee.com/profile/sshkeys  个人-> 设置-> ssh 秘钥 中 需要输入密码
      3. ssh -T git@gitee.com  # 测试是否成功
         ssh -T git@github.com  # 测试是否成功

    2. 关联远程仓库
      1. gitee: https://gitee.com/wangjl580/md_pot  创建一个仓库, 点击ssh  复制 git@gitee.com:wangjl580/md_pot.git
      2. 把本地目录把本地目录变成仓库
      进入 /Users/wangjinlong/job/science_research/sci_scripts/construct_pot/md_pot 目录: git init; git add .; git commit -m 'first commit'; git log --oneline --graph 
      3. 关联远程仓库
      git remote add origin git@gitee.com:wangjl580/md_pot.git   origin 是远程仓库名
      git remote -v # 查看远程仓库
      可以关联多个仓库 
        1. 在github 上面创建一个仓库 https://github.com/wangjl580/md_pot
        2. git remote add github git@github.com:wangjl580/md_pot.git   # github 是远程仓库名 不能和gitee 的 origin 一样了 
    3. 把本地main 分支 推送到远程仓库 git push origin main 
      git branch -vv
      git push --set-upstream(或者-u) origin main:main # 本地main 和 远程main分支绑定, 第一次推送的时候
      git branch -vv # 查看
      git push  # 直接推送就可以了
      ---
      git push github main:main  # 推送本地仓库main到 github  main 
      git push origin main:main  # 推送本地仓库main到 gitee  main 
    4. clone 
      1. git clone git@gitee.com:wangjl580/md_pot.git  hello-git # 指定的文件名 也可以不指定
    5. fetch 抓取 
      1. git fetch  # 从远程仓库拉取最新的版本到本地, 不会合并分支
      2. git merge origin/main  # 合并分支
    6. pull  拉取 # 相当于 fetch + merge 
      git pull 
    """

  def some_order(self):
    """
      ## github  网上的资源

      1. 理解 git 是本地管理库, github 是 online 管理库

      ## github 用法  

      1. 在 github 或者 gitee 注册一个账户
      2. 然后添加你的一个 online 版本库 repository:
      3. 增加远程仓库 在需要上传的目录中 执行: `git remote add origin git@github.com:wangjl580/git_demo.git`  # 增加的仓库名称为 origin 网址为 ...
      4. 添加一个额外的远程仓库 `git remote add gitee https://gitee.com/wangjl580/git_learn.git`  # > 添加多个远程仓库时, 名称不能一样
      5. 推送 `git push -u origin master` # 把master 推送到 名称为origin的远程仓库, 使用-u选项的主要好处是，它将设置默认的上游分支。这意味着在接下来的推送操作中，你只需执行 `git push` 命令
      6. 也可以推送dev 分支 `git push origin dev`
      7. 更改远程仓库的URL `git remote set-url origin https://gitee.com/wangjl580/git_learn.git` #  重置远程仓库origin 的URL为 https...
      8. 如果要删除名为 origin 的远程仓库，可以运行以下命令：`git remote remove origin` # 或者 `git remote rm origin` # 请注意，删除远程仓库不会影响本地仓库的内容，它只是删除了与远程仓库的关联。

      ### 拉取远程文件

      1. mkdir tt3
      2. cd tt3
      3. git init
      4. git remote add origin <git@gitee.com>:wangjl580/git_test_local.git
      5. git pull origin master # 拉取 远程仓库origin 中的 master branch # 这将获取远程仓库 origin 的 master 分支的最新更改并将其合并到你的本地 master 分支。

      ## 运行以下命令来克隆GitHub上的项目到本地

      `git clone https://github.com/MorvanZhou/Evolutionary-Algorithm.git`
    """
    pass

  def old_tips(self):
    r"""
      #用法tips, 需要记忆，如果看不懂，则看Lesson01-19
      #用于重要文件中的修改，以及保存到开源中国的服务器上
      #以test目录为例cd test
      git init #初始化,建立本地库
      git config -l #查看或者配置
      git config --global alias.cm commit #将commit命令简化为cm,建立别名，知道有这个命令即可
      git help config #config的帮助文档

      #
      git status  #查看状态，常用
      git add . #增加文件到索引区
      git commit -m "1st commit" #提交到本地库
      git commit --amend  #后来修改的内容不再做新的提交记录，追加到上一次的提交记录里面去
      git log --oneline -6 #查看提交历史
      touch .gitignore #添加*.tmp 表示*.tmp文件和目录不参与Git库的提交和管理。

      #---回到某次提交时的状态
      git reflog -6 #查看提交的记录,获取第一列字符如28a4661
      git reset --hard 28a4661  #回到提交id时的状态

      #---建立分支,可能用不到
      git branch #查看分支桩体
      git branch dev #开一个dev分支
      git checkout dev #切换到分支
      #之后的操作都是在分支中进行，其他命令一样
      git checkout master #且换回主分支 master
      git merge dev #在主分支中进行操作，dev分支中编辑修改完成后，回到主分支，然后合并dev分支
      git branch -d dev #删除dev分支

      #---增加系统版本号标签
      git tag #显示版本号
      git tag v1.0.0 #添加版本标签, 之后在commite

      #---提交代码到服务器端,首先在OSChina我的空间中建立一个库https://gitee.com/wangjl580/test
      git remote -v #查看远端服务器地址，如果为空则建立
      git remote add ox https://gitee.com/wangjl580/test.git #增加远程库地址，ox为后面地址的简写
      git remote remove ox #如果不对可以删除
      git remote add origin https://gitee.com/wangjl580/test.git
      #git add .; git commit -m "4th commit" 之后同步
      git push origin master [-f]#将本地库同步(sync)到远程Git服务器
      #或者git tag v1.0.0; git push origin v1.0.0
      git clone https://gitee.com/wangjl580/test.git #把远程库克隆到本地文件夹
      git pull origin master #取回 origin/master 分支

      #---git push origin master 需要输入密码
      如果不想每次输入用户名和密码，则可以使用credential.helper（凭证助手）来记住Username和Password。
      $ git config --global credential.helper store
      $ git push https://github.com/owner/repo.git #或者git push origin master
      # 然后输入用户名和密码
      这样下次再git push时，就不用输入用户和密码了。

      上传并指定默认	push -u origin master	指定origin为默认主机，以后push默认上传到origin上 #-u 为指定默认
      以后想在commit后同步到Github上，只要直接执行 git push 就行啦：
      从远程仓库同步	pull	在本地版本低于远程仓库版本的时候，获取远程仓库的commit

      如果你在创建 repository 的时候，加入了 README.md 或者 LICENSE ，那么 github 会拒绝你的 push 。你需要先执行 git pull origin master。


      #----如果用ssh的方式,需要进行如下操作
      如果想通过git@github 的方式：
      git remote add ssh git@github.com:wangjl580/github_test.git
      git push -u ssh main  #必须先进行下面的操作,以后直接git push
      参考网址：https://www.cnblogs.com/schaepher/p/5561193.html
      #如果是通过html
      git remote add origin https://github.com/wangjl580/github_test.git
      git push -u origin main #第一次输入账号密码，以后可以直接git push

      本地Git和Github的连接到Github[4]注册账号。

      本地配置用户名和邮箱（如果已经设置好，跳过该步）：
      git config --global user.name "你的用户名"
      git config --global user.email "你的邮箱"

      或者你直接在config文件里改，位置在 C:\Users\你的用户名\.gitconfig 。如下图所示，添加相应信息：
      生成ssh key
      运行 ssh-keygen -t rsa -C "你的邮箱" ，它会有三次等待你输入，直接回车即可。

      将生成的ssh key复制到剪贴板，执行 clip < ~/.ssh/id_rsa.pub （或者到上图提示的路径里去打开文件并复制）：

      打开Github，进入Settings：
      点击左边的 SSH and GPG keys ，将ssh key粘贴到右边的Key里面。Title随便命名即可。
      点击下面的 Add SSH key 就添加成功了。
      测试一下吧，执行 ssh -T git@github.com ：
      嗯，这样就成功了！

      注：
      对于 oschina 的 “码云” ，执行 ssh -T git@git.oschina.net
      对于 coding 的 “码市” ，执行 ssh -T git@git.coding.net
    """
    pass
