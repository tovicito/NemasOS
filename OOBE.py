#!/usr/bin/env python3
import gi
import threading
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk
import subprocess
import os
import getpass

class OOBE(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="NEMÁS OOBE")
        self.set_border_width(10)
        self.set_default_size(6000, 4000)
        self.fullscreen()
        self.set_deletable(False)
        
        self.set_skip_taskbar_hint(True)
        self.set_keep_above(True)
        self.set_modal(True)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(500)

        self.pages = [
            self.page_welcome(),
            self.page_connection(),
            self.page_user(),
            self.page_env(),
            self.page_mode(),
            self.page_summary(),
            self.page_install(),
        ]

        for idx, page in enumerate(self.pages):
            self.stack.add_titled(page, f"page{idx}", f"Page {idx}")

        nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.back_btn = Gtk.Button(label="Atrás")
        self.next_btn = Gtk.Button(label="Siguiente")
        self.back_btn.connect("clicked", self.on_back_clicked)
        self.next_btn.connect("clicked", self.on_next_clicked)
        nav_box.pack_start(self.back_btn, True, True, 0)
        nav_box.pack_end(self.next_btn, True, True, 0)

        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_vbox.pack_start(self.stack, True, True, 0)
        main_vbox.pack_end(nav_box, False, False, 0)

        self.add(main_vbox)
        self.page_index = 0
        self.update_nav_buttons()

    def page_welcome(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        label = Gtk.Label(label="¡Bienvenido a Nemás OOBE!")
        label.set_line_wrap(True)
        box.pack_start(label, True, True, 0)
        return box

    def page_connection(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.network_label = Gtk.Label(label="Verificando conexión a Internet...")
        box.pack_start(self.network_label, False, False, 0)

        btn = Gtk.Button(label="Revisar conexión")
        btn.connect("clicked", self.check_network)
        box.pack_start(btn, False, False, 0)
        return box

    def check_network(self, widget):
        result = subprocess.call(["ping", "-c", "1", "1.1.1.1"], stdout=subprocess.DEVNULL)
        if result == 0:
            self.network_label.set_text("¡Conectado a Internet!")
        else:
            self.network_label.set_text("No hay conexión a Internet")

    def page_user(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.entry_user = Gtk.Entry()
        self.entry_user.set_placeholder_text("Nombre de usuario")
        self.entry_pass = Gtk.Entry()
        self.entry_pass.set_placeholder_text("Contraseña")
        self.entry_pass.set_visibility(False)
        box.pack_start(Gtk.Label(label="Crea tu usuario:"), False, False, 0)
        box.pack_start(self.entry_user, False, False, 0)
        box.pack_start(self.entry_pass, False, False, 0)
        return box

    def page_env(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.env_combo = Gtk.ComboBoxText()
        for env in ["XFCE", "LXQt", "MATE", "GNOME", "KDE Plasma"]:
            self.env_combo.append_text(env)
        self.env_combo.set_active(0)
        box.pack_start(Gtk.Label(label="Elige tu entorno de escritorio:"), False, False, 0)
        box.pack_start(self.env_combo, False, False, 0)
        return box

    def page_mode(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.mode_combo = Gtk.ComboBoxText()
        self.mode_combo.append_text("Mínima (solo DE)")
        self.mode_combo.append_text("Completa (DE + apps)")
        self.mode_combo.set_active(0)
        box.pack_start(Gtk.Label(label="Modo de instalación:"), False, False, 0)
        box.pack_start(self.mode_combo, False, False, 0)
        return box

    def page_summary(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.lbl_summary = Gtk.Label(label="Resumen de instalación")
        self.lbl_summary.set_line_wrap(True)
        box.pack_start(self.lbl_summary, False, False, 0)
        return box

    def page_install(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.progress = Gtk.ProgressBar()
        self.install_log = Gtk.TextView()
        self.install_log.set_editable(False)
        self.install_log.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(150)
        scrolled.add(self.install_log)
        box.pack_start(self.progress, False, False, 0)
        box.pack_start(scrolled, True, True, 0)
        return box

    def on_back_clicked(self, button):
        if self.page_index > 0:
            self.page_index -= 1
            self.stack.set_visible_child_name(f"page{self.page_index}")
        self.update_nav_buttons()

    def on_next_clicked(self, button):
        if self.page_index < len(self.pages) - 1:
            self.page_index += 1
            if self.page_index == len(self.pages) - 2:
                self.generate_summary()
            elif self.page_index == len(self.pages) - 1:
                self.start_installation()
            self.stack.set_visible_child_name(f"page{self.page_index}")
        self.update_nav_buttons()

    def update_nav_buttons(self):
        self.back_btn.set_sensitive(self.page_index > 0)
        if self.page_index == len(self.pages) - 1:
            self.next_btn.set_label("Finalizar")
        else:
            self.next_btn.set_label("Siguiente")

    def generate_summary(self):
        summary = f"Usuario: {self.entry_user.get_text()}\n"
        summary += f"Entorno: {self.env_combo.get_active_text()}\n"
        summary += f"Modo: {self.mode_combo.get_active_text()}\n"
        self.lbl_summary.set_text(summary)

    def append_log(self, message):
        buffer = self.install_log.get_buffer()
        buffer.insert(buffer.get_end_iter(), message + "\n")

    def start_installation(self):
        threading.Thread(target=self.perform_installation).start()

    def perform_installation(self):
        GLib.idle_add(self.progress.set_fraction, 0.1)
        user = self.entry_user.get_text()
        passwd = self.entry_pass.get_text()
        env = self.env_combo.get_active_text()
        mode = self.mode_combo.get_active_text()

        self.run_cmd(f"useradd -m -s /bin/bash {user}")
        self.run_cmd(f"echo '{user}:{passwd}' | chpasswd")
        self.run_cmd(f"usermod -aG sudo {user}")
        self.append_log(f"Usuario {user} creado.")

        GLib.idle_add(self.progress.set_fraction, 0.3)

        # Instalar DE
        env_cmds = {
            "XFCE": "task-xfce-desktop",
            "LXQt": "lxqt",
            "MATE": "mate-desktop-environment",
            "GNOME": "gnome-core",
            "KDE Plasma": "kde-standard"
        }
        self.run_cmd(f"apt update && apt install -y {env_cmds[env]} lightdm")
        self.append_log(f"Entorno {env} instalado.")

        GLib.idle_add(self.progress.set_fraction, 0.6)

        if "Completa" in mode:
            self.run_cmd("apt install -y libreoffice gimp vlc firefox-esr")
            self.append_log("Aplicaciones completas instaladas.")

        GLib.idle_add(self.progress.set_fraction, 0.8)

        # Plymouth personalizado
        self.run_cmd("apt install -y plymouth")
        theme = "/usr/share/plymouth/themes/nemas"
        os.makedirs(theme, exist_ok=True)
        with open(f"{theme}/nemas.plymouth", "w") as f:
            f.write("[Plymouth Theme]\nName=Nemas Spinner\nAnimation=spinner\n")
        self.run_cmd("update-alternatives --install /usr/share/plymouth/themes/default.plymouth default.plymouth " + theme + "/nemas.plymouth 100")
        self.run_cmd("update-alternatives --set default.plymouth " + theme + "/nemas.plymouth")
        self.run_cmd("update-initramfs -u")
        self.append_log("Plymouth personalizado configurado.")
        
     #Eliminando OOBE
        os_remove("/etc/OOBE.py")

        self.append_log("OOBE ELIMINADO")
        



        GLib.idle_add(self.progress.set_fraction, 1.0)
        self.append_log("Instalación finalizada. ¡Reinicia para aplicar los cambios!")
        
        
class CountdownWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Finalizando configuración")
        self.set_default_size(800, 600)
        self.fullscreen()
        self.set_deletable(False)
        self.set_skip_taskbar_hint(True)
        self.set_keep_above(True)

        self.timeout = 10  # segundos
        self.label = Gtk.Label(label=f"¡Listo! Reiniciando en {self.timeout} segundos...")
        self.label.set_name("big-label")

        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
        #big-label {
            font-size: 42px;
        }
        """)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.add(self.label)
        self.show_all()

        # Empieza el contador
        GLib.timeout_add_seconds(1, self.update_countdown)

    def update_countdown(self):
        self.timeout -= 1
        if self.timeout == 0:
            self.label.set_text("¡Reiniciando ahora!")
            GLib.timeout_add_seconds(1, self.reboot_system)
            return False  # detener el contador
        else:
            self.label.set_text(f"¡Listo! Reiniciando en {self.timeout} segundos...")
            return True  # continuar

    def reboot_system(self):
        subprocess.call(['reboot'])
        return False

# Si quieres ejecutarlo directamente
if __name__ == "__main__":
    win = CountdownWindow()
    win.connect("delete-event", Gtk.main_quit)
    Gtk.main()
        

    def run_cmd(self, cmd):
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            GLib.idle_add(self.append_log, line.strip())
        process.wait()

win = OOBE()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
