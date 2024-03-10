import customtkinter

import os
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

        self.ldd = ldd_ctrl.ldd_control()

        # Create an empty data frame for exporting AuditTrail of change
        # the set pointsand actual values of the pump diode and the
        # crystal TECs

        self.df_audittrail = pd.DataFrame([], columns=[
            "Time",
            "Crystal_SP",
            "Diode_SP"]
        )

        self.df_historian = pd.DataFrame([], columns=[
            "Time",
            "Crystal_AV",
            "Diode_AV"]
        )

        # Definie the tab configuration
        signin, overview, settings = "Sign In", "Overview", "Settings"
        self.tabview = customtkinter.CTkTabview(
            self, width=800, height=480
        )

        self.tabview.grid(
            row=0,
            column=1,
            padx=(0, 0),
            pady=(0, 0)
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
        self.sidebar_frame1 = customtkinter.CTkFrame(
            self.tabview.tab(overview),
            width=350,
            height=40,
            fg_color="grey80",
            corner_radius=5
        )

        self.sidebar_frame1.grid(
            row=0,
            column=1,
            padx=10,
            pady=(10, 0),
            sticky="nsew",
            rowspan=2
        )

        self.sidebar_frame1.grid_rowconfigure(4, weight=1)

        self.sidebar_frame2 = customtkinter.CTkFrame(
            self.tabview.tab(overview),
            # "Channel 2",
            width=350,
            height=40,
            fg_color="grey80",
            corner_radius=5,
        )
        self.sidebar_frame2.grid(
            row=2,
            column=1,
            padx=10,
            pady=(10, 0),
            sticky="nsew",
            rowspan=3
        )
        self.sidebar_frame2.grid_rowconfigure(4, weight=1)

        self.sidebar_frame3 = customtkinter.CTkFrame(
            self.tabview.tab(overview),
            # "Laser Config",
            width=350,
            height=40,
            fg_color="grey80",
            corner_radius=5,
        )

        self.sidebar_frame3.grid(
            row=0,
            column=2,
            padx=10,
            pady=(10, 0),
            sticky="nsew",
            rowspan=2
        )
        self.sidebar_frame3.grid_rowconfigure(4, weight=1)
        
        self.sidebar_frame4 = customtkinter.CTkFrame(
            self.tabview.tab(settings),
            # "Laser Config",
            width=350,
            height=40,
            fg_color="grey80",
            corner_radius=5,
        )

        self.sidebar_frame4.grid(
            row=0,
            column=0,
            padx=10,
            pady=(10, 0),
            sticky="nsew",
            rowspan=2
        )
        self.sidebar_frame4.grid_rowconfigure(4, weight=1)

        self.sidebar_frame5 = customtkinter.CTkFrame(
            self.tabview.tab(settings),
            # "Laser Config",
            width=350,
            height=40,
            fg_color="grey80",
            corner_radius=5,
        )

        self.sidebar_frame5.grid(
            row=0,
            column=0,
            padx=10,
            pady=(10, 0),
            sticky="nsew",
            rowspan=2
        )
        self.sidebar_frame5.grid_rowconfigure(4, weight=1)

        self.sidebar_frame6 = customtkinter.CTkFrame(
            self.tabview.tab(settings),
            # "Laser Config",
            width=350,
            height=40,
            fg_color="grey80",
            corner_radius=5,
        )

        self.sidebar_frame6.grid(
            row=0,
            column=0,
            padx=10,
            pady=(10, 0),
            sticky="nsew",
            rowspan=2
        )
        self.sidebar_frame6.grid_rowconfigure(4, weight=1)

        # Channel 1 Properties
        self.ch1_label = customtkinter.CTkLabel(
            self.sidebar_frame1,
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
            self.sidebar_frame1,
            text=f'{self.mt_1.get_data()["object temperature"][0]:.2f}°C',
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
            self.sidebar_frame1,
            text=f'{self.mt_1.get_data()["target object temperature"][0]:.2f}°C',
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
            self.sidebar_frame1,
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
            self.sidebar_frame1,
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
            self.sidebar_frame2,
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
            self.sidebar_frame2,
            text=f'{self.mt_2.get_data()["object temperature"][0]:.2f}°C',
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
            self.sidebar_frame2,
            text=f'{self.mt_2.get_data()["target object temperature"][0]:.2f}°C',
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
            self.sidebar_frame2,
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
            self.sidebar_frame2,
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
            self.sidebar_frame3,
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
            self.sidebar_frame3,
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
            self.sidebar_frame3,
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
            self.sidebar_frame3,
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
            self.sidebar_frame3,
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
            self.sidebar_frame3,
            from_=0,
            to=1
        )

        self.laser_beam_bar.grid(
            row=2,
            column=2,
            padx=(5, 0),
            pady=(10, 10),
            rowspan=1
        )

        self.laser_go = customtkinter.CTkButton(
            self.sidebar_frame3,
            text="LASER GO",
            command=self.laser_go_button_event
        )

        self.laser_go.grid(
            row=4,
            column=0,
            padx=(10, 0),
            pady=0
        )

        self.laser_nogo = customtkinter.CTkButton(
            self.sidebar_frame3,
            text="LASER STOP",
            command=self.laser_nogo_button_event
        )

        self.laser_nogo.grid(
            row=4,
            column=2,
            padx=(10, 0),
            pady=0
        )

        # Design Settings tab
        # CPU Temperature

        self.csv_export = customtkinter.CTkButton(
            self.sidebar_frame4,
            text="Export Data",
            command=self.expo
        )

        self.laser_nogo.grid(
            row=4,
            column=2,
            padx=(10, 0),
            pady=0
        )

        self.settings_features = customtkinter.CTkLabel(
            self.tabview.tab(settings),
            text="Features:",
            anchor="w",
            font=("Arial", 22)
        )

        self.settings_features.grid(
            row=5,
            column=0,
            padx=20,
            pady=(0, 0)
        )

        self.cpu_temp_av_label = customtkinter.CTkLabel(
            self.sidebar_frame5,
            text="CPU Temperature:",
            anchor="w"
        )

        self.cpu_temp_av_label.grid(
            row=5,
            column=0,
            padx=20,
            pady=(0, 0)
        )

        self.cpu_temp_av = customtkinter.CTkLabel(
            self.sidebar_frame5,
            text=f"{CPUTemperature().temperature:.2f}",
            anchor="w"
        )

        self.cpu_temp_av.grid(
            row=5,
            column=0,
            padx=20,
            pady=(40, 0)
        )

        # Appearance mode properties
        self.appearance_mode_label = customtkinter.CTkLabel(
            self.sidebar_frame6,
            text="Appearance Mode:",
            anchor="w"
        )

        self.appearance_mode_label.grid(
            row=9,
            column=0,
            padx=20,
            pady=(0, 0)
        )

        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(
            self.sidebar_frame6,
            values=["Light", "Dark"],
            command=self.change_appearance_mode_event
        )

        self.appearance_mode_optionemenu.grid(
            row=7,
            column=0,
            padx=20,
            pady=(50, 0)
        )

        self.quiter = customtkinter.CTkButton(
            self.sidebar_frame7,
            text="Quit",
            # command=self.quit  # quit the window (not working)
            command=threading.Thread(target=quit, daemon=True).start()
        )

        self.quiter.grid(
            row=5,
            column=8,
            padx=0,
            pady=0
        )

        self.shut_down = customtkinter.CTkButton(
            self.sidebar_frame7,
            text="Shut down",
            command=self.shut_down_button_event  # self.shut_down
            # command=threading.Thread(target=self.shut_down_button_event).start()
        )

        self.shut_down.grid(
            row=7,
            column=8,
            padx=0,
            pady=0
        )

        if __name__ != "__main__":
            self.quiter.configure(state="disable")

        if __name__ == "__main__":
            self.shut_down.configure(state="disable")

        self.laser_beam_bar.set(0)

    # Definitions and methods, button events
    def ch1_increase_button_event(self):
        self.mt_1.set_temp(
            self.mt_1.get_data()["target object temperature"][0] + 1.0
        )
        self.df_audittrail.to_csv(
            "/home/pi/Desktop/export_audittrail.csv",
            mode="a"
        )
    def ch1_decrease_button_event(self):
        self.mt_1.set_temp(
            self.mt_1.get_data()["target object temperature"][0] - 1.0
        )
        self.df_audittrail.to_csv(
            "/home/pi/Desktop/export_audittrail.csv",
            mode="a"
        )

    def ch2_increase_button_event(self):
        self.mt_2.set_temp(
            self.mt_2.get_data()["target object temperature"][0] + 1.0
        )
        self.df_audittrail.to_csv(
            "/home/pi/Desktop/export_audittrail.csv",
            mode="a"
        )

    def ch2_decrease_button_event(self):
        self.mt_2.set_temp(
            self.mt_2.get_data()["target object temperature"][0] - 1.0
        )
        self.df_audittrail.to_csv(
            "/home/pi/Desktop/export_audittrail.csv",
            mode="a"
        )

    def update_ch1_temp_av(self):
        self.ch1_temp_av.configure(
            text=f'{self.mt_1.get_data()["object temperature"][0]:.2f}°C'
        )
        self.df_historian.to_csv(
            "/home/pi/Desktop/export_av.csv",
            mode="a"
        )
        self.ch1_temp_av.after(1000, self.update_ch1_temp_av)

    def update_ch1_temp_sp(self):
        self.ch1_temp_sp.configure(
            text=f'{self.mt_1.get_data()["target object temperature"][0]:.2f}°C'
        )
        self.df_historian.to_csv(
            "/home/pi/Desktop/export_sp.csv",
            mode="a"
        )
        self.ch1_temp_sp.after(1000, self.update_ch1_temp_sp)

    def update_ch2_temp_av(self):
        self.ch2_temp_av.configure(
            text=f'{self.mt_2.get_data()["object temperature"][0]:.2f}°C'
        )
        self.df_historian.to_csv(
            "/home/pi/Desktop/export_av.csv",
            mode="a"
        )
        self.ch2_temp_av.after(1000, self.update_ch2_temp_av)

    def update_ch2_temp_sp(self):
        self.ch2_temp_sp.configure(
            text=f'{self.mt_2.get_data()["target object temperature"][0]:.2f}°C'
        )
        self.df_historian.to_csv(
            "/home/pi/Desktop/export_sp.csv",
            mode="a"
        )
        self.ch2_temp_sp.after(1000, self.update_ch2_temp_sp)

    def update_ldd_current_av(self):
        self.ldd_current_av.configure(
            text=f'{self.ldd.ldd_get_av():.2f}A'
        )
        self.df_historian.to_csv(
            "/home/pi/Desktop/export_av.csv",
            mode="a"
        )
        self.ldd_current_av.after(1000, self.update_ldd_current_av)

    def update_ldd_current_sp(self):
        self.ldd_current_sp.configure(
            text=f'{self.ldd.ldd_get_sp():.2f}A'
        )
        self.df_historian.to_csv(
            "/home/pi/Desktop/export_sp.csv",
            mode="a"
        )
        self.ldd_current_sp.after(500, self.update_ldd_current_sp)

    def ldd_increase_button_event(self):
        self.ldd_current_sp.configure(
            text=f'{self.ldd.ldd_sp_increase()}'
        )
        self.df.to_csv(
            "/home/pi/Desktop/export_audittrail.csv",
            mode="a"
        )

    def ldd_decrease_button_event(self):
        self.ldd_current_sp.configure(
            text=f'{self.ldd.ldd_sp_decrease()}'
        )
        self.df_audittrail.to_csv(
            "/home/pi/Desktop/export_audittrail.csv",
            mode="a"
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
        self.laser_go.after(10, self.laser_gonogo_event)
        self.df_audittrail.to_csv(
            "/home/pi/Desktop/export_audittrail.csv",
            mode="a"
        )

    def laser_go_button_event(self):
        """
        Start the Laser. The current is going to ramp up until setpoint.
        Take the setpoint from the ldd_control.py file and feed it as an
        argument in to the statement below.
        """
        if self.laser_beam_bar.get() == 1:
            self.ldd.laser_start()
        self.laser_beam_bar.set(0)
        self.df_audittrail.to_csv(
            "/home/pi/Desktop/export_audittrail.csv",
            mode="a"
        )

    def laser_nogo_button_event(self):
        """
        Start the Laser.
        The current is going to ramp down until setpoint
        """
        self.ldd.laser_stop()
        self.laser_beam_bar.set(0)
        self.df_audittrail.to_csv(
            "/home/pi/Desktop/export_audittrail.csv",
            mode="a"
        )

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def cpu_temp(self):
        self.cpu_temp_av.configure(
            text=f'{CPUTemperature().temperature:.3f}°C'
        )
        self.cpu_temp_av.after(2000, self.cpu_temp)

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
        # self.laser_go_button_event()
        self.cpu_temp()
        self.laser_gonogo_event()

if __name__ == "__main__":

    # Initialising the GUI
    app = GUI()
    
    # Initiating the thread to the main thread
    threaded_task = threading.Thread(target=app.update_gui())
    threaded_task.start()

    # Starting the mainloop of the GUI
    app.mainloop()
