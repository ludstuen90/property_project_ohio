from django.test import TestCase

# Create your tests here.


import unittest
import utils


class TestAdd(unittest.TestCase):

    def test_add_function_works(self):
        # Capture the results of the function
        result = utils.add_function(5, 6)
        # Check for expected output
        self.assertEqual(11, result)


# Run the tests
if __name__ == '__main__':
    unittest.main()
