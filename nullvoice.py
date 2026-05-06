import customtkinter as ctk
import sounddevice as sd
import numpy as np
import scipy.signal as signal
import threading
import time
import sys
from PIL import Image

# Configuration
SAMPLE_RATE = 44100
BLOCK_SIZE = 1024
CHANNELS = 1

class NullVoiceGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("NULLVOICE | Cybernetic Modulator")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Audio State
        self.pitch_val = 0.65  # Deep Anonymous style voice
        self.ring_val = 0      # No metallic effect
        self.bits_val = 16     # Clean audio by default
        self.gate_val = 0.005  # Lower gate for better sensitivity
        self.monitor_active = ctk.BooleanVar(value=True)
        self.is_streaming = False
        self.stream = None
        self.phi = 0
        self.current_audio_data = np.zeros(BLOCK_SIZE)

        # UI Components
        self.setup_ui()
        
    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar (Logo & Stats)
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="NULLVOICE", font=ctk.CTkFont(size=24, weight="bold", family="Orbitron"))
        self.logo_label.pack(pady=30)

        self.status_label = ctk.CTkLabel(self.sidebar, text="STATUS: STANDBY", text_color="red")
        self.status_label.pack(pady=10)

        self.start_btn = ctk.CTkButton(self.sidebar, text="INITIALIZE CORE", fg_color="green", hover_color="darkgreen", command=self.toggle_stream)
        self.start_btn.pack(pady=20, padx=20)

        self.monitor_switch = ctk.CTkSwitch(self.sidebar, text="MONITOR MODE", variable=self.monitor_active)
        self.monitor_switch.pack(pady=20)

        # Main Panel
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Device Selection
        self.device_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.device_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        
        self.input_device_var = ctk.StringVar(value="Default Input")
        self.input_menu = ctk.CTkOptionMenu(self.device_frame, values=self.get_devices("input"), variable=self.input_device_var)
        self.input_menu.pack(side="left", padx=10, expand=True, fill="x")

        self.output_device_var = ctk.StringVar(value="Default Output")
        self.output_menu = ctk.CTkOptionMenu(self.device_frame, values=self.get_devices("output"), variable=self.output_device_var)
        self.output_menu.pack(side="left", padx=10, expand=True, fill="x")

        # Visualizer Canvas
        self.canvas = ctk.CTkCanvas(self.main_frame, height=150, bg="#0a0a0a", highlightthickness=0)
        self.canvas.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Level Meter
        self.level_meter = ctk.CTkProgressBar(self.main_frame, height=10, fg_color="#1a1a1a", progress_color="cyan")
        self.level_meter.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        self.level_meter.set(0)

        # Sliders Container
        self.sliders_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.sliders_frame.grid(row=3, column=0, padx=20, pady=20, sticky="nsew")

        # Pitch Slider
        self.add_control("PITCH SHIFT", 0.5, 1.5, 0.65, self.update_pitch)
        
        # Ring Mod Slider
        self.add_control("METALLIC FREQ (Hz)", 0, 100, 0, self.update_ring)

        # Bit Depth Slider
        self.add_control("BIT DEPTH", 2, 16, 16, self.update_bits)

        # Noise Gate Slider
        self.add_control("NOISE GATE", 0.0, 0.1, 0.01, self.update_gate)

    def add_control(self, label, min_val, max_val, default, callback):
        frame = ctk.CTkFrame(self.sliders_frame, fg_color="transparent")
        frame.pack(fill="x", pady=10)
        
        lbl = ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=12, weight="bold"))
        lbl.pack(side="left", padx=10)
        
        val_lbl = ctk.CTkLabel(frame, text=f"{default:.2f}", width=50)
        val_lbl.pack(side="right", padx=10)

        slider = ctk.CTkSlider(frame, from_=min_val, to=max_val, number_of_steps=100, command=lambda v: [callback(v), val_lbl.configure(text=f"{v:.2f}")])
        slider.set(default)
        slider.pack(side="right", fill="x", expand=True, padx=20)

    def get_devices(self, kind):
        devices = sd.query_devices()
        names = []
        for i, d in enumerate(devices):
            if (kind == "input" and d["max_input_channels"] > 0) or \
               (kind == "output" and d["max_output_channels"] > 0):
                names.append(f"{i}: {d['name']}")
        return names

    def update_pitch(self, v): self.pitch_val = float(v)
    def update_ring(self, v): self.ring_val = float(v)
    def update_bits(self, v): self.bits_val = int(float(v))
    def update_gate(self, v): self.gate_val = float(v)

    def draw_visualizer(self):
        """Simple waveform visualization and level meter."""
        try:
            self.canvas.delete("all")
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            if width < 10: width = 600
            
            data = self.current_audio_data
            rms = np.sqrt(np.mean(data**2))
            self.level_meter.set(min(1.0, rms * 5)) # Boost for visibility
            
            points = []
            step = len(data) / width
            for i in range(width):
                idx = int(i * step)
                val = data[idx] if idx < len(data) else 0
                y = (height / 2) + (val * height / 2)
                points.extend([i, y])
            
            if len(points) >= 4:
                self.canvas.create_line(points, fill="#00ffff", width=2)
        except:
            pass
            
        self.after(50, self.draw_visualizer)

    def audio_callback(self, indata, outdata, frames, time_info, status):
        audio = indata[:, 0].copy()
        
        # 1. Noise Gate
        rms = np.sqrt(np.mean(audio**2))
        if rms < self.gate_val:
            audio = np.zeros_like(audio)
        
        # Update current data for visualizer
        self.current_audio_data = audio

        # 2. Time-Domain Pitch Shifting (Granular / Resampling)
        # This preserves speech clarity much better than naive FFT
        if 0.98 < self.pitch_val < 1.02:
            pass # No shift needed
        else:
            n = len(audio)
            # Create fractional indices for interpolation (stretching the wave)
            indices = np.arange(n) * self.pitch_val
            audio = np.interp(indices, np.arange(n), audio)
            
            # Apply a tiny 2ms fade in/out to smooth the block boundaries (prevents clicking)
            fade_len = int(SAMPLE_RATE * 0.002) 
            if fade_len > 0 and fade_len * 2 < n:
                fade_in = np.linspace(0, 1, fade_len)
                fade_out = np.linspace(1, 0, fade_len)
                audio[:fade_len] *= fade_in
                audio[-fade_len:] *= fade_out

        # 3. Ring Mod (Metallic effect)
        if self.ring_val > 0:
            t = (np.arange(len(audio)) + self.phi) / SAMPLE_RATE
            carrier = np.sin(2 * np.pi * self.ring_val * t)
            audio = audio * carrier
            self.phi += len(audio)

        # 4. Low-Pass Filter (Improve Intelligibility)
        # Removes high-frequency "digital fizz" from FFT artifacts
        sos = signal.butter(4, 3000, 'lp', fs=SAMPLE_RATE, output='sos')
        audio = signal.sosfilt(sos, audio)

        # 5. Bitcrush
        if self.bits_val < 16:
            q = 2**(self.bits_val - 1)
            audio = np.round(audio * q) / q

        # Limiter
        max_v = np.max(np.abs(audio))
        if max_v > 0.1: # Only normalize if there's actual sound
            if max_v > 1.0: audio /= max_v
        
        # Output
        if self.monitor_active.get():
            outdata[:, 0] = audio
        else:
            outdata.fill(0)

    def toggle_stream(self):
        if not self.is_streaming:
            try:
                # Get selected devices
                in_dev = int(self.input_device_var.get().split(":")[0]) if ":" in self.input_device_var.get() else None
                out_dev = int(self.output_device_var.get().split(":")[0]) if ":" in self.output_device_var.get() else None
                
                self.stream = sd.Stream(device=(in_dev, out_dev), channels=CHANNELS, callback=self.audio_callback,
                                      samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE)
                self.stream.start()
                self.is_streaming = True
                self.start_btn.configure(text="SHUTDOWN CORE", fg_color="red", hover_color="darkred")
                self.status_label.configure(text="STATUS: ONLINE", text_color="cyan")
            except Exception as e:
                self.status_label.configure(text=f"ERROR: {str(e)[:20]}...", text_color="orange")
                print(f"Error: {e}")
        else:
            if self.stream:
                self.stream.stop()
                self.stream.close()
            self.is_streaming = False
            self.start_btn.configure(text="INITIALIZE CORE", fg_color="green", hover_color="darkgreen")
            self.status_label.configure(text="STATUS: STANDBY", text_color="red")

if __name__ == "__main__":
    app = NullVoiceGUI()
    app.after(100, app.draw_visualizer) # Start visualizer loop
    app.mainloop()
