# Encrypted Chat - Desktop Prototype
# Simulates the client-side encryption concept from the Android Chat task.
# Built with Tkinter instead of native Android due to environment constraints -
# the encryption logic and key-storage discussion below map directly to how
# this would work using Android's Keystore system in a real mobile build.

import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime
import os
import json
import base64
import logging
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY_FILE = "device_key.bin"   # simulates where a real app would store its key reference
HISTORY_FILE = "message_history.json"

logging.basicConfig(
    filename="chat_app.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)


class CryptoManager:
    """
    Handles local AES-GCM encryption/decryption.

    IMPORTANT - secure storage note:
    This demo generates and stores the AES key in a local file (device_key.bin)
    purely so the prototype runs standalone with no extra setup. This is NOT
    how a real app should do it - see the Security Considerations section in
    the README for why, and what Android's Keystore does differently.
    """

    def __init__(self):
        self.key = self._load_or_create_key()

    def _load_or_create_key(self):
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, "rb") as f:
                return f.read()
        else:
            key = AESGCM.generate_key(bit_length=256)
            with open(KEY_FILE, "wb") as f:
                f.write(key)
            return key

    def encrypt(self, plaintext):
        aesgcm = AESGCM(self.key)
        nonce = os.urandom(12)  # GCM's version of an IV - must be unique per message
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
        packet = base64.b64encode(nonce + ciphertext).decode()
        return packet

    def decrypt(self, packet):
        raw = base64.b64decode(packet)
        nonce = raw[:12]
        ciphertext = raw[12:]
        aesgcm = AESGCM(self.key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode()


class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Encrypted Chat (Prototype)")
        self.root.geometry("420x520")

        self.crypto = CryptoManager()
        self.history = self._load_history()

        # --- UI layout ---
        title_label = tk.Label(root, text="Encrypted Chat - Prototype", font=("Segoe UI", 13, "bold"))
        title_label.pack(pady=8)

        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, state="disabled", height=18)
        self.chat_display.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.encrypted_preview = tk.Label(root, text="Encrypted packet: (nothing sent yet)",
                                           fg="gray", wraplength=380, justify="left", font=("Consolas", 8))
        self.encrypted_preview.pack(padx=10, pady=(0, 5), anchor="w")

        input_frame = tk.Frame(root)
        input_frame.pack(padx=10, pady=5, fill=tk.X)

        self.message_entry = tk.Entry(input_frame, font=("Segoe UI", 11))
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.message_entry.bind("<Return>", lambda event: self.send_message())

        send_button = tk.Button(input_frame, text="Send", command=self.send_message)
        send_button.pack(side=tk.RIGHT)

        # load any previous message history into the display
        self._render_history()

    def _load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        return []

    def _save_history(self):
        with open(HISTORY_FILE, "w") as f:
            json.dump(self.history, f)

    def _render_history(self):
        for entry in self.history:
            self._append_display(entry["text"], entry["timestamp"])

    def _append_display(self, text, timestamp):
        self.chat_display.configure(state="normal")
        self.chat_display.insert(tk.END, f"[{timestamp}] You: {text}\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see(tk.END)

    def send_message(self):
        text = self.message_entry.get().strip()

        if not text:
            messagebox.showwarning("Empty message", "Type something before sending.")
            return

        try:
            # encrypt locally before anything else happens - this is the core
            # requirement from the task ("perform local encryption/decryption")
            encrypted_packet = self.crypto.encrypt(text)
            self.encrypted_preview.config(text=f"Encrypted packet: {encrypted_packet[:50]}...")

            # simulate "sending" by immediately decrypting - proves the round trip works
            decrypted_back = self.crypto.decrypt(encrypted_packet)

            timestamp = datetime.now().strftime("%H:%M:%S")
            self._append_display(decrypted_back, timestamp)

            self.history.append({"text": decrypted_back, "timestamp": timestamp})
            self._save_history()

            logging.info(f"Message sent: {decrypted_back}")
            self.message_entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Encryption error", str(e))
            logging.error(f"Encryption error: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()