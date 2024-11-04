package storage.metadata_store;

import java.util.HashMap;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.Date;
import java.util.UUID;
import java.io.Serializable;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;

/**
 * MetadataManager class handles the storage, retrieval, and management
 * of document metadata such as crawl date, source URL, etc
 */
public class MetadataManager implements Serializable {
    private static final long serialVersionUID = 1L;

    // In-memory store for metadata
    private Map<String, DocumentMetadata> metadataStore;
    private String metadataFilePath = "metadata_store.dat";

    public MetadataManager() {
        metadataStore = new HashMap<>();
        loadMetadataStore();
    }

    /**
     * Add a new document's metadata to the store.
     *
     * @param url The source URL of the document.
     * @param crawlDate The date the document was crawled.
     * @param contentHash Hash representing the document content.
     * @return The generated metadata ID.
     */
    public String addMetadata(String url, Date crawlDate, String contentHash) {
        String metadataId = generateMetadataId();
        DocumentMetadata metadata = new DocumentMetadata(metadataId, url, crawlDate, contentHash);
        metadataStore.put(metadataId, metadata);
        saveMetadataStore();
        return metadataId;
    }

    /**
     * Retrieve metadata by its unique ID.
     *
     * @param metadataId The ID of the metadata to retrieve.
     * @return The document metadata, or null if not found.
     */
    public DocumentMetadata getMetadata(String metadataId) {
        return metadataStore.get(metadataId);
    }

    /**
     * Update existing metadata.
     *
     * @param metadataId The ID of the metadata to update.
     * @param updatedMetadata Updated metadata object.
     */
    public void updateMetadata(String metadataId, DocumentMetadata updatedMetadata) {
        if (metadataStore.containsKey(metadataId)) {
            metadataStore.put(metadataId, updatedMetadata);
            saveMetadataStore();
        }
    }

    /**
     * Delete metadata from the store.
     *
     * @param metadataId The ID of the metadata to delete.
     */
    public void deleteMetadata(String metadataId) {
        metadataStore.remove(metadataId);
        saveMetadataStore();
    }

    /**
     * Search metadata by source URL.
     *
     * @param url The URL to search for.
     * @return A list of metadata entries that match the URL.
     */
    public List<DocumentMetadata> searchMetadataByUrl(String url) {
        List<DocumentMetadata> result = new ArrayList<>();
        for (DocumentMetadata metadata : metadataStore.values()) {
            if (metadata.getUrl().equals(url)) {
                result.add(metadata);
            }
        }
        return result;
    }

    /**
     * Save the metadata store to disk.
     */
    private void saveMetadataStore() {
        try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(metadataFilePath))) {
            oos.writeObject(metadataStore);
        } catch (IOException e) {
            System.err.println("Error saving metadata store: " + e.getMessage());
        }
    }

    /**
     * Load the metadata store from disk.
     */
    @SuppressWarnings("unchecked")
    private void loadMetadataStore() {
        try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream(metadataFilePath))) {
            metadataStore = (Map<String, DocumentMetadata>) ois.readObject();
        } catch (IOException | ClassNotFoundException e) {
            System.err.println("Error loading metadata store: " + e.getMessage());
            metadataStore = new HashMap<>();
        }
    }

    /**
     * Generate a unique ID for each metadata entry.
     *
     * @return A unique metadata ID.
     */
    private String generateMetadataId() {
        return UUID.randomUUID().toString();
    }

    // Inner class representing metadata of a document
    public static class DocumentMetadata implements Serializable {
        private static final long serialVersionUID = 1L;
        private String metadataId;
        private String url;
        private Date crawlDate;
        private String contentHash;

        public DocumentMetadata(String metadataId, String url, Date crawlDate, String contentHash) {
            this.metadataId = metadataId;
            this.url = url;
            this.crawlDate = crawlDate;
            this.contentHash = contentHash;
        }

        public String getMetadataId() {
            return metadataId;
        }

        public String getUrl() {
            return url;
        }

        public Date getCrawlDate() {
            return crawlDate;
        }

        public String getContentHash() {
            return contentHash;
        }

        public void setUrl(String url) {
            this.url = url;
        }

        public void setCrawlDate(Date crawlDate) {
            this.crawlDate = crawlDate;
        }

        public void setContentHash(String contentHash) {
            this.contentHash = contentHash;
        }

        @Override
        public String toString() {
            return "MetadataID: " + metadataId + ", URL: " + url + ", CrawlDate: " + crawlDate + ", ContentHash: " + contentHash;
        }
    }

    public static void main(String[] args) {
        MetadataManager manager = new MetadataManager();

        // Adding metadata
        String id1 = manager.addMetadata("https://website.com/page1", new Date(), "hash1");
        String id2 = manager.addMetadata("https://website.com/page2", new Date(), "hash2");

        // Retrieving metadata
        DocumentMetadata meta1 = manager.getMetadata(id1);
        System.out.println("Retrieved Metadata: " + meta1);

        // Updating metadata
        meta1.setUrl("https://website.com/updated_page1");
        manager.updateMetadata(id1, meta1);

        // Searching by URL
        List<DocumentMetadata> searchResults = manager.searchMetadataByUrl("https://website.com/updated_page1");
        System.out.println("Search Results: " + searchResults);

        // Deleting metadata
        manager.deleteMetadata(id2);

        // Printing final state of the metadata store
        System.out.println("Final Metadata Store: " + manager.metadataStore);
    }
}