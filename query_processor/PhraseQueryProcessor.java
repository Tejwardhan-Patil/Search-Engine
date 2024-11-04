package query_processor;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Class for processing phrase queries.
 * This class handles exact phrase matching queries, ensuring that the sequence of terms appears in the correct order in the documents.
 */
public class PhraseQueryProcessor {

    // Inverted index storing term positions within documents.
    private final Map<String, Map<Integer, List<Integer>>> invertedIndex;

    /**
     * Constructor for PhraseQueryProcessor.
     *
     * @param invertedIndex the inverted index where each term is mapped to a list of document IDs and their positions.
     */
    public PhraseQueryProcessor(Map<String, Map<Integer, List<Integer>>> invertedIndex) {
        this.invertedIndex = invertedIndex;
    }

    /**
     * Processes a phrase query and returns the list of document IDs where the phrase appears.
     *
     * @param phraseQuery the phrase query string to be searched in the documents.
     * @return list of document IDs that contain the exact phrase.
     */
    public List<Integer> processPhraseQuery(String phraseQuery) {
        // Split the phrase into individual terms
        String[] terms = phraseQuery.split("\\s+");

        if (terms.length == 0) {
            return new ArrayList<>();
        }

        // Retrieve the list of documents for the first term
        Map<Integer, List<Integer>> firstTermDocs = invertedIndex.get(terms[0]);
        if (firstTermDocs == null) {
            return new ArrayList<>();
        }

        // Iterate through each document where the first term appears
        List<Integer> matchingDocuments = new ArrayList<>();
        for (Map.Entry<Integer, List<Integer>> entry : firstTermDocs.entrySet()) {
            Integer docId = entry.getKey();
            List<Integer> positions = entry.getValue();

            // Check if the phrase exists in this document
            if (checkPhraseInDocument(docId, terms, positions)) {
                matchingDocuments.add(docId);
            }
        }

        return matchingDocuments;
    }

    /**
     * Checks if the entire phrase exists in the given document starting at one of the positions of the first term.
     *
     * @param docId the document ID to search for the phrase.
     * @param terms the terms of the phrase to search.
     * @param positions the positions of the first term in the document.
     * @return true if the phrase exists, false otherwise.
     */
    private boolean checkPhraseInDocument(int docId, String[] terms, List<Integer> positions) {
        // Iterate through the positions of the first term
        for (Integer position : positions) {
            boolean phraseFound = true;

            // Check the other terms of the phrase
            for (int i = 1; i < terms.length; i++) {
                String term = terms[i];
                Map<Integer, List<Integer>> termDocs = invertedIndex.get(term);

                // If the term is not in the index or not in the document, break
                if (termDocs == null || !termDocs.containsKey(docId)) {
                    phraseFound = false;
                    break;
                }

                // Check if the term appears at the correct position
                List<Integer> termPositions = termDocs.get(docId);
                if (!termPositions.contains(position + i)) {
                    phraseFound = false;
                    break;
                }
            }

            if (phraseFound) {
                return true;
            }
        }

        return false;
    }

    /**
     * Adds a new document to the inverted index.
     * This function is primarily for testing and extending the inverted index.
     *
     * @param docId   the document ID.
     * @param content the content of the document.
     */
    public void addDocument(int docId, String content) {
        String[] terms = content.split("\\s+");

        // Populate the inverted index with term positions
        for (int i = 0; i < terms.length; i++) {
            String term = terms[i];
            invertedIndex.putIfAbsent(term, new HashMap<>());
            invertedIndex.get(term).putIfAbsent(docId, new ArrayList<>());
            invertedIndex.get(term).get(docId).add(i);
        }
    }

    /**
     * Utility function to print the inverted index for debugging.
     */
    public void printInvertedIndex() {
        for (Map.Entry<String, Map<Integer, List<Integer>>> entry : invertedIndex.entrySet()) {
            System.out.println("Term: " + entry.getKey());
            for (Map.Entry<Integer, List<Integer>> docEntry : entry.getValue().entrySet()) {
                System.out.println("  Document ID: " + docEntry.getKey() + " Positions: " + docEntry.getValue());
            }
        }
    }

    public static void main(String[] args) {
        // Usage of the PhraseQueryProcessor

        // Inverted index
        Map<String, Map<Integer, List<Integer>>> invertedIndex = new HashMap<>();
        
        // Creating an instance of PhraseQueryProcessor
        PhraseQueryProcessor processor = new PhraseQueryProcessor(invertedIndex);
        
        // Adding documents to the inverted index
        processor.addDocument(1, "this is a sample document");
        processor.addDocument(2, "this is another example of a document");
        processor.addDocument(3, "sample document with phrase query");

        // Print the inverted index
        processor.printInvertedIndex();

        // Process a phrase query
        String phraseQuery = "sample document";
        List<Integer> results = processor.processPhraseQuery(phraseQuery);

        // Output the results
        System.out.println("Documents containing the phrase '" + phraseQuery + "': " + results);
    }
}