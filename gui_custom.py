import os
import sys
import time
import threading
from queue import Queue

import numpy as np
import pandas as pd
import customtkinter

import tec_control as tec_ctrl
import ldd_control_ang as ldd_ctrl

from gpiozero import CPUTemperature

customtkinter.set_appearance_mode("dark")
customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("blue")


class LabelTitle(customtkinter.CTkLabel):
    def __init__(self,
                master,
                text="Empty",
                font=None,
                anchor="w",
                pos=(0, 0)):

        super().__init__(master,
                         text=text,
                         font=("Arial", 30))
        self.text = text
        self.font = font
        self.anchor="w"
        
        self.grid(row=pos[0],
                  column=pos[1],
                  padx=(0, 0),
                  pady=(0, 0))


class StdLabel(customtkinter.CTkLabel):
    def __init__(self,
                master,
                text="Empty",
                font=None,
                pos=(0, 0),
                offset=((0, 0), (0, 0))):

        super().__init__(master,
                         text=text,
                         font=("Arial", 24))
        self.text = text
        self.font = font
        
        self.grid(row=pos[0],
                  column=pos[1],
                  padx=offset[0],
                  pady=offset[1],
                  sticky="w")


class Button(customtkinter.CTkButton):
    def __init__(self,
                 master,
                 text="Empty",
                 command=None,
                 dim=(40, 40),
                 pos=(0, 0),
                 offset=((0, 0), (0, 0))):

        super().__init__(master,
                         text=text,
                         command=command,
                         height=dim[0],
                         width=dim[1])

        self.grid(row=pos[0],
                  column=pos[1],
                  padx=offset[0],
                  pady=offset[1],
                  sticky="w")


class Frame(customtkinter.CTkFrame):
    def __init__(self,
                 master,
                 dim=(0, 0),
                 colour="grey70",
                 corner=5,
                 rowspan=1,
                 pos=(0, 0),
                 offset=((0, 0), (0, 0))):

        super().__init__(master, fg_color=colour)

        self.width=dim[0]
        self.height=dim[1]
        self.fg_color=colour
        self.corner_radius=corner

        self.grid(row=pos[0],
                  column=pos[1],
                  padx=offset[0],
                  pady=offset[1],
                  rowspan=rowspan,
                  sticky="nsew")

        self.grid_rowconfigure(4, weight=1)


