"""
DecodeLabs - Project 2: Advanced Cryptographic GUI Engine (Full Frame Height Fix)
Features:
- Perfectly Filled Window Background (No Bottom Blank Gaps)
- Caesar Cipher Encryption & Decryption (Symmetric Verification)
- Security Vulnerabilities & Remediations Analysis
- Fullscreen Toggle, Copy Report & Export Options
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os

CYBER_COLORS = {
    'bg': '#071122',        # Unified main panel background
    'panel': '#071122',     # Matching panel color
    'accent': '#00ffd1',
    'accent2': '#6ae0ff',
    'muted': '#b0c7d9',
    'danger': '#ff4d6d',
    'warning': '#ffb86b',
    'ok': '#54ff7a',
}

def encrypt_caesar(plaintext: str, shift: int) -> str:
    ciphertext = []
    shift = shift % 26
    for char in plaintext:
        if char.isupper():
            ciphertext.append(chr((ord(char) - 65 + shift) % 26 + 65))
        elif char.islower():
            ciphertext.append(chr((ord(char) - 97 + shift) % 26 + 97))
        else:
            ciphertext.append(char)
    return "".join(ciphertext)

def decrypt_caesar(ciphertext: str, shift: int) -> str:
    plaintext = []
    shift = shift % 26
    for char in ciphertext:
        if char.isupper():
            plaintext.append(chr((ord(char) - 65 - shift) % 26 + 65))
        elif char.islower():
            plaintext.append(chr((ord(char) - 97 - shift) % 26 + 97))
        else:
            plaintext.append(char)
    return "".join(plaintext)

class CryptoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Caesar Cipher Engine v2.5")
        self.geometry("980x480")
        self.minsize(800, 600)
        self.configure(bg=CYBER_COLORS['bg'])

        self.fullscreen = False
        self._last_report = ""

        self._setup_style()
        self._build_ui()

        # Root level grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('TFrame', background=CYBER_COLORS['panel'])
        style.configure('TLabel', background=CYBER_COLORS['panel'], foreground=CYBER_COLORS['muted'])
        style.configure('TRadiobutton', background=CYBER_COLORS['panel'], foreground=CYBER_COLORS['muted'])
        style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'), foreground=CYBER_COLORS['accent'])
        style.configure('Accent.TButton', foreground='#0b0f18', background=CYBER_COLORS['accent'])
        style.map('Accent.TButton', background=[('active', CYBER_COLORS['accent2'])])

    def _build_ui(self):
        # Main Canvas with Unified Background
        self.canvas = tk.Canvas(self, bg=CYBER_COLORS['bg'], highlightthickness=0)
        self.vbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vbar.set)

        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.vbar.grid(row=0, column=1, sticky='ns')

        self.container = ttk.Frame(self.canvas, padding=14)
        self.container_id = self.canvas.create_window((0, 0), window=self.container, anchor='nw')

        self.container.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        # Mousewheel scroll support
        def _on_mousewheel(event):
            delta = 1 if (event.num == 5 or event.delta < 0) else -1
            self.canvas.yview_scroll(delta, 'units')

        self.canvas.bind_all('<MouseWheel>', _on_mousewheel)
        self.canvas.bind_all('<Button-4>', _on_mousewheel)
        self.canvas.bind_all('<Button-5>', _on_mousewheel)

        self.container.grid_columnconfigure(0, weight=1)

        # 1. Header Toolbar
        toolbar = ttk.Frame(self.container)
        toolbar.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        toolbar.grid_columnconfigure(0, weight=1)

        ttk.Label(toolbar, text="Cryptographic Security Module", style='Header.TLabel').grid(row=0, column=0, sticky='w')

        btn_box = ttk.Frame(toolbar)
        btn_box.grid(row=0, column=1, sticky='e')

        self.fs_btn = ttk.Button(btn_box, text="⤢ Fullscreen", command=self._toggle_fullscreen)
        self.fs_btn.grid(row=0, column=0, padx=4)

        ttk.Button(btn_box, text="Copy Report", command=self._copy_report).grid(row=0, column=1, padx=4)
        ttk.Button(btn_box, text="Export Report", command=self._export_report).grid(row=0, column=2, padx=4)

        # 2. Controls Section
        controls = ttk.Frame(self.container)
        controls.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        controls.grid_columnconfigure(1, weight=1)

        ttk.Label(controls, text="Shift Key (0-25):").grid(row=0, column=0, sticky='w', padx=(0, 8))

        self.shift_var = tk.IntVar(value=3)
        self.shift_spin = ttk.Spinbox(controls, from_=0, to=25, textvariable=self.shift_var, width=5, command=self._on_input_change)
        self.shift_spin.grid(row=0, column=1, sticky='w')
        self.shift_spin.bind('<KeyRelease>', lambda e: self._on_input_change())

        mode_frame = ttk.Frame(controls)
        mode_frame.grid(row=0, column=2, sticky='e')

        ttk.Label(mode_frame, text="Check Mode:").grid(row=0, column=0, padx=(0, 6))
        self.mode_var = tk.StringVar(value="realtime")

        rb_realtime = ttk.Radiobutton(mode_frame, text="Real-time (While typing)", value="realtime", variable=self.mode_var, command=self.process_crypto)
        rb_realtime.grid(row=0, column=1, padx=4)

        rb_manual = ttk.Radiobutton(mode_frame, text="On Button Click (After typing)", value="manual", variable=self.mode_var)
        rb_manual.grid(row=0, column=2, padx=4)

        # 3. Main Input/Output Text Area
        main_io = ttk.Frame(self.container)
        main_io.grid(row=2, column=0, sticky='nsew', pady=(0, 10))
        main_io.grid_columnconfigure(0, weight=1)
        main_io.grid_columnconfigure(1, weight=1)

        # Left: Plaintext Input
        left_box = ttk.Frame(main_io)
        left_box.grid(row=0, column=0, sticky='nsew', padx=(0, 6))
        left_box.grid_columnconfigure(0, weight=1)

        ttk.Label(left_box, text="Plaintext Input:").grid(row=0, column=0, sticky='w', pady=(0, 4))
        self.input_text = scrolledtext.ScrolledText(left_box, height=5, wrap='word')
        self.input_text.grid(row=1, column=0, sticky='nsew')
        self.input_text.configure(bg='#04121a', fg=CYBER_COLORS['accent2'], insertbackground=CYBER_COLORS['accent'])
        self.input_text.bind('<KeyRelease>', lambda e: self._on_input_change())

        # Right: Ciphertext Output
        right_box = ttk.Frame(main_io)
        right_box.grid(row=0, column=1, sticky='nsew', padx=(6, 0))
        right_box.grid_columnconfigure(0, weight=1)

        ttk.Label(right_box, text="Generated Ciphertext:").grid(row=0, column=0, sticky='w', pady=(0, 4))
        self.output_text = scrolledtext.ScrolledText(right_box, height=5, wrap='word')
        self.output_text.grid(row=1, column=0, sticky='nsew')
        self.output_text.configure(bg='#04121a', fg=CYBER_COLORS['ok'], insertbackground=CYBER_COLORS['ok'])

        # Action Buttons
        btn_row = ttk.Frame(self.container)
        btn_row.grid(row=3, column=0, sticky='ew', pady=(0, 10))

        ttk.Button(btn_row, text="Run Cryptographic Process", command=self.process_crypto, style='Accent.TButton').grid(row=0, column=0, padx=(0, 8))
        ttk.Button(btn_row, text="Clear All Fields", command=self._clear_all).grid(row=0, column=1)

        # 4. Decryption & Analysis Panel
        panels_frame = ttk.Frame(self.container)
        panels_frame.grid(row=4, column=0, sticky='nsew', pady=(0, 10))
        panels_frame.grid_columnconfigure(0, weight=1)
        panels_frame.grid_columnconfigure(1, weight=1)

        # Left: Decryption Verification
        dec_box = ttk.Frame(panels_frame)
        dec_box.grid(row=0, column=0, sticky='nsew', padx=(0, 6))
        dec_box.grid_columnconfigure(0, weight=1)

        ttk.Label(dec_box, text="Verified Decryption (Reversible Test):").grid(row=0, column=0, sticky='w', pady=(0, 4))
        self.decrypted_box = scrolledtext.ScrolledText(dec_box, height=5, wrap='word')
        self.decrypted_box.grid(row=1, column=0, sticky='nsew')
        self.decrypted_box.configure(state='disabled', bg='#04121a', fg=CYBER_COLORS['muted'])

        # Right: Vulnerabilities & Attack Vectors
        vuln_box = ttk.Frame(panels_frame)
        vuln_box.grid(row=0, column=1, sticky='nsew', padx=(6, 0))
        vuln_box.grid_columnconfigure(0, weight=1)

        ttk.Label(vuln_box, text="Cipher Vulnerabilities & Risks:").grid(row=0, column=0, sticky='w', pady=(0, 4))
        self.vuln_text = scrolledtext.ScrolledText(vuln_box, height=5, wrap='word')
        self.vuln_text.grid(row=1, column=0, sticky='nsew')
        self.vuln_text.configure(state='disabled', bg='#04121a', fg=CYBER_COLORS['danger'])

        # 5. Bottom Remediations Section
        bottom = ttk.Frame(self.container)
        bottom.grid(row=5, column=0, sticky='nsew', pady=(0, 10))
        bottom.grid_columnconfigure(0, weight=1)

        ttk.Label(bottom, text="Security Remediations & Cryptographic Upgrades:").grid(row=0, column=0, sticky='w', pady=(0, 4))
        self.rem_box = scrolledtext.ScrolledText(bottom, height=5, wrap='word')
        self.rem_box.grid(row=1, column=0, sticky='nsew')
        self.rem_box.configure(state='disabled', bg='#04121a', fg=CYBER_COLORS['warning'])

        self.process_crypto()

    # FIX: Layout Handlers for seamless auto-expansion
    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def _on_canvas_configure(self, event):
        # Dynamically fit container width to canvas width
        self.canvas.itemconfig(self.container_id, width=event.width)

    def _on_input_change(self):
        if self.mode_var.get() == "realtime":
            self.process_crypto()

    def process_crypto(self):
        try:
            shift = self.shift_var.get()
        except tk.TclError:
            shift = 3

        plaintext = self.input_text.get('1.0', tk.END).rstrip('\n')
        
        ciphertext = encrypt_caesar(plaintext, shift)
        decrypted = decrypt_caesar(ciphertext, shift)

        # Update Outputs
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, ciphertext)

        self.decrypted_box.configure(state='normal')
        self.decrypted_box.delete('1.0', tk.END)
        self.decrypted_box.insert(tk.END, decrypted)
        self.decrypted_box.configure(state='disabled')

        # Update Vulnerabilities
        self.vuln_text.configure(state='normal')
        self.vuln_text.delete('1.0', tk.END)
        vuln_info = (
            "• TINY KEY SPACE:\n"
            "  Only 25 possible shift keys exist. Easily broken using Brute-Force in < 1 millisecond.\n\n"
            "• PATTERN PRESERVATION:\n"
            "  Mono-alphabetic cipher preserves character frequencies (e.g., 'E' remains most frequent), "
            "making it highly vulnerable to Frequency Analysis attacks."
        )
        self.vuln_text.insert(tk.END, vuln_info)
        self.vuln_text.configure(state='disabled')

        # Update Remediations
        self.rem_box.configure(state='normal')
        self.rem_box.delete('1.0', tk.END)
        rem_info = (
            "1. Vigenère / Poly-alphabetic Cipher: Use multiple shift keys based on a keyword to obscure letter frequencies.\n"
            "2. Modern Symmetric Algorithms: Migrate to AES-256 (Advanced Encryption Standard) using 128-bit/256-bit keys.\n"
            "3. Confusion & Diffusion: Combine substitution and permutation blocks to neutralize pattern detection."
        )
        self.rem_box.insert(tk.END, rem_info)
        self.rem_box.configure(state='disabled')

        # Store last report
        self._last_report = (
            f"=== DecodeLabs Cryptographic Audit Report ===\n"
            f"Shift Key Used: {shift}\n"
            f"Plaintext     : {plaintext}\n"
            f"Ciphertext    : {ciphertext}\n"
            f"Decrypted     : {decrypted}\n\n"
            f"[!] VULNERABILITIES IDENTIFIED:\n"
            f"1. Key space is restricted to 25 values (Instant Brute Force).\n"
            f"2. Letter frequency distribution preserved (Frequency Analysis threat).\n\n"
            f"[+] REMEDIATIONS & UPGRADES:\n"
            f"1. Implement Poly-alphabetic substitution (e.g., Vigenère Cipher).\n"
            f"2. Upgrade to AES-256 for military-grade data protection in transit.\n"
            f"============================================="
        )

    def _clear_all(self):
        self.input_text.delete('1.0', tk.END)
        self.process_crypto()

    def _toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.attributes('-fullscreen', self.fullscreen)
        self.fs_btn.config(text="Exit Fullscreen" if self.fullscreen else "⤢ Fullscreen")

    def _copy_report(self):
        try:
            self.clipboard_clear()
            self.clipboard_append(self._last_report)
            messagebox.showinfo("Copied", "Cryptographic report copied to clipboard!")
        except Exception as e:
            messagebox.showwarning("Copy Failed", f"Could not copy report: {e}")

    def _export_report(self):
        try:
            path = os.path.join(os.getcwd(), 'crypto_report.txt')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self._last_report)
            messagebox.showinfo("Exported", f"Report successfully saved to:\n{path}")
        except Exception as e:
            messagebox.showwarning("Export Failed", f"Could not export report: {e}")

if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()