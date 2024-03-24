from __future__ import print_function

import sys
import time
import numpy as np
import pandas as pd

from pixtendv2l import PiXtendV2L


class ldd_control:
    """
    Class to control the whole behavior of the PiXtend PLC. Get and set
    information and parameters.
    """
    def __init__(self):
        # Initialization of misc. variables
        self.laser_start_bit: bool = 0
        self.ldd_current_sp: float = 0.1
        self.bit_keeper: int = 0
        self.case_dict: dict = {
            "100": "Diode current above 1.5A",
            "101": "Diode current below 0A",
            "102": "Laser running...",
            "103": "Laser Ready...",
            "104": "Laser Ramping-Up",
        }

        # Read the curernt2power table once. The whole path is needed as
        # automatic start would not recognize the file location.
        self.c2p = pd.read_csv(
            "/home/pi/Desktop/folder_bak_edit/ldd_current2power.csv"
        ).to_numpy()  # Directly convert the table into an numpy array

        # Initialization of the PLC (PiXtend)
        self.p = PiXtendV2L()
        if self.p != PiXtendV2L():
            self.p = PiXtendV2L()

    # configuration of the setpoint (sp) of the LDD Current
    def ldd_get_sp(self):
        """
        Return the setpoint of the setting the user has choosen on the
        HMI.
        """
        return self.ldd_current_sp

    def ldd_sp_increase(self):
        """
        Increase the current setpoint by 0.1A
        """
        self.ldd_current_sp += 0.1

    def ldd_sp_decrease(self):
        """
        Decrease the current setpoint by 0.1A
        """
        if self.ldd_current_sp >= 0.1:
            self.ldd_current_sp -= 0.1

    def interpol(
        self,
        up_left: float,
        up_right: float,
        down_left: float,
        down_right: float,
        actual_value: float) -> float:
        """
        A non-general inear interpolation of values taking four values.
        This interpolation works for values with a lower bound at 0.
        """
        return (down_right-up_right)/(down_left-up_left)* \
            (actual_value-up_left)+down_left

    # Configuration of the actual value of the laser
    def ldd_get_av(self):
        """
        Try to get the current information from the PiXtend PLC.
        "try" method is in place if an abortion/error occures in the
        pulling process. This actual values is being searched for in a
        list of corresponding values to evaluate the optical power of
        the osciallator. The current2power table in the file location
        needs to be edited manually and the name of the file containing
        the table must be named "ldd_current2power.csv" otherwise error.
        """
        try:
            # ldd_current = self.p.analog_in0  # For the act. current in
            ldd_current = 0.125  # Dummy variable
            array_y, array_x = np.where(self.c2p <= ldd_current)
            # print(self.c2p[array_y[-1]:array_y[-1]+1, array_x[-1]:array_x[-1]+1])
            up_left = self.c2p[array_y[-1], array_x[-1]]
            up_right = self.c2p[array_y[-1], array_x[-1]+1]
            down_left = self.c2p[array_y[-1]+1, array_x[-1]]
            down_right = self.c2p[array_y[-1]+1, array_x[-1]+1]

            opt_power_av = self.interpol(
                up_left,
                up_right,
                down_left,
                down_right,
                ldd_current
            )
            
            return opt_power_av
            # return self.c2p[array_y[-1], array_x[-1]+1]

        except(
            IOError,
            ValueError,
            RuntimeError,
            KeyboardInterrupt
        ):
            print("Error Handler Active")
            self.p.close()
            time.sleep(1)
            del self.p
            self.p = None

    def A_limit(self):  # , case: str
        """
        Check if the limit of the current/voltage has not been exeeded.
        Status on the overview window.
        """
        if round(self.ldd_current_sp, 3) > 1.5:
            return "Diode current above 1.5A", False  # Case 100
        elif round(self.ldd_current_sp) < 0:
            return "User input too low", False  # Case 101
        elif round(self.ldd_get_av()) > 0 and self.laser_start_bit == 1:
            return "Laser running...", True  # Case 102
        else:
            return "Laser Ready...", True  # Case 103

    # Configuration of laser ignition prerequisites current / voltage
    def A_ramper(self):
        """
        Method to ramp the laser output if it already has started and
        does not start from 0.
        """
        if self.laser_start_bit == 0:
            self.A_limit()[1]

    def A_bits(self):
        """
        Calculate the the output voltage / current bits for the analog
        output. 0 is 0V/0A 1023 is 5V/1.5A MAX of the spec. LDD. Limit
        must be set to 0.8A due to the possible destruction of the la-
        ser diode
        """
        return 511 / 1.5 * self.ldd_current_sp

    # Configurations of start / stop the laser depending on the 
    def laser_start(self):
        """
        Laser ignition / start -> Depending on the prerequesites of the
        methods above (A_calc, A_limit, A_ramper)
        """
        if self.A_limit()[1]:
            try:
                # self.p.set_dac_output(
                #         self.p.DAC_B, 1023
                # )
                for ramps in np.linspace(
                    self.bit_keeper,
                    self.A_bits(),
                    num=10,
                    endpoint=True
                ):
                    self.current = self.p.set_dac_output(
                        self.p.DAC_A, int(ramps)
                    )
                    self.bit_keeper = self.A_bits()
                    # print(int(ramps), self.A_bits())
                    time.sleep(0.25)
                self.laser_start_bit = 1
                print(self.laser_start_bit)
                    

            except(
                    IOError,
                    ValueError,
                    RuntimeError,
                    KeyboardInterrupt
            ):
                    print("Error Handler Active")
                    self.p.close()
                    time.sleep(0.5)
                    del self.p
                    self.p = None

    def laser_stop(self):
        """
        Laser stop -> ramps down the current of the ldd. Beginning at
        the latest started current value.
        """
        if self.A_bits() != 0:
            try:
                # self.p.set_dac_output(
                #         self.p.DAC_B, 0
                # )
                for ramps in np.linspace(
                    self.bit_keeper,
                    # self.A_bits(),
                    0,
                    num=10,
                    endpoint=True
                ):
                    self.current = self.p.set_dac_output(
                        self.p.DAC_A, int(ramps)
                    )
                    # print(ramps)
                    time.sleep(0.25)
                self.laser_start_bit = 0
                print(self.laser_start_bit)                    

            except(
                    IOError,
                    ValueError,
                    RuntimeError,
                    KeyboardInterrupt
            ):
                print("Error Handler Active")
                self.p.close()
                time.sleep(0.5)
                del self.p
                self.p = None

    def ldd_test(self):
        print(self.p)
        if self.p is not None:
            # Set some variables needed in the main loop
            is_config = False
            cycle_counter = 0
            while True:
                try:
                    # Check if SPI communication is running and the re-
                    # ceived data is correct
                    if self.p.crc_header_in_error is False and self.p.crc_data_in_error is False:
                        cycle_counter += 1
                        if not is_config:
                            is_config = True
                            self.p.relay0 = self.p.ON
                            self.p.digital_out0 = self.p.ON
                        # Toggle the relays and digital outputs on and off
                        # self.p.relay0 = not self.p.relay0
                        # self.p.digital_out0 = not self.p.digital_out0
                    else:
                        self.p.relay0 = self.p.OFF
                        self.p.digital_out0 = self.p.OFF
                        time.sleep(1)
                        self.p.close()
                        del self.p
                        self.p = None
                        break

                # Catch errors and if an error is caught, leave the program
                except(
                    IOError,
                    ValueError,
                    RuntimeError,
                    KeyboardInterrupt
                ):
                    print("Error Handler Active")
                    self.p.close()
                    time.sleep(1)
                    del self.p
                    self.p = None
                    break


if __name__ == "__main__":
    from gui_custom import GUI
    import threading

    # Initialising the GUI
    app = GUI()
    
    # Initiating the thread to the main thread
    threaded_task = threading.Thread(target=app.update_gui,
            daemon=True
    ).start()

    # Starting the mainloop of the GUI
    app.mainloop()
