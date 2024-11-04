package security.authentication;

import java.util.Base64;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import javax.net.ssl.HttpsURLConnection;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

public class OAuth2Auth {
    
    private static final String TOKEN_ENDPOINT = "https://website.com/oauth/token";
    private static final String AUTHORIZATION_ENDPOINT = "https://website.com/oauth/authorize";
    private static final String CLIENT_ID = "client_id";
    private static final String CLIENT_SECRET = "client_secret";
    private static final String REDIRECT_URI = "https://website.com/callback";
    private static final String GRANT_TYPE = "authorization_code";

    // Method to generate the OAuth2 Authorization URL
    public static String getAuthorizationUrl(String state) {
        return AUTHORIZATION_ENDPOINT + "?response_type=code"
                + "&client_id=" + CLIENT_ID
                + "&redirect_uri=" + REDIRECT_URI
                + "&state=" + state;
    }

    // Method to exchange authorization code for access token
    public static String getAccessToken(String authorizationCode) throws Exception {
        URL url = new URL(TOKEN_ENDPOINT);
        HttpsURLConnection conn = (HttpsURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
        conn.setDoOutput(true);

        String body = "grant_type=" + GRANT_TYPE
                + "&code=" + authorizationCode
                + "&redirect_uri=" + REDIRECT_URI
                + "&client_id=" + CLIENT_ID
                + "&client_secret=" + CLIENT_SECRET;

        OutputStream os = conn.getOutputStream();
        os.write(body.getBytes(StandardCharsets.UTF_8));
        os.flush();
        os.close();

        BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;

        while ((line = br.readLine()) != null) {
            response.append(line);
        }

        br.close();
        return response.toString();
    }

    // Method to validate access token
    public static boolean validateToken(String token, String expectedAudience) {
        try {
            // Decode token payload
            String[] tokenParts = token.split("\\.");
            if (tokenParts.length != 3) {
                throw new IllegalArgumentException("Invalid token format");
            }

            String payload = new String(Base64.getDecoder().decode(tokenParts[1]), StandardCharsets.UTF_8);
            // Extract 'aud' (audience) from payload and validate it
            if (!payload.contains("\"aud\":\"" + expectedAudience + "\"")) {
                return false;
            }

            // Validate the token signature using CLIENT_SECRET
            if (!validateTokenSignature(token, CLIENT_SECRET)) {
                return false;
            }

            return true;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }

    // Helper method to validate token signature
    private static boolean validateTokenSignature(String token, String clientSecret) throws Exception {
        String[] parts = token.split("\\.");
        if (parts.length != 3) {
            return false;
        }

        String headerPayload = parts[0] + "." + parts[1];
        String signature = parts[2];

        Mac hmac = Mac.getInstance("HmacSHA256");
        SecretKeySpec secretKey = new SecretKeySpec(clientSecret.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
        hmac.init(secretKey);

        byte[] signedBytes = hmac.doFinal(headerPayload.getBytes(StandardCharsets.UTF_8));
        String expectedSignature = Base64.getEncoder().encodeToString(signedBytes);

        return expectedSignature.equals(signature);
    }

    // Method to refresh access token using refresh token
    public static String refreshToken(String refreshToken) throws Exception {
        URL url = new URL(TOKEN_ENDPOINT);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
        conn.setDoOutput(true);

        String body = "grant_type=refresh_token"
                + "&refresh_token=" + refreshToken
                + "&client_id=" + CLIENT_ID
                + "&client_secret=" + CLIENT_SECRET;

        OutputStream os = conn.getOutputStream();
        os.write(body.getBytes(StandardCharsets.UTF_8));
        os.flush();
        os.close();

        BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;

        while ((line = br.readLine()) != null) {
            response.append(line);
        }

        br.close();
        return response.toString();
    }

    // Method to generate state value for CSRF protection
    public static String generateState() {
        try {
            byte[] randomBytes = new byte[32];
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            digest.update(randomBytes);
            return Base64.getEncoder().encodeToString(digest.digest());
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    // Method to generate secure hash for PKCE (Proof Key for Code Exchange)
    public static String generateCodeChallenge(String codeVerifier) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] hash = digest.digest(codeVerifier.getBytes(StandardCharsets.UTF_8));
        return Base64.getEncoder().encodeToString(hash);
    }

    // Method to handle PKCE-based authentication
    public static String getAuthorizationUrlWithPKCE(String codeChallenge, String state) {
        return AUTHORIZATION_ENDPOINT + "?response_type=code"
                + "&client_id=" + CLIENT_ID
                + "&redirect_uri=" + REDIRECT_URI
                + "&code_challenge=" + codeChallenge
                + "&code_challenge_method=S256"
                + "&state=" + state;
    }

    // Method to exchange authorization code for access token with PKCE
    public static String getAccessTokenWithPKCE(String authorizationCode, String codeVerifier) throws Exception {
        URL url = new URL(TOKEN_ENDPOINT);
        HttpsURLConnection conn = (HttpsURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
        conn.setDoOutput(true);

        String body = "grant_type=" + GRANT_TYPE
                + "&code=" + authorizationCode
                + "&redirect_uri=" + REDIRECT_URI
                + "&client_id=" + CLIENT_ID
                + "&client_secret=" + CLIENT_SECRET
                + "&code_verifier=" + codeVerifier;

        OutputStream os = conn.getOutputStream();
        os.write(body.getBytes(StandardCharsets.UTF_8));
        os.flush();
        os.close();

        BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;

        while ((line = br.readLine()) != null) {
            response.append(line);
        }

        br.close();
        return response.toString();
    }

    public static void main(String[] args) {
        try {
            // Usage
            String state = generateState();
            System.out.println("Authorization URL: " + getAuthorizationUrl(state));

            String authorizationCode = "received_auth_code";
            String accessToken = getAccessToken(authorizationCode);
            System.out.println("Access Token: " + accessToken);

            boolean isValid = validateToken(accessToken, CLIENT_ID);
            System.out.println("Is token valid: " + isValid);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}