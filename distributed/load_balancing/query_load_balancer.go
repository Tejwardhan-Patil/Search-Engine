package load_balancing

import (
	"errors"
	"fmt"
	"math/rand"
	"net/http"
	"sync"
	"time"
)

// Node represents a single query processing node
type Node struct {
	ID       string
	Address  string
	IsActive bool
	Load     int
}

// LoadBalancer distributes queries across multiple processing nodes
type LoadBalancer struct {
	nodes     []*Node
	mutex     sync.Mutex
	threshold int // Threshold to redistribute load
}

// NewLoadBalancer initializes a LoadBalancer with given nodes
func NewLoadBalancer(nodeAddresses []string, threshold int) (*LoadBalancer, error) {
	if len(nodeAddresses) == 0 {
		return nil, errors.New("no nodes provided")
	}
	nodes := make([]*Node, len(nodeAddresses))
	for i, addr := range nodeAddresses {
		nodes[i] = &Node{
			ID:       fmt.Sprintf("node-%d", i+1),
			Address:  addr,
			IsActive: true,
			Load:     0,
		}
	}
	return &LoadBalancer{
		nodes:     nodes,
		threshold: threshold,
	}, nil
}

// SelectNode selects the least loaded active node to handle a query
func (lb *LoadBalancer) SelectNode() (*Node, error) {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	var selectedNode *Node
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

// BalanceLoad distributes the incoming query load across nodes
func (lb *LoadBalancer) BalanceLoad(query string) error {
	node, err := lb.SelectNode()
	if err != nil {
		return err
	}

	err = lb.forwardQueryToNode(node, query)
	if err != nil {
		lb.MarkNodeInactive(node)
		return err
	}

	node.Load++
	if node.Load > lb.threshold {
		go lb.redistributeLoad(node)
	}

	return nil
}

// forwardQueryToNode forwards the query to the selected node
func (lb *LoadBalancer) forwardQueryToNode(node *Node, query string) error {
	url := fmt.Sprintf("http://%s/query", node.Address)
	req, err := http.NewRequest("POST", url, nil)
	if err != nil {
		return errors.New("failed to create request")
	}

	q := req.URL.Query()
	q.Add("query", query)
	req.URL.RawQuery = q.Encode()

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil || resp.StatusCode != http.StatusOK {
		return errors.New("failed to forward query to node")
	}

	fmt.Printf("Query '%s' sent to node %s\n", query, node.ID)
	return nil
}

// MarkNodeInactive marks a node as inactive
func (lb *LoadBalancer) MarkNodeInactive(node *Node) {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()
	node.IsActive = false
	fmt.Printf("Node %s marked inactive\n", node.ID)
}

// redistributeLoad redistributes the load of an overloaded node
func (lb *LoadBalancer) redistributeLoad(overloadedNode *Node) {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	overloadedNode.Load = 0 // Reset load of the overloaded node
	fmt.Printf("Redistributing load from node %s\n", overloadedNode.ID)

	for i := 0; i < len(lb.nodes); i++ {
		if lb.nodes[i].IsActive && lb.nodes[i] != overloadedNode {
			lb.nodes[i].Load--
		}
	}
}

// MonitorNodes checks the health of nodes periodically
func (lb *LoadBalancer) MonitorNodes(interval time.Duration) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for range ticker.C {
		for _, node := range lb.nodes {
			go lb.checkNodeHealth(node)
		}
	}
}

// checkNodeHealth pings the node to check its health status
func (lb *LoadBalancer) checkNodeHealth(node *Node) {
	resp, err := http.Get(fmt.Sprintf("http://%s/health", node.Address))
	if err != nil || resp.StatusCode != http.StatusOK {
		lb.MarkNodeInactive(node)
	} else {
		node.IsActive = true
	}
}

// AddNode adds a new node to the load balancer
func (lb *LoadBalancer) AddNode(address string) {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	newNode := &Node{
		ID:       fmt.Sprintf("node-%d", len(lb.nodes)+1),
		Address:  address,
		IsActive: true,
		Load:     0,
	}
	lb.nodes = append(lb.nodes, newNode)
	fmt.Printf("Added new node: %s\n", newNode.ID)
}

// RemoveNode removes a node from the load balancer
func (lb *LoadBalancer) RemoveNode(nodeID string) error {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	for i, node := range lb.nodes {
		if node.ID == nodeID {
			lb.nodes = append(lb.nodes[:i], lb.nodes[i+1:]...)
			fmt.Printf("Removed node: %s\n", nodeID)
			return nil
		}
	}
	return errors.New("node not found")
}

// RandomizeLoad simulates random load assignment to nodes
func (lb *LoadBalancer) RandomizeLoad() {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	for _, node := range lb.nodes {
		node.Load = rand.Intn(lb.threshold)
	}
}

// NodeCount returns the number of active nodes
func (lb *LoadBalancer) NodeCount() int {
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

// ResetLoad resets the load of all nodes
func (lb *LoadBalancer) ResetLoad() {
	lb.mutex.Lock()
	defer lb.mutex.Unlock()

	for _, node := range lb.nodes {
		node.Load = 0
	}
}

func main() {
	// Node addresses
	nodeAddresses := []string{"127.0.0.1:8001", "127.0.0.1:8002", "127.0.0.1:8003"}
	lb, err := NewLoadBalancer(nodeAddresses, 10)
	if err != nil {
		fmt.Println("Error initializing load balancer:", err)
		return
	}

	go lb.MonitorNodes(5 * time.Second)

	queries := []string{"query1", "query2", "query3", "query4", "query5"}
	for _, query := range queries {
		err := lb.BalanceLoad(query)
		if err != nil {
			fmt.Println("Error balancing load:", err)
		}
		time.Sleep(1 * time.Second)
	}

	// Simulate adding and removing nodes
	time.Sleep(10 * time.Second)
	lb.AddNode("127.0.0.1:8004")
	lb.RemoveNode("node-2")
	lb.RandomizeLoad()
}
