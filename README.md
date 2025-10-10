# 🎤 TXT-To-Voice - Professional Text-to-Speech

**Convert any text to natural speech with a simple hotkey!**

Visit: **[txttovoice.com](https://txttovoice.com)**

## ✨ Features

- 🎯 **Global Hotkey** - Select text anywhere and press Ctrl+Shift+J
- 🎤 **6 Professional Voices** - Choose from OpenAI's premium voices
- 📌 **System Tray** - Runs quietly in the background
- ⚡ **Speed Control** - Adjust speech speed from 0.5x to 2.0x
- 🖥️ **Windows Integration** - Native Windows application
- 🔒 **Privacy First** - Your API key stays on your computer

## 🚀 Quick Start

### 1. Download
- **[Download Latest Release](https://github.com/yourusername/txttovoice/releases/latest)**
- Or visit **[txttovoice.com](https://txttovoice.com)** for direct download

### 2. Install
```bash
# Extract the downloaded files
# Run the installer
install.bat
```

### 3. Setup
1. Get your OpenAI API key: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Launch txttovoice
3. Click "Settings" and enter your API key
4. Done! 🎉

## 🎯 How to Use

### Method 1: Global Hotkey (Recommended)
1. **Select any text** in any application (browser, document, email, etc.)
2. **Press Ctrl+Shift+J**
3. **Listen** to the natural speech!

### Method 2: Manual Input
1. Open txttovoice
2. Type or paste your text
3. Click "Speak"

### Method 3: System Tray
1. Right-click the tray icon
2. Select "Quick TTS"
3. Works with selected text

## 🎤 Voice Options

Choose from 6 professional OpenAI voices:

- **alloy** - Balanced and natural
- **echo** - Clear and professional  
- **fable** - Warm storytelling voice
- **onyx** - Deep and authoritative
- **nova** - Bright and energetic
- **shimmer** - Soft and gentle

## ⚙️ System Requirements

- **Windows 10/11** (64-bit)
- **Python 3.7+** (automatically checked during install)
- **OpenAI API Key** (get yours at [platform.openai.com](https://platform.openai.com/api-keys))
- **Internet connection** (for text-to-speech conversion)

## 💰 Pricing

txttovoice is **free to use**! You only pay for OpenAI API usage:

- **~$0.015 per 1,000 characters** (about 1¢ per page)
- **First $5 free** with new OpenAI accounts
- **Pay only for what you use**

## 🛠️ Installation Options

### Option 1: One-Click Installer (Recommended)
1. Download from [txttovoice.com](https://txttovoice.com)
2. Run `install.bat`
3. Follow the prompts

### Option 2: Manual Installation
```bash
# Clone or download this repository
git clone https://github.com/yourusername/txttovoice.git
cd txttovoice

# Install dependencies
pip install pygame requests pyautogui pyperclip pystray pillow pynput

# Run the application
python txttovoice.py
```

## 🔧 Configuration

### Settings Available:
- **OpenAI API Key** - Your personal API key
- **Default Voice** - Choose your preferred voice
- **Speech Speed** - Adjust from 0.5x to 2.0x
- **Global Hotkey** - Customize the hotkey combination

### Config File Location:
- Windows: `%USERPROFILE%\.txttovoice\config.json`

## 🆘 Troubleshooting

### Common Issues:

**"No text selected"**
- Make sure text is highlighted (blue background)
- Try different applications (some PDFs don't allow copying)
- Use manual input as a test

**"Please set your OpenAI API key"**
- Get an API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- Click Settings in txttovoice and enter the key

**Hotkey not working**
- Try running as Administrator
- Check if another app uses the same hotkey
- Change hotkey in Settings

**No sound**
- Check Windows volume settings
- Verify your internet connection
- Test with manual input first

### Getting Help:
- Visit [txttovoice.com](https://txttovoice.com) for support
- Check the logs at `%USERPROFILE%\.txttovoice\app.log`
- Create an issue on GitHub

## 🔄 Updates

txttovoice automatically checks for updates. You can also:
- Visit [txttovoice.com](https://txttovoice.com) for the latest version
- Watch this GitHub repository for releases
- Follow [@txttovoice](https://twitter.com/txttovoice) for announcements

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Links

- **Website**: [txttovoice.com](https://txttovoice.com)
- **Support**: [txttovoice.com/support](https://txttovoice.com/support)
- **API Keys**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **GitHub**: [github.com/MafConquest/txt-to-voice](https://github.com/MafConquest/txt-to-voice)

---

**Made with ❤️ for productivity enthusiasts**

*Convert any text to speech in seconds - try it now!*
