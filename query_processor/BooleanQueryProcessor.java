package query_processor;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class BooleanQueryProcessor {

    private Map<String, List<Integer>> invertedIndex;

    public BooleanQueryProcessor(Map<String, List<Integer>> invertedIndex) {
        this.invertedIndex = invertedIndex;
    }

    public List<Integer> processQuery(String query) {
        query = query.trim().toLowerCase();
        List<String> tokens = tokenize(query);
        return evaluate(tokens);
    }

    private List<String> tokenize(String query) {
        List<String> tokens = new ArrayList<>();
        StringBuilder token = new StringBuilder();
        for (char c : query.toCharArray()) {
            if (c == ' ' || c == '(' || c == ')' || c == '&' || c == '|' || c == '!') {
                if (token.length() > 0) {
                    tokens.add(token.toString());
                    token = new StringBuilder();
                }
                if (c != ' ') {
                    tokens.add(String.valueOf(c));
                }
            } else {
                token.append(c);
            }
        }
        if (token.length() > 0) {
            tokens.add(token.toString());
        }
        return tokens;
    }

    private List<Integer> evaluate(List<String> tokens) {
        return evaluate(tokens, 0, tokens.size() - 1);
    }

    private List<Integer> evaluate(List<String> tokens, int start, int end) {
        if (start == end) {
            return getPostings(tokens.get(start));
        }

        int level = 0;
        int operatorIndex = -1;

        // Look for top-level operators (AND, OR)
        for (int i = start; i <= end; i++) {
            if (tokens.get(i).equals("(")) {
                level++;
            } else if (tokens.get(i).equals(")")) {
                level--;
            } else if (level == 0) {
                if (tokens.get(i).equals("&") || tokens.get(i).equals("|")) {
                    operatorIndex = i;
                    break;
                }
            }
        }

        // If no top-level operator, it must be a NOT or a simple term
        if (operatorIndex == -1) {
            if (tokens.get(start).equals("!")) {
                return notOperation(evaluate(tokens, start + 1, end));
            } else if (tokens.get(start).equals("(") && tokens.get(end).equals(")")) {
                return evaluate(tokens, start + 1, end - 1);
            } else {
                return getPostings(tokens.get(start));
            }
        }

        // Evaluate left and right subexpressions
        List<Integer> left = evaluate(tokens, start, operatorIndex - 1);
        List<Integer> right = evaluate(tokens, operatorIndex + 1, end);

        // Apply the operator
        if (tokens.get(operatorIndex).equals("&")) {
            return andOperation(left, right);
        } else {
            return orOperation(left, right);
        }
    }

    private List<Integer> getPostings(String term) {
        if (invertedIndex.containsKey(term)) {
            return invertedIndex.get(term);
        }
        return new ArrayList<>();
    }

    private List<Integer> andOperation(List<Integer> left, List<Integer> right) {
        List<Integer> result = new ArrayList<>();
        int i = 0, j = 0;
        while (i < left.size() && j < right.size()) {
            if (left.get(i).equals(right.get(j))) {
                result.add(left.get(i));
                i++;
                j++;
            } else if (left.get(i) < right.get(j)) {
                i++;
            } else {
                j++;
            }
        }
        return result;
    }

    private List<Integer> orOperation(List<Integer> left, List<Integer> right) {
        List<Integer> result = new ArrayList<>();
        int i = 0, j = 0;
        while (i < left.size() && j < right.size()) {
            if (left.get(i).equals(right.get(j))) {
                result.add(left.get(i));
                i++;
                j++;
            } else if (left.get(i) < right.get(j)) {
                result.add(left.get(i));
                i++;
            } else {
                result.add(right.get(j));
                j++;
            }
        }
        while (i < left.size()) {
            result.add(left.get(i++));
        }
        while (j < right.size()) {
            result.add(right.get(j++));
        }
        return result;
    }

    private List<Integer> notOperation(List<Integer> postings) {
        List<Integer> allDocs = getAllDocuments();
        List<Integer> result = new ArrayList<>();
        int i = 0, j = 0;
        while (i < allDocs.size() && j < postings.size()) {
            if (allDocs.get(i).equals(postings.get(j))) {
                i++;
                j++;
            } else {
                result.add(allDocs.get(i));
                i++;
            }
        }
        while (i < allDocs.size()) {
            result.add(allDocs.get(i++));
        }
        return result;
    }

    private List<Integer> getAllDocuments() {
        Set<Integer> allDocsSet = new HashSet<>();
        for (List<Integer> postings : invertedIndex.values()) {
            allDocsSet.addAll(postings);
        }
        return new ArrayList<>(allDocsSet);
    }

    // Test the Boolean Query Processor
    public static void main(String[] args) {
        Map<String, List<Integer>> invertedIndex = new HashMap<>();
        invertedIndex.put("term1", List.of(1, 2, 3));
        invertedIndex.put("term2", List.of(2, 3, 4));
        invertedIndex.put("term3", List.of(1, 4, 5));

        BooleanQueryProcessor processor = new BooleanQueryProcessor(invertedIndex);

        String query = "(term1 & term2) | (!term3)";
        List<Integer> result = processor.processQuery(query);

        System.out.println("Query result: " + result);
    }
}