import struct as _struct
# Note: there are lazy imports

def _to_bytes_iterator(data):
    # bytes
    try:
        return iter([b"" + data])
    except:
        pass

    # string
    try:
        return iter([b"" + data.encode("utf8")])
    except:
        pass

    def to_bytes(chunk, origin, allow_None=False):
        try: # bytes
            return b"" + chunk
        except:
            try: # string
                return b"" + chunk.encode("utf8")
            except:
                if allow_None and chunk is None:
                    return None
                else:
                    raise TypeError(f"Expected string and/or bytes in {origin}. Got {type(chunk)}.")

    # iterable (generator)
    from types import GeneratorType
    if isinstance(data, GeneratorType):
        def gen():
            try:
                chunk = next(data)
                while True:
                    chunk = data.send((yield to_bytes(chunk, "generator", allow_None=True)))
            except StopIteration:
                pass
        return gen()

    # iterable
    from collections.abc import Iterable
    if isinstance(data, Iterable):
        def gen():
            for chunk in data:
                yield to_bytes(chunk, "iterable")
        return gen()

    # pathlib.Path
    import pathlib
    if isinstance(data, pathlib.Path):
        def gen():
            with data.open("rb") as file:
                while True:
                    chunk = file.read(0x2000)
                    if not chunk:
                        break
                    yield chunk
        return gen()

    # .read()-able
    if hasattr(data, "read"):
        def gen():
            while True:
                chunk = data.read(0x2000)
                if not chunk:
                    break
                yield to_bytes(chunk, ".read()-able")
        return gen()

    raise TypeError(f"Expected string, bytes, iterable, .read()-able or pathlib.Path. Got {type(data)}.")

def _get_next_chunk(data_it, save_state):
    chunk = next(data_it)
    while chunk is None: # Send current state to generator
        chunk = data_it.send(save_state())
    return chunk

def md2(data, initial_state=None) -> bytes:
    # Reference: RFC 1319

    # A.3
    S = (
        41, 46, 67, 201, 162, 216, 124, 1, 61, 54, 84, 161, 236, 240, 6,
        19, 98, 167, 5, 243, 192, 199, 115, 140, 152, 147, 43, 217, 188,
        76, 130, 202, 30, 155, 87, 60, 253, 212, 224, 22, 103, 66, 111, 24,
        138, 23, 229, 18, 190, 78, 196, 214, 218, 158, 222, 73, 160, 251,
        245, 142, 187, 47, 238, 122, 169, 104, 121, 145, 21, 178, 7, 63,
        148, 194, 16, 137, 11, 34, 95, 33, 128, 127, 93, 154, 90, 144, 50,
        39, 53, 62, 204, 231, 191, 247, 151, 3, 255, 25, 48, 179, 72, 165,
        181, 209, 215, 94, 146, 42, 172, 86, 170, 198, 79, 184, 56, 210,
        150, 164, 125, 182, 118, 252, 107, 226, 156, 116, 4, 241, 69, 157,
        112, 89, 100, 113, 135, 32, 134, 91, 207, 101, 230, 45, 168, 2, 27,
        96, 37, 173, 174, 176, 185, 246, 28, 70, 97, 105, 52, 64, 126, 15,
        85, 71, 163, 35, 221, 81, 175, 58, 195, 92, 249, 206, 186, 197,
        234, 38, 44, 83, 13, 110, 133, 40, 132, 9, 211, 223, 205, 244, 65,
        129, 77, 82, 106, 220, 55, 200, 108, 193, 171, 250, 36, 225, 123,
        8, 12, 189, 177, 74, 120, 136, 149, 139, 227, 99, 232, 109, 233,
        203, 213, 254, 59, 0, 29, 57, 242, 239, 183, 14, 102, 88, 208, 228,
        166, 119, 114, 248, 235, 117, 75, 10, 49, 68, 80, 180, 143, 237,
        31, 26, 219, 153, 141, 51, 159, 17, 131, 20
    )

    if initial_state:
        X = bytearray(initial_state[:48])
        C = bytearray(initial_state[48:64])
        L = initial_state[64]
        buffer = initial_state[65:]
    else:
        # 3.3
        X = bytearray(48)

        # 3.2
        C = bytearray(16)
        L = 0 # one byte

        buffer = b""

    # 3.2
    def update_checksum(block):
        nonlocal L
        for j, c in enumerate(block):
            C[j] ^= S[c ^ L]
            L = C[j]

    data_it = _to_bytes_iterator(data)
    has_data = True
    while has_data:
        try:
            buffer += _get_next_chunk(data_it, save_state=lambda: bytes(X + C + _struct.pack("B", L) + buffer))
        except StopIteration:
            has_data = False

            # 3.1
            i = 16 - len(buffer) % 16
            buffer += _struct.pack("B", i) * i

            update_checksum(block=buffer)

            # 3.2
            buffer += C

        # 3.4
        while len(buffer) >= 16:
            update_checksum(block=buffer[:16])

            for j in range(16):
                X[16 + j] = buffer[j]
                X[32 + j] = X[16 + j] ^ X[j]

            buffer = buffer[16:]

            t = 0

            for j in range(18):
                for k in range(48):
                    t = X[k] = (X[k] ^ S[t])
                t = (t + j) % 256

    # 3.5
    return bytes(X[:16])

