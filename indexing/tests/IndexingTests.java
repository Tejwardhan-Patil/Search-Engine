package indexing.tests;

import indexing.inverted_index.inverted_index_builder;
import indexing.inverted_index.CompressedInvertedIndex;
import indexing.index_storage.IndexFileManager;
import indexing.index_storage.IndexSharding;
import indexing.TermFrequency;
import indexing.DocumentFrequency;
import indexing.TfidfCalculator;
import org.junit.Before;
import org.junit.Test;

import java.io.File;
import java.util.List;
import java.util.Map;

import static org.junit.Assert.*;

/**
 * Unit tests for the Indexing components.
 */
public class IndexingTests {

    private inverted_index_builder invertedIndexBuilder;
    private CompressedInvertedIndex compressedInvertedIndex;
    private IndexFileManager indexFileManager;
    private IndexSharding indexSharding;
    private TermFrequency termFrequency;
    private DocumentFrequency documentFrequency;
    private TfidfCalculator tfidfCalculator;

    @Before
    public void setup() {
        invertedIndexBuilder = new inverted_index_builder();
        compressedInvertedIndex = new CompressedInvertedIndex();
        indexFileManager = new IndexFileManager();
        indexSharding = new IndexSharding();
        termFrequency = new TermFrequency();
        documentFrequency = new DocumentFrequency();
        tfidfCalculator = new TfidfCalculator();
    }

    @Test
    public void testInvertedIndexBuilder() {
        // Build inverted index from sample data
        String[] documents = {
            "This is a sample document.",
            "This document is another example.",
            "Indexing is fun."
        };

        Map<String, List<Integer>> index = invertedIndexBuilder.buildIndex(documents);

        // Test for correct indexing
        assertTrue(index.containsKey("this"));
        assertTrue(index.containsKey("document"));
        assertFalse(index.containsKey("missing"));

        // Test term positions
        assertEquals(2, index.get("this").size());
        assertEquals(1, index.get("fun").size());
    }

    @Test
    public void testCompressedInvertedIndex() {
        // Test compression and decompression of the index
        String[] terms = { "apple", "banana", "cherry" };
        int[] positions = { 1, 5, 12 };

        byte[] compressed = compressedInvertedIndex.compress(terms, positions);
        Map<String, List<Integer>> decompressed = compressedInvertedIndex.decompress(compressed);

        assertEquals(3, decompressed.size());
        assertEquals(1, (int) decompressed.get("apple").get(0));
        assertEquals(5, (int) decompressed.get("banana").get(0));
    }

    @Test
    public void testIndexFileManager() {
        // Test storing and retrieving the index
        String filePath = "test_index_file";
        Map<String, List<Integer>> index = invertedIndexBuilder.buildIndex(new String[] {
            "quick brown fox",
            "lazy dog",
            "brown dog"
        });

        indexFileManager.saveIndex(index, filePath);

        Map<String, List<Integer>> loadedIndex = indexFileManager.loadIndex(filePath);
        assertEquals(index, loadedIndex);

        // Cleanup
        new File(filePath).delete();
    }

    @Test
    public void testIndexSharding() {
        // Test sharding the index across multiple nodes
        Map<String, List<Integer>> index = invertedIndexBuilder.buildIndex(new String[] {
            "apple banana",
            "banana cherry",
            "cherry apple"
        });

        List<Map<String, List<Integer>>> shards = indexSharding.shardIndex(index, 2);

        assertEquals(2, shards.size());
        assertTrue(shards.get(0).containsKey("apple"));
        assertTrue(shards.get(1).containsKey("cherry"));
    }

    @Test
    public void testTermFrequency() {
        // Test calculation of term frequency
        String document = "apple banana apple cherry apple";
        Map<String, Integer> tf = termFrequency.calculate(document);

        assertEquals(3, (int) tf.get("apple"));
        assertEquals(1, (int) tf.get("banana"));
        assertNull(tf.get("missing"));
    }

    @Test
    public void testDocumentFrequency() {
        // Test calculation of document frequency across multiple documents
        String[] documents = {
            "apple banana",
            "banana cherry",
            "cherry apple"
        };

        Map<String, Integer> df = documentFrequency.calculate(documents);

        assertEquals(2, (int) df.get("apple"));
        assertEquals(2, (int) df.get("banana"));
        assertEquals(2, (int) df.get("cherry"));
    }

    @Test
    public void testTfidfCalculator() {
        // Test calculation of TF-IDF scores
        String[] documents = {
            "apple banana",
            "banana cherry",
            "cherry apple"
        };

        Map<String, Integer> tf = termFrequency.calculate(documents[0]);
        Map<String, Integer> df = documentFrequency.calculate(documents);

        Map<String, Double> tfidf = tfidfCalculator.calculate(tf, df, documents.length);

        assertTrue(tfidf.get("apple") > 0.0);
        assertTrue(tfidf.get("banana") > 0.0);
    }

    @Test
    public void testEmptyDocument() {
        // Test with empty document input
        String emptyDoc = "";
        Map<String, Integer> tf = termFrequency.calculate(emptyDoc);
        Map<String, List<Integer>> index = invertedIndexBuilder.buildIndex(new String[] { emptyDoc });

        assertTrue(tf.isEmpty());
        assertTrue(index.isEmpty());
    }

    @Test
    public void testSingleWordDocument() {
        // Test with a single-word document
        String singleWordDoc = "apple";
        Map<String, Integer> tf = termFrequency.calculate(singleWordDoc);
        Map<String, List<Integer>> index = invertedIndexBuilder.buildIndex(new String[] { singleWordDoc });

        assertEquals(1, (int) tf.get("apple"));
        assertEquals(1, index.size());
    }

    @Test
    public void testMultipleTermFrequency() {
        // Test term frequency for multiple documents
        String[] documents = {
            "apple banana",
            "banana banana",
            "apple cherry"
        };

        Map<String, Integer> tfDoc1 = termFrequency.calculate(documents[0]);
        Map<String, Integer> tfDoc2 = termFrequency.calculate(documents[1]);

        assertEquals(1, (int) tfDoc1.get("apple"));
        assertEquals(2, (int) tfDoc2.get("banana"));
    }
}