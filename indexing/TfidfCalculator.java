package indexing;

import java.util.HashMap;
import java.util.Map;

public class TfidfCalculator {

    // Stores the term frequency (TF) for each term in each document
    private Map<String, Map<String, Double>> termFrequencies; // document -> (term -> TF)
    
    // Stores the document frequency (DF) for each term across the document corpus
    private Map<String, Integer> documentFrequencies; // term -> DF
    
    // Total number of documents in the corpus
    private int totalDocuments;

    public TfidfCalculator(Map<String, Map<String, Double>> termFrequencies, Map<String, Integer> documentFrequencies, int totalDocuments) {
        this.termFrequencies = termFrequencies;
        this.documentFrequencies = documentFrequencies;
        this.totalDocuments = totalDocuments;
    }

    /**
     * Compute the TF-IDF score for each term in each document.
     *
     * @return A map where each document is mapped to its corresponding TF-IDF scores for each term.
     */
    public Map<String, Map<String, Double>> computeTfidfScores() {
        Map<String, Map<String, Double>> tfidfScores = new HashMap<>();

        for (String document : termFrequencies.keySet()) {
            Map<String, Double> tfidfForDoc = new HashMap<>();
            Map<String, Double> termsInDoc = termFrequencies.get(document);

            for (String term : termsInDoc.keySet()) {
                double tf = termsInDoc.get(term);
                double idf = computeIdf(term);
                double tfidf = tf * idf;
                tfidfForDoc.put(term, tfidf);
            }

            tfidfScores.put(document, tfidfForDoc);
        }

        return tfidfScores;
    }

    /**
     * Computes the Inverse Document Frequency (IDF) of a term.
     * IDF = log(Total Documents / Document Frequency of the term)
     *
     * @param term The term whose IDF is to be calculated.
     * @return The IDF value for the given term.
     */
    private double computeIdf(String term) {
        int df = documentFrequencies.getOrDefault(term, 1);
        return Math.log((double) totalDocuments / df);
    }

    /**
     * Returns the term frequency (TF) for a given term in a specific document.
     *
     * @param document The document name or ID.
     * @param term     The term whose TF is to be retrieved.
     * @return The term frequency of the term in the document.
     */
    public double getTermFrequency(String document, String term) {
        return termFrequencies.getOrDefault(document, new HashMap<>()).getOrDefault(term, 0.0);
    }

    /**
     * Returns the document frequency (DF) of a term across the entire corpus.
     *
     * @param term The term whose DF is to be retrieved.
     * @return The document frequency of the term.
     */
    public int getDocumentFrequency(String term) {
        return documentFrequencies.getOrDefault(term, 0);
    }

    /**
     * Print the TF-IDF scores for each document.
     */
    public void printTfidfScores() {
        Map<String, Map<String, Double>> tfidfScores = computeTfidfScores();

        for (String document : tfidfScores.keySet()) {
            System.out.println("Document: " + document);
            Map<String, Double> scores = tfidfScores.get(document);
            for (String term : scores.keySet()) {
                System.out.println("Term: " + term + ", TF-IDF: " + scores.get(term));
            }
            System.out.println();
        }
    }

    public static void main(String[] args) {
        // Data setup
        Map<String, Map<String, Double>> termFrequencies = new HashMap<>();
        Map<String, Integer> documentFrequencies = new HashMap<>();
        int totalDocuments = 5;

        // Document 1
        Map<String, Double> doc1Terms = new HashMap<>();
        doc1Terms.put("search", 0.1);
        doc1Terms.put("engine", 0.2);
        termFrequencies.put("doc1", doc1Terms);

        // Document 2
        Map<String, Double> doc2Terms = new HashMap<>();
        doc2Terms.put("search", 0.3);
        doc2Terms.put("index", 0.4);
        termFrequencies.put("doc2", doc2Terms);

        // Document Frequencies
        documentFrequencies.put("search", 2);
        documentFrequencies.put("engine", 1);
        documentFrequencies.put("index", 1);

        TfidfCalculator calculator = new TfidfCalculator(termFrequencies, documentFrequencies, totalDocuments);
        calculator.printTfidfScores();
    }
}