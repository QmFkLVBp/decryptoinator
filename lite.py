#!/usr/bin/env python3
# DECRYPTOINATOR Lite — compact, optimized version (append_log fix)
# Fix: add missing _append_log method to LiteApp to avoid AttributeError from tkinter.
# Functionality: RSA, Vigenère (ROT, table), Polybius, Cipser, Settings, About.

from __future__ import annotations
import tkinter as tk
from tkinter import messagebox
import string

try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
except Exception:
    CTK_AVAILABLE = False

try:
    import urllib.request
    LOGO_SUPPORT = True
except Exception:
    LOGO_SUPPORT = False

APP_VERSION = "Lite-1.7.2-compact"

# Alphabets
EN_UP, EN_LO = string.ascii_uppercase, string.ascii_lowercase
UA_UP = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"  # 33
UA_LO = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"

# Themes
THEMES = {
    "Нічна Прохолода": {"app_bg": "#0F2027", "frame_bg": "#203A43"},
    "Світанок": {"app_bg": "#FFF0F5", "frame_bg": "#E6E6FA"},
}

# Language
LANG = {
    "ua": {
        "title": "ДЕКРИПТОІНАТОР LITE",
        "nav": ["RSA", "Полібій", "Віженер", "Cipser", "Налаштування", "Про автора"],
        "log_title": "Логи:",
        "rsa_title": "RSA — Завдання 4",
        "rsa_desc": "Відомі: d або e, p, q. Обчислити N, φ(N), e, Ek, Dk. Шифрувати M, Дешифрувати C.",
        "rsa_labels": {"d": "d (приватний, optional):", "e": "e (публічний, optional):", "p": "p:", "q": "q:", "M": "M:", "C": "C:"},
        "rsa_actions": {"compute": "Обчислити", "enc": "Зашифрувати M → C", "dec": "Розшифрувати C → M"},
        "rsa_params": "Параметри (N, φ(N), e, Ek, Dk):",
        "poly_title": "Квадрат Полібія", "poly_alpha": "Алфавіт (EN/UA):", "poly_in": "Вхідний текст:", "poly_out": "Результат:", "poly_enc": "Зашифрувати", "poly_dec": "Розшифрувати",
        "vig_title": "Шифр Віженера", "vig_alpha": "Алфавіт:", "vig_in": "Вхідний текст:", "vig_key": "Ключ:", "vig_rot": "ROT (зсув):", "vig_enc": "ЗАШИФРУВАТИ", "vig_dec": "РОЗШИФРУВАТИ",
        "vig_tbl_gen": "Згенерувати таблицю", "vig_tbl_copy": "Копіювати таблицю", "vig_tbl_label": "Таблиця (оригінал | ключ | результат):",
        "cip_title": "Cipser (Цезар)", "cip_in": "Вхідний текст:", "cip_alpha": "Алфавіт:", "cip_shift": "Зсув (ціле):", "cip_enc": "Зашифрувати", "cip_dec": "Розшифрувати",
        "about_title": "Про автора", "about_text": f"Автори: Крилевич Мирослав та Кондратюк Віталій\nГрупа: УБД-32\nВерсія: {APP_VERSION}", "about_links": "Посилання: GitHub/QmFkLVBp",
    },
    "en": {
        "title": "DECRYPTOINATOR LITE",
        "nav": ["RSA", "Polybius", "Vigenère", "Cipser", "Settings", "About"],
        "log_title": "Logs:",
        "rsa_title": "RSA — Task 4",
        "rsa_desc": "Known: d or e, p, q. Compute N, φ(N), e, Ek, Dk. Encrypt M, Decrypt C.",
        "rsa_labels": {"d": "d (private, optional):", "e": "e (public, optional):", "p": "p:", "q": "q:", "M": "M:", "C": "C:"},
        "rsa_actions": {"compute": "Compute", "enc": "Encrypt M → C", "dec": "Decrypt C → M"},
        "rsa_params": "Parameters (N, φ(N), e, Ek, Dk):",
        "poly_title": "Polybius Square", "poly_alpha": "Alphabet (EN/UA):", "poly_in": "Input text:", "poly_out": "Output:", "poly_enc": "Encrypt", "poly_dec": "Decrypt",
        "vig_title": "Vigenère", "vig_alpha": "Alphabet:", "vig_in": "Input text:", "vig_key": "Key:", "vig_rot": "ROT (shift):", "vig_enc": "ENCRYPT", "vig_dec": "DECRYPT",
        "vig_tbl_gen": "Generate table", "vig_tbl_copy": "Copy table", "vig_tbl_label": "Table (orig | key | result):",
        "cip_title": "Cipser (Caesar)", "cip_in": "Input text:", "cip_alpha": "Alphabet:", "cip_shift": "Shift (int):", "cip_enc": "Encrypt", "cip_dec": "Decrypt",
        "about_title": "About", "about_text": f"Author: Krylevych Myroslav & Kondratyk Vitaliy\nGroup: UBD-32\nVersion: {APP_VERSION}", "about_links": "Links: GitHub/QmFkLVBp",
    }
}

