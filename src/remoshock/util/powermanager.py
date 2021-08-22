#
# Copyright nilswinter 2020-2021. License: AGPL
# _____________________________________________


def inhibit():
    """tries to inhibit automatic power save mode (hibernation).

    This will not prevent a user from manually going into hibernation.
    The inhibiter will be automatically cleared when the process ends"""

    successful = False
    try:
        import dbus

        try:
            proxy = dbus.SessionBus().get_object("org.freedesktop.PowerManagement", "/org/freedesktop/PowerManagement")
            pm = dbus.Interface(proxy, 'org.freedesktop.PowerManagement')
            pm.Inhibit("remoshock", "playing...")
            successful = True
        except:  # noqa: E722
            pass

        try:
            proxy = dbus.SessionBus().get_object("org.freedesktop.ScreenSaver", "/ScreenSaver")
            screenSaver = dbus.Interface(proxy, 'org.freedesktop.ScreenSaver')
            screenSaver.Inhibit("remoshock", "playing...")

            proxy = dbus.SessionBus().get_object("org.gnome.SessionManager", "/org/gnome/SessionManager")
            sessionManager = dbus.Interface(proxy, 'org.gnome.SessionManager')
            sessionManager.Inhibit("remoshock", 0, "playing...", 8)
            successful = True
        except:  # noqa: E722
            pass

    except:  # noqa: E722
        pass

    if not successful:
        print("Please disable power save mode in your operating system settings,")
        print("to prevent your computer from going into hibernation after a certain period without user interaction.")
