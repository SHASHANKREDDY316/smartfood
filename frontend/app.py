import streamlit as st
import requests
import base64
import time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="SmartFood", layout="wide")

API = "https://smartfood-backend-ssr.onrender.com/api/v1"

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
}

/* HEADER */
.header {
    text-align: center;
    padding: 20px;
}
.header h1 {
    color: white;
    font-size: 40px;
}
.header p {
    color: #aaa;
}

/* NAV */
.nav {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-bottom: 20px;
}

/* CARD */
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 20px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 20px;
}

/* BUTTON */
.stButton>button {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white;
    border-radius: 10px;
    border: none;
}

/* STATS */
.stat {
    background: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 15px;
    text-align: center;
}
.stat h2 {
    color: #6366f1;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="header">
    <h1>🍽️ Smart Food Waste Redistribution System</h1>
    <p>Connect Hotels with NGOs to reduce food waste and help communities</p>
</div>
""", unsafe_allow_html=True)

# ---------------- MENU ----------------
menu = st.radio(
    "",
    ["🍴 Restaurant", "🏢 NGO Dashboard", "📦 Delivery Tracking"],
    horizontal=True
)

# ---------------- IMAGE ENCODE ----------------
def encode_image(img):
    return base64.b64encode(img.read()).decode()

# ---------------- STATS ----------------
def get_stats(data):
    total = len(data)
    available = sum(1 for v in data.values() if v["status"] == "AVAILABLE")
    assigned = sum(1 for v in data.values() if v["status"] == "ASSIGNED")
    delivered = sum(1 for v in data.values() if v["status"] == "DELIVERED")
    return total, available, assigned, delivered


# ---------------- 🍴 RESTAURANT ----------------
if menu == "🍴 Restaurant":

    st.subheader("Upload Food Listing")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Restaurant Name")
        item = st.text_input("Food Item")
        price = st.number_input("Price", min_value=0.0)
        location = st.text_input("Location")

    with col2:
        image = st.file_uploader("Upload Food Image", type=["jpg", "png"])
        if image:
            st.image(image, use_container_width=True)

    if st.button("🚀 Submit Listing"):
        img_base64 = encode_image(image) if image else None

        payload = {
            "restaurant_name": name,
            "food_item": item,
            "original_price": price,
            "location": location,
            "lat": 0,
            "lng": 0,
            "image": img_base64
        }

        try:
            res = requests.post(f"{API}/listings", json=payload)
            if res.status_code == 201:
                st.success("✅ Food Uploaded Successfully")
            else:
                st.error("Upload failed")
        except:
            st.error("Backend not reachable")


# ---------------- 🏢 NGO DASHBOARD ----------------
elif menu == "🏢 NGO Dashboard":

    st.subheader("Available Food")

    try:
        res = requests.get(f"{API}/listings")
        data = res.json() if res.status_code == 200 else {}

        total, available, assigned, delivered = get_stats(data)

        # Stats Row
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='stat'><h2>{total}</h2>Total</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='stat'><h2>{available}</h2>Available</div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='stat'><h2>{assigned}</h2>Assigned</div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='stat'><h2>{delivered}</h2>Delivered</div>", unsafe_allow_html=True)

        st.markdown("---")

        cols = st.columns(2)

        for i, (key, val) in enumerate(data.items()):
            with cols[i % 2]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)

                st.subheader(val.get("item"))
                st.write("🏪", val.get("restaurant"))
                st.write("📍", val.get("location"))
                st.write("📦 Status:", val.get("status"))

                if val.get("image"):
                    st.image(val["image"], use_container_width=True)

                if val.get("status") == "AVAILABLE":
                    if st.button("Accept", key=f"a{key}"):
                        requests.post(f"{API}/accept/{key}")
                        st.rerun()

                elif val.get("status") == "ASSIGNED":
                    proof = st.file_uploader("Upload Proof", key=f"p{key}")
                    if proof and st.button("Deliver", key=f"d{key}"):
                        proof_base64 = encode_image(proof)
                        requests.post(
                            f"{API}/deliver/{key}",
                            json={"proof": proof_base64}
                        )
                        st.rerun()

                else:
                    st.success("Delivered")

                st.markdown("</div>", unsafe_allow_html=True)

    except:
        st.error("Error loading data")


# ---------------- 📦 DELIVERY TRACKING ----------------
elif menu == "📦 Delivery Tracking":

    st.subheader("Track Deliveries")

    try:
        res = requests.get(f"{API}/listings")
        data = res.json() if res.status_code == 200 else {}

        for val in data.values():
            st.markdown("<div class='card'>", unsafe_allow_html=True)

            st.subheader(val.get("item"))
            st.write("📍", val.get("location"))
            st.write("📦 Status:", val.get("status"))

            progress = {
                "AVAILABLE": 0.3,
                "ASSIGNED": 0.6,
                "DELIVERED": 1.0
            }.get(val.get("status"), 0)

            st.progress(progress)

            if val.get("image"):
                st.image(val["image"], width=250)

            if val.get("proof"):
                st.write("📸 Delivery Proof")
                st.image(val["proof"], width=250)

            st.markdown("</div>", unsafe_allow_html=True)

    except:
        st.error("Backend not reachable")


# ---------------- AUTO REFRESH ----------------
time.sleep(5)
st.rerun()