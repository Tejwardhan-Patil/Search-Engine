package ranking.pagerank;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class PageRankComputation {

    private static final double DAMPING_FACTOR = 0.85;
    private static final int MAX_ITERATIONS = 100;
    private static final double CONVERGENCE_THRESHOLD = 0.0001;

    // Graph structure with outgoing links
    private Map<String, Set<String>> outgoingLinks;
    private Map<String, Set<String>> incomingLinks;

    // PageRank scores
    private Map<String, Double> pageRanks;

    // Constructor
    public PageRankComputation() {
        outgoingLinks = new HashMap<>();
        incomingLinks = new HashMap<>();
        pageRanks = new HashMap<>();
    }

    // Add link between two pages
    public void addLink(String fromPage, String toPage) {
        // Outgoing link
        outgoingLinks.putIfAbsent(fromPage, new HashSet<>());
        outgoingLinks.get(fromPage).add(toPage);

        // Incoming link
        incomingLinks.putIfAbsent(toPage, new HashSet<>());
        incomingLinks.get(toPage).add(fromPage);

        // Initialize PageRank score
        if (!pageRanks.containsKey(fromPage)) {
            pageRanks.put(fromPage, 1.0);
        }
        if (!pageRanks.containsKey(toPage)) {
            pageRanks.put(toPage, 1.0);
        }
    }

    // Initialize the graph with initial PageRank values
    private void initializePageRank() {
        double initialRank = 1.0 / pageRanks.size();
        for (String page : pageRanks.keySet()) {
            pageRanks.put(page, initialRank);
        }
    }

    // Compute PageRank using the iterative method
    public void computePageRank() {
        initializePageRank();
        int iteration = 0;
        boolean converged = false;

        while (!converged && iteration < MAX_ITERATIONS) {
            Map<String, Double> newPageRanks = new HashMap<>();
            double totalDifference = 0.0;

            for (String page : pageRanks.keySet()) {
                double rankSum = 0.0;

                // Sum up ranks from incoming links
                if (incomingLinks.containsKey(page)) {
                    for (String incomingPage : incomingLinks.get(page)) {
                        double outgoingLinkCount = outgoingLinks.get(incomingPage).size();
                        rankSum += pageRanks.get(incomingPage) / outgoingLinkCount;
                    }
                }

                // Apply the PageRank formula
                double newRank = (1 - DAMPING_FACTOR) / pageRanks.size() + DAMPING_FACTOR * rankSum;
                newPageRanks.put(page, newRank);

                // Track total difference for convergence check
                totalDifference += Math.abs(newRank - pageRanks.get(page));
            }

            // Update PageRank values
            pageRanks = newPageRanks;

            // Check if the algorithm has converged
            if (totalDifference < CONVERGENCE_THRESHOLD) {
                converged = true;
            }

            iteration++;
        }

        System.out.println("PageRank computation completed in " + iteration + " iterations.");
    }

    // Display the computed PageRank scores
    public void displayPageRanks() {
        for (Map.Entry<String, Double> entry : pageRanks.entrySet()) {
            System.out.println("Page: " + entry.getKey() + " | Rank: " + entry.getValue());
        }
    }

    // Main method for testing
    public static void main(String[] args) {
        PageRankComputation pageRankComputation = new PageRankComputation();

        // Add links between pages
        pageRankComputation.addLink("PageA", "PageB");
        pageRankComputation.addLink("PageA", "PageC");
        pageRankComputation.addLink("PageB", "PageC");
        pageRankComputation.addLink("PageC", "PageA");
        pageRankComputation.addLink("PageD", "PageC");
        pageRankComputation.addLink("PageE", "PageD");

        // Compute and display PageRank scores
        pageRankComputation.computePageRank();
        pageRankComputation.displayPageRanks();
    }
}