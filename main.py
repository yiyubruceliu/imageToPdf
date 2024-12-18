import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Toplevel
from PIL import Image, ImageTk
import os

def photos_to_pdf(images, output_pdf):
    if not images:
        messagebox.showerror("Error", "No images selected!")
        return

    try:
        # Convert all images to RGB mode if needed
        rgb_images = []
        for img in images:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            rgb_images.append(img)

        # Save the PDF
        rgb_images[0].save(output_pdf, save_all=True, append_images=rgb_images[1:])
        messagebox.showinfo("Success", f"PDF saved successfully as {output_pdf}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create PDF: {e}")

class PhotoToPDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo to PDF Converter")
        
        # Create main container
        main_container = tk.Frame(root)
        main_container.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)
        
        # Left side - File list and buttons
        left_frame = tk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Listbox to display selected files
        self.file_list = Listbox(left_frame, selectmode=tk.SINGLE, width=40, height=20)
        self.file_list.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Bind selection event to preview
        self.file_list.bind('<<ListboxSelect>>', self.show_preview)
        
        # Right side - Preview
        right_frame = tk.Frame(main_container)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Preview label
        self.preview_label = tk.Label(right_frame, text="Preview")
        self.preview_label.pack()
        
        # Preview canvas
        self.preview_canvas = tk.Canvas(right_frame, width=300, height=300)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Image manipulation buttons
        manipulation_frame = tk.Frame(right_frame)
        manipulation_frame.pack(pady=5)
        
        self.rotate_left_btn = tk.Button(manipulation_frame, text="↺", command=lambda: self.rotate_image(-90))
        self.rotate_left_btn.grid(row=0, column=0, padx=2)
        
        self.rotate_right_btn = tk.Button(manipulation_frame, text="↻", command=lambda: self.rotate_image(90))
        self.rotate_right_btn.grid(row=0, column=1, padx=2)
        
        self.flip_h_btn = tk.Button(manipulation_frame, text="↔", command=lambda: self.flip_image("horizontal"))
        self.flip_h_btn.grid(row=0, column=2, padx=2)
        
        self.flip_v_btn = tk.Button(manipulation_frame, text="↕", command=lambda: self.flip_image("vertical"))
        self.flip_v_btn.grid(row=0, column=3, padx=2)
        
        self.crop_btn = tk.Button(manipulation_frame, text="Crop", command=self.start_crop)
        self.crop_btn.grid(row=0, column=4, padx=2)
        
        # Store the current preview photo and original image
        self.current_preview = None
        self.current_image = None
        self.modified_images = {}  # Store modified versions of images
        
        # Crop mode variables
        self.crop_mode = False
        self.crop_start = None
        self.crop_rect = None
        
        # Bind canvas events for cropping
        self.preview_canvas.bind('<Button-1>', self.crop_start_point)
        self.preview_canvas.bind('<B1-Motion>', self.crop_move)
        self.preview_canvas.bind('<ButtonRelease-1>', self.crop_end)

        # Buttons for actions
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack()

        self.add_btn = tk.Button(btn_frame, text="Add Photos", command=self.add_photos)
        self.add_btn.grid(row=0, column=0, padx=5, pady=5)

        self.remove_btn = tk.Button(btn_frame, text="Remove Selected", command=self.remove_selected)
        self.remove_btn.grid(row=0, column=1, padx=5, pady=5)

        self.up_btn = tk.Button(btn_frame, text="Move Up", command=self.move_up)
        self.up_btn.grid(row=0, column=2, padx=5, pady=5)

        self.down_btn = tk.Button(btn_frame, text="Move Down", command=self.move_down)
        self.down_btn.grid(row=0, column=3, padx=5, pady=5)

        self.generate_btn = tk.Button(root, text="Generate PDF", command=self.generate_pdf)
        self.generate_btn.pack(pady=10)

        self.image_files = []

    def add_photos(self):
        files = filedialog.askopenfilenames(
            title="Select Photos",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")]
        )
        for file in files:
            if file not in self.image_files:
                self.image_files.append(file)
                self.file_list.insert(tk.END, os.path.basename(file))

    def remove_selected(self):
        selected_index = self.file_list.curselection()
        if selected_index:
            index = selected_index[0]
            self.file_list.delete(index)
            self.image_files.pop(index)

    def move_up(self):
        selected_index = self.file_list.curselection()
        if selected_index:
            index = selected_index[0]
            if index > 0:
                self.image_files[index], self.image_files[index - 1] = self.image_files[index - 1], self.image_files[index]
                self.refresh_listbox()
                self.file_list.select_set(index - 1)

    def move_down(self):
        selected_index = self.file_list.curselection()
        if selected_index:
            index = selected_index[0]
            if index < len(self.image_files) - 1:
                self.image_files[index], self.image_files[index + 1] = self.image_files[index + 1], self.image_files[index]
                self.refresh_listbox()
                self.file_list.select_set(index + 1)

    def refresh_listbox(self):
        selected_index = self.file_list.curselection()
        self.file_list.delete(0, tk.END)
        for file in self.image_files:
            self.file_list.insert(tk.END, os.path.basename(file))
        if selected_index:
            self.file_list.select_set(selected_index)

    def generate_pdf(self):
        if not self.image_files:
            messagebox.showerror("Error", "No images selected!")
            return

        output_pdf = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if output_pdf:
            # Use modified images if they exist
            final_images = []
            for image_path in self.image_files:
                if image_path in self.modified_images:
                    final_images.append(self.modified_images[image_path])
                else:
                    final_images.append(Image.open(image_path))
            photos_to_pdf(final_images, output_pdf)

    def show_preview(self, event=None):
        selected_index = self.file_list.curselection()
        if not selected_index:
            return
            
        try:
            # Get selected image path
            image_path = self.image_files[selected_index[0]]
            
            # Get the image (original or modified)
            if image_path in self.modified_images:
                img = self.modified_images[image_path]
            else:
                img = Image.open(image_path)
            
            self.current_image = img  # Store the current image
            
            # Calculate aspect ratio and resize
            aspect_ratio = img.width / img.height
            
            # Get canvas dimensions
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            # Calculate new dimensions maintaining aspect ratio
            if aspect_ratio > 1:
                new_width = min(canvas_width, 300)
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = min(canvas_height, 300)
                new_width = int(new_height * aspect_ratio)
            
            # Resize image
            display_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(display_img)
            
            # Update canvas
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(
                canvas_width//2, canvas_height//2,
                image=photo,
                anchor="center"
            )
            
            # Keep a reference
            self.current_preview = photo
            
        except Exception as e:
            messagebox.showerror("Preview Error", f"Failed to load preview: {e}")

    def rotate_image(self, angle):
        selected_index = self.file_list.curselection()
        if not selected_index or not self.current_image:
            return
            
        image_path = self.image_files[selected_index[0]]
        if image_path not in self.modified_images:
            self.modified_images[image_path] = self.current_image.copy()
            
        self.modified_images[image_path] = self.modified_images[image_path].rotate(angle, expand=True)
        self.show_preview()

    def flip_image(self, direction):
        selected_index = self.file_list.curselection()
        if not selected_index or not self.current_image:
            return
            
        image_path = self.image_files[selected_index[0]]
        if image_path not in self.modified_images:
            self.modified_images[image_path] = self.current_image.copy()
            
        if direction == "horizontal":
            self.modified_images[image_path] = self.modified_images[image_path].transpose(Image.FLIP_LEFT_RIGHT)
        else:
            self.modified_images[image_path] = self.modified_images[image_path].transpose(Image.FLIP_TOP_BOTTOM)
        self.show_preview()

    def start_crop(self):
        self.crop_mode = not self.crop_mode
        self.crop_btn.config(relief=tk.SUNKEN if self.crop_mode else tk.RAISED)
        if not self.crop_mode and self.crop_rect:
            self.preview_canvas.delete(self.crop_rect)
            self.crop_rect = None

    def crop_start_point(self, event):
        if not self.crop_mode:
            return
        self.crop_start = (event.x, event.y)
        if self.crop_rect:
            self.preview_canvas.delete(self.crop_rect)
        self.crop_rect = self.preview_canvas.create_rectangle(
            event.x, event.y, event.x, event.y, outline='red'
        )

    def crop_move(self, event):
        if not self.crop_mode or not self.crop_start:
            return
        self.preview_canvas.coords(
            self.crop_rect,
            self.crop_start[0], self.crop_start[1],
            event.x, event.y
        )

    def crop_end(self, event):
        if not self.crop_mode or not self.crop_start or not self.current_image:
            return
            
        # Get canvas coordinates
        x1, y1 = self.crop_start
        x2, y2 = event.x, event.y
        
        # Get canvas dimensions
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        # Convert canvas coordinates to image coordinates
        img_width, img_height = self.current_image.size
        scale_x = img_width / canvas_width
        scale_y = img_height / canvas_height
        
        img_x1 = min(x1, x2) * scale_x
        img_y1 = min(y1, y2) * scale_y
        img_x2 = max(x1, x2) * scale_x
        img_y2 = max(y1, y2) * scale_y
        
        # Crop the image
        selected_index = self.file_list.curselection()
        if selected_index:
            image_path = self.image_files[selected_index[0]]
            if image_path not in self.modified_images:
                self.modified_images[image_path] = self.current_image.copy()
            
            self.modified_images[image_path] = self.modified_images[image_path].crop(
                (int(img_x1), int(img_y1), int(img_x2), int(img_y2))
            )
            
            self.show_preview()
            self.crop_mode = False
            self.crop_btn.config(relief=tk.RAISED)
            if self.crop_rect:
                self.preview_canvas.delete(self.crop_rect)
                self.crop_rect = None

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoToPDFApp(root)
    root.mainloop()
