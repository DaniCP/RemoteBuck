import sys
from PyQt4 import QtGui
import RPi.GPIO as GPIO

class GPIO_Manager(QtGui.QWidget):

    pin1 = False
    pin2 = False
    pin3 = False

    def __init__(self):
        super(GPIO_Manager, self).__init__()        
        self.configureGPIO()
        self.initUI()

    def configureGPIO(self):
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(23, GPIO.OUT)
	#GPIO.setup(25, GPIO.OUT)
	#GPIO.setup(37, GPIO.OUT)

    def updateGPIO(self):
	if self.pin1 is True:
	    GPIO.output(23, GPIO.HIGH)
	if self.pin1 is False:
	    GPIO.output(23, GPIO.LOW)

    def enableGPIO(self, pin=0, action=False):
        #este es el slot, aqui puedo llamar al socket si se hace aplicacion web
        #inputs: pin is the GPIO number    action is True to enable, False to disable
        if pin == 1:
            self.pin1 = action
        if pin == 2:
            self.pin2 = action
        if pin == 3:
            self.pin3 = action

        print 'pin1:', self.pin1, 'pin2:', self.pin2, 'pin3:', self.pin3
        self.updateGPIO()

    def initUI(self):

        label_23 = QtGui.QLabel(self)
        label_23.move(50, 10)
        #1 enable
        btn1_enable = QtGui.QPushButton('Enable', self)
        btn1_enable.clicked.connect(lambda: self.enableGPIO(1, True))
        btn1_enable.resize(btn1_enable.sizeHint())
        btn1_enable.move(50, 50)
        #1 disable
        btn1_disable = QtGui.QPushButton('Disable', self)
        btn1_disable.clicked.connect(lambda: self.enableGPIO(1, False))
        btn1_disable.resize(btn1_disable.sizeHint())
        btn1_disable.move(150, 50)

        #2 enable
        btn2_enable = QtGui.QPushButton('Enable', self)
        btn2_enable.clicked.connect(lambda: self.enableGPIO(2, True))
        btn2_enable.resize(btn1_enable.sizeHint())
        btn2_enable.move(50, 100)
        #2 disable
        btn2_disable = QtGui.QPushButton('Disable', self)
        btn2_disable.clicked.connect(lambda: self.enableGPIO(2, False))
        btn2_disable.resize(btn1_disable.sizeHint())
        btn2_disable.move(150, 100)
        
        #3 enable
        btn3_enable = QtGui.QPushButton('Enable', self)
        btn3_enable.clicked.connect(lambda: self.enableGPIO(3, True))
        btn3_enable.resize(btn1_enable.sizeHint())
        btn3_enable.move(50, 150)
        #3 disable
        btn3_disable = QtGui.QPushButton('Disable', self)
        btn3_disable.clicked.connect(lambda: self.enableGPIO(3, False))
        btn3_disable.resize(btn1_disable.sizeHint())
        btn3_disable.move(150, 150)

        self.setGeometry(300, 300, 350, 200)
        self.setWindowTitle('GPIO Manager')
        self.show()


def main():

    app = QtGui.QApplication(sys.argv)
    ex = GPIO_Manager()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

