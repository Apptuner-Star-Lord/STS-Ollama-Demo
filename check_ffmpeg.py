#!/usr/bin/env python3
"""
Check if FFmpeg is properly installed for audio processing
"""

import subprocess
import sys
import os

def check_ffmpeg():
    """Check if FFmpeg is installed and accessible."""
    try:
        # Try to run ffmpeg -version
        result = subprocess.run(
            ["ffmpeg", "-version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            # Extract version from output
            lines = result.stdout.split('\n')
            version_line = lines[0] if lines else "Unknown version"
            print(f"✅ FFmpeg is installed: {version_line}")
            return True
        else:
            print(f"❌ FFmpeg command failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ FFmpeg is not installed or not in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg command timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking FFmpeg: {e}")
        return False

def check_pydub_ffmpeg():
    """Check if pydub can find FFmpeg."""
    try:
        from pydub.utils import which
        ffmpeg_path = which("ffmpeg")
        if ffmpeg_path:
            print(f"✅ Pydub found FFmpeg at: {ffmpeg_path}")
            return True
        else:
            print("❌ Pydub cannot find FFmpeg")
            return False
    except ImportError:
        print("❌ Pydub is not installed")
        return False
    except Exception as e:
        print(f"❌ Error checking pydub FFmpeg: {e}")
        return False

def test_audio_conversion():
    """Test basic audio conversion functionality."""
    try:
        from pydub import AudioSegment
        import tempfile
        import os
        
        # Create a simple test audio segment
        test_audio = AudioSegment.silent(duration=1000)  # 1 second of silence
        
        # Try to export it
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            test_audio.export(temp_file.name, format="wav")
            temp_file_path = temp_file.name
        
        # Clean up
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        
        print("✅ Audio conversion test passed")
        return True
        
    except Exception as e:
        print(f"❌ Audio conversion test failed: {e}")
        return False

def main():
    """Main check function."""
    print("🔍 Checking FFmpeg Installation")
    print("=" * 40)
    
    # Check FFmpeg installation
    ffmpeg_ok = check_ffmpeg()
    
    # Check pydub FFmpeg detection
    pydub_ok = check_pydub_ffmpeg()
    
    # Test audio conversion
    conversion_ok = test_audio_conversion()
    
    print("\n" + "=" * 40)
    print("📊 Results:")
    print(f"   FFmpeg installed: {'✅' if ffmpeg_ok else '❌'}")
    print(f"   Pydub FFmpeg detection: {'✅' if pydub_ok else '❌'}")
    print(f"   Audio conversion: {'✅' if conversion_ok else '❌'}")
    
    if all([ffmpeg_ok, pydub_ok, conversion_ok]):
        print("\n🎉 FFmpeg is properly configured!")
        print("✅ Voice chat audio processing will work correctly")
    else:
        print("\n⚠️  FFmpeg needs attention:")
        if not ffmpeg_ok:
            print("   - Install FFmpeg (see FFMPEG_SETUP.md)")
        if not pydub_ok:
            print("   - Check PATH environment variable")
        if not conversion_ok:
            print("   - Restart terminal after FFmpeg installation")
        
        print("\n📚 See FFMPEG_SETUP.md for installation instructions")

if __name__ == "__main__":
    main() 