from __future__ import annotations
import base64, binascii
import hashlib
import io
import json
import os
import string
import threading
import time
import webbrowser
from collections import Counter
from typing import Tuple, List, Optional
import requests
from PIL import Image, ImageChops, ImageDraw, ImageTk
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import math
import random

# NEW: matplotlib for charts
try:
    import matplotlib
    matplotlib.use('Agg')  # backend without display for saving
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False

# Optional AES dependency (PyCryptodome)
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad

    CRYPTO_AVAILABLE = True
except Exception:
    CRYPTO_AVAILABLE = False

APP_VERSION = "2.0.7" # Оновлено
# Fixed raw URL path (removed invalid refs/heads)
APP_LOGO_URL = "https://raw.githubusercontent.com/QmFkLVBp/decryptoinator/main/logo.png"

# --- S-DES Constants ---
P10 = (3, 5, 2, 7, 4, 10, 1, 9, 8, 6)
P8 = (6, 3, 7, 4, 8, 5, 10, 9)
IP = (2, 6, 3, 1, 4, 8, 5, 7)
IP_INV = (4, 1, 3, 5, 7, 2, 8, 6)
EP = (4, 1, 2, 3, 2, 3, 4, 1)
P4 = (2, 4, 3, 1)

S0 = [
    [1, 0, 3, 2],
    [3, 2, 1, 0],
    [0, 2, 1, 3],
    [3, 1, 3, 2]
]
S1 = [
    [0, 1, 2, 3],
    [2, 0, 1, 3],
    [3, 0, 1, 0],
    [2, 1, 0, 3]
]
# --- End S-DES Constants ---

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
        "nav_aes": "AES",
        "nav_sdes": "S-DES",
        "aes_title": "AES: Шифрування / Дешифрування",
        "sdes_title": "S-DES: Шифрування / Дешифрування",
        "mode_encrypt": "Зашифрувати",
        "mode_decrypt": "Розшифрувати",
        "run": "ВИКОНАТИ",
        "key_label": "Ключ / Пароль:",
        "input_label": "Вхідні дані:",
        "output_label": "Результат:",
        "aes_bruteforce_label": "AES PIN bruteforce (numeric PIN): max length",
        "aes_bruteforce_run": "BRUTE AES (обмежено PIN)",
        "sdes_bruteforce_label": "S-DES brute: знайти ключ за відомою підстрокой",
        "sdes_bruteforce_run": "BRUTE S-DES",
        "brute_status": "Brute-force виконується...",
        "brute_done": "Brute-force завершено. Знайдено:",
        "brute_no_results": "Нічого не знайдено.",
        "crypto_error_crypto_missing": "PyCryptodome не встановлено — AES недоступний.",
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
        "picker_text_default": "Останній клик: ...",
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
        "vigenere_status_ok_decrypt": "Шифрування Віженера завершено.",
        "vigenere_status_error_input": "Помилка: Введіть текст та ключ.",
        "vigenere_status_error_key": "Помилка: Ключ повинен містити лише літери.",
        "vigenere_crack_btn": "Зламати (без ключа)",
        "vigenere_crack_max_key_label": "Макс. довжина ключа:",
        "vigenere_key_guess_default": "Відновлений ключ: ?",
        "vigenere_status_cracking": "Злам Віженера...",
        "vigenere_status_ok_crack": "Злам завершено.",
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
        "about_text": f"Автор: Крилевич Мирослав та Кондратюк Віталій\nГрупа: УБД-32\n\nРозроблено для навчальних цілей в криптографії.\n\nВерсія: {APP_VERSION}",
        "about_links_label": "Посилання:",
        "theme_night_cool": "Нічна Прохолода",
        "theme_forest_calm": "Лісовий Спокій",
        "theme_ocean_depth": "Океанська Глибина",
        "theme_sunrise": "Світанок",
        "theme_coffee": "Кава з Молоком",
        "theme_spring_meadow": "Весняний Луг",
        "tab_sdes": "S-DES",
        "sdes_title": "Шифр S-DES (Навчальний)",
        "sdes_input_label": "Вхід (Текст для шифр., Base64 для дешифр.):",
        "sdes_key_label": "Ключ (10-біт двійковий, н-д, 1010000010):",
        "sdes_output_label": "Вихід:",
        "sdes_log_label": "Журнал виконання:",
        "sdes_run": "Виконати S-DES",
        "sdes_status_ok": "S-DES {} завершено.",
        "sdes_status_error_key": "Помилка: Ключ S-DES має бути рівно 10 біт (0 та 1)",
        "sdes_status_error_b64": "Помилка: Вхідні дані для дешифрування - невалідний Base64.",
        "sdes_brute_title": "Злам S-DES (Brute-force)",
        "sdes_brute_ciphertext_label": "Шифротекст (Base64, з поля 'Вхід'):",
        "sdes_brute_known_label": "Відомий фрагмент тексту (опційно):",
        "sdes_brute_run": "Почати S-DES Brute-force (1024 ключі)",
        "dialog_brute_sdes_msg": "Знайдено {0} можливих збігів (макс. 100):\n\n{1}",
        "dialog_brute_sdes_match": "Ключ: {0}\nТекст: {1}...\n",
        "dialog_brute_sdes_no_match": "Не знайдено ключа, що відповідає критеріям.",
        # Substitution cipher strings
        "nav_subst": "Заміни",
        "subst_title": "Вікно: Моноалфавітна Заміна",
        "subst_input_label": "Шифротекст:",
        "subst_freq_chars_label": "Частотний аналіз символів:",
        "subst_freq_bigrams_label": "Частотний аналіз біграм:",
        "subst_mapping_label": "Таблиця заміни:",
        "subst_cipher_col": "Шифр",
        "subst_plain_col": "Текст",
        "subst_add_row": "+ Рядок",
        "subst_remove_row": "- Рядок",
        "subst_analyze": "Аналізувати",
        "subst_apply": "Застосувати",
        "subst_clear": "Очистити",
        "subst_export": "Експорт",
        "subst_import": "Імпорт",
        "subst_suggest": "Brute force",
        "subst_output_label": "Результат заміни:",
        "subst_lang_label": "Мова частот:",
        "subst_lang_ua": "Українська",
        "subst_lang_en": "Англійська",
        "subst_status_ok_analyze": "Частотний аналіз завершено.",
        "subst_status_ok_apply": "Заміну застосовано.",
        "subst_status_ok_suggest": "Brute force згенеровано. Таблицю оновлено.",
        "subst_status_ok_export": "Таблицю експортовано.",
        "subst_status_ok_import": "Таблицю імпортовано.",
        "subst_status_ok_clear": "Таблицю очищено.",
        "subst_status_error_input": "Помилка: Введіть шифротекст.",
        "subst_status_error_import": "Помилка: Невалідний JSON файл.",
        "subst_status_error_export": "Помилка: Не вдалося зберегти файл.",
        "subst_auto_replace": "Автоматична заміна",
        "subst_undo": "Відмінити",
        "subst_redo": "Повторити",
        "subst_status_ok_auto": "Автоматичну заміну застосовано.",
        "subst_export_txt": "Експорт TXT",
        "subst_import_txt": "Імпорт TXT",
        "subst_status_ok_export_txt": "Таблицю експортовано в TXT.",
        "subst_status_ok_import_txt": "Таблицю імпортовано з TXT.",
        "subst_status_error_import_txt": "Помилка: Невалідний TXT файл.",
        "subst_export_report": "Звіт",
        "subst_status_ok_export_report": "Звіт експортовано.",
        "subst_bigram_connectivity_label": "Біграми та з'єднання:",
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
        "nav_aes": "AES",
        "nav_sdes": "S-DES",
        "aes_title": "AES: Encrypt / Decrypt",
        "sdes_title": "S-DES: Encrypt / Decrypt",
        "mode_encrypt": "Encrypt",
        "mode_decrypt": "Decrypt",
        "run": "RUN",
        "key_label": "Key / Password:",
        "input_label": "Input data:",
        "output_label": "Output:",
        "aes_bruteforce_label": "AES PIN bruteforce (numeric PIN): max length",
        "aes_bruteforce_run": "BRUTE AES (limited PIN)",
        "sdes_bruteforce_label": "S-DES brute: find key by known fragment",
        "sdes_bruteforce_run": "BRUTE S-DES",
        "brute_status": "Brute-force running...",
        "brute_done": "Brute-force done. Found:",
        "brute_no_results": "No results.",
        "crypto_error_crypto_missing": "PyCryptodome not installed — AES unavailable.",
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
        "lsb_error_decode": "[Error decoding Base64: {e}\n\nCollected string:\n{s}]",
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
        "vigenere_crack_btn": "CRACK (no key)",
        "vigenere_crack_max_key_label": "Max key length:",
        "vigenere_key_guess_default": "Guessed key: ?",
        "vigenere_status_cracking": "Cracking Vigenère...",
        "vigenere_status_ok_crack": "Cracking complete.",
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
        "about_text": f"Author: Krylevych Myroslav and Kondratyk Vitaliy\nGroup: UBD-32\n\nDeveloped for learning scope in cybersecurity.\n\nVersion: {APP_VERSION}",
        "about_links_label": "Links:",
        "theme_night_cool": "Night Cool",
        "theme_forest_calm": "Forest Calm",
        "theme_ocean_depth": "Ocean Depth",
        "theme_sunrise": "Sunrise",
        "theme_coffee": "Coffee Milk",
        "theme_spring_meadow": "Spring Meadow",
        "tab_sdes": "S-DES",
        "sdes_title": "S-DES Cipher (Educational)",
        "sdes_input_label": "Input (Text for Encrypt, Base64 for Decrypt):",
        "sdes_key_label": "Key (10-bit binary, e.g., 1010000010):",
        "sdes_output_label": "Output:",
        "sdes_log_label": "Execution Log:",
        "sdes_run": "Run S-DES",
        "sdes_status_ok": "S-DES {} complete.",
        "sdes_status_error_key": "Error: S-DES Key must be exactly 10 bits (0s and 1s)",
        "sdes_status_error_b64": "Error: Input data for decryption is not valid Base64.",
        "sdes_brute_title": "S-DES Key Cracker (Brute-force)",
        "sdes_brute_ciphertext_label": "Ciphertext (Base64, from 'Input' field):",
        "sdes_brute_known_label": "Known Plaintext Fragment (optional):",
        "sdes_brute_run": "Start S-DES Brute-force (1024 keys)",
        "dialog_brute_sdes_msg": "Found {0} possible matches (max 100 shown):\n\n{1}",
        "dialog_brute_sdes_match": "Key: {0}\nPlaintext: {1}...\n",
        "dialog_brute_sdes_no_match": "No key found that matched the criteria.",
        # Substitution cipher strings
        "nav_subst": "Substitution",
        "subst_title": "Window: Monoalphabetic Substitution",
        "subst_input_label": "Ciphertext:",
        "subst_freq_chars_label": "Character Frequency Analysis:",
        "subst_freq_bigrams_label": "Bigram Frequency Analysis:",
        "subst_mapping_label": "Substitution Table:",
        "subst_cipher_col": "Cipher",
        "subst_plain_col": "Plain",
        "subst_add_row": "+ Row",
        "subst_remove_row": "- Row",
        "subst_analyze": "Analyze",
        "subst_apply": "Apply",
        "subst_clear": "Clear",
        "subst_export": "Export",
        "subst_import": "Import",
        "subst_suggest": "Brute force",
        "subst_output_label": "Decrypted Result:",
        "subst_lang_label": "Frequency Language:",
        "subst_lang_ua": "Ukrainian",
        "subst_lang_en": "English",
        "subst_status_ok_analyze": "Frequency analysis complete.",
        "subst_status_ok_apply": "Substitution applied.",
        "subst_status_ok_suggest": "Brute force generated. Table updated.",
        "subst_status_ok_export": "Mapping exported.",
        "subst_status_ok_import": "Mapping imported.",
        "subst_status_ok_clear": "Mapping cleared.",
        "subst_status_error_input": "Error: Enter ciphertext.",
        "subst_status_error_import": "Error: Invalid JSON file.",
        "subst_status_error_export": "Error: Could not save file.",
        "subst_auto_replace": "Auto Replace",
        "subst_undo": "Undo",
        "subst_redo": "Redo",
        "subst_status_ok_auto": "Auto replacement applied.",
        "subst_export_txt": "Export TXT",
        "subst_import_txt": "Import TXT",
        "subst_status_ok_export_txt": "Mapping exported to TXT.",
        "subst_status_ok_import_txt": "Mapping imported from TXT.",
        "subst_status_error_import_txt": "Error: Invalid TXT file.",
        "subst_export_report": "Report",
        "subst_status_ok_export_report": "Report exported.",
        "subst_bigram_connectivity_label": "Bigrams & Connectivity:",
    }
}

VALID_BASE64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="

# -------------------------
# S-DES Implementation (pure Python)
# -------------------------
P10 = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
P8 = [6, 3, 7, 4, 8, 5, 10, 9]
IP = [2, 6, 3, 1, 4, 8, 5, 7]
IP_INV = [4, 1, 3, 5, 7, 2, 8, 6]
EP = [4, 1, 2, 3, 2, 3, 4, 1]
P4 = [2, 4, 3, 1]
S0 = [
    [1, 0, 3, 2],
    [3, 2, 1, 0],
    [0, 2, 1, 3],
    [3, 1, 3, 2],
]
S1 = [
    [0, 1, 2, 3],
    [2, 0, 1, 3],
    [3, 0, 1, 0],
    [2, 1, 0, 3],
]


def _permute(bits, table):
    return [bits[i - 1] for i in table]


def _left_shift(bits, n):
    return bits[n:] + bits[:n]


def _bits_from_int(value, bits_count):
    return [(value >> (bits_count - 1 - i)) & 1 for i in range(bits_count)]


def _int_from_bits(bits):
    v = 0
    for b in bits:
        v = (v << 1) | (b & 1)
    return v


def sdes_generate_subkeys(key10):
    p10 = _permute(key10, P10)
    left = p10[:5]
    right = p10[5:]
    ls1_l = _left_shift(left, 1)
    ls1_r = _left_shift(right, 1)
    k1 = _permute(ls1_l + ls1_r, P8)
    ls2_l = _left_shift(ls1_l, 2)
    ls2_r = _left_shift(ls1_r, 2)
    k2 = _permute(ls2_l + ls2_r, P8)
    return k1, k2


def _fk(bits8, subkey):
    left = bits8[:4]
    right = bits8[4:]
    ep = _permute(right, EP)
    xor_res = [ep[i] ^ subkey[i] for i in range(8)]
    left_ep = xor_res[:4]
    right_ep = xor_res[4:]
    row0 = (left_ep[0] << 1) | left_ep[3]
    col0 = (left_ep[1] << 1) | left_ep[2]
    s0_val = S0[row0][col0]
    row1 = (right_ep[0] << 1) | right_ep[3]
    col1 = (right_ep[1] << 1) | right_ep[2]
    s1_val = S1[row1][col1]
    s_out = _bits_from_int(s0_val, 2) + _bits_from_int(s1_val, 2)
    p4 = _permute(s_out, P4)
    new_left = [left[i] ^ p4[i] for i in range(4)]
    return new_left + right


def sdes_encrypt_block(plain8bits, key10bits):
    k1, k2 = sdes_generate_subkeys(key10bits)
    ip = _permute(plain8bits, IP)
    after_fk1 = _fk(ip, k1)
    swapped = after_fk1[4:] + after_fk1[:4]
    after_fk2 = _fk(swapped, k2)
    ciphertext = _permute(after_fk2, IP_INV)
    return ciphertext


def sdes_decrypt_block(cipher8bits, key10bits):
    k1, k2 = sdes_generate_subkeys(key10bits)
    ip = _permute(cipher8bits, IP)
    after_fk1 = _fk(ip, k2)
    swapped = after_fk1[4:] + after_fk1[:4]
    after_fk2 = _fk(swapped, k1)
    plain = _permute(after_fk2, IP_INV)
    return plain


def sdes_encrypt_bytes(data: bytes, key10: int) -> bytes:
    out = bytearray()
    keybits = _bits_from_int(key10, 10)
    for b in data:
        block_bits = _bits_from_int(b, 8)
        ct_bits = sdes_encrypt_block(block_bits, keybits)
        out.append(_int_from_bits(ct_bits))
    return bytes(out)


def sdes_decrypt_bytes(data: bytes, key10: int) -> bytes:
    out = bytearray()
    keybits = _bits_from_int(key10, 10)
    for b in data:
        block_bits = _bits_from_int(b, 8)
        pt_bits = sdes_decrypt_block(block_bits, keybits)
        out.append(_int_from_bits(pt_bits))
    return bytes(out)


# -------------------------

# ---- AES: improved key handling, encrypt/decrypt with key-length detection ----
import binascii


def aes_prepare_key(key_input: str, prefer_bits: int | None = None) -> tuple[bytes, int, str]:
    s = (key_input or "").strip()
    if not s:
        return (b"\x00" * 16, 128, "empty->zero-key")
    valid_sizes = (16, 24, 32)
    hex_ok = all(c in string.hexdigits for c in s) and (len(s) % 2 == 0)
    if hex_ok:
        try:
            kbytes = binascii.unhexlify(s)
            if len(kbytes) in valid_sizes:
                return (kbytes, len(kbytes) * 8, f"hex ({len(kbytes) * 8} bits)")
        except Exception:
            pass
    raw = s.encode("utf-8", errors="ignore")
    if prefer_bits in (128, 192, 256):
        needed = prefer_bits // 8
        if len(raw) >= needed:
            return (raw[:needed], prefer_bits, "raw-trimmed")
        derived = hashlib.sha256(raw).digest()[:needed]
        return (derived, prefer_bits, "derived(SHA256)->trimmed")
    if len(raw) in valid_sizes:
        return (raw, len(raw) * 8, "raw-exact")
    if len(raw) > 32:
        kb = hashlib.sha256(raw).digest()[:32]
        return (kb, 256, "derived(SHA256)->256")
    elif len(raw) > 24:
        kb = hashlib.sha256(raw).digest()[:32][:24]
        return (kb, 192, "derived(SHA256)->192")
    elif len(raw) >= 16:
        if len(raw) >= 24:
            kb = hashlib.sha256(raw).digest()[:24]
            return (kb, 192, "derived(SHA256)->192")
        kb = hashlib.sha256(raw).digest()[:16]
        return (kb, 128, "derived(SHA256)->128")
    else:
        kb = hashlib.sha256(raw).digest()[:16]
        return (kb, 128, "derived(SHA256)->128 (input too short)")


def aes_prepare_key(key_input: str, prefer_bits: int | None = None) -> tuple[bytes, int, str]:
    """
    Prepare AES key from user input. Returns (key_bytes, key_bits, source_description).
    - Accepts hex (even-length hex string) of sizes 16/24/32 bytes.
    - Accepts raw UTF-8 string; if exact size, use as-is; otherwise derive via SHA-256 and trim/extend.
    - prefer_bits can be 128/192/256 to force key size.
    """
    import binascii
    s = (key_input or "").strip()
    if not s:
        return (b"\x00" * 16, 128, "empty->zero-key")
    valid_sizes = (16, 24, 32)
    # Try hex
    hex_ok = all(c in string.hexdigits for c in s) and (len(s) % 2 == 0)
    if hex_ok:
        try:
            kbytes = binascii.unhexlify(s)
            if len(kbytes) in valid_sizes:
                return (kbytes, len(kbytes) * 8, f"hex ({len(kbytes) * 8} bits)")
        except Exception:
            pass
    raw = s.encode('utf-8', errors='ignore')
    if prefer_bits in (128, 192, 256):
        needed = prefer_bits // 8
        if len(raw) >= needed:
            return (raw[:needed], prefer_bits, 'raw-trimmed')
        derived = hashlib.sha256(raw).digest()[:needed]
        return (derived, prefer_bits, 'derived(SHA256)->trimmed')
    if len(raw) in valid_sizes:
        return (raw, len(raw) * 8, 'raw-exact')
    if len(raw) > 32:
        kb = hashlib.sha256(raw).digest()[:32]
        return (kb, 256, 'derived(SHA256)->256')
    elif len(raw) > 24:
        kb = hashlib.sha256(raw).digest()[:32][:24]
        return (kb, 192, 'derived(SHA256)->192')
    elif len(raw) >= 16:
        if len(raw) >= 24:
            kb = hashlib.sha256(raw).digest()[:24]
            return (kb, 192, 'derived(SHA256)->192')
        kb = hashlib.sha256(raw).digest()[:16]
        return (kb, 128, 'derived(SHA256)->128')
    else:
        kb = hashlib.sha256(raw).digest()[:16]
        return (kb, 128, 'derived(SHA256)->128 (input too short)')


def aes_encrypt_text(plaintext: str, key_input: str, prefer_bits: int | None = None) -> tuple[str, int, str]:
    if not CRYPTO_AVAILABLE:
        raise RuntimeError("Crypto not available")
    key_bytes, key_bits, src = aes_prepare_key(key_input, prefer_bits)
    iv = os.urandom(16)
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv=iv)
    ct = cipher.encrypt(pad(plaintext.encode('utf-8'), AES.block_size))
    payload = iv + ct
    return base64.b64encode(payload).decode('utf-8'), key_bits, src


def aes_decrypt_text(b64cipher: str, key_input: str, prefer_bits: int | None = None) -> tuple[str, int, str]:
    if not CRYPTO_AVAILABLE:
        raise RuntimeError("Crypto not available")
    raw = base64.b64decode(b64cipher)
    if len(raw) < 16:
        raise ValueError("Ciphertext too short (no IV)")
    iv = raw[:16]
    ct = raw[16:]
    key_bytes, key_bits, src = aes_prepare_key(key_input, prefer_bits)
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv=iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode('utf-8', errors='replace'), key_bits, src


# -------------------------
# Brute-force helpers
# -------------------------
def sdes_bruteforce(cipherbytes: bytes, known_fragment: bytes = None, max_results=50):
    results = []
    for key in range(0, 1024):
        try:
            pt = sdes_decrypt_bytes(cipherbytes, key)
            if known_fragment:
                if known_fragment in pt:
                    results.append((key, pt))
                    if len(results) >= max_results:
                        break
            else:
                if len(results) < 5:
                    results.append((key, pt))
        except Exception:
            continue
    return results


def aes_bruteforce_pin(cipher_b64: str, known_fragment: bytes = None, max_pin_length=4):
    if not CRYPTO_AVAILABLE:
        raise RuntimeError("Crypto not available")
    matches = []
    data = base64.b64decode(cipher_b64)
    if len(data) < 16:
        return matches
    iv = data[:16]
    ct = data[16:]
    for length in range(1, max_pin_length + 1):
        for num in range(0, 10 ** length):
            pin = str(num).zfill(length)
            key = aes_derive_key_from_password(pin)
            try:
                cipher = AES.new(key, AES.MODE_CBC, iv=iv)
                pt = unpad(cipher.decrypt(ct), AES.block_size)
                if known_fragment:
                    if known_fragment in pt:
                        matches.append((pin, pt))
                else:
                    matches.append((pin, pt))
                    return matches
            except Exception:
                continue
    return matches


import logging

