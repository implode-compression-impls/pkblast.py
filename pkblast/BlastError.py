from enum import IntEnum


class BlastError(IntEnum):
	success = 0

	# If there is not enough input available or there is not enough output space, then a positive error is returned.
	outputError = 1
	inputExhausted = 2

	# Errors in the source data
	wrongLiteralFlag = -1  # literal flag not zero or one
	wrongDictionary = -2  # dictionary size not in 4..6
	distanceTooBig = -3  # distance is too far back
