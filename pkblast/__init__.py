import typing
from collections.abc import ByteString
from io import BytesIO, IOBase
from mmap import mmap
from warnings import warn

from .BlastError import BlastError
from .ctypes import _decompressBytes, _decompressStream

__all__ = ("decompressStreamToStream", "decompressStreamToBytes", "decompressBytesWholeToStream", "decompressBytesWholeToBytes", "decompressBytesChunkedToStream", "decompressBytesChunkedToBytes", "decompress", "DEFAULT_CHUNK_SIZE")

DEFAULT_CHUNK_SIZE = 16384


def decompressStreamToStream(inputStream: IOBase, outputStream: IOBase, chunkSize: int = DEFAULT_CHUNK_SIZE) -> (int, IOBase):
	"""Used to do streaming decompression. The first arg is the stream to read from, the second ard is the stream to write to.
	May be a memory map. `chunkSize` is the hint"""

	errorCode, left = _decompressStream(inputStream, outputStream, chunkSize=chunkSize)

	if errorCode:
		raise Exception(BlastError(errorCode))

	return left.value, outputStream


def decompressStreamToBytes(inputStream: IOBase, chunkSize: int = DEFAULT_CHUNK_SIZE) -> (int, ByteString):
	"""Decompresses `inputStream` into `outputStream`. Processes the whole data. You should use it instead of `decompressBytesChunkedToStream`, if it is possible."""
	with BytesIO() as outputStream:
		left, _ = decompressStreamToStream(inputStream, outputStream, chunkSize)
		return left, outputStream.getvalue()


def decompressBytesWholeToStream(compressed: ByteString, outputStream: IOBase) -> (int, IOBase):
	"""Decompresses `compressed` into `outputStream`. Processes the whole data. You should use it instead of `decompressBytesChunkedToStream`, if it is possible."""
	errorCode, left = _decompressBytes(compressed, outputStream)

	if errorCode:
		raise Exception(BlastError(errorCode))

	return left.value, outputStream


def decompressBytesWholeToBytes(compressed: ByteString) -> (int, ByteString):
	"""Decompresses `compressed` and returns tuple (remaining, decompressed)`. Processes the whole data. You should use it instead of `decompressBytesChunkedToStream`, if it is possible."""
	with BytesIO() as outputStream:
		left, _ = decompressBytesWholeToStream(compressed, outputStream)
		return left, outputStream.getvalue()


def decompressBytesChunkedToStream(compressed: ByteString, outputStream: IOBase, chunkSize: int = DEFAULT_CHUNK_SIZE) -> (int, IOBase):
	"""Decompresses `compressed` into `outputStream`. Processes the `compressed` the same way `decompressStreamToStream` does. In fact it is just a wrapper around it and `BytesIO`. Has bigger overhead than `decompressBytesWholeToStream` for the data that is already in memory: first it copies the data into `BytesIO`, then it allocates space for chunks, then it copies data from there into chunks, each copying has overhead of calling from C into python."""
	_efficiencyDeprecationMessage(decompressBytesChunkedToStream, decompressBytesWholeToStream)
	chunkSize = min(chunkSize, len(compressed))
	with BytesIO(compressed) as inputStream:
		return decompressStreamToStream(inputStream, outputStream, chunkSize=chunkSize)


def decompressBytesChunkedToBytes(compressed: ByteString, chunkSize: int = DEFAULT_CHUNK_SIZE) -> (int, ByteString):
	"""Decompresses `compressed` into `bytes`. Processes the `compressed` the same way `decompressStreamToStream` does. In fact it is just a wrapper around it and `BytesIO`. Has bigger overhead than `decompressBytesWholeToStream` for the data that is already in memory: first it copies the data into `BytesIO`, then it allocates space for chunks, then it copies data from there into chunks, each copying has overhead of calling from C into python."""
	_efficiencyDeprecationMessage(decompressBytesChunkedToBytes, decompressBytesWholeToBytes)
	with BytesIO() as outputStream:
		left, _ = decompressBytesChunkedToStream(compressed, outputStream, chunkSize)
		return left, outputStream.getvalue()


def _efficiencyDeprecationMessage(calledFunc, func) -> None:
	warn("It is inefficient to use `" + calledFunc.__name__ + "`. Use `" + func.__name__ + "` for this use case")


_functionsUseCaseMapping = (
	decompressStreamToStream,
	decompressBytesWholeToStream,
	decompressStreamToBytes,
	decompressBytesWholeToBytes,
)


def decompress(compressed: typing.Union[ByteString, IOBase], outputStream: typing.Optional[IOBase] = None, chunkSize: int = DEFAULT_CHUNK_SIZE) -> (int, typing.Union[ByteString, IOBase]):
	"""A convenience function. It is better to use the more specialized ones since they have less overhead. It decompresses `compressed` into `outputStream` and returns a tuple `(left, output)`.
	`compressed` can be either a stream, or `bytes`-like stuff.
	If `outputStream` is None, then it returns `bytes`. If `outputStream` is a stream, it writes into it.
	`left` returned is the count of bytes in the array/stream that weren't processed."""

	isOutputBytes = outputStream is None
	isInputBytes = isinstance(compressed, (ByteString, mmap))
	selector = isOutputBytes << 1 | int(isInputBytes)
	func = _functionsUseCaseMapping[selector]
	argz = [compressed]
	if not isOutputBytes:
		argz.append(outputStream)
	if not isInputBytes:
		argz.append(chunkSize)
	_efficiencyDeprecationMessage(decompress, func)
	return func(*argz)
