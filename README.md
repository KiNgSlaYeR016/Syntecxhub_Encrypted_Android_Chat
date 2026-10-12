# Encrypted Chat - Desktop Prototype

A Python/Tkinter desktop application simulating the client-side encryption concepts from the Syntecxhub Cybersecurity internship Week 2 task: "Encrypted Android Chat."

## A note on scope
The original task asked for a native Android app. This submission is a desktop prototype built with Python and Tkinter instead, due to environment constraints (no Android SDK/emulator setup available). The core security concepts the task is testing - client-side AES encryption, local encrypt/decrypt, key storage awareness, basic UI, message history, and error handling - are all implemented and demonstrated here. Where this prototype differs from a real Android implementation, that's explicitly called out below rather than glossed over.

## What it does
A single-user chat interface where every message is encrypted locally with AES-GCM before being "sent" (simulated by immediately decrypting it back and displaying it). Shows the actual encrypted packet on screen so the encryption step is visibly proven, not just assumed. Message history persists between runs.

## Features
- AES-GCM encryption (authenticated encryption — detects tampering, not just confidentiality)
- A unique nonce generated for every message (GCM's equivalent of an IV)
- Local encrypt/decrypt round trip, with the encrypted packet shown in the UI
- Basic GUI built with Tkinter - message display, input box, send button
- Message history saved to disk and reloaded on restart
- Error handling with user-facing dialogs for encryption failures or empty input
- Logging of message activity to `chat_app.log`

## Technologies used
- Python 3
- `tkinter` - GUI (built into Python, no extra install)
- `cryptography` - AES-GCM encryption
- `json` - message history storage
- `logging` - activity logging

## How it works
On first run, the app generates a 256-bit AES key and stores it in `device_key.bin`. Every message typed gets encrypted locally using AES-GCM with a fresh random nonce, then the encrypted packet (nonce + ciphertext, base64-encoded) is shown in the UI as proof of what actually gets "sent." The app then decrypts it back to simulate the receiving side and displays the message in the chat window. Message history is saved to a local JSON file so previous messages reload the next time the app runs.

## How to run
```bash
pip install cryptography
python encrypted_chat_gui.py
```

## Security considerations
- **Key storage — the main gap vs. a real Android app.** This prototype stores the AES key in a plain local file (`device_key.bin`) for simplicity. A real Android implementation should instead use the **Android Keystore system**, which generates and holds the key inside secure hardware (when available) - the raw key bytes are never exposed to the app or extractable from the device, even with root access in many cases. Storing a key in a plain file, as this prototype does, would be considered insecure in a production mobile app, since anyone with access to the device's file system could copy the key out directly.
- **AES-GCM was chosen over AES-CBC** specifically because GCM provides built-in authentication - it detects if ciphertext has been tampered with, not just encrypts it. This matches what a real Android Keystore-based implementation would typically use.
- **Nonce/IV reuse** is avoided by generating a new random nonce per message, consistent with the Week 2 Project 1 requirement around safe IV usage.
- This is a **single-device, single-user simulation** - there's no real network transmission or second party involved, so it doesn't demonstrate interception resistance, only the encryption mechanics themselves.

## Limitations
- Not an actual Android app - a desktop simulation of the same concepts
- No real network communication between two separate clients 
- Key stored in plaintext on disk, which would not be acceptable in a real mobile deployment
- No authentication or multi-user support

## Future improvements
- Port this logic into an actual Android app using Kotlin and the Android Keystore API, replacing the plain-file key storage with hardware-backed key storage
- Add real two-device communication (could reuse the client/server architecture from Project 1)
- Add key rotation and the ability to wipe/reset the stored key

## Real-world relevance
Secure local key storage is one of the most common places mobile apps actually fail at security - plenty of real incidents trace back to apps storing encryption keys or secrets in plain, extractable locations instead of using platform-provided secure storage like Android Keystore or iOS Keychain. Understanding why that distinction matters, even when prototyping on a different platform, is directly relevant to application security review and mobile security awareness.
