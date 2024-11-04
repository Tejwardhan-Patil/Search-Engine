package ranking;

import java.util.HashMap;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.PriorityQueue;

public class personalization {

    // UserProfile class to store user's preferences, history, and other personalization metrics
    public static class UserProfile {
        private String userId;
        private Map<String, Double> preferredTopics; // Topic -> Preference Score
        private List<String> searchHistory; // List of past search queries
        private List<String> clickedResults; // List of clicked URLs

        public UserProfile(String userId) {
            this.userId = userId;
            this.preferredTopics = new HashMap<>();
            this.searchHistory = new ArrayList<>();
            this.clickedResults = new ArrayList<>();
        }

        // Get userId
        public String getUserId() {
            return userId;
        }

        // Add or update topic preference
        public void updatePreferredTopic(String topic, double score) {
            preferredTopics.put(topic, preferredTopics.getOrDefault(topic, 0.0) + score);
        }

        // Get the preference score for a specific topic
        public double getTopicPreference(String topic) {
            return preferredTopics.getOrDefault(topic, 0.0);
        }

        // Add a query to search history
        public void addSearchQuery(String query) {
            searchHistory.add(query);
        }

        // Add a clicked result URL
        public void addClickedResult(String url) {
            clickedResults.add(url);
        }

        // Getters
        public List<String> getSearchHistory() {
            return searchHistory;
        }

        public List<String> getClickedResults() {
            return clickedResults;
        }
    }

    // SearchResult class to hold search result data
    public static class SearchResult implements Comparable<SearchResult> {
        private String url;
        private String title;
        private double baseRankScore;
        private double personalizedScore;

        public SearchResult(String url, String title, double baseRankScore) {
            this.url = url;
            this.title = title;
            this.baseRankScore = baseRankScore;
            this.personalizedScore = 0.0;
        }

        // Set personalized score
        public void setPersonalizedScore(double score) {
            this.personalizedScore = score;
        }

        // Get final score (combination of base rank score and personalized score)
        public double getFinalScore() {
            return baseRankScore + personalizedScore;
        }

        // Comparison for ranking
        @Override
        public int compareTo(SearchResult other) {
            return Double.compare(other.getFinalScore(), this.getFinalScore());
        }

        // Getters
        public String getUrl() {
            return url;
        }

        public String getTitle() {
            return title;
        }
    }

    // Class responsible for personalizing the search results based on the user's profile
    public class PersonalizationEngine {

        // Method to apply personalization to search results
        public List<SearchResult> applyPersonalization(UserProfile userProfile, List<SearchResult> searchResults) {
            logUserProfile(userProfile);  // Log the user profile information (incorporating userId)

            for (SearchResult result : searchResults) {
                double personalizedScore = calculatePersonalizedScore(userProfile, result);
                result.setPersonalizedScore(personalizedScore);
            }

            // Sort results based on the final score (baseRank + personalized)
            PriorityQueue<SearchResult> resultQueue = new PriorityQueue<>(searchResults);

            List<SearchResult> sortedResults = new ArrayList<>();
            while (!resultQueue.isEmpty()) {
                sortedResults.add(resultQueue.poll());
            }
            return sortedResults;
        }

        // Calculate the personalized score for a search result
        private double calculatePersonalizedScore(UserProfile userProfile, SearchResult result) {
            double score = 0.0;

            // Check for topic matches in the user's preferences and the result
            for (Map.Entry<String, Double> topicEntry : userProfile.preferredTopics.entrySet()) {
                if (result.getTitle().toLowerCase().contains(topicEntry.getKey().toLowerCase())) {
                    score += topicEntry.getValue();
                }
            }

            // Additional personalization logic based on user's history and clicks
            if (userProfile.getClickedResults().contains(result.getUrl())) {
                score += 5.0; // Boost for previously clicked results
            }

            return score;
        }

        // Log the user profile details, including userId, for debugging or tracking
        private void logUserProfile(UserProfile userProfile) {
            System.out.println("Applying personalization for User: " + userProfile.getUserId());
            System.out.println("User's Preferred Topics: " + userProfile.preferredTopics);
            System.out.println("User's Search History: " + userProfile.getSearchHistory());
            System.out.println("User's Clicked Results: " + userProfile.getClickedResults());
        }
    }

    // Usage
    public static void main(String[] args) {
        // Create a user profile
        UserProfile userProfile = new UserProfile("user123");

        // Update user preferences
        userProfile.updatePreferredTopic("technology", 3.0);
        userProfile.updatePreferredTopic("sports", 2.0);
        userProfile.addSearchQuery("latest smartphones");
        userProfile.addClickedResult("website.com/tech-news");

        // Create search results
        List<SearchResult> searchResults = new ArrayList<>();
        searchResults.add(new SearchResult("website.com/tech-news", "Latest Technology News", 7.0));
        searchResults.add(new SearchResult("website.com/sports-updates", "Sports News Today", 6.5));
        searchResults.add(new SearchResult("website.com/finance-tips", "Finance and Investment", 6.0));

        // Apply personalization
        PersonalizationEngine engine = new personalization().new PersonalizationEngine();
        List<SearchResult> personalizedResults = engine.applyPersonalization(userProfile, searchResults);

        // Print results
        for (SearchResult result : personalizedResults) {
            System.out.println(result.getTitle() + " - Final Score: " + result.getFinalScore());
        }
    }
}