#!/usr/bin/env python3
import mmap
import os
import sys
import unittest
from collections import OrderedDict
from pathlib import Path

from fileTestSuite.unittest import FileTestSuiteTestCaseMixin

dict = OrderedDict

thisDir = Path(__file__).resolve().absolute().parent
repoRootDir = thisDir.parent

sys.path.insert(0, str(repoRootDir))

from pkblast import decompress, decompressBytesChunkedToBytes, decompressBytesWholeToBytes, decompressStreamToBytes

class Tests(unittest.TestCase, FileTestSuiteTestCaseMixin):
	@property
	def fileTestSuiteDir(self) -> Path:
		return thisDir / "testDataset"

	def _testProcessorImpl(self, challFile: Path, respFile: Path, paramsDict=None) -> None:
		self._testChallengeResponsePair(respFile.read_bytes(), challFile.read_bytes())

	def _testChallengeResponsePair(self, chall: bytes, resp: bytes):
		self._testPack(chall, resp)

		#with mmap.mmap(-1, len(chall), access=mmap.ACCESS_READ|mmap.ACCESS_WRITE) as mm:
		#	mm.write(chall)
		#	mm.seek(0)
		#	self._testPack(mm, resp)

	def _testPack(self, chall: bytes, resp: bytes):
		tpName = chall.__class__.__name__
		with self.subTest(mode="decompress " + tpName):
			self.assertEqual((0, resp), decompress(chall))
		with self.subTest(mode="decompressBytesChunkedToBytes " + tpName):
			self.assertEqual((0, resp), decompressBytesChunkedToBytes(chall))
		with self.subTest(mode="decompressBytesWholeToBytes " + tpName):
			self.assertEqual((0, resp), decompressBytesWholeToBytes(chall))


if __name__ == "__main__":
	unittest.main()
