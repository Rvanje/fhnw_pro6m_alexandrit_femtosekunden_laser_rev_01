import customtkinter

import os
import time
import threading
import pandas as pd

import tec_control as tec_ctrl
import ldd_control as ldd_ctrl

from gpiozero import CPUTemperature

# Implement the default Matplotlib key bindings.
# from matplotlib.backend_bases import key_press_handler  # I.O.
# from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# from matplotlib.figure import Figure

# Colour schemes of the application
customtkinter.set_appearance_mode("dark")
customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("blue")


class GUI(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        # Window settings
        self.title("Laser Configuration Utility")  # Main title
        self.geometry("800x480")  # Window size
        # self.overrideredirect(True)  # Enter quasi-fullscreen

        # Initialisation of the TEC-controller communication
        self.mt_1 = tec_ctrl.MeerstetterTEC(channel=1)
        self.mt_2 = tec_ctrl.MeerstetterTEC(channel=2)

        #Initialisation of the ldd driver
        self.ldd = ldd_ctrl.ldd_control()

        # Instanciation of the av and sp variables
        self.mt1_ot = self.mt_1.get_data()["object temperature"][0]
        self.mt2_ot = self.mt_2.get_data()["object temperature"][0]
        self.mt1_tot = self.mt_1.get_data()["target object temperature"][0]
        self.mt2_tot = self.mt_2.get_data()["target object temperature"][0]

        # Create an empty dictionaries for creating and exporting
        # AuditTrail of change the set points and actual values of the
        # pump diode and the crystal TECs, respectively
        self.dict_historian_cr_av = {}
        self.dict_audittrail_cr_sp = {}
        self.dict_historian_di_av = {}
        self.dict_audittrail_di_sp = {}
        self.dict_historian_ldd_av = {}
        self.dict_audittrail_ldd_sp = {}

        # Definie the tab configuration
        signin, overview, settings = "Sign In", "Overview", "Settings"
        self.tabview = customtkinter.CTkTabview(
            self,
            width=800,
            height=480
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
            row=0,
            column=1,
            padx=10,
            pady=(10, 0),
            sticky="nsew",
            rowspan=2
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
            row=2,
            column=1,
            padx=10,
            pady=(10, 0),
            sticky="nsew",
            rowspan=3
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
            row=0,
            column=2,
            padx=10,
            pady=(10, 0),
            sticky="nsew",
            rowspan=2
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
            rowspan=2
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
            rowspan=2
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
            rowspan=2
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
            row=3,
            column=2,
            padx=10,
            pady=(10, 0),
            sticky="nsew",
            rowspan=2
        )
        self.frame_notifications.grid_rowconfigure(4, weight=1)

        self.frame_ldd_config = customtkinter.CTkFrame(
            self.tabview.tab(overview),
            width=350,
            height=40,
            fg_color="grey80",
            corner_radius=5,
        )

        self.frame_ldd_config.grid(
            row=2,
            column=2,
            padx=10,
            pady=(10, 0),
            sticky="nsew",
            # rowspan=2
        )
        self.frame_ldd_config.grid_rowconfigure(4, weight=1)

        # Channel 1 Properties
        self.ch1_label = customtkinter.CTkLabel(
            self.frame_temp_crystal,
            text=f'TEC Crystal',
            font=("Arial", 25)
        )

        self.ch1_label.grid(
            row=0,
            column=0,
            padx=(5, 0),
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
            padx=(0, 0),
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
        self.ch2_label = customtkinter.CTkLabel(
            self.frame_temp_diode,
            text=f'TEC Diode',
            font=("Arial", 25)
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

        self.ch2_temp_sp = customtkinter.CTkLabel(
            self.frame_temp_diode,
            text=f'{self.mt2_tot:.2f}°C',
            font=("Arial", 22)
        )

        self.ch2_temp_sp.grid(
            row=1,
            column=2,
            padx=(0, 0),
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

        # Laser Beam-bar properties
        self.ch2_label = customtkinter.CTkLabel(
            self.frame_ldd,
            text=f'LDD Laser',
            font=("Arial", 25)
        )

        self.ch2_label.grid(
            row=0,
            column=0,
            padx=(5, 0),
            pady=(0, 0),
            sticky="w"
        )

        self.ldd_current_av = customtkinter.CTkLabel(
            self.frame_ldd,
            text=f'{self.ldd.ldd_get_av():.2f}A',
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
            padx=(0, 0),
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
            font=("Arial", 22)
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
            command=self.start_quit_all  # quit the window (not working)
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

        if __name__ == "__main__":
            self.shut_down.configure(state="disable")

        if __name__ == "__main__":
            self.csv_export.configure(state="disable")

        self.laser_beam_bar.set(0)

    # Definitions and methods, button events
    def start_quit_all(self):
        thread_quit = threading.Thread(target=self.quit_all)
        thread_quit.start()

    def quit_all(self):
        """
        All the threads need to be closed -> How is the function for
        that? - thread.join()?
        """
        quit()

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
# Unter FUNC Bearbeiten!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def update_ch1_temp_av(self):
        lst_temp_av = self.mt_1.get_data()["object temperature"][0]
        # lst_temp_av.append(self.mt_1.get_data()["object temperature"][0])
        self.ch1_temp_av.configure(text=f'{lst_temp_av:.2f}°C')
        # self.dict_historian_cr_av[f"{time.time()}"] = lst_temp_av
        # del lst_temp_av[:]
        self.ch1_temp_av.after(1000, self.update_ch1_temp_av)
        # threading.Timer(1, self.update_ch1_temp_av).start()

    def update_ch1_temp_sp(self):
        lst_temp_sp = self.mt_1.get_data()["target object temperature"][0]
        # lst_temp_sp.append(self.mt_1.get_data()["target object temperature"][0])
        self.ch1_temp_sp.configure(text=f'{lst_temp_sp:.2f}°C')
        # self.dict_audittrail_cr_sp[f"{time.time()}"] = lst_temp_sp
        # del lst_temp_sp[:]
        self.ch1_temp_sp.after(500, self.update_ch1_temp_sp)

    def update_ch2_temp_av(self):
        lst_temp_av = self.mt_2.get_data()["object temperature"][0]
        # lst_temp_av.append(self.mt_2.get_data()["object temperature"][0])
        self.ch2_temp_av.configure(text=f'{lst_temp_av:.2f}°C')
        # self.dict_historian_di_av[f"{time.time()}"] = lst_temp_av
        # del lst_temp_av[:]
        self.ch2_temp_av.after(1000, self.update_ch2_temp_av)

    def update_ch2_temp_sp(self):
        lst_temp_sp = self.mt_2.get_data()["target object temperature"][0]
        # lst_temp_sp.append(self.mt_2.get_data()["target object temperature"][0])
        self.ch2_temp_sp.configure(text=f'{lst_temp_sp:.2f}°C')
        # self.dict_audittrail_di_sp[f"{time.time()}"] = lst_temp_sp
        # del lst_temp_sp[:]
        self.ch2_temp_sp.after(500, self.update_ch2_temp_sp)

    def update_ldd_current_av(self):
        lst_current_av = []
        lst_current_av.append(self.ldd.ldd_get_av())
        self.ldd_current_av.configure(text=f'{lst_current_av[0]:.2f}A')
        self.dict_historian_ldd_av[f"{time.time()}"] = lst_current_av
        del lst_current_av[:]
        self.ldd_current_av.after(1000, self.update_ldd_current_av)

    def update_ldd_current_sp(self):
        lst_current_sp = []
        lst_current_sp.append(self.ldd.ldd_get_sp())
        self.ldd_current_sp.configure(text=f'{lst_current_sp[0]:.2f}A')
        self.dict_audittrail_ldd_sp[f"{time.time()}"] = lst_current_sp
        del lst_current_sp[:]
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
            # daemon=True  # Terminate the thread after end of script
        )
        thread_export.start()

    def export_data(self):
        print(self.dict_historian_cr_av)
        # threading.Lock().acquire()
        df_historian_cr_av = pd.DataFrame.from_dict(
            self.dict_historian_cr_av,
            orient="index",
            columns=["Time", "Crystal_av"]
        )

        df_audittrail_cr_sp = pd.DataFrame.from_dict(
            self.dict_audittrail_cr_sp,
            orient="index",
            columns=["Time", "Crystal_SP"]
        )

        df_historian_di_av = pd.DataFrame.from_dict(
            self.dict_historian_di_av,
            orient="index",
            columns=["Time", "Diode_AV"]
        )

        df_audittrail_di_sp = pd.DataFrame.from_dict(
            self.dict_audittrail_di_sp,
            orient="index",
            columns=["Time", "Diode_SP"]
        )

        df_historian_ldd_av = pd.DataFrame.from_dict(
            self.dict_historian_ldd_av,
            orient="index",
            columns=["Time", "LDD_AV"]
        )

        df_audittrail_ldd_sp = pd.DataFrame.from_dict(
            self.dict_audittrail_ldd_sp,
            orient="index",
            columns=["Time", "LDD_SP"]
        )
        
        # df_data_concat = pd.concat(
        #     [df_historian_cr_av,
        #     df_audittrail_cr_sp,
        #     df_historian_di_av,
        #     df_audittrail_di_sp,
        #     df_historian_ldd_av,
        #     df_audittrail_ldd_sp],
        #     axis=1
        # )
        # print(df_data_concat)
        # df_data_concat.to_csv("/home/pi/Desktop/hist_audit.csv", "a")
        # threading.Lock().release()

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
    threaded_task = threading.Thread(target=app.update_gui())
    threaded_task.start()

    # Starting the mainloop of the GUI
    app.mainloop()
