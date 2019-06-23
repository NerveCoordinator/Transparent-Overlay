import sys

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QPixmap
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QRect

from pynput import mouse

'''
Minimal example of a transparent click through window 
also shows off mouse recording behavior.

make sure compton is running and you've got pyqt5 installed.
'''

# globals are bad but I am unsure if there is a better way to do it here

# keeps track of current mouse position
global x_pos, y_pos
x_pos = 0
y_pos = 0

# this enforces the window only full screening & becoming transparent once
global not_blocked
not_blocked = True        


# move rectangle under mouse
def paint_mouse(x,y):
    global x_pos, y_pos
    x_pos = x
    y_pos = y
    global window    
    #window.func = (window.drawNumber, {"notePoint": QPoint(x, y)})
    window.func = (window.drawRectangles, {"notePoint": QPoint(x, y)})
    window.mModified = True
    window.update()

# this makes sure we can click through the window
def unblock_input():
    global not_blocked
    if not_blocked:
        global window        

        # CLICK THROUGH
        # prevents any input from user whatsoever going to window
        #
        window.setWindowFlags(Qt.WindowTransparentForInput) 
        
        #redraws screen as above flag makes window invisible (todo: why?)
        
        # FULL SCREEN
        window.showFullScreen()   
        not_blocked = False


#pynput example code, fires on associated events

# fires whenever mouse moves
def on_move(x, y):
    print('Pointer moved to {0}'.format(
        (x, y)))
    paint_mouse(x,y)

# fires whenever mouse clicks
def on_click(x, y, button, pressed):
    print('{0} at {1}'.format(
        'Pressed' if pressed else 'Released',
        (x, y)))
    unblock_input()    

# fires whenever mouse scrolls
def on_scroll(x, y, dx, dy):
    print('Scrolled {0} at {1}'.format(
        'down' if dy < 0 else 'up',
        (x, y)))


# defines the window
# qt example code from where? I've changed it a lot.
class Example(QWidget):

    # window object setup
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("overlay")
        self.mModified = True
        self.mPixmap = QPixmap()
        self.func = (None, None)

    # repaints buffer
    def paintEvent(self, event):
        # if anything has changed
        if self.mModified:
            pixmap = QPixmap(self.size())
            # set buffer to 'black' but transparent
            c = QColor(0)            
            c.setAlpha(0)       
            pixmap.fill(c)            
            painter = QPainter(pixmap)        
            self.mPixmap.fill(c)
            painter.drawPixmap(0, 0, self.mPixmap)
            self.drawBackground(painter)
            self.mPixmap = pixmap
            self.mModified = False

        # redraw buffer with buffer data
        qp = QPainter(self)
        qp.drawPixmap(0, 0, self.mPixmap)
        
    # ?
    def drawBackground(self, qp):
        func, kwargs = self.func
        if func is not None:
            kwargs["qp"] = qp
            func(**kwargs)

    # draws rectangles in buffer
    def drawRectangles(self, qp, notePoint):
        col = QColor(0, 0, 0)
        col.setNamedColor('#d4d4d4')
        qp.setPen(col)

        qp.setBrush(QColor(200, 0, 0))
        qp.drawRect(x_pos, y_pos, 90, 60)

        qp.setBrush(QColor(25, 25, 200, 150))
        qp.drawRect(250, 15, 90, 60)
        

# associates listener object to its asyncronous functions
listener = mouse.Listener(
    on_move=on_move,
    on_click=on_click,
    on_scroll=on_scroll)
listener.start()


# on start of program
if __name__ == '__main__':

    # it is a qt app
    app = QApplication(sys.argv)

    # globals are bad
    global window
    window = Example()  
      
    # TRANSPARENT WINDOW
    #need compositor like compton for transparancy to work
    window.setAttribute(Qt.WA_TranslucentBackground, True) 

    # FULLSCREEN
    window.showFullScreen()    

    # Start program
    sys.exit(app.exec_())