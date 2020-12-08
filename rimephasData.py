import csv
import pandas as pd
from threading import Timer,Thread,Event

motorPin = 4
pirPin = 5

numberOfActivations = 0
numberOfPeople = 0

motorActivated = False
pirActivated = False

filename = "dataRimephas.csv"

seconds = 0
minutes = 0
hours = 0


class TimerClass():

   def __init__(self,t,hFunction):
      self.t=t
      self.hFunction = hFunction
      self.thread = Timer(self.t,self.handle_function)

   def handle_function(self):
      self.hFunction()
      self.thread = Timer(self.t,self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()



def clearFile(filename):
    open(filename, 'w').close()

def incrementSeconds():
    global seconds, minutes, hours

    seconds += 1

    if(seconds == 60):
        minutes += 1
        seconds = 0

    if(minutes == 60):
        hours += 1
        minutes = 0

    
def readDataFromFile(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            print(row)
        file.close()


def readDataToPDframe(filename):
    df = pd.read_csv(filename)
    print(df)


def writeDataToFile(filename, type):
    with open(filename, 'a') as file:
        print("Writing to File")
        writer = csv.writer(file)
        writer.writerow([type, hours, minutes, seconds, numberOfActivations, numberOfPeople])
        file.close()



def setupLogging():
    pass



def main():

    clearFile(filename)

    timer = TimerClass(1, incrementSeconds)
    timer.start()

    motorActivated = True

    with open(filename, 'a') as file:
            writer = csv.writer(file)
            writer.writerow(["Type", "Hours", "Minutes", "Seconds", "Total Activations", "Total People"])
            file.close()

    if(pirActivated):
        pass
        #writeDataToFile(filename, "Person")

    if(motorActivated):
        pass
        #writeDataToFile(filename, "Activation")

    while(seconds < 10):
        #print(seconds)
        
        if(motorActivated and seconds == 3):
            writeDataToFile(filename, "Activation")
            break


    timer.cancel()

    readDataToPDframe(filename)



main()