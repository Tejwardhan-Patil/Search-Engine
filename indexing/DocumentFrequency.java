package indexing;

import java.io.*;
import java.util.*;

public class DocumentFrequency {

    private Map<String, Integer> termDocumentFrequency;
    private Map<String, Set<String>> documentTerms;
    private int totalDocuments;

    // Constructor
    public DocumentFrequency() {
        this.termDocumentFrequency = new HashMap<>();
        this.documentTerms = new HashMap<>();
        this.totalDocuments = 0;
    }

    // Method to process documents and calculate document frequency
    public void processDocument(String documentId, List<String> terms) {
        // Ensure unique terms per document
        Set<String> uniqueTerms = new HashSet<>(terms);
        documentTerms.put(documentId, uniqueTerms);
        totalDocuments++;

        for (String term : uniqueTerms) {
            termDocumentFrequency.put(term, termDocumentFrequency.getOrDefault(term, 0) + 1);
        }
    }

    // Method to calculate document frequency for a single term
    public int getDocumentFrequency(String term) {
        return termDocumentFrequency.getOrDefault(term, 0);
    }

    // Method to return all terms and their document frequencies
    public Map<String, Integer> getAllDocumentFrequencies() {
        return Collections.unmodifiableMap(termDocumentFrequency);
    }

    // Method to retrieve terms from a specific document
    public Set<String> getDocumentTerms(String documentId) {
        return documentTerms.getOrDefault(documentId, Collections.emptySet());
    }

    // Method to save document frequencies to a file
    public void saveDocumentFrequencies(String filePath) throws IOException {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(filePath))) {
            for (Map.Entry<String, Integer> entry : termDocumentFrequency.entrySet()) {
                writer.write(entry.getKey() + "\t" + entry.getValue() + "\n");
            }
        }
    }

    // Method to load document frequencies from a file
    public void loadDocumentFrequencies(String filePath) throws IOException {
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split("\t");
                if (parts.length == 2) {
                    String term = parts[0];
                    int frequency = Integer.parseInt(parts[1]);
                    termDocumentFrequency.put(term, frequency);
                }
            }
        }
    }

    // Method to display document frequency statistics
    public void displayStatistics() {
        System.out.println("Total Documents: " + totalDocuments);
        System.out.println("Unique Terms: " + termDocumentFrequency.size());
    }

    // Method to calculate inverse document frequency (IDF)
    public double calculateIDF(String term) {
        int df = getDocumentFrequency(term);
        if (df == 0) {
            return 0.0;
        }
        return Math.log((double) totalDocuments / df);
    }

    // Main method for demonstration purposes
    public static void main(String[] args) {
        DocumentFrequency dfCalculator = new DocumentFrequency();

        // Documents with terms
        List<String> doc1Terms = Arrays.asList("search", "engine", "optimization", "search");
        List<String> doc2Terms = Arrays.asList("machine", "learning", "search");
        List<String> doc3Terms = Arrays.asList("artificial", "intelligence", "learning");

        // Process the documents
        dfCalculator.processDocument("doc1", doc1Terms);
        dfCalculator.processDocument("doc2", doc2Terms);
        dfCalculator.processDocument("doc3", doc3Terms);

        // Display document frequencies
        dfCalculator.displayStatistics();

        // Calculate and print document frequency for specific terms
        System.out.println("DF of 'search': " + dfCalculator.getDocumentFrequency("search"));
        System.out.println("DF of 'learning': " + dfCalculator.getDocumentFrequency("learning"));

        // Calculate and print inverse document frequency (IDF)
        System.out.println("IDF of 'search': " + dfCalculator.calculateIDF("search"));
        System.out.println("IDF of 'learning': " + dfCalculator.calculateIDF("learning"));

        // Save document frequencies to file
        try {
            dfCalculator.saveDocumentFrequencies("document_frequencies.txt");
        } catch (IOException e) {
            System.err.println("Error saving document frequencies: " + e.getMessage());
        }

        // Load document frequencies from file
        DocumentFrequency loadedDfCalculator = new DocumentFrequency();
        try {
            loadedDfCalculator.loadDocumentFrequencies("document_frequencies.txt");
            System.out.println("Loaded DF of 'search': " + loadedDfCalculator.getDocumentFrequency("search"));
        } catch (IOException e) {
            System.err.println("Error loading document frequencies: " + e.getMessage());
        }
    }
}