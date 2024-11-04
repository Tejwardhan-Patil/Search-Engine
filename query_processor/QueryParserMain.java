package query_processor;

import java.util.*;

// Token class to represent different types of tokens in the query
class Token {
    public enum TokenType {
        AND, OR, NOT, LEFT_PAREN, RIGHT_PAREN, TERM
    }

    private TokenType type;
    private String value;

    public Token(TokenType type, String value) {
        this.type = type;
        this.value = value;
    }

    public TokenType getType() {
        return type;
    }

    public String getValue() {
        return value;
    }
}

// Tokenizer class to split query string into tokens
class QueryTokenizer {
    private String query;
    private int index;

    public QueryTokenizer(String query) {
        this.query = query;
        this.index = 0;
    }

    public List<Token> tokenize() {
        List<Token> tokens = new ArrayList<>();
        StringBuilder termBuffer = new StringBuilder();

        while (index < query.length()) {
            char currentChar = query.charAt(index);

            switch (currentChar) {
                case ' ':
                    if (termBuffer.length() > 0) {
                        tokens.add(new Token(Token.TokenType.TERM, termBuffer.toString()));
                        termBuffer.setLength(0);
                    }
                    index++;
                    break;
                case '(':
                    if (termBuffer.length() > 0) {
                        tokens.add(new Token(Token.TokenType.TERM, termBuffer.toString()));
                        termBuffer.setLength(0);
                    }
                    tokens.add(new Token(Token.TokenType.LEFT_PAREN, "("));
                    index++;
                    break;
                case ')':
                    if (termBuffer.length() > 0) {
                        tokens.add(new Token(Token.TokenType.TERM, termBuffer.toString()));
                        termBuffer.setLength(0);
                    }
                    tokens.add(new Token(Token.TokenType.RIGHT_PAREN, ")"));
                    index++;
                    break;
                case 'A':
                case 'O':
                case 'N':
                    if (termBuffer.length() > 0) {
                        tokens.add(new Token(Token.TokenType.TERM, termBuffer.toString()));
                        termBuffer.setLength(0);
                    }
                    String word = getWord();
                    if (word.equalsIgnoreCase("AND")) {
                        tokens.add(new Token(Token.TokenType.AND, "AND"));
                    } else if (word.equalsIgnoreCase("OR")) {
                        tokens.add(new Token(Token.TokenType.OR, "OR"));
                    } else if (word.equalsIgnoreCase("NOT")) {
                        tokens.add(new Token(Token.TokenType.NOT, "NOT"));
                    } else {
                        tokens.add(new Token(Token.TokenType.TERM, word));
                    }
                    break;
                default:
                    termBuffer.append(currentChar);
                    index++;
                    break;
            }
        }

        if (termBuffer.length() > 0) {
            tokens.add(new Token(Token.TokenType.TERM, termBuffer.toString()));
        }

        return tokens;
    }

    private String getWord() {
        StringBuilder sb = new StringBuilder();
        while (index < query.length() && Character.isLetter(query.charAt(index))) {
            sb.append(query.charAt(index));
            index++;
        }
        return sb.toString();
    }
}

// Node class for constructing a query tree
class QueryNode {
    public enum NodeType {
        AND, OR, NOT, TERM
    }

    private NodeType type;
    private String value;
    private QueryNode left;
    private QueryNode right;

    public QueryNode(NodeType type, String value) {
        this.type = type;
        this.value = value;
    }

    public QueryNode(NodeType type, QueryNode left, QueryNode right) {
        this.type = type;
        this.left = left;
        this.right = right;
    }

    public NodeType getType() {
        return type;
    }

    public String getValue() {
        return value;
    }

    public QueryNode getLeft() {
        return left;
    }

    public QueryNode getRight() {
        return right;
    }
}

// Parser class to construct a query tree from tokens
class QueryParser {
    private List<Token> tokens;
    private int currentIndex;

    public QueryParser(List<Token> tokens) {
        this.tokens = tokens;
        this.currentIndex = 0;
    }

    public QueryNode parse() throws Exception {
        return parseOrExpression();
    }

    private QueryNode parseOrExpression() throws Exception {
        QueryNode left = parseAndExpression();

        while (currentIndex < tokens.size() && tokens.get(currentIndex).getType() == Token.TokenType.OR) {
            currentIndex++; // consume OR token
            QueryNode right = parseAndExpression();
            left = new QueryNode(QueryNode.NodeType.OR, left, right);
        }

        return left;
    }

    private QueryNode parseAndExpression() throws Exception {
        QueryNode left = parseNotExpression();

        while (currentIndex < tokens.size() && tokens.get(currentIndex).getType() == Token.TokenType.AND) {
            currentIndex++; // consume AND token
            QueryNode right = parseNotExpression();
            left = new QueryNode(QueryNode.NodeType.AND, left, right);
        }

        return left;
    }

    private QueryNode parseNotExpression() throws Exception {
        if (currentIndex < tokens.size() && tokens.get(currentIndex).getType() == Token.TokenType.NOT) {
            currentIndex++; // consume NOT token
            QueryNode operand = parsePrimary();
            return new QueryNode(QueryNode.NodeType.NOT, operand, null);
        }

        return parsePrimary();
    }

    private QueryNode parsePrimary() throws Exception {
        if (currentIndex >= tokens.size()) {
            throw new Exception("Unexpected end of query");
        }

        Token token = tokens.get(currentIndex);

        if (token.getType() == Token.TokenType.TERM) {
            currentIndex++; // consume TERM token
            return new QueryNode(QueryNode.NodeType.TERM, token.getValue());
        } else if (token.getType() == Token.TokenType.LEFT_PAREN) {
            currentIndex++; // consume LEFT_PAREN
            QueryNode expression = parseOrExpression();

            if (currentIndex >= tokens.size() || tokens.get(currentIndex).getType() != Token.TokenType.RIGHT_PAREN) {
                throw new Exception("Missing closing parenthesis");
            }

            currentIndex++; // consume RIGHT_PAREN
            return expression;
        }

        throw new Exception("Invalid query token: " + token.getValue());
    }
}

// Evaluator class to process the query tree and return a readable form
class QueryEvaluator {

    public String evaluate(QueryNode node) {
        if (node == null) {
            return "";
        }

        switch (node.getType()) {
            case AND:
                return "(" + evaluate(node.getLeft()) + " AND " + evaluate(node.getRight()) + ")";
            case OR:
                return "(" + evaluate(node.getLeft()) + " OR " + evaluate(node.getRight()) + ")";
            case NOT:
                return "(NOT " + evaluate(node.getLeft()) + ")";
            case TERM:
                return node.getValue();
            default:
                throw new IllegalArgumentException("Unknown node type");
        }
    }
}

// Main class for parsing and evaluation functionality
public class QueryParserMain {
    public static void main(String[] args) {
        try {
            // Query input
            String query = "(apple AND orange) OR NOT banana";

            // Tokenize the input query
            QueryTokenizer tokenizer = new QueryTokenizer(query);
            List<Token> tokens = tokenizer.tokenize();

            // Parse the tokens into a query tree
            QueryParser parser = new QueryParser(tokens);
            QueryNode queryTree = parser.parse();

            // Evaluate the query tree
            QueryEvaluator evaluator = new QueryEvaluator();
            String evaluatedQuery = evaluator.evaluate(queryTree);

            // Output the evaluated query
            System.out.println("Parsed and evaluated query: " + evaluatedQuery);
        } catch (Exception e) {
            System.err.println("Error parsing query: " + e.getMessage());
        }
    }
}