import time
from threading import Thread

from connection import Connection
from userdialog import UserDialog
from whiteboard import WhiteBoard


class Client(Thread,WhiteBoard):
    Objects = {'line': 'L', 'oval': 'O', 'circle': 'C', 'rectangle': 'R', 'square': 'S', 'erase': 'E', 'drag': 'DR'}

    def __init__(self):
        self.conn = Connection()
        Thread.__init__(self)
        WhiteBoard.__init__(self)
        self._init_mouse_event()
        self.setDaemon(True)
        self.isMouseDown = False
        self.x_pos = None
        self.y_pos = None
        self.last_time = None

        self.x1_line, self.y1_line, self.x2_line, self.y2_line = None, None, None, None


    def _init_mouse_event(self):
        self.drawing_area.bind("<Motion>", self.motion)
        self.drawing_area.bind("<ButtonPress-1>", self.left_but_down)
        self.drawing_area.bind("<ButtonRelease-1>", self.left_but_up)

    #(tpye，startx,starty,endx,endy,color)
    #('D',startx,starty,endx,endy,'red')
    def left_but_down(self, event=None):
        self.isMouseDown = True
        self.x_pos = event.x
        self.y_pos = event.y

        self.x1_line,self.y1_line = event.x ,event.y

        self.last_time = time.time()


    def left_but_up(self,event=None):
        self.isMouseDown = False
        print(event.x,event.y)
        self.last_time=None

        self.x2_line , self.y2_line = event.x , event.y
        self.draw_one_obj()
        if self.drawing_tool == 'text':
            self.draw_text()
        else:
            self.draw_one_obj()

    def draw_text(self):
        text_to_draw = UserDialog._Text
        msg = ('T', self.x1_line, self.y1_line, 'red', text_to_draw)
        self.conn.send_message(msg)

    def draw_one_obj(self):
        tool = self.drawing_tool
        if tool not in Client.Objects.keys():
            return
        else:
            cmd_type = Client.Objects[tool]
            msg = (cmd_type, self.x1_line, self.y1_line, self.x2_line, self.y2_line, 'red')
            self.conn.send_message(msg)

    # (tpye，startx,starty,endx,endy,color)
    # ('D',startx,starty,endx,endy,'red')
    def motion(self,event=None):
        if self.isMouseDown == True and self.drawing_tool == 'pencil':
            now = time.time()
            if now - self.last_time < 0.02:
                print('too fast')
                return
            self.last_time = now

            msg = ('D', self.x_pos, self.y_pos, event.x, event.y, 'red')
            self.conn.send_message(msg)
            self.x_pos = event.x
            self.y_pos = event.y


    def run(self):
        # print('run')aa
        while True:
            msg = self.conn.receive_msg()
            self.draw_from_msg(msg)
            # print(msg)
            if msg == 'xxx':
                pass
            # print('i am running')
            # time.sleep(0.1)

if __name__ == '__main__':
    client = Client()
    print('startt')
    client.start()
    client.show_window()




