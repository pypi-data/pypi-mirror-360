import unittest
from atlaz.codeGen.generate_input.directory_tree import build_directory_tree_string

class TestBuildDirectoryTreeString(unittest.TestCase):
    def test_empty_list(self):
        """Test with an empty list of selected files."""
        selected_files = []
        expected = ""
        self.assertEqual(build_directory_tree_string(selected_files), expected)

    def test_single_file(self):
        """Test with a single file."""
        selected_files = ["file.txt"]
        expected = "└── file.txt"
        self.assertEqual(build_directory_tree_string(selected_files), expected)

    def test_nested_directories(self):
        """Test with nested directories containing files."""
        selected_files = [
            "dir1/dir2/file1.txt",
            "dir1/dir2/file2.txt",
            "dir1/dir3/file3.txt"
        ]
        expected = (
            "└── dir1\n"
            "    ├── dir2\n"
            "    │   ├── file1.txt\n"
            "    │   └── file2.txt\n"
            "    └── dir3\n"
            "        └── file3.txt"
        )
        self.assertEqual(build_directory_tree_string(selected_files), expected)

    def test_conflicting_file_and_directory(self):
        """Test conflict where a path is both a file and a directory."""
        selected_files = [
            "dir1/file1.txt",
            "dir1/file1.txt/subfile.txt"  # Implies file1.txt is a directory
        ]
        with self.assertRaises(ValueError) as context:
            build_directory_tree_string(selected_files)
        self.assertIn("Conflict at 'file1.txt'", str(context.exception))

if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)

if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)
