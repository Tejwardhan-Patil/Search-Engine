package distributed_crawling

import (
	"log"
	"net"
	"net/rpc"
	"sync"
	"time"
)

// SyncData represents the data to be synchronized
type SyncData struct {
	URL         string
	LastFetched time.Time
	ContentHash string
	NodeID      string
}

// SynchronizationService manages synchronization between crawlers
type SynchronizationService struct {
	mu          sync.Mutex
	nodeID      string
	peers       map[string]string
	dataStore   map[string]SyncData
	syncChannel chan SyncData
}

// NewSynchronizationService creates a new service
func NewSynchronizationService(nodeID string, peers map[string]string) *SynchronizationService {
	return &SynchronizationService{
		nodeID:      nodeID,
		peers:       peers,
		dataStore:   make(map[string]SyncData),
		syncChannel: make(chan SyncData, 100),
	}
}

// SyncRequest represents a sync request between nodes
type SyncRequest struct {
	Data SyncData
}

// SyncResponse represents the result of a sync operation
type SyncResponse struct {
	Success bool
}

// AddData adds new data to the local node and initiates sync with peers
func (s *SynchronizationService) AddData(data SyncData) {
	s.mu.Lock()
	defer s.mu.Unlock()

	// Add data to the local store
	s.dataStore[data.URL] = data
	log.Printf("Node %s: Added data for URL: %s", s.nodeID, data.URL)

	// Sync with peers asynchronously
	go s.syncWithPeers(data)
}

// syncWithPeers sends data to all connected peers
func (s *SynchronizationService) syncWithPeers(data SyncData) {
	for peerID, address := range s.peers {
		log.Printf("Node %s: Syncing with peer %s at %s", s.nodeID, peerID, address)

		client, err := rpc.Dial("tcp", address)
		if err != nil {
			log.Printf("Node %s: Failed to connect to peer %s: %v", s.nodeID, peerID, err)
			continue
		}

		req := &SyncRequest{Data: data}
		var res SyncResponse
		err = client.Call("SynchronizationService.SyncData", req, &res)
		if err != nil || !res.Success {
			log.Printf("Node %s: Sync failed with peer %s: %v", s.nodeID, peerID, err)
		} else {
			log.Printf("Node %s: Sync succeeded with peer %s", s.nodeID, peerID)
		}
		client.Close()
	}
}

// SyncData receives sync data from a peer
func (s *SynchronizationService) SyncData(req *SyncRequest, res *SyncResponse) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	// Check if data is already up-to-date
	existingData, exists := s.dataStore[req.Data.URL]
	if exists && existingData.ContentHash == req.Data.ContentHash {
		log.Printf("Node %s: Data for URL %s already up-to-date", s.nodeID, req.Data.URL)
		res.Success = true
		return nil
	}

	// Update local data store
	s.dataStore[req.Data.URL] = req.Data
	log.Printf("Node %s: Synchronized data for URL %s", s.nodeID, req.Data.URL)
	res.Success = true

	return nil
}

// Start starts the synchronization service on the specified address
func (s *SynchronizationService) Start(address string) error {
	rpc.Register(s)
	listener, err := net.Listen("tcp", address)
	if err != nil {
		return err
	}
	log.Printf("Node %s: Synchronization service started at %s", s.nodeID, address)

	// Accept incoming connections
	for {
		conn, err := listener.Accept()
		if err != nil {
			log.Printf("Node %s: Connection error: %v", s.nodeID, err)
			continue
		}
		go rpc.ServeConn(conn)
	}
}

// DistributedLock for synchronization
type DistributedLock struct {
	mu         sync.Mutex
	lockedBy   string
	lockChan   chan string
	lockStatus bool
}

// NewDistributedLock initializes a new distributed lock
func NewDistributedLock() *DistributedLock {
	return &DistributedLock{
		lockChan:   make(chan string, 1),
		lockStatus: false,
	}
}

// AcquireLock attempts to acquire the lock
func (dl *DistributedLock) AcquireLock(nodeID string) bool {
	dl.mu.Lock()
	defer dl.mu.Unlock()

	if dl.lockStatus {
		log.Printf("Node %s: Lock already acquired by %s", nodeID, dl.lockedBy)
		return false
	}

	// Acquire the lock
	dl.lockedBy = nodeID
	dl.lockStatus = true
	dl.lockChan <- nodeID
	log.Printf("Node %s: Lock acquired", nodeID)
	return true
}

// ReleaseLock releases the lock
func (dl *DistributedLock) ReleaseLock(nodeID string) bool {
	dl.mu.Lock()
	defer dl.mu.Unlock()

	if dl.lockedBy != nodeID || !dl.lockStatus {
		log.Printf("Node %s: Cannot release lock. Either not owner or lock not acquired", nodeID)
		return false
	}

	// Release the lock
	dl.lockStatus = false
	log.Printf("Node %s: Lock released", nodeID)
	return true
}

// WaitForLock waits until the lock is acquired by the current node
func (dl *DistributedLock) WaitForLock(nodeID string) {
	log.Printf("Node %s: Waiting for lock...", nodeID)
	owner := <-dl.lockChan
	log.Printf("Node %s: Lock acquired by %s", nodeID, owner)
}
