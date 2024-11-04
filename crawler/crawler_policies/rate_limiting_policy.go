package crawler_policies

import (
	"context"
	"errors"
	"net/http"
	"sync"
	"time"
)

// RateLimiter defines the structure for rate limiting policy
type RateLimiter struct {
	maxRequests int
	interval    time.Duration
	tokens      chan struct{}
	mu          sync.Mutex
	lastRequest time.Time
	cooldown    time.Duration
	ctx         context.Context
	cancel      context.CancelFunc
}

// NewRateLimiter initializes a new RateLimiter instance
func NewRateLimiter(maxRequests int, interval, cooldown time.Duration) *RateLimiter {
	if maxRequests <= 0 {
		panic("maxRequests must be greater than zero")
	}
	ctx, cancel := context.WithCancel(context.Background())
	rl := &RateLimiter{
		maxRequests: maxRequests,
		interval:    interval,
		tokens:      make(chan struct{}, maxRequests),
		cooldown:    cooldown,
		ctx:         ctx,
		cancel:      cancel,
	}
	rl.startRefill()
	return rl
}

// startRefill starts the token refill mechanism
func (rl *RateLimiter) startRefill() {
	ticker := time.NewTicker(rl.interval / time.Duration(rl.maxRequests))
	go func() {
		for {
			select {
			case <-ticker.C:
				rl.refill()
			case <-rl.ctx.Done():
				ticker.Stop()
				return
			}
		}
	}()
}

// refill adds tokens to the bucket until full
func (rl *RateLimiter) refill() {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	if len(rl.tokens) < cap(rl.tokens) {
		rl.tokens <- struct{}{}
	}
}

// Allow checks if a request can proceed under the rate limiting policy
func (rl *RateLimiter) Allow() bool {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	if len(rl.tokens) > 0 {
		<-rl.tokens
		rl.lastRequest = time.Now()
		return true
	}
	return false
}

// EnforceRateLimit wraps an HTTP request with rate-limiting logic
func (rl *RateLimiter) EnforceRateLimit(req *http.Request) (*http.Response, error) {
	if !rl.Allow() {
		return nil, errors.New("rate limit exceeded")
	}

	client := &http.Client{
		Timeout: rl.interval,
	}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}

	return resp, nil
}

// StopRateLimiter stops the refill process and cleans up
func (rl *RateLimiter) StopRateLimiter() {
	rl.cancel()
}

// Cooldown allows a pause in crawling during high traffic periods
func (rl *RateLimiter) CooldownPeriod() {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	time.Sleep(rl.cooldown)
}

// Crawler defines a structure to manage crawling processes
type Crawler struct {
	rateLimiter *RateLimiter
}

// NewCrawler initializes a new crawler with a rate limiting policy
func NewCrawler(rateLimiter *RateLimiter) *Crawler {
	return &Crawler{
		rateLimiter: rateLimiter,
	}
}

// FetchURL fetches the content of a URL with rate limiting applied
func (c *Crawler) FetchURL(url string) (*http.Response, error) {
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}

	resp, err := c.rateLimiter.EnforceRateLimit(req)
	if err != nil {
		return nil, err
	}

	return resp, nil
}

// GracefulShutdown allows the crawler to shutdown while respecting rate limits
func (c *Crawler) GracefulShutdown() {
	c.rateLimiter.StopRateLimiter()
}

// Usage
func main() {
	maxRequests := 5
	interval := 10 * time.Second
	cooldown := 2 * time.Second

	rateLimiter := NewRateLimiter(maxRequests, interval, cooldown)
	crawler := NewCrawler(rateLimiter)

	urls := []string{
		"https://website.com/page1",
		"https://website.com/page2",
		"https://website.com/page3",
		"https://website.com/page4",
		"https://website.com/page5",
	}

	for _, url := range urls {
		resp, err := crawler.FetchURL(url)
		if err != nil {
			if err.Error() == "rate limit exceeded" {
				rateLimiter.CooldownPeriod() // Apply cooldown before retrying
			} else {
				panic(err)
			}
		} else {
			defer resp.Body.Close()
			// Handle response body processing
		}
	}

	// Gracefully shutdown the rate limiter
	crawler.GracefulShutdown()
}
