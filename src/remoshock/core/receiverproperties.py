#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________


class ReceiverProperties:
    """properties of a receiver such as name and capabilities"""

    def __init__(self,
                 receiver_type, name="receiver", color="#FFF",
                 action_light=False, action_beep=False, action_vibrate=False, action_shock=False,
                 duration_min_ms=500, duration_increment_ms=250,
                 awake_time_s=0):
        """
        creates a ReceiverProperties object

        @param receiver_type type of receiver
        @param name name of the receiver as displayed on the web remote control
        @param color color of the receiver used by the web remote control
        @param action_light does this receiver support light?
        @param action_beep does this receiver support beep sounds?
        @param action_vibrate does this receiver support vibrations?
        @param action_shock does this receiver support shocks?
        @param duration_min_ms minimum duration of a shock in milliseconds
        @param duration_increment_ms duration increment for shocks in milliseconds
        @param awake_time_s how long does the receiver stay aware without receiving a message
                                (0: indefinite, no keep awake messages required)
        """

        self.receiver_type = receiver_type
        self.name = name
        self.color = color

        self.action_light = action_light
        self.action_beep = action_beep
        self.action_vibrate = action_vibrate
        self.action_shock = action_shock

        self.duration_min_ms = duration_min_ms
        self.duration_increment_ms = duration_increment_ms

        self.awake_time_s = awake_time_s


    def capabilities(self, action_light=False, action_beep=False, action_vibrate=False, action_shock=False):
        """
        sets the capabilities of this receiver

        @param action_light does this receiver support light?
        @param action_beep does this receiver support beep sounds?
        @param action_vibrate does this receiver support vibrations?
        @param action_shock does this receiver support shocks?
        """
        self.action_light = action_light
        self.action_beep = action_beep
        self.action_vibrate = action_vibrate
        self.action_shock = action_shock


    def timings(self, duration_min_ms=500, duration_increment_ms=250, awake_time_s=0):
        """
        sets the timing characteristics of this receiver

        @param duration_min_ms minimum duration of a shock in milliseconds
        @param duration_increment_ms duration increment for shocks in milliseconds
        @param awake_time_s how long does the receiver stay aware without receiving a message
                                (0: indefinite, no keep awake messages required)
        """
        self.duration_min_ms = duration_min_ms
        self.duration_increment_ms = duration_increment_ms

        self.awake_time_s = awake_time_s
