#!/usr/bin/env python3
#
# Copyright 2025 Daniel Balparda (balparda@github.com) - Apache-2.0 license
#
"""Balparda's base library of util methods and classes.

Docs for crypto: https://cryptography.io/en/latest/
"""

import base64
import bz2
import functools
import hashlib
import json
import logging
import os
import os.path
import pickle  # nosec - this is a dangerous module!
# import pdb
import re
import time
from typing import Any, Callable, Literal

from cryptography.hazmat.primitives import ciphers
from cryptography.hazmat.primitives.ciphers import algorithms, modes
from cryptography.hazmat.primitives import hashes as hazmat_hashes
from cryptography.hazmat.primitives.kdf import pbkdf2 as hazmat_pbkdf2
from PIL import Image

from . import bin_fernet

__author__ = 'balparda@github.com'
__version__: tuple[int, int] = (1, 11)  # v1.11, 2025-07-04


# log format string, example logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
LOG_FORMAT: str = '%(asctime)-15s: %(module)s/%(funcName)s/%(lineno)d: %(message)s'

# advanced log formats
_LOG_FORMATS: list[str] = [
    '%(asctime)s.%(msecs)03d%(levelname)08s[%(funcName)s]: %(message)s',  # without process name # cspell:disable-line
    '%(asctime)s.%(msecs)03d%(levelname)08s[%(processName)s.%(funcName)s]: %(message)s',  # with prc # cspell:disable-line
    '%Y%m%d.%H:%M:%S',  # date format
]
# example '20220209.14:16:47.667    INFO[SomeMethodName]: Some message'

# user directories
USER_DIRECTORY: str = os.path.expanduser('~/')
EXECUTION_DIRECTORY: str = os.getcwd()
# get a private directory in user root directory: PRIVATE_DIR('.cache')
PRIVATE_DIR: Callable[[str], str] = lambda p: os.path.join(
    USER_DIRECTORY, p[len(USER_DIRECTORY):] if p.startswith(USER_DIRECTORY) else p)
# get module directory: MODULE_DIR(__file__)
MODULE_DIR: Callable[[str], str] = lambda f: os.path.dirname(os.path.realpath(f))
# get module private directory (remember to .gitignore): MODULE_PRIVATE_DIR(__file__, '.cache')
MODULE_PRIVATE_DIR: Callable[[str, str], str] = lambda f, p: os.path.join(MODULE_DIR(f), p)

# time utils
_TIME_FORMAT: str = '%Y/%b/%d-%H:%M:%S-UTC'
STD_TIME_STRING: Callable[[int | float], str] = lambda t: (
    time.strftime(_TIME_FORMAT, time.gmtime(t)) if t else '-')  # cspell:disable-line
INT_TIME: Callable[[], int] = lambda: int(time.time())
STR_TIME: Callable[[], str] = lambda: STD_TIME_STRING(INT_TIME())

# terminal colors; can be compounded, but always use TERM_END to go back to default
TERM_END = '\033[0m'  # disables colors/styles in terminal text
# colors
TERM_BLACK = '\033[30m'
TERM_WHITE = '\033[97m'
TERM_LIGHT_GRAY = '\033[37m'
TERM_DARK_GRAY = '\033[90m'
TERM_MAGENTA = '\033[35m'
TERM_BLUE = '\033[34m'
TERM_CYAN = '\033[36m'
TERM_GREEN = '\033[32m'
TERM_RED = '\033[31m'
TERM_YELLOW = '\033[33m'
TERM_LIGHT_MAGENTA = '\033[95m'
TERM_LIGHT_BLUE = '\033[94m'
TERM_LIGHT_CYAN = '\033[96m'
TERM_LIGHT_GREEN = '\033[92m'
TERM_LIGHT_RED = '\033[91m'
TERM_LIGHT_YELLOW = '\033[93m'
# warnings/errors
TERM_WARNING = TERM_LIGHT_YELLOW
TERM_FAIL = TERM_LIGHT_RED
# text style
TERM_BOLD = '\033[1m'
TERM_UNDERLINE = '\033[4m'

