# This code is the property of Mantra Information Security and is provided 
# solely for use within the x86/x64 Reverse Engineering training course or
# one of its related workshops.
# It is confidential and proprietary information and should not be distributed
# or shared with anyone else. Any unauthorized distribution, reproduction, 
# or use of this code is strictly prohibited.
#
# Mantra Information Security
# https://mantrainfosec.com
#

from unicorn import *
from unicorn.x86_const import *
import struct

def hook_block(uc, address, size, user_data):
    print(">>> Tracing block at 0x%x, instruction size = 0x%x" %(address, size))
    rip = uc.reg_read(UC_X86_REG_RIP)
    print(">>> RIP is 0x%x" %rip);

def hook_code(uc, address, size, user_data):
    print(">>> Tracing instruction at 0x%x, instruction size = 0x%x" %(address, size))
    rip = uc.reg_read(UC_X86_REG_RIP)
    print(">>> RIP is 0x%x" %rip);
#    print(">>> EAX is 0x%x" %uc.reg_read(UC_X86_REG_RAX));

def hook_mem_access(uc, access, address, size, value, user_data):
    if access == UC_MEM_WRITE:
        print(">>> Memory is being WRITE at 0x%x, data size = %u, data value = 0x%x" \
                %(address, size, value))
    else:   # READ
        print(">>> Memory is being READ at 0x%x, data size = %u" \
                %(address, size))

# Read the ELF binary
with open("02cipher", "rb") as f:
    binary = f.read()

# Set the memory address where the code will be loaded (base address)
BINARY = 0x100000
STACK = 0x300000
HEAP = 0x400000

# Create an instance of the Unicorn Engine emulating x64
uc = Uc(UC_ARCH_X86, UC_MODE_64)

# Map memory for the code
uc.mem_map(BINARY, 2 * 1024 * 1024)  # 2 MB
uc.mem_map(STACK, 1024 * 1024)  # 1 MB
uc.mem_map(HEAP, 1024 * 1024)  # 1 MB

# Write the ELF binary to the memory
uc.mem_write(BINARY, binary)

# Set the string and offset values in memory
input_str = b"Hello this is NOT the secret message."
uc.mem_write(HEAP, input_str)  # Address where input_str is stored (binary 16K, string at 17K)
uc.reg_write(UC_X86_REG_RDI, HEAP)  # Set the first argument (address of the string)

uc.reg_write(UC_X86_REG_RSP, STACK + 512)  # Set the stack if needed

#uc.hook_add(UC_HOOK_CODE, hook_code, None, BINARY, BINARY + (3*1024*1024))
#uc.hook_add(UC_HOOK_MEM_READ, hook_mem_access)

# Emulate code execution
try:
    uc.emu_start(BINARY + 0x119a, BINARY + 0x12b4)  # Address of the call

    # Read the result from memory (assuming the C program prints the result)
    result = uc.mem_read(HEAP, len(input_str)).decode("utf-8")
    print(f"Deciphered string: {result}")

except UcError as e:
    print("Error: %s" % e)