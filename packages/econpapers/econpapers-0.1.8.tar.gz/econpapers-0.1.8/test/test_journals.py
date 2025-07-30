import unittest
import sys
import os

# Add the src folder to sys.path to import module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from econpapers import journals

# Get the DataFrame for the test
journal_test = journals.papers_dataframe(['Acta Economica Et Turistica'])
journ_length = 100  #number of papers as of 07/07/2025, adjust if needed


class JournalTest(unittest.TestCase):
    
    def test_all_rows(self):
        """Check if the number of papers is as expected."""
        self.assertEqual(len(journal_test), journ_length, "Unexpected number of rows in DataFrame")

    def test_all_cols(self):
        """Ensure all metadata columns are present."""
        self.assertEqual(len(journal_test.columns), 7, "DataFrame should have 7 columns")


if __name__ == '__main__':
    unittest.main()
