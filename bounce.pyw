from time import time
from random import choice
import sys, os
import math
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QKeyEvent, QPainter,QImage, QPen, QIcon, QPixmap, QColor, QBrush, QCursor, QFont, QPalette
from PyQt5.QtCore import Qt, QPoint, QPointF, QSize, QEvent, QTimer, QCoreApplication

from random import choice

class Ball():
    def __init__(self):

        self.bx = 0
        self.by = 0
        self.bw = 0
        self.bh = 0

        self.bst = 0
        self.bs = 0
        self.bxt = 0
        self.byt = 0

        self.line_max = 0
        self.angle = 0
        self.random_angle = False

    def init(self):

        self.line_coords = [(self.bx,self.by),(self.bx,self.by)]
        self.line_index = 1

        self.bst = 50 / 1000 # 50 milliseconds
        # self.bs = 14 # move 14 pixels per time unit

        self.pi = math.pi
        self.conv = self.pi / 180
        
        self.trajectory()

        if self.line_max == 0:
            self.line_index = 0
            del self.line_coords[-1]

    def trajectory(self):
        self.bxt = math.cos(self.angle)
        self.byt = math.sin(self.angle)

    def update(self, dt, w, h):

        self.trajectory()

        self.bx += dt * (self.bs / self.bst) * self.bxt
        self.by += dt * (self.bs / self.bst) * self.byt
        
        ycollision = False
        xcollision = False

        # right side of screen
        if self.bx  + self.bw/2 > w:
            self.bx = w - self.bw/2
            xcollision = True
        # left side
        elif self.bx - self.bw/2 < 0:
            self.bx = 0 + self.bw/2
            xcollision = True

        # bottom
        if self.by + self.bh/2 > h:
            self.by = h - self.bh/2
            ycollision = True
        # top
        elif self.by - self.bh/2 < 0:
            self.by = 0 + self.bh/2
            ycollision = True
        
        self.line_coords[self.line_index] = (self.bx, self.by)

        if xcollision:
            self.angle = (self.pi - self.angle)
        if ycollision:
            self.angle = (self.pi * 2 - self.angle)

        if xcollision or ycollision:
            if self.line_index != self.line_max:
                self.line_index += 1
            else:
                del self.line_coords[0]
            self.line_coords.append((self.bx, self.by))
    
        if self.random_angle:
            self.angle = choice(range(360)) * self.conv