# useful
SEPARATION_LINE: str = TERM_BLUE + TERM_BOLD + ('-' * 80) + TERM_END
STRONG_SEPARATION_LINE: str = TERM_BLUE + TERM_BOLD + ('=' * 80) + TERM_END
_ANSI_ESCAPE: re.Pattern[str] = re.compile(r'\x1b\[[0-9;]*m')
STRIP_ANSI: Callable[[str], str] = lambda s: _ANSI_ESCAPE.sub('', s)


class Error(Exception):
  """Base exception."""


JsonType = dict[str, None | int | str | bool | float | list[Any] | dict[str, Any]]


def JsonToString(obj: JsonType, /, *, human_readable: bool = True) -> str:
  """Convert JSON to string, either compact or with indentation (human_readable True, default)."""
  return json.dumps(obj, indent=4 if human_readable else None)


def JsonToBytes(obj: JsonType, /) -> bytes:
  """Convert JSON to bytes."""
  return json.dumps(obj).encode('utf-8')


def StringToJson(obj: str, /) -> JsonType:
  """Convert string to JSON."""
  return json.loads(obj)


def BytesToJson(obj: bytes, /) -> JsonType:
  """Convert bytes to JSON."""
  return json.loads(obj.decode('utf-8'))


def BytesBinHash(data: bytes, /) -> bytes:
  """SHA-256 hash of bytes data. Always a length 32 bytes."""
  return hashlib.sha256(data).digest()


def BytesHexHash(data: bytes, /) -> str:
  """SHA-256 hex hash of bytes data. Always a length 64 string (32 bytes, hexadecimal)."""
  return hashlib.sha256(data).hexdigest()


def FileHexHash(full_path: str, /) -> str:
  """SHA-256 hex hash of file on disk. Always a length 64 string (32 bytes, hexadecimal)."""
  logging.info('Hashing file %r', full_path)
  if not os.path.exists(full_path):
    raise Error(f'File {full_path!r} not found for hashing')
  with open(full_path, 'rb') as file_obj:
    return BytesHexHash(file_obj.read())


def ImageHexHash(img: Image.Image, /) -> str:
  """SHA-256 hex hash of internal image data (ignores metadata!). Always a length 64 string."""
  return BytesHexHash(img.tobytes())  # type:ignore


def HumanizedBytes(inp_sz: int, /) -> str:
  """Return human-readable byte sizes.

  Args:
    inp: A bytes length

  Returns:
    human-readable length for inp_sz

  Raises:
    Error: negative size
  """
  if inp_sz < 0:
    raise Error(f'Input should be >=0 and got {inp_sz}')
  if inp_sz < 1024:
    return f'{inp_sz}b'
  if inp_sz < 1024 * 1024:
    return f'{(inp_sz / 1024.0):0.2f}kb'
  if inp_sz < 1024 * 1024 * 1024:
    return f'{(inp_sz / (1024.0 * 1024.0)):0.2f}Mb'
  if inp_sz < 1024 * 1024 * 1024 * 1024:
    return f'{(inp_sz / (1024.0 * 1024.0 * 1024.0)):0.2f}Gb'
  return f'{(inp_sz / (1024.0 * 1024.0 * 1024.0 * 1024.0)):0.2f}Tb'


def HumanizedDecimal(inp_sz: int, /) -> str:
  """Return human-readable decimal-measured sizes.

  Args:
    inp: A length from a measure to be converted by multiples of 1000, like Megapixel.

  Returns:
    human-readable length of decimal inp_sz

  Raises:
    Error: negative size
  """
  if inp_sz < 0:
    raise Error(f'Input should be >=0 and got {inp_sz}')
  if inp_sz < 1000:
    return str(inp_sz)
  if inp_sz < 1000 * 1000:
    return f'{(inp_sz / 1000.0):0.2f}k'
  if inp_sz < 1000 * 1000 * 1000:
    return f'{(inp_sz / (1000.0 * 1000.0)):0.2f}M'
  if inp_sz < 1000 * 1000 * 1000 * 1000:
    return f'{(inp_sz / (1000.0 * 1000.0 * 1000.0)):0.2f}G'
  return f'{(inp_sz / (1000.0 * 1000.0 * 1000.0 * 1000.0)):0.2f}T'


