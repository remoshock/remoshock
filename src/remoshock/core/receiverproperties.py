#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________


class ReceiverProperties:
    """properties of a receiver such as name and capabilities"""

    def __init__(self,
                 receiver_type, name="receiver", color="#FFF",
                 action_light=False, action_beep=False, action_vibrate=False, action_shock=False,
                 duration_min_ms=500, duration_increment_ms=250,
                 awake_time_s=0,
                 beep_shock_delay_ms=1000,
                 limit_shock_max_duration_ms=1000,
                 limit_shock_max_power_percent=100,
                 random_probability_weight=None,
                 random_shock_min_duration_ms=None,
                 random_shock_max_duration_ms=None,
                 random_shock_min_power_percent=None,
                 random_shock_max_power_percent=None,
                 ):
        """
        creates a ReceiverProperties object

        @param receiver_type   type of receiver
        @param name            name of the receiver as displayed on the web remote control
        @param color           color of the receiver used by the web remote control
        @param action_light    does this receiver support light?
        @param action_beep     does this receiver support beep sounds?
        @param action_vibrate  does this receiver support vibrations?
        @param action_shock    does this receiver support shocks?
        @param duration_min_ms minimum  shortest duration of a shock in milliseconds supported by hardware
        @param duration_increment_ms    duration increment for shocks in milliseconds
        @param awake_time_s how long does the receiver stay aware without receiving a message
                                (0: indefinite, no keep awake messages required)
        @param beep_shock_delay_ms            delay between beep and shock for Action.BEEPSHOCK
        @param limit_shock_max_duration_ms    hard limit for shock duration
        @param limit_shock_max_power_percent  hard limit for shock power
        @param random_probability_weight      randomizer setting to weight probability
        @param random_shock_min_duration_ms   randomizer setting for this device: minimal duration of a shock
        @param random_shock_max_duration_ms   randomizer setting for this device: maximal duration of a shock
        @param random_shock_min_power_percent randomizer setting for this device: minimal power of a shock
        @param random_shock_max_power_percent randomizer setting for this device: maximal power of a shock
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

        self.beep_shock_delay_ms = beep_shock_delay_ms
        self.limit_shock_max_duration_ms = limit_shock_max_duration_ms
        self.limit_shock_max_power_percent = limit_shock_max_power_percent

        self.random_probability_weight = random_probability_weight
        self.random_shock_min_duration_ms = random_shock_min_duration_ms
        self.random_shock_max_duration_ms = random_shock_max_duration_ms
        self.random_shock_min_power_percent = random_shock_min_power_percent
        self.random_shock_max_power_percent = random_shock_max_power_percent


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
