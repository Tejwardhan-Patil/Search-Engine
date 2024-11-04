package crawler

import (
	"errors"
	"fmt"
	"sync"
	"time"
)

// URLQueue represents a thread-safe queue for managing URLs to be crawled
type URLQueue struct {
	queue    []string
	visited  map[string]bool
	lock     sync.Mutex
	notEmpty *sync.Cond
	maxSize  int
}

// NewURLQueue initializes a new URL queue with a given maximum size
func NewURLQueue(maxSize int) *URLQueue {
	q := &URLQueue{
		queue:   make([]string, 0, maxSize),
		visited: make(map[string]bool),
		maxSize: maxSize,
	}
	q.notEmpty = sync.NewCond(&q.lock)
	return q
}

// AddURL adds a new URL to the queue if it hasn't been visited
func (q *URLQueue) AddURL(url string) error {
	q.lock.Lock()
	defer q.lock.Unlock()

	if len(q.queue) >= q.maxSize {
		return errors.New("queue is full")
	}

	if q.visited[url] {
		return nil // URL has already been visited
	}

	q.queue = append(q.queue, url)
	q.visited[url] = true
	q.notEmpty.Signal() // Notify any waiting goroutines that the queue is not empty

	return nil
}

// PopURL removes and returns the next URL from the queue, blocking if the queue is empty
func (q *URLQueue) PopURL() (string, error) {
	q.lock.Lock()
	defer q.lock.Unlock()

	for len(q.queue) == 0 {
		q.notEmpty.Wait() // Block until queue is not empty
	}

	url := q.queue[0]
	q.queue = q.queue[1:]
	return url, nil
}

// IsEmpty checks whether the URL queue is empty
func (q *URLQueue) IsEmpty() bool {
	q.lock.Lock()
	defer q.lock.Unlock()
	return len(q.queue) == 0
}

// Size returns the current size of the queue
func (q *URLQueue) Size() int {
	q.lock.Lock()
	defer q.lock.Unlock()
	return len(q.queue)
}

// Visited checks if a URL has been visited
func (q *URLQueue) Visited(url string) bool {
	q.lock.Lock()
	defer q.lock.Unlock()
	return q.visited[url]
}

// ProcessURLs is a worker function that continuously pops and processes URLs from the queue
func (q *URLQueue) ProcessURLs(workerID int, processFunc func(string)) {
	for {
		url, err := q.PopURL()
		if err != nil {
			fmt.Printf("Worker %d: Error popping URL: %v\n", workerID, err)
			return
		}

		// Process the URL
		processFunc(url)
	}
}

// ProcessWorkerPool starts a pool of workers to process URLs concurrently
func (q *URLQueue) ProcessWorkerPool(workerCount int, processFunc func(string)) {
	for i := 1; i <= workerCount; i++ {
		go q.ProcessURLs(i, processFunc)
	}
}

// Crawl simulates crawling a URL
func Crawl(url string) {
	fmt.Printf("Crawling URL: %s\n", url)
	time.Sleep(1 * time.Second) // Simulate time delay for crawling
}

// Usage of the URLQueue with worker pool and concurrent processing
func main() {
	maxQueueSize := 100
	queue := NewURLQueue(maxQueueSize)

	// Add some URLs to the queue
	urls := []string{
		"https://website.com/page1",
		"https://website.com/page2",
		"https://website.com/page3",
		"https://website.com/page4",
		"https://website.com/page5",
	}

	for _, url := range urls {
		err := queue.AddURL(url)
		if err != nil {
			fmt.Printf("Error adding URL: %v\n", err)
		}
	}

	// Start a worker pool with 3 workers to process the URLs
	workerCount := 3
	queue.ProcessWorkerPool(workerCount, Crawl)

	// Wait for a while to let the workers process the URLs
	time.Sleep(10 * time.Second)
}