def HumanizedSeconds(inp_secs: int | float, /) -> str:  # pylint: disable=too-many-return-statements
  """Return human-readable time.

  Args:
    inp: An amount of time, in seconds, int or float

  Returns:
    human-readable time from the give number of seconds (inp_secs)

  Raises:
    Error: negative value
  """
  if inp_secs == 0:
    return '0 secs'
  inp_secs = float(inp_secs)
  if inp_secs < 0.0:
    raise Error(f'Input should be >=0 and got {inp_secs}')
  if inp_secs < 0.01:
    return f'{inp_secs * 1000.0:0.3f} msecs'  # cspell:disable-line
  if inp_secs < 1.0:
    return f'{inp_secs:0.4f} secs'
  if inp_secs < 60.0:
    return f'{inp_secs:0.2f} secs'
  if inp_secs < 60.0 * 60.0:
    return f'{(inp_secs / 60.0):0.2f} mins'
  if inp_secs < 24.0 * 60.0 * 60.0:
    return f'{(inp_secs / (60.0 * 60.0)):0.2f} hours'
  return f'{(inp_secs / (24.0 * 60.0 * 60.0)):0.2f} days'


class Timer:
  """A chronometer context.

  Use with auto-logging, like:
      with Timer(log='Foo'):
        # do something
      # here it will log to info: 'Timed: Foo: X.XX min'

  Or use with manual access, like:
      with Timer() as tm:
        # do something
        print(tm.partial)  # will print '10.3 min' for example
        # do more
      time_delta_in_seconds = tm.delta
      print(tm.readable)  # will print '1.56 hours' for example

  See also the Timed() decorator below.
  """

  def __init__(self, log: str | None = None) -> None:
    """Construct.

    Args:
      log: (default None) If given as string will logging.info a log upon __exit__
          like '%s: %s' % (log, execution_time)
    """
    self._start: float | None = None
    self._end: float | None = None
    self._log: str | None = log

  def __enter__(self) -> Any:
    """Enter Timed context. Starts the timer."""
    self._start = time.time()
    return self

  def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Literal[False]:
    """Exit Timed context. Will stop the timer and will log if necessary."""
    _: str = self.partial
    return False  # do not stop exceptions from propagating!

  @property
  def delta(self) -> float:
    """The time, in seconds. Cannot be called before some end is stored.

    Returns:
      delta, if any

    Raises:
      Error: chronometer is not set yet
    """
    if not self._start or not self._end:
      raise Error('Cannot get time from this chronometer yet.')
    return self._end - self._start

  @property
  def readable(self) -> str:
    """A readable string for the delta, in 'sec', 'min' or 'hours'."""
    return HumanizedSeconds(self.delta)

  @property
  def partial(self) -> str:
    """Stores an end time (and will log if necessary)."""
    self._end = time.time()
    readable: str = self.readable
    if self._log is not None:
      logging.info('%s: %s', self._log, readable)
    return readable


def Timed(log: str | None = None) -> Callable[[Callable[[Any], Any]], Callable[[Any], Any]]:
  """Make any call print its execution time, to be used as a decorator.

  Args:
    log: (default None) If given: The message to be displayed with the time;
        if not given will use the decorated method name for a simple message
  """

  def _Timed(func: Callable[[Any], Any]) -> Callable[[Any], Any]:

    @functools.wraps(func)
    def _WrappedCall(*args: list[Any], **kwargs: dict[Any, Any]) -> Any:
      log_message: str = f'{(func.__name__ + "()") if log is None else log!r} execution time'
      with Timer(log=log_message):
        return func(*args, **kwargs)

    return _WrappedCall

  return _Timed