class GUI(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        self.geometry("800x480")
        # self.overrideredirect(True)
        
        self.q_cr_av = Queue()
        self.q_cr_sp = Queue()
        self.q_di_av = Queue()
        self.q_di_sp = Queue()
        self.q_ldd_av = Queue()
        self.q_ldd_sp = Queue()
        self.q_ldd_w = Queue()

        self.mt_2 = tec_ctrl.MeerstetterTEC(channel=1)  # Diode
        self.mt_1 = tec_ctrl.MeerstetterTEC(channel=2)  # Crystal

        self.ldd = ldd_ctrl.ldd_control()

        self.mt1_ot = self.mt_1.get_data()["object temperature"][0]
        self.mt2_ot = self.mt_2.get_data()["object temperature"][0]
        self.mt1_tot = self.mt_1.get_data()["target object temperature"][0]
        self.mt2_tot = self.mt_2.get_data()["target object temperature"][0]

        self.array_cr_av = np.array([[0, 0]], dtype=np.float64)
        self.array_cr_sp = np.array([[0, 0]], dtype=np.float64)
        self.array_di_av = np.array([[0, 0]], dtype=np.float64)
        self.array_di_sp = np.array([[0, 0]], dtype=np.float64)
        self.array_ldd_av = np.array([[0, 0]], dtype=np.float64)
        self.array_ldd_sp = np.array([[0, 0]], dtype=np.float64)
        self.array_ldd_w = np.array([[0, 0]], dtype=np.float64)

        overview: str = "Overview"
        settings: str = "Settings"
        self.toplevel_window = None
        self.shut_down_window = None
        self.sign_in_window = None

        self.l_quit: str = ""
        self.l_shut: str = ""

        self.tabview = customtkinter.CTkTabview(
            self,
            width=800,
            height=480)

        self.tabview.grid(column=1)

        self.tabview.add(overview)
        self.tabview.add(settings)

        self.tabview.tab(overview).grid_columnconfigure(
            (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
            weight=1)

        self.tabview.tab(overview).grid_rowconfigure(
            (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
            weight=1)

        self.tabview.tab(settings).grid_columnconfigure(
            (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
            weight=1)

        self.tabview.tab(settings).grid_rowconfigure(
            (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
            weight=1)

        self.frame_temp_crystal = Frame(
            self.tabview.tab(overview),
            pos=(1, 1),  # (row, column)
            offset=((0, 0), (0, 0)))  # offset

        self.frame_temp_diode = Frame(
            self.tabview.tab(overview),
            pos=(1, 2),  # (row, column)
            offset=((10, 0), (0, 0)))  # offset

        self.frame_ldd = Frame(
            self.tabview.tab(overview),
            rowspan=2,
            pos=(4, 1),  # (row, column)
            offset=((0, 0), (0, 0)))  # offset

        self.frame_notifications = Frame(
            self.tabview.tab(overview),
            pos=(5, 2),  # (row, column)
            offset=((10, 0), (10, 0)))  # offset

        self.frame_export_data = Frame(
            self.tabview.tab(settings),
            pos=(2, 0),  # (row, column)
            offset=((10, 0), (10, 0)))  # offset

        self.frame_cpu_temp = Frame(
            self.tabview.tab(settings),
            pos=(1, 0),  # (row, column)
            offset=((10, 0), (10, 0)))  # offset

        self.frame_appearance = Frame(
            self.tabview.tab(settings),
            pos=(1, 2),  # (row, column
            offset=((10, 0), (10, 0)))  # offset

        self.frame_shutdown_quit = Frame(
            self.tabview.tab(settings),
            pos=(2, 2),  # (row, column)
            offset=((10, 0), (10, 0)))  # offset

        self.frame_ldd_config = Frame(
            self.tabview.tab(overview),
            pos=(4, 2),  # (row, column)
            offset=((10, 0), (0, 0)))  # offset

        self.title_crystal = LabelTitle(
            self.tabview.tab(overview),
            text="Crystal Temperature",
            pos=(0, 1))  # (row, column)

        self.ch1_label_av = StdLabel(
            self.frame_temp_crystal,
            text=f'Actual Value',
            pos=(0, 0),  # (row, column)
            offset=((5, 0), (0, 0)))  # offset

        self.ch1_label_sp = StdLabel(
            self.frame_temp_crystal,
            text=f'Setpoint',
            pos=(0, 2),  # (row, column)
            offset=((20, 0), (0, 0)))  # offset

        self.ch1_temp_av = StdLabel(
            self.frame_temp_crystal,
            text= None,
            pos=(1, 0),
            offset=((5, 0), (0, 0)))

        self.ch1_temp_sp = StdLabel(
            self.frame_temp_crystal,
            text= None,
            pos=(1, 2),
            offset=((20, 0), (0, 0)))

        self.ch1_button_increase = Button(
            self.frame_temp_crystal,
            text="+",
            command=self.ch1_increase_button_event,
            pos=(1, 3),  # (row, column)
            offset=((10, 0), (0, 0)))  # offset

        self.ch1_button_decrease = Button(
            self.frame_temp_crystal,
            text="-",
            command=self.ch1_decrease_button_event,
            pos=(1, 3),  # (row, column)
            offset=((60, 0), (0, 0)))  # offset

        self.title_ldd = LabelTitle(
            self.tabview.tab(overview),
            text="LDD Power",
            pos=(3, 1))  # (row, column)

        self.ch2_label_av = StdLabel(
            self.frame_temp_diode,
            text=f'Actual Value',
            pos=(0, 0),  # (row, column)
            offset=((5, 0), (0, 0)))  # offset

        self.ch2_label_sp = StdLabel(
            self.frame_temp_diode,
            text=f'Setpoint',
            pos=(0, 2),  # (row, column)
            offset=((20, 0), (0, 0)))  # offset

        self.ch2_temp_av = StdLabel(
            self.frame_temp_diode,
            text= None,
            pos=(1, 0),
            offset=((5, 0), (0, 0)))

        self.ch2_temp_sp = StdLabel(
            self.frame_temp_diode,
            text=f'{self.mt2_tot:.2f}°C',
            pos=(1, 2),
            offset=((20, 0), (0, 0)))

        self.ch2_button_increase = Button(
            self.frame_temp_diode,
            text="+",
            command=self.ch2_increase_button_event,
            pos=(1, 3),  # (row, column)
            offset=((10, 0), (0, 0)))  # offset

        self.ch2_button_decrease = Button(
            self.frame_temp_diode,
            text="-",
            command=self.ch2_decrease_button_event,
            pos=(1, 3),  # (row, column)
            offset=((60, 0), (0, 0)))  # offset

        self.diode_title = LabelTitle(
            self.tabview.tab(overview),
            text="Diode Temperature",
            pos=(0, 2))  # (row, column)

        self.ldd_label_av = StdLabel(
            self.frame_ldd,
            text=f'Actual Value',
            pos=(0, 0),  # (row, column)
            offset=((5, 0), (0, 0)))  # offset

        self.ldd_label_sp = StdLabel(
            self.frame_ldd,
            text=f'Setpoint',
            pos=(0, 2),  # (row, column)
            offset=((20, 0), (0, 0)))  # offset

        self.ldd_label_sp = StdLabel(
            self.frame_ldd,
            text=f'Opt. Power',
            pos=(2, 0),  # (row, column)
            offset=((5, 0), (0, 0)))  # offset

        self.ldd_w_av = StdLabel(
            self.frame_ldd,
            text= None,
            pos=(1, 0),  # (row, column)
            offset=((5, 0), (0, 0)))

        self.ldd_current_av = StdLabel(
            self.frame_ldd,
            text=f'{self.ldd.ldd_get_w():.2f}W',
            pos=(3, 0),
            offset=((5, 0), (0, 0)))

        self.ldd_current_sp = StdLabel(
            self.frame_ldd,
            text= None,
            pos=(1, 2),
            offset=((20, 0), (0, 0)))

        self.ldd_current_increase = Button(
            self.frame_ldd,
            text="+",
            command=self.ldd_increase_button_event,
            pos=(1, 3),  # (row, column)
            offset=((10, 0), (0, 0)))  # offset

        self.ldd_current_decrease = Button(
            self.frame_ldd,
            text="-",
            command=self.ldd_decrease_button_event,
            pos=(1, 3),  # (row, column)
            offset=((60, 0), (0, 0)))  # offset

        self.ldd_settings_features = LabelTitle(
            self.tabview.tab(overview),
            text="LDD Properties",
            pos=(3, 2))  # (row, column)

        self.laser_beam_bar = customtkinter.CTkSwitch(
            self.frame_ldd_config,
            text="Laser Enable",
            switch_height=25,
            switch_width=50)

        self.laser_beam_bar.grid(
            row=0,
            column=0,
            padx=(5, 0),
            pady=(10, 10),
            columnspan=3)

        self.laser_go = Button(
            self.frame_ldd_config,
            text="LASER GO",
            command=self.laser_go_button_event,
            dim=(40, 100),
            pos=(2, 1),  # (row, column)
            offset=((20, 0), (0, 0)))  # offset

        self.laser_nogo = Button(
            self.frame_ldd_config,
            text="LASER STOP",
            command=self.laser_nogo_button_event,
            dim=(40, 100),
            pos=(2, 2),  # (row, column)
            offset=((20, 0), (0, 0)))  # offset

        self.notifications = StdLabel(
            self.frame_notifications,
            text= None,
            pos=(0, 0),  # (row, column)
            offset=((10, 0), (0, 0)))  # offset

        self.ldd_settings_features = LabelTitle(
            self.tabview.tab(settings),
            text="Features",
            pos=(0, 0))  # (row, column)

        self.csv_import = Button(
            self.frame_export_data,
            text="Import table",
            command=self.start_import,
            dim=(40, 100),
            pos=(0, 0),  # (row, column)
            offset=((10, 0), (10, 0)))  # offset

        self.csv_export = Button(
            self.frame_export_data,
            text="Export Data",
            command=self.start_export,
            dim=(40, 100),
            pos=(0, 1),  # (row, column)
            offset=((10, 0), (10, 0)))  # offset

        self.cpu_temp_av_label = StdLabel(
            self.frame_cpu_temp,
            text="CPU Temperature:",
            pos=(0, 0),
            offset=((10, 0), (10, 0)))

        self.cpu_temp_av = StdLabel(
            self.frame_cpu_temp,
            text= None,
            pos=(1, 0),  # (row, column)
            offset=((80, 0), (25, 0)))  # offset

        self.appearance_mode_label = StdLabel(
            self.frame_appearance,
            text="Appearance Mode:",
            pos=(0, 0),
            offset=((10, 0), (10, 0)))

        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(
            self.frame_appearance,
            values=["Light", "Dark"],
            command=self.change_appearance_mode_event,
            height=40,
            width=100)

        self.appearance_mode_optionemenu.grid(
            row=1,
            column=0,
            padx=10,
            pady=(0, 0))

        self.quiter = Button(
            self.frame_shutdown_quit,
            text="Quit",
            command=self.manage_top_lvl_window,
            dim=(40, 100),
            pos=(0, 0),
            offset=((10, 0), (10, 0)))

        self.shut_down = Button(
            self.frame_shutdown_quit,
            text="Shut down",
            command=self.manage_shut_down_window,
            dim=(40, 100),
            pos=(0, 0),
            offset=((130, 0), (10, 0)))

        self.laser_beam_bar.deselect()
        self.csv_import.configure(state="disabled")

    def start_quit_all(self):
        _ = threading.Thread(target=self.quit_all,
                             daemon=True).start()

    def quit_all(self):
        """
        Cold-kill of the program yet, the laser must be shut-down. The
        window shall not be manipulateble anymore.
        """
        self.b_quit_n.configure(state="disabled")
        self.l_quit.configure(text="Quitting...")
        self.laser_beam_bar.deselect()
        self.laser_nogo_button_event()
        time.sleep(4)
        os._exit(0)
    
    def shutter(self):
        self.b_shut_n.configure(state="disabled")
        self.l_shut.configure(text="Shutting down...")
        self.laser_beam_bar.deselect()
        self.laser_nogo_button_event()
        time.sleep(4)
        os.system("sudo shutdown -h 0")

    def start_shut_down(self):
        _ = threading.Thread(target=self.shutter,
                             daemon=True).start()

    def ch1_increase_button_event(self):
        self.mt_1.set_temp(
            self.mt_1.get_data()["target object temperature"][0] + 1.0)

    def ch1_decrease_button_event(self):
        self.mt_1.set_temp(
            self.mt_1.get_data()["target object temperature"][0] - 1.0)

    def ch2_increase_button_event(self):
        self.mt_2.set_temp(
            self.mt_2.get_data()["target object temperature"][0] + 1.0)

    def ch2_decrease_button_event(self):
        self.mt_2.set_temp(
            self.mt_2.get_data()["target object temperature"][0] - 1.0)

    def update_ch1_temp_av(self):  # Crystal
        _temp_av = self.mt_1.get_data()["object temperature"][0]
        self.q_cr_av.put(_temp_av)
        self.array_cr_av = np.insert(
            self.array_cr_av,
            np.shape(self.array_cr_av)[0],
            [time.time(), _temp_av],
            axis=0)
        self.ch1_temp_av.configure(text=f'{self.q_cr_av.get():.2f}°C')
        if self.mt_2.get_data()["device status"][0] != 2 :
            self.frame_temp_crystal.configure(fg_color="red")
        elif self.mt_1.get_data()["temp stable"][0]:
            self.frame_temp_crystal.configure(fg_color="green")
        else:
            self.frame_temp_crystal.configure(fg_color="grey70")
        self.ch1_temp_av.after(1000, self.update_ch1_temp_av)

    def update_ch1_temp_sp(self):  # Crystal
        _temp_sp = self.mt_1.get_data()["target object temperature"][0]
        self.q_cr_sp.put(_temp_sp)
        self.array_cr_sp = np.insert(
            self.array_cr_sp,
            np.shape(self.array_cr_sp)[0],
            [time.time(), _temp_sp],
            axis=0)
        self.ch1_temp_sp.configure(text=f'{self.q_cr_sp.get():.2f}°C')
        self.ch1_temp_sp.after(1000, self.update_ch1_temp_sp)

    def update_ch2_temp_av(self):  # Diode
        _temp_av = self.mt_2.get_data()["object temperature"][0]
        self.q_di_av.put(_temp_av)
        self.array_di_av = np.insert(
            self.array_di_av,
            np.shape(self.array_di_av)[0],
            [time.time(), _temp_av],
            axis=0)
        self.ch2_temp_av.configure(text=f'{self.q_di_av.get():.2f}°C')
        if self.mt_2.get_data()["device status"][0] != 2:
            self.frame_temp_diode.configure(fg_color="red")
        elif self.mt_2.get_data()["temp stable"][0]:
            self.frame_temp_diode.configure(fg_color="green")
        else:
            self.frame_temp_diode.configure(fg_color="grey70")
        self.ch2_temp_av.after(1000, self.update_ch2_temp_av)

    def update_ch2_temp_sp(self):  # Diode
        _temp_sp = self.mt_2.get_data()["target object temperature"][0]
        self.q_di_sp.put(_temp_sp)
        self.array_di_sp = np.insert(
            self.array_di_sp,
            np.shape(self.array_di_sp)[0],
            [time.time(), _temp_sp],
            axis=0)
        self.ch2_temp_sp.configure(text=f'{self.q_di_sp.get():.2f}°C')
        self.ch2_temp_sp.after(1000, self.update_ch2_temp_sp)

    def update_ldd_w_av(self):
        ldd_w = self.ldd.ldd_current_av()
        self.q_ldd_w.put(ldd_w)
        self.array_ldd_w = np.insert(
            self.array_ldd_w,
            np.shape(self.array_ldd_w)[0],
            [time.time(), ldd_w],
            axis=0)
        self.ldd_w_av.configure(text=f'{self.q_ldd_w.get():.2f}A')
        self.ldd_w_av.after(500, self.update_ldd_w_av)

    def update_ldd_current_av(self):
        _ldd_av = self.ldd.ldd_get_w()
        self.q_ldd_av.put(_ldd_av)
        self.array_ldd_av = np.insert(
            self.array_ldd_av,
            np.shape(self.array_ldd_av)[0],
            [time.time(), _ldd_av],
            axis=0)
        self.ldd_current_av.configure(text=f'{self.q_ldd_av.get():.2f}W')
        self.ldd_current_av.after(500, self.update_ldd_current_av)

    def update_ldd_current_sp(self):
        ldd_sp = self.ldd.ldd_get_sp()
        self.q_ldd_sp.put(ldd_sp)
        self.array_ldd_sp = np.insert(
            self.array_ldd_sp,
            np.shape(self.array_ldd_sp)[0],
            [time.time(), ldd_sp],
            axis=0)
        self.ldd_current_sp.configure(text=f'{self.q_ldd_sp.get():.2f}A')
        self.ldd_current_sp.after(50, self.update_ldd_current_sp)

    def ldd_increase_button_event(self):
        self.ldd_current_sp.configure(
            text=f'{self.ldd.ldd_sp_increase()}')

    def ldd_decrease_button_event(self):
        self.ldd_current_sp.configure(
            text=f'{self.ldd.ldd_sp_decrease()}')

    def laser_gonogo_event(self):
        if self.laser_beam_bar.get() == 1:
            self.laser_go.configure(
            fg_color="green")
        else:
            self.laser_go.configure(
                fg_color=('#3B8ED0', '#1F6AA5'))
        self.laser_go.after(10, self.laser_gonogo_event)

    def laser_beam_bar_reset(self):
        """
        Reset the laser beam bar after 5 seconds only if it has been
        activated.
        """
        if self.laser_beam_bar.get() >= 0:
            self.laser_beam_bar.deselect()
            self.laser_beam_bar.after(10000, self.laser_beam_bar_reset)

    def laser_go_button_event(self):
        """
        Start the Laser. The current is going to ramp up until setpoint.
        Take the setpoint from the ldd_control.py file and feed it as an
        argument in to the statement below.
        """
        if self.laser_beam_bar.get() == 1:
            self.ldd.laser_start()
        self.laser_beam_bar_reset()

    def laser_nogo_button_event(self):
        """
        Start the Laser.
        The current ramps down until setpoint
        """
        self.ldd.laser_stop()
        self.laser_beam_bar.deselect()

    def ldd_notifications(self):
        self.notifications.configure(text=f'{self.ldd.A_limit()[0]}')
        self.notifications.after(1000, self.ldd_notifications)

    def start_import(self):
        """
        Import the files with the current to optical power table.
        """
        _ = threading.Thread(target=self.import_data,
                             name="start_import",
                             daemon=True).start()

    def import_data(self):
        """
        Start the thread to import the table.
        """
        pass
        
    def start_export(self):
        """
        Function to start the exporting function indirectly.
        """
        _ = threading.Thread(target=self.export_data,
                             name="start_export",
                             daemon=True).start()

    def export_data(self):
        df_historian_cr_av = pd.DataFrame(
            self.array_cr_av,
            columns=["Time", "Crystal_av"])

        df_audittrail_cr_sp = pd.DataFrame(
            self.array_cr_sp,
            columns=["Time", "Crystal_SP"])

        df_historian_di_av = pd.DataFrame(
            self.array_di_av,
            columns=["Time", "Diode_AV"])

        df_audittrail_di_sp = pd.DataFrame(
            self.array_di_sp,
            columns=["Time", "Diode_SP"])

        df_historian_ldd_av = pd.DataFrame(
            self.array_ldd_av,
            columns=["Time", "LDD_AV"])

        df_audittrail_ldd_sp = pd.DataFrame(
            self.array_ldd_sp,
            columns=["Time", "LDD_SP"])

        df_data_concat = pd.concat(
            [df_historian_cr_av,
            df_audittrail_cr_sp,
            df_historian_di_av,
            df_audittrail_di_sp,
            df_historian_ldd_av,
            df_audittrail_ldd_sp],
            axis=1)

        df_data_concat.to_csv(
            "/home/pi/Desktop/hist_audit.csv",
            sep=",")

    def change_appearance_mode_event(self,
                                     new_appearance_mode: str) -> None:
        customtkinter.set_appearance_mode(new_appearance_mode)

    def cpu_temp(self) -> None:
        self.cpu_temp_av.configure(
            text=f'{CPUTemperature().temperature:.2f}°C')
        self.cpu_temp_av.after(1000, self.cpu_temp)

    def manage_top_lvl_window(self) -> None:
        def window_withdraw():
            self.quit_lvl_window.withdraw()

        if self.toplevel_window is None:

            self.quit_lvl_window = customtkinter.CTkToplevel(self)
            self.quit_lvl_window.geometry("800x480")
            # self.quit_lvl_window.overrideredirect(True)

            self.l_quit = customtkinter.CTkLabel(self.quit_lvl_window,
                                                text="Quit?")
            self.l_quit.pack(padx=20, pady=20)

            _b_quit_y = customtkinter.CTkButton(self.quit_lvl_window,
                                                   text="Yes",
                                                   command=self.start_quit_all)
            _b_quit_y.pack(padx=50, pady=20)

            self.b_quit_n = customtkinter.CTkButton(self.quit_lvl_window,
                                                   text="No",
                                                   command=window_withdraw)
            self.b_quit_n.pack(padx=50, pady=100)
        elif self.quit_lvl_window.state() == "iconic" \
            or self.quit_lvl_window.state() == "withdrawn":
            self.quit_lvl_window.deiconify()
        else:
            self.quit_lvl_window.focus()

    def manage_shut_down_window(self) -> None:
        def window_withdraw():
            self.shut_down_window.withdraw()

        if self.shut_down_window is None:
            self.shut_down_window = customtkinter.CTkToplevel(self)
            self.shut_down_window.geometry("800x480")
            # self.shut_down_window.overrideredirect(True)

            self.l_shut = customtkinter.CTkLabel(self.shut_down_window,
                                             text="Shut down?")
            self.l_shut.pack(padx=20, pady=20)

            _b_quit_y = customtkinter.CTkButton(self.shut_down_window,
                                                text="Yes",
                                                command=self.start_shut_down)
            _b_quit_y.pack(padx=50, pady=20)

            self.b_shut_n = customtkinter.CTkButton(self.shut_down_window,
                                                text="No",
                                                command=window_withdraw)
            self.b_shut_n.pack(padx=50, pady=100)
        elif self.shut_down_window.state() == "iconic" \
            or self.shut_down_window.state() == "withdrawn":
            self.shut_down_window.deiconify()
        else:
            self.shut_down_window.focus()

    def update_gui(self) -> None:
        self.update_ch1_temp_av()
        self.update_ch1_temp_sp()
        self.update_ch2_temp_av()
        self.update_ch2_temp_sp()
        self.update_ldd_current_sp()
        self.update_ldd_current_av()
        self.update_ldd_w_av()
        self.cpu_temp()
        self.laser_gonogo_event()
        self.ldd_notifications()
        self.laser_beam_bar_reset()


if __name__ == "__main__":

    # Initialising the GUI
    app = GUI()
    
    # Initiating the thread to the main thread
    threaded_task = threading.Thread(target=app.update_gui,
                                     daemon=True).start()

    # Starting the mainloop of the GUI
    app.mainloop()
