class LimaLearn:
  def __init__(self):
    """https://lima-vm.io/docs/
    """
    pass

  def install(self):
    """brew install lima
    """
    pass

  def usage(self, fname='/Users/wangjinlong/job/soft_learn/lima_learn/ubuntu2404.yaml'):
    """lima nerdctl run -it --rm ubuntu:24.04
    """
    pass
    ubuntu2404 = """
    images:
      - location: "https://cloud-images.ubuntu.com/releases/24.04/release/ubuntu-24.04-server-cloudimg-amd64.img"
        arch: "x86_64"

    provision:
      - mode: system
        script: |
          #!/bin/bash
          apt update
          apt upgrade -y

    mounts:
      - location: "~"
        writable: true
        propagation: shared
    """
    with open(fname, 'w') as f:
      f.write(ubuntu2404)
    # 2.启动实例
    # limactl start ubuntu2404.yaml
    # limactl start --arch=x86_64 ubuntu2404.yaml
    # 删除实例
    # limactl delete ubuntu2404
    pass
