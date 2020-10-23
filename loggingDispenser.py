import dispenser           #dispenser.py
import stattracker         #stattracker.py
import keyboard
import csv


if __name__ == '__main__':
    

   # Initialize dispenser
    dispenser = dispenser.Dispenser()
    dispenser.init_GPIO()
    
    # Initialize stats variables
    stats = stattracker.StatTracker()
    print("program started")
    running = True
    while running:
        
        if keyboard.is_pressed('q'):
            running = False
            print("Terminating program")
        if keyboard.is_pressed('a'):
            dispenser.numberOfActivations += 1
            print("Activations: ", dispenser.numberOfActivations)
        if keyboard.is_pressed('o'):
            with open('dataDispenser.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(stats.hoursList)
                writer.writerow(stats.activationsList)
                writer.writerow(stats.daysList)
                writer.writerow(stats.activationsListWeek)
                writer.writerow([dispenser.numberOfActivations])
                print("Writing to CSV file")         
                
        
        stats.update_activations_plot(dispenser.numberOfActivations)
        stats.update_activations_plot_week(dispenser.numberOfActivations)
        dispenser.update()
        
            
    dispenser.cleanup()
