import sys, os
import threading
from PyQt4.QtGui import *
from time import sleep
# sys.path.append(os.getcwd() + '\..\CAN')
sys.path.append(sys.path[0] + '\..\CAN')
import can_handler


class GUI_CAN_Manager(QWidget):

    def __init__(self):
        self.node_id_selected = 1
        super(GUI_CAN_Manager, self).__init__()
        self.initUI()
        self.can_h = can_handler.can_handler()
        self.can_h.configure('CANOpen')
        self.can_h.send_msg([0x01, 0x00], 0x00)  # to operational
#         self.can_h.send_msg((0x2f, 0x02, 0x21, 0x01, 0x01, 0x00, 0x00, 0x00), 0x601)
#         self.can_h.send_msg((0x2f, 0x02, 0x21, 0x01, 0x01, 0x00, 0x00, 0x00), 0x602)
        self.run_loop()

    def closeEvent(self, event):
        self.th_periodic.cancel()
        sleep(0.5)
        event.accept() # let the window close


    def initUI(self):
        # 1 enable
        btn1_enable = QPushButton('Configure ID', self)
        btn1_enable.clicked.connect(lambda: self.configure_id())
        btn1_enable.resize(btn1_enable.sizeHint())
        btn1_enable.move(125, 25)

        # Ratio buttons
        self.b1 = QRadioButton("Node ID 1", self)
        self.b1.setChecked(True)
        self.b1.toggled.connect(lambda: self.radio_btn_state(self.b1))
        self.b1.resize(self.b1.sizeHint())
        self.b1.move(25, 25)

        self.b2 = QRadioButton("Node ID 2", self)
        self.b2.setChecked(False)
        self.b2.toggled.connect(lambda: self.radio_btn_state(self.b2))
        self.b2.resize(self.b2.sizeHint())
        self.b2.move(25, 50)

        self.setGeometry(300, 300, 250, 100)
        self.setWindowTitle('Great Plains Manager')
        self.show()

    def configure_id(self):
        '''    SECUENCIA CAMBIO DE NODE ID    '''
        self.th_periodic.cancel()
        # si quiero configurar a id1 supongo que estaba en 2
        if self.node_id_selected == 1:
            i = 2
        else:
            i = 1

        self.can_h.send_msg((0x2f, 0x00, 0x20, 0x00, self.node_id_selected, 0x00, 0x00, 0), 0x600+i)
        self.can_h.send_msg((0x23, 0x10, 0x10, 0x01, 0x73, 0x61, 0x76, 0x65), 0x600+i)
        sleep(1)
        self.can_h.send_msg((0x80, 0x10, 0x10, 0x01, 0x00, 0x00, 0x04, 0x05), 0x600+i)
        sleep(0.5)
        self.can_h.send_msg([0x81, i], 0x00)  # reset

        sleep(1)
        self.run_loop()

    def radio_btn_state(self, b):
        if b.text() == "Node ID 1":
            if b.isChecked() == True:
                self.node_id_selected = 1
        if b.text() == "Node ID 2":
            if b.isChecked() == True:
                self.node_id_selected = 2

    def run_loop(self):
        msg_clear_error = (0x2f, 0x02, 0x21, 0x01, 0x01, 0x00, 0x00, 0x00)
        msg_mode_speed = (0x2f, 0x03, 0x21, 0x00, 0x02, 0x00, 0x00, 0x00) # speed mode
#         msg_set_speed = (0x23, 0x01, 0x22, 0x00, 0x1a, 0x4f, 0x00, 0x00) # 1a4f = 25rpm
        msg_set_speed = (0x23, 0x01, 0x22, 0x00, 0xd8, 0xbd, 0x00, 0x00) # 60rpm
#         msg_break_on = (0x2f, 0x04, 0x21, 0x00, 0x00, 0x00, 0x00, 0x00) # deprecated
        msg_set_heartbeat = (0x23, 0x16, 0x10, 0x01, 0xdc, 0x05, 0x64, 0x00)

        write_buffer = (msg_mode_speed, msg_set_speed, msg_set_heartbeat, msg_clear_error)

        node_id = self.node_id_selected
        node_id_c = 0x600 + node_id
        '''actions'''
        try:
            # detener el otro nodo
            if node_id == 1:
                self.can_h.send_msg((0x23, 0x01, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00), 0x602) # speed 0
    #             for msg in write_buffer:
    #                 self.can_h.send_msg(msg, node_id_c)
            else:
                self.can_h.send_msg((0x23, 0x01, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00), 0x601) # speed 0
    #         self.can_h.send_msg([0x01, 0x00], 0x00)  # to operational
            for msg in write_buffer:
                self.can_h.send_msg(msg, node_id_c)
            sleep(0.020)
            self.can_h.send_msg([0x05], 0x764) # operational

            self.th_periodic = threading.Timer(1, self.run_loop)
            self.th_periodic.start()
        except:
            self.th_periodic.cancel()
            self.th_periodic = threading.Timer(1, self.run_loop)
            self.th_periodic.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GUI_CAN_Manager()

    sys.exit(app.exec_())
