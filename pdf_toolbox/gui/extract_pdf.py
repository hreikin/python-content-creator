from utilities import constants
from gui import scroll_frame

import fitz
from tkinter import *
from tkinter import font, filedialog, messagebox

class ExtractPDF(Frame):
    """Create a subclass of Frame for our window element to display PDF files."""
    def __init__(self, master=None):
        """Initialize and set the font."""
        Frame.__init__(self, master)
        self.master = master
        self.myfont = font.Font(family="Ubuntu", size=16)
        self.zoom = False
        self.zoom_on = False
        self.init_window()

    def init_window(self):
        """Construct the layout"""
        self.pw = PanedWindow(self.master, sashrelief="raised", sashwidth=10)

        self.extract_options = Frame(self.pw)

        self.scrapy_download = Frame(self.extract_options, relief="groove", borderwidth=5)
        self.scrapy_some_text = Label(self.scrapy_download, text="This is the Scrapy options area.")
        self.scrapy_some_text.pack(fill="x", expand=1)
        self.scrapy_download.pack(fill="both", expand=1)

        self.adobe_api = Frame(self.extract_options, relief="groove", borderwidth=5)
        self.adobe_some_text = Label(self.adobe_api, text="This is the Adobe options area.")
        self.adobe_some_text.pack(fill="x", expand=1)
        self.adobe_api.pack(fill="both", expand=1)

        self.pymupdf_extract = Frame(self.extract_options, relief="groove", borderwidth=5)
        self.pymupdf_some_text = Label(self.pymupdf_extract, text="This is the PyMuPDF options area.")
        self.pymupdf_some_text.pack(fill="x", expand=1)
        self.pymupdf_extract.pack(fill="both", expand=1)

        self.ocr_extract = Frame(self.extract_options, relief="groove", borderwidth=5)
        self.ocr_some_text = Label(self.ocr_extract, text="This is the OCR options area.")
        self.ocr_some_text.pack(fill="x", expand=1)
        self.ocr_extract.pack(fill="both", expand=1)

        self.preview_area = Frame(self.pw)

        self.top_bar = Frame(self.preview_area, relief="groove", borderwidth=5)
        self.open_btn = Button(self.top_bar, text="Open", command=self.open_extract)
        self.open_btn.pack(side="left", padx=0, pady=0)
        self.next_btn = Button(self.top_bar, text="Next", state="disabled", command=self.next_page)
        self.next_btn.pack(side="left", padx=0, pady=0)
        self.prev_btn = Button(self.top_bar, text="Prev", state="disabled", command=self.prev_page)
        self.prev_btn.pack(side="left", padx=0, pady=0)
        self.zoom_btn = Button(self.top_bar, text="Zoom", state="disabled", command=self.toggle_zoom)
        self.zoom_btn.pack(side="left", padx=0, pady=0)
        self.top_bar.pack(side="top", fill="x")

        self.pdf_preview = scroll_frame.ScrollFrame(self.preview_area, relief="groove", borderwidth=5)
        self.pdf_page_img = Label(self.pdf_preview.view_port, text="Open a PDF to view or manually extract content.", image=None, pady=150)
        self.pdf_page_img.pack(side="left", fill="both", expand=1)
        self.pdf_preview.pack(side="bottom", fill="both", expand=1)

        self.pw.add(self.extract_options)
        self.pw.add(self.preview_area)
        self.pw.pack(fill="both", expand=True)

# ------------------------------------------------------------------------------
# Open the PDF file to view/edit/extract from.
# ------------------------------------------------------------------------------
    def open_extract(self):
        self.fname = filedialog.askopenfile(
            title="PDF Toolbox Document Browser", 
            initialdir=constants.pdf_dir, 
            filetypes=(
                ("PDF Files", "*.pdf"), 
                ("XPS Files", "*.*xps"), 
                ("Epub Files", "*.epub"), 
                ("Fiction Books", "*.fb2"), 
                ("Comic Books", "*.cbz"), 
                ("HTML", "*.htm*")
                )
            )
        if not self.fname:
            messagebox.showerror(title="Cancelling.", message="No file chosen.")
            return
        self.doc = fitz.open(self.fname)
        self.page_count = len(self.doc)
        # Allocate storage for page display lists.
        self.dlist_tab = [None] * self.page_count
        # self.title = f"PyMuPDF display of {self.fname}, pages: {self.page_count}"
        self.max_width = self.pdf_preview.winfo_screenwidth() - 20
        self.max_height = self.pdf_preview.winfo_screenheight() - 150
        self.max_size = (self.max_width, self.max_height)
        # self.zoom_on = False
        self.cur_page = 0
        if self.zoom_on == False:
            self.data, self.clip_pos = self.get_page(
                self.cur_page,
                max_size=self.max_size
                )
        elif self.zoom_on == True:
            self.data, self.clip_pos = self.get_page(
                self.cur_page,
                max_size=self.zoom_max_size
                )
        self.pdf_page_data = PhotoImage(data=self.data)
        self.pdf_page_img.configure(image=self.pdf_page_data, text=None)
        self.next_btn.configure(state="normal")
        self.prev_btn.configure(state="normal")
        self.zoom_btn.configure(state="normal")

