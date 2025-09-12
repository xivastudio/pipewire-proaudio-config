#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
import subprocess
import os
import locale
import gettext
from pipewire_settings_page import PipewireSettingsPage
from audio_system_tweaks_page import AudioSystemTweaksPage

# Set up gettext for application localization.
DOMAIN = 'pipewire-proaudio-config'
LOCALE_DIR = '/usr/share/locale'

locale.setlocale(locale.LC_ALL, '')
locale.bindtextdomain(DOMAIN, LOCALE_DIR)
locale.textdomain(DOMAIN)

gettext.bindtextdomain(DOMAIN, LOCALE_DIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext

class PipeWireProAudioConfig(Adw.Application):
    """The main application class."""
    def __init__(self):
        super().__init__(application_id='org.xivastudio.pipewire-proaudio-config')

        # Set the color scheme to follow the system's preference (light/dark).
        # This prevents Adwaita from complaining about legacy GTK settings.
        style_manager = Adw.StyleManager.get_default()
        style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)

        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        """Called when the application is activated."""
        # Use the CustomWindow class which includes the ToastOverlay
        self.window = CustomWindow(application=app)
        self.window.present()

class SystemSettingsWindow(Adw.ApplicationWindow):
    """The main window for the application, containing all UI elements."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Window configuration
        self.set_title(_("PipeWire ProAudio Config"))
        self.set_default_size(600, 870)

        # Load custom CSS for styling
        self.load_css()

        # Build the user interface
        self.setup_ui()

    def load_css(self):
        """Loads custom CSS for styling widgets like status indicators."""
        provider = Gtk.CssProvider()
        css = """
        preferencesgroup .heading {
            font-size: 1.3rem;
        }
        .status-indicator {
            min-width: 16px;
            min-height: 16px;
            border-radius: 8px;
            margin: 0 8px;
        }
        .status-on {
            background-color: @success_color;
        }
        .status-off {
            background-color: @error_color;
        }
        .status-unavailable {
            background-color: @insensitive_fg_color;
        }
        """
        provider.load_from_string(css)
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def setup_ui(self):
        """Constructs the main UI layout and populates it with widgets."""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)

        header_bar = Adw.HeaderBar()
        main_box.append(header_bar)

        # ViewStack to contain the different settings pages
        view_stack = Adw.ViewStack()
        main_box.append(view_stack)

        # ViewSwitcher to control the ViewStack, placed in the HeaderBar
        view_switcher = Adw.ViewSwitcher()
        view_switcher.set_stack(view_stack)
        header_bar.set_title_widget(view_switcher)

        # Page creation
        pipewire_page = self.create_pipewire_page()
        view_stack.add_titled_with_icon(pipewire_page, "pipewire", _("PipeWire Settings"), "audio-card-symbolic")

        system_page = self.create_audio_system_page()
        view_stack.add_titled_with_icon(system_page, "system", _("Audio System Tweaks"), "preferences-system-symbolic")

    def create_audio_system_page(self):
        """Builds the page for system tweaks and checks."""
        return AudioSystemTweaksPage(self)

    def create_pipewire_page(self):
        """Builds the page for PipeWire settings by instantiating the external class."""
        return PipewireSettingsPage(self)

class CustomWindow(SystemSettingsWindow):
    """A subclass of the main window that wraps its content in an Adw.ToastOverlay.
    This is necessary for the `show_toast` method to work correctly."""
    def __init__(self, **kwargs):
        # O ToastOverlay precisa envolver o conteúdo principal.
        self.toast_overlay = Adw.ToastOverlay()

        # Call the parent's __init__ which builds the UI
        super().__init__(**kwargs)

        # Get the UI content built by the parent...
        content = self.get_content()
        # ...detach it from the window...
        self.set_content(None)
        # ...place it inside the ToastOverlay...
        self.toast_overlay.set_child(content)
        # ...and set the ToastOverlay as the new window content.
        self.set_content(self.toast_overlay)

    def show_toast(self, message):
        """Overrides the parent method to ensure it adds toasts to its own overlay."""
        toast = Adw.Toast(title=message, timeout=3)
        self.toast_overlay.add_toast(toast)

def main():
    # SIMPLIFICATION: We only need one Application class.
    app = PipeWireProAudioConfig()
    return app.run()

if __name__ == "__main__":
    main()
