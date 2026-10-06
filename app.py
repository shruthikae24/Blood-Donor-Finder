import streamlit as st
import sqlite3
import math
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
import urllib.parse


# ==================================================
# PAGE SETTINGS
# ==================================================

st.set_page_config(
    page_title="Real-Time Blood Donor Finder",
    page_icon="🩸",
    layout="wide"
)


# ==================================================
# COLORFUL DESIGN
# ==================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #fff5f5 0%,
        #ffe4e6 45%,
        #f3e8ff 100%
    );
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

h1 {
    color: #be123c;
    font-weight: 800;
    text-align: center;
    font-size: 42px;
}

h2 {
    color: #be123c;
    font-weight: 700;
}

h3 {
    color: #9f1239;
    font-weight: 700;
}

p {
    color: #374151;
    font-size: 17px;
}


/* Header */

.app-header {
    background: linear-gradient(
        90deg,
        #be123c,
        #e11d48,
        #9333ea
    );

    padding: 30px;
    border-radius: 22px;
    color: white;
    text-align: center;
    margin-bottom: 25px;

    box-shadow:
        0px 8px 25px rgba(190,18,60,0.25);
}

.app-header h1 {
    color: white;
    font-size: 40px;
    margin: 0;
}

.app-header p {
    color: white;
    font-size: 18px;
}


/* Buttons */

.stButton > button {

    width: 100%;

    border-radius: 14px;

    border: none;

    padding: 13px 20px;

    font-size: 17px;

    font-weight: 700;

    background: linear-gradient(
        90deg,
        #e11d48,
        #be123c
    );

    color: white;

    box-shadow:
        0px 5px 15px rgba(190,18,60,0.25);

    transition: 0.3s;
}

.stButton > button:hover {

    transform: translateY(-3px);

    background: linear-gradient(
        90deg,
        #be123c,
        #9333ea
    );

    box-shadow:
        0px 8px 20px rgba(190,18,60,0.35);
}


/* Text Input */

.stTextInput input {

    border-radius: 12px;

    border: 2px solid #fda4af;

    padding: 12px;

    background-color: white;
}

.stTextInput input:focus {

    border-color: #e11d48;

    box-shadow:
        0 0 8px rgba(225,29,72,0.25);
}


/* Select Box */

.stSelectbox > div > div {

    border-radius: 12px;

    border: 2px solid #fda4af;

    background-color: white;
}


/* Labels */

label {

    font-weight: 700 !important;

    color: #4c0519 !important;
}


/* Messages */

.stSuccess,
.stError,
.stWarning {

    border-radius: 12px;

    font-weight: 600;
}


/* Lines */

hr {

    border: none;

    height: 2px;

    background: linear-gradient(
        90deg,
        #fb7185,
        #c084fc,
        #60a5fa
    );

    margin: 25px 0;
}


/* Donor Card */

.donor-card {

    background: linear-gradient(
        135deg,
        #ffffff,
        #fff1f2
    );

    padding: 22px;

    border-radius: 20px;

    border: 1px solid #fecdd3;

    box-shadow:
        0px 6px 20px rgba(190,18,60,0.12);

    margin: 15px 0;
}


/* Hospital Card */

.hospital-card {

    background: linear-gradient(
        135deg,
        #ffffff,
        #eff6ff
    );

    padding: 22px;

    border-radius: 20px;

    border: 1px solid #bfdbfe;

    box-shadow:
        0px 6px 20px rgba(37,99,235,0.12);

    margin: 15px 0;
}


/* Blood Bank Card */

.blood-bank-card {

    background: linear-gradient(
        135deg,
        #ffffff,
        #fef3c7
    );

    padding: 22px;

    border-radius: 20px;

    border: 1px solid #fde68a;

    box-shadow:
        0px 6px 20px rgba(217,119,6,0.12);

    margin: 15px 0;
}


/* Profile Card */

.profile-card {

    background: white;

    padding: 25px;

    border-radius: 20px;

    border-left: 7px solid #e11d48;

    box-shadow:
        0px 6px 20px rgba(0,0,0,0.08);

    margin: 15px 0;
}


/* Footer */

