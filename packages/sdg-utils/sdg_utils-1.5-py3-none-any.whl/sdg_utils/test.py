from sdg_utils import dump_bits, nums2bits
from sdg_utils import get_comports

if __name__ == '__main__':
    # print(dump_bits(0x0001))
    # print(dump_bits(0x8000))
    # print(dump_bits(0x8080))
    # print(bin(nums2bits(1, 2, 3, 4)))
    # print(bin(nums2bits(1, 2, 3, 4, shift=-1)))

    for p, d, i in get_comports():
        print(f"{p:7} {d:55} {i}")

    print("\n----get_comports(id_list='0483:3752'")
    for p, d, i in get_comports(vidpid='0483:3752'):
        print(f"{p:7} {d:55} {i}")

    print("\n----get_comports(id_list=('0483:3752', '0403:6001')")
    for p, d, i in get_comports(vidpid=('0483:3752', '0403:6001')):
        print(f"{p:7} {d:55} {i}")
