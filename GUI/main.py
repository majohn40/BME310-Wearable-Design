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
from kivy.properties import ObjectProperty, StringProperty	
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock, mainthread
from kivy.logger import Logger



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
	temperature = 60;
	heartrate = 70;
	count = 0;

	stop = threading.Event()
	def start_serial_thread(self):
		threading.Thread(target=self.serial_thread).start()
		print("New thread")
	
	def serial_thread(self):
		time.sleep(1000);
		if counter <5:
			counter += 1
			self.get_count(counter)

		if self.stop.is_set():
			Logger.critical("Serial Thread Exiting".format(thing))
			return

	@mainthread
	def get_count(self, count):
		self.count = counter



	pass


class ScreenManager(ScreenManager):
	pass


if __name__ == "__main__":
	MainApp().run()
