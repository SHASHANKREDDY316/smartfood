from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os
import json

app = Flask(__name__)
CORS(app)

# ---------------- HEALTH CHECK ----------------
@app.route('/healthz')
def health():
    return "OK", 200


# ---------------- FIREBASE INIT ----------------
cred_dict = json.loads(os.environ.get("FIREBASE_KEY"))

firebase_admin.initialize_app(credentials.Certificate(cred_dict), {
    'databaseURL': 'https://smartfood-c172e-default-rtdb.firebaseio.com/'
})


# ---------------- CREATE LISTING ----------------
@app.route('/api/v1/listings', methods=['POST'])
def create_listing():
    data = request.get_json()

    orig_price = float(data.get("original_price", 0))

    listing = {
        "restaurant": data.get("restaurant_name"),
        "item": data.get("food_item"),
        "original_price": orig_price,
        "sale_price": round(orig_price * 0.15, 2),
        "location": data.get("location", ""),
        "lat": data.get("lat", 0),
        "lng": data.get("lng", 0),
        "status": "AVAILABLE",
        "assigned_to": None,
        "timestamp": str(datetime.datetime.now())
    }

    db.reference('listings').push(listing)

    return jsonify({"success": True}), 201


# ---------------- GET LISTINGS ----------------
@app.route('/api/v1/listings', methods=['GET'])
def get_listings():
    data = db.reference('listings').get()
    return jsonify(data or {}), 200


# ---------------- ACCEPT JOB ----------------
@app.route('/api/v1/accept/<listing_id>', methods=['POST'])
def accept_job(listing_id):
    ref = db.reference(f'listings/{listing_id}')
    listing = ref.get()

    if not listing:
        return jsonify({"error": "Not found"}), 404

    if listing.get("status") != "AVAILABLE":
        return jsonify({"error": "Already taken"}), 400

    ref.update({
        "status": "ASSIGNED",
        "assigned_to": "Volunteer"
    })

    return jsonify({"success": True}), 200


# ---------------- MARK DELIVERED ----------------
@app.route('/api/v1/deliver/<listing_id>', methods=['POST'])
def deliver_job(listing_id):
    ref = db.reference(f'listings/{listing_id}')
    listing = ref.get()

    if not listing:
        return jsonify({"error": "Not found"}), 404

    ref.update({
        "status": "DELIVERED"
    })

    return jsonify({"success": True}), 200


# ---------------- RUN APP ----------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)