def DeriveKeyFromStaticPassword(str_password: str, /) -> bytes:
  """Derive crypto key using string password.

  This is, purposefully, a very costly operation that should be cheap to execute once
  after the user typed a password, but costly for an attacker to run a dictionary campaign on.
  We do not use salt (or, more precisely, we use a fixed salt), as this is meant for direct use,
  not to store the key in a DB. To compensate, the number o iterations is set especially high:
  on the computer this was developed it takes ~1 sec to execute and is almost triple the
  recommended amount of 600,000 (see https://en.wikipedia.org/wiki/PBKDF2).

  The salt and the iteration number were randomly generated when this method was written
  so as to be unique to this implementation and not a standard one that can have a standard
  dictionary (i.e. attacks would have to generate a dictionary specific to this implementation).
  ON THE OTHER HAND, this only serves the purpose of generating keys from static passwords.
  NEVER use this method to save a database of keys. ONLY use it for direct user input.

  Docs: https://cryptography.io/en/latest/

  Args:
    str_password: Non-empty string password

  Returns:
    Fernet crypto key to use (URL-safe base64-encoded 32-byte key)

  Raises:
    Error: empty password
  """
  if not str_password or not str_password.strip():
    raise Error('Empty passwords not allowed, for safety reasons')
  kdf = hazmat_pbkdf2.PBKDF2HMAC(
      algorithm=hazmat_hashes.SHA256(),
      length=32,
      salt=b'\xda4,92\x80\x88\xf1\xc8\x18x@Q\x95*&',  # fixed salt: do NOT ever change!
      iterations=1745202)                             # fixed iterations: do NOT ever change!
  crypto_key: bytes = kdf.derive(str_password.encode('utf-8'))
  return base64.urlsafe_b64encode(crypto_key)


def Encrypt(plaintext: bytes, key: bytes, /) -> bytes:
  """Encryption wrapper."""
  return bin_fernet.BinaryFernet(key).encrypt(plaintext)


def Decrypt(ciphertext: bytes, key: bytes, /) -> bytes:
  """Decryption wrapper."""
  return bin_fernet.BinaryFernet(key).decrypt(ciphertext)


class BlockEncoder256:
  """The simplest encryption possible (UNSAFE if misused): 256 bit block AES256-ECB, 256 bit key.

  Please DO **NOT** use this for regular cryptography. For regular crypto use Encrypt()/Decrypt().
  This class was specifically built to encode/decode SHA-256 hashes using a pre-existing key.

  Docs: https://cryptography.io/en/latest/
  """

  def __init__(self, key256: bytes, /) -> None:
    """Construct.

    Args:
      key256: 256 bits (32 bytes) of key material

    Raises:
      Error: invalid key
    """
    if len(key256) != 32:
      raise Error(f'Key must be 256 bits (32 bytes) long, got {len(key256)}')
    self._cipher = ciphers.Cipher(algorithms.AES256(key256), modes.ECB())  # nosec

  def EncryptBlock256(self, plaintext256: bytes, /) -> bytes:
    """Encrypt a 256 bits block."""
    if len(plaintext256) != 32:
      raise Error(f'Plaintext must be 256 bits (32 bytes) long, got {len(plaintext256)}')
    encoder: ciphers.CipherContext = self._cipher.encryptor()  # cspell:disable-line
    return encoder.update(plaintext256) + encoder.finalize()

  def DecryptBlock256(self, ciphertext256: bytes, /) -> bytes:
    """Decrypt a 256 bits block."""
    if len(ciphertext256) != 32:
      raise Error(f'Ciphertext must be 256 bits (32 bytes) long, got {len(ciphertext256)}')
    encoder: ciphers.CipherContext = self._cipher.decryptor()  # cspell:disable-line
    return encoder.update(ciphertext256) + encoder.finalize()

  def EncryptHexdigest256(self, plaintext_hexdigest: str, /) -> str:
    """Encrypt a 256 bits hexadecimal block, outputting also a 256 bits hexadecimal."""
    return self.EncryptBlock256(bytes.fromhex(plaintext_hexdigest)).hex()

  def DecryptHexdigest256(self, ciphertext_hexdigest: str, /) -> str:
    """Decrypt a 256 bits hexadecimal block, outputting also a 256 bits hexadecimal."""
    return self.DecryptBlock256(bytes.fromhex(ciphertext_hexdigest)).hex()


