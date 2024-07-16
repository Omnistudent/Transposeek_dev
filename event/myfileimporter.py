import os
import shutil

def find_and_copy_cleaned_files(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Walk through the directory structure starting from the input folder
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith("_cleaned.gbk"):
                # Define the new file name based on the parent folder of the found file
                parent_folder_name = os.path.basename(root).replace("_Curated","")
                new_file_name = f"{parent_folder_name}"
                output_file_path = os.path.join(output_folder, new_file_name)
                
                # Copy the file to the output folder with the new name
                shutil.copy(os.path.join(root, file), output_file_path)

# Replace the placeholders with your actual folder paths before running the function
input_folder_name = 'c:/Users/Eris/Documents/autothinktestfolder/collectedgenomes'  # Replace with your input folder path
output_folder_name = 'c:/Users/Eris/Documents/autothinktestfolder/newfold'  # Replace with your output folder path

# Call the function with the actual paths
find_and_copy_cleaned_files(input_folder_name, output_folder_name)