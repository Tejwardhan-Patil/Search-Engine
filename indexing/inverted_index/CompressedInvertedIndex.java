import java.io.*;
import java.util.*;
import java.util.zip.GZIPOutputStream;
import java.util.zip.GZIPInputStream;

public class CompressedInvertedIndex {

    // Inverted index structure (word -> list of document IDs)
    private Map<String, List<Integer>> invertedIndex;

    // Constructor
    public CompressedInvertedIndex() {
        invertedIndex = new HashMap<>();
    }

    // Add a term to the index
    public void addTerm(String term, int docID) {
        invertedIndex.putIfAbsent(term, new ArrayList<>());
        List<Integer> docIDs = invertedIndex.get(term);
        if (docIDs.isEmpty() || docIDs.get(docIDs.size() - 1) != docID) {
            docIDs.add(docID);
        }
    }

    // Build inverted index from document list
    public void buildIndex(List<String> documents) {
        for (int i = 0; i < documents.size(); i++) {
            String[] terms = documents.get(i).split("\\s+");
            for (String term : terms) {
                addTerm(term, i);
            }
        }
    }

    // Delta encoding for document IDs
    public List<Integer> deltaEncode(List<Integer> docIDs) {
        List<Integer> deltaEncoded = new ArrayList<>();
        if (docIDs.isEmpty()) return deltaEncoded;
        deltaEncoded.add(docIDs.get(0));
        for (int i = 1; i < docIDs.size(); i++) {
            deltaEncoded.add(docIDs.get(i) - docIDs.get(i - 1));
        }
        return deltaEncoded;
    }

    // Variable-byte encoding for delta-encoded document IDs
    public byte[] variableByteEncode(List<Integer> deltaEncoded) {
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
        for (int number : deltaEncoded) {
            while (true) {
                int byteVal = number % 128;
                number /= 128;
                if (number == 0) {
                    byteVal += 128;
                    byteArrayOutputStream.write(byteVal);
                    break;
                } else {
                    byteArrayOutputStream.write(byteVal);
                }
            }
        }
        return byteArrayOutputStream.toByteArray();
    }

    // Variable-byte decoding
    public List<Integer> variableByteDecode(byte[] encoded) {
        List<Integer> decoded = new ArrayList<>();
        int number = 0;
        for (byte b : encoded) {
            if ((b & 128) != 0) {
                number = (number << 7) | (b & 127);
                decoded.add(number);
                number = 0;
            } else {
                number = (number << 7) | b;
            }
        }
        return decoded;
    }

    // Delta decoding
    public List<Integer> deltaDecode(List<Integer> deltaEncoded) {
        List<Integer> decoded = new ArrayList<>();
        if (deltaEncoded.isEmpty()) return decoded;
        decoded.add(deltaEncoded.get(0));
        for (int i = 1; i < deltaEncoded.size(); i++) {
            decoded.add(decoded.get(i - 1) + deltaEncoded.get(i));
        }
        return decoded;
    }

    // Compress the inverted index
    public Map<String, byte[]> compressIndex() {
        Map<String, byte[]> compressedIndex = new HashMap<>();
        for (Map.Entry<String, List<Integer>> entry : invertedIndex.entrySet()) {
            List<Integer> deltaEncoded = deltaEncode(entry.getValue());
            byte[] variableByteEncoded = variableByteEncode(deltaEncoded);
            compressedIndex.put(entry.getKey(), variableByteEncoded);
        }
        return compressedIndex;
    }

    // Decompress the inverted index
    public Map<String, List<Integer>> decompressIndex(Map<String, byte[]> compressedIndex) {
        Map<String, List<Integer>> decompressedIndex = new HashMap<>();
        for (Map.Entry<String, byte[]> entry : compressedIndex.entrySet()) {
            byte[] encoded = entry.getValue();
            List<Integer> variableByteDecoded = variableByteDecode(encoded);
            List<Integer> deltaDecoded = deltaDecode(variableByteDecoded);
            decompressedIndex.put(entry.getKey(), deltaDecoded);
        }
        return decompressedIndex;
    }

    // Save compressed index to a file using GZIP compression
    public void saveCompressedIndexToFile(Map<String, byte[]> compressedIndex, String filePath) throws IOException {
        try (ObjectOutputStream oos = new ObjectOutputStream(new GZIPOutputStream(new FileOutputStream(filePath)))) {
            oos.writeObject(compressedIndex);
        }
    }

    // Load compressed index from a file using GZIP decompression
    @SuppressWarnings("unchecked")
    public Map<String, byte[]> loadCompressedIndexFromFile(String filePath) throws IOException, ClassNotFoundException {
        try (ObjectInputStream ois = new ObjectInputStream(new GZIPInputStream(new FileInputStream(filePath)))) {
            return (Map<String, byte[]>) ois.readObject();
        }
    }

    // Search for documents containing the term
    public List<Integer> search(String term) {
        return invertedIndex.getOrDefault(term, Collections.emptyList());
    }

    // Usage
    public static void main(String[] args) {
        CompressedInvertedIndex index = new CompressedInvertedIndex();
        
        // List of documents to index
        List<String> documents = Arrays.asList(
                "search engine indexing is important",
                "inverted index helps in fast search",
                "compression reduces storage space",
                "search algorithms are crucial"
        );

        // Build the inverted index
        index.buildIndex(documents);

        // Compress the index
        Map<String, byte[]> compressedIndex = index.compressIndex();

        // Save compressed index to file
        try {
            index.saveCompressedIndexToFile(compressedIndex, "compressedIndex.gz");

            // Load compressed index from file
            Map<String, byte[]> loadedCompressedIndex = index.loadCompressedIndexFromFile("compressedIndex.gz");

            // Decompress the index
            Map<String, List<Integer>> decompressedIndex = index.decompressIndex(loadedCompressedIndex);

            // Perform search after decompression
            System.out.println("Search results for 'search': " + decompressedIndex.get("search"));
            System.out.println("Search results for 'compression': " + decompressedIndex.get("compression"));

        } catch (IOException | ClassNotFoundException e) {
            e.printStackTrace();
        }
    }
}