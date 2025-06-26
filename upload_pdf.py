from pypdf import PdfReader, PdfWriter
from tkinter import Tk, filedialog
import os

def upload_pdf():
    """
    1. Upload a PDF from the system.
    2. Load and extract text.
    3. Append its pages into 'example.pdf' in the project directory.
    """
    root = Tk()
    root.withdraw()
    
    file_path = filedialog.askopenfilename(
        title="Select a PDF file from the system.",
        filetypes=[("PDF files", "*.pdf")],
    ) 

    if not file_path:
        print("No file selected.")
        return None 

    try:
        # Step 1: Load selected PDF
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        print(f"\nPDF file content loaded successfully:\n{text}")

        # Step 2: Write to or merge into example.pdf
        writer = PdfWriter()

        # If example.pdf exists and is valid, load its pages first
        if os.path.exists("example.pdf"):
            try:
                existing_reader = PdfReader("example.pdf")
                for page in existing_reader.pages:
                    writer.add_page(page)
                print("Existing 'example.pdf' loaded for merging.")
            except Exception as e:
                print(f"'example.pdf' exists but is not valid. Overwriting. ({e})")

        # Add new pages from selected PDF
        for page in reader.pages:
            writer.add_page(page)

        with open("example.pdf", "wb") as f:
            writer.write(f)

        print("PDF content merged and saved into 'example.pdf'.")

    except Exception as e:
        print(f"Error: {e}")
        return None

upload_pdf()
reader = PdfReader("example.pdf")
for page in reader.pages:
    print(page.extract_text() ,"extracting the text from the pdf file ")