import streamlit as st
import requests
import time
from streamlit_folium import st_folium
import folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# ---------------- CONFIG ----------------
st.set_page_config(page_title="SmartFood", layout="wide", page_icon="🍲")

# 🔥 BACKEND URL (FINAL)
API = "https://smartfood-backend-ssr.onrender.com/api/v1"

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
    color: white;
}
.stButton>button {
    border-radius: 20px;
    background: linear-gradient(45deg, #00c6ff, #0072ff);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- GEO ----------------
geolocator = Nominatim(user_agent="smartfood")

def get_coords(location):
    try:
        loc = geolocator.geocode(location)
        return (loc.latitude, loc.longitude)
    except:
        return (0, 0)

# ---------------- SIDEBAR ----------------
st.sidebar.title("SmartFood Ecosystem")
page = st.sidebar.selectbox(
    "Select Role",
    ["🍴 Restaurant", "🏢 NGO / Youth", "📦 Delivery Status"]
)

# ---------------- 🍴 RESTAURANT ----------------
if page == "🍴 Restaurant":
    st.header("Upload Surplus Food")

    with st.form("food_form"):
        name = st.text_input("Restaurant Name")
        item = st.text_input("Food Item")
        price = st.number_input("Original Price", min_value=0.0)
        location = st.text_input("Location")

        submit = st.form_submit_button("Upload")

        if submit:
            coords = get_coords(location)

            payload = {
                "restaurant_name": name,
                "food_item": item,
                "original_price": price,
                "location": location,
                "lat": coords[0],
                "lng": coords[1]
            }

            try:
                res = requests.post(f"{API}/listings", json=payload)

                if res.status_code == 201:
                    st.success("✅ Food Listed Successfully!")
                else:
                    st.error("❌ Upload failed")

            except:
                st.error("⚠️ Backend not reachable (wait 30–60 sec)")

# ---------------- 🏢 NGO ----------------
elif page == "🏢 NGO / Youth":
    st.header("🔎 Search Food Near You")

    search_location = st.text_input("Enter Area")

    if st.button("Search"):
        st.session_state["search_location"] = search_location

    if "search_location" in st.session_state:
        loc = st.session_state["search_location"]

        try:
            res = requests.get(f"{API}/listings")
            data = res.json() if res.status_code == 200 else {}

            found = False

            for key, val in data.items():
                location = val.get("location", "").lower()

                if loc.lower() in location:
                    found = True

                    with st.container(border=True):
                        st.write(f"🍲 {val.get('item')}")
                        st.write(f"📍 {val.get('location')}")
                        st.write(f"📦 Status: {val.get('status')}")

                        # ACCEPT
                        if val.get("status") == "AVAILABLE":
                            if st.button("Accept", key=f"a{key}"):
                                requests.post(f"{API}/accept/{key}")
                                st.success("✅ Accepted")

                        # DELIVER
                        elif val.get("status") == "ASSIGNED":
                            if st.button("Deliver", key=f"d{key}"):
                                requests.post(f"{API}/deliver/{key}")
                                st.success("✅ Delivered")

                        else:
                            st.success("✅ Delivered")

            if not found:
                st.warning("❌ No listings found")

        except:
            st.error("⚠️ Backend error")

    # ---------------- MAP ----------------
    st.header("📍 Nearby Listings")

    user_loc = st.text_input("Enter Your Location for Map")

    if user_loc:
        user_coords = get_coords(user_loc)

        try:
            res = requests.get(f"{API}/listings")
            data = res.json() if res.status_code == 200 else {}

            m = folium.Map(location=user_coords, zoom_start=12)
            jobs = []

            for key, val in data.items():
                lat = val.get("lat", 0)
                lng = val.get("lng", 0)

                if lat == 0:
                    continue

                dist = geodesic(user_coords, (lat, lng)).km

                val["distance"] = dist
                val["id"] = key
                jobs.append(val)

                folium.Marker(
                    [lat, lng],
                    popup=f"{val.get('item')} ({dist:.2f} km)"
                ).add_to(m)

            jobs = sorted(jobs, key=lambda x: x["distance"])

            st.subheader("🗺 Map")
            st_folium(m, width=700)

            st.subheader("Nearest Listings")

            for job in jobs[:5]:
                st.write(f"🍲 {job.get('item')}")
                st.write(f"📍 {job.get('location')}")
                st.write(f"📏 {job['distance']:.2f} km")

        except:
            st.error("⚠️ Map loading error")

# ---------------- 📦 STATUS ----------------
elif page == "📦 Delivery Status":
    st.header("All Deliveries")

    try:
        res = requests.get(f"{API}/listings")
        data = res.json() if res.status_code == 200 else {}

        for val in data.values():
            st.write(f"{val.get('item')} → {val.get('status')}")

    except:
        st.error("⚠️ Backend not reachable")

# ---------------- AUTO REFRESH ----------------
time.sleep(3)
st.rerun()