# ------------------------------------------------------------------------------
# Read the page data.
# ------------------------------------------------------------------------------
    def get_page(self, pno, max_size=None):
        """Return a tkinter.PhotoImage or a PNG image for a document page number.
        :arg int pno: 0-based page number
        :arg zoom: top-left of old clip rect, and one of -1, 0, +1 for dim. x or y
                to indicate the arrow key pressed
        :arg max_size: (width, height) of available image area
        :arg bool first: if True, we cannot use tkinter
        """
        self.dlist = self.dlist_tab[pno]  # get display list of page number
        if not self.dlist:  # create if not yet there
            self.dlist_tab[pno] = self.doc[pno].get_displaylist()
            self.dlist = self.dlist_tab[pno]
        self.r = self.dlist.rect  # the page rectangle
        self.clip = self.r
        # ensure image fits screen:
        # exploit, but do not exceed width or height
        self.zoom_0 = 1
        if max_size:
            self.zoom_0 = min(1, max_size[0] / self.r.width, max_size[1] / self.r.height)
            if self.zoom_0 == 1:
                self.zoom_0 = min(max_size[0] / self.r.width, max_size[1] / self.r.height)
        self.mat_0 = fitz.Matrix(self.zoom_0, self.zoom_0)
        self.pix = self.dlist.get_pixmap(matrix=self.mat_0, alpha=False)
        self.img = self.pix.tobytes("ppm")  # make PPM image from pixmap for tkinter
        return self.img, self.clip.tl  # return image, clip position

    def next_page(self):
        self.cur_page += 1
        # sanitize page number
        while self.cur_page >= self.page_count:  # wrap around
            self.cur_page -= self.page_count
        while self.cur_page < 0:  # pages < 0 are valid but look bad
            self.cur_page += self.page_count
        # self.zoom = False
        if self.zoom_on == False:
            self.data, self.clip_pos = self.get_page(
                self.cur_page,
                max_size=self.max_size
                )
        elif self.zoom_on == True:
            self.data, self.clip_pos = self.get_page(
                self.cur_page,
                max_size=self.zoom_max_size
                )
        self.pdf_page_data = PhotoImage(data=self.data)
        self.pdf_page_img.configure(image=self.pdf_page_data, text=None)

    def prev_page(self):
        self.cur_page -= 1
        # sanitize page number
        while self.cur_page >= self.page_count:  # wrap around
            self.cur_page -= self.page_count
        while self.cur_page < 0:  # pages < 0 are valid but look bad
            self.cur_page += self.page_count
        # self.zoom = False
        if self.zoom_on == False:
            self.data, self.clip_pos = self.get_page(
                self.cur_page,
                max_size=self.max_size
                )
        elif self.zoom_on == True:
            self.data, self.clip_pos = self.get_page(
                self.cur_page,
                max_size=self.zoom_max_size
                )
        self.pdf_page_data = PhotoImage(data=self.data)
        self.pdf_page_img.configure(image=self.pdf_page_data, text=None)

    def toggle_zoom(self):
        if self.zoom_on == False:
            self.zoom_on = True
            # self.zoom = (self.clip.tl, 0, 0)
            self.zoom_width = self.max_width * 2
            self.zoom_height = self.max_height * 2
            self.zoom_max_size = (self.zoom_width, self.zoom_height)
            self.data, self.clip_pos = self.get_page(
                self.cur_page,
                max_size=self.zoom_max_size
                )
        elif self.zoom_on == True:
            self.zoom_on = False
            self.data, self.clip_pos = self.get_page(
                self.cur_page,
                max_size=self.max_size
                )
        self.pdf_page_data = PhotoImage(data=self.data)
        self.pdf_page_img.configure(image=self.pdf_page_data, text=None)

# ------------------------------------------------------------------------------
# Run standalone.
# ------------------------------------------------------------------------------

# mainwindow = Tk()
# preview = ExtractPDF(mainwindow)
# preview.mainloop()