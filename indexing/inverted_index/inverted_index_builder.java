import java.io.*;
import java.util.*;

public class inverted_index_builder {

    private Map<String, Map<Integer, List<Integer>>> invertedIndex;
    private List<String> documents;

    public inverted_index_builder() {
        this.invertedIndex = new HashMap<>();
        this.documents = new ArrayList<>();
    }

    public void addDocument(String content) {
        int docId = documents.size();
        documents.add(content);
        String[] words = preprocess(content);

        for (int position = 0; position < words.length; position++) {
            String word = words[position];
            invertedIndex.computeIfAbsent(word, k -> new HashMap<>());
            invertedIndex.get(word).computeIfAbsent(docId, k -> new ArrayList<>());
            invertedIndex.get(word).get(docId).add(position);
        }
    }

    private String[] preprocess(String content) {
        content = content.toLowerCase();
        return content.replaceAll("[^a-z0-9 ]", "").split("\\s+");
    }

    public Map<String, Map<Integer, List<Integer>>> getInvertedIndex() {
        return invertedIndex;
    }

    public void saveIndexToFile(String filePath) throws IOException {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(filePath))) {
            for (Map.Entry<String, Map<Integer, List<Integer>>> entry : invertedIndex.entrySet()) {
                String word = entry.getKey();
                writer.write(word + ": ");
                for (Map.Entry<Integer, List<Integer>> docEntry : entry.getValue().entrySet()) {
                    int docId = docEntry.getKey();
                    writer.write("Doc " + docId + " -> ");
                    writer.write(docEntry.getValue().toString() + "; ");
                }
                writer.newLine();
            }
        }
    }

    public void loadIndexFromFile(String filePath) throws IOException {
        invertedIndex.clear();
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split(": ");
                String word = parts[0];
                String[] docInfos = parts[1].split("; ");
                for (String docInfo : docInfos) {
                    String[] docParts = docInfo.split(" -> ");
                    int docId = Integer.parseInt(docParts[0].replace("Doc ", ""));
                    List<Integer> positions = parsePositions(docParts[1]);
                    invertedIndex.computeIfAbsent(word, k -> new HashMap<>());
                    invertedIndex.get(word).put(docId, positions);
                }
            }
        }
    }

    private List<Integer> parsePositions(String positionsString) {
        positionsString = positionsString.replace("[", "").replace("]", "");
        String[] positionArray = positionsString.split(", ");
        List<Integer> positions = new ArrayList<>();
        for (String pos : positionArray) {
            positions.add(Integer.parseInt(pos));
        }
        return positions;
    }

    public List<Integer> searchWord(String word) {
        word = word.toLowerCase();
        if (!invertedIndex.containsKey(word)) {
            return Collections.emptyList();
        }
        List<Integer> result = new ArrayList<>();
        for (Map.Entry<Integer, List<Integer>> entry : invertedIndex.get(word).entrySet()) {
            result.add(entry.getKey());
        }
        return result;
    }

    public List<Integer> searchPhrase(String phrase) {
        String[] words = preprocess(phrase);
        if (words.length == 0) return Collections.emptyList();
        Set<Integer> candidateDocs = new HashSet<>(searchWord(words[0]));

        for (int i = 1; i < words.length; i++) {
            Set<Integer> wordDocs = new HashSet<>(searchWord(words[i]));
            candidateDocs.retainAll(wordDocs);
        }

        List<Integer> resultDocs = new ArrayList<>();
        for (Integer docId : candidateDocs) {
            if (checkPhraseInDocument(docId, words)) {
                resultDocs.add(docId);
            }
        }

        return resultDocs;
    }

    private boolean checkPhraseInDocument(int docId, String[] words) {
        Map<Integer, List<Integer>> docPositions = invertedIndex.get(words[0]);
        List<Integer> positions = docPositions.get(docId);
        for (Integer position : positions) {
            boolean phraseMatch = true;
            for (int i = 1; i < words.length; i++) {
                if (!invertedIndex.containsKey(words[i]) || !invertedIndex.get(words[i]).containsKey(docId)
                        || !invertedIndex.get(words[i]).get(docId).contains(position + i)) {
                    phraseMatch = false;
                    break;
                }
            }
            if (phraseMatch) {
                return true;
            }
        }
        return false;
    }

    public static void main(String[] args) {
        inverted_index_builder indexBuilder = new inverted_index_builder();

        indexBuilder.addDocument("Hello world");
        indexBuilder.addDocument("World of Java");
        indexBuilder.addDocument("Hello Java and the world");

        System.out.println("Inverted Index: ");
        System.out.println(indexBuilder.getInvertedIndex());

        List<Integer> searchResult = indexBuilder.searchWord("world");
        System.out.println("Search Result for 'world': " + searchResult);

        List<Integer> phraseSearchResult = indexBuilder.searchPhrase("Hello world");
        System.out.println("Search Result for 'Hello world': " + phraseSearchResult);

        try {
            String indexFilePath = "inverted_index.txt";
            indexBuilder.saveIndexToFile(indexFilePath);
            System.out.println("Index saved to file.");

            inverted_index_builder loadedIndexBuilder = new inverted_index_builder();
            loadedIndexBuilder.loadIndexFromFile(indexFilePath);
            System.out.println("Loaded Inverted Index: ");
            System.out.println(loadedIndexBuilder.getInvertedIndex());
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}