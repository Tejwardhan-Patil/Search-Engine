package indexing.index_storage;

import java.io.*;
import java.nio.file.*;
import java.util.*;

/**
 * The IndexFileManager class is responsible for managing
 * the storage and retrieval of the search engine index files.
 * It provides methods for saving, loading, and deleting index files.
 */
public class IndexFileManager {

    private Path indexDirectory;

    /**
     * Constructor to initialize the index file manager with a specified directory.
     * @param directory The directory where index files are stored.
     */
    public IndexFileManager(String directory) {
        this.indexDirectory = Paths.get(directory);
        createDirectoryIfNotExists();
    }

    /**
     * Creates the index directory if it does not already exist.
     */
    private void createDirectoryIfNotExists() {
        try {
            if (!Files.exists(indexDirectory)) {
                Files.createDirectories(indexDirectory);
            }
        } catch (IOException e) {
            throw new RuntimeException("Error creating index directory", e);
        }
    }

    /**
     * Saves a given index to the specified file.
     * @param fileName The name of the file to save the index in.
     * @param indexData The data of the index to be saved.
     */
    public void saveIndex(String fileName, Map<String, List<Integer>> indexData) {
        Path filePath = indexDirectory.resolve(fileName);
        try (BufferedWriter writer = Files.newBufferedWriter(filePath)) {
            for (Map.Entry<String, List<Integer>> entry : indexData.entrySet()) {
                writer.write(entry.getKey() + ":" + entry.getValue());
                writer.newLine();
            }
        } catch (IOException e) {
            throw new RuntimeException("Error saving index file", e);
        }
    }

    /**
     * Loads the index from a specified file.
     * @param fileName The name of the file to load the index from.
     * @return A map representing the index loaded from the file.
     */
    public Map<String, List<Integer>> loadIndex(String fileName) {
        Path filePath = indexDirectory.resolve(fileName);
        Map<String, List<Integer>> indexData = new HashMap<>();
        try (BufferedReader reader = Files.newBufferedReader(filePath)) {
            String line;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split(":");
                if (parts.length == 2) {
                    String term = parts[0];
                    List<Integer> postings = parsePostings(parts[1]);
                    indexData.put(term, postings);
                }
            }
        } catch (IOException e) {
            throw new RuntimeException("Error loading index file", e);
        }
        return indexData;
    }

    /**
     * Deletes a specific index file.
     * @param fileName The name of the file to delete.
     */
    public void deleteIndex(String fileName) {
        Path filePath = indexDirectory.resolve(fileName);
        try {
            Files.deleteIfExists(filePath);
        } catch (IOException e) {
            throw new RuntimeException("Error deleting index file", e);
        }
    }

    /**
     * Lists all index files in the directory.
     * @return A list of index file names.
     */
    public List<String> listIndexFiles() {
        List<String> fileNames = new ArrayList<>();
        try (DirectoryStream<Path> stream = Files.newDirectoryStream(indexDirectory)) {
            for (Path entry : stream) {
                if (Files.isRegularFile(entry)) {
                    fileNames.add(entry.getFileName().toString());
                }
            }
        } catch (IOException e) {
            throw new RuntimeException("Error listing index files", e);
        }
        return fileNames;
    }

    /**
     * Parses a string representation of postings into a list of integers.
     * @param postingsString The string representation of postings.
     * @return A list of integers representing document IDs.
     */
    private List<Integer> parsePostings(String postingsString) {
        String[] parts = postingsString.replaceAll("[\\[\\]]", "").split(",");
        List<Integer> postings = new ArrayList<>();
        for (String part : parts) {
            postings.add(Integer.parseInt(part.trim()));
        }
        return postings;
    }

    /**
     * Updates an existing index file by appending new data.
     * @param fileName The name of the file to update.
     * @param newData The new data to append to the index.
     */
    public void updateIndex(String fileName, Map<String, List<Integer>> newData) {
        Map<String, List<Integer>> existingData = loadIndex(fileName);
        for (Map.Entry<String, List<Integer>> entry : newData.entrySet()) {
            existingData.merge(entry.getKey(), entry.getValue(), (oldList, newList) -> {
                Set<Integer> mergedSet = new HashSet<>(oldList);
                mergedSet.addAll(newList);
                return new ArrayList<>(mergedSet);
            });
        }
        saveIndex(fileName, existingData);
    }

    /**
     * Clears all index files in the directory.
     */
    public void clearAllIndexes() {
        List<String> files = listIndexFiles();
        for (String fileName : files) {
            deleteIndex(fileName);
        }
    }

    /**
     * Checks if an index file exists.
     * @param fileName The name of the file to check.
     * @return True if the file exists, false otherwise.
     */
    public boolean indexExists(String fileName) {
        Path filePath = indexDirectory.resolve(fileName);
        return Files.exists(filePath);
    }

    /**
     * Retrieves the size of an index file in bytes.
     * @param fileName The name of the file to check.
     * @return The size of the file in bytes.
     */
    public long getIndexSize(String fileName) {
        Path filePath = indexDirectory.resolve(fileName);
        try {
            return Files.size(filePath);
        } catch (IOException e) {
            throw new RuntimeException("Error getting index file size", e);
        }
    }

    /**
     * Moves an index file to a new location.
     * @param fileName The name of the file to move.
     * @param newDirectory The directory to move the file to.
     */
    public void moveIndexFile(String fileName, String newDirectory) {
        Path sourcePath = indexDirectory.resolve(fileName);
        Path destinationPath = Paths.get(newDirectory).resolve(fileName);
        try {
            Files.move(sourcePath, destinationPath, StandardCopyOption.REPLACE_EXISTING);
        } catch (IOException e) {
            throw new RuntimeException("Error moving index file", e);
        }
    }

    /**
     * Copies an index file to a new location.
     * @param fileName The name of the file to copy.
     * @param newDirectory The directory to copy the file to.
     */
    public void copyIndexFile(String fileName, String newDirectory) {
        Path sourcePath = indexDirectory.resolve(fileName);
        Path destinationPath = Paths.get(newDirectory).resolve(fileName);
        try {
            Files.copy(sourcePath, destinationPath, StandardCopyOption.REPLACE_EXISTING);
        } catch (IOException e) {
            throw new RuntimeException("Error copying index file", e);
        }
    }
}