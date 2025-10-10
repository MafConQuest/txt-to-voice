#!/usr/bin/env python3
"""
txttovoice - Professional Text-to-Voice Application
==================================================

A professional text-to-voice application with global hotkey support.
Visit: https://txttovoice.com

Author: txttovoice.com
Version: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import requests
import pygame
import pyautogui
import pyperclip
import pystray
from PIL import Image
from pynput import keyboard
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import io
from datetime import datetime


class TxtToVoiceApp:
    """Professional Text-to-Voice Application."""
    
    def __init__(self):
        """Initialize the application."""
        self.setup_logging()
        self.load_config()
        self.setup_audio()
        
        # State
        self.is_running = False
        self.hotkey_listener = None
        self.tray_icon = None
        self.current_audio_data = None
        
        # Create UI
        self.setup_ui()
        self.setup_system_tray()
        self.start_hotkey_listener()
        
        self.logger.info("txttovoice initialized successfully")
    
    def setup_logging(self):
        """Setup basic logging."""
        log_dir = Path.home() / '.txttovoice'
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'app.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self):
        """Load configuration from file."""
        self.config_file = Path.home() / '.txttovoice' / 'config.json'
        self.config_file.parent.mkdir(exist_ok=True)
        
        default_config = {
            'openai_api_key': '',
            'voice': 'alloy',
            'speed': 1.0,
            'hotkey': 'ctrl+shift+j',
            'window_geometry': '500x400'
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = {**default_config, **json.load(f)}
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
                self.config = default_config
        else:
            self.config = default_config
    
    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
    
    def setup_audio(self):
        """Initialize audio system."""
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.logger.info("Audio system initialized")
        except Exception as e:
            self.logger.error(f"Error initializing audio: {e}")
    
    def setup_ui(self):
        """Create the main UI."""
        self.root = tk.Tk()
        self.root.title("txttovoice - Professional Text-to-Speech")
        self.root.geometry(self.config['window_geometry'])
        self.root.minsize(450, 350)
        
        # Set icon
        try:
            icon_path = Path(__file__).parent / "icons" / "txttovoice.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        title_label = ttk.Label(header_frame, text="🎤 txttovoice", 
                               font=('Arial', 18, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        website_label = ttk.Label(header_frame, text="txttovoice.com", 
                                 font=('Arial', 10), foreground='blue')
        website_label.pack(side=tk.RIGHT)
        
        # Text input
        text_label = ttk.Label(main_frame, text="Text to convert:")
        text_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.text_input = tk.Text(main_frame, height=8, wrap=tk.WORD, 
                                 font=('Arial', 11))
        self.text_input.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), 
                            pady=(0, 15))
        
        # Add placeholder text
        placeholder = "Type text here or use Ctrl+Shift+J to convert selected text from anywhere..."
        self.text_input.insert('1.0', placeholder)
        self.text_input.bind('<FocusIn>', self.on_text_focus_in)
        self.text_input.bind('<FocusOut>', self.on_text_focus_out)
        
        # Controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Voice and speed
        ttk.Label(controls_frame, text="Voice:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.voice_var = tk.StringVar(value=self.config['voice'])
        voice_combo = ttk.Combobox(controls_frame, textvariable=self.voice_var, 
                                  values=['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'],
                                  state='readonly', width=12)
        voice_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 15))
        voice_combo.bind('<<ComboboxSelected>>', self.on_voice_changed)
        
        ttk.Label(controls_frame, text="Speed:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        
        self.speed_var = tk.StringVar(value=str(self.config['speed']))
        speed_combo = ttk.Combobox(controls_frame, textvariable=self.speed_var,
                                  values=['0.5', '0.75', '1.0', '1.25', '1.5', '2.0'],
                                  state='readonly', width=8)
        speed_combo.grid(row=0, column=3, sticky=tk.W)
        speed_combo.bind('<<ComboboxSelected>>', self.on_speed_changed)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        self.speak_button = ttk.Button(button_frame, text="🎤 Speak", 
                                      command=self.speak_text, width=12)
        self.speak_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="⚙️ Settings", 
                  command=self.show_settings, width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📌 Minimize", 
                  command=self.minimize_to_tray, width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="❌ Exit", 
                  command=self.quit_app, width=8).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Hotkey: Ctrl+Shift+J")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                               font=('Arial', 9), foreground='green')
        status_label.grid(row=5, column=0, columnspan=3, pady=(15, 0))
        
        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        # Save geometry on configure
        self.root.bind('<Configure>', self.on_window_configure)
    
    def on_text_focus_in(self, event):
        """Handle text input focus in."""
        if self.text_input.get('1.0', tk.END).strip().startswith('Type text here'):
            self.text_input.delete('1.0', tk.END)
    
    def on_text_focus_out(self, event):
        """Handle text input focus out."""
        if not self.text_input.get('1.0', tk.END).strip():
            placeholder = "Type text here or use Ctrl+Shift+J to convert selected text from anywhere..."
            self.text_input.insert('1.0', placeholder)
    
    def on_voice_changed(self, event):
        """Handle voice selection change."""
        self.config['voice'] = self.voice_var.get()
        self.save_config()
    
    def on_speed_changed(self, event):
        """Handle speed selection change."""
        self.config['speed'] = float(self.speed_var.get())
        self.save_config()
    
    def on_window_configure(self, event):
        """Handle window resize/move."""
        if event.widget == self.root:
            self.config['window_geometry'] = self.root.geometry()
            self.save_config()
    
    def on_window_close(self):
        """Handle window close."""
        result = messagebox.askyesnocancel(
            "txttovoice",
            "What would you like to do?\n\n"
            "• Yes = Minimize to system tray\n"
            "• No = Exit completely\n"
            "• Cancel = Keep window open"
        )
        
        if result is True:  # Yes - minimize to tray
            self.minimize_to_tray()
        elif result is False:  # No - exit completely
            self.quit_app()
    
    def start_hotkey_listener(self):
        """Start the global hotkey listener."""
        try:
            self.is_running = True
            
            def on_hotkey():
                """Handle hotkey press."""
                threading.Thread(target=self.handle_hotkey, daemon=True).start()
            
            # Parse hotkey
            hotkey_combo = self.config['hotkey'].replace('ctrl', '<ctrl>').replace('shift', '<shift>')
            
            self.hotkey_listener = keyboard.GlobalHotKeys({
                hotkey_combo: on_hotkey
            })
            self.hotkey_listener.start()
            
            self.logger.info(f"Hotkey listener started: {self.config['hotkey']}")
            self.update_status(f"Ready - Hotkey: {self.config['hotkey'].upper()}")
            
        except Exception as e:
            self.logger.error(f"Error starting hotkey listener: {e}")
            self.update_status("Hotkey setup failed")
    
    def handle_hotkey(self):
        """Handle global hotkey press."""
        try:
            self.logger.info("Hotkey pressed - capturing selected text")
            self.update_status("Capturing selected text...")
            
            text = self.capture_selected_text()
            
            if text and text.strip():
                self.logger.info(f"Captured text ({len(text)} chars): {text[:50]}...")
                self.update_status("Converting selected text...")
                self.convert_and_play_text(text)
            else:
                self.logger.warning("No text captured")
                self.update_status("No text selected - highlight text and try again")
                
                # Show helpful message after a delay
                def show_help():
                    time.sleep(2)
                    self.update_status("Ready - Select text then press Ctrl+Shift+J")
                
                threading.Thread(target=show_help, daemon=True).start()
                
        except Exception as e:
            self.logger.error(f"Error handling hotkey: {e}")
            self.update_status("Error processing hotkey")
    
    def capture_selected_text(self) -> Optional[str]:
        """Capture selected text using multiple robust methods."""
        methods = [
            self.method_1_basic_clipboard,
            self.method_2_enhanced_clipboard,
            self.method_3_multiple_attempts
        ]
        
        for i, method in enumerate(methods, 1):
            try:
                self.logger.debug(f"Trying capture method {i}")
                text = method()
                if text and text.strip():
                    self.logger.info(f"Method {i} succeeded: {text[:50]}...")
                    return text.strip()
            except Exception as e:
                self.logger.debug(f"Method {i} failed: {e}")
                continue
        
        self.logger.warning("All text capture methods failed")
        return None
    
    def method_1_basic_clipboard(self) -> Optional[str]:
        """Method 1: Basic clipboard approach."""
        try:
            original = pyperclip.paste()
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.2)
            new_text = pyperclip.paste()
            pyperclip.copy(original)
            
            if new_text and new_text != original and new_text.strip():
                return new_text
            return None
        except Exception:
            return None
    
    def method_2_enhanced_clipboard(self) -> Optional[str]:
        """Method 2: Enhanced clipboard with marker."""
        try:
            original = pyperclip.paste()
            marker = f"TTS_MARKER_{int(time.time())}"
            pyperclip.copy(marker)
            time.sleep(0.1)
            
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.3)
            
            new_text = pyperclip.paste()
            pyperclip.copy(original)
            
            if new_text and new_text != marker and new_text != original and new_text.strip():
                return new_text
            return None
        except Exception:
            return None
    
    def method_3_multiple_attempts(self) -> Optional[str]:
        """Method 3: Multiple attempts with varying timing."""
        try:
            original = pyperclip.paste()
            
            for attempt in range(3):
                try:
                    pyperclip.copy("")
                    time.sleep(0.05)
                    
                    pyautogui.hotkey('ctrl', 'c')
                    wait_time = 0.2 + (attempt * 0.1)
                    time.sleep(wait_time)
                    
                    new_text = pyperclip.paste()
                    
                    if new_text and new_text != original and new_text.strip():
                        pyperclip.copy(original)
                        return new_text
                        
                except Exception:
                    continue
            
            pyperclip.copy(original)
            return None
        except Exception:
            return None
    
    def speak_text(self):
        """Speak the text in the input field."""
        text = self.text_input.get('1.0', tk.END).strip()
        
        if text.startswith('Type text here'):
            self.update_status("Please enter some text first")
            return
        
        if not text:
            self.update_status("Please enter some text first")
            return
        
        threading.Thread(target=self.convert_and_play_text, args=(text,), daemon=True).start()
    
    def convert_and_play_text(self, text: str):
        """Convert text to speech and play it."""
        try:
            if not self.config['openai_api_key']:
                self.update_status("Please set your OpenAI API key in Settings")
                return
            
            self.update_status("Converting to speech...")
            
            audio_data = self.call_openai_tts(text, self.config['voice'], self.config['speed'])
            
            if audio_data:
                self.update_status("Playing audio...")
                self.play_audio(audio_data)
                self.update_status("Ready")
            else:
                self.update_status("Failed to convert text")
                
        except Exception as e:
            self.logger.error(f"Error converting text: {e}")
            self.update_status("Error converting text")
    
    def call_openai_tts(self, text: str, voice: str, speed: float) -> Optional[bytes]:
        """Call OpenAI TTS API."""
        try:
            url = "https://api.openai.com/v1/audio/speech"
            headers = {
                "Authorization": f"Bearer {self.config['openai_api_key']}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "tts-1",
                "input": text,
                "voice": voice,
                "speed": speed,
                "response_format": "mp3"
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                return response.content
            else:
                self.logger.error(f"API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error calling OpenAI API: {e}")
            return None
    
    def play_audio(self, audio_data: bytes):
        """Play audio data using pygame."""
        try:
            self.current_audio_data = audio_data
            audio_file = io.BytesIO(audio_data)
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
        except Exception as e:
            self.logger.error(f"Error playing audio: {e}")
    
    def update_status(self, message: str):
        """Update status message."""
        def update():
            self.status_var.set(message)
        
        if self.root:
            self.root.after(0, update)
    
    def show_settings(self):
        """Show settings dialog."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("txttovoice Settings")
        settings_window.geometry("450x250")
        settings_window.resizable(False, False)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Center the window
        settings_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        frame = ttk.Frame(settings_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(frame, text="⚙️ txttovoice Settings", 
                 font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # API Key
        ttk.Label(frame, text="OpenAI API Key:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        api_key_var = tk.StringVar(value=self.config['openai_api_key'])
        api_key_entry = ttk.Entry(frame, textvariable=api_key_var, width=50, show="*")
        api_key_entry.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Get API Key link
        def open_api_link():
            import webbrowser
            webbrowser.open("https://platform.openai.com/api-keys")
        
        link_button = ttk.Button(frame, text="🔗 Get API Key", command=open_api_link)
        link_button.grid(row=3, column=0, sticky=tk.W, pady=(0, 15))
        
        # Hotkey
        ttk.Label(frame, text="Global Hotkey:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        hotkey_var = tk.StringVar(value=self.config['hotkey'])
        hotkey_entry = ttk.Entry(frame, textvariable=hotkey_var, width=20)
        hotkey_entry.grid(row=5, column=0, sticky=tk.W, pady=(0, 15))
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(15, 0))
        
        def save_settings():
            self.config['openai_api_key'] = api_key_var.get()
            old_hotkey = self.config['hotkey']
            self.config['hotkey'] = hotkey_var.get()
            self.save_config()
            
            # Restart hotkey listener if changed
            if old_hotkey != self.config['hotkey']:
                if self.hotkey_listener:
                    self.hotkey_listener.stop()
                self.start_hotkey_listener()
            
            settings_window.destroy()
            self.update_status("Settings saved")
        
        ttk.Button(button_frame, text="💾 Save", command=save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Cancel", command=settings_window.destroy).pack(side=tk.LEFT)
        
        # Focus on API key field
        api_key_entry.focus()
    
    def create_tray_icon(self):
        """Create system tray icon."""
        try:
            # Try to load the txttovoice icon
            icon_path = Path(__file__).parent / "icons" / "txttovoice.png"
            if icon_path.exists():
                image = Image.open(icon_path)
                # Resize to appropriate tray size
                image = image.resize((64, 64), Image.Resampling.LANCZOS)
                return image
        except Exception:
            pass
        
        # Create a simple fallback icon
        image = Image.new('RGB', (64, 64), color='blue')
        return image
    
    def setup_system_tray(self):
        """Setup system tray."""
        try:
            icon_image = self.create_tray_icon()
            
            menu_items = [
                pystray.MenuItem("🎤 Show txttovoice", self.show_from_tray, default=True),
                pystray.MenuItem("🎯 Quick TTS (Ctrl+Shift+J)", self.tray_quick_tts),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("⚙️ Settings", self.show_settings),
                pystray.MenuItem("🌐 Visit txttovoice.com", self.open_website),
                pystray.MenuItem("❌ Exit", self.quit_app)
            ]
            
            self.tray_icon = pystray.Icon(
                "txttovoice",
                icon_image,
                "txttovoice - Professional Text-to-Speech",
                menu=pystray.Menu(*menu_items)
            )
            
        except Exception as e:
            self.logger.error(f"Error setting up system tray: {e}")
    
    def minimize_to_tray(self):
        """Minimize to system tray."""
        if self.tray_icon:
            self.root.withdraw()
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
    
    def show_from_tray(self, icon=None, item=None):
        """Show window from system tray."""
        self.root.deiconify()
        self.root.lift()
        if self.tray_icon:
            self.tray_icon.stop()
    
    def tray_quick_tts(self, icon=None, item=None):
        """Quick TTS from tray."""
        threading.Thread(target=self.handle_hotkey, daemon=True).start()
    
    def open_website(self, icon=None, item=None):
        """Open txttovoice.com website."""
        import webbrowser
        webbrowser.open("https://txttovoice.com")
    
    def quit_app(self, icon=None, item=None):
        """Quit the application."""
        self.is_running = False
        
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        
        if self.tray_icon:
            self.tray_icon.stop()
        
        if self.root:
            self.root.quit()
    
    def run(self):
        """Run the application."""
        try:
            self.logger.info("Starting txttovoice")
            
            # Show welcome message if no API key
            if not self.config['openai_api_key']:
                self.root.after(1000, lambda: messagebox.showinfo(
                    "Welcome to txttovoice",
                    "Welcome to txttovoice!\n\n"
                    "🚀 Quick Start:\n"
                    "1. Click 'Settings' to add your OpenAI API key\n"
                    "2. Type text and click 'Speak' to test\n"
                    "3. Use Ctrl+Shift+J to convert selected text anywhere\n\n"
                    "Visit txttovoice.com for more info!"
                ))
            
            self.root.mainloop()
        except KeyboardInterrupt:
            self.quit_app()


def main():
    """Main entry point."""
    # Check dependencies
    required_modules = {
        'pygame': 'pygame',
        'pyautogui': 'pyautogui', 
        'pyperclip': 'pyperclip',
        'pynput': 'pynput',
        'requests': 'requests',
        'pystray': 'pystray',
        'PIL': 'Pillow'
    }
    
    missing = []
    for import_name, pip_name in required_modules.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pip_name)
    
    if missing:
        print("Missing required modules:")
        print(f"pip install {' '.join(missing)}")
        input("Press Enter to exit...")
        return
    
    # Start application
    try:
        app = TxtToVoiceApp()
        app.run()
    except Exception as e:
        print(f"Failed to start txttovoice: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()