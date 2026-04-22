import os
import numpy as np
import pydub
from time import time

def aread(f, normalized=False):
    """Audio to numpy array"""
    a = pydub.AudioSegment.from_file(f)
    y = np.array(a.get_array_of_samples())
    if a.channels == 2:
        y = y.reshape((-1, 2))
    if normalized:
        return a.frame_rate, np.float32(y) / 2**15
    else:
        return a.frame_rate, y

def get_safe_char(v):
    if v == 92: return "\\\\"
    if v == 96: return "\\`"
    if v == 10: return "\\n"
    if v == 13: return "\\r"
    if 32 <= v <= 126 or v > 160:
        return chr(v)
    return f"\\x{v:02x}"

print("--- AUDIO TO BYTEBEAT (PRO VERSION) ---")
input_mp3 = input("Enter audio file (e.g., song.mp3): ")
samplerate = int(input("Sample rate (Hz): "))
loop = input("Loop? (y/n): ") == 'y'

print("\nConverting audio format...")
# Convert whatever audio file to a temporary WAV using FFMPEG
ret = os.system(f'ffmpeg -y -hide_banner -loglevel error -i "{input_mp3}" -ac 1 -ar {samplerate} temp.wav')

if ret != 0 or not os.path.exists("temp.wav"):
    print("❌ FFMPEG FAILED — check if the file exists and ffmpeg is installed.")
    exit(1)

# Read the audio values
sr, vals = aread("temp.wav", normalized=True)
vals = ((vals + 1) / 2 * 255).astype(np.uint8)

print("Encoding to Bytebeat...")
final = ""
i = 0
start_time = time()

# Run-length encoding compression
while i < len(vals):
    current_val = vals[i]
    count = 0
    while i < len(vals) and vals[i] == current_val:
        count += 1
        i += 1
    
    char = get_safe_char(current_val)
    r_str = f"${{r(`{char}`,{count})}}"
    
    # Only use the repeat function if it actually saves space!
    if count > 1 and len(r_str) < (len(char) * count):
        final += r_str
    else:
        final += char * count

# Calculate statistics for the summary table
duration = len(vals) / samplerate
original_size = len(vals)
compressed_size = len(final)
ratio = (compressed_size / original_size) * 100

print("\n" + "="*40)
print("       BYTEBEAT CONVERSION COMPLETE      ")
print("="*40)
print(f"  Duration:        {duration:.2f} seconds")
print(f"  Original Samples: {original_size:,}")
print(f"  Final Code Size:  {compressed_size:,} bytes")
print(f"  Compression:      {ratio:.2f}% of original size")
print("="*40)

# Build the final JavaScript string
if loop:
    final_code = f"z=0,r=(b,c)=>b.repeat(c),a=`{final}`;return ((t,sr)=>{{z+=((a.charCodeAt((t*{samplerate})%a.length)/(255/2)-1)-z)/Math.max(sr/{samplerate},1);return z}})"
else:
    final_code = f"z=0,r=(b,c)=>b.repeat(c),a=`{final}`;return ((t,sr)=>{{z+=(((t*{samplerate}<a.length?a.charCodeAt(t*{samplerate})/(255/2)-1:0))-z)/Math.max(sr/{samplerate},1);return z}})"

# Save to output file
with open("output.txt", "w", encoding="utf-8") as f:
    f.write(final_code)

print(f"✅ Success! Your code is ready in output.txt (took {time()-start_time:.2f}s)")

# Clean up the temp file
if os.path.exists("temp.wav"):
    os.remove("temp.wav")