def md4(data, initial_state=None) -> bytes:
    # Reference: RFC 1320

    # 2. X <<< s
    def ROTL(x, s): return ((x << s) | (x >> 32 - s)) % 2**32

    # 3.4
    def F(X,Y,Z): return X & Y | ~X & Z
    def G(X,Y,Z): return X & Y | X & Z | Y & Z
    def H(X,Y,Z): return X ^ Y ^ Z
    def R1(a,b,c,d, k, s): return ROTL((a + F(b,c,d) + X[k]             ) % 2**32, s)
    def R2(a,b,c,d, k, s): return ROTL((a + G(b,c,d) + X[k] + 0x5A827999) % 2**32, s)
    def R3(a,b,c,d, k, s): return ROTL((a + H(b,c,d) + X[k] + 0x6ED9EBA1) % 2**32, s)

    if initial_state:
        A, B, C, D, data_size = _struct.unpack_from("<4IQ", initial_state)
        buffer = initial_state[24:]
    else:
        # 3.3
        A = 0x67452301
        B = 0xefcdab89
        C = 0x98badcfe
        D = 0x10325476

        data_size = 0
        buffer = b""

    data_it = _to_bytes_iterator(data)
    has_data = True
    while has_data:
        try:
            chunk = _get_next_chunk(data_it, save_state=lambda: _struct.pack("<4IQ", A, B, C, D, data_size) + buffer)
            buffer += chunk
            data_size += len(chunk)
        except StopIteration:
            has_data = False

            # 3.1
            buffer += b"\x80"
            while len(buffer) % 64 != 56:
                buffer += b"\0"

            # 3.2
            buffer += _struct.pack("<Q", data_size*8 % 2**64)

        # 3.4
        while len(buffer) >= 64:
            X = _struct.unpack("<16I", buffer[:64])
            buffer = buffer[64:]

            AA = A
            BB = B
            CC = C
            DD = D

            # Round 1
            A=R1(A,B,C,D,  0, 3); D=R1(D,A,B,C,  1, 7); C=R1(C,D,A,B,  2, 11); B=R1(B,C,D,A,  3, 19)
            A=R1(A,B,C,D,  4, 3); D=R1(D,A,B,C,  5, 7); C=R1(C,D,A,B,  6, 11); B=R1(B,C,D,A,  7, 19)
            A=R1(A,B,C,D,  8, 3); D=R1(D,A,B,C,  9, 7); C=R1(C,D,A,B, 10, 11); B=R1(B,C,D,A, 11, 19)
            A=R1(A,B,C,D, 12, 3); D=R1(D,A,B,C, 13, 7); C=R1(C,D,A,B, 14, 11); B=R1(B,C,D,A, 15, 19)

            # Round 2
            A=R2(A,B,C,D,  0, 3); D=R2(D,A,B,C,  4, 5); C=R2(C,D,A,B,  8,  9); B=R2(B,C,D,A, 12, 13)
            A=R2(A,B,C,D,  1, 3); D=R2(D,A,B,C,  5, 5); C=R2(C,D,A,B,  9,  9); B=R2(B,C,D,A, 13, 13)
            A=R2(A,B,C,D,  2, 3); D=R2(D,A,B,C,  6, 5); C=R2(C,D,A,B, 10,  9); B=R2(B,C,D,A, 14, 13)
            A=R2(A,B,C,D,  3, 3); D=R2(D,A,B,C,  7, 5); C=R2(C,D,A,B, 11,  9); B=R2(B,C,D,A, 15, 13)

            # Round 3
            A=R3(A,B,C,D,  0, 3); D=R3(D,A,B,C,  8, 9); C=R3(C,D,A,B,  4, 11); B=R3(B,C,D,A, 12, 15)
            A=R3(A,B,C,D,  2, 3); D=R3(D,A,B,C, 10, 9); C=R3(C,D,A,B,  6, 11); B=R3(B,C,D,A, 14, 15)
            A=R3(A,B,C,D,  1, 3); D=R3(D,A,B,C,  9, 9); C=R3(C,D,A,B,  5, 11); B=R3(B,C,D,A, 13, 15)
            A=R3(A,B,C,D,  3, 3); D=R3(D,A,B,C, 11, 9); C=R3(C,D,A,B,  7, 11); B=R3(B,C,D,A, 15, 15)

            A = (A + AA) % 2**32
            B = (B + BB) % 2**32
            C = (C + CC) % 2**32
            D = (D + DD) % 2**32

    # 3.5
    return _struct.pack("<4I", A, B, C, D)

