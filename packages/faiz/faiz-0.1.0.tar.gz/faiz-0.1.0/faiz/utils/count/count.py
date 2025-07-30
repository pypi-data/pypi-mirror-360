import os
import glob

def main(args):
    if not args or args[0] not in {"*", "type"}:
        print("Usage:\n  faiz count *\n  faiz count type <pattern>")
        return

    # If they want everything in the directory
    if args[0] == "*":
        # Prepare extension-based categories
        categories = {
            "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".avif"},
            "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"},
            "Video": {".mp4", ".avi", ".mkv", ".mov", ".flv", ".wmv"},
            "Documents": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md"},
        }

        counts = {name: 0 for name in categories}
        counts["Other Files"] = 0
        folder_count = 0

        # Scan the cwd
        for entry in os.scandir():
            if entry.is_dir():
                folder_count += 1
            elif entry.is_file():
                ext = os.path.splitext(entry.name.lower())[1]
                # Find category
                for cat, exts in categories.items():
                    if ext in exts:
                        counts[cat] += 1
                        break
                else:
                    counts["Other Files"] += 1

        # Print breakdown
        print(f"📁 Folders: {folder_count}")
        for cat, num in counts.items():
            print(f"📄 {cat}: {num}")

        total_items = folder_count + sum(counts.values())
        print(f"\n🔢 Total entries (files + folders): {total_items}")

    # If they want to count by a glob pattern
    elif args[0] == "type" and len(args) > 1:
        pattern = args[1]
        matching = glob.glob(pattern)
        file_count = sum(1 for p in matching if os.path.isfile(p))
        folder_count = sum(1 for p in matching if os.path.isdir(p))
        print(f"📂 Total matching entries for '{pattern}': {len(matching)}")
        print(f"   - Files:   {file_count}")
        print(f"   - Folders: {folder_count}")
    else:
        print("❌ Invalid usage.\nUse:\n  faiz count *\n  faiz count type <pattern>")
