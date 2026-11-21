import os
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageDraw, ImageTk

PHOTO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "photos")
VALID_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
DISPLAY_SIZE = (520, 380)
THUMB_SIZE = (240, 170)

SAMPLE_SCENES = [
    ("sunset.png", (255, 140, 66), (88, 46, 120), (255, 225, 120)),
    ("ocean.png", (120, 200, 240), (10, 60, 130), (255, 255, 255)),
    ("forest.png", (170, 220, 170), (20, 90, 60), (255, 240, 160)),
]

photos = []
current_index = 0
current_image = None
details_window = None

root = tk.Tk()
root.title("Photo Album")
root.geometry("580x620")
root.resizable(False, False)

caption_var = tk.StringVar()
counter_var = tk.StringVar()


def make_scene(top, bottom, accent):
    width, height = 640, 480
    scene = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(scene)
    for y in range(height):
        ratio = y / height
        color = tuple(int(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3))
        draw.line([(0, y), (width, y)], fill=color)
    draw.ellipse([430, 60, 560, 190], fill=accent)
    draw.polygon([(0, height), (150, 290), (330, height)], fill=(25, 30, 45))
    draw.polygon([(220, height), (420, 250), (640, height)], fill=(35, 40, 60))
    return scene


def create_sample_photos():
    os.makedirs(PHOTO_DIR, exist_ok=True)
    for filename, top, bottom, accent in SAMPLE_SCENES:
        make_scene(top, bottom, accent).save(os.path.join(PHOTO_DIR, filename))


def load_photo_paths():
    if not os.path.isdir(PHOTO_DIR) or not os.listdir(PHOTO_DIR):
        create_sample_photos()
    names = sorted(os.listdir(PHOTO_DIR))
    return [
        os.path.join(PHOTO_DIR, name)
        for name in names
        if name.lower().endswith(VALID_EXTENSIONS)
    ]


def load_scaled(path, size):
    with Image.open(path) as image:
        scaled = image.convert("RGBA")
    scaled.thumbnail(size)
    return scaled


def show_photo():
    global current_image
    if not photos:
        image_label.config(image="", text="No photos in the album", fg="white")
        current_image = None
        caption_var.set("")
        counter_var.set("0 / 0")
        return

    path = photos[current_index]
    try:
        current_image = ImageTk.PhotoImage(load_scaled(path, DISPLAY_SIZE))
    except OSError:
        messagebox.showerror("Cannot open photo", f"'{os.path.basename(path)}' could not be opened.")
        photos.pop(current_index)
        fix_index()
        show_photo()
        return

    image_label.config(image=current_image, text="")
    caption_var.set(os.path.basename(path))
    counter_var.set(f"{current_index + 1} / {len(photos)}")


def fix_index():
    global current_index
    current_index = max(0, min(current_index, len(photos) - 1))


def next_photo(event=None):
    global current_index
    if photos:
        current_index = (current_index + 1) % len(photos)
        show_photo()


def previous_photo(event=None):
    global current_index
    if photos:
        current_index = (current_index - 1) % len(photos)
        show_photo()


def add_photos():
    global current_index
    selected = filedialog.askopenfilenames(
        title="Choose photos",
        filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")],
    )
    added = 0
    for path in selected:
        if path not in photos:
            photos.append(path)
            added += 1
    if added:
        current_index = len(photos) - added
        show_photo()
        messagebox.showinfo("Photos added", f"{added} photo(s) added to your album.")


def remove_photo():
    if not photos:
        messagebox.showwarning("Empty album", "There are no photos to remove.")
        return
    name = os.path.basename(photos[current_index])
    confirmed = messagebox.askyesno(
        "Remove photo",
        f"Remove '{name}' from the album?\nThe file stays on your computer.",
    )
    if confirmed:
        photos.pop(current_index)
        fix_index()
        show_photo()


def show_details():
    global details_window
    if not photos:
        messagebox.showwarning("Empty album", "Add a photo first to see its details.")
        return

    path = photos[current_index]
    with Image.open(path) as image:
        rows = [
            ("File name", os.path.basename(path)),
            ("Format", image.format),
            ("Dimensions", f"{image.width} x {image.height} px"),
            ("Color mode", image.mode),
            ("File size", f"{os.path.getsize(path) / 1024:.1f} KB"),
            ("Location", os.path.dirname(path)),
        ]
    thumbnail = ImageTk.PhotoImage(load_scaled(path, THUMB_SIZE))

    if details_window is not None and details_window.winfo_exists():
        details_window.destroy()

    details_window = tk.Toplevel(root)
    details_window.title("Photo Details")
    details_window.resizable(False, False)
    details_window.transient(root)
    details_window.thumbnail = thumbnail

    tk.Label(details_window, image=thumbnail).pack(padx=20, pady=(20, 10))

    table = tk.Frame(details_window)
    table.pack(padx=20, pady=5)
    for row_number, (label, value) in enumerate(rows):
        tk.Label(table, text=f"{label}:", font=("Helvetica", 11, "bold"), anchor="e").grid(
            row=row_number, column=0, sticky="e", padx=(0, 10), pady=2
        )
        tk.Label(table, text=value, font=("Helvetica", 11), anchor="w", wraplength=260, justify="left").grid(
            row=row_number, column=1, sticky="w", pady=2
        )

    tk.Button(details_window, text="Close", width=10, command=details_window.destroy).pack(pady=15)


tk.Label(root, text="My Photo Album", font=("Helvetica", 20, "bold")).pack(pady=(15, 10))

image_frame = tk.Frame(root, width=DISPLAY_SIZE[0] + 20, height=DISPLAY_SIZE[1] + 20, bg="#222222")
image_frame.pack_propagate(False)
image_frame.pack()

image_label = tk.Label(image_frame, bg="#222222", font=("Helvetica", 14))
image_label.pack(expand=True)

tk.Label(root, textvariable=caption_var, font=("Helvetica", 13, "bold")).pack(pady=(10, 0))
tk.Label(root, textvariable=counter_var, font=("Helvetica", 11)).pack()

buttons_frame = tk.Frame(root)
buttons_frame.pack(pady=15)

button_specs = [
    ("Previous", previous_photo),
    ("Next", next_photo),
    ("Details", show_details),
    ("Add Photos", add_photos),
    ("Remove", remove_photo),
]

for text, command in button_specs:
    tk.Button(buttons_frame, text=text, width=9, command=command).pack(side="left", padx=4)

root.bind("<Left>", previous_photo)
root.bind("<Right>", next_photo)

photos.extend(load_photo_paths())
show_photo()
root.mainloop()