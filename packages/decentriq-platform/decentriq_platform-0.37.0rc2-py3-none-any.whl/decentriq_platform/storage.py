import os
from hashlib import sha256
from typing import BinaryIO, Iterator, List, Optional, Tuple

import chily

from .proto import (
    ChunkHeader,
    EncryptionHeader,
    VersionHeader,
    serialize_length_delimited,
    parse_length_delimited,
)

__all__ = ["Key"]

KEY_LEN = 32


class Key:
    """
    This class wraps the key material that is used to encrypt the
    files that are uploaded to the decentriq platform.
    """

    material: bytes

    def __init__(self, material: Optional[bytes] = None):
        """
        Returns a new `Key` instance, can optional specify the raw key material.
        """
        if material is None:
            key_bytes = os.urandom(KEY_LEN)
        else:
            if len(material) != KEY_LEN:
                raise Exception("Invalid key length, must be 32 bytes")
            key_bytes = material
        self.material = key_bytes


def create_chunk_header(
    extra_entropy: bytes, content_size: Optional[int], chunk_content_sizes: List[int]
) -> bytes:
    chunk_header = ChunkHeader()
    chunk_header.extraEntropy = extra_entropy
    if content_size is not None:
        chunk_header.untrustedContentSize = content_size
    chunk_header.untrustedChunkContentSizes.extend(chunk_content_sizes)

    chunk_header_bytes = serialize_length_delimited(chunk_header)
    return chunk_header_bytes


def create_version_header() -> bytes:
    version_header = VersionHeader()
    version_header.version = 0
    return serialize_length_delimited(version_header)


# Returns (integrity hash, encrypted blob)
def create_encrypted_chunk(
    key: bytes,
    extra_entropy: bytes,
    data: bytes,
    content_size: Optional[int],
    chunk_content_sizes: List[int],
) -> Tuple[bytes, bytes]:
    chunk_bytes = []

    version_header = create_version_header()
    chunk_bytes.append(version_header)

    chunk_header = create_chunk_header(extra_entropy, content_size, chunk_content_sizes)
    chunk_bytes.append(chunk_header)

    chunk_bytes.append(data)

    chunk = b"".join(chunk_bytes)
    chunk_hasher = sha256()
    chunk_hasher.update(chunk)
    chunk_hash = chunk_hasher.digest()

    cipher = StorageCipher(key)
    encrypted_chunk = cipher.encrypt(chunk)

    return chunk_hash, encrypted_chunk

def decrypt_chunk(key: Key, expected_chunk_hash_hex: str, chunk: bytes) -> bytes:
    cipher = StorageCipher(key.material)
    decrypted_chunk = cipher.decrypt(chunk)
    chunk_hasher = sha256()
    chunk_hasher.update(decrypted_chunk)
    chunk_hash = chunk_hasher.digest()
    if chunk_hash.hex() != expected_chunk_hash_hex:
        raise Exception("Chunk hash mismatch")
    version_header = VersionHeader()
    offset = parse_length_delimited(decrypted_chunk, version_header)
    if version_header.version != 0:
        raise Exception(f"Unsupported chunk version {version_header.version}")
    chunk_header = ChunkHeader()
    offset = parse_length_delimited(decrypted_chunk, chunk_header, offset)
    return decrypted_chunk[offset:]

class Chunker(Iterator):
    def __init__(self, input_stream: BinaryIO, chunk_size: int):
        self.chunk_size = chunk_size
        self.content_size = 0
        self.input_stream = input_stream

    def __iter__(self) -> Iterator[Tuple[bytes, bytes, int]]:
        self.input_stream.seek(0)
        return self

    # returns (hash, chunk, chunk content size)
    def __next__(self) -> Tuple[bytes, bytes, int]:
        version_header_bytes = create_version_header()
        chunk_header_bytes = create_chunk_header(
            os.urandom(16), content_size=None, chunk_content_sizes=[]
        )

        # Does not account for header size
        chunk_bytes = [version_header_bytes, chunk_header_bytes]

        input_chunk_bytes = self.input_stream.read(self.chunk_size)
        chunk_content_size = len(input_chunk_bytes)
        self.content_size += chunk_content_size
        if chunk_content_size == 0:
            raise StopIteration
        chunk_bytes.append(input_chunk_bytes)

        chunk = b"".join(chunk_bytes)
        chunk_hasher = sha256()
        chunk_hasher.update(chunk)
        chunk_hash = chunk_hasher.digest()
        return chunk_hash, chunk, chunk_content_size


class StorageCipher:
    def __init__(self, symmetric_key: bytes):
        self.enc_key = symmetric_key
        self.cipher: chily.Cipher = chily.Cipher.from_symmetric(self.enc_key)

    def encrypt(self, data: bytes) -> bytes:
        nonce = chily.Nonce.from_random()
        encrypted_data = self.cipher.encrypt("storage cipher encrypt", data, nonce)

        encryption_header = EncryptionHeader()
        encryption_header.chilyKey.encryptionNonce = nonce.bytes

        serialized_encryption_header = serialize_length_delimited(encryption_header)
        encrypted_data_with_header = serialized_encryption_header + encrypted_data
        return encrypted_data_with_header

    def decrypt(self, encrypted_data: bytes) -> bytes:
        encryption_header = EncryptionHeader()
        offset = parse_length_delimited(encrypted_data, encryption_header)

        nonce = chily.Nonce.from_bytes(encryption_header.chilyKey.encryptionNonce)
        return self.cipher.decrypt("storage cipher decrypt", encrypted_data[offset:], nonce)
