import sys
import tkinter
import tkinter.ttk
import customtkinter
import os
import ctypes
import smtplib
import threading
import re
import random
import string
import MySQLdb
import configparser
import ipaddress
from datetime import datetime
from CTkMessagebox import CTkMessagebox
from customtkinter import CTkInputDialog
from email.message import EmailMessage
from PIL import Image, ImageTk, ImageDraw
from PyQt5.QtCore import QUrl, Qt, QEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile

# Directorios de recursos e imágenes
main_dir = os.path.dirname(__file__)
resource_dir = os.path.join(main_dir, "assets")
img_dir = os.path.join(resource_dir, "img")
config_dir = os.path.join(resource_dir, "config")
config_path = os.path.join(config_dir, "data.ini")


def read_config(section):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config[section]


config = read_config("APP_CONFIG")

first_time = int(config["first_time"])

# Configuración inicial de apariencia y tema
customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("blue")


# define iconos
error_icon = os.path.join(img_dir, "error-ico.png")
info_icon = os.path.join(img_dir, "info-ico.png")
msg_icon = os.path.join(img_dir, "msg-ico.png")
off_icon = os.path.join(img_dir, "off-ico.png")
ok_icon = os.path.join(img_dir, "ok-ico.png")
ask_icon = os.path.join(img_dir, "ask-ico.png")

database = read_config("DB_CONFIG")

# Configuración de la base de datos
db_host = database["host"]
db_user = database["user"]
db_password = "#upapSala7"
db_name = database["database"]


# configuración de global_code, una cadena de caracteres aleatorios
global_code = "upappasswordsimple"

id = 0
nombre_completo = ""
correo = ""
carrera = ""
contrasena = ""

current_register = 0

MASTER_PASSWORD = "#upapSala7"

