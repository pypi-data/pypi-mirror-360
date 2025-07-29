import pefile
import sys
import struct

def parse_rdata_section(file_path):
    # Load the PE file
    pe = pefile.PE(file_path)

    # Iterate through the sections to find .RDATA
    for section in pe.sections:
        if section.Name.strip(b'\x00') == b'.rdata':
            rdata_section = section
            break
    else:
        print(".RDATA section not found.")
        return

    # Get the data in the .RDATA section
    rdata_data = pe.get_data(rdata_section.VirtualAddress, rdata_section.SizeOfRawData)

    # Display some information about the .RDATA section
    print(f".RDATA Section Info:")
    print(f"  Virtual Address: 0x{rdata_section.VirtualAddress:X}")
    print(f"  Virtual Size: 0x{rdata_section.Misc_VirtualSize:X}")
    print(f"  Raw Size: 0x{rdata_section.SizeOfRawData:X}")

    # Parse the .RDATA section
    used_offsets = set()
    used_offsets.update(parse_strings(rdata_data))
    used_offsets.update(parse_import_table(pe, rdata_data))

    # Display used and unused parts of the .RDATA section
    display_summary(rdata_data, used_offsets)

def parse_strings(data):
    #print("\nStrings in .RDATA Section:")
    printable = set(bytes(range(32, 127)))
    current_string = bytearray()
    used_offsets = set()

    for i, byte in enumerate(data):
        if byte in printable:
            current_string.append(byte)
            used_offsets.add(i)
        else:
            if len(current_string) > 4:  # Only print strings longer than 4 characters
                print(current_string.decode('ascii', errors='ignore'))
            current_string = bytearray()

    return used_offsets

def parse_import_table(pe, rdata_data):
    print("\nImport Table in .RDATA Section:")
    used_offsets = set()

    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        print(f"Imported DLL: {entry.dll.decode('ascii')}")
        dll_offset = entry.struct.OriginalFirstThunk - pe.OPTIONAL_HEADER.ImageBase - pe.sections[0].Misc_VirtualSize
        used_offsets.update(range(dll_offset, dll_offset + len(entry.dll) + 1))

        for imp in entry.imports:
            if imp.name is not None:
                #print(f"  {imp.name.decode('ascii')} at 0x{imp.address:X}")
                imp_name_offset = imp.address - pe.OPTIONAL_HEADER.ImageBase - pe.sections[0].Misc_VirtualSize
                used_offsets.update(range(imp_name_offset, imp_name_offset + len(imp.name) + 1))
            
    return used_offsets

def display_summary(data, used_offsets):
    total_bytes = len(data)
    used_bytes = len(used_offsets)
    unused_bytes = total_bytes - used_bytes
    used_percentage = (used_bytes / total_bytes) * 100
    unused_percentage = (unused_bytes / total_bytes) * 100

    print("\nSummary of .RDATA Section Usage:")
    print(f"Total bytes: {total_bytes}")
    print(f"Used bytes: {used_bytes} ({used_percentage:.2f}%)")
    print(f"Unused bytes: {unused_bytes} ({unused_percentage:.2f}%)")

if __name__ == "__main__":
    file_path = sys.argv[1]  # Replace with the path to your PE file
    parse_rdata_section(file_path)
