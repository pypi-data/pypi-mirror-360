import tts_accelerator

# Specify any supported voice from Edge TTS (e.g., en-IN-PrabhatNeural, en-GB-LibbyNeural, en-US-GuyNeural)
voice ="en-US-AvaMultilingualNeural" #You can pass any voice from edge tts.

text = (
    "Imagine reading out a 1,000-word story or a chatbot message stream — "
    "normally, you'd wait several seconds or even minutes before hearing anything. "
    "But with tts-accelerator, audio playback begins in just 2–3 seconds, "
    "no matter how long the input is. It streams audio directly from RAM, "
    "without saving to disk, and keeps the voice natural and fluid throughout. "
    "This makes it perfect for assistants, narrators, or any real-time voice-based apps."
)


tts_accelerator.speak_text(text,voice)

# PyPI Token:
# pypi-AgEIcHlwaS5vcmcCJDYyMjFkN2UxLWMwNGYtNGMyMi05ODg0LTliZTRhZjBmY2JjYgACF1sxLFsidHRzLWFjY2VsZXJhdG9yIl1dAAIsWzIsWyI5NGNmNzYyMi1hNWNkLTRlYzQtYTUzNC1iZTNiOWM2ZmYyOGUiXV0AAAYgWqM71O7M0Zq-DZl6GwEm-Bg9nGG7SP0fi_aa8yabhdk

