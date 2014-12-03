#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
""" This module contains all programs (major modes) used by the guidance computer.
"""
#  This file is part of basaGC (https://github.com/cashelcomputers/basaGC),
#  copyright 2014 Tim Buchanan, cashelcomputers (at) gmail.com
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
#  Includes code and images from the Virtual AGC Project (http://www.ibiblio.org/apollo/index.html)
#  by Ronald S. Burkey <info@sandroid.org>
from basagc import hohmann_transfer

import utils
import config
from telemachus import get_telemetry, KSPNotConnected
from basagc.burn import Burn

gc = None
dsky = None


class Program(object):

    """ Major mode base class.
    """

    def __init__(self, description, number):

        """ Class constructor.
        :param description: description of the program
        :param number: program number
        :return: None
        """

        self.description = description
        self.number = number

    def execute(self):

        """ Executes the program.
        :return: None
        """

        utils.log("Executing Program {}: {}".format(self.number, self.description))
        dsky.flash_comp_acty()
        dsky.control_registers["program"].display(self.number)
        # gc.running_programs.append(self)
        gc.active_program = self

    def terminate(self):

        """Terminates the program"""

        # gc.running_programs.remove(self)
        if gc.active_program == self:
            gc.active_program = None
        raise ProgramTerminated

    def restart(self):

        """ Restarts the program if required by program alarms.
        :return: None
        """

        # self.terminate()
        self.execute()


class Program00(Program):

    """ AGC Idling.
    :return: None
    """

    def __init__(self):

        """ Class constructor.
        :return: None
        """

        super(Program00, self).__init__(description="AGC Idling", number="00")

    def execute(self):

        """ Executes the program.
        :return: None
        """

        super(Program00, self).execute()
        dsky.control_registers["program"].display("00")

# class Program01(Program):
#     def __init__(self, name, number):
#         super(Program01, self).__init__(name=, number)
#
#     def execute(self):
#         super(Program01, self).execute()
#         log.info("Program 01 executing")
#         dsky.annunciators["no_att"].on()


class Program11(Program):

    """ Earth Orbit Insertion Monitor.
    :return: None
    """

    def __init__(self):

        """ Class constructor.
        :return: None
        """

        super(Program11, self).__init__(description="Earth Orbit Insertion Monitor", number="11")

    def execute(self):

        """ Executes the program.
        :return: None
        """

        super(Program11, self).execute()
        utils.log("Program 11 executing", log_level="INFO")

        # test if KSP is connected
        try:
            get_telemetry("universalTime")
        except KSPNotConnected:
            self.terminate()
            return

        # --> call average G integration with ΔV integration
        gc.run_average_g_routine = True

        # --> terminate gyrocompassing
        if "02" in gc.running_programs:
            gc.programs["02"].terminate()

        # --> compute initial state vector
        # gc.routines["average_g"]()

        # --> Display on DSKY:
        # --> V06 N62 (we are going to use V16N62 though, so we can have a updated display
        # --> R1: Velocity
        # --> R2: Rate of change of vehicle altitude
        # --> R3: Vehicle altitude in km to nearest .1 km
        gc.execute_verb(verb="16", noun="62")


