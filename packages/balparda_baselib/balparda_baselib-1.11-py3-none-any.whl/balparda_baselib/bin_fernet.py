"""Fernet class minus the base64 input/output.

All algorithm just like in https://cryptography.io/en/latest/fernet/#cryptography.fernet.Fernet
except the base64 conversions on input and output. For my use case they amount to a large
time delay. The key is still base64, only input/output were touched.

Copyright 2025 Daniel Balparda (balparda@github.com) - Apache-2.0 license
This code was Apache License, Version 2.0, in the original.
"""
# pylint: disable=invalid-name,missing-function-docstring,protected-access,raise-missing-from
# cspell:disable

import base64
import binascii
import os
import time
from typing import Optional, Union

from cryptography import utils
from cryptography import exceptions
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hmac


_MAX_CLOCK_SKEW = 60


class InvalidToken(Exception):  # noqa: N818
  """Invalid token exception."""


class BinaryFernet:
  """Binary Fernet. Same implementation, no base64 conversions on output."""

  def __init__(self, key: Union[bytes, str]) -> None:  # noqa: D107
    try:
      key = base64.urlsafe_b64decode(key)
    except binascii.Error as exc:
      raise ValueError("Fernet key must be 32 url-safe base64-encoded bytes.") from exc
    if len(key) != 32:
      raise ValueError("Fernet key must be 32 url-safe base64-encoded bytes.")
    self._signing_key = key[:16]
    self._encryption_key = key[16:]

  def encrypt(self, data: bytes) -> bytes:  # noqa: D102
    return self.encrypt_at_time(data, int(time.time()))

  def encrypt_at_time(self, data: bytes, current_time: int) -> bytes:  # noqa: D102
    iv = os.urandom(16)
    return self._encrypt_from_parts(data, current_time, iv)

  def _encrypt_from_parts(self, data: bytes, current_time: int, iv: bytes) -> bytes:
    utils._check_bytes("data", data)  # type: ignore

    padder = padding.PKCS7(algorithms.AES.block_size).padder()  # type: ignore
    padded_data = padder.update(data) + padder.finalize()
    encryptor = Cipher(
        algorithms.AES(self._encryption_key),
        modes.CBC(iv),
    ).encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    basic_parts = b"\x80" + current_time.to_bytes(length=8, byteorder="big") + iv + ciphertext

    h = hmac.HMAC(self._signing_key, hashes.SHA256())
    h.update(basic_parts)
    final_hmac = h.finalize()
    return basic_parts + final_hmac

  def decrypt(self, token: bytes, ttl: Optional[int] = None) -> bytes:  # noqa: D102
    timestamp, data = BinaryFernet._get_unverified_token_data(token)
    if ttl is None:
      time_info = None
    else:
      time_info = (ttl, int(time.time()))
    return self._decrypt_data(data, timestamp, time_info)

  @staticmethod
  def _get_unverified_token_data(token: bytes) -> tuple[int, bytes]:
    if not isinstance(token, (str, bytes)):
      raise TypeError("token must be bytes or str")

    if not token or token[0] != 0x80:
      raise InvalidToken

    if len(token) < 9:
      raise InvalidToken

    timestamp = int.from_bytes(token[1:9], byteorder="big")
    return timestamp, token

  def _verify_signature(self, data: bytes) -> None:
    h = hmac.HMAC(self._signing_key, hashes.SHA256())
    h.update(data[:-32])
    try:
      h.verify(data[-32:])
    except exceptions.InvalidSignature:
      raise InvalidToken

  def _decrypt_data(
      self, data: bytes, timestamp: int, time_info: Optional[tuple[int, int]]) -> bytes:
    if time_info is not None:
      ttl, current_time = time_info
      if timestamp + ttl < current_time:
        raise InvalidToken

      if current_time + _MAX_CLOCK_SKEW < timestamp:
        raise InvalidToken

    self._verify_signature(data)

    iv = data[9:25]
    ciphertext = data[25:-32]
    decryptor = Cipher(
        algorithms.AES(self._encryption_key), modes.CBC(iv)
    ).decryptor()
    plaintext_padded = decryptor.update(ciphertext)
    try:
      plaintext_padded += decryptor.finalize()
    except ValueError:
      raise InvalidToken
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()  # type: ignore

    unpadded = unpadder.update(plaintext_padded)
    try:
      unpadded += unpadder.finalize()
    except ValueError:
      raise InvalidToken
    return unpadded

  # @classmethod
  # def generate_key(cls) -> bytes:  # noqa: D102
  #   return base64.urlsafe_b64encode(os.urandom(32))

  # def decrypt_at_time(
  #     self, token: Union[bytes, str], ttl: int, current_time: int) -> bytes:  # noqa: D102
  #   if ttl is None:
  #       raise ValueError(
  #           "decrypt_at_time() can only be used with a non-None ttl"
  #       )
  #   timestamp, data = Fernet._get_unverified_token_data(token)
  #   return self._decrypt_data(data, timestamp, (ttl, current_time))

  # def extract_timestamp(self, token: Union[bytes, str]) -> int:  # noqa: D102
  #   timestamp, data = Fernet._get_unverified_token_data(token)
  #   # Verify the token was not tampered with.
  #   self._verify_signature(data)
  #   return timestamp
