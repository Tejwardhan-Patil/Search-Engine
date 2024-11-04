package fault_tolerance

import (
	"fmt"
	"log"
	"net"
	"os"
	"sync"
	"time"
)

const (
	replicationFactor = 3
	nodePort          = ":8080"
)

// Node represents a single node in the distributed system
type Node struct {
	IP    string
	ID    string
	Alive bool
	Mutex sync.Mutex
	Peers []*Node
	Data  map[string]string
}

// Cluster represents the entire distributed cluster
type Cluster struct {
	Nodes []*Node
	Mutex sync.Mutex
}

// ReplicationManager handles data replication across nodes
type ReplicationManager struct {
	Cluster *Cluster
}

// NewNode initializes a new Node
func NewNode(id, ip string) *Node {
	return &Node{
		IP:    ip,
		ID:    id,
		Alive: true,
		Data:  make(map[string]string),
		Peers: []*Node{},
	}
}

// AddPeer adds a peer node to the current node
func (n *Node) AddPeer(peer *Node) {
	n.Mutex.Lock()
	defer n.Mutex.Unlock()
	n.Peers = append(n.Peers, peer)
}

// StoreData stores key-value data on the node
func (n *Node) StoreData(key, value string) {
	n.Mutex.Lock()
	defer n.Mutex.Unlock()
	n.Data[key] = value
	log.Printf("Node %s stored data: %s -> %s", n.ID, key, value)
}

// ReplicateData replicates data across multiple peers
func (n *Node) ReplicateData(key, value string) {
	n.StoreData(key, value)
	for i := 0; i < replicationFactor-1 && i < len(n.Peers); i++ {
		go func(peer *Node) {
			peer.StoreData(key, value)
			log.Printf("Replicated data to Node %s: %s -> %s", peer.ID, key, value)
		}(n.Peers[i])
	}
}

// HealthCheck periodically checks if the node is alive
func (n *Node) HealthCheck() {
	for {
		time.Sleep(5 * time.Second)
		if !n.Alive {
			log.Printf("Node %s is down", n.ID)
		} else {
			log.Printf("Node %s is alive", n.ID)
		}
	}
}

// HandleFailure attempts to recover data from peers
func (n *Node) HandleFailure() {
	for _, peer := range n.Peers {
		if peer.Alive {
			log.Printf("Recovering data from Node %s", peer.ID)
			for key, value := range peer.Data {
				n.StoreData(key, value)
			}
			break
		}
	}
}

// NewCluster initializes a new cluster
func NewCluster() *Cluster {
	return &Cluster{
		Nodes: []*Node{},
	}
}

// AddNode adds a new node to the cluster
func (c *Cluster) AddNode(node *Node) {
	c.Mutex.Lock()
	defer c.Mutex.Unlock()
	c.Nodes = append(c.Nodes, node)
	for _, existingNode := range c.Nodes {
		if existingNode != node {
			node.AddPeer(existingNode)
			existingNode.AddPeer(node)
		}
	}
	log.Printf("Node %s added to the cluster", node.ID)
}

// NewReplicationManager initializes a new replication manager
func NewReplicationManager(cluster *Cluster) *ReplicationManager {
	return &ReplicationManager{
		Cluster: cluster,
	}
}

// Replicate replicates data across the cluster
func (rm *ReplicationManager) Replicate(key, value string) {
	for _, node := range rm.Cluster.Nodes {
		node.ReplicateData(key, value)
	}
}

// NodeListener listens for incoming data replication requests
func (n *Node) NodeListener() {
	listener, err := net.Listen("tcp", n.IP+nodePort)
	if err != nil {
		log.Fatalf("Error starting listener on Node %s: %v", n.ID, err)
		os.Exit(1)
	}
	defer listener.Close()
	log.Printf("Node %s is listening on %s", n.ID, n.IP+nodePort)

	for {
		conn, err := listener.Accept()
		if err != nil {
			log.Printf("Error accepting connection on Node %s: %v", n.ID, err)
			continue
		}
		go n.HandleConnection(conn)
	}
}

// HandleConnection processes incoming data replication requests
func (n *Node) HandleConnection(conn net.Conn) {
	defer conn.Close()
	var key, value string
	fmt.Fscan(conn, &key, &value)
	n.StoreData(key, value)
}

// ClusterListener monitors cluster-wide node health
func (c *Cluster) ClusterListener() {
	for {
		for _, node := range c.Nodes {
			go node.HealthCheck()
		}
		time.Sleep(10 * time.Second)
	}
}

// SimulateNodeFailure simulates node failure by marking a node as down
func (n *Node) SimulateNodeFailure() {
	n.Mutex.Lock()
	defer n.Mutex.Unlock()
	n.Alive = false
	log.Printf("Node %s has failed", n.ID)
}

// SimulateNodeRecovery simulates node recovery and data restoration
func (n *Node) SimulateNodeRecovery() {
	n.Mutex.Lock()
	defer n.Mutex.Unlock()
	n.Alive = true
	log.Printf("Node %s has recovered", n.ID)
	n.HandleFailure()
}

// TestCluster sets up a test cluster for fault tolerance and replication
func TestCluster() {
	cluster := NewCluster()

	node1 := NewNode("node1", "192.168.1.1")
	node2 := NewNode("node2", "192.168.1.2")
	node3 := NewNode("node3", "192.168.1.3")

	cluster.AddNode(node1)
	cluster.AddNode(node2)
	cluster.AddNode(node3)

	replicationManager := NewReplicationManager(cluster)
	replicationManager.Replicate("key1", "value1")

	// Simulate node failure
	node2.SimulateNodeFailure()

	// Simulate recovery
	node2.SimulateNodeRecovery()

	// Start cluster listener
	go cluster.ClusterListener()

	// Start node listeners
	go node1.NodeListener()
	go node2.NodeListener()
	go node3.NodeListener()

	// Keep the test running
	select {}
}

func main() {
	TestCluster()
}
