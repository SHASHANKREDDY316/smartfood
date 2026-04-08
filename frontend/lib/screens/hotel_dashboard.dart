import 'package:flutter/material.dart';
import '../services/api_service.dart';

class HotelDashboard extends StatefulWidget {
  @override
  _HotelDashboardState createState() => _HotelDashboardState();
}

class _HotelDashboardState extends State<HotelDashboard> {
  final TextEditingController hotelController = TextEditingController();
  final TextEditingController foodController = TextEditingController();
  final TextEditingController quantityController = TextEditingController();

  bool isLoading = false;

  void submitDonation() async {
    setState(() => isLoading = true);

    final success = await ApiService.postLeftoverFood(
      hotelController.text,
      foodController.text,
      int.tryParse(quantityController.text) ?? 0,
    );

    setState(() => isLoading = false);

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Donation added successfully ✅")),
      );

      hotelController.clear();
      foodController.clear();
      quantityController.clear();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Failed to add donation ❌")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Hotel Dashboard 🍽️"),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: hotelController,
              decoration: InputDecoration(
                labelText: "Hotel Name",
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 15),

            TextField(
              controller: foodController,
              decoration: InputDecoration(
                labelText: "Food Type",
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 15),

            TextField(
              controller: quantityController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: "Quantity (Servings)",
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 20),

            ElevatedButton(
              onPressed: isLoading ? null : submitDonation,
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.symmetric(horizontal: 40, vertical: 15),
              ),
              child: isLoading
                  ? CircularProgressIndicator(color: Colors.white)
                  : Text("Submit Donation"),
            ),
          ],
        ),
      ),
    );
  }
}