logger = logging.getLogger("decrypto")
if not logger.handlers:
    # простий файловий логер, якщо ще не створено
    fh = logging.FileHandler("decrypto.log", encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    logger.addHandler(fh)
    logger.setLevel(logging.DEBUG)


def evp_bytes_to_key(password: bytes, salt: bytes, key_len: int, iv_len: int, hasher=hashlib.md5) -> Tuple[
    bytes, bytes]:
    """
    Реалізація OpenSSL EVP_BytesToKey (MD5 variant).
    Повертає (key, iv). Використовується формою 'Salted__' + 8-byte salt + ciphertext.
    """
    derived = b""
    prev = b""
    # Loop like OpenSSL EVP_BytesToKey with MD5
    while len(derived) < (key_len + iv_len):
        prev = hasher(prev + password + salt).digest()
        derived += prev
    key = derived[:key_len]
    iv = derived[key_len:key_len + iv_len]
    return key, iv


def openssl_aes_encrypt(plaintext: str, password: str, prefer_bits: Optional[int] = None) -> str:
    """
    Шифрує у форматі сумісному з OpenSSL/aesencryption.net:
    payload = b"Salted__" + salt(8) + ciphertext
    Повертає base64(payload).
    prefer_bits: 128/192/256 або None -> по замовчуванню використовуємо 256 для derivation.
    """
    if not CRYPTO_AVAILABLE:
        raise RuntimeError("Crypto not available")
    if prefer_bits not in (None, 128, 192, 256):
        raise ValueError("prefer_bits must be 128/192/256 or None")

    salt = os.urandom(8)
    key_len = (prefer_bits // 8) if prefer_bits else 32
    iv_len = AES.block_size  # 16
    key, iv = evp_bytes_to_key(password.encode("utf-8"), salt, key_len, iv_len, hashlib.md5)

    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    padded = pad(plaintext.encode("utf-8"), AES.block_size, style='pkcs7')
    ct = cipher.encrypt(padded)
    payload = b"Salted__" + salt + ct
    return base64.b64encode(payload).decode('utf-8')


def openssl_aes_decrypt(b64payload: str, password: str, prefer_bits: Optional[int] = None) -> str:
    """
    Дешифрує OpenSSL 'Salted__' payload.
    prefer_bits може підказати бажаний key-size (128/192/256) — якщо None, будемо використовувати 256 для derivation.
    Повертає рядок utf-8 (errors='replace').
    """
    if not CRYPTO_AVAILABLE:
        raise RuntimeError("Crypto not available")
    try:
        data = base64.b64decode(b64payload)
    except Exception as e:
        raise ValueError(f"Invalid base64 payload: {e}")

    if not data.startswith(b"Salted__") or len(data) < 16:
        raise ValueError("Input is not OpenSSL salted format (missing 'Salted__' + salt).")

    salt = data[8:16]
    ct = data[16:]
    key_len = (prefer_bits // 8) if prefer_bits else 32
    iv_len = AES.block_size
    key, iv = evp_bytes_to_key(password.encode("utf-8"), salt, key_len, iv_len, hashlib.md5)

    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    try:
        pt = unpad(cipher.decrypt(ct), AES.block_size, style='pkcs7')
    except ValueError as e:
        # padding error or wrong key
        raise ValueError(f"Decryption failed (padding/incorrect key): {e}")
    return pt.decode('utf-8', errors='replace')


def aes_derive_key_from_password(password: str, bits: int = 128) -> bytes:
    """
    Простий derive для brute-force PIN: SHA256(password)[:bits//8].
    (Використовується у aes_bruteforce_pin, якщо ваш bruteforce очікує derive).
    """
    h = hashlib.sha256(password.encode('utf-8')).digest()
    return h[: (bits // 8)]


# ---- (A) Гнучкий AES-декодер: вставити після імпортів (перед класом StegoApp) ----
def openssl_or_iv_decrypt(b64payload: str, password: str, prefer_bits: Optional[int] = None) -> tuple[str, str]:
    """
    Прагматичний декодер, що пробує кілька форматів:
      - OpenSSL salted (b"Salted__" + 8-byte salt + ciphertext) -> EVP_BytesToKey (MD5)
      - IV-prefixed (first 16 bytes -> IV, rest -> ciphertext) -> tries prefer_bits or 128/192/256 using aes_prepare_key
    Повертає (plaintext_str, info_str) або піднімає ValueError з діагностикою.
    Залежить від CRYPTO_AVAILABLE, AES, pad/unpad, aes_prepare_key на модульному рівні.
    """
    if not CRYPTO_AVAILABLE:
        raise RuntimeError("Crypto not available")

    # Базове декодування Base64
    try:
        data = base64.b64decode(b64payload)
    except Exception as e:
        raise ValueError(f"Invalid base64 payload: {e}")

    # --- 1) OpenSSL "Salted__" формат ---
    try:
        if data.startswith(b"Salted__") and len(data) > 16:
            salt = data[8:16]
            ct = data[16:]
            # key_len decision
            key_len = (prefer_bits // 8) if prefer_bits else 32
            iv_len = AES.block_size
            key, iv = evp_bytes_to_key(password.encode("utf-8"), salt, key_len, iv_len, hashlib.md5)
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            return pt.decode('utf-8', errors='replace'), f"OpenSSL-salted (MD5 EVP_BytesToKey), key_bits={key_len * 8}"
    except Exception as e:
        # Не відразу фейлим — продовжимо спроби, але запишемо повідомлення
        openssl_err = str(e)
    else:
        openssl_err = None

    # --- 2) IV-prefixed format: first 16 bytes are IV, rest ciphertext ---
    if len(data) >= 16:
        iv = data[:16]
        ct = data[16:]
        # If prefer_bits specified, try that first
        bits_attempts = []
        if prefer_bits in (128, 192, 256):
            bits_attempts.append(prefer_bits)
        # append common sizes
        for b in (128, 192, 256):
            if b not in bits_attempts:
                bits_attempts.append(b)

        last_exception = None
        for bits in bits_attempts:
            try:
                # Use aes_prepare_key to support hex/raw passwords and derivation rules
                key_bytes, key_bits, src = aes_prepare_key(password, prefer_bits=bits)
                cipher = AES.new(key_bytes, AES.MODE_CBC, iv=iv)
                pt = unpad(cipher.decrypt(ct), AES.block_size)
                info = f"IV-prefixed payload, used aes_prepare_key -> key_bits={key_bits} ({src})"
                return pt.decode('utf-8', errors='replace'), info
            except Exception as e:
                last_exception = e
                continue
        # якщо не спрацювало, зберігаємо помилку
        iv_err = str(last_exception) if last_exception else "unknown error in IV-prefixed attempts"
    else:
        iv_err = "payload too short (<16 bytes) to be IV-prefixed"

    # Якщо дійшли сюди — нічого не спрацювало. Повертаємо diagnostic message
    msg_parts = []
    if openssl_err:
        msg_parts.append(f"OpenSSL attempt failed: {openssl_err}")
    msg_parts.append(f"IV-prefixed attempt failed: {iv_err}")
    raise ValueError(
        "Input is not OpenSSL salted format and IV-prefixed attempts failed. Details: " + " | ".join(msg_parts))


def aes_bruteforce_password(cipher_b64: str, known_fragment: Optional[bytes] = None,
                            max_pin_length: int = 4, prefer_bits: Optional[int] = None,
                            try_keysizes_if_salted: Optional[List[int]] = None):
    """
    Brute-force candidate passwords (numeric PINs by length) against a Base64 AES payload.
    - If payload is OpenSSL-salted (starts with b"Salted__"), uses evp_bytes_to_key(MD5) with salt for key/iv derivation.
      try_keysizes_if_salted: list of key sizes to try (e.g. [192,256,128]) or None to use [256,192,128].
    - Otherwise, if payload is IV-prefixed (first 16 bytes = IV), uses aes_prepare_key(candidate, prefer_bits).
    - Returns list of matches: [(candidate_password_str, plaintext_bytes), ...]
    """
    matches = []
    if not CRYPTO_AVAILABLE:
        raise RuntimeError("Crypto not available")
    try:
        data = base64.b64decode(cipher_b64.strip())
    except Exception as e:
        raise ValueError(f"Base64 decode error: {e}")

    if len(data) < 1:
        return matches

    # Detect salted OpenSSL format
    is_salted = data.startswith(b"Salted__") and len(data) >= 16
    if is_salted:
        salt = data[8:16]
        ct = data[16:]
        if try_keysizes_if_salted is None:
            # default try order: try prefer_bits first (if provided), else 256->192->128
            if prefer_bits in (128, 192, 256):
                order = [prefer_bits] + [b for b in (256, 192, 128) if b != prefer_bits]
            else:
                order = [256, 192, 128]
        else:
            order = try_keysizes_if_salted

        # Iterate over PIN lengths/numeric candidates (1..max_pin_length)
        for length in range(1, max_pin_length + 1):
            upper = 10 ** length
            for num in range(0, upper):
                candidate = str(num).zfill(length)
                # for each candidate, try key sizes in order
                for bits in order:
                    try:
                        key_len = bits // 8
                        key, iv = evp_bytes_to_key(candidate.encode('utf-8'), salt, key_len, AES.block_size,
                                                   hashlib.md5)
                        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
                        pt = unpad(cipher.decrypt(ct), AES.block_size)
                        # success
                        matches.append((candidate, pt))
                        # Optionally return immediately on first find; here collect multiple
                        # return matches
                    except Exception:
                        continue
        return matches

    # Not salted => maybe IV-prefixed or raw ciphertext
    if len(data) >= 16:
        iv = data[:16]
        ct = data[16:]
        # candidate loop
        for length in range(1, max_pin_length + 1):
            upper = 10 ** length
            for num in range(0, upper):
                candidate = str(num).zfill(length)
                try:
                    # use aes_prepare_key which supports hex/raw/derived
                    key_bytes, key_bits, src = aes_prepare_key(candidate, prefer_bits=prefer_bits)
                    cipher = AES.new(key_bytes, AES.MODE_CBC, iv=iv)
                    pt = unpad(cipher.decrypt(ct), AES.block_size)
                    matches.append((candidate, pt))
                except Exception:
                    continue
        return matches

    # otherwise cannot attempt
    return matches


# -------------------------
# Substitution Cipher Helper Functions
# -------------------------

# Ukrainian letter frequencies (approximate values based on corpus analysis).
# Source: Standard Ukrainian language frequency analysis; values normalized to sum to ~1.0.
# Note: These are averages across typical literary/newspaper texts.
UKRAINIAN_LETTER_FREQ = [
    ('О', 0.094), ('А', 0.073), ('Н', 0.066), ('І', 0.062), ('Е', 0.055),
    ('И', 0.054), ('В', 0.052), ('Р', 0.047), ('Т', 0.045), ('С', 0.040),
    ('К', 0.038), ('Л', 0.036), ('Д', 0.033), ('П', 0.031), ('М', 0.029),
    ('У', 0.028), ('Я', 0.024), ('Б', 0.020), ('З', 0.019), ('Ь', 0.017),
    ('Г', 0.016), ('Ч', 0.015), ('Й', 0.014), ('Х', 0.011), ('Ц', 0.009),
    ('Ж', 0.008), ('Ш', 0.007), ('Ю', 0.006), ('Є', 0.005), ('Щ', 0.004),
    ('Ф', 0.003), ('Ї', 0.002), ('Ґ', 0.001),
]

# English letter frequencies (approximate values based on standard English corpus).
# Source: Commonly cited English letter frequency (e.g., Wikipedia, Lewand 2000).
ENGLISH_LETTER_FREQ = [
    ('E', 0.127), ('T', 0.091), ('A', 0.082), ('O', 0.075), ('I', 0.070),
    ('N', 0.067), ('S', 0.063), ('H', 0.061), ('R', 0.060), ('D', 0.043),
    ('L', 0.040), ('C', 0.028), ('U', 0.028), ('M', 0.024), ('W', 0.024),
    ('F', 0.022), ('G', 0.020), ('Y', 0.020), ('P', 0.019), ('B', 0.015),
    ('V', 0.010), ('K', 0.008), ('J', 0.002), ('X', 0.002), ('Q', 0.001),
    ('Z', 0.001),
]

# Common English bigrams (digraphs) frequency order
# Source: Standard English bigram frequency analysis
ENGLISH_BIGRAM_FREQ = [
    ('TH', 0.0356), ('HE', 0.0307), ('IN', 0.0243), ('ER', 0.0205), ('AN', 0.0199),
    ('RE', 0.0185), ('ON', 0.0176), ('AT', 0.0149), ('EN', 0.0145), ('ND', 0.0135),
    ('TI', 0.0134), ('ES', 0.0134), ('OR', 0.0128), ('TE', 0.0120), ('OF', 0.0117),
    ('ED', 0.0117), ('IS', 0.0113), ('IT', 0.0112), ('AL', 0.0109), ('AR', 0.0107),
    ('ST', 0.0105), ('TO', 0.0104), ('NT', 0.0104), ('NG', 0.0095), ('SE', 0.0093),
    ('HA', 0.0093), ('AS', 0.0087), ('OU', 0.0087), ('IO', 0.0083), ('LE', 0.0083),
]

# Common Ukrainian bigrams (digraphs) frequency order
# Source: Standard Ukrainian language bigram frequency analysis
UKRAINIAN_BIGRAM_FREQ = [
    ('СТ', 0.025), ('НО', 0.022), ('НА', 0.021), ('ПО', 0.019), ('РА', 0.018),
    ('НИ', 0.017), ('КО', 0.016), ('ТО', 0.016), ('ПР', 0.015), ('РО', 0.015),
    ('ВА', 0.014), ('ЕН', 0.014), ('ТА', 0.013), ('ВО', 0.013), ('НЕ', 0.013),
    ('АН', 0.012), ('ОВ', 0.012), ('ОР', 0.011), ('ЛА', 0.011), ('ОМ', 0.010),
    ('ТИ', 0.010), ('ИН', 0.010), ('АТ', 0.009), ('ЕР', 0.009), ('КА', 0.009),
    ('ЛИ', 0.009), ('ЛО', 0.008), ('АВ', 0.008), ('ІН', 0.008), ('ІВ', 0.008),
]

# Lowercase frequency dictionaries for algorithm use (normalized)
ukr_letter_freq = {letter.lower(): freq for letter, freq in UKRAINIAN_LETTER_FREQ}
ukr_bigrams = {bg.lower(): freq for bg, freq in UKRAINIAN_BIGRAM_FREQ}
en_letter_freq = {letter.lower(): freq for letter, freq in ENGLISH_LETTER_FREQ}
en_bigrams = {bg.lower(): freq for bg, freq in ENGLISH_BIGRAM_FREQ}

# Connectivity matrix: scores adjacency likelihood for letter pairs
# Higher scores indicate common adjacent pairs; can be extended with more pairs
connectivity_matrix = {
    # Ukrainian common pairs (adjacent in words)
    'на': 2.0, 'по': 2.0, 'ст': 2.0, 'но': 1.8, 'ко': 1.8,
    'ро': 1.7, 'ва': 1.7, 'та': 1.6, 'ти': 1.6, 'не': 1.5,
    'ні': 1.5, 'ра': 1.5, 'ен': 1.4, 'ан': 1.4, 'ов': 1.4,
    'ор': 1.3, 'ла': 1.3, 'ом': 1.3, 'ин': 1.2, 'ат': 1.2,
    'ер': 1.2, 'ка': 1.2, 'ли': 1.1, 'ло': 1.1, 'ав': 1.1,
    'ін': 1.1, 'ів': 1.0, 'пр': 1.0, 'ни': 1.0, 'во': 1.0,
    # English common pairs
    'th': 2.0, 'he': 2.0, 'in': 1.8, 'er': 1.8, 'an': 1.7,
    're': 1.7, 'on': 1.6, 'at': 1.6, 'en': 1.5, 'nd': 1.5,
    'ti': 1.5, 'es': 1.4, 'or': 1.4, 'te': 1.4, 'of': 1.3,
    'ed': 1.3, 'is': 1.3, 'it': 1.2, 'al': 1.2, 'ar': 1.2,
    'st': 1.2, 'to': 1.1, 'nt': 1.1, 'ng': 1.1, 'se': 1.0,
    'ha': 1.0, 'as': 1.0, 'ou': 1.0, 'io': 1.0, 'le': 1.0,
}

# Constants for substitution algorithms and UI
MAX_CIPHER_SYMBOLS = 100  # Maximum cipher symbols to process
MAX_BIGRAMS_TO_ANALYZE = 20  # Maximum bigrams to analyze during refinement
MAX_UNDO_STACK_SIZE = 50  # Maximum undo stack entries
CONFIDENCE_HIGH_COLOR = '#90EE90'  # Light green for high confidence
CONFIDENCE_LOW_COLOR = '#FFB6C1'  # Light red/pink for low confidence

# ----------------------------
# UA Phonotactics Constants
# ----------------------------

# Ukrainian vowels and consonants
UA_VOWELS = set('аеиіоуяєюїАЕИІОУЯЄЮЇ')
UA_CONSONANTS = set('бвгґджзйклмнпрстфхцчшщьБВГҐДЖЗЙКЛМНПРСТФХЦЧШЩЬ')
UA_ALPHABET = UA_VOWELS | UA_CONSONANTS

# Target vowel ratio (≈41% vowels in Ukrainian text)
UA_VOWEL_RATIO_TARGET = 0.41
UA_VOWEL_RATIO_TOLERANCE = 0.08  # allowed deviation

# Default punctuation charset for ignore punctuation feature
# Basic punctuation: / ? ! , . : ; " ' ( ) [ ] { } - _
# Unicode dashes: — (em dash, U+2014), – (en dash, U+2013)
# Unicode quotes: « » „ " " ' ' (various quotation marks)
DEFAULT_PUNCT_CHARSET = set([
    '/', '?', '!', ',', '.', ':', ';', '"', "'", '(', ')', '[', ']', '{', '}', '-', '_',
    '\u2014',  # — em dash
    '\u2013',  # – en dash
    '\u00ab',  # « left-pointing double angle quotation mark
    '\u00bb',  # » right-pointing double angle quotation mark
    '\u201e',  # „ double low-9 quotation mark
    '\u201c',  # " left double quotation mark
    '\u201d',  # " right double quotation mark
    '\u2018',  # ' left single quotation mark
    '\u2019',  # ' right single quotation mark
])

# Human-readable representation for UI display
DEFAULT_PUNCT_DISPLAY = '/ ? ! , . : ; " \' ( ) [ ] { } - _'

# Common UA bigrams for scoring (expanded set for bonuses)
UA_COMMON_BIGRAMS = {
    'на': 2.0, 'он': 1.8, 'ст': 2.0, 'пр': 1.8, 'ро': 1.7,
    'за': 1.6, 'та': 1.6, 'ли': 1.5, 'ні': 1.5, 'ко': 1.6,
    'но': 1.6, 'ра': 1.5, 'по': 1.7, 'ва': 1.5, 'ен': 1.4,
    'ти': 1.5, 'ан': 1.4, 'ов': 1.4, 'ор': 1.3, 'не': 1.5,
    'ла': 1.3, 'ін': 1.3, 'ка': 1.3, 'ом': 1.2, 'ин': 1.2,
    'ат': 1.2, 'ер': 1.2, 'іс': 1.1, 'то': 1.4, 'во': 1.3,
}

# Common UA trigrams for scoring (bonuses)
UA_COMMON_TRIGRAMS = {
    'про': 2.5, 'при': 2.3, 'сто': 2.0, 'ник': 1.8, 'ани': 1.7,
    'енн': 2.2, 'ств': 1.9, 'ові': 1.6, 'ост': 1.8, 'ого': 1.7,
    'ння': 2.0, 'тис': 1.5, 'ком': 1.5, 'ина': 1.6, 'ьки': 1.5,
    'ати': 1.7, 'ити': 1.6, 'ова': 1.5, 'ськ': 1.8,  # removed duplicate 'ити'
}

# Forbidden patterns with penalties (higher = worse)
UA_FORBIDDEN_PATTERNS = {
    'ьь': 50.0,  # double soft sign is impossible
    'йй': 40.0,  # double й is invalid
    'щщ': 30.0,  # rare double щ
}

# Word-start penalty characters
UA_WORD_START_HEAVY_PENALTY = set('ьЬ')  # Ь cannot start a word
UA_WORD_START_STRONG_PENALTY = set('йЙ')  # Й rarely starts words
UA_WORD_START_SOFT_PENALTY = set('иєюїИЄЮЇ')  # these rarely start words


# ----------------------------
# Punctuation Strip Helper
# ----------------------------

def strip_punctuation(text: str, charset: Optional[set] = None) -> str:
    """
    Remove punctuation characters from text.
    If charset is None, uses DEFAULT_PUNCT_CHARSET.
    Preserves spacing and other characters.
    """
    if charset is None:
        charset = DEFAULT_PUNCT_CHARSET
    return ''.join(c for c in text if c not in charset)


def compute_char_freq(text: str) -> List[Tuple[str, int, float]]:
    """
    Compute frequency of each character in text.
    Returns list of (char, count, percentage) sorted by count descending.
    Only considers visible printable characters (excludes whitespace).
    """
    filtered = [c for c in text if c.isprintable() and not c.isspace()]
    if not filtered:
        return []
    counter = Counter(filtered)
    total = len(filtered)
    result = []
    for char, count in counter.most_common():
        pct = (count / total) * 100 if total > 0 else 0.0
        result.append((char, count, pct))
    return result


def compute_bigram_freq(text: str, top_n: int = 20) -> List[Tuple[str, int, float]]:
    """
    Compute frequency of bigrams (2-character pairs) in text.
    Returns list of (bigram, count, percentage) sorted by count descending.
    Only considers alphanumeric characters (letters and digits) in sequence.
    Note: Uses alphanumeric filter (stricter than char_freq) to focus on
    meaningful letter pairs for cryptanalysis.
    """
    filtered = [c for c in text if c.isalnum()]
    if len(filtered) < 2:
        return []
    bigrams = [''.join(pair) for pair in zip(filtered, filtered[1:])]
    counter = Counter(bigrams)
    total = len(bigrams)
    result = []
    for bg, count in counter.most_common(top_n):
        pct = (count / total) * 100 if total > 0 else 0.0
        result.append((bg, count, pct))
    return result


def _map_char_with_case(c: str, mapping: dict, ignore_punct: bool = False, punct_charset: Optional[set] = None) -> str:
    """
    Map a single non-digit character using mapping with case-aware behavior:
    - If ignore_punct is True and c is in punct_charset, return c unchanged.
    - Prefer exact key match (use value as-is).
    - Else try opposite-case key; if found and the value is a single alphabetic letter,
      adjust the output case to the input char's case.
    - If value is empty or not found, return original char.
    """
    # Safe-guard: leave punctuation unchanged when ignoring is enabled
    if ignore_punct:
        if punct_charset is None:
            punct_charset = DEFAULT_PUNCT_CHARSET
        if c in punct_charset:
            return c
    
    # Exact key first
    if c in mapping:
        v = mapping[c]
        if v == '':
            return c
        return v

    # Case-insensitive fallback (only if counterpart exists)
    if len(c) == 1 and c.isalpha():
        alt_key = c.swapcase()
        if alt_key in mapping:
            v = mapping[alt_key]
            if v == '':
                return c
            # If the mapped value is a single alpha, adjust case to source
            if isinstance(v, str) and len(v) == 1 and v.isalpha():
                return v.upper() if c.isupper() else v.lower()
            # Otherwise return as-is
            return v

    return c


def apply_substitution_mapping(text: str, mapping: dict, ignore_punct: bool = False) -> str:
    """
    Auto-select substitution method:
    - If mapping contains ANY numeric keys (tokens of digits), apply mixed token logic
      (supports 1- and 2-digit numeric tokens with longest-match-first + char mapping).
    - Otherwise, perform character substitution with case-aware behavior:
        * exact key match => use value as-is
        * else case-insensitive fallback with output case adjusted for single-letter mappings
    - If ignore_punct is True, punctuation characters are preserved unchanged.
    Note: This does not modify UI, only the substitution behavior.
    """
    if not mapping:
        return text

    has_numeric_keys = any(k.isdigit() for k in mapping.keys())
    if has_numeric_keys:
        return apply_mapping_mixed_tokens(text, mapping, ignore_punct=ignore_punct)

    # Character-only mapping with case-aware behavior
    out_chars: List[str] = []
    for ch in text:
        out_chars.append(_map_char_with_case(ch, mapping, ignore_punct=ignore_punct))
    return ''.join(out_chars)

# NEW: Mixed tokenization — supports 1- and 2-digit tokens in the same text
def tokenize_digits_with_mapping(text: str, mapping_keys: set) -> List[Tuple[str, bool]]:
    """
    Tokenize text into (token, is_digit_token) with longest-match-first for digits.
    - If mapping includes 2-digit numeric keys, always attempt a 2-digit match before single-digit.
    - Non-digit characters are preserved as single-character tokens.
    - Unmatched digits are preserved as tokens and do not break surrounding text.
    """
    tokens: List[Tuple[str, bool]] = []
    i = 0
    n = len(text)

    # Hints for matching strategy
    has_two_digit_keys = any(k.isdigit() and len(k) == 2 for k in mapping_keys)
    has_one_digit_keys = any(k.isdigit() and len(k) == 1 for k in mapping_keys)

    while i < n:
        ch = text[i]
        if ch.isdigit():
            # Longest-match-first: try 2-digit match if available
            if has_two_digit_keys and (i + 1 < n) and text[i + 1].isdigit():
                pair = text[i:i + 2]
                if pair in mapping_keys:
                    tokens.append((pair, True))
                    i += 2
                    continue
            # Fallback to single-digit token (mapped or not)
            tokens.append((ch, True))
            i += 1
        else:
            tokens.append((ch, False))
            i += 1
    return tokens

def apply_mapping_mixed_tokens(text: str, mapping: dict, ignore_punct: bool = False) -> str:
    """
    Apply a mixed substitution mapping:
    - Supports numeric tokens (1- or 2-digit) with longest-match-first.
    - Also supports character mapping (symbol -> symbol), case-aware as per _map_char_with_case.
    - Preserves punctuation and whitespace.
    - If ignore_punct is True, punctuation characters are preserved unchanged.
    - Unmatched tokens are preserved and do not break the rest of the text.
    """
    if not mapping:
        return text

    keys = set(mapping.keys())
    tokens = tokenize_digits_with_mapping(text, keys)

    out_parts: List[str] = []
    for tok, is_digit in tokens:
        if is_digit:
            # digits: only replace if exact key exists and value is not empty
            if tok in mapping and mapping[tok] != '':
                out_parts.append(mapping[tok])
            else:
                out_parts.append(tok)
        else:
            # non-digits: case-aware mapping with optional punctuation ignore
            out_parts.append(_map_char_with_case(tok, mapping, ignore_punct=ignore_punct))

    return ''.join(out_parts)

def detect_cipher_symbols(text: str) -> List[str]:
    """
    Detect distinct cipher symbols in text, sorted by frequency (most frequent first).
    Considers printable characters that are not whitespace.
    """
    filtered = [c for c in text if c.isprintable() and not c.isspace()]
    if not filtered:
        return []
    counter = Counter(filtered)
    # Return symbols sorted by frequency
    return [char for char, _ in counter.most_common()]


def suggest_mapping_by_frequency(units: List[str], unit_freq: dict, lang: str, limit: Optional[int] = None) -> dict:
    """
    Map cipher units (characters or tokens) by frequency to target language letters.
    """
    if lang == 'ua':
        ref_letters = [letter for letter, _ in UKRAINIAN_LETTER_FREQ]
    else:
        ref_letters = [letter for letter, _ in ENGLISH_LETTER_FREQ]
    if limit is None:
        num_to_map = min(len(units), MAX_CIPHER_SYMBOLS)
    else:
        num_to_map = min(limit, len(units), MAX_CIPHER_SYMBOLS)
    # Sort units by frequency
    sorted_units = sorted(unit_freq.items(), key=lambda x: x[1], reverse=True)
    mapping = {}
    for i in range(min(num_to_map, len(sorted_units))):
        unit = sorted_units[i][0]
        if i < len(ref_letters):
            mapping[unit] = ref_letters[i]
    return mapping


def compute_cipher_frequencies_lower(text: str) -> dict:
    """
    Compute normalized frequency of each character in text (lowercase).
    Returns dict of {char_lower: frequency} normalized to sum to 1.0.
    Only considers printable non-whitespace characters.
    """
    filtered = [c.lower() for c in text if c.isprintable() and not c.isspace()]
    if not filtered:
        return {}
    counter = Counter(filtered)
    total = len(filtered)
    return {char: count / total for char, count in counter.items()}


def compare_frequencies(cipher_freq: dict, lang_freq: dict) -> dict:
    """
    Compare cipher symbol frequencies to language letter frequencies.
    Maps cipher symbols (sorted by frequency desc) to language letters (sorted by frequency desc).
    Returns dict of {cipher_symbol: suggested_letter}.
    """
    # Sort cipher symbols by frequency (descending)
    cipher_sorted = sorted(cipher_freq.items(), key=lambda x: x[1], reverse=True)
    # Sort language letters by frequency (descending)
    lang_sorted = sorted(lang_freq.items(), key=lambda x: x[1], reverse=True)

    mapping = {}
    for i, (cipher_sym, _) in enumerate(cipher_sorted):
        if i < len(lang_sorted):
            mapping[cipher_sym] = lang_sorted[i][0]
    return mapping


def refine_with_bigrams(text: str, mapping: dict, bigrams: dict, conn_matrix: dict) -> dict:
    """
    Refine a mapping using bigram frequencies and connectivity scoring.
    Analyzes the ciphertext bigrams, applies the current mapping, and adjusts
    mappings based on how well they produce common target language bigrams.

    Returns a refined mapping dict.
    """
    if not mapping or not text:
        return mapping

    # Compute ciphertext bigrams (lowercase)
    filtered = [c.lower() for c in text if c.isalnum()]
    if len(filtered) < 2:
        return mapping

    cipher_bigrams = Counter([''.join(pair) for pair in zip(filtered, filtered[1:])])

    # Score the current mapping based on how well it produces common bigrams
    refined = dict(mapping)

    # For each pair of cipher symbols that appear together frequently,
    # check if their mapped values form a common bigram in the target language
    top_cipher_bigrams = cipher_bigrams.most_common(MAX_BIGRAMS_TO_ANALYZE)

    for cipher_bg, count in top_cipher_bigrams:
        if len(cipher_bg) != 2:
            continue
        c1, c2 = cipher_bg[0], cipher_bg[1]

        # Get current mapped values
        m1 = refined.get(c1, c1)
        m2 = refined.get(c2, c2)
        mapped_bg = (m1 + m2).lower()

        # Check connectivity score
        conn_score = conn_matrix.get(mapped_bg, 0)
        bigram_score = bigrams.get(mapped_bg, 0)

        # If the mapped bigram is common, increase confidence (no change needed)
        # If not, this could indicate a need for swap, but we keep it simple
        # Advanced: could try swapping mappings to improve bigram match rate

    return refined


def auto_suggest_substitution(text: str, lang: str) -> dict:
    """
    AutoSuggest pipeline for monoalphabetic substitution cipher.
    (Старий базовий варіант залишено для швидкого наближення; глибший hillclimb нижче.)
    """
    if not text or not text.strip():
        return {}
    cipher_symbols = detect_cipher_symbols(text)
    if not cipher_symbols:
        return {}
    cipher_symbols = cipher_symbols[:MAX_CIPHER_SYMBOLS]
    cipher_freq = compute_cipher_frequencies_lower(text)
    if lang == 'ua':
        lang_freq = ukr_letter_freq
        bigrams = ukr_bigrams
    else:
        lang_freq = en_letter_freq
        bigrams = en_bigrams
    base_mapping = compare_frequencies(cipher_freq, lang_freq)
    refined_mapping = refine_with_bigrams(text, base_mapping, bigrams, connectivity_matrix)
    final_mapping = {}
    for orig_sym in cipher_symbols:
        lower_sym = orig_sym.lower()
        if lower_sym in refined_mapping:
            final_mapping[orig_sym] = refined_mapping[lower_sym].upper()
    return final_mapping

def tokenize_text_two_digit_mode(text: str) -> List[Tuple[str, bool]]:
    """
    Two-digit mode tokenizer:
    - Group consecutive digits into 2-digit tokens (pairs) with a possible trailing single digit.
      Example: '12345' -> ['12','34','5']
    - Non-digit characters are preserved as single-character tokens.
    - This is a grouping hint mode for UI; mixed logic is still handled at apply time.
    """
    tokens: List[Tuple[str, bool]] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch.isdigit():
            j = i
            while j < n and text[j].isdigit():
                j += 1
            run = text[i:j]
            k = 0
            # group into pairs
            while k + 2 <= len(run):
                tokens.append((run[k:k + 2], True))
                k += 2
            if k < len(run):
                tokens.append((run[k], True))
            i = j
        else:
            tokens.append((ch, False))
            i += 1
    return tokens

def detokenize_apply_mapping(text: str, mapping: dict, use_two_digit_mode: bool, ignore_punct: bool = False) -> str:
    """
    Central dispatcher for applying mapping, honoring the UI 'use_two_digit_mode':
    - If mapping is empty -> return input as-is.
    - If use_two_digit_mode is True:
        * Tokenize digits into pairs (with trailing single digit) via tokenize_text_two_digit_mode.
        * Replace digit tokens by mapping values when present.
        * Also apply character mapping (case-aware) to non-digit tokens.
    - If use_two_digit_mode is False:
        * If mapping contains numeric keys, apply full mixed logic
          (tokenize_digits_with_mapping + longest-match-first + char mapping).
        * Else, perform character-only mapping (case-aware).
    - If ignore_punct is True, punctuation characters are preserved unchanged.
    In all modes, unmatched tokens are preserved and punctuation/spacing is kept intact.
    """
    if not mapping:
        return text

    has_numeric_keys = any(k.isdigit() for k in mapping.keys())

    if use_two_digit_mode:
        # Two-digit token mode: pair grouping + character mapping
        tokens = tokenize_text_two_digit_mode(text)
        out_parts: List[str] = []
        for tok, is_digit in tokens:
            if is_digit and tok in mapping and mapping[tok] != '':
                out_parts.append(mapping[tok])
            elif is_digit:
                out_parts.append(tok)
            else:
                out_parts.append(_map_char_with_case(tok, mapping, ignore_punct=ignore_punct))
        return ''.join(out_parts)

    # Not two-digit mode
    if has_numeric_keys:
        # Mixed-mode with longest-match-first digit handling + char mapping
        return apply_mapping_mixed_tokens(text, mapping, ignore_punct=ignore_punct)

    # Character-only mapping
    return apply_substitution_mapping(text, mapping, ignore_punct=ignore_punct)

def compute_token_freq(tokens: List[Tuple[str, bool]]) -> List[Tuple[str, int, float]]:
    """Frequency of digit tokens only in two-digit mode."""
    digit_tokens = [t for t, is_digit in tokens if is_digit]
    if not digit_tokens:
        return []
    counter = Counter(digit_tokens)
    total = len(digit_tokens)
    return [(tok, cnt, (cnt / total) * 100 if total else 0.0) for tok, cnt in counter.most_common()]

def compute_token_bigram_freq(tokens: List[Tuple[str, bool]], top_n: int = 20) -> List[Tuple[str, int, float]]:
    """Bigram frequencies over consecutive digit tokens only."""
    digit_tokens = [t for t, is_digit in tokens if is_digit]
    if len(digit_tokens) < 2:
        return []
    bigrams = ['{}{}'.format(a, b) for a, b in zip(digit_tokens, digit_tokens[1:])]
    counter = Counter(bigrams)
    total = len(bigrams)
    result = []
    for bg, count in counter.most_common(top_n):
        pct = (count / total) * 100 if total > 0 else 0.0
        result.append((bg, count, pct))
    return result


def compute_cipher_bigram_freq_table(text: str, mapping: dict, use_two_digit: bool, top_n: int = 15) -> List[dict]:
    """
    Compute cipher numeric-token bigram frequency table with mapped plaintext bigrams and connectivity scores.
    Returns a list of dicts with keys: cipher_bigram, count, pct, mapped_bigram, connectivity_score
    """
    if use_two_digit:
        tokens = tokenize_text_two_digit_mode(text)
        digit_tokens = [t for t, is_digit in tokens if is_digit]
    else:
        # Extract consecutive digit sequences as tokens
        digit_tokens = []
        current_num = ""
        for c in text:
            if c.isdigit():
                current_num += c
            else:
                if current_num:
                    digit_tokens.append(current_num)
                    current_num = ""
        if current_num:
            digit_tokens.append(current_num)
    
    if len(digit_tokens) < 2:
        return []
    
    # Compute cipher bigrams
    cipher_bigrams = [(digit_tokens[i], digit_tokens[i+1]) for i in range(len(digit_tokens) - 1)]
    counter = Counter(cipher_bigrams)
    total = len(cipher_bigrams)
    
    result = []
    for (tok1, tok2), count in counter.most_common(top_n):
        cipher_bg_str = f"{tok1}-{tok2}"
        pct = (count / total) * 100 if total > 0 else 0.0
        
        # Get mapped letters
        mapped1 = mapping.get(tok1, '?')
        mapped2 = mapping.get(tok2, '?')
        mapped_bg = (mapped1 + mapped2).lower()
        
        # Compute connectivity score against UA bigram model
        conn_score = UA_COMMON_BIGRAMS.get(mapped_bg, 0.0)
        if conn_score == 0:
            conn_score = ukr_bigrams.get(mapped_bg, 0.0) * 10  # Scale for visibility
        
        result.append({
            'cipher_bigram': cipher_bg_str,
            'count': count,
            'pct': pct,
            'mapped_bigram': mapped_bg.upper(),
            'connectivity_score': conn_score
        })
    
    return result


def compute_plaintext_bigram_freq_table(plaintext: str, top_n: int = 15) -> List[dict]:
    """
    Compute mapped plaintext bigram frequency table with connectivity scores.
    Returns a list of dicts with keys: bigram, count, pct, connectivity_score
    """
    filtered = [c.lower() for c in plaintext if c.isalpha()]
    if len(filtered) < 2:
        return []
    
    bigrams = [''.join(pair) for pair in zip(filtered, filtered[1:])]
    counter = Counter(bigrams)
    total = len(bigrams)
    
    result = []
    for bg, count in counter.most_common(top_n):
        pct = (count / total) * 100 if total > 0 else 0.0
        
        # Compute connectivity score against UA bigram model
        conn_score = UA_COMMON_BIGRAMS.get(bg, 0.0)
        if conn_score == 0:
            conn_score = ukr_bigrams.get(bg, 0.0) * 10  # Scale for visibility
        
        result.append({
            'bigram': bg.upper(),
            'count': count,
            'pct': pct,
            'connectivity_score': conn_score
        })
    
    return result


def format_connectivity_table(cipher_table: List[dict], plain_table: List[dict]) -> str:
    """
    Format bigram connectivity tables for display.
    Returns a formatted string with both tables.
    """
    lines = []
    
    # Cipher token bigram table
    lines.append("=== Cipher Token Bigrams ===")
    lines.append(f"{'Tokens':10} {'Count':6} {'%':6} {'Mapped':8} {'UA Score':8}")
    lines.append("-" * 42)
    for entry in cipher_table:
        score_str = f"{entry['connectivity_score']:.1f}" if entry['connectivity_score'] > 0 else "-"
        lines.append(f"{entry['cipher_bigram']:10} {entry['count']:6} {entry['pct']:5.1f}% {entry['mapped_bigram']:8} {score_str:8}")
    
    lines.append("")
    
    # Plaintext bigram table
    lines.append("=== Plaintext Bigrams ===")
    lines.append(f"{'Bigram':8} {'Count':6} {'%':6} {'UA Score':8}")
    lines.append("-" * 32)
    for entry in plain_table:
        score_str = f"{entry['connectivity_score']:.1f}" if entry['connectivity_score'] > 0 else "-"
        lines.append(f"{entry['bigram']:8} {entry['count']:6} {entry['pct']:5.1f}% {score_str:8}")
    
    return '\n'.join(lines)


def export_mapping_report(mapping: dict, text: str, plaintext: str, use_two_digit: bool, filepath: str, format: str = 'txt'):
    """
    Export number→letter correspondence report to file.
    Supports TXT and CSV formats.
    """
    if format.lower() == 'csv':
        lines = ['Cipher,Plain']
        for cipher, plain in sorted(mapping.items()):
            lines.append(f'"{cipher}","{plain}"')
        
        # Add bigram connectivity section
        lines.append('')
        lines.append('Cipher Bigram,Count,Pct,Mapped Bigram,UA Score')
        cipher_table = compute_cipher_bigram_freq_table(text, mapping, use_two_digit)
        for entry in cipher_table:
            lines.append(f'"{entry["cipher_bigram"]}",{entry["count"]},{entry["pct"]:.1f},"{entry["mapped_bigram"]}",{entry["connectivity_score"]:.1f}')
        
        content = '\n'.join(lines)
    else:  # TXT format
        lines = []
        lines.append("=" * 50)
        lines.append("SUBSTITUTION MAPPING REPORT")
        lines.append("=" * 50)
        lines.append("")
        
        # Mapping table
        lines.append("--- Number → Letter Mapping ---")
        lines.append(f"{'Cipher':10} {'Plain':10}")
        lines.append("-" * 22)
        for cipher, plain in sorted(mapping.items()):
            lines.append(f"{cipher:10} {plain:10}")
        
        lines.append("")
        
        # Bigram connectivity
        cipher_table = compute_cipher_bigram_freq_table(text, mapping, use_two_digit)
        plain_table = compute_plaintext_bigram_freq_table(plaintext)
        lines.append(format_connectivity_table(cipher_table, plain_table))
        
        content = '\n'.join(lines)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def detect_cipher_symbols_tokens(tokens: List[Tuple[str, bool]]) -> List[str]:
    """Return distinct digit tokens sorted by frequency."""
    counter = Counter([t for t, is_digit in tokens if is_digit])
    return [tok for tok, _ in counter.most_common()]

def serialize_mapping(mapping: dict) -> str:
    """Serialize mapping dict to JSON string."""
    return json.dumps({"mapping": mapping}, ensure_ascii=False, indent=2)


def deserialize_mapping(s: str) -> dict:
    """Deserialize JSON string to mapping dict. Raises ValueError on invalid JSON."""
    try:
        data = json.loads(s)
        if isinstance(data, dict) and "mapping" in data:
            return data["mapping"]
        elif isinstance(data, dict):
            # Try to use data directly as mapping
            return data
        else:
            raise ValueError("Invalid mapping format")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

def _apply_mapping_fast(text: str, mapping: dict) -> str:
    """Швидке застосування заміни (лише односимвольні ключі)."""
    if not mapping:
        return text
    table = str.maketrans(mapping)
    return text.translate(table)

def _build_bigram_model(lang: str):
    """Повертає bigram частоти (у нижньому регістрі)."""
    if lang == 'ua':
        return ukr_bigrams
    return en_bigrams

def _build_letter_freq_model(lang: str):
    if lang == 'ua':
        return ukr_letter_freq
    return en_letter_freq

def _subst_score_plaintext(plain: str, bigram_model: dict, letter_model: dict,
                           smoothing: float = 1e-6, lang: str = 'ua') -> float:
    """
    Enhanced UA-aware scoring for substitution plaintext quality.
    
    Combines:
    - Chi-squared letter frequency deviation
    - Bigram log-probabilities  
    - Vowel/consonant ratio penalty (≈41% vowels target)
    - Forbidden pattern penalties (ЬЬ, ЙЙ, 4+ repeated same letter, 5+ consonants)
    - Word-start penalties (Ь heavy, Й strong, И/Є/Ю/Ї soft)
    - Syllable shape rewards (CV, VC) and penalties (VV)
    - Common bigram and trigram bonuses
    
    Returns a score (higher = better).
    """
    filtered = [c.lower() for c in plain if c.isalpha()]
    score = 0.0
    
    if not filtered:
        return float('-inf')
    
    N = len(filtered)
    counts = Counter(filtered)
    
    # 1. Chi-squared letter frequency deviation
    chi2 = 0.0
    for ltr, expected in letter_model.items():
        obs = counts.get(ltr, 0)
        exp = expected * N
        if exp > 0:
            chi2 += (obs - exp) ** 2 / exp
    score -= 0.5 * chi2
    
    # 2. Bigram log-probabilities
    bigrams = [''.join(pair) for pair in zip(filtered, filtered[1:])]
    for bg in bigrams:
        p = bigram_model.get(bg, smoothing)
        score += math.log(p)
    
    # UA-specific scoring (only for Ukrainian)
    if lang == 'ua':
        # 3. Vowel/consonant ratio penalty
        vowel_count = sum(1 for c in filtered if c in UA_VOWELS or c.upper() in UA_VOWELS)
        vowel_ratio = vowel_count / N if N > 0 else 0.5
        ratio_deviation = abs(vowel_ratio - UA_VOWEL_RATIO_TARGET)
        if ratio_deviation > UA_VOWEL_RATIO_TOLERANCE:
            score -= (ratio_deviation - UA_VOWEL_RATIO_TOLERANCE) * 30.0
        
        # 4. Forbidden pattern penalties
        text_lower = ''.join(filtered)
        for pattern, penalty in UA_FORBIDDEN_PATTERNS.items():
            if pattern in text_lower:
                score -= penalty * text_lower.count(pattern)
        
        # 4b. Repeated letter penalties (4+ same letter in a row)
        max_repeat = 1
        current_repeat = 1
        for i in range(1, len(filtered)):
            if filtered[i] == filtered[i-1]:
                current_repeat += 1
                max_repeat = max(max_repeat, current_repeat)
            else:
                current_repeat = 1
        if max_repeat >= 4:
            score -= (max_repeat - 3) * 15.0
        
        # 4c. Consonant run penalties (5+ consonants severe, 4 consonants light)
        max_cc_run = 0
        cc_run = 0
        for c in filtered:
            if c in UA_CONSONANTS or c.upper() in UA_CONSONANTS:
                cc_run += 1
                max_cc_run = max(max_cc_run, cc_run)
            else:
                cc_run = 0
        if max_cc_run >= 5:
            score -= (max_cc_run - 4) * 12.0
        elif max_cc_run == 4:
            score -= 3.0  # light penalty for 4 consonants
        
        # 5. Word-start penalties (check after spaces or at text start)
        words = plain.split()
        for word in words:
            if not word:
                continue
            first_char = word[0]
            if first_char in UA_WORD_START_HEAVY_PENALTY:
                score -= 25.0  # Ь cannot start a word
            elif first_char in UA_WORD_START_STRONG_PENALTY:
                score -= 10.0  # Й rarely starts words
            elif first_char in UA_WORD_START_SOFT_PENALTY:
                score -= 2.0   # soft penalty for less common starters
        
        # 6. Syllable shape rewards/penalties (CV = good, VC = ok, VV = bad, CC = moderate)
        def is_vowel(c):
            return c in UA_VOWELS or c.upper() in UA_VOWELS
        
        for i in range(len(filtered) - 1):
            c1_v = is_vowel(filtered[i])
            c2_v = is_vowel(filtered[i+1])
            if not c1_v and c2_v:  # CV pattern (consonant-vowel)
                score += 0.3
            elif c1_v and not c2_v:  # VC pattern
                score += 0.15
            elif c1_v and c2_v:  # VV pattern (less common)
                score -= 0.2
            # CC pattern gets no adjustment (moderate)
        
        # 7. Common UA bigram bonuses
        for bg in bigrams:
            if bg in UA_COMMON_BIGRAMS:
                score += UA_COMMON_BIGRAMS[bg]
        
        # 8. Common UA trigram bonuses
        for i in range(len(filtered) - 2):
            trigram = ''.join(filtered[i:i+3])
            if trigram in UA_COMMON_TRIGRAMS:
                score += UA_COMMON_TRIGRAMS[trigram]
    
    return score


def _compute_plaintext_diagnostics(plain: str, lang: str = 'ua') -> dict:
    """
    Compute diagnostic metrics for plaintext quality.
    Returns dict with keys: vowel_ratio, bad_repeats, max_cc_run, word_start_issues
    """
    filtered = [c.lower() for c in plain if c.isalpha()]
    if not filtered:
        return {'vowel_ratio': 0.0, 'bad_repeats': 0, 'max_cc_run': 0, 'word_start_issues': 0}
    
    N = len(filtered)
    
    # Vowel ratio
    vowel_count = sum(1 for c in filtered if c in UA_VOWELS or c.upper() in UA_VOWELS)
    vowel_ratio = (vowel_count / N * 100) if N > 0 else 0.0
    
    # Repeated letter count (4+ repeats)
    bad_repeats = 0
    current_repeat = 1
    for i in range(1, len(filtered)):
        if filtered[i] == filtered[i-1]:
            current_repeat += 1
        else:
            if current_repeat >= 4:
                bad_repeats += 1
            current_repeat = 1
    if current_repeat >= 4:
        bad_repeats += 1
    
    # Max consonant run
    max_cc_run = 0
    cc_run = 0
    for c in filtered:
        if c in UA_CONSONANTS or c.upper() in UA_CONSONANTS:
            cc_run += 1
            max_cc_run = max(max_cc_run, cc_run)
        else:
            cc_run = 0
    
    # Word start issues
    word_start_issues = 0
    words = plain.split()
    for word in words:
        if word and word[0] in (UA_WORD_START_HEAVY_PENALTY | UA_WORD_START_STRONG_PENALTY):
            word_start_issues += 1
    
    return {
        'vowel_ratio': vowel_ratio,
        'bad_repeats': bad_repeats,
        'max_cc_run': max_cc_run,
        'word_start_issues': word_start_issues
    }

def _random_initial_mapping(cipher_symbols: list, target_letters: list, rng: random.Random) -> dict:
    """
    Створює випадковий початковий mapping (букви тупо переставляються).
    """
    m = {}
    shuffled = target_letters[:]
    rng.shuffle(shuffled)
    limit = min(len(cipher_symbols), len(shuffled))
    for i in range(limit):
        m[cipher_symbols[i]] = shuffled[i]
    return m

def _initial_frequency_mapping(cipher_symbols: list, cipher_freq: dict, letter_model: dict) -> dict:
    """
    Початковий mapping за частотами (cipher freq desc → letter freq desc).
    """
    c_sorted = sorted(cipher_freq.items(), key=lambda x: x[1], reverse=True)
    l_sorted = sorted(letter_model.items(), key=lambda x: x[1], reverse=True)
    mapping = {}
    for i, (sym, _) in enumerate(c_sorted):
        if i < len(l_sorted):
            mapping[sym] = l_sorted[i][0].upper()
    return mapping


def _frequency_seeded_mapping(cipher_symbols: list, cipher_freq: dict, lang: str = 'ua') -> dict:
    """
    Create frequency-seeded initial mapping using UA phonotactics:
    - Very high frequency tokens → vowels (О, А, Н, І, Е)
    - High frequency → common consonants (Н, Т, Р, С, Л, В)
    - Medium frequency → L/K/M/D/P/U type consonants
    - Low frequency → rare consonants (Ф, Щ, Ь, Ц, Ж, Х)
    """
    if lang != 'ua':
        # For non-UA, fall back to simple frequency mapping
        letter_model = _build_letter_freq_model(lang)
        return _initial_frequency_mapping(cipher_symbols, cipher_freq, letter_model)
    
    # Create a set of lowercase cipher symbols for comparison
    cipher_symbols_lower = set(s.lower() for s in cipher_symbols)
    
    # Ukrainian vowels by frequency
    ua_vowels_freq = ['о', 'а', 'і', 'е', 'и', 'у', 'я', 'ю', 'є', 'ї']
    # Ukrainian consonants by frequency tiers
    ua_cons_high = ['н', 'в', 'р', 'т', 'с', 'к']  # very common
    ua_cons_mid = ['л', 'д', 'п', 'м', 'б', 'з', 'г', 'ч']  # medium
    ua_cons_low = ['й', 'х', 'ц', 'ж', 'ш', 'щ', 'ф', 'ь', 'ґ']  # rare
    
    # Sort cipher symbols by frequency
    c_sorted = sorted(cipher_freq.items(), key=lambda x: x[1], reverse=True)
    
    mapping = {}
    used_letters = set()
    vowel_idx, cons_high_idx, cons_mid_idx, cons_low_idx = 0, 0, 0, 0
    
    for i, (sym, freq) in enumerate(c_sorted):
        # Check if symbol (lowercase) is in our cipher symbols
        if sym.lower() not in cipher_symbols_lower:
            continue
        
        # Assign based on frequency percentile
        percentile = i / max(1, len(c_sorted))
        
        if percentile < 0.15:  # Top 15% → vowels
            if vowel_idx < len(ua_vowels_freq):
                ltr = ua_vowels_freq[vowel_idx]
                if ltr not in used_letters:
                    mapping[sym] = ltr.upper()
                    used_letters.add(ltr)
                    vowel_idx += 1
                    continue
        
        if percentile < 0.35:  # 15-35% → high frequency consonants
            if cons_high_idx < len(ua_cons_high):
                ltr = ua_cons_high[cons_high_idx]
                if ltr not in used_letters:
                    mapping[sym] = ltr.upper()
                    used_letters.add(ltr)
                    cons_high_idx += 1
                    continue
        
        if percentile < 0.65:  # 35-65% → medium consonants
            if cons_mid_idx < len(ua_cons_mid):
                ltr = ua_cons_mid[cons_mid_idx]
                if ltr not in used_letters:
                    mapping[sym] = ltr.upper()
                    used_letters.add(ltr)
                    cons_mid_idx += 1
                    continue
        
        # Remaining → low frequency consonants
        if cons_low_idx < len(ua_cons_low):
            ltr = ua_cons_low[cons_low_idx]
            if ltr not in used_letters:
                mapping[sym] = ltr.upper()
                used_letters.add(ltr)
                cons_low_idx += 1
                continue
        
        # Fallback: any remaining letter
        all_letters = ua_vowels_freq + ua_cons_high + ua_cons_mid + ua_cons_low
        for ltr in all_letters:
            if ltr not in used_letters:
                mapping[sym] = ltr.upper()
                used_letters.add(ltr)
                break
    
    return mapping


def _refine_mapping_via_swaps(mapping: dict, rng: random.Random) -> dict:
    """Випадково міняє місцями дві літери в mapping (для hillclimb)."""
    if len(mapping) < 2:
        return mapping
    keys = list(mapping.keys())
    k1, k2 = rng.sample(keys, 2)
    new_map = mapping.copy()
    new_map[k1], new_map[k2] = new_map[k2], new_map[k1]
    return new_map


def _token_aware_swap(mapping: dict, rng: random.Random, cross_swap_prob: float = 0.1) -> dict:
    """
    Token-aware selective swap for hillclimb.
    - Primarily swaps within digit-token mappings or char mappings
    - Occasionally (cross_swap_prob) swaps across types to escape local minima
    """
    if len(mapping) < 2:
        return mapping
    
    keys = list(mapping.keys())
    digit_keys = [k for k in keys if k.isdigit()]
    char_keys = [k for k in keys if not k.isdigit()]
    
    new_map = mapping.copy()
    
    # Occasionally do cross-swap
    if rng.random() < cross_swap_prob and digit_keys and char_keys:
        k1 = rng.choice(digit_keys)
        k2 = rng.choice(char_keys)
        new_map[k1], new_map[k2] = new_map[k2], new_map[k1]
        return new_map
    
    # Prefer swapping within same type
    if digit_keys and len(digit_keys) >= 2 and (not char_keys or rng.random() < 0.7):
        k1, k2 = rng.sample(digit_keys, 2)
    elif char_keys and len(char_keys) >= 2:
        k1, k2 = rng.sample(char_keys, 2)
    else:
        # Fallback to any two keys
        k1, k2 = rng.sample(keys, 2)
    
    new_map[k1], new_map[k2] = new_map[k2], new_map[k1]
    return new_map


def subst_hillclimb(cipher_text: str, lang: str = 'ua',
                    iterations: int = 5000, restarts: int = 5,
                    smoothing: float = 1e-6, temp_start: float = 1.0,
                    temp_decay: float = 0.0003, seed: int | None = None,
                    early_stop_threshold: int = 800) -> tuple[dict, str, float]:
    """
    Enhanced Hill-Climb + Simulated Annealing for substitution cipher solving.
    
    Features:
    - Frequency-seeded initial mapping (UA phonotactics aware)
    - Multi-start with seeded + random + bigram-biased initializations
    - Token-aware selective swaps with occasional cross-swaps
    - Early-stopping on stagnation
    - UA-aware scoring with phonotactic penalties/bonuses
    
    Returns (best_mapping, best_plaintext, best_score).
    """
    if not cipher_text.strip():
        return {}, "", float('-inf')

    rng = random.Random(seed)
    bigram_model = _build_bigram_model(lang)
    letter_model = _build_letter_freq_model(lang)

    cipher_symbols = detect_cipher_symbols(cipher_text)
    cipher_symbols = cipher_symbols[:MAX_CIPHER_SYMBOLS]
    cipher_freq = compute_cipher_frequencies_lower(cipher_text)

    # Набір можливих цільових літер
    if lang == 'ua':
        target_letters_order = [ltr.lower() for ltr, _ in UKRAINIAN_LETTER_FREQ]
    else:
        target_letters_order = [ltr.lower() for ltr, _ in ENGLISH_LETTER_FREQ]
    target_letters_order = target_letters_order[:max(len(cipher_symbols), len(target_letters_order))]

    best_global_map = {}
    best_global_score = float('-inf')
    best_global_plain = ""

    for r in range(restarts):
        # Multi-start strategy: alternate between different initialization methods
        if r == 0:
            # First restart: frequency-seeded mapping (UA-aware)
            base_map = _frequency_seeded_mapping(cipher_symbols, cipher_freq, lang)
        elif r == 1:
            # Second restart: standard frequency mapping
            base_map = _initial_frequency_mapping(cipher_symbols, cipher_freq, letter_model)
        elif r % 3 == 0:
            # Every third restart: random mapping
            base_map = _random_initial_mapping(cipher_symbols, target_letters_order, rng)
        else:
            # Other restarts: frequency with random perturbation
            base_map = _initial_frequency_mapping(cipher_symbols, cipher_freq, letter_model)
            # Add some random swaps to perturb
            for _ in range(rng.randint(2, 5)):
                base_map = _refine_mapping_via_swaps(base_map, rng)
        
        # Ensure all cipher symbols are covered
        used_letters = set(l.lower() for l in base_map.values() if l)
        for sym in cipher_symbols:
            if sym not in base_map or not base_map[sym]:
                for ltr in target_letters_order:
                    if ltr not in used_letters:
                        base_map[sym] = ltr.upper()
                        used_letters.add(ltr)
                        break

        current_map = base_map
        current_plain = apply_substitution_mapping(cipher_text, current_map)
        current_score = _subst_score_plaintext(current_plain, bigram_model, letter_model, smoothing, lang)

        temp = temp_start
        stagnation_count = 0
        last_improvement_score = current_score

        for it in range(iterations):
            # Use token-aware swap for better exploration
            if rng.random() < 0.3:
                candidate_map = _token_aware_swap(current_map, rng, cross_swap_prob=0.15)
            else:
                candidate_map = _refine_mapping_via_swaps(current_map, rng)
            
            candidate_plain = apply_substitution_mapping(cipher_text, candidate_map)
            candidate_score = _subst_score_plaintext(candidate_plain, bigram_model, letter_model, smoothing, lang)

            accept = False
            if candidate_score > current_score:
                accept = True
                stagnation_count = 0
                last_improvement_score = candidate_score
            else:
                # Probabilistic acceptance (simulated annealing)
                delta = candidate_score - current_score
                prob = math.exp(delta / max(temp, 1e-9))
                if rng.random() < prob:
                    accept = True
                stagnation_count += 1

            if accept:
                current_map = candidate_map
                current_score = candidate_score
                current_plain = candidate_plain

                if current_score > best_global_score:
                    best_global_map = current_map
                    best_global_score = current_score
                    best_global_plain = current_plain

            temp = max(0.0001, temp - temp_decay)
            
            # Early stopping on stagnation
            if stagnation_count >= early_stop_threshold:
                break

    return best_global_map, best_global_plain, best_global_score


if MATPLOTLIB_AVAILABLE:
    def create_and_render_chart(freq_items: List[Tuple[str, int, float]], title: str, palette: dict) -> Figure:
        """Helper to create a matplotlib bar chart figure."""

        fig = Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)

        # Limit to top 30/20 items for plotting
        if "Char" in title or "Символ" in title:
            freq_items = freq_items[:30]
        elif "Bigram" in title or "Біграм" in title:
            freq_items = freq_items[:20]

        units = [u for (u, _, _) in freq_items]
        counts = [c for (_, c, _) in freq_items]

        # Use theme colors
        app_bg = palette.get('app_bg', 'gray')
        frame_bg = palette.get('frame_bg', 'white')
        button_fg = palette.get('button_fg', 'lightblue')
        text_color = palette.get('text_color', 'black')

        # Set figure colors
        fig.patch.set_facecolor(frame_bg)
        ax.set_facecolor(app_bg)
        ax.tick_params(colors=text_color)
        ax.yaxis.label.set_color(text_color)
        ax.xaxis.label.set_color(text_color)
        ax.title.set_color(text_color)

        # Bar chart
        ax.bar(units, counts, color=button_fg)
        ax.set_title(title)
        ax.set_xlabel('Unit')
        ax.set_ylabel('Count')
        ax.tick_params(axis='x', rotation=60, labelsize=8)
        fig.tight_layout()
        return fig
else:
    def create_and_render_chart(*args, **kwargs):
        return None

def _use_mixed_token_mode(self, mapping: dict) -> bool:
    """Checks if mapping contains both 1-digit and 2-digit numeric keys."""
    has_two_digit_num = any(k.isdigit() and len(k) == 2 for k in mapping)
    has_one_digit_num = any(k.isdigit() and len(k) == 1 for k in mapping)
    return has_two_digit_num and has_one_digit_num

def _render_subst_charts(self, char_freq, bigram_freq):
    """Creates and embeds the frequency charts."""
    if not MATPLOTLIB_AVAILABLE:
        return

    lang = LANG_STRINGS[self.current_lang.get()]
    current_palette = self.app_settings # Assuming app_settings holds the current theme palette

    # Clear old canvases
    for canvas in [self.subst_char_canvas, self.subst_bigram_canvas]:
        if canvas and canvas.get_tk_widget().winfo_exists():
            canvas.get_tk_widget().destroy()

    # 1. Character Chart
    self.subst_char_fig = create_and_render_chart(char_freq, lang["subst_freq_chars_label"], current_palette)
    if self.subst_char_fig:
        self.subst_char_canvas = FigureCanvasTkAgg(self.subst_char_fig, master=self.subst_freq_chars_frame)
        self.subst_char_canvas.draw()
        self.subst_char_canvas.get_tk_widget().pack(fill="both", expand=True)
        self.subst_freq_chars_textbox.grid_remove() # Hide textbox if chart is shown
    else:
        self.subst_freq_chars_textbox.grid() # Show textbox fallback

    # 2. Bigram Chart
    self.subst_bigram_fig = create_and_render_chart(bigram_freq, lang["subst_freq_bigrams_label"], current_palette)
    if self.subst_bigram_fig:
        self.subst_bigram_canvas = FigureCanvasTkAgg(self.subst_bigram_fig, master=self.subst_freq_bigrams_frame)
        self.subst_bigram_canvas.draw()
        self.subst_bigram_canvas.get_tk_widget().pack(fill="both", expand=True)
        self.subst_freq_bigrams_textbox.grid_remove() # Hide textbox if chart is shown
    else:
        self.subst_freq_bigrams_textbox.grid() # Show textbox fallback

class StegoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.all_widgets = []

        self.current_lang = ctk.StringVar(value="ua")
        self.current_lang.trace_add("write", self.change_language)

        self.geometry("1100x760")
        self.title(LANG_STRINGS[self.current_lang.get()]["title"])

        # file paths and PIL image caches
        self.xor_image_path1 = None
        self.xor_image_path2 = None
        self.lsb_image_path = None
        self.picker_pil_image = None
        self.ela_image_path = None

        self.subst_char_fig = None
        self.subst_char_canvas = None
        self.subst_bigram_fig = None
        self.subst_bigram_canvas = None

        # PIL caches
        self.xor_pil1 = None
        self.xor_pil2 = None
        self.xor_result_pil = None
        self.lsb_original_pil = None
        self.lsb_result_pil = None
        self.ela_original_pil = None
        self.ela_result_pil = None

        # crypto fields
        self.aes_cipher_text_b64 = ""
        self.sdes_cipher_bytes = b""

        self.vigenere_mode = ctk.StringVar(value=LANG_STRINGS[self.current_lang.get()]["vigenere_mode_decrypt"])
        self.base64_mode = ctk.StringVar(value=LANG_STRINGS[self.current_lang.get()]["base64_mode_encode"])

        # Substitution undo/redo stacks
        self.subst_undo_stack = []
        self.subst_redo_stack = []

        self.logo_image = None
        self._resize_after_id = None
        self._self_destruct_running = False

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_nav_frame()
        self.setup_content_frames()

        # initial population of labels/buttons — ensure all widgets get correct texts
        self.update_all_texts(self.current_lang.get())
        self.update_aes_texts()
        self.update_sdes_texts()
        self.update_vigenere_labels()
        self.update_base64_labels()

        # logo and theme
        self.load_network_logo()
        # apply theme after a short delay so CTk widgets exist; still ensure texts applied above
        self.after(50, lambda: self.apply_theme_by_name("Нічна Прохолода"))

        # show default frame
        self.show_xor_frame()

        self.change_language()
        self.update_aes_texts()
        self.update_sdes_texts()
        self.update_vigenere_labels()
        self.update_base64_labels()

        self.bind("<Configure>", self.on_main_resize)

    def _create_widget(self, widget_class, *args, **kwargs):
        widget = widget_class(*args, **kwargs)
        if isinstance(widget,
                      (ctk.CTkFrame, ctk.CTkButton, ctk.CTkLabel, ctk.CTkOptionMenu, ctk.CTkTextbox, ctk.CTkProgressBar,
                       ctk.CTkEntry, ctk.CTkSlider, ctk.CTkSegmentedButton)):
            widget.is_themeable = True
            self.all_widgets.append(widget)
        else:
            try:
                widget.is_themeable = False
                self.all_widgets.append(widget)
            except Exception:
                pass
        return widget

    def setup_nav_frame(self):
        self.nav_frame = self._create_widget(ctk.CTkFrame, self, width=220, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="nswe")
        self.nav_frame.is_themeable = True

        self.app_logo_label = self._create_widget(ctk.CTkLabel, self.nav_frame, text="",
                                                  font=ctk.CTkFont(size=48, weight="bold"))
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

        self.aes_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_aes_frame, anchor="w")
        self.aes_button.grid(row=6, column=0, padx=20, pady=5, sticky="ew")

        self.sdes_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_sdes_frame, anchor="w")
        self.sdes_button.grid(row=7, column=0, padx=20, pady=5, sticky="ew")

        self.ela_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_ela_frame, anchor="w")
        self.ela_button.grid(row=8, column=0, padx=20, pady=5, sticky="ew")

        self.subst_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_subst_frame,
                                                anchor="w")
        self.subst_button.grid(row=9, column=0, padx=20, pady=5, sticky="ew")

        self.nav_frame.grid_rowconfigure(10, weight=1)

        self.settings_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_settings_frame,
                                                   anchor="w")
        self.settings_button.grid(row=11, column=0, padx=20, pady=5, sticky="ew")

        self.about_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_about_frame,
                                                anchor="w")
        self.about_button.grid(row=12, column=0, padx=20, pady=20, sticky="ew")

    def load_network_logo(self):
        threading.Thread(target=self._download_logo, daemon=True).start()

    def _download_logo(self):
        try:
            response = requests.get(APP_LOGO_URL, timeout=5)
            response.raise_for_status()

            image_data = response.content
            pil_image = Image.open(io.BytesIO(image_data)).convert("RGBA")
            self.logo_image = ctk.CTkImage(pil_image, size=(80, 80))
            self.after(0, self._update_logo_widget)
        except Exception:
            self.after(0, self._set_default_logo_text)

    def _update_logo_widget(self):
        if self.logo_image and self.app_logo_label.winfo_exists():
            try:
                self.app_logo_label.configure(text="", image=self.logo_image)
            except Exception:
                self._set_default_logo_text()

    def _set_default_logo_text(self):
        if self.app_logo_label.winfo_exists():
            self.app_logo_label.configure(image=None, text="🔒", font=ctk.CTkFont(size=48))

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
        self.aes_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent");
        self.aes_frame.is_themeable = False
        self.sdes_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent");
        self.sdes_frame.is_themeable = False
        self.subst_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent");
        self.subst_frame.is_themeable = False
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
        self.setup_aes_frame_widgets()
        self.setup_sdes_frame_widgets()
        self.setup_subst_frame_widgets()
        self.setup_settings_frame_widgets()
        self.setup_about_frame_widgets()

    # --- setup methods for frames ---
    def setup_xor_frame_widgets(self):
        self.xor_frame.grid_columnconfigure((0, 1), weight=1)
        self.xor_title = self._create_widget(ctk.CTkLabel, self.xor_frame, font=ctk.CTkFont(size=24, weight="bold"))
        self.xor_title.grid(row=0, column=0, columnspan=2, pady=20, padx=20)

        self.xor_label1 = self._create_widget(ctk.CTkLabel, self.xor_frame, width=400, height=400, fg_color="gray20",
                                              corner_radius=10, text="");
        self.xor_label1.is_themeable = False
        self.xor_label1.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.xor_load_btn1 = self._create_widget(ctk.CTkButton, self.xor_frame, command=self.load_xor_image1)
        self.xor_load_btn1.grid(row=2, column=0, padx=20, pady=10)

        self.xor_label2 = self._create_widget(ctk.CTkLabel, self.xor_frame, width=400, height=400, fg_color="gray20",
                                              corner_radius=10, text="");
        self.xor_label2.is_themeable = False
        self.xor_label2.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        self.xor_load_btn2 = self._create_widget(ctk.CTkButton, self.xor_frame, command=self.load_xor_image2)
        self.xor_load_btn2.grid(row=2, column=1, padx=20, pady=10)

        self.xor_run_btn = self._create_widget(ctk.CTkButton, self.xor_frame, command=self.perform_xor,
                                               font=ctk.CTkFont(size=16, weight="bold"))
        self.xor_run_btn.grid(row=3, column=0, columnspan=2, pady=20)

        self.xor_result_label = self._create_widget(ctk.CTkLabel, self.xor_frame, width=800, height=400,
                                                    fg_color="gray25", corner_radius=10, text="");
        self.xor_result_label.is_themeable = False
        self.xor_result_label.grid(row=4, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")

        self.xor_save_btn = self._create_widget(ctk.CTkButton, self.xor_frame, text="Save XOR Result",
                                                command=lambda: self.save_image_from_pil(self.xor_result_pil,
                                                                                         "xor_result.png"))
        self.xor_save_btn.grid(row=5, column=0, columnspan=2, pady=(0, 10))

        self.xor_status_label = self._create_widget(ctk.CTkLabel, self.xor_frame, text="", text_color="yellow");
        self.xor_status_label.is_themeable = False
        self.xor_status_label.grid(row=6, column=0, columnspan=2, pady=(0, 10))

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

        self.lsb_original_label = self._create_widget(ctk.CTkLabel, img_frame, width=450, height=350, fg_color="gray20",
                                                      corner_radius=10, text="");
        self.lsb_original_label.is_themeable = False
        self.lsb_original_label.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")

        self.lsb_result_label = self._create_widget(ctk.CTkLabel, img_frame, width=450, height=350, fg_color="gray25",
                                                    corner_radius=10, text="");
        self.lsb_result_label.is_themeable = False
        self.lsb_result_label.grid(row=0, column=1, pady=10, padx=10, sticky="nsew")

        self.lsb_save_btn = self._create_widget(ctk.CTkButton, self.lsb_frame, text="Save LSB Result",
                                                command=lambda: self.save_image_from_pil(self.lsb_result_pil,
                                                                                         "lsb_result.png"))
        self.lsb_save_btn.grid(row=3, column=0, pady=(0, 10))

        self.lsb_decoded_text_label = self._create_widget(ctk.CTkLabel, self.lsb_frame, font=ctk.CTkFont(size=16))
        self.lsb_decoded_text_label.grid(row=4, column=0, pady=(10, 0), sticky="s")

        self.lsb_text_result = self._create_widget(ctk.CTkTextbox, self.lsb_frame, height=100, font=("Consolas", 14))
        self.lsb_text_result.grid(row=5, column=0, pady=10, padx=20, sticky="nsew")

        self.lsb_status_label = self._create_widget(ctk.CTkLabel, self.lsb_frame, text="", text_color="yellow");
        self.lsb_status_label.is_themeable = False
        self.lsb_status_label.grid(row=6, column=0, pady=(0, 10))

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
        self.picker_status_label.grid(row=6, column=0, pady=(0, 10))

    def setup_vigenere_frame_widgets(self):
        self.vigenere_frame.grid_columnconfigure(0, weight=1)
        self.vigenere_frame.grid_rowconfigure(3, weight=1)
        self.vigenere_frame.grid_rowconfigure(7, weight=1)

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

        self.vigenere_crack_max_key_label = self._create_widget(ctk.CTkLabel, controls_frame)
        self.vigenere_crack_max_key_label.grid(row=1, column=0, padx=(0, 5), pady=(8, 0), sticky="w")
        self.vigenere_crack_max_key_entry = self._create_widget(ctk.CTkEntry, controls_frame, width=80)
        self.vigenere_crack_max_key_entry.grid(row=1, column=1, padx=5, pady=(8, 0), sticky="w")
        self.vigenere_crack_max_key_entry.insert(0, "20")
        self.vigenere_crack_btn = self._create_widget(ctk.CTkButton, controls_frame,
                                                      command=self.perform_vigenere_crack)
        self.vigenere_crack_btn.grid(row=1, column=2, padx=(20, 0), pady=(8, 0))

        self.vigenere_key_guess_label = self._create_widget(ctk.CTkLabel, self.vigenere_frame,
                                                            font=ctk.CTkFont(size=14))
        self.vigenere_key_guess_label.grid(row=5, column=0, pady=(0, 0), padx=20, sticky="w")

        self.vigenere_output_label = self._create_widget(ctk.CTkLabel, self.vigenere_frame, font=ctk.CTkFont(size=16))
        self.vigenere_output_label.grid(row=6, column=0, pady=(10, 0), padx=20, sticky="w")
        self.vigenere_output_textbox = self._create_widget(ctk.CTkTextbox, self.vigenere_frame, height=150)
        self.vigenere_output_textbox.grid(row=7, column=0, pady=5, padx=20, sticky="nsew")

        self.vigenere_status_label = self._create_widget(ctk.CTkLabel, self.vigenere_frame, text="",
                                                         text_color="yellow");
        self.vigenere_status_label.is_themeable = False
        self.vigenere_status_label.grid(row=8, column=0, pady=(0, 10), padx=20, sticky="w")

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
        self.base64_status_label.grid(row=7, column=0, pady=(0, 10), padx=20, sticky="w")

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

        self.ela_quality_slider = self._create_widget(ctk.CTkSlider, controls_frame, from_=1, to=100,
                                                      number_of_steps=99,
                                                      command=self.on_ela_quality_slider)
        self.ela_quality_slider.grid(row=1, column=2, padx=(10, 10), pady=5, sticky="we")
        self.ela_quality_slider.set(95)

        self.ela_scale_slider = self._create_widget(ctk.CTkSlider, controls_frame, from_=1, to=100, number_of_steps=99,
                                                    command=self.on_ela_scale_slider)
        self.ela_scale_slider.grid(row=2, column=2, padx=(10, 10), pady=5, sticky="we")
        self.ela_scale_slider.set(15)

        self.ela_quality_entry.bind("<FocusOut>", self.on_ela_quality_entry_change)
        self.ela_quality_entry.bind("<Return>", self.on_ela_quality_entry_change)
        self.ela_scale_entry.bind("<FocusOut>", self.on_ela_scale_entry_change)
        self.ela_scale_entry.bind("<Return>", self.on_ela_scale_entry_change)

        self.ela_run_btn = self._create_widget(ctk.CTkButton, controls_frame, command=self.run_ela_analysis,
                                               font=ctk.CTkFont(size=16, weight="bold"))
        self.ela_run_btn.grid(row=1, column=3, rowspan=2, padx=20, pady=10)

        img_frame = self._create_widget(ctk.CTkFrame, self.ela_frame, fg_color="transparent");
        img_frame.is_themeable = False
        img_frame.grid(row=2, column=0, pady=10, padx=20, sticky="ew")
        img_frame.grid_columnconfigure((0, 1), weight=1)

        self.ela_original_label = self._create_widget(ctk.CTkLabel, img_frame, width=450, height=350, fg_color="gray20",
                                                      corner_radius=10, text="");
        self.ela_original_label.is_themeable = False
        self.ela_original_label.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")

        self.ela_result_label = self._create_widget(ctk.CTkLabel, img_frame, width=450, height=350, fg_color="gray25",
                                                    corner_radius=10, text="");
        self.ela_result_label.is_themeable = False
        self.ela_result_label.grid(row=0, column=1, pady=10, padx=10, sticky="nsew")

        self.ela_save_btn = self._create_widget(ctk.CTkButton, self.ela_frame, text="Save ELA Result",
                                                command=lambda: self.save_image_from_pil(self.ela_result_pil,
                                                                                         "ela_result.png"))
        self.ela_save_btn.grid(row=3, column=0, pady=(0, 10))

        self.ela_status_label = self._create_widget(ctk.CTkLabel, self.ela_frame, text="", text_color="yellow");
        self.ela_status_label.is_themeable = False
        self.ela_status_label.grid(row=4, column=0, pady=(0, 10), padx=20, sticky="w")

    def on_ela_quality_slider(self, value):
        try:
            v = int(float(value))
            self.ela_quality_entry.delete(0, "end")
            self.ela_quality_entry.insert(0, str(v))
        except Exception:
            pass

    def on_ela_scale_slider(self, value):
        try:
            v = int(float(value))
            self.ela_scale_entry.delete(0, "end")
            self.ela_scale_entry.insert(0, str(v))
        except Exception:
            pass

    def on_ela_quality_entry_change(self, event):
        try:
            v = int(self.ela_quality_entry.get())
            if v < 1: v = 1
            if v > 100: v = 100
            self.ela_quality_slider.set(v)
            self.ela_quality_entry.delete(0, "end")
            self.ela_quality_entry.insert(0, str(v))
        except Exception:
            self.ela_quality_slider.set(95)
            self.ela_quality_entry.delete(0, "end")
            self.ela_quality_entry.insert(0, "95")

    def on_ela_scale_entry_change(self, event):
        try:
            v = int(self.ela_scale_entry.get())
            if v < 1: v = 1
            if v > 100: v = 100
            self.ela_scale_slider.set(v)
            self.ela_scale_entry.delete(0, "end")
            self.ela_scale_entry.insert(0, str(v))
        except Exception:
            self.ela_scale_slider.set(15)
            self.ela_scale_entry.delete(0, "end")
            self.ela_scale_entry.insert(0, "15")

    def setup_aes_frame_widgets(self):
        tab = self.aes_frame
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(7, weight=1)

        lang = LANG_STRINGS[self.current_lang.get()]

        self.aes_title = self._create_widget(ctk.CTkLabel, tab, font=ctk.CTkFont(size=24, weight="bold"))
        self.aes_title.grid(row=0, column=0, pady=20, padx=20, sticky="w")

        # режим (Encrypt / Decrypt)
        self.aes_mode = ctk.StringVar(value=lang["mode_encrypt"])
        mode_vals = [lang["mode_encrypt"], lang["mode_decrypt"]]
        self.aes_mode_selector = self._create_widget(ctk.CTkSegmentedButton, tab,
                                                     values=mode_vals, variable=self.aes_mode)
        self.aes_mode_selector.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        # Key size selector (Auto / 128 / 192 / 256)
        keysize_frame = self._create_widget(ctk.CTkFrame, tab)
        keysize_frame.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        keysize_frame.grid_columnconfigure(1, weight=1)
        self.aes_keysize_var = ctk.StringVar(value="Auto")
        self.aes_keysize_menu = self._create_widget(ctk.CTkOptionMenu, keysize_frame,
                                                    values=["Auto", "128", "192", "256"], variable=self.aes_keysize_var)
        self.aes_keysize_menu.grid(row=0, column=0, padx=(0, 8), pady=6, sticky="w")
        self.aes_key_label = self._create_widget(ctk.CTkLabel, keysize_frame, text=lang["key_label"])
        self.aes_key_label.grid(row=0, column=1, padx=(8, 8), pady=6, sticky="w")
        self.aes_key_entry = self._create_widget(ctk.CTkEntry, keysize_frame)
        self.aes_key_entry.grid(row=0, column=2, padx=(0, 8), pady=6, sticky="ew")

        # вхідні дані
        self.aes_input_label = self._create_widget(ctk.CTkLabel, tab, font=ctk.CTkFont(size=14))
        self.aes_input_label.grid(row=3, column=0, padx=20, sticky="w")
        self.aes_input_textbox = self._create_widget(ctk.CTkTextbox, tab, height=160)
        self.aes_input_textbox.grid(row=4, column=0, padx=20, pady=(4, 10), sticky="nsew")

        # кнопка виконати + статус
        controls = self._create_widget(ctk.CTkFrame, tab)
        controls.grid(row=5, column=0, padx=20, pady=8, sticky="ew")
        controls.grid_columnconfigure((0, 1, 2), weight=1)

        self.aes_run_btn = self._create_widget(ctk.CTkButton, controls, command=self.perform_aes_operation,
                                               font=ctk.CTkFont(size=14, weight="bold"))
        self.aes_run_btn.grid(row=0, column=0, padx=5, pady=4, sticky="w")

        # Brute-force controls (pin bruteforce)
        bf_frame = self._create_widget(ctk.CTkFrame, controls)
        bf_frame.grid(row=0, column=1, padx=5, sticky="e")
        bf_frame.grid_columnconfigure(1, weight=1)

        bf_label = self._create_widget(ctk.CTkLabel, bf_frame, text=lang["aes_bruteforce_label"])
        bf_label.grid(row=0, column=0, padx=(0, 6), sticky="w")
        self.aes_pin_maxlen_entry = self._create_widget(ctk.CTkEntry, bf_frame, width=60)
        self.aes_pin_maxlen_entry.grid(row=0, column=1, sticky="w")
        self.aes_pin_maxlen_entry.insert(0, "4")
        self.aes_brute_btn = self._create_widget(ctk.CTkButton, controls, text=lang["aes_bruteforce_run"],
                                                 command=self.perform_aes_bruteforce)
        self.aes_brute_btn.grid(row=0, column=2, padx=5, pady=4, sticky="e")

        # Вихід (результат)
        self.aes_output_label = self._create_widget(ctk.CTkLabel, tab, font=ctk.CTkFont(size=14))
        self.aes_output_label.grid(row=6, column=0, padx=20, pady=(8, 0), sticky="w")
        self.aes_output_textbox = self._create_widget(ctk.CTkTextbox, tab, height=140)
        self.aes_output_textbox.grid(row=7, column=0, padx=20, pady=(4, 10), sticky="nsew")

        # статус
        self.aes_status_label = self._create_widget(ctk.CTkLabel, tab, text="", text_color="yellow")
        self.aes_status_label.is_themeable = False
        self.aes_status_label.grid(row=8, column=0, padx=20, pady=(0, 10), sticky="w")

        # Ініціалізуємо локальні тексти під мову
        self.update_aes_texts()

    def perform_aes_operation(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        if not CRYPTO_AVAILABLE:
            self.aes_status_label.configure(text=lang["crypto_error_crypto_missing"], text_color="red")
            return

        txt = self.aes_input_textbox.get("1.0", "end").strip()
        key_input = self.aes_key_entry.get().strip()
        ks = self.aes_keysize_var.get() if hasattr(self, "aes_keysize_var") else "Auto"
        prefer_bits = None
        if ks in ("128", "192", "256"):
            try:
                prefer_bits = int(ks)
            except Exception:
                prefer_bits = None

        if not txt:
            self.aes_status_label.configure(text="Input empty", text_color="red")
            return

        if self.aes_mode.get() == LANG_STRINGS[self.current_lang.get()]["mode_encrypt"]:
            # Зашифрувати у вибраному форматі.
            # Якщо хочете OpenSSL-сумісний результат — використовуємо openssl_aes_encrypt.
            try:
                out_b64 = openssl_aes_encrypt(txt, key_input, prefer_bits=prefer_bits)
                self._safe_set_textbox_text(self.aes_output_textbox, out_b64)
                self.aes_status_label.configure(text=f"Encrypted — key {prefer_bits or 'Auto'} (OpenSSL format)",
                                                text_color="green")
            except Exception as e:
                logger.exception("encrypt failed")
                self.aes_status_label.configure(text=f"Error: {e}", text_color="red")
        else:
            # Дешифрування: пробуємо OpenSSL-salted або IV-prefixed (gнучкий декодер)
            try:
                plaintext, info = openssl_or_iv_decrypt(txt, key_input, prefer_bits=prefer_bits)
                self._safe_set_textbox_text(self.aes_output_textbox, plaintext)
                self.aes_status_label.configure(text=f"Decrypted ({info})", text_color="green")
            except Exception as e:
                logger.debug("decrypt attempts failed", exc_info=True)
                # Виводимо детальну помилку в статус (коротко) і в логи повний trace
                msg = str(e)
                self.aes_status_label.configure(text=f"Error: {msg}", text_color="red")

    def perform_aes_bruteforce(self):
        """
        GUI handler: brute-force password candidates (numeric PINs by length) for AES payload.
        Uses aes_bruteforce_password (module-level) which handles OpenSSL-salted and IV-prefixed payloads.
        """
        lang = LANG_STRINGS[self.current_lang.get()]
        if not CRYPTO_AVAILABLE:
            self.aes_status_label.configure(text=lang["crypto_error_crypto_missing"], text_color="red")
            return

        cipher_b64 = self.aes_input_textbox.get("1.0", "end").strip()
        if not cipher_b64:
            self.aes_status_label.configure(text="Input empty", text_color="red")
            return

        # prefer_bits from UI selector if present
        ks = self.aes_keysize_var.get() if hasattr(self, "aes_keysize_var") else "Auto"
        prefer_bits = None
        if ks in ("128", "192", "256"):
            try:
                prefer_bits = int(ks)
            except Exception:
                prefer_bits = None

        # numeric max length field still used to limit candidate lengths
        try:
            maxlen = int(self.aes_pin_maxlen_entry.get().strip() or "4")
            if maxlen < 1:
                maxlen = 1
            if maxlen > 6:
                # safety cap to avoid too long brute (adjust as desired)
                maxlen = 6
        except Exception:
            maxlen = 4

        self.aes_status_label.configure(text=lang["brute_status"], text_color="yellow")
        self.update_idletasks()

        def worker(cipher_b64=cipher_b64, maxlen=maxlen, prefer_bits=prefer_bits):
            try:
                matches = aes_bruteforce_password(cipher_b64, known_fragment=None,
                                                  max_pin_length=maxlen, prefer_bits=prefer_bits)
                # prepare output text
                if not matches:
                    self.after(0,
                               lambda: self.aes_status_label.configure(text=lang["brute_no_results"], text_color="red"))
                    return

                out_lines = []
                for candidate, pt in matches[:20]:
                    try:
                        text_preview = pt.decode("utf-8", errors="replace")
                    except Exception:
                        text_preview = repr(pt)
                    out_lines.append(f"Password: {candidate} => plaintext preview:\n{text_preview}\n{'-' * 40}")
                out_text = "\n\n".join(out_lines)

                # update GUI: output textbox and status
                def gui_update(o=out_text):
                    try:
                        self._safe_set_textbox_text(self.aes_output_textbox, o)
                    except Exception:
                        self.aes_output_textbox.delete("1.0", tk.END)
                        self.aes_output_textbox.insert("1.0", o)
                    self.aes_status_label.configure(text=lang["brute_done"], text_color="green")

                self.after(0, gui_update)
            except Exception as e:
                err = str(e)
                try:
                    logger.exception("aes brute worker failed")
                except Exception:
                    pass
                self.after(0, lambda msg=err: self.aes_status_label.configure(text=f"Error: {msg}", text_color="red"))

        threading.Thread(target=worker, daemon=True).start()

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
        links_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        linkedin_url = "https://www.linkedin.com/in/cybersecsprofile/"
        github_url = "https://github.com/QmFkLVBp"
        htb_url = "https://app.hackthebox.com/profile/1969974"
        thm_url = "https://tryhackme.com/p/0xW1ZARD"
        website_url = "http://bad-pi.me"

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

        self.website_btn = self._create_widget(ctk.CTkButton, links_frame, text="Website",
                                               command=lambda: self.open_link(website_url))
        self.website_btn.grid(row=0, column=4, padx=5, pady=5)

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
        else:
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

    def change_language(self, *args):
        lang_code = self.current_lang.get()
        self.update_all_texts(lang_code)
        self.update_aes_texts()
        self.update_sdes_texts()
        self.update_vigenere_labels()
        self.update_base64_labels()
        # S-DES

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

        self.vigenere_title.configure(text=lang.get("vigenere_title", "Vigenère"))
        self.vigenere_key_label.configure(text=lang["vigenere_key_label"])
        self.vigenere_crack_max_key_label.configure(text=lang["vigenere_crack_max_key_label"])
        self.vigenere_crack_btn.configure(text=lang["vigenere_crack_btn"])
        self.vigenere_key_guess_label.configure(text=lang["vigenere_key_guess_default"])

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

        self.base64_title.configure(text=lang.get("base64_title", "Base64"))

    def update_aes_texts(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        if hasattr(self, "aes_title"):
            self.aes_title.configure(text=lang["aes_title"])
        if hasattr(self, "aes_mode_selector"):
            vals = [lang["mode_encrypt"], lang["mode_decrypt"]]
            cur = self.aes_mode.get()
            self.aes_mode_selector.configure(values=vals)
            if cur not in vals:
                self.aes_mode.set(vals[0])
        if hasattr(self, "aes_input_label"):
            self.aes_input_label.configure(text=lang["input_label"])
        if hasattr(self, "aes_key_label"):
            self.aes_key_label.configure(text=lang["key_label"])
        if hasattr(self, "aes_pin_maxlen_label"):
            self.aes_pin_maxlen_label.configure(text=lang["aes_bruteforce_label"])
        if hasattr(self, "aes_run_btn"):
            self.aes_run_btn.configure(text=lang["run"])
        if hasattr(self, "aes_brute_btn"):
            self.aes_brute_btn.configure(text=lang["aes_bruteforce_run"])
        if hasattr(self, "aes_output_label"):
            self.aes_output_label.configure(text=lang["output_label"])

    def update_sdes_texts(self):
        # Fixed: use LANG_STRINGS (was using self.translations which did not exist)
        lang_code = self.current_lang.get()
        lang = LANG_STRINGS.get(lang_code, LANG_STRINGS["en"])

        # Update UI elements with proper keys
        if hasattr(self, 'sdes_title'):
            self.sdes_title.configure(text=lang.get("sdes_title", "S-DES"))
        if hasattr(self, 'sdes_mode_selector'):
            vals = [lang.get("mode_encrypt", "Encrypt"), lang.get("mode_decrypt", "Decrypt")]
            cur = self.sdes_mode.get() if hasattr(self, 'sdes_mode') else ""
            self.sdes_mode_selector.configure(values=vals)
            if cur not in vals:
                # default to encrypt
                try:
                    self.sdes_mode.set(vals[0])
                except Exception:
                    pass
        if hasattr(self, 'sdes_input_label'):
            self.sdes_input_label.configure(text=lang.get("sdes_input_label", "Input"))
        if hasattr(self, 'sdes_key_label'):
            self.sdes_key_label.configure(text=lang.get("sdes_key_label", "Key"))
        if hasattr(self, 'sdes_output_label'):
            self.sdes_output_label.configure(text=lang.get("sdes_output_label", "Output:"))
        if hasattr(self, 'sdes_log_label'):
            self.sdes_log_label.configure(text=lang.get("sdes_log_label", "Execution Log:"))

        # Brute force related text
        if hasattr(self, 'sdes_run_btn'):
            self.sdes_run_btn.configure(text=lang.get("sdes_run", "Run S-DES"))
        if hasattr(self, 'sdes_brute_title'):
            self.sdes_brute_title.configure(text=lang.get("sdes_brute_title", "S-DES Brute"))
        if hasattr(self, 'sdes_brute_ciphertext_label'):
            self.sdes_brute_ciphertext_label.configure(text=lang.get("sdes_brute_ciphertext_label", "Ciphertext"))
        if hasattr(self, 'sdes_known_fragment_label'):
            self.sdes_known_fragment_label.configure(text=lang.get("sdes_brute_known_label", "Known fragment:"))
        if hasattr(self, 'sdes_brute_btn'):
            self.sdes_brute_btn.configure(text=lang.get("sdes_brute_run", "Start S-DES Brute-force (1024 keys)"))

    def update_all_texts(self, lang_code):
        lang = LANG_STRINGS.get(lang_code, LANG_STRINGS["ua"])
        self.title(lang["title"])

        if hasattr(self, 'xor_button'): self.xor_button.configure(text=lang["nav_xor"])
        if hasattr(self, 'lsb_button'): self.lsb_button.configure(text=lang["nav_lsb"])
        if hasattr(self, 'picker_button'): self.picker_button.configure(text=lang["nav_picker"])
        if hasattr(self, 'vigenere_button'): self.vigenere_button.configure(text=lang["nav_vigenere"])
        if hasattr(self, 'base64_button'): self.base64_button.configure(text=lang["nav_base64"])
        if hasattr(self, 'aes_button'): self.aes_button.configure(text=lang["nav_aes"])
        if hasattr(self, 'sdes_button'): self.sdes_button.configure(text=lang["nav_sdes"])
        if hasattr(self, 'ela_button'): self.ela_button.configure(text=lang["nav_ela"])
        if hasattr(self, 'settings_button'): self.settings_button.configure(text=lang["nav_settings"])
        if hasattr(self, 'about_button'): self.about_button.configure(text=lang["nav_about"])

        if hasattr(self, 'xor_title'): self.xor_title.configure(text=lang.get("xor_title", "XOR"))
        if hasattr(self, 'lsb_title'): self.lsb_title.configure(text=lang.get("lsb_title", "LSB"))
        if hasattr(self, 'picker_title'): self.picker_title.configure(text=lang.get("picker_title", "Picker"))
        if hasattr(self, 'vigenere_title'): self.vigenere_title.configure(text=lang.get("vigenere_title", "Vigenère"))
        if hasattr(self, 'base64_title'): self.base64_title.configure(text=lang.get("base64_title", "Base64"))
        if hasattr(self, 'ela_title'): self.ela_title.configure(text=lang.get("ela_title", "ELA"))
        if hasattr(self, 'settings_title'): self.settings_title.configure(text=lang.get("settings_title", "Settings"))
        if hasattr(self, 'about_title'): self.about_title.configure(text=lang.get("about_title", "About"))

        # XOR texts
        if hasattr(self, "xor_label1") and (self.xor_pil1 is None):
            self._safe_set_label_text(self.xor_label1, lang["xor_img1_text"])
        if hasattr(self, "xor_label2") and (self.xor_pil2 is None):
            self._safe_set_label_text(self.xor_label2, lang["xor_img2_text"])
        if hasattr(self, "xor_result_label") and (self.xor_result_pil is None):
            self._safe_set_label_text(self.xor_result_label, lang["xor_result_text"])
        if hasattr(self, "xor_load_btn1"):
            self.xor_load_btn1.configure(text=lang["xor_load1"])
        if hasattr(self, "xor_load_btn2"):
            self.xor_load_btn2.configure(text=lang["xor_load2"])
        if hasattr(self, "xor_run_btn"):
            self.xor_run_btn.configure(text=lang["xor_run"])

        # LSB texts
        if hasattr(self, "lsb_load_btn"):
            self.lsb_load_btn.configure(text=lang["lsb_load"])
        if hasattr(self, "lsb_run_btn"):
            self.lsb_run_btn.configure(text=lang["lsb_run"])
        if hasattr(self, "lsb_original_label") and (self.lsb_original_pil is None):
            self._safe_set_label_text(self.lsb_original_label, lang["lsb_original_text"])
        if hasattr(self, "lsb_result_label") and (self.lsb_result_pil is None):
            self._safe_set_label_text(self.lsb_result_label, lang["lsb_result_text"])
        if hasattr(self, "lsb_decoded_text_label"):
            self.lsb_decoded_text_label.configure(text=lang["lsb_decoded_text_label"])

        # Picker texts
        if hasattr(self, "picker_load_btn"):
            self.picker_load_btn.configure(text=lang["picker_load"])
        if hasattr(self, "picker_image_label") and (self.picker_pil_image is None):
            self._safe_set_label_text(self.picker_image_label, lang["picker_img_text"])
        if hasattr(self, "picker_hex_label"):
            self.picker_hex_label.configure(text=lang["picker_hex_default"])
        if hasattr(self, "picker_last_text_label"):
            self.picker_last_text_label.configure(text=lang["picker_text_default"])
        if hasattr(self, "picker_clear_btn"):
            self.picker_clear_btn.configure(text=lang["picker_clear"])
        if hasattr(self, "picker_status_label") and not self.picker_pil_image:
            self.picker_status_label.configure(text=lang["picker_status_default"])

        # ELA texts
        if hasattr(self, "ela_load_btn"):
            self.ela_load_btn.configure(text=lang["ela_load"])
        if hasattr(self, "ela_original_label") and (self.ela_original_pil is None):
            self._safe_set_label_text(self.ela_original_label, lang["ela_original_text"])
        if hasattr(self, "ela_result_label") and (self.ela_result_pil is None):
            self._safe_set_label_text(self.ela_result_label, lang["ela_result_text"])
        if hasattr(self, "ela_quality_label"):
            self.ela_quality_label.configure(text=lang["ela_quality_label"])
        if hasattr(self, "ela_scale_label"):
            self.ela_scale_label.configure(text=lang["ela_scale_label"])
        if hasattr(self, "ela_run_btn"):
            self.ela_run_btn.configure(text=lang["ela_run"])

        # Settings texts
        if hasattr(self, "settings_lang_label"):
            self.settings_lang_label.configure(text=lang["settings_lang"])
        if hasattr(self, "settings_theme_label"):
            self.settings_theme_label.configure(text=lang["settings_theme"])
        if hasattr(self, "settings_danger_label"):
            self.settings_danger_label.configure(text=lang["settings_danger_zone"])
        if hasattr(self, "self_destruct_btn"):
            self.self_destruct_btn.configure(text=lang["settings_self_destruct"])

        # About
        if hasattr(self, "about_text_label"):
            self.about_text_label.configure(text=lang["about_text"])
        if hasattr(self, "about_links_label"):
            self.about_links_label.configure(text=lang["about_links_label"])

        # Substitution texts
        if hasattr(self, 'subst_button'):
            self.subst_button.configure(text=lang.get("nav_subst", "Substitution"))
        if hasattr(self, 'subst_title'):
            self.subst_title.configure(text=lang.get("subst_title", "Substitution"))
        if hasattr(self, 'subst_input_label'):
            self.subst_input_label.configure(text=lang.get("subst_input_label", "Ciphertext:"))
        if hasattr(self, 'subst_freq_chars_label'):
            self.subst_freq_chars_label.configure(text=lang.get("subst_freq_chars_label", "Character Frequency:"))
        if hasattr(self, 'subst_freq_bigrams_label'):
            self.subst_freq_bigrams_label.configure(text=lang.get("subst_freq_bigrams_label", "Bigram Frequency:"))
        if hasattr(self, 'subst_mapping_label'):
            self.subst_mapping_label.configure(text=lang.get("subst_mapping_label", "Mapping Table:"))
        if hasattr(self, 'subst_header_cipher'):
            self.subst_header_cipher.configure(text=lang.get("subst_cipher_col", "Cipher"))
        if hasattr(self, 'subst_header_plain'):
            self.subst_header_plain.configure(text=lang.get("subst_plain_col", "Plain"))
        if hasattr(self, 'subst_add_row_btn'):
            self.subst_add_row_btn.configure(text=lang.get("subst_add_row", "+ Row"))
        if hasattr(self, 'subst_remove_row_btn'):
            self.subst_remove_row_btn.configure(text=lang.get("subst_remove_row", "- Row"))
        if hasattr(self, 'subst_analyze_btn'):
            self.subst_analyze_btn.configure(text=lang.get("subst_analyze", "Analyze"))
        if hasattr(self, 'subst_apply_btn'):
            self.subst_apply_btn.configure(text=lang.get("subst_apply", "Apply"))
        if hasattr(self, 'subst_suggest_btn'):
            self.subst_suggest_btn.configure(text=lang.get("subst_suggest", "Suggest"))
        if hasattr(self, 'subst_clear_btn'):
            self.subst_clear_btn.configure(text=lang.get("subst_clear", "Clear"))
        if hasattr(self, 'subst_export_btn'):
            self.subst_export_btn.configure(text=lang.get("subst_export", "Export"))
        if hasattr(self, 'subst_import_btn'):
            self.subst_import_btn.configure(text=lang.get("subst_import", "Import"))
        if hasattr(self, 'subst_auto_replace_btn'):
            self.subst_auto_replace_btn.configure(text=lang.get("subst_auto_replace", "Auto Replace"))
        if hasattr(self, 'subst_undo_btn'):
            self.subst_undo_btn.configure(text=lang.get("subst_undo", "Undo"))
        if hasattr(self, 'subst_redo_btn'):
            self.subst_redo_btn.configure(text=lang.get("subst_redo", "Redo"))
        if hasattr(self, 'subst_export_txt_btn'):
            self.subst_export_txt_btn.configure(text=lang.get("subst_export_txt", "Export TXT"))
        if hasattr(self, 'subst_import_txt_btn'):
            self.subst_import_txt_btn.configure(text=lang.get("subst_import_txt", "Import TXT"))
        if hasattr(self, 'subst_export_report_btn'):
            self.subst_export_report_btn.configure(text=lang.get("subst_export_report", "Report"))
        if hasattr(self, 'subst_output_label'):
            self.subst_output_label.configure(text=lang.get("subst_output_label", "Decrypted Result:"))
        if hasattr(self, 'subst_bigram_connectivity_label'):
            self.subst_bigram_connectivity_label.configure(text=lang.get("subst_bigram_connectivity_label", "Bigrams & Connectivity:"))
        if hasattr(self, 'subst_lang_label'):
            self.subst_lang_label.configure(text=lang.get("subst_lang_label", "Frequency Language:"))
        # Update the language menu values
        if hasattr(self, 'subst_freq_lang_menu'):
            current_val = self.subst_freq_lang_var.get()
            new_values = [lang.get("subst_lang_ua", "Ukrainian"), lang.get("subst_lang_en", "English")]
            self.subst_freq_lang_menu.configure(values=new_values)
            # Try to keep the selection consistent
            if current_val in ["Українська", "Ukrainian", lang.get("subst_lang_ua", "Ukrainian")]:
                self.subst_freq_lang_var.set(lang.get("subst_lang_ua", "Ukrainian"))
            else:
                self.subst_freq_lang_var.set(lang.get("subst_lang_en", "English"))

    # ---------- AES and S-DES UI setup ----------
    # ---- Додайте на рівні модуля (після імпортів) ----
    def evp_bytes_to_key(password: bytes, salt: bytes, key_len: int, iv_len: int, hasher=hashlib.md5) -> Tuple[
        bytes, bytes]:
        """
        Реалізація OpenSSL EVP_BytesToKey (MD5 варіант) — повертає (key, iv).
        Використовується aesencryption.net (формат OpenSSL 'Salted__' + 8-byte salt).
        """
        derived = b""
        prev = b""
        while len(derived) < (key_len + iv_len):
            prev = hasher(prev + password + salt).digest()
            derived += prev
        key = derived[:key_len]
        iv = derived[key_len:key_len + iv_len]
        return key, iv

    def openssl_aes_encrypt(plaintext: str, password: str, prefer_bits: Optional[int] = None) -> str:
        """
        Шифрує у форматі сумісному з aesencryption.net / OpenSSL enc:
        payload = b"Salted__" + salt(8) + ciphertext
        Повертає base64(payload).
        prefer_bits: 128/192/256 або None (за замовчуванням 256 якщо password достатньо довгий буде використано EVP_BytesToKey з key_len відповідно).
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Crypto not available")
        if prefer_bits not in (128, 192, 256, None):
            raise ValueError("prefer_bits must be 128/192/256 or None")

        salt = os.urandom(8)
        # Визначаємо довжину ключа в байтах
        if prefer_bits is None:
            # якщо не вказано, використаємо 256-бітну довжину як дефолт для derivation
            key_len = 32
        else:
            key_len = prefer_bits // 8
        iv_len = AES.block_size  # 16
        key, iv = evp_bytes_to_key(password.encode("utf-8"), salt, key_len, iv_len, hashlib.md5)

        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        padded = pad(plaintext.encode("utf-8"), AES.block_size, style='pkcs7')
        ct = cipher.encrypt(padded)
        payload = b"Salted__" + salt + ct
        return base64.b64encode(payload).decode('utf-8')

    def openssl_aes_decrypt(b64payload: str, password: str, prefer_bits: Optional[int] = None) -> str:
        """
        Дешифрує payload у форматі OpenSSL ('Salted__' + salt + ciphertext).
        prefer_bits може підказати бажаний key-size (128/192/256) — якщо None, використовує ключ-деривацію з key_len=32 (256) для сумісності.
        Повертає розшифрований utf-8 рядок (errors='replace').
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Crypto not available")
        try:
            data = base64.b64decode(b64payload)
        except Exception as e:
            raise ValueError(f"Invalid base64 payload: {e}")

        if not data.startswith(b"Salted__") or len(data) < 16:
            raise ValueError("Input is not OpenSSL salted format (missing 'Salted__' + salt).")

        salt = data[8:16]
        ct = data[16:]
        if prefer_bits is None:
            key_len = 32
        else:
            key_len = prefer_bits // 8
        iv_len = AES.block_size
        key, iv = evp_bytes_to_key(password.encode("utf-8"), salt, key_len, iv_len, hashlib.md5)

        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        try:
            pt = unpad(cipher.decrypt(ct), AES.block_size, style='pkcs7')
        except ValueError as e:
            # padding error або некоректний ключ
            raise ValueError(f"Decryption failed (padding/incorrect key): {e}")
        return pt.decode('utf-8', errors='replace')

    def aes_derive_key_from_password(password: str, bits: int = 128) -> bytes:
        """
        Простий derive для brute-force PIN: SHA256(password)[:bits//8].
        (Використовується в aes_bruteforce_pin для швидкого brute-force)
        """
        h = hashlib.sha256(password.encode('utf-8')).digest()
        return h[: (bits // 8)]

    # ---- Кінець доданих модульних функцій ----

    def _aes_process(self, mode: str):
        if not CRYPTO_AVAILABLE:
            messagebox.showerror(lang.get("dialog_error_title", "Error"),
                                 lang.get("dialog_crypto_error", "PyCryptodome library is not installed."))
            return

        lang = self.master.lang
        key = self.aes_key_entry.get()
        input_text = self._safe_get_textbox_text(self.aes_input_textbox)

        if not key:
            messagebox.showerror(lang.get("dialog_error_title", "Error"),
                                 lang.get("dialog_aes_error_key", "Key cannot be empty."))
            return
        if not input_text:
            messagebox.showerror(lang.get("dialog_error_title", "Error"),
                                 lang.get("dialog_aes_error_input", "Input cannot be empty."))
            return

        try:
            key_bytes = key.encode('utf-8')
            key_size = int(self.aes_key_size.get())
            key_len_bytes = key_size // 8
            iv_len_bytes = AES.block_size  # 16 байт для AES

            # aesencryption.net використовує MD5 для EVP_BytesToKey
            hasher = hashlib.md5

            if mode == lang.get("mode_encrypt", "Encrypt"):
                # 1. Генеруємо випадкову 8-байтну сіль
                salt = os.urandom(8)

                # 2. Отримуємо ключ та IV з пароля та солі
                final_key, final_iv = evp_bytes_to_key(key_bytes, salt, key_len_bytes, iv_len_bytes, hasher)

                # 3. Шифруємо
                cipher = AES.new(final_key, AES.MODE_CBC, final_iv)
                data_bytes = input_text.encode('utf-8')
                padded_data = pad(data_bytes, AES.block_size, style='pkcs7')
                ciphertext = cipher.encrypt(padded_data)

                # 4. Додаємо заголовок "Salted__" та саму сіль (стандарт OpenSSL)
                salted_ciphertext = b"Salted__" + salt + ciphertext

                # 5. Кодуємо в Base64
                output_b64 = base64.b64encode(salted_ciphertext).decode('utf-8')
                self._safe_set_textbox_text(self.aes_output_textbox, output_b64)

            else:  # Decrypt
                # 1. Декодуємо з Base64
                try:
                    ciphertext_bytes = base64.b64decode(input_text.encode('utf-8'))
                except Exception as e:
                    messagebox.showerror(lang.get("dialog_error_title", "Error"),
                                         lang.get("dialog_aes_error_base64", "Input is not valid Base64.") + f"\n{e}")
                    return

                # 2. Перевіряємо заголовок "Salted__" та витягуємо сіль
                if not ciphertext_bytes.startswith(b"Salted__"):
                    messagebox.showerror(lang.get("dialog_error_title", "Error"),
                                         "Помилка: Вхідні дані не у форматі OpenSSL 'Salted'.\n"
                                         "Цей метод сумісний лише з aesencryption.net (або подібними), "
                                         "які використовують сіль.")
                    return

                salt = ciphertext_bytes[8:16]  # 8 байт солі
                actual_ciphertext = ciphertext_bytes[16:]  # Решта - зашифровані дані

                if len(salt) != 8:
                    messagebox.showerror(lang.get("dialog_error_title", "Error"),
                                         "Помилка: Сіль пошкоджена або відсутня.")
                    return

                # 3. Отримуємо ключ та IV з пароля та солі
                final_key, final_iv = evp_bytes_to_key(key_bytes, salt, key_len_bytes, iv_len_bytes, hasher)

                # 4. Розшифровуємо
                cipher = AES.new(final_key, AES.MODE_CBC, final_iv)
                decrypted_padded_data = cipher.decrypt(actual_ciphertext)

                # 5. Знімаємо "padding" та виводимо
                try:
                    decrypted_data = unpad(decrypted_padded_data, AES.block_size, style='pkcs7')
                    self._safe_set_textbox_text(self.aes_output_textbox, decrypted_data.decode('utf-8'))
                except (ValueError, UnicodeDecodeError) as e:
                    messagebox.showerror(lang.get("dialog_error_title", "Error"),
                                         lang.get("dialog_aes_error_decrypt",
                                                  "Decryption failed. Check key, key size, or padding.") + f"\n{e}")
                    self._safe_set_textbox_text(self.aes_output_textbox, "")  # Очистити вивід

        except Exception as e:
            messagebox.showerror(lang.get("dialog_error_title", "Error"),
                                 lang.get("dialog_aes_error_generic",
                                          "An error occurred during AES processing.") + f"\n{type(e).__name__}: {e}")
            self._safe_set_textbox_text(self.aes_output_textbox, "")

    def setup_sdes_frame_widgets(self):
        # ВАЖЛИВО: Встановлюємо 'tab' як псевдонім для 'self.sdes_frame'
        tab = self.sdes_frame

        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(5, weight=1)  # Дозволяємо контейнеру виводу розтягуватися

        self.sdes_title = self._create_widget(ctk.CTkLabel, tab,
                                              font=ctk.CTkFont(size=18, weight="bold"))
        self.sdes_title.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Use current language strings so SegmentedButton values are unique
        lang = LANG_STRINGS[self.current_lang.get()]

        # Створюємо віджети з коректними унікальними значеннями
        self.sdes_mode = tk.StringVar()
        self.sdes_mode_selector = self._create_widget(
            ctk.CTkSegmentedButton,
            tab,
            values=[lang.get("mode_encrypt", "Encrypt"), lang.get("mode_decrypt", "Decrypt")],
            variable=self.sdes_mode
        )
        self.sdes_mode_selector.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        # set default mode
        try:
            self.sdes_mode.set(lang.get("mode_encrypt", "Encrypt"))
        except Exception:
            pass

        # --- Input Frame ---
        self.sdes_input_frame = self._create_widget(ctk.CTkFrame, tab, fg_color="transparent")
        self.sdes_input_frame.grid(row=2, column=0, padx=20, pady=0, sticky="nsew")
        self.sdes_input_frame.grid_columnconfigure(0, weight=1)

        self.sdes_input_label = self._create_widget(ctk.CTkLabel, self.sdes_input_frame)
        self.sdes_input_label.grid(row=0, column=0, sticky="w")
        self.sdes_input_textbox = self._create_widget(ctk.CTkTextbox, self.sdes_input_frame, height=100)
        self.sdes_input_textbox.grid(row=1, column=0, sticky="nsew")

        # --- Key Frame ---
        self.sdes_key_frame = self._create_widget(ctk.CTkFrame, tab, fg_color="transparent")
        self.sdes_key_frame.grid(row=3, column=0, padx=20, pady=0, sticky="nsew")
        self.sdes_key_frame.grid_columnconfigure(0, weight=1)

        self.sdes_key_label = self._create_widget(ctk.CTkLabel, self.sdes_key_frame)
        self.sdes_key_label.grid(row=0, column=0, sticky="w")
        self.sdes_key_entry = self._create_widget(ctk.CTkEntry, self.sdes_key_frame)
        self.sdes_key_entry.grid(row=1, column=0, sticky="ew")

        # --- Run Button ---
        self.sdes_run_btn = self._create_widget(ctk.CTkButton, tab,
                                                command=self.on_sdes_run)
        self.sdes_run_btn.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        # --- Output & Log (Side-by-side) ---
        self.sdes_output_container = self._create_widget(ctk.CTkFrame, tab, fg_color="transparent")
        self.sdes_output_container.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="nsew")
        self.sdes_output_container.grid_columnconfigure((0, 1), weight=1)
        self.sdes_output_container.grid_rowconfigure(1, weight=1)

        # Output (Left)
        self.sdes_output_frame = self._create_widget(ctk.CTkFrame, self.sdes_output_container, fg_color="transparent")
        self.sdes_output_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        self.sdes_output_frame.grid_rowconfigure(1, weight=1)

        self.sdes_output_label = self._create_widget(ctk.CTkLabel, self.sdes_output_frame)
        self.sdes_output_label.grid(row=0, column=0, sticky="w")
        self.sdes_output_textbox = self._create_widget(ctk.CTkTextbox, self.sdes_output_frame, height=150)
        self.sdes_output_textbox.grid(row=1, column=0, sticky="nsew")

        # Log (Right) - НОВИЙ
        self.sdes_log_frame = self._create_widget(ctk.CTkFrame, self.sdes_output_container, fg_color="transparent")
        self.sdes_log_frame.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        self.sdes_log_frame.grid_rowconfigure(1, weight=1)

        self.sdes_log_label = self._create_widget(ctk.CTkLabel, self.sdes_log_frame)
        self.sdes_log_label.grid(row=0, column=0, sticky="w")
        self.sdes_log_textbox = self._create_widget(ctk.CTkTextbox, self.sdes_log_frame, height=150,
                                                    font=("Courier New", 10))
        self.sdes_log_textbox.configure(state="disabled")  # НЕ МОЖНА РЕДАГУВАТИ
        self.sdes_log_textbox.grid(row=1, column=0, sticky="nsew")

        # --- Status Label ---
        self.sdes_status_label = self._create_widget(ctk.CTkLabel, tab, text="",
                                                     font=ctk.CTkFont(size=12))
        self.sdes_status_label.grid(row=6, column=0, padx=20, pady=5, sticky="w")

        # --- Separator and Brute-force ---
        sep = self._create_widget(ctk.CTkFrame, tab, height=2, fg_color=("gray", "gray"))
        sep.grid(row=7, column=0, padx=20, pady=10, sticky="ew")

        self.sdes_brute_frame = self._create_widget(ctk.CTkFrame, tab, fg_color="transparent")
        self.sdes_brute_frame.grid(row=8, column=0, padx=20, pady=0, sticky="nsew")
        self.sdes_brute_frame.grid_columnconfigure(0, weight=1)

        self.sdes_brute_title = self._create_widget(ctk.CTkLabel, self.sdes_brute_frame,
                                                    font=ctk.CTkFont(size=16, weight="bold"))
        self.sdes_brute_title.grid(row=0, column=0, sticky="w")

        self.sdes_brute_ciphertext_label = self._create_widget(ctk.CTkLabel, self.sdes_brute_frame)
        self.sdes_brute_ciphertext_label.grid(row=1, column=0, pady=(5, 0), sticky="w")

        self.sdes_known_fragment_label = self._create_widget(ctk.CTkLabel, self.sdes_brute_frame)
        self.sdes_known_fragment_label.grid(row=2, column=0, pady=(5, 0), sticky="w")
        self.sdes_known_fragment_entry = self._create_widget(ctk.CTkEntry, self.sdes_brute_frame)
        self.sdes_known_fragment_entry.grid(row=3, column=0, pady=5, sticky="ew")

        self.sdes_brute_btn = self._create_widget(ctk.CTkButton, self.sdes_brute_frame,
                                                  command=self.on_sdes_brute_run)
        self.sdes_brute_btn.grid(row=4, column=0, pady=10, sticky="ew")

    def setup_subst_frame_widgets(self):
        """Setup the Substitution Cipher frame widgets."""
        tab = self.subst_frame

        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(4, weight=1)

        # Title
        self.subst_title = self._create_widget(ctk.CTkLabel, tab,
                                               font=ctk.CTkFont(size=18, weight="bold"))
        self.subst_title.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="w")

        # --- Left Column: Input & Frequency Analysis ---
        left_frame = self._create_widget(ctk.CTkFrame, tab, fg_color="transparent")
        left_frame.grid(row=1, column=0, rowspan=4, padx=(20, 10), pady=10, sticky="nsew")
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(6, weight=1)
        left_frame.grid_rowconfigure(9, weight=2)

        # Input textbox
        self.subst_input_label = self._create_widget(ctk.CTkLabel, left_frame)
        self.subst_input_label.grid(row=0, column=0, sticky="w")
        self.subst_input_textbox = self._create_widget(ctk.CTkTextbox, left_frame, height=100)
        self.subst_input_textbox.grid(row=1, column=0, pady=(0, 10), sticky="nsew")

        # NEW: two-digit token mode checkbox
        self.subst_two_digit_var = ctk.BooleanVar(value=False)
        self.subst_two_digit_checkbox = self._create_widget(
            ctk.CTkCheckBox, left_frame,
            text="Multi-digit tokens (2-digit = 1 letter)",
            variable=self.subst_two_digit_var
        )
        self.subst_two_digit_checkbox.grid(row=2, column=0, pady=(5, 0), sticky="w")
        
        # NEW: Inline hint under multi-digit checkbox
        self.subst_two_digit_hint = self._create_widget(
            ctk.CTkLabel, left_frame,
            text="Підказка: якщо у мапі є 7 і 78 → токен 78 має пріоритет.",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.subst_two_digit_hint.grid(row=3, column=0, pady=(0, 5), sticky="w")
        
        # NEW: Ignore punctuation checkbox
        self.subst_ignore_punct_var = ctk.BooleanVar(value=False)
        self.subst_ignore_punct_checkbox = self._create_widget(
            ctk.CTkCheckBox, left_frame,
            text=f"Ignore punctuation ({DEFAULT_PUNCT_DISPLAY})",
            variable=self.subst_ignore_punct_var
        )
        self.subst_ignore_punct_checkbox.grid(row=4, column=0, pady=5, sticky="w")

        # Analyze button
        self.subst_analyze_btn = self._create_widget(ctk.CTkButton, left_frame, command=self.perform_subst_analyze)
        self.subst_analyze_btn.grid(row=5, column=0, pady=5, sticky="ew")

        # Character/token frequency label and textbox
        self.subst_freq_chars_label = self._create_widget(ctk.CTkLabel, left_frame)
        self.subst_freq_chars_label.grid(row=6, column=0, sticky="w")
        self.subst_freq_chars_textbox = self._create_widget(ctk.CTkTextbox, left_frame, height=100,
                                                            font=("Courier New", 11))
        self.subst_freq_chars_textbox.grid(row=7, column=0, pady=(0, 10), sticky="nsew")
        self.subst_freq_chars_textbox.configure(state="disabled")

        # Bigram frequency label and textbox
        self.subst_freq_bigrams_label = self._create_widget(ctk.CTkLabel, left_frame)
        self.subst_freq_bigrams_label.grid(row=8, column=0, sticky="w")
        self.subst_freq_bigrams_textbox = self._create_widget(ctk.CTkTextbox, left_frame, height=130,
                                                              font=("Courier New", 11))
        self.subst_freq_bigrams_textbox.grid(row=9, column=0, pady=(0, 5), sticky="nsew")
        self.subst_freq_bigrams_textbox.configure(state="disabled")
        
        # NEW: Static UA bigrams note under bigram frequency area
        self.subst_bigrams_note = self._create_widget(
            ctk.CTkLabel, left_frame,
            text="UA common: СТ, НО, НА, ПО, РА, НИ, КО, ТО, ПР, РО",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.subst_bigrams_note.grid(row=10, column=0, pady=(0, 10), sticky="w")

        # --- Right Column: Mapping Table & Output ---
        right_frame = self._create_widget(ctk.CTkFrame, tab, fg_color="transparent")
        right_frame.grid(row=1, column=1, rowspan=4, padx=(10, 20), pady=10, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)  # mapping table
        right_frame.grid_rowconfigure(6, weight=1)  # output textbox - give it weight too

        # Mapping table label and language selector
        mapping_header = self._create_widget(ctk.CTkFrame, right_frame, fg_color="transparent")
        mapping_header.grid(row=0, column=0, sticky="ew")
        mapping_header.grid_columnconfigure(1, weight=1)

        self.subst_mapping_label = self._create_widget(ctk.CTkLabel, mapping_header)
        self.subst_mapping_label.grid(row=0, column=0, sticky="w")

        # Language dropdown for frequency baseline
        self.subst_lang_label = self._create_widget(ctk.CTkLabel, mapping_header)
        self.subst_lang_label.grid(row=0, column=2, padx=(10, 5), sticky="e")

        lang = LANG_STRINGS[self.current_lang.get()]
        self.subst_freq_lang_var = ctk.StringVar(value=lang.get("subst_lang_ua", "Ukrainian"))
        self.subst_freq_lang_menu = self._create_widget(
            ctk.CTkOptionMenu, mapping_header,
            values=[lang.get("subst_lang_ua", "Ukrainian"), lang.get("subst_lang_en", "English")],
            variable=self.subst_freq_lang_var,
            width=120
        )
        self.subst_freq_lang_menu.grid(row=0, column=3, padx=5, sticky="e")

        # Mapping table container with scrollable frame - INCREASED height
        self.subst_mapping_container = self._create_widget(ctk.CTkScrollableFrame, right_frame, height=220)
        self.subst_mapping_container.grid(row=1, column=0, pady=5, sticky="nsew")
        self.subst_mapping_container.grid_columnconfigure((0, 1), weight=1)

        # Initialize mapping rows list
        self.subst_mapping_rows = []

        # Header row for mapping table
        header_cipher = self._create_widget(ctk.CTkLabel, self.subst_mapping_container, text="")
        header_cipher.grid(row=0, column=0, padx=5, pady=2, sticky="ew")
        self.subst_header_cipher = header_cipher

        header_plain = self._create_widget(ctk.CTkLabel, self.subst_mapping_container, text="")
        header_plain.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.subst_header_plain = header_plain

        # Initialize with a few empty rows instead of digits 0-9
        for _ in range(5):
            self.add_mapping_row()

        # Buttons for add/remove rows
        row_btns_frame = self._create_widget(ctk.CTkFrame, right_frame, fg_color="transparent")
        row_btns_frame.grid(row=2, column=0, pady=5, sticky="ew")

        self.subst_add_row_btn = self._create_widget(ctk.CTkButton, row_btns_frame, width=80,
                                                     command=self.add_mapping_row)
        self.subst_add_row_btn.grid(row=0, column=0, padx=5)

        self.subst_remove_row_btn = self._create_widget(ctk.CTkButton, row_btns_frame, width=80,
                                                        command=self.remove_mapping_row)
        self.subst_remove_row_btn.grid(row=0, column=1, padx=5)

        # Action buttons frame - first row
        action_btns_frame = self._create_widget(ctk.CTkFrame, right_frame, fg_color="transparent")
        action_btns_frame.grid(row=3, column=0, pady=5, sticky="ew")

        self.subst_apply_btn = self._create_widget(ctk.CTkButton, action_btns_frame, width=80,
                                                   command=self.perform_subst_apply)
        self.subst_apply_btn.grid(row=0, column=0, padx=3)

        self.subst_suggest_btn = self._create_widget(ctk.CTkButton, action_btns_frame, width=80,
                                                     command=self.perform_subst_suggest)
        self.subst_suggest_btn.grid(row=0, column=1, padx=3)

        self.subst_auto_replace_btn = self._create_widget(ctk.CTkButton, action_btns_frame, width=100,
                                                          command=self.perform_subst_auto_replace)
        self.subst_auto_replace_btn.grid(row=0, column=2, padx=3)

        self.subst_clear_btn = self._create_widget(ctk.CTkButton, action_btns_frame, width=80,
                                                   command=self.perform_subst_clear)
        self.subst_clear_btn.grid(row=0, column=3, padx=3)

        # Second row of action buttons (Undo/Redo, Export/Import)
        action_btns_frame2 = self._create_widget(ctk.CTkFrame, right_frame, fg_color="transparent")
        action_btns_frame2.grid(row=4, column=0, pady=2, sticky="ew")

        self.subst_undo_btn = self._create_widget(ctk.CTkButton, action_btns_frame2, width=70,
                                                  command=self.perform_subst_undo)
        self.subst_undo_btn.grid(row=0, column=0, padx=3)

        self.subst_redo_btn = self._create_widget(ctk.CTkButton, action_btns_frame2, width=70,
                                                  command=self.perform_subst_redo)
        self.subst_redo_btn.grid(row=0, column=1, padx=3)

        self.subst_export_btn = self._create_widget(ctk.CTkButton, action_btns_frame2, width=70,
                                                    command=self.perform_subst_export)
        self.subst_export_btn.grid(row=0, column=2, padx=3)

        self.subst_import_btn = self._create_widget(ctk.CTkButton, action_btns_frame2, width=70,
                                                    command=self.perform_subst_import)
        self.subst_import_btn.grid(row=0, column=3, padx=3)

        self.subst_export_txt_btn = self._create_widget(ctk.CTkButton, action_btns_frame2, width=80,
                                                        command=self.perform_subst_export_txt)
        self.subst_export_txt_btn.grid(row=0, column=4, padx=3)

        self.subst_import_txt_btn = self._create_widget(ctk.CTkButton, action_btns_frame2, width=80,
                                                        command=self.perform_subst_import_txt)
        self.subst_import_txt_btn.grid(row=0, column=5, padx=3)

        # NEW: Export Report button (exports number→letter correspondence with bigram connectivity)
        self.subst_export_report_btn = self._create_widget(ctk.CTkButton, action_btns_frame2, width=70,
                                                           command=self.perform_subst_export_report)
        self.subst_export_report_btn.grid(row=0, column=6, padx=3)

        # Output textbox - INCREASED height for better visibility of results
        self.subst_output_label = self._create_widget(ctk.CTkLabel, right_frame)
        self.subst_output_label.grid(row=5, column=0, sticky="w")
        self.subst_output_textbox = self._create_widget(ctk.CTkTextbox, right_frame, height=150)
        self.subst_output_textbox.grid(row=6, column=0, pady=(0, 10), sticky="nsew")
        
        # NEW: Bigram connectivity label and textbox
        self.subst_bigram_connectivity_label = self._create_widget(ctk.CTkLabel, right_frame)
        self.subst_bigram_connectivity_label.grid(row=7, column=0, sticky="w")
        self.subst_bigram_connectivity_textbox = self._create_widget(ctk.CTkTextbox, right_frame, height=100,
                                                                      font=("Courier New", 9))
        self.subst_bigram_connectivity_textbox.grid(row=8, column=0, pady=(0, 5), sticky="nsew")
        self.subst_bigram_connectivity_textbox.configure(state="disabled")

        # Status label
        self.subst_status_label = self._create_widget(ctk.CTkLabel, tab, text="",
                                                      font=ctk.CTkFont(size=12))
        self.subst_status_label.grid(row=5, column=0, columnspan=2, padx=20, pady=5, sticky="w")

    def add_mapping_row(self, initial_cipher: str = "", initial_plain: str = ""):
        """Add a new row to the substitution mapping table."""
        row_idx = len(self.subst_mapping_rows) + 1  # +1 because row 0 is header

        cipher_entry = self._create_widget(ctk.CTkEntry, self.subst_mapping_container, width=80)
        cipher_entry.grid(row=row_idx, column=0, padx=5, pady=2, sticky="ew")
        if initial_cipher:
            cipher_entry.insert(0, initial_cipher)

        plain_entry = self._create_widget(ctk.CTkEntry, self.subst_mapping_container, width=80)
        plain_entry.grid(row=row_idx, column=1, padx=5, pady=2, sticky="ew")
        if initial_plain:
            plain_entry.insert(0, initial_plain)

        self.subst_mapping_rows.append((cipher_entry, plain_entry))

    def remove_mapping_row(self):
        """Remove the last row from the substitution mapping table."""
        if self.subst_mapping_rows:
            cipher_entry, plain_entry = self.subst_mapping_rows.pop()
            cipher_entry.destroy()
            plain_entry.destroy()

    def get_current_mapping(self) -> dict:
        """Get the current mapping dict from the UI entries."""
        mapping = {}
        for cipher_entry, plain_entry in self.subst_mapping_rows:
            cipher = cipher_entry.get().strip()
            plain = plain_entry.get().strip()
            if cipher:  # Only add if cipher symbol is not empty
                mapping[cipher] = plain
        return mapping

    def set_mapping_rows(self, mapping: dict):
        """Set the mapping table rows from a dict."""
        # Clear existing rows
        while self.subst_mapping_rows:
            self.remove_mapping_row()

        # Add rows for the mapping
        for cipher, plain in mapping.items():
            self.add_mapping_row(initial_cipher=cipher, initial_plain=plain)

        # If empty mapping, add at least one empty row
        if not mapping:
            self.add_mapping_row()

    def perform_subst_analyze(self):
        """Analyze the input ciphertext for token/character and bigram frequencies."""
        lang = LANG_STRINGS[self.current_lang.get()]
        text = self.subst_input_textbox.get("1.0", tk.END).strip()

        if not text:
            self.subst_status_label.configure(text=lang["subst_status_error_input"], text_color="red")
            return

        use_two_digit = bool(self.subst_two_digit_var.get())
        if use_two_digit:
            tokens = tokenize_text_two_digit_mode(text)
            # Token frequency (digit tokens only)
            freqs = compute_token_freq(tokens)
            char_text = "Tok  Count   %\n" + "-" * 22 + "\n"
            for tok, cnt, pct in freqs[:30]:
                char_text += f"{tok:4} {cnt:5}  {pct:5.1f}%\n"
            # Token bigrams
            bg_freqs = compute_token_bigram_freq(tokens, top_n=15)
            bigram_text = "TokTok  Count   %\n" + "-" * 24 + "\n"
            for bg, cnt, pct in bg_freqs:
                bigram_text += f"{bg:6} {cnt:5}  {pct:5.1f}%\n"
        else:
            char_freq = compute_char_freq(text)
            char_text = "Sym  Count   %\n" + "-" * 20 + "\n"
            for char, count, pct in char_freq[:30]:
                char_text += f"{char:4} {count:5}  {pct:5.1f}%\n"
            bigram_freq = compute_bigram_freq(text, top_n=15)
            bigram_text = "Bigram  Count   %\n" + "-" * 22 + "\n"
            for bg, count, pct in bigram_freq:
                bigram_text += f"{bg:6} {count:5}  {pct:5.1f}%\n"

        self.subst_freq_chars_textbox.configure(state="normal")
        self.subst_freq_chars_textbox.delete("1.0", tk.END)
        self.subst_freq_chars_textbox.insert("1.0", char_text)
        self.subst_freq_chars_textbox.configure(state="disabled")

        self.subst_freq_bigrams_textbox.configure(state="normal")
        self.subst_freq_bigrams_textbox.delete("1.0", tk.END)
        self.subst_freq_bigrams_textbox.insert("1.0", bigram_text)
        self.subst_freq_bigrams_textbox.configure(state="disabled")

        self.subst_status_label.configure(text=lang["subst_status_ok_analyze"], text_color="green")


    def perform_subst_suggest(self):
        """
        Suggest mapping using token or character frequency depending on mode.
        """
        lang_ui = LANG_STRINGS[self.current_lang.get()]
        text = self.subst_input_textbox.get("1.0", tk.END).strip()

        if not text:
            self.subst_status_label.configure(text=lang_ui["subst_status_error_input"], text_color="red")
            return

        self.snapshot_current_mapping()

        freq_lang_value = self.subst_freq_lang_var.get()
        target_lang = "en" if freq_lang_value == lang_ui.get("subst_lang_en", "English") else "ua"

        use_two_digit = bool(self.subst_two_digit_var.get())
        if use_two_digit:
            tokens = tokenize_text_two_digit_mode(text)
            units_sorted = detect_cipher_symbols_tokens(tokens)
            # normalized frequency over digit tokens only
            dfreq = Counter([t for t, is_digit in tokens if is_digit])
            total = sum(dfreq.values()) or 1
            unit_freq = {tok: dfreq[tok] / total for tok in dfreq}
            suggested = suggest_mapping_by_frequency(units_sorted, unit_freq, target_lang, limit=None)
        else:
            cipher_symbols = detect_cipher_symbols(text)
            cipher_freq = compute_cipher_frequencies_lower(text)
            suggested = compare_frequencies(cipher_freq, ukr_letter_freq if target_lang == 'ua' else en_letter_freq)

        self.set_mapping_rows(suggested)
        self.perform_subst_analyze()
        self.subst_status_label.configure(text=lang_ui["subst_status_ok_suggest"], text_color="green")

    def perform_subst_apply(self):
        """Apply the current mapping to the input text and show result."""
        lang = LANG_STRINGS[self.current_lang.get()]
        text = self.subst_input_textbox.get("1.0", tk.END).strip()

        if not text:
            self.subst_status_label.configure(text=lang["subst_status_error_input"], text_color="red")
            return

        self.snapshot_current_mapping()

        mapping = self.get_current_mapping()
        # Normalize mapping values to uppercase single letters (leave non-letters as-is)
        norm_mapping = {k: (v.upper() if len(v) == 1 else v) for k, v in mapping.items() if k}
        
        # Get ignore punctuation setting
        ignore_punct = bool(self.subst_ignore_punct_var.get()) if hasattr(self, 'subst_ignore_punct_var') else False
        use_two_digit = bool(self.subst_two_digit_var.get())

        result = detokenize_apply_mapping(
            text, norm_mapping, 
            use_two_digit_mode=use_two_digit,
            ignore_punct=ignore_punct
        )
        self.subst_output_textbox.delete("1.0", tk.END)
        self.subst_output_textbox.insert("1.0", result)
        
        # Update bigram connectivity display
        self.update_bigram_connectivity_display(text, norm_mapping, result, use_two_digit)
        
        self.subst_status_label.configure(text=lang["subst_status_ok_apply"], text_color="green")

    def perform_subst_clear(self):
        """Clear the mapping table."""
        lang = LANG_STRINGS[self.current_lang.get()]
        # Save state before clear
        self.snapshot_current_mapping()
        while self.subst_mapping_rows:
            self.remove_mapping_row()
        # Re-add a few empty rows for user convenience
        for _ in range(5):
            self.add_mapping_row()
        self.subst_output_textbox.delete("1.0", tk.END)
        self.subst_status_label.configure(text=lang["subst_status_ok_clear"], text_color="green")

    def perform_subst_export(self):
        """Export the current mapping to a JSON file."""
        lang = LANG_STRINGS[self.current_lang.get()]
        mapping = self.get_current_mapping()

        try:
            path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("All files", "*.*")],
                initialfile="mapping.json"
            )
            if not path:
                return

            json_str = serialize_mapping(mapping)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(json_str)

            self.subst_status_label.configure(text=lang["subst_status_ok_export"], text_color="green")
        except Exception as e:
            logger.error(f"Export mapping failed: {e}")
            self.subst_status_label.configure(text=lang['subst_status_error_export'], text_color="red")

    def perform_subst_import(self):
        """Import a mapping from a JSON file."""
        lang = LANG_STRINGS[self.current_lang.get()]

        try:
            path = filedialog.askopenfilename(
                filetypes=[("JSON Files", "*.json"), ("All files", "*.*")]
            )
            if not path:
                return

            with open(path, 'r', encoding='utf-8') as f:
                json_str = f.read()

            mapping = deserialize_mapping(json_str)
            self.snapshot_current_mapping()  # Save state before import
            self.set_mapping_rows(mapping)
            self.subst_status_label.configure(text=lang["subst_status_ok_import"], text_color="green")
        except Exception as e:
            logger.error(f"Import mapping failed: {e}")
            self.subst_status_label.configure(text=lang['subst_status_error_import'], text_color="red")

    def snapshot_current_mapping(self):
        """Save the current mapping state to the undo stack."""
        mapping = self.get_current_mapping()
        self.subst_undo_stack.append(mapping)
        # Clear redo stack when a new action is taken
        self.subst_redo_stack.clear()
        # Limit stack size to prevent memory issues
        if len(self.subst_undo_stack) > MAX_UNDO_STACK_SIZE:
            self.subst_undo_stack.pop(0)

    def restore_mapping(self, mapping: dict):
        """Restore a mapping from a snapshot and apply it to the UI."""
        self.set_mapping_rows(mapping)
        # Apply the mapping
        text = self.subst_input_textbox.get("1.0", tk.END).strip()
        if text:
            result = apply_substitution_mapping(text, mapping)
            self.subst_output_textbox.delete("1.0", tk.END)
            self.subst_output_textbox.insert("1.0", result)

    def perform_subst_undo(self):
        """Undo the last mapping change."""
        lang = LANG_STRINGS[self.current_lang.get()]
        if not self.subst_undo_stack:
            return

        # Save current state to redo stack
        current = self.get_current_mapping()
        self.subst_redo_stack.append(current)

        # Restore previous state
        prev_mapping = self.subst_undo_stack.pop()
        self.restore_mapping(prev_mapping)
        self.subst_status_label.configure(text=lang.get("subst_undo", "Undo"), text_color="gray")

    def perform_subst_redo(self):
        """Redo the last undone mapping change."""
        lang = LANG_STRINGS[self.current_lang.get()]
        if not self.subst_redo_stack:
            return

        # Save current state to undo stack
        current = self.get_current_mapping()
        self.subst_undo_stack.append(current)

        # Restore redo state
        next_mapping = self.subst_redo_stack.pop()
        self.restore_mapping(next_mapping)
        self.subst_status_label.configure(text=lang.get("subst_redo", "Redo"), text_color="gray")

    def perform_subst_auto_replace(self):
        """
        Auto Replace with hillclimb.
        In two-digit mode, we generate mapping over digit tokens and apply token-aware rendering.
        Supports ignore punctuation mode.
        """
        lang_ui = LANG_STRINGS[self.current_lang.get()]
        text = self.subst_input_textbox.get("1.0", tk.END).strip()
        if not text:
            self.subst_status_label.configure(text=lang_ui["subst_status_error_input"], text_color="red")
            return

        freq_lang_value = self.subst_freq_lang_var.get()
        lang_code = 'ua' if freq_lang_value == lang_ui.get("subst_lang_ua", "Українська") else 'en'

        use_two_digit = bool(self.subst_two_digit_var.get())
        ignore_punct = bool(self.subst_ignore_punct_var.get()) if hasattr(self, 'subst_ignore_punct_var') else False
        
        self.subst_status_label.configure(text="⏳ Оптимізація (hillclimb)...", text_color="yellow")
        self.update_idletasks()

        def worker():
            try:
                if use_two_digit:
                    # Build initial mapping from digit tokens
                    tokens = tokenize_text_two_digit_mode(text)
                    units_sorted = detect_cipher_symbols_tokens(tokens)
                    dfreq = Counter([t for t, is_digit in tokens if is_digit])
                    total = sum(dfreq.values()) or 1
                    unit_freq = {tok: dfreq[tok] / total for tok in dfreq}
                    base_mapping = suggest_mapping_by_frequency(units_sorted, unit_freq, lang_code, limit=None)

                    # Simple refinement via random swaps on token mapping using scoring of rendered plaintext
                    rng = random.Random()
                    best_map = base_mapping.copy()
                    best_plain = detokenize_apply_mapping(text, best_map, use_two_digit_mode=True, ignore_punct=ignore_punct)
                    bigram_model = _build_bigram_model(lang_code)
                    letter_model = _build_letter_freq_model(lang_code)
                    best_score = _subst_score_plaintext(best_plain, bigram_model, letter_model, lang=lang_code)

                    iterations = 4000
                    stagnation_count = 0
                    for _ in range(iterations):
                        if len(best_map) < 2:
                            break
                        keys = list(best_map.keys())
                        k1, k2 = rng.sample(keys, 2)
                        cand = best_map.copy()
                        cand[k1], cand[k2] = cand[k2], cand[k1]
                        cand_plain = detokenize_apply_mapping(text, cand, use_two_digit_mode=True, ignore_punct=ignore_punct)
                        cand_score = _subst_score_plaintext(cand_plain, bigram_model, letter_model, lang=lang_code)
                        if cand_score > best_score:
                            best_map, best_plain, best_score = cand, cand_plain, cand_score
                            stagnation_count = 0
                        else:
                            stagnation_count += 1
                        # Early stopping
                        if stagnation_count > 500:
                            break

                    self.after(0, lambda: self._subst_auto_done(best_map, best_plain, best_score, lang_code))
                else:
                    mapping, plaintext, score = subst_hillclimb(
                        text, lang=lang_code,
                        iterations=5000, restarts=6,
                        smoothing=1e-6, temp_start=1.0,
                        temp_decay=0.00025, seed=None,
                        early_stop_threshold=800
                    )
                    self.after(0, lambda: self._subst_auto_done(mapping, plaintext, score, lang_code))
            except Exception as e:
                self.after(0, lambda: self.subst_status_label.configure(
                    text=f"Помилка оптимізації: {e}", text_color="red"))

        threading.Thread(target=worker, daemon=True).start()


    def _subst_auto_done(self, mapping, plaintext, score, lang_code):
        lang_ui = LANG_STRINGS[self.current_lang.get()]
        if not mapping:
            self.subst_status_label.configure(text="Не вдалося побудувати заміну.", text_color="red")
            return

        # Оновити таблицю
        self.set_mapping_rows(mapping)
        
        # Apply ignore punctuation setting if enabled
        ignore_punct = bool(self.subst_ignore_punct_var.get()) if hasattr(self, 'subst_ignore_punct_var') else False
        text = self.subst_input_textbox.get("1.0", tk.END).strip()
        use_two_digit = bool(self.subst_two_digit_var.get())
        
        if ignore_punct:
            # Re-apply with punctuation ignored for display
            plaintext = detokenize_apply_mapping(
                text, mapping, 
                use_two_digit_mode=use_two_digit,
                ignore_punct=True
            )
        
        # Compute diagnostics for result header
        diagnostics = _compute_plaintext_diagnostics(plaintext, lang_code)
        
        # Build result header with diagnostics
        header = f"Score={score:.2f}, Vowels={diagnostics['vowel_ratio']:.1f}%, BadRepeats={diagnostics['bad_repeats']}, MaxCCRun={diagnostics['max_cc_run']}\n"
        header += "-" * 50 + "\n"
        
        # Поставити результат with header
        self.subst_output_textbox.delete("1.0", tk.END)
        self.subst_output_textbox.insert("1.0", header + plaintext)

        # Запустити аналіз частот (оновити панелі)
        self.perform_subst_analyze()
        # Підсвічування (використовує існуючий метод)
        self.highlight_mapping_confidence(plaintext, lang_code)
        
        # Update bigram connectivity display
        self.update_bigram_connectivity_display(text, mapping, plaintext, use_two_digit)

        self.subst_status_label.configure(
            text=f"{lang_ui.get('subst_status_ok_auto','Auto replacement applied.')} | Score={score:.2f}",
            text_color="green"
        )

    def highlight_mapping_confidence(self, text: str, lang: str):
        """
        Highlight mapping entries based on confidence level.
        High-probability mappings get light green background,
        low-probability get light red background.
        """
        if lang == 'ua':
            lang_freq = ukr_letter_freq
        else:
            lang_freq = en_letter_freq

        # Calculate cipher symbol frequencies
        cipher_freq = compute_cipher_frequencies_lower(text)

        # Sort both by frequency
        cipher_sorted = sorted(cipher_freq.items(), key=lambda x: x[1], reverse=True)
        lang_sorted = sorted(lang_freq.items(), key=lambda x: x[1], reverse=True)

        # Create a confidence score for each position
        # Higher positions (more frequent) get higher confidence
        for idx, (cipher_entry, plain_entry) in enumerate(self.subst_mapping_rows):
            try:
                # Top quartile = high confidence (green)
                # Bottom quartile = low confidence (red)
                # Middle = neutral (default)
                total = len(self.subst_mapping_rows)
                if total == 0:
                    continue

                position_ratio = idx / total

                if position_ratio <= 0.25:
                    # High confidence - light green
                    self.set_entry_confidence(plain_entry, "high")
                elif position_ratio >= 0.75:
                    # Low confidence - light red
                    self.set_entry_confidence(plain_entry, "low")
                else:
                    # Neutral - default
                    self.set_entry_confidence(plain_entry, "neutral")
            except Exception:
                pass

    def set_entry_confidence(self, entry, level: str):
        """Set entry background color based on confidence level."""
        try:
            if level == "high":
                entry.configure(fg_color=CONFIDENCE_HIGH_COLOR)
            elif level == "low":
                entry.configure(fg_color=CONFIDENCE_LOW_COLOR)
            else:
                entry.configure(fg_color=None)  # Default
        except Exception:
            pass

    def perform_subst_export_txt(self):
        """Export the current mapping to a TXT file (cipher=plain format)."""
        lang = LANG_STRINGS[self.current_lang.get()]
        mapping = self.get_current_mapping()

        try:
            path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All files", "*.*")],
                initialfile="mapping.txt"
            )
            if not path:
                return

            # Write lines in "cipher=plain" format
            lines = [f"{cipher}={plain}" for cipher, plain in mapping.items()]
            with open(path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            self.subst_status_label.configure(text=lang.get("subst_status_ok_export_txt", "Mapping exported to TXT."),
                                              text_color="green")
        except Exception as e:
            logger.error(f"Export TXT mapping failed: {e}")
            self.subst_status_label.configure(text=lang.get('subst_status_error_export', "Export error"),
                                              text_color="red")

    def perform_subst_import_txt(self):
        """Import a mapping from a TXT file (cipher=plain format)."""
        lang = LANG_STRINGS[self.current_lang.get()]

        try:
            path = filedialog.askopenfilename(
                filetypes=[("Text Files", "*.txt"), ("All files", "*.*")]
            )
            if not path:
                return

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse lines in "cipher=plain" format
            mapping = {}
            for line in content.strip().split('\n'):
                line = line.strip()
                if '=' in line:
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        cipher, plain = parts
                        mapping[cipher] = plain

            self.snapshot_current_mapping()  # Save state before import
            self.set_mapping_rows(mapping)
            self.subst_status_label.configure(text=lang.get("subst_status_ok_import_txt", "Mapping imported from TXT."),
                                              text_color="green")
        except Exception as e:
            logger.error(f"Import TXT mapping failed: {e}")
            self.subst_status_label.configure(text=lang.get('subst_status_error_import_txt', "Invalid TXT file."),
                                              text_color="red")

    def perform_subst_export_report(self):
        """Export number→letter correspondence report with bigram connectivity to TXT or CSV."""
        lang = LANG_STRINGS[self.current_lang.get()]
        mapping = self.get_current_mapping()
        text = self.subst_input_textbox.get("1.0", tk.END).strip()
        use_two_digit = bool(self.subst_two_digit_var.get())
        ignore_punct = bool(self.subst_ignore_punct_var.get()) if hasattr(self, 'subst_ignore_punct_var') else False
        
        # Get current plaintext
        plaintext = self.subst_output_textbox.get("1.0", tk.END).strip()
        if not plaintext:
            # Generate if not available
            norm_mapping = {k: (v.upper() if len(v) == 1 else v) for k, v in mapping.items() if k}
            plaintext = detokenize_apply_mapping(text, norm_mapping, use_two_digit_mode=use_two_digit, ignore_punct=ignore_punct)
        
        try:
            path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All files", "*.*")],
                initialfile="mapping_report.txt"
            )
            if not path:
                return
            
            # Determine format from extension
            file_format = 'csv' if path.lower().endswith('.csv') else 'txt'
            
            export_mapping_report(mapping, text, plaintext, use_two_digit, path, format=file_format)
            
            self.subst_status_label.configure(text=lang.get("subst_status_ok_export_report", "Report exported."),
                                              text_color="green")
        except Exception as e:
            logger.error(f"Export report failed: {e}")
            self.subst_status_label.configure(text=lang.get('subst_status_error_export', "Export error"),
                                              text_color="red")

    def update_bigram_connectivity_display(self, text: str, mapping: dict, plaintext: str, use_two_digit: bool):
        """Update the bigram connectivity textbox with current cipher and plaintext bigram tables."""
        try:
            cipher_table = compute_cipher_bigram_freq_table(text, mapping, use_two_digit, top_n=10)
            plain_table = compute_plaintext_bigram_freq_table(plaintext, top_n=10)
            
            display_text = format_connectivity_table(cipher_table, plain_table)
            
            self.subst_bigram_connectivity_textbox.configure(state="normal")
            self.subst_bigram_connectivity_textbox.delete("1.0", tk.END)
            self.subst_bigram_connectivity_textbox.insert("1.0", display_text)
            self.subst_bigram_connectivity_textbox.configure(state="disabled")
        except Exception as e:
            logger.error(f"Error updating bigram connectivity: {e}")

    # --- show/hide frames ---
    def hide_all_frames(self):
        for f in [self.xor_frame, self.lsb_frame, self.picker_frame, self.vigenere_frame, self.base64_frame,
                  self.ela_frame,
                  self.aes_frame, self.sdes_frame, self.subst_frame, self.settings_frame, self.about_frame]:
            try:
                f.grid_forget()
            except Exception:
                pass

    def show_aes_frame(self):
        self.hide_all_frames()
        self.aes_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

    def show_sdes_frame(self):
        self.hide_all_frames()
        self.sdes_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

    def show_subst_frame(self):
        self.hide_all_frames()
        self.subst_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

    def show_xor_frame(self):
        self.hide_all_frames()
        self.xor_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
        self._refresh_all_images()

    def show_lsb_frame(self):
        self.hide_all_frames()
        self.lsb_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
        self._refresh_all_images()

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
        self._refresh_all_images()

    def show_settings_frame(self):
        self.hide_all_frames()
        self.settings_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

    def show_about_frame(self):
        self.hide_all_frames()
        self.about_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

    # ---------- AES / S-DES operations ----------

    def _aes_brute_done_callback(self, matches, duration):
        lang = LANG_STRINGS[self.current_lang.get()]
        self.aes_output_textbox.delete("1.0", tk.END)
        if not matches:
            self.aes_status_label.configure(text=lang["brute_no_results"], text_color="red")
            return
        s = []
        for pin, pt in matches:
            try:
                pt_text = pt.decode("utf-8", errors="replace")
            except Exception:
                pt_text = repr(pt)
            s.append(f"PIN={pin} => plaintext: {pt_text}\n")
        s.append(f"\nDuration: {duration:.2f}s\n")
        self.aes_output_textbox.insert("1.0", "\n".join(s))
        self.aes_status_label.configure(text=lang["brute_done"], text_color="green")

    def perform_sdes_operation(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        mode = self.sdes_mode.get()
        data_text = self.sdes_input_textbox.get("1.0", tk.END).strip()
        key_s = self.sdes_key_entry.get().strip()
        try:
            key_int = int(key_s)
            if not (0 <= key_int <= 1023):
                raise ValueError("Key must be 0..1023")
        except Exception:
            self.sdes_status_label.configure(text="Invalid 10-bit key", text_color="red")
            return

        try:
            if mode == lang["mode_encrypt"]:
                out = sdes_encrypt_bytes(data_text.encode("utf-8"), key_int)
                self.sdes_output_textbox.delete("1.0", tk.END)
                self.sdes_output_textbox.insert("1.0", base64.b64encode(out).decode('utf-8'))
            else:
                try:
                    cb = base64.b64decode(data_text)
                    pt = sdes_decrypt_bytes(cb, key_int)
                    self.sdes_output_textbox.delete("1.0", tk.END)
                    self.sdes_output_textbox.insert("1.0", pt.decode("utf-8", errors="replace"))
                except Exception as e:
                    self.sdes_output_textbox.delete("1.0", tk.END)
                    self.sdes_output_textbox.insert("1.0", f"Error decoding/decrypting: {e}")
            self.sdes_status_label.configure(text="OK", text_color="green")
        except Exception as e:
            self.sdes_status_label.configure(text=f"Error: {e}", text_color="red")

    def perform_sdes_bruteforce(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        data_b64 = self.sdes_input_textbox.get("1.0", tk.END).strip()
        known_frag = self.sdes_known_fragment_entry.get().strip().encode(
            'utf-8') if self.sdes_known_fragment_entry.get().strip() else None
        if not data_b64:
            self.sdes_status_label.configure(text="Provide S-DES base64 ciphertext in input box", text_color="red")
            return
        try:
            cipherbytes = base64.b64decode(data_b64)
        except Exception:
            self.sdes_status_label.configure(text="Input must be base64 S-DES ciphertext", text_color="red")
            return

        self.sdes_status_label.configure(text=lang["brute_status"], text_color="yellow")
        self.update_idletasks()

        def worker():
            start = time.time()
            matches = sdes_bruteforce(cipherbytes, known_fragment=known_frag)
            duration = time.time() - start
            self.after(0, self._sdes_brute_done_callback, matches, duration)

        threading.Thread(target=worker, daemon=True).start()

    def _sdes_brute_done_callback(self, matches, duration):
        lang = LANG_STRINGS[self.current_lang.get()]
        self.sdes_output_textbox.delete("1.0", tk.END)
        if not matches:
            self.sdes_status_label.configure(text=lang["brute_no_results"], text_color="red")
            return
        out_lines = []
        for key, pt in matches:
            try:
                pt_text = pt.decode('utf-8', errors='replace')
            except Exception:
                pt_text = repr(pt)
            out_lines.append(f"key={key:03d} => {pt_text}")
        out_lines.append(f"\nDuration: {duration:.2f}s")
        self.sdes_output_textbox.insert("1.0", "\n".join(out_lines))
        self.sdes_status_label.configure(text=lang["brute_done"], text_color="green")

    # ---------- The rest: image handling, LSB extraction, Vigenere, Base64, ELA, helper methods ----------
    def load_xor_image1(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.bmp")])
        if not path: return
        self.xor_image_path1 = path
        try:
            pil_img = Image.open(path).convert('RGB')
            self.xor_pil1 = pil_img
            self.show_pil_image_on_label(self.xor_pil1, self.xor_label1, keep_aspect=True)
            self.xor_status_label.configure(text="")
        except Exception as e:
            self.xor_status_label.configure(text=f"Error loading: {e}", text_color="red")

    def load_xor_image2(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.bmp")])
        if not path: return
        self.xor_image_path2 = path
        try:
            pil_img = Image.open(path).convert('RGB')
            self.xor_pil2 = pil_img
            self.show_pil_image_on_label(self.xor_pil2, self.xor_label2, keep_aspect=True)
            self.xor_status_label.configure(text="")
        except Exception as e:
            self.xor_status_label.configure(text=f"Error loading: {e}", text_color="red")

    def perform_xor(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        if not self.xor_pil1 or not self.xor_pil2:
            self.xor_status_label.configure(text=lang["xor_status_error_load"], text_color="red")
            return

        self.xor_status_label.configure(text=lang["xor_status_processing"], text_color="yellow")
        self.update_idletasks()
        try:
            result_pil = self.xor_images_from_pils(self.xor_pil1, self.xor_pil2)
            self.xor_result_pil = result_pil
            self.show_pil_image_on_label(result_pil, self.xor_result_label, keep_aspect=True)
            self.xor_status_label.configure(text=lang["xor_status_ok"], text_color="green")
        except Exception as e:
            self.xor_status_label.configure(text=f"Error: {e}", text_color="red")

    def xor_images_from_pils(self, pil1, pil2):
        lang = LANG_STRINGS[self.current_lang.get()]
        img1 = pil1.convert('RGB')
        img2 = pil2.convert('RGB')

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

    def load_lsb_image(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        path = filedialog.askopenfilename(filetypes=[("Images (PNG/BMP)", "*.png *.bmp"), ("All files", "*.*")])
        if not path: return

        self.lsb_image_path = path
        try:
            pil_img = Image.open(path).convert('RGB')
            self.lsb_original_pil = pil_img
            self.show_pil_image_on_label(pil_img, self.lsb_original_label, keep_aspect=True)
            self.lsb_text_result.delete("1.0", "end")

            if not path.lower().endswith((".png", ".bmp")):
                self.lsb_status_label.configure(text=lang["lsb_status_warn_format"], text_color="orange")
            else:
                self.lsb_status_label.configure(text=lang["lsb_status_ok_load"], text_color="gray")

            try:
                result_pil_img = self.extract_lsb_image(self.lsb_image_path)
                if result_pil_img:
                    self.lsb_result_pil = result_pil_img
                    self.show_pil_image_on_label(result_pil_img, self.lsb_result_label, keep_aspect=True)
            except Exception:
                self._safe_set_label_text(self.lsb_result_label, lang["lsb_result_text"])
                self.lsb_result_label.image = None
        except Exception as e:
            self.lsb_status_label.configure(text=f"Error loading: {e}", text_color="red")

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

    def load_picker_image(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.bmp")])
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
            self.show_pil_image_on_label(self.picker_pil_image, self.picker_image_label, keep_aspect=True)
            return

        for i in range(0, w, 10):
            draw.line([(i, 0), (i, h)], fill=(128, 128, 128, 100), width=1)
        for i in range(0, h, 10):
            draw.line([(0, i), (w, i)], fill=(128, 128, 128, 100), width=1)
        self.show_pil_image_on_label(img_with_grid, self.picker_image_label, keep_aspect=True)

    def on_image_click(self, event):
        lang = LANG_STRINGS[self.current_lang.get()]
        if not self.picker_pil_image:
            self.picker_status_label.configure(text=lang["picker_status_error_load"], text_color="yellow")
            return
        try:
            label = self.picker_image_label
            if not hasattr(label, "image") or label.image is None:
                display_w, display_h = self.picker_pil_image.size
            else:
                display_w = label.winfo_width() or self.picker_pil_image.size[0]
                display_h = label.winfo_height() or self.picker_pil_image.size[1]

            pil_img_w, pil_img_h = self.picker_pil_image.size
            w_ratio = pil_img_w / max(1, display_w)
            h_ratio = pil_img_h / max(1, display_h)
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

    def hex_color_to_text(self, hex_code: str) -> str:
        try:
            hex_val = hex_code.lstrip('#')
            r_int, g_int, b_int = int(hex_val[0:2], 16), int(hex_val[2:4], 16), int(hex_val[4:6], 16)
            r_char = chr(r_int) if chr(r_int).isprintable() else ''
            g_char = chr(g_int) if chr(g_int).isprintable() else ''
            b_char = chr(b_int) if chr(b_int).isprintable() else ''
            return f"{r_char}{g_char}{b_char}"
        except Exception:
            return ""

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

    def perform_vigenere_crack(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        ciphertext = self.vigenere_input_textbox.get("1.0", tk.END).strip()
        if not ciphertext:
            self.vigenere_status_label.configure(text=lang["vigenere_status_error_input"], text_color="red")
            return
        try:
            try:
                max_k = int(self.vigenere_crack_max_key_entry.get())
                if max_k < 1 or max_k > 60:
                    max_k = 20
            except Exception:
                max_k = 20

            self.vigenere_status_label.configure(text=lang["vigenere_status_cracking"], text_color="yellow")
            self.update_idletasks()

            def worker():
                try:
                    key, klen, plaintext = self.break_vigenere_no_key(ciphertext, max_key_len=max_k)
                    self.after(0, lambda: self._vigenere_crack_done(key, klen, plaintext))
                except Exception as e:
                    self.after(0, lambda: self.vigenere_status_label.configure(text=f"Error: {e}", text_color="red"))

            threading.Thread(target=worker, daemon=True).start()
        except Exception as e:
            self.vigenere_status_label.configure(text=f"Error: {e}", text_color="red")

    def _vigenere_crack_done(self, key, klen, plaintext):
        lang = LANG_STRINGS[self.current_lang.get()]
        self.vigenere_output_textbox.delete("1.0", tk.END)
        self.vigenere_output_textbox.insert("1.0", plaintext)
        guess_msg = f"{lang['vigenere_key_guess_default'].split(':')[0]}: {key}  (len={klen})"
        self.vigenere_key_guess_label.configure(text=guess_msg)
        self.vigenere_status_label.configure(text=lang["vigenere_status_ok_crack"], text_color="green")

    def perform_base64_operation(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        mode = self.base64_mode.get()
        input_text = self.base64_input_textbox.get("1.0", tk.END).strip()

        if not input_text:
            self.base64_status_label.configure(text=lang["base64_status_error_input"], text_color="red")
            return

        self.base64_output_textbox.delete("1.0", tk.END)
        try:
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

        except (base64.binascii.Error, UnicodeDecodeError):
            self.base64_status_label.configure(text=lang["base64_status_error_decode"], text_color="red")
        except Exception as e:
            self.base64_status_label.configure(text=f"Error: {e}", text_color="red")

    def load_ela_image(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tiff")])
        if not path: return

        self.ela_image_path = path
        try:
            pil_img = Image.open(path).convert('RGB')
            self.ela_original_pil = pil_img
            self.show_pil_image_on_label(pil_img, self.ela_original_label, keep_aspect=True)
            self._safe_set_label_text(self.ela_result_label, lang["ela_result_text"])
            self.ela_result_label.image = None
            self.ela_status_label.configure(text="")
        except Exception as e:
            self.ela_status_label.configure(text=f"Error loading: {e}", text_color="red")

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
                self.ela_result_pil = ela_result_img
                self.show_pil_image_on_label(ela_result_img, self.ela_result_label, keep_aspect=True)
                self.ela_status_label.configure(text=lang["ela_status_ok"], text_color="green")
            else:
                self._safe_set_label_text(self.ela_result_label, lang["ela_result_text"])
                self.ela_result_label.image = None
                self.ela_status_label.configure(text="ELA Error", text_color="red")
        except Exception as e:
            self._safe_set_label_text(self.ela_result_label, lang["ela_result_text"])
            self.ela_result_label.image = None
            self.ela_status_label.configure(text=f"Error: {e}", text_color="red")

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

    def self_destruct(self):
        if self._self_destruct_running:
            return
        lang = LANG_STRINGS[self.current_lang.get()]
        try:
            self._self_destruct_running = True
            self.self_destruct_progress.set(0)
            self.self_destruct_btn.configure(state="disabled", text=lang["settings_self_destruct_run"])

            start = time.time()
            duration = 2.0  # seconds
            steps = 100
            interval_ms = int(duration * 1000 / steps)

            def step(i=0):
                if i > steps:
                    self.self_destruct_btn.configure(state="normal", text=lang["settings_self_destruct"])
                    self._self_destruct_running = False
                    try:
                        messagebox.showinfo(lang["settings_self_destruct"], lang["settings_self_destruct_prank"])
                    except Exception:
                        pass
                    return
                self.self_destruct_progress.set(i / steps)
                self.after(interval_ms, lambda: step(i + 1))

            step(0)
        except Exception:
            self._self_destruct_running = False
            self.self_destruct_btn.configure(state="normal", text=lang["settings_self_destruct"])

    def _safe_set_label_text(self, label, text):
        try:
            label.configure(image=None, text=text)
            label.image = None
        except tk.TclError:
            try:
                if hasattr(label, "_label") and getattr(label, "_label") is not None:
                    label._label.configure(image="", text=text)
                    label.image = None
            except Exception:
                try:
                    label.configure(text=text)
                except Exception:
                    pass

    def show_pil_image_on_label(self, pil_img, label, size=None, keep_aspect=False):
        if not label or not label.winfo_exists():
            return

        if pil_img is None:
            try:
                self._safe_set_label_text(label, "Error")
            except Exception:
                pass
            return
        try:
            display_size = size
            if size is None:
                w = label.winfo_width()
                h = label.winfo_height()
                if w <= 1 or h <= 1:
                    main_w = max(600, self.winfo_width() - 240)
                    main_h = max(400, self.winfo_height() - 160)
                    display_size = (min(800, main_w), min(600, main_h // 2))
                else:
                    display_size = (w, h)

            if keep_aspect:
                iw, ih = pil_img.size
                if iw == 0 or ih == 0:
                    return
                max_w, max_h = int(display_size[0]), int(display_size[1])
                ratio = min(max_w / iw, max_h / ih) if iw > 0 and ih > 0 else 1
                target_w = max(1, int(iw * ratio))
                target_h = max(1, int(ih * ratio))
            else:
                target_w = max(1, int(display_size[0]))
                target_h = max(1, int(display_size[1]))

            resized = pil_img.copy().resize((target_w, target_h), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(resized)
            try:
                label.configure(image=tk_img, text="")
                label.image = tk_img
            except tk.TclError:
                try:
                    if hasattr(label, "_label") and getattr(label, "_label") is not None:
                        label._label.configure(image=tk_img, text="")
                    label.image = tk_img
                except Exception as e:
                    self._safe_set_label_text(label, f"Error\n{e}")
                    label.image = None
        except Exception as e:
            try:
                self._safe_set_label_text(label, f"Error\n{e}")
            except Exception:
                pass
            label.image = None

    def save_image_from_pil(self, pil_img, default_name="result.png"):
        if pil_img is None:
            messagebox.showerror("No image", "No image available to save.")
            return
        try:
            path = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg;*.jpeg"),
                                                           ("All files", "*.*")],
                                                initialfile=default_name)
            if not path:
                return
            ext = os.path.splitext(path)[1].lower()
            if ext in (".jpg", ".jpeg"):
                pil_img.convert("RGB").save(path, "JPEG")
            else:
                pil_img.save(path)
            messagebox.showinfo("Saved", f"Image saved to {path}")
        except Exception as e:
            messagebox.showerror("Save error", f"Failed to save image: {e}")

    def on_main_resize(self, event):
        if self._resize_after_id:
            try:
                self.after_cancel(self._resize_after_id)
            except Exception:
                pass
        self._resize_after_id = self.after(150, self._refresh_all_images)

    def _refresh_all_images(self):
        try:
            if hasattr(self, "xor_pil1") and self.xor_pil1:
                self.show_pil_image_on_label(self.xor_pil1, self.xor_label1, keep_aspect=True)
            if hasattr(self, "xor_pil2") and self.xor_pil2:
                self.show_pil_image_on_label(self.xor_pil2, self.xor_label2, keep_aspect=True)
            if hasattr(self, "xor_result_pil") and self.xor_result_pil:
                self.show_pil_image_on_label(self.xor_result_pil, self.xor_result_label, keep_aspect=True)

            if hasattr(self, "lsb_original_pil") and self.lsb_original_pil:
                self.show_pil_image_on_label(self.lsb_original_pil, self.lsb_original_label, keep_aspect=True)
            if hasattr(self, "lsb_result_pil") and self.lsb_result_pil:
                self.show_pil_image_on_label(self.lsb_result_pil, self.lsb_result_label, keep_aspect=True)

            if hasattr(self, "picker_pil_image") and self.picker_pil_image:
                self.draw_picker_grid()

            if hasattr(self, "ela_original_pil") and self.ela_original_pil:
                self.show_pil_image_on_label(self.ela_original_pil, self.ela_original_label, keep_aspect=True)
            if hasattr(self, "ela_result_pil") and self.ela_result_pil:
                self.show_pil_image_on_label(self.ela_result_pil, self.ela_result_label, keep_aspect=True)
        except Exception as e:
            print(f"Error refreshing images on resize: {e}")

    # ---------------- Vigenère helpers and cryptoanalysis ----------------
    def vigenere_process(self, text: str, key: str, mode: str = 'encrypt') -> str:
        result = ""
        key_index = 0
        key = key.upper()
        alphabet = string.ascii_uppercase

        for char in text:
            if char.isalpha():
                char_upper = char.upper()
                text_pos = alphabet.find(char_upper)
                if text_pos == -1:
                    result += char
                    continue
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

    def vigenere_encrypt(self, plaintext: str, key: str) -> str:
        return self.vigenere_process(plaintext, key, mode='encrypt')

    def vigenere_decrypt(self, ciphertext: str, key: str) -> str:
        return self.vigenere_process(ciphertext, key, mode='decrypt')

    def _only_letters_upper(self, s: str) -> str:
        return "".join([c for c in s.upper() if c in string.ascii_uppercase])

    def _index_of_coincidence(self, s: str) -> float:
        s = self._only_letters_upper(s)
        N = len(s)
        if N <= 1:
            return 0.0
        counts = Counter(s)
        num = sum(f * (f - 1) for f in counts.values())
        den = N * (N - 1)
        return num / den if den else 0.0

    def _friedman_estimate_keylen(self, s: str) -> int:
        s = self._only_letters_upper(s)
        N = len(s)
        if N < 2:
            return 1
        IC = self._index_of_coincidence(s)
        IC_random = 1.0 / 26.0
        IC_english = 0.065
        try:
            k = ((IC_english - IC_random) * N) / (((N - 1) * IC) - IC_random * N + IC_english)
            k = int(round(max(1.0, k)))
        except ZeroDivisionError:
            k = 1
        return max(1, min(k, 60))

    def _kasiski_candidates(self, s: str, min_len=3, max_len=5, max_key_len=30):
        s = self._only_letters_upper(s)
        distances = []
        for size in range(min_len, max_len + 1):
            seen = {}
            for i in range(0, len(s) - size + 1):
                chunk = s[i:i + size]
                if chunk in seen:
                    prev = seen[chunk]
                    distances.append(i - prev)
                seen[chunk] = i
        if not distances:
            return []

        factor_counts = Counter()
        for d in distances:
            for f in range(2, max_key_len + 1):
                if d % f == 0:
                    factor_counts[f] += 1
        return [k for k, _ in factor_counts.most_common()]

    def _english_frequencies(self):
        return [
            0.08167, 0.01492, 0.02782, 0.04253, 0.12702, 0.02228, 0.02015, 0.06094, 0.06966, 0.00153,
            0.00772, 0.04025, 0.02406, 0.06749, 0.07507, 0.01929, 0.00095, 0.05987, 0.06327, 0.09056,
            0.02758, 0.00978, 0.02360, 0.00150, 0.01974, 0.00074
        ]

    def _chi_squared_for_shift(self, column_text: str, shift: int) -> float:
        alphabet = string.ascii_uppercase
        N = len(column_text)
        if N == 0:
            return float('inf')
        decrypted = [((ord(c) - 65 - shift) % 26) for c in column_text]
        counts = [0] * 26
        for idx in decrypted:
            counts[idx] += 1
        exp_freq = self._english_frequencies()
        chi2 = 0.0
        for i in range(26):
            expected = exp_freq[i] * N
            if expected > 0:
                chi2 += ((counts[i] - expected) ** 2) / expected
        return chi2

    def _best_key_for_length(self, s: str, k: int) -> Tuple[str, float]:
        s_only = self._only_letters_upper(s)
        columns = ['' for _ in range(k)]
        for i, c in enumerate(s_only):
            columns[i % k] += c
        key_chars = []
        score_sum = 0.0
        for col in columns:
            best_shift = 0
            best_score = float('inf')
            for shift in range(26):
                chi2 = self._chi_squared_for_shift(col, shift)
                if chi2 < best_score:
                    best_score = chi2
                    best_shift = shift
            score_sum += best_score
            key_chars.append(chr(ord('A') + best_shift))
        return "".join(key_chars), score_sum

    def break_vigenere_no_key(self, ciphertext: str, max_key_len=20) -> Tuple[str, int, str]:
        fried_k = self._friedman_estimate_keylen(ciphertext)
        kasiski = self._kasiski_candidates(ciphertext, max_key_len=min(max_key_len, 30))

        candidates = []
        if fried_k >= 1:
            candidates.extend([fried_k - 1, fried_k, fried_k + 1, fried_k + 2])
        candidates.extend(kasiski[:8])
        candidates.extend(range(1, min(6, max_key_len + 1)))
        candidates = [k for k in dict.fromkeys(candidates) if 1 <= k <= max_key_len]

        best_key = "A"
        best_len = 1
        best_score = float('inf')

        for k in candidates:
            key_guess, score = self._best_key_for_length(ciphertext, k)
            if score < best_score:
                best_score = score
                best_key = key_guess
                best_len = k

        plaintext = self.vigenere_decrypt(ciphertext, best_key)
        return best_key, best_len, plaintext

    # ====================================================================
    # --- S-DES LOGIC METHODS (NEW) ---
    # ====================================================================

    def _permute(self, original: str, p_table: Tuple[int, ...]) -> str:
        """Виконує перестановку бітів 'original' згідно з 'p_table'."""
        return "".join(original[i - 1] for i in p_table)

    def _left_shift(self, bits: str, n: int) -> str:
        """Виконує циклічний зсув вліво на 'n' біт."""
        return bits[n:] + bits[:n]

    def _get_sbox_val(self, input_4bit: str, s_box: List[List[int]]) -> str:
        """Пошук значення в S-боксі."""
        row = int(input_4bit[0] + input_4bit[3], 2)
        col = int(input_4bit[1] + input_4bit[2], 2)
        val = s_box[row][col]
        return format(val, '02b')

    def _f_k(self, data_4bit: str, subkey: str, log: List[str]) -> str:
        """
        Функція раунду Фейстеля (f_k).
        Приймає 4-бітний вхід (права половина) та 8-бітний підключ.
        """
        log.append(f"    [f_k] Вхід (R): {data_4bit}")

        # Використовуємо self._permute та self._get_sbox_val
        ep_result = self._permute(data_4bit, EP)
        log.append(f"    [f_k] Після E/P: {ep_result}")

        xor_result = format(int(ep_result, 2) ^ int(subkey, 2), '08b')
        log.append(f"    [f_k] XOR з K:  {xor_result} (Ключ: {subkey})")

        left_4 = xor_result[:4]
        right_4 = xor_result[4:]

        s0_result = self._get_sbox_val(left_4, S0)
        log.append(f"    [f_k] S0 вхід: {left_4}, S0 вихід: {s0_result}")
        s1_result = self._get_sbox_val(right_4, S1)
        log.append(f"    [f_k] S1 вхід: {right_4}, S1 вихід: {s1_result}")

        s_combined = s0_result + s1_result

        p4_result = self._permute(s_combined, P4)
        log.append(f"    [f_k] Після P4: {p4_result}")

        return p4_result

    def generate_keys(self, key10: str, log: List[str]) -> Tuple[str, str]:
        """Генерує два 8-бітні підключі (K1, K2) з 10-бітного ключа."""
        log.append("--- Генерація ключів ---")
        log.append(f"Вхідний ключ (10-біт): {key10}")

        p10_result = self._permute(key10, P10)
        log.append(f"Після P10:            {p10_result}")

        ls_left = p10_result[:5]
        ls_right = p10_result[5:]
        log.append(f"Поділ: L={ls_left}, R={ls_right}")

        ls1_left = self._left_shift(ls_left, 1)
        ls1_right = self._left_shift(ls_right, 1)
        log.append(f"Після LS-1: L={ls1_left}, R={ls1_right}")

        k1 = self._permute(ls1_left + ls1_right, P8)
        log.append(f"ПІДКЛЮЧ K1:         {k1}")

        ls2_left = self._left_shift(ls1_left, 2)
        ls2_right = self._left_shift(ls1_right, 2)
        log.append(f"Після LS-2: L={ls2_left}, R={ls2_right}")

        k2 = self._permute(ls2_left + ls2_right, P8)
        log.append(f"ПІДКЛЮЧ K2:         {k2}")
        log.append("-------------------------")

        return k1, k2

    def sdes_process_block(self, block8: str, k1: str, k2: str, log: List[str]) -> str:
        """Виконує шифрування (або дешифрування) одного 8-бітного блоку."""
        log.append(f"Обробка блоку: {block8}")

        ip_result = self._permute(block8, IP)
        log.append(f"Після IP:      {ip_result}")

        l0 = ip_result[:4]
        r0 = ip_result[4:]
        log.append(f"Поділ: L0={l0}, R0={r0}")

        log.append("\n--- Раунд 1 (з K1) ---")
        f_result1 = self._f_k(r0, k1, log)
        l1 = format(int(l0, 2) ^ int(f_result1, 2), '04b')
        r1 = r0
        log.append(f"[Раунд 1] L1 (L0^f_k): {l1}")
        log.append(f"[Раунд 1] R1 (R0):    {r1}")

        log.append("\n--- Раунд 2 (з K2) ---")
        f_result2 = self._f_k(r1, k2, log)
        l2 = format(int(l1, 2) ^ int(f_result2, 2), '04b')
        r2 = r1
        log.append(f"[Раунд 2] L2 (L1^f_k): {l2}")
        log.append(f"[Раунд 2] R2 (R1):    {r2}")

        combined = l2 + r2
        log.append(f"\nРезультат 2-х раундів: {combined}")

        final_result = self._permute(combined, IP_INV)
        log.append(f"Кінцевий результат (після IP-1): {final_result}")

        return final_result

    def sdes_encrypt(self, text: str, key10: str) -> Tuple[bytes, str]:
        """
        Шифрує текстовий рядок 'text' з 10-бітним ключем 'key10'.
        Повертає (ciphertext_bytes, log_string).
        """
        log = ["=== S-DES ШИФРУВАННЯ ==="]
        try:
            if not all(c in '01' for c in key10) or len(key10) != 10:
                return b"", "Помилка: Ключ має бути 10-бітним (0 або 1)."

            k1, k2 = self.generate_keys(key10, log)

            input_bytes = text.encode('utf-8')
            output_bytes = bytearray()

            log.append("\n--- Обробка байтів ---")

            for i, byte in enumerate(input_bytes):
                log.append(f"\n[Байт {i + 1}: {format(byte, '08b')} ('{chr(byte)}')]")
                block8 = format(byte, '08b')
                encrypted_block = self.sdes_process_block(block8, k1, k2, log)
                output_bytes.append(int(encrypted_block, 2))

            log.append("=========================")
            return bytes(output_bytes), "\n".join(log)

        except Exception as e:
            log.append(f"\nКРИТИЧНА ПОМИЛКА: {e}")
            return b"", "\n".join(log)

    def sdes_decrypt(self, cipher_bytes: bytes, key10: str) -> Tuple[str, str]:
        """
        Розшифровує 'cipher_bytes' з 10-бітним ключем 'key10'.
        Повертає (plaintext_string, log_string).
        """
        log = ["=== S-DES ДЕШИФРУВАННЯ ==="]
        try:
            if not all(c in '01' for c in key10) or len(key10) != 10:
                return "", "Помилка: Ключ має бути 10-бітним (0 або 1)."

            k1, k2 = self.generate_keys(key10, log)
            log.append(f"\n*** Використання ключів для дешифрування: K1={k2}, K2={k1} ***")

            output_bytes = bytearray()
            log.append("\n--- Обробка байтів ---")

            for i, byte in enumerate(cipher_bytes):
                log.append(f"\n[Байт {i + 1}: {format(byte, '08b')}]")
                block8 = format(byte, '08b')
                decrypted_block = self.sdes_process_block(block8, k2, k1, log)
                output_bytes.append(int(decrypted_block, 2))

            log.append("=========================")

            plaintext = output_bytes.decode('utf-8', errors='ignore')
            return plaintext, "\n".join(log)

        except Exception as e:
            log.append(f"\nКРИТИЧНА ПОМИЛКА: {e}")
            return "", "\n".join(log)

    def sdes_bruteforce(self, cipherbytes: bytes, known_fragment: Optional[bytes] = None, max_results=100) -> List[
        Tuple[str, str]]:
        """
        Криптоаналіз: перебирає всі 1024 ключі.
        Повертає список [(key_str, plaintext_str)].
        """
        results = []

        for key_int in range(1024):  # 2^10 = 1024
            key10 = format(key_int, '010b')

            try:
                log_dummy = []
                k1_dummy, k2_dummy = self.generate_keys(key10, log_dummy)

                output_bytes = bytearray()
                for byte in cipherbytes:
                    block8 = format(byte, '08b')
                    decrypted_block = self.sdes_process_block(block8, k2_dummy, k1_dummy, log_dummy)
                    output_bytes.append(int(decrypted_block, 2))

                if known_fragment:
                    if known_fragment in output_bytes:
                        plaintext = output_bytes.decode('utf-8', errors='ignore')
                        results.append((key10, plaintext))
                else:
                    plaintext = output_bytes.decode('utf-8', errors='ignore')
                    results.append((key10, plaintext))

                if len(results) >= max_results:
                    break

            except Exception:
                continue

        return results

    # ====================================================================
    # --- END S-DES LOGIC METHODS ---
    # ====================================================================
    def _safe_set_log_text(self, textbox_widget, content: str):
        """Вставляє текст у віджет логу, який вимкнено."""
        try:
            if not textbox_widget or not textbox_widget.winfo_exists():
                return
            textbox_widget.configure(state="normal")
            textbox_widget.delete("1.0", tk.END)
            textbox_widget.insert("1.0", content)
            textbox_widget.configure(state="disabled")
        except Exception as e:
            print(f"Error setting log text: {e}")

    def on_sdes_run(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        mode = self.sdes_mode.get()
        key10 = self.sdes_key_entry.get().strip()
        data_in = self.sdes_input_textbox.get("1.0", tk.END).strip()

        # Очищення полів перед виконанням
        self._safe_set_textbox_text(self.sdes_output_textbox, "")
        self._safe_set_log_text(self.sdes_log_textbox, "")  # Очищуємо лог
        self.sdes_status_label.configure(text="")

        if not key10 or not data_in:
            self.sdes_status_label.configure(text=lang["vigenere_status_error_input"], text_color="red")
            return

        if len(key10) != 10 or not all(c in '01' for c in key10):
            self.sdes_status_label.configure(text=lang["sdes_status_error_key"], text_color="red")
            return

        try:
            if mode == lang["mode_encrypt"]:
                # 1. Шифрування
                # Викликаємо метод self.sdes_encrypt
                ciphertext_bytes, log_str = self.sdes_encrypt(data_in, key10)

                if not ciphertext_bytes and "Помилка" in log_str:
                    self.sdes_status_label.configure(text=log_str, text_color="red")
                    self._safe_set_log_text(self.sdes_log_textbox, log_str)
                    return

                result_b64 = base64.b64encode(ciphertext_bytes).decode('utf-8')
                self._safe_set_textbox_text(self.sdes_output_textbox, result_b64)
                self._safe_set_log_text(self.sdes_log_textbox, log_str)  # Вставляємо лог
                self.sdes_status_label.configure(text=lang["sdes_status_ok"].format(mode.lower()), text_color="green")

            else:
                # 2. Дешифрування
                try:
                    cipher_bytes = base64.b64decode(data_in)
                except Exception:
                    self.sdes_status_label.configure(text=lang["sdes_status_error_b64"], text_color="red")
                    return

                # Викликаємо метод self.sdes_decrypt
                plaintext, log_str = self.sdes_decrypt(cipher_bytes, key10)

                if not plaintext and "Помилка" in log_str:
                    self.sdes_status_label.configure(text=log_str, text_color="red")
                    self._safe_set_log_text(self.sdes_log_textbox, log_str)
                    return

                self._safe_set_textbox_text(self.sdes_output_textbox, plaintext)
                self._safe_set_log_text(self.sdes_log_textbox, log_str)  # Вставляємо лог
                self.sdes_status_label.configure(text=lang["sdes_status_ok"].format(mode.lower()), text_color="green")

        except Exception as e:
            self.sdes_status_label.configure(text=f"Помилка виконання: {e}", text_color="red")
            self._safe_set_log_text(self.sdes_log_textbox, f"Помилка: {e}")

    def on_sdes_brute_run(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        # Вхідні дані (шифртекст) беруться з ОСНОВНОГО поля вводу
        data_b64 = self.sdes_input_textbox.get("1.0", tk.END).strip()
        known_frag_str = self.sdes_known_fragment_entry.get().strip()

        known_frag = known_frag_str.encode('utf-8') if known_frag_str else None

        if not data_b64:
            self.sdes_status_label.configure(text=lang["sdes_brute_ciphertext_label"], text_color="red")
            return

        try:
            cipherbytes = base64.b64decode(data_b64)
        except Exception:
            self.sdes_status_label.configure(text=lang["sdes_status_error_b64"], text_color="red")
            return

        self.sdes_status_label.configure(text=lang["brute_status"], text_color="yellow")
        self.update_idletasks()
        self.sdes_brute_btn.configure(state="disabled")

        def worker():
            start = time.time()
            # ВИКЛИК НОВОГО МЕТОДУ self.sdes_bruteforce
            matches = self.sdes_bruteforce(cipherbytes, known_fragment=known_frag, max_results=100)
            duration = time.time() - start
            self.after(0, self.on_sdes_brute_done, matches, duration)

        # Запускаємо bruteforce у окремому потоці
        threading.Thread(target=worker, daemon=True).start()

    def on_sdes_brute_done(self, matches, duration):
        lang = LANG_STRINGS[self.current_lang.get()]
        self.sdes_brute_btn.configure(state="normal")
        # Ensure key for message formatting exists; fallback if missing
        brute_done_text = lang.get("brute_done", "Brute-force done. Found:")
        try:
            # If brute_done is expected to take a duration, keep original behavior safe
            self.sdes_status_label.configure(text=brute_done_text, text_color="green")
        except Exception:
            self.sdes_status_label.configure(text=brute_done_text, text_color="green")

        if not matches:
            msg = lang.get("dialog_brute_sdes_no_match", "No key found that matched the criteria.")
        else:
            result_text = ""
            for key, text in matches:
                preview = text.replace('\n', ' ').replace('\r', '')[:60]
                result_text += lang.get("dialog_brute_sdes_match", "Key: {0}\nPlaintext: {1}...\n").format(key, preview)

            msg = lang.get("dialog_brute_sdes_msg", "Found {0} possible matches (max 100 shown):\n\n{1}").format(
                len(matches), result_text)

        # Show a simple messagebox with results (original code attempted to instantiate StegoApp incorrectly)
        try:
            messagebox.showinfo("S-DES Brute-force", msg)
        except Exception:
            print(msg)

        # Якщо є збіг, помістимо перший у поля
        if matches:
            best_key, best_text = matches[0]
            try:
                self.sdes_key_entry.delete(0, tk.END)
                self.sdes_key_entry.insert(0, best_key)
                self._safe_set_textbox_text(self.sdes_output_textbox, best_text)
                # set mode to decrypt if possible
                try:
                    self.sdes_mode.set(lang.get("mode_decrypt", "Decrypt"))
                except Exception:
                    pass
            except Exception:
                pass

    def _safe_set_textbox_text(self, textbox_widget, content: str):
        try:
            if not textbox_widget or not textbox_widget.winfo_exists():
                return
            textbox_widget.delete("1.0", tk.END)
            textbox_widget.insert("1.0", content)
        except Exception as e:
            print(f"Error setting textbox text: {e}")


# Entry point
if __name__ == "__main__":
    app = StegoApp()
    app.mainloop()
