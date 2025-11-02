from __future__ import annotations

import base64
import hashlib
import io
import os
import string
import threading
import time
import webbrowser
from collections import Counter
from typing import Tuple

import requests
from PIL import Image, ImageChops, ImageDraw, ImageTk

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox

# Optional AES dependency (PyCryptodome)
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad

    CRYPTO_AVAILABLE = True
except Exception:
    CRYPTO_AVAILABLE = False

APP_VERSION = "1.4.1"
# Fixed raw URL path (removed invalid refs/heads)
APP_LOGO_URL = "https://raw.githubusercontent.com/QmFkLVBp/decryptoinator/main/logo.png"

# -------------------------
# UI Themes and Localization
# -------------------------
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
        "vigenere_status_ok_decrypt": "Розшифровка Віженера завершена.",
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
# AES helpers (uses PyCryptodome if available)
# -------------------------
def aes_derive_key_from_password(password: str) -> bytes:
    h = hashlib.sha256(password.encode('utf-8')).digest()
    return h[:16]


def aes_encrypt_text(plaintext: str, password: str) -> str:
    if not CRYPTO_AVAILABLE:
        raise RuntimeError("Crypto not available")
    key = aes_derive_key_from_password(password)
    cipher = AES.new(key, AES.MODE_CBC)
    ct = cipher.encrypt(pad(plaintext.encode('utf-8'), AES.block_size))
    payload = cipher.iv + ct
    return base64.b64encode(payload).decode('utf-8')


def aes_decrypt_text(b64cipher: str, password: str) -> str:
    if not CRYPTO_AVAILABLE:
        raise RuntimeError("Crypto not available")
    data = base64.b64decode(b64cipher)
    if len(data) < 16:
        raise ValueError("Ciphertext too short")
    iv = data[:16]
    ct = data[16:]
    key = aes_derive_key_from_password(password)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode('utf-8', errors='replace')


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


