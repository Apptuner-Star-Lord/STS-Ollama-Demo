# FFmpeg Setup Guide

The voice chat application uses `pydub` for audio processing, which requires FFmpeg to be installed on your system.

## Windows Installation

### Option 1: Using Chocolatey (Recommended)
```bash
# Install Chocolatey first if you don't have it
# Then install FFmpeg
choco install ffmpeg
```

### Option 2: Manual Installation
1. Download FFmpeg from: https://ffmpeg.org/download.html#build-windows
2. Extract the archive to a folder (e.g., `C:\ffmpeg`)
3. Add the `bin` folder to your system PATH:
   - Open System Properties → Advanced → Environment Variables
   - Edit the PATH variable
   - Add `C:\ffmpeg\bin`
4. Restart your terminal/command prompt

### Option 3: Using Winget
```bash
winget install FFmpeg
```

## macOS Installation

### Using Homebrew
```bash
brew install ffmpeg
```

### Using MacPorts
```bash
sudo port install ffmpeg
```

## Linux Installation

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

### CentOS/RHEL/Fedora
```bash
# CentOS/RHEL
sudo yum install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

### Arch Linux
```bash
sudo pacman -S ffmpeg
```

## Verify Installation

After installation, verify FFmpeg is working:
```bash
ffmpeg -version
```

You should see output similar to:
```
ffmpeg version 4.4.2 Copyright (c) 2000-2021 the FFmpeg developers
...
```

## Alternative: Use Docker

If you prefer not to install FFmpeg locally, you can use the Docker setup:

```bash
docker-compose up
```

The Docker container includes FFmpeg and all necessary dependencies.

## Troubleshooting

If you still see the FFmpeg warning after installation:

1. **Restart your terminal/command prompt**
2. **Verify PATH**: `echo $PATH` (Linux/macOS) or `echo %PATH%` (Windows)
3. **Test FFmpeg**: `ffmpeg -version`
4. **Restart your Python application**

The warning is not critical - the application will still work, but audio processing may be slower or less reliable without FFmpeg. 