class Program15(Program):

    """ TMI Initiate/Cutoff
    :return: None
    """

    def __init__(self):

        """ Class constructor.
        :return: None
        """
        # sequence of events:
        # V37E15E
        # Flashing V01N30 displays target octal ID
        # PRO to accept, V21 to change
        # Display blanks for 5 seconds at TIG - 105 seconds
        # Display V16N95
        # at TIG - 10 seconds: Flashing V99
        # if proceed: execute maneuver

        # FIXME: this program should only *calculate* the maneuver, the actual execution of the burn should be
        # FIXME: performed by P40

        # TODO: scale final altitude based on crafts TWR
        # TODO: request twr from user

        super(Program15, self).__init__(description="TMI Initiate/Cutoff", number="15")
        self.delta_v_first_burn = 0.0
        self.delta_v_second_burn = 0.0
        self.time_to_transfer = 0.0
        self.orbiting_body = None
        self.phase_angle_required = 0.0
        self.time_of_ignition_first_burn = 0.0
        self.time_of_ignition_second_burn = 0.0
        self.delta_time_to_burn = 0.0
        self.phase_angle_difference = 0.0
        self.target_octal_id = ""
        self.departure_body = get_telemetry("body")
        self.departure_altitude = 0
        self.destination_altitude = 0
        self.grav_param = 0.0
        self.orbital_period = 0
        self.departure_body_orbital_period = 0
        self.is_display_blanked = False
        self.first_burn = None
        self.second_burn = None

    def terminate(self):

        utils.log("Removing burn data", log_level="DEBUG")
        gc.burn_data.remove(self.first_burn)
        gc.burn_data.remove(self.second_burn)
        super(Program15, self).terminate()


    def calculate_maneuver(self):

        """ Calculates the maneuver parameters and creates a Burn object
        :return: Nothing
        """

        # load target
        target = config.OCTAL_BODY_NAMES[self.target_octal_id]
        target_apoapsis = get_telemetry("body_ApA", body_number=config.TELEMACHUS_BODY_IDS[target])

        # set destination altitude
        self.destination_altitude = target_apoapsis # + 100000
        # if target == "Mun":
        #     self.destination_altitude = 12750000

        # obtain parameters to calculate burn
        self.departure_altitude = get_telemetry("altitude")
        self.orbital_period = get_telemetry("period")
        self.departure_body_orbital_period = get_telemetry("body_period", body_number=config.TELEMACHUS_BODY_IDS[
            "Kerbin"])
        self.grav_param = get_telemetry("body_gravParameter", body_number=config.TELEMACHUS_BODY_IDS[
            self.orbiting_body])
        current_phase_angle = get_telemetry("body_phaseAngle", body_number=config.TELEMACHUS_BODY_IDS[target])

        # calculate the first and second burn Δv parameters
        self.delta_v_first_burn, self.delta_v_second_burn = hohmann_transfer.delta_v(self.departure_altitude,
                                                                                     self.destination_altitude)

        # calculate the time to complete the Hohmann transfer
        self.time_to_transfer = hohmann_transfer.time_to_transfer(self.departure_altitude, self.destination_altitude,
                                                                  self.grav_param)

        # calculate the correct phase angle for the start of the burn
        # note that the burn impulse is calculated as a instantaneous burn, to be correct the burn should be halfway
        # complete at this calculated time

        self.phase_angle_required = hohmann_transfer.phase_angle(self.departure_altitude, self.destination_altitude,
                                                                     self.grav_param)

        # calculate the current difference in phase angle required and current phase angle
        self.phase_angle_difference = current_phase_angle - self.phase_angle_required
        if self.phase_angle_difference < 0:
            self.phase_angle_difference = 180 + abs(self.phase_angle_difference)

        # calculate time of ignition (TIG)
        self.delta_time_to_burn = self.phase_angle_difference / ((360 / self.orbital_period) -
                                                                 (360 / self.departure_body_orbital_period))

        # if the time of ignition is less than 120 seconds in the future, schedule the burn for next orbit
        if self.delta_time_to_burn <= 120:
            utils.log("Time of ignition less that 2 minutes in the future, starting burn during next orbit")
            self.delta_time_to_burn += get_telemetry("period")

        # convert the raw value in seconds to HMS
        delta_time = utils.seconds_to_time(self.delta_time_to_burn)

        # log the maneuver calculations
        utils.log("P15 calculations:")
        utils.log("Phase angle: {}, Δv for burn: {} m/s, time to transfer: {}".format(
            round(self.phase_angle_required, 2),
            int(self.delta_v_first_burn),
            utils.seconds_to_time(self.time_to_transfer)))
        utils.log("Current Phase Angle: {}, difference: {}".format(
            current_phase_angle,
            self.phase_angle_difference))
        utils.log("Time to burn: {} hours, {} minutes, {} seconds".format(
            int(delta_time["hours"]),
            int(delta_time["minutes"]),
            delta_time["seconds"]))

        # calculate the Δt from now of TIG for both burns
        self.time_of_ignition_first_burn = get_telemetry("missionTime") + self.delta_time_to_burn
        self.time_of_ignition_second_burn = self.time_of_ignition_first_burn + self.time_to_transfer

        # create a Burn object for the outbound burn
        self.first_burn = Burn(delta_v=self.delta_v_first_burn,
                              direction="prograde",
                              time_of_ignition=self.time_of_ignition_first_burn)

        # create a Burn object for the outbound burn
        self.second_burn = Burn(delta_v=self.delta_v_second_burn,
                                direction="retrograde",
                                time_of_ignition=self.time_of_ignition_second_burn)

        # load the Burn objects into computer
        gc.load_burn(self.first_burn)
        gc.load_burn(self.second_burn)

        # display burn parameters and finish
        gc.execute_verb(verb="06", noun="95")

    # def recalculate_maneuver(self):
    #
    #     """ This function is to be placed in the GC main loop to recalculate maneuver parameters.
    #     :return: nothing
    #     """
    #
    #     # update orbital altitude
    #     self.departure_altitude = get_telemetry("altitude")
    #
    #     # update current phase angle
    #     telemachus_body_id = config.TELEMACHUS_BODY_IDS[config.OCTAL_BODY_NAMES[self.target_octal_id]]
    #     current_phase_angle = get_telemetry("body_phaseAngle",
    #                                         body_number=telemachus_body_id)
    #
    #     # recalculate phase angle difference
    #     phase_angle_difference = current_phase_angle - self.phase_angle_required
    #     if phase_angle_difference < 0:
    #         phase_angle_difference = 180 + abs(phase_angle_difference)
    #     self.delta_time_to_burn = phase_angle_difference / ((360 / self.orbital_period) - (360 /
    #                                                                                 self.departure_body_orbital_period))
    #     delta_time = utils.seconds_to_time(self.delta_time_to_burn)
    #     velocity_at_cutoff = get_telemetry("orbitalVelocity") + self.delta_v_first_burn
    #     self.first_burn.delta_v =
    #     # gc.noun_data["95"] = [
    #     #     delta_time,
    #     #     self.delta_v_first_burn,
    #     #     velocity_at_cutoff,
    #     # ]


    def check_orbital_parameters(self):

        """ Checks to see if current orbital parameters are within an acceptable range to plot maneuver
        :return: Bool
        """

        # check if orbit is circular
        if get_telemetry("eccentricity") > 0.001:
            gc.poodoo_abort(224)
            return False

        # check if orbit is excessively inclined
        target_inclination = float(get_telemetry("target_inclination"))
        vessel_inclination = get_telemetry("inclination")
        if (vessel_inclination > (target_inclination - 0.5)) and (vessel_inclination > (target_inclination + 0.5)):
            gc.poodoo_abort(225)
            return False
        else:
            return True

    def check_target(self):

        """Checks if a target exists, it not, returns the default target, else returns the selected target number
        Returns: octal target code
        :rtype: str

        """

        if get_telemetry("target_name") == u"No Target Selected.":
            utils.log("No target selected in KSP, defaulting to Mun", log_level="WARNING")
            return config.OCTAL_BODY_IDS["Mun"].zfill(5)
        else:
            return config.OCTAL_BODY_IDS[get_telemetry("target_name")].zfill(5)

    def execute(self):

        """ Executes the program.
        :return: None
        """

        super(Program15, self).execute()
        self.orbiting_body = get_telemetry("body")

        if not self.check_orbital_parameters():
            return
        gc.noun_data["30"] = self.check_target()
        self.target_octal_id = self.check_target()
        gc.execute_verb(verb="01", noun="30")
        gc.dsky.request_data(requesting_object=self.accept_target_input, display_location=dsky.registers[1],
                             is_proceed_available=True)

    def accept_target_input(self, target):

        """ Called by P15 after user as entered target choice.
        :param target: string of octal target code
        :return: None
        """

        if target == "proceed":
            self.target_octal_id = self.target_octal_id.lstrip("0")
        elif target[0] == ("+" or "-"):
            dsky.operator_error("Expected octal input, decimal input provided")
            self.execute()
            return
        elif target not in config.OCTAL_BODY_IDS.values():
            utils.log("{} {} is not a valid target".format(target, type(target)))
            gc.poodoo_abort(223, message="Target not valid")
            return
        else:
            self.target_octal_id = target.lstrip("0")
        # calculate the maneuver and add recalculation job to gc main loop
        self.calculate_maneuver()
        # gc.loop_items.append(self.recalculate_maneuver)
        gc.loop_items.append(self.first_burn._coarse_start_time_monitor)
        gc.execute_verb(verb="16", noun="95")


        #gc.poodoo_abort(310)
        # gc.execute_verb(verb=16, noun=79)
        # gc.set_attitude("prograde")


class ProgramNotImplementedError(Exception):

    """ This exception is raised when the selected program hasn't been implemented yet.
    """

    pass


class ProgramTerminated(Exception):

    """ This exception is raised when a program self-terminates.
    """

    pass
