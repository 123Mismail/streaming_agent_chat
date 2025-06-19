import os
import shutil
import tkinter as tk
from tkinter import filedialog

def upload_pdf(file_path, destination_dir):
    """
    Uploads a PDF file to the specified directory.
    Creates the directory if it doesn't exist.
    
    Args:
        file_path (str): Path to the source PDF file
        destination_dir (str): Target directory path
    
    Returns:
        tuple: (bool, str) - Success status and message
    """
    try:
        # Verify if source file exists and is a PDF
        if not os.path.exists(file_path):
            return False, "Source file does not exist"
        
        if not file_path.lower().endswith('.pdf'):
            return False, "File is not a PDF"

        # Create destination directory if it doesn't exist
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
            print(f"Created directory: {destination_dir}")

        # Get the filename from the source path
        file_name = os.path.basename(file_path)
        
        # Construct destination path
        destination_path = os.path.join(destination_dir, file_name)
        
        # Copy file to destination
        shutil.copy2(file_path, destination_path)
        
        return True, f"File successfully uploaded to {destination_path}"
    
    except Exception as e:
        return False, f"Error uploading file: {str(e)}"

def select_and_upload_pdf(destination_dir):
    """
    Opens a file dialog to select a PDF file and uploads it to the destination directory.
    
    Args:
        destination_dir (str): Target directory path
    """
    # Initialize Tkinter
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Open file dialog to select a PDF file
    file_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=[("PDF files", "*.pdf")]
    )
    
    # Check if a file was selected
    if file_path:
        success, message = upload_pdf(file_path, destination_dir)
        print(message)
    else:
        print("No file selected")

if __name__ == "__main__":
    # Example destination directory
    target_dir = "project/uploads/pdfs"
    
    # Run the file selection and upload process
    select_and_upload_pdf(target_dir)