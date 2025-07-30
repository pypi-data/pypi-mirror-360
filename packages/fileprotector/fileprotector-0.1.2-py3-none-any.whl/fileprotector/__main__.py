import os
import sys
from PyPDF2 import PdfWriter, PdfReader
from PyPDF2.errors import FileNotDecryptedError, PdfReadError
import msoffcrypto
import subprocess


def encrypt_excel(input_path, output_path, password):
    file = open(input_path, 'rb')
    office_file = msoffcrypto.OfficeFile(file)

    with open(output_path, 'wb') as output:
        office_file.encrypt(password, output)

    file.close()


def protect_files(input_folder, output_folder, password):
    skipped_files = []
    processed_files = []

    supported_extensions = {'.pdf', '.xlsx', '.xls'}

    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in supported_extensions:
                input_path = os.path.join(root, filename)

                try:
                    rel_path = os.path.relpath(root, input_folder)
                    output_path = os.path.join(output_folder, rel_path)
                    os.makedirs(output_path, exist_ok=True)

                    if file_ext == '.pdf':
                        reader = PdfReader(input_path)
                        if reader.is_encrypted:
                            print(f"File already encrypted: {input_path}")
                            try_decrypt = input("Decrypt it to re-encrypt with new password? (y/n): ").lower()
                            if try_decrypt == 'y':
                                while True:
                                    pdf_password = input("Enter PDF password (or 'skip'): ")
                                    if pdf_password.lower() == 'skip':
                                        raise ValueError("User skipped file")
                                    try:
                                        if reader.decrypt(pdf_password):
                                            break
                                        print("Wrong password, try again")
                                    except:
                                        print("Decryption error, try again")
                            else:
                                raise ValueError("Encrypted file skipped")

                        writer = PdfWriter()
                        for page in reader.pages:
                            writer.add_page(page)
                        writer.encrypt(password)

                        output_file = os.path.join(output_path, filename)
                        with open(output_file, "wb") as f:
                            writer.write(f)

                    elif file_ext in {'.xlsx', '.xls'}:
                        output_file = os.path.join(output_path, filename)
                        encrypt_excel(input_path, output_file, password)

                    processed_files.append(input_path)
                    print(f"Encrypted: {input_path} -> {output_file}")

                except (FileNotDecryptedError, PdfReadError):
                    print(f"Skipped (PDF error): {input_path}")
                    skipped_files.append(input_path)
                except ValueError as e:
                    print(f"Skipped (user): {input_path} - {str(e)}")
                    skipped_files.append(input_path)
                except Exception as e:
                    print(f"Error: {input_path} - {str(e)}")
                    skipped_files.append(input_path)

    return processed_files, skipped_files


def main():
    if len(sys.argv) != 3:
        print("Usage: fileprotector <input_folder> <password>")
        print("Example: fileprotector '/path/to/files' Secure123")
        print("Supported: PDF (.pdf), Excel (.xlsx, .xls)")
        sys.exit(1)

    input_folder = sys.argv[1]
    password = sys.argv[2]

    folder_name = os.path.basename(input_folder)
    parent_dir = os.path.dirname(input_folder)
    output_folder = os.path.join(parent_dir, f"Protected {folder_name}")

    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' not found.")
        sys.exit(1)

    processed_files, skipped_files = protect_files(input_folder, output_folder, password)

    print("\nDone!")
    print(f"{len(processed_files)} files encrypted")
    if skipped_files:
        print(f"Skipped: {len(skipped_files)} files")
        for file in skipped_files:
            print(f"- {file}")

if __name__ == "__main__":
    main()