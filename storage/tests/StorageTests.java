package storage.tests;

import org.junit.jupiter.api.*;
import storage.document_store.DocumentStore;
import storage.metadata_store.MetadataManager;
import java.util.Optional;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class StorageTests {

    private DocumentStore documentStore;
    private MetadataManager metadataManager;

    @BeforeAll
    public void setup() {
        documentStore = new DocumentStore();
        metadataManager = new MetadataManager();
    }

    @Test
    @DisplayName("Test: Adding Document to DocumentStore")
    public void testAddDocument() {
        documentStore.addDocument("doc1", "This is a test document");

        Optional<String> retrievedDocument = documentStore.getDocumentContent("doc1");
        assertTrue(retrievedDocument.isPresent(), "Document should be present in store");
        assertEquals("This is a test document", retrievedDocument.get(), "Content should match");
    }

    @Test
    @DisplayName("Test: Adding Metadata to MetadataManager")
    public void testAddMetadata() {
        metadataManager.addMetadata("doc1", "2023-10-12", "http://website.com/test");

        Optional<String> retrievedMetadata = metadataManager.getMetadataByDocId("doc1");
        assertTrue(retrievedMetadata.isPresent(), "Metadata should be present");
        assertEquals("2023-10-12", metadataManager.getCrawlDate("doc1").get(), "Crawl date should match");
    }

    @Test
    @DisplayName("Test: Updating Document in DocumentStore")
    public void testUpdateDocument() {
        documentStore.updateDocument("doc1", "Updated content");

        Optional<String> updatedDocument = documentStore.getDocumentContent("doc1");
        assertTrue(updatedDocument.isPresent(), "Document should be present after update");
        assertEquals("Updated content", updatedDocument.get(), "Content should be updated");
    }

    @Test
    @DisplayName("Test: Deleting Document from DocumentStore")
    public void testDeleteDocument() {
        documentStore.deleteDocument("doc1");
        Optional<String> deletedDocument = documentStore.getDocumentContent("doc1");
        assertFalse(deletedDocument.isPresent(), "Document should be deleted");
    }

    @Test
    @DisplayName("Test: Retrieving All Documents")
    public void testRetrieveAllDocuments() {
        documentStore.addDocument("doc2", "Another document");
        List<String> allDocuments = documentStore.getAllDocuments();

        assertEquals(1, allDocuments.size(), "There should be 1 document in the store");
        assertEquals("Another document", allDocuments.get(0), "Document content should match");
    }

    @Test
    @DisplayName("Test: Retrieving Document by URL")
    public void testRetrieveDocumentByUrl() {
        documentStore.addDocument("doc3", "Document from URL");
        metadataManager.addMetadata("doc3", "2023-10-12", "http://website.com/doc3");

        Optional<String> documentByUrl = documentStore.getDocumentByUrl("http://website.com/doc3", metadataManager);
        assertTrue(documentByUrl.isPresent(), "Document should be retrieved by URL");
        assertEquals("Document from URL", documentByUrl.get(), "Document content should match");
    }

    @Test
    @DisplayName("Test: Updating Metadata")
    public void testUpdateMetadata() {
        metadataManager.updateMetadata("doc3", "2024-01-01", "http://website.com/doc3");

        Optional<String> updatedMetadata = metadataManager.getMetadataByDocId("doc3");
        assertTrue(updatedMetadata.isPresent(), "Metadata should be present after update");
        assertEquals("2024-01-01", metadataManager.getCrawlDate("doc3").get(), "Crawl date should be updated");
    }

    @Test
    @DisplayName("Test: Deleting Metadata")
    public void testDeleteMetadata() {
        metadataManager.deleteMetadata("doc3");
        Optional<String> deletedMetadata = metadataManager.getMetadataByDocId("doc3");
        assertFalse(deletedMetadata.isPresent(), "Metadata should be deleted");
    }

    @Test
    @DisplayName("Test: Retrieving Metadata by Document ID")
    public void testRetrieveMetadataByDocId() {
        metadataManager.addMetadata("doc4", "2023-10-13", "http://website.com/doc4");

        Optional<String> retrievedMetadata = metadataManager.getMetadataByDocId("doc4");
        assertTrue(retrievedMetadata.isPresent(), "Metadata should be present");
        assertEquals("2023-10-13", metadataManager.getCrawlDate("doc4").get(), "Crawl date should match");
    }

    @Test
    @DisplayName("Test: Storing and Retrieving Compressed Documents")
    public void testDocumentCompression() {
        documentStore.addCompressedDocument("doc5", "Compressed content");

        Optional<String> retrievedCompressedDocument = documentStore.getDocumentContent("doc5");
        assertTrue(retrievedCompressedDocument.isPresent(), "Compressed document should be stored and retrieved");
        assertEquals("Compressed content", retrievedCompressedDocument.get(), "Content should match");
    }

    @AfterAll
    public void cleanup() {
        documentStore.clearAllDocuments();
        metadataManager.clearAllMetadata();
    }
}