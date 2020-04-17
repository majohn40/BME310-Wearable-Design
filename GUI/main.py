import kivy
kivy.require('1.11.1') # replace with your current kivy version !

from kivy.uix.screenmanager import Screen

from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.font_definitions import theme_font_styles




class MainApp(MDApp):
    def build(self):
        screen = Screen()
        screen.add_widget(
        	MDLabel(
                    text="Welcome to Heatsleeve",
                    halign="center",
                    font_style="H1"
                )
        	)
        screen.add_widget(
            MDRectangleFlatButton(
                text="Get Started",
                pos_hint={"center_x": 0.5, "center_y": 0.2},
            )
        )
        return screen


MainApp().run()