# Copyright Pololu Corporation.  For more information, see https://www.pololu.com/
# This example tests the speed of reads and writes to the slave device.


import os, sys, timeit

# For being able to import files from ./../src/ and run it from anywhere in the system of the RPi (useful for run.sh)
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(script_dir, "../src"))
sys.path.append(src_path)
from balboa import Balboa


rocky = Balboa()
n = 500
total_time = timeit.timeit(rocky.test_write8, number=n)
write_kbits_per_second = 8 * n * 8 / total_time / 1000

print("Writes of 8 bytes: "+'%.1f'%write_kbits_per_second+" kilobits/second")

n = 500
total_time = timeit.timeit(rocky.test_read8, number=n)
read_kbits_per_second = 8 * n * 8 / total_time / 1000

print("Reads of 8 bytes: "+'%.1f'%read_kbits_per_second+" kilobits/second")
