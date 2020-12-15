import ctypes
import platform
from collections.abc import ByteString
from functools import partial
from mmap import mmap

__all__ = ("_decompressBytes", "_decompressStream")

#                                            how                   buf
blast_in = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.POINTER(None), ctypes.POINTER(ctypes.POINTER(ctypes.c_ubyte)))
#                                            how                   buf                             len
blast_out = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.POINTER(None), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_uint32)


lib = None


def blast(infun: blast_in, inhow: ctypes.c_void_p, outfun: blast_out, outhow: ctypes.c_void_p, left: ctypes.POINTER(ctypes.c_uint32) = None, optionalInputArrayAndOutputLeftInfoPtr: ctypes.POINTER(ctypes.POINTER(ctypes.c_byte)) = None) -> ctypes.c_int:
	"""If there is any unused input, *left is set to the number of bytes that were read and *in points to them.  Otherwise *left is set to zero and *in is set to NULL.  If left or in are NULL, then they are not set."""

	return lib.blast(infun, inhow, outfun, outhow, left, optionalInputArrayAndOutputLeftInfoPtr)


def _initLibrary():
	if platform.system() == "Windows":
		lib = ctypes.CDLL("libblast.dll")
	else:
		lib = ctypes.CDLL("libblast.so")

	lib.blast.argtypes = [blast.__annotations__[argName] for argName in blast.__code__.co_varnames[: blast.__code__.co_argcount]]
	lib.blast.restype = blast.__annotations__["return"]
	return lib


lib = _initLibrary()


def outputCallback(outputStream, how, buf, l):
	return outputStream.write(bytes(buf[:l])) != l


def inputCallbackStream(inputStream, hold, holdPtr, how, buf):
	countRead = inputStream.readinto(hold)
	buf[0] = holdPtr
	return countRead


def _decompressStream(inputStream, outputStream, chunkSize: int = 16384) -> (int, int):
	hold = (ctypes.c_byte * chunkSize).from_buffer(bytearray(chunkSize))
	holdPtr = ctypes.cast(ctypes.pointer(hold), ctypes.POINTER(ctypes.c_ubyte))

	left = ctypes.c_uint32(0)

	return (
		blast(
			blast_in(partial(inputCallbackStream, inputStream, hold, holdPtr)), None,
			blast_out(partial(outputCallback, outputStream)), None,
			ctypes.byref(left), None
		),
		left
	)


def inputCallbackBytes(inputBytesPtr, l, how, buf):
	buf[0] = inputBytesPtr
	return l


def _decompressBytes(inputBytes: ByteString, outputStream) -> (int, int):
	if isinstance(inputBytes, bytes):
		inputBytesC = ctypes.create_string_buffer(inputBytes)
	else:
		inputBytesC = (ctypes.c_byte * len(inputBytes)).from_buffer(inputBytes)
	inputBytesPtr = ctypes.cast(ctypes.pointer(inputBytesC), ctypes.POINTER(ctypes.c_ubyte))
	left = ctypes.c_uint32(0)

	return (
		blast(
			blast_in(partial(inputCallbackBytes, inputBytesPtr, len(inputBytes))), None,
			blast_out(partial(outputCallback, outputStream)), None,
			ctypes.byref(left), None
		),
		left
	)
