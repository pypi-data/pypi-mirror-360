import unittest
import numpy as np

# Import from sibling directory.
import sys
import os

# Add the parent directory (containing differintP) to the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from differintP.core import *


from .__init__ import test_N

# Define constants to be used in tests.
sqrtpi2 = 0.88622692545275794

# Get results for checking accuracy.
GL_r = GL(0.5, lambda x: np.sqrt(x), 0, 1, test_N)
GL_result = GL_r[-1]

class TestAlgorithmsAccuray(unittest.TestCase):
    """Tests for algorithm accuracy."""


    def test_GL_accuracy_sqrt(self):
        self.assertTrue(abs(GL_result - sqrtpi2) <= 1e-4)


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)

    # Ensure all docstring examples work.
    import doctest

    doctest.testmod()
