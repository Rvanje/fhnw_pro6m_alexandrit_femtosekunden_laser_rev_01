# Std. lib imports
import os
import time
import threading
from queue import Queue

# Third party imports, yet std. libraries
import numpy as np
import pandas as pd
import customtkinter

# Third party special imports, absolut no std. libraries
import tec_control as tec_ctrl
import ldd_control_ang as ldd_ctrl

# Raspberry PI specific libraries
from gpiozero import CPUTemperature

# Colour schemes of the application's GUI
customtkinter.set_appearance_mode("dark")
customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("blue")


class GUI(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        # Window settings
        self.title("Laser Configuration Utility")  # Main window title
        self.geometry("800x480")  # Main window size
        # self.overrideredirect(True)  # Enter fullscreen (no escape)
        
        # Initailisation of the queue
        self.queue_cr_av = Queue()
        self.queue_cr_sp = Queue()
        self.queue_di_av = Queue()
        self.queue_di_sp = Queue()
        self.queue_ldd_av = Queue()
        self.queue_ldd_sp = Queue()

        # Initialisation of the TEC-controller communication
        self.mt_1 = tec_ctrl.MeerstetterTEC(channel=1)
        self.mt_2 = tec_ctrl.MeerstetterTEC(channel=2)

        #Initialisation of the ldd driver
        self.ldd = ldd_ctrl.ldd_control()

        # Initialisation of the av and sp variables
        self.mt1_ot = self.mt_1.get_data()["object temperature"][0]
        self.mt2_ot = self.mt_2.get_data()["object temperature"][0]
        self.mt1_tot = self.mt_1.get_data()["target object temperature"][0]
        self.mt2_tot = self.mt_2.get_data()["target object temperature"][0]
        self.lst_mean_temp_cr: list = []
        self.lst_mean_temp_di: list = []
        self.array_cr_av = np.array([[0, 0]], dtype=np.float64)
        self.array_cr_sp = np.array([[0, 0]], dtype=np.float64)
        self.array_di_av = np.array([[0, 0]], dtype=np.float64)
        self.array_di_sp = np.array([[0, 0]], dtype=np.float64)
        self.array_ldd_av = np.array([[0, 0]], dtype=np.float64)
        self.array_ldd_sp = np.array([[0, 0]], dtype=np.float64)

        # Create empty dictionaries to create and export AuditTrail of
        # change the set points and actual values of the pump diode
        # and the crystal TECs, respectively.
        self.dict_historian_cr_av = {}
        self.dict_audittrail_cr_sp = {}
        self.dict_historian_di_av = {}
        self.dict_audittrail_di_sp = {}
        self.dict_historian_ldd_av = {}
        self.dict_audittrail_ldd_sp = {}

        # Definie the "tab" configuration, pages of the GUI
        signin, overview, settings = "Sign In", "Overview", "Settings"
        self.tabview = customtkinter.CTkTabview(
            self,
            width=800,
            height=480,
            # border_width=40
        )

        self.tabview.grid(
            column=1,
        )

        # self.tabview.add(signin)
        self.tabview.add(overview)
        self.tabview.add(settings)
        
        # Characteristics of the tabs
        self.tabview.tab(overview).grid_columnconfigure(
            (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
            weight=1
        )

        self.tabview.tab(overview).grid_rowconfigure(
            (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
            weight=1
        )
        self.tabview.tab(settings).grid_columnconfigure(
            (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
            weight=1
        )

        self.tabview.tab(settings).grid_rowconfigure(
            (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
            weight=1
        )

        # Design "Overview" tab
        self.frame_temp_crystal = customtkinter.CTkFrame(
            self.tabview.tab(overview),
            width=350,
            height=40,
            fg_color="grey80",
            corner_radius=5
        )

        self.frame_temp_crystal.grid(
            row=1,
            column=1,
            padx=0,
            pady=0,
            sticky="nsew",
        )

        self.frame_temp_crystal.grid_rowconfigure(4, weight=1)

        self.frame_temp_diode = customtkinter.CTkFrame(
            self.tabview.tab(overview),
            width=350,
            height=40,
            fg_color="grey80",
            corner_radius=5,
        )
        self.frame_temp_diode.grid(
            row=4,
            column=1,
            padx=0,
            pady=0,
            sticky="nsew",
            rowspan=2
        )
        self.frame_temp_diode.grid_rowconfigure(4, weight=1)

        self.frame_ldd = customtkinter.CTkFrame(
            self.tabview.tab(overview),
            width=350,
            height=40,
            fg_color="grey80",
            corner_radius=5,
        )

        self.frame_ldd.grid(
            row=1,
            column=2,
            padx=10,
            pady=0,
            sticky="nsew",
        )
        self.frame_ldd.grid_rowconfigure(4, weight=1)

        self.frame_export_data = customtkinter.CTkFrame(
            self.tabview.tab(settings),
            width=350,
            height=40,
            fg_color="grey80",
            corner_radius=5,
        )

        self.frame_export_data.grid(
            row=1,
            column=0,
            padx=10,
            pady=(10, 0),
            sticky="nsew",
        )
        self.frame_export_data.grid_rowconfigure(4, weight=1)

        self.frame_cpu_temp = customtkinter.CTkFrame(
            self.tabview.tab(settings),
            width=350,
            height=40,
            fg_color="grey80",
            corner_radius=5,
        )

        self.frame_cpu_temp.grid(
            row=3,
            column=0,
            padx=10,
            pady=(10, 0),
            sticky="nsew",
        )
        self.frame_cpu_temp.grid_rowconfigure(4, weight=1)

        self.frame_appearance = customtkinter.CTkFrame(
            self.tabview.tab(settings),
            width=350,
            height=40,
            fg_color="grey80",
            corner_radius=5,
        )

        self.frame_appearance.grid(
            row=5,
            column=0,
            padx=10,
            pady=(10, 0),
            sticky="nsew",
        )
        self.frame_appearance.grid_rowconfigure(4, weight=1)

        self.frame_shutdown_quit = customtkinter.CTkFrame(
            self.tabview.tab(settings),
            width=350,
            height=40,
            fg_color="grey80",
            corner_radius=5,
        )

        self.frame_shutdown_quit.grid(
            row=5,
            column=6,
            padx=10,
            pady=(10, 0),
            sticky="nsew",
        )
        self.frame_shutdown_quit.grid_rowconfigure(4, weight=1)

        self.frame_notifications = customtkinter.CTkFrame(
            self.tabview.tab(overview),
            width=350,
            height=40,
            fg_color="grey80",
            corner_radius=5,
        )

        self.frame_notifications.grid(
            row=5,
            column=2,
            padx=10,
            pady=(10, 0),
            sticky="nsew",
        )
        self.frame_notifications.grid_rowconfigure(4, weight=1)

        # self.frame_notifications_tec = customtkinter.CTkFrame(
        #     self.tabview.tab(overview),
        #     width=350,
        #     height=40,
        #     fg_color="grey80",
        #     corner_radius=5,
        # )
        
        # self.frame_notifications_tec.grid(
        #     row=5,
        #     column=1,
        #     padx=0,
        #     pady=(10, 0),
        #     sticky="nsew",
        # )
        # self.frame_notifications_tec.grid_rowconfigure(4, weight=1)

        self.frame_ldd_config = customtkinter.CTkFrame(
            self.tabview.tab(overview),
            width=350,
            height=40,
            fg_color="grey80",
            corner_radius=5,
        )

        self.frame_ldd_config.grid(
            row=4,
            column=2,
            padx=10,
            pady=0,
            sticky="nsew",
        )
        self.frame_ldd_config.grid_rowconfigure(4, weight=1)

        # Channel 1 Properties
        self.settings_features = customtkinter.CTkLabel(
            self.tabview.tab(overview),
            text="Crystal Temperature",
            anchor="w",
            font=("Arial", 30)
        )

        self.settings_features.grid(
            row=0,
            column=1,
            padx=10,
            pady=(0, 0)
        )

        self.ch1_label = customtkinter.CTkLabel(
            self.frame_temp_crystal,
            text=f'Actual Value',
            font=("Arial", 23)
        )

        self.ch1_label.grid(
            row=0,
            column=0,
            padx=(5, 0),
            pady=(0, 0),
            sticky="w"
        )

        self.ch1_label = customtkinter.CTkLabel(
            self.frame_temp_crystal,
            text=f'Setpoint',
            font=("Arial", 23)
        )

        self.ch1_label.grid(
            row=0,
            column=2,
            padx=(20, 0),
            pady=(0, 0),
            sticky="w"
        )

        self.ch1_temp_av = customtkinter.CTkLabel(
            self.frame_temp_crystal,
            text=f'{self.mt1_ot:.2f}°C',
            font=("Arial", 22)
        )

        self.ch1_temp_av.grid(
            row=1,
            column=0,
            padx=(5, 0),
            pady=(0, 0),
            sticky="w"
        )

        self.ch1_temp_sp = customtkinter.CTkLabel(
            self.frame_temp_crystal,
            text=f'{self.mt1_tot:.2f}°C',
            font=("Arial", 22),
        )

        self.ch1_temp_sp.grid(
            row=1,
            column=2,
            padx=(20, 0),
            pady=(0, 0),
            sticky="w"
        )

        self.ch1_button_increase = customtkinter.CTkButton(
            self.frame_temp_crystal,
            text="+", command=self.ch1_increase_button_event,
            height=30,
            width=30,
        )

        self.ch1_button_increase.grid(
            row=1,
            column=3,
            padx=10,
            pady=0,
            sticky="w"
        )

        self.ch1_button_decrease = customtkinter.CTkButton(
            self.frame_temp_crystal,
            text="-",
            command=self.ch1_decrease_button_event,
            height=30,
            width=30
        )

        self.ch1_button_decrease.grid(
            row=1,
            column=3,
            padx=50,
            pady=0
        )

        # Channel 2 Properties
        self.settings_features = customtkinter.CTkLabel(
            self.tabview.tab(overview),
            text="Diode Temperature",
            anchor="w",
            font=("Arial", 30)
        )

        self.settings_features.grid(
            row=3,
            column=1,
            padx=10,
            pady=(0, 0)
        )


        self.ch2_label = customtkinter.CTkLabel(
            self.frame_temp_diode,
            text=f'Actual Value',
            font=("Arial", 23)
        )

        self.ch2_label.grid(
            row=0,
            column=0,
            padx=(5, 0),
            pady=(0, 0),
            sticky="w"
        )

        self.ch2_temp_av = customtkinter.CTkLabel(
            self.frame_temp_diode,
            text=f'{self.mt2_ot:.2f}°C',
            font=("Arial", 22)
        )

        self.ch2_temp_av.grid(
            row=1,
            column=0,
            padx=(5, 0),
            pady=(0, 0),
            sticky="w"
        )

        self.ch2_label = customtkinter.CTkLabel(
            self.frame_temp_diode,
            text=f'Setpoint',
            font=("Arial", 25)
        )

        self.ch2_label.grid(
            row=0,
            column=2,
            padx=(20, 0),
            pady=(0, 0),
            sticky="w"
        )


        self.ch2_temp_sp = customtkinter.CTkLabel(
            self.frame_temp_diode,
            text=f'{self.mt2_tot:.2f}°C',
            font=("Arial", 22)
        )

        self.ch2_temp_sp.grid(
            row=1,
            column=2,
            padx=(20, 0),
            pady=(0, 0),
            sticky="w"
        )

        self.ch2_button_increase = customtkinter.CTkButton(
            self.frame_temp_diode,
            text="+", command=self.ch2_increase_button_event,
            height=30,
            width=30
        )

        self.ch2_button_increase.grid(
            row=1,
            column=3,
            padx=10,
            pady=0,
            sticky="w"
        )

        self.ch2_button_decrease = customtkinter.CTkButton(
            self.frame_temp_diode,
            text="-",
            command=self.ch2_decrease_button_event,
            height=30,
            width=30
        )

        self.ch2_button_decrease.grid(
            row=1,
            column=3,
            padx=50,
            pady=0,
            sticky="w"
        )

        # self.notifications = customtkinter.CTkLabel(
        #     self.frame_notifications_tec,
        #     text=f"{self.ldd.A_limit()[0]}",
        #     anchor="w",
        #     font=("Arial", 22)
        # )
        # 
        # self.notifications.grid(
        #     row=0,
        #     column=0,
        #     padx=10,
        #     pady=(0, 0)
        # )

        # Laser Beam-bar properties
        self.settings_features = customtkinter.CTkLabel(
            self.tabview.tab(overview),
            text="LDD Power",
            anchor="w",
            font=("Arial", 30)
        )

        self.settings_features.grid(
            row=0,
            column=2,
            padx=10,
            pady=(0, 0)
        )

        self.ch2_label = customtkinter.CTkLabel(
            self.frame_ldd,
            text=f'Actual Value',
            font=("Arial", 23)
        )

        self.ch2_label.grid(
            row=0,
            column=0,
            padx=(5, 0),
            pady=(0, 0),
            sticky="w"
        )

        self.ch2_label = customtkinter.CTkLabel(
            self.frame_ldd,
            text=f'SetPoint',
            font=("Arial", 23)
        )

        self.ch2_label.grid(
            row=0,
            column=2,
            padx=(20, 0),
            pady=(0, 0),
            sticky="w"
        )

        self.ldd_current_av = customtkinter.CTkLabel(
            self.frame_ldd,
            text=f'{self.ldd.ldd_get_av():.2f}W',
            font=("Arial", 22)
        )

        self.ldd_current_av.grid(
            row=1,
            column=0,
            padx=(5, 0),
            pady=(0, 0),
            sticky="w"
        )

        self.ldd_current_sp = customtkinter.CTkLabel(
            self.frame_ldd,
            text=f'{self.ldd.ldd_get_sp():.2f}A',
            font=("Arial", 22)
        )

        self.ldd_current_sp.grid(
            row=1,
            column=2,
            padx=(20, 0),
            pady=(0, 0),
            sticky="w"
        )

        self.ldd_current_increase = customtkinter.CTkButton(
            self.frame_ldd,
            text="+",
            command=self.ldd_increase_button_event,
            height=30,
            width=30
        )

        self.ldd_current_increase.grid(
            row=1,
            column=3,
            padx=10,
            pady=0,
            sticky="w"
        )

        self.ldd_current_decrease = customtkinter.CTkButton(
            self.frame_ldd,
            text="-",
            command=self.ldd_decrease_button_event,
            height=30,
            width=30
        )

        self.ldd_current_decrease.grid(
            row=1,
            column=3,
            padx=50,
            pady=0,
            sticky="w"
        )

        self.settings_features = customtkinter.CTkLabel(
            self.tabview.tab(overview),
            text="LDD Properties",
            anchor="w",
            font=("Arial", 30)
        )

        self.settings_features.grid(
            row=3,
            column=2,
            padx=10,
            pady=(0, 0)
        )


        self.laser_beam_bar = customtkinter.CTkSlider(
            self.frame_ldd_config,
            from_=0,
            to=1
        )

        self.laser_beam_bar.grid(
            row=0,
            column=0,
            padx=(5, 0),
            pady=(10, 10),
            rowspan=2
        )

        self.laser_go = customtkinter.CTkButton(
            self.frame_ldd_config,
            text="LASER GO",
            command=self.laser_go_button_event
        )

        self.laser_go.grid(
            row=2,
            column=0,
            padx=(10, 0),
            pady=0
        )

        self.laser_nogo = customtkinter.CTkButton(
            self.frame_ldd_config,
            text="LASER STOP",
            command=self.laser_nogo_button_event
        )

        self.laser_nogo.grid(
            row=2,
            column=1,
            padx=(10, 0),
            pady=0
        )

        self.notifications = customtkinter.CTkLabel(
            self.frame_notifications,
            text=f"{self.ldd.A_limit()[0]}",
            anchor="w",
            font=("Arial", 22)
        )

        self.notifications.grid(
            row=0,
            column=0,
            padx=10,
            pady=(0, 0)
        )

        # Design Settings tab
        # CPU Temperature
        self.settings_features = customtkinter.CTkLabel(
            self.tabview.tab(settings),
            text="Features:",
            anchor="w",
            font=("Arial", 30)
        )

        self.settings_features.grid(
            row=0,
            column=0,
            padx=10,
            pady=(0, 0)
        )

        self.csv_export = customtkinter.CTkButton(
            self.frame_export_data,
            text="Export Data",
            command=self.start_export
        )

        self.csv_export.grid(
            row=0,
            column=0,
            padx=(60, 0),
            pady=(30, 0)
        )

        self.cpu_temp_av_label = customtkinter.CTkLabel(
            self.frame_cpu_temp,
            text="CPU Temperature:",
            anchor="center"
        )

        self.cpu_temp_av_label.grid(
            row=0,
            column=0,
            padx=80,
            pady=(0, 0)
        )

        self.cpu_temp_av = customtkinter.CTkLabel(
            self.frame_cpu_temp,
            text=f"{CPUTemperature().temperature:.2f}",
            anchor="center"
        )

        self.cpu_temp_av.grid(
            row=0,
            column=0,
            padx=80,
            pady=(40, 0)
        )

        # Appearance mode properties
        self.appearance_mode_label = customtkinter.CTkLabel(
            self.frame_appearance,
            text="Appearance Mode:",
            anchor="w"
        )

        self.appearance_mode_label.grid(
            row=0,
            column=0,
            padx=60,
            pady=(0, 0)
        )

        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(
            self.frame_appearance,
            values=["Light", "Dark"],
            command=self.change_appearance_mode_event
        )

        self.appearance_mode_optionemenu.grid(
            row=0,
            column=0,
            padx=60,
            pady=(50, 0)
        )

        self.quiter = customtkinter.CTkButton(
            self.frame_shutdown_quit,
            text="Quit",
            command=self.open_dialog_box  # quit the window (not working)
        )

        self.quiter.grid(
            row=0,
            column=0,
            padx=100,
            pady=(0, 0)
        )

        self.quiter = customtkinter.CTkButton(
            self.frame_shutdown_quit,
            text="Quit",
            command=self.start_quit_all  # quit the app (not working)
        )

        self.quiter.grid(
            row=0,
            column=0,
            padx=100,
            pady=(0, 0)
        )

        self.shut_down = customtkinter.CTkButton(
            self.frame_shutdown_quit,
            text="Shut down",
            command=self.shut_down_button_event  # self.shut_down
        )


        self.shut_down.grid(
            row=0,
            column=0,
            padx=100,
            pady=(100, 0)
        )

        if __name__ != "__main__":
            self.quiter.configure(state="disable")

        # if __name__ == "__main__":
        #     self.shut_down.configure(state="disable")

        self.laser_beam_bar.set(0)

    # Definitions and methods, button events
    def open_dialog_box(self):
        #customtkinter
        pass

    def start_quit_all(self):
        quit_thread = threading.Thread(target=self.quit_all,
            daemon=True
        ).start()

    def quit_all(self):
        """
        All the threads need to be closed -> How is the function for
        that? - thread.join()?
        """
        # threaded_task.join()
        # for thread in threading.enumerate():
        #     print(thread.name)
            # print(Thread-5.join())
        self.quit

    def ch1_increase_button_event(self):
        self.mt_1.set_temp(
            self.mt_1.get_data()["target object temperature"][0] + 1.0
        )

    def ch1_decrease_button_event(self):
        self.mt_1.set_temp(
            self.mt_1.get_data()["target object temperature"][0] - 1.0
        )

    def ch2_increase_button_event(self):
        self.mt_2.set_temp(
            self.mt_2.get_data()["target object temperature"][0] + 1.0
        )

    def ch2_decrease_button_event(self):
        self.mt_2.set_temp(
            self.mt_2.get_data()["target object temperature"][0] - 1.0
        )

    def tec_temp_stable(self, lst: list) -> str:
        """
        Test if the temperatur of both TECs are stable and show it in
        the status bar on the overview tab. Fill a list with ten values
        and take the mean of the 10.
        """
        if True:
            return True

    def update_ch1_temp_av(self):  # Crystal
        temp_av = self.mt_1.get_data()["object temperature"][0]
        self.queue_cr_av.put(temp_av)
        self.array_cr_av = np.insert(
            self.array_cr_av,
            np.shape(self.array_cr_av)[0],
            [time.time(), temp_av],
            axis=0
        )
        self.ch1_temp_av.configure(text=f'{self.queue_cr_av.get():.2f}°C')
        self.ch1_temp_av.after(1000, self.update_ch1_temp_av)

    def update_ch1_temp_sp(self):  # Crystal
        temp_sp = self.mt_1.get_data()["target object temperature"][0]
        self.queue_cr_sp.put(temp_sp)
        self.array_cr_sp = np.insert(
            self.array_cr_sp,
            np.shape(self.array_cr_sp)[0],
            [time.time(), temp_sp],
            axis=0
        )
        self.ch1_temp_sp.configure(text=f'{self.queue_cr_sp.get():.2f}°C')
        self.ch1_temp_sp.after(500, self.update_ch1_temp_sp)

    def update_ch2_temp_av(self):  # Diode
        temp_av = self.mt_2.get_data()["object temperature"][0]
        self.queue_di_av.put(temp_av)
        self.array_di_av = np.insert(
            self.array_di_av,
            np.shape(self.array_di_av)[0],
            [time.time(), temp_av],
            axis=0
        )
        self.ch2_temp_av.configure(text=f'{self.queue_di_av.get():.2f}°C')
        self.ch2_temp_av.after(1000, self.update_ch2_temp_av)

    def update_ch2_temp_sp(self):  # Diode
        temp_sp = self.mt_2.get_data()["target object temperature"][0]
        self.queue_di_sp.put(temp_sp)
        self.array_di_sp = np.insert(
            self.array_di_sp,
            np.shape(self.array_di_sp)[0],
            [time.time(), temp_sp],
            axis=0
        )
        self.ch2_temp_sp.configure(text=f'{self.queue_di_sp.get():.2f}°C')
        self.ch2_temp_sp.after(500, self.update_ch2_temp_sp)

    def tec_temp_limits(self, channel="di"):
        """
        Return if the temperatures of both TECS are in an good con-
        dition.
        """
        if channel == "cr":
            temp_av = self.mt_1.get_data()["object temperature"][0]
        else:
            temp_av = self.mt_2.get_data()["object temperature"][0]
        
        if True:
            pass
        elif True:
            pass
        elif True:
            pass
        else:
            pass

    def update_ldd_current_av(self):
        ldd_av = self.ldd.ldd_get_av()
        self.queue_ldd_av.put(ldd_av)
        self.array_ldd_av = np.insert(
            self.array_ldd_av,
            np.shape(self.array_ldd_av)[0],
            [time.time(), ldd_av],
            axis=0
        )
        self.ldd_current_av.configure(text=f'{self.queue_ldd_av.get():.2f}W')
        self.ldd_current_av.after(1000, self.update_ldd_current_av)

    def update_ldd_current_sp(self):
        ldd_sp = self.ldd.ldd_get_sp()
        self.queue_ldd_sp.put(ldd_sp)
        self.array_ldd_sp = np.insert(
            self.array_ldd_sp,
            np.shape(self.array_ldd_sp)[0],
            [time.time(), ldd_sp],
            axis=0
        )
        self.ldd_current_sp.configure(text=f'{self.queue_ldd_sp.get():.2f}A')
        self.ldd_current_sp.after(50, self.update_ldd_current_sp)

    def ldd_increase_button_event(self):
        self.ldd_current_sp.configure(
            text=f'{self.ldd.ldd_sp_increase()}'
        )

    def ldd_decrease_button_event(self):
        self.ldd_current_sp.configure(
            text=f'{self.ldd.ldd_sp_decrease()}'
        )

    def laser_gonogo_event(self):
        if self.laser_beam_bar.get() == 1:
            self.laser_go.configure(
            fg_color="green"
        )
        else:
            self.laser_go.configure(
                fg_color=('#3B8ED0', '#1F6AA5')
        )
        self.laser_go.after(10, self.laser_gonogo_event)  # 0.01 seconds

    def laser_go_button_event(self):
        """
        Start the Laser. The current is going to ramp up until setpoint.
        Take the setpoint from the ldd_control.py file and feed it as an
        argument in to the statement below.
        """
        if self.laser_beam_bar.get() == 1:
            self.ldd.laser_start()
        self.laser_beam_bar.set(0)

    def laser_nogo_button_event(self):
        """
        Start the Laser.
        The current ramps down until setpoint
        """
        self.ldd.laser_stop()
        self.laser_beam_bar.set(0)

    def ldd_notifications(self):
        self.notifications.configure(text=f'{self.ldd.A_limit()[0]}')
        self.notifications.after(1000, self.ldd_notifications)

    def start_export(self):
        """
        Function to start the exporting function indirectly.
        """
        thread_export = threading.Thread(
            target=self.export_data,
            daemon=True  # Terminate the thread after end of script
        )
        thread_export.start()

    def export_data(self):
        df_historian_cr_av = pd.DataFrame(
            self.array_cr_av,
            columns=["Time", "Crystal_av"]
        )

        df_audittrail_cr_sp = pd.DataFrame(
            self.array_cr_sp,
            columns=["Time", "Crystal_SP"]
        )

        df_historian_di_av = pd.DataFrame(
            self.array_di_av,
            columns=["Time", "Diode_AV"]
        )

        df_audittrail_di_sp = pd.DataFrame(
            self.array_di_sp,
            columns=["Time", "Diode_SP"]
        )

        df_historian_ldd_av = pd.DataFrame(
            self.array_ldd_av,
            columns=["Time", "LDD_AV"]
        )

        df_audittrail_ldd_sp = pd.DataFrame(
            self.array_ldd_sp,
            columns=["Time", "LDD_SP"]
        )

        df_data_concat = pd.concat(
            [df_historian_cr_av,
            df_audittrail_cr_sp,
            df_historian_di_av,
            df_audittrail_di_sp,
            df_historian_ldd_av,
            df_audittrail_ldd_sp],
            axis=1
        )
        df_data_concat.to_csv(
            "/home/pi/Desktop/hist_audit.csv",
            sep=","
        )

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def cpu_temp(self):
        self.cpu_temp_av.configure(
            text=f'{CPUTemperature().temperature:.2f}°C'
        )
        self.cpu_temp_av.after(1000, self.cpu_temp)

    def shut_down_button_event(self):
        self.laser_beam_bar.set(0)
        self.laser_nogo_button_event()
        os.system("sudo shutdown")

    def check_queue(self):
        """
        Read the Queue.
        """
        value = self.queue_cr_av.get()

    def update_gui(self):
        self.update_ch1_temp_av()
        self.update_ch1_temp_sp()
        self.update_ch2_temp_av()
        self.update_ch2_temp_sp()
        self.update_ldd_current_sp()
        self.update_ldd_current_av()
        self.cpu_temp()
        self.laser_gonogo_event()
        self.ldd_notifications()


if __name__ == "__main__":

    # Initialising the GUI
    app = GUI()
    
    # Initiating the thread to the main thread
    threaded_task = threading.Thread(target=app.update_gui,
            daemon=True
    ).start()

    # Starting the mainloop of the GUI
    app.mainloop()
