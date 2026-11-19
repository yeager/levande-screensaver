#!/usr/bin/env python3
import math
import os
import random
import time
import gettext
import locale
from pathlib import Path
import cairo
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, Gdk, GLib

locale.setlocale(locale.LC_ALL, '')
translations = gettext.translation('living-screensavers', localedir=Path(__file__).with_name('locale'), fallback=True)
_ = translations.gettext

class Screensaver(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='se.yeager.Levande')
        rng = random.Random(17)
        self.stars = [(rng.random(), rng.random(), rng.random()) for _ in range(230)]
        assets = Path(__file__).with_name("assets")
        self.koi_image = cairo.ImageSurface.create_from_png(str(assets / "koi.png"))
        self.jelly_image = cairo.ImageSurface.create_from_png(str(assets / "jellyfish.png"))
        self.lantern_image = cairo.ImageSurface.create_from_png(str(assets / "lantern.png"))
        self.scene = 0
        self.started = time.monotonic()
        self.fullscreened = False

    def do_activate(self):
        self.window = Gtk.ApplicationWindow(application=self, title=_('Living Screensavers'))
        self.window.set_default_size(1100, 700)
        self.area = Gtk.DrawingArea(hexpand=True, vexpand=True)
        self.area.set_draw_func(self.draw)
        self.window.set_child(self.area)
        keys = Gtk.EventControllerKey()
        keys.connect('key-pressed', self.on_key)
        self.window.add_controller(keys)
        GLib.timeout_add(33, self.tick)
        if os.environ.get("LEVANDE_FULLSCREEN") == "1":
            self.fullscreened = True
            self.window.fullscreen()
        self.window.present()

    def tick(self):
        self.area.queue_draw()
        return GLib.SOURCE_CONTINUE

    def on_key(self, controller, key, code, state):
        if key in (Gdk.KEY_Escape, Gdk.KEY_q):
            self.quit()
        elif key in (Gdk.KEY_Right, Gdk.KEY_space):
            self.scene = (self.scene + 1) % 9
        elif key == Gdk.KEY_Left:
            self.scene = (self.scene - 1) % 9
        elif key in (Gdk.KEY_f, Gdk.KEY_F11):
            self.fullscreened = not self.fullscreened
            if self.fullscreened:
                self.window.fullscreen()
            else:
                self.window.unfullscreen()
        elif Gdk.KEY_1 <= key <= Gdk.KEY_9:
            self.scene = key - Gdk.KEY_1
        return True

    def draw(self, area, cr, width, height):
        t = time.monotonic() - self.started
        cr.scale(width, height)
        if self.scene == 0:
            self.aurora(cr, t)
        elif self.scene == 1:
            self.orbit(cr, t, width, height)
        elif self.scene == 2:
            self.ocean(cr, t)
        elif self.scene == 3:
            self.jellyfish(cr, t, width, height)
        elif self.scene == 4:
            self.fireflies(cr, t, width, height)
        elif self.scene == 5:
            self.asteroids(cr, t, width, height)
        elif self.scene == 6:
            self.lanterns(cr, t, width, height)
        elif self.scene == 7:
            self.rain(cr, t)
        else:
            self.koi(cr, t, width, height)

    def background(self, cr, top, bottom):
        import cairo
        gradient = cairo.LinearGradient(0, 0, 0, 1)
        gradient.add_color_stop_rgb(0, *top)
        gradient.add_color_stop_rgb(1, *bottom)
        cr.set_source(gradient)
        cr.paint()

    def aurora(self, cr, t):
        self.background(cr, (0.005, 0.012, 0.055), (0.025, 0.13, 0.18))
        for x, y, size in self.stars:
            alpha = 0.25 + 0.5 * (0.5 + 0.5 * math.sin(t * 1.2 + x * 80))
            cr.set_source_rgba(0.8, 0.92, 1, alpha)
            cr.arc(x, y * 0.7, 0.0006 + size * 0.001, 0, math.tau)
            cr.fill()
        for layer in range(32):
            cr.move_to(0, 0.28 + layer * 0.008)
            for i in range(101):
                x = i / 100
                y = 0.28 + layer * 0.008 + 0.075 * math.sin(x * 6 + t * 0.23 + layer * 0.025) + 0.035 * math.sin(x * 12 - t * 0.15)
                cr.line_to(x, y)
            cr.line_to(1, 0.75)
            cr.line_to(0, 0.75)
            cr.close_path()
            cr.set_source_rgba(0.08, 0.95, 0.22 + layer * 0.003, 0.022)
            cr.fill()
        cr.set_source_rgb(0.012, 0.025, 0.04)
        cr.move_to(0, 0.84)
        for i in range(101):
            x = i / 100
            cr.line_to(x, 0.83 - 0.07 * abs(math.sin(x * 13)) - 0.025 * math.sin(x * 31))
        cr.line_to(1, 1); cr.line_to(0, 1); cr.close_path(); cr.fill()

    def orbit(self, cr, t, width, height):
        import cairo
        self.background(cr, (0.005, 0.008, 0.025), (0.015, 0.025, 0.07))
        for x, y, size in self.stars:
            cr.set_source_rgba(0.75, 0.84, 1, 0.25 + size * 0.6)
            cr.arc(x, y, 0.0007 + size * 0.001, 0, math.tau); cr.fill()
        cr.save(); cr.translate(0.5, 0.5); cr.scale(height / width, 1)
        for ring in range(7):
            cr.save(); cr.rotate(ring * 0.35 + t * 0.025); cr.scale(1, 0.32 + ring * 0.045)
            cr.set_source_rgba(0.3, 0.67, 1, 0.11 + ring * 0.025)
            cr.set_line_width(0.0015); cr.arc(0, 0, 0.31 + ring * 0.018, 0, math.tau); cr.stroke()
            a = t * (0.16 + ring * 0.018) + ring * 2
            cr.set_source_rgba(0.55, 0.86, 1, 0.9); cr.arc(math.cos(a) * (0.31 + ring * 0.018), math.sin(a) * (0.31 + ring * 0.018), 0.005, 0, math.tau); cr.fill(); cr.restore()
        gradient = cairo.RadialGradient(-0.08, -0.1, 0.01, 0, 0, 0.23)
        gradient.add_color_stop_rgb(0, 0.36, 0.64, 0.8); gradient.add_color_stop_rgb(0.55, 0.045, 0.18, 0.28); gradient.add_color_stop_rgb(1, 0.005, 0.02, 0.045)
        cr.set_source(gradient); cr.arc(0, 0, 0.23, 0, math.tau); cr.fill(); cr.restore()

    def ocean(self, cr, t):
        self.background(cr, (0.015, 0.045, 0.095), (0.01, 0.24, 0.29))
        for band in range(55):
            y = 0.32 + band * 0.014
            cr.move_to(0, y)
            for i in range(101):
                x = i / 100
                wave = 0.008 * math.sin(x * (12 + band * 0.12) + t * (0.4 + band * 0.006) + band * 0.48)
                cr.line_to(x, y + wave)
            cr.set_source_rgba(0.35, 0.85, 0.82, 0.025 + 0.045 * (band / 55))
            cr.set_line_width(0.0015); cr.stroke()
        for x, y, size in self.stars[:55]:
            yy = (y + t * (0.008 + size * 0.015)) % 1
            cr.set_source_rgba(0.48, 0.94, 0.87, 0.15 + size * 0.35)
            cr.arc((x + 0.015 * math.sin(t + y * 30)) % 1, yy, 0.0008 + size * 0.002, 0, math.tau); cr.fill()

    def jellyfish(self, cr, t, width, height):
        self.background(cr, (0.005, 0.015, 0.06), (0.015, 0.15, 0.18))
        for index in range(7):
            phase = t * (0.22 + index * 0.013) + index * 4.1
            x = 0.12 + (index * 0.137) % 0.78 + 0.025 * math.sin(phase)
            y = (1.15 - t * (0.025 + index * 0.002) + index * 0.17) % 1.35 - 0.17
            size = 0.035 + (index % 3) * 0.008
            cr.save()
            cr.translate(x, y)
            cr.scale(height / width, 1)
            image = self.jelly_image
            image_width = image.get_width()
            image_height = image.get_height()
            pulse = 1 + 0.08 * math.sin(phase * 3)
            cr.scale(size * 2.1 * pulse / image_width, size * 4.1 / pulse / image_height)
            slices = 32
            for section in range(slices):
                top = image_height * section / slices
                section_height = image_height / slices + 1
                drift = image_width * 0.035 * (section / slices) ** 2 * math.sin(phase * 3 - section * 0.17)
                cr.save()
                cr.rectangle(-image_width, top - image_height * 0.2, image_width * 2, section_height)
                cr.clip()
                cr.translate(drift, 0)
                cr.set_source_surface(image, -image_width / 2, -image_height * 0.2)
                cr.paint_with_alpha(0.72)
                cr.restore()
            cr.restore()

    def fireflies(self, cr, t, width, height):
        import cairo
        self.background(cr, (0.012, 0.025, 0.04), (0.025, 0.11, 0.07))
        for x, y, size in self.stars[:75]:
            x = (x + 0.035 * math.sin(t * 0.35 + y * 30)) % 1
            y = (y + 0.045 * math.cos(t * 0.25 + x * 20)) % 1
            pulse = 0.2 + 0.8 * (0.5 + 0.5 * math.sin(t * 1.5 + size * 30)) ** 3
            cr.save()
            cr.translate(x, y)
            cr.scale(height / width, 1)
            radius = 0.012 + size * 0.012
            glow = cairo.RadialGradient(0, 0, 0, 0, 0, radius)
            glow.add_color_stop_rgba(0, 1, 0.91, 0.35, pulse)
            glow.add_color_stop_rgba(1, 0.7, 0.9, 0.15, 0)
            cr.set_source(glow)
            cr.arc(0, 0, radius, 0, math.tau)
            cr.fill()
            cr.restore()

    def asteroids(self, cr, t, width, height):
        self.background(cr, (0.008, 0.008, 0.035), (0.07, 0.025, 0.1))
        cr.save()
        cr.translate(0.5, 0.5)
        cr.scale(height / width, 1)
        for x, y, size in self.stars:
            angle = x * math.tau
            depth = (y + t * (0.07 + size * 0.03)) % 1
            radius = depth ** 2 * 0.85
            cr.set_source_rgba(0.65 + size * 0.35, 0.75, 1, depth)
            cr.arc(math.cos(angle) * radius, math.sin(angle) * radius,
                   0.0007 + depth * size * 0.004, 0, math.tau)
            cr.fill()
        cr.restore()

    def lanterns(self, cr, t, width, height):
        import cairo
        self.background(cr, (0.012, 0.017, 0.045), (0.19, 0.075, 0.065))
        for x, y, size in self.stars:
            cr.set_source_rgba(0.85, 0.88, 1, 0.15 + size * 0.35)
            cr.arc(x, y * 0.8, 0.0005 + size * 0.0008, 0, math.tau)
            cr.fill()
        for index, (x, y, depth) in enumerate(self.stars[:22]):
            x = (x + 0.014 * math.sin(t * 0.2 + index)) % 1
            y = (y - t * (0.009 + depth * 0.009)) % 1.25 - 0.12
            radius = 0.012 + depth * 0.022
            flicker = 0.8 + 0.12 * math.sin(t * 4.1 + index * 4) + 0.08 * math.sin(t * 7.3 + index)
            cr.save()
            cr.translate(x, y)
            cr.scale(height / width, 1)
            cr.rotate(0.06 * math.sin(t * 0.4 + index))
            glow = cairo.RadialGradient(0, radius * 0.4, 0, 0, 0, radius * 4.5)
            glow.add_color_stop_rgba(0, 1, 0.55, 0.16, 0.32 * flicker)
            glow.add_color_stop_rgba(1, 1, 0.22, 0.04, 0)
            cr.set_source(glow)
            cr.arc(0, 0, radius * 4.5, 0, math.tau)
            cr.fill()
            image = self.lantern_image
            image_width = image.get_width()
            image_height = image.get_height()
            cr.scale(radius * 2.0 / image_width, radius * 2.2 / image_height)
            cr.set_source_surface(image, -image_width / 2, -image_height / 2)
            cr.paint_with_alpha(0.85 + 0.15 * flicker)
            # The source image contains a wick at 79% of its height. Draw a
            # changing flame above it, in the image's own coordinate system.
            flame_x = image_width * 0.006 * math.sin(t * 5 + index)
            flame_y = image_height * 0.29
            flame_height = image_height * (0.065 + 0.012 * math.sin(t * 6.3 + index))
            flame_width = image_width * 0.018
            cr.move_to(flame_x, flame_y + flame_height * 0.5)
            cr.curve_to(flame_x - flame_width, flame_y + flame_height * 0.2,
                        flame_x - flame_width * 0.5, flame_y - flame_height * 0.15,
                        flame_x + flame_width * math.sin(t * 5 + index), flame_y - flame_height * 0.5)
            cr.curve_to(flame_x + flame_width * 0.5, flame_y - flame_height * 0.1,
                        flame_x + flame_width, flame_y + flame_height * 0.25,
                        flame_x, flame_y + flame_height * 0.5)
            cr.set_source_rgba(1, 0.86, 0.5, 0.75)
            cr.fill()
            cr.restore()

    def rain(self, cr, t):
        self.background(cr, (0.035, 0.07, 0.13), (0.12, 0.18, 0.22))
        for index, (x, y, size) in enumerate(self.stars):
            yy = (y + t * (0.12 + size * 0.08)) % 1
            cr.set_source_rgba(0.7, 0.85, 0.95, 0.15 + size * 0.3)
            cr.set_line_width(0.0008 + size * 0.0006)
            cr.move_to(x, yy)
            cr.line_to(x - 0.004, yy + 0.025 + size * 0.025)
            cr.stroke()
        for x, y, size in self.stars[:20]:
            phase = (t * 0.28 + y) % 1
            cr.set_source_rgba(0.7, 0.85, 0.92, (1 - phase) * 0.25)
            cr.set_line_width(0.001)
            cr.arc(x, 0.85 + size * 0.12, phase * 0.04, 0, math.tau)
            cr.stroke()

    def koi(self, cr, t, width, height):
        import cairo
        self.background(cr, (0.025, 0.13, 0.14), (0.008, 0.055, 0.065))
        for i in range(14):
            y = 0.08 + i * 0.068
            cr.move_to(0, y)
            for step in range(61):
                x = step / 60
                cr.line_to(x, y + 0.008 * math.sin(x * 12 + t * 0.3 + i))
            cr.set_source_rgba(0.48, 0.72, 0.67, 0.055)
            cr.set_line_width(0.001)
            cr.stroke()
        for index in range(6):
            phase = t * (0.12 + index * 0.009) + index * 1.3
            x = 0.5 + 0.32 * math.sin(phase)
            y = 0.5 + 0.32 * math.sin(phase * 0.77 + index)
            dx = 0.32 * math.cos(phase)
            dy = 0.32 * 0.77 * math.cos(phase * 0.77 + index)
            angle = math.atan2(dy, dx * width / height)
            cr.save()
            cr.translate(x, y)
            cr.scale(height / width, 1)
            cr.rotate(angle)
            image = self.koi_image
            image_width = image.get_width()
            image_height = image.get_height()
            fish_length = 0.14 + 0.012 * (index % 3)
            cr.scale(fish_length / image_width, fish_length * 0.34 / image_height)
            # Bend the image in overlapping narrow strips. The head stays
            # steady while the tail and fins sway with a travelling wave.
            slices = 48
            for section in range(slices):
                left = image_width * section / slices
                strip_width = image_width / slices + 1
                tail_weight = (1 - section / slices) ** 1.7
                displacement = image_height * 0.11 * tail_weight * math.sin(
                    t * 3.2 + index * 1.7 - section * 0.13)
                fin_pulse = 1 + 0.045 * math.sin(t * 3.2 + index + section * 0.1)
                cr.save()
                cr.rectangle(left - image_width / 2, -image_height,
                             strip_width, image_height * 2)
                cr.clip()
                cr.translate(0, displacement)
                cr.scale(1, fin_pulse)
                cr.set_source_surface(image, -image_width / 2, -image_height / 2)
                cr.paint_with_alpha(0.92)
                cr.restore()
            cr.restore()



if __name__ == '__main__':
    Screensaver().run(None)
