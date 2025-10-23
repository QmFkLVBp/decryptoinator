import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageChops
import base64
import os
import webbrowser
import string
import io
import requests
import threading

APP_VERSION = "1.2.5"

APP_LOGO_URL = "https://raw.githubusercontent.com/QmFkLVBp/decryptoinator/refs/heads/main/logo.png"

THEMES = {
    "Нічна Прохолода": {
        "type": "dark",
        "app_bg": "#0F2027",
        "frame_bg": "#203A43",
        "button_fg": "#2C5364",
        "text_color": "#EAEAEA",
        "hover_color": "#3E606F"
    },
    "Лісовий Спокій": {
        "type": "dark",
        "app_bg": "#1A4314",
        "frame_bg": "#2E572A",
        "button_fg": "#44743F",
        "text_color": "#E0E0E0",
        "hover_color": "#5A8A55"
    },
    "Океанська Глибина": {
        "type": "dark",
        "app_bg": "#141E30",
        "frame_bg": "#243B55",
        "button_fg": "#3F6E95",
        "text_color": "#DDEEFF",
        "hover_color": "#528AAE"
    },
    "Світанок": {
        "type": "light",
        "app_bg": "#FFF0F5",
        "frame_bg": "#E6E6FA",
        "button_fg": "#ADD8E6",
        "text_color": "#333333",
        "hover_color": "#B0E0E6"
    },
    "Кава з Молоком": {
        "type": "light",
        "app_bg": "#F5F5DC",
        "frame_bg": "#DEB887",
        "button_fg": "#D2B48C",
        "text_color": "#4F4F4F",
        "hover_color": "#CDAA7D"
    },
    "Весняний Луг": {
        "type": "light",
        "app_bg": "#F0FFF0",
        "frame_bg": "#C1E1C1",
        "button_fg": "#98FB98",
        "text_color": "#2F4F4F",
        "hover_color": "#ACE1AF"
    }
}

LANG_STRINGS = {
    "ua": {
        "title": "ДЕКРИПТОІНАТОР 1000",
        "nav_xor": "XOR Аналіз",
        "nav_lsb": "LSB Екстрактор",
        "nav_picker": "Color Picker",
        "nav_vigenere": "Шифр Віженера",
        "nav_base64": "Base64 Кодер/Декодер",
        "nav_ela": "ELA Аналіз",
        "nav_settings": "Налаштування",
        "nav_about": "Про автора",
        "xor_title": "Вікно: XOR Аналіз Зображень",
        "xor_img1_text": "Зображення 1",
        "xor_img2_text": "Зображення 2",
        "xor_load1": "Завантажити Зображення 1",
        "xor_load2": "Завантажити Зображення 2",
        "xor_run": "ВИКОНАТИ XOR",
        "xor_result_text": "Тут буде результат XOR",
        "xor_status_error_load": "Помилка: Завантажте ОБИДВА зображення",
        "xor_status_processing": "Обробка...",
        "xor_status_warn_resize": "Увага: Розміри не збігались. Приведено до розміру Зобр. 1.",
        "xor_status_ok": "XOR успішно виконано!",
        "lsb_title": "Вікно: LSB Екстрактор Тексту",
        "lsb_load": "Завантажити Контейнер",
        "lsb_run": "РОЗШИФРУВАТИ LSB",
        "lsb_original_text": "Оригінал",
        "lsb_result_text": "Результат (LSB-площина)",
        "lsb_decoded_text_label": "Розшифроване Повідомлення:",
        "lsb_status_warn_format": "УВАГА: Це, скоріш за все, 'lossy' формат. Метод може не спрацювати.",
        "lsb_status_ok_load": "Контейнер 'lossless' завантажено. Натисніть 'Розшифрувати'.",
        "lsb_status_error_load": "Спочатку завантажте контейнер!",
        "lsb_status_processing": "Розшифровка...",
        "lsb_status_ok": "Розшифровка завершена.",
        "lsb_error_base64": "[Повідомлення не знайдено (невалідні дані Base64 або це JPEG)]",
        "lsb_error_eof": "[Повідомлення не знайдено (досягнуто кінець зображення)]",
        "lsb_error_general": "[Помилка читання LSB-тексту: {e}]",
        "lsb_error_decode": "[Помилка декодування Base64: {e}]\n\nЗібраний рядок:\n{s}",
        "picker_title": "Вікно: Color Picker та Hex->Text",
        "picker_load": "Завантажити зображення",
        "picker_img_text": "Завантажте зображення, щоб клікнути",
        "picker_hex_default": "Hex: #000000",
        "picker_text_default": "Останній клік: ...",
        "picker_clear": "Очистити поле",
        "picker_status_default": "Клікніть на зображення",
        "picker_status_error_load": "Спочатку завантажте зображення!",
        "vigenere_title": "Вікно: Шифр Віженера",
        "vigenere_mode_encrypt": "Зашифрувати",
        "vigenere_mode_decrypt": "Розшифрувати",
        "vigenere_input_label_encrypt": "Відкритий текст:",
        "vigenere_input_label_decrypt": "Зашифрований текст:",
        "vigenere_key_label": "Ключове слово:",
        "vigenere_run_encrypt": "ЗАШИФРУВАТИ",
        "vigenere_run_decrypt": "РОЗШИФРУВАТИ",
        "vigenere_output_label_encrypt": "Зашифрований текст:",
        "vigenere_output_label_decrypt": "Розшифрований текст:",
        "vigenere_status_ok_encrypt": "Шифрування Віженера завершено.",
        "vigenere_status_ok_decrypt": "Розшифровка Віженера завершена.",
        "vigenere_status_error_input": "Помилка: Введіть текст та ключ.",
        "vigenere_status_error_key": "Помилка: Ключ повинен містити лише літери.",
        "base64_title": "Вікно: Base64 Кодер/Декодер",
        "base64_mode_encode": "Кодувати (в Base64)",
        "base64_mode_decode": "Декодувати (з Base64)",
        "base64_input_label_encode": "Текст (UTF-8):",
        "base64_input_label_decode": "Base64 рядок:",
        "base64_run_encode": "КОДУВАТИ",
        "base64_run_decode": "ДЕКОДУВАТИ",
        "base64_output_label_encode": "Base64 рядок:",
        "base64_output_label_decode": "Текст (UTF-8):",
        "base64_status_ok_encode": "Кодування Base64 завершено.",
        "base64_status_ok_decode": "Декодування Base64 завершено.",
        "base64_status_error_input": "Помилка: Введіть дані для обробки.",
        "base64_status_error_decode": "Помилка: Недійсний Base64 рядок або падінг.",
        "ela_title": "Вікно: ELA Аналіз (Рівень Помилок)",
        "ela_load": "Завантажити Зображення",
        "ela_original_text": "Оригінал",
        "ela_result_text": "ELA Результат",
        "ela_quality_label": "Якість JPEG (%):",
        "ela_scale_label": "Масштаб різниці:",
        "ela_run": "ВИКОНАТИ ELA",
        "ela_status_processing": "Виконується ELA...",
        "ela_status_ok": "ELA аналіз завершено.",
        "ela_status_error_load": "Спочатку завантажте зображення.",
        "ela_status_error_params": "Помилка: Якість має бути 1-100, Масштаб > 0.",
        "settings_title": "Вікно: Налаштування",
        "settings_lang": "Мова (Language):",
        "settings_theme": "Тема:",
        "settings_danger_zone": "Зона небезпеки ☣️",
        "settings_self_destruct": "САМОЗНИЩЕННЯ",
        "settings_self_destruct_run": "ЗНИЩЕННЯ...",
        "settings_self_destruct_prank": "Жартую! 😜\nВсе на місці.",
        "about_title": "Вікно: Про автора",
        "about_text": f"Автор: Крилевич Мирослав\n" \
                      f"Група: УБД-32\n\n" \
                      f"Розроблено для навчальних цілей в криптографії.\n" \
                      f"<<  Поки я не почитав ККУ - життя здавалось більш яскравішим >>\n\n" \
                      f"Версія: {APP_VERSION}",
        "about_links_label": "Посилання:",
        "theme_night_cool": "Нічна Прохолода",
        "theme_forest_calm": "Лісовий Спокій",
        "theme_ocean_depth": "Океанська Глибина",
        "theme_sunrise": "Світанок",
        "theme_coffee": "Кава з Молоком",
        "theme_spring_meadow": "Весняний Луг",
    },
    "en": {
        "title": "DECRYPTOINATOR 1000",
        "nav_xor": "XOR Analysis",
        "nav_lsb": "LSB Extractor",
        "nav_picker": "Color Picker",
        "nav_vigenere": "Vigenère Cipher",
        "nav_base64": "Base64 Encoder/Decoder",
        "nav_ela": "ELA Analysis",
        "nav_settings": "Settings",
        "nav_about": "About",
        "xor_title": "Window: XOR Image Analysis",
        "xor_img1_text": "Image 1",
        "xor_img2_text": "Image 2",
        "xor_load1": "Load Image 1",
        "xor_load2": "Load Image 2",
        "xor_run": "PERFORM XOR",
        "xor_result_text": "XOR result will be here",
        "xor_status_error_load": "Error: Load BOTH images first",
        "xor_status_processing": "Processing...",
        "xor_status_warn_resize": "Warning: Sizes mismatched. Resized to Image 1.",
        "xor_status_ok": "XOR successful!",
        "lsb_title": "Window: LSB Text Extractor",
        "lsb_load": "Load Container",
        "lsb_run": "DECRYPT LSB",
        "lsb_original_text": "Original",
        "lsb_result_text": "Result (LSB Plane)",
        "lsb_decoded_text_label": "Decrypted Message:",
        "lsb_status_warn_format": "WARNING: This is likely a 'lossy' format. Method may fail.",
        "lsb_status_ok_load": "'Lossless' container loaded. Press 'Decrypt'.",
        "lsb_status_error_load": "Load a container first!",
        "lsb_status_processing": "Decrypting...",
        "lsb_status_ok": "Decryption complete.",
        "lsb_error_base64": "[Message not found (invalid Base64 data or JPEG)]",
        "lsb_error_eof": "[Message not found (end of image reached)]",
        "lsb_error_general": "[Error reading LSB text: {e}]",
        "lsb_error_decode": "[Error decoding Base64: {e}]\n\nCollected string:\n{s}",
        "picker_title": "Window: Color Picker & Hex->Text",
        "picker_load": "Load Image",
        "picker_img_text": "Load an image to click on",
        "picker_hex_default": "Hex: #000000",
        "picker_text_default": "Last Click: ...",
        "picker_clear": "Clear Field",
        "picker_status_default": "Click on the image",
        "picker_status_error_load": "Load an image first!",
        "vigenere_title": "Window: Vigenère Cipher",
        "vigenere_mode_encrypt": "Encrypt",
        "vigenere_mode_decrypt": "Decrypt",
        "vigenere_input_label_encrypt": "Plaintext:",
        "vigenere_input_label_decrypt": "Ciphertext:",
        "vigenere_key_label": "Keyword:",
        "vigenere_run_encrypt": "ENCRYPT",
        "vigenere_run_decrypt": "DECRYPT",
        "vigenere_output_label_encrypt": "Ciphertext:",
        "vigenere_output_label_decrypt": "Plaintext:",
        "vigenere_status_ok_encrypt": "Vigenère encryption complete.",
        "vigenere_status_ok_decrypt": "Vigenère decryption complete.",
        "vigenere_status_error_input": "Error: Enter text and keyword.",
        "vigenere_status_error_key": "Error: Keyword must contain only letters.",
        "base64_title": "Window: Base64 Encoder/Decoder",
        "base64_mode_encode": "Encode (to Base64)",
        "base64_mode_decode": "Decode (from Base64)",
        "base64_input_label_encode": "Text (UTF-8):",
        "base64_input_label_decode": "Base64 String:",
        "base64_run_encode": "ENCODE",
        "base64_run_decode": "DECODE",
        "base64_output_label_encode": "Base64 String:",
        "base64_output_label_decode": "Text (UTF-8):",
        "base64_status_ok_encode": "Base64 encoding complete.",
        "base64_status_ok_decode": "Base64 decoding complete.",
        "base64_status_error_input": "Error: Enter data to process.",
        "base64_status_error_decode": "Error: Invalid Base64 string or padding.",
        "ela_title": "Window: ELA (Error Level Analysis)",
        "ela_load": "Load Image",
        "ela_original_text": "Original",
        "ela_result_text": "ELA Result",
        "ela_quality_label": "JPEG Quality (%):",
        "ela_scale_label": "Difference Scale:",
        "ela_run": "PERFORM ELA",
        "ela_status_processing": "Performing ELA...",
        "ela_status_ok": "ELA analysis complete.",
        "ela_status_error_load": "Load an image first.",
        "ela_status_error_params": "Error: Quality must be 1-100, Scale > 0.",
        "settings_title": "Window: Settings",
        "settings_lang": "Language:",
        "settings_theme": "Theme:",
        "settings_danger_zone": "Danger Zone ☣️",
        "settings_self_destruct": "SELF-DESTRUCT",
        "settings_self_destruct_run": "DESTRUCTING...",
        "settings_self_destruct_prank": "Just kidding! 😜\nEverything is fine.",
        "about_title": "Window: About",
        "about_text": f"Author: Krylevych Myroslav\n" \
                      f"Group: UBD-32\n\n" \
                      f"Developed for learning scope in cybersecurity.\n" \
                      f"<< Until I read the KKU - life seemed brighter >>\n\n" \
                      f"Version: {APP_VERSION}",
        "about_links_label": "Links:",
        "theme_night_cool": "Night Cool",
        "theme_forest_calm": "Forest Calm",
        "theme_ocean_depth": "Ocean Depth",
        "theme_sunrise": "Sunrise",
        "theme_coffee": "Coffee Milk",
        "theme_spring_meadow": "Spring Meadow",
    }
}

