import unittest
import os
from read_record import RecordReader, Record

class TestRecordReader(unittest.TestCase):
    """Unit tests for RecordReader module."""

    def setUp(self):
        """Set up test environment."""
        self.test_path = "D:\\ECG DB\\"
        self.test_number = "00"
        self.test_channel = 0
        self.test_sampfrom = 0
        self.test_sampto = 1000

    def test_read_valid_record(self):
        """Test reading a valid ECG record."""
        record = RecordReader.read(self.test_path, self.test_number, self.test_channel, self.test_sampfrom, self.test_sampto)
        
        self.assertIsInstance(record, Record)
        self.assertEqual(record['parent'], self.test_number)
        self.assertIsNotNone(record['signal'])
        self.assertIsNotNone(record['symbol'])
        self.assertIsNotNone(record['aux'])
        self.assertIsNotNone(record['sample'])
        self.assertIsNotNone(record['label'])
        self.assertIsNotNone(record['sampling_frequency'])

    def test_read_invalid_path(self):
        """Test reading a record with invalid path."""
        with self.assertRaises(ValueError):
            RecordReader.read("invalid_path", self.test_number, self.test_channel, self.test_sampfrom, self.test_sampto)

    def test_read_invalid_record(self):
        """Test reading an invalid ECG record."""
        with self.assertRaises(ValueError):
            RecordReader.read(self.test_path, "invalid_record", self.test_channel, self.test_sampfrom, self.test_sampto)

if __name__ == '__main__':
    unittest.main()
