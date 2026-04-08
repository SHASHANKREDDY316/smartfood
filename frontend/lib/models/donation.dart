class Donation {
  final String id;
  final String hotelName;
  final String foodType;
  final int servings;
  final double distanceKm;
  final bool isFresh;

  Donation({required this.id, required this.hotelName, required this.foodType, required this.servings, required this.distanceKm, required this.isFresh});

  factory Donation.fromJson(Map<String, dynamic> json) {
    return Donation(
      id: json['id'],
      hotelName: json['hotel_name'],
      foodType: json['food_type'],
      servings: json['servings'],
      distanceKm: json['distance_km'].toDouble(),
      isFresh: json['status'] == 'FRESH',
    );
  }
}