VALID_BASE64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="


class StegoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.all_widgets = []

        self.current_lang = ctk.StringVar(value="ua")
        self.current_lang.trace_add("write", self.change_language)

        self.geometry("1100x700")
        self.title(LANG_STRINGS[self.current_lang.get()]["title"])

        self.xor_image_path1 = None
        self.xor_image_path2 = None
        self.lsb_image_path = None
        self.picker_pil_image = None
        self.ela_image_path = None
        self.vigenere_mode = ctk.StringVar(value=LANG_STRINGS[self.current_lang.get()]["vigenere_mode_decrypt"])
        self.base64_mode = ctk.StringVar(value=LANG_STRINGS[self.current_lang.get()]["base64_mode_encode"])

        self.logo_image = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_nav_frame()
        self.setup_content_frames()

        self.update_all_texts(self.current_lang.get())
        self.load_network_logo()
        self.after(50, lambda: self.apply_theme_by_name("Нічна Прохолода"))
        self.show_xor_frame()

    def _create_widget(self, widget_class, *args, **kwargs):
        widget = widget_class(*args, **kwargs)
        if isinstance(widget,
                      (ctk.CTkFrame, ctk.CTkButton, ctk.CTkLabel, ctk.CTkOptionMenu, ctk.CTkTextbox, ctk.CTkProgressBar,
                       ctk.CTkEntry, ctk.CTkSlider, ctk.CTkSegmentedButton)):
            widget.is_themeable = True
            self.all_widgets.append(widget)
        elif isinstance(widget, tk.PhotoImage):
            pass
        else:
            try:
                widget.is_themeable = False
                self.all_widgets.append(widget)
            except AttributeError:
                pass
        return widget

    def setup_nav_frame(self):
        self.nav_frame = self._create_widget(ctk.CTkFrame, self, width=180, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="nswe")
        self.nav_frame.is_themeable = True

        self.app_logo_label = self._create_widget(ctk.CTkLabel, self.nav_frame, text="",
                                                  font=ctk.CTkFont(size=40, weight="bold"))
        self.app_logo_label.grid(row=0, column=0, padx=20, pady=20)

        self.xor_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_xor_frame, anchor="w")
        self.xor_button.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        self.lsb_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_lsb_frame, anchor="w")
        self.lsb_button.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.picker_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_picker_frame,
                                                 anchor="w")
        self.picker_button.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        self.vigenere_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_vigenere_frame,
                                                   anchor="w")
        self.vigenere_button.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        self.base64_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_base64_frame,
                                                 anchor="w")
        self.base64_button.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        self.ela_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_ela_frame, anchor="w")
        self.ela_button.grid(row=6, column=0, padx=20, pady=5, sticky="ew")

        self.nav_frame.grid_rowconfigure(7, weight=1)

        self.settings_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_settings_frame,
                                                   anchor="w")
        self.settings_button.grid(row=8, column=0, padx=20, pady=5, sticky="ew")

        self.about_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_about_frame,
                                                anchor="w")
        self.about_button.grid(row=9, column=0, padx=20, pady=20, sticky="ew")

    def load_network_logo(self):
        threading.Thread(target=self._download_logo, daemon=True).start()

    def _download_logo(self):
        try:
            response = requests.get(APP_LOGO_URL, timeout=5)
            response.raise_for_status()

            image_data = response.content
            pil_image = Image.open(io.BytesIO(image_data))

            self.logo_image = ctk.CTkImage(pil_image, size=(40, 40))

            self.after(0, self._update_logo_widget)
        except Exception as e:
            print(f"Failed to load network logo: {e}")
            self.after(0, self._set_default_logo_text)

    def _update_logo_widget(self):
        if self.logo_image and self.app_logo_label.winfo_exists():
            self.app_logo_label.configure(text="", image=self.logo_image)

    def _set_default_logo_text(self):
        if self.app_logo_label.winfo_exists():
            self.app_logo_label.configure(image=None, text="🔒")

    def setup_content_frames(self):
        self.xor_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent");
        self.xor_frame.is_themeable = False
        self.lsb_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent");
        self.lsb_frame.is_themeable = False
        self.picker_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent");
        self.picker_frame.is_themeable = False
        self.vigenere_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent");
        self.vigenere_frame.is_themeable = False
        self.base64_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent");
        self.base64_frame.is_themeable = False
        self.ela_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent");
        self.ela_frame.is_themeable = False
        self.settings_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent");
        self.settings_frame.is_themeable = False
        self.about_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent");
        self.about_frame.is_themeable = False

        self.setup_xor_frame_widgets()
        self.setup_lsb_frame_widgets()
        self.setup_picker_frame_widgets()
        self.setup_vigenere_frame_widgets()
        self.setup_base64_frame_widgets()
        self.setup_ela_frame_widgets()
        self.setup_settings_frame_widgets()
        self.setup_about_frame_widgets()

    def setup_xor_frame_widgets(self):
        self.xor_frame.grid_columnconfigure((0, 1), weight=1)
        self.xor_title = self._create_widget(ctk.CTkLabel, self.xor_frame, font=ctk.CTkFont(size=24, weight="bold"))
        self.xor_title.grid(row=0, column=0, columnspan=2, pady=20, padx=20)

        self.xor_label1 = self._create_widget(ctk.CTkLabel, self.xor_frame, width=300, height=300, fg_color="gray20",
                                              corner_radius=10, text="");
        self.xor_label1.is_themeable = False
        self.xor_label1.grid(row=1, column=0, padx=20, pady=10, sticky="n")
        self.xor_load_btn1 = self._create_widget(ctk.CTkButton, self.xor_frame, command=self.load_xor_image1)
        self.xor_load_btn1.grid(row=2, column=0, padx=20, pady=10)

        self.xor_label2 = self._create_widget(ctk.CTkLabel, self.xor_frame, width=300, height=300, fg_color="gray20",
                                              corner_radius=10, text="");
        self.xor_label2.is_themeable = False
        self.xor_label2.grid(row=1, column=1, padx=20, pady=10, sticky="n")
        self.xor_load_btn2 = self._create_widget(ctk.CTkButton, self.xor_frame, command=self.load_xor_image2)
        self.xor_load_btn2.grid(row=2, column=1, padx=20, pady=10)

        self.xor_run_btn = self._create_widget(ctk.CTkButton, self.xor_frame, command=self.perform_xor,
                                               font=ctk.CTkFont(size=16, weight="bold"))
        self.xor_run_btn.grid(row=3, column=0, columnspan=2, pady=20)

        self.xor_result_label = self._create_widget(ctk.CTkLabel, self.xor_frame, width=300, height=300,
                                                    fg_color="gray25", corner_radius=10, text="");
        self.xor_result_label.is_themeable = False
        self.xor_result_label.grid(row=4, column=0, columnspan=2, pady=10)
        self.xor_status_label = self._create_widget(ctk.CTkLabel, self.xor_frame, text="", text_color="yellow");
        self.xor_status_label.is_themeable = False

    def setup_lsb_frame_widgets(self):
        self.lsb_frame.grid_columnconfigure(0, weight=1)
        self.lsb_frame.grid_rowconfigure(4, weight=1)

        self.lsb_title = self._create_widget(ctk.CTkLabel, self.lsb_frame, font=ctk.CTkFont(size=24, weight="bold"))
        self.lsb_title.grid(row=0, column=0, pady=20, padx=20)

        controls_frame = self._create_widget(ctk.CTkFrame, self.lsb_frame)
        controls_frame.grid(row=1, column=0, pady=10, padx=20)

        self.lsb_load_btn = self._create_widget(ctk.CTkButton, controls_frame, command=self.load_lsb_image)
        self.lsb_load_btn.grid(row=0, column=0, padx=10, pady=10)

        self.lsb_run_btn = self._create_widget(ctk.CTkButton, controls_frame, command=self.perform_lsb_extraction,
                                               font=ctk.CTkFont(size=16, weight="bold"))
        self.lsb_run_btn.grid(row=0, column=1, padx=10, pady=10)

        img_frame = self._create_widget(ctk.CTkFrame, self.lsb_frame, fg_color="transparent");
        img_frame.is_themeable = False
        img_frame.grid(row=2, column=0, pady=10, padx=20, sticky="ew")
        img_frame.grid_columnconfigure((0, 1), weight=1)

        self.lsb_original_label = self._create_widget(ctk.CTkLabel, img_frame, width=350, height=250, fg_color="gray20",
                                                      corner_radius=10, text="");
        self.lsb_original_label.is_themeable = False
        self.lsb_original_label.grid(row=0, column=0, pady=10, padx=10)

        self.lsb_result_label = self._create_widget(ctk.CTkLabel, img_frame, width=350, height=250, fg_color="gray25",
                                                    corner_radius=10, text="");
        self.lsb_result_label.is_themeable = False
        self.lsb_result_label.grid(row=0, column=1, pady=10, padx=10)

        self.lsb_decoded_text_label = self._create_widget(ctk.CTkLabel, self.lsb_frame, font=ctk.CTkFont(size=16))
        self.lsb_decoded_text_label.grid(row=3, column=0, pady=(10, 0), sticky="s")

        self.lsb_text_result = self._create_widget(ctk.CTkTextbox, self.lsb_frame, height=100, font=("Consolas", 14))
        self.lsb_text_result.grid(row=4, column=0, pady=10, padx=20, sticky="nsew")

        self.lsb_status_label = self._create_widget(ctk.CTkLabel, self.lsb_frame, text="", text_color="yellow");
        self.lsb_status_label.is_themeable = False

    def setup_picker_frame_widgets(self):
        self.picker_frame.grid_columnconfigure(0, weight=1)
        self.picker_frame.grid_rowconfigure(2, weight=1)
        self.picker_frame.grid_rowconfigure(4, weight=1)

        self.picker_title = self._create_widget(ctk.CTkLabel, self.picker_frame,
                                                font=ctk.CTkFont(size=24, weight="bold"))
        self.picker_title.grid(row=0, column=0, pady=20, padx=20)

        self.picker_load_btn = self._create_widget(ctk.CTkButton, self.picker_frame, command=self.load_picker_image)
        self.picker_load_btn.grid(row=1, column=0, pady=10)

        self.picker_image_label = self._create_widget(ctk.CTkLabel, self.picker_frame, fg_color="gray20",
                                                      corner_radius=10, text="");
        self.picker_image_label.is_themeable = False
        self.picker_image_label.grid(row=2, column=0, pady=10, padx=20, sticky="nswe")
        self.picker_image_label.bind("<Button-1>", self.on_image_click)

        result_frame = self._create_widget(ctk.CTkFrame, self.picker_frame)
        result_frame.grid(row=3, column=0, pady=10)
        self.picker_hex_label = self._create_widget(ctk.CTkLabel, result_frame,
                                                    font=ctk.CTkFont(size=16, family="Consolas"))
        self.picker_hex_label.grid(row=0, column=0, padx=20, pady=5)
        self.picker_last_text_label = self._create_widget(ctk.CTkLabel, result_frame,
                                                          font=ctk.CTkFont(size=16, family="Consolas"))
        self.picker_last_text_label.grid(row=0, column=1, padx=20, pady=5)

        self.picker_accumulated_text = self._create_widget(ctk.CTkTextbox, self.picker_frame, height=100,
                                                           font=("Consolas", 14))
        self.picker_accumulated_text.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 10))
        self.picker_clear_btn = self._create_widget(ctk.CTkButton, self.picker_frame, command=self.clear_picker_text)
        self.picker_clear_btn.grid(row=5, column=0, pady=5)

        self.picker_status_label = self._create_widget(ctk.CTkLabel, self.picker_frame, text_color="gray");
        self.picker_status_label.is_themeable = False

    def setup_vigenere_frame_widgets(self):
        self.vigenere_frame.grid_columnconfigure(0, weight=1)
        self.vigenere_frame.grid_rowconfigure(3, weight=1)
        self.vigenere_frame.grid_rowconfigure(6, weight=1)

        self.vigenere_title = self._create_widget(ctk.CTkLabel, self.vigenere_frame,
                                                  font=ctk.CTkFont(size=24, weight="bold"))
        self.vigenere_title.grid(row=0, column=0, pady=20, padx=20)

        lang_code = self.current_lang.get()
        mode_values = [LANG_STRINGS[lang_code]["vigenere_mode_encrypt"],
                       LANG_STRINGS[lang_code]["vigenere_mode_decrypt"]]
        self.vigenere_mode_selector = self._create_widget(ctk.CTkSegmentedButton, self.vigenere_frame,
                                                          values=mode_values,
                                                          variable=self.vigenere_mode,
                                                          command=self.update_vigenere_labels)
        self.vigenere_mode_selector.grid(row=1, column=0, pady=10, padx=20)
        self.vigenere_mode.set(mode_values[1])

        self.vigenere_input_label = self._create_widget(ctk.CTkLabel, self.vigenere_frame, font=ctk.CTkFont(size=16))
        self.vigenere_input_label.grid(row=2, column=0, pady=(10, 0), padx=20, sticky="w")
        self.vigenere_input_textbox = self._create_widget(ctk.CTkTextbox, self.vigenere_frame, height=150)
        self.vigenere_input_textbox.grid(row=3, column=0, pady=5, padx=20, sticky="nsew")

        controls_frame = self._create_widget(ctk.CTkFrame, self.vigenere_frame)
        controls_frame.grid(row=4, column=0, pady=10, padx=20)

        self.vigenere_key_label = self._create_widget(ctk.CTkLabel, controls_frame)
        self.vigenere_key_label.grid(row=0, column=0, padx=(0, 5))
        self.vigenere_key_entry = self._create_widget(ctk.CTkEntry, controls_frame, width=200)
        self.vigenere_key_entry.grid(row=0, column=1, padx=5)
        self.vigenere_run_btn = self._create_widget(ctk.CTkButton, controls_frame,
                                                    command=self.perform_vigenere_operation)
        self.vigenere_run_btn.grid(row=0, column=2, padx=(20, 0))

        self.vigenere_output_label = self._create_widget(ctk.CTkLabel, self.vigenere_frame, font=ctk.CTkFont(size=16))
        self.vigenere_output_label.grid(row=5, column=0, pady=(10, 0), padx=20, sticky="w")
        self.vigenere_output_textbox = self._create_widget(ctk.CTkTextbox, self.vigenere_frame, height=150)
        self.vigenere_output_textbox.grid(row=6, column=0, pady=5, padx=20, sticky="nsew")

        self.vigenere_status_label = self._create_widget(ctk.CTkLabel, self.vigenere_frame, text="",
                                                         text_color="yellow");
        self.vigenere_status_label.is_themeable = False

    def setup_base64_frame_widgets(self):
        self.base64_frame.grid_columnconfigure(0, weight=1)
        self.base64_frame.grid_rowconfigure(3, weight=1)
        self.base64_frame.grid_rowconfigure(6, weight=1)

        self.base64_title = self._create_widget(ctk.CTkLabel, self.base64_frame,
                                                font=ctk.CTkFont(size=24, weight="bold"))
        self.base64_title.grid(row=0, column=0, pady=20, padx=20)

        lang_code = self.current_lang.get()
        mode_values = [LANG_STRINGS[lang_code]["base64_mode_encode"], LANG_STRINGS[lang_code]["base64_mode_decode"]]
        self.base64_mode_selector = self._create_widget(ctk.CTkSegmentedButton, self.base64_frame,
                                                        values=mode_values,
                                                        variable=self.base64_mode,
                                                        command=self.update_base64_labels)
        self.base64_mode_selector.grid(row=1, column=0, pady=10, padx=20)
        self.base64_mode.set(mode_values[0])

        self.base64_input_label = self._create_widget(ctk.CTkLabel, self.base64_frame, font=ctk.CTkFont(size=16))
        self.base64_input_label.grid(row=2, column=0, pady=(10, 0), padx=20, sticky="w")
        self.base64_input_textbox = self._create_widget(ctk.CTkTextbox, self.base64_frame, height=150)
        self.base64_input_textbox.grid(row=3, column=0, pady=5, padx=20, sticky="nsew")

        self.base64_run_btn = self._create_widget(ctk.CTkButton, self.base64_frame,
                                                  command=self.perform_base64_operation,
                                                  font=ctk.CTkFont(size=16, weight="bold"))
        self.base64_run_btn.grid(row=4, column=0, pady=10, padx=20)

        self.base64_output_label = self._create_widget(ctk.CTkLabel, self.base64_frame, font=ctk.CTkFont(size=16))
        self.base64_output_label.grid(row=5, column=0, pady=(10, 0), padx=20, sticky="w")
        self.base64_output_textbox = self._create_widget(ctk.CTkTextbox, self.base64_frame, height=150)
        self.base64_output_textbox.grid(row=6, column=0, pady=5, padx=20, sticky="nsew")

        self.base64_status_label = self._create_widget(ctk.CTkLabel, self.base64_frame, text="", text_color="yellow");
        self.base64_status_label.is_themeable = False

    def setup_ela_frame_widgets(self):
        self.ela_frame.grid_columnconfigure(0, weight=1)

        self.ela_title = self._create_widget(ctk.CTkLabel, self.ela_frame, font=ctk.CTkFont(size=24, weight="bold"))
        self.ela_title.grid(row=0, column=0, pady=20, padx=20)

        controls_frame = self._create_widget(ctk.CTkFrame, self.ela_frame)
        controls_frame.grid(row=1, column=0, pady=10, padx=20)
        controls_frame.grid_columnconfigure(1, weight=1)

        self.ela_load_btn = self._create_widget(ctk.CTkButton, controls_frame, command=self.load_ela_image)
        self.ela_load_btn.grid(row=0, column=0, padx=10, pady=10)

        self.ela_quality_label = self._create_widget(ctk.CTkLabel, controls_frame)
        self.ela_quality_label.grid(row=1, column=0, padx=(10, 5), pady=5, sticky="w")
        self.ela_quality_entry = self._create_widget(ctk.CTkEntry, controls_frame, width=50)
        self.ela_quality_entry.grid(row=1, column=1, padx=(0, 10), pady=5, sticky="w")
        self.ela_quality_entry.insert(0, "95")

        self.ela_scale_label = self._create_widget(ctk.CTkLabel, controls_frame)
        self.ela_scale_label.grid(row=2, column=0, padx=(10, 5), pady=5, sticky="w")
        self.ela_scale_entry = self._create_widget(ctk.CTkEntry, controls_frame, width=50)
        self.ela_scale_entry.grid(row=2, column=1, padx=(0, 10), pady=5, sticky="w")
        self.ela_scale_entry.insert(0, "15")

        self.ela_run_btn = self._create_widget(ctk.CTkButton, controls_frame, command=self.run_ela_analysis,
                                               font=ctk.CTkFont(size=16, weight="bold"))
        self.ela_run_btn.grid(row=1, column=2, rowspan=2, padx=20, pady=10)

        img_frame = self._create_widget(ctk.CTkFrame, self.ela_frame, fg_color="transparent");
        img_frame.is_themeable = False
        img_frame.grid(row=2, column=0, pady=10, padx=20, sticky="ew")
        img_frame.grid_columnconfigure((0, 1), weight=1)

        self.ela_original_label = self._create_widget(ctk.CTkLabel, img_frame, width=350, height=300, fg_color="gray20",
                                                      corner_radius=10, text="");
        self.ela_original_label.is_themeable = False
        self.ela_original_label.grid(row=0, column=0, pady=10, padx=10)

        self.ela_result_label = self._create_widget(ctk.CTkLabel, img_frame, width=350, height=300, fg_color="gray25",
                                                    corner_radius=10, text="");
        self.ela_result_label.is_themeable = False
        self.ela_result_label.grid(row=0, column=1, pady=10, padx=10)

        self.ela_status_label = self._create_widget(ctk.CTkLabel, self.ela_frame, text="", text_color="yellow");
        self.ela_status_label.is_themeable = False

    def setup_settings_frame_widgets(self):
        self.settings_frame.grid_columnconfigure(0, weight=1)
        self.settings_title = self._create_widget(ctk.CTkLabel, self.settings_frame,
                                                  font=ctk.CTkFont(size=24, weight="bold"))
        self.settings_title.grid(row=0, column=0, pady=20, padx=20)

        lang_frame = self._create_widget(ctk.CTkFrame, self.settings_frame)
        lang_frame.grid(row=1, column=0, pady=10)
        self.settings_lang_label = self._create_widget(ctk.CTkLabel, lang_frame)
        self.settings_lang_label.grid(row=0, column=0, padx=10)
        self.settings_lang_menu = self._create_widget(ctk.CTkOptionMenu, lang_frame, values=["ua", "en"],
                                                      variable=self.current_lang)
        self.settings_lang_menu.grid(row=0, column=1, padx=10)

        theme_frame = self._create_widget(ctk.CTkFrame, self.settings_frame)
        theme_frame.grid(row=2, column=0, pady=10)
        self.settings_theme_label = self._create_widget(ctk.CTkLabel, theme_frame)
        self.settings_theme_label.grid(row=0, column=0, padx=10, pady=5)

        theme_display_names = list(THEMES.keys())

        self.settings_theme_menu = self._create_widget(ctk.CTkOptionMenu, theme_frame, values=theme_display_names,
                                                       command=self.apply_theme_by_name)
        self.settings_theme_menu.grid(row=0, column=1, padx=10, pady=5)
        self.settings_theme_menu.set("Нічна Прохолода")

        self.settings_danger_label = self._create_widget(ctk.CTkLabel, self.settings_frame,
                                                         font=ctk.CTkFont(size=16, weight="bold"))
        self.settings_danger_label.grid(row=9, column=0, pady=(50, 10))

        self.self_destruct_btn = self._create_widget(ctk.CTkButton, self.settings_frame,
                                                     fg_color="red", hover_color="darkred",
                                                     command=self.self_destruct);
        self.self_destruct_btn.is_themeable = False
        self.self_destruct_btn.grid(row=10, column=0, pady=10, padx=50, sticky="ew")

        self.self_destruct_progress = self._create_widget(ctk.CTkProgressBar, self.settings_frame, fg_color="gray20",
                                                          progress_color="red");
        self.self_destruct_progress.is_themeable = False
        self.self_destruct_progress.set(0)
        self.self_destruct_progress.grid(row=11, column=0, padx=50, pady=(0, 20), sticky="ew")

    def setup_about_frame_widgets(self):
        self.about_frame.grid_columnconfigure(0, weight=1)
        self.about_frame.grid_rowconfigure(0, weight=0)
        self.about_frame.grid_rowconfigure(1, weight=1)
        self.about_frame.grid_rowconfigure(2, weight=1)

        self.about_title = self._create_widget(ctk.CTkLabel, self.about_frame, font=ctk.CTkFont(size=24, weight="bold"))
        self.about_title.grid(row=0, column=0, pady=20, padx=20)

        center_frame = self._create_widget(ctk.CTkFrame, self.about_frame, fg_color="transparent");
        center_frame.is_themeable = False
        center_frame.grid(row=1, column=0, sticky="nsew", pady=20)
        center_frame.grid_columnconfigure(0, weight=1)

        self.about_text_label = self._create_widget(ctk.CTkLabel, center_frame, justify=tk.CENTER,
                                                    font=ctk.CTkFont(size=16))
        self.about_text_label.grid(row=0, column=0, padx=20, pady=20)

        self.about_links_label = self._create_widget(ctk.CTkLabel, center_frame,
                                                     font=ctk.CTkFont(size=16, weight="bold"))
        self.about_links_label.grid(row=1, column=0, padx=20, pady=(20, 5))

        links_frame = self._create_widget(ctk.CTkFrame, center_frame, fg_color="transparent");
        links_frame.is_themeable = False
        links_frame.grid(row=2, column=0, padx=20)
        links_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        linkedin_url = "https://www.linkedin.com/in/cybersecsprofile/"
        github_url = "https://github.com/QmFkLVBp"
        htb_url = "https://app.hackthebox.com/profile/1969974"
        thm_url = "https://tryhackme.com/p/0xW1ZARD"

        self.linkedin_btn = self._create_widget(ctk.CTkButton, links_frame, text="LinkedIn",
                                                command=lambda: self.open_link(linkedin_url))
        self.linkedin_btn.grid(row=0, column=0, padx=5, pady=5)
        self.github_btn = self._create_widget(ctk.CTkButton, links_frame, text="GitHub",
                                              command=lambda: self.open_link(github_url))
        self.github_btn.grid(row=0, column=1, padx=5, pady=5)
        self.htb_btn = self._create_widget(ctk.CTkButton, links_frame, text="HackTheBox",
                                           command=lambda: self.open_link(htb_url))
        self.htb_btn.grid(row=0, column=2, padx=5, pady=5)
        self.thm_btn = self._create_widget(ctk.CTkButton, links_frame, text="TryHackMe",
                                           command=lambda: self.open_link(thm_url))
        self.thm_btn.grid(row=0, column=3, padx=5, pady=5)

    def open_link(self, url):
        webbrowser.open_new(url)

    def apply_theme_by_name(self, theme_display_name):
        theme_key = None
        current_lang_code = self.current_lang.get()

        for lang_key, name in LANG_STRINGS[current_lang_code].items():
            if name == theme_display_name and lang_key.startswith("theme_"):
                for en_name in THEMES.keys():
                    internal_theme_key = "theme_" + en_name.lower().replace(" ", "_").replace("і", "i").replace("ї",
                                                                                                                "i")
                    if lang_key.replace("_", "") == internal_theme_key.replace("_", ""):
                        theme_key = en_name
                        break
                break

        if not theme_key and theme_display_name in THEMES:
            theme_key = theme_display_name

        palette = THEMES.get(theme_key)

        if palette:
            self.apply_theme(palette)
            print(f"Applied theme: {theme_key}")
        else:
            print(f"Error: Theme '{theme_display_name}' (mapped to '{theme_key}') not found in THEMES dictionary.")
            self.apply_theme(THEMES["Нічна Прохолода"])
            self.settings_theme_menu.set(LANG_STRINGS[current_lang_code]["theme_night_cool"])

    def apply_theme(self, palette):
        app_bg = palette['app_bg']
        frame_bg = palette['frame_bg']
        button_fg = palette['button_fg']
        text_color = palette['text_color']
        hover_color = palette['hover_color']

        button_text_color = "#EAEAEA" if palette["type"] == "dark" else "#333333"
        if palette["type"] == "light" and button_fg == "#98FB98":
            button_text_color = "#2F4F4F"
        elif palette["type"] == "light" and button_fg == "#ADD8E6":
            button_text_color = "#333333"

        self.configure(fg_color=app_bg)

        for widget in self.all_widgets:
            if not widget or not widget.winfo_exists():
                continue
            if not getattr(widget, 'is_themeable', True):
                continue

            widget_type = type(widget)

            try:
                if widget_type == ctk.CTkFrame:
                    if str(widget.cget("fg_color")) != "transparent":
                        widget.configure(fg_color=frame_bg)
                elif widget_type == ctk.CTkButton:
                    if widget is not self.self_destruct_btn:
                        widget.configure(fg_color=button_fg, text_color=button_text_color, hover_color=hover_color)
                    else:
                        widget.configure(text_color="white")
                elif widget_type == ctk.CTkLabel:
                    current_text_color_obj = widget.cget("text_color")
                    is_status_color = False
                    if isinstance(current_text_color_obj, str):
                        current_text_color = current_text_color_obj.lower()
                        if any(color in current_text_color for color in ["yellow", "red", "green", "orange", "gray"]):
                            is_status_color = True

                    if not is_status_color:
                        widget.configure(text_color=text_color)
                elif widget_type == ctk.CTkTextbox:
                    widget.configure(fg_color=frame_bg, text_color=text_color, border_color=hover_color)
                elif widget_type == ctk.CTkEntry:
                    widget.configure(fg_color=frame_bg, text_color=text_color, border_color=hover_color)
                elif widget_type == ctk.CTkOptionMenu:
                    widget.configure(fg_color=button_fg, button_color=button_fg, button_hover_color=hover_color,
                                     text_color=button_text_color, dropdown_fg_color=frame_bg,
                                     dropdown_hover_color=hover_color, dropdown_text_color=text_color)
                elif widget_type == ctk.CTkSegmentedButton:
                    widget.configure(fg_color=frame_bg, selected_color=button_fg, selected_hover_color=hover_color,
                                     unselected_color=frame_bg, unselected_hover_color=hover_color,
                                     text_color=text_color)
                elif widget_type == ctk.CTkProgressBar:
                    if widget is not self.self_destruct_progress:
                        widget.configure(progress_color=button_fg, fg_color=frame_bg)

            except Exception as e:
                print(f"Minor error applying theme to {widget} ({widget_type}): {e}")

        self.update_idletasks()

    def update_theme_menu_default(self):
        if hasattr(self, 'settings_theme_menu'):
            default_theme_name = LANG_STRINGS[self.current_lang.get()]["theme_night_cool"]
            self.settings_theme_menu.set(default_theme_name)

    def _get_current_color_theme_name(self):
        return "blue"

    def change_language(self, *args):
        lang_code = self.current_lang.get()
        self.update_all_texts(lang_code)

    def update_vigenere_labels(self, selected_mode=None):
        lang = LANG_STRINGS[self.current_lang.get()]
        if selected_mode is None:
            selected_mode = self.vigenere_mode.get()

        mode_values = [lang["vigenere_mode_encrypt"], lang["vigenere_mode_decrypt"]]
        if hasattr(self, 'vigenere_mode_selector') and self.vigenere_mode_selector.winfo_exists():
            self.vigenere_mode_selector.configure(values=mode_values)
            if selected_mode not in mode_values:
                current_mode_index = 1
                self.vigenere_mode.set(mode_values[current_mode_index])
                selected_mode = mode_values[current_mode_index]

            if selected_mode == lang["vigenere_mode_encrypt"]:
                self.vigenere_input_label.configure(text=lang["vigenere_input_label_encrypt"])
                self.vigenere_run_btn.configure(text=lang["vigenere_run_encrypt"])
                self.vigenere_output_label.configure(text=lang["vigenere_output_label_encrypt"])
            else:
                self.vigenere_input_label.configure(text=lang["vigenere_input_label_decrypt"])
                self.vigenere_run_btn.configure(text=lang["vigenere_run_decrypt"])
                self.vigenere_output_label.configure(text=lang["vigenere_output_label_decrypt"])

    def update_base64_labels(self, selected_mode=None):
        lang = LANG_STRINGS[self.current_lang.get()]
        if selected_mode is None:
            selected_mode = self.base64_mode.get()

        mode_values = [lang["base64_mode_encode"], lang["base64_mode_decode"]]
        if hasattr(self, 'base64_mode_selector') and self.base64_mode_selector.winfo_exists():
            self.base64_mode_selector.configure(values=mode_values)
            if selected_mode not in mode_values:
                current_mode_index = 0
                self.base64_mode.set(mode_values[current_mode_index])
                selected_mode = mode_values[current_mode_index]

            if selected_mode == lang["base64_mode_encode"]:
                self.base64_input_label.configure(text=lang["base64_input_label_encode"])
                self.base64_run_btn.configure(text=lang["base64_run_encode"])
                self.base64_output_label.configure(text=lang["base64_output_label_encode"])
            else:
                self.base64_input_label.configure(text=lang["base64_input_label_decode"])
                self.base64_run_btn.configure(text=lang["base64_run_decode"])
                self.base64_output_label.configure(text=lang["base64_output_label_decode"])

    def update_all_texts(self, lang_code):
        lang = LANG_STRINGS.get(lang_code, LANG_STRINGS["ua"])

        self.title(lang["title"])

        self.theme_name_map = {
            LANG_STRINGS["ua"]["theme_night_cool"]: THEMES["Нічна Прохолода"],
            LANG_STRINGS["en"]["theme_night_cool"]: THEMES["Нічна Прохолода"],
            LANG_STRINGS["ua"]["theme_forest_calm"]: THEMES["Лісовий Спокій"],
            LANG_STRINGS["en"]["theme_forest_calm"]: THEMES["Лісовий Спокій"],
            LANG_STRINGS["ua"]["theme_ocean_depth"]: THEMES["Океанська Глибина"],
            LANG_STRINGS["en"]["theme_ocean_depth"]: THEMES["Океанська Глибина"],
            LANG_STRINGS["ua"]["theme_sunrise"]: THEMES["Світанок"],
            LANG_STRINGS["en"]["theme_sunrise"]: THEMES["Світанок"],
            LANG_STRINGS["ua"]["theme_coffee"]: THEMES["Кава з Молоком"],
            LANG_STRINGS["en"]["theme_coffee"]: THEMES["Кава з Молоком"],
            LANG_STRINGS["ua"]["theme_spring_meadow"]: THEMES["Весняний Луг"],
            LANG_STRINGS["en"]["theme_spring_meadow"]: THEMES["Весняний Луг"],
        }

        theme_display_names = [
            lang.get("theme_night_cool", "Night Cool"), lang.get("theme_forest_calm", "Forest Calm"),
            lang.get("theme_ocean_depth", "Ocean Depth"),
            lang.get("theme_sunrise", "Sunrise"), lang.get("theme_coffee", "Coffee Milk"),
            lang.get("theme_spring_meadow", "Spring Meadow")
        ]

        if hasattr(self, 'settings_theme_menu'):
            current_theme_display_name = self.settings_theme_menu.get()
            current_palette = None

            for name, palette in self.theme_name_map.items():
                if name == current_theme_display_name:
                    current_palette = palette
                    break
            if not current_palette:
                for theme_key in THEMES.keys():
                    if theme_key == current_theme_display_name:
                        current_palette = THEMES[theme_key]
                        break

            self.settings_theme_menu.configure(values=theme_display_names)

            new_display_name = None
            if current_palette:
                for name_key, palette_val in THEMES.items():
                    if palette_val == current_palette:
                        lang_key = None
                        for code in LANG_STRINGS:
                            for key, value in LANG_STRINGS[code].items():
                                if value == name_key and key.startswith("theme_"):
                                    lang_key = key
                                    break
                            if lang_key:
                                break
                        if lang_key:
                            new_display_name = lang.get(lang_key)
                        break

            if new_display_name and new_display_name in theme_display_names:
                self.settings_theme_menu.set(new_display_name)
            else:
                self.settings_theme_menu.set(theme_display_names[0])

        if hasattr(self, 'app_logo_label'):
            if self.logo_image is None:
                self.app_logo_label.configure(text=lang.get("app_logo_text", "🔒")) 

        if hasattr(self, 'xor_button'): self.xor_button.configure(text=lang["nav_xor"])
        if hasattr(self, 'lsb_button'): self.lsb_button.configure(text=lang["nav_lsb"])
        if hasattr(self, 'picker_button'): self.picker_button.configure(text=lang["nav_picker"])
        if hasattr(self, 'vigenere_button'): self.vigenere_button.configure(text=lang["nav_vigenere"])
        if hasattr(self, 'base64_button'): self.base64_button.configure(text=lang["nav_base64"])
        if hasattr(self, 'ela_button'): self.ela_button.configure(text=lang["nav_ela"])
        if hasattr(self, 'settings_button'): self.settings_button.configure(text=lang["nav_settings"])
        if hasattr(self, 'about_button'): self.about_button.configure(text=lang["nav_about"])

        if hasattr(self, 'xor_title'): self.xor_title.configure(text=lang["xor_title"])
        if hasattr(self, 'xor_label1') and (not hasattr(self.xor_label1, 'image') or self.xor_label1.image is None):
            self.xor_label1.configure(text=lang["xor_img1_text"])
        if hasattr(self, 'xor_label2') and (not hasattr(self.xor_label2, 'image') or self.xor_label2.image is None):
            self.xor_label2.configure(text=lang["xor_img2_text"])
        if hasattr(self, 'xor_load_btn1'): self.xor_load_btn1.configure(text=lang["xor_load1"])
        if hasattr(self, 'xor_load_btn2'): self.xor_load_btn2.configure(text=lang["xor_load2"])
        if hasattr(self, 'xor_run_btn'): self.xor_run_btn.configure(text=lang["xor_run"])
        if hasattr(self, 'xor_result_label') and (
                not hasattr(self.xor_result_label, 'image') or self.xor_result_label.image is None):
            self.xor_result_label.configure(text=lang["xor_result_text"])

        if hasattr(self, 'lsb_title'): self.lsb_title.configure(text=lang["lsb_title"])
        if hasattr(self, 'lsb_load_btn'): self.lsb_load_btn.configure(text=lang["lsb_load"])
        if hasattr(self, 'lsb_run_btn'): self.lsb_run_btn.configure(text=lang["lsb_run"])
        if hasattr(self, 'lsb_original_label') and (
                not hasattr(self.lsb_original_label, 'image') or self.lsb_original_label.image is None):
            self.lsb_original_label.configure(text=lang["lsb_original_text"])
        if hasattr(self, 'lsb_result_label') and (
                not hasattr(self.lsb_result_label, 'image') or self.lsb_result_label.image is None):
            self.lsb_result_label.configure(text=lang["lsb_result_text"])
        if hasattr(self, 'lsb_decoded_text_label'): self.lsb_decoded_text_label.configure(
            text=lang["lsb_decoded_text_label"])

        if hasattr(self, 'picker_title'): self.picker_title.configure(text=lang["picker_title"])
        if hasattr(self, 'picker_load_btn'): self.picker_load_btn.configure(text=lang["picker_load"])
        if hasattr(self, 'picker_image_label') and (
                not hasattr(self.picker_image_label, 'image') or self.picker_image_label.image is None):
            self.picker_image_label.configure(text=lang["picker_img_text"])
        if hasattr(self, 'picker_hex_label'): self.picker_hex_label.configure(text=lang["picker_hex_default"])
        if hasattr(self, 'picker_last_text_label'): self.picker_last_text_label.configure(
            text=lang["picker_text_default"])
        if hasattr(self, 'picker_clear_btn'): self.picker_clear_btn.configure(text=lang["picker_clear"])
        if hasattr(self, 'picker_status_label'): self.picker_status_label.configure(text=lang["picker_status_default"])

        if hasattr(self, 'vigenere_title'): self.vigenere_title.configure(text=lang["vigenere_title"])
        if hasattr(self, 'vigenere_key_label'): self.vigenere_key_label.configure(text=lang["vigenere_key_label"])
        if hasattr(self, 'vigenere_mode_selector'): self.update_vigenere_labels()

        if hasattr(self, 'base64_title'): self.base64_title.configure(text=lang["base64_title"])
        if hasattr(self, 'base64_mode_selector'): self.update_base64_labels()

        if hasattr(self, 'ela_title'): self.ela_title.configure(text=lang["ela_title"])
        if hasattr(self, 'ela_load_btn'): self.ela_load_btn.configure(text=lang["ela_load"])
        if hasattr(self, 'ela_quality_label'): self.ela_quality_label.configure(text=lang["ela_quality_label"])
        if hasattr(self, 'ela_scale_label'): self.ela_scale_label.configure(text=lang["ela_scale_label"])
        if hasattr(self, 'ela_run_btn'): self.ela_run_btn.configure(text=lang["ela_run"])
        if hasattr(self, 'ela_original_label') and (
                not hasattr(self.ela_original_label, 'image') or self.ela_original_label.image is None):
            self.ela_original_label.configure(text=lang["ela_original_text"])
        if hasattr(self, 'ela_result_label') and (
                not hasattr(self.ela_result_label, 'image') or self.ela_result_label.image is None):
            self.ela_result_label.configure(text=lang["ela_result_text"])

        if hasattr(self, 'settings_title'): self.settings_title.configure(text=lang["settings_title"])
        if hasattr(self, 'settings_lang_label'): self.settings_lang_label.configure(text=lang["settings_lang"])
        if hasattr(self, 'settings_theme_label'): self.settings_theme_label.configure(text=lang["settings_theme"])
        if hasattr(self, 'settings_danger_label'): self.settings_danger_label.configure(
            text=lang["settings_danger_zone"])
        if hasattr(self, 'self_destruct_btn') and self.self_destruct_btn.winfo_exists() and self.self_destruct_btn.cget(
                'state') == tk.NORMAL:
            self.self_destruct_btn.configure(text=lang["settings_self_destruct"])

        if hasattr(self, 'about_title'): self.about_title.configure(text=lang["about_title"])
        if hasattr(self, 'about_text_label'): self.about_text_label.configure(text=lang["about_text"])
        if hasattr(self, 'about_links_label'): self.about_links_label.configure(text=lang["about_links_label"])

    def find_theme_name_in_lang(self, current_display_name, target_lang_code):
        original_key = None
        for lang in LANG_STRINGS.values():
            for key, display_name in lang.items():
                if display_name == current_display_name and key.startswith("theme_"):
                    original_key = key
                    break
            if original_key:
                break
        if original_key:
            return LANG_STRINGS.get(target_lang_code, {}).get(original_key, None)
        return None

    def hide_all_frames(self):
        self.xor_frame.grid_forget()
        self.lsb_frame.grid_forget()
        self.picker_frame.grid_forget()
        self.vigenere_frame.grid_forget()
        self.base64_frame.grid_forget()
        self.ela_frame.grid_forget()
        self.settings_frame.grid_forget()
        self.about_frame.grid_forget()

    def show_xor_frame(self):
        self.hide_all_frames()
        self.xor_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

    def show_lsb_frame(self):
        self.hide_all_frames()
        self.lsb_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

    def show_picker_frame(self):
        self.hide_all_frames()
        self.picker_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

    def show_vigenere_frame(self):
        self.hide_all_frames()
        self.vigenere_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

    def show_base64_frame(self):
        self.hide_all_frames()
        self.base64_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

    def show_ela_frame(self):
        self.hide_all_frames()
        self.ela_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

    def show_settings_frame(self):
        self.hide_all_frames()
        self.settings_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

    def show_about_frame(self):
        self.hide_all_frames()
        self.about_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

    def load_xor_image1(self):
        path = filedialog.askopenfilename(filetypes=[("Зображення", "*.png *.jpg *.bmp")])
        if not path: return
        self.xor_image_path1 = path
        self.show_image_on_label(path, self.xor_label1, (300, 300))
        self.xor_status_label.configure(text="")

    def load_xor_image2(self):
        path = filedialog.askopenfilename(filetypes=[("Зображення", "*.png *.jpg *.bmp")])
        if not path: return
        self.xor_image_path2 = path
        self.show_image_on_label(path, self.xor_label2, (300, 300))
        self.xor_status_label.configure(text="")

    def perform_xor(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        if not self.xor_image_path1 or not self.xor_image_path2:
            self.xor_status_label.configure(text=lang["xor_status_error_load"], text_color="red")
            return

        self.xor_status_label.configure(text=lang["xor_status_processing"], text_color="yellow")
        self.update_idletasks()
        try:
            result_pil = self.xor_images(self.xor_image_path1, self.xor_image_path2)
            self.show_pil_image_on_label(result_pil, self.xor_result_label, (300, 300))
            if lang["xor_status_warn_resize"] not in self.xor_status_label.cget("text"):
                self.xor_status_label.configure(text=lang["xor_status_ok"], text_color="green")
        except Exception as e:
            self.xor_status_label.configure(text=f"Error: {e}", text_color="red")

    def load_lsb_image(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        path = filedialog.askopenfilename(filetypes=[("Зображення (PNG/BMP)", "*.png *.bmp"), ("Всі файли", "*.*")])
        if not path: return

        self.lsb_image_path = path
        self.show_image_on_label(path, self.lsb_original_label, (350, 250))
        self.lsb_text_result.delete("1.0", "end")

        if not path.lower().endswith((".png", ".bmp")):
            self.lsb_status_label.configure(text=lang["lsb_status_warn_format"], text_color="orange")
        else:
            self.lsb_status_label.configure(text=lang["lsb_status_ok_load"], text_color="gray")

        try:
            result_pil_img = self.extract_lsb_image(self.lsb_image_path)
            if result_pil_img:
                self.show_pil_image_on_label(result_pil_img, self.lsb_result_label, (350, 250))
        except Exception:
            self.lsb_result_label.configure(image=None, text=lang["lsb_result_text"])
            self.lsb_result_label.image = None

    def perform_lsb_extraction(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        if not self.lsb_image_path:
            self.lsb_status_label.configure(text=lang["lsb_status_error_load"], text_color="red")
            return

        self.lsb_status_label.configure(text=lang["lsb_status_processing"], text_color="yellow")
        self.update_idletasks()
        self.lsb_text_result.delete("1.0", "end")

        try:
            text_msg = self.extract_lsb_text_base64_V10(self.lsb_image_path)
            self.lsb_text_result.insert("1.0", text_msg)

            if lang["lsb_status_warn_format"] not in self.lsb_status_label.cget("text"):
                self.lsb_status_label.configure(text=lang["lsb_status_ok"], text_color="green")

        except Exception as e:
            self.lsb_text_result.insert("1.0", lang["lsb_error_general"].format(e=e))
            self.lsb_status_label.configure(text=lang["lsb_error_general"].format(e=e), text_color="red")

    def load_picker_image(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        path = filedialog.askopenfilename(filetypes=[("Зображення", "*.png *.jpg *.bmp")])
        if not path: return
        try:
            self.picker_pil_image = Image.open(path).convert('RGB')
            self.draw_picker_grid()
            self.picker_status_label.configure(text=lang["picker_status_default"])
            self.clear_picker_text()
        except Exception as e:
            self.picker_status_label.configure(text=f"Error loading: {e}", text_color="red")

    def draw_picker_grid(self):
        if not self.picker_pil_image: return
        img_with_grid = self.picker_pil_image.copy()
        draw = ImageDraw.Draw(img_with_grid)
        w, h = img_with_grid.size
        if w > 2000 or h > 2000:
            self.show_pil_image_on_label(self.picker_pil_image, self.picker_image_label, (700, 500), keep_aspect=True)
            return

        for i in range(0, w, 10):
            draw.line([(i, 0), (i, h)], fill=(128, 128, 128, 100), width=1)
        for i in range(0, h, 10):
            draw.line([(0, i), (w, i)], fill=(128, 128, 128, 100), width=1)
        self.show_pil_image_on_label(img_with_grid, self.picker_image_label, (700, 500), keep_aspect=True)

    def on_image_click(self, event):
        lang = LANG_STRINGS[self.current_lang.get()]
        if not self.picker_pil_image:
            self.picker_status_label.configure(text=lang["picker_status_error_load"], text_color="yellow")
            return
        try:
            current_image = self.picker_image_label.cget("image")
            if not current_image or not hasattr(current_image, "cget"): return

            ctk_img_w, ctk_img_h = current_image.cget("size")
            if ctk_img_w == 0 or ctk_img_h == 0: return

            pil_img_w, pil_img_h = self.picker_pil_image.size

            w_ratio = pil_img_w / ctk_img_w
            h_ratio = pil_img_h / ctk_img_h
            pil_x = int(event.x * w_ratio)
            pil_y = int(event.y * h_ratio)

            if not (0 <= pil_x < pil_img_w and 0 <= pil_y < pil_img_h): return

            r, g, b = self.picker_pil_image.getpixel((pil_x, pil_y))
            hex_code = f"#{r:02x}{g:02x}{b:02x}".upper()
            text_result = self.hex_color_to_text(hex_code)

            self.picker_hex_label.configure(text=f"Hex: {hex_code}")
            label_part = lang['picker_text_default'].split(':')[0]
            self.picker_last_text_label.configure(text=f"{label_part}: {text_result}")
            self.picker_status_label.configure(text=f"Coords: (x:{pil_x}, y:{pil_y})")
            if text_result:
                self.picker_accumulated_text.insert("end", text_result)
        except Exception as e:
            self.picker_status_label.configure(text=f"Error: {e}", text_color="red")

    def clear_picker_text(self):
        self.picker_accumulated_text.delete("1.0", "end")

    def perform_vigenere_operation(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        mode = self.vigenere_mode.get()
        input_text = self.vigenere_input_textbox.get("1.0", tk.END).strip()
        key = self.vigenere_key_entry.get().strip()

        if not input_text or not key:
            self.vigenere_status_label.configure(text=lang["vigenere_status_error_input"], text_color="red")
            return

        if not key.isalpha():
            self.vigenere_status_label.configure(text=lang["vigenere_status_error_key"], text_color="red")
            return

        try:
            result_text = ""
            status_ok_msg = ""
            if mode == lang["vigenere_mode_encrypt"]:
                result_text = self.vigenere_encrypt(input_text, key)
                status_ok_msg = lang["vigenere_status_ok_encrypt"]
            else:
                result_text = self.vigenere_decrypt(input_text, key)
                status_ok_msg = lang["vigenere_status_ok_decrypt"]

            self.vigenere_output_textbox.delete("1.0", tk.END)
            self.vigenere_output_textbox.insert("1.0", result_text)
            self.vigenere_status_label.configure(text=status_ok_msg, text_color="green")
        except Exception as e:
            self.vigenere_status_label.configure(text=f"Error: {e}", text_color="red")

    def perform_base64_operation(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        mode = self.base64_mode.get()
        input_text = self.base64_input_textbox.get("1.0", tk.END).strip()

        if not input_text:
            self.base64_status_label.configure(text=lang["base64_status_error_input"], text_color="red")
            return

        self.base64_output_textbox.delete("1.0", tk.END)
        try:
            result_text = ""
            status_ok_msg = ""
            if mode == lang["base64_mode_encode"]:
                result_text = base64.b64encode(input_text.encode('utf-8')).decode('utf-8')
                status_ok_msg = lang["base64_status_ok_encode"]
            else:
                missing_padding = len(input_text) % 4
                if missing_padding:
                    input_text += '=' * (4 - missing_padding)
                result_text = base64.b64decode(input_text.encode('utf-8')).decode('utf-8')
                status_ok_msg = lang["base64_status_ok_decode"]

            self.base64_output_textbox.insert("1.0", result_text)
            self.base64_status_label.configure(text=status_ok_msg, text_color="green")

        except (base64.binascii.Error, UnicodeDecodeError) as e:
            self.base64_status_label.configure(text=lang["base64_status_error_decode"], text_color="red")
            print(f"Base64 Error: {e}")
        except Exception as e:
            self.base64_status_label.configure(text=f"Error: {e}", text_color="red")

    def load_ela_image(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        path = filedialog.askopenfilename(filetypes=[("Зображення", "*.png *.jpg *.jpeg *.bmp *.tiff")])
        if not path: return

        self.ela_image_path = path
        self.show_image_on_label(path, self.ela_original_label, (350, 300), keep_aspect=True)
        self.ela_result_label.configure(image=None, text=lang["ela_result_text"])
        self.ela_result_label.image = None
        self.ela_status_label.configure(text="")

    def run_ela_analysis(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        if not self.ela_image_path:
            self.ela_status_label.configure(text=lang["ela_status_error_load"], text_color="red")
            return

        try:
            quality = int(self.ela_quality_entry.get())
            scale = int(self.ela_scale_entry.get())
            if not (1 <= quality <= 100 and scale > 0):
                raise ValueError("Invalid parameters")
        except ValueError:
            self.ela_status_label.configure(text=lang["ela_status_error_params"], text_color="red")
            return

        self.ela_status_label.configure(text=lang["ela_status_processing"], text_color="yellow")
        self.update_idletasks()

        try:
            ela_result_img = self.perform_ela(self.ela_image_path, quality, scale)
            if ela_result_img:
                self.show_pil_image_on_label(ela_result_img, self.ela_result_label, (350, 300), keep_aspect=True)
                self.ela_status_label.configure(text=lang["ela_status_ok"], text_color="green")
            else:
                self.ela_result_label.configure(image=None, text=lang["ela_result_text"])
                self.ela_result_label.image = None
                self.ela_status_label.configure(text="ELA Error", text_color="red")
        except Exception as e:
            self.ela_result_label.configure(image=None, text=lang["ela_result_text"])
            self.ela_result_label.image = None
            self.ela_status_label.configure(text=f"Error: {e}", text_color="red")
            print(f"ELA Error: {e}")

    def self_destruct(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        self.self_destruct_btn.configure(state="disabled", text=lang["settings_self_destruct_run"])
        self.self_destruct_progress.set(0)

        def update_progress(val):
            if val > 1.0:
                self.self_destruct_progress.set(0)
                self.self_destruct_btn.configure(state="normal", text=lang["settings_self_destruct"])
                msg_box = ctk.CTkToplevel(self)
                msg_box.attributes("-topmost", True)
                msg_box.title(" ")
                msg_box.geometry("300x150")
                msg_box.grab_set()
                ctk.CTkLabel(msg_box, text=lang["settings_self_destruct_prank"],
                             font=("Arial", 18)).pack(expand=True, padx=20, pady=20)
                self.center_window(msg_box, 300, 150)
                msg_box.after(2000, msg_box.destroy)
                return
            self.self_destruct_progress.set(val)
            self.after(15, update_progress, val + 0.01)

        update_progress(0.01)

    def center_window(self, window, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def xor_images(self, image_path1, image_path2):
        lang = LANG_STRINGS[self.current_lang.get()]
        img1 = Image.open(image_path1).convert('RGB')
        img2 = Image.open(image_path2).convert('RGB')

        if img1.size != img2.size:
            self.xor_status_label.configure(text=lang["xor_status_warn_resize"], text_color="orange")
            img2 = img2.resize(img1.size, Image.Resampling.NEAREST)

        result_img = Image.new('RGB', img1.size)
        pixels1 = img1.load()
        pixels2 = img2.load()
        result_pixels = result_img.load()

        for y in range(img1.height):
            for x in range(img1.width):
                r1, g1, b1 = pixels1[x, y]
                r2, g2, b2 = pixels2[x, y]
                result_pixels[x, y] = (r1 ^ r2, g1 ^ g2, b1 ^ b2)

        return result_img

    def extract_lsb_image(self, container_image_path):
        try:
            container_img = Image.open(container_image_path).convert('RGB')
            pixels = container_img.load()
            hidden_img = Image.new('RGB', container_img.size)
            hidden_pixels = hidden_img.load()

            for y in range(container_img.height):
                for x in range(container_img.width):
                    r, g, b = pixels[x, y]
                    hidden_pixels[x, y] = ((r & 1) * 255, (g & 1) * 255, (b & 1) * 255)
            return hidden_img
        except Exception as e:
            print(f"Error extracting LSB image: {e}")
            return None

    def hex_color_to_text(self, hex_code):
        try:
            hex_val = hex_code.lstrip('#')
            r_int, g_int, b_int = int(hex_val[0:2], 16), int(hex_val[2:4], 16), int(hex_val[4:6], 16)
            r_char = chr(r_int) if chr(r_int).isprintable() else ''
            g_char = chr(g_int) if chr(g_int).isprintable() else ''
            b_char = chr(b_int) if chr(b_int).isprintable() else ''
            return f"{r_char}{g_char}{b_char}"
        except Exception:
            return ""

    def extract_lsb_text_base64_V10(self, image_path):
        lang = LANG_STRINGS[self.current_lang.get()]
        try:
            img = Image.open(image_path)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            pixels = img.load()
            width, height = img.size

            base64_string = ""
            current_byte = 0
            bit_count = 0

            for y in range(height):
                for x in range(width):
                    r, g, b, a = pixels[x, y]

                    pixel_bits = [r & 1, g & 1, b & 1]

                    for bit in pixel_bits:
                        current_byte |= (bit << bit_count)
                        bit_count += 1

                        if bit_count == 8:
                            char = chr(current_byte)
                            if char in VALID_BASE64_CHARS:
                                base64_string += char
                            else:
                                if len(base64_string) > 0:
                                    return self.decode_base64_string(base64_string)
                                else:
                                    return lang["lsb_error_base64"]

                            current_byte = 0
                            bit_count = 0

            if len(base64_string) > 0:
                return self.decode_base64_string(base64_string)

            return lang["lsb_error_eof"]

        except Exception as e:
            return lang["lsb_error_general"].format(e=e)

    def decode_base64_string(self, s):
        lang = LANG_STRINGS[self.current_lang.get()]
        try:
            padding = len(s) % 4
            if padding != 0:
                s += "=" * (4 - padding)

            decoded_bytes = base64.b64decode(s)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            return lang["lsb_error_decode"].format(e=e, s=s)

    def vigenere_process(self, text, key, mode='encrypt'):
        result = ""
        key_index = 0
        key = key.upper()
        alphabet = string.ascii_uppercase

        for char in text:
            if char.isalpha():
                char_upper = char.upper()
                text_pos = alphabet.find(char_upper)
                key_char = key[key_index % len(key)]
                key_pos = alphabet.find(key_char)

                if mode == 'encrypt':
                    result_pos = (text_pos + key_pos) % len(alphabet)
                else:
                    result_pos = (text_pos - key_pos + len(alphabet)) % len(alphabet)

                result_char = alphabet[result_pos]
                result += result_char if char.isupper() else result_char.lower()
                key_index += 1
            else:
                result += char
        return result

    def vigenere_encrypt(self, plaintext, key):
        return self.vigenere_process(plaintext, key, mode='encrypt')

    def vigenere_decrypt(self, ciphertext, key):
        return self.vigenere_process(ciphertext, key, mode='decrypt')

    def perform_ela(self, image_path, quality, scale):
        try:
            original = Image.open(image_path).convert('RGB')
            temp_buffer = io.BytesIO()
            original.save(temp_buffer, 'JPEG', quality=quality)
            temp_buffer.seek(0)
            resaved = Image.open(temp_buffer).convert('RGB')
            temp_buffer.close()

            diff = ImageChops.difference(original, resaved)

            pixels = diff.getdata()
            scaled_pixels = [tuple(min(p * scale, 255) for p in pixel) for pixel in pixels]

            ela_img = Image.new('RGB', diff.size)
            ela_img.putdata(scaled_pixels)

            return ela_img

        except Exception as e:
            print(f"Error during ELA: {e}")
            return None

    def show_pil_image_on_label(self, pil_img, label, size, keep_aspect=False):
        if not label or not label.winfo_exists():
            print("Label does not exist, cannot show image.")
            return

        if pil_img is None:
            label.configure(image=None, text="Error")
            label.image = None
            return
        try:
            display_size = size
            if keep_aspect:
                w, h = pil_img.size
                if w == 0 or h == 0: return
                max_w, max_h = size
                ratio = min(max_w / w, max_h / h) if w > 0 and h > 0 else 1
                display_size = (int(w * ratio), int(h * ratio))

            ctk_img = ctk.CTkImage(light_image=pil_img.copy(), size=display_size)
            label.configure(image=ctk_img, text="")
            label.image = ctk_img
        except Exception as e:
            label.configure(image=None, text=f"Error\n{e}")
            label.image = None

    def show_image_on_label(self, path, label, size, keep_aspect=False):
        if not label or not label.winfo_exists():
            print("Label does not exist, cannot show image.")
            return
        try:
            pil_img = Image.open(path)
            self.show_pil_image_on_label(pil_img, label, size, keep_aspect)
        except Exception as e:
            label.configure(image=None, text=f"Error\n{e}")
            label.image = None


if __name__ == "__main__":
    app = StegoApp()
    app.mainloop()
