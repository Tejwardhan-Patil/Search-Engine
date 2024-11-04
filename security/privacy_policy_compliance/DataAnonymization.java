package security.privacy_policy_compliance;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Base64;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import java.util.regex.Pattern;
import java.util.regex.Matcher;

public class DataAnonymization {

    // Encrypt sensitive data using AES encryption
    public static String encrypt(String data, String secretKey) throws Exception {
        byte[] keyBytes = secretKey.getBytes();
        SecretKeySpec keySpec = new SecretKeySpec(keyBytes, "AES");

        Cipher cipher = Cipher.getInstance("AES");
        cipher.init(Cipher.ENCRYPT_MODE, keySpec);

        byte[] encryptedBytes = cipher.doFinal(data.getBytes());
        return Base64.getEncoder().encodeToString(encryptedBytes);
    }

    // Decrypt data using AES decryption
    public static String decrypt(String encryptedData, String secretKey) throws Exception {
        byte[] keyBytes = secretKey.getBytes();
        SecretKeySpec keySpec = new SecretKeySpec(keyBytes, "AES");

        Cipher cipher = Cipher.getInstance("AES");
        cipher.init(Cipher.DECRYPT_MODE, keySpec);

        byte[] decryptedBytes = cipher.doFinal(Base64.getDecoder().decode(encryptedData));
        return new String(decryptedBytes);
    }

    // Generate secure random keys for encryption
    public static String generateSecretKey() throws NoSuchAlgorithmException {
        KeyGenerator keyGen = KeyGenerator.getInstance("AES");
        keyGen.init(128); // AES 128-bit key size
        SecretKey secretKey = keyGen.generateKey();
        return Base64.getEncoder().encodeToString(secretKey.getEncoded());
    }

    // Hash sensitive data using SHA-256 hashing
    public static String hashData(String data) throws NoSuchAlgorithmException {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] hashBytes = digest.digest(data.getBytes());
        return Base64.getEncoder().encodeToString(hashBytes);
    }

    // Tokenize data by replacing it with unique tokens
    public static String tokenize(String data) {
        String token = Base64.getEncoder().encodeToString(data.getBytes());
        return token;
    }

    // Anonymize email addresses by removing identifiable parts
    public static String anonymizeEmail(String email) {
        String[] parts = email.split("@");
        String localPart = parts[0];
        String domain = parts[1];

        // Keep the first and last character of the local part, replace others with asterisks
        String anonymizedLocalPart = localPart.charAt(0) + "****" + localPart.charAt(localPart.length() - 1);
        return anonymizedLocalPart + "@" + domain;
    }

    // Anonymize phone numbers by masking all but the last four digits
    public static String anonymizePhoneNumber(String phoneNumber) {
        return phoneNumber.replaceAll("\\d(?=\\d{4})", "*");
    }

    // Data masking for other personal information
    public static String maskData(String data) {
        return data.replaceAll(".", "*");
    }

    // Validate email format to ensure compliance with data collection policies
    public static boolean isValidEmail(String email) {
        String emailRegex = "^[A-Za-z0-9+_.-]+@(.+)$";
        Pattern pattern = Pattern.compile(emailRegex);
        Matcher matcher = pattern.matcher(email);
        return matcher.matches();
    }

    // Validate phone number format
    public static boolean isValidPhoneNumber(String phoneNumber) {
        String phoneRegex = "\\d{10}";
        Pattern pattern = Pattern.compile(phoneRegex);
        Matcher matcher = pattern.matcher(phoneNumber);
        return matcher.matches();
    }

    // Secure random ID generation for anonymized data records
    public static String generateSecureId() {
        SecureRandom random = new SecureRandom();
        byte[] bytes = new byte[16];
        random.nextBytes(bytes);
        return Base64.getUrlEncoder().encodeToString(bytes);
    }

    // Data anonymization workflow
    public static void anonymizeUserData(String email, String phoneNumber, String name) throws Exception {
        // Ensure compliance by validating data format
        if (!isValidEmail(email) || !isValidPhoneNumber(phoneNumber)) {
            throw new IllegalArgumentException("Invalid email or phone number format.");
        }

        // Anonymize data
        String anonymizedEmail = anonymizeEmail(email);
        String anonymizedPhone = anonymizePhoneNumber(phoneNumber);
        String anonymizedName = maskData(name);

        // Generate encrypted versions of data for secure storage
        String secretKey = generateSecretKey();
        String encryptedEmail = encrypt(anonymizedEmail, secretKey);
        String encryptedPhone = encrypt(anonymizedPhone, secretKey);
        String encryptedName = encrypt(anonymizedName, secretKey);

        System.out.println("Anonymized and Encrypted Email: " + encryptedEmail);
        System.out.println("Anonymized and Encrypted Phone: " + encryptedPhone);
        System.out.println("Anonymized and Encrypted Name: " + encryptedName);
    }

    public static void main(String[] args) {
        try {
            String email = "person1@website.com";
            String phoneNumber = "1234567890";
            String name = "Person1";

            anonymizeUserData(email, phoneNumber, name);

            // Tokenizing sensitive data
            String tokenizedEmail = tokenize(email);
            System.out.println("Tokenized Email: " + tokenizedEmail);

            // Hashing sensitive data
            String hashedEmail = hashData(email);
            System.out.println("Hashed Email: " + hashedEmail);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}