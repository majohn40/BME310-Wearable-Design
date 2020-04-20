import kivy
kivy.require('1.11.1') # replace with your current kivy version !


from kivy.factory import Factory
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.font_definitions import theme_font_styles
from kivy.uix.screenmanager import Screen





class MainApp(MDApp):
	def __init__(self, **kwargs):
		self.title = "Heatsleeve"
		super().__init__(**kwargs)

	def build(self):
		self.root=Builder.load_file("heatsleeveKivy.kv")


class WelcomeScreen(Screen):
	pass

class LoginScreen(Screen):
	pass

class ScreenManager(ScreenManager):
	pass


if __name__ == "__main__":
	MainApp().run()