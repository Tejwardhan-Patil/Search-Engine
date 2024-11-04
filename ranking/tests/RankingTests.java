package ranking.tests;

import ranking.RankingModel;
import ranking.pagerank.PageRankComputation;
import ranking.RelevanceFeedback;
import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.*;

public class RankingTests {

    private RankingModel rankingModel;
    private PageRankComputation pageRank;
    private RelevanceFeedback relevanceFeedback;

    @Before
    public void setUp() {
        rankingModel = new RankingModel();
        pageRank = new PageRankComputation();
        relevanceFeedback = new RelevanceFeedback();
    }

    @Test
    public void testRankingModel_BM25() {
        double score = rankingModel.computeBM25(2, 100, 5, 50, 0.75, 1.2);
        assertEquals(0.566, score, 0.001);
    }

    @Test
    public void testRankingModel_VectorSpace() {
        double[] docVector = {1.0, 2.0, 3.0};
        double[] queryVector = {0.5, 1.5, 2.0};
        double score = rankingModel.computeVectorSpace(docVector, queryVector);
        assertEquals(0.979, score, 0.001);
    }

    @Test
    public void testPageRankComputation() {
        double[] pageScores = pageRank.computePageRank(new double[][]{
            {0.0, 0.5, 0.5},
            {1.0, 0.0, 0.0},
            {0.0, 1.0, 0.0}
        }, 3);
        assertEquals(0.333, pageScores[0], 0.001);
        assertEquals(0.5, pageScores[1], 0.001);
        assertEquals(0.167, pageScores[2], 0.001);
    }

    @Test
    public void testPageRank_DampingFactor() {
        pageRank.setDampingFactor(0.85);
        double dampingFactor = pageRank.getDampingFactor();
        assertEquals(0.85, dampingFactor, 0.001);
    }

    @Test
    public void testRelevanceFeedback_PositiveFeedback() {
        double[] initialRanking = {0.1, 0.2, 0.3};
        double[] feedbackRanking = relevanceFeedback.applyPositiveFeedback(initialRanking, new int[]{1});
        assertEquals(0.1, feedbackRanking[0], 0.001);
        assertEquals(0.25, feedbackRanking[1], 0.001);
        assertEquals(0.3, feedbackRanking[2], 0.001);
    }

    @Test
    public void testRelevanceFeedback_NegativeFeedback() {
        double[] initialRanking = {0.1, 0.2, 0.3};
        double[] feedbackRanking = relevanceFeedback.applyNegativeFeedback(initialRanking, new int[]{2});
        assertEquals(0.1, feedbackRanking[0], 0.001);
        assertEquals(0.2, feedbackRanking[1], 0.001);
        assertEquals(0.25, feedbackRanking[2], 0.001);
    }

    @Test
    public void testRankingModel_TFIDF() {
        double tfidfScore = rankingModel.computeTFIDF(3, 1000, 5);
        assertEquals(0.405, tfidfScore, 0.001);
    }

    @Test
    public void testRankingModel_TermFrequency() {
        double termFrequency = rankingModel.computeTermFrequency(5, 50);
        assertEquals(0.1, termFrequency, 0.001);
    }

    @Test
    public void testRankingModel_DocumentFrequency() {
        double documentFrequency = rankingModel.computeDocumentFrequency(5, 1000);
        assertEquals(0.005, documentFrequency, 0.001);
    }

    @Test
    public void testPageRank_MaxIterations() {
        pageRank.setMaxIterations(100);
        int iterations = pageRank.getMaxIterations();
        assertEquals(100, iterations);
    }

    @Test
    public void testRankingModel_CompressedIndex() {
        double[] docVector = {0.9, 0.8, 0.7};
        double[] compressedVector = rankingModel.compressVector(docVector);
        assertEquals(0.85, compressedVector[0], 0.001);
        assertEquals(0.75, compressedVector[1], 0.001);
        assertEquals(0.65, compressedVector[2], 0.001);
    }

    @Test
    public void testRankingModel_ApplyWeights() {
        double[] scores = {0.3, 0.4, 0.5};
        double[] weights = {0.6, 0.7, 0.8};
        double[] weightedScores = rankingModel.applyWeights(scores, weights);
        assertEquals(0.18, weightedScores[0], 0.001);
        assertEquals(0.28, weightedScores[1], 0.001);
        assertEquals(0.4, weightedScores[2], 0.001);
    }

    @Test
    public void testRelevanceFeedback_Smoothing() {
        relevanceFeedback.setSmoothingFactor(0.9);
        double smoothingFactor = relevanceFeedback.getSmoothingFactor();
        assertEquals(0.9, smoothingFactor, 0.001);
    }

    @Test
    public void testRankingModel_Personalization() {
        rankingModel.setUserPreference(0.7);
        double userPreference = rankingModel.getUserPreference();
        assertEquals(0.7, userPreference, 0.001);
    }

    @Test
    public void testRankingModel_NormalizeScores() {
        double[] scores = {0.5, 0.7, 0.9};
        double[] normalizedScores = rankingModel.normalizeScores(scores);
        assertEquals(0.555, normalizedScores[0], 0.001);
        assertEquals(0.777, normalizedScores[1], 0.001);
        assertEquals(1.0, normalizedScores[2], 0.001);
    }

    @Test
    public void testRankingModel_MultiQueryRank() {
        double[] query1Scores = {0.5, 0.7, 0.6};
        double[] query2Scores = {0.3, 0.5, 0.8};
        double[] combinedScores = rankingModel.multiQueryRank(query1Scores, query2Scores);
        assertEquals(0.4, combinedScores[0], 0.001);
        assertEquals(0.6, combinedScores[1], 0.001);
        assertEquals(0.7, combinedScores[2], 0.001);
    }

    @Test
    public void testPageRank_Convergence() {
        pageRank.setTolerance(0.0001);
        double tolerance = pageRank.getTolerance();
        assertEquals(0.0001, tolerance, 0.00001);
    }

    @Test
    public void testPageRank_ParallelExecution() {
        pageRank.enableParallelExecution(true);
        assertTrue(pageRank.isParallelExecutionEnabled());
    }

    @Test
    public void testRankingModel_MaxScore() {
        double[] scores = {0.5, 0.9, 0.6};
        double maxScore = rankingModel.getMaxScore(scores);
        assertEquals(0.9, maxScore, 0.001);
    }
}