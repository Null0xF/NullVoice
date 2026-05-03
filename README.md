# 🎙️ NullVoice
**Cybernetic Real-Time Voice Modulator**

NullVoice is a professional-grade Python utility designed to modulate your voice in real-time, creating a "hacker" or "cybernetic" aesthetic. It uses low-latency digital signal processing (DSP) to apply pitch shifting, ring modulation, and bitcrushing effects.

---

## 🚀 Features
- **Pitch Shifting**: Deepen or sharpen your voice (default is deep/anonymous).
- **Ring Modulation**: Adds a metallic, robotic texture to the audio signal.
- **Bitcrushing**: Simulates vintage digital distortion for a lo-fi "encrypted" feel.
- **Noise Gate**: Automatically filters out background static and silence.
- **HUD Interface**: A professional terminal dashboard showing system status.

## 🛠️ Installation

1. **Install Dependencies**:
   Ensure you have Python 3.8+ installed. Run:
   ```bash
   pip install -r requirements.txt
   ```

2. **System Requirements**:
   - On Windows: No additional drivers usually needed.
   - On Linux: May require `libportaudio2`.

## 🎮 Usage

Per lanciare l'interfaccia grafica:
```bash
python nullvoice.py
```
Dal pannello potrai selezionare il microfono, regolare gli effetti in tempo reale e attivare il **MONITOR MODE** per ascoltarti.

### Customization (GUI)
Dal pannello potrai regolare:

| Controllo | Effetto | Suggerito |
|------|-------------|---------|
| **PITCH SHIFT** | Rende la voce profonda o acuta | `0.85` (Profonda/Anonima) |
| **METALLIC FREQ** | Aggiunge una risonanza robotica | `15 Hz` (Sottile) |
| **BIT DEPTH** | Distorce il suono stile radio vecchia | `16` (Pulito) |
| **NOISE GATE** | Taglia il rumore di fondo | `0.005` |

**Example (Extremely Deep & Robotic):**
```bash
python nullvoice.py --pitch 0.5 --ring 60 --bits 4
```

## ⚠️ Troubleshooting
- **Latenza (Delay)**: If you experience delay, try reducing the `BLOCK_SIZE` in the code, though this may cause audio glitches.
- **Feedback Loop**: Ensure you are using headphones. Using speakers will create a loud feedback loop as the microphone picks up the modulated audio.

---
*Developed for PROGETTOCYB | Part of the Null Security Suite.*
