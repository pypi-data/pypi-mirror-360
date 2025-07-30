import matplotlib
import numpy as np
import multiprocessing

matplotlib.rcParams['webagg.open_in_browser'] = False
matplotlib.use('webagg')

import matplotlib.pyplot as plt
from matplotlib.pyplot import *


def show_fig_(fig):
    fig.show()
    plt.show(block=False)

# 这是一个全局列表
current_progress = None

def show(fig=None):
    if fig is None:
        fig = plt.gcf()

    global current_progress
    if current_progress is not None:
        # 停止当前进程，并释放
        current_progress.terminate()
        current_progress.join()
    current_progress = multiprocessing.Process(target=show_fig_, kwargs=dict(fig=fig))
    current_progress.start()

def ax_3D(fig=None, overload=111):
    if fig is None:
        fig = figure()
    
    # 切换fig
    plt.figure(fig.number)
    ax = fig.add_subplot(overload, projection='3d')
    return ax

if __name__ == '__main__':
    
    ax = ax_3D()
    
    ax.scatter(np.random.rand(100), np.random.rand(100), np.random.rand(100))
    
    show()
    
    
    print('Done')
