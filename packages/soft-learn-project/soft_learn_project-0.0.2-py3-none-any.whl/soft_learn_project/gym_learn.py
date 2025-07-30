# 安装
# pip install -i https://pypi.tuna.tsinghua.edu.cn/simple gym
# pip install -i https://pypi.tuna.tsinghua.edu.cn/simple 'gym[box2d]'
# pip install -i https://pypi.tuna.tsinghua.edu.cn/simple box2d box2d-kengz

# 在增强学习中有2个基本概念，一个是环境（environment），称为外部世界，另一个为智能体agent（写的算法）。agent发送action至environment，environment返回观察和回报。
import gym

# env_name = 'LunarLander-v2'
# env = gym.make(id=env_name)
# state_dim = env.observation_space.shape[0]

# 创建环境

env = gym.make("CartPole-v1")
env.reset()

# 环境可能采取的行动: env.action_space，每个环境都带有 action_space 和 observation_space 对象。这些属性是 Space 类型，描述格式化的有效的行动和观察。
print("action_space: {}".format(env.action_space))
print("observation_space: {}".format(env.observation_space))
