import streamlit as st
import os
import re
import json
from pathlib import Path

# Supported image extensions
ALL_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"]
UNDO_LOG = ".undo_log.json"

def get_next_index(prefix, files):
    pattern = re.compile(rf"^{re.escape(prefix)}_(\d+)")
    max_index = -1
    for file in files:
        match = pattern.match(file.stem)
        if match:
            idx = int(match.group(1))
            if idx > max_index:
                max_index = idx
    return max_index + 1

def rename_images(folder_path, prefix, skip_prefix, selected_exts):
    folder = Path(folder_path)
    image_files = sorted([
        f for f in folder.iterdir()
        if f.suffix.lower() in selected_exts and f.is_file()
    ])

    if not image_files:
        return "No image files found in the selected folder.", []

    existing_files = [f for f in image_files if f.stem.startswith(prefix + "_")]
    start_index = get_next_index(prefix, existing_files)

    renamed_files = []
    for file in image_files:
        if skip_prefix and file.stem.startswith(skip_prefix):
            continue
        if file.stem.startswith(prefix + "_"):
            continue

        new_name = f"{prefix}_{start_index}{file.suffix.lower()}"
        new_path = folder / new_name

        if new_path.exists():
            continue  # skip if destination already exists

        file.rename(new_path)
        renamed_files.append((new_name, file.name))
        start_index += 1

    # Save undo log
    if renamed_files:
        with open(folder / UNDO_LOG, "w") as f:
            json.dump(renamed_files, f)

    return f"Renamed {len(renamed_files)} image(s).", [(old, new) for new, old in renamed_files]

def undo_last_rename(folder_path):
    folder = Path(folder_path)
    undo_file = folder / UNDO_LOG
    if not undo_file.exists():
        return "No undo history found."

    with open(undo_file, "r") as f:
        rename_pairs = json.load(f)

    restored_count = 0
    for current_name, original_name in reversed(rename_pairs):
        current_path = folder / current_name
        original_path = folder / original_name

        if current_path.exists() and not original_path.exists():
            current_path.rename(original_path)
            restored_count += 1

    undo_file.unlink(missing_ok=True)
    return f"Restored {restored_count} file(s) to original names."

# --- Streamlit UI ---
st.set_page_config(page_title="File Control", layout="centered")
st.title("🖼️ Advanced File Control")

folder_path = st.text_input("📁 Folder path:")

col1, col2 = st.columns(2)
with col1:
    prefix = st.text_input("New prefix:")
with col2:
    skip_prefix = st.text_input("Skip prefix (optional):")

# File extension filters
with st.expander("⚙️ File Type Filters"):
    selected_exts = []
    cols = st.columns(3)
    for i, ext in enumerate(ALL_EXTENSIONS):
        with cols[i % 3]:
            if st.checkbox(ext, value=True):
                selected_exts.append(ext)

# Preview and rename
if st.button("🔄 Preview and Rename"):
    if not folder_path or not prefix:
        st.warning("Please enter both folder path and prefix.")
    elif not os.path.isdir(folder_path):
        st.error("Invalid folder path.")
    elif not selected_exts:
        st.warning("Please select at least one file type.")
    else:
        message, renamed_files = rename_images(folder_path, prefix, skip_prefix, selected_exts)
        st.success(message)
        if renamed_files:
            st.subheader("📝 Renamed Files")
            st.table([{"Old": old, "New": new} for old, new in renamed_files])

# Undo button
if st.button("⏪ Undo Last Rename"):
    if not folder_path or not os.path.isdir(folder_path):
        st.error("Enter a valid folder path to undo.")
    else:
        msg = undo_last_rename(folder_path)
        st.success(msg)
