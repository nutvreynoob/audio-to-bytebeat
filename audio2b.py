import os
import numpy as np
import pydub
from time import time

def aread(f, normalized=False):
    a = pydub.AudioSegment.from_file(f)
    y = np.array(a.get_array_of_samples())
    if a.channels == 2: y = y.reshape((-1, 2)).mean(axis=1) # Mono conversion
    if normalized:
        return a.frame_rate, np.float32(y) / 2**15
    return a.frame_rate, y

def get_safe_char(v):
    if v == 92: return "\\\\"
    if v == 96: return "\\`"
    return chr(v) if (32 <= v <= 126) else f"\\x{v:02x}"

print("--- OFFLINE AUDIO TO BYTEBEAT ---")
input_file = input("Enter audio filename: ")
sr_target = int(input("Target Sample Rate (Hz): "))

# Temp conversion via ffmpeg
os.system(f'ffmpeg -y -loglevel error -i "{input_file}" -ac 1 -ar {sr_target} temp.wav')

sr, vals = aread("temp.wav", normalized=True)
vals = ((vals + 1) / 2 * 255).astype(np.uint8)

print("Processing...")
final = "".join([get_safe_char(v) for v in vals])

# The output template
template = "z=0,a=`{}`;return ((t,sr)=>{{z+=((a.charCodeAt((t*{})%a.length)/(255/2)-1)-z)/Math.max(sr/{},1);return z}})"
output_code = template.format(final, sr_target, sr_target)

with open("output.txt", "w", encoding="utf-8") as f:
    f.write(output_code)

print("\n" + "="*30)
print(f"DONE: {len(vals)} samples converted.")
print(f"Output saved to output.txt")
print("="*30)

if os.path.exists("temp.wav"): os.remove("temp.wav")
