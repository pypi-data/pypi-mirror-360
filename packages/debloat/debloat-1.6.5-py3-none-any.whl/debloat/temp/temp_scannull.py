import pefile 
import sys
import mmap

def scan_rdata_for_large_null_bytes(pe_path, null_byte_threshold=0x100000, chunk_size=0x100000):
    try:
        # Load the PE file
        pe = pefile.PE(pe_path)
        
        # Find the .RDATA section
        for section in pe.sections:
            if section.Name.strip(b'\x00') == b'.rdata':
                rdata_section = section
                break
        else:
            print("No .RDATA section found.")
            return

        # Prepare to read the .RDATA section data using mmap
        rdata_va = rdata_section.VirtualAddress
        rdata_pointer = rdata_section.PointerToRawData
        rdata_size = rdata_section.SizeOfRawData

        with open(pe_path, 'rb') as f:
            mmapped_file = mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ)
            mmapped_file.seek(rdata_pointer)

            null_start = None
            null_length = 0

            offset = 0
            while offset < rdata_size:
                # Read a chunk of data
                chunk = mmapped_file.read(min(chunk_size, rdata_size - offset))
                if not chunk:
                    break

                # Scan the chunk for large null byte sequences
                for i, byte in enumerate(chunk):
                    if byte == 0:
                        if null_start is None:
                            null_start = offset + i
                        null_length += 1
                    else:
                        if null_length >= null_byte_threshold:
                            null_start_address = rdata_va + null_start
                            print(f"First null byte sequence over threshold found at address: 0x{null_start_address:08X}, size: {null_length} bytes")
                            mmapped_file.close()
                            return
                        null_start = None
                        null_length = 0

                offset += len(chunk)

            # Check the last sequence if it ended with null bytes
            if null_length >= null_byte_threshold:
                null_start_address = rdata_va + null_start
                print(f"First null byte sequence over threshold found at address: 0x{null_start_address:08X}, size: {null_length} bytes")

            mmapped_file.close()

    except pefile.PEFormatError as e:
        print(f"Error loading PE file: {e}")

def main():
    # Replace with the path to your PE file
    pe_path = sys.argv[1]
    scan_rdata_for_large_null_bytes(pe_path)

if __name__ == "__main__":
    main()