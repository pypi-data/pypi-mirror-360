import tkinter as tk
import fitz  # PyMuPDF
from tkinter import ttk
from threading import Thread
import math
from PIL import Image, ImageTk

class tkPDFViewer(tk.Frame):
    """
    A class to display PDF documents within a Tkinter application,
    acting as a self-contained PDF viewer widget.
    """

    def __init__(self, master=None, pdf_location="", show_loading_bar=True, dpi=130, **kwargs):
        """
        Initializes the tkPDFViewer widget.

        Args:
            master (tk.Tk or tk.Frame): The parent Tkinter widget.
            pdf_location (str): The file path to the PDF document.
            show_loading_bar (bool): If True, a progress bar and message are shown during loading.
            dpi (int): Dots per inch for rendering PDF pages. Higher DPI means better quality
                       but more memory usage.
            **kwargs: Arbitrary keyword arguments to pass to the tk.Frame constructor
                      (e.g., bg, bd, relief).
        """
        super().__init__(master, **kwargs)

        self.img_object_li = []
        self.tkimg_object_li = []
        self.orig_size = 0
        self.text = None
        self.scroll_x = None
        self.scroll_y = None

        self.pdf_location = pdf_location
        self.dpi = dpi
        self.show_loading_bar = show_loading_bar

        self.percentage_load_var = tk.StringVar()
        self.display_msg_label = None
        self.loading_progressbar = None

        self._setup_ui()

    def _setup_ui(self):
        """
        Sets up the internal Tkinter UI components for displaying the PDF.
        This method is called during initialization of the tkPDFViewer instance.
        """
        self.scroll_y = ttk.Scrollbar(self, orient="vertical")
        self.scroll_x = ttk.Scrollbar(self, orient="horizontal")

        self.scroll_x.pack(fill="x", side="bottom")
        self.scroll_y.pack(fill="y", side="right")

        if self.show_loading_bar:
            self.display_msg_label = ttk.Label(self, textvariable=self.percentage_load_var)
            self.display_msg_label.pack(pady=10)

            self.loading_progressbar = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=100, mode='determinate')
            self.loading_progressbar.pack(side=tk.TOP, fill=tk.X)

        self.text = tk.Text(self, yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set, wrap="none")
        self.text.config(bg="grey")
        self.text.pack(expand=True, fill="both")

        self.scroll_x.config(command=self.text.xview)
        self.scroll_y.config(command=self.text.yview)

        if self.pdf_location:
            self._start_pdf_loading_thread()

    def display_pdf(self, pdf_location):
        self.pdf_location = pdf_location
        self._start_pdf_loading_thread()

    def _start_pdf_loading_thread(self):
        Thread(target=self._load_pdf_pages, daemon=True).start()

    def _load_pdf_pages(self):
        """
        Loads PDF pages as images and inserts them into the Tkinter Text widget.
        This method runs in a separate thread to prevent UI freezing.
        """
        try:
            open_pdf = fitz.open(self.pdf_location)
            total_pages = len(open_pdf)

            self.img_object_li.clear()
            self.tkimg_object_li.clear()

            for i, page in enumerate(open_pdf):
                pix = page.get_pixmap(dpi=self.dpi)
                mode = "RGBA" if pix.alpha else "RGB"
                img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
                self.img_object_li.append(img)

                self.tkimg_object_li.append(ImageTk.PhotoImage(img))

                if self.show_loading_bar:
                    percentage_view = (float(i + 1) / float(total_pages) * float(100))
                    self.after(0, self._update_loading_progress, percentage_view)

            if self.tkimg_object_li:
                self.orig_size = self.tkimg_object_li[0].width()

            self.after(0, self._display_images_in_text_widget)

        except Exception as e:
            print(f"Error loading PDF: {e}")
            if self.display_msg_label:
                self.after(0, self.percentage_load_var.set, f"Error loading PDF: {e}")

    def _update_loading_progress(self, percentage):
        """Updates the loading progress bar and message on the main thread."""
        if self.loading_progressbar:
            self.loading_progressbar['value'] = percentage
        if self.display_msg_label:
            self.percentage_load_var.set(f"Loading {int(math.floor(percentage))}%")

    def _display_images_in_text_widget(self):
        """
        Inserts all loaded PhotoImage objects into the Text widget.
        This must be called on the main Tkinter thread.
        """
        if self.loading_progressbar:
            self.loading_progressbar.pack_forget()
        if self.display_msg_label:
            self.display_msg_label.pack_forget()

        self.text.configure(state="normal")
        self.text.delete(1.0, tk.END)

        for im in self.tkimg_object_li:
            self.text.image_create(tk.END, image=im)
            self.text.insert(tk.END, "\n\n")

        self.text.configure(state="disabled")

# Example Usage:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("PDF Viewer Example")
    root.geometry("1120x700")

    dummy_pdf_path = "dummy_example.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "This is a dummy PDF for testing.", fontname="helv", fontsize=24)
    page = doc.new_page()
    page.insert_text((50, 50), "new page !", fontname="helv", fontsize=24)
    doc.save(dummy_pdf_path)
    doc.close()
    print(f"Created a dummy PDF at: {dummy_pdf_path}")

    pdf_viewer = tkPDFViewer(root, pdf_location=dummy_pdf_path, bg="white", relief="sunken", bd=2)
    pdf_viewer.pack(expand=True, fill="both", padx=10, pady=10)

    root.mainloop()
