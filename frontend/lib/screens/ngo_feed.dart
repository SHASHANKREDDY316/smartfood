import 'package:flutter/material.dart';
import '../services/api_service.dart';

class NgoFeed extends StatefulWidget {
  @override
  _NgoFeedState createState() => _NgoFeedState();
}

class _NgoFeedState extends State<NgoFeed> {
  List donations = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    loadDonations();
  }

  void loadDonations() async {
    final data = await ApiService.getNearbyDonations();
    setState(() {
      donations = data;
      isLoading = false;
    });
  }

  void claimDonation(String id) async {
    final otp = await ApiService.claimDonation(id);

    if (otp != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Accepted! OTP: $otp ✅")),
      );
      loadDonations(); // refresh list
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Failed to accept ❌")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("NGO Feed 🥗"),
        centerTitle: true,
      ),
      body: isLoading
          ? Center(child: CircularProgressIndicator())
          : donations.isEmpty
              ? Center(child: Text("No donations available"))
              : RefreshIndicator(
                  onRefresh: () async => loadDonations(),
                  child: ListView.builder(
                    itemCount: donations.length,
                    itemBuilder: (context, index) {
                      final d = donations[index];

                      return Card(
                        margin: EdgeInsets.all(10),
                        child: ListTile(
                          title: Text(d['food_type'] ?? "Unknown"),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text("Servings: ${d['servings']}"),
                              Text("Status: ${d['status']}"),
                              Text("Distance: ${d['distance_km']} km"),
                            ],
                          ),
                          trailing: ElevatedButton(
                            onPressed: () => claimDonation(d['id']),
                            child: Text("Accept"),
                          ),
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}