package ranking;

import java.util.HashMap;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.Collections;

public class RankingModel {

    // BM25 Parameters
    private static final double k1 = 1.5;
    private static final double b = 0.75;

    // Document and Corpus Metadata
    private Map<String, Integer> documentLengths = new HashMap<>();
    private Map<String, Double> documentScores = new HashMap<>();
    private int totalDocuments = 0;
    private double averageDocumentLength = 0.0;

    // Inverted Index for Term Frequencies
    private Map<String, Map<String, Integer>> invertedIndex = new HashMap<>();
    private Map<String, Integer> documentFrequency = new HashMap<>();

    public RankingModel(List<Document> documents) {
        totalDocuments = documents.size();
        buildInvertedIndex(documents);
        computeAverageDocumentLength();
    }

    // Build the Inverted Index from Documents
    private void buildInvertedIndex(List<Document> documents) {
        for (Document doc : documents) {
            String docID = doc.getDocumentID();
            String[] terms = doc.getText().split("\\s+");
            documentLengths.put(docID, terms.length);

            for (String term : terms) {
                invertedIndex.putIfAbsent(term, new HashMap<>());
                invertedIndex.get(term).put(docID, invertedIndex.get(term).getOrDefault(docID, 0) + 1);
            }
        }

        // Compute Document Frequency for each term
        for (String term : invertedIndex.keySet()) {
            documentFrequency.put(term, invertedIndex.get(term).size());
        }
    }

    // Compute the average document length in the corpus
    private void computeAverageDocumentLength() {
        int totalLength = 0;
        for (int length : documentLengths.values()) {
            totalLength += length;
        }
        averageDocumentLength = (double) totalLength / totalDocuments;
    }

    // BM25 Score Calculation for a single term in a document
    private double computeBM25Score(String term, String docID) {
        int tf = invertedIndex.getOrDefault(term, Collections.emptyMap()).getOrDefault(docID, 0);
        int df = documentFrequency.getOrDefault(term, 0);
        int docLength = documentLengths.getOrDefault(docID, 0);

        if (tf == 0 || df == 0) {
            return 0.0;
        }

        double idf = Math.log((totalDocuments - df + 0.5) / (df + 0.5));
        double tfComponent = ((k1 + 1) * tf) / (k1 * (1 - b + b * (docLength / averageDocumentLength)) + tf);

        return idf * tfComponent;
    }

    // Ranking the documents based on a query
    public List<String> rankDocuments(String query) {
        String[] queryTerms = query.split("\\s+");

        // Initialize document scores
        for (String docID : documentLengths.keySet()) {
            documentScores.put(docID, 0.0);
        }

        // Compute BM25 score for each term in the query
        for (String term : queryTerms) {
            for (String docID : invertedIndex.getOrDefault(term, Collections.emptyMap()).keySet()) {
                double score = computeBM25Score(term, docID);
                documentScores.put(docID, documentScores.get(docID) + score);
            }
        }

        // Sort documents by score in descending order
        List<String> rankedDocuments = new ArrayList<>(documentScores.keySet());
        rankedDocuments.sort((doc1, doc2) -> Double.compare(documentScores.get(doc2), documentScores.get(doc1)));

        return rankedDocuments;
    }

    // Displaying the top-ranked documents
    public void displayRankedDocuments(String query, int topN) {
        List<String> rankedDocuments = rankDocuments(query);
        System.out.println("Top " + topN + " documents for the query: " + query);
        for (int i = 0; i < Math.min(topN, rankedDocuments.size()); i++) {
            String docID = rankedDocuments.get(i);
            System.out.println((i + 1) + ". " + docID + " (Score: " + documentScores.get(docID) + ")");
        }
    }

    // Main method for testing
    public static void main(String[] args) {
        List<Document> documents = new ArrayList<>();
        documents.add(new Document("doc1", "search engine indexing algorithm"));
        documents.add(new Document("doc2", "java programming language ranking algorithm"));
        documents.add(new Document("doc3", "document frequency term frequency inverse"));

        RankingModel rankingModel = new RankingModel(documents);
        rankingModel.displayRankedDocuments("ranking algorithm", 3);
    }
}

// Document class representing a document in the collection
class Document {
    private String documentID;
    private String text;

    public Document(String documentID, String text) {
        this.documentID = documentID;
        this.text = text;
    }

    public String getDocumentID() {
        return documentID;
    }

    public String getText() {
        return text;
    }
}