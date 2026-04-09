from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os
import json

# 🔥 NEW IMPORTS FOR IMAGE UPLOAD
from google.cloud import storage
import base64
import uuid

app = Flask(__name__)
CORS(app)

# ---------------- HEALTH CHECK ----------------
@app.route('/healthz')
def health():
    return "OK", 200


# ---------------- FIREBASE INIT ----------------
try:
    firebase_key = os.environ.get("FIREBASE_KEY")

    if not firebase_key:
        raise ValueError("FIREBASE_KEY not set")

    cred_dict = json.loads(firebase_key)

    firebase_admin.initialize_app(
        credentials.Certificate(cred_dict),
        {
            'databaseURL': 'https://smartfood-c172e-default-rtdb.firebaseio.com/'
        }
    )

    print("✅ Firebase connected")

except Exception as e:
    print("❌ Firebase error:", e)


# ---------------- IMAGE UPLOAD FUNCTION ----------------
def upload_image_to_firebase(image_base64, folder="images"):
    try:
        bucket_name = "smartfood-c172e.appspot.com"

        client = storage.Client.from_service_account_info(
            json.loads(os.environ.get("FIREBASE_KEY"))
        )

        bucket = client.bucket(bucket_name)

        filename = f"{folder}/{uuid.uuid4().hex}.jpg"
        blob = bucket.blob(filename)

        image_data = base64.b64decode(image_base64)
        blob.upload_from_string(image_data, content_type='image/jpeg')

        blob.make_public()

        return blob.public_url

    except Exception as e:
        print("❌ Image upload error:", e)
        return None


# ---------------- CREATE LISTING ----------------
@app.route('/api/v1/listings', methods=['POST'])
def create_listing():
    try:
        data = request.get_json()

        orig_price = float(data.get("original_price", 0))

        # 📸 FOOD IMAGE
        image_base64 = data.get("image")
        image_url = upload_image_to_firebase(image_base64, "food") if image_base64 else None

        listing = {
            "restaurant": data.get("restaurant_name"),
            "item": data.get("food_item"),
            "original_price": orig_price,
            "sale_price": round(orig_price * 0.15, 2),
            "location": data.get("location", ""),
            "lat": data.get("lat", 0),
            "lng": data.get("lng", 0),
            "image": image_url,
            "status": "AVAILABLE",
            "assigned_to": None,
            "timestamp": str(datetime.datetime.now())
        }

        db.reference('listings').push(listing)

        return jsonify({"success": True}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- GET LISTINGS ----------------
@app.route('/api/v1/listings', methods=['GET'])
def get_listings():
    try:
        data = db.reference('listings').get()
        return jsonify(data or {}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- ACCEPT JOB ----------------
@app.route('/api/v1/accept/<listing_id>', methods=['POST'])
def accept_job(listing_id):
    try:
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

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- MARK DELIVERED ----------------
@app.route('/api/v1/deliver/<listing_id>', methods=['POST'])
def deliver_job(listing_id):
    try:
        ref = db.reference(f'listings/{listing_id}')
        listing = ref.get()

        if not listing:
            return jsonify({"error": "Not found"}), 404

        data = request.get_json()

        # 📸 DELIVERY PROOF IMAGE
        proof_base64 = data.get("proof")
        proof_url = upload_image_to_firebase(proof_base64, "delivery") if proof_base64 else None

        ref.update({
            "status": "DELIVERED",
            "proof": proof_url
        })

        return jsonify({"success": True}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- RUN APP ----------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)