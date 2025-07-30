import os


class DockerLearn:
  def __init__(self):
    """learn: https://www.bilibili.com/video/BV1HP4118797?spm_id_from=333.788.player.switch&vd_source=5ec84b7f759de5474190c5f84b86a564&p=5
    https://github.com/xiaohejun/cpp_tutorials
    https://docs.docker.com/get-started/
    https://hub-stage.docker.com/  # 镜像仓库
    https://github.com/Daocloud/crproxy
    https://github.com/DaoCloud/public-image-mirror
    https://github.com/kubesre/docker-registry-mirrors
    """
    self.dockerfile = """
        # Dockerfile for a simple Python application
        FROM python:3.9-slim
        WORKDIR /app
        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt
        COPY . .. . /app
        CMD ["python", "main.py"]
        """

  def install(self):
    """ ubuntu 安装 docker
    1. 安装依赖
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
    ---ubuntu 安装 docker
    Set up Docker's apt repository.
    # Add Docker's official GPG key:
    sudo apt-get update
    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    Install the Docker packages.
    Latest Specific version
    To install the latest version, run:
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    Verify that the installation is successful by running the hello-world image:
    sudo docker run hello-world
    --- centOS 安装 docker
    sudo dnf remove docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-engine
    1. 安装依赖
    sudo dnf install -y dnf-plugins-core
    2. 添加 Docker 仓库
     sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    3. 安装 Docker 引擎
    sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    4. 启动 Docker 服务
    sudo systemctl enable --now docker
    5. 验证 Docker 安装
    sudo docker run hello-world
    6. 加入用户组
    sudo groupadd docker
    sudo usermod -aG docker $USER
    newgrp docker
    # 先配置镜像加速器 然后重启
    docker run hello-world
    7. 开机启动
    sudo systemctl enable docker.service
    sudo systemctl enable containerd.service
    8. 配置镜像加速器
    sudo mkdir -p /etc/docker
    sudo tee /etc/docker/daemon.json <<-'EOF'
    {
      "registry-mirrors": [
      "https://docker.m.daocloud.io",
      "https://docker.1ms.run",
      "https://docker.domys.cc",
      "https://docker.imgdb.de",
      "https://docker-0.unsee.tech",
      "https://docker.hlmirror.com",
      "https://cjie.eu.org",
      "https://hub.rat.dev",
      "https://docker.1panel.livedocker.rainbond.cc",
        "https://registry.docker-cn.com",
        "https://docker.mirrors.ustc.edu.cn",
        "https://hub-mirror.c.163.com",
        "https://mirror.baidubce.com"
      ]
    }
    EOF
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    docker run hello-world
    """
    pass

  def vscode_set(self):
    """
    1. 安装 docker 插件
    2. 安装 dev container 插件
    之后会看到 vscode 中左侧的鲸鱼图标，点击之后会出现一个选项，选择 Reopen in Container，然后会自动打开一个容器
    ---
    3. C/C++ Extension Pack
    4. CMake Tools, cmake 工具
    5. 搜索框中输入>cmake build 会出现一个选项，点击之后会自动编译
    """

  def learn_镜像(self):
    """--- 镜像源
    docker.m.daocloud.io
    docker.1ms.run
    docker.domys.cc
    docker.imgdb.de
    docker-0.unsee.tech
    docker.hlmirror.com
    cjie.eu.org
    hub.rat.dev
    docker.1panel.livedocker.rainbond.cc
    ---
    构建docker镜像
    1. 拉取镜像 docker pull docker.1ms.run/nginx
    2. 根据 Dockerfile 构建镜像
    docker build -t cpp_tutorials .
    该命令的各个部分的解释如下：
    -t cpp_tutorials: -t 参数用于指定构建的镜像的标签（tag）。在这个例子中，镜像的标签被设置为 cpp_tutorials，您可以根据需要自行更改。
    .: 这表示 Dockerfile 的路径，. 表示当前目录。Dockerfile 是一个包含构建指令的文本文件，它定义了如何构建 Docker 镜像。
    ---
    # 查看镜像列表
    docker images
    --- # 删除镜像
    docker rmi -f <镜像ID>
    --- push 镜像
    docker login
    docker tag <镜像ID> <仓库地址>/<镜像名称>:<标签>
    docker push <仓库地址>/<镜像名称>:<标签>
    --- 拉取镜像
    docker pull <仓库地址>/<镜像名称>:<标签>
    --- 保存和加载镜像
    ---
    # 保存镜像
    docker save -o my_image.tar my_image
    # 加载镜像
    docker load -i my_image.tar
    ---
    # 指定平台
    # 拉取 AMD64 架构的 Ubuntu 镜像
    docker pull --platform linux/amd64 ubuntu
    # 运行 AMD64 容器
    docker run -it --platform linux/amd64 ubuntu
    # 验证架构（容器内执行）
    uname -m  # 将显示 x86_64
    ---
    通过 docker buildx 构建多平台镜像
    <BASH>
    # 创建支持多架构的构建器（只需设置一次）
    docker buildx create --name multiarch-builder --use
    # 在容器中验证架构（AMD64）
    docker run -it --platform linux/amd64 ubuntu uname -m
    """
    pass

  def learn_dockerfile(self,
                       fname_dockerfile='/Users/wangjinlong/job/soft_learn/Docker_learn/Dockerfile',
                       image='my_ubuntu_amd64:22.04',
                       name_container='my_ubuntu2',
                       port_host=2222,
                       ):
    dockerfile = f"""
      # 使用Ubuntu 22.04作为基础镜像
      FROM --platform=linux/amd64 ubuntu:22.04

      # 设置时区
      ENV TZ=Asia/Shanghai
      RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

      # 安装SSH服务和必要工具
      RUN apt-get update && \
          apt-get install -y openssh-server sudo && \
          rm -rf /var/lib/apt/lists/*

      # 配置SSH
      RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
          echo 'root:password' | chpasswd

      # 创建数据目录
      RUN mkdir /data

      # 暴露SSH端口
      EXPOSE 22

      # 启动SSH服务前确保目录存在并具有正确权限
      CMD ["sh", "-c", "mkdir -p /var/run/sshd && chmod 0755 /var/run/sshd && exec /usr/sbin/sshd -D"]
    """
    with open(fname_dockerfile, 'w') as f:
      for line in dockerfile.split('\n'):
        line = line.strip()
        f.write(line + '\n')

    # 构建镜像
    # docker build -t my_ubuntu_amd64:22.04 . # 即使使用 -f 指定Dockerfile路径，点号仍决定上下文根目录, 指定上下文确保Docker能访问到构建所需的文件, 确定了构建的基准目录。
    # 运行容器
    # docker run -dit --name my_ubuntu_amd64 --platform linux/amd64 -p 2222:22 -v /Users/wangjinlong/job/soft_learn/Docker_learn/my_ubuntu_volume:/data --network mynet   my_ubuntu_amd64:22.04
    pass

  def learn_容器(self):
    """创建并运行镜像 docker run -d 后台运行 -it 交互模式 -p 端口映射(宿主机端口: 容器内端口) -v 卷挂载 -e 环境变量 --name 容器名称 + 镜像名称(:tag)
    启动容器时指定 IP：
    --network mynet # 指定网络
    --ip 192.168.100.100  # 指定 IP 地址
    ---
    docker run --name u4 -it ubuntu-22.04
    docker start  u4 # 启动容器
    # docker run -p 80:5000 -d my-finance # -p 80:5000 表示将容器的 5000 端口映射到主机的 80 端口，-d 表示在后台运行容器。
    docker run --name cpp_tutorials_container -v /Users/wangjinlong/job/soft_learn/Docker_learn/cpp_tutorials:/cpp_tutorials -it cpp_tutorials
    该命令的各个部分的解释如下：
    docker run: 这是 Docker 命令的一部分，用于在容器中运行镜像。
    --name cpp_tutorials_container: --name 参数用于指定容器的名称。在这个例子中，容器的名称被设置为 cpp_tutorials_container，您可以根据需要自行更改。
    -v /Users/hejun/project/cpp_tutorials:/cpp_tutorials: -v 参数用于将主机的目录（/Users/hejun/project/cpp_tutorials）与容器内部的目录（/cpp_tutorials）进行挂载（映射）。这样可以在容器内访问主机上的文件和目录。
    -it: -i 和 -t 参数一起使用，以交互模式运行容器，并分配一个终端（TTY）以便与容器进行交互。
    cpp_tutorials: 这是要运行的镜像的名称。 使用这个命令，您可以在一个新的容器中运行名为 cpp_tutorials 的镜像。容器将会创建，并在交互模式下启动，您可以在容器的终端中执行命令和操作。
    在容器中，您通过 -v 参数将主机上的 /Users/hejun/project/cpp_tutorials 目录挂载到容器内的 /cpp_tutorials 目录。这使得容器内的操作可以访问主机上的文件和目录，方便在开发环境中共享和处理代码。
    ---

    # stop 容器
    docker stop <容器 ID>
    # 启动容器
    docker start <容器 ID>
    # 重启容器
    docker restart <容器 ID>
    # 删除容器
    docker rm <容器 ID>
    docker rm -v nginx # 在删除容器时添加 -v 参数自动删除关联的匿名卷：
    # 进入容器
    docker exec -it <容器 ID> bash
    docker exec -it u4 /bin/bash
    docker exec my_ubuntu apt update # 运行容器内的命令
    # 查看容器日志
    docker logs <容器 ID>
    # 查看容器状态
    docker ps
    # 查看容器详细信息
    docker inspect <容器 ID>
    # 查看容器网络信息
    docker network inspect <网络 ID>
    # 查看容器的挂载信息
    docker inspect <容器 ID> | grep Mounts
    ---  当您在容器内进行更改后，可以通过以下方式将其保存为新的镜像：
    # 1. 运行一个基础容器
    docker run -it --name my_container ubuntu:22.04 /bin/bash
    # 2. 在容器内进行修改
    ➜ (容器内) apt update
    ➜ (容器内) apt install -y python3 pip
    ➜ (容器内) pip install numpy pandas
    ➜ (容器内) exit
    # 3. 提交容器为镜像
    docker commit my_container my_python_env:1.0
    # 4. 验证新镜像
    docker images | grep my_python_env
    # 5. 使用新镜像运行容器
    docker run -it my_python_env:1.0 python3 -c "import numpy; print(numpy.__version__)"
    """

  def learn_数据卷(self):
    """docker run -d --name mysql -p 3307:3306 -e TZ=Asia/Shanghai -e MYSQL_ROOT_PASSWORD=123 docker.1ms.run/mysql
    ---
    命令
    docker volume --help # 查看帮助信息 下面的不用记, 记住这个就行了, 随时查看帮助信息
    docker volume create --help

    docker volume create # 创建数据卷
    docker volume ls # 查看所有数据卷
    docker volume rm # 删除指定数据卷
    docker volume inspect # 查看某个数据卷的详情
    docker volume prune # 清除数据卷
    ---
    在执行docker run命令时，使用 -v 数据卷:容器内目录 可以完成数据卷挂载当创建容器时，如果挂载了数据卷且数据卷不存在，会自动创建数据卷
    """

  def example_1(self):
    """ 1. 搜索 docker 镜像 www.hub.docker.com  # nginx 镜像
    docker pull docker.1ms.run/nginx
    2. docker images 查看镜像列表
    docker save --help 查看保存镜像的帮助信息
    docker save -o nginx.tar docker.1ms.run/nginx:latest
    docker rmi docker.1ms.run/nginx:latest 删除镜像
    docker load -i nginx.tar 加载镜像
    3. 启动镜像
    docker run -d --name nginx -p 80:80 docker.1ms.run/nginx:latest
    4. 查看容器列表 docker ps
    #也可以加格式化方式访问，格式会更加清爽
    docker ps --format "table\t{{.ID}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}\t{{.Names}}"
    #第6步，访问网页，地址:http://虚拟机地址
    #第7步，停止容器
    docker stop nginx
    #第8步，查看所有容器
    docker ps --format "table\t{{.ID}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}\t{{.Names}}"
    # 查看所有容器
    docker ps -a
    #第9步，再次启动nginx容器
    docker start nginx
    #第10步，再次查看容器
    docker ps --format "table\t{{.ID}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}\t{{.Names}}"
    # 查看日志
    docker logs nginx i
    docker logs -f nginx # follow 模式 一直输出日志
    # 本机 ip
    192.168.1.7:80 # 浏览器访问 nginx 服务器
    # 进入容器交互
    docker exec -it nginx /bin/bash # 进入容器
    docker exec -it mysql bash
    mysql -uroot -p # 进入 mysql 数据库
    docker exec -it mysql mysql -uroot -p # 进入 mysql 数据库
    # 删除容器
    docker run -d --name nginx2 -p 81:80 docker.1ms.run/nginx:latest
    docker ps -a # 查看所有容器
    docker stop nginx2 # 先停止容器
    docker rm nginx2 # 再删除容器
    # docker rm -f nginx2 # 或者强制删除容器
    # docker rm -f $(docker ps -a -q) # 删除所有容器
    """
    pass

  def example_2(self):
    """
    案例1-利用Nginx容器部署静态资源
    需求:
    创建Nginx容器，修改nginx容器内的html目录下的index.html文件，查看变化将静态资源部署到nginx的html目录
    ---
    1.
    docker exec -it nginx bash
    cd /usr/share/nginx/html
    2. docker stop nginx
    docker rm nginx
    3. docker run -d --name nginx -p 80:80 -v /Users/wangjinlong/job/soft_learn/Docker_learn/nginx_volume:/usr/share/nginx/html docker.1ms.run/nginx:latest # 挂载目录
    复制容器内文件到宿主机:  docker cp ntest:/usr/share/nginx/html/. /Users/wangjinlong/job/soft_learn/Docker_learn/nginx_volume/
    # 创建个临时容器 docker run -d --name ntest  docker.1ms.run/nginx:latest
    # 复制容器内文件到宿主机:  docker cp ntest:/usr/share/nginx/html/. /Users/wangjinlong/job/soft_learn/Docker_learn/nginx_volume/
    # 清理临时容器: docker stop ntest && docker rm ntest
    4. docker volume ls # 查看数据卷
    5. docker volume inspect html # 查看数据卷详情
    找到挂载点 "Mountpoint": "/var/lib/docker/volumes/html/_data",
    # 查看容器的详情
    docker inspect mysql
    基于宿主机目录实现MySQL数据目录、配置文件、初始化脚本的挂载(查阅官方镜像文档
    1). 挂载/root/mysql/data到容器内的/var/lib/mysql目录
    2). 挂载/root/mysql/init到容器内的/docker-entrypoint-initdb.d目录，携带课前资料准备的SQL脚本
    3). 挂载/root/mysql/conf到容器内的/etc/mysql/conf.d目录，携带课前资料准备的配置文件 # 这些目录的位置通过查看官方镜像文档来确定
    docker run -d \
      --name mysql \
      -p 3307:3306 \
      -e TZ=Asia/Shanghai \
      -e MYSQL_ROOT_PASSWORD=123\
      -v /Users/wangjinlong/job/soft_learn/Docker_learn/mysql_volume/data:/var/lib/mysql \
      -v /Users/wangjinlong/job/soft_learn/Docker_learn/mysql_volume/init:/docker-entrypoint-initdb.d \
      -v /Users/wangjinlong/job/soft_learn/Docker_learn/mysql_volume/conf:/etc/mysql/conf.d \
      docker.1ms.run/mysql:latest
    """

  def example_3(self):
    """
    1. 自定义镜像
    Dockerfile就是一个文本文件，其中包含一个个的指令(Instruction)，用指令来说明要执行什么操作来构建镜像,来Docker可以根据Dockerfile帮我们构建镜像。常见指令如下:
    指令  说明    示例
    FROM  指定基础镜像    FROM centos:6
    ENV  设置环境变量，可在后面指令使用    ENV key value
    COPY  拷贝文件到镜像中    COPY jre1.8.tar.gz /tmp
    RUN  执行Linux的shell命令，一般是安装过程的命令    RUN tar -zxvf /tmp/jre11.tar.gz&& EXPORTs path=/tmp/jre11:$path
    EXPOSE  指定容器运行时监听的端口，是给镜像使用者看的    EXPOSE 8080
    ENTRYPOINT  镜像中应用的启动命令，容器运行时调用    ENTRYPOINT java -jar xx.jar
    2. 构建镜像

    cd ~/job/soft_learn/Docker_learn/demo # 进入目录
    docker build -t openjdk:11.0-jre-buster . # 构建镜像 根据 Dockerfile 构建的镜像
    # FROM docker.1ms.run/python:3.13.3-slim-bookworm
    docker build -t cpp_tutorials .
    解释该命令的各个部分：
    docker build: 这是 Docker 命令的一部分，用于构建 Docker 镜像。
    - -t cpp_tutorials:
    -t 参数用于指定构建的镜像的标签（tag）。在这个例子中，镜像的标签被设置为 cpp_tutorials，您可以根据需要自行更改。

    - .:
    这表示 Dockerfile 的路径，. 表示当前目录。Dockerfile 是一个包含构建指令的文本文件，它定义了如何构建 Docker 镜像。

    使用这个命令，您可以在当前目录中的 Dockerfile 中定义的环境中构建一个名为 cpp_tutorials 的 Docker 镜像。Docker 将按照 Dockerfile 中指定的指令执行构建过程，并生成一个可用的镜像。
    3. 构建容器
    docker run -d --name openjdk -p 8080:8080 openjdk
    4. 查看容器
    docker ps
    5. 查看容器日志
    docker logs -f openjdk
    6. 测试访问 打开浏览器
    http://192.168.1.7:8080/hello/count
    # docker 网络
    docker inspect mysql  #  172.17.0.3
    docker inspect openjdk # 172.17.0.4
    1. 连接 openjdk 容器
    docker exec -it openjdk /bin/bash
    ping 172.17.0.3 # 可以 ping 通 mysql 容器
    """

  def learn_网络(self):
    """
    网络
    加入自定义网络的容器才可以通过容器名互相访问，Docker的网络操作命令如下:
    命令  说明
    docker network create # 创建一个网络
    docker network ls # 查看所有网络
    docker network rm # 删除指定网络
    docker network prune # 清除未使用的网络
    docker network connect # 使指定容器连接加入某网络
    docker network disconnect # 使指定容器连接离开某网络
    docker network inspect # 查看网络详细信息
    # 示例
    1. docker network ls # 查看所有网络
    2. docker network create mynet # 创建一个名为mynet的桥接网络
    # docker network ls
    3. docker network connect mynet mysql # 将mysql容器加入mynet网络
    # docker inspect mysql # 查看mysql容器的详细信息
    # docker network connect mynet openjdk # 将openjdk容器加入mynet网络
    # 还可以创建的时候就连上该网络
    docker rm -f openjdk # 删除 openjdk 容器
    # 创建 openjdk 容器并加入 mynet 网络, docker inspect openjdk # 查看 openjdk 容器的详细信息
    docker run -d --name openjdk -p 8080:8080 --network mynet openjdk
    # docker exec -it openjdk /bin/bash # 进入 openjdk 容器
    # ping mysql # 可以 ping 通 mysql 容器
    # ping nginx # 不行, 因为 nginx 容器不在 mynet 网络中
    """
    pass

  def learn_网络端口(self):
    """
    # 安装 ping
    sudo apt install iputils-ping
    ---
    netstat -an -p tcp | grep 22 # 查看端口是否被占用
    查看特定端口(如22) netstat -an | grep 22
    -a ：显示所有连接和监听端口
    -n ：以数字形式显示地址和端口
    -p : 指定协议（tcp/udp）
    -r ：显示路由表项
    要检查12345端口是否可用作Docker端口映射，可以使用以下方法：
    1. 检查端口占用 （macOS/Linux通用命令）：
    # 检查TCP端口
    /usr/sbin/lsof -i :12345
    # 或使用netstat
    netstat -an | grep 12345
    2. 结果解读 ：
    - 无输出 → 端口可用
    - 有 LISTEN 状态 → 端口已被占用
    """
    pass

  def example_4(self):
    """
    DockerCompose
    Docker Compose通过一个单独的docker-compose.yml 模板文件(YAML 格式)来定义一组相关联的应用容器，帮助我们实现多个相互关联的Docker容器的快速部署。
    docker compose [OPTIONS] [COMMAND]
    options
    -f, --file FILE 指定一个或多个使用 YAML 格式编写的配置文件，默认值是 docker-compose.yml。
    -p, --project-name NAME 指定项目名称，用于区分不同的 Compose 项目。
    docker compose --help
    参数或指令
    up # 创建并启动所有service容器
    down # 停止并移除所有容器、网络
    ps # 列出所有启动的容器
    logs # 查看指定容器的日志
    stop # 停止容器
    start # 启动容器
    restart # 重启容器
    top # 查看运行的进程
    exec # 在指定的运行中容器中执行命令
    """
    pass

  def learn_other(self):
    """
    1. 查看所有Docker对象占用空间
    docker system df
    2. 查看镜像大小
    docker images --format "table\t{{.Repository}}\t{{.Tag}}\t{{.Size}}"
    3. 查看容器大小
    docker ps -s -a 
    4. 清理未使用的空间
    docker system prune
    # 或仅清理未使用的镜像
    docker image prune
    """


