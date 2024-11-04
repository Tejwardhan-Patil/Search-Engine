package distributed.distributed_indexing;

import java.io.*;
import java.util.*;
import java.nio.file.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;

public class IndexMerger {

    private final List<String> indexPaths;
    private final String outputPath;

    public IndexMerger(List<String> indexPaths, String outputPath) {
        this.indexPaths = indexPaths;
        this.outputPath = outputPath;
    }

    public void mergeIndexes() throws IOException {
        Map<String, List<Posting>> globalInvertedIndex = new ConcurrentHashMap<>();

        ExecutorService executor = Executors.newFixedThreadPool(indexPaths.size());
        List<Future<Map<String, List<Posting>>>> futures = new ArrayList<>();

        for (String path : indexPaths) {
            futures.add(executor.submit(() -> loadIndex(path)));
        }

        for (Future<Map<String, List<Posting>>> future : futures) {
            try {
                Map<String, List<Posting>> localIndex = future.get();
                mergeLocalIndex(globalInvertedIndex, localIndex);
            } catch (InterruptedException | ExecutionException e) {
                e.printStackTrace();
            }
        }

        executor.shutdown();
        saveMergedIndex(globalInvertedIndex);
    }

    private Map<String, List<Posting>> loadIndex(String path) throws IOException {
        Map<String, List<Posting>> localIndex = new HashMap<>();
        try (BufferedReader reader = Files.newBufferedReader(Paths.get(path))) {
            String line;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split(":");
                String term = parts[0];
                List<Posting> postings = Arrays.stream(parts[1].split(";"))
                        .map(Posting::fromString)
                        .collect(Collectors.toList());
                localIndex.put(term, postings);
            }
        }
        return localIndex;
    }

    private void mergeLocalIndex(Map<String, List<Posting>> globalIndex, Map<String, List<Posting>> localIndex) {
        localIndex.forEach((term, postings) -> {
            globalIndex.merge(term, postings, (existingPostings, newPostings) -> {
                existingPostings.addAll(newPostings);
                return existingPostings;
            });
        });
    }

    private void saveMergedIndex(Map<String, List<Posting>> globalIndex) throws IOException {
        try (BufferedWriter writer = Files.newBufferedWriter(Paths.get(outputPath))) {
            for (Map.Entry<String, List<Posting>> entry : globalIndex.entrySet()) {
                writer.write(entry.getKey() + ":" + entry.getValue().stream()
                        .map(Posting::toString)
                        .collect(Collectors.joining(";")) + "\n");
            }
        }
    }

    public static class Posting {
        private final int documentId;
        private final int termFrequency;

        public Posting(int documentId, int termFrequency) {
            this.documentId = documentId;
            this.termFrequency = termFrequency;
        }

        public static Posting fromString(String str) {
            String[] parts = str.split(",");
            return new Posting(Integer.parseInt(parts[0]), Integer.parseInt(parts[1]));
        }

        @Override
        public String toString() {
            return documentId + "," + termFrequency;
        }
    }

    public static void main(String[] args) {
        if (args.length < 2) {
            System.err.println("Usage: java IndexMerger <output-path> <index-paths>");
            System.exit(1);
        }

        String outputPath = args[0];
        List<String> indexPaths = Arrays.asList(Arrays.copyOfRange(args, 1, args.length));

        IndexMerger merger = new IndexMerger(indexPaths, outputPath);
        try {
            merger.mergeIndexes();
            System.out.println("Index merging complete.");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}