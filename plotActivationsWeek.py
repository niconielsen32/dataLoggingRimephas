import matplotlib
matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
import pylab
import matplotlib.pyplot as plt
import pygame
from pygame.locals import *
import datetime as dt
import random
from matplotlib.ticker import MaxNLocator

pygame.init()

# Matplotlib plot
fig = plt.figure(figsize=[8, 4.8], dpi=100)


days = "%A"

timeFormat = days

numberOfActivations = 0
numberOfActivationsDay = 0

lastDay = 0

daysList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
activationsListWeek = [0]*7


def update_activations_plot_week(weekdays, numberOfActivations):
    global lastDay, activationsListWeek, numberOfActivationsDay


    day = dt.datetime.now()
    day = day.strftime(timeFormat)
    #print("Day: ", day)

    indexDay = weekdays.index(day)

    if day != lastDay:
        trailingActivations = numberOfActivations - numberOfActivationsDay
        print("Activations: ", trailingActivations)
        activationsListWeek.insert(indexDay, round(trailingActivations))
        activationsListWeek.pop(indexDay + 1)
        print("acti list: ", activationsListWeek)
        numberOfActivationsDay = numberOfActivations

    lastDay = day
        
    return activationsListWeek



# Pygame plot from matplotlib plot

window = pygame.display.set_mode((800, 480), DOUBLEBUF)
screen = pygame.display.get_surface()


print(daysList)
print(activationsListWeek)

# Pygame loop
terminated = False

while not terminated:

    antivationsListWeek = update_activations_plot_week(daysList, numberOfActivations)

    acti = [120, 80, 180, 60, 150, 170, 100]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminated = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print("ESC")
                terminated = True
            if event.key == pygame.K_a:
                numberOfActivations += 1
                print("Number of Activations Week", numberOfActivations)
            if event.key == pygame.K_p:

                print(daysList)
                print(activationsListWeek)

                plt.clf()
                plt.bar(daysList,acti)
                plt.title('Number Of Activations Week')


                ax = plt.gca()
                ax.yaxis.set_major_locator(MaxNLocator(integer=True))

                #send to local webserver
                #mpld3.show()
    

                # Using backend
                canvas = agg.FigureCanvasAgg(fig)
                canvas.draw()
                renderer = canvas.get_renderer()
                raw_data = renderer.tostring_rgb()

                size = canvas.get_width_height()

                surf = pygame.image.fromstring(raw_data, size, "RGB")
                screen.blit(surf, (0,0))
                pygame.display.flip()

                    
pygame.display.quit()
pygame.quit()
