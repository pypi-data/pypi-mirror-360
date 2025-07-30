class apptainerLearn:
  def __init__(self):
    """https://apptainer.org/docs/admin/main/installation.html
    http://www.achelous.org/Container-Tech/Singularity-in-nutshell.html
    """
    pass

  def usage(self):
    from soft_learn.lima_learn import limaLearn
    ll = limaLearn.LimaLearn()
    """
    brew install lima
    limactl start --arch=x86_64 template://apptainer
    limactl shell apptainer
    By default, the host home directory is mounted as read-only in the guest, but there is also a shared writable directory mounted in /tmp/lima that can be accessed both from the host and in the guest.
    """
    pass

  def other(self):
    """放弃使用singularity
    """
    from soft_learn.singularity_learn import singularityLearn
    sl = singularityLearn.SingularityLearn()
    sl.usage()
    pass

  def step1_docker_container(self):
    """建立docker容器 安装 apptainer
    docker run --privileged -dit -v $HOME:/host_home --platform linux/amd64 --name "apptainer-amd64-vm" -p 2322:22 ubuntu:24.04
    docker exec -it apptainer-amd64-vm bash
    apt update
    apt install -y software-properties-common
    add-apt-repository -y ppa:apptainer/ppa
    apt update
    apt install -y apptainer
    for centos # sudo dnf install -y epel-release # $ sudo dnf install -y apptainer
    测试
    apptainer exec docker://alpine cat /etc/alpine-release
    apptainer exec docker://docker.m.daocloud.io/library/alpine cat /etc/alpine-release
    ---
    limactl shell apptainer
    """
    pass

  def step2_images(self):
    """http://www.achelous.org/Container-Tech/Singularity-in-nutshell.html
    构建自己的容器
    singularity build ./jason-tensorflow.sif docker://tensorflow/tensorflow:latest-gpu
    方法二: 手动定制
    #步骤1: 从Docker Hub下载Tensorflow GPU镜像，存储为本地sandbox
    singularity build --sandbox sandbox docker://tensorflow/tensorflow:latest-gpu
    #步骤2: sandbox目录为可修改的容器，可以直接进行修改
    mkdir sandbox/opt/train -p
    cp train.sh sandbox/opt/train
    ...
    #步骤3: 从修改后的sanbox生成只读的SIF格式容器，用于生产
    singularity build jason-tf.sif sandbox/
    上述步骤2中，用户也可以选择以可写（writable）方式运行容器，进行修改。
    #步骤1: 从Docker Hub下载Tensorflow GPU镜像，存储为本地sandbox
    singularity build --sandbox sandbox docker://tensorflow/tensorflow:latest-gpu
    #步骤2: 从sandbox以可修改的方式运行容器，进行修改和定制
    singularity shell --writable sandbox/
    方法三： 通过Definition文件制作容器
    Singularity支持用户编写Definition文件创建容器，详细的指令参考链接 (https://sylabs.io/guides/3.7/user-guide/definition_files.html) 。为了创建上述Tensorflow的容器，用户可以编写下述jason_tf.def文件。
    Bootstrap: docker
    From: tensorflow/tensorflow:latest-gpu
    Stage: build

    %files
        /var/py/train.py /opt/train.py

    %labels
        Author jason.zhang@xtaotech.com
        Version v0.0.1

    %help
        This is a demo container used to illustrate a def file that uses all
        supported sections.
    编写好自己的def文件，通过运行下述命令产生SIF格式的容器用于生产。
    singularity build jason-tf.sif jason_tf.def
    ...

    #步骤3: 从修改后的sanbox生成只读的SIF格式容器，用于生产
    singularity build jason-tf.sif sandbox/
    ---
    # 拉取镜像 pull | build 
    apptainer pull ubuntu.sif docker://docker.m.daocloud.io/library/ubuntu:24.04
    用户也可使用其它类型的URI（源）下载容器：
    singularity build lolcow.sif library://sylabs-jms/testing/lolcow # 从Container Library
    singularity pull hello.sif shub://vsoch/hello-world # 从Singularity Hub下载容器
    apptainer build he.sif docker-daemon://hello-world:latest
    docker save hello-world:latest -o hello.tar
    apptainer build hello.sif docker-archive://hello.tar
    # 构建沙盒镜像, 上面的 he.sif 换成 --sandbox hello-world/ 即可
    apptainer build --sandbox ubuntu_sandbox2/ docker-daemon://hello-world:latest
    apptainer.lima build --sandbox /tmp/lima/my_ubuntu_amd64 docker-daemon://my_ubuntu_amd64:22.04
    # 从cif 转换为 sandbox
    apptainer build --sandbox ubuntu_sandbox ubuntu.sif
    apptainer build ubuntu.sif ubuntu_sandbox
    # 通过定义文件构建 （创建 ubuntu.def 文件）
    ```
    Bootstrap: docker
    From: docker.m.daocloud.io/ubuntu:24.04

    %post
      apt update
      apt install -y vim curl
    %runscript
      echo "这是容器启动时运行的脚本"
      exec "$@" # 允许传递参数给容器
    %environment
      # 设置环境变量
      export PATH=/usr/local/bin:$PATH
    ```
    apptainer build ubuntu.sif ubuntu.def
    使用定义文件构建镜像, 构建后， %runscript 内容会被编译进 .sif 文件, - 使用命令： apptainer inspect --runscript my_container.sif 这会显示容器中定义的runscript内容, - 当使用 apptainer run 命令时，会自动执行 %runscript 中的内容, 可以包含任何有效的shell命令
    # 即使不是通过 .def 文件创建的sandbox容器，您仍然可以通过以下方式修改 apptainer run 的执行内容：
    1. 对于沙盒模式容器:
    - 直接编辑容器内的 /.singularity.d/runscript 文件
    - 修改后保存即可生效
    2.临时覆盖:
    - 使用 apptainer exec 替代 run 来执行特定命令
    - 通过环境变量或绑定目录传递配置
    """
    pass

  def step3_run(self):
    """http://www.achelous.org/Container-Tech/Singularity-in-nutshell.html
    运行一个程序
    用户可通过singularity exec命令运行一个容器内的程序，程序执行完毕，容器退出。类似于docker run命令。
    singularity exec jason-tf.sif python /opt/train.py
    运行容器中默认命令
    用户运行singularity run 命令会执行singularity 镜像默认的 runscript 命令,例如
    [root@host] singularity run jason-tf.sif
    $ docker run -u $(id -u):$(id -g) args...
    Singularity> python /opt/test.py 
    2021-06-01 11:04:46.541868: I tensorflow/stream_executor/platform/default/dso_loader.cc:53] Successfully opened dynamic library libcudart.so.11.0
    ...
    [name: "/device:CPU:0"
    device_type: "CPU"
    memory_limit: 268435456
    locality {
    }
    incarnation: 17604286807710674827
    ]
    Singularity>
    交互式启动容器运行命令
    用户运行singularity shell命令可以交互式的方式运行容器，执行一系列命令。这种执行方式与docker run -it类似。例如：

    [root@host] singularity shell jason-tf.sif
    INFO:    Using cached SIF image
    ---
    # 运行镜像
    #  shell 命令更明确地表达了交互意图, exec 方式更适合在脚本中使用
    apptainer shell ubuntu.sif  # 交互式 shell
    apptainer exec ubuntu.sif bash  # 运行bash shell, 这两个命令最终都会进入bash shell
    apptainer exec ubuntu.sif cat /etc/os-release  # 运行命令
    apptainer shell --writable --fakeroot ubuntu_sandbox/
    apptainer exec --writable ubuntu_sandbox bash
    # 在沙盒中安装软件包
    apptainer exec --writable ubuntu_sandbox bash -c "apt update && apt install -y package"
    # Run the user-defined default command within a container
    apptainer run ubuntu.sif
    """
    pass

  def volume(self):
    """http://www.achelous.org/Container-Tech/Singularity-in-nutshell.html
    如何映射和访问存储卷
    Singularity容器与Docker容器最大区别是生产使用的SIF格式容器是只读的。容器启动的时候，singularity命令自动挂载一些主机的目录到容器（$HOME , /sys:/sys , /proc:/proc, /tmp:/tmp, /var/tmp:/var/tmp, /etc/resolv.conf:/etc/resolv.conf, /etc/passwd:/etc/passwd, 和 $PWD）。如果需要访问主机上的其它目录或者挂载的存储卷，用户需要使用--bind选项映射主机目录到容器内。

    singularity exec --bind /mnt/nfs:/mnt/nfs jason-tf.sif python /opt/test.py
    """
    pass

  def step4_instance(self):
    """
    # 查看实例
    apptainer instance list
    # 启动实例
    - start 是后台服务模式， run 是前台执行模式
    - start 需要后续使用 apptainer shell 或 apptainer exec 与实例交互
    - run 会阻塞终端直到命令执行完成
    - start 更适合数据库/服务器等长期运行的服务
    - run 更适合执行一次性命令
    apptainer instance start --writable --fakeroot --network=bridge  my_ubuntu_amd64/  my_ubuntu_amd64
    apptainer instance run --writable ubuntu/ ubuntu
    apptainer instance stop ubuntu
    # 要进入已经启动的Apptainer实例进行交互，可以使用以下命令：
    - 如果实例是用 --writable 参数启动的，你在shell中的修改会持久化
    - 退出shell不会停止实例，实例会继续在后台运行
    apptainer shell instance://my_ubuntu_amd64
    apptainer exec instance://my_ubuntu_amd64 bash
    ----
    apptainer instance start --writable --fakeroot --network=bridge  my_ubuntu_amd64/  my_ubuntu_amd64
    apptainer instance start --writable --fakeroot --network=host  my_ubuntu_amd64/  u2
    # 获取实例PID
    INSTANCE_PID=$(apptainer instance list | grep my_ubuntu_amd64_instance | awk '{print $2}')
    # 设置端口转发
    sudo apt install -y socat
    sudo nsenter -t $INSTANCE_PID -n socat TCP-LISTEN:2222,fork TCP:localhost:22
    """
    pass

  def step5_newtork_ssh(self):
    """
    - Apptainer默认使用主机网络，SSH端口与主机共享
    - 可使用 --net 或 --network 参数指定网络配置
    - 建议绑定到特定端口
    apptainer instance start --writable --network=bridge --port 2222:22 my_ubuntu_amd64/ my_ubuntu_amd64
    apptainer instance start --network=bridge --network-args "portmap=2222:22/tcp" my_ubuntu_amd64/ my_ubuntu_amd64_instance
    """
    pass

  def my_test(self):
    """
      limactl shell apptainer  # 进入Lima虚拟机
      export name=ubuntu2404

      # 构建可写容器
      apptainer build --sandbox $name docker-daemon://ubuntu:24.04 

      # 安装必要服务
      apptainer exec --fakeroot --writable $name bash -c "
        apt update -y &&
        apt install -y openssh-server iproute2 net-tools vim&&
        sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config &&
        echo 'root:123456' | chpasswd
      "
      apptainer exec --writable $name systemctl enable ssh

      # 启动实例
      apptainer instance start --fakeroot --network=bridge --writable $name $name
      sudo apptainer instance start --network=bridge --writable --boot $name $name
      sudo apptainer instance stop $name
      这样容器会尝试启动 /sbin/init，如果你的容器里有 systemd, 就会顺便启动 ssh 等守护进程。 --network=bridge 可以不加

      # 查看动态分配的IP
      apptainer instance list
      container_ip=$(sudo apptainer exec instance://$name ip -4 -o addr show eth0 | awk '{print $4}' | cut -d/ -f1)
      echo "容器IP: $container_ip"

      # 启动ssh 服务 
      sudo apptainer exec instance://$name bash -c "service ssh status"  # start 
      sudo apptainer exec instance://$name /usr/sbin/sshd # 或者
      # 自动启动 ssh服务  修改容器内部的 /.singularity 目录下的 startscript 或 runscript
      sudo apptainer shell --writable $name 
      mkdir -p /.singularity.d
      echo '#!/bin/bash
      service ssh start
      exec "$@"
      ' > /.singularity.d/startscript
      chmod +x /.singularity.d/startscript
      exit
      注意：/.singularity.d/startscript 是 Apptainer（Singularity）默认在 instance start 时执行的启动脚本。
      apptainer instance stop $name 
      sudo apptainer instance start --network=bridge --writable $name $name

      # 从Lima虚拟机内验证SSH, 密码:123456
      ssh root@$container_ip  
      其他相关选项：
      -o StrictHostKeyChecking=no  跳过主机密钥验证：如果远程服务器的密钥不在本地 known_hosts 文件中，直接自动接受并连接，无需用户确认。
      -o UserKnownHostsFile=/dev/null，则不会保存密钥到 known_hosts，避免文件冲突（常用于临时容器场景）。
      ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@$container_ip

      # 免密码登录
      cat ~/.ssh/id_rsa.pub | ssh root@$container_ip "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
      ssh root@$container_ip
      "
      ----
      sudo apptainer exec instance://$name bash
      --- 挂载 注意：你在沙盒里要提前确保 /mnt/host_home 存在，否则挂载时目录不会自动创建。
      ~/ubuntu2404/mnt$ mkdir host_home # 需要现在沙盒中创建要挂载的目录
      sudo apptainer instance start --network=bridge --writable --bind $HOME:/mnt/host_home $name $name
      sudo apptainer exec instance://$name bash
      sudo apptainer instance stop $name
      # 构建sif
      sudo apptainer build ${name}.sif $name
      apptainer instance start --network=bridge --bind $HOME:/mnt/host_home ${name}.sif $name 
      apptainer instance start --boot --bind $HOME:/mnt/host_home ${name}.sif $name
      apptainer instance start --fakeroot --network=bridge --bind $HOME:/mnt/host_home ${name}.sif $name
      apptainer instance start --network=bridge --bind $HOME:/mnt/host_home ${name}.sif $name
      apptainer exec instance://$name ps aux | grep ssh

      --- sudo 沙盒  修改沙盒中 vim etc/ssh/sshd_config 中的 Port 22 为 Port 2222  可以不用 --network=bridge  连接的时候变成 ssh root@localhost -p 2222
      sudo apptainer instance start --network=bridge --bind $HOME:/mnt/host_home ${name} $name
      sudo apptainer instance list
      sudo apptainer instance start --bind $HOME:/mnt/host_home ${name} $name
      sudo apptainer exec instance://$name bash -c "service ssh status"
      ssh root@localhost -p 2222 # 可以连接上
      sudo apptainer instance stop $name
      sudo apptainer shell instance://$name
      /usr/sbin/sshd -D -d
      --- sudo sif 
      sudo apptainer instance start --bind $HOME:/mnt/host_home ${name}.sif $name

      --- 非root 沙盒 
      apptainer instance start --fakeroot --writable --bind $HOME:/mnt/host_home ${name} $name
      apptainer exec instance://$name bash -c "service ssh status"
      ssh root@localhost -p 2222 
      ssh root@<服务器IP> -p 2222 # 本地连接服务器
      apptainer instance stop $name
      apptainer shell --writable ${name}
      service ssh status

      --- 用sif不行
      apptainer shell ${name}.sif
      sudo apptainer instance start --network=bridge --bind $HOME:/mnt/host_home ${name}.sif $name
      sudo apptainer instance list
      ssh root@10.22.0.48 # 不能连接上
      sudo apptainer exec instance://$name bash -c "service ssh status"
    """
    pass

  def my_def(self):
    r"""
      Bootstrap: docker
      From: docker.m.daocloud.io/ubuntu:24.04

      %labels
      Author wangjinlong
      Version v1.0

      %post
          apt-get update && apt-get install -y \
              systemd systemd-sysv \
              openssh-server \
              sudo \
              wget curl vim \
              build-essential 
          # 创建 ssh 默认目录
          mkdir -p /var/run/sshd
          mkdir -p /root/.ssh

          # 允许root远程登录（仅测试，生产环境慎用）
          echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config
          echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

          # 设置root密码 (示范用, 实际请更换)
          echo 'root:123456' | chpasswd

          # 禁用dns解析（加速ssh登录）
          echo 'UseDNS no' >> /etc/ssh/sshd_config

          # 安装你科学计算软件（举例）
          # pip3 install numpy scipy matplotlib

      %environment
          export PATH=/usr/local/bin:$PATH

      %runscript
          echo "Container started. Use instance mode for services."
          exec bash

      %startscript
          echo "Starting sshd..."
          service ssh start
          exec "$@"
          # exec /sbin/init
          # 但注意 systemd 模式对沙盒权限、cgroups 要求更高，适合服务器用。 如果你是科研开发机器、个人笔记本，通常前面的轻量模式已经足够用了。
    """
    # 3. 构建镜像
    # export name=my-ubuntu24
    # sudo apptainer build --sandbox $name ubuntu24.def  # 注意：--sandbox 生成的是可读写目录，方便你后续添加软件。

    # 4. 启动容器
    # 第一次手动测试一下 ssh 是否能正常启动：
    # sudo apptainer instance start --writable $name $name
    # sudo apptainer shell instance://$name
    # 在容器内部确认 ssh 是否已启动：
    # ps aux | grep sshd
    # 5. 网络与远程访问（进阶）
    # 你如果希望本机能通过 ssh 进入容器，需要做端口映射：
    # sudo apptainer instance start --writable --net --network-args "portmap=2222:22/tcp" my-ubuntu my-ubuntu-instance
    # 这样你可以：
    # ssh root@localhost -p 2222

    pass
