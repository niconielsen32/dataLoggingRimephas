import RPi.GPIO as GPIO

#global variables
#numberOfActivations = 0
# Pins
PIN_MOTORDETECT = 4
PIN_IRSENOR = 20
#PIN_LED = 25
PIN_PIR = 17
#PIN_LEFT_IR = 
#PIN_RIGHT_IR = 




class Dispenser:
    def __init__(self):
        self.irSensorThreshold = 0
        self.dispenserEmpty = False
        self.turnOffDispenser = False
        self.dispenserRefilled = False
        self.dispenserEmptyTemp = 0
        self.activated = False
        self.numberOfActivations = 0
        self.numberOfPeople = 0
        self.leftIR = False
        self.rightIR = False

    def init_GPIO(self):
        # Init GPIO pins
        GPIO.setmode(GPIO.BCM)
        #GPIO.setup(PIN_LED, GPIO.OUT)
        #GPIO.output(PIN_LED, False)
        GPIO.setup(PIN_MOTORDETECT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        GPIO.setup(PIN_PIR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    def readPIR(self):
        if GPIO.input(PIN_PIR):
            #print("PIR activated")
            #self.numberOfPeople += 1
            return True
        else:
            #print("NONE")
            return False

    # Read SPI data from ADC  
    def recvBits(self, numBits, clkPin, misoPin):
        retVal = 0   
        for bit in range(numBits):
            # Pulse clock pin 
            GPIO.output(clkPin, GPIO.HIGH)
            GPIO.output(clkPin, GPIO.LOW)       
            # Read 1 data bit in
            if GPIO.input(misoPin):
                retVal |= 0x1        
            # Advance input to next bit
            retVal <<= 1   
        # Divide by two to drop the NULL bit
        return (retVal/2)

    def readAdc(self, channel, clkPin, misoPin, mosiPin, csPin):
        if (channel < 0) or (channel > 7):
            print("Invalid ADC Channel number, must be between [0,7]")
            return -1        
        # Datasheet says chip select must be pulled high between conversions
        GPIO.output(csPin, GPIO.HIGH)
        
        # Start the read with both clock and chip select low
        GPIO.output(csPin, GPIO.LOW)
        GPIO.output(clkPin, GPIO.HIGH)
        
        adc = self.recvBits(10, clkPin, misoPin)    
        # Set chip select high to end the read
        GPIO.output(csPin, GPIO.HIGH)  
        return round(adc)

    def update(self):
        #global numberOfActivations, irSensorThreshhold, dispenserEmpty, turnOffDispenser, dispenserRefilled, dispenserEmptyTemp, activated
        #ADCvalue = self.readAdc(0, PIN_CLK, PIN_MISO, PIN_MOSI, PIN_CS)
        if not self.turnOffDispenser and not self.activated and GPIO.input(PIN_MOTORDETECT):          
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
        """     
        # Test MOSFET
        if(self.turnOffDispenser == False):
            GPIO.output(PIN_LED, True)
        else:
            GPIO.output(PIN_LED, False)
        """
    def dispenser_callback(self, channel):
        #print("callback activation")
        self.numberOfActivations += 1
        
    def pir_callback(self, channel):
        #print("callback pir")
        self.numberOfPeople += 1
        
        
    def right_callback(self, channel):
        self.rightIR = True
        
    def left_callback(self, channel):
        self.leftIR = True

    def gelUpdate(self):
        GPIO.add_event_detect(PIN_MOTORDETECT, GPIO.RISING, callback=self.dispenser_callback, bouncetime=2000)
        GPIO.add_event_detect(PIN_PIR, GPIO.RISING, callback=self.pir_callback, bouncetime=2000)
    """    
    def getRightIR:
        GPIO.add_event_detect(PIN_RIGHT_IR, GPIO.RISING, callback=self.right_callback, bouncetime=2000)
        
    def getLeftIR:
        GPIO.add_event_detect(PIN_LEFT_IR, GPIO.RISING, callback=self.left_callback, bouncetime=2000)
    """    