# ---------- Math ----------
def egcd(a: int, b: int):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def modinv(a: int, m: int) -> int:
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("No modular inverse (gcd != 1)")
    return x % m

# ---------- Crypto helpers ----------
def rotate_alphabet(alpha: str, rot: int) -> str:
    if not alpha: return alpha
    rot %= len(alpha)
    return alpha[rot:] + alpha[:rot]

def vigenere(text: str, key: str, encrypt: bool, up: str) -> str:
    if not key: raise ValueError("Key required")
    key = key.upper()
    if any(ch not in up for ch in key): raise ValueError("Key contains invalid characters")
    out, ki, n = [], 0, len(up)
    for ch in text:
        cu = ch.upper()
        if cu in up:
            tp, kp = up.index(cu), up.index(key[ki % len(key)])
            rp = (tp + kp) % n if encrypt else (tp - kp) % n
            rc = up[rp]
            out.append(rc if ch.isupper() else rc.lower())
            ki += 1
        else:
            out.append(ch)
    return "".join(out)

def vigenere_table(text: str, key: str, up: str) -> str:
    if not key: raise ValueError("Key required")
    key_up = key.upper()
    if any(ch not in up for ch in key_up): raise ValueError("Key contains invalid characters")
    n = len(up)
    ks, ct, ki = [], [], 0
    for ch in text:
        cu = ch.upper()
        if cu in up:
            kch = key_up[ki % len(key_up)]
            enc_pos = (up.index(cu) + up.index(kch)) % n
            enc_ch = up[enc_pos]
            ks.append(kch if ch.isupper() else kch.lower())
            ct.append(enc_ch if ch.isupper() else enc_ch.lower())
            ki += 1
        else:
            ks.append("-"); ct.append(ch)
    orig, kstream, cipher = text, "".join(ks), "".join(ct)
    header = f"{'Idx':>4} {'Orig':^6} {'Key':^6} {'Enc':^6}"
    lines = [header, "-" * len(header)]
    for i, (o, k, c) in enumerate(zip(orig, kstream, cipher), start=1):
        lines.append(f"{i:4} {o.replace('\t','\\t').replace('\n','\\n'):^6} {k:^6} {c.replace('\t','\\t').replace('\n','\\n'):^6}")
    return "\n".join([f"Original: {orig}", f"Keystream: {kstream}", f"Encrypted: {cipher}", "", *lines])

def caesar(text: str, shift: int, up: str, lo: str) -> str:
    n, s = len(up), (shift % len(up))
    out = []
    for ch in text:
        if ch in up:
            out.append(up[(up.index(ch) + s) % n])
        elif ch in lo:
            out.append(lo[(lo.index(ch) + s) % n])
        else:
            out.append(ch)
    return "".join(out)

# ---------- UI ----------
class UI:
    def __init__(self, app):
        self.app = app
        self.lang = LANG[app.current_lang.get()]
        self.theme = THEMES[app.current_theme_name.get()]

    def frame(self, parent=None, width=None, transparent=False):
        parent = parent or self.app
        if CTK_AVAILABLE:
            return ctk.CTkFrame(parent, width=width or 0, fg_color=("transparent" if transparent else self.theme["frame_bg"]))
        return tk.Frame(parent, bg=self.theme["frame_bg"])

    def label(self, parent, text, size=14, bold=False):
        if CTK_AVAILABLE:
            return ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=size, weight="bold" if bold else "normal"))
        return tk.Label(parent, text=text)

    def button(self, parent, text, cmd):
        return ctk.CTkButton(parent, text=text, command=cmd) if CTK_AVAILABLE else tk.Button(parent, text=text, command=cmd)

    def entry(self, parent, width=240):
        return ctk.CTkEntry(parent, width=width) if CTK_AVAILABLE else tk.Entry(parent, width=max(10, int(width / 8)))

    def textbox(self, parent, height=140):
        return ctk.CTkTextbox(parent, height=height) if CTK_AVAILABLE else tk.Text(parent, height=max(6, int(height / 18)))

    def optmenu(self, parent, variable, values):
        return ctk.CTkOptionMenu(parent, values=values, variable=variable) if CTK_AVAILABLE else tk.OptionMenu(parent, variable, *values)

