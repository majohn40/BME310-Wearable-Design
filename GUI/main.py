import kivy
kivy.require('1.11.1') # replace with your current kivy version !

import time
import datetime as dt
import threading
import serial

from kivy.factory import Factory
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.font_definitions import theme_font_styles
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, ListProperty
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock, mainthread
from kivy.core.window import Window


from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import matplotlib.pyplot as plt


class MainApp(MDApp):
	def __init__(self, **kwargs):
		self.title = "Heatsleeve"
		super().__init__(**kwargs)

	def on_stop(self):
		self.root.screens[2].stop.set()


	def build(self):
		self.root=Builder.load_file("heatsleeveKivy.kv")

class WelcomeScreen(Screen):
	pass

class LoginScreen(Screen):
	username = StringProperty('')
	def save_username(self):
		self.username= self.ids.username_text_field.text;
		self.manager.current = "Dashboard"
		self.manager.transition.direction = "left"
	pass

class Dashboard(Screen):
	username = StringProperty('')
	step_count = NumericProperty()
	temperature = NumericProperty()
	humidity =  NumericProperty()
	heartrate = 0
	red = NumericProperty()
	green = NumericProperty()
	blue = NumericProperty()
	uv_index = NumericProperty()
	heat_index = NumericProperty()
	body_temp = NumericProperty()
	heartrate = NumericProperty()
	xs = ListProperty();
	ys = ListProperty()

	stop = threading.Event()


	def __init__(self, **kwargs):
		super(Dashboard, self).__init__(**kwargs)
		self.step_count = 0
		self.uv_index = 0
		self.heat_index = 100

		##Initialize Graph Stuff

		self.fig = plt.figure()
		self.fig.patch.set_facecolor((250/255,250/255,250/255,1))
		self.ax = plt.gca()
		self.ax.set_facecolor((250/255,250/255,250/255,1))
		plt.ylabel('Average BPM')
		self.xs = []
		self.ys = []

		self.start_serial_thread()

	def start_serial_thread(self):
		threading.Thread(target=self.serial_thread).start()
		##threading.Thread(target=self.serial_thread, args=(arg1,)).start()
	
	def serial_thread(self):
		##When this thread is initialized, open serial port
		ser = serial.Serial(
		    port='COM4',\
		    baudrate=115200,\
		    parity=serial.PARITY_NONE,\
		    stopbits=serial.STOPBITS_ONE,\
		    bytesize=serial.EIGHTBITS,\
		        timeout=0)

		ser.flushInput()
		ser.flushOutput()

		while True:
			##If GUI is closed, stop this thread so python can exit fully
			if self.stop.is_set():
				return
			##Read Serial Data, checking first if there is data available
			if ser.in_waiting:
				while True:
					try:
						sensor_packet= ser.readline().decode('utf-8')
						break
					except:
						"Invalid character, try again"
				sensors = sensor_packet.split("\t")
				if len(sensors)==10: ##Stop code from exiting if it reads an incomplete packet
					temperature_f = 1.8*float(sensors[2]) + 32
					self.update_temp(round(temperature_f, 2))
					self.update_humidity(sensors[3][:3])
					self.update_red(sensors[4])
					self.update_green(sensors[5])
					self.update_blue(sensors[6])
					self.update_step_count(sensors[7])
					self.update_body_temp(sensors[8])
					self.update_heartrate(sensors[9])
					self.update_graph(self.xs, self.ys, sensors[7])
					time.sleep(0.1)


	#Functions to update GUI Values
	@mainthread
	def update_step_count(self, new_val):
		self.step_count = new_val;

	@mainthread 
	def update_temp(self, new_val):
		self.temperature = new_val;


	@mainthread
	def update_humidity(self, new_val):
		self.humidity = new_val;

	@mainthread
	def update_red (self, new_val):
		self.red = new_val;

	@mainthread
	def update_green (self, new_val):
		self.green = new_val;

	@mainthread
	def update_blue (self, new_val):
		self.blue = new_val;

	@mainthread
	def update_uv_index (self, new_val):
		self.uv_index = new_val;		

	@mainthread
	def update_heat_index(self, new_val):
		self.heat_index = new_val;

	@mainthread
	def update_body_temp(self, new_val):
		self.body_temp = round(15*(float(new_val)/1023) + 92.048, 1);

	@mainthread
	def update_heartrate(self, new_val):
		self.heartrate = new_val;
	
	@mainthread
	def update_graph(self,xs, ys, new_val):
		xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
		ys.append(new_val)
		xs = xs[-20:]
		ys = ys[-20:]
		self.ax.clear()
		self.ax.plot(xs, ys)
		plt.xticks(rotation=45, ha='right')
		plt.subplots_adjust(bottom=0.30)
		plt.draw()

	pass

class MyFigure(FigureCanvasKivyAgg):
    def __init__(self, **kwargs):
        super(MyFigure, self).__init__(plt.gcf(), **kwargs)

class ScreenManager(ScreenManager):
	    pass


if __name__ == "__main__":
	MainApp().run()
