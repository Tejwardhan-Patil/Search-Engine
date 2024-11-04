package documentstore

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"os"
	"sync"
	"time"
)

// Document represents the structure of a document to be stored
type Document struct {
	ID        string            `json:"id"`
	Title     string            `json:"title"`
	Content   string            `json:"content"`
	Metadata  map[string]string `json:"metadata"`
	CreatedAt time.Time         `json:"created_at"`
	UpdatedAt time.Time         `json:"updated_at"`
}

// DocumentDB defines the structure of the in-memory database
type DocumentDB struct {
	documents map[string]*Document
	mutex     sync.RWMutex
}

// NewDocumentDB initializes and returns a new instance of DocumentDB
func NewDocumentDB() *DocumentDB {
	return &DocumentDB{
		documents: make(map[string]*Document),
	}
}

// AddDocument adds a new document to the database
func (db *DocumentDB) AddDocument(doc *Document) error {
	db.mutex.Lock()
	defer db.mutex.Unlock()

	if _, exists := db.documents[doc.ID]; exists {
		return errors.New("document with the same ID already exists")
	}

	doc.CreatedAt = time.Now()
	doc.UpdatedAt = doc.CreatedAt
	db.documents[doc.ID] = doc
	return nil
}

// GetDocument retrieves a document by ID
func (db *DocumentDB) GetDocument(id string) (*Document, error) {
	db.mutex.RLock()
	defer db.mutex.RUnlock()

	if doc, exists := db.documents[id]; exists {
		return doc, nil
	}
	return nil, errors.New("document not found")
}

// UpdateDocument updates the content of a document
func (db *DocumentDB) UpdateDocument(id string, newContent string) error {
	db.mutex.Lock()
	defer db.mutex.Unlock()

	if doc, exists := db.documents[id]; exists {
		doc.Content = newContent
		doc.UpdatedAt = time.Now()
		return nil
	}
	return errors.New("document not found")
}

// DeleteDocument removes a document from the database by ID
func (db *DocumentDB) DeleteDocument(id string) error {
	db.mutex.Lock()
	defer db.mutex.Unlock()

	if _, exists := db.documents[id]; exists {
		delete(db.documents, id)
		return nil
	}
	return errors.New("document not found")
}

// ListDocuments returns a list of all documents
func (db *DocumentDB) ListDocuments() []*Document {
	db.mutex.RLock()
	defer db.mutex.RUnlock()

	var docs []*Document
	for _, doc := range db.documents {
		docs = append(docs, doc)
	}
	return docs
}

// FindDocumentsByMetadata searches for documents by matching metadata key-value pairs
func (db *DocumentDB) FindDocumentsByMetadata(key, value string) []*Document {
	db.mutex.RLock()
	defer db.mutex.RUnlock()

	var results []*Document
	for _, doc := range db.documents {
		if v, exists := doc.Metadata[key]; exists && v == value {
			results = append(results, doc)
		}
	}
	return results
}

// BulkAddDocuments allows adding multiple documents at once
func (db *DocumentDB) BulkAddDocuments(docs []*Document) error {
	db.mutex.Lock()
	defer db.mutex.Unlock()

	for _, doc := range docs {
		if _, exists := db.documents[doc.ID]; exists {
			return fmt.Errorf("document with ID %s already exists", doc.ID)
		}

		doc.CreatedAt = time.Now()
		doc.UpdatedAt = doc.CreatedAt
		db.documents[doc.ID] = doc
	}
	return nil
}

// SearchDocuments searches for documents by matching part of the title
func (db *DocumentDB) SearchDocuments(query string) []*Document {
	db.mutex.RLock()
	defer db.mutex.RUnlock()

	var results []*Document
	for _, doc := range db.documents {
		if contains(doc.Title, query) {
			results = append(results, doc)
		}
	}
	return results
}

// Helper function to check if a string contains a substring
func contains(str, substr string) bool {
	return len(str) >= len(substr) && str[:len(substr)] == substr
}

// ConcurrentFindDocumentsByContent searches for documents concurrently by content matching
func (db *DocumentDB) ConcurrentFindDocumentsByContent(content string) []*Document {
	db.mutex.RLock()
	defer db.mutex.RUnlock()

	var wg sync.WaitGroup
	results := make([]*Document, 0)
	resultsCh := make(chan *Document, len(db.documents))

	for _, doc := range db.documents {
		wg.Add(1)
		go func(d *Document) {
			defer wg.Done()
			if contains(d.Content, content) {
				resultsCh <- d
			}
		}(doc)
	}

	go func() {
		wg.Wait()
		close(resultsCh)
	}()

	for doc := range resultsCh {
		results = append(results, doc)
	}
	return results
}

// BackupDatabase creates a backup of the document database to a file
func (db *DocumentDB) BackupDatabase(filePath string) error {
	db.mutex.RLock()
	defer db.mutex.RUnlock()

	file, err := os.Create(filePath)
	if err != nil {
		return err
	}
	defer file.Close()

	data, err := json.Marshal(db.documents)
	if err != nil {
		return err
	}

	_, err = file.Write(data)
	if err != nil {
		return err
	}

	fmt.Printf("Database backed up to %s\n", filePath)
	return nil
}

// RestoreDatabase restores the database from a backup file
func (db *DocumentDB) RestoreDatabase(filePath string) error {
	db.mutex.Lock()
	defer db.mutex.Unlock()

	file, err := os.Open(filePath)
	if err != nil {
		return err
	}
	defer file.Close()

	data, err := ioutil.ReadAll(file)
	if err != nil {
		return err
	}

	var restoredDocs map[string]*Document
	err = json.Unmarshal(data, &restoredDocs)
	if err != nil {
		return err
	}

	db.documents = restoredDocs
	fmt.Printf("Database restored from %s\n", filePath)
	return nil
}

// PurgeOldDocuments removes documents older than a specific time
func (db *DocumentDB) PurgeOldDocuments(olderThan time.Time) int {
	db.mutex.Lock()
	defer db.mutex.Unlock()

	removedCount := 0
	for id, doc := range db.documents {
		if doc.CreatedAt.Before(olderThan) {
			delete(db.documents, id)
			removedCount++
		}
	}
	return removedCount
}

// GetDocumentCount returns the total number of documents in the database
func (db *DocumentDB) GetDocumentCount() int {
	db.mutex.RLock()
	defer db.mutex.RUnlock()

	return len(db.documents)
}

// ExportDocuments exports all documents to a specified file
func (db *DocumentDB) ExportDocuments(filePath string) error {
	db.mutex.RLock()
	defer db.mutex.RUnlock()

	file, err := os.Create(filePath)
	if err != nil {
		return err
	}
	defer file.Close()

	for _, doc := range db.documents {
		line := fmt.Sprintf("Document ID: %s, Title: %s\n", doc.ID, doc.Title)
		_, err := file.WriteString(line)
		if err != nil {
			return err
		}
	}

	fmt.Printf("Documents exported to %s\n", filePath)
	return nil
}