class myExercise:
  def __init__(self):
    pass

  def step1_images(self):
    """
    1. 建立一个 ubuntu 镜像, 镜像名为 my_ubuntu, 端口为 8080, 目录为 / data, 时区为 Asia/Shanghai, 自动重启
    docker run -dit --name my_ubuntu_amd64 --platform linux/amd64 -p 2222: 22 - v / Users/wangjinlong/job/soft_learn/Docker_learn/my_ubuntu_amd64_volume: / data - e TZ = Asia/Shanghai --restart always ubuntu: 22.04
    2. 运行容器
    docker run -dit --name ubuntu22.04-amd64 --platform linux/amd64 -p 2222:22 ubuntu:22.04
    docker run -dit --name ubuntu2204 -p 2222:22 ubuntu:22.04
    ---  使用自定义网络并指定静态IP ：
    # 创建自定义网络
    docker network create --subnet=172.18.0.0/16 mynet
    # 运行容器并指定IP
    docker run -dit --name my_ubuntu2404 --network mynet --ip 172.18.0.100 --restart unless-stopped my_ubuntu2404:latest

    """
    pass

  def step2_ssh_连接(self):
    """
    export name=ubuntu2404
    1. 进入容器
    docker exec -it $name /bin/bash
    exit 
    2. SSH 连接（网络隔离环境）
    # Step 1: 容器内安装 SSH
    docker exec $name sh -c "apt update && apt install -y openssh-server"
    docker exec $name bash -c "apt install -y vim iproute2 curl"
    # 允许 root 登录
    docker exec $name sh -c "sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config"
    # 启动 SSH 服务
    docker exec $name service ssh start  | status # 查看|启动
    # 启用SSH服务开机启动, enable 改为status 是检查服务状态 # 可能不管用 如果ssh 连不上 先启动服务
    docker exec $name systemctl enable ssh
    # Step 2: 设置 root 密码
    docker exec -it $name passwd
    docker exec  $name bash -c "echo 'root:123456' | chpasswd"
    # Step 3: 获取容器 IP
    docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $name
    ----
    # Step 4: 从主机连接 可能需要删除本地主机的已知主机# ssh-keygen -R "[localhost]:2422" 
    # 或者删除旧的known_hosts条目: ssh-keygen -R 172.17.0.2  
    # 永久解决方案 (修改SSH配置):--- echo "StrictHostKeyChecking no" >> ~/.ssh/config
    echo "UserKnownHostsFile /dev/null" >> ~/.ssh/config
    ---
    ssh root@172.17.0.2 
    ssh root@localhost -p 2222
    # step 6: 配置 ssh 免密登录
    # ssh-keygen -t rsa -b 4096 # 如果没有密钥对
    # 复制公钥到远程主机
    export IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $name)
    cat ~/.ssh/id_rsa.pub | ssh root@$IP "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
    # cat ~/.ssh/id_rsa.pub | ssh root@localhost -p 2322 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
    ---
    方法 4：使用 VS Code 远程开发（最佳体验）
    安装 Dev Containers 扩展
    按 F1 输入 "Attach to Running Container"
    选择你的 Ubuntu 容器
      配置 SSH 连接

    <BASH >
    # 1. 启用 Rosetta 转译（需 Docker Desktop 4.17+）
    docker run - -privileged linuxserver/qemu-user-static
    # 2. 创建使用 Rosetta 的容器
    docker run - it \
      - -platform = linux/amd64 \
      - -security-opt seccomp = unconfined \  # 解除安全限制
      --cpus = 4 \                           # 分配更多资源
    💡 提示：Apple Silicon 用户总会加上 - -platform linux/amd64 以绕过 ARM 兼容性问题，否则您可能会遇到无法运行 x86 二进制文件的情况。
    --- 从mac 连接 vmware 虚拟机centos 的 容器
    ssh root@172.16.81.153 - p 2122
    # ssh wjl@172.16.81.153 # 连接 vmware 虚拟机centos
    --- 免密码
    cat ~/.ssh/id_rsa.pub | ssh root@172.16.81.153 - p 2122 "mkdir -p ~/.ssh && cat >>~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
    --- 实现 vscode 连接容器
    1. 配置 SSH 连接  # 或者直接add new 在里面输入 ssh root@172.16.81.153 -p 2022
    按下 F1 打开命令面板
    输入 "ssh" → 选择 Remote-SSH: Open SSH Configuration File
    选择默认配置文件(通常是 ~/.ssh/config)
    添加以下配置并保存：
    Host MyDockerContainer
      HostName 172.16.81.153
      User root
      Port 2122
      ForwardAgent yes
      IdentityFile ~/.ssh/id_rsa
      # 可选：指定远程路径
      # RemoteCommand cd /workspace && /bin/bash
    3. 通过 VSCode 连接
    按 F1 → 输入 "Connect to Host" → 选择 Remote-SSH: Connect to Host...
    在下拉列表中选择刚创建的配置 MyDockerContainer
    首次连接会弹出验证：Continue
    """
    pass

  def run_with_static_ip(self, name='my',
                         image='ubuntu',
                         ip='172.18.0.100'):
    """运行带有静态IP的容器"""
    cmd = f"docker network create --subnet=172.18.0.0/16 {name}_net"
    os.system(cmd)
    cmd = f"docker run -d --name {name} --network {name}_net --ip {ip} {image}"
    os.system(cmd)
