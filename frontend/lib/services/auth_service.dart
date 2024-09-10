import 'package:frontend/models/user_model.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart'; // For local storage of JWT
import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  final _storage = const FlutterSecureStorage(); // For storing the JWT securely

  // Store JWT token in secure storage
  Future<void> saveToken(String token) async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();

    await _storage.write(key: 'jwt_token', value: token);

    final DateTime now = DateTime.now();
    await prefs.setString('token_timestamp', now.toIso8601String());
  }

  // Get JWT token from secure storage
  Future<String?> getToken() async {
    return await _storage.read(key: 'jwt_token');
  }

  // Perform login and save the JWT
  Future<UserModel> login(String userName, String password) async {
    final response = await http.post(
      Uri.parse('http://localhost:8000/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'username': userName, 'password': password}),
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> data = jsonDecode(response.body);
      final String token = data['access_token'];
      await saveToken(token); // Save the token locally
      final String role = decodeJwt(token)['role'];
      return UserModel(username: userName, role: role);
    } else {
      throw Exception('Failed to login');
    }
  }

  // Check if the stored token is still valid (within 10-minute window)
  Future<bool> isTokenValid() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    final String? token = await getToken();
    final String? timestampString = prefs.getString('token_timestamp');

    if (token != null && timestampString != null) {
      final DateTime tokenTimestamp = DateTime.parse(timestampString);
      final DateTime now = DateTime.now();
      final Duration difference = now.difference(tokenTimestamp);

      // Check if the token is still valid (within 10 minutes)
      if (difference.inMinutes < 10) {
        return true; // Token is valid
      } else {
        await logout(); // Token expired, clear token and timestamp
      }
    }
    return false; // No valid token
  }

  // Perform logout by clearing the JWT
  Future<void> logout() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();

    await _storage.delete(key: 'jwt_token'); // Clear the stored JWT token

    await prefs.remove('token_timestamp'); // Clear the token timestamp
  }

  // Decode JWT token
  Map<String, dynamic> decodeJwt(String token) {
    final parts = token.split('.');
    if (parts.length != 3) {
      throw Exception('Invalid token');
    }
    final payload = parts[1];
    final normalized = base64Url.normalize(payload);
    final decoded = utf8.decode(base64Url.decode(normalized));
    return json.decode(decoded);
  }

  // Auto-login: Check if a valid token exists and return the user model
  Future<UserModel?> autoLogin() async {
    final bool isValid = await isTokenValid();
    if (isValid) {
      final String? token = await getToken();
      if (token != null) {
        final String username = decodeJwt(token)['sub'];
        final String role = decodeJwt(token)['role'];
        return UserModel(username: username, role: role);
      }
    }
    return null; // No valid token found
  }
}
