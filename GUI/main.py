import kivy
kivy.require('1.11.1') # replace with your current kivy version !

import time
import threading
import serial

from kivy.factory import Factory
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.font_definitions import theme_font_styles
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock, mainthread



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
	step_count_text = StringProperty()
	step_count = NumericProperty()
	temperature = NumericProperty()
	heartrate = 70;

	stop = threading.Event()

	def __init__(self, **kwargs):
		super(Dashboard, self).__init__(**kwargs)
		self.step_count = 0
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
				sensor_packet= ser.readline().decode('utf-8')
				sensors = sensor_packet.split("\t")
				if len(sensors)==7: ##Stop code from exiting if it reads an incomplete packet
					temperature_f = 1.8*float(sensors[2]) + 32
					self.update_temp(temperature_f)
					self.update_step_count(sensors[0])

			time.sleep(1)

	@mainthread
	def update_step_count(self, new_val):
		self.step_count = new_val;
		self.step_count_text = str(self.step_count);

	pass

	@mainthread 
	def update_temp(self, new_val):
		self.temperature = new_val;

	pass


class ScreenManager(ScreenManager):
	pass


if __name__ == "__main__":
	MainApp().run()
