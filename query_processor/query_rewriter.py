import nltk
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import wordnet
from spellchecker import SpellChecker
import re

# Initialize stemmer, lemmatizer, and spell checker
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()
spell = SpellChecker()

# Download NLTK resources
nltk.download('wordnet')
nltk.download('punkt')

class QueryRewriter:
    def __init__(self):
        # Initialize a list of stopwords
        self.stopwords = set(nltk.corpus.stopwords.words('english'))
        # Custom stopwords
        self.custom_stopwords = {'example', 'additional'}
        self.stopwords.update(self.custom_stopwords)
    
    def tokenize_query(self, query):
        """
        Tokenize the input query into individual words and handle basic cleaning.
        """
        # Lowercase the query and remove any non-alphabetical characters
        query = query.lower()
        query = re.sub(r'[^a-zA-Z\s]', '', query)
        
        # Tokenize the query using nltk word_tokenizer
        tokens = nltk.word_tokenize(query)
        
        return tokens

    def remove_stopwords(self, tokens):
        """
        Remove stopwords from a list of tokens.
        """
        filtered_tokens = [token for token in tokens if token not in self.stopwords]
        return filtered_tokens

    def spell_correction(self, tokens):
        """
        Perform spell correction on each token using a spell checker.
        """
        corrected_tokens = [spell.correction(token) for token in tokens]
        return corrected_tokens

    def stem_tokens(self, tokens):
        """
        Apply stemming to the list of tokens using the PorterStemmer.
        """
        stemmed_tokens = [stemmer.stem(token) for token in tokens]
        return stemmed_tokens

    def lemmatize_tokens(self, tokens):
        """
        Apply lemmatization to the list of tokens using WordNetLemmatizer.
        """
        lemmatized_tokens = [lemmatizer.lemmatize(token, self.get_wordnet_pos(token)) for token in tokens]
        return lemmatized_tokens

    def get_wordnet_pos(self, word):
        """
        Map POS tag to first character lemmatize() accepts.
        """
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {
            'J': wordnet.ADJ,
            'N': wordnet.NOUN,
            'V': wordnet.VERB,
            'R': wordnet.ADV
        }
        return tag_dict.get(tag, wordnet.NOUN)

    def synonym_expansion(self, tokens):
        """
        Perform synonym expansion for each token using WordNet.
        """
        expanded_tokens = []
        for token in tokens:
            synonyms = wordnet.synsets(token)
            synonym_list = [lemma.name() for syn in synonyms for lemma in syn.lemmas()]
            expanded_tokens.extend(synonym_list if synonym_list else [token])
        return expanded_tokens

    def query_rewrite(self, query):
        """
        Main method to rewrite the query by processing it step by step.
        """
        # Tokenize the query
        tokens = self.tokenize_query(query)
        
        # Remove stopwords
        tokens = self.remove_stopwords(tokens)
        
        # Correct spelling mistakes
        tokens = self.spell_correction(tokens)
        
        # Apply stemming
        stemmed_tokens = self.stem_tokens(tokens)
        
        # Apply lemmatization
        lemmatized_tokens = self.lemmatize_tokens(stemmed_tokens)
        
        # Perform synonym expansion
        expanded_tokens = self.synonym_expansion(lemmatized_tokens)
        
        # Return final processed query
        return ' '.join(expanded_tokens)

    def optimize_query(self, query):
        """
        Optimizes the query for efficient search processing and retrieval.
        """
        rewritten_query = self.query_rewrite(query)
        optimized_query = rewritten_query.strip()
        
        return optimized_query

# Usage
if __name__ == '__main__':
    query_rewriter = QueryRewriter()
    
    input_query = "Optimizing the search results for typos and synonms"
    
    optimized_query = query_rewriter.optimize_query(input_query)
    
    print(f"Original Query: {input_query}")
    print(f"Optimized Query: {optimized_query}")