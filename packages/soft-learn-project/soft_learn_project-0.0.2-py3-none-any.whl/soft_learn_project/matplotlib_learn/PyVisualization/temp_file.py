import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

fig,ax = plt.subplots()
ax: plt.Axes
ax.set_xlim(0,np.pi*2)
ax.set_ylim(-1,1.1)
x = []
y = []


def update(n):
    x.append(n)
    y.append(np.sin(n))
    plt.plot(x,y,color="black")

ani = animation.FuncAnimation(fig=fig,func=update, frames=iter(np.arange(0,np.pi *2,0.1)),repeat=False, interval=1000)
plt.show()