class Bounce(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        # self.pid = os.getpid()
        # self.root = os.path.dirname(os.path.abspath(__file__))  + "\\"

        self.setWindowTitle("Bounce")

        self.w = 400
        self.h = 400
        self.w_def = self.w * 1
        self.h_def = self.h * 1

        self.midx = self.w / 2
        self.midy = self.h / 2

        self.pi = math.pi
        self.conv = self.pi / 180

        self.have_control = False
        self.num_balls = 0

        # universal ball speed
        self.bs = 14 # move 14 pixels per time unit 

        self.balls = []

        # inputs
        # --------------------------------------
        self.draw_balls = True
        self.draw_lines = False
        self.random_angle = False
        self.line_max = 10
        start_balls = 1
        self.speed_control = 2
        # --------------------------------------

        self.create_balls(start_balls)

        self.setGeometry(300, 300, self.w, self.h)
        self.center()

        self.installEventFilter(self)

        self.timer = QTimer()
        self.timer.timeout.connect(self.updater)
        self.timer.start(15) # 25 milliseconds

        self.t0 = time()


    def give_control(self):
        self.control = Control()
        self.control.show()
        self.have_control = True

    def destroy_balls(self, num):
        # num is number to destroy
        for i in range(num):
            try:
                del self.balls[i]
            except:
                pass
        self.num_balls = len(self.balls)


    def create_balls(self, num):
        # num is number to create
        for _ in range(num):
            balli = self.create_ball()
            self.balls.append(balli)
        self.num_balls = len(self.balls)

    def create_ball(self):
        balli = Ball()
        balli.bx = self.midx + 0
        balli.by = self.midy + 0
        balli.bw = 20
        balli.bh = 20
        balli.bs = self.bs + 0
        balli.line_max = self.line_max
        balli.angle = choice(range(360)) * self.conv
        balli.random_angle = self.random_angle
        balli.init()
        return balli

    def set_bs(self):
        for i in range(len(self.balls)):
            self.balls[i].bs = self.bs

    def set_lm(self):
        for i in range(len(self.balls)):
            self.balls[i].line_max = self.line_max

    def set_random(self):
        for i in range(len(self.balls)):
            self.balls[i].random_angle = self.random_angle

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.eraseRect(0,0,self.w,self.h)
        painter.setRenderHint(QPainter.Antialiasing,True)

        pen = QPen()
        pen.setWidth(1)
        pen.setColor(Qt.black)
        painter.setPen(pen)
        painter.setBrush(Qt.black)
        for i in range(len(self.balls)):
            balli = self.balls[i]
            if self.draw_balls:
                painter.drawEllipse(balli.bx - balli.bw/2,balli.by - balli.bh/2, balli.bw, balli.bh)

            if self.draw_lines:
                for j in range(1,len(balli.line_coords)):
                    painter.drawLine(balli.line_coords[j-1][0], balli.line_coords[j-1][1], balli.line_coords[j][0], balli.line_coords[j][1])

    
    
    def updater(self):

        dt = time() - self.t0

        self.t0 = time()

        for i in range(len(self.balls)):
            self.balls[i].update(dt, self.w, self.h)

        self.repaint()



    def resizeEvent(self, event):
        qr = self.geometry()
        self.w = qr.width()
        self.h = qr.height()
        self.midx = self.w / 2
        self.midy = self.h / 2



    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    
    def custom_close(self):
        QCoreApplication.instance().quit()

    def mousePressEvent(self, QMouseEvent):
        pos = QMouseEvent.pos()
        new_ball = self.create_ball()
        new_ball.bx = pos.x()
        new_ball.by = pos.y()
        new_ball.init()
        self.balls.append(new_ball)
        self.num_balls += 1


    def eventFilter(self,source,event):

        if event.type() == QEvent.KeyPress:
            
            modifiers = QApplication.keyboardModifiers()

            if modifiers == Qt.ControlModifier and event.key() == Qt.Key_C:
                if not self.have_control:
                    self.control = Control()
                    self.control.show()
                    self.have_control = True


            if event.key() == Qt.Key_Right:
                self.bs += self.speed_control
                self.set_bs()

            elif event.key() == Qt.Key_Left:
                self.bs -= self.speed_control
                self.set_bs()


        return 0

    def closeEvent(self, event):
        self.custom_close()














class Control(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()        
        
    def initUI(self):

        self.gui = gui

        self.setWindowTitle('Control')


        self.lbl1 = QLabel('Number of balls:', self)
        self.sld_num = QSlider(Qt.Horizontal, self)
        self.sld_num.setMinimum(0)
        self.sld_num.setMaximum(1000)
        self.sld_num.setMaximumWidth(100)
        self.sld_num.valueChanged.connect(self.change_num_balls)
        self.sld_num.setValue(self.gui.num_balls)

        self.lbl1_2 = QLabel(str(self.gui.num_balls), self)
        self.lbl2_2 = QLabel(str(self.gui.bs), self)
        self.lbl3_2 = QLabel(str(self.gui.line_max), self)

        self.lbl2 = QLabel('Speed:', self)
        self.sld_speed = QSlider(Qt.Horizontal, self)
        self.sld_speed.setMinimum(-250)
        self.sld_speed.setMaximum(250)
        self.sld_speed.setMaximumWidth(100)
        self.sld_speed.valueChanged.connect(self.change_speed)
        self.sld_speed.setValue(self.gui.bs)

        self.draw_balls = QCheckBox("Draw Balls",self)
        self.draw_balls.setChecked(self.gui.draw_balls)
        self.draw_balls.installEventFilter(self)

        self.draw_lines = QCheckBox("Draw Lines",self)
        self.draw_lines.setChecked(self.gui.draw_lines)
        self.draw_lines.installEventFilter(self)

        self.random = QCheckBox("Random",self)
        self.random.setChecked(self.gui.random_angle)
        self.random.installEventFilter(self)

        self.lbl3 = QLabel('Line Max:', self)
        self.sld_lm = QSlider(Qt.Horizontal, self)
        self.sld_lm.setMinimum(1)
        self.sld_lm.setMaximum(1000)
        self.sld_lm.setMaximumWidth(100)
        self.sld_lm.valueChanged.connect(self.change_lm)
        self.sld_lm.setValue(self.gui.line_max)

        self.reset_btn = QPushButton('Reset', self)
        self.reset_btn.clicked.connect(self.reset)
        self.reset_btn.resize(self.reset_btn.sizeHint())

        self.submit_btn = QPushButton('Submit', self)
        self.submit_btn.clicked.connect(self.submit)
        self.submit_btn.resize(self.submit_btn.sizeHint())

        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        cspan = 1
        row = 0

        self.grid.addWidget(self.lbl1, row, 0, 1, 1)
        self.grid.addWidget(self.sld_num, row, 1, 1, cspan)
        self.grid.addWidget(self.lbl1_2, row, cspan + 1, 1, 1)

        row += 1
        self.grid.addWidget(self.lbl2, row, 0, 1, 1)
        self.grid.addWidget(self.sld_speed, row, 1, 1, cspan)
        self.grid.addWidget(self.lbl2_2, row, cspan + 1, 1, 1)

        row += 1
        self.grid.addWidget(self.lbl3, row, 0, 1, 1)
        self.grid.addWidget(self.sld_lm, row, 1, 1, cspan)
        self.grid.addWidget(self.lbl3_2, row, cspan + 1, 1, 1)

        row += 1
        self.grid.addWidget(self.draw_balls, row, 0, 1, 1)
        self.grid.addWidget(self.draw_lines, row, 1, 1, cspan)
        self.grid.addWidget(self.random, row, cspan + 1, 1, 1)

        row += 1
        self.grid.addWidget(self.reset_btn, row, 0, 1, 1)
        self.grid.addWidget(self.submit_btn, row, 1, 1, 1)


        self.setLayout(self.grid)
        self.setGeometry(300, 300, 300, 200)
        self.show()


    def refresh(self):
        self.sld_num.setValue(self.gui.num_balls)
        self.sld_speed.setValue(self.gui.bs)
        self.draw_balls.setChecked(self.gui.draw_balls)
        self.draw_lines.setChecked(self.gui.draw_lines)
        self.sld_lm.setValue(self.gui.line_max)

        self.lbl1_2.setText(str(self.gui.num_balls))
        self.lbl2_2.setText(str(self.gui.bs))
        self.lbl3_2.setText(str(self.gui.line_max))


    def change_num_balls(self):
        new_num = self.sld_num.value()

        if new_num == self.gui.num_balls:
            return
        elif new_num < self.gui.num_balls:
            self.gui.destroy_balls(self.gui.num_balls - new_num)
            self.gui.destroy_balls(self.gui.num_balls - new_num)
            self.gui.destroy_balls(self.gui.num_balls - new_num)
            self.gui.destroy_balls(self.gui.num_balls - new_num)
        else:
            self.gui.create_balls(new_num - self.gui.num_balls)

        self.lbl1_2.setText(str(self.gui.num_balls))



    def change_speed(self):
        self.gui.bs = self.sld_speed.value()
        self.gui.set_bs()

        self.lbl2_2.setText(str(self.gui.bs))


    def change_lm(self):
        new_num = self.sld_lm.value()

        if len(self.gui.balls) == 0:
            self.gui.line_max = new_num
            self.gui.set_lm()
            return

        if new_num == self.gui.line_max:
            return
        elif new_num > self.gui.line_max or new_num > len(self.gui.balls[0].line_coords):
            self.gui.line_max = new_num
            self.gui.set_lm()
        else:
            for i in range(len(self.gui.balls)):
                # print(new_num)
                # print(len(self.gui.balls[0].line_coords),self.gui.balls[i].line_index,len(self.gui.balls[i].line_coords[:new_num]), new_num-1  )
                self.gui.balls[i].line_coords = self.gui.balls[i].line_coords[:new_num]
                self.gui.balls[i].line_index = new_num-1

            self.gui.line_max = new_num
            self.gui.set_lm()

        self.lbl3_2.setText(str(self.gui.line_max))
    
    def reset(self):
        num_balls = self.gui.num_balls
        # self.gui.destroy_balls(num_balls)
        self.gui.balls = []
        self.gui.create_balls(num_balls)
        self.submit()

    def submit(self):
        self.gui.draw_balls = self.draw_balls.isChecked()
        self.gui.draw_lines = self.draw_lines.isChecked()
        self.change_num_balls()
        self.change_speed()

    def closeEvent(self, event):
        self.gui.have_control = False

    def eventFilter(self, source, event):
        if source is self.draw_balls:
            self.gui.draw_balls = self.draw_balls.isChecked()
        elif source is self.draw_lines:
            self.gui.draw_lines = self.draw_lines.isChecked()
        elif source is self.random:
            self.gui.random_angle = self.random.isChecked()
            self.gui.set_random()

        self.refresh()

        return 0

            
if __name__ == '__main__':

    # import ctypes
    # ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("bounce_gui_ctypes_thing")

    app = QApplication(sys.argv)
    QApplication.setQuitOnLastWindowClosed(False)
    gui = Bounce()
    gui.show()
    gui.give_control()
    app.exec_()

