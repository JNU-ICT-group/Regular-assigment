import sys
import unittest

sys.path.append('.\\lib\\')
from lib import (byteSourceTest, byteSourceCoderTest, repetitionCoderTest, byteChannelTest)

byteSourceTest.test_flow()
byteSourceCoderTest.test_flow()
unittest.main(repetitionCoderTest, argv=['repetitionCoderTest'], exit=False)
byteChannelTest.test_flow()

