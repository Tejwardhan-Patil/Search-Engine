package load_balancing

import (
	"errors"
	"fmt"
	"math/rand"
	"net/http"
	"sync"
	"time"
)

// CrawlerNode represents a single crawler node
type CrawlerNode struct {
	ID       string
	Address  string
	IsActive bool
	Load     int
	MaxLoad  int
}

// CrawlerLoadBalancer manages load distribution among crawler nodes
type CrawlerLoadBalancer struct {
	nodes []*CrawlerNode
	mutex sync.Mutex
}

// NewCrawlerLoadBalancer initializes a CrawlerLoadBalancer with the given nodes
func NewCrawlerLoadBalancer(nodeAddresses []string, maxLoad int) (*CrawlerLoadBalancer, error) {
	if len(nodeAddresses) == 0 {
		return nil, errors.New("no nodes provided")
	}
	nodes := make([]*CrawlerNode, len(nodeAddresses))
	for i, addr := range nodeAddresses {
		nodes[i] = &CrawlerNode{
			ID:       fmt.Sprintf("crawler-node-%d", i+1),
			Address:  addr,
			IsActive: true,
			Load:     0,
			MaxLoad:  maxLoad,
		}
	}
	return &CrawlerLoadBalancer{
		nodes: nodes,
	}, nil
}

// SelectNode selects the least loaded active node to handle the next crawl task
func (lb *CrawlerLoadBalancer) SelectNode() (*CrawlerNode, error) {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	var selectedNode *CrawlerNode
	minLoad := int(^uint(0) >> 1) // Max int value

	for _, node := range lb.nodes {
		if node.IsActive && node.Load < minLoad {
			selectedNode = node
			minLoad = node.Load
		}
	}

	if selectedNode == nil {
		return nil, errors.New("no active nodes available")
	}

	return selectedNode, nil
}

// AssignCrawlTask assigns a crawl task to the least loaded node
func (lb *CrawlerLoadBalancer) AssignCrawlTask(url string) error {
	node, err := lb.SelectNode()
	if err != nil {
		return err
	}

	err = lb.forwardCrawlTaskToNode(node, url)
	if err != nil {
		lb.MarkNodeInactive(node)
		return err
	}

	node.Load++
	if node.Load >= node.MaxLoad {
		go lb.redistributeLoad(node)
	}

	return nil
}

// forwardCrawlTaskToNode forwards the crawl task to the selected node
func (lb *CrawlerLoadBalancer) forwardCrawlTaskToNode(node *CrawlerNode, url string) error {
	resp, err := http.Post(fmt.Sprintf("http://%s/crawl", node.Address), "application/json", nil)
	if err != nil || resp.StatusCode != http.StatusOK {
		return errors.New("failed to forward crawl task to node")
	}
	fmt.Printf("Crawl task for %s sent to node %s\n", url, node.ID)
	return nil
}

// MarkNodeInactive marks a node as inactive due to errors
func (lb *CrawlerLoadBalancer) MarkNodeInactive(node *CrawlerNode) {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()
	node.IsActive = false
	fmt.Printf("Crawler node %s marked inactive\n", node.ID)
}

// redistributeLoad redistributes the load from an overloaded or failed node
func (lb *CrawlerLoadBalancer) redistributeLoad(overloadedNode *CrawlerNode) {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	fmt.Printf("Redistributing load from crawler node %s\n", overloadedNode.ID)
	overloadedNode.Load = 0 // Reset load of the overloaded node

	for _, node := range lb.nodes {
		if node.IsActive && node != overloadedNode && node.Load < node.MaxLoad {
			node.Load++
			fmt.Printf("Redistributed task to node %s\n", node.ID)
		}
	}
}

// MonitorNodes periodically checks the health of the crawler nodes
func (lb *CrawlerLoadBalancer) MonitorNodes(interval time.Duration) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for range ticker.C {
		for _, node := range lb.nodes {
			go lb.checkNodeHealth(node)
		}
	}
}

// checkNodeHealth checks the health of a single crawler node
func (lb *CrawlerLoadBalancer) checkNodeHealth(node *CrawlerNode) {
	resp, err := http.Get(fmt.Sprintf("http://%s/health", node.Address))
	if err != nil || resp.StatusCode != http.StatusOK {
		lb.MarkNodeInactive(node)
	} else {
		node.IsActive = true
	}
}

// AddNode adds a new crawler node to the load balancer
func (lb *CrawlerLoadBalancer) AddNode(address string, maxLoad int) {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	newNode := &CrawlerNode{
		ID:       fmt.Sprintf("crawler-node-%d", len(lb.nodes)+1),
		Address:  address,
		IsActive: true,
		Load:     0,
		MaxLoad:  maxLoad,
	}
	lb.nodes = append(lb.nodes, newNode)
	fmt.Printf("Added new crawler node: %s\n", newNode.ID)
}

// RemoveNode removes a crawler node from the load balancer
func (lb *CrawlerLoadBalancer) RemoveNode(nodeID string) error {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	for i, node := range lb.nodes {
		if node.ID == nodeID {
			lb.nodes = append(lb.nodes[:i], lb.nodes[i+1:]...)
			fmt.Printf("Removed crawler node: %s\n", nodeID)
			return nil
		}
	}
	return errors.New("node not found")
}

// RandomizeLoad simulates random load assignment to nodes
func (lb *CrawlerLoadBalancer) RandomizeLoad() {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	for _, node := range lb.nodes {
		node.Load = rand.Intn(node.MaxLoad)
	}
}

// NodeCount returns the number of active nodes
func (lb *CrawlerLoadBalancer) NodeCount() int {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	count := 0
	for _, node := range lb.nodes {
		if node.IsActive {
			count++
		}
	}
	return count
}

// ResetLoad resets the load of all crawler nodes
func (lb *CrawlerLoadBalancer) ResetLoad() {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	for _, node := range lb.nodes {
		node.Load = 0
	}
}