# Configuración de correo, SMTP y contrasena
SMTP_SERVER = "mail.tecnolem.com"  # Cambia esto por tu servidor SMTP
SMTP_PORT = 465  # Usa 465 si quieres conexión SSL
EMAIL_SENDER = "noreply@tecnolem.com"  # Tu correo personal
EMAIL_PASSWORD = "#upapSala7"  # La contraseña de tu correo


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("User Security")
        self.geometry("500x350")
        # No permitir redimensionar la ventana
        self.resizable(False, False)
        # Establecer el icono
        self.iconbitmap(os.path.join(img_dir, "ico.ico"))
        # Establecer el protocolo para cerrar la ventana
        # self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Establecer el icono en la barra de tareas (Windows)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            os.path.join(img_dir, "ico.ico")
        )

        # Configuración de pantalla completa y siempre visible
        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)

        # 📌 Contenedor principal (similar a un "div" en HTML)
        self.main_frame = customtkinter.CTkFrame(
            self, corner_radius=10, fg_color="transparent"
        )
        self.main_frame.place(
            relx=0.5, rely=0.5, anchor="center"
        )  # Centrado en la pantalla

        # boton de salida de emergencia en la parte inferior derecha
        self.exit_button = customtkinter.CTkButton(
            self,
            text="Emergencia",
            fg_color="red",
            font=("Arial", 14, "bold"),
            command=self.emergency_exit,
            width=100,
            height=40,
        )
        self.exit_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        # efecto hover para el boton de salida de emergencia
        self.exit_button.bind("<Enter>", self.on_enter_exit_button)
        self.exit_button.bind("<Leave>", self.on_leave_exit_button)

        # 🔹 Secciones dentro del contenedor principal
        self.left_frame = customtkinter.CTkFrame(
            self.main_frame, width=200, corner_radius=10, fg_color="transparent"
        )
        self.left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.right_frame = customtkinter.CTkFrame(
            self.main_frame, width=250, corner_radius=20
        )
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # 🔹 Cargar imagen de fondo en el lado izquierdo
        self.image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(img_dir, "back3.png")), size=(450, 450)
        )
        self.image_label = customtkinter.CTkLabel(
            self.left_frame, image=self.image, text=""
        )
        self.image_label.pack(expand=False, pady=(20, 20))

        # 🔹 Cargar imágenes de logos
        self.logo_img = self.make_circle(os.path.join(img_dir, "upap.jpg"), (100, 100))
        self.logo_label = customtkinter.CTkLabel(
            self, image=self.logo_img, text="", fg_color="transparent"
        )
        self.logo_label.place(y=70, x=70, anchor="center")

        self.iusa_img = self.load_rounded_image(
            os.path.join(img_dir, "iusa.png"), (80, 100), 5, 20
        )
        self.iusa_label = customtkinter.CTkLabel(
            self, image=self.iusa_img, text="", fg_color="#ffffff"
        )
        self.iusa_label.place(y=80, x=1300, anchor="center")

        # 🔹 Crear el formulario de inicio de sesión
        self.create_login_form()

    def create_login_form(self):
        """Crea el formulario de inicio de sesión en el panel derecho"""
        self.form_frame = customtkinter.CTkFrame(
            self.right_frame, fg_color="transparent"
        )
        self.form_frame.pack(expand=True)

        # 🔹 Título de bienvenida
        self.title_label = customtkinter.CTkLabel(
            self.form_frame,
            text="Bienvenido a Sala de Informática",
            font=("Arial", 30, "bold"),
        )
        self.title_label.pack(pady=30, padx=50)

        # 🔹 Entrada de correo
        self.email_entry_login = customtkinter.CTkEntry(
            self.form_frame,
            width=300,
            height=40,
            placeholder_text="Correo institucional",
            font=("Arial", 16),
        )
        self.email_entry_login.pack(pady=15)
        self.email_entry_login.bind(
            "<FocusIn>", lambda event: self.start_glow(self.email_entry_login)
        )
        self.email_entry_login.bind(
            "<FocusOut>", lambda event: self.start_fade(self.email_entry_login)
        )

        # 🔹 Entrada de contraseña
        self.password_entry_login = customtkinter.CTkEntry(
            self.form_frame,
            width=300,
            height=40,
            placeholder_text="Contraseña",
            show="·",
            font=("Arial", 16),
        )
        self.password_entry_login.pack(pady=15)
        self.password_entry_login.bind(
            "<FocusIn>", lambda event: self.start_glow(self.password_entry_login)
        )
        self.password_entry_login.bind(
            "<FocusOut>", lambda event: self.start_fade(self.password_entry_login)
        )

        # 🔹 Botón de "¿Olvidaste tu contraseña?"
        self.forget_password_button = customtkinter.CTkLabel(
            self.form_frame,
            width=300,
            text="¿Olvidaste tu contraseña?",
            font=("Arial", 12),
            cursor="hand2",
            text_color="gray",
        )
        self.forget_password_button.pack(pady=5, anchor="e", padx=10)

        # 🔹 Evento para cambiar color al pasar el mouse
        self.forget_password_button.bind(
            "<Enter>",
            lambda event: self.forget_password_button.configure(text_color="#1F6AA5"),
        )

        # 🔹 Evento para volver al color original al quitar el mouse
        self.forget_password_button.bind(
            "<Leave>",
            lambda event: self.forget_password_button.configure(text_color="gray"),
        )

        # 🔹 Accion al dar click
        self.forget_password_button.bind("<Button-1>", self.forget_password)

        # 🔹 Botón de inicio de sesión
        self.login_button = customtkinter.CTkButton(
            self.form_frame,
            height=40,
            text="Iniciar Sesión",
            font=("Arial", 16, "bold"),
            command=self.login,
        )
        self.login_button.pack(pady=15)

        # 🔹 Línea divisoria
        self.divider = customtkinter.CTkFrame(
            self.form_frame, height=1.5, fg_color="gray"
        )
        self.divider.pack(fill="x", padx=20, pady=5)

        # 🔹 Opción de registro
        self.register_label = customtkinter.CTkLabel(
            self.form_frame, text="¿No tienes una cuenta?", font=("Arial", 12)
        )
        self.register_label.pack(pady=(15, 0))

        self.register_button = customtkinter.CTkButton(
            self.form_frame,
            height=40,
            text="Registrarse",
            font=("Arial", 16, "bold"),
            command=self.registrarse,
        )
        self.register_button.pack(pady=(0, 20))

    def login(self):
        # print("Iniciando sesión...")
        email = self.email_entry_login.get()
        password = self.password_entry_login.get()

        # verificar si estan escritos los campos
        if email == "" or password == "":
            CTkMessagebox(
                title="Error",
                message="Por favor, completa todos los campos del formulario",
                icon=error_icon,
            )
            return

        try:
            connection = MySQLdb.connect(
                host=db_host,
                port=3306,
                user=db_user,
                password=db_password,
                database=db_name,
            )

            check_email = connection.cursor()
            query = "SELECT * FROM users WHERE email = %s"
            check_email.execute(query, (email,))
            user = check_email.fetchone()
            check_email.close()

            print(user)

            if user is None:
                CTkMessagebox(
                    title="Error",
                    message="El correo no existe en la base de datos, por favor registrese en el sistema",
                    icon=error_icon,
                )
                return

            # Verificar si el correo esta activo en otra computadora

            if user[5] == 1:
                CTkMessagebox(
                    title="Error",
                    message="El usuario ya ha iniciado sesión en otra computadora. Por favor cierre sesión en la otra computadora",
                    icon=error_icon,
                )
                return

            print("no ha iniciado sesion en otra computadora")

            cursor = connection.cursor()
            query = (
                "SELECT * FROM users WHERE email = %s AND password = %s AND status = 0"
            )
            cursor.execute(query, (email, password))
            user = cursor.fetchone()
            cursor.close()

            print("comfirmado usuario y contrasena")

            if user:
                update = connection.cursor()
                query = "UPDATE users SET status = 1 WHERE email = %s"
                update.execute(query, (email,))
                connection.commit()

                print("actualizado status")

                if update.rowcount > 0:

                    register = connection.cursor()
                    query = "INSERT INTO sessions (id_user, computer) VALUES (%s, %s)"
                    register.execute(query, (user[0], int(config["computer"])))
                    connection.commit()
                    register.close()

                    print("registrado sesion")

                    if register.rowcount > 0:
                        global current_register
                        global correo
                        global id
                        current_register = register.lastrowid
                        correo = user[2]
                        id = user[0]

                        print("sesion registrada")

                        # if self.web_view is not None:  # Verifica si la ventana existe
                        #     try:
                        #         self.web_view.destroy()  # Cierra la ventana
                        #         self.web_view = None  # Elimina la referencia
                        #     except Exception as e:
                        #         print(f"Error al cerrar la ventana: {e}")

                        # CTkMessagebox(
                        #     master=self,
                        #     title="Inicio de sesión exitoso",
                        #     message="Iniciaste sesión correctamente. Bienvenido de nuevo " + user[1],
                        #     icon= ok_icon,
                        # )

                        # resetear campos
                        self.email_entry_login.delete(0, "end")
                        self.password_entry_login.delete(0, "end")

                        print("mensaje de inicio de sesion")

                        self.destroy()

                        contador_app = counterUser()
                        contador_app.mainloop()

                else:
                    CTkMessagebox(
                        title="Error",
                        message="Error al iniciar sesión",
                        icon=error_icon,
                    )

                update.close()
                connection.close()

            else:
                CTkMessagebox(
                    title="Error",
                    message="El correo o la contraseña son incorrectos, por favor inténtalo de nuevo",
                    icon=error_icon,
                )
                connection.close()

        except MySQLdb.Error as error:
            # print("Error al conectar con la base de datos:", error)
            CTkMessagebox(
                title="Error",
                message="Error al conectar con la base de datos: " + str(error),
                icon=error_icon,
            )

    # 🔹 Resaltar borde del campo al enfocar
    def start_glow(self, widget):
        widget.configure(border_color="#1F6AA5")

    # 🔹 Quitar resaltado al perder foco
    def start_fade(self, widget):
        widget.configure(border_color="#565b5e")

    def cerrar(self):
        """Cierra la aplicación"""
        self.destroy()

    # 🔹 Función para abrir la ventana de registro
    def registrarse(self):
        self.main_frame.place_forget()

        self.register_frame = customtkinter.CTkFrame(
            self, corner_radius=10, fg_color="transparent"
        )

        self.register_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.left_reg_frame = customtkinter.CTkFrame(
            self.register_frame, width=250, corner_radius=20
        )
        self.left_reg_frame.pack(
            side="left", fill="both", expand=True, padx=10, pady=10
        )

        # 🔹 Secciones dentro del contenedor principal
        self.right_reg_frame = customtkinter.CTkFrame(
            self.register_frame, width=200, corner_radius=10, fg_color="transparent"
        )
        self.right_reg_frame.pack(
            side="right", fill="both", expand=True, padx=10, pady=10
        )

        # 🔹 Cargar imagen de fondo en el lado derecho
        self.image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(img_dir, "back2.png")), size=(450, 450)
        )
        self.image_label = customtkinter.CTkLabel(
            self.right_reg_frame, image=self.image, text=""
        )
        self.image_label.pack(expand=False, pady=(150, 20))

        self.form_reg_frame = customtkinter.CTkFrame(
            self.left_reg_frame, fg_color="transparent"
        )
        self.form_reg_frame.pack(expand=True)

        # 🔹 Título de bienvenida
        self.title_label = customtkinter.CTkLabel(
            self.form_reg_frame,
            text="Registrate en Sala de Informática",
            font=("Arial", 30, "bold"),
        )
        self.title_label.pack(pady=30, padx=50)

        # 🔹 Entrada de nombre
        self.name_entry = customtkinter.CTkEntry(
            self.form_reg_frame,
            width=300,
            height=40,
            placeholder_text="Nombre completo",
            font=("Arial", 16),
        )
        self.name_entry.pack(pady=15)

        self.name_entry.bind("<KeyRelease>", self.force_uppercase)

        self.name_entry.bind(
            "<FocusIn>", lambda event: self.start_glow(self.name_entry)
        )
        self.name_entry.bind(
            "<FocusOut>", lambda event: self.start_fade(self.name_entry)
        )

        # 🔹 Entrada de correo
        self.email_entry_login = customtkinter.CTkEntry(
            self.form_reg_frame,
            width=300,
            height=40,
            placeholder_text="Correo institucional",
            font=("Arial", 16),
        )
        self.email_entry_login.pack(pady=15)
        self.email_entry_login.bind(
            "<FocusIn>", lambda event: self.start_glow(self.email_entry_login)
        )
        self.email_entry_login.bind(
            "<FocusOut>", lambda event: self.start_fade(self.email_entry_login)
        )

        # obtener opciones de base de datos
        connection = MySQLdb.connect(
            host=db_host,
            port=3306,
            user=db_user,
            password=db_password,
            database=db_name,
        )
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM careers")
        careers = cursor.fetchall()
        cursor.close()

        self.careers = []
        for career in careers:
            self.careers.append(career[1])

        # 🔹 Entrada de carrera
        self.carrera_select = customtkinter.CTkOptionMenu(
            self.form_reg_frame,
            width=300,
            height=40,
            values=self.careers,
            font=("Arial", 16),
        )
        self.carrera_select.pack(pady=15)
        self.carrera_select.bind(
            "<FocusIn>", lambda event: self.start_glow(self.carrera_select)
        )
        self.carrera_select.bind(
            "<FocusOut>", lambda event: self.start_fade(self.carrera_select)
        )

        # 🔹 Entrada de contraseña
        self.password_entry_login = customtkinter.CTkEntry(
            self.form_reg_frame,
            width=300,
            height=40,
            placeholder_text="Contraseña",
            show="·",
            font=("Arial", 16),
        )
        self.password_entry_login.pack(pady=15)
        self.password_entry_login.bind(
            "<FocusIn>", lambda event: self.start_glow(self.password_entry_login)
        )
        self.password_entry_login.bind(
            "<FocusOut>", lambda event: self.start_fade(self.password_entry_login)
        )

        # 🔹 Entrada repite la cotraseña
        self.repeat_password_entry = customtkinter.CTkEntry(
            self.form_reg_frame,
            width=300,
            height=40,
            placeholder_text="Repite la contraseña",
            show="·",
            font=("Arial", 16),
        )
        self.repeat_password_entry.pack(pady=15)
        self.repeat_password_entry.bind(
            "<FocusIn>", lambda event: self.start_glow(self.repeat_password_entry)
        )
        self.repeat_password_entry.bind(
            "<FocusOut>", lambda event: self.start_fade(self.repeat_password_entry)
        )

        # 🔹 Botón de inicio de sesión
        self.login_button = customtkinter.CTkButton(
            self.form_reg_frame,
            height=40,
            text="Registrarse",
            font=("Arial", 16, "bold"),
            command=self.register_user,
        )
        self.login_button.pack(pady=15)

        # 🔹 Línea divisoria
        self.divider = customtkinter.CTkFrame(
            self.form_reg_frame, height=1.5, fg_color="gray"
        )
        self.divider.pack(fill="x", padx=20, pady=5)

        # 🔹 Opción de registro
        self.register_label = customtkinter.CTkLabel(
            self.form_reg_frame,
            text="¿Deseas regresar al menu principal?",
            font=("Arial", 12),
        )
        self.register_label.pack(pady=(15, 0))

        self.register_button = customtkinter.CTkButton(
            self.form_reg_frame,
            height=40,
            text="Volver",
            font=("Arial", 16, "bold"),
            command=self.volver_register,
        )
        self.register_button.pack(pady=(0, 20))

    # 🔹 Función de registro
    def register_user(self):

        global nombre_completo
        global correo
        global carrera
        global contrasena

        nombre_completo = self.name_entry.get()
        correo = self.email_entry_login.get()

        # carrera
        connection = MySQLdb.connect(
            host=db_host,
            port=3306,
            user=db_user,
            password=db_password,
            database=db_name,
        )
        cursor = connection.cursor()
        query = "SELECT id FROM careers WHERE name = %s"
        cursor.execute(query, (self.carrera_select.get(),))
        carrera = cursor.fetchone()[0]
        cursor.close()
        connection.close()

        contrasena = self.password_entry_login.get()
        contrasena_repetida = self.repeat_password_entry.get()

        # Validaciones de campos
        if contrasena != contrasena_repetida:

            CTkMessagebox(
                title="Error",
                message="Las contrasenas no coinciden, por favor, introduce las contrasenas correctas.",
                icon=error_icon,
            )
            return

        # Validaciones de campos
        if (
            nombre_completo == ""
            or correo == ""
            or carrera == ""
            or contrasena == ""
            or contrasena_repetida == ""
        ):

            CTkMessagebox(
                title="Error",
                message="Por favor, llena todos los campos. No deben estar vacios.",
                icon=error_icon,
            )
            return

        # Validaciones de campos
        if self.is_valid_email(correo) == False:

            CTkMessagebox(
                title="Error",
                message="El correo introducido es incorrecto, por favor, introduce un correo valido.",
                icon=error_icon,
            )

            return

        # Validaciones de campos, longitud de contrasena
        if len(contrasena) < 8:

            CTkMessagebox(
                title="Error",
                message="La contrasena debe tener al menos 8 caracteres. Por favor, introduce una contrasena correcta.",
                icon=error_icon,
            )

            return

        try:
            # Conectar a la base de datos
            db_connection = MySQLdb.connect(
                host=db_host,
                port=3306,
                user=db_user,
                passwd=db_password,
                database=db_name,
                # connect_timeout=10,
            )

            # Verificar la conexión
            print("Conexión exitosa a la base de datos")

            # Crear el cursor
            db_cursor = db_connection.cursor()

            # Ejecutar la consulta SQL
            db_cursor.execute("SELECT * FROM users WHERE email = %s", (correo,))

            # Obtener el resultado de la consulta
            result = db_cursor.fetchone()

            # Cerrar el cursor
            db_cursor.close()

            # Cerrar la conexión a la base de datos
            db_connection.close()

            # Verificar si el correo ya existe en la base de datos
            if result is not None:

                CTkMessagebox(
                    title="Error",
                    message="El correo introducido ya esta registrado, por favor, introduce un correo diferente.",
                    icon=error_icon,
                )

                return

        except MySQLdb.Error as e:
            print(f"Error al conectar a la base de datos: {e}")

            CTkMessagebox(
                title="Error",
                message="Error al conectar a la base de datos: "
                + str(e)
                + ". Por favor, intenta de nuevo.",
                icon=error_icon,
            )

            return

        # mandar correo con el codigo de recuperacion
        try:
            global global_code
            global_code = self.generate_code()
            html_content = f"""\
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Registro de nuevo usuario - User Security UPAP</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background-color: #f4f4f4;
                            margin: 0;
                            padding: 0;
                        }}
                        .container {{
                            width: 100%;
                            max-width: 600px;
                            margin: 20px auto;
                            background-color: #ffffff;
                            border-radius: 8px;
                            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
                            overflow: hidden;
                        }}
                        .header {{
                            background-color: #003366;
                            padding: 15px;
                            display: flex;
                            align-items: center;
                            justify-content: space-between;
                            color: white;
                            font-size: 18px;
                            font-weight: bold;
                        }}
                        .header img {{
                            max-width: 8%;
                            max-height: 50px;
                        }}
                        .content {{
                            padding: 20px;
                            text-align: center;
                        }}
                        .code {{
                            font-size: 24px;
                            font-weight: bold;
                            color: #003366;
                            background-color: #f0f8ff;
                            padding: 10px;
                            border-radius: 5px;
                            display: inline-block;
                            margin: 15px 0;
                            letter-spacing: 2px;
                        }}
                        .footer {{
                            background-color: #003366;
                            color: white;
                            text-align: center;
                            padding: 10px;
                            font-size: 14px;
                        }}
                    </style>
                </head>
                <body>

                    <div class="container">
                        <div class="header">
                            <img src="https://upap.mx/wp-content/uploads/2023/06/upap.logo_-2.jpg" alt="UPAP Logo">
                            <span>User Security UPAP</span>
                            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Logo_Grupo_IUSA.svg/500px-Logo_Grupo_IUSA.svg.png" alt="IUSA Logo">
                        </div>

                        <div class="content">
                            <h2>Registro de nuevo usuario</h2>
                            <p>Hola {nombre_completo}, bienvenido a <strong>User Security UPAP</strong>. Hemos recibido una solicitud de registro para tu cuenta. Por favor, copia y pega el siguiente código en la sección de verificación de tu cuenta:</p>
                            <div class="code">{global_code}</div>
                            <p>Gracias por utilizar <strong>User Security UPAP</strong>. Si no solicitaste un registro, puedes ignorar este mensaje.</p>
                        </div>

                        <div class="footer">
                            Pastejé, 50734 Cdad. de Jocotitlán, Méx.
                        </div>
                    </div>

                </body>
                </html>"""

            threading.Thread(
                target=self.send_email,
                args=(
                    correo,
                    "Verificación de cuenta - User Security UPAP",
                    html_content,
                ),
                daemon=True,
            ).start()

            CTkMessagebox(
                title="Correo enviado",
                message="El correo de verificación ha sido enviado. Por favor, ingresa a tu correo institucional y revisa tu bandeja de entrada o spam.",
                icon=ok_icon,
            )

            self.validation_email_page()

            self.web_view = RecoveryWindow()  # Sin pasar "self"
            self.web_view.show()

        except Exception as e:
            print(f"Error al enviar el correo: {e}")

            CTkMessagebox(
                title="Error",
                message="Error al enviar el correo: "
                + str(e)
                + ". Por favor, intenta nuevamente.",
                icon=error_icon,
            )

    # 🔹 Función para la pantalla de validación de correo
    def validation_email_page(self):
        self.register_frame.place_forget()

        global global_code

        # print(f"\n\nCodigo: " + global_code + "\n\n")

        # self.recovery_frame.place_forget()

        # 🔹 Crea un nuevo frame para la recuperación de contraseña
        self.validation_frame = customtkinter.CTkFrame(self, corner_radius=10)
        self.validation_frame.place(relx=0.5, rely=0.5, anchor="center")

        # 🔹 Secciones dentro del contenedor principal
        self.left_val_frame = customtkinter.CTkFrame(
            self.validation_frame, width=200, corner_radius=10, fg_color="transparent"
        )
        self.left_val_frame.pack(
            side="left", fill="both", expand=True, padx=10, pady=10
        )

        self.right_val_frame = customtkinter.CTkFrame(
            self.validation_frame, width=250, corner_radius=20
        )
        self.right_val_frame.pack(
            side="right", fill="both", expand=True, padx=10, pady=10
        )

        # 🔹 Cargar imagen de fondo en el lado izquierdo
        self.image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(img_dir, "back2.png")), size=(350, 350)
        )
        self.image_label = customtkinter.CTkLabel(
            self.left_val_frame, image=self.image, text=""
        )
        self.image_label.pack(expand=False, pady=(20, 20))

        # 🔹 Título de recuperación de contraseña
        self.code_title = customtkinter.CTkLabel(
            self.right_val_frame,
            text="Comprobar Código - Validación",
            font=("Arial", 30, "bold"),
        )
        self.code_title.pack(pady=30, padx=50)

        # 🔹 Entrada de correo
        self.code_entry_validation = customtkinter.CTkEntry(
            self.right_val_frame,
            width=300,
            height=40,
            placeholder_text="Codigo de validación",
            font=("Arial", 16),
        )
        self.code_entry_validation.pack(pady=15)
        self.code_entry_validation.bind(
            "<FocusIn>", lambda event: self.start_glow(self.code_entry_validation)
        )
        self.code_entry_validation.bind(
            "<FocusOut>", lambda event: self.start_fade(self.code_entry_validation)
        )

        # 🔹 Botón de enviar
        self.send_button = customtkinter.CTkButton(
            self.right_val_frame,
            height=40,
            text="Registrar",
            font=("Arial", 16, "bold"),
            command=self.val_code_register,
        )
        self.send_button.pack(pady=15)

        # 🔹 Línea divisoria
        self.divider = customtkinter.CTkFrame(
            self.right_val_frame, height=1.5, fg_color="gray"
        )
        self.divider.pack(fill="x", padx=20, pady=(20, 10))

        # 🔹 Opción de registro
        self.register_label = customtkinter.CTkLabel(
            self.right_val_frame,
            text="¿Deseas regresar al registro?",
            font=("Arial", 12),
        )
        self.register_label.pack(pady=(15, 0))

        # 🔹 Opción de inicio de sesió)
        self.back_button = customtkinter.CTkButton(
            self.right_val_frame,
            height=40,
            text="Volver",
            font=("Arial", 16, "bold"),
            command=self.volver_validation,
        )
        self.back_button.pack(pady=(0, 20))

    # 🔹 Función para comprobar el codigo
    def val_code_register(self):

        print("Aqui estoy")

        global global_code
        global nombre_completo
        global correo
        global carrera
        global contrasena

        if self.code_entry_validation.get() == global_code:

            print("Aqui estoy 2")

            # Conectar a la base de datos
            try:
                # Conectar a la base de datos
                db_connection = MySQLdb.connect(
                    host=db_host,
                    port=3306,
                    user=db_user,
                    passwd=db_password,
                    database=db_name,
                    # connect_timeout=10,
                )

                # Verificar la conexión
                print("Conexión exitosa a la base de datos")

                # Crear el cursor
                cursor = db_connection.cursor()

                # Ejecutar la consulta
                cursor.execute(
                    "INSERT INTO users(name, email, career, password) VALUES (%s, %s, %s, %s)",
                    (nombre_completo, correo, carrera, contrasena),
                )

                # Confirmar la transacción
                db_connection.commit()

                # Mostrar mensaje de registro exitoso
                CTkMessagebox(
                    title="Registrado",
                    message="El usuario ha sido registrado correctamente, puedes iniciar sesion ahora.",
                    icon=ok_icon,
                )

                # resetear variables globales
                global_code = None
                nombre_completo = None
                correo = None
                carrera = None
                contrasena = None

                # Cerrar el cursor
                cursor.close()

            except MySQLdb.Error as err:
                print(f"Error al conectar a la base de datos: {err}")
                CTkMessagebox(
                    title="Error",
                    message="Error al conectar a la base de datos: " + str(err),
                    icon=error_icon,
                )
                # Mostrar mensaje de error
                return

            finally:
                # cerrar la conexión
                db_connection.close()

            CTkMessagebox(
                title="Registrado",
                message="El usuario ha sido registrado correctamente, puedes iniciar sesion ahora.",
                icon=ok_icon,
            )

            self.validation_frame.place_forget()
            self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        else:
            CTkMessagebox(
                title="Error",
                message="El codigo de validación es incorrecto. Por favor, intenta nuevamente.",
                icon=error_icon,
            )

    # 📌 Botón de volver
    def volver_validation(self):
        self.validation_frame.place_forget()
        self.register_frame.place(relx=0.5, rely=0.5, anchor="center")

    # 📌 Recuperación de contraseña
    def forget_password(self, event):
        self.main_frame.place_forget()

        # 🔹 Crea un nuevo frame para la recuperación de contraseña
        self.recovery_frame = customtkinter.CTkFrame(self, corner_radius=10)
        self.recovery_frame.place(relx=0.5, rely=0.5, anchor="center")

        # 🔹 Secciones dentro del contenedor principal
        self.left_frame = customtkinter.CTkFrame(
            self.recovery_frame, width=200, corner_radius=10, fg_color="transparent"
        )
        self.left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.right_frame = customtkinter.CTkFrame(
            self.recovery_frame, width=250, corner_radius=20
        )
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # 🔹 Cargar imagen de fondo en el lado izquierdo
        self.image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(img_dir, "back4.png")), size=(350, 350)
        )
        self.image_label = customtkinter.CTkLabel(
            self.left_frame, image=self.image, text=""
        )
        self.image_label.pack(expand=False, pady=(20, 20))

        # 🔹 Título de recuperación de contraseña
        self.recovery_title = customtkinter.CTkLabel(
            self.right_frame,
            text="Recuperación de contraseña",
            font=("Arial", 30, "bold"),
        )
        self.recovery_title.pack(pady=30, padx=50)

        # 🔹 Entrada de correo
        self.email_entry_login = customtkinter.CTkEntry(
            self.right_frame,
            width=300,
            height=40,
            placeholder_text="Correo institucional",
            font=("Arial", 16),
        )
        self.email_entry_login.pack(pady=15)
        self.email_entry_login.bind(
            "<FocusIn>", lambda event: self.start_glow(self.email_entry_login)
        )
        self.email_entry_login.bind(
            "<FocusOut>", lambda event: self.start_fade(self.email_entry_login)
        )

        # 🔹 Botón de enviar
        self.send_button = customtkinter.CTkButton(
            self.right_frame,
            height=40,
            text="Enviar",
            font=("Arial", 16, "bold"),
            command=self.open_recovery_page,
        )
        self.send_button.pack(pady=15)

        # 🔹 Línea divisoria
        self.divider = customtkinter.CTkFrame(
            self.right_frame, height=1.5, fg_color="gray"
        )
        self.divider.pack(fill="x", padx=20, pady=(20, 10))

        # 🔹 Opción de registro
        self.register_label = customtkinter.CTkLabel(
            self.right_frame,
            text="¿Deseas regresar al inicio de sesión?",
            font=("Arial", 12),
        )
        self.register_label.pack(pady=(15, 0))

        # 🔹 Opción de inicio de sesió)
        self.back_button = customtkinter.CTkButton(
            self.right_frame,
            height=40,
            text="Volver",
            font=("Arial", 16, "bold"),
            command=self.volver_forget,
        )
        self.back_button.pack(pady=(0, 20))

    # 📌 Abre la ventana de recuperación
    def open_recovery_page(self):
        global correo
        correo = self.email_entry_login.get()
        if self.is_valid_email(correo):

            try:
                connection = MySQLdb.connect(
                    host=db_host,
                    port=3306,
                    user=db_user,
                    password=db_password,
                    database=db_name,
                )
                cursor = connection.cursor()
                query = "SELECT * FROM users WHERE email = %s"
                cursor.execute(query, (correo,))
                user = cursor.fetchone()
                cursor.close()
                connection.close()

                # si no existe el usuario
                if user is None:
                    CTkMessagebox(
                        title="Error",
                        message="El correo no esta registrado en la base de datos",
                        icon=error_icon,
                    )
                    return

            except MySQLdb.Error as err:
                print(f"Error al conectar a la base de datos: {err}")

            global global_code
            global_code = self.generate_code()
            html_content = f"""\
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Recuperación de Contraseña - User Security UPAP</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background-color: #f4f4f4;
                            margin: 0;
                            padding: 0;
                        }}
                        .container {{
                            width: 100%;
                            max-width: 600px;
                            margin: 20px auto;
                            background-color: #ffffff;
                            border-radius: 8px;
                            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
                            overflow: hidden;
                        }}
                        .header {{
                            background-color: #003366;
                            padding: 15px;
                            display: flex;
                            align-items: center;
                            justify-content: space-between;
                            color: white;
                            font-size: 18px;
                            font-weight: bold;
                        }}
                        .header img {{
                            max-width: 8%;
                            max-height: 50px;
                        }}
                        .content {{
                            padding: 20px;
                            text-align: center;
                        }}
                        .code {{
                            font-size: 24px;
                            font-weight: bold;
                            color: #003366;
                            background-color: #f0f8ff;
                            padding: 10px;
                            border-radius: 5px;
                            display: inline-block;
                            margin: 15px 0;
                            letter-spacing: 2px;
                        }}
                        .footer {{
                            background-color: #003366;
                            color: white;
                            text-align: center;
                            padding: 10px;
                            font-size: 14px;
                        }}
                    </style>
                </head>
                <body>

                    <div class="container">
                        <div class="header">
                            <img src="https://upap.mx/wp-content/uploads/2023/06/upap.logo_-2.jpg" alt="UPAP Logo">
                            <span>User Security UPAP</span>
                            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Logo_Grupo_IUSA.svg/500px-Logo_Grupo_IUSA.svg.png" alt="IUSA Logo">
                        </div>

                        <div class="content">
                            <h2>Recuperación de Contraseña</h2>
                            <p>Hola, has solicitado un cambio de contraseña. Por favor, copia y pega el siguiente código en la sección de recuperación de contraseña:</p>
                            <div class="code">{global_code}</div>
                            <p>Gracias por utilizar <strong>User Security UPAP</strong>. Si no solicitaste este cambio, puedes ignorar este mensaje.</p>
                        </div>

                        <div class="footer">
                            Pastejé, 50734 Cdad. de Jocotitlán, Méx.
                        </div>
                    </div>

                </body>
                </html>"""

            threading.Thread(
                target=self.send_email,
                args=(
                    correo,
                    "Recuperación de contraseña",
                    html_content,
                ),
                daemon=True,
            ).start()

            CTkMessagebox(
                title="Recuperación de contraseña",
                message="El correo de recuperación de contraseña ha sido enviado. Por favor, ingresa a tu correo institucional y revisa tu bandeja de entrada o spam.",
                icon=ok_icon,
                # option_2="Cancelar",
            )

            self.open_check_code()

            self.web_view = RecoveryWindow()  # Sin pasar "self"
            self.web_view.show()

        else:

            CTkMessagebox(
                title="Error",
                message="Correo inválido. Por favor, introduce un correo institucional. Ejemplo: tu.nombre@upap.mx",
                icon=error_icon,
            )

    # 📌 Abre la ventana de comprobación de código
    def open_check_code(self):
        global global_code

        print(f"\n\nCodigo: " + global_code + "\n\n")

        self.recovery_frame.place_forget()

        # 🔹 Crea un nuevo frame para la recuperación de contraseña
        self.check_code_frame = customtkinter.CTkFrame(self, corner_radius=10)
        self.check_code_frame.place(relx=0.5, rely=0.5, anchor="center")

        # 🔹 Secciones dentro del contenedor principal
        self.left_code_frame = customtkinter.CTkFrame(
            self.check_code_frame, width=200, corner_radius=10, fg_color="transparent"
        )
        self.left_code_frame.pack(
            side="left", fill="both", expand=True, padx=10, pady=10
        )

        self.right_code_frame = customtkinter.CTkFrame(
            self.check_code_frame, width=250, corner_radius=20
        )
        self.right_code_frame.pack(
            side="right", fill="both", expand=True, padx=10, pady=10
        )

        # 🔹 Cargar imagen de fondo en el lado izquierdo
        self.image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(img_dir, "back4.png")), size=(350, 350)
        )
        self.image_label = customtkinter.CTkLabel(
            self.left_code_frame, image=self.image, text=""
        )
        self.image_label.pack(expand=False, pady=(20, 20))

        # 🔹 Título de recuperación de contraseña
        self.code_title = customtkinter.CTkLabel(
            self.right_code_frame,
            text="Comprobar Código",
            font=("Arial", 30, "bold"),
        )
        self.code_title.pack(pady=30, padx=50)

        # 🔹 Entrada de correo
        self.code_entry = customtkinter.CTkEntry(
            self.right_code_frame,
            width=300,
            height=40,
            placeholder_text="Codigo de recuperación",
            font=("Arial", 16),
        )
        self.code_entry.pack(pady=15)
        self.code_entry.bind(
            "<FocusIn>", lambda event: self.start_glow(self.code_entry)
        )
        self.code_entry.bind(
            "<FocusOut>", lambda event: self.start_fade(self.code_entry)
        )

        # 🔹 Botón de enviar
        self.send_button = customtkinter.CTkButton(
            self.right_code_frame,
            height=40,
            text="Comprobar",
            font=("Arial", 16, "bold"),
            command=self.check_code,
        )
        self.send_button.pack(pady=15)

        # 🔹 Línea divisoria
        self.divider = customtkinter.CTkFrame(
            self.right_code_frame, height=1.5, fg_color="gray"
        )
        self.divider.pack(fill="x", padx=20, pady=(20, 10))

        # 🔹 Opción de registro
        self.register_label = customtkinter.CTkLabel(
            self.right_code_frame,
            text="¿Deseas regresar al inicio de sesión?",
            font=("Arial", 12),
        )
        self.register_label.pack(pady=(15, 0))

        # 🔹 Opción de inicio de sesió)
        self.back_button = customtkinter.CTkButton(
            self.right_code_frame,
            height=40,
            text="Volver",
            font=("Arial", 16, "bold"),
            command=self.volver_check_code,
        )
        self.back_button.pack(pady=(0, 20))

    # 📌 Comprobación de código
    def check_code(self):
        user_code = self.code_entry.get()
        if user_code == global_code:
            self.change_pass_frame()
        else:

            CTkMessagebox(
                title="Error",
                message="El código de recuperación es incorrecto. Por favor, introduce el código correcto.",
                icon=error_icon,
            )

    # 📌 Abre la ventana de cambio de contraseña
    def change_pass_frame(self):
        self.check_code_frame.place_forget()
        self.change_password_frame = customtkinter.CTkFrame(self, corner_radius=10)
        self.change_password_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.change_password_title = customtkinter.CTkLabel(
            self.change_password_frame,
            text="Cambio de contraseña",
            font=("Arial", 30, "bold"),
        )
        self.change_password_title.pack(pady=30, padx=50)

        self.change_password_entry = customtkinter.CTkEntry(
            self.change_password_frame,
            width=300,
            height=40,
            placeholder_text="Nueva contraseña",
            font=("Arial", 16),
            show="·",
        )
        self.change_password_entry.pack(pady=15)
        self.change_password_entry.bind(
            "<FocusIn>", lambda event: self.start_glow(self.change_password_entry)
        )
        self.change_password_entry.bind(
            "<FocusOut>", lambda event: self.start_fade(self.change_password_entry)
        )

        self.change_password_confirm_entry = customtkinter.CTkEntry(
            self.change_password_frame,
            width=300,
            height=40,
            placeholder_text="Confirmar nueva contraseña",
            font=("Arial", 16),
            show="·",
        )
        self.change_password_confirm_entry.pack(pady=15)
        self.change_password_confirm_entry.bind(
            "<FocusIn>",
            lambda event: self.start_glow(self.change_password_confirm_entry),
        )
        self.change_password_confirm_entry.bind(
            "<FocusOut>",
            lambda event: self.start_fade(self.change_password_confirm_entry),
        )

        self.change_password_button = customtkinter.CTkButton(
            self.change_password_frame,
            height=40,
            text="Cambiar",
            font=("Arial", 16, "bold"),
            command=self.change_password,
        )
        self.change_password_button.pack(pady=15)

        self.divider = customtkinter.CTkFrame(
            self.change_password_frame, height=1.5, fg_color="gray"
        )
        self.divider.pack(fill="x", padx=20, pady=(20, 10))

        self.register_label = customtkinter.CTkLabel(
            self.change_password_frame,
            text="¿Deseas regresar al inicio de sesión?",
            font=("Arial", 12),
        )
        self.register_label.pack(pady=(15, 0))

        self.back_button = customtkinter.CTkButton(
            self.change_password_frame,
            height=40,
            text="Volver",
            font=("Arial", 16, "bold"),
            command=self.volver_change_password,
        )
        self.back_button.pack(pady=(0, 20))

    def volver_forget(self):
        self.recovery_frame.place_forget()
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

    def volver_register(self):
        self.register_frame.place_forget()
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

    def volver_check_code(self):
        self.check_code_frame.place_forget()
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

    def volver_change_password(self):
        self.change_password_frame.place_forget()
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

    def change_password(self):
        new_password = self.change_password_entry.get()
        confirm_password = self.change_password_confirm_entry.get()
        if new_password != confirm_password:

            CTkMessagebox(
                title="Error",
                message="Las contrasenas no coinciden. Por favor, introduce las contrasenas correctas.",
                icon=error_icon,
            )

            return
        print(new_password)

        try:
            conecction = MySQLdb.connect(
                host=db_host,
                port=3306,
                user=db_user,
                passwd=db_password,
                db=db_name,
                # connect_timeout=10,
            )

            try:
                global correo
                cursor = conecction.cursor()
                cursor.execute(
                    "UPDATE users SET password = %s WHERE email = %s",
                    (new_password, correo),
                )
                conecction.commit()
                cursor.close()

                if cursor.rowcount == 1:
                    CTkMessagebox(
                        title="Información",
                        message="La contraseña ha sido cambiada con exito",
                        icon=ok_icon,
                    )

                    # resetear variables globales
                    global global_code
                    global nombre_completo
                    # global correo
                    global carrera
                    global contrasena

                    global_code = ""
                    nombre_completo = ""
                    # correo = ""
                    carrera = ""
                    contrasena = ""

                    self.check_code_frame.place_forget()
                    self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

            except Exception as e:
                print(e)
                CTkMessagebox(
                    title="Error",
                    message="Ha ocurrido un error al cambiar la contraseña: " + str(e),
                    icon=error_icon,
                )
                return
        except Exception as e:
            print(e)
            CTkMessagebox(
                title="Error",
                message="Ha ocurrido un error al cambiar la contraseña: " + str(e),
                icon=error_icon,
            )
            return

        self.volver_change_password()

    # 📌 Función para hacer una imagen circular
    def make_circle(self, image_path, size):
        img = Image.open(image_path).convert("RGBA")
        img = img.resize(size, Image.LANCZOS)

        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)

        circular_img = Image.new("RGBA", size, (0, 0, 0, 0))
        circular_img.paste(img, (0, 0), mask)

        return ImageTk.PhotoImage(circular_img)

    def load_rounded_image(self, image_path, size, margin, corner_radius):
        """Carga una imagen y la redondea con esquinas suaves"""
        try:
            img = Image.open(image_path).convert("RGBA")
            img = img.resize(size, Image.LANCZOS)

            new_size = (size[0] + margin * 2, size[1] + margin * 2)
            new_img = Image.new("RGB", new_size, "white")
            new_img.paste(img, (margin, margin), img)

            mask = Image.new("L", new_size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle(
                (0, 0, new_size[0], new_size[1]), corner_radius, fill=255
            )

            rounded_img = Image.new("RGBA", new_size)
            rounded_img.paste(new_img, (0, 0), mask)

            return ImageTk.PhotoImage(rounded_img)
        except Exception as e:
            print(f"Error al cargar la imagen: {e}")
            return None

    def on_closing(self):
        pass

    def send_email(self, to_email, subject, html_body):
        msg = EmailMessage()
        msg["From"] = EMAIL_SENDER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(
            "Este correo contiene contenido HTML. Si no puedes verlo, habilita la visualización de HTML."
        )
        msg.add_alternative(html_body, subtype="html")  # Agregar contenido HTML

        try:
            print(f" **** Enviando correo a: {to_email}")
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                print(f" **** Conectando al servidor SMTP")
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)  # Iniciar sesión
                server.send_message(msg)  # Enviar mensaje
            print(f" **** Correo enviado exitosamente")
        except Exception as e:
            print(f" **** Error al enviar correo: {e}")

    def is_valid_email(self, email):
        """Verifica si el email tiene un formato válido."""
        email_regex = r"^[a-zA-Z0-9_.+-]+@upap+\.[a-zA-Z0-9-.]+$"
        return re.match(email_regex, email) is not None

    def generate_code(self):
        return "".join(random.choices(string.ascii_letters + string.digits, k=6))

    def force_uppercase(self, event):
        """Convierte el texto a mayúsculas en tiempo real"""
        text = self.name_entry.get().upper()  # Convierte a mayúsculas
        self.name_entry.delete(0, "end")  # Borra el texto actual
        self.name_entry.insert(0, text)  # Inserta el texto en mayúsculas

    def on_enter_exit_button(self, event):
        self.exit_button.configure(
            fg_color="#cc0000"
        )  # un rojo más oscuro al pasar el mouse

    def on_leave_exit_button(self, event):
        self.exit_button.configure(fg_color="red")  # vuelve al color original
        
    def emergency_exit(self):
        dialog = PasswordDialog(self, title="Contrasena Maestra")
        self.wait_window(dialog)
        if dialog.result is not None:
            # confirmar la contrasena maestra
            if dialog.result == MASTER_PASSWORD:
                # preguntar si desea cerrar app
                reply = CTkMessagebox(
                    title="Cerrar App",
                    message="Desea cerrar la app?",
                    icon=ask_icon,
                    option_1="Si",
                    option_2="No",
                ).get()

                # print(reply)
                
                if reply == "Si": 
                    # print("App cerrada")   
                    self.destroy()
            else:
                print("Contrasena incorrecta")
                CTkMessagebox(
                    title="Error",
                    message="La contrasena maestra es incorrecta",
                    icon=error_icon,
                ) 

        else:
            # si no se ingreso la contrasena maestra
            CTkMessagebox(
                title="Error",
                message="No se ingreso la contrasena maestra",
                icon=error_icon,
            )

