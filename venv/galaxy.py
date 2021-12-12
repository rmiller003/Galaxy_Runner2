# This is an Advanced Galaxy Runner Desktop Kivy/Python App written in Python 3.9

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty


class MainWidget(Widget):
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    def __init__(self, **kwargs):
        super(MainWidget, self). __init__(**kwargs)
        # print("INIT W:" + str(self.width) + " H:" + str(self.height))

    def on_parent(self, widget, parent):
        # print("ON PARENT W:" + str(self.width) + " H:" + str(self.height))
        pass


class GalaxyApp(App):
    pass



GalaxyApp().run()
