import RPi.GPIO as GPIO

# Pins
PIN_MOTORDETECT = 24



class Dispenser:
    def __init__(self):
        self.irSensorThreshold = 0
        self.dispenserEmpty = False
        self.dispenserRefilled = False
        self.dispenserEmptyTemp = 0
        self.activated = False
        self.numberOfActivations = 0

    def init_GPIO(self):
        # Init GPIO pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN_MOTORDETECT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


    def update(self):

        if not self.activated and GPIO.input(PIN_MOTORDETECT):          
            print("Motor Activated!")
            #count number of times used
            self.numberOfActivations += 1
            print("Activations: ", self.numberOfActivations)
            self.activated = True

        elif self.activated and not GPIO.input(PIN_MOTORDETECT):
            self.activated = False
        
        if(self.dispenserEmpty):
            # If dispenser refilled - button pushed in gui - rest all conditions and turn on system/motor again
            if(self.dispenserRefilled):
                self.dispenserEmptyTemp = 0
                self.dispenserEmpty = False
                self.dispenserRefilled = False
                self.turnOffDispenser = False
             
            
    def cleanup(self):
        GPIO.cleanup()
        print("GPIO cleaned up")