def BinSerialize(
    obj: Any, /, *, file_path: str | None = None,
    compress: bool = True, key: bytes | None = None) -> bytes:
  """Serialize a Python object into a BLOB.

  If encryption is "on", note that the original Fernet deals in URL-safe base64, but we have a
  copy here (bin_fernet.BinaryFernet) that deals in raw bytes.

  Args:
    obj: Any serializable Python object
    file_path: (default None) File full path to optionally save the data to;
        IO failures will be logged and ignored
    compress: (default True) Compress before saving?
    key: (default None) If given will be interpreted as a Fernet crypto key to use
        (URL-safe base64-encoded 32-byte key; use DeriveKeyFromStaticPassword() to get from string)

  Returns:
    Serialized binary data (bytes) corresponding to obj
  """
  # serialize
  with Timer() as tm_pickle:
    s_obj: bytes = pickle.dumps(obj, protocol=-1)
  # compress, if needed
  with Timer() as tm_compress:
    c_obj: bytes = bz2.compress(s_obj, 9) if compress else s_obj
  # encrypt, if needed
  with Timer() as tm_crypto:
    e_obj: bytes = c_obj if key is None else Encrypt(c_obj, key)
  # output some logs, with measurements
  logging.info(
      'SERIALIZATION: %s serial (%s pickle)%s%s',
      HumanizedBytes(len(s_obj)), tm_pickle.readable,
      f'; {HumanizedBytes(len(c_obj))} compressed ({tm_compress.readable})' if compress else '',
      '' if key is None else f'; {HumanizedBytes(len(e_obj))} encrypted ({tm_crypto.readable})')
  # optionally save to disk
  if file_path is not None:
    with Timer() as tm_save:
      with open(file_path, 'wb') as file_obj:
        file_obj.write(e_obj)
    logging.info('Bin file saved: %r (%s)', file_path, tm_save.readable)
  return e_obj


def BinDeSerialize(
    *, data: bytes | None = None, file_path: str | None = None,
    compress: bool = True, key: bytes | None = None) -> Any:
  """De-Serializes a BLOB back to a Python object.

  If encryption is "on", note that the original Fernet deals in URL-safe base64, but we have a
  copy here (bin_fernet.BinaryFernet) that deals in raw bytes.

  Args:
    data: (default None) BLOB (binary data string)
    file_path: (default None) File full path to optionally load the data from;
        if you use this option, then `data` WILL BE IGNORED and errors will be fatal
    compress: (default True) Compress before saving?
    key: (default None) If given will be interpreted as a Fernet crypto key to use
        (URL-safe base64-encoded 32-byte key; use DeriveKeyFromStaticPassword() to get from string)

  Returns:
    De-Serialized Python object corresponding to data; None if `file_name` is
    given and does not exist in config dir

  Raises:
    Error: file not found
  """
  if file_path is None:
    # no disk operation needed
    if data is None:
      return None
    e_obj: bytes = data
  else:
    # load data from disk
    if not os.path.exists(file_path):
      raise Error(f'File {file_path!r} not found')
    with Timer() as tm_load:
      with open(file_path, 'rb') as file_obj:
        e_obj = file_obj.read()
    logging.info('Read bin file: %r (%s)', file_path, tm_load.readable)
  # we have the data; decrypt, if needed
  with Timer() as tm_crypto:
    c_obj: bytes = e_obj if key is None else Decrypt(e_obj, key)
  # decompress, if needed
  with Timer() as tm_decompress:
    s_obj: bytes = bz2.decompress(c_obj) if compress else c_obj
  # create the actual object
  with Timer() as tm_pickle:
    obj: Any = pickle.loads(s_obj)  # nosec - this is dangerous!
  # output some logs, with measurements
  logging.info(
      'DE-SERIALIZATION: %s serial (%s pickle)%s%s',
      HumanizedBytes(len(s_obj)), tm_pickle.readable,
      f'; {HumanizedBytes(len(c_obj))} compressed ({tm_decompress.readable})' if compress else '',
      '' if key is None else f'; {HumanizedBytes(len(e_obj))} encrypted ({tm_crypto.readable})')
  return obj