class PasswordDialog(customtkinter.CTkToplevel):
    def __init__(self, parent, title="Conaseña maestra", prompt="Por favor, ingresa la contraseña maestra:"):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x150")
        self.resizable(False, False)
        self.grab_set()  # Bloquea la ventana principal
        # colocar la ventana en el centro de la pantalla
        self.geometry("+%d+%d" % (parent.winfo_screenwidth() // 2 - 150, parent.winfo_screenheight() // 2 - 75))
        
        # quitar encabezado
        # self.overrideredirect(True)
        
        # colocar encima de otras ventanas
        self.attributes("-topmost", True)

        # configurar icono
        self.iconbitmap(os.path.join(img_dir, "ico.ico"))

        # icono en barra de tareas
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            os.path.join(img_dir, "ico.ico")
        )

        customtkinter.CTkLabel(self, text=prompt, font=("Arial", 14)).pack(pady=10)

        self.entry = customtkinter.CTkEntry(self, font=("Arial", 14), show="*", width=200)
        self.entry.pack(pady=5)
        self.entry.focus()

        self.result = None
        btn = customtkinter.CTkButton(self, text="Aceptar", font=("Arial", 14, "bold"), command=self.submit)
        btn.pack(pady=10)

        self.bind("<Return>", lambda event: self.submit())  # Enter también valida

    def submit(self):
        self.result = self.entry.get()
        self.destroy()

class RecoveryWindow(QMainWindow):
    def __init__(self):

        super().__init__()
        self.setWindowTitle("Recuperación de Contraseña")
        self.setGeometry(100, 100, 800, 600)

        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # Crear un QWebEngineView para cargar la página con JavaScript
        self.browser = QWebEngineView(self)
        self.browser.setUrl(
            QUrl(
                "https://login.live.com/login.srf?wa=wsignin1.0&rpsnv=174&ct=1743026037&rver=7.5.2211.0&wp=MBI_SSL&wreply=https%3a%2f%2foutlook.live.com%2fowa%2f%3fnlp%3d1%26cobrandid%3dab0455a0-8d03-46b9-b18b-df2f57b9e44c%26culture%3des-bz%26country%3dbz%26RpsCsrfState%3da75ddc70-807c-89af-3cac-f20568bbd434&id=292841&aadredir=1&CBCXT=out&lw=1&fl=dob%2cflname%2cwld&cobrandid=ab0455a0-8d03-46b9-b18b-df2f57b9e44c"
            )
        )  # Cambia la URL

        # Crear un layout y agregar el navegador al layout
        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        # Crear un widget central y asignarle el layout
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


class counterUser(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("250x40")  # Ventana pequeña
        self.title("User Security")
        self.resizable(False, False)
        self.attributes("-topmost", True)  # Mantener encima de otras ventanas
        # evitar redimensionar
        self.resizable(False, False)
        # Protocolo para cerrar la ventana
        # self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # colocar inferior izquierda de la pantalla
        self.geometry("+%d+%d" % (0, self.winfo_screenheight() - 90))

        # quitar encabezado
        self.overrideredirect(True)

        # configurar icono
        self.iconbitmap(os.path.join(img_dir, "ico.ico"))

        # icono en barra de tareas
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            os.path.join(img_dir, "ico.ico")
        )

        self.counter = 0  # Contador de tiempo en segundos

        # frame principal
        self.frame = customtkinter.CTkFrame(
            self, corner_radius=10, fg_color="transparent"
        )
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        # imagen con icono
        # self.image = self.load_image(os.path.join(img_dir, "ico.ico"), (20, 20))
        # self.image_label = customtkinter.CTkLabel(self.frame, image=self.image, text="")
        # self.image_label.pack(side="left", pady=0, padx=10)

        # Etiqueta que muestra el tiempo transcurrido
        self.label = customtkinter.CTkLabel(
            self.frame, text="Tiempo: 0s", font=("Arial", 14, "bold")
        )
        self.label.pack(side="right", pady=5)

        # icono de cerrar
        self.image = self.load_image(off_icon, (20, 20))

        # boton de cerrar con icono
        self.boton_cerrar = customtkinter.CTkButton(
            self.frame,
            text="",
            command=self.cerrar_sesion,
            image=self.image,
            compound="left",
            fg_color="transparent",
            width=20,
            height=20,
        )
        self.boton_cerrar.pack(side="left", pady=0, padx=5)

        # Crear el tooltip pero sin mostrarlo aún
        self.tooltip = customtkinter.CTkLabel(
            self.frame,
            text="Cerrar sesión",
            # fg_color="black",
            # text_color="white",
            corner_radius=5,
        )

        self.imagen_msg = self.load_image(msg_icon, (20, 20))

        self.boton_reporte = customtkinter.CTkButton(
            self.frame,
            text="",
            command=self.reportar,
            image=self.imagen_msg,
            compound="left",
            fg_color="transparent",
            width=20,
            height=20,
        )
        self.boton_reporte.pack(side="right", pady=0, padx=5)

        self.update_timer()  # Iniciar el contador

    def reportar(self):
        # Abrir la ventana de reporte
        report = Report()
        report.mainloop()

    def update_timer(self):
        hours = self.counter // 3600  # Obtiene las horas
        minutes = (self.counter % 3600) // 60  # Obtiene los minutos
        seconds = self.counter % 60  # Obtiene los segundos

        # Formatear como "HH:MM:SS"
        time_str = f"{hours:02}:{minutes:02}.{seconds:02}"

        # Actualizar la etiqueta
        self.label.configure(text=f"Tiempo: {time_str}")

        # Incrementar el contador y llamar de nuevo en 1 segundo
        self.counter += 1
        self.after(1000, self.update_timer)

    def cerrar_sesion(self):

        # confirmar cerrar sesion

        confirmar = CTkMessagebox(
            title="Cerrar sesión",
            message="¿Estas seguro que deseas cerrar sesión?",
            icon=ask_icon,
            option_1="Si",
            option_2="No",
        ).get()

        if confirmar:
            global correo
            global current_register
            try:
                # configura base de datos
                connection = MySQLdb.connect(
                    host=db_host,
                    port=3306,
                    user=db_user,
                    password=db_password,
                    database=db_name,
                )

                # actualizar base de datos
                actualizar = connection.cursor()
                query = "UPDATE users SET status = 0 WHERE email = %s"
                actualizar.execute(query, (correo,))
                connection.commit()
                actualizar.close()
                # connection.close()

                print(current_register)
                print(datetime.now())

                # actualizar fecha de ciererre de sesion
                act_cierre = connection.cursor()
                query = "UPDATE sessions SET end_time = %s WHERE id = %s"

                try:
                    act_cierre.execute(query, (datetime.now(), current_register))
                    connection.commit()

                    # si se han actuializado correctamente
                    if actualizar.rowcount == 1 and act_cierre.rowcount == 1:
                        self.destroy()

                        app_principal = App()
                        app_principal.mainloop()

                    act_cierre.close()
                    connection.close()

                except Exception as e:
                    print(f"Error al actualizar la fecha de cierre de sesion: {e}")

            except Exception as e:
                print(f"Error al cerrar la sesión: {e}")

    def load_image(self, image_path, size):
        """Carga una imagen sin fondo y sin redondear."""
        try:
            img = Image.open(image_path).convert("RGBA")  # Mantiene la transparencia
            img = img.resize(size, Image.LANCZOS)  # Ajusta el tamaño
            return ImageTk.PhotoImage(img)  # Convierte la imagen para usar en Tkinter
        except Exception as e:
            print(f"Error al cargar la imagen: {e}")
            return None


class Report(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("Reporte")
        self.geometry("400x300")
        self.resizable(False, False)

        # colocar en el centro de la pantalla
        self.geometry(
            "+%d+%d"
            % (
                self.winfo_screenwidth() // 2 - 200,
                self.winfo_screenheight() // 2 - 150,
            )
        )

        # quitar encabezado
        self.overrideredirect(True)

        # configurar icono
        self.iconbitmap(os.path.join(img_dir, "ico.ico"))

        # icono en barra de tareas
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            os.path.join(img_dir, "ico.ico")
        )

        # frame principal
        self.frame = customtkinter.CTkFrame(
            self, corner_radius=10, fg_color="transparent"
        )
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        # Etiqueta que muestra el tiempo transcurrido
        self.label = customtkinter.CTkLabel(
            self.frame, text="Registrar reporte", font=("Arial", 16, "bold")
        )
        self.label.pack(side="top", pady=5)

        # input de texto
        self.entry = customtkinter.CTkTextbox(
            self.frame, width=300, height=100, font=("Arial", 14), corner_radius=10
        )
        self.entry.pack(side="top", pady=10)

        # botones
        self.boton_cerrar = customtkinter.CTkButton(
            self.frame,
            text="Cerrar",
            font=("Arial", 14, "bold"),
            command=self.cerrar,
            corner_radius=10,
        )
        self.boton_cerrar.pack(side="top", pady=10)

        self.boton_enviar = customtkinter.CTkButton(
            self.frame,
            text="Enviar",
            font=("Arial", 14, "bold"),
            command=self.enviar,
            corner_radius=10,
        )
        self.boton_enviar.pack(side="top", pady=10)

    def cerrar(self):
        self.destroy()

    def enviar(self):
        reporte = self.entry.get("1.0", "end-1c")
        # enviar reporte
        try:
            # configura base de datos
            connection = MySQLdb.connect(
                host=db_host,
                port=3306,
                user=db_user,
                password=db_password,
                database=db_name,
            )

            # registrar reporte
            global id
            registrar = connection.cursor()
            query = "INSERT INTO reports (id_user, report) VALUES (%s, %s)"
            registrar.execute(
                query,
                (
                    int(id),
                    reporte,
                ),
            )
            connection.commit()
            registrar.close()

            if registrar.rowcount == 1:
                CTkMessagebox(
                    title="Reporte enviado",
                    message="Reporte enviado correctamente",
                    icon="info",
                )

            connection.close()

            self.destroy()
        except Exception as e:
            print(f"Error al enviar el reporte: {e}")
            CTkMessagebox(
                title="Error",
                message="Error al enviar el reporte" + str(e),
                icon="info",
            )


class FirstConfig(customtkinter.CTk):
    # elevate()
    def __init__(self):

        super().__init__()
        # Configuración de la ventana principal
        self.title("Configuracion de inicio")
        self.geometry("500x350")
        # No permitir redimensionar la ventana
        self.resizable(False, False)
        # Establecer el icono
        self.iconbitmap(os.path.join(img_dir, "ico.ico"))
        # Establecer el protocolo para cerrar la ventana
        # self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Establecer el icono en la barra de tareas (Windows)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            os.path.join(img_dir, "ico.ico")
        )

        # centrar ventana en la pantalla
        self.geometry(
            "+%d+%d"
            % (
                self.winfo_screenwidth() // 2 - 250,
                self.winfo_screenheight() // 2 - 175,
            )
        )

        # mostrar minimizar y maximizar
        # self.overrideredirect(True)

        # 📌 Contenedor principal (similar a un "div" en HTML)
        self.main_frame = customtkinter.CTkFrame(
            self, corner_radius=10, fg_color="transparent"
        )
        self.main_frame.place(
            relx=0.5, rely=0.5, anchor="center"
        )  # Centrado en la pantalla

        # colocar icono al inicio de la ventana
        self.icono = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(img_dir, "ico.png")),
            dark_image=Image.open(os.path.join(img_dir, "ico.png")),
            size=(60, 60),
        )
        self.icono_label = customtkinter.CTkLabel(
            self.main_frame, image=self.icono, text=""
        )
        # centrar icono en la parte superior
        # self.icono_label.place(relx=0.5, rely=0.5, anchor="center")
        self.icono_label.place(relx=0, rely=0, anchor="center")
        self.icono_label.pack(side="top", pady=0)

        # colocar texto superior de la ventana
        self.label = customtkinter.CTkLabel(
            self.main_frame, text="Configuracion de inicio", font=("Arial", 20, "bold")
        )
        self.label.pack(side="top", pady=(10, 20))

        # crear input de numero de computadora
        self.entry = customtkinter.CTkEntry(
            self.main_frame,
            font=("Arial", 14),
            placeholder_text="Numero de computadora",
            width=300,
            height=40,
            corner_radius=10,
        )
        # centrar texto de entrada
        self.entry.place(relx=0.5, rely=0.5, anchor="center")
        self.entry.pack(side="top", pady=10)

        # crear input de ip de la base de datos
        self.entry_ip = customtkinter.CTkEntry(
            self.main_frame,
            font=("Arial", 14),
            placeholder_text="IP de la base de datos",
            width=300,
            height=40,
            corner_radius=10,
        )
        self.entry_ip.pack(side="top", pady=10)

        # frame de botones
        self.boton_frame = customtkinter.CTkFrame(
            self.main_frame, corner_radius=10, fg_color="transparent"
        )
        self.boton_frame.pack(side="bottom", pady=(20, 10))

        # boton de registrar reporte
        self.boton_reporte = customtkinter.CTkButton(
            self.boton_frame,
            text="Guardar",
            font=("Arial", 14, "bold"),
            command=self.guardar,
            corner_radius=10,
            height=40,
        )
        self.boton_reporte.pack(side="left", padx=10)

        # boton de cerrar
        self.boton_cerrar = customtkinter.CTkButton(
            self.boton_frame,
            text="Cerrar",
            font=("Arial", 14, "bold"),
            command=self.cerrar,
            corner_radius=10,
            height=40,
        )
        self.boton_cerrar.pack(side="right", padx=10)

    # crear opción de cerrar
    def cerrar(self):
        self.destroy()

    # opciones de modificar archivo data.ini
    def guardar(self):
        computer = self.entry.get()
        host_ip = self.entry_ip.get()

        # validar campos
        if not computer or not host_ip:
            CTkMessagebox(
                title="Error",
                message="Por favor, complete todos los campos",
                icon=error_icon,
            )
            return

        # validar numero de computadora
        if not computer.isdigit():
            CTkMessagebox(
                title="Error",
                message="El numero de computadora debe ser un numero entero",
                icon=error_icon,
            )
            return

        # validar ip de la base de datos
        if not self.validate_ip(host_ip):
            CTkMessagebox(
                title="Error",
                message="La ip de la base de datos es invalida",
                icon=error_icon,
            )
            return

        # archivo data.ini
        # [APP_CONFIG]
        # app_name = User Security UPAP
        # version = 1.0.0
        # install_date = 2000-01-01
        # created_by = Juan C. Orzuna
        # computer = 1
        # fisrt_time = 1

        # [DB_CONFIG]
        # host = 10.0.25.37
        # user = users_upap
        # database = upap
        # password = 123456
        try:

            config = configparser.ConfigParser()
            config.read(config_path)
            config.set(
                "APP_CONFIG",
                "install_date",
                datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
            )
            config.set("APP_CONFIG", "computer", computer)
            config.set("APP_CONFIG", "first_time", "0")
            config.set("DB_CONFIG", "host", host_ip)
            with open(config_path, "w") as f:
                config.write(f)

            # ocultar archivo
            ctypes.windll.kernel32.SetFileAttributesW(config_path, 0x02)

            # CTkMessagebox(
            #     title="Guardado",
            #     message="Configuracion guardada correctamente",
            #     icon=ok_icon,
            # )

            self.destroy()
            app_principal = App()
            app_principal.mainloop()

        except Exception as e:
            CTkMessagebox(
                title="Error",
                message="Error al guardar la configuración: " + str(e),
                icon=error_icon,
            )

    def validate_ip(self, ip_address):
        try:
            ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False

    def make_circle(self, image_path, size):
        img = Image.open(image_path).convert("RGBA")
        img = img.resize(size, Image.LANCZOS)

        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)

        circular_img = Image.new("RGBA", size, (0, 0, 0, 0))
        circular_img.paste(img, (0, 0), mask)

        return ImageTk.PhotoImage(circular_img)


# Iniciar la aplicación
app = QApplication(sys.argv)  # Iniciar el aplicativo Qt
if first_time == 0:
    window = App()
    window.mainloop()
else:
    config_app = FirstConfig()
    config_app.mainloop()
