from __future__ import print_function

import sys
import time
import numpy as np
import pandas as pd

from pixtendv2l import PiXtendV2L


class ldd_control:
    """
    Class to control the behavior of the PiXtend PLC. Get and set
    information and parameters.
    """
    def __init__(self):
        self.laser_start_bit: bool = 0
        self.ldd_current_sp: float = 0.1
        self.bit_keeper: int = 0

        self.c2p = pd.read_csv(
            "/home/pi/Desktop/folder_bak_edit_oop/ldd_current2power.csv"
        ).to_numpy()

        self.a2c = pd.read_csv(
            "/home/pi/Desktop/folder_bak_edit_oop/ldd_ang2current.csv"
        ).to_numpy()

        self.p = PiXtendV2L()
        if self.p != PiXtendV2L():
            self.p = PiXtendV2L()

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
        self.ldd_current_sp += 0.01

    def ldd_sp_decrease(self):
        """
        Decrease the current setpoint by 0.1A
        """
        if self.ldd_current_sp >= 0.1:
            self.ldd_current_sp -= 0.01

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
        return ((down_right-up_right)/(down_left-up_left))* \
            (actual_value-up_left)+up_right

    def ldd_get_w(self):
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
            _ldd_current = self.p.analog_in0

            if _ldd_current == 0:
                return 0
            else:
                y, x = np.where(self.c2p <= _ldd_current)
                _up_left = self.c2p[y[-1], x[-1]]
                _up_right = self.c2p[y[-1], x[-1]+1]
                _down_left = self.c2p[y[-1]+1, x[-1]]
                _down_right = self.c2p[y[-1]+1, x[-1]+1]

                _opt_power_av = self.interpol(
                    _up_left,
                    _up_right,
                    _down_left,
                    _down_right,
                    _ldd_current
                )
                return _opt_power_av

        except(
            IOError,
            ValueError,
            RuntimeError,
            KeyboardInterrupt
        ):
            self.p.close()
            time.sleep(1)
            del self.p
            self.p = None

    def ldd_current_av(self):
        try:
            _ldd_current = self.p.analog_in0

            if _ldd_current == 0:
                return 0
            else:
                y, x = np.where(self.a2c <= _ldd_current)
                _up_left = self.a2c[y[-1], x[-1]]
                _up_right = self.a2c[y[-1], x[-1]+1]
                _down_left = self.a2c[y[-1]+1, x[-1]]
                _down_right = self.a2c[y[-1]+1, x[-1]+1]

                _ldd_current_av = self.interpol(
                    _up_left,
                    _up_right,
                    _down_left,
                    _down_right,
                    _ldd_current
                )

                return float(_ldd_current_av )

        except(
            IOError,
            ValueError,
            RuntimeError,
            KeyboardInterrupt
        ):
            self.p.close()
            time.sleep(1)
            del self.p
            self.p = None


    def A_limit(self):
        """
        Check if the limit of the current/voltage has not been exeeded.
        Status on the overview window.
        """
        if round(self.ldd_current_sp, 3) > 0.8:
            return "Diode current above 0.8A", False
        elif round(self.ldd_current_sp) < 0:
            return "User input too low", False
        elif round(self.ldd_current_av(), 3) > 0:
            return "Laser running...", True
        else:
            return "Laser ready...", True

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

    def laser_start(self):
        """
        Laser ignition / start -> Depending on the prerequesites of the
        methods above (A_calc, A_limit, A_ramper)
        """
        if self.A_limit()[1]:
            try:
                self.p.set_dac_output(
                        self.p.DAC_B, 1023
                )
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
                    time.sleep(0.25)
                self.laser_start_bit = 1

            except(
                    IOError,
                    ValueError,
                    RuntimeError,
                    KeyboardInterrupt
            ):
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
                self.p.set_dac_output(
                        self.p.DAC_B, 0
                )
                for ramps in np.linspace(
                    self.bit_keeper,
                    0,
                    num=10,
                    endpoint=True
                ):
                    self.current = self.p.set_dac_output(
                        self.p.DAC_A, int(ramps)
                    )
                    time.sleep(0.25)
                self.laser_start_bit = 0

            except(
                    IOError,
                    ValueError,
                    RuntimeError,
                    KeyboardInterrupt
            ):
                self.p.close()
                time.sleep(0.5)
                del self.p
                self.p = None

    def ldd_test(self):
        if self.p is not None:
            is_config = False
            cycle_counter = 0
            while True:
                try:
                    if self.p.crc_header_in_error is False \
                    and self.p.crc_data_in_error is False:
                        cycle_counter += 1
                        if not is_config:
                            is_config = True
                            self.p.relay0 = self.p.ON
                            self.p.digital_out0 = self.p.ON
                    else:
                        self.p.relay0 = self.p.OFF
                        self.p.digital_out0 = self.p.OFF
                        time.sleep(1)
                        self.p.close()
                        del self.p
                        self.p = None
                        break

                except(
                    IOError,
                    ValueError,
                    RuntimeError,
                    KeyboardInterrupt
                ):
                    self.p.close()
                    time.sleep(1)
                    del self.p
                    self.p = None
                    break


if __name__ == "__main__":
    """
    Arbitrary testing sequences
    """
    print(ldd_control())
