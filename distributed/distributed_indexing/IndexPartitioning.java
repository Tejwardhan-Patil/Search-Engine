package distributed.distributed_indexing;

import java.io.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class IndexPartitioning {

    private final ConcurrentHashMap<String, List<Integer>> invertedIndex = new ConcurrentHashMap<>();
    private final List<String> documents;
    private final int numPartitions;
    private final List<IndexPartition> partitions;

    public IndexPartitioning(List<String> documents, int numPartitions) {
        this.documents = documents;
        this.numPartitions = numPartitions;
        this.partitions = new ArrayList<>();
        createPartitions();
    }

    private void createPartitions() {
        int partitionSize = documents.size() / numPartitions;
        for (int i = 0; i < numPartitions; i++) {
            int start = i * partitionSize;
            int end = (i == numPartitions - 1) ? documents.size() : (i + 1) * partitionSize;
            List<String> partitionDocs = documents.subList(start, end);
            partitions.add(new IndexPartition(partitionDocs, i));
        }
    }

    public void buildIndex() {
        ExecutorService executor = Executors.newFixedThreadPool(numPartitions);
        for (IndexPartition partition : partitions) {
            executor.execute(() -> {
                try {
                    partition.buildLocalIndex();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            });
        }
        executor.shutdown();
        while (!executor.isTerminated()) {
            // Wait for all partitions to finish building
        }
    }

    public void mergePartitions() {
        System.out.println("Merging partitions...");
        for (IndexPartition partition : partitions) {
            partition.mergeLocalIndex(invertedIndex);
        }
    }

    public void printIndex() {
        invertedIndex.forEach((term, postings) -> {
            System.out.println(term + " -> " + postings);
        });
    }

    public static void main(String[] args) throws IOException {
        List<String> documents = Arrays.asList(
                "Document1: Java programming is fun.",
                "Document2: Distributed systems are efficient.",
                "Document3: Index partitioning improves performance.",
                "Document4: Concurrency is challenging.",
                "Document5: Java offers concurrency features."
        );
        
        IndexPartitioning indexPartitioning = new IndexPartitioning(documents, 3);
        indexPartitioning.buildIndex();
        indexPartitioning.mergePartitions();
        indexPartitioning.printIndex();
    }

    static class IndexPartition {

        private final List<String> documents;
        private final int partitionId;
        private final ConcurrentHashMap<String, List<Integer>> localInvertedIndex = new ConcurrentHashMap<>();

        public IndexPartition(List<String> documents, int partitionId) {
            this.documents = documents;
            this.partitionId = partitionId;
        }

        public void buildLocalIndex() throws IOException {
            System.out.println("Building local index for partition " + partitionId);
            for (int docId = 0; docId < documents.size(); docId++) {
                String document = documents.get(docId);
                String[] words = document.split("\\W+");
                for (String word : words) {
                    word = word.toLowerCase();
                    localInvertedIndex.computeIfAbsent(word, k -> new ArrayList<>()).add(docId + partitionId * 1000);
                }
            }
        }

        public void mergeLocalIndex(ConcurrentHashMap<String, List<Integer>> globalInvertedIndex) {
            System.out.println("Merging local index of partition " + partitionId + " into global index.");
            localInvertedIndex.forEach((word, postings) -> {
                globalInvertedIndex.merge(word, postings, (existingList, newList) -> {
                    if (existingList == null) {
                        return newList;
                    }
                    Set<Integer> mergedPostings = new HashSet<>(existingList);
                    mergedPostings.addAll(newList);
                    return new ArrayList<>(mergedPostings);
                });
            });
        }
    }
}