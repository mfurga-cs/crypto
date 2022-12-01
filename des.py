#!/usr/bin/env python3
#
# Data Encryption Standard (DES).
#

import random
from bitarray import Bitarray
from typing import List

# Initial permutation.
IP = [
  57, 49, 41, 33, 25, 17,  9,  1,
  59, 51, 43, 35, 27, 19, 11,  3,
  61, 53, 45, 37, 29, 21, 13,  5,
  63, 55, 47, 39, 31, 23, 15,  7,
  56, 48, 40, 32, 24, 16,  8,  0,
  58, 50, 42, 34, 26, 18, 10,  2,
  60, 52, 44, 36, 28, 20, 12,  4,
  62, 54, 46, 38, 30, 22, 14,  6,
]

# Final permutation.
FP = [
  39,  7, 47, 15, 55, 23, 63, 31,
  38,  6, 46, 14, 54, 22, 62, 30,
  37,  5, 45, 13, 53, 21, 61, 29,
  36,  4, 44, 12, 52, 20, 60, 28,
  35,  3, 43, 11, 51, 19, 59, 27,
  34,  2, 42, 10, 50, 18, 58, 26,
  33,  1, 41,  9, 49, 17, 57, 25,
  32,  0, 40,  8, 48, 16, 56, 24
]

# Permutation used in Feistel function.
PBOX = [
  15,  6, 19, 20, 28, 11, 27, 16,
   0, 14, 22, 25,  4, 17, 30,  9,
   1,  7, 23, 13, 31, 26,  2,  8,
  18, 12, 29,  5, 21, 10,  3, 24
]

# Permuted Choice 1.
PC1 = [
  56, 48, 40, 32, 24, 16,  8,  0,
  57, 49, 41, 33, 25, 17,  9,  1,
  58, 50, 42, 34, 26, 18, 10,  2,
  59, 51, 43, 35, 62, 54, 46, 38,
  30, 22, 14,  6, 61, 53, 45, 37,
  29, 21, 13,  5, 60, 52, 44, 36,
  28, 20, 12,  4, 27, 19, 11,  3
]

# Permuted Choice 2.
PC2 = [
  13, 16, 10, 23,  0,  4,  2, 27,
  14,  5, 20,  9, 22, 18, 11,  3,
  25,  7, 15,  6, 26, 19, 12,  1,
  40, 51, 30, 36, 46, 54, 29, 39,
  50, 44, 32, 47, 43, 48, 38, 55,
  33, 52, 45, 41, 49, 35, 28, 31
]

# Converts 32-bit number to 48-bit (a[31:0] -> b[47:0])
# b[i] = a[EXPANSION[i]]
# b[0] = a[31]
# b[1] = a[0]
EXPANSION = [
  31,  0,  1,  2,  3,  4,  3,  4,
   5,  6,  7,  8,  7,  8,  9, 10,
  11, 12, 11, 12, 13, 14, 15, 16,
  15, 16, 17, 18, 19, 20, 19, 20,
  21, 22, 23, 24, 23, 24, 25, 26,
  27, 28, 27, 28, 29, 30, 31,  0
]

SBOX = [
  # S-Box 1
  [
    [14,  4, 13,  1,  2, 15, 11,  8,  3, 10,  6, 12,  5,  9,  0,  7],
    [ 0, 15,  7,  4, 14,  2, 13,  1, 10,  6, 12, 11,  9,  5,  3,  8],
    [ 4,  1, 14,  8, 13,  6,  2, 11, 15, 12,  9,  7,  3, 10,  5,  0],
    [15, 12,  8,  2,  4,  9,  1,  7,  5, 11,  3, 14, 10,  0,  6, 13]
  ],
  # S-Box 2
  [
    [15,  1,  8, 14,  6, 11,  3,  4,  9,  7,  2, 13, 12,  0,  5, 10],
    [ 3, 13,  4,  7, 15,  2,  8, 14, 12,  0,  1, 10,  6,  9, 11,  5],
    [ 0, 14,  7, 11, 10,  4, 13,  1,  5,  8, 12,  6,  9,  3,  2, 15],
    [13,  8, 10,  1,  3, 15,  4,  2, 11,  6,  7, 12,  0,  5, 14,  9]
  ],
  # S-Box 3
  [
    [10,  0,  9, 14,  6,  3, 15,  5,  1, 13, 12,  7, 11,  4,  2,  8],
    [13,  7,  0,  9,  3,  4,  6, 10,  2,  8,  5, 14, 12, 11, 15,  1],
    [13,  6,  4,  9,  8, 15,  3,  0, 11,  1,  2, 12,  5, 10, 14,  7],
    [ 1, 10, 13,  0,  6,  9,  8,  7,  4, 15, 14,  3, 11,  5,  2, 12]
  ],
  # S-Box 4
  [
    [ 7, 13, 14,  3,  0,  6,  9, 10,  1,  2,  8,  5, 11, 12,  4, 15],
    [13,  8, 11,  5,  6, 15,  0,  3,  4,  7,  2, 12,  1, 10, 14,  9],
    [10,  6,  9,  0, 12, 11,  7, 13, 15,  1,  3, 14,  5,  2,  8,  4],
    [ 3, 15,  0,  6, 10,  1, 13,  8,  9,  4,  5, 11, 12,  7,  2, 14]
  ],
  # S-Box 5
  [
    [ 2, 12,  4,  1,  7, 10, 11,  6,  8,  5,  3, 15, 13,  0, 14,  9],
    [14, 11,  2, 12,  4,  7, 13,  1,  5,  0, 15, 10,  3,  9,  8,  6],
    [ 4,  2,  1, 11, 10, 13,  7,  8, 15,  9, 12,  5,  6,  3,  0, 14],
    [11,  8, 12,  7,  1, 14,  2, 13,  6, 15,  0,  9, 10,  4,  5,  3]
  ],
  # S-Box 6
  [
    [12,  1, 10, 15,  9,  2,  6,  8,  0, 13,  3,  4, 14,  7,  5, 11],
    [10, 15,  4,  2,  7, 12,  9,  5,  6,  1, 13, 14,  0, 11,  3,  8],
    [ 9, 14, 15,  5,  2,  8, 12,  3,  7,  0,  4, 10,  1, 13, 11,  6],
    [ 4,  3,  2, 12,  9,  5, 15, 10, 11, 14,  1,  7,  6,  0,  8, 13]
  ],
  # S-Box 7
  [
    [ 4, 11,  2, 14, 15,  0,  8, 13,  3, 12,  9,  7,  5, 10,  6,  1],
    [13,  0, 11,  7,  4,  9,  1, 10, 14,  3,  5, 12,  2, 15,  8,  6],
    [ 1,  4, 11, 13, 12,  3,  7, 14, 10, 15,  6,  8,  0,  5,  9,  2],
    [ 6, 11, 13,  8,  1,  4, 10,  7,  9,  5,  0, 15, 14,  2,  3, 12]
  ],
  # S-Box 8
  [
    [13,  2,  8,  4,  6, 15, 11,  1, 10,  9,  3, 14,  5,  0, 12,  7],
    [ 1, 15, 13,  8, 10,  3,  7,  4, 12,  5,  6, 11,  0, 14,  9,  2],
    [ 7, 11,  4,  1,  9, 12, 14,  2,  0,  6, 10, 13, 15,  3,  5,  8],
    [ 2,  1, 14,  7,  4, 10,  8, 13, 15, 12,  9,  0,  3,  5,  6, 11]
  ]
]

