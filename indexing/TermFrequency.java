package indexing;

import java.util.HashMap;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;

public class TermFrequency {
    private Map<String, Integer> termCounts;
    private Map<String, Double> termFrequencies;

    public TermFrequency() {
        termCounts = new HashMap<>();
        termFrequencies = new HashMap<>();
    }

    // Method to calculate term frequency for a single document
    public void calculateTermFrequency(String documentContent) {
        String[] terms = tokenize(documentContent);
        int totalTerms = terms.length;

        for (String term : terms) {
            term = normalize(term);
            if (term.isEmpty()) {
                continue;
            }
            termCounts.put(term, termCounts.getOrDefault(term, 0) + 1);
        }

        for (Map.Entry<String, Integer> entry : termCounts.entrySet()) {
            String term = entry.getKey();
            int count = entry.getValue();
            termFrequencies.put(term, (double) count / totalTerms);
        }
    }

    // Tokenization method to split document content into terms
    private String[] tokenize(String content) {
        return content.split("\\s+");
    }

    // Normalize terms to lowercase, remove punctuation, etc
    private String normalize(String term) {
        term = term.toLowerCase();
        return term.replaceAll("[^a-zA-Z0-9]", "");
    }

    // Get the term frequencies for the document
    public Map<String, Double> getTermFrequencies() {
        return termFrequencies;
    }

    // Print term frequencies in a sorted order
    public void printSortedTermFrequencies() {
        List<Map.Entry<String, Double>> sortedEntries = new ArrayList<>(termFrequencies.entrySet());

        // Sort by frequency
        Collections.sort(sortedEntries, new Comparator<Map.Entry<String, Double>>() {
            @Override
            public int compare(Map.Entry<String, Double> entry1, Map.Entry<String, Double> entry2) {
                return entry2.getValue().compareTo(entry1.getValue());
            }
        });

        System.out.println("Term Frequencies:");
        for (Map.Entry<String, Double> entry : sortedEntries) {
            System.out.println(entry.getKey() + ": " + entry.getValue());
        }
    }

    // Reset term counts and frequencies
    public void reset() {
        termCounts.clear();
        termFrequencies.clear();
    }

    // Main method to demonstrate the calculation of term frequency
    public static void main(String[] args) {
        String document1 = "This is a sample document. This document is only a test.";
        String document2 = "Another document with more sample content.";

        TermFrequency tfCalculator = new TermFrequency();

        // Process first document
        tfCalculator.calculateTermFrequency(document1);
        tfCalculator.printSortedTermFrequencies();
        tfCalculator.reset();

        // Process second document
        tfCalculator.calculateTermFrequency(document2);
        tfCalculator.printSortedTermFrequencies();
    }
}