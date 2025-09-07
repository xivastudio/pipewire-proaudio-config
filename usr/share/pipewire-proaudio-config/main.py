#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
import subprocess
import os
import locale
import gettext

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
        self.set_default_size(600, 760)

        # Dictionaries to map UI widgets to their corresponding shell scripts
        self.switch_scripts = {}
        self.status_indicators = {}

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
        # Main vertical box container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)

        # Header bar with the main title
        header_bar = Adw.HeaderBar()
        header_bar.set_title_widget(Adw.WindowTitle(title=_("PipeWire ProAudio Config")))
        main_box.append(header_bar)

        # ScrolledWindow for the content area
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        main_box.append(scrolled)

        # Main content container with margins
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        content_box.set_margin_top(20)
        content_box.set_margin_bottom(20)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)
        scrolled.set_child(content_box)

        # Create the preference groups
        self.checks_group(content_box)
        self.system_group(content_box)
        # self.create_example_group(content_box)

        # Initial synchronization of UI state with system state
        self.sync_all_switches()

    def on_reload_clicked(self, widget):
        """Callback for the reload button. Triggers a full UI state sync."""
        print("Reloading all statuses...")
        self.sync_all_switches()

    def create_indicator_row(self, parent_group, title, subtitle, script_name):
        """Builds a custom indicator row that is visually consistent with the switch rows."""
        row = Adw.PreferencesRow()

        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12, margin_top=6, margin_bottom=6, margin_start=12, margin_end=12)
        row.set_child(main_box)

        title_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True)
        main_box.append(title_area)

        title_label = Gtk.Label(xalign=0, label=title)
        title_label.add_css_class("title-5")
        title_area.append(title_label)

        subtitle_label = Gtk.Label(xalign=0, label=subtitle)
        subtitle_label.add_css_class("caption")
        subtitle_label.add_css_class("dim-label")
        title_area.append(subtitle_label)

        indicator = Gtk.Box(valign=Gtk.Align.CENTER)
        indicator.add_css_class("status-indicator")
        main_box.append(indicator)

        script_group = getattr(parent_group, 'script_group', 'default')
        script_path = os.path.join(script_group, f"{script_name}.sh")
        self.status_indicators[indicator] = script_path

        parent_group.add(row)
        return indicator

    # Function to create a switch with a details area and clickable link.
    def create_row_with_clickable_link(self, parent_group, title, subtitle_with_markup, script_name):
        """Builds a custom row mimicking Adw.ActionRow to allow for a clickable link in the subtitle."""
        # Usa Adw.PreferencesRow como base para obter o estilo de fundo e borda corretos.
        row = Adw.PreferencesRow()

        # Box horizontal principal para conter a área de título e o switch.
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12, margin_top=6, margin_bottom=6, margin_start=12, margin_end=12)
        row.set_child(main_box)

        # Box vertical para o título e o subtítulo clicável.
        # hexpand=True é crucial para empurrar o switch para a direita.
        title_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True)
        main_box.append(title_area)

        title_label = Gtk.Label(xalign=0, label=title)
        title_label.add_css_class("title-5")
        title_area.append(title_label)

        subtitle_label = Gtk.Label(
            xalign=0,
            wrap=True,
            use_markup=True,
            label=subtitle_with_markup
        )
        subtitle_label.add_css_class("caption")
        subtitle_label.add_css_class("dim-label")
        title_area.append(subtitle_label)

        # O switch, alinhado ao centro verticalmente.
        switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        main_box.append(switch)

        # Associate the script with the switch
        script_group = getattr(parent_group, 'script_group', 'default')
        script_path = os.path.join(script_group, f"{script_name}.sh")
        self.switch_scripts[switch] = script_path
        switch.connect("state-set", self.on_switch_changed)

        parent_group.add(row)
        return switch

    def checks_group(self, parent):
        """Builds the 'Checks' preferences group."""
        group = Adw.PreferencesGroup()
        group.set_title(_("Checks"))
        group.script_group = "checks"
        group.set_description(_("ProAudio Checks"))
        parent.append(group)

        # Create and add the reload button to the group's header
        reload_button = Gtk.Button(
            icon_name="view-refresh-symbolic",
            valign=Gtk.Align.CENTER,
            tooltip_text=_("Reload all statuses")
        )
        reload_button.connect("clicked", self.on_reload_clicked)
        group.set_header_suffix(reload_button)

        # Low Latency
        self.lowLatency_indicator = self.create_indicator_row(
            group,
            _("Kernel Low Latency"),
            _("Check if the kernel configuration has lowlatency enabled"),
            "kernelLowLatency"
        )

    def system_group(self, parent):
        """Builds the 'System' preferences group."""
        group = Adw.PreferencesGroup()
        group.set_title(_("System"))
        group.script_group = "system"
        group.set_description(_("ProAudio System Settings"))
        parent.append(group)

        # Power Profile
        self.powerProfile_switch = self.create_row_with_clickable_link(
            group,
            _("CPU Performance Power Profile"),
            _("Turn on CPU performance power profile."),
            "powerProfile"
        )
        # Meltdown mitigations
        link_meltdown = "https://meltdownattack.com"
        self.meltdownMitigations_switch = self.create_row_with_clickable_link(
            group,
            _("Meltdown Mitigations off"),
            _("Warning: Using mitigations=off will make your machine less secure! For more information see: <a href='{link}'>{link}</a>").format(link=link_meltdown),
            "meltdownMitigations"
        )
        # noWatchdog
        self.noWatchdog_switch = self.create_row_with_clickable_link(
            group,
            _("noWatchdog"),
            _("Disables the hardware watchdog and TSC clocksource systems, maintaining high performance but removing automatic protections against system crashes."),
            "noWatchdog"
        )
        # Kernel Threadirqs
        self.kernelThreadirqs_switch = self.create_row_with_clickable_link(
            group,
            _("IRQ Forced Threading"),
            _("Warning: If you do not know what this is and/or are not sure, DO NOT enable this feature."),
            "kernelThreadirqs"
        )
        # Multi/Hyper Threading
        link_smt = "https://en.wikipedia.org/wiki/Simultaneous_multithreading"
        self.multiThreading_switch = self.create_row_with_clickable_link(
            group,
            _("Multi/Hyper Threading OFF"),
            _("Simultaneous Multithreading (SMT) or hyperthreading can cause spikes in DSP load at higher DSP loads.\nIt can improve single-task performance, but it can worsen multitasking and other programs, so use it wisely.\n<a href='{link}'>{link}</a>").format(link=link_smt),
            "multiThreading"
        )
        # User in Audio Group
        self.audioGroup_switch = self.create_row_with_clickable_link(
            group,
            _("User in Audio Group"),
            _("It is generally good practice to have an audio group, and add any users that should be allowed to perform audio tasks to this group."),
            "audioGroup"
        )
        # Disable Wifi
        self.disableWifi_switch = self.create_row_with_clickable_link(
            group,
            _("Disable Wifi"),
            _("NetworkManager keeps scanning for new wireless networks in the background and this might cause xruns. The best option is to not use a wireless network in a low-latency real-time audio environment."),
            "disableWifi"
        )
        # Disable Bluetooth
        self.disableBluetooth_switch = self.create_row_with_clickable_link(
            group,
            _("Disable Bluetooth"),
            _("Bluetooth keeps scanning for new devices in the background and this might cause xruns. The best option is to not use a bluetooth in a low-latency real-time audio environment."),
            "disableBluetooth"
        )

    def check_script_state(self, script_path):
        """Executes a script with the 'check' argument to get its current state.
        Returns True if the script's stdout is 'true', False otherwise."""
        if not os.path.exists(script_path):
            msg = _("Unavailable: script not found.")
            print(_("Script not found: {}").format(script_path))
            return (None, msg)

        try:
            result = subprocess.run([script_path, "check"],
            capture_output=True,
            text=True,
            timeout=10)
            if result.returncode == 0:
                output = result.stdout.strip().lower()
                if output == "true":
                    return (True, _("Enabled"))
                elif output == "false":
                    return (False, _("Disabled"))
                else:
                    msg = _("Unavailable: script returned invalid output.")
                    print(_("Invalid output from script {}: {}").format(script_path, result.stdout.strip()))
                    return (None, msg)
            else:
                msg = _("Unavailable: script returned an error.")
                print(_("Error checking state: {}").format(result.stderr))
                return (None, msg)
        except (subprocess.TimeoutExpired, Exception) as e:
            msg = _("Unavailable: failed to run script.")
            print(_("Error running script {}: {}").format(script_path, e))
            return (None, msg)

    def toggle_script_state(self, script_path, new_state):
        """Executes a script with the 'toggle' argument to change the system state.
        Returns True on success, False on failure."""
        if not os.path.exists(script_path):
            error_msg = _("Script not found: {}").format(script_path)
            print(f"ERROR: {error_msg}")
            return False

        try:
            state_str = "true" if new_state else "false"
            result = subprocess.run([script_path, "toggle", state_str],
            capture_output=True,
            text=True,
            timeout=30)

            if result.returncode == 0:
                print(_("State changed successfully"))
                if result.stdout.strip():
                    print(_("Script output: {}").format(result.stdout.strip()))
                return True
            else:
                # Exit code != 0 indica falha
                error_msg = _("Script failed with exit code: {}").format(result.returncode)
                print(f"ERROR: {error_msg}")

                if result.stderr.strip():
                    print(f"ERROR: Script stderr: {result.stderr.strip()}")

                if result.stdout.strip():
                    print(f"ERROR: Script stdout: {result.stdout.strip()}")

                return False

        except subprocess.TimeoutExpired:
            error_msg = _("Script timeout: {}").format(script_path)
            print(f"ERROR: {error_msg}")
            return False
        except Exception as e:
            error_msg = _("Error running script {}: {}").format(script_path, e)
            print(f"ERROR: {error_msg}")
            return False

    def sync_all_switches(self):
        """Synchronizes all UI widgets and disables them if their script is invalid, providing a tooltip with the reason."""
        # Sync all switches
        for switch, script_path in self.switch_scripts.items():
            row = switch.get_parent().get_parent()
            status, message = self.check_script_state(script_path)

            if status is None:
                row.set_sensitive(False)
                row.set_tooltip_text(message)
            else:
                row.set_sensitive(True)
                row.set_tooltip_text(None)
                switch.handler_block_by_func(self.on_switch_changed)
                switch.set_active(status)
                switch.handler_unblock_by_func(self.on_switch_changed)
            print(_("Switch {} synchronized: {}").format(os.path.basename(script_path), status))

        # Sync all status indicators
        for indicator, script_path in self.status_indicators.items():
            row = indicator.get_parent().get_parent()
            status, message = self.check_script_state(script_path)

            # Always remove all state classes first to ensure a clean slate
            indicator.remove_css_class("status-on")
            indicator.remove_css_class("status-off")
            indicator.remove_css_class("status-unavailable")

            if status is None:
                row.set_sensitive(False)
                row.set_tooltip_text(message)
                indicator.add_css_class("status-unavailable")
            else:
                row.set_sensitive(True)
                row.set_tooltip_text(None)
                if status:
                    indicator.add_css_class("status-on")
                else:
                    indicator.add_css_class("status-off")
            print(_("Indicator {} synchronized: {}").format(os.path.basename(script_path), status))

    def on_switch_changed(self, switch, state):
        """Callback executed when a user manually toggles a switch."""
        script_path = self.switch_scripts.get(switch)

        if script_path:
            script_name = os.path.basename(script_path)
            print(_("Changing {} to {}").format(script_name, "on" if state else "off"))

            # Attempt to change the system state
            success = self.toggle_script_state(script_path, state)

            # If the script fails, revert the switch to its previous state
            # to keep the UI consistent with the actual system state.
            if not success:
                # Block signal to prevent an infinite loop
                switch.handler_block_by_func(self.on_switch_changed)
                switch.set_active(not state)
                switch.handler_unblock_by_func(self.on_switch_changed)

                print(_("ERROR: Failed to change {} to {}").format(script_name, "on" if state else "off"))
                self.show_toast(_("Failed to change setting: {}").format(script_name))

        return False

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