def md5(data, initial_state=None) -> bytes:
    # Reference: RFC 1321

    # 2. X <<< s
    def ROTL(x, s): return ((x << s) | (x >> 32 - s)) % 2**32

    # 3.4
    def F(X,Y,Z): return X & Y | ~X & Z
    def G(X,Y,Z): return X & Z | Y & ~Z
    def H(X,Y,Z): return X ^ Y ^ Z
    def I(X,Y,Z): return Y ^ (X | ~Z)
    T = (
        0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee, 0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
        0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be, 0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
        0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa, 0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
        0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed, 0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
        0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c, 0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
        0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05, 0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
        0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039, 0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
        0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1, 0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391,
    )
    def R(aux, a,b,c,d, k, s, i): return (b + ROTL((a + aux(b,c,d) + X[k] + T[i-1]) % 2**32, s)) % 2**32

    if initial_state:
        A, B, C, D, data_size = _struct.unpack_from("<4IQ", initial_state)
        buffer = initial_state[24:]
    else:
        # 3.3
        A = 0x67452301
        B = 0xefcdab89
        C = 0x98badcfe
        D = 0x10325476

        data_size = 0
        buffer = b""

    data_it = _to_bytes_iterator(data)
    has_data = True
    while has_data:
        try:
            chunk = _get_next_chunk(data_it, save_state=lambda: _struct.pack("<4IQ", A, B, C, D, data_size) + buffer)
            buffer += chunk
            data_size += len(chunk)
        except StopIteration:
            has_data = False

            # 3.1
            buffer += b"\x80"
            while len(buffer) % 64 != 56:
                buffer += b"\0"

            # 3.2
            buffer += _struct.pack("<Q", data_size*8 % 2**64)

        # 3.4
        while len(buffer) >= 64:
            X = _struct.unpack("<16I", buffer[:64])
            buffer = buffer[64:]

            AA = A
            BB = B
            CC = C
            DD = D

            # Round 1
            A=R(F, A,B,C,D,  0, 7,  1); D=R(F, D,A,B,C,  1, 12,  2); C=R(F, C,D,A,B,  2, 17,  3); B=R(F, B,C,D,A,  3, 22,  4)
            A=R(F, A,B,C,D,  4, 7,  5); D=R(F, D,A,B,C,  5, 12,  6); C=R(F, C,D,A,B,  6, 17,  7); B=R(F, B,C,D,A,  7, 22,  8)
            A=R(F, A,B,C,D,  8, 7,  9); D=R(F, D,A,B,C,  9, 12, 10); C=R(F, C,D,A,B, 10, 17, 11); B=R(F, B,C,D,A, 11, 22, 12)
            A=R(F, A,B,C,D, 12, 7, 13); D=R(F, D,A,B,C, 13, 12, 14); C=R(F, C,D,A,B, 14, 17, 15); B=R(F, B,C,D,A, 15, 22, 16)

            # Round 2
            A=R(G, A,B,C,D,  1, 5, 17); D=R(G, D,A,B,C,  6,  9, 18); C=R(G, C,D,A,B, 11, 14, 19); B=R(G, B,C,D,A,  0, 20, 20)
            A=R(G, A,B,C,D,  5, 5, 21); D=R(G, D,A,B,C, 10,  9, 22); C=R(G, C,D,A,B, 15, 14, 23); B=R(G, B,C,D,A,  4, 20, 24)
            A=R(G, A,B,C,D,  9, 5, 25); D=R(G, D,A,B,C, 14,  9, 26); C=R(G, C,D,A,B,  3, 14, 27); B=R(G, B,C,D,A,  8, 20, 28)
            A=R(G, A,B,C,D, 13, 5, 29); D=R(G, D,A,B,C,  2,  9, 30); C=R(G, C,D,A,B,  7, 14, 31); B=R(G, B,C,D,A, 12, 20, 32)

            # Round 3
            A=R(H, A,B,C,D,  5, 4, 33); D=R(H, D,A,B,C,  8, 11, 34); C=R(H, C,D,A,B, 11, 16, 35); B=R(H, B,C,D,A, 14, 23, 36)
            A=R(H, A,B,C,D,  1, 4, 37); D=R(H, D,A,B,C,  4, 11, 38); C=R(H, C,D,A,B,  7, 16, 39); B=R(H, B,C,D,A, 10, 23, 40)
            A=R(H, A,B,C,D, 13, 4, 41); D=R(H, D,A,B,C,  0, 11, 42); C=R(H, C,D,A,B,  3, 16, 43); B=R(H, B,C,D,A,  6, 23, 44)
            A=R(H, A,B,C,D,  9, 4, 45); D=R(H, D,A,B,C, 12, 11, 46); C=R(H, C,D,A,B, 15, 16, 47); B=R(H, B,C,D,A,  2, 23, 48)

            # Round 4
            A=R(I, A,B,C,D,  0, 6, 49); D=R(I, D,A,B,C,  7, 10, 50); C=R(I, C,D,A,B, 14, 15, 51); B=R(I, B,C,D,A,  5, 21, 52)
            A=R(I, A,B,C,D, 12, 6, 53); D=R(I, D,A,B,C,  3, 10, 54); C=R(I, C,D,A,B, 10, 15, 55); B=R(I, B,C,D,A,  1, 21, 56)
            A=R(I, A,B,C,D,  8, 6, 57); D=R(I, D,A,B,C, 15, 10, 58); C=R(I, C,D,A,B,  6, 15, 59); B=R(I, B,C,D,A, 13, 21, 60)
            A=R(I, A,B,C,D,  4, 6, 61); D=R(I, D,A,B,C, 11, 10, 62); C=R(I, C,D,A,B,  2, 15, 63); B=R(I, B,C,D,A,  9, 21, 64)

            A = (A + AA) % 2**32
            B = (B + BB) % 2**32
            C = (C + CC) % 2**32
            D = (D + DD) % 2**32

    # 3.5
    return _struct.pack("<4I", A, B, C, D)

# RIPEMD-160 Appendix A

def _rol(x, s): return ((x << s) | (x >> 32 - s)) % 2**32

