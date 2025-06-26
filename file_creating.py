def create_file(file_path):
    """
    Create a file at the specified path.
    
    :param file_path: The path where the file should be created.
    """
    try:
        with open(file_path, 'w') as file:
            file.write("")  # Create an empty file
        print(f"File created at: {file_path}")
    except Exception as e:
        print(f"An error occurred while creating the file: {e}")
    
try:
    create_file("example.pdf")
    print("File created successfully.")
except Exception as e:
    print(f"Failed to create file: {e}")
