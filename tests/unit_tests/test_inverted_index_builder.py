import unittest
import subprocess
import json
import os

class TestInvertedIndexBuilder(unittest.TestCase):
    
    def setUp(self):
        # Path to the compiled Java class or jar file
        self.java_class_path = "indexing/inverted_index/InvertedIndexBuilder"
        self.java_command = ["java", self.java_class_path]
    
    def test_add_document(self):
        # Test adding a document to the index using subprocess
        doc_id = 1
        content = "This is a sample document"
        result = subprocess.run(self.java_command + ["addDocument", str(doc_id), content], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        output = result.stdout.strip()
        self.assertTrue("Document added" in output)
    
    def test_get_index(self):
        # Test getting the inverted index using subprocess
        result = subprocess.run(self.java_command + ["getIndex"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        output = result.stdout.strip()
        index = json.loads(output)
        self.assertIsInstance(index, dict)
        self.assertIn("sample", index)
    
    def test_index_content_case_insensitive(self):
        # Test adding case-insensitive content to the index
        doc_id = 2
        content = "Test test TEST"
        subprocess.run(self.java_command + ["addDocument", str(doc_id), content], capture_output=True, text=True)
        result = subprocess.run(self.java_command + ["getIndex"], capture_output=True, text=True)
        output = result.stdout.strip()
        index = json.loads(output)
        self.assertIn("test", index)
        self.assertEqual(len(index["test"]), 1)  # Case-insensitive check
    
    def test_remove_document(self):
        # Test removing a document from the index using subprocess
        doc_id = 3
        content = "Document to be removed"
        subprocess.run(self.java_command + ["addDocument", str(doc_id), content], capture_output=True, text=True)
        result = subprocess.run(self.java_command + ["removeDocument", str(doc_id)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        output = result.stdout.strip()
        self.assertIn("Document removed", output)
    
    def test_index_persistence(self):
        # Test saving and loading the index from a file using subprocess
        doc_id = 4
        content = "Persistent document"
        subprocess.run(self.java_command + ["addDocument", str(doc_id), content], capture_output=True, text=True)
        subprocess.run(self.java_command + ["saveIndex", "test_index.json"], capture_output=True, text=True)
        
        # Clear current index and load the saved one
        subprocess.run(self.java_command + ["clearIndex"], capture_output=True, text=True)
        subprocess.run(self.java_command + ["loadIndex", "test_index.json"], capture_output=True, text=True)
        
        result = subprocess.run(self.java_command + ["getIndex"], capture_output=True, text=True)
        output = result.stdout.strip()
        index = json.loads(output)
        self.assertIn("persistent", index)
    
    def test_large_document(self):
        # Test adding a large document to the index
        doc_id = 5
        content = "word " * 10000  # Very large document
        result = subprocess.run(self.java_command + ["addDocument", str(doc_id), content], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        output = result.stdout.strip()
        self.assertIn("Document added", output)
    
    def test_invalid_document(self):
        # Test invalid document handling (null content)
        doc_id = 6
        content = None
        result = subprocess.run(self.java_command + ["addDocument", str(doc_id), str(content)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)  # Expect an error
        output = result.stdout.strip()
        self.assertIn("Invalid document", output)
    
    def test_parallel_processing(self):
        # Test parallel processing of documents using subprocess
        doc1_id = 7
        doc2_id = 8
        content1 = "Parallel document one"
        content2 = "Parallel document two"
        
        # Run parallel processes
        proc1 = subprocess.Popen(self.java_command + ["addDocument", str(doc1_id), content1], stdout=subprocess.PIPE, text=True)
        proc2 = subprocess.Popen(self.java_command + ["addDocument", str(doc2_id), content2], stdout=subprocess.PIPE, text=True)
        
        out1, _ = proc1.communicate()
        out2, _ = proc2.communicate()
        
        self.assertIn("Document added", out1.strip())
        self.assertIn("Document added", out2.strip())
    
    def tearDown(self):
        # Clean up after tests, clear the index
        subprocess.run(self.java_command + ["clearIndex"], capture_output=True, text=True)

if __name__ == "__main__":
    unittest.main()