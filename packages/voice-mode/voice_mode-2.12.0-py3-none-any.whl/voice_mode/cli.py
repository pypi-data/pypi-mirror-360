"""
CLI entry points for voice-mode package.
"""
import sys
from .server import main as voice_mode_main

def voice_mode() -> None:
    """Entry point for voicemode command."""
    voice_mode_main()