# ---------- App ----------
class LiteApp(ctk.CTk if CTK_AVAILABLE else tk.Tk):
    def __init__(self):
        super().__init__()
        self.current_lang = tk.StringVar(self, value="ua")
        self.current_theme_name = tk.StringVar(self, value="Нічна Прохолода")
        self.ui = UI(self)

        self.title(self.ui.lang["title"])
        self.geometry("1120x800")
        if CTK_AVAILABLE: ctk.set_appearance_mode("dark")

        # Layout
        self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        self.nav = self.ui.frame(width=260); self.nav.grid(row=0, column=0, sticky="nswe")
        for i in (self.nav,): self._set_bg(self.nav, THEMES[self.current_theme_name.get()]["app_bg"])

        # Pages
        self.pages = {name: self.ui.frame() for name in ("rsa","poly","vig","cip","settings","about")}
        for p in self.pages.values(): p.grid(row=0, column=1, sticky="nswe", padx=12, pady=12); p.grid_remove()

        # Build
        self.build_nav()
        self.build_rsa()
        self.build_poly()
        self.build_vig()
        self.build_cip()
        self.build_settings()
        self.build_about()

        # Apply theme/lang
        self.current_lang.trace_add("write", lambda *_: self.on_lang_change())
        self.current_theme_name.trace_add("write", lambda *_: self.apply_theme())
        self.apply_theme()
        self.show("rsa")

        # RSA state
        self.rsa_state = None

    # ----- helpers -----
    def _set_bg(self, widget, color):
        try:
            if CTK_AVAILABLE: self.configure(fg_color=color); widget.configure(fg_color=color)
            else: self.configure(bg=color); widget.configure(bg=color)
        except Exception: pass

    def show(self, key):
        for f in self.pages.values(): f.grid_remove()
        self.pages[key].grid()

    def apply_theme(self):
        theme = THEMES[self.current_theme_name.get()]
        self._set_bg(self, theme["app_bg"])
        self._set_bg(self.nav, theme["app_bg"])
        for f in self.pages.values(): self._set_bg(f, theme["frame_bg"])

    def on_lang_change(self):
        self.ui.lang = LANG[self.current_lang.get()]
        self.title(self.ui.lang["title"])
        for child in list(self.nav.children.values()): child.destroy()
        self.build_nav()

    # ----- nav -----
    def build_nav(self):
        names = self.ui.lang["nav"]

        # Logo
        logo_holder = self.ui.frame(self.nav, transparent=True)
        logo_holder.grid(row=0, column=0, sticky="ew", padx=12, pady=(12,6))
        self.load_logo(logo_holder)

        # Top buttons (RSA, Polybius, Vigenère, Cipser)
        top = self.ui.frame(self.nav, transparent=True)
        top.grid(row=1, column=0, sticky="ew", padx=12, pady=6)
        top_mapping = [
            (names[0], lambda: self.show("rsa")),
            (names[1], lambda: self.show("poly")),
            (names[2], lambda: self.show("vig")),
            (names[3], lambda: self.show("cip")),
        ]
        for i, (label, cmd) in enumerate(top_mapping):
            self.ui.button(top, label, cmd).grid(row=i, column=0, sticky="ew", pady=6)

        # Bottom buttons (Settings, About)
        bottom = self.ui.frame(self.nav, transparent=True)
        bottom.grid(row=3, column=0, sticky="ew", padx=12, pady=6)
        bottom_mapping = [
            (names[4], lambda: self.show("settings")),
            (names[5], lambda: self.show("about")),
        ]
        for i, (label, cmd) in enumerate(bottom_mapping):
            self.ui.button(bottom, label, cmd).grid(row=i, column=0, sticky="ew", pady=6)

    def load_logo(self, parent):
        if not LOGO_SUPPORT:
            self.ui.label(parent, "DECRYPTOINATOR", size=16, bold=True).grid(row=0, column=0, sticky="ew"); return
        url = "https://raw.githubusercontent.com/QmFkLVBp/decryptoinator/main/assets/logo.png"
        try:
            with urllib.request.urlopen(url, timeout=4) as r: r.read()
            self.ui.label(parent, "DECRYPTOINATOR", size=16, bold=True).grid(row=0, column=0, sticky="ew")
        except Exception:
            self.ui.label(parent, "DECRYPTOINATOR", size=16, bold=True).grid(row=0, column=0, sticky="ew")

    # ----- RSA -----
    def build_rsa(self):
        f, L = self.pages["rsa"], self.ui.lang
        self.ui.label(f, L["rsa_title"], size=18, bold=True).grid(row=0, column=0, sticky="w", padx=8, pady=(8,4))
        self.ui.label(f, L["rsa_desc"], size=12).grid(row=1, column=0, sticky="w", padx=8, pady=(0,10))
        row = 2
        self.rsa_d = self.entry_row(f, row, L["rsa_labels"]["d"]); row += 1
        self.rsa_e = self.entry_row(f, row, L["rsa_labels"]["e"]); row += 1
        self.rsa_p = self.entry_row(f, row, L["rsa_labels"]["p"]); row += 1
        self.rsa_q = self.entry_row(f, row, L["rsa_labels"]["q"]); row += 1
        self.rsa_M = self.entry_row(f, row, L["rsa_labels"]["M"], preset="2897878135"); row += 1
        self.rsa_C = self.entry_row(f, row, L["rsa_labels"]["C"], preset="20979746"); row += 1

        act = self.ui.frame(f, transparent=True); act.grid(row=row, column=0, sticky="ew", padx=8, pady=2); row += 1
        self.ui.button(act, L["rsa_actions"]["compute"], self.rsa_compute).grid(row=0, column=0, sticky="w", padx=6)
        self.ui.button(act, L["rsa_actions"]["enc"], self.rsa_encrypt).grid(row=0, column=1, sticky="w", padx=6)
        self.ui.button(act, L["rsa_actions"]["dec"], self.rsa_decrypt).grid(row=0, column=2, sticky="w", padx=6)

        self.ui.label(f, L["rsa_params"], size=13, bold=True).grid(row=row, column=0, sticky="w", padx=8); row += 1
        self.rsa_params_box = self.ui.textbox(f, 160); self.rsa_params_box.grid(row=row, column=0, sticky="nsew", padx=8); row += 1
        self.ui.label(f, self.ui.lang["log_title"], size=14, bold=True).grid(row=row, column=0, sticky="w", padx=8); row += 1
        self.rsa_log = self.ui.textbox(f, 140); self.rsa_log.grid(row=row, column=0, sticky="nsew", padx=8); row += 1
        self._append_log(self.rsa_log, "Ready: RSA")
        f.grid_rowconfigure(row-2, weight=1); f.grid_rowconfigure(row, weight=1)

    def entry_row(self, parent, row, label, preset=None):
        fr = self.ui.frame(parent, transparent=True); fr.grid(row=row, column=0, sticky="ew", padx=8, pady=2)
        self.ui.label(fr, label).grid(row=0, column=0, sticky="w")
        e = self.ui.entry(fr, width=280); e.grid(row=0, column=1, sticky="we", padx=6)
        if preset: e.insert(0, preset)
        return e

    def rsa_compute(self):
        try:
            p, q = int(self.rsa_p.get()), int(self.rsa_q.get())
            if p <= 1 or q <= 1: raise ValueError("p,q must be > 1")
            N, phi = p*q, (p-1)*(q-1)
            d = self._intval(self.rsa_d.get()); e = self._intval(self.rsa_e.get())
            if d is None and e is None: raise ValueError("Provide at least d or e")
            if d is not None and e is None: e = modinv(d % phi, phi)
            elif e is not None and d is None: d = modinv(e % phi, phi)
            elif (e*d) % phi != 1: raise ValueError("e and d are not modular inverses modulo φ(N)")
            self.rsa_state = {"p": p, "q": q, "N": N, "phi": phi, "d": d, "e": e}
            text = "\n".join([f"d = {d}", f"e = {e}", f"p = {p}", f"q = {q}", f"N = {N}", f"φ(N) = {phi}", f"Ek = ({e}, {N})", f"Dk = ({d}, {N})"])
            self._set_text(self.rsa_params_box, text); self._append_log(self.rsa_log, "Computed RSA parameters")
        except Exception as exc:
            self.rsa_state = None; self._append_log(self.rsa_log, f"Compute error: {exc}"); messagebox.showerror("RSA compute", str(exc))

    def rsa_encrypt(self):
        try:
            if not self.rsa_state: self._append_log(self.rsa_log, "Auto compute..."); self.rsa_compute()
            if not self.rsa_state: raise RuntimeError("RSA params not available")
            N, e = self.rsa_state["N"], self.rsa_state["e"]
            M = self._require_int(self.rsa_M.get(), "M")
            if not (0 <= M < N): raise ValueError(f"M must be in [0, {N-1}]")
            C = pow(M, e, N)
            self._append("Encrypt", f"M = {M}\nC = {C}")
            self._append_log(self.rsa_log, f"Encryption done. C={C}")
        except Exception as exc:
            self._append_log(self.rsa_log, f"Encrypt error: {exc}"); messagebox.showerror("RSA encrypt", str(exc))

    def rsa_decrypt(self):
        try:
            if not self.rsa_state: self._append_log(self.rsa_log, "Auto compute..."); self.rsa_compute()
            if not self.rsa_state: raise RuntimeError("RSA params not available")
            N, d = self.rsa_state["N"], self.rsa_state["d"]
            C = self._require_int(self.rsa_C.get(), "C")
            if not (0 <= C < N): raise ValueError(f"C must be in [0, {N-1}]")
            M = pow(C, d, N)
            self._append("Decrypt", f"C = {C}\nM = {M}")
            self._append_log(self.rsa_log, f"Decryption done. M={M}")
        except Exception as exc:
            self._append_log(self.rsa_log, f"Decrypt error: {exc}"); messagebox.showerror("RSA decrypt", str(exc))

    def _append(self, section, text):
        prev = self._get_text(self.rsa_params_box).rstrip()
        self._set_text(self.rsa_params_box, prev + f"\n\n{section}:\n{text}\n")

    def _intval(self, s):
        s = str(s).strip()
        return int(s) if s and s.lstrip("-").isdigit() else None

    def _require_int(self, s, name):
        s = str(s).strip()
        if not s or not s.lstrip("-").isdigit(): raise ValueError(f"{name} must be integer")
        return int(s)

    # ----- Polybius -----
    def build_poly(self):
        f, L = self.pages["poly"], self.ui.lang
        self.ui.label(f, L["poly_title"], size=18, bold=True).grid(row=0, column=0, sticky="w", padx=8, pady=(8,6))
        self.ui.label(f, L["poly_alpha"]).grid(row=1, column=0, sticky="w", padx=8)
        row2 = self.ui.frame(f, transparent=True); row2.grid(row=2, column=0, sticky="ew", padx=8)
        self.poly_alpha = tk.StringVar(self, value="EN"); self.ui.optmenu(row2, self.poly_alpha, ["EN","UA"]).grid(row=0, column=1, sticky="w", padx=6)
        self.ui.label(f, L["poly_in"]).grid(row=3, column=0, sticky="w", padx=8)
        self.poly_in = self.ui.textbox(f, 140); self.poly_in.grid(row=4, column=0, sticky="nsew", padx=8)
        r5 = self.ui.frame(f, transparent=True); r5.grid(row=5, column=0, sticky="ew", padx=8)
        self.ui.button(r5, L["poly_enc"], lambda: self.poly_run(True)).grid(row=0, column=0, sticky="w", padx=6)
        self.ui.button(r5, L["poly_dec"], lambda: self.poly_run(False)).grid(row=0, column=1, sticky="w", padx=6)
        self.ui.label(f, L["poly_out"]).grid(row=6, column=0, sticky="w", padx=8)
        self.poly_out = self.ui.textbox(f, 140); self.poly_out.grid(row=7, column=0, sticky="nsew", padx=8)
        self.ui.label(f, self.ui.lang["log_title"], size=14, bold=True).grid(row=8, column=0, sticky="w", padx=8)
        self.poly_log = self.ui.textbox(f, 120); self.poly_log.grid(row=9, column=0, sticky="nsew", padx=8)
        self._append_log(self.poly_log, "Ready: Polybius")
        f.grid_rowconfigure(4, weight=1); f.grid_rowconfigure(7, weight=1); f.grid_rowconfigure(9, weight=1)

    def _poly_alpha(self):
        return ("ABCDEFGHIKLMNOPQRSTUVWXYZ" if self.poly_alpha.get()=="EN" else UA_UP + "012")

    def _poly_maps(self, alphabet):
        s = "".join(dict.fromkeys(alphabet)); n = len(s); size = 5 if n==25 else 6
        enc, dec = {}, {}; idx = 0
        for r in range(1,size+1):
            for c in range(1,size+1):
                ch = s[idx]; enc[ch]=f"{r}{c}"; dec[f"{r}{c}"]=ch; idx += 1
        return enc, dec

    def poly_run(self, encrypt):
        try:
            alpha = self._poly_alpha(); text = self._get_text(self.poly_in)
            enc, dec = self._poly_maps(alpha)
            if encrypt:
                out = [(enc.get(ch.upper() if ch.isalpha() else ch, ch)) for ch in text]
                res = " ".join(out).replace("  "," ")
            else:
                tokens = text.replace("\n"," ").split(); res = "".join([dec.get(t,t) for t in tokens])
            self._set_text(self.poly_out, res); self._append_log(self.poly_log, "Done Polybius.")
        except Exception as e:
            self._append_log(self.poly_log, f"Polybius error: {e}"); messagebox.showerror("Polybius", str(e))

    # ----- Vigenère -----
    def build_vig(self):
        f, L = self.pages["vig"], self.ui.lang
        self.ui.label(f, L["vig_title"], size=18, bold=True).grid(row=0, column=0, sticky="w", padx=8, pady=(8,6))
        row1 = self.ui.frame(f, transparent=True); row1.grid(row=1, column=0, sticky="ew", padx=8)
        self.ui.label(row1, L["vig_alpha"]).grid(row=0, column=0, sticky="w")
        self.vig_alpha = tk.StringVar(self, value="UA"); self.ui.optmenu(row1, self.vig_alpha, ["UA","EN"]).grid(row=0, column=1, sticky="w", padx=6)
        self.ui.label(f, L["vig_in"]).grid(row=2, column=0, sticky="w", padx=8)
        self.vig_in = self.ui.textbox(f, 140); self.vig_in.grid(row=3, column=0, sticky="nsew", padx=8)
        row4 = self.ui.frame(f, transparent=True); row4.grid(row=4, column=0, sticky="ew", padx=8)
        self.ui.label(row4, L["vig_key"]).grid(row=0, column=0, sticky="w")
        self.vig_key = self.ui.entry(row4, 220); self.vig_key.grid(row=0, column=1, sticky="we", padx=6)
        self.ui.label(row4, L["vig_rot"]).grid(row=0, column=2, sticky="w", padx=(12,4))
        self.vig_rot = self.ui.entry(row4, 80); self.vig_rot.grid(row=0, column=3, sticky="w"); self.vig_rot.insert(0,"0")
        row5 = self.ui.frame(f, transparent=True); row5.grid(row=5, column=0, sticky="ew", padx=8)
        self.ui.button(row5, L["vig_enc"], lambda: self.vig_run(True)).grid(row=0, column=0, sticky="w", padx=6)
        self.ui.button(row5, L["vig_dec"], lambda: self.vig_run(False)).grid(row=0, column=1, sticky="w", padx=6)
        self.ui.button(row5, L["vig_tbl_gen"], self.vig_gen_table).grid(row=0, column=2, sticky="w", padx=6)
        self.ui.button(row5, L["vig_tbl_copy"], self.vig_copy_table).grid(row=0, column=3, sticky="w", padx=6)
        self.ui.label(f, "Output:").grid(row=6, column=0, sticky="w", padx=8)
        self.vig_out = self.ui.textbox(f, 140); self.vig_out.grid(row=7, column=0, sticky="nsew", padx=8)
        self.vig_tbl_label = self.ui.label(f, L["vig_tbl_label"], size=13, bold=True); self.vig_tbl_label.grid(row=8, column=0, sticky="w", padx=8, pady=(8,2))
        self.vig_tbl = self.ui.textbox(f, 180); self.vig_tbl.grid(row=9, column=0, sticky="nsew", padx=8)
        self.ui.label(f, self.ui.lang["log_title"], size=14, bold=True).grid(row=10, column=0, sticky="w", padx=8)
        self.vig_log = self.ui.textbox(f, 120); self.vig_log.grid(row=11, column=0, sticky="nsew", padx=8)
        self._append_log(self.vig_log, "Ready: Vigenère")
        f.grid_rowconfigure(3, weight=1); f.grid_rowconfigure(7, weight=1); f.grid_rowconfigure(9, weight=1); f.grid_rowconfigure(11, weight=1)

    def _vig_alph(self):
        return (UA_UP, UA_LO) if self.vig_alpha.get()=="UA" else (EN_UP, EN_LO)

    def _vig_rot_val(self, up):
        s = self.vig_rot.get().strip()
        return int(s) % len(up) if s.lstrip("-").isdigit() else 0

    def vig_run(self, encrypt):
        try:
            up, lo = self._vig_alph(); rot = self._vig_rot_val(up)
            upR = rotate_alphabet(up, rot); loR = rotate_alphabet(lo, rot) if len(lo)==len(up) else "".join(ch.lower() for ch in upR)
            text, key = self._get_text(self.vig_in), self.vig_key.get().strip()
            res = vigenere(text, key, encrypt, upR)
            self._set_text(self.vig_out, res); self._append_log(self.vig_log, "Vigenère done")
        except Exception as e:
            self._append_log(self.vig_log, f"Error: {e}"); messagebox.showerror("Vigenère", str(e))

    def vig_gen_table(self):
        try:
            up, _ = self._vig_alph(); rot = self._vig_rot_val(up)
            upR = rotate_alphabet(up, rot)
            text, key = self._get_text(self.vig_in), self.vig_key.get().strip()
            tbl = vigenere_table(text, key, upR)
            self._set_text(self.vig_tbl, f"Alphabet (ROT={rot}): {upR}\n{tbl}")
            self._append_log(self.vig_log, "Mapping table generated")
        except Exception as e:
            self._append_log(self.vig_log, f"Table error: {e}"); messagebox.showerror("Vigenère table", str(e))

    def vig_copy_table(self):
        try:
            content = self._get_text(self.vig_tbl)
            self.clipboard_clear(); self.clipboard_append(content)
            self._append_log(self.vig_log, "Table copied to clipboard")
        except Exception as e:
            self._append_log(self.vig_log, f"Copy error: {e}"); messagebox.showerror("Copy", str(e))

    # ----- Cipser -----
    def build_cip(self):
        f, L = self.pages["cip"], self.ui.lang
        self.ui.label(f, L["cip_title"], size=18, bold=True).grid(row=0, column=0, sticky="w", padx=8, pady=(8,6))
        self.ui.label(f, L["cip_in"]).grid(row=1, column=0, sticky="w", padx=8)
        self.cip_in = self.ui.textbox(f, 140); self.cip_in.grid(row=2, column=0, sticky="nsew", padx=8)
        r3 = self.ui.frame(f, transparent=True); r3.grid(row=3, column=0, sticky="ew", padx=8)
        self.ui.label(r3, L["cip_alpha"]).grid(row=0, column=0, sticky="w")
        self.cip_alpha = tk.StringVar(self, value="UA"); self.ui.optmenu(r3, self.cip_alpha, ["UA","EN"]).grid(row=0, column=1, sticky="w", padx=6)
        self.ui.label(r3, L["cip_shift"]).grid(row=0, column=2, sticky="w", padx=(12,4))
        self.cip_shift = self.ui.entry(r3, 100); self.cip_shift.grid(row=0, column=3, sticky="w"); self.cip_shift.insert(0,"3")
        r4 = self.ui.frame(f, transparent=True); r4.grid(row=4, column=0, sticky="ew", padx=8)
        self.ui.button(r4, L["cip_enc"], lambda: self.cip_run(True)).grid(row=0, column=0, sticky="w", padx=6)
        self.ui.button(r4, L["cip_dec"], lambda: self.cip_run(False)).grid(row=0, column=1, sticky="w", padx=6)
        self.ui.label(f, self.ui.lang["poly_out"]).grid(row=5, column=0, sticky="w", padx=8)
        self.cip_out = self.ui.textbox(f, 140); self.cip_out.grid(row=6, column=0, sticky="nsew", padx=8)
        self.ui.label(f, self.ui.lang["log_title"], size=14, bold=True).grid(row=7, column=0, sticky="w", padx=8)
        self.cip_log = self.ui.textbox(f, 120); self.cip_log.grid(row=8, column=0, sticky="nsew", padx=8)
        self._append_log(self.cip_log, "Ready: Cipser")
        f.grid_rowconfigure(2, weight=1); f.grid_rowconfigure(6, weight=1); f.grid_rowconfigure(8, weight=1)

    def cip_run(self, encrypt):
        try:
            up, lo = ((UA_UP, UA_LO) if self.cip_alpha.get()=="UA" else (EN_UP, EN_LO))
            s = self.cip_shift.get().strip(); shift = int(s) if s.lstrip("-").isdigit() else 0
            text = self._get_text(self.cip_in)
            res = caesar(text, (shift if encrypt else -shift), up, lo)
            self._set_text(self.cip_out, res); self._append_log(self.cip_log, "Cipser done")
        except Exception as e:
            self._append_log(self.cip_log, f"Cipser error: {e}"); messagebox.showerror("Cipser", str(e))

    # ----- Settings & About -----
    def build_settings(self):
        f, L = self.pages["settings"], self.ui.lang
        self.ui.label(f, L["nav"][4], size=18, bold=True).grid(row=0, column=0, sticky="w", padx=8, pady=(8,6))
        self.ui.label(f, "Мова / Language:").grid(row=1, column=0, sticky="w", padx=8)
        if CTK_AVAILABLE:
            ctk.CTkOptionMenu(f, values=["ua","en"], variable=self.current_lang, command=lambda *_: self.on_lang_change()).grid(row=1, column=1, sticky="w", padx=8)
            ctk.CTkOptionMenu(f, values=list(THEMES.keys()), variable=self.current_theme_name, command=lambda *_: self.apply_theme()).grid(row=2, column=1, sticky="w", padx=8)
        else:
            tk.OptionMenu(f, self.current_lang, "ua","en", command=lambda *_: self.on_lang_change()).grid(row=1, column=1, sticky="w", padx=8)
            tk.OptionMenu(f, self.current_theme_name, *list(THEMES.keys()), command=lambda *_: self.apply_theme()).grid(row=2, column=1, sticky="w", padx=8)
        self.ui.label(f, "Тема / Theme:").grid(row=2, column=0, sticky="w", padx=8)
        self.ui.label(f, self.ui.lang["log_title"], size=14, bold=True).grid(row=3, column=0, sticky="w", padx=8)
        self.settings_log = self.ui.textbox(f, 120); self.settings_log.grid(row=4, column=0, sticky="nsew", padx=8)
        self._append_log(self.settings_log, "Ready: Settings")
        f.grid_rowconfigure(4, weight=1)

    def build_about(self):
        f, L = self.pages["about"], self.ui.lang
        self.ui.label(f, L["about_title"], size=18, bold=True).grid(row=0, column=0, sticky="w", padx=8, pady=(8,6))
        self.ui.label(f, L["about_text"]).grid(row=1, column=0, sticky="w", padx=8)
        self.ui.label(f, L["about_links"]).grid(row=2, column=0, sticky="w", padx=8)
        logo_holder = self.ui.frame(f, transparent=True); logo_holder.grid(row=3, column=0, sticky="w", padx=8)
        self.load_logo(logo_holder)
        self.ui.label(f, self.ui.lang["log_title"], size=14, bold=True).grid(row=4, column=0, sticky="w", padx=8)
        self.about_log = self.ui.textbox(f, 120); self.about_log.grid(row=5, column=0, sticky="nsew", padx=8)
        self._append_log(self.about_log, "Ready: About")
        f.grid_rowconfigure(5, weight=1)

    # ----- generic text helpers -----
    def _get_text(self, box) -> str:
        return box.get("1.0", "end" if CTK_AVAILABLE else tk.END)

    def _set_text(self, box, content: str):
        box.delete("1.0", "end" if CTK_AVAILABLE else tk.END); box.insert("1.0", content)

    def _append_log(self, box, msg: str):
        """Append a line to a CTkTextbox/Tk Text widget safely."""
        try:
            cur = self._get_text(box).rstrip()
            new = (cur + ("\n" if cur else "") + msg)
            self._set_text(box, new)
        except Exception:
            # Last resort: ignore to avoid hard crash
            pass

# ---------- run ----------
def main():
    app = LiteApp()
    app.mainloop()

if __name__ == "__main__":
    main()