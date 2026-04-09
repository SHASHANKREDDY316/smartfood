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
.card {
    background-color: #1e1e1e;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 15px;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.5);
}
</style>
""", unsafe_allow_html=True)

# ---------------- IMAGE ENCODE ----------------
def encode_image(img):
    return base64.b64encode(img.read()).decode()

# ---------------- SIDEBAR ----------------
page = st.sidebar.selectbox(
    "Select Role",
    ["🍴 Restaurant", "🏢 NGO / Youth", "📦 Delivery Status"]
)

# ---------------- 🍴 RESTAURANT ----------------
if page == "🍴 Restaurant":
    st.header("Upload Food")

    name = st.text_input("Restaurant Name")
    item = st.text_input("Food Item")
    price = st.number_input("Price", min_value=0.0)
    location = st.text_input("Location")
    image = st.file_uploader("Upload Food Image", type=["jpg", "png"])

    if st.button("Submit"):
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
                st.success("✅ Uploaded Successfully")
            else:
                st.error("Upload failed")

        except:
            st.error("Backend not reachable")

# ---------------- 🏢 NGO ----------------
elif page == "🏢 NGO / Youth":
    st.header("Available Food")

    try:
        res = requests.get(f"{API}/listings")
        data = res.json() if res.status_code == 200 else {}

        for key, val in data.items():
            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.subheader(val.get("item"))
            st.write("📍", val.get("location"))
            st.write("📦 Status:", val.get("status"))

            if val.get("image"):
                st.image(val["image"], width=250)

            # ACCEPT
            if val.get("status") == "AVAILABLE":
                if st.button("Accept", key=f"a{key}"):
                    requests.post(f"{API}/accept/{key}")
                    st.success("Accepted")

            # DELIVERY WITH PROOF
            elif val.get("status") == "ASSIGNED":
                proof = st.file_uploader("Upload Proof", key=f"p{key}")

                if proof and st.button("Deliver", key=f"d{key}"):
                    proof_base64 = encode_image(proof)

                    requests.post(
                        f"{API}/deliver/{key}",
                        json={"proof": proof_base64}
                    )

                    st.success("Delivered with proof")

            else:
                st.success("Delivered")

            st.markdown('</div>', unsafe_allow_html=True)

    except:
        st.error("Error loading data")

# ---------------- 📦 DELIVERY STATUS ----------------
elif page == "📦 Delivery Status":
    st.header("All Deliveries")

    try:
        res = requests.get(f"{API}/listings")
        data = res.json() if res.status_code == 200 else {}

        for val in data.values():
            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.subheader(val.get("item"))
            st.write("📍", val.get("location"))
            st.write("📦 Status:", val.get("status"))

            # FOOD IMAGE
            if val.get("image"):
                st.image(val["image"], width=200)

            # DELIVERY PROOF
            if val.get("proof"):
                st.write("📸 Delivery Proof:")
                st.image(val["proof"], width=200)

            st.markdown('</div>', unsafe_allow_html=True)

    except:
        st.error("Backend not reachable")

# ---------------- AUTO REFRESH ----------------
time.sleep(3)
st.rerun()