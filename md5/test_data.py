import hashlib
import struct
import itertools

# Write teh test file:
# hash (32 bytes), data size (int, 4 bytes), data
with open("test.data", "wb") as fd:
  for i in range(1, 200):
    data = b"3" * i
    md5hash = hashlib.md5(data).hexdigest().encode('utf-8')
    fd.write(struct.pack(f"32sI{i}s", md5hash, i, data))

    data = b"\xff" * i
    md5hash = hashlib.md5(data).hexdigest().encode('utf-8')
    fd.write(struct.pack(f"32sI{i}s", md5hash, i, data))

  for i in range(1, 200):
    data = b"".join(itertools.islice(itertools.cycle((b"\xff", b"a", b"\x00", b"\xf0")), i))
    md5hash = hashlib.md5(data).hexdigest().encode('utf-8')
    fd.write(struct.pack(f"32sI{i}s", md5hash, i, data))

  for i in range(1, 200):
    data = b"\x00" * i
    md5hash = hashlib.md5(data).hexdigest().encode('utf-8')
    fd.write(struct.pack(f"32sI{i}s", md5hash, i, data))
