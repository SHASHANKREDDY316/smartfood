from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
import datetime

app = Flask(__name__)
CORS(app)

cred = credentials.Certificate("smartfood_api.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://smartfood-c172e-default-rtdb.firebaseio.com/'
    })

# ---------------- CREATE LISTING ----------------
@app.route('/api/v1/listings', methods=['POST'])
def create_listing():
    try:
        data = request.get_json()

        listing = {
            "restaurant": data.get("restaurant_name", "Unknown"),
            "item": data.get("food_item", "Unknown Item"),
            "location": data.get("location", "Unknown"),
            "lat": data.get("lat", 0),
            "lng": data.get("lng", 0),
            "sale_price": round(float(data.get("original_price", 0)) * 0.15, 2),
            "status": "AVAILABLE",
            "assigned_to": None,
            "proof": None,
            "timestamp": str(datetime.datetime.now())
        }

        ref = db.reference('listings').push(listing)

        return jsonify({"id": ref.key, "success": True}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- GET LISTINGS ----------------
@app.route('/api/v1/listings', methods=['GET'])
def get_listings():
    try:
        data = db.reference('listings').get()
        return jsonify(data if data else {}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- ACCEPT JOB ----------------
@app.route('/api/v1/accept/<id>', methods=['POST'])
def accept_job(id):
    try:
        data = request.get_json()

        db.reference(f'listings/{id}').update({
            "status": "ASSIGNED",
            "assigned_to": data.get("name", "Volunteer")
        })

        return jsonify({"success": True}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- MARK DELIVERED ----------------
@app.route('/api/v1/deliver/<id>', methods=['POST'])
def deliver(id):
    try:
        data = request.get_json()

        db.reference(f'listings/{id}').update({
            "status": "DELIVERED",
            "proof": data.get("proof", "uploaded")
        })

        return jsonify({"success": True}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)