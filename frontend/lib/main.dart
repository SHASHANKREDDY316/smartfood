import 'package:flutter/material.dart';
import 'screens/hotel_dashboard.dart';
import 'screens/ngo_feed.dart';

void main() => runApp(const SmartFoodApp());

class SmartFoodApp extends StatelessWidget {
  const SmartFoodApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0F172A),
      ),
      home: const RoleSelectionScreen(),
    );
  }
}

// =========================
// 🎭 ROLE SELECTION
// =========================
class RoleSelectionScreen extends StatelessWidget {
  const RoleSelectionScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Smart Food 🍱"),
        centerTitle: true,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text(
                "Choose Role",
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 30),

              // 🍽️ HOTEL
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 60),
                ),
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => HotelDashboard()),
                  );
                },
                child: const Text('Login as Hotel 🍽️'),
              ),

              const SizedBox(height: 16),

              // 🥗 NGO
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 60),
                ),
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => NgoFeed()),
                  );
                },
                child: const Text('Login as NGO 🥗'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}