import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import base64
import os
import webbrowser

APP_VERSION = "1.0.2"

LANG_STRINGS = {
    "ua": {
        "title": "ДЕКРИПТОІНАТОР 1000",
        "app_logo_text": "🔒",
        "nav_xor": "XOR Аналіз",
        "nav_lsb": "LSB Екстрактор",
        "nav_picker": "Color Picker",
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
        "lsb_run": "РОЗШИФРУВАТИ",
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
                      f"<<  Поки я не почитав ККУ - життя здавалось більш яскравішим >>\n\n"\
                      f"Версія: {APP_VERSION}",
        "about_links_label": "Посилання:",
        "error_icon_load_title": "Помилка іконки",
        "error_icon_load_msg": "Не вдалося завантажити файл іконки 'logo.png'.\nПеревірте, чи файл існує, чи це PNG, і чи він не пошкоджений.\nВикористовується стандартна іконка.",
        "theme_dark_blue": "Темно-синя",
        "theme_dark_green": "Темно-зелена",
        "theme_dark_darkblue": "Темно-темносиня",
        "theme_light_blue": "Світло-синя",
        "theme_light_green": "Світло-зелена",
        "theme_light_darkblue": "Світло-темносиня",
    },
    "en": {
        "title": "DECRYPTOINATOR 1000",
        "app_logo_text": "🔒",
        "nav_xor": "XOR Analysis",
        "nav_lsb": "LSB Extractor",
        "nav_picker": "Color Picker",
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
        "lsb_run": "DECRYPT",
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
                      f"Version: {APP_VERSION}", # Version added
        "about_links_label": "Links:",
        "error_icon_load_title": "Icon Error",
        "error_icon_load_msg": "Failed to load the icon file 'logo.png'.\nCheck if the file exists, is a valid PNG, and is not corrupted.\nUsing the default icon.",
        "theme_dark_blue": "Dark Blue",
        "theme_dark_green": "Dark Green",
        "theme_dark_darkblue": "Dark Dark-Blue",
        "theme_light_blue": "Light Blue",
        "theme_light_green": "Light Green",
        "theme_light_darkblue": "Light Dark-Blue",
    }
}

VALID_BASE64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="

class StegoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.current_lang = ctk.StringVar(value="ua")
        self.current_lang.trace_add("write", self.change_language)

        self.geometry("1100x700")
        self.title(LANG_STRINGS[self.current_lang.get()]["title"])

        self.xor_image_path1 = None
        self.xor_image_path2 = None
        self.lsb_image_path = None
        self.picker_pil_image = None

        self.all_widgets = []

        self.setup_window_icon()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_nav_frame()
        self.setup_content_frames()

        self.update_all_texts(self.current_lang.get())
        self.show_xor_frame()

    def _create_widget(self, widget_class, *args, **kwargs):
        widget = widget_class(*args, **kwargs)
        if isinstance(widget, (ctk.CTkFrame, ctk.CTkButton, ctk.CTkLabel, ctk.CTkOptionMenu, ctk.CTkTextbox, ctk.CTkProgressBar, ctk.CTkEntry)):
            self.all_widgets.append(widget)
        return widget

    def setup_window_icon(self):
        icon_path = "logo.png"
        if os.path.exists(icon_path):
            try:
                self.app_icon = tk.PhotoImage(file=icon_path)
                self.iconphoto(True, self.app_icon)
            except Exception as e:
                self.after(100, self.show_icon_error, e)
                print(f"Error loading icon '{icon_path}': {e}")
        else:
             print(f"Icon file 'logo.png' not found. Using default icon.")

    def show_icon_error(self, error_exception):
         lang_code = self.current_lang.get()
         lang = LANG_STRINGS.get(lang_code, LANG_STRINGS["ua"])
         messagebox.showerror(lang["error_icon_load_title"], f"{lang['error_icon_load_msg']}\n\nError: {error_exception}")

    def setup_nav_frame(self):
        self.nav_frame = self._create_widget(ctk.CTkFrame, self, width=180, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="nswe")

        self.app_logo_label = self._create_widget(ctk.CTkLabel, self.nav_frame, text="",
                                           font=ctk.CTkFont(size=40, weight="bold"))
        self.app_logo_label.grid(row=0, column=0, padx=20, pady=20)

        self.xor_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_xor_frame, anchor="w")
        self.xor_button.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        self.lsb_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_lsb_frame, anchor="w")
        self.lsb_button.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.picker_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_picker_frame, anchor="w")
        self.picker_button.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        self.nav_frame.grid_rowconfigure(4, weight=1)

        self.settings_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_settings_frame, anchor="w")
        self.settings_button.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        self.about_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_about_frame, anchor="w")
        self.about_button.grid(row=6, column=0, padx=20, pady=20, sticky="ew")

    def setup_content_frames(self):
        self.xor_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent")
        self.lsb_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent")
        self.picker_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent")
        self.settings_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent")
        self.about_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent")

        self.setup_xor_frame_widgets()
        self.setup_lsb_frame_widgets()
        self.setup_picker_frame_widgets()
        self.setup_settings_frame_widgets()
        self.setup_about_frame_widgets()

    def setup_xor_frame_widgets(self):
        self.xor_frame.grid_columnconfigure((0, 1), weight=1)
        self.xor_title = self._create_widget(ctk.CTkLabel, self.xor_frame, font=ctk.CTkFont(size=24, weight="bold"))
        self.xor_title.grid(row=0, column=0, columnspan=2, pady=20, padx=20)

        self.xor_label1 = self._create_widget(ctk.CTkLabel, self.xor_frame, width=300, height=300, fg_color="gray20", corner_radius=10, text="")
        self.xor_label1.grid(row=1, column=0, padx=20, pady=10, sticky="n")
        self.xor_load_btn1 = self._create_widget(ctk.CTkButton, self.xor_frame, command=self.load_xor_image1)
        self.xor_load_btn1.grid(row=2, column=0, padx=20, pady=10)

        self.xor_label2 = self._create_widget(ctk.CTkLabel, self.xor_frame, width=300, height=300, fg_color="gray20", corner_radius=10, text="")
        self.xor_label2.grid(row=1, column=1, padx=20, pady=10, sticky="n")
        self.xor_load_btn2 = self._create_widget(ctk.CTkButton, self.xor_frame, command=self.load_xor_image2)
        self.xor_load_btn2.grid(row=2, column=1, padx=20, pady=10)

        self.xor_run_btn = self._create_widget(ctk.CTkButton, self.xor_frame, command=self.perform_xor, font=ctk.CTkFont(size=16, weight="bold"))
        self.xor_run_btn.grid(row=3, column=0, columnspan=2, pady=20)

        self.xor_result_label = self._create_widget(ctk.CTkLabel, self.xor_frame, width=300, height=300, fg_color="gray25", corner_radius=10, text="")
        self.xor_result_label.grid(row=4, column=0, columnspan=2, pady=10)
        self.xor_status_label = self._create_widget(ctk.CTkLabel, self.xor_frame, text="", text_color="yellow")
        self.xor_status_label.grid(row=5, column=0, columnspan=2, pady=10)

    def setup_lsb_frame_widgets(self):
        self.lsb_frame.grid_columnconfigure(0, weight=1)
        self.lsb_frame.grid_rowconfigure(4, weight=1)

        self.lsb_title = self._create_widget(ctk.CTkLabel, self.lsb_frame, font=ctk.CTkFont(size=24, weight="bold"))
        self.lsb_title.grid(row=0, column=0, pady=20, padx=20)

        controls_frame = self._create_widget(ctk.CTkFrame, self.lsb_frame)
        controls_frame.grid(row=1, column=0, pady=10, padx=20)

        self.lsb_load_btn = self._create_widget(ctk.CTkButton, controls_frame, command=self.load_lsb_image)
        self.lsb_load_btn.grid(row=0, column=0, padx=10, pady=10)

        self.lsb_run_btn = self._create_widget(ctk.CTkButton, controls_frame, command=self.perform_lsb_extraction, font=ctk.CTkFont(size=16, weight="bold"))
        self.lsb_run_btn.grid(row=0, column=1, padx=10, pady=10)

        img_frame = self._create_widget(ctk.CTkFrame, self.lsb_frame, fg_color="transparent")
        img_frame.grid(row=2, column=0, pady=10, padx=20, sticky="ew")
        img_frame.grid_columnconfigure((0, 1), weight=1)

        self.lsb_original_label = self._create_widget(ctk.CTkLabel, img_frame, width=350, height=250, fg_color="gray20", corner_radius=10, text="")
        self.lsb_original_label.grid(row=0, column=0, pady=10, padx=10)

        self.lsb_result_label = self._create_widget(ctk.CTkLabel, img_frame, width=350, height=250, fg_color="gray25", corner_radius=10, text="")
        self.lsb_result_label.grid(row=0, column=1, pady=10, padx=10)

        self.lsb_decoded_text_label = self._create_widget(ctk.CTkLabel, self.lsb_frame, font=ctk.CTkFont(size=16))
        self.lsb_decoded_text_label.grid(row=3, column=0, pady=(10, 0), sticky="s")

        self.lsb_text_result = self._create_widget(ctk.CTkTextbox, self.lsb_frame, height=100, font=("Consolas", 14))
        self.lsb_text_result.grid(row=4, column=0, pady=10, padx=20, sticky="nsew")

        self.lsb_status_label = self._create_widget(ctk.CTkLabel, self.lsb_frame, text="", text_color="yellow")
        self.lsb_status_label.grid(row=5, column=0, pady=10)

    def setup_picker_frame_widgets(self):
        self.picker_frame.grid_columnconfigure(0, weight=1)
        self.picker_frame.grid_rowconfigure(2, weight=1)
        self.picker_frame.grid_rowconfigure(4, weight=1)

        self.picker_title = self._create_widget(ctk.CTkLabel, self.picker_frame, font=ctk.CTkFont(size=24, weight="bold"))
        self.picker_title.grid(row=0, column=0, pady=20, padx=20)

        self.picker_load_btn = self._create_widget(ctk.CTkButton, self.picker_frame, command=self.load_picker_image)
        self.picker_load_btn.grid(row=1, column=0, pady=10)

        self.picker_image_label = self._create_widget(ctk.CTkLabel, self.picker_frame, fg_color="gray20", corner_radius=10, text="")
        self.picker_image_label.grid(row=2, column=0, pady=10, padx=20, sticky="nswe")
        self.picker_image_label.bind("<Button-1>", self.on_image_click)

        result_frame = self._create_widget(ctk.CTkFrame, self.picker_frame)
        result_frame.grid(row=3, column=0, pady=10)
        self.picker_hex_label = self._create_widget(ctk.CTkLabel, result_frame, font=ctk.CTkFont(size=16, family="Consolas"))
        self.picker_hex_label.grid(row=0, column=0, padx=20, pady=5)
        self.picker_last_text_label = self._create_widget(ctk.CTkLabel, result_frame, font=ctk.CTkFont(size=16, family="Consolas"))
        self.picker_last_text_label.grid(row=0, column=1, padx=20, pady=5)

        self.picker_accumulated_text = self._create_widget(ctk.CTkTextbox, self.picker_frame, height=100, font=("Consolas", 14))
        self.picker_accumulated_text.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 10))
        self.picker_clear_btn = self._create_widget(ctk.CTkButton, self.picker_frame, command=self.clear_picker_text)
        self.picker_clear_btn.grid(row=5, column=0, pady=5)

        self.picker_status_label = self._create_widget(ctk.CTkLabel, self.picker_frame, text_color="gray")
        self.picker_status_label.grid(row=6, column=0, pady=10)

    def setup_settings_frame_widgets(self):
        self.settings_frame.grid_columnconfigure(0, weight=1)
        self.settings_title = self._create_widget(ctk.CTkLabel, self.settings_frame, font=ctk.CTkFont(size=24, weight="bold"))
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

        lang_code = self.current_lang.get()
        theme_display_names = [
            LANG_STRINGS[lang_code]["theme_dark_blue"], LANG_STRINGS[lang_code]["theme_dark_green"], LANG_STRINGS[lang_code]["theme_dark_darkblue"],
            LANG_STRINGS[lang_code]["theme_light_blue"], LANG_STRINGS[lang_code]["theme_light_green"], LANG_STRINGS[lang_code]["theme_light_darkblue"]
        ]
        self.theme_name_map = {
            LANG_STRINGS["ua"]["theme_dark_blue"]: ("Dark", "blue"), LANG_STRINGS["en"]["theme_dark_blue"]: ("Dark", "blue"),
            LANG_STRINGS["ua"]["theme_dark_green"]: ("Dark", "green"), LANG_STRINGS["en"]["theme_dark_green"]: ("Dark", "green"),
            LANG_STRINGS["ua"]["theme_dark_darkblue"]: ("Dark", "dark-blue"), LANG_STRINGS["en"]["theme_dark_darkblue"]: ("Dark", "dark-blue"),
            LANG_STRINGS["ua"]["theme_light_blue"]: ("Light", "blue"), LANG_STRINGS["en"]["theme_light_blue"]: ("Light", "blue"),
            LANG_STRINGS["ua"]["theme_light_green"]: ("Light", "green"), LANG_STRINGS["en"]["theme_light_green"]: ("Light", "green"),
            LANG_STRINGS["ua"]["theme_light_darkblue"]: ("Light", "dark-blue"), LANG_STRINGS["en"]["theme_light_darkblue"]: ("Light", "dark-blue"),
        }

        self.settings_theme_menu = self._create_widget(ctk.CTkOptionMenu, theme_frame, values=theme_display_names,
                                                     command=self.apply_combined_theme_from_name)
        self.settings_theme_menu.grid(row=0, column=1, padx=10, pady=5)
        self.update_theme_menu_default()


        self.settings_danger_label = self._create_widget(ctk.CTkLabel, self.settings_frame, font=ctk.CTkFont(size=16, weight="bold"))
        self.settings_danger_label.grid(row=9, column=0, pady=(50, 10))

        self.self_destruct_btn = self._create_widget(ctk.CTkButton, self.settings_frame,
                                               fg_color="red", hover_color="darkred",
                                               command=self.self_destruct)
        self.self_destruct_btn.grid(row=10, column=0, pady=10, padx=50, sticky="ew")

        self.self_destruct_progress = self._create_widget(ctk.CTkProgressBar, self.settings_frame, fg_color="gray20",
                                                         progress_color="red")
        self.self_destruct_progress.set(0)
        self.self_destruct_progress.grid(row=11, column=0, padx=50, pady=(0, 20), sticky="ew")

    def setup_about_frame_widgets(self):
        self.about_frame.grid_columnconfigure(0, weight=1)
        self.about_frame.grid_rowconfigure(0, weight=0)
        self.about_frame.grid_rowconfigure(1, weight=1)
        self.about_frame.grid_rowconfigure(2, weight=1)

        self.about_title = self._create_widget(ctk.CTkLabel, self.about_frame, font=ctk.CTkFont(size=24, weight="bold"))
        self.about_title.grid(row=0, column=0, pady=20, padx=20)

        center_frame = self._create_widget(ctk.CTkFrame, self.about_frame, fg_color="transparent")
        center_frame.grid(row=1, column=0, sticky="nsew", pady=20)
        center_frame.grid_columnconfigure(0, weight=1)

        self.about_text_label = self._create_widget(ctk.CTkLabel, center_frame, justify=tk.CENTER,
                                             font=ctk.CTkFont(size=16))
        self.about_text_label.grid(row=0, column=0, padx=20, pady=20)

        self.about_links_label = self._create_widget(ctk.CTkLabel, center_frame, font=ctk.CTkFont(size=16, weight="bold"))
        self.about_links_label.grid(row=1, column=0, padx=20, pady=(20, 5))

        links_frame = self._create_widget(ctk.CTkFrame, center_frame, fg_color="transparent")
        links_frame.grid(row=2, column=0, padx=20)
        links_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        linkedin_url = "https://www.linkedin.com/in/cybersecsprofile/"
        github_url = "https://github.com/QmFkLVBp"
        htb_url = "https://app.hackthebox.com/profile/1969974"
        thm_url = "https://tryhackme.com/p/0xW1ZARD"

        self.linkedin_btn = self._create_widget(ctk.CTkButton, links_frame, text="LinkedIn", command=lambda: self.open_link(linkedin_url))
        self.linkedin_btn.grid(row=0, column=0, padx=5, pady=5)
        self.github_btn = self._create_widget(ctk.CTkButton, links_frame, text="GitHub", command=lambda: self.open_link(github_url))
        self.github_btn.grid(row=0, column=1, padx=5, pady=5)
        self.htb_btn = self._create_widget(ctk.CTkButton, links_frame, text="HackTheBox", command=lambda: self.open_link(htb_url))
        self.htb_btn.grid(row=0, column=2, padx=5, pady=5)
        self.thm_btn = self._create_widget(ctk.CTkButton, links_frame, text="TryHackMe", command=lambda: self.open_link(thm_url))
        self.thm_btn.grid(row=0, column=3, padx=5, pady=5)

    def open_link(self, url):
        webbrowser.open_new(url)

    def apply_combined_theme_from_name(self, theme_display_name):
        theme_params = self.theme_name_map.get(theme_display_name)
        if theme_params:
            mode, color = theme_params
            ctk.set_appearance_mode(mode)
            ctk.set_default_color_theme(color)
            print(f"Applied theme: Mode='{mode}', Color='{color}'")
        else:
            print(f"Error: Could not find parameters for theme name: {theme_display_name}")

    def update_theme_menu_default(self):
        current_mode = ctk.get_appearance_mode()
        current_color = self._get_current_color_theme_name()
        lang_code = self.current_lang.get()
        current_theme_name = None

        for name, params in self.theme_name_map.items():
            if name in LANG_STRINGS[lang_code].values() and params == (current_mode, current_color):
                current_theme_name = name
                break

        if current_theme_name and hasattr(self, 'settings_theme_menu'):
            self.settings_theme_menu.set(current_theme_name)
        elif hasattr(self, 'settings_theme_menu'):
            default_theme_name = LANG_STRINGS[lang_code]["theme_dark_blue"]
            self.settings_theme_menu.set(default_theme_name)

    def _get_current_color_theme_name(self):
         try:
             internal_theme_path = getattr(ctk.ThemeManager, "_currently_loaded_theme", "").lower()
             if "dark-blue" in internal_theme_path: return "dark-blue"
             if "green" in internal_theme_path: return "green"
             return "blue"
         except Exception as e:
             print(f"Could not reliably determine current color theme: {e}")
             return "blue"


    def change_language(self, *args):
        lang_code = self.current_lang.get()
        self.update_all_texts(lang_code)

        theme_display_names = [
            LANG_STRINGS[lang_code]["theme_dark_blue"], LANG_STRINGS[lang_code]["theme_dark_green"], LANG_STRINGS[lang_code]["theme_dark_darkblue"],
            LANG_STRINGS[lang_code]["theme_light_blue"], LANG_STRINGS[lang_code]["theme_light_green"], LANG_STRINGS[lang_code]["theme_light_darkblue"]
        ]
        if hasattr(self, 'settings_theme_menu'):
            self.settings_theme_menu.configure(values=theme_display_names)
            self.update_theme_menu_default()


    def update_all_texts(self, lang_code):
        lang = LANG_STRINGS.get(lang_code, LANG_STRINGS["ua"])

        self.title(lang["title"])
        self.app_logo_label.configure(text=lang["app_logo_text"])

        self.xor_button.configure(text=lang["nav_xor"])
        self.lsb_button.configure(text=lang["nav_lsb"])
        self.picker_button.configure(text=lang["nav_picker"])
        self.settings_button.configure(text=lang["nav_settings"])
        self.about_button.configure(text=lang["nav_about"])

        self.xor_title.configure(text=lang["xor_title"])
        if not hasattr(self.xor_label1, 'image') or self.xor_label1.image is None:
            self.xor_label1.configure(text=lang["xor_img1_text"])
        if not hasattr(self.xor_label2, 'image') or self.xor_label2.image is None:
            self.xor_label2.configure(text=lang["xor_img2_text"])
        self.xor_load_btn1.configure(text=lang["xor_load1"])
        self.xor_load_btn2.configure(text=lang["xor_load2"])
        self.xor_run_btn.configure(text=lang["xor_run"])
        if not hasattr(self.xor_result_label, 'image') or self.xor_result_label.image is None:
            self.xor_result_label.configure(text=lang["xor_result_text"])

        self.lsb_title.configure(text=lang["lsb_title"])
        self.lsb_load_btn.configure(text=lang["lsb_load"])
        self.lsb_run_btn.configure(text=lang["lsb_run"])
        if not hasattr(self.lsb_original_label, 'image') or self.lsb_original_label.image is None:
             self.lsb_original_label.configure(text=lang["lsb_original_text"])
        if not hasattr(self.lsb_result_label, 'image') or self.lsb_result_label.image is None:
            self.lsb_result_label.configure(text=lang["lsb_result_text"])
        self.lsb_decoded_text_label.configure(text=lang["lsb_decoded_text_label"])

        self.picker_title.configure(text=lang["picker_title"])
        self.picker_load_btn.configure(text=lang["picker_load"])
        if not hasattr(self.picker_image_label, 'image') or self.picker_image_label.image is None:
            self.picker_image_label.configure(text=lang["picker_img_text"])
        self.picker_hex_label.configure(text=lang["picker_hex_default"])
        self.picker_last_text_label.configure(text=lang["picker_text_default"])
        self.picker_clear_btn.configure(text=lang["picker_clear"])
        self.picker_status_label.configure(text=lang["picker_status_default"])

        self.settings_title.configure(text=lang["settings_title"])
        self.settings_lang_label.configure(text=lang["settings_lang"])
        self.settings_theme_label.configure(text=lang["settings_theme"])
        self.settings_danger_label.configure(text=lang["settings_danger_zone"])
        if hasattr(self, 'self_destruct_btn') and self.self_destruct_btn.winfo_exists() and self.self_destruct_btn.cget('state') == tk.NORMAL:
             self.self_destruct_btn.configure(text=lang["settings_self_destruct"])

        self.about_title.configure(text=lang["about_title"])
        self.about_text_label.configure(text=lang["about_text"])
        self.about_links_label.configure(text=lang["about_links_label"])


    def hide_all_frames(self):
        self.xor_frame.grid_forget()
        self.lsb_frame.grid_forget()
        self.picker_frame.grid_forget()
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

    def show_pil_image_on_label(self, pil_img, label, size, keep_aspect=False):
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
                ratio = min(max_w/w, max_h/h) if w > 0 and h > 0 else 1
                display_size = (int(w * ratio), int(h * ratio))

            ctk_img = ctk.CTkImage(light_image=pil_img.copy(), size=display_size)
            label.configure(image=ctk_img, text="")
            label.image = ctk_img
        except Exception as e:
            label.configure(image=None, text=f"Error\n{e}")
            label.image = None

    def show_image_on_label(self, path, label, size, keep_aspect=False):
        try:
            pil_img = Image.open(path)
            self.show_pil_image_on_label(pil_img, label, size, keep_aspect)
        except Exception as e:
            label.configure(image=None, text=f"Error\n{e}")
            label.image = None

if __name__ == "__main__":
    app = StegoApp()
    app.mainloop()
