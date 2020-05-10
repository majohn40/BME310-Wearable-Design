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
from kivymd.uix.button import MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.font_definitions import theme_font_styles
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, ListProperty
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem




from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import matplotlib.pyplot as plt

class ItemConfirm(OneLineAvatarIconListItem):
    divider = None

    def set_icon(self, instance_check):
        instance_check.active = True
        check_list = instance_check.get_widgets(instance_check.group)
        for check in check_list:
            if check != instance_check:
                check.active = False

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
	red = NumericProperty()
	green = NumericProperty()
	blue = NumericProperty()
	uv = NumericProperty()
	heat_index = NumericProperty()
	body_temp = NumericProperty()
	heartrate = NumericProperty()
	calories_burned= NumericProperty()
	xs = ListProperty();
	ys = ListProperty()
	heat_index = NumericProperty();
	met_value = 6; 
	start_time = NumericProperty();
	stop = threading.Event()
	dialog = None
	weight = 100;
	#warning_text = StringProperty('')



	def __init__(self, **kwargs):
		super(Dashboard, self).__init__(**kwargs)
		self.step_count = 0
		self.uv= 0
		self.calories_burned = 0;
		self.start_time = time.time()
		#self.warning_text = "Safe to Exercise"

		##Initialize Graph Stuff

		self.fig = plt.figure()
		self.fig.patch.set_facecolor((250/255,250/255,250/255,1))
		self.ax = plt.gca()
		self.ax.set_facecolor((250/255,250/255,250/255,1))
		
		self.xs = []
		self.ys = []

		self.start_serial_thread()

	def show_exercise_dialog(self):
		if not self.dialog:
			self.dialog = MDDialog(
				title="Select Exercise",
                type="confirmation",
                items=[
                    ItemConfirm(text="Running", id="running"),
                ],
                buttons=[
                    MDFlatButton(
                        text="CANCEL"
                    ),
                    MDFlatButton(
                        text="OK"
                    ),
                ],
            )
		self.dialog.open()

	def record_start_time(self):
		self.start = time.time();

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
					self.update_uv(sensors[8])
					self.update_heat_index(temperature_f,float(sensors[3][:3]))
					self.update_graph(self.xs, self.ys, sensors[7])
					self.update_calories(self.met_value, self.start_time, self.weight)


	#Functions to update GUI Values
	@mainthread
	def update_step_count(self, new_val):
		self.step_count = new_val;

	@mainthread 
	def update_temp(self, new_val):
		self.temperature = round(new_val,1);


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
	def update_heat_index(self, new_val):
		self.heat_index = new_val;

	@mainthread
	def update_body_temp(self, new_val):
		self.body_temp = round(15*(float(new_val)/1023) + 92.048, 1);

	@mainthread
	def update_heartrate(self, new_val):
		self.heartrate = new_val;

	@mainthread
	def update_uv(self, new_val):
		voltage = (float(new_val)/1023)
		self.uv = round(0.62*voltage+.1262, 1)

	@mainthread
	def update_heat_index(self, T, RH):
		self.heat_index = round(-42.379 + 2.04901523*T + 10.14333127*RH - .22475541*T*RH - .00683783*T*T - .05481717*RH*RH + .00122874*T*T*RH + .00085282*T*RH*RH - .00000199*T*T*RH*RH,1)

	@mainthread
	def update_calories(self, met, start, weight):
		self.calories_burned = ((time.time()-start)/60)/60 * met*weight;

	@mainthread
	def update_graph(self,xs, ys, new_val):
		xs.append(dt.datetime.now().strftime('%S'))
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
	Window.size = (1200, 700)
	MainApp().run()

