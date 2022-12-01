#!/usr/bin/env python3

import math

class Bitarray:
  pass

class Bitarray:
  def __init__(self, data: int | list | tuple | bytes = [0], size=None) -> None:
    if isinstance(data, int):
      self.__load_from_int(data)
    else:
      self.__load_from_bytes(bytes(data))
    if size is not None:
      self.__set_size(size)

  def __load_from_int(self, data: int) -> None:
    self._data = bytearray()
    while data > 0:
      self._data.append(data & 0xff)
      data >>= 8
    self._size = len(self._data) * 8

  def __load_from_bytes(self, data: bytes) -> None:
    self._data = bytearray(data)[::-1]
    self._size = len(data) * 8

  def __set_size(self, size: int) -> None:
    if size >= self._size:
      size -= self._size
      for _ in range(math.ceil(size / 8)):
        self._data.append(0)
      self._size += size
    else:
      for i in range(self._size - 1, size - 1, -1):
        assert self[i] == 0
      self._size = size

  def __int__(self):
    r = 0
    for i in range(len(self._data) - 1, -1, -1):
      r <<= 8
      r |= self._data[i]
    return r

  def __len__(self):
    return self._size

  def __setitem__(self, key: int, value: int) -> None:
    assert key < self._size
    byte = self._data[key // 8]
    byte ^= (-value ^ byte) & (1 << (key % 8))
    self._data[key // 8] = (byte & 0xff)

  def __getitem__(self, key: int) -> int:
    if isinstance(key, slice):
      start, stop, step = key.indices(len(self))
      return self.get(start, stop)
    return self.get(key)

  def __lshift__(self, shift: int) -> None:
    if shift >= len(self):
      self._data = [0] * len(self._data)
    else:
      for i in range(self._size - 1, -1 + shift, -1):
        self[i] = self[i - shift]
      for i in range(shift):
        self[i] = 0
    return self

  def __xor__(self, other: Bitarray | int) -> Bitarray:
    if isinstance(other, int):
      other = Bitarray(other, size=len(self))
    assert len(self) == len(other)
    return Bitarray(
      [x ^ y for x, y in zip(self._data, other._data)][::-1],
      size=len(self)
    )

  def __or__(self, other: Bitarray | int) -> Bitarray:
    if isinstance(other, int):
      other = Bitarray(other, size=len(self))
    assert len(self) == len(other)
    return Bitarray(
      [x | y for x, y in zip(self._data, other._data)][::-1],
      size=len(self)
    )

  def __str__(self) -> str:
    res = []
    for i in range(self._size - 1, -1, -1):
      res.append(str(self[i]))
      if i % 8 == 0 and i > 0:
        res.append("_")
    res.append(" (")
    for i in range(len(self._data) - 1, -1, -1):
      res.append(hex(self._data[i])[2:].zfill(2))
    res.append(")")
    return "".join(res)

  def __add__(self, other: Bitarray) -> Bitarray:
    res = Bitarray(size=len(self) + len(other))
    i = 0
    while i < len(other):
      res[i] = other[i]
      i += 1
    for j in range(len(self)):
      res[i] = self[j]
      i += 1
    return res

  def get(self, start: int, end: int = None) -> int | Bitarray:
    assert start < self._size
    if end is None:
      return (self._data[start // 8] >> (start % 8)) & 1
    assert end < self._size and start >= end
    s = start - end + 1
    r = Bitarray(size=s)
    for i in range(start, end - 1, -1):
      r <<= 1
      r |= (self._data[i // 8] >> (i % 8)) & 1
    return r

  def rotl(self, s: int) -> None:
    s %= len(self)
    t = Bitarray(self._data[::-1], len(self))
    for i in range(len(self)):
      self[i] = t[(i - s) % len(self)]

  def rotr(self, s: int) -> None:
    s %= len(self)
    t = Bitarray(self._data[::-1], len(self))
    for i in range(len(self)):
      self[i] = t[(i + s) % len(self)]

  def bytes(self) -> bytes:
    return bytes(self._data[::-1])

def equal(b, n):
  i = 0
  while n > 0:
    if b[i] != n & 1:
      return False
    n >>= 1
    i += 1
  while i < len(b):
    if b[i] != 0:
      return False
    i += 1
  return True

def test():
  b = Bitarray(0xabcd)
  assert len(b) == 2 * 8
  assert equal(b, 0xabcd) == True
  assert int(b) == 0xabcd

  b = Bitarray(0xabcde, size=20)
  assert len(b) == 20
  assert equal(b, 0xabcde) == True
  assert int(b) == 0xabcde

  b = Bitarray([0x0f, 0xa0, 0xf0])
  assert len(b) == 3 * 8
  assert equal(b, 0x0fa0f0) == True
  assert int(b) == 0x0fa0f0

  b = Bitarray([0x0f, 0xa0, 0xf0], size=20)
  assert len(b) == 20
  assert equal(b, 0x0fa0f0) == True

  b = Bitarray([0x0b, 0xa0, 0xf1], size=20)
  assert len(b) == 20
  t = b.get(7, 0)
  assert len(t) == 8
  assert equal(t, 0xf1) == True
  t = b[0:0]
  assert len(t) == 1
  assert equal(t, 1) == True
  t = b[19:16]
  assert len(t) == 4
  assert equal(t, 0xb) == True

  b = Bitarray([0x0a, 0xbb, 0xdd], size=20)
  assert len(b) == 20
  assert equal(b, 0xabbdd) == True
  b <<= 1
  assert equal(b, 0x577ba) == True
  b <<= 3
  assert equal(b, 0xbbdd0) == True
  b <<= 15
  assert len(b) == 20
  assert equal(b, 0x80000) == True
  b <<= 1
  assert len(b) == 20
  assert equal(b, 0) == True

  b = Bitarray([0x0a, 0xbb, 0xdd], size=20)
  b <<= 30
  assert len(b) == 20
  assert equal(b, 0) == True

  a = Bitarray([0xf0, 0xff, 0xf0])
  b = Bitarray([0x00, 0xff, 0x0f])
  c = a | b
  assert len(c) == 3 * 8
  assert equal(c, 0xf0ffff) == True

  a = Bitarray([0x0a, 0xff, 0xc0], size=20)
  b = Bitarray([0x0b, 0x00, 0x0a], size=20)
  c = a | b
  assert len(c) == 20
  assert equal(c, 0x0b_ff_ca) == True

  a = Bitarray([0xab, 0xff, 0xc0], size=28)
  b = Bitarray([0xba, 0xab, 0x0a], size=28)
  c = a ^ b
  assert len(c) == 28
  assert equal(c, 0x11_54_ca) == True

  a = Bitarray([0xab, 0xcd, 0xef])
  assert len(a) == 3 * 8
  a.rotl(4)
  assert equal(a, 0xbc_de_fa) == True
  a.rotl(1)
  assert equal(a, 0x79bdf5) == True
  a.rotl(24)
  assert equal(a, 0x79bdf5) == True
  a.rotr(1)
  assert equal(a, 0xbc_de_fa) == True
  a.rotr(4)
  assert equal(a, 0xabcdef) == True


if __name__ == "__main__":
  test()

