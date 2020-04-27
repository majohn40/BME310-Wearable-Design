import kivy
kivy.require('1.11.1') # replace with your current kivy version !

import time
import threading

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
	test_count = StringProperty()
	count = NumericProperty()
	temperature = 60;
	heartrate = 70;

	stop = threading.Event()
	def __init__(self, **kwargs):
		super(Dashboard, self).__init__(**kwargs)
		self.test_count = "test1"
		self.count = 0

	def start_serial_thread(self):
		threading.Thread(target=self.serial_thread).start()
		print("New thread")
	
	def serial_thread(self, count):

		if self.stop.is_set():
			return

	@mainthread
	def get_count(self, count):
		self.count = count+1;
		self.test_count = str(self.count);

	pass


class ScreenManager(ScreenManager):
	pass


if __name__ == "__main__":
	MainApp().run()
