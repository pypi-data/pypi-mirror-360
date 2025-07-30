from PIL import Image, ExifTags
import pillow_heif
import os
import sys
import glob
import time
import signal
import threading
from concurrent.futures import ThreadPoolExecutor

# Enable HEIC support
pillow_heif.register_heif_opener()

OUTPUT_DIR = "converted_webp"

# Shared Stats
stats = {
    "total_images": 0,
    "converted": 0,
    "failed": 0,
    "total_input_size": 0,
    "total_output_size": 0,
    "start_time": None
}
lock = threading.Lock()
progress = {"current": 0}
should_stop = False

def format_size(bytes_size):
    return f"{bytes_size / (1024 * 1024):.2f} MB" if bytes_size > 1024 * 1024 else f"{bytes_size / 1024:.2f} KB"

def signal_handler(sig, frame):
    global should_stop
    should_stop = True
    print("\n🛑 Interrupted! Finalizing...\n")
    print_summary()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def convert_to_webp(input_path, output_path=None, batch_mode=False, total=None):
    global stats, should_stop

    if should_stop:
        return

    try:
        input_size = os.path.getsize(input_path)

        with Image.open(input_path) as img:
            try:
                for orientation_tag in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation_tag] == 'Orientation':
                        break
                exif = img._getexif()
                if exif is not None:
                    orientation = exif.get(orientation_tag, None)
                    if orientation == 3:
                        img = img.rotate(180, expand=True)
                    elif orientation == 6:
                        img = img.rotate(270, expand=True)
                    elif orientation == 8:
                        img = img.rotate(90, expand=True)
            except Exception:
                pass

            base_name = os.path.splitext(os.path.basename(input_path))[0]
            if output_path is None:
                output_path = os.path.join(OUTPUT_DIR if batch_mode else os.path.dirname(input_path), base_name + ".webp")

            img.convert("RGB").save(output_path, "WEBP")
            output_size = os.path.getsize(output_path)

            with lock:
                stats["converted"] += 1
                stats["total_input_size"] += input_size
                stats["total_output_size"] += output_size
                progress["current"] += 1
                idx = progress["current"]

            reduction = 100 * (input_size - output_size) / input_size if input_size else 0

            print(f"[{idx}/{total}] ✅ {os.path.basename(input_path)}")
            print(f"    ⏹ Before:  {format_size(input_size)}")
            print(f"    🟢 After:   {format_size(output_size)}")
            print(f"    📉 Reduced: {reduction:.2f}%\n")

    except Exception as e:
        with lock:
            stats["failed"] += 1
            progress["current"] += 1
            idx = progress["current"]

        print(f"[{idx}/{total}] ❌ Error converting {input_path}: {e}")

def process_images(image_files):
    stats["start_time"] = time.time()
    stats["total_images"] = len(image_files)
    ensure_output_dir()

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(convert_to_webp, img, batch_mode=True, total=len(image_files)) for img in image_files]

        for future in futures:
            future.result()  # Wait for all threads to finish


def print_summary():
    total_time = time.time() - stats["start_time"]
    converted = stats["converted"]
    in_size = stats["total_input_size"]
    out_size = stats["total_output_size"]

    avg_in = in_size / converted if converted else 0
    avg_out = out_size / converted if converted else 0
    total_saved = in_size - out_size
    avg_reduction = 100 * (avg_in - avg_out) / avg_in if avg_in else 0

    print("\n📊 Conversion Summary")
    print("=" * 40)
    print(f"🖼️  Total Images:       {stats['total_images']}")
    print(f"✅ Converted:          {converted}")
    print(f"❌ Failed:             {stats['failed']}")
    print(f"⏱️  Time Taken:         {total_time:.2f} seconds")

    if converted:
        print(f"\n📦 Size Info:")
        print(f"📥 Total Before:       {format_size(in_size)}")
        print(f"📤 Total After:        {format_size(out_size)}")
        print(f"📉 Total Saved:        {format_size(total_saved)}")
        print(f"⚖️  Avg Before:         {format_size(avg_in)}")
        print(f"⚖️  Avg After:          {format_size(avg_out)}")
        print(f"🔻 Avg Reduction:       {avg_reduction:.2f}%")
    print("=" * 40)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_heic_to_webp.py <image_path_or_glob_pattern>")
    else:
        pattern = sys.argv[1]
        if "*" in pattern:
            images = glob.glob(pattern)
            if not images:
                print("❌ No matching files found.")
            else:
                print(f"🔄 Found {len(images)} image(s). Starting conversion...\n")
                process_images(images)
        else:
            img_path = pattern
            out_path = sys.argv[2] if len(sys.argv) > 2 else None
            stats["start_time"] = time.time()
            stats["total_images"] = 1
            convert_to_webp(img_path, out_path, batch_mode=False, total=1)
        print_summary()
