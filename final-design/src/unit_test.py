import os
import sys
import unittest

sys.path.append('.\\lib\\')
from lib import (byteSourceTest, byteSourceCoderTest, repetitionCoderTest, byteChannelTest, calcInfoTest)

byteSourceTest.test_flow()
unittest.main(byteSourceCoderTest, argv=['byteSourceCoderTest'], exit=False)
unittest.main(repetitionCoderTest, argv=['repetitionCoderTest'], exit=False)
byteChannelTest.test_flow()
unittest.main(calcInfoTest, argv=['calcInfoTest'], exit=False)

