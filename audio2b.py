import os
import numpy as np
import pydub
from time import time

def aread(f, normalized=False):
    a = pydub.AudioSegment.from_file(f)
    y = np.array(a.get_array_of_samples())
    if a.channels == 2: y = y.reshape((-1, 2)).mean(axis=1)
    if normalized:
        return a.frame_rate, np.float32(y) / 2**15
    return a.frame_rate, y

def get_safe_char(v):
    if v == 92: return "\\\\"
    if v == 96: return "\\`"
    if v == 10: return "\\n"
    if v == 13: return "\\r"
    if 32 <= v <= 126 or v > 160: return chr(v)
    return f"\\x{v:02x}"

print("--- PRO AUDIO TO BYTEBEAT CONVERTER ---")
input_file = input("Enter source file (e.g., input.mp3): ")
sr_target = int(input("Target Sample Rate (Hz): "))
loop = input("Loop audio? (y/n): ") == 'y'

# Initial Conversion
print("Running FFMPEG...")
os.system(f'ffmpeg -y -hide_banner -loglevel error -i "{input_file}" -ac 1 -ar {sr_target} temp.wav')

sr, vals = aread("temp.wav", normalized=True)
vals = ((vals + 1) / 2 * 255).astype(np.uint8)

print("Encoding samples...")
final = "".join([get_safe_char(v) for v in vals])

# The output function string
if loop:
    output = f"z=0,r=(b,c)=>b.repeat(c),a=`{final}`;return ((t,sr)=>{{z+=((a.charCodeAt((t*{sr_target})%a.length)/(255/2)-1)-z)/Math.max(sr/{sr_target},1);return z}})"
else:
    output = f"z=0,r=(b,c)=>b.repeat(c),a=`{final}`;return ((t,sr)=>{{z+=(((t*{sr_target}<a.length?a.charCodeAt(t*{sr_target})/(255/2)-1:0))-z)/Math.max(sr/{sr_target},1);return z}})"

# Finalizing
with open("output.txt", "w", encoding="utf-8") as f:
    f.write(output)

# --- Summary Table ---
duration = len(vals) / sr_target
print("\n" + "="*35)
print("      CONVERSION SUMMARY")
print("="*35)
print(f" Duration:     {duration:.2f}s")
print(f" Sample Count: {len(vals):,}")
print(f" Final Size:   {len(output):,} bytes")
print("="*35)
print("✅ Success! Check output.txt")

if os.path.exists("temp.wav"): os.remove("temp.wav")
