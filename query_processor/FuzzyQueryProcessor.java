package query_processor;

import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.Set;
import java.util.Arrays;

public class FuzzyQueryProcessor {

    private Map<String, Set<String>> invertedIndex;
    private int maxEditDistance;

    public FuzzyQueryProcessor(Map<String, Set<String>> invertedIndex, int maxEditDistance) {
        this.invertedIndex = invertedIndex;
        this.maxEditDistance = maxEditDistance;
    }

    // Process the query with fuzzy matching based on edit distance
    public List<String> processQuery(String query) {
        String[] terms = query.split("\\s+");
        List<String> results = new ArrayList<>();
        for (String term : terms) {
            results.addAll(findFuzzyMatches(term));
        }
        return results;
    }

    // Find fuzzy matches for a given term using Levenshtein distance
    private Set<String> findFuzzyMatches(String term) {
        Set<String> matches = new HashSet<>();
        for (String indexTerm : invertedIndex.keySet()) {
            if (calculateLevenshteinDistance(term, indexTerm) <= maxEditDistance) {
                matches.addAll(invertedIndex.get(indexTerm));
            }
        }
        return matches;
    }

    // Calculate the Levenshtein Distance between two terms
    private int calculateLevenshteinDistance(String s1, String s2) {
        int[][] dp = new int[s1.length() + 1][s2.length() + 1];

        for (int i = 0; i <= s1.length(); i++) {
            for (int j = 0; j <= s2.length(); j++) {
                if (i == 0) {
                    dp[i][j] = j;
                } else if (j == 0) {
                    dp[i][j] = i;
                } else if (s1.charAt(i - 1) == s2.charAt(j - 1)) {
                    dp[i][j] = dp[i - 1][j - 1];
                } else {
                    dp[i][j] = 1 + Math.min(dp[i - 1][j - 1], Math.min(dp[i - 1][j], dp[i][j - 1]));
                }
            }
        }

        return dp[s1.length()][s2.length()];
    }

    public static void main(String[] args) {
        // Inverted index
        Map<String, Set<String>> invertedIndex = new HashMap<>();
        invertedIndex.put("apple", Set.of("doc1", "doc2"));
        invertedIndex.put("application", Set.of("doc3"));
        invertedIndex.put("apricot", Set.of("doc4"));
        invertedIndex.put("banana", Set.of("doc5"));

        // Create a fuzzy query processor with a maximum edit distance of 2
        FuzzyQueryProcessor processor = new FuzzyQueryProcessor(invertedIndex, 2);

        // Process a sample query
        String query = "aple"; // A misspelled query term
        List<String> results = processor.processQuery(query);

        // Print results
        System.out.println("Search results for query '" + query + "': " + results);
    }
}

// A second class to improve performance using Trie structure for faster lookup
class TrieNode {
    Map<Character, TrieNode> children;
    boolean isEndOfWord;

    public TrieNode() {
        children = new HashMap<>();
        isEndOfWord = false;
    }
}

class Trie {
    private TrieNode root;

    public Trie() {
        root = new TrieNode();
    }

    // Insert a word into the Trie
    public void insert(String word) {
        TrieNode current = root;
        for (char ch : word.toCharArray()) {
            current = current.children.computeIfAbsent(ch, c -> new TrieNode());
        }
        current.isEndOfWord = true;
    }

    // Search words that are close to the input term based on Levenshtein distance
    public Set<String> searchFuzzy(String term, int maxDistance) {
        Set<String> result = new HashSet<>();
        char[] termArray = term.toCharArray();
        int[] currentRow = new int[termArray.length + 1];
        for (int i = 0; i <= termArray.length; i++) {
            currentRow[i] = i;
        }
        searchRecursive(root, "", termArray, currentRow, result, maxDistance);
        return result;
    }

    private void searchRecursive(TrieNode node, String currentWord, char[] termArray, int[] previousRow, Set<String> result, int maxDistance) {
        int columns = termArray.length + 1;
        int[] currentRow = new int[columns];
        currentRow[0] = previousRow[0] + 1;

        for (int i = 1; i < columns; i++) {
            int insertCost = currentRow[i - 1] + 1;
            int deleteCost = previousRow[i] + 1;
            int replaceCost = previousRow[i - 1];
            if (termArray[i - 1] != currentWord.charAt(currentWord.length() - 1)) {
                replaceCost++;
            }
            currentRow[i] = Math.min(Math.min(insertCost, deleteCost), replaceCost);
        }

        if (currentRow[columns - 1] <= maxDistance && node.isEndOfWord) {
            result.add(currentWord);
        }

        if (Arrays.stream(currentRow).min().orElse(maxDistance + 1) <= maxDistance) {
            for (Map.Entry<Character, TrieNode> entry : node.children.entrySet()) {
                searchRecursive(entry.getValue(), currentWord + entry.getKey(), termArray, currentRow, result, maxDistance);
            }
        }
    }
}

// Optimized FuzzyQueryProcessor using Trie structure
class OptimizedFuzzyQueryProcessor {
    private Trie trie;
    private Map<String, Set<String>> invertedIndex;
    private int maxEditDistance;

    public OptimizedFuzzyQueryProcessor(Map<String, Set<String>> invertedIndex, int maxEditDistance) {
        this.trie = new Trie();
        this.invertedIndex = invertedIndex;
        this.maxEditDistance = maxEditDistance;

        for (String term : invertedIndex.keySet()) {
            trie.insert(term);
        }
    }

    public List<String> processQuery(String query) {
        String[] terms = query.split("\\s+");
        List<String> results = new ArrayList<>();
        for (String term : terms) {
            Set<String> matches = trie.searchFuzzy(term, maxEditDistance);
            for (String match : matches) {
                results.addAll(invertedIndex.get(match));
            }
        }
        return results;
    }

    public static void main(String[] args) {
        // Inverted index
        Map<String, Set<String>> invertedIndex = new HashMap<>();
        invertedIndex.put("apple", Set.of("doc1", "doc2"));
        invertedIndex.put("application", Set.of("doc3"));
        invertedIndex.put("apricot", Set.of("doc4"));
        invertedIndex.put("banana", Set.of("doc5"));

        // Create an optimized fuzzy query processor with a maximum edit distance of 2
        OptimizedFuzzyQueryProcessor processor = new OptimizedFuzzyQueryProcessor(invertedIndex, 2);

        // Process a sample query
        String query = "aple"; // A misspelled query term
        List<String> results = processor.processQuery(query);

        // Print results
        System.out.println("Search results for query '" + query + "': " + results);
    }
}