import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw
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

class PipewireSettingsPage(Adw.Bin):
    """A self-contained page for managing PipeWire settings."""
    def __init__(self, main_window, **kwargs):
        super().__init__(**kwargs)
        self.main_window = main_window # Referência à janela principal para mostrar toasts

        # Verifica se pw-metadata está disponível antes de construir a UI
        if not self._check_pw_metadata_exists():
            self._build_warning_ui()
            return

        self._build_main_ui()
        self._load_initial_state()

    def _build_warning_ui(self):
        """Builds a warning message if pw-metadata is not found."""
        warning_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER, spacing=12)
        warning_icon = Gtk.Image(icon_name="dialog-warning-symbolic", icon_size=Gtk.IconSize.LARGE)
        warning_icon.add_css_class("error")
        warning_label = Gtk.Label(label=_("`pw-metadata` command not found.\nPlease install pipewire-utils or a similar package."))
        warning_box.append(warning_icon)
        warning_box.append(warning_label)
        self.set_child(warning_box)

    def _build_main_ui(self):
        """Builds the main user interface for this page with clearer button actions."""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.set_child(scrolled)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20, margin_top=20, margin_bottom=20, margin_start=20, margin_end=20)
        scrolled.set_child(content_box)

        self.group = Adw.PreferencesGroup(title=_("Audio Interface"))
        content_box.append(self.group)

        reload_button = Gtk.Button(
            icon_name="view-refresh-symbolic",
            valign=Gtk.Align.CENTER,
            tooltip_text=_("Reload live settings from PipeWire")
        )
        reload_button.connect("clicked", self._on_reload_clicked)
        self.group.set_header_suffix(reload_button)

        # Dropdown para Sample Rate
        self.samplerate_row = Adw.ActionRow(title=_("Sample Rate"))
        self.samplerate_options = ["44100", "48000", "88200", "96000"]
        self.samplerate_dropdown = Gtk.DropDown.new_from_strings(self.samplerate_options)
        self.samplerate_dropdown.set_valign(Gtk.Align.CENTER)
        self.samplerate_row.add_suffix(self.samplerate_dropdown)
        self.group.add(self.samplerate_row)

        # Dropdown para Buffer Size (agora criado como placeholder)
        self.buffersize_row = Adw.ActionRow(title=_("Buffer Size (Quantum)"))
        self.buffersize_dropdown = Gtk.DropDown.new_from_strings([]) # Começa vazio
        self.buffersize_dropdown.set_valign(Gtk.Align.CENTER)
        self.buffersize_row.add_suffix(self.buffersize_dropdown)
        self.group.add(self.buffersize_row)

        # Box for buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, halign=Gtk.Align.END, spacing=12, margin_top=10)
        content_box.append(button_box)

        # Button to apply temporarily
        self.apply_button = Gtk.Button(label=_("Apply Session"))
        self.apply_button.set_tooltip_text(_("Apply settings for the current session only. Lost on restart."))
        self.apply_button.connect("clicked", self._on_apply_session_clicked)
        button_box.append(self.apply_button)

        # Button to make permanent
        self.permanent_button = Gtk.Button(label=_("Make Permanent & Apply"))
        self.permanent_button.set_tooltip_text(_("Apply settings now and save them for future sessions."))
        self.permanent_button.get_style_context().add_class("suggested-action")
        self.permanent_button.connect("clicked", self._on_save_and_apply_clicked)
        button_box.append(self.permanent_button)

    def _load_initial_state(self):
        """Loads live settings, dynamically generates buffer size options, and updates the UI."""
        live_settings = self._get_live_pipewire_settings()
        rate_is_forced = live_settings.get('clock.force-rate', '0') != '0'
        quantum_is_forced = live_settings.get('clock.force-quantum', '0') != '0'

        description = _("Apply changes temporarily or make them permanent for future sessions.")
        if rate_is_forced or quantum_is_forced:
            forced_msg = _("Settings are being controlled by an external application. Applying new values will override this.")
            description = f"<span weight='bold' foreground='orange'>{forced_msg}</span>"

        self.group.set_description(description)

        # Sample Rate
        current_rate = live_settings.get("clock.rate")
        if current_rate and current_rate in self.samplerate_options:
            self.samplerate_dropdown.set_selected(self.samplerate_options.index(current_rate))
        else:
            self.samplerate_dropdown.set_selected(1)

        # Buffer Size
        try:
            min_q = int(live_settings.get('clock.min-quantum', '64'))
            max_q = int(live_settings.get('clock.max-quantum', '1024'))
        except (ValueError, TypeError):
            min_q, max_q = 64, 1024 # Fallback seguro

        # Generates powers of 2 between the minimum and maximum
        self.buffersize_options = []
        val = 32
        while val < max_q:
            val *= 2
            if val >= min_q:
                self.buffersize_options.append(str(val))

        # If the list is empty (rare case), use a fallback
        if not self.buffersize_options:
            self.buffersize_options = ["64", "128", "256", "512", "1024"]

        self.buffersize_row.remove(self.buffersize_dropdown)
        self.buffersize_dropdown = Gtk.DropDown.new_from_strings(self.buffersize_options)
        self.buffersize_dropdown.set_valign(Gtk.Align.CENTER)
        self.buffersize_row.add_suffix(self.buffersize_dropdown)

        # Selects the current value
        current_quantum = live_settings.get("clock.quantum")
        if current_quantum and current_quantum in self.buffersize_options:
            self.buffersize_dropdown.set_selected(self.buffersize_options.index(current_quantum))
        else:
            # Select the option closest to the end as a safe default
            self.buffersize_dropdown.set_selected(len(self.buffersize_options) - 1)

    def _get_live_pipewire_settings(self):
        """Reads all live PipeWire settings and returns them as a dictionary."""
        # Implementation is the same as before...
        settings_dict = {}
        try:
            result = subprocess.run(["pw-metadata", "-n", "settings"], capture_output=True, text=True, timeout=5)
            if result.returncode != 0: return {}
            for line in result.stdout.splitlines():
                if "key:'" in line and "value:'" in line:
                    try:
                        key = line.split("key:'")[1].split("'")[0]
                        value = line.split("value:'")[1].split("'")[0]
                        settings_dict[key] = value
                    except IndexError: continue
            return settings_dict
        except Exception: return {}

    def _check_pw_metadata_exists(self):
        """Checks if the pw-metadata command is available on the system."""
        try:
            subprocess.run(["which", "pw-metadata"], capture_output=True, check=True, timeout=2)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _apply_live_settings(self, samplerate, buffersize):
        """Applies settings live using pw-metadata, returning True on success."""
        try:
            live_settings = self._get_live_pipewire_settings()

            if live_settings.get('clock.force-rate', '0') != '0':
                subprocess.run(["pw-metadata", "-n", "settings", "0", "clock.force-rate", "0"], check=True, timeout=5)

            subprocess.run(["pw-metadata", "-n", "settings", "0", "clock.rate", samplerate], check=True, timeout=5)

            if live_settings.get('clock.force-quantum', '0') != '0':
                subprocess.run(["pw-metadata", "-n", "settings", "0", "clock.force-quantum", "0"], check=True, timeout=5)

            subprocess.run(["pw-metadata", "-n", "settings", "0", "clock.quantum", buffersize], check=True, timeout=5)

            return True

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"Error applying live settings: {e}")
            return False

    def _on_apply_session_clicked(self, widget):
        """Handler for the temporary 'Apply Session' button."""
        samplerate = self.samplerate_dropdown.get_selected_item().get_string()
        buffersize = self.buffersize_dropdown.get_selected_item().get_string()

        success = self._apply_live_settings(samplerate, buffersize)

        if success:
            message = _("Settings applied for the current session.")
        else:
            message = _("Failed to apply live settings.")
        self.main_window.show_toast(message)

    def _on_save_and_apply_clicked(self, widget):
        """Handler for the 'Save & Apply' button."""
        samplerate = self.samplerate_dropdown.get_selected_item().get_string()
        buffersize = self.buffersize_dropdown.get_selected_item().get_string()

        # 1. Write to config file
        config_dir = os.path.expanduser("~/.config/pipewire/pipewire.conf.d")
        config_file = os.path.join(config_dir, "10-proaudio-config.conf")
        config_content = f"""context.properties = {{\n    default.clock.rate    = {samplerate}\n    default.clock.quantum = {buffersize}\n}}"""

        try:
            os.makedirs(config_dir, exist_ok=True)
            with open(config_file, 'w') as f:
                f.write(config_content.strip() + '\n')
        except Exception as e:
            self.main_window.show_toast(_("Error: Failed to save configuration file."))
            print(f"Error writing config: {e}")
            return

        # 2. Apply live settings
        success = self._apply_live_settings(samplerate, buffersize)
        if success:
            self.main_window.show_toast(_("Settings saved and applied permanently."))
        else:
            # says it saved but failed to apply live.
            self.main_window.show_toast(_("Settings saved, but failed to apply live."))

    def _on_reload_clicked(self, widget):
        """Reloads the live PipeWire settings and refreshes the UI."""
        print("Reloading PipeWire settings...")
        self._load_initial_state()
        self.main_window.show_toast(_("PipeWire settings reloaded."))
