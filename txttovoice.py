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
        self.is_processing = False  # Flag to prevent multiple API calls
        self.last_api_call_time = 0  # Timestamp of last API call for rate limiting
        self.api_call_cooldown = 5.0  # 5 second cooldown between API calls
        self.is_audio_playing = False  # Track if audio is currently playing
        
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
    
    def stop_current_audio(self):
        """Stop any currently playing audio."""
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                self.is_audio_playing = False
                self.logger.info("Stopped current audio playback")
        except Exception as e:
            self.logger.error(f"Error stopping audio: {e}")
    
    def setup_ui(self):
        """Create the main UI."""
        self.root = tk.Tk()
        self.root.title("txttovoice - Professional Text-to-Speech")
        self.root.geometry(self.config['window_geometry'])
        self.root.minsize(500, 400)
        self.root.configure(bg='white')  # Set consistent white background
        
        # Set window attributes for better Windows integration
        try:
            # This helps with taskbar grouping on Windows
            self.root.wm_attributes('-toolwindow', False)
        except Exception:
            pass
        
        # Initialize history
        self.history = []
        
        # Set taskbar icon but keep title bar clean
        try:
            # Use high-quality PNG and ICO files
            icon_paths = [
                Path(__file__).parent / "icons" / "txttovoice.png",    # High-quality PNG
                Path("icons") / "txttovoice.png",
                Path(__file__).parent / "txttovoice.ico",             # High-quality ICO
                Path("txttovoice.ico"),
                Path(__file__).parent / "icons" / "txttovoice.ico",
                Path("icons") / "txttovoice.ico"
            ]
            
            # Set the taskbar icon using iconphoto (this affects taskbar but not title bar)
            for icon_path in icon_paths:
                if icon_path.exists():
                    from PIL import Image, ImageTk
                    # Load the icon and convert to PhotoImage
                    icon_img = Image.open(icon_path)
                    # Use high-quality size for taskbar (48x48 for better clarity)
                    icon_img = icon_img.resize((48, 48), Image.Resampling.LANCZOS)
                    self.taskbar_icon = ImageTk.PhotoImage(icon_img)
                    
                    # Set the taskbar icon using iconphoto
                    self.root.iconphoto(True, self.taskbar_icon)
                    self.logger.info(f"Taskbar icon set: {icon_path}")
                    break
            
            # Store icon paths for system tray use
            self.icon_paths = icon_paths
                
        except Exception as e:
            self.logger.error(f"Error setting taskbar icon: {e}")
            # Fallback to iconbitmap if iconphoto fails
            try:
                for icon_path in icon_paths:
                    if icon_path.exists():
                        self.root.iconbitmap(str(icon_path))
                        self.logger.info(f"Fallback: Set icon using iconbitmap: {icon_path}")
                        break
            except Exception as e2:
                self.logger.error(f"Fallback icon setting also failed: {e2}")
        
        # Configure style with modern colors inspired by the logo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Define colors from the new logo
        lime_green = '#9ACD32'  # Vibrant lime green from logo
        teal_green = '#20B2AA'  # Teal green from logo
        dark_bg = '#2B2B2B'     # Dark background
        light_bg = '#F0F0F0'    # Light background
        
        # Configure modern button styles
        style.configure('Accent.TButton', 
                       background=lime_green,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        style.map('Accent.TButton',
                 background=[('active', teal_green),
                           ('pressed', '#7BA428')])
        
        style.configure('Secondary.TButton',
                       background=teal_green,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        style.map('Secondary.TButton',
                 background=[('active', lime_green),
                           ('pressed', '#1A9B94')])
        
        # Configure frame styles - remove borders and backgrounds
        style.configure('Header.TFrame', 
                       background='white',
                       relief='flat',
                       borderwidth=0)
        style.configure('Main.TFrame', 
                       background='white',
                       relief='flat',
                       borderwidth=0)
        style.configure('Controls.TFrame',
                       background='white',
                       relief='flat',
                       borderwidth=0)
        
        # Configure combobox styling to reduce borders
        style.configure('TCombobox',
                       fieldbackground='white',
                       background='white',
                       borderwidth=1,
                       relief='solid')
        style.map('TCombobox',
                 fieldbackground=[('readonly', 'white')],
                 selectbackground=[('readonly', lime_green)])
        
        # Configure label styling for clean appearance
        style.configure('TLabel',
                       background='white',
                       foreground='black')
        
        # Configure button frame styling to remove borders
        style.configure('Buttons.TFrame',
                       background='white',
                       relief='flat',
                       borderwidth=0)
        
        # Main frame with modern styling
        main_frame = ttk.Frame(self.root, padding="15", style='Main.TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header with logo and website - clean styling without borders
        header_frame = ttk.Frame(main_frame, style='Header.TFrame')
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Left side - Logo and title - clean frame
        left_header = ttk.Frame(header_frame, style='Header.TFrame')
        left_header.pack(side=tk.LEFT)
        
        # Load and display larger logo without text
        try:
            logo_paths = [
                Path(__file__).parent / "icons" / "txttovoice.png",    # High-quality PNG
                Path("icons") / "txttovoice.png",
                Path(__file__).parent / "txttovoice.ico",
                Path("txttovoice.ico"),
                Path(__file__).parent / "icons" / "txttovoice.ico"
            ]
            
            for logo_path in logo_paths:
                if logo_path.exists():
                    from PIL import Image, ImageTk
                    logo_img = Image.open(logo_path)
                    # Make the logo a good size - 100x100 pixels
                    logo_img = logo_img.resize((100, 100), Image.Resampling.LANCZOS)
                    self.logo_photo = ImageTk.PhotoImage(logo_img)
                    
                    # Center the logo without text
                    logo_label = ttk.Label(left_header, image=self.logo_photo)
                    logo_label.pack(side=tk.LEFT)
                    break
        except Exception as e:
            self.logger.debug(f"Could not load logo: {e}")
            # Fallback: show text only if logo fails
            title_label = ttk.Label(left_header, text="txttovoice", 
                                   font=('Arial', 18, 'bold'))
            title_label.pack(side=tk.LEFT)
        
        # Right side - Clickable website link - clean frame
        right_header = ttk.Frame(header_frame, style='Header.TFrame')
        right_header.pack(side=tk.RIGHT)
        
        def open_website():
            import webbrowser
            webbrowser.open("https://txttovoice.com")
        
        website_label = ttk.Label(right_header, text="🌐 txttovoice.com", 
                                 font=('Arial', 10, 'bold'), foreground='#20B2AA',
                                 cursor='hand2')
        website_label.pack(side=tk.RIGHT)
        website_label.bind("<Button-1>", lambda e: open_website())
        
        # Add tooltip-like effect with logo colors
        def on_enter(e):
            website_label.configure(foreground='#9ACD32')
        def on_leave(e):
            website_label.configure(foreground='#20B2AA')
        
        website_label.bind("<Enter>", on_enter)
        website_label.bind("<Leave>", on_leave)
        
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
        
        # Controls frame - clean styling without borders
        controls_frame = ttk.Frame(main_frame, style='Controls.TFrame')
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
        
        # Buttons - clean frame without borders
        button_frame = ttk.Frame(main_frame, style='Buttons.TFrame')
        button_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        self.speak_button = ttk.Button(button_frame, text="🎤 Speak", 
                                      command=self.speak_text, width=12,
                                      style='Accent.TButton')
        self.speak_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="⚙️ Settings", 
                  command=self.show_settings, width=12,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📚 History", 
                  command=self.show_history, width=12,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📌 Minimize", 
                  command=self.minimize_to_tray, width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="❌ Exit", 
                  command=self.quit_app, width=8).pack(side=tk.LEFT, padx=5)
        
        # Status bar with logo colors
        self.status_var = tk.StringVar(value="Ready - Hotkey: Ctrl+Shift+J")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                               font=('Arial', 9, 'bold'), foreground='#20B2AA')
        status_label.grid(row=5, column=0, columnspan=3, pady=(15, 0))
        
        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        # Save geometry on configure
        self.root.bind('<Configure>', self.on_window_configure)
    
    def show_history(self):
        """Show history window."""
        history_window = tk.Toplevel(self.root)
        history_window.title("txttovoice History")
        history_window.geometry("600x400")
        history_window.transient(self.root)
        
        # Center the window
        history_window.update_idletasks()
        x = (history_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (history_window.winfo_screenheight() // 2) - (400 // 2)
        history_window.geometry(f"600x400+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(history_window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(header_frame, text="📚 Conversion History", 
                 font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        
        ttk.Button(header_frame, text="🗑️ Clear All", 
                  command=lambda: self.clear_history_and_refresh(history_tree)).pack(side=tk.RIGHT)
        
        # History list
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create treeview
        columns = ('Time', 'Text', 'Voice', 'Speed')
        history_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        history_tree.heading('Time', text='Time')
        history_tree.heading('Text', text='Text Preview')
        history_tree.heading('Voice', text='Voice')
        history_tree.heading('Speed', text='Speed')
        
        history_tree.column('Time', width=80)
        history_tree.column('Text', width=300)
        history_tree.column('Voice', width=80)
        history_tree.column('Speed', width=60)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=history_tree.yview)
        history_tree.configure(yscrollcommand=scrollbar.set)
        
        history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate history
        for item in self.history:
            history_tree.insert('', 'end', values=(
                item['time'],
                item['text_preview'],
                item['voice'],
                f"{item['speed']}x"
            ))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def replay_selected():
            # Check if already processing
            if self.is_processing:
                self.update_status("Please wait - already processing...")
                return
            
            # Check API call cooldown
            current_time = time.time()
            time_since_last_call = current_time - self.last_api_call_time
            if time_since_last_call < self.api_call_cooldown:
                remaining_time = self.api_call_cooldown - time_since_last_call
                self.update_status(f"Please wait {remaining_time:.1f} seconds before next conversion")
                return
                
            selection = history_tree.selection()
            if selection:
                item_index = history_tree.index(selection[0])
                if item_index < len(self.history):
                    history_item = self.history[item_index]
                    self.voice_var.set(history_item['voice'])
                    self.speed_var.set(str(history_item['speed']))
                    self.config['voice'] = history_item['voice']
                    self.config['speed'] = history_item['speed']
                    
                    # Stop any currently playing audio
                    self.stop_current_audio()
                    
                    threading.Thread(target=self.convert_and_play_text, 
                                   args=(history_item['text'],), daemon=True).start()
                    history_window.destroy()
        
        def use_text():
            selection = history_tree.selection()
            if selection:
                item_index = history_tree.index(selection[0])
                if item_index < len(self.history):
                    history_item = self.history[item_index]
                    self.text_input.delete('1.0', tk.END)
                    self.text_input.insert('1.0', history_item['text'])
                    history_window.destroy()
        
        ttk.Button(button_frame, text="🔊 Replay Selected", 
                  command=replay_selected, style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📝 Use Text", 
                  command=use_text, style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="❌ Close", 
                  command=history_window.destroy).pack(side=tk.RIGHT)
    
    def clear_history_and_refresh(self, tree):
        """Clear history and refresh the tree view."""
        self.history = []
        for item in tree.get_children():
            tree.delete(item)
        self.update_status("History cleared")
    
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
            # Check if already processing
            if self.is_processing:
                self.update_status("Please wait - already processing...")
                return
            
            # Check API call cooldown
            current_time = time.time()
            time_since_last_call = current_time - self.last_api_call_time
            if time_since_last_call < self.api_call_cooldown:
                remaining_time = self.api_call_cooldown - time_since_last_call
                self.update_status(f"Please wait {remaining_time:.1f} seconds before next conversion")
                return
                
            self.logger.info("Hotkey pressed - capturing selected text")
            self.update_status("Capturing selected text...")
            
            text = self.capture_selected_text()
            
            if text and text.strip():
                self.logger.info(f"Captured text ({len(text)} chars): {text[:50]}...")
                self.update_status("Converting selected text...")
                
                # Stop any currently playing audio
                self.stop_current_audio()
                
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
        # Check if already processing
        if self.is_processing:
            self.update_status("Please wait - already processing...")
            return
        
        # Check API call cooldown
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call_time
        if time_since_last_call < self.api_call_cooldown:
            remaining_time = self.api_call_cooldown - time_since_last_call
            self.update_status(f"Please wait {remaining_time:.1f} seconds before next conversion")
            return
            
        text = self.text_input.get('1.0', tk.END).strip()
        
        if text.startswith('Type text here'):
            self.update_status("Please enter some text first")
            return
        
        if not text:
            self.update_status("Please enter some text first")
            return
        
        # Stop any currently playing audio
        self.stop_current_audio()
        
        threading.Thread(target=self.convert_and_play_text, args=(text,), daemon=True).start()
    
    def convert_and_play_text(self, text: str):
        """Convert text to speech and play it."""
        try:
            # Set processing flag to prevent multiple API calls
            self.is_processing = True
            self.update_speak_button_state(False)  # Disable speak button
            
            if not self.config['openai_api_key']:
                self.update_status("Please set your OpenAI API key in Settings")
                return
            
            self.update_status("Converting to speech...")
            
            # Record API call timestamp
            self.last_api_call_time = time.time()
            
            audio_data = self.call_openai_tts(text, self.config['voice'], self.config['speed'])
            
            if audio_data:
                self.update_status("Playing audio...")
                # Clear processing flag when playback starts
                self.is_processing = False
                self.update_speak_button_state(True)  # Re-enable speak button
                
                self.play_audio(audio_data)
                
                # Add to history
                self.add_to_history(text, self.config['voice'], self.config['speed'])
                
                self.update_status("Ready")
            else:
                self.update_status("Failed to convert text")
                
        except Exception as e:
            self.logger.error(f"Error converting text: {e}")
            self.update_status("Error converting text")
        finally:
            # Always clear processing flag and re-enable button
            self.is_processing = False
            self.update_speak_button_state(True)
    
    def call_openai_tts(self, text: str, voice: str, speed: float) -> Optional[bytes]:
        """Call OpenAI TTS API."""
        return self.call_openai_tts_with_config(text, self.config)
    
    def call_openai_tts_with_config(self, text: str, config: dict) -> Optional[bytes]:
        """Call OpenAI TTS API with specific config."""
        try:
            url = "https://api.openai.com/v1/audio/speech"
            headers = {
                "Authorization": f"Bearer {config['openai_api_key']}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "tts-1",
                "input": text,
                "voice": config['voice'],
                "speed": config['speed'],
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
            
            self.is_audio_playing = True
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            self.is_audio_playing = False
                
        except Exception as e:
            self.logger.error(f"Error playing audio: {e}")
            self.is_audio_playing = False
    
    def update_status(self, message: str):
        """Update status message."""
        def update():
            self.status_var.set(message)
        
        if self.root:
            self.root.after(0, update)
    
    def update_speak_button_state(self, enabled: bool):
        """Update the speak button enabled/disabled state."""
        def update():
            if enabled:
                self.speak_button.configure(state='normal', text='🎤 Speak')
            else:
                self.speak_button.configure(state='disabled', text='⏳ Processing...')
        
        if self.root:
            self.root.after(0, update)
    
    def show_settings(self):
        """Show settings dialog."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("txttovoice Settings")
        settings_window.geometry("600x750")
        settings_window.minsize(580, 750)
        settings_window.resizable(True, True)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Center the window
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (settings_window.winfo_screenheight() // 2) - (500 // 2)
        settings_window.geometry(f"600x500+{x}+{y}")
        
        # Main frame with scrollable content
        main_frame = ttk.Frame(settings_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configure grid weights for proper resizing
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)  # Make the space above buttons expandable
        
        # Header
        header_label = ttk.Label(main_frame, text="⚙️ txttovoice Settings", 
                                font=('Arial', 16, 'bold'))
        header_label.grid(row=0, column=0, columnspan=2, pady=(0, 25), sticky=tk.W)
        
        # API Key Section
        api_section = ttk.LabelFrame(main_frame, text="OpenAI Configuration", padding="15")
        api_section.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        api_section.columnconfigure(0, weight=1)
        
        ttk.Label(api_section, text="API Key:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        api_key_var = tk.StringVar(value=self.config['openai_api_key'])
        api_key_entry = ttk.Entry(api_section, textvariable=api_key_var, show="*", width=50)
        api_key_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Get API Key link
        def open_api_link():
            import webbrowser
            webbrowser.open("https://platform.openai.com/api-keys")
        
        link_frame = ttk.Frame(api_section)
        link_frame.grid(row=2, column=0, sticky=tk.W)
        
        ttk.Label(link_frame, text="Don't have an API key?").pack(side=tk.LEFT)
        link_button = ttk.Button(link_frame, text="Get one here", command=open_api_link)
        link_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Hotkey Section
        hotkey_section = ttk.LabelFrame(main_frame, text="Hotkey Configuration", padding="15")
        hotkey_section.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        hotkey_section.columnconfigure(0, weight=1)
        
        ttk.Label(hotkey_section, text="Global Hotkey:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        hotkey_var = tk.StringVar(value=self.config['hotkey'])
        hotkey_entry = ttk.Entry(hotkey_section, textvariable=hotkey_var, width=25)
        hotkey_entry.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(hotkey_section, text="Example: ctrl+shift+j", 
                 font=('Arial', 9), foreground='gray').grid(row=2, column=0, sticky=tk.W)
        
        # Voice Settings Section
        voice_section = ttk.LabelFrame(main_frame, text="Voice Settings", padding="15")
        voice_section.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        voice_section.columnconfigure(1, weight=1)
        
        ttk.Label(voice_section, text="Default Voice:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        voice_var = tk.StringVar(value=self.config['voice'])
        voice_combo = ttk.Combobox(voice_section, textvariable=voice_var,
                                  values=['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'],
                                  state='readonly', width=15)
        voice_combo.grid(row=0, column=1, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(voice_section, text="Default Speed:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        
        speed_var = tk.StringVar(value=str(self.config['speed']))
        speed_combo = ttk.Combobox(voice_section, textvariable=speed_var,
                                  values=['0.5', '0.75', '1.0', '1.25', '1.5', '2.0'],
                                  state='readonly', width=15)
        speed_combo.grid(row=1, column=1, sticky=tk.W)
        
        # Spacer to push buttons to bottom
        spacer = ttk.Frame(main_frame)
        spacer.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Buttons at bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        
        def save_settings():
            try:
                # Validate API key
                api_key = api_key_var.get().strip()
                if api_key and not api_key.startswith('sk-'):
                    messagebox.showwarning("Invalid API Key", 
                                         "OpenAI API keys should start with 'sk-'")
                    return
                
                # Save settings
                self.config['openai_api_key'] = api_key
                self.config['voice'] = voice_var.get()
                self.config['speed'] = float(speed_var.get())
                
                old_hotkey = self.config['hotkey']
                self.config['hotkey'] = hotkey_var.get().strip()
                
                self.save_config()
                
                # Restart hotkey listener if changed
                if old_hotkey != self.config['hotkey']:
                    if self.hotkey_listener:
                        self.hotkey_listener.stop()
                    self.start_hotkey_listener()
                
                settings_window.destroy()
                self.update_status("Settings saved successfully")
                messagebox.showinfo("Settings Saved", "Your settings have been saved successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings: {e}")
        
        def test_settings():
            """Test the current settings"""
            if not api_key_var.get().strip():
                messagebox.showwarning("No API Key", "Please enter your OpenAI API key first.")
                return
            
            test_text = "This is a test of your txttovoice settings."
            self.update_status("Testing settings...")
            
            def run_test():
                try:
                    # Temporarily use the dialog settings
                    temp_config = self.config.copy()
                    temp_config['openai_api_key'] = api_key_var.get().strip()
                    temp_config['voice'] = voice_var.get()
                    temp_config['speed'] = float(speed_var.get())
                    
                    # Test API call
                    audio_data = self.call_openai_tts_with_config(test_text, temp_config)
                    if audio_data:
                        self.play_audio(audio_data)
                        self.update_status("Settings test successful!")
                        messagebox.showinfo("Test Successful", "Your settings are working correctly!")
                    else:
                        self.update_status("Settings test failed")
                        messagebox.showerror("Test Failed", "Could not connect with these settings. Please check your API key.")
                except Exception as e:
                    self.update_status("Settings test failed")
                    messagebox.showerror("Test Failed", f"Settings test failed: {e}")
            
            threading.Thread(target=run_test, daemon=True).start()
        
        # Button layout
        ttk.Button(button_frame, text="🧪 Test Settings", 
                  command=test_settings).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="💾 Save Settings", 
                  command=save_settings).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="❌ Cancel", 
                  command=settings_window.destroy).pack(side=tk.LEFT)
        
        # Focus on API key field if empty, otherwise on save button
        if not self.config['openai_api_key']:
            api_key_entry.focus()
        else:
            button_frame.children['!button2'].focus()  # Save button
    
    def create_tray_icon(self):
        """Create system tray icon."""
        try:
            # Try to load your custom txttovoice icon
            icon_paths = [
                Path(__file__).parent / "txttovoice.ico",
                Path("txttovoice.ico"),
                Path(__file__).parent / "icons" / "txttovoice.png",
                Path("icons") / "txttovoice.png"
            ]
            
            for icon_path in icon_paths:
                if icon_path.exists():
                    image = Image.open(icon_path)
                    # Use original size for better quality - system tray will scale appropriately
                    return image
        except Exception as e:
            self.logger.debug(f"Could not load tray icon: {e}")
        
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
    
    def add_to_history(self, text: str, voice: str, speed: float):
        """Add conversion to history."""
        from datetime import datetime
        
        # Limit text preview
        text_preview = text[:50] + "..." if len(text) > 50 else text
        
        history_item = {
            'time': datetime.now().strftime("%H:%M:%S"),
            'text': text,
            'text_preview': text_preview,
            'voice': voice,
            'speed': speed
        }
        
        # Add to beginning of history
        self.history.insert(0, history_item)
        
        # Limit history size
        if len(self.history) > 20:
            self.history = self.history[:20]
        
        # History updated (display will refresh when history window is opened)
    

    
    def clear_history(self):
        """Clear all history."""
        self.history = []
        self.refresh_history_display()
        self.update_status("History cleared")
    

    
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