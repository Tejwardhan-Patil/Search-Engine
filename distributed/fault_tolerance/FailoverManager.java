package distributed.fault_tolerance;

import java.util.*;
import java.util.concurrent.*;
import java.util.logging.Level;
import java.util.logging.Logger;

public class FailoverManager {
    
    private static final Logger logger = Logger.getLogger(FailoverManager.class.getName());
    
    // Node states
    private enum NodeState {
        ACTIVE, BACKUP, FAILED
    }

    // Representation of a node in the distributed system
    public static class Node {
        private String nodeId;
        private NodeState state;
        private long lastHeartbeat;
        
        public Node(String nodeId) {
            this.nodeId = nodeId;
            this.state = NodeState.BACKUP;
            this.lastHeartbeat = System.currentTimeMillis();
        }
        
        public String getNodeId() {
            return nodeId;
        }

        public NodeState getState() {
            return state;
        }

        public void setState(NodeState state) {
            this.state = state;
        }

        public long getLastHeartbeat() {
            return lastHeartbeat;
        }

        public void updateHeartbeat() {
            this.lastHeartbeat = System.currentTimeMillis();
        }
    }
    
    // Heartbeat interval for active nodes
    private static final long HEARTBEAT_INTERVAL = 5000;
    // Timeout period for detecting failure
    private static final long FAILOVER_TIMEOUT = 10000;
    
    // List of nodes in the system
    private List<Node> nodes;
    private Node activeNode;
    private ScheduledExecutorService scheduler;
    
    public FailoverManager() {
        this.nodes = new ArrayList<>();
        this.scheduler = Executors.newScheduledThreadPool(1);
    }

    // Add a node to the system
    public void addNode(Node node) {
        nodes.add(node);
        logger.log(Level.INFO, "Node added: " + node.getNodeId());
    }

    // Remove a node from the system
    public void removeNode(String nodeId) {
        nodes.removeIf(n -> n.getNodeId().equals(nodeId));
        logger.log(Level.INFO, "Node removed: " + nodeId);
    }
    
    // Start monitoring nodes and managing failover
    public void start() {
        scheduler.scheduleAtFixedRate(this::checkNodes, 0, HEARTBEAT_INTERVAL, TimeUnit.MILLISECONDS);
        logger.log(Level.INFO, "Failover manager started");
    }

    // Check the status of nodes and handle failover
    private void checkNodes() {
        long currentTime = System.currentTimeMillis();
        
        if (activeNode != null && currentTime - activeNode.getLastHeartbeat() > FAILOVER_TIMEOUT) {
            logger.log(Level.WARNING, "Active node failed: " + activeNode.getNodeId());
            activeNode.setState(NodeState.FAILED);
            performFailover();
        } else if (activeNode != null) {
            logger.log(Level.INFO, "Active node is healthy: " + activeNode.getNodeId());
        } else {
            performFailover();
        }
    }

    // Perform failover by promoting a backup node to active
    private void performFailover() {
        Optional<Node> backupNodeOpt = nodes.stream()
                                            .filter(n -> n.getState() == NodeState.BACKUP)
                                            .findFirst();
        
        if (backupNodeOpt.isPresent()) {
            Node backupNode = backupNodeOpt.get();
            backupNode.setState(NodeState.ACTIVE);
            activeNode = backupNode;
            logger.log(Level.INFO, "Failover successful, new active node: " + activeNode.getNodeId());
        } else {
            logger.log(Level.SEVERE, "No backup node available for failover");
        }
    }
    
    // Simulate heartbeat received from a node
    public void receiveHeartbeat(String nodeId) {
        nodes.stream()
             .filter(n -> n.getNodeId().equals(nodeId))
             .findFirst()
             .ifPresent(Node::updateHeartbeat);
        logger.log(Level.INFO, "Heartbeat received from node: " + nodeId);
    }

    // Shut down the failover manager
    public void shutdown() {
        scheduler.shutdownNow();
        logger.log(Level.INFO, "Failover manager shut down");
    }

    // Test scenario
    public static void main(String[] args) throws InterruptedException {
        FailoverManager manager = new FailoverManager();
        
        Node node1 = new Node("Node1");
        Node node2 = new Node("Node2");
        Node node3 = new Node("Node3");

        manager.addNode(node1);
        manager.addNode(node2);
        manager.addNode(node3);
        
        // Mark Node1 as active and Node2, Node3 as backups
        node1.setState(NodeState.ACTIVE);
        node2.setState(NodeState.BACKUP);
        node3.setState(NodeState.BACKUP);
        manager.activeNode = node1;
        
        // Start the failover manager
        manager.start();
        
        // Simulate heartbeats from Node1
        for (int i = 0; i < 5; i++) {
            Thread.sleep(3000);
            manager.receiveHeartbeat("Node1");
        }

        // Simulate Node1 failure by not sending further heartbeats
        Thread.sleep(15000);
        
        // Manager will failover to Node2
        Thread.sleep(10000);
        
        // Shut down the manager
        manager.shutdown();
    }
}