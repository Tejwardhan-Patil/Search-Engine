package query_processor.tests;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import org.junit.Before;
import org.junit.Test;
import query_processor.BooleanQueryProcessor;
import query_processor.FuzzyQueryProcessor;
import query_processor.PhraseQueryProcessor;
import query_processor.QueryParserMain;

import java.util.*;


public class QueryProcessingTests {

    private QueryParserMain QueryParserMain;
    private BooleanQueryProcessor booleanQueryProcessor;
    private PhraseQueryProcessor phraseQueryProcessor;
    private FuzzyQueryProcessor fuzzyQueryProcessor;

    @Before
    public void setUp() {
        // Initialize QueryParserMain directly with raw input or compatible constructor
        QueryParserMain = new QueryParserMain(); 
        
        // Setup for BooleanQueryProcessor
        Map<String, List<Integer>> booleanIndex = new HashMap<>();
        booleanIndex.put("search", List.of(1, 2, 3));
        booleanIndex.put("engine", List.of(2, 3, 4));
        booleanIndex.put("fast", List.of(3, 4, 5));
        booleanQueryProcessor = new BooleanQueryProcessor(booleanIndex);
        
        // Setup for PhraseQueryProcessor
        Map<String, Map<Integer, List<Integer>>> phraseIndex = new HashMap<>();
        phraseIndex.put("fast", Map.of(1, List.of(1, 5), 2, List.of(3)));
        phraseIndex.put("search", Map.of(1, List.of(2), 2, List.of(4)));
        phraseIndex.put("engine", Map.of(1, List.of(3), 2, List.of(5)));
        phraseQueryProcessor = new PhraseQueryProcessor(phraseIndex);
        
        // Setup for FuzzyQueryProcessor
        Map<String, Set<String>> fuzzyIndex = new HashMap<>();
        fuzzyIndex.put("apple", Set.of("doc1", "doc2"));
        fuzzyIndex.put("application", Set.of("doc3"));
        fuzzyIndex.put("apricot", Set.of("doc4"));
        fuzzyIndex.put("banana", Set.of("doc5"));
        fuzzyQueryProcessor = new FuzzyQueryProcessor(fuzzyIndex, 2);
    }
       

    // Test for Boolean Query Processing (AND)
    @Test
    public void testBooleanQueryProcessingAND() {
        String query = "search AND engine";
        List<Integer> result = booleanQueryProcessor.processQuery(query);

        assertTrue("Boolean query processing failed", result.size() > 0);
        assertTrue("Boolean query did not return expected documents", result.contains(2));
    }

    // Test for Boolean Query Processing (OR)
    @Test
    public void testBooleanQueryProcessingOR() {
        String query = "search OR engine";
        List<Integer> result = booleanQueryProcessor.processQuery(query);

        assertTrue("Boolean query processing failed", result.size() > 0);
        assertTrue("Boolean query did not return expected documents", result.contains(2));
    }

    // Test for Boolean Query Processing (NOT)
    @Test
    public void testBooleanQueryProcessingNOT() {
        String query = "search AND NOT engine";
        List<Integer> result = booleanQueryProcessor.processQuery(query);

        assertTrue("Boolean query processing failed", result.size() > 0);
        assertTrue("Boolean query did not exclude unexpected documents", !result.contains(2));
    }

    // Test for Phrase Query Processing (Exact match)
    @Test
    public void testPhraseQueryProcessingExactMatch() {
        String query = "\"fast search engine\"";
        List<Integer> result = phraseQueryProcessor.processPhraseQuery(query);

        assertTrue("Phrase query processing failed", result.size() > 0);
        assertTrue("Phrase query did not return exact match", result.contains(1));
    }

    // Test for Phrase Query Processing (No match)
    @Test
    public void testPhraseQueryProcessingNoMatch() {
        String query = "\"nonexistent phrase\"";
        List<Integer> result = phraseQueryProcessor.processPhraseQuery(query);

        assertTrue("Phrase query processing should return no results", result.isEmpty());
    }

    // Test for Fuzzy Query Processing (Single typo)
    @Test
    public void testFuzzyQueryProcessingSingleTypo() {
        String query = "aple"; // Typo in "apple"
        List<String> result = fuzzyQueryProcessor.processQuery(query);

        assertTrue("Fuzzy query processing failed", result.size() > 0);
        assertTrue("Fuzzy query did not correct typo", result.contains("doc1"));
    }

    // Test for Fuzzy Query Processing (Multiple typos)
    @Test
    public void testFuzzyQueryProcessingMultipleTypos() {
        String query = "aplicat"; // Typo in "application"
        List<String> result = fuzzyQueryProcessor.processQuery(query);

        assertTrue("Fuzzy query processing failed", result.size() > 0);
        assertTrue("Fuzzy query did not correct multiple typos", result.contains("doc3"));
    }

    // Test for Query Expansion (Synonym expansion)
    @Test
    public void testQueryExpansionSynonyms() {
        String query = "quick";
        List<String> expandedTerms = QueryParserMain.expandQuery(query);

        assertTrue("Query expansion failed to include synonyms", expandedTerms.contains("fast"));
        assertTrue("Query expansion failed to include synonyms", expandedTerms.contains("rapid"));
    }

    // Test for Query Rewriting (Stemming)
    @Test
    public void testQueryRewritingStemming() {
        String query = "running";
        List<String> rewrittenTerms = QueryParserMain.rewriteQuery(query);

        assertTrue("Query rewriting failed to stem terms", rewrittenTerms.contains("run"));
    }

    // Test for processing complex query (AND, OR, NOT)
    @Test
    public void testComplexQueryProcessing() {
        String query = "search AND engine OR fast AND NOT slow";
        List<Integer> result = booleanQueryProcessor.processQuery(query);

        assertTrue("Complex query processing failed", result.size() > 0);
        assertTrue("Complex query did not return expected documents", result.contains(3));
    }
}