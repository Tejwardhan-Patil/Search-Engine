import re
import nltk
from nltk.corpus import wordnet
from spellchecker import SpellChecker
from collections import defaultdict

# Load NLTK resources
nltk.download('wordnet')
nltk.download('punkt')

class QueryExpansion:
    def __init__(self):
        self.spellchecker = SpellChecker()
        self.synonyms_cache = defaultdict(list)
    
    def normalize_query(self, query):
        """
        Normalize the query by lowercasing, removing special characters, and tokenizing.
        """
        query = query.lower()
        query = re.sub(r'[^a-z0-9\s]', '', query)
        tokens = nltk.word_tokenize(query)
        return tokens

    def correct_spelling(self, tokens):
        """
        Correct spelling mistakes in query tokens using SpellChecker.
        """
        corrected_tokens = [self.spellchecker.correction(token) for token in tokens]
        return corrected_tokens

    def expand_synonyms(self, tokens):
        """
        Expand the query tokens by finding synonyms using WordNet.
        """
        expanded_tokens = []
        for token in tokens:
            expanded_tokens.append(token)
            if token in self.synonyms_cache:
                expanded_tokens.extend(self.synonyms_cache[token])
            else:
                synonyms = set()
                for syn in wordnet.synsets(token):
                    for lemma in syn.lemmas():
                        synonyms.add(lemma.name().replace('_', ' '))
                self.synonyms_cache[token] = list(synonyms)
                expanded_tokens.extend(synonyms)
        return list(set(expanded_tokens))  # Remove duplicates

    def expand_query(self, query):
        """
        Expand the input query by normalizing, correcting spelling, and adding synonyms.
        """
        tokens = self.normalize_query(query)
        tokens = self.correct_spelling(tokens)
        expanded_tokens = self.expand_synonyms(tokens)
        return ' '.join(expanded_tokens)

class QueryProcessor:
    def __init__(self):
        self.query_expander = QueryExpansion()

    def process_query(self, query):
        """
        Process the query by expanding it.
        """
        expanded_query = self.query_expander.expand_query(query)
        return expanded_query

# Utility Functions for Query Expansion

def query_contains_synonyms(query, synonym_list):
    """
    Check if the query contains any word from a synonym list.
    """
    query_tokens = query.lower().split()
    for synonym in synonym_list:
        if synonym in query_tokens:
            return True
    return False

def expand_with_concepts(query, concept_dict):
    """
    Expand a query by appending related concepts.
    """
    expanded_query = query
    for word in query.split():
        if word in concept_dict:
            expanded_query += ' ' + ' '.join(concept_dict[word])
    return expanded_query

def boost_query_terms(query, boost_factor=2):
    """
    Boost important query terms by repeating them a number of times.
    """
    terms = query.split()
    boosted_terms = []
    for term in terms:
        boosted_terms.extend([term] * boost_factor)
    return ' '.join(boosted_terms)

# Query expansion with custom synonym dictionary
custom_synonyms = {
    'python': ['programming language', 'code'],
    'search': ['find', 'lookup'],
}

def custom_synonym_expansion(query, custom_synonyms):
    """
    Expand the query using custom synonyms defined by the user.
    """
    expanded_query = query
    for word, synonyms in custom_synonyms.items():
        if word in query.split():
            expanded_query += ' ' + ' '.join(synonyms)
    return expanded_query

# Advanced Query Expansion with Multiple Strategies
class AdvancedQueryExpansion:
    def __init__(self):
        self.query_expander = QueryExpansion()

    def process_query(self, query):
        """
        Expand and process the query using multiple strategies.
        """
        expanded_query = self.query_expander.expand_query(query)
        
        # Custom expansions
        expanded_query = custom_synonym_expansion(expanded_query, custom_synonyms)
        
        # Boost terms
        expanded_query = boost_query_terms(expanded_query)

        return expanded_query

# Test Cases for Query Expansion
def run_tests():
    # Initialize query processor
    query_processor = AdvancedQueryExpansion()
    
    test_queries = [
        "What is Python programming?",
        "How to search for data?",
        "Best methods for fuzzy search"
    ]
    
    for query in test_queries:
        expanded_query = query_processor.process_query(query)
        print(f"Original Query: {query}")
        print(f"Expanded Query: {expanded_query}")
        print('-' * 50)

# Running test cases
if __name__ == "__main__":
    run_tests()