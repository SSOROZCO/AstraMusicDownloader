#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import sys
import os
import traceback
from datetime import datetime
from pathlib import Path


class LoggerYtDlp:
    """Captura los mensajes internos de yt-dlp y los envía a la consola de la app."""
    def __init__(self, app):
        self.app = app

    def debug(self, msg):
        if msg.startswith('[debug] '):
            return
        self.app.root.after(0, self.app.log_consola, f"{msg}\n")

    def info(self, msg):
        self.app.root.after(0, self.app.log_consola, f"{msg}\n")

    def warning(self, msg):
        self.app.root.after(0, self.app.log_consola, f"AVISO: {msg}\n")

    def error(self, msg):
        self.app.root.after(0, self.app.log_consola, f"ERROR: {msg}\n")


class AstraMusicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Astra Music Downloader v2.4")
        self.root.geometry("720x290")
        self.root.resizable(False, False)

        # Paleta de colores Dark premium integrada con Astra Linux Blue
        self.bg_color = "#121212"
        self.card_color = "#1e1e1e"
        self.accent_color = "#0f7cd4"  # Azul Astra Linux 💻
        self.text_color = "#FFFFFF"
        self.text_muted = "#AAAAAA"

        self.root.configure(bg=self.bg_color)

        # Icono actualizado al nuevo nombre
        ruta_icono = "/usr/share/icons/hicolor/256x256/apps/astramusic-logo.png"
        if os.path.exists(ruta_icono):
            try:
                self.icono_img = tk.PhotoImage(file=ruta_icono)
                self.root.iconphoto(False, self.icono_img)
            except Exception:
                pass

        self.url_var = tk.StringVar()
        self.carpeta_var = tk.StringVar(value=str(Path.home() / "Música"))
        self.descargando = False
        self.actualizando = False
        self.consola_visible = False

        self.configurar_estilos()
        self.crear_interfaz()
        threading.Thread(target=self.verificar_dependencias_inicio, daemon=True).start()

    def configurar_estilos(self):
        self.estilos = ttk.Style()
        self.estilos.theme_use("clam")

        # Configuración de estilos oscuros para TTK
        self.estilos.configure(".", background=self.bg_color, foreground=self.text_color)

        # TProgressbar (Azul Astra)
        self.estilos.configure("TProgressbar", thickness=8, troughcolor="#2c2c2c", background=self.accent_color, borderwidth=0)

        # Botón de Descarga Primario (Texto blanco sobre fondo azul)
        self.estilos.configure("Accent.TButton", background=self.accent_color, foreground="#FFFFFF", font=("Arial", 10, "bold"), borderwidth=0, focuscolor="none")
        self.estilos.map("Accent.TButton", background=[("active", "#0a5fa3"), ("disabled", "#555555")], foreground=[("disabled", "#888888")])

        # Botones Secundarios (Gris oscuro con texto blanco)
        self.estilos.configure("Normal.TButton", background="#333333", foreground=self.text_color, font=("Arial", 10), borderwidth=0, focuscolor="none")
        self.estilos.map("Normal.TButton", background=[("active", "#444444"), ("disabled", "#222222")], foreground=[("disabled", "#666666")])

    def crear_interfaz(self):
        self.main_frame = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=15)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Encabezado (Header)
        header_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        titulo = tk.Label(header_frame, text="🎵 Astra Music Downloader", font=("Arial", 16, "bold"), bg=self.bg_color, fg=self.accent_color)
        titulo.pack(side=tk.LEFT)

        subtitulo = tk.Label(header_frame, text="320 kbps Ultra Edition", font=("Arial", 9, "italic"), bg=self.bg_color, fg=self.text_muted)
        subtitulo.pack(side=tk.LEFT, padx=10, pady=(5, 0))

        # Entrada de la URL de YouTube
        tk.Label(self.main_frame, text="URL de YouTube:", font=("Arial", 10, "bold"), bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)
        url_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        url_frame.pack(fill=tk.X, pady=(2, 10))

        self.url_entry = tk.Entry(url_frame, textvariable=self.url_var, font=("Arial", 11), bg="#222222", fg=self.text_color, insertbackground="white", bd=1, relief="flat")
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4, padx=(0, 5))

        self.btn_pegar = ttk.Button(url_frame, text="📋 Pegar", style="Normal.TButton", command=self.pegar_url, width=8)
        self.btn_pegar.pack(side=tk.RIGHT)

        # Entrada de la Ruta Destino
        tk.Label(self.main_frame, text="Guardar en:", font=("Arial", 10, "bold"), bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)
        ruta_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        ruta_frame.pack(fill=tk.X, pady=(2, 12))

        self.ruta_entry = tk.Entry(ruta_frame, textvariable=self.carpeta_var, state="readonly", font=("Arial", 10), bg="#222222", fg=self.text_muted, bd=1, relief="flat")
        self.ruta_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4, padx=(0, 5))

        self.btn_buscar = ttk.Button(ruta_frame, text="Buscar...", style="Normal.TButton", command=self.seleccionar_carpeta, width=10)
        self.btn_buscar.pack(side=tk.RIGHT)

        # Panel de Acciones/Botones
        self.acciones_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.acciones_frame.pack(fill=tk.X, pady=(5, 5))

        self.btn_descargar = ttk.Button(self.acciones_frame, text="Descargar en 320 kbps 🔥", style="Accent.TButton", command=self.iniciar_descarga)
        self.btn_descargar.pack(side=tk.LEFT, padx=(0, 5), expand=True, fill=tk.X)

        self.btn_actualizar = ttk.Button(self.acciones_frame, text="Actualizar Librerías", style="Normal.TButton", command=self.iniciar_actualizacion)
        self.btn_actualizar.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.btn_consola_toggle = ttk.Button(self.acciones_frame, text="Ver Consola 🛠️", style="Normal.TButton", command=self.alternar_consola)
        self.btn_consola_toggle.pack(side=tk.LEFT, padx=(5, 0), expand=True, fill=tk.X)

        # Estado de la descarga y barra de progreso
        self.lbl_estado = tk.Label(self.main_frame, text="", font=("Arial", 9, "italic"), bg=self.bg_color, fg=self.text_muted)
        self.lbl_estado.pack(pady=(5, 2))

        self.progress_bar = ttk.Progressbar(self.main_frame, orient="horizontal", mode="determinate", style="TProgressbar")

        # Consola de diagnóstico integrada
        self.consola_container = tk.Canvas(self.main_frame, bg=self.bg_color, highlightthickness=0)
        self.txt_consola = tk.Text(self.consola_container, bd=0, background="#1e1e1e", foreground="#ffffff", font=("Courier", 9), state="disabled", wrap="word")
        self.consola_container.bind("<Configure>", self.dibujar_consola_redondeada)

        self.btn_copiar_consola = None

    def pegar_url(self):
        try:
            contenido = self.root.clipboard_get()
            self.url_var.set(contenido)
        except Exception:
            pass

    def dibujar_consola_redondeada(self, event=None):
        self.consola_container.delete("all")
        w = self.consola_container.winfo_width()
        h = self.consola_container.winfo_height()
        r = 16
        self.consola_container.create_arc(0, 0, r*2, r*2, start=90, extent=90, fill="#1e1e1e", outline="#1e1e1e")
        self.consola_container.create_arc(w-r*2, 0, w, r*2, start=0, extent=90, fill="#1e1e1e", outline="#1e1e1e")
        self.consola_container.create_arc(w-r*2, h-r*2, w, h, start=270, extent=90, fill="#1e1e1e", outline="#1e1e1e")
        self.consola_container.create_arc(0, h-r*2, r*2, h, start=180, extent=90, fill="#1e1e1e", outline="#1e1e1e")
        self.consola_container.create_polygon(r, 0, w-r, 0, w, r, w, h-r, w-r, h, r, h, 0, h-r, 0, r, fill="#1e1e1e", outline="#1e1e1e")
        self.consola_container.create_window(8, 8, window=self.txt_consola, anchor="nw", width=w-16, height=h-40)

    def alternar_consola(self):
        if not self.consola_visible:
            self.root.geometry("720x590")
            self.consola_container.pack(fill=tk.BOTH, expand=True, pady=(10, 5))
            if self.btn_copiar_consola is None:
                self.btn_copiar_consola = ttk.Button(self.main_frame, text="📋 Copiar historial de consola", style="Normal.TButton", command=self.copiar_consola)
            self.btn_copiar_consola.pack(pady=(0, 5))
            self.btn_consola_toggle.config(text="Ocultar Consola ❌")
            self.consola_visible = True
        else:
            self.consola_container.pack_forget()
            if self.btn_copiar_consola is not None:
                self.btn_copiar_consola.pack_forget()
            self.root.geometry("720x290")
            self.btn_consola_toggle.config(text="Ver Consola 🛠️")
            self.consola_visible = False

    def copiar_consola(self):
        contenido = self.txt_consola.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(contenido)
        messagebox.showinfo("Astra Music Downloader", "Contenido de la consola copiado.")

    def seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory(initialdir=self.carpeta_var.get(), title="Seleccionar Carpeta")
        if carpeta:
            self.carpeta_var.set(carpeta)

    def timestamp(self):
        return datetime.now().strftime("%H:%M:%S")

    def verificar_dependencias_inicio(self):
        try:
            subprocess.run([sys.executable, "-c", "import yt_dlp"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, timeout=5)
            self.root.after(0, self.log_consola, f"[{self.timestamp()}] Sistema listo. Dependencias correctas.\n")
        except Exception:
            self.root.after(0, self.log_consola, f"[{self.timestamp()}] Aviso: 'yt-dlp' no detectado. Presiona 'Actualizar Librerías'.\n")

    def log_consola(self, texto):
        self.txt_consola.config(state="normal")
        self.txt_consola.insert(tk.END, texto)
        self.txt_consola.see(tk.END)
        self.txt_consola.config(state="disabled")

    def alternar_controles(self, estado):
        self.btn_descargar.config(state=estado)
        self.btn_buscar.config(state=estado)
        self.btn_actualizar.config(state=estado)
        self.btn_pegar.config(state=estado)
        self.url_entry.config(state=estado)

    def iniciar_actualizacion(self):
        if self.descargando or self.actualizando:
            return
        self.actualizando = True
        self.alternar_controles("disabled")
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        self.progress_bar['value'] = 0
        self.lbl_estado.config(text="Actualizando yt-dlp... 0%")
        self.log_consola(f"[{self.timestamp()}] Iniciando actualización de yt-dlp...\n")
        hilo_actualizacion = threading.Thread(target=self.actualizar_librerias)
        hilo_actualizacion.daemon = True
        hilo_actualizacion.start()

    def actualizar_librerias(self):
        import socket
        try:
            socket.create_connection(("pypi.org", 80), timeout=3)
        except OSError:
            self.root.after(0, self.log_consola, f"[{self.timestamp()}] ERROR: Sin conexión a internet.\n")
            self.root.after(0, self.finalizar_actualizacion_error, "Error: Sin conexión a internet.")
            return

        # Modificado con '--break-system-packages' para compatibilidad total con Astra Linux / Debian 12
        comando = [sys.executable, "-m", "pip", "install", "-U", "yt-dlp", "--user", "--break-system-packages"]
        self.root.after(0, self.actualizar_progreso_ui, 20, "Actualizando yt-dlp... 20%")

        try:
            proceso = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            self.root.after(0, self.actualizar_progreso_ui, 60, "Descargando e instalando... 60%")

            for linea in proceso.stdout:
                self.root.after(0, self.log_consola, linea)

            proceso.communicate()
            if proceso.returncode == 0:
                self.root.after(0, self.actualizar_progreso_ui, 100, "Actualización completa.")
                self.root.after(0, self.log_consola, f"[{self.timestamp()}] Actualización completada con éxito.\n")
                self.root.after(0, self.finalizar_actualizacion_exito)
            else:
                self.root.after(0, self.log_consola, f"[{self.timestamp()}] ERROR: pip terminó con código {proceso.returncode}.\n")
                self.root.after(0, self.finalizar_actualizacion_error, "Error en pip.")
        except Exception as e:
            self.root.after(0, self.log_consola, f"[{self.timestamp()}] ERROR: {str(e)}\n{traceback.format_exc()}\n")
            self.root.after(0, self.finalizar_actualizacion_error, f"Error: {str(e)}")

    def actualizar_progreso_ui(self, porcentaje, texto_estado):
        self.progress_bar['value'] = porcentaje
        self.lbl_estado.config(text=texto_estado)

    def finalizar_actualizacion_exito(self):
        messagebox.showinfo("Astra Music Downloader", "Librerías actualizadas.\nReiniciando...")
        self.root.after(1500, self.reiniciar_programa)

    def finalizar_actualizacion_error(self, mensaje_error):
        messagebox.showerror("Error", mensaje_error)
        self.progress_bar.pack_forget()
        self.alternar_controles("normal")
        self.actualizando = False

    def reiniciar_programa(self):
        try:
            args = [sys.executable] + sys.argv
            os.execv(sys.executable, args)
        except Exception:
            self.progress_bar.pack_forget()
            self.alternar_controles("normal")
            self.actualizando = False

    def iniciar_descarga(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Atención", "Introduce una URL válida.")
            return
        self.descargando = True
        self.alternar_controles("disabled")
        self.lbl_estado.config(text="Descargando audio... 0%")
        self.progress_bar.config(mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        self.progress_bar['value'] = 0
        self.log_consola(f"[{self.timestamp()}] Iniciando descarga: {url}\n")

        hilo_descarga = threading.Thread(target=self.ejecutar_descarga, args=(url,))
        hilo_descarga.daemon = True
        hilo_descarga.start()

    def _hook_progreso(self, d):
        if d.get('status') == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            descargado = d.get('downloaded_bytes', 0)
            if total:
                porcentaje = descargado / total * 100
                self.root.after(0, self.actualizar_progreso_ui, porcentaje,
                                 f"Descargando audio... {porcentaje:.0f}%")
        elif d.get('status') == 'finished':
            self.root.after(0, self.actualizar_progreso_ui, 100, "Convirtiendo a MP3 a 320 kbps...")
            self.root.after(0, self.log_consola, f"[{self.timestamp()}] Descarga completa. Convirtiendo a MP3 a 320 kbps...\n")

    def ejecutar_descarga(self, url, intento=1, max_intentos=2):
        try:
            import yt_dlp
        except ImportError:
            self.root.after(0, self.log_consola, f"[{self.timestamp()}] ERROR: yt-dlp no está instalado.\n")
            self.root.after(0, self.finalizar_descarga, False,
                             "Error: 'yt-dlp' no está instalado.\nPresiona 'Actualizar Librerías'.")
            return

        carpeta_destino = self.carpeta_var.get()
        output_template = os.path.join(carpeta_destino, "%(title)s.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'noplaylist': True,
            'progress_hooks': [self._hook_progreso],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',  # Forzado real a 320 kbps (CBR)
            }],
            'audioquality': '320',          # Asegura metadatos consistentes a 320 kbps
            'quiet': True,
            'no_warnings': False,
            'logger': LoggerYtDlp(self),
        }

        self.root.after(0, self.log_consola, f"[{self.timestamp()}] Intento {intento}/{max_intentos}...\n")

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.root.after(0, self.log_consola, f"[{self.timestamp()}] Descarga completada con éxito.\n")
            self.root.after(0, self.finalizar_descarga, True, "Descarga completada con éxito a 320 kbps.")
        except Exception as e:
            detalle = f"[{self.timestamp()}] ERROR en intento {intento}: {str(e)}\n"
            self.root.after(0, self.log_consola, detalle)

            if intento < max_intentos:
                self.root.after(0, self.log_consola, f"[{self.timestamp()}] Reintentando descarga automáticamente...\n")
                self.root.after(0, self.actualizar_progreso_ui, 0, f"Reintentando... (intento {intento + 1}/{max_intentos})")
                self.ejecutar_descarga(url, intento=intento + 1, max_intentos=max_intentos)
            else:
                self.root.after(0, self.log_consola, f"[{self.timestamp()}] Se agotaron los {max_intentos} intentos.\n")
                self.root.after(0, self.finalizar_descarga, False, f"Error tras {max_intentos} intentos:\n{str(e)}")

    def finalizar_descarga(self, exito, mensaje):
        self.progress_bar.pack_forget()
        self.progress_bar['value'] = 0
        if exito:
            messagebox.showinfo("Astra Music Downloader", mensaje)
            self.lbl_estado.config(text="Descarga finalizada.")
            self.url_var.set("")
        else:
            messagebox.showerror("Error", mensaje)
            self.lbl_estado.config(text="Descarga interrumpida.")
        self.alternar_controles("normal")
        self.descargando = False


if __name__ == "__main__":
    root = tk.Tk()
    app = AstraMusicApp(root)
    root.mainloop()
