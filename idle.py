#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

from gi.repository import Gio, GLib

BUS_NAME = 'se.yeager.Levande.Idle'
IDLE_INTERFACE = 'org.gnome.Mutter.IdleMonitor'


class IdleLauncher:
    def __init__(self):
        self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        reply = self.bus.call_sync('org.freedesktop.DBus', '/org/freedesktop/DBus',
                                   'org.freedesktop.DBus', 'RequestName',
                                   GLib.Variant('(su)', (BUS_NAME, 4)),
                                   GLib.VariantType.new('(u)'), 0, -1, None)
        if reply.unpack()[0] != 1:
            raise RuntimeError('Idle service is already running')
        self.monitor = Gio.DBusProxy.new_sync(self.bus, 0, None, 'org.gnome.Mutter.IdleMonitor',
                                               '/org/gnome/Mutter/IdleMonitor/Core', IDLE_INTERFACE, None)
        self.screen = Gio.DBusProxy.new_sync(self.bus, 0, None, 'org.gnome.ScreenSaver',
                                              '/org/gnome/ScreenSaver', 'org.gnome.ScreenSaver', None)
        self.session = Gio.Settings.new('org.gnome.desktop.session')
        self.process = None
        self.idle_watch = 0
        self.active_watch = 0
        self.monitor.connect('g-signal', self.on_monitor_signal)
        self.screen.connect('g-signal', self.on_screen_signal)
        self.session.connect('changed::idle-delay', lambda *_: self.schedule())
        self.schedule()

    def remove_watch(self, name):
        watch = getattr(self, name)
        if watch:
            self.monitor.call_sync('RemoveWatch', GLib.Variant('(u)', (watch,)), 0, -1, None)
            setattr(self, name, 0)

    def schedule(self):
        self.remove_watch('idle_watch')
        delay = self.session.get_uint('idle-delay')
        if delay == 0:
            return
        # Keep the existing GNOME lock schedule. Show the animation during
        # the final minute before the session becomes idle.
        interval = max(1, delay - 60) * 1000
        self.idle_watch = self.monitor.call_sync('AddIdleWatch', GLib.Variant('(t)', (interval,)), 0, -1, None).unpack()[0]

    def stop_animation(self):
        if self.process is not None:
            if self.process.poll() is None:
                self.process.terminate()
            self.process = None

    def on_monitor_signal(self, proxy, sender, signal, parameters):
        if signal != 'WatchFired':
            return
        watch = parameters.unpack()[0]
        if watch == self.idle_watch:
            self.remove_watch('idle_watch')
            if self.screen.call_sync('GetActive', None, 0, -1, None).unpack()[0]:
                return
            env = os.environ.copy()
            env['LEVANDE_FULLSCREEN'] = '1'
            self.process = subprocess.Popen([sys.executable, str(Path(__file__).with_name('levande.py'))], env=env)
            self.active_watch = self.monitor.call_sync('AddUserActiveWatch', None, 0, -1, None).unpack()[0]
        elif watch == self.active_watch:
            self.active_watch = 0
            self.stop_animation()
            self.schedule()

    def on_screen_signal(self, proxy, sender, signal, parameters):
        if signal != 'ActiveChanged':
            return
        if parameters.unpack()[0]:
            self.stop_animation()
            self.remove_watch('active_watch')
            self.remove_watch('idle_watch')
        else:
            self.schedule()

    def close(self):
        self.stop_animation()
        self.remove_watch('idle_watch')
        self.remove_watch('active_watch')


if __name__ == '__main__':
    launcher = IdleLauncher()
    loop = GLib.MainLoop()
    for signal in (2, 15):
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal, lambda: (loop.quit(), GLib.SOURCE_REMOVE)[1])
    try:
        loop.run()
    finally:
        launcher.close()
