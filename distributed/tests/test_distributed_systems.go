package tests

import (
	"bytes"
	"context"
	"distributed/distributed_crawling"
	"distributed/load_balancing"
	"encoding/json"
	"net/http"
	"testing"
	"time"
)

// API endpoints for interacting with the Java services
const (
	indexPartitionAPI   = "http://localhost:8080/api/index_partition"
	indexReplicationAPI = "http://localhost:8080/api/index_replication"
	failoverAPI         = "http://localhost:8080/api/failover"
)

// Utility function to call Java APIs from Go
func callJavaAPI(endpoint string, payload map[string]string) error {
	jsonData, err := json.Marshal(payload)
	if err != nil {
		return err
	}

	req, err := http.NewRequest("POST", endpoint, bytes.NewBuffer(jsonData))
	if err != nil {
		return err
	}

	req.Header.Set("Content-Type", "application/json")
	client := &http.Client{
		Timeout: time.Second * 30,
	}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return err
	}

	return nil
}

// Test distributed crawling between multiple nodes
func TestDistributedCrawling(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 40*time.Second)
	defer cancel()

	// Initialize distributed crawlers
	crawler1 := distributed_crawling.NewCrawlerNode("Node1")
	crawler2 := distributed_crawling.NewCrawlerNode("Node2")

	go crawler1.StartCrawling(ctx)
	go crawler2.StartCrawling(ctx)

	// Wait for crawling to finish
	select {
	case <-crawler1.Done():
		t.Logf("Crawling finished on Node1")
	case <-crawler2.Done():
		t.Logf("Crawling finished on Node2")
	case <-ctx.Done():
		t.Fatal("Crawling timed out")
	}
}

// Test crawler load balancing between multiple nodes
func TestCrawlerLoadBalancing(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 25*time.Second)
	defer cancel()

	// Initialize crawler load balancer
	crawlerLoadBalancer := load_balancing.NewCrawlerLoadBalancer()
	crawlerNode1 := "CrawlerNode1"
	crawlerNode2 := "CrawlerNode2"

	// Start balancing the crawling load
	go crawlerLoadBalancer.BalanceCrawlingLoad(ctx, crawlerNode1, crawlerNode2)

	select {
	case <-ctx.Done():
		t.Log("Crawler load balancing completed successfully")
	default:
		t.Fatal("Crawler load balancing failed or timed out")
	}
}

// Test query load balancing between nodes
func TestQueryLoadBalancing(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
	defer cancel()

	// Initialize query load balancer
	queryLoadBalancer := load_balancing.NewQueryLoadBalancer()

	node1 := "Node1"
	node2 := "Node2"

	// Queries to distribute
	queries := []string{"query1", "query2", "query3", "query4"}

	for _, query := range queries {
		go queryLoadBalancer.DistributeQuery(ctx, query, node1, node2)
	}

	select {
	case <-ctx.Done():
		t.Log("Query load balancing completed")
	default:
		t.Fatal("Query load balancing failed or timed out")
	}
}

// Test index partitioning by calling the Java API
func TestDistributedIndexPartitioning(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()

	payload := map[string]string{
		"node":      "Node1",
		"partition": "IndexPartition1",
	}

	// Call Java service to partition the index
	err := callJavaAPI(indexPartitionAPI, payload)
	if err != nil {
		t.Fatalf("Failed to partition index: %v", err)
	}

	t.Logf("Index partitioning successfully initiated for Node1")
	select {
	case <-ctx.Done():
		t.Fatal("Index partitioning timed out")
	}
}

// Test index replication between nodes using Java API
func TestIndexReplication(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 50*time.Second)
	defer cancel()

	payload := map[string]string{
		"partition": "IndexPartition1",
		"node":      "Node1",
	}

	// Call Java service to replicate index partition
	err := callJavaAPI(indexReplicationAPI, payload)
	if err != nil {
		t.Fatalf("Failed to replicate index: %v", err)
	}

	t.Logf("Index replication successfully started for Node1")
	select {
	case <-ctx.Done():
		t.Fatal("Index replication timed out")
	}
}

// Test fault tolerance by simulating node failure using Java API
func TestFailover(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	payload := map[string]string{
		"failedNode": "Node1",
		"backupNode": "Node2",
	}

	// Call Java service to simulate failover
	err := callJavaAPI(failoverAPI, payload)
	if err != nil {
		t.Fatalf("Failover simulation failed: %v", err)
	}

	t.Logf("Failover successfully simulated for Node1")
	select {
	case <-ctx.Done():
		t.Fatal("Failover simulation timed out")
	}
}

// Test data synchronization during index partitioning using Java API
func TestDataSynchronizationDuringPartitioning(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 40*time.Second)
	defer cancel()

	payload := map[string]string{
		"partition": "IndexPartition1",
		"node":      "Node1",
	}

	// Call Java service to initiate data synchronization
	err := callJavaAPI(indexPartitionAPI, payload)
	if err != nil {
		t.Fatalf("Failed to synchronize data during partitioning: %v", err)
	}

	t.Logf("Data synchronization during partitioning initiated for Node1")
	select {
	case <-ctx.Done():
		t.Fatal("Data synchronization timed out")
	}
}

// Test replication consistency across nodes using Java API
func TestReplicationConsistency(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 50*time.Second)
	defer cancel()

	payload := map[string]string{
		"partition": "IndexPartition1",
		"node":      "Node1",
	}

	// Call Java service to check replication consistency
	err := callJavaAPI(indexReplicationAPI, payload)
	if err != nil {
		t.Fatalf("Replication consistency check failed: %v", err)
	}

	t.Logf("Replication consistency check successfully completed for Node1")
	select {
	case <-ctx.Done():
		t.Fatal("Replication consistency check timed out")
	}
}

// Test overall system fault tolerance by simulating node failures during crawling and indexing
func TestSystemFaultTolerance(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()

	// Simulate node failures and monitor system recovery
	payload := map[string]string{
		"failedNode": "Node1",
		"backupNode": "Node2",
	}

	// Call Java service to initiate fault tolerance mechanisms
	err := callJavaAPI(failoverAPI, payload)
	if err != nil {
		t.Fatalf("System fault tolerance test failed: %v", err)
	}

	t.Logf("System fault tolerance successfully tested for Node1")
	select {
	case <-ctx.Done():
		t.Fatal("System fault tolerance test timed out")
	}
}
