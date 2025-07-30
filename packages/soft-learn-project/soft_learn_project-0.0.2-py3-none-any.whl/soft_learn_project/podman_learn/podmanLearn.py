import os


class PodmanLear():
  def __init__(self):
    """
    https://docs.podman.io/en/latest/Introduction.html
    https://github.com/containers/podman/blob/main/docs/tutorials/podman_tutorial.md
    https://podman.io/docs
    https://podman-desktop.io/downloads
    """
    pass

  def install(self):
    """brew install podman
    brew install podman-desktop
    """
    pass

  def def_file(self):
    """
      FROM docker://docker.m.daocloud.io/ubuntu:24.04

      RUN apt update && apt install -y openssh-server sudo \
        && mkdir /var/run/sshd \
        && echo 'root:123456' | chpasswd \
        && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
        && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

      EXPOSE 22

      CMD ["/usr/sbin/sshd", "-D"]
    """
    pass

  def run(self):
    """
    export name=ubuntu-amd64
    # 构建镜像：
    podman build -t $name .
    podman build --platform linux/amd64 -t $name .
    # 运行 
    podman run -d --name $name -p 2222:22 $name
    # 交互
    podman exec -it $name bash
    podman exec --privileged -it $name bash
    ssh-keygen -R "[localhost]:2222" # 删除 know_host 中的已知行
    # 本地 ssh 连接
    ssh root@server-ip -p 2222

    --- 其它命令
    查看运行的容器：
    podman ps -a 
    # 停止容器
    podman stop $name
    # 删除容器
    podman rm $name
    ----
    # 先导出 tar：
    podman save $name -o ${name}.tar  
    # 然后用 Apptainer 转换：
    limactl shell apptainer
    apptainer.lima build ${name}.sif docker-archive://${name}.tar 
    # 启动
    apptainer run -f ubuntu-amd64.sif bash -c "service ssh start"
    apptainer instance start -f --bind $HOME:/mnt/host_home ${name}.sif $name
    apptainer exec instance://$name bash -c "service ssh status"
    apptainer instance stop $name 
    ----不行
    apptainer build --sandbox ~/$name $name.sif
    apptainer instance start -f --bind $HOME:/mnt/host_home ${name} $name
    --- 可以 
    sudo apptainer instance start --boot --bind $HOME:/mnt/host_home ${name} $name
    sudo apptainer exec instance://$name bash -c "service ssh status"

    """
    pass
