package storage.document_store;

import java.io.*;
import java.nio.file.*;
import java.util.zip.GZIPOutputStream;
import java.util.zip.GZIPInputStream;
import java.util.HashMap;
import java.util.Map;

// Document storage class
public class DocumentStore {
    private final String storageDirectory;
    private final Map<String, String> metadataStore;

    public DocumentStore(String storageDirectory) {
        this.storageDirectory = storageDirectory;
        this.metadataStore = new HashMap<>();
        try {
            Files.createDirectories(Paths.get(storageDirectory));
        } catch (IOException e) {
            throw new RuntimeException("Error creating storage directory: " + e.getMessage(), e);
        }
    }

    // Store a document with compression
    public void storeDocument(String docId, String content) {
        String compressedFilePath = storageDirectory + File.separator + docId + ".gz";
        try (FileOutputStream fos = new FileOutputStream(compressedFilePath);
             GZIPOutputStream gzipOS = new GZIPOutputStream(fos)) {
            byte[] data = content.getBytes();
            gzipOS.write(data);
            gzipOS.flush();
            updateMetadata(docId, compressedFilePath, content.length());
        } catch (IOException e) {
            throw new RuntimeException("Error storing document: " + e.getMessage(), e);
        }
    }

    // Retrieve a document by decompressing
    public String retrieveDocument(String docId) {
        String compressedFilePath = storageDirectory + File.separator + docId + ".gz";
        try (FileInputStream fis = new FileInputStream(compressedFilePath);
             GZIPInputStream gzipIS = new GZIPInputStream(fis);
             InputStreamReader reader = new InputStreamReader(gzipIS);
             BufferedReader bufferedReader = new BufferedReader(reader)) {

            StringBuilder contentBuilder = new StringBuilder();
            String line;
            while ((line = bufferedReader.readLine()) != null) {
                contentBuilder.append(line);
            }
            return contentBuilder.toString();
        } catch (IOException e) {
            throw new RuntimeException("Error retrieving document: " + e.getMessage(), e);
        }
    }

    // Delete a document
    public void deleteDocument(String docId) {
        String compressedFilePath = storageDirectory + File.separator + docId + ".gz";
        try {
            Files.deleteIfExists(Paths.get(compressedFilePath));
            metadataStore.remove(docId);
        } catch (IOException e) {
            throw new RuntimeException("Error deleting document: " + e.getMessage(), e);
        }
    }

    // List all documents
    public void listDocuments() {
        File folder = new File(storageDirectory);
        File[] files = folder.listFiles();
        if (files != null) {
            for (File file : files) {
                System.out.println(file.getName());
            }
        }
    }

    // Update metadata
    private void updateMetadata(String docId, String filePath, int originalSize) {
        metadataStore.put(docId, "Path: " + filePath + ", Original Size: " + originalSize);
    }

    // Retrieve metadata
    public String getMetadata(String docId) {
        return metadataStore.getOrDefault(docId, "No metadata found");
    }

    public static void main(String[] args) {
        DocumentStore store = new DocumentStore("document_store");

        // Store a document
        String documentContent = "This is a document content. It will be compressed and stored.";
        store.storeDocument("doc1", documentContent);

        // List stored documents
        store.listDocuments();

        // Retrieve a document
        String retrievedContent = store.retrieveDocument("doc1");
        System.out.println("Retrieved Document Content: " + retrievedContent);

        // Get metadata
        String metadata = store.getMetadata("doc1");
        System.out.println("Document Metadata: " + metadata);

        // Delete a document
        store.deleteDocument("doc1");
    }
}