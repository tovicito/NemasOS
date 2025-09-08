import wave
import struct
import math
import os

def generate_wav_file(filename="nemas_webcar/assets/music/test_tone.wav", duration=3, frequency=440.0):
    """
    Generates a simple sine wave and saves it as a .wav file.
    """
    # Ensure the target directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    sample_rate = 44100.0  # Hz
    num_samples = int(sample_rate * duration)

    # WAV file parameters
    comptype = "NONE"
    compname = "not compressed"
    nchannels = 1  # Mono
    sampwidth = 2  # 16-bit

    # Open the WAV file for writing
    with wave.open(filename, 'w') as wav_file:
        wav_file.setparams((nchannels, sampwidth, int(sample_rate), num_samples, comptype, compname))

        # Generate the sine wave
        for i in range(num_samples):
            # Calculate the sample value
            value = int(32767.0 * math.sin(2 * math.pi * frequency * (i / sample_rate)))
            # Pack the value as a 16-bit signed integer
            data = struct.pack('<h', value)
            wav_file.writeframes(data)

    print(f"Successfully generated audio file: {filename}")

if __name__ == "__main__":
    generate_wav_file()