def _f(j,x,y,z):
    # RIPEMD-160 3.1
    def f1(x,y,z): return x ^ y ^ z
    def f2(x,y,z): return (x & y) | (~x & z)
    def f3(x,y,z): return (x | ~y) ^ z
    def f4(x,y,z): return (x & z) | (y & ~z)
    def f5(x,y,z): return x ^ (y | ~z)

    return (f1, f2, f3, f4, f5)[j//16](x, y, z)

def _K(j):  return (0x00000000, 0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xA953FD4E)[j//16]

_r =  (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
       7, 4, 13, 1, 10, 6, 15, 3, 12, 0, 9, 5, 2, 14, 11, 8,
       3, 10, 14, 4, 9, 15, 8, 1, 2, 7, 0, 6, 13, 11, 5, 12,
       1, 9, 11, 10, 0, 8, 12, 4, 13, 3, 7, 15, 14, 5, 6, 2,
       4, 0, 5, 9, 7, 12, 2, 10, 14, 1, 3, 8, 11, 6, 15, 13)
_r_ = (5, 14, 7, 0, 9, 2, 11, 4, 13, 6, 15, 8, 1, 10, 3, 12,
       6, 11, 3, 7, 0, 13, 5, 10, 14, 15, 8, 12, 4, 9, 1, 2,
       15, 5, 1, 3, 7, 14, 6, 9, 11, 8, 12, 2, 10, 0, 4, 13,
       8, 6, 4, 1, 3, 11, 15, 0, 5, 12, 2, 13, 9, 7, 10, 14,
       12, 15, 10, 4, 1, 5, 8, 7, 6, 2, 13, 14, 0, 3, 9, 11)

_s =  (11, 14, 15, 12, 5, 8, 7, 9, 11, 13, 14, 15, 6, 7, 9, 8,
       7, 6, 8, 13, 11, 9, 7, 15, 7, 12, 15, 9, 11, 7, 13, 12,
       11, 13, 6, 7, 14, 9, 13, 15, 14, 8, 13, 6, 5, 12, 7, 5,
       11, 12, 14, 15, 14, 15, 9, 8, 9, 14, 5, 6, 8, 6, 5, 12,
       9, 15, 5, 11, 6, 8, 13, 12, 5, 12, 13, 14, 11, 8, 5, 6)
_s_ = (8, 9, 9, 11, 13, 15, 15, 5, 7, 7, 8, 11, 14, 14, 12, 6,
       9, 13, 15, 7, 12, 8, 9, 11, 7, 7, 12, 7, 6, 15, 13, 11,
       9, 7, 15, 11, 8, 6, 6, 14, 12, 13, 5, 14, 13, 13, 7, 5,
       15, 5, 8, 11, 14, 14, 6, 14, 6, 9, 12, 9, 12, 5, 15, 8,
       8, 5, 12, 9, 12, 5, 14, 6, 8, 13, 6, 5, 15, 13, 11, 11)

def _ripemd(data, initial_state, H0, compress):
    # Reference: RIPEMD-160: A Strengthened Version of RIPEMD

    if initial_state:
        H = list(_struct.unpack_from(f"<{len(H0)}I", initial_state))
        data_size, = _struct.unpack_from("<Q", initial_state, len(H)*4)
        buffer = initial_state[len(H)*4+8:]
    else:
        H = list(H0)
        data_size = 0
        buffer = b""

    data_it = _to_bytes_iterator(data)
    has_data = True
    while has_data:
        try:
            chunk = _get_next_chunk(data_it, save_state=lambda: _struct.pack(f"<{len(H)}IQ", *H, data_size) + buffer)
            buffer += chunk
            data_size += len(chunk)
        except StopIteration:
            has_data = False

            buffer += b"\x80"
            while len(buffer) % 64 != 56:
                buffer += b"\0"
            buffer += _struct.pack("<Q", data_size*8 % 2**64)

        while len(buffer) >= 64:
            X = _struct.unpack("<16I", buffer[:64])
            buffer = buffer[64:]

            compress(H, X)

    return _struct.pack(f"<{len(H0)}I", *H)

def ripemd128(data, initial_state=None) -> bytes:
    # Reference: http://web.archive.org/web/20060712025200/http://homes.esat.kuleuven.be/~bosselae/ripemd/rmd128.txt

    H0 = 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476

    def _K_(j): return (0x50A28BE6, 0x5C4DD124, 0x6D703EF3, 0x00000000)[j//16]

    def compress(H, X):
        A,  B , C , D  = H
        A_, B_, C_, D_ = H

        for j in range(64):
            T = _rol((A + _f(j,B,C,D) + X[_r[j]] + _K(j)) % 2**32, _s[j])
            A = D; D = C; C = B; B = T
            T = _rol((A_ + _f(63-j,B_,C_,D_) + X[_r_[j]] + _K_(j)) % 2**32, _s_[j])
            A_ = D_; D_ = C_; C_ = B_; B_ = T

        T    = (H[1] + C + D_) % 2**32
        H[1] = (H[2] + D + A_) % 2**32
        H[2] = (H[3] + A + B_) % 2**32
        H[3] = (H[0] + B + C_) % 2**32
        H[0] = T

    return _ripemd(data, initial_state, H0, compress)

def ripemd160(data, initial_state=None) -> bytes:
    # Reference: http://web.archive.org/web/20060712025212/http://homes.esat.kuleuven.be/~bosselae/ripemd/rmd160.txt

    H0 = 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0

    def _K_(j): return (0x50A28BE6, 0x5C4DD124, 0x6D703EF3, 0x7A6D76E9, 0x00000000)[j//16]

    def compress(H, X):
        A,  B , C , D , E  = H
        A_, B_, C_, D_, E_ = H

        for j in range(80):
            T = (_rol((A + _f(j,B,C,D) + X[_r[j]] + _K(j)) % 2**32, _s[j]) + E) % 2**32
            A = E; E = D; D = _rol(C, 10); C = B; B = T
            T = (_rol((A_ + _f(79-j,B_,C_,D_) + X[_r_[j]] + _K_(j)) % 2**32, _s_[j]) + E_) % 2**32
            A_ = E_; E_ = D_; D_ = _rol(C_, 10); C_ = B_; B_ = T

        T    = (H[1] + C + D_) % 2**32
        H[1] = (H[2] + D + E_) % 2**32
        H[2] = (H[3] + E + A_) % 2**32
        H[3] = (H[4] + A + B_) % 2**32
        H[4] = (H[0] + B + C_) % 2**32
        H[0] = T

    return _ripemd(data, initial_state, H0, compress)

def ripemd256(data, initial_state=None) -> bytes:
    # Reference: http://web.archive.org/web/20060712025226/http://homes.esat.kuleuven.be/~bosselae/ripemd/rmd256.txt

    H0 = 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0x76543210, 0xFEDCBA98, 0x89ABCDEF, 0x01234567

    def _K_(j): return (0x50A28BE6, 0x5C4DD124, 0x6D703EF3, 0x00000000)[j//16]

    def compress(H, X):
        A, B, C, D, A_, B_, C_, D_ = H

        for j in range(64):
            T = _rol((A + _f(j,B,C,D) + X[_r[j]] + _K(j)) % 2**32, _s[j])
            A = D; D = C; C = B; B = T
            T = _rol((A_ + _f(63-j,B_,C_,D_) + X[_r_[j]] + _K_(j)) % 2**32, _s_[j])
            A_ = D_; D_ = C_; C_ = B_; B_ = T

            if   j == 15: A, A_ = A_, A
            elif j == 31: B, B_ = B_, B
            elif j == 47: C, C_ = C_, C
            elif j == 63: D, D_ = D_, D

        H[0] = (H[0] + A ) % 2**32
        H[1] = (H[1] + B ) % 2**32
        H[2] = (H[2] + C ) % 2**32
        H[3] = (H[3] + D ) % 2**32
        H[4] = (H[4] + A_) % 2**32
        H[5] = (H[5] + B_) % 2**32
        H[6] = (H[6] + C_) % 2**32
        H[7] = (H[7] + D_) % 2**32

    return _ripemd(data, initial_state, H0, compress)

def ripemd320(data, initial_state=None) -> bytes:
    # Reference: http://web.archive.org/web/20060712025237/http://homes.esat.kuleuven.be/~bosselae/ripemd/rmd320.txt

    H0 = 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0, 0x76543210, 0xFEDCBA98, 0x89ABCDEF, 0x01234567, 0x3C2D1E0F

    def _K_(j): return (0x50A28BE6, 0x5C4DD124, 0x6D703EF3, 0x7A6D76E9, 0x00000000)[j//16]

    def compress(H, X):
        A, B, C, D, E, A_, B_, C_, D_, E_ = H

        for j in range(80):
            T = (_rol((A + _f(j,B,C,D) + X[_r[j]] + _K(j)) % 2**32, _s[j]) + E) % 2**32
            A = E; E = D; D = _rol(C, 10); C = B; B = T
            T = (_rol((A_ + _f(79-j,B_,C_,D_) + X[_r_[j]] + _K_(j)) % 2**32, _s_[j]) + E_) % 2**32
            A_ = E_; E_ = D_; D_ = _rol(C_, 10); C_ = B_; B_ = T

            if   j == 15: B, B_ = B_, B
            elif j == 31: D, D_ = D_, D
            elif j == 47: A, A_ = A_, A
            elif j == 63: C, C_ = C_, C
            elif j == 79: E, E_ = E_, E

        H[0] = (H[0] + A ) % 2**32
        H[1] = (H[1] + B ) % 2**32
        H[2] = (H[2] + C ) % 2**32
        H[3] = (H[3] + D ) % 2**32
        H[4] = (H[4] + E ) % 2**32
        H[5] = (H[5] + A_) % 2**32
        H[6] = (H[6] + B_) % 2**32
        H[7] = (H[7] + C_) % 2**32
        H[8] = (H[8] + D_) % 2**32
        H[9] = (H[9] + E_) % 2**32

    return _ripemd(data, initial_state, H0, compress)

# FIPS 180-4 4.1.1
def _Ch(x,y,z): return (x & y) ^ (~x & z)
def _Maj(x,y,z): return (x & y) ^ (x & z) ^ (y & z)

def sha1(data, initial_state=None) -> bytes:
    # Reference: FIPS 180-4

    # 4.1.1
    def Parity(x,y,z): return x ^ y ^ z

    # 3.2
    def ROTL(x, n): return ((x << n) | (x >> 32 - n)) % 2**32

    # 4.1.1
    F = _Ch, Parity, _Maj, Parity

    # 4.2.1
    K128 = 0x5a827999, 0x6ed9eba1, 0x8f1bbcdc, 0xca62c1d6

    if initial_state:
        H = list(_struct.unpack_from("<5I", initial_state))
        data_size, = _struct.unpack_from("<Q", initial_state, 20)
        buffer = initial_state[28:]
    else:
        # 5.3.1
        H = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476, 0xc3d2e1f0]

        data_size = 0
        buffer = b""

    data_it = _to_bytes_iterator(data)
    has_data = True
    while has_data:
        try:
            chunk = _get_next_chunk(data_it, save_state=lambda: _struct.pack("<5IQ", *H, data_size) + buffer)
            buffer += chunk
            data_size += len(chunk)
        except StopIteration:
            has_data = False

            # 5.1.1
            buffer += b"\x80"
            while len(buffer) % 64 != 56:
                buffer += b"\0"
            buffer += _struct.pack(">Q", data_size*8 % 2**64)

        while len(buffer) >= 64:
            # 5.2.1
            W = list(_struct.unpack(">16I", buffer[:64]))
            buffer = buffer[64:]

            # 6.1.2

            # 1.
            for t in range(16, 80):
                W.append(ROTL(W[t-3] ^ W[t-8] ^ W[t-14] ^ W[t-16], 1))

            # 2.
            a, b, c, d, e = H

            # 3.
            for t in range(80):
                T = (ROTL(a, 5) + F[t//20](b,c,d) + e + K128[t//20] + W[t]) % 2**32
                e = d
                d = c
                c = ROTL(b, 30)
                b = a
                a = T

            # 4.
            H[0] = (a + H[0]) % 2**32
            H[1] = (b + H[1]) % 2**32
            H[2] = (c + H[2]) % 2**32
            H[3] = (d + H[3]) % 2**32
            H[4] = (e + H[4]) % 2**32

    return _struct.pack(">5I", *H)

def _sha2_32(data, initial_state, H0, output_size):
    # Reference: FIPS 180-4

    # 3.2
    def SHR(x, n): return x >> n
    def ROTR(x, n): return ((x >> n) | (x << 32 - n)) % 2**32

    # 4.1.2
    def SIGMA0_256(x): return ROTR(x,  2) ^ ROTR(x, 13) ^ ROTR(x, 22)
    def SIGMA1_256(x): return ROTR(x,  6) ^ ROTR(x, 11) ^ ROTR(x, 25)
    def sigma0_256(x): return ROTR(x,  7) ^ ROTR(x, 18) ^ SHR(x, 3)
    def sigma1_256(x): return ROTR(x, 17) ^ ROTR(x, 19) ^ SHR(x, 10)

    # 4.2.2
    K256 = (
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
    )

    if initial_state:
        H = list(_struct.unpack_from("<8I", initial_state))
        data_size, = _struct.unpack_from("<Q", initial_state, 32)
        buffer = initial_state[40:]
    else:
        H = list(H0)
        data_size = 0
        buffer = b""

    data_it = _to_bytes_iterator(data)
    has_data = True
    while has_data:
        try:
            chunk = _get_next_chunk(data_it, save_state=lambda: _struct.pack("<8IQ", *H, data_size) + buffer)
            buffer += chunk
            data_size += len(chunk)
        except StopIteration:
            has_data = False

            # 5.1.1
            buffer += b"\x80"
            while len(buffer) % 64 != 56:
                buffer += b"\0"
            buffer += _struct.pack(">Q", data_size*8 % 2**64)

        while len(buffer) >= 64:
            # 5.2.1
            W = list(_struct.unpack(">16I", buffer[:64]))
            buffer = buffer[64:]

            # 6.2.2

            # 1.
            for t in range(16, 64):
                W.append((sigma1_256(W[t-2]) + W[t-7] + sigma0_256(W[t-15]) + W[t-16]) % 2**32)

            # 2.
            a, b, c, d, e, f, g, h = H

            # 3.
            for t in range(64):
                T1 = (h + SIGMA1_256(e) + _Ch(e,f,g) + K256[t] + W[t]) % 2**32
                T2 = (SIGMA0_256(a) + _Maj(a,b,c)) % 2**32
                h = g
                g = f
                f = e
                e = (d + T1) % 2**32
                d = c
                c = b
                b = a
                a = (T1 + T2) % 2**32

            # 4.
            H[0] = (a + H[0]) % 2**32
            H[1] = (b + H[1]) % 2**32
            H[2] = (c + H[2]) % 2**32
            H[3] = (d + H[3]) % 2**32
            H[4] = (e + H[4]) % 2**32
            H[5] = (f + H[5]) % 2**32
            H[6] = (g + H[6]) % 2**32
            H[7] = (h + H[7]) % 2**32

    return _struct.pack(">8I", *H)[:output_size]

def sha224(data, initial_state=None) -> bytes:
    # Reference: FIPS 180-4 5.3.2
    H0 = 0xc1059ed8, 0x367cd507, 0x3070dd17, 0xf70e5939, 0xffc00b31, 0x68581511, 0x64f98fa7, 0xbefa4fa4

    return _sha2_32(data, initial_state, H0, output_size=28)

def sha256(data, initial_state=None) -> bytes:
    # Reference: FIPS 180-4 5.3.3
    H0 = 0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19

    return _sha2_32(data, initial_state, H0, output_size=32)

def _sha2_64(data, initial_state, H0, output_size):
    # Reference: FIPS 180-4

    # 3.2
    def SHR(x, n): return x >> n
    def ROTR(x, n): return ((x >> n) | (x << 64 - n)) % 2**64

    # 4.1.3
    def SIGMA0_512(x): return ROTR(x, 28) ^ ROTR(x, 34) ^ ROTR(x, 39)
    def SIGMA1_512(x): return ROTR(x, 14) ^ ROTR(x, 18) ^ ROTR(x, 41)
    def sigma0_512(x): return ROTR(x,  1) ^ ROTR(x,  8) ^ SHR(x, 7)
    def sigma1_512(x): return ROTR(x, 19) ^ ROTR(x, 61) ^ SHR(x, 6)

    # 4.2.3
    K512 = (
        0x428a2f98d728ae22, 0x7137449123ef65cd, 0xb5c0fbcfec4d3b2f, 0xe9b5dba58189dbbc,
        0x3956c25bf348b538, 0x59f111f1b605d019, 0x923f82a4af194f9b, 0xab1c5ed5da6d8118,
        0xd807aa98a3030242, 0x12835b0145706fbe, 0x243185be4ee4b28c, 0x550c7dc3d5ffb4e2,
        0x72be5d74f27b896f, 0x80deb1fe3b1696b1, 0x9bdc06a725c71235, 0xc19bf174cf692694,
        0xe49b69c19ef14ad2, 0xefbe4786384f25e3, 0x0fc19dc68b8cd5b5, 0x240ca1cc77ac9c65,
        0x2de92c6f592b0275, 0x4a7484aa6ea6e483, 0x5cb0a9dcbd41fbd4, 0x76f988da831153b5,
        0x983e5152ee66dfab, 0xa831c66d2db43210, 0xb00327c898fb213f, 0xbf597fc7beef0ee4,
        0xc6e00bf33da88fc2, 0xd5a79147930aa725, 0x06ca6351e003826f, 0x142929670a0e6e70,
        0x27b70a8546d22ffc, 0x2e1b21385c26c926, 0x4d2c6dfc5ac42aed, 0x53380d139d95b3df,
        0x650a73548baf63de, 0x766a0abb3c77b2a8, 0x81c2c92e47edaee6, 0x92722c851482353b,
        0xa2bfe8a14cf10364, 0xa81a664bbc423001, 0xc24b8b70d0f89791, 0xc76c51a30654be30,
        0xd192e819d6ef5218, 0xd69906245565a910, 0xf40e35855771202a, 0x106aa07032bbd1b8,
        0x19a4c116b8d2d0c8, 0x1e376c085141ab53, 0x2748774cdf8eeb99, 0x34b0bcb5e19b48a8,
        0x391c0cb3c5c95a63, 0x4ed8aa4ae3418acb, 0x5b9cca4f7763e373, 0x682e6ff3d6b2b8a3,
        0x748f82ee5defb2fc, 0x78a5636f43172f60, 0x84c87814a1f0ab72, 0x8cc702081a6439ec,
        0x90befffa23631e28, 0xa4506cebde82bde9, 0xbef9a3f7b2c67915, 0xc67178f2e372532b,
        0xca273eceea26619c, 0xd186b8c721c0c207, 0xeada7dd6cde0eb1e, 0xf57d4f7fee6ed178,
        0x06f067aa72176fba, 0x0a637dc5a2c898a6, 0x113f9804bef90dae, 0x1b710b35131c471b,
        0x28db77f523047d84, 0x32caab7b40c72493, 0x3c9ebe0a15c9bebc, 0x431d67c49c100d4c,
        0x4cc5d4becb3e42b6, 0x597f299cfc657e2a, 0x5fcb6fab3ad6faec, 0x6c44198c4a475817,
    )

    if initial_state:
        H = list(_struct.unpack_from("<8Q", initial_state))
        data_size, = _struct.unpack_from("<Q", initial_state, 64)
        buffer = initial_state[72:]
    else:
        H = list(H0)
        data_size = 0
        buffer = b""

    data_it = _to_bytes_iterator(data)
    has_data = True
    while has_data:
        try:
            chunk = _get_next_chunk(data_it, save_state=lambda: _struct.pack("<9Q", *H, data_size) + buffer)
            buffer += chunk
            data_size += len(chunk)
        except StopIteration:
            has_data = False

            # 5.1.1
            buffer += b"\x80"
            while len(buffer) % 128 != 112:
                buffer += b"\0"
            buffer += (data_size*8 % 2**128).to_bytes(16, byteorder="big")

        while len(buffer) >= 128:
            # 5.2.2
            W = list(_struct.unpack(">16Q", buffer[:128]))
            buffer = buffer[128:]

            # 6.4.2

            # 1.
            for t in range(16, 80):
                W.append((sigma1_512(W[t-2]) + W[t-7] + sigma0_512(W[t-15]) + W[t-16]) % 2**64)

            # 2.
            a, b, c, d, e, f, g, h = H

            # 3.
            for t in range(80):
                T1 = (h + SIGMA1_512(e) + _Ch(e,f,g) + K512[t] + W[t]) % 2**64
                T2 = (SIGMA0_512(a) + _Maj(a,b,c)) % 2**64
                h = g
                g = f
                f = e
                e = (d + T1) % 2**64
                d = c
                c = b
                b = a
                a = (T1 + T2) % 2**64

            # 4.
            H[0] = (a + H[0]) % 2**64
            H[1] = (b + H[1]) % 2**64
            H[2] = (c + H[2]) % 2**64
            H[3] = (d + H[3]) % 2**64
            H[4] = (e + H[4]) % 2**64
            H[5] = (f + H[5]) % 2**64
            H[6] = (g + H[6]) % 2**64
            H[7] = (h + H[7]) % 2**64

    return _struct.pack(">8Q", *H)[:output_size]

def sha384(data, initial_state=None) -> bytes:
    # Reference: FIPS 180-4 5.3.4
    H0 = 0xcbbb9d5dc1059ed8, 0x629a292a367cd507, 0x9159015a3070dd17, 0x152fecd8f70e5939, 0x67332667ffc00b31, 0x8eb44a8768581511, 0xdb0c2e0d64f98fa7, 0x47b5481dbefa4fa4

    return _sha2_64(data, initial_state, H0, output_size=48)

def sha512(data, initial_state=None) -> bytes:
    # Reference: FIPS 180-4 5.3.5
    H0 = 0x6a09e667f3bcc908, 0xbb67ae8584caa73b, 0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1, 0x510e527fade682d1, 0x9b05688c2b3e6c1f, 0x1f83d9abfb41bd6b, 0x5be0cd19137e2179

    return _sha2_64(data, initial_state, H0, output_size=64)

def sha512_224(data, initial_state=None) -> bytes:
    # Reference: FIPS 180-4 5.3.6.1
    H0 = 0x8C3D37C819544DA2, 0x73E1996689DCD4D6, 0x1DFAB7AE32FF9C82, 0x679DD514582F9FCF, 0x0F6D2B697BD44DA8, 0x77E36F7304C48942, 0x3F9D85A86A1D36C8, 0x1112E6AD91D692A1

    return _sha2_64(data, initial_state, H0, output_size=28)

def sha512_256(data, initial_state=None) -> bytes:
    # Reference: FIPS 180-4 5.3.6.2
    H0 = 0x22312194FC2BF72C, 0x9F555FA3C84C64C2, 0x2393B86B6F53B151, 0x963877195940EABD, 0x96283EE2A88EFFE3, 0xBE5E1E2553863992, 0x2B0199FC2C85B8AA, 0x0EB72DDC81C52CA2

    return _sha2_64(data, initial_state, H0, output_size=32)

def sm3(data, initial_state=None) -> bytes:
    # Reference: https://datatracker.ietf.org/doc/html/draft-sca-cfrg-sm3-02

    # 3.1
    # a <<< i
    ROTL = lambda a,i: ((a << i) | (a >> 32 - i)) % 2**32

    # 4.1
    IV = 0x7380166f, 0x4914b2b9, 0x172442d7, 0xda8a0600, 0xa96f30bc, 0x163138aa, 0xe38dee4d, 0xb0fb0e4e

    # 4.2
    T = [0x79cc4519 if j < 16 else 0x7a879d8a for j in range(64)]

    # 4.3
    FF = [(lambda X,Y,Z: X ^ Y ^ Z) if j < 16 else (lambda X,Y,Z: (X & Y) | (X & Z) | (Y & Z)) for j in range(64)]
    GG = [(lambda X,Y,Z: X ^ Y ^ Z) if j < 16 else (lambda X,Y,Z: (X & Y) | (~X & Z)) for j in range(64)]

    # 4.4
    P0 = lambda X: X ^ ROTL(X, 9) ^ ROTL(X, 17)
    P1 = lambda X: X ^ ROTL(X, 15) ^ ROTL(X, 23)

    if initial_state:
        V = list(_struct.unpack_from("<8I", initial_state))
        data_size, = _struct.unpack_from("<Q", initial_state, 32)
        buffer = initial_state[40:]
    else:
        V = list(IV)
        data_size = 0
        buffer = b""

    data_it = _to_bytes_iterator(data)
    has_data = True
    while has_data:
        try:
            chunk = _get_next_chunk(data_it, save_state=lambda: _struct.pack("<8IQ", *V, data_size) + buffer)
            buffer += chunk
            data_size += len(chunk)
        except StopIteration:
            has_data = False

            # 5.2
            buffer += b"\x80"
            while len(buffer) % 64 != 56:
                buffer += b"\0"
            buffer += _struct.pack(">Q", data_size*8 % 2**64)

        while len(buffer) >= 64:
            # 5.3.2

            W = list(_struct.unpack(">16I", buffer[:64]))
            buffer = buffer[64:]

            for j in range(16,68):
                W.append(P1(W[j-16] ^ W[j-9] ^ ROTL(W[j-3], 15)) ^ ROTL(W[j-13], 7) ^ W[j-6])
            W_ = [W[j] ^ W[j+4] for j in range(64)]

            # 5.3.3

            A, B, C, D, E, F, G, H = V
            for j in range(64):
                SS1 = ROTL((ROTL(A, 12) + E + ROTL(T[j], j % 32)) % 2**32, 7)
                SS2 = SS1 ^ ROTL(A, 12)
                TT1 = (FF[j](A, B, C) + D + SS2 + W_[j]) % 2**32
                TT2 = (GG[j](E, F, G) + H + SS1 + W[j]) % 2**32
                D = C
                C = ROTL(B, 9)
                B = A
                A = TT1
                H = G
                G = ROTL(F, 19)
                F = E
                E = P0(TT2)

            V[0] ^= A
            V[1] ^= B
            V[2] ^= C
            V[3] ^= D
            V[4] ^= E
            V[5] ^= F
            V[6] ^= G
            V[7] ^= H

    # 5.3.4
    return _struct.pack(f">8I", *V)

__all__ = tuple(name for name in globals().keys() if not name.startswith("_"))
