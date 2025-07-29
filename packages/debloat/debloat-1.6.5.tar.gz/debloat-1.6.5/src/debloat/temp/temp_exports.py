import sys
import pefile

def modify_pe(file_path):
    # Load the PE file with fast_load=True
    pe = pefile.PE(file_path, fast_load=True)

    # Manually parse the Export Directory
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']])

    # Check if the PE file has an export directory
    if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
        export_directory = pe.DIRECTORY_ENTRY_EXPORT

        # Print current export entries
        for exp in export_directory.symbols:
            print(f"Name: {exp.name}, Address: {hex(exp.address)}")

            # Example modification: change the address of an export entry
            # exp.address = new_address  # Uncomment and set new_address to the desired value

        # Write the modified PE file
        modified_file_path = file_path + "_modified"
        pe.write(modified_file_path)
        print(f"Modified PE file written to {modified_file_path}")
    else:
        print("No export directory found in the PE file.")

    # Close the PE file
    pe.close()

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path_to_pe_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    modify_pe(file_path)

if __name__ == "__main__":
    main()
