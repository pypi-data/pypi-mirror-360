import zipfile


def repackage_zip(input_zip_path, output_zip_path):
    # Open the original zip file in read mode
    with zipfile.ZipFile(input_zip_path, 'r') as input_zip:
        # Create a new zip file with the desired compression (deflate)
        with zipfile.ZipFile(output_zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as output_zip:
            # Iterate through each file in the original zip
            for zip_info in input_zip.infolist():
                # Extract the file's content from the original zip
                with input_zip.open(zip_info.filename) as file:
                    file_data = file.read()

                # Write the content to the new zip file using deflate compression
                output_zip.writestr(zip_info, file_data)

    print(f"Repackaging complete: {output_zip_path}")
