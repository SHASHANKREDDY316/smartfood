import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // 🔥 FIXED BASE URL
  static const String baseUrl = 'http://10.0.2.2:5000/api/v1';

  // =========================
  // 🍱 POST DONATION
  // =========================
  static Future<bool> postLeftoverFood(
      String hotelName, String foodType, int servings) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/donations'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'hotel_name': hotelName,
          'food_type': foodType,
          'servings': servings
        }),
      );

      return res.statusCode == 201;
    } catch (e) {
      print("Error: $e");
      return false;
    }
  }

  // =========================
  // 📥 GET DONATIONS
  // =========================
  static Future<List<dynamic>> getNearbyDonations() async {
    try {
      final res =
          await http.get(Uri.parse('$baseUrl/donations/nearby'));

      if (res.statusCode == 200) {
        return jsonDecode(res.body);
      }
      return [];
    } catch (e) {
      print("Error: $e");
      return [];
    }
  }

  // =========================
  // 🚚 CLAIM DONATION
  // =========================
  static Future<String?> claimDonation(String donationId) async {
    try {
      final res = await http.patch(
        Uri.parse('$baseUrl/donations/$donationId/claim'),
      );

      if (res.statusCode == 200) {
        return jsonDecode(res.body)['pickup_otp'];
      }
      return null;
    } catch (e) {
      print("Error: $e");
      return null;
    }
  }
}