# -------------------------
# GUI Application
# -------------------------
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

        self.logo_image = None
        self._resize_after_id = None
        self._self_destruct_running = False

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_nav_frame()
        self.setup_content_frames()

        self.update_all_texts(self.current_lang.get())
        self.load_network_logo()
        self.after(50, lambda: self.apply_theme_by_name("Нічна Прохолода"))
        self.show_xor_frame()

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

        self.nav_frame.grid_rowconfigure(9, weight=1)

        self.settings_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_settings_frame,
                                                   anchor="w")
        self.settings_button.grid(row=10, column=0, padx=20, pady=5, sticky="ew")

        self.about_button = self._create_widget(ctk.CTkButton, self.nav_frame, command=self.show_about_frame,
                                                anchor="w")
        self.about_button.grid(row=11, column=0, padx=20, pady=20, sticky="ew")

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
        self.xor_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent"); self.xor_frame.is_themeable = False
        self.lsb_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent"); self.lsb_frame.is_themeable = False
        self.picker_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent"); self.picker_frame.is_themeable = False
        self.vigenere_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent"); self.vigenere_frame.is_themeable = False
        self.base64_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent"); self.base64_frame.is_themeable = False
        self.ela_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent"); self.ela_frame.is_themeable = False

        self.aes_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent"); self.aes_frame.is_themeable = False
        self.sdes_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent"); self.sdes_frame.is_themeable = False

        self.settings_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent"); self.settings_frame.is_themeable = False
        self.about_frame = self._create_widget(ctk.CTkFrame, self, fg_color="transparent"); self.about_frame.is_themeable = False

        self.setup_xor_frame_widgets()
        self.setup_lsb_frame_widgets()
        self.setup_picker_frame_widgets()
        self.setup_vigenere_frame_widgets()
        self.setup_base64_frame_widgets()
        self.setup_ela_frame_widgets()
        self.setup_aes_frame_widgets()
        self.setup_sdes_frame_widgets()
        self.setup_settings_frame_widgets()
        self.setup_about_frame_widgets()

    # --- setup methods for frames ---
    def setup_xor_frame_widgets(self):
        self.xor_frame.grid_columnconfigure((0, 1), weight=1)
        self.xor_title = self._create_widget(ctk.CTkLabel, self.xor_frame, font=ctk.CTkFont(size=24, weight="bold"))
        self.xor_title.grid(row=0, column=0, columnspan=2, pady=20, padx=20)

        self.xor_label1 = self._create_widget(ctk.CTkLabel, self.xor_frame, width=400, height=400, fg_color="gray20",
                                              corner_radius=10, text=""); self.xor_label1.is_themeable = False
        self.xor_label1.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.xor_load_btn1 = self._create_widget(ctk.CTkButton, self.xor_frame, command=self.load_xor_image1)
        self.xor_load_btn1.grid(row=2, column=0, padx=20, pady=10)

        self.xor_label2 = self._create_widget(ctk.CTkLabel, self.xor_frame, width=400, height=400, fg_color="gray20",
                                              corner_radius=10, text=""); self.xor_label2.is_themeable = False
        self.xor_label2.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        self.xor_load_btn2 = self._create_widget(ctk.CTkButton, self.xor_frame, command=self.load_xor_image2)
        self.xor_load_btn2.grid(row=2, column=1, padx=20, pady=10)

        self.xor_run_btn = self._create_widget(ctk.CTkButton, self.xor_frame, command=self.perform_xor,
                                               font=ctk.CTkFont(size=16, weight="bold"))
        self.xor_run_btn.grid(row=3, column=0, columnspan=2, pady=20)

        self.xor_result_label = self._create_widget(ctk.CTkLabel, self.xor_frame, width=800, height=400,
                                                    fg_color="gray25", corner_radius=10, text=""); self.xor_result_label.is_themeable = False
        self.xor_result_label.grid(row=4, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")

        self.xor_save_btn = self._create_widget(ctk.CTkButton, self.xor_frame, text="Save XOR Result",
                                               command=lambda: self.save_image_from_pil(self.xor_result_pil, "xor_result.png"))
        self.xor_save_btn.grid(row=5, column=0, columnspan=2, pady=(0, 10))

        self.xor_status_label = self._create_widget(ctk.CTkLabel, self.xor_frame, text="", text_color="yellow"); self.xor_status_label.is_themeable = False
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

        img_frame = self._create_widget(ctk.CTkFrame, self.lsb_frame, fg_color="transparent"); img_frame.is_themeable = False
        img_frame.grid(row=2, column=0, pady=10, padx=20, sticky="ew")
        img_frame.grid_columnconfigure((0, 1), weight=1)

        self.lsb_original_label = self._create_widget(ctk.CTkLabel, img_frame, width=450, height=350, fg_color="gray20",
                                                      corner_radius=10, text=""); self.lsb_original_label.is_themeable = False
        self.lsb_original_label.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")

        self.lsb_result_label = self._create_widget(ctk.CTkLabel, img_frame, width=450, height=350, fg_color="gray25",
                                                    corner_radius=10, text=""); self.lsb_result_label.is_themeable = False
        self.lsb_result_label.grid(row=0, column=1, pady=10, padx=10, sticky="nsew")

        self.lsb_save_btn = self._create_widget(ctk.CTkButton, self.lsb_frame, text="Save LSB Result",
                                               command=lambda: self.save_image_from_pil(self.lsb_result_pil, "lsb_result.png"))
        self.lsb_save_btn.grid(row=3, column=0, pady=(0, 10))

        self.lsb_decoded_text_label = self._create_widget(ctk.CTkLabel, self.lsb_frame, font=ctk.CTkFont(size=16))
        self.lsb_decoded_text_label.grid(row=4, column=0, pady=(10, 0), sticky="s")

        self.lsb_text_result = self._create_widget(ctk.CTkTextbox, self.lsb_frame, height=100, font=("Consolas", 14))
        self.lsb_text_result.grid(row=5, column=0, pady=10, padx=20, sticky="nsew")

        self.lsb_status_label = self._create_widget(ctk.CTkLabel, self.lsb_frame, text="", text_color="yellow"); self.lsb_status_label.is_themeable = False
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
                                                      corner_radius=10, text=""); self.picker_image_label.is_themeable = False
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

        self.picker_status_label = self._create_widget(ctk.CTkLabel, self.picker_frame, text_color="gray"); self.picker_status_label.is_themeable = False
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
                                                         text_color="yellow"); self.vigenere_status_label.is_themeable = False
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

        self.base64_status_label = self._create_widget(ctk.CTkLabel, self.base64_frame, text="", text_color="yellow"); self.base64_status_label.is_themeable = False
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

        self.ela_quality_slider = self._create_widget(ctk.CTkSlider, controls_frame, from_=1, to=100, number_of_steps=99,
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

        img_frame = self._create_widget(ctk.CTkFrame, self.ela_frame, fg_color="transparent"); img_frame.is_themeable = False
        img_frame.grid(row=2, column=0, pady=10, padx=20, sticky="ew")
        img_frame.grid_columnconfigure((0, 1), weight=1)

        self.ela_original_label = self._create_widget(ctk.CTkLabel, img_frame, width=450, height=350, fg_color="gray20",
                                                      corner_radius=10, text=""); self.ela_original_label.is_themeable = False
        self.ela_original_label.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")

        self.ela_result_label = self._create_widget(ctk.CTkLabel, img_frame, width=450, height=350, fg_color="gray25",
                                                    corner_radius=10, text=""); self.ela_result_label.is_themeable = False
        self.ela_result_label.grid(row=0, column=1, pady=10, padx=10, sticky="nsew")

        self.ela_save_btn = self._create_widget(ctk.CTkButton, self.ela_frame, text="Save ELA Result",
                                               command=lambda: self.save_image_from_pil(self.ela_result_pil, "ela_result.png"))
        self.ela_save_btn.grid(row=3, column=0, pady=(0, 10))

        self.ela_status_label = self._create_widget(ctk.CTkLabel, self.ela_frame, text="", text_color="yellow"); self.ela_status_label.is_themeable = False
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
                                                     command=self.self_destruct); self.self_destruct_btn.is_themeable = False
        self.self_destruct_btn.grid(row=10, column=0, pady=10, padx=50, sticky="ew")

        self.self_destruct_progress = self._create_widget(ctk.CTkProgressBar, self.settings_frame, fg_color="gray20",
                                                          progress_color="red"); self.self_destruct_progress.is_themeable = False
        self.self_destruct_progress.set(0)
        self.self_destruct_progress.grid(row=11, column=0, padx=50, pady=(0, 20), sticky="ew")

    def setup_about_frame_widgets(self):
        self.about_frame.grid_columnconfigure(0, weight=1)
        self.about_frame.grid_rowconfigure(0, weight=0)
        self.about_frame.grid_rowconfigure(1, weight=1)
        self.about_frame.grid_rowconfigure(2, weight=1)

        self.about_title = self._create_widget(ctk.CTkLabel, self.about_frame, font=ctk.CTkFont(size=24, weight="bold"))
        self.about_title.grid(row=0, column=0, pady=20, padx=20)

        center_frame = self._create_widget(ctk.CTkFrame, self.about_frame, fg_color="transparent"); center_frame.is_themeable = False
        center_frame.grid(row=1, column=0, sticky="nsew", pady=20)
        center_frame.grid_columnconfigure(0, weight=1)

        self.about_text_label = self._create_widget(ctk.CTkLabel, center_frame, justify=tk.CENTER,
                                                    font=ctk.CTkFont(size=16))
        self.about_text_label.grid(row=0, column=0, padx=20, pady=20)

        self.about_links_label = self._create_widget(ctk.CTkLabel, center_frame,
                                                     font=ctk.CTkFont(size=16, weight="bold"))
        self.about_links_label.grid(row=1, column=0, padx=20, pady=(20, 5))

        links_frame = self._create_widget(ctk.CTkFrame, center_frame, fg_color="transparent"); links_frame.is_themeable = False
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
                    internal_theme_key = "theme_" + en_name.lower().replace(" ", "_").replace("і", "i").replace("ї", "i")
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
        lang = LANG_STRINGS[self.current_lang.get()]
        if hasattr(self, "sdes_title"):
            self.sdes_title.configure(text=lang["sdes_title"])
        if hasattr(self, "sdes_mode_selector"):
            vals = [lang["mode_encrypt"], lang["mode_decrypt"]]
            cur = self.sdes_mode.get()
            self.sdes_mode_selector.configure(values=vals)
            if cur not in vals:
                self.sdes_mode.set(vals[0])
        if hasattr(self, "sdes_input_label"):
            self.sdes_input_label.configure(text=lang["input_label"])
        if hasattr(self, "sdes_brute_label"):
            self.sdes_brute_label.configure(text=lang["sdes_bruteforce_label"])
        if hasattr(self, "sdes_run_btn"):
            self.sdes_run_btn.configure(text=lang["run"])
        if hasattr(self, "sdes_brute_btn"):
            self.sdes_brute_btn.configure(text=lang["sdes_bruteforce_run"])
        if hasattr(self, "sdes_output_label"):
            self.sdes_output_label.configure(text=lang["output_label"])

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

    # ---------- AES and S-DES UI setup ----------
    def setup_aes_frame_widgets(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        self.aes_frame.grid_columnconfigure(0, weight=1)
        self.aes_title = self._create_widget(ctk.CTkLabel, self.aes_frame, font=ctk.CTkFont(size=20, weight="bold"))
        self.aes_title.grid(row=0, column=0, pady=10, padx=20)
        self.aes_mode = ctk.StringVar(value=lang["mode_encrypt"])
        self.aes_mode_selector = self._create_widget(ctk.CTkSegmentedButton, self.aes_frame,
                                                     values=[lang["mode_encrypt"], lang["mode_decrypt"]],
                                                     variable=self.aes_mode)
        self.aes_mode_selector.grid(row=1, column=0, padx=20, pady=5)

        self.aes_input_label = self._create_widget(ctk.CTkLabel, self.aes_frame, text=lang["input_label"])
        self.aes_input_label.grid(row=2, column=0, sticky="w", padx=20)
        self.aes_input_textbox = self._create_widget(ctk.CTkTextbox, self.aes_frame, height=120)
        self.aes_input_textbox.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")

        key_frame = self._create_widget(ctk.CTkFrame, self.aes_frame)
        key_frame.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        self.aes_key_label = self._create_widget(ctk.CTkLabel, key_frame, text=lang["key_label"])
        self.aes_key_label.grid(row=0, column=0, padx=(0, 10))
        self.aes_key_entry = self._create_widget(ctk.CTkEntry, key_frame, width=240)
        self.aes_key_entry.grid(row=0, column=1, padx=(0, 10))
        self.aes_pin_maxlen_label = self._create_widget(ctk.CTkLabel, key_frame, text=lang["aes_bruteforce_label"])
        self.aes_pin_maxlen_label.grid(row=1, column=0, padx=(0, 10), pady=(6, 0))
        self.aes_pin_maxlen_entry = self._create_widget(ctk.CTkEntry, key_frame, width=80)
        self.aes_pin_maxlen_entry.grid(row=1, column=1, padx=(0, 10), pady=(6, 0), sticky="w")
        self.aes_pin_maxlen_entry.insert(0, "4")

        controls = self._create_widget(ctk.CTkFrame, self.aes_frame)
        controls.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        self.aes_run_btn = self._create_widget(ctk.CTkButton, controls, text=lang["run"], command=self.perform_aes_operation)
        self.aes_run_btn.grid(row=0, column=0, padx=5)
        self.aes_brute_btn = self._create_widget(ctk.CTkButton, controls, text=lang["aes_bruteforce_run"], command=self.perform_aes_bruteforce)
        self.aes_brute_btn.grid(row=0, column=1, padx=5)

        self.aes_output_label = self._create_widget(ctk.CTkLabel, self.aes_frame, text=lang["output_label"])
        self.aes_output_label.grid(row=6, column=0, sticky="w", padx=20)
        self.aes_output_textbox = self._create_widget(ctk.CTkTextbox, self.aes_frame, height=150)
        self.aes_output_textbox.grid(row=7, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.aes_status_label = self._create_widget(ctk.CTkLabel, self.aes_frame, text="", text_color="yellow"); self.aes_status_label.is_themeable = False
        self.aes_status_label.grid(row=8, column=0, padx=20, pady=(0, 10), sticky="w")

    def setup_sdes_frame_widgets(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        self.sdes_frame.grid_columnconfigure(0, weight=1)
        self.sdes_title = self._create_widget(ctk.CTkLabel, self.sdes_frame, font=ctk.CTkFont(size=20, weight="bold"))
        self.sdes_title.grid(row=0, column=0, pady=10, padx=20)

        self.sdes_mode = ctk.StringVar(value=lang["mode_encrypt"])
        self.sdes_mode_selector = self._create_widget(ctk.CTkSegmentedButton, self.sdes_frame,
                                                      values=[lang["mode_encrypt"], lang["mode_decrypt"]],
                                                      variable=self.sdes_mode)
        self.sdes_mode_selector.grid(row=1, column=0, padx=20, pady=5)

        self.sdes_input_label = self._create_widget(ctk.CTkLabel, self.sdes_frame, text=lang["input_label"])
        self.sdes_input_label.grid(row=2, column=0, sticky="w", padx=20)
        self.sdes_input_textbox = self._create_widget(ctk.CTkTextbox, self.sdes_frame, height=120)
        self.sdes_input_textbox.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")

        key_frame = self._create_widget(ctk.CTkFrame, self.sdes_frame)
        key_frame.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        self.sdes_key_label = self._create_widget(ctk.CTkLabel, key_frame, text="10-bit key (0..1023):")
        self.sdes_key_label.grid(row=0, column=0, padx=(0, 10))
        self.sdes_key_entry = self._create_widget(ctk.CTkEntry, key_frame, width=120)
        self.sdes_key_entry.grid(row=0, column=1, padx=(0, 10))
        self.sdes_key_entry.insert(0, "0")

        self.sdes_known_fragment_entry = self._create_widget(ctk.CTkEntry, key_frame, width=200)
        self.sdes_known_fragment_entry.grid(row=1, column=1, padx=(0, 10), pady=(6, 0))
        self.sdes_known_fragment_entry.insert(0, "")

        self.sdes_brute_label = self._create_widget(ctk.CTkLabel, key_frame, text=lang["sdes_bruteforce_label"])
        self.sdes_brute_label.grid(row=1, column=0, padx=(0, 10), pady=(6, 0))

        controls = self._create_widget(ctk.CTkFrame, self.sdes_frame)
        controls.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        self.sdes_run_btn = self._create_widget(ctk.CTkButton, controls, text=lang["run"], command=self.perform_sdes_operation)
        self.sdes_run_btn.grid(row=0, column=0, padx=5)
        self.sdes_brute_btn = self._create_widget(ctk.CTkButton, controls, text=lang["sdes_bruteforce_run"], command=self.perform_sdes_bruteforce)
        self.sdes_brute_btn.grid(row=0, column=1, padx=5)

        self.sdes_output_label = self._create_widget(ctk.CTkLabel, self.sdes_frame, text=lang["output_label"])
        self.sdes_output_label.grid(row=6, column=0, sticky="w", padx=20)
        self.sdes_output_textbox = self._create_widget(ctk.CTkTextbox, self.sdes_frame, height=150)
        self.sdes_output_textbox.grid(row=7, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.sdes_status_label = self._create_widget(ctk.CTkLabel, self.sdes_frame, text="", text_color="yellow"); self.sdes_status_label.is_themeable = False
        self.sdes_status_label.grid(row=8, column=0, padx=20, pady=(0, 10), sticky="w")

    # --- show/hide frames ---
    def hide_all_frames(self):
        for f in [self.xor_frame, self.lsb_frame, self.picker_frame, self.vigenere_frame, self.base64_frame, self.ela_frame,
                  self.aes_frame, self.sdes_frame, self.settings_frame, self.about_frame]:
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
    def perform_aes_operation(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        mode = self.aes_mode.get()
        data = self.aes_input_textbox.get("1.0", tk.END).strip()
        key = self.aes_key_entry.get().strip()

        self.aes_output_textbox.delete("1.0", tk.END)
        if not CRYPTO_AVAILABLE:
            self.aes_status_label.configure(text=lang["crypto_error_crypto_missing"], text_color="red")
            return

        try:
            if mode == lang["mode_encrypt"]:
                ct_b64 = aes_encrypt_text(data, key)
                self.aes_output_textbox.insert("1.0", ct_b64)
            else:
                try:
                    pt = aes_decrypt_text(data, key)
                    self.aes_output_textbox.insert("1.0", pt)
                except Exception as e:
                    self.aes_output_textbox.insert("1.0", f"Decrypt error: {e}")
            self.aes_status_label.configure(text="OK", text_color="green")
        except Exception as e:
            self.aes_status_label.configure(text=f"Error: {e}", text_color="red")

    def perform_aes_bruteforce(self):
        lang = LANG_STRINGS[self.current_lang.get()]
        cipher_b64 = self.aes_input_textbox.get("1.0", tk.END).strip()
        maxlen_s = self.aes_pin_maxlen_entry.get().strip()
        known_fragment_s = self.aes_output_textbox.get("1.0", tk.END).strip()
        try:
            maxlen = int(maxlen_s)
            if maxlen < 1: maxlen = 1
            if maxlen > 6: maxlen = 6
        except Exception:
            maxlen = 4
        known_fragment = known_fragment_s.encode('utf-8') if known_fragment_s else None

        if not cipher_b64:
            self.aes_status_label.configure(text="Provide AES base64 ciphertext in input box", text_color="red")
            return
        if not CRYPTO_AVAILABLE:
            self.aes_status_label.configure(text=lang["crypto_error_crypto_missing"], text_color="red")
            return

        self.aes_status_label.configure(text=lang["brute_status"], text_color="yellow")
        self.update_idletasks()

        def worker():
            try:
                start = time.time()
                matches = aes_bruteforce_pin(cipher_b64, known_fragment=known_fragment, max_pin_length=maxlen)
                duration = time.time() - start
                self.after(0, self._aes_brute_done_callback, matches, duration)
            except Exception as e:
                self.after(0, lambda: self.aes_status_label.configure(text=f"Error: {e}", text_color="red"))

        threading.Thread(target=worker, daemon=True).start()

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
        known_frag = self.sdes_known_fragment_entry.get().strip().encode('utf-8') if self.sdes_known_fragment_entry.get().strip() else None
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
                                                filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg;*.jpeg"), ("All files", "*.*")],
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


# Entry point
if __name__ == "__main__":
    app = StegoApp()
    app.mainloop()