def apply_permutation(block: Bitarray, perm: list) -> Bitarray:
  res = Bitarray(size=len(perm))
  for i, p in enumerate(perm):
    res[i] = block[p]
  return res

def generate_round_keys(key: Bitarray) -> List[Bitarray]:
  assert len(key) == 64
  SHIFTS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
  round_keys = []

  # PC1 permutation. (64 -> 48)
  key = apply_permutation(key, PC1)

  # Split key in half.
  left, right = key[55:28], key[27:0]

  for shift in SHIFTS:
    left.rotl(shift)
    right.rotl(shift)
    round_keys.append(apply_permutation(left + right, PC2))
  return round_keys


def F(hblock: Bitarray, roundkey: Bitarray) -> Bitarray:
  """
  Feistel function.
  """
  assert len(hblock) == 32
  assert len(roundkey) == 48

  xored = apply_permutation(hblock, EXPANSION) ^ roundkey

  sboxed = Bitarray(size=32)
  for i, sbox in enumerate(SBOX):
    j = 7 - i
    chunk = xored[j * 6 + 5: j * 6]
    row = chunk[5] << 1 | chunk[0]
    col = int(chunk[4:1])
    sboxed <<= 4
    sboxed |= sbox[row][col]

  return apply_permutation(sboxed, PBOX)

def DES_encrypt_block(block: bytes, key: bytes) -> bytes:
  assert len(block) == 8
  assert len(key) == 8

  block, key = Bitarray(block), Bitarray(key)

  # Generate round keys.
  round_keys = generate_round_keys(key)

  # Initial permutation.
  block = apply_permutation(block, IP)

  # Split block in half.
  left, right = block[63:32], block[31:0]

  for round_key in round_keys:
    left, right = right, F(right, round_key) ^ left

  # Final permutation.
  return apply_permutation(right + left, FP).bytes()

def DES_decrypt_block(block: bytes, key: bytes) -> bytes:
  assert len(block) == 8
  assert len(key) == 8

  block, key = Bitarray(block), Bitarray(key)

  # Generate round keys.
  round_keys = generate_round_keys(key)

  # Initial permutation.
  block = apply_permutation(block, IP)

  # Split block in half.
  left, right = block[63:32], block[31:0]

  for round_key in round_keys[::-1]:
    left, right = right, F(right, round_key) ^ left

  # Final permutation.
  return apply_permutation(right + left, FP).bytes()

def DES_encrypt(message: bytes, key: bytes) -> bytes:
  assert len(key) == 8
  n = len(message)

  # Add Padding.
  if n % 8 != 0:
    message += b"\x00" * ((8 - n) % 8)

  # Divide in blocks and encrypt.
  result = b""
  for i in range(0, len(message), 8):
    result += DES_encrypt_block(message[i:i + 8], key)

  return result

def DES_decrypt(message: bytes, key: bytes) -> bytes:
  assert len(key) == 8
  assert len(message) % 8 == 0

  # Divide in blocks and decrypt.
  result = bytearray()
  for i in range(0, len(message), 8):
    result += DES_decrypt_block(message[i:i + 8], key)

  # Remove padding.
  while result[-1] == 0:
    result.pop(-1)

  return bytes(result)

def main() -> None:
  random.seed(0)

  plaintext = "DES cipher".encode()
  key = random.randbytes(8)

  print(f"plaintext: {plaintext}")
  print(f"key: {key}")

  ciphertext = DES_encrypt(plaintext, key)
  decrypted = DES_decrypt(ciphertext, key)

  print(f"ciphertext: {ciphertext}")
  print(f"decrypted: {decrypted}")

if __name__ == "__main__":
  main()

