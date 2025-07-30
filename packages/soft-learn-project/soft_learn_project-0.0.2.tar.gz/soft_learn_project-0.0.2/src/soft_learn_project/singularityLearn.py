class SingularityLearn:
  def __init__(self):
    pass

  def install(self):
    """
    Install singularity
    https://docs.sylabs.io/guides/latest/user-guide/quick_start.html

    https://www.bilibili.com/video/BV1F44y1H7hB/?spm_id_from=333.337.search-card.all.click&vd_source=5ec84b7f759de5474190c5f84b86a564

    sudo dnf install -y dnf-plugins-core 
    sudo dnf config-manager --enable crb || dnf config-manager --enable powertools
    # Install basic tools for compiling 
    sudo dnf groupinstall -y "Development Tools" 
    # Install RPM packages for dependencies 
    sudo dnf install  -y autoconf  automake crun cryptsetup fuse fuse3 fuse3-devel git libseccomp-devel libtool shadow-utils-subid-devel squashfs-tools wget zlib-devel
    # 
    export VERSION=1.24.1 OS=linux ARCH=arm64 && \ 
    wget https://dl.google.com/go/go$VERSION.$OS-$ARCH.tar.gz && \
    sudo tar -C /usr/local -xzvf go$VERSION.$OS-$ARCH.tar.gz
    echo 'export PATH=/usr/local/go/bin:$PATH' >> ~/.bashrc && \
    source ~/.bashrc
    export VERSION=4.3.1
    # wget https://github.com/sylabs/singularity/releases/download/v${VERSION}/singularity-ce-${VERSION}.tar.gz
    # tar -xzf singularity-ce-${VERSION}.tar.gz && 
    cd singularity-ce-${VERSION}
    # 必须在虚拟机硬盘上安装，否则会报错
    ./mconfig
    cd builddir
    make 
    sudo make install
    # make -C builddir && \
    # sudo make -C builddir install
    """
    pass

  def learn_def_file(self):
    """
    1. 编写容器定义文件（.def）：
    编写一个容器定义文件，描述容器的基础镜像、安装的软件和配置。
    Bootstrap: docker
    From: docker.m.daocloud.io/library/ubuntu:22.04

    %post
        # 设置国内软件源（可选）
        sed -i 's@archive.ubuntu.com@cn.archive.ubuntu.com@g' /etc/apt/sources.list

        # 安装基本系统工具
        apt-get -y update
        DEBIAN_FRONTEND=noninteractive apt-get -y install \
            software-properties-common \
            build-essential \
            wget \
            git \
            python3 \
            python3-pip \
            python3.10-venv

        # 创建隔离的Python虚拟环境
        python3 -m venv /opt/venv

        # 更新pip并安装基础工具（留作后续安装用）
        /opt/venv/bin/pip install --upgrade pip wheel setuptools
        /opt/venv/bin/pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ ase

        # 设置环境变量（激活虚拟环境）
        echo 'export PATH="/opt/venv/bin:$PATH"' >> $SINGULARITY_ENVIRONMENT
        echo 'export PS1="(ase-env) $PS1"' >> $SINGULARITY_ENVIRONMENT

    %environment
        # 设置容器内语言环境
        export LC_ALL=C.UTF-8
        export LANG=C.UTF-8

    %runscript
        # 默认行为：进入虚拟环境下的Python
        exec /opt/venv/bin/python "$@"  # 直接使用虚拟环境中的 Python 解释器

    %labels
        Maintainer "Your Name"
        Version "1.0"

    %help
        原子模拟环境（基础版）
        内置Python虚拟环境位于: /opt/venv
        进入容器后自动激活虚拟环境

    """

  def learn_构建容器(self):
    """
    1. 构建容器：
    sudo singularity build ase_container.sif ase_container.def
    2. 以沙盒方式构建容器：
    singularity build --fakeroot --sandbox ase_sandbox/ ase_container2.def
    3. 从 Docker 镜像构建容器：
    singularity build --fakeroot --sandbox ase_sandbox/ docker://ubuntu:22.04
    singularity build hello-world.sif docker-archive:/home/wjl/tmp2/def/hello-world.tar
    singularity run hello-world.sif
    """
    pass

  def learn_shell_交互(self):
    """
    1. sandbox 方式
    sudo /usr/local/bin/singularity shell --writable ase_sandbox
    singularity shell --writable ase_sandbox
    2. SIF 方式
    singularity shell ase.sif
    """
    pass

  def learn_run_exec(self):
    """ ase.sif 可以换成 ase_sandbox/ 目录
    singularity run ase.sif  
    singularity exec ase.sif python 

    加上 -c 'print("OK")' 执行命令, 加上文件就是执行文件
    singularity run ase.sif -c 'print("OK")'
    singularity exec ase.sif python -c 'print("OK")'
    singularity run ase.sif z.py
    singularity exec ase.sif python z.py
    """

  def sandbox_to_sif(self):
    """
    沙盒目录（sandbox）转换为 .sif 文件，
    sudo /usr/local/bin/singularity build ase_sandbox.sif ase_sandbox/
    singularity build t.sif ase_sandbox/
    """
    pass

  def usage(self):
    """
    ---
    与原 SIF 文件对比
    操作类型	SIF 文件命令	沙盒目录命令
    执行 Python 代码	singularity run image.sif -c "..."	singularity exec sandbox/ python -c "..."
    进入交互式 shell: singularity shell image.sif	
    sudo singularity shell --writable ase_sandbox/
    singularity shell --fakeroot --writable ase_sandbox/
    绑定额外目录	singularity run -B /host/path image.sif ...	singularity exec -B /host/path sandbox/ ...

    4. 直接调用沙盒内的 Python 解释器
    singularity exec ase_sandbox/ /opt/venv/bin/python z.py
    # 进入容器的 shell 环境, 并执行 Python 命令
    singularity shell ase_sandbox/ 
    python z.py
    # 
    singularity exec ase_sandbox/ python z.py 
    """
    pass

  def my_exacise_1(self):
    """
    1. 直接从本地Docker镜像构建 SIF 容器

    singularity build --arch amd64 my_ubuntu.sif docker-daemon://my_ubuntu:latest
    # singularity build --sandbox my_ubuntu/ docker-daemon://my_ubuntu:latest 
    - docker-daemon:// 前缀表示从本地Docker引擎获取镜像
    - --arch amd64 选项指定构建的目标架构为 AMD64
    2. 检查Docker镜像的架构
    docker inspect my_ubuntu | grep Architecture
    """
