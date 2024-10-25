import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import yt_dlp
import os
import threading
from datetime import datetime
import concurrent.futures
import re

class VideoDownloader:
    def __init__(self):
        self.setup_window()
        self.setup_styles()
        self.create_widgets()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self.save_dir = ""
        
    def setup_window(self):
        self.root = ctk.CTk()
        self.root.title("Ultimate Video Downloader")
        self.root.geometry("800x800")
        self.root.resizable(True, True)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("custom.Horizontal.TProgressbar",
                             troughcolor='#2b2b2b',
                             background='#1f538d')
        
        self.style.configure("Custom.Vertical.TScrollbar",
                           background='#1f538d',
                           troughcolor='#2b2b2b',
                           width=10,
                           arrowsize=13)

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Ultimate Video Downloader",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        url_frame = ctk.CTkFrame(main_frame)
        url_frame.pack(fill="x", padx=20, pady=10)
        
        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="Pega aquí el enlace del video...",
            height=40,
            width=400
        )
        self.url_entry.pack(side="left", expand=True, padx=(0, 10))
        
        paste_button = ctk.CTkButton(
            url_frame,
            text="Pegar",
            width=100,
            command=self.paste_url
        )
        paste_button.pack(side="left", padx=5)
        
        search_button = ctk.CTkButton(
            url_frame,
            text="Buscar",
            width=100,
            command=self.search_video
        )
        search_button.pack(side="left", padx=5)
        
        self.video_info_frame = ctk.CTkFrame(main_frame)
        self.video_info_frame.pack(fill="x", padx=20, pady=10)
        
        self.platform_label = ctk.CTkLabel(
            self.video_info_frame,
            text="",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.platform_label.pack(pady=5)
        
        self.video_title_label = ctk.CTkLabel(
            self.video_info_frame,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.video_title_label.pack(pady=5)
        
        self.video_duration_label = ctk.CTkLabel(
            self.video_info_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.video_duration_label.pack(pady=5)

        options_frame = ctk.CTkFrame(main_frame)
        options_frame.pack(fill="x", padx=20, pady=20)
        
        format_frame = ctk.CTkFrame(options_frame)
        format_frame.pack(fill="x", pady=10)
        
        format_label = ctk.CTkLabel(
            format_frame,
            text="Formato:",
            font=ctk.CTkFont(size=16)
        )
        format_label.pack(side="left", padx=10)
        
        self.format_var = tk.StringVar(value="MP4")
        
        mp4_radio = ctk.CTkRadioButton(
            format_frame,
            text="MP4 (Video)",
            variable=self.format_var,
            value="MP4",
            command=self.toggle_quality_options
        )
        mp4_radio.pack(side="left", padx=20)
        
        mp3_radio = ctk.CTkRadioButton(
            format_frame,
            text="MP3 (Audio)",
            variable=self.format_var,
            value="MP3",
            command=self.toggle_quality_options
        )
        mp3_radio.pack(side="left", padx=20)
        self.quality_frame = ctk.CTkFrame(options_frame)
        self.quality_frame.pack(fill="x", pady=10)
        
        quality_label = ctk.CTkLabel(
            self.quality_frame,
            text="Calidad:",
            font=ctk.CTkFont(size=16)
        )
        quality_label.pack(side="left", padx=10)
        
        self.quality_var = tk.StringVar(value="720")
        qualities = [("360p", "360"), ("720p", "720"), ("1080p", "1080"), ("4K", "2160")]
        
        for text, value in qualities:
            radio = ctk.CTkRadioButton(
                self.quality_frame,
                text=text,
                variable=self.quality_var,
                value=value
            )
            radio.pack(side="left", padx=20)
        
        location_button = ctk.CTkButton(
            main_frame,
            text="Seleccionar ubicación de guardado",
            width=200,
            height=40,
            command=self.select_save_location,
            font=ctk.CTkFont(size=14)
        )
        location_button.pack(pady=10)
        
        self.location_label = ctk.CTkLabel(
            main_frame,
            text="No se ha seleccionado ubicación",
            font=ctk.CTkFont(size=12)
        )
        self.location_label.pack()
            
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            style="custom.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate",
            length=700
        )
        self.progress_bar.pack(pady=10)
        
        self.status_label = ctk.CTkLabel(
            progress_frame,
            text="Listo para descargar",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack()
        
        self.download_button = ctk.CTkButton(
            main_frame,
            text="Descargar",
            width=200,
            height=40,
            command=self.start_download,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.download_button.pack(pady=20)
        
        history_frame = ctk.CTkFrame(main_frame)
        history_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        history_label = ctk.CTkLabel(
            history_frame,
            text="Historial de Descargas",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        history_label.pack(pady=10)
        
        history_container = ctk.CTkFrame(history_frame)
        history_container.pack(fill="both", expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(history_container, style="Custom.Vertical.TScrollbar")
        scrollbar.pack(side="right", fill="y")
        
        self.history_text = ctk.CTkTextbox(
            history_container,
            height=150,
            yscrollcommand=scrollbar.set
        )
        self.history_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.history_text.yview)

    def select_save_location(self):
        self.save_dir = filedialog.askdirectory(title="Seleccionar carpeta de destino")
        if self.save_dir:
            self.location_label.configure(text=f"Ubicación: {self.save_dir}")
        
    def paste_url(self):
        try:
            clipboard = self.root.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard)
        except:
            messagebox.showwarning("Error", "No hay contenido en el portapapeles")

    def search_video(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Error", "Ingrese una URL primero")
            return
            
        valid, platform = self.validate_url(url)
        if not valid:
            messagebox.showerror("URL inválida", "Ingrese una URL válida de una plataforma soportada")
            return
            
        self.status_label.configure(text="Buscando información del video...")
        
        def fetch_info():
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': True
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Sin título')
                    duration = info.get('duration', 0)
                    self.root.after(0, lambda: self.update_video_info(title, duration, platform))
                    self.root.after(0, lambda: self.status_label.configure(text="Video encontrado"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.status_label.configure(text=f"Error: {str(e)}"))
                
        threading.Thread(target=fetch_info, daemon=True).start()

    def update_video_info(self, title, duration, platform):
        platform_names = {
            'youtube': 'YouTube',
            'tiktok': 'TikTok',
            'facebook': 'Facebook',
            'twitter': 'Twitter/X',
            'instagram': 'Instagram'
        }
        
        self.platform_label.configure(text=f"Plataforma: {platform_names.get(platform, platform)}")
        self.video_title_label.configure(text=f"Título: {title}")
        if duration:
            minutes = duration // 60
            seconds = duration % 60
            self.video_duration_label.configure(text=f"Duración: {minutes}:{seconds:02d}")
        else:
            self.video_duration_label.configure(text="Duración: No disponible")
        
    def toggle_quality_options(self):
        if self.format_var.get() == "MP3":
            for widget in self.quality_frame.winfo_children():
                if isinstance(widget, ctk.CTkRadioButton):
                    widget.configure(state="disabled")
        else:
            for widget in self.quality_frame.winfo_children():
                if isinstance(widget, ctk.CTkRadioButton):
                    widget.configure(state="normal")
            
    def validate_url(self, url):
        patterns = {
            'youtube': r'(?:youtube\.com|youtu\.be)',
            'tiktok': r'tiktok\.com',
            'facebook': r'(facebook\.com|fb\.com)',
            'twitter': r'(twitter\.com|x\.com)',
            'instagram': r'instagram\.com'
        }
        for platform, pattern in patterns.items():
            if re.search(pattern, url):
                return True, platform
        return False, None

    def get_format_options(self, platform, format_type):
        if format_type == 'MP4':
            if platform in ['tiktok', 'facebook', 'instagram']:
                return 'best[ext=mp4]/best'
            else:
                quality = self.quality_var.get()
                return f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best'
        else:  # MP3
            return 'bestaudio/best'

    def download_file(self, url, format_type, quality, save_dir):
        valid, platform = self.validate_url(url)
        if not valid:
            return "URL no válida"

        try:
            # Configuración básica
            ydl_opts = {
                'outtmpl': os.path.join(save_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [self.update_progress],
                'quiet': True,
                'no_warnings': True,
                'format': self.get_format_options(platform, format_type)
            }

            # Configuración específica para Facebook
            if platform == 'facebook':
                ydl_opts.update({
                    'extract_flat': False,
                    'no_warnings': False,  # Habilitamos warnings para Facebook
                    'extractor_args': {
                        'facebook': {
                            'browser_agent': 'firefox',  # Cambiado a firefox
                            'download_timeout': 60,  # Aumentado el timeout
                            'format': 'best'  # Forzar mejor calidad disponible
                        }
                    },
                    # Intentar diferentes formatos si el primero falla
                    'format': 'best/bestvideo+bestaudio/best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]',
                    'force_generic_extractor': False,
                    'socket_timeout': 60,
                    'retries': 3,  # Número de reintentos si falla
                })

                # Comprobar si existe el archivo de cookies
                cookies_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')
                if os.path.exists(cookies_file):
                    ydl_opts['cookiefile'] = cookies_file
                else:
                    # Si no hay cookies, mostrar mensaje instructivo
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Cookies no encontradas", 
                        "Para descargar videos de Facebook de forma más confiable, necesitas crear un archivo 'cookies.txt' "
                        "con tus cookies de Facebook. Puedes usar extensiones como 'Get cookies.txt' en tu navegador."
                    ))


            # Proceso de descarga
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    # Primero extraemos la información
                    info = ydl.extract_info(url, download=False)
                    # Verificamos si el video está disponible
                    if not info:
                        return "Error: No se pudo obtener información del video"
                    
                    # Procedemos con la descarga
                    ydl.download([url])
                    
                    return "Descarga completada exitosamente"
                except yt_dlp.utils.DownloadError as e:
                    error_message = str(e)
                    if "This video is unavailable" in error_message:
                        return "Error: El video no está disponible"
                    elif "Sign in to confirm your age" in error_message:
                        return "Error: Video con restricción de edad"
                    else:
                        return f"Error en la descarga: {error_message}"
                        
        except Exception as e:
            return f"Error inesperado: {str(e)}"

    def update_progress(self, d):
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                
                if total:
                    percentage = (downloaded / total) * 100
                    self.root.after(0, lambda: self.progress_bar.configure(value=percentage))
                    
                speed = d.get('speed', 0)
                if speed:
                    speed_mb = speed / 1024 / 1024  # Convertir a MB/s
                    eta = d.get('eta', 0)
                    status_text = f"Descargando... {speed_mb:.1f} MB/s - ETA: {eta} segundos"
                    self.root.after(0, lambda: self.status_label.configure(text=status_text))
                    
            except Exception as e:
                print(f"Error actualizando progreso: {str(e)}")
                
        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.status_label.configure(text="Procesando archivo..."))
            
    def validate_url(self, url):
        patterns = {
            'youtube': r'(?:youtube\.com|youtu\.be)',
            'tiktok': r'tiktok\.com',
            'facebook': r'(facebook\.com|fb\.com)',
            'twitter': r'(twitter\.com|x\.com)',
            'instagram': r'instagram\.com'
        }
        
        for platform, pattern in patterns.items():
            if re.search(pattern, url, re.IGNORECASE):
                return True, platform
        return False, None

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Error", "Ingrese una URL primero")
            return
            
        if not self.save_dir:
            messagebox.showwarning("Error", "Seleccione una ubicación de guardado")
            return
            
        self.download_button.configure(state="disabled")
        self.progress_bar.configure(value=0)
        self.status_label.configure(text="Iniciando descarga...")
        
        format_type = self.format_var.get()
        quality = self.quality_var.get()
        
        def download_thread():
            try:
                status = self.download_file(url, format_type, quality, self.save_dir)
                self.root.after(0, lambda: self.download_completed(status))
                self.root.after(0, lambda: self.add_to_history(url, format_type, status))
            except Exception as e:
                error_msg = f"Error inesperado: {str(e)}"
                self.root.after(0, lambda: self.download_completed(error_msg))
                self.root.after(0, lambda: self.add_to_history(url, format_type, error_msg))
            
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
        
    def download_completed(self, status):
        self.download_button.configure(state="normal")
        self.progress_bar.configure(value=100)
        self.status_label.configure(text=status)
        
        if "exitosamente" in status:
            messagebox.showinfo("Éxito", "Descarga completada exitosamente")
        else:
            messagebox.showerror("Error", status)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = VideoDownloader()
    app.run()
