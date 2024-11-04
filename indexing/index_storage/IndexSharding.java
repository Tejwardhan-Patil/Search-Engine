package indexing.index_storage;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.Scanner;

public class IndexSharding {

    private static final int NUM_SHARDS = 5;
    private Map<Integer, File> shardFiles;
    private Map<Integer, FileWriter> shardWriters;
    private String shardDirectory;

    public IndexSharding(String shardDirectory) throws IOException {
        this.shardDirectory = shardDirectory;
        shardFiles = new HashMap<>();
        shardWriters = new HashMap<>();
        initializeShards();
    }

    private void initializeShards() throws IOException {
        for (int i = 0; i < NUM_SHARDS; i++) {
            File shardFile = new File(shardDirectory + "/shard_" + i + ".txt");
            if (!shardFile.exists()) {
                shardFile.createNewFile();
            }
            shardFiles.put(i, shardFile);
            shardWriters.put(i, new FileWriter(shardFile, true));
        }
    }

    private int getShardId(String term) {
        // Hash function to determine shard ID
        return Math.abs(term.hashCode() % NUM_SHARDS);
    }

    public void addToIndex(String term, String documentId) throws IOException {
        int shardId = getShardId(term);
        FileWriter writer = shardWriters.get(shardId);
        writer.write(term + ":" + documentId + "\n");
        writer.flush();
    }

    public List<String> searchTerm(String term) throws IOException {
        int shardId = getShardId(term);
        File shardFile = shardFiles.get(shardId);
        List<String> results = new ArrayList<>();
        try (Scanner scanner = new Scanner(shardFile)) {
            while (scanner.hasNextLine()) {
                String line = scanner.nextLine();
                if (line.startsWith(term + ":")) {
                    String[] parts = line.split(":");
                    if (parts.length == 2) {
                        results.add(parts[1]);
                    }
                }
            }
        }
        return results;
    }

    public void close() throws IOException {
        for (FileWriter writer : shardWriters.values()) {
            writer.close();
        }
    }

    public static void main(String[] args) {
        try {
            IndexSharding indexSharding = new IndexSharding("shards");
            
            // Adding documents to index
            indexSharding.addToIndex("search", "doc1");
            indexSharding.addToIndex("engine", "doc2");
            indexSharding.addToIndex("search", "doc3");

            // Search for the term
            List<String> results = indexSharding.searchTerm("search");
            System.out.println("Search results for 'search': " + results);

            // Close resources
            indexSharding.close();

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}