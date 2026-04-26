VERSION = "0.4"

import os
import sys
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import cv2
import webbrowser

class CheIMG(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración principal de la ventana
        self.title("Che IMG - Sitios de Memoria")
        self.geometry("1200x800")
        self.minsize(1000, 600)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ==========================================
        # LÓGICA DE RUTAS Y ASSETS
        # ==========================================
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        ruta_assets = os.path.join(base_dir, "_internal", "assets")
        ruta_logo = os.path.join(ruta_assets, "icono_cheimg.png") 
        ruta_icono_ventana = os.path.join(ruta_assets, "icono_cheimg.ico")

        # --- LÓGICA MULTIPLATAFORMA ---
        if sys.platform.startswith("win"):
            # En Windows usamos el .ico clásico
            if os.path.exists(ruta_icono_ventana):
                self.iconbitmap(ruta_icono_ventana)
        else:
            # En Linux o macOS usamos el .png con iconphoto
            if os.path.exists(ruta_logo):
                img_icono = ImageTk.PhotoImage(Image.open(ruta_logo))
                self.iconphoto(True, img_icono)

        # Variables de estado y lógica interna
        self.puntos_izq = {}
        self.puntos_der = {}
        self.img_izq_original = None
        self.img_der_original = None
        self.img_izq_tk = None
        self.img_der_tk = None
        self.zoom_izq = 1.0
        self.pan_x_izq = 0
        self.pan_y_izq = 0
        self.zoom_der = 1.0
        self.pan_x_der = 0
        self.pan_y_der = 0
        self.entry_zoom_izq = None
        self.entry_zoom_der = None
        self.interaccion = {
            'izq': {'start_x': 0, 'start_y': 0, 'arrastrando': False},
            'der': {'start_x': 0, 'start_y': 0, 'arrastrando': False}
        }

        # ==========================================
        # ENCABEZADO GLOBAL
        # ==========================================
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(10, 0))

        if os.path.exists(ruta_logo):
            imagen_logo = ctk.CTkImage(light_image=Image.open(ruta_logo), dark_image=Image.open(ruta_logo), size=(60, 60))
            self.lbl_logo = ctk.CTkLabel(self.header_frame, text="", image=imagen_logo)
        else:
            self.lbl_logo = ctk.CTkLabel(self.header_frame, text="🖼️", font=ctk.CTkFont(size=40))
            
        self.lbl_logo.pack(side="left", padx=(0, 10))

        self.header_text_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.header_text_frame.pack(side="left", fill="y")
        
        self.lbl_title = ctk.CTkLabel(self.header_text_frame, text="Che IMG", font=ctk.CTkFont(size=28, weight="bold"))
        self.lbl_title.pack(anchor="w")
        
        self.lbl_subtitle = ctk.CTkLabel(self.header_text_frame, text="Un desarrollo de sitiosdememoria.uy", text_color="#64b5f6", font=ctk.CTkFont(size=12, underline=True))
        self.lbl_subtitle.pack(anchor="w")

        self.divider = ctk.CTkFrame(self, height=2, fg_color="#333333")
        self.divider.pack(fill="x", padx=20, pady=10)

        # ==========================================
        # BARRA DE NAVEGACIÓN SUPERIOR PERSONALIZADA
        # ==========================================
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.nav_buttons_container = ctk.CTkFrame(self.nav_frame, fg_color="transparent")
        self.nav_buttons_container.pack(anchor="center")

        self.pages_container = ctk.CTkFrame(self, fg_color="transparent")
        self.pages_container.pack(expand=True, fill="both", padx=20, pady=(0, 20))

        self.tab_main = ctk.CTkFrame(self.pages_container, fg_color="transparent")
        self.tab_config = ctk.CTkFrame(self.pages_container, fg_color="transparent")
        self.tab_help = ctk.CTkFrame(self.pages_container, fg_color="transparent")
        self.tab_about = ctk.CTkFrame(self.pages_container, fg_color="transparent")
        self.tab_donate = ctk.CTkFrame(self.pages_container, fg_color="transparent")

        self.nav_buttons = []
        self.frames = [self.tab_main, self.tab_config, self.tab_help, self.tab_about, self.tab_donate]

        self.crear_boton_nav("🔍", "Edición y Unión", self.tab_main)
        self.crear_boton_nav("⚙️", "Configuración", self.tab_config)
        self.crear_boton_nav("❓", "Ayuda", self.tab_help)
        self.crear_boton_nav("ℹ️", "Acerca de", self.tab_about)
        self.crear_boton_nav("❤️", "Donar", self.tab_donate)

        self.seleccionar_pagina(self.tab_main, self.nav_buttons[0])

        self.construir_pestana_principal()
        self.construir_pestana_configuracion()
        self.construir_pestana_ayuda()
        self.construir_pestana_acerca_de()
        self.construir_pestana_donar()

    # ==========================================
    # LÓGICA DE NAVEGACIÓN SUPERIOR
    # ==========================================
    def crear_boton_nav(self, icono, texto, frame_destino):
        btn = ctk.CTkButton(
            self.nav_buttons_container,
            text=f"{icono}\n{texto}",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            text_color="#9e9e9e",
            hover_color="#2b2b2b",
            corner_radius=8,
            width=120,
            height=60,
            command=lambda: self.seleccionar_pagina(frame_destino, btn)
        )
        btn.pack(side="left", padx=5)
        self.nav_buttons.append(btn)

    def seleccionar_pagina(self, frame_destino, boton_activo):
        for frame in self.frames:
            frame.pack_forget()
            
        for btn in self.nav_buttons:
            btn.configure(text_color="#9e9e9e", fg_color="transparent")

        frame_destino.pack(expand=True, fill="both")
        boton_activo.configure(text_color="#64b5f6", fg_color="#2b2b2b")

    # ==========================================
    # CONSTRUCCIÓN DE LA PESTAÑA PRINCIPAL
    # ==========================================
    def construir_pestana_principal(self):
        self.tab_main.grid_columnconfigure(0, weight=1)
        self.tab_main.grid_rowconfigure(0, weight=1)

        self.work_area = ctk.CTkFrame(self.tab_main, fg_color="transparent")
        self.work_area.grid(row=0, column=0, sticky="nsew")
        self.work_area.grid_columnconfigure(0, weight=1)
        self.work_area.grid_columnconfigure(1, weight=1)
        self.work_area.grid_rowconfigure(1, weight=1)

        self.top_panel = ctk.CTkFrame(self.work_area, corner_radius=10)
        self.top_panel.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        self.btn_auto = ctk.CTkButton(self.top_panel, text="✨ Unión Automática (SIFT)", width=200, fg_color="#1976d2", hover_color="#1565c0", command=self.ejecutar_union_automatica)
        self.btn_auto.pack(side="left", padx=20, pady=15)

        self.btn_manual = ctk.CTkButton(self.top_panel, text="📌 Unión Manual (Puntos)", width=200, fg_color="#b85d19", hover_color="#8f4610", command=self.ejecutar_union_manual)
        self.btn_manual.pack(side="left", padx=10, pady=15)
        
        self.btn_limpiar_puntos = ctk.CTkButton(self.top_panel, text="Borrar Puntos", width=120, fg_color="transparent", text_color="#ef5350", border_width=1, border_color="#ef5350", hover_color="#3b1f1f", command=self.limpiar_puntos)
        self.btn_limpiar_puntos.pack(side="left", padx=10, pady=15)

        self.btn_salir = ctk.CTkButton(self.top_panel, text="Salir", width=80, fg_color="transparent", border_width=1, text_color="#ef5350", hover_color="#3b1f1f", command=self.destroy)
        self.btn_salir.pack(side="right", padx=20, pady=15)

        self.left_panel = ctk.CTkFrame(self.work_area, corner_radius=10)
        self.left_panel.grid(row=1, column=0, padx=(0, 5), sticky="nsew")
        self.canvas_left = ctk.CTkCanvas(self.left_panel, bg="#1e1e1e", highlightthickness=0, cursor="hand2")
        self.canvas_left.pack(expand=True, fill="both", padx=10, pady=(10, 0))
        self.configurar_eventos_canvas(self.canvas_left, 'izq')
        self.crear_controles_zoom(self.left_panel, 'izq')

        self.right_panel = ctk.CTkFrame(self.work_area, corner_radius=10)
        self.right_panel.grid(row=1, column=1, padx=(5, 0), sticky="nsew")
        self.canvas_right = ctk.CTkCanvas(self.right_panel, bg="#1e1e1e", highlightthickness=0, cursor="hand2")
        self.canvas_right.pack(expand=True, fill="both", padx=10, pady=(10, 0))
        self.configurar_eventos_canvas(self.canvas_right, 'der')
        self.crear_controles_zoom(self.right_panel, 'der')

        self.canvas_left.bind("<Configure>", lambda e: self.redibujar_placeholder_si_vacio('izq'))
        self.canvas_right.bind("<Configure>", lambda e: self.redibujar_placeholder_si_vacio('der'))

    # ==========================================
    # CONSTRUCCIÓN DE PESTAÑAS SECUNDARIAS
    # ==========================================
    def construir_pestana_configuracion(self):
        frame = ctk.CTkFrame(self.tab_config, fg_color="transparent")
        frame.pack(padx=40, pady=40, fill="both", expand=True)
        
        ctk.CTkLabel(frame, text="Configuración del Motor de Visión", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(frame, text="Ajusta los parámetros internos para el procesamiento de imágenes de alta resolución.", text_color="gray").pack(anchor="w", pady=(0, 20))
        
        ctk.CTkLabel(frame, text="Resolución máxima para análisis SIFT (px):", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        ctk.CTkLabel(frame, text="Reducir este valor aumenta la velocidad pero podría perder precisión en textos pequeños.", text_color="gray").pack(anchor="w")
        self.entry_sift_max = ctk.CTkEntry(frame, width=200)
        self.entry_sift_max.insert(0, "1500")
        self.entry_sift_max.pack(anchor="w", pady=(5, 20))

        btn_guardar = ctk.CTkButton(frame, text="💾 Guardar Configuración", fg_color="#388e3c", hover_color="#2e7d32")
        btn_guardar.pack(anchor="w", pady=10)

    def construir_pestana_ayuda(self):
        frame = ctk.CTkScrollableFrame(self.tab_help, fg_color="transparent")
        frame.pack(padx=40, pady=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Guía de Uso de Che IMG", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(frame, text="Che IMG te permite unir recortes escaneados de diarios y afiches gigantes mediante algoritmos de visión por computadora y fundido de transparencias (Feathering).", text_color="gray", wraplength=800, justify="left").pack(anchor="w", pady=(5, 30))

        ctk.CTkLabel(frame, text="Paso a Paso: Unión Automática", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(frame, text="1. Haz clic en los recuadros para cargar las mitades.\n2. Gira las mitades si es necesario usando los iconos que estan en la parte inferior izquierda de cada imagen, de modo que las partes a unir queden enfrentadas entre sí (al centro de la pantalla).\n3. Presiona '✨ Unión Automática (SIFT)'.\n4. El programa escaneará las franjas de solapamiento y creará un panorama perfecto.\n5. Si el programa falla o el escaneo es muy complejo, usa la Unión Manual.", text_color="#d4d4d4", justify="left").pack(anchor="w", pady=(10, 20))

        ctk.CTkLabel(frame, text="Paso a Paso: Unión Manual", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(frame, text="1. Usa la rueda del ratón para hacer zoom y mantén presionado el clic izquierdo (o derecho) para arrastrar la imagen.\n2. Haz clic rápido para marcar puntos de control. Necesitas marcar el mismo punto exacto en ambas imágenes.\n3. Marca al menos 4 puntos (ej: letras cortadas, manchas) de forma distribuida.\n4. Presiona '📌 Unión Manual (Puntos)'.", text_color="#d4d4d4", justify="left").pack(anchor="w", pady=(10, 20))

    def construir_pestana_acerca_de(self):
        frame = ctk.CTkFrame(self.tab_about, fg_color="transparent")
        frame.pack(padx=40, pady=40, fill="both", expand=True)
        
        ctk.CTkLabel(frame, text="Che IMG", font=ctk.CTkFont(size=36, weight="bold")).pack()
        ctk.CTkLabel(frame, text="Motor avanzado de reconstrucción documental mediante visión artificial.", text_color="gray").pack(pady=(5, 40))
        
        info_frame = ctk.CTkFrame(frame, fg_color="transparent")
        info_frame.pack()
        ctk.CTkLabel(info_frame, text="Detalles del Proyecto", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(info_frame, text="• Versión: 1.0\n• Motor Matemático: OpenCV / RANSAC / SIFT\n• Fecha de creación: Marzo de 2026\n• Licencia: GNU GPLv3 (Software Libre)", justify="left").pack(anchor="w", pady=10)
        
        ctk.CTkLabel(frame, text="Esta aplicación fue desarrollada por sitiosdememoria.uy con el objetivo de facilitar el análisis y la investigación de grandes volúmenes documentales. Cuenta con una licencia de software libre que permite su uso, estudio, difusión y modificación, como parte del compromiso del proyecto con las luchas por memoria, verdad y justicia.", text_color="#64b5f6", wraplength=700, justify="center", font=ctk.CTkFont(slant="italic")).pack(pady=30)

    def construir_pestana_donar(self):
        frame = ctk.CTkFrame(self.tab_donate, fg_color="transparent")
        frame.pack(padx=40, pady=40, fill="both", expand=True)
        
        ctk.CTkLabel(frame, text="Apoya el proyecto", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(20, 10))
        ctk.CTkLabel(frame, text="Che IMG es y siempre será una herramienta de software libre y gratuita. Tu aporte voluntario nos ayuda a mantener nuestra infraestructura, desarrollar nuevas herramientas y continuar con el trabajo militante de investigación y preservación de la memoria histórica.", text_color="gray", wraplength=600, justify="center").pack(pady=20)
        
        btn_donar = ctk.CTkButton(
            frame, 
            text="❤️ Hacer un aporte solidario", 
            font=ctk.CTkFont(size=16, weight="bold"), 
            fg_color="#c2185b", 
            hover_color="#880e4f", 
            width=250, 
            height=50,
            command=lambda: webbrowser.open("https://ko-fi.com/sitiosdememoriauy")
        )
        btn_donar.pack(pady=30)

    # ==========================================
    # LÓGICA DE INTERFAZ Y EVENTOS
    # ==========================================
    def crear_controles_zoom(self, parent_frame, lado):
        bottom_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        bottom_frame.pack(pady=5, fill="x", padx=10)
        
        btn_eliminar = ctk.CTkButton(
            bottom_frame, text="🗑️", width=40, fg_color="transparent", 
            text_color="#ef5350", border_width=1, border_color="#ef5350", 
            hover_color="#3b1f1f", command=lambda: self.eliminar_imagen(lado)
        )
        
        btn_rotar_izq = ctk.CTkButton(bottom_frame, text="↺", width=30, fg_color="transparent", border_width=1, command=lambda: self.girar_imagen(lado, 'izq'))
        btn_rotar_der = ctk.CTkButton(bottom_frame, text="↻", width=30, fg_color="transparent", border_width=1, command=lambda: self.girar_imagen(lado, 'der'))

        if lado == 'izq':
            self.btn_eliminar_izq = btn_eliminar
            self.btn_rotar_izq_izq = btn_rotar_izq
            self.btn_rotar_der_izq = btn_rotar_der
        else:
            self.btn_eliminar_der = btn_eliminar
            self.btn_rotar_izq_der = btn_rotar_izq
            self.btn_rotar_der_der = btn_rotar_der

        zoom_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        zoom_frame.pack(side="right")
        
        btn_out = ctk.CTkButton(zoom_frame, text="-", width=30, command=lambda: self.modificar_zoom(lado, 1/1.2))
        btn_out.pack(side="left", padx=5)
        
        entry = ctk.CTkEntry(zoom_frame, width=60, justify="center")
        entry.pack(side="left", padx=5)
        entry.bind("<Return>", lambda event, l=lado: self.aplicar_zoom_manual(l))
        
        if lado == 'izq': self.entry_zoom_izq = entry
        else: self.entry_zoom_der = entry
            
        btn_in = ctk.CTkButton(zoom_frame, text="+", width=30, command=lambda: self.modificar_zoom(lado, 1.2))
        btn_in.pack(side="left", padx=5)

        btn_11 = ctk.CTkButton(zoom_frame, text="1:1", width=35, fg_color="transparent", border_width=1, command=lambda: self.escala_original(lado))
        btn_11.pack(side="left", padx=5)

        btn_fit = ctk.CTkButton(zoom_frame, text="⛶", width=30, fg_color="transparent", border_width=1, command=lambda: self.ajustar_pantalla(lado))
        btn_fit.pack(side="left", padx=5)

    def dibujar_placeholder(self, lado):
        canvas = self.canvas_left if lado == 'izq' else self.canvas_right
        canvas.delete("all")
        texto = "Agregar imagen izquierda" if lado == 'izq' else "Agregar imagen derecha"
        
        c_w = canvas.winfo_width()
        c_h = canvas.winfo_height()
        
        if c_w <= 1: c_w = 400
        if c_h <= 1: c_h = 600

        canvas.create_text(c_w/2, c_h/2 - 30, text="+", font=("Arial", 80, "bold"), fill="#444444", tags="placeholder")
        canvas.create_text(c_w/2, c_h/2 + 40, text=texto, font=("Arial", 24, "bold"), fill="#666666", tags="placeholder")
        canvas.configure(cursor="hand2")

    def redibujar_placeholder_si_vacio(self, lado):
        img_orig = self.img_izq_original if lado == 'izq' else self.img_der_original
        if not img_orig:
            self.dibujar_placeholder(lado)

    def configurar_eventos_canvas(self, canvas, lado):
        canvas.bind("<ButtonPress-1>", lambda event, l=lado: self.iniciar_interaccion(event, l))
        canvas.bind("<B1-Motion>", lambda event, l=lado: self.arrastrar_imagen(event, l))
        canvas.bind("<ButtonRelease-1>", lambda event, l=lado: self.finalizar_interaccion(event, l))
        canvas.bind("<Button-3>", lambda event, l=lado: self.eliminar_punto(event, l))
        canvas.bind("<MouseWheel>", lambda event, l=lado: self.zoom_rueda(event, l))
        canvas.bind("<Button-4>", lambda event, l=lado: self.zoom_rueda(event, l))
        canvas.bind("<Button-5>", lambda event, l=lado: self.zoom_rueda(event, l))

    def iniciar_interaccion(self, event, lado):
        img_orig = self.img_izq_original if lado == 'izq' else self.img_der_original
        if not img_orig:
            self.cargar_imagen(lado)
            return

        self.interaccion[lado]['start_x'] = event.x
        self.interaccion[lado]['start_y'] = event.y
        self.interaccion[lado]['arrastrando'] = False

    def arrastrar_imagen(self, event, lado):
        dx = event.x - self.interaccion[lado]['start_x']
        dy = event.y - self.interaccion[lado]['start_y']
        
        if not self.interaccion[lado]['arrastrando']:
            if abs(dx) > 3 or abs(dy) > 3:
                self.interaccion[lado]['arrastrando'] = True
                canvas = self.canvas_left if lado == 'izq' else self.canvas_right
                canvas.configure(cursor="hand2")
            else: return 

        if self.interaccion[lado]['arrastrando']:
            if lado == 'izq' and self.img_izq_original:
                self.pan_x_izq += dx
                self.pan_y_izq += dy
                self.canvas_left.move("all", dx, dy)
            elif lado == 'der' and self.img_der_original:
                self.pan_x_der += dx
                self.pan_y_der += dy
                self.canvas_right.move("all", dx, dy)
                
            self.interaccion[lado]['start_x'] = event.x
            self.interaccion[lado]['start_y'] = event.y

    def finalizar_interaccion(self, event, lado):
        img_orig = self.img_izq_original if lado == 'izq' else self.img_der_original
        if not img_orig: return

        canvas = self.canvas_left if lado == 'izq' else self.canvas_right
        canvas.configure(cursor="crosshair") 
        if not self.interaccion[lado]['arrastrando']:
            self.marcar_punto(event, lado)
        self.interaccion[lado]['arrastrando'] = False

    def actualizar_texto_zoom(self, lado):
        entry = self.entry_zoom_izq if lado == 'izq' else self.entry_zoom_der
        zoom = self.zoom_izq if lado == 'izq' else self.zoom_der
        if entry:
            porcentaje = int(zoom * 100)
            entry.delete(0, 'end')
            entry.insert(0, f"{porcentaje}%")

    def aplicar_zoom_manual(self, lado):
        entry = self.entry_zoom_izq if lado == 'izq' else self.entry_zoom_der
        texto = entry.get().replace('%', '').strip()
        try:
            nuevo_zoom = float(texto) / 100.0
            nuevo_zoom = max(0.01, min(nuevo_zoom, 50.0))
            if lado == 'izq' and self.img_izq_original:
                self.zoom_izq = nuevo_zoom
                self.actualizar_texto_zoom('izq')
                self.dibujar_estado('izq')
            elif lado == 'der' and self.img_der_original:
                self.zoom_der = nuevo_zoom
                self.actualizar_texto_zoom('der')
                self.dibujar_estado('der')
        except ValueError:
            self.actualizar_texto_zoom(lado)

    def cargar_imagen(self, lado):
        tipos = [("Imágenes", "*.jpg *.jpeg *.png *.tiff *.tif"), ("Todos", "*.*")]
        ruta = filedialog.askopenfilename(title="Seleccionar imagen", filetypes=tipos)
        if not ruta: return

        img = Image.open(ruta)
        if lado == 'izq':
            self.img_izq_original = img
            self.puntos_izq.clear()
            self.canvas_left.configure(cursor="crosshair")
            if hasattr(self, 'btn_eliminar_izq'):
                self.btn_eliminar_izq.pack(side="left")
                self.btn_rotar_izq_izq.pack(side="left", padx=(10, 0))
                self.btn_rotar_der_izq.pack(side="left", padx=5)
            self.ajustar_pantalla('izq')
        else:
            self.img_der_original = img
            self.puntos_der.clear()
            self.canvas_right.configure(cursor="crosshair")
            if hasattr(self, 'btn_eliminar_der'):
                self.btn_eliminar_der.pack(side="left")
                self.btn_rotar_izq_der.pack(side="left", padx=(10, 0))
                self.btn_rotar_der_der.pack(side="left", padx=5)
            self.ajustar_pantalla('der')

    def eliminar_imagen(self, lado):
        if lado == 'izq':
            self.img_izq_original = None
            self.img_izq_tk = None
            self.puntos_izq.clear()
            self.zoom_izq = 1.0
            self.pan_x_izq = 0
            self.pan_y_izq = 0
            if self.entry_zoom_izq: self.entry_zoom_izq.delete(0, 'end')
            if hasattr(self, 'btn_eliminar_izq'):
                self.btn_eliminar_izq.pack_forget()
                self.btn_rotar_izq_izq.pack_forget()
                self.btn_rotar_der_izq.pack_forget()
        else:
            self.img_der_original = None
            self.img_der_tk = None
            self.puntos_der.clear()
            self.zoom_der = 1.0
            self.pan_x_der = 0
            self.pan_y_der = 0
            if self.entry_zoom_der: self.entry_zoom_der.delete(0, 'end')
            if hasattr(self, 'btn_eliminar_der'):
                self.btn_eliminar_der.pack_forget()
                self.btn_rotar_izq_der.pack_forget()
                self.btn_rotar_der_der.pack_forget()

        self.dibujar_placeholder(lado)

    def girar_imagen(self, lado, direccion):
        img_orig = self.img_izq_original if lado == 'izq' else self.img_der_original
        if not img_orig: return

        puntos = self.puntos_izq if lado == 'izq' else self.puntos_der
        w, h = img_orig.size
        
        if direccion == 'izq':
            img_rotated = img_orig.transpose(Image.Transpose.ROTATE_90)
            nuevos_puntos = {pid: (py, w - px) for pid, (px, py) in puntos.items()}
        else:
            img_rotated = img_orig.transpose(Image.Transpose.ROTATE_270)
            nuevos_puntos = {pid: (h - py, px) for pid, (px, py) in puntos.items()}

        puntos.clear()
        puntos.update(nuevos_puntos)

        if lado == 'izq':
            self.img_izq_original = img_rotated
        else:
            self.img_der_original = img_rotated

        self.ajustar_pantalla(lado)

    def escala_original(self, lado):
        if lado == 'izq' and self.img_izq_original:
            self.zoom_izq = 1.0
            self.pan_x_izq = 0
            self.pan_y_izq = 0
            self.actualizar_texto_zoom('izq')
            self.dibujar_estado('izq')
        elif lado == 'der' and self.img_der_original:
            self.zoom_der = 1.0
            self.pan_x_der = 0
            self.pan_y_der = 0
            self.actualizar_texto_zoom('der')
            self.dibujar_estado('der')

    def ajustar_pantalla(self, lado):
        canvas = self.canvas_left if lado == 'izq' else self.canvas_right
        img = self.img_izq_original if lado == 'izq' else self.img_der_original
        if not img: return

        canvas.update()
        c_w, c_h = canvas.winfo_width(), canvas.winfo_height()
        i_w, i_h = img.size
        
        ratio_ajuste = min(c_w / i_w, c_h / i_h)

        if lado == 'izq':
            self.zoom_izq = ratio_ajuste
            self.pan_x_izq, self.pan_y_izq = 0, 0
            self.actualizar_texto_zoom('izq')
            self.dibujar_estado('izq')
        else:
            self.zoom_der = ratio_ajuste
            self.pan_x_der, self.pan_y_der = 0, 0
            self.actualizar_texto_zoom('der')
            self.dibujar_estado('der')

    def modificar_zoom(self, lado, factor_multiplicacion):
        if lado == 'izq' and self.img_izq_original:
            self.zoom_izq = max(0.01, min(self.zoom_izq * factor_multiplicacion, 50.0))
            self.actualizar_texto_zoom('izq')
            self.dibujar_estado('izq')
        elif lado == 'der' and self.img_der_original:
            self.zoom_der = max(0.01, min(self.zoom_der * factor_multiplicacion, 50.0))
            self.actualizar_texto_zoom('der')
            self.dibujar_estado('der')

    def zoom_rueda(self, event, lado):
        if event.num == 5 or event.delta < 0:
            self.modificar_zoom(lado, 1/1.1)
        if event.num == 4 or event.delta > 0:
            self.modificar_zoom(lado, 1.1)

    def obtener_parametros_geometria(self, img_original, canvas, zoom_abs, pan_x, pan_y):
        canvas.update()
        c_w, c_h = canvas.winfo_width(), canvas.winfo_height()
        i_w, i_h = img_original.size
        w_render, h_render = int(i_w * zoom_abs), int(i_h * zoom_abs)
        x0 = (c_w / 2) - (w_render / 2) + pan_x
        y0 = (c_h / 2) - (h_render / 2) + pan_y
        return zoom_abs, x0, y0, w_render, h_render

    def dibujar_estado(self, lado):
        canvas = self.canvas_left if lado == 'izq' else self.canvas_right
        img_orig = self.img_izq_original if lado == 'izq' else self.img_der_original
        zoom_abs = self.zoom_izq if lado == 'izq' else self.zoom_der
        pan_x = self.pan_x_izq if lado == 'izq' else self.pan_x_der
        pan_y = self.pan_y_izq if lado == 'izq' else self.pan_y_der
        puntos = self.puntos_izq if lado == 'izq' else self.puntos_der

        canvas.delete("all")
        if not img_orig: return

        ratio, x0, y0, w_render, h_render = self.obtener_parametros_geometria(img_orig, canvas, zoom_abs, pan_x, pan_y)

        if w_render > 0 and h_render > 0:
            img_resize = img_orig.resize((w_render, h_render), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img_resize)
            if lado == 'izq': self.img_izq_tk = img_tk
            else: self.img_der_tk = img_tk
            canvas.create_image(x0, y0, anchor="nw", image=img_tk)

        for pid, (orig_x, orig_y) in puntos.items():
            cx = orig_x * ratio + x0
            cy = orig_y * ratio + y0
            canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="#ef5350" if lado=='izq' else "#64b5f6", outline="white", tags="punto")
            canvas.create_text(cx+12, cy-12, text=str(pid), fill="white", font=("Arial", 12, "bold"), tags="punto")

    def refrescar_solo_puntos(self, lado):
        canvas = self.canvas_left if lado == 'izq' else self.canvas_right
        img_orig = self.img_izq_original if lado == 'izq' else self.img_der_original
        zoom_abs = self.zoom_izq if lado == 'izq' else self.zoom_der
        pan_x = self.pan_x_izq if lado == 'izq' else self.pan_x_der
        pan_y = self.pan_y_izq if lado == 'izq' else self.pan_y_der
        puntos = self.puntos_izq if lado == 'izq' else self.puntos_der

        canvas.delete("punto") 
        if not img_orig: return
        
        ratio, x0, y0, _, _ = self.obtener_parametros_geometria(img_orig, canvas, zoom_abs, pan_x, pan_y)
        
        for pid, (orig_x, orig_y) in puntos.items():
            cx = orig_x * ratio + x0
            cy = orig_y * ratio + y0
            canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="#ef5350" if lado=='izq' else "#64b5f6", outline="white", tags="punto")
            canvas.create_text(cx+12, cy-12, text=str(pid), fill="white", font=("Arial", 12, "bold"), tags="punto")

    def marcar_punto(self, event, lado):
        img_orig = self.img_izq_original if lado == 'izq' else self.img_der_original
        if not img_orig: return

        canvas = self.canvas_left if lado == 'izq' else self.canvas_right
        zoom_abs = self.zoom_izq if lado == 'izq' else self.zoom_der
        pan_x = self.pan_x_izq if lado == 'izq' else self.pan_x_der
        pan_y = self.pan_y_izq if lado == 'izq' else self.pan_y_der
        puntos = self.puntos_izq if lado == 'izq' else self.puntos_der

        ratio, x0, y0, _, _ = self.obtener_parametros_geometria(img_orig, canvas, zoom_abs, pan_x, pan_y)
        orig_x = (event.x - x0) / ratio
        orig_y = (event.y - y0) / ratio

        i_w, i_h = img_orig.size
        if 0 <= orig_x <= i_w and 0 <= orig_y <= i_h:
            nuevo_id = 1
            while nuevo_id in puntos: nuevo_id += 1
            puntos[nuevo_id] = (orig_x, orig_y)
            cx = orig_x * ratio + x0
            cy = orig_y * ratio + y0
            canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="#ef5350" if lado=='izq' else "#64b5f6", outline="white", tags="punto")
            canvas.create_text(cx+12, cy-12, text=str(nuevo_id), fill="white", font=("Arial", 12, "bold"), tags="punto")

    def eliminar_punto(self, event, lado):
        img_orig = self.img_izq_original if lado == 'izq' else self.img_der_original
        if not img_orig: return

        canvas = self.canvas_left if lado == 'izq' else self.canvas_right
        zoom_abs = self.zoom_izq if lado == 'izq' else self.zoom_der
        pan_x = self.pan_x_izq if lado == 'izq' else self.pan_x_der
        pan_y = self.pan_y_izq if lado == 'izq' else self.pan_y_der
        puntos = self.puntos_izq if lado == 'izq' else self.puntos_der

        ratio, x0, y0, _, _ = self.obtener_parametros_geometria(img_orig, canvas, zoom_abs, pan_x, pan_y)
        orig_x = (event.x - x0) / ratio
        orig_y = (event.y - y0) / ratio
        tolerancia_orig = 8 / ratio

        punto_a_borrar = None
        for pid, (px, py) in puntos.items():
            if abs(px - orig_x) <= tolerancia_orig and abs(py - orig_y) <= tolerancia_orig:
                punto_a_borrar = pid
                break

        if punto_a_borrar is not None:
            del puntos[punto_a_borrar]
            self.refrescar_solo_puntos(lado)

    def limpiar_puntos(self):
        self.puntos_izq.clear()
        self.puntos_der.clear()
        self.canvas_left.delete("punto")
        self.canvas_right.delete("punto")

    # ==========================================
    # LÓGICA DE OPEN-CV
    # ==========================================
    def ejecutar_union_manual(self):
        if not self.img_izq_original or not self.img_der_original:
            messagebox.showerror("Error", "Debes cargar ambas imágenes primero.")
            return

        ids_comunes = set(self.puntos_izq.keys()).intersection(set(self.puntos_der.keys()))
        
        if len(ids_comunes) < 4:
            messagebox.showwarning("Atención", "Se necesitan al menos 4 puntos coincidentes en ambas imágenes.")
            return

        ids_ordenados = sorted(list(ids_comunes))
        pts1 = np.float32([self.puntos_izq[pid] for pid in ids_ordenados])
        pts2 = np.float32([self.puntos_der[pid] for pid in ids_ordenados])

        img1_cv = cv2.cvtColor(np.array(self.img_izq_original), cv2.COLOR_RGB2BGR)
        img2_cv = cv2.cvtColor(np.array(self.img_der_original), cv2.COLOR_RGB2BGR)

        M, inliers = cv2.estimateAffinePartial2D(pts2, pts1, method=cv2.RANSAC)

        if M is None:
            messagebox.showerror("Error Matemático", "Los puntos están demasiado alineados o son contradictorios.")
            return

        H = np.vstack([M, [0.0, 0.0, 1.0]])
        self.procesar_fusion_y_mostrar(img1_cv, img2_cv, H)

    def ejecutar_union_automatica(self):
        if not self.img_izq_original or not self.img_der_original:
            messagebox.showerror("Error", "Debes cargar ambas imágenes primero.")
            return

        img1_cv = cv2.cvtColor(np.array(self.img_izq_original), cv2.COLOR_RGB2BGR)
        img2_cv = cv2.cvtColor(np.array(self.img_der_original), cv2.COLOR_RGB2BGR)
        
        try:
            MAX_DIM = float(self.entry_sift_max.get())
        except:
            MAX_DIM = 1500.0

        h_orig, w_orig = img1_cv.shape[:2]
        escala = min(1.0, MAX_DIM / max(h_orig, w_orig))

        if escala < 1.0:
            small1 = cv2.resize(img1_cv, (0,0), fx=escala, fy=escala, interpolation=cv2.INTER_AREA)
            small2 = cv2.resize(img2_cv, (0,0), fx=escala, fy=escala, interpolation=cv2.INTER_AREA)
        else:
            small1, small2 = img1_cv, img2_cv

        gray1 = cv2.cvtColor(small1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(small2, cv2.COLOR_BGR2GRAY)

        h_small, w_small = gray1.shape

        mask1 = np.zeros_like(gray1)
        mask1[:, int(w_small * 0.70):] = 255  
        
        mask2 = np.zeros_like(gray2)
        mask2[:, :int(w_small * 0.30)] = 255  

        sift = cv2.SIFT_create()
        kp1, des1 = sift.detectAndCompute(gray1, mask1)
        kp2, des2 = sift.detectAndCompute(gray2, mask2)

        if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
            messagebox.showwarning("Atención", "El algoritmo no encontró suficientes coincidencias. Usa la Unión Manual.")
            return

        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)

        good_matches = []
        for match in matches:
            if len(match) == 2:
                m, n = match
                if m.distance < 0.75 * n.distance:
                    good_matches.append(m)

        if len(good_matches) < 4:
            messagebox.showwarning("Atención", "Coincidencias insuficientes. Usa la Unión Manual.")
            return

        pts1 = np.float32([kp1[m.queryIdx].pt for m in good_matches])
        pts2 = np.float32([kp2[m.trainIdx].pt for m in good_matches])

        M_small, inliers = cv2.estimateAffinePartial2D(pts2, pts1, method=cv2.RANSAC)

        if M_small is None:
            messagebox.showerror("Error Matemático", "Las coincidencias fueron contradictorias. Usa la Unión Manual.")
            return

        M_large = M_small.copy()
        M_large[0, 2] /= escala
        M_large[1, 2] /= escala

        H_large = np.vstack([M_large, [0.0, 0.0, 1.0]])
        self.procesar_fusion_y_mostrar(img1_cv, img2_cv, H_large)

    def procesar_fusion_y_mostrar(self, img1_cv, img2_cv, H):
        h1, w1 = img1_cv.shape[:2]
        h2, w2 = img2_cv.shape[:2]
        
        corners1 = np.float32([[0,0], [0,h1], [w1,h1], [w1,0]]).reshape(-1,1,2)
        corners2 = np.float32([[0,0], [0,h2], [w2,h2], [w2,0]]).reshape(-1,1,2)
        warped_corners2 = cv2.perspectiveTransform(corners2, H)
        
        all_corners = np.concatenate((corners1, warped_corners2), axis=0)
        [x_min, y_min] = np.int32(all_corners.min(axis=0).ravel() - 0.5)
        [x_max, y_max] = np.int32(all_corners.max(axis=0).ravel() + 0.5)
        
        translation_dist = [-x_min, -y_min]
        H_translation = np.array([[1, 0, translation_dist[0]], 
                                  [0, 1, translation_dist[1]], 
                                  [0, 0, 1]], dtype=np.float32)
        
        output_w = x_max - x_min
        output_h = y_max - y_min

        result_img1 = cv2.warpPerspective(img1_cv, H_translation, (output_w, output_h))
        result_img2 = cv2.warpPerspective(img2_cv, H_translation.dot(H), (output_w, output_h))

        mask1_orig = np.ones((h1, w1), dtype=np.uint8) * 255
        mask2_orig = np.ones((h2, w2), dtype=np.uint8) * 255
        
        mask1 = cv2.warpPerspective(mask1_orig, H_translation, (output_w, output_h))
        mask2 = cv2.warpPerspective(mask2_orig, H_translation.dot(H), (output_w, output_h))

        dist1 = cv2.distanceTransform(mask1, cv2.DIST_L2, 3)
        dist2 = cv2.distanceTransform(mask2, cv2.DIST_L2, 3)

        alpha = np.zeros((output_h, output_w), dtype=np.float32)
        overlap = (mask1 > 0) & (mask2 > 0)

        alpha[overlap] = dist1[overlap] / (dist1[overlap] + dist2[overlap] + 1e-8)
        alpha[(mask1 > 0) & (mask2 == 0)] = 1.0

        alpha_3d = np.repeat(alpha[:, :, np.newaxis], 3, axis=2)
        blended = (result_img1 * alpha_3d + result_img2 * (1 - alpha_3d)).astype(np.uint8)
        blended_rgb = cv2.cvtColor(blended, cv2.COLOR_BGR2RGB)
        
        img_final_pil = Image.fromarray(blended_rgb)
        self.mostrar_resultado(img_final_pil)

    def mostrar_resultado(self, img_pil):
        ventana_resultado = ctk.CTkToplevel(self)
        ventana_resultado.title("Resultado de la Unión")
        ventana_resultado.geometry("900x700")
        
        btn_guardar = ctk.CTkButton(ventana_resultado, text="💾 Guardar Imagen Final", font=ctk.CTkFont(size=14, weight="bold"), fg_color="#388e3c", hover_color="#2e7d32", 
                                    command=lambda: self.guardar_imagen_final(img_pil))
        btn_guardar.pack(pady=15)

        canvas_res = ctk.CTkCanvas(ventana_resultado, bg="#1e1e1e", highlightthickness=0)
        canvas_res.pack(expand=True, fill="both", padx=20, pady=(0, 20))

        ventana_resultado.update()
        c_w, c_h = canvas_res.winfo_width(), canvas_res.winfo_height()
        i_w, i_h = img_pil.size
        ratio = min(c_w / i_w, c_h / i_h)
        
        nuevo_w, nuevo_h = int(i_w * ratio), int(i_h * ratio)
        if nuevo_w > 0 and nuevo_h > 0:
            img_resize = img_pil.resize((nuevo_w, nuevo_h), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img_resize)
            canvas_res.image = img_tk 
            canvas_res.create_image(c_w//2, c_h//2, anchor="center", image=img_tk)

    def guardar_imagen_final(self, img_pil):
        tipos_archivo = [
            ("Imágenes soportadas", "*.jpg *.jpeg *.png *.tiff *.tif"), 
            ("Todos los archivos", "*.*")
        ]
        
        ruta = filedialog.asksaveasfilename(title="Guardar resultado como...", filetypes=tipos_archivo)
        
        if ruta:
            import os
            _, ext = os.path.splitext(ruta)
            ext = ext.lower()
            
            if not ext:
                ruta += ".jpg"
                ext = ".jpg"
                
            if ext not in [".jpg", ".jpeg", ".png", ".tiff", ".tif"]:
                messagebox.showerror("Error", "Extensión no soportada. Por favor termina el nombre del archivo en .jpg, .png o .tiff")
                return

            if ext in [".jpg", ".jpeg"] and img_pil.mode in ("RGBA", "P"):
                img_pil = img_pil.convert("RGB")
                
            # ==========================================
            # RESCATE FORENSE DE METADATOS Y COMPRESIÓN
            # ==========================================
            orig_img = self.img_izq_original or self.img_der_original
            
            parametros_guardado = {
                'dpi': (300, 300) 
            }

            if orig_img:
                if 'dpi' in orig_img.info:
                    parametros_guardado['dpi'] = orig_img.info['dpi']
                if 'icc_profile' in orig_img.info:
                    parametros_guardado['icc_profile'] = orig_img.info['icc_profile']
                if 'exif' in orig_img.info:
                    parametros_guardado['exif'] = orig_img.info['exif']

                if ext in [".tiff", ".tif"] and 'compression' in orig_img.info:
                    parametros_guardado['compression'] = orig_img.info['compression']

            if ext in [".jpg", ".jpeg"]:
                if orig_img and hasattr(orig_img, 'quantization') and orig_img.quantization:
                    parametros_guardado['qtables'] = orig_img.quantization
                    
                    if 'subsampling' in orig_img.info:
                        parametros_guardado['subsampling'] = orig_img.info['subsampling']
                    else:
                        parametros_guardado['subsampling'] = 0
                else:
                    parametros_guardado['quality'] = 95
                    parametros_guardado['subsampling'] = 0
                
            try:
                img_pil.save(ruta, **parametros_guardado)
                    
                mensaje_exito = f"¡Imagen guardada correctamente como {ext.upper()}!\n"
                mensaje_exito += f"• Resolución: {int(parametros_guardado['dpi'][0])} DPI\n"
                if 'icc_profile' in parametros_guardado: mensaje_exito += "• Perfil de color ICC conservado\n"
                if 'qtables' in parametros_guardado: mensaje_exito += "• Tablas de compresión original (Calidad exacta) replicadas\n"
                
                messagebox.showinfo("Éxito", mensaje_exito)
                
            except Exception as e:
                messagebox.showerror("Error al guardar", f"Hubo un problema al guardar la imagen:\n{e}")

if __name__ == "__main__":
    app = CheIMG()
    app.mainloop()