.footer {

    text-align: center;

    padding: 20px;

    margin-top: 40px;

    color: #6b7280;

    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# SESSION STATE
# ==================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "login_type" not in st.session_state:
    st.session_state.login_type = ""

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "hospital_data" not in st.session_state:
    st.session_state.hospital_data = None

if "hospital_location" not in st.session_state:
    st.session_state.hospital_location = None


# ==================================================
# DATABASE
# ==================================================

conn = sqlite3.connect(
    "blood_donor.db",
    check_same_thread=False
)

cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS donors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    mobile TEXT NOT NULL,
    email TEXT NOT NULL,
    blood_group TEXT NOT NULL,
    location TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    password TEXT NOT NULL,
    available TEXT NOT NULL
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS acceptors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    mobile TEXT NOT NULL,
    email TEXT NOT NULL,
    blood_group TEXT NOT NULL,
    location TEXT NOT NULL,
    password TEXT NOT NULL
)
""")


conn.commit()


# ==================================================
# LOCATION
# ==================================================

geolocator = Nominatim(
    user_agent="real_time_blood_donor_finder"
)


def get_location(location_name):

    try:

        place = geolocator.geocode(
            location_name
        )

        if place:

            return (
                place.latitude,
                place.longitude
            )

        return None, None

    except Exception:

        return None, None


# ==================================================
# DISTANCE
# ==================================================

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    R = 6371

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)

    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        +
        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


# ==================================================
# HOME PAGE
# ==================================================

if st.session_state.page == "home":

    with st.container(key="home-header"):

        st.title(
            "🩸 Real-Time Blood Donor Finder"
        )

        st.write(
            "❤️ Find blood donors quickly and help save lives ❤️"
        )


    st.subheader(
        "🔎 Find Blood When You Need It"
    )

    st.write(
        "This application helps people find "
        "available blood donors based on blood "
        "group and location."
    )

    st.write("")


    if st.button(
        "🔐 Login",
        use_container_width=True
    ):

        st.session_state.page = "login"

        st.rerun()


    st.write("")


    if st.button(
        "📝 Register",
        use_container_width=True
    ):

        st.session_state.page = "register"

        st.rerun()


    with st.container(key="home-footer"):

        st.write(
            "🩸 Donate Blood • Save Lives • Be a Hero ❤️"
        )


# ==================================================
# LOGIN PAGE
# ==================================================

elif st.session_state.page == "login":

    with st.container(key="login-header"):

        st.title(
            "🔐 Login"
        )

        st.write(
            "Welcome back to Blood Donor Finder"
        )


    login_type = st.selectbox(
        "Login As",
        [
            "Blood Donor",
            "Blood Acceptor"
        ]
    )


    email = st.text_input(
        "📧 Email"
    )


    password = st.text_input(
        "🔑 Password",
        type="password"
    )


    if st.button(
        "🔐 Login",
        use_container_width=True
    ):

        if login_type == "Blood Donor":

            cursor.execute(
                """
                SELECT * FROM donors
                WHERE email=? AND password=?
                """,
                (email, password)
            )

        else:

            cursor.execute(
                """
                SELECT * FROM acceptors
                WHERE email=? AND password=?
                """,
                (email, password)
            )


        user = cursor.fetchone()


        if user:

            st.session_state.logged_in = True

            st.session_state.login_type = login_type

            st.session_state.user_email = email

            st.session_state.page = "dashboard"

            st.success(
                "✅ Login successful!"
            )

            st.rerun()

        else:

            st.error(
                "❌ Invalid email or password"
            )


    st.write("")


    if st.button("⬅️ Back"):

        st.session_state.page = "home"

        st.rerun()


# ==================================================
# REGISTER PAGE
# ==================================================

elif st.session_state.page == "register":

    with st.container(key="register-header"):

        st.title(
            "📝 Registration"
        )

        st.write(
            "Join our blood donation community"
        )


    register_type = st.selectbox(
        "Register As",
        [
            "Blood Donor",
            "Blood Acceptor"
        ]
    )


    name = st.text_input(
        "👤 Full Name"
    )


    mobile = st.text_input(
        "📱 Mobile Number"
    )


    email = st.text_input(
        "📧 Email"
    )


    blood_group = st.selectbox(
        "🩸 Blood Group",
        [
            "A+",
            "A-",
            "B+",
            "B-",
            "AB+",
            "AB-",
            "O+",
            "O-"
        ]
    )


    location = st.text_input(
        "📍 Location",
        placeholder="Example: Hyderabad"
    )


    password = st.text_input(
        "🔑 Password",
        type="password"
    )


    if register_type == "Blood Donor":

        available = st.selectbox(
            "❤️ Available for Donation?",
            [
                "Yes",
                "No"
            ]
        )


    if st.button(
        "📝 Register",
        use_container_width=True
    ):

        if (
            name == ""
            or mobile == ""
            or email == ""
            or location == ""
            or password == ""
        ):

            st.error(
                "❌ Please fill all fields."
            )

        else:

            if register_type == "Blood Donor":

                lat, lon = get_location(
                    location
                )


                cursor.execute(
                    """
                    INSERT INTO donors
                    (
                        name,
                        mobile,
                        email,
                        blood_group,
                        location,
                        latitude,
                        longitude,
                        password,
                        available
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        name,
                        mobile,
                        email,
                        blood_group,
                        location,
                        lat,
                        lon,
                        password,
                        available
                    )
                )


                conn.commit()


                st.success(
                    "🩸 Blood donor registered successfully!"
                )

            else:

                cursor.execute(
                    """
                    INSERT INTO acceptors
                    (
                        name,
                        mobile,
                        email,
                        blood_group,
                        location,
                        password
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        name,
                        mobile,
                        email,
                        blood_group,
                        location,
                        password
                    )
                )


                conn.commit()


                st.success(
                    "❤️ Blood acceptor registered successfully!"
                )


    st.write("")


    if st.button("⬅️ Back"):

        st.session_state.page = "home"

        st.rerun()


# ==================================================
# DASHBOARD
# ==================================================

elif st.session_state.page == "dashboard":

    with st.container(key="dashboard-header"):

        st.title(
            "🏠 Dashboard"
        )

        st.write(
            "Real-Time Blood Donor Finder"
        )


    if st.session_state.login_type == "Blood Donor":

        st.success(
            "🩸 Logged in as Blood Donor"
        )

    else:

        st.success(
            "❤️ Logged in as Blood Acceptor"
        )


    st.write("")


    col1, col2 = st.columns(2)


    with col1:

        if st.button(
            "🩸 Find Blood Donor",
            use_container_width=True
        ):

            st.session_state.page = "find_donor"

            st.rerun()


        if st.button(
            "🏥 Nearby Hospitals",
            use_container_width=True
        ):

            st.session_state.page = "hospitals"

            st.rerun()


    with col2:

        if st.button(
            "🏦 Blood Banks",
            use_container_width=True
        ):

            st.session_state.page = "blood_banks"

            st.rerun()


        if st.button(
            "👤 My Profile",
            use_container_width=True
        ):

            st.session_state.page = "profile"

            st.rerun()


    st.write("")


    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False

        st.session_state.login_type = ""

        st.session_state.user_email = ""

        st.session_state.page = "home"

        st.rerun()


# ==================================================
# FIND BLOOD DONOR
# ==================================================

elif st.session_state.page == "find_donor":

    with st.container(key="find-donor-header"):

        st.title(
            "🩸 Find Blood Donor"
        )

        st.write(
            "Find available donors near your location"
        )


    blood_group = st.selectbox(
        "Required Blood Group",
        [
            "A+",
            "A-",
            "B+",
            "B-",
            "AB+",
            "AB-",
            "O+",
            "O-"
        ]
    )


    search_location = st.text_input(
        "📍 Enter Your Location",
        placeholder="Example: Hyderabad"
    )


    radius = st.selectbox(
        "📏 Search Radius",
        [
            2,
            5,
            10,
            20,
            50
        ]
    )


    if st.button(
        "🔎 Search Donors",
        use_container_width=True
    ):

        if search_location == "":

            st.error(
                "❌ Please enter your location."
            )

        else:

            lat, lon = get_location(
                search_location
            )


            if lat is None:

                st.error(
                    "❌ Location not found."
                )

            else:

                cursor.execute(
                    """
                    SELECT
                        name,
                        mobile,
                        email,
                        blood_group,
                        location,
                        latitude,
                        longitude
                    FROM donors
                    WHERE blood_group=?
                    AND available='Yes'
                    """,
                    (blood_group,)
                )


                donors = cursor.fetchall()


                nearby_donors = []


                for donor in donors:

                    name = donor[0]
                    mobile = donor[1]
                    email = donor[2]
                    bg = donor[3]
                    donor_location = donor[4]
                    donor_lat = donor[5]
                    donor_lon = donor[6]


                    if (
                        donor_lat is not None
                        and donor_lon is not None
                    ):

                        distance = calculate_distance(
                            lat,
                            lon,
                            donor_lat,
                            donor_lon
                        )


                        if distance <= radius:

                            nearby_donors.append(
                                (
                                    name,
                                    mobile,
                                    email,
                                    bg,
                                    donor_location,
                                    distance,
                                    donor_lat,
                                    donor_lon
                                )
                            )


                if nearby_donors:

                    st.success(
                        f"🩸 {len(nearby_donors)} donor(s) found!"
                    )


                    nearby_donors.sort(
                        key=lambda x: x[5]
                    )


                    for i, donor in enumerate(
                        nearby_donors
                    ):

                        name = donor[0]
                        mobile = donor[1]
                        email = donor[2]
                        bg = donor[3]
                        donor_location = donor[4]
                        distance = donor[5]


                        with st.container(
                            key=f"donor-card-{i}"
                        ):

                            st.subheader(
                                f"🩸 {name}"
                            )


                            st.write(
                                f"🩸 Blood Group: {bg}"
                            )


                            st.write(
                                f"📍 Location: {donor_location}"
                            )


                            st.write(
                                f"📏 Distance: "
                                f"{distance:.2f} km"
                            )


                            st.write(
                                f"📞 Mobile: {mobile}"
                            )


                            st.markdown(
                                f"[📞 Call Donor](tel:{mobile})"
                            )


                            whatsapp_number = (
                                str(mobile)
                                .replace(" ", "")
                                .replace("-", "")
                            )


                            if whatsapp_number.startswith("0"):

                                whatsapp_number = (
                                    "91"
                                    + whatsapp_number[1:]
                                )

                            elif not whatsapp_number.startswith("91"):

                                whatsapp_number = (
                                    "91"
                                    + whatsapp_number
                                )


                            whatsapp_url = (
                                "https://wa.me/"
                                + whatsapp_number
                            )


                            st.markdown(
                                f"[💬 WhatsApp Donor]({whatsapp_url})"
                            )


                else:

                    st.warning(
                        "⚠️ No nearby donor found."
                    )


    st.write("")


    if st.button(
        "⬅️ Back to Dashboard"
    ):

        st.session_state.page = "dashboard"

        st.rerun()


# ==================================================
# HOSPITALS
# ==================================================

elif st.session_state.page == "hospitals":

    with st.container(key="hospitals-header"):

        st.title(
            "🏥 Nearby Hospitals"
        )

        st.write(
            "Find hospitals near your location"
        )


    hospital_location = st.text_input(
        "📍 Enter Location",
        placeholder="Example: Hyderabad"
    )


    if st.button(
        "🔎 Find Hospitals",
        use_container_width=True
    ):

        if hospital_location == "":

            st.error(
                "❌ Please enter a location."
            )

        else:

            lat, lon = get_location(
                hospital_location
            )


            if lat is None:

                st.error(
                    "❌ Location not found."
                )

            else:

                hospitals = [

                    {
                        "name":
                        "Nearby Government Hospital",

                        "lat":
                        lat + 0.01,

                        "lon":
                        lon + 0.01,

                        "phone":
                        "040-00000000"
                    },

                    {
                        "name":
                        "City Care Hospital",

                        "lat":
                        lat - 0.01,

                        "lon":
                        lon - 0.01,

                        "phone":
                        "040-11111111"
                    },

                    {
                        "name":
                        "Emergency Care Hospital",

                        "lat":
                        lat + 0.02,

                        "lon":
                        lon - 0.01,

                        "phone":
                        "040-22222222"
                    }
                ]


                st.session_state.hospital_data = hospitals

                st.session_state.hospital_location = (
                    lat,
                    lon
                )


    if st.session_state.hospital_data:

        lat, lon = (
            st.session_state.hospital_location
        )


        st.success(
            "🏥 Hospital details found!"
        )


        for i, hospital in enumerate(
            st.session_state.hospital_data
        ):

            distance = calculate_distance(
                lat,
                lon,
                hospital["lat"],
                hospital["lon"]
            )


            with st.container(
                key=f"hospital-card-{i}"
            ):

                st.subheader(
                    f"🏥 {hospital['name']}"
                )


                st.write(
                    f"📏 Distance: "
                    f"{distance:.2f} km"
                )


                st.write(
                    f"📞 Phone: "
                    f"{hospital['phone']}"
                )


                st.markdown(
                    f"[📞 Call Hospital](tel:{hospital['phone']})"
                )


                hospital_phone = (
                    hospital["phone"]
                    .replace("-", "")
                    .replace(" ", "")
                )


                whatsapp_url = (
                    "https://wa.me/91"
                    + hospital_phone
                )


                st.markdown(
                    f"[💬 WhatsApp Hospital]({whatsapp_url})"
                )


                maps_url = (
                    "https://www.google.com/maps/dir/"
                    f"{lat},{lon}/"
                    f"{hospital['lat']},"
                    f"{hospital['lon']}"
                )


                st.markdown(
                    f"[🗺️ Get Directions]({maps_url})"
                )


        st.markdown("---")


        st.subheader(
            "🗺️ Hospital Map"
        )


        map_object = folium.Map(
            location=[
                lat,
                lon
            ],
            zoom_start=13
        )


        folium.Marker(
            [
                lat,
                lon
            ],
            popup="Your Location",
            tooltip="Your Location",
            icon=folium.Icon(
                color="blue",
                icon="user"
            )
        ).add_to(
            map_object
        )


        for hospital in (
            st.session_state.hospital_data
        ):

            folium.Marker(
                [
                    hospital["lat"],
                    hospital["lon"]
                ],
                popup=(
                    f"{hospital['name']}"
                    f"<br>"
                    f"Phone: "
                    f"{hospital['phone']}"
                ),
                tooltip=hospital["name"],
                icon=folium.Icon(
                    color="red",
                    icon="plus"
                )
            ).add_to(
                map_object
            )


        st_folium(
            map_object,
            width=900,
            height=500
        )


    st.write("")


    if st.button(
        "⬅️ Back to Dashboard"
    ):

        st.session_state.hospital_data = None

        st.session_state.hospital_location = None

        st.session_state.page = "dashboard"

        st.rerun()


# ==================================================
# BLOOD BANKS
# ==================================================

elif st.session_state.page == "blood_banks":

    with st.container(key="blood-banks-header"):

        st.title(
            "🏦 Blood Banks"
        )

        st.write(
            "Check available blood stock information"
        )


    st.write(
        "Available blood stock information"
    )


    blood_stock = {

        "A+": 5,
        "A-": 2,

        "B+": 6,
        "B-": 1,

        "AB+": 3,
        "AB-": 1,

        "O+": 8,
        "O-": 2
    }


    st.subheader(
        "🩸 Blood Stock"
    )


    with st.container(
        key="blood-bank-stock"
    ):

        for group, units in blood_stock.items():

            st.write(
                f"🩸 **{group}** : {units} units"
            )


    st.markdown("---")


    st.subheader(
        "🏦 Blood Bank Details"
    )


    with st.container(
        key="blood-bank-details"
    ):

        st.write(
            "🏦 **City Blood Bank**"
        )


        st.write(
            "📍 Location: Hyderabad"
        )


        st.write(
            "📞 Phone: 040-12345678"
        )


        st.markdown(
            "[📞 Call Blood Bank](tel:04012345678)"
        )


        st.markdown(
            "[🗺️ Open Google Maps]"
            "(https://www.google.com/maps)"
        )


    st.warning(
        "⚠️ Note: Blood stock shown here is "
        "demo data. Actual availability "
        "must be confirmed with the blood bank."
    )


    if st.button(
        "⬅️ Back to Dashboard"
    ):

        st.session_state.page = "dashboard"

        st.rerun()


# ==================================================
# PROFILE
# ==================================================

elif st.session_state.page == "profile":

    with st.container(key="profile-header"):

        st.title(
            "👤 My Profile"
        )

        st.write(
            "View your registered details"
        )


    email = st.session_state.user_email


    if st.session_state.login_type == "Blood Donor":

        cursor.execute(
            """
            SELECT
                name,
                mobile,
                email,
                blood_group,
                location,
                available
            FROM donors
            WHERE email=?
            """,
            (email,)
        )


        user = cursor.fetchone()


        if user:

            with st.container(
                key="profile-card-donor"
            ):

                st.subheader(
                    "🩸 Blood Donor Profile"
                )


                st.write(
                    f"**👤 Name:** {user[0]}"
                )


                st.write(
                    f"**📱 Mobile:** {user[1]}"
                )


                st.write(
                    f"**📧 Email:** {user[2]}"
                )


                st.write(
                    f"**🩸 Blood Group:** {user[3]}"
                )


                st.write(
                    f"**📍 Location:** {user[4]}"
                )


                st.write(
                    f"**❤️ Available:** {user[5]}"
                )


    else:

        cursor.execute(
            """
            SELECT
                name,
                mobile,
                email,
                blood_group,
                location
            FROM acceptors
            WHERE email=?
            """,
            (email,)
        )


        user = cursor.fetchone()


        if user:

            with st.container(
                key="profile-card-acceptor"
            ):

                st.subheader(
                    "🧑 Blood Acceptor Profile"
                )


                st.write(
                    f"**👤 Name:** {user[0]}"
                )


                st.write(
                    f"**📱 Mobile:** {user[1]}"
                )


                st.write(
                    f"**📧 Email:** {user[2]}"
                )


                st.write(
                    f"**🩸 Required Blood Group:** {user[3]}"
                )


                st.write(
                    f"**📍 Location:** {user[4]}"
                )


    st.write("")


    if st.button(
        "⬅️ Back to Dashboard"
    ):

        st.session_state.page = "dashboard"

        st.rerun()