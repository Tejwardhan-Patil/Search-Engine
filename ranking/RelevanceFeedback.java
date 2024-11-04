package ranking;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Collections;

public class RelevanceFeedback {
    private Map<String, Map<String, Double>> termFrequencies; 
    private Map<String, Integer> documentFrequencies; 
    private int totalDocuments; 

    // Constructor to initialize with term and document frequencies
    public RelevanceFeedback(Map<String, Map<String, Double>> termFrequencies, Map<String, Integer> documentFrequencies, int totalDocuments) {
        this.termFrequencies = termFrequencies;
        this.documentFrequencies = documentFrequencies;
        this.totalDocuments = totalDocuments;
    }

    // Calculate the inverse document frequency (IDF) for a term
    private double calculateIDF(String term) {
        int df = documentFrequencies.getOrDefault(term, 0);
        if (df == 0) return 0;
        return Math.log((double) totalDocuments / df);
    }

    // Rank documents based on the query and feedback from the user
    public List<DocumentScore> rankDocuments(String query, Set<String> relevantDocuments, Set<String> nonRelevantDocuments) {
        // Tokenize the query
        String[] queryTerms = query.toLowerCase().split("\\s+");
        Map<String, Double> queryVector = createQueryVector(queryTerms);

        // Adjust the query vector using relevance feedback and IDF
        queryVector = adjustQueryVectorWithFeedback(queryVector, relevantDocuments, nonRelevantDocuments);

        // Rank documents based on the adjusted query vector
        return calculateDocumentScores(queryVector);
    }

    // Create a query vector with term frequencies and IDF
    private Map<String, Double> createQueryVector(String[] queryTerms) {
        Map<String, Double> queryVector = new HashMap<>();
        for (String term : queryTerms) {
            double tf = queryVector.getOrDefault(term, 0.0) + 1.0;
            double idf = calculateIDF(term);
            queryVector.put(term, tf * idf);
        }
        return queryVector;
    }

    // Adjust the query vector using relevance feedback with Rocchio's algorithm and IDF
    private Map<String, Double> adjustQueryVectorWithFeedback(Map<String, Double> queryVector, Set<String> relevantDocuments, Set<String> nonRelevantDocuments) {
        double alpha = 1.0;  // Weight for the original query
        double beta = 0.75;  // Weight for relevant documents
        double gamma = 0.25; // Weight for non-relevant documents

        Map<String, Double> adjustedQueryVector = new HashMap<>();

        // Original query contribution
        for (Map.Entry<String, Double> entry : queryVector.entrySet()) {
            String term = entry.getKey();
            double value = entry.getValue();
            adjustedQueryVector.put(term, alpha * value);
        }

        // Contribution from relevant documents
        if (!relevantDocuments.isEmpty()) {
            Map<String, Double> relevantVector = calculateDocumentSetVector(relevantDocuments);
            for (Map.Entry<String, Double> entry : relevantVector.entrySet()) {
                String term = entry.getKey();
                double value = entry.getValue();
                adjustedQueryVector.put(term, adjustedQueryVector.getOrDefault(term, 0.0) + beta * value / relevantDocuments.size());
            }
        }

        // Contribution from non-relevant documents
        if (!nonRelevantDocuments.isEmpty()) {
            Map<String, Double> nonRelevantVector = calculateDocumentSetVector(nonRelevantDocuments);
            for (Map.Entry<String, Double> entry : nonRelevantVector.entrySet()) {
                String term = entry.getKey();
                double value = entry.getValue();
                adjustedQueryVector.put(term, adjustedQueryVector.getOrDefault(term, 0.0) - gamma * value / nonRelevantDocuments.size());
            }
        }

        return adjustedQueryVector;
    }

    // Calculate the centroid vector for a set of documents
    private Map<String, Double> calculateDocumentSetVector(Set<String> documentIds) {
        Map<String, Double> centroidVector = new HashMap<>();

        for (String docId : documentIds) {
            Map<String, Double> docVector = termFrequencies.get(docId);
            if (docVector == null) continue;

            for (Map.Entry<String, Double> entry : docVector.entrySet()) {
                String term = entry.getKey();
                double value = entry.getValue();
                double idf = calculateIDF(term);
                centroidVector.put(term, centroidVector.getOrDefault(term, 0.0) + value * idf);
            }
        }

        return centroidVector;
    }

    // Calculate document scores using cosine similarity between query vector and document vectors
    private List<DocumentScore> calculateDocumentScores(Map<String, Double> queryVector) {
        List<DocumentScore> documentScores = new ArrayList<>();

        for (Map.Entry<String, Map<String, Double>> docEntry : termFrequencies.entrySet()) {
            String docId = docEntry.getKey();
            Map<String, Double> docVector = docEntry.getValue();
            double score = calculateCosineSimilarity(queryVector, docVector);

            documentScores.add(new DocumentScore(docId, score));
        }

        // Sort documents by score in descending order
        Collections.sort(documentScores);
        return documentScores;
    }

    // Calculate cosine similarity between two vectors
    private double calculateCosineSimilarity(Map<String, Double> vector1, Map<String, Double> vector2) {
        double dotProduct = 0.0;
        double norm1 = 0.0;
        double norm2 = 0.0;

        Set<String> allTerms = new HashSet<>(vector1.keySet());
        allTerms.addAll(vector2.keySet());

        for (String term : allTerms) {
            double value1 = vector1.getOrDefault(term, 0.0);
            double value2 = vector2.getOrDefault(term, 0.0);

            dotProduct += value1 * value2;
            norm1 += value1 * value1;
            norm2 += value2 * value2;
        }

        if (norm1 == 0 || norm2 == 0) return 0.0;
        return dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
    }

    // Helper class to store document scores
    public static class DocumentScore implements Comparable<DocumentScore> {
        private String documentId;
        private double score;

        public DocumentScore(String documentId, double score) {
            this.documentId = documentId;
            this.score = score;
        }

        public String getDocumentId() {
            return documentId;
        }

        public double getScore() {
            return score;
        }

        @Override
        public int compareTo(DocumentScore other) {
            return Double.compare(other.score, this.score);
        }
    }

    public static void main(String[] args) {
        // Term frequencies for documents
        Map<String, Map<String, Double>> termFrequencies = new HashMap<>();

        // Document frequencies for the corpus
        Map<String, Integer> documentFrequencies = new HashMap<>();

        int totalDocuments = 100;

        RelevanceFeedback relevanceFeedback = new RelevanceFeedback(termFrequencies, documentFrequencies, totalDocuments);

        Set<String> relevantDocs = new HashSet<>();
        Set<String> nonRelevantDocs = new HashSet<>();

        String query = "search engine";
        List<DocumentScore> rankedDocuments = relevanceFeedback.rankDocuments(query, relevantDocs, nonRelevantDocs);

        // Output ranked documents
        for (DocumentScore docScore : rankedDocuments) {
            System.out.println("Document: " + docScore.getDocumentId() + " Score: " + docScore.getScore());
        }
    }
}