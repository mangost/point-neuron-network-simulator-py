import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import itertools

from debug_print import debug_print as dbp


class Controller:
    #self.dt_frame = 0
    #self.time     = 0
    #self.fps      = 0

    def __init__(self, callback_prototype,time0 = 0, dt= 1.0/32, fps = 30):
        self.callback_prototype = callback_prototype
        self.dt= dt
        self.time = time0
        self.fps  = fps
        self.on   = True

    def step(self, ndt = 1):
        if self.on:
            self.time += self.dt * ndt

    def callback_producer(self):
        return self.callback_prototype(self)

        
def on_key_prototype(controller):
    def on_key(event):
        global controller
        if event.key == ' ':
            controller.on = not controller.on
        elif event.key == 'a':
            controller.step(-100)
        elif event.key == 'd':
            controller.step(100)
        else:
            pass
    return on_key


# data is np.ndarray
#def running_plot(data,legend,points,dt,y_lim,controller):
def running_plot(data,legend,points,dt,y_lim):

    # Check legend
    if len(data) != len(legend):
        dbp("Error: the size of legend does not metch that of data. Ignored and all other legend be blank.")
        if len(data) < len(legend):
            legend = legend[0:len(data)]
        else:
            for i in range(len(data)-len(legend)):
                legend.append(' ')
    

    fig = plt.figure()

    ax = plt.axes((0,points*dt),y_lim)
    ax.grid()


    time_text = ax.text(0.02,0.95*y_lim[1],'',transformation=ax.transAxes)
    time_text.figure.canvas.mpl_connect('key_press_event',on_key)

    x = np.linspace(0,points*dt,points)

    lines = []
    for one in legend:
        line, = ax.plot([],[],label=one)
        lines.append(line)

    controller = Controller(on_key_prototype)


    def init():
        time_text.set_text('')
        for line in lines:
            line.set_data([],[])
        return tuple(lines.append(time_text))
        
    def animate():
        global controller
        controller.step()
        t = controller.quantum
        time = controller.time

        time_text.set_text('time = %.3f' % time)
        data_piece = data[:,t:t+points]
        for d,l in  itertools.izip_longest(data_piece,lines):
            l.set_data(x,d)
        return tuple(lines.append(time_text))




    # call the animator.  blit=True means only re-draw the parts that have changed.
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=200, interval=0.01 , blit=True)

    plt.show(block=False)
