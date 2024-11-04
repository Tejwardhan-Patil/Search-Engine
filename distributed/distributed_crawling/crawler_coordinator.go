package distributed_crawling

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"
)

// CrawlerCoordinator is responsible for coordinating multiple crawler instances
type CrawlerCoordinator struct {
	urlQueue     []string
	crawlers     []*Crawler
	results      map[string]string
	resultMutex  sync.Mutex
	crawlerMutex sync.Mutex
	maxCrawlers  int
	ctx          context.Context
	cancelFunc   context.CancelFunc
	errorChan    chan error
	taskComplete chan struct{}
	wg           sync.WaitGroup
}

// Crawler represents an individual crawler worker
type Crawler struct {
	id     int
	active bool
}

// NewCrawlerCoordinator initializes a new CrawlerCoordinator
func NewCrawlerCoordinator(urlQueue []string, maxCrawlers int) *CrawlerCoordinator {
	ctx, cancel := context.WithCancel(context.Background())
	return &CrawlerCoordinator{
		urlQueue:     urlQueue,
		crawlers:     make([]*Crawler, 0, maxCrawlers),
		results:      make(map[string]string),
		maxCrawlers:  maxCrawlers,
		ctx:          ctx,
		cancelFunc:   cancel,
		errorChan:    make(chan error),
		taskComplete: make(chan struct{}),
	}
}

// Start initializes the crawling process with the available crawlers
func (cc *CrawlerCoordinator) Start() {
	log.Println("Starting CrawlerCoordinator")

	for i := 0; i < cc.maxCrawlers; i++ {
		crawler := &Crawler{id: i, active: false}
		cc.crawlers = append(cc.crawlers, crawler)
	}

	go cc.assignTasks()

	select {
	case <-cc.taskComplete:
		log.Println("All tasks completed.")
	case err := <-cc.errorChan:
		log.Printf("Error occurred during crawling: %v\n", err)
		cc.cancelFunc()
	}

	cc.wg.Wait() // Wait for all crawlers to complete
}

// assignTasks distributes URLs to idle crawlers
func (cc *CrawlerCoordinator) assignTasks() {
	cc.wg.Add(1)
	defer cc.wg.Done()

	taskCh := make(chan string)

	// Start crawlers
	for _, crawler := range cc.crawlers {
		go cc.runCrawler(crawler, taskCh)
	}

	// Feed tasks to task channel
	for _, url := range cc.urlQueue {
		select {
		case <-cc.ctx.Done():
			log.Println("Crawling process stopped")
			return
		case taskCh <- url:
			log.Printf("Assigned URL to crawler: %s", url)
		}
	}

	close(taskCh) // No more tasks
}

// runCrawler processes assigned URLs
func (cc *CrawlerCoordinator) runCrawler(crawler *Crawler, taskCh <-chan string) {
	cc.wg.Add(1)
	defer cc.wg.Done()

	for {
		select {
		case <-cc.ctx.Done():
			log.Printf("Crawler %d stopped", crawler.id)
			return
		case url, ok := <-taskCh:
			if !ok {
				log.Printf("Crawler %d no more tasks.", crawler.id)
				return
			}
			crawler.active = true
			cc.crawl(url, crawler.id)
			crawler.active = false
		}
	}
}

// crawl fetches the URL and stores the result
func (cc *CrawlerCoordinator) crawl(url string, crawlerID int) {
	log.Printf("Crawler %d fetching URL: %s", crawlerID, url)
	resp, err := http.Get(url)
	if err != nil {
		cc.errorChan <- fmt.Errorf("crawler %d failed to fetch %s: %v", crawlerID, url, err)
		return
	}
	defer resp.Body.Close()

	cc.resultMutex.Lock()
	cc.results[url] = resp.Status
	cc.resultMutex.Unlock()

	log.Printf("Crawler %d successfully fetched: %s", crawlerID, url)
}

// Stop gracefully stops the crawling process
func (cc *CrawlerCoordinator) Stop() {
	cc.cancelFunc()
}

// GetResults returns the results of the crawling process
func (cc *CrawlerCoordinator) GetResults() map[string]string {
	cc.resultMutex.Lock()
	defer cc.resultMutex.Unlock()

	return cc.results
}

// monitorCrawlers continuously checks for inactive crawlers and reassigns tasks
func (cc *CrawlerCoordinator) monitorCrawlers() {
	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-cc.ctx.Done():
			return
		case <-ticker.C:
			cc.crawlerMutex.Lock()
			inactiveCount := 0
			for _, crawler := range cc.crawlers {
				if !crawler.active {
					inactiveCount++
				}
			}
			if inactiveCount == len(cc.crawlers) {
				cc.taskComplete <- struct{}{}
			}
			cc.crawlerMutex.Unlock()
		}
	}
}

// main function
func main() {
	urls := []string{
		"http://website.com/page1",
		"http://website.com/page2",
		"http://website.com/page3",
	}

	coordinator := NewCrawlerCoordinator(urls, 3)
	go coordinator.Start()

	time.Sleep(30 * time.Second) // simulate some delay for crawling to happen

	results := coordinator.GetResults()
	for url, status := range results {
		fmt.Printf("URL: %s, Status: %s\n", url, status)
	}

	coordinator.Stop()
}
