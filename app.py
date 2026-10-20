
import streamlit as st
import pandas as pd
from datetime import datetime

from graph_retriever import find_transport_partners
from groq_chat import ask_logistics_question


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Logistics Graph RAG",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# CUSTOM UI STYLING
# --------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 85% 5%, #172554 0%, transparent 28%),
            linear-gradient(135deg, #080d1a 0%, #0b1220 55%, #101827 100%);
        color: #e5e7eb;
    }

    [data-testid="stSidebar"] {
        background: #0c1322;
        border-right: 1px solid #263247;
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #f8fafc;
    }

    .hero {
        padding: 30px 32px;
        border: 1px solid #293750;
        border-radius: 22px;
        background: linear-gradient(115deg, #111d33, #101827 65%, #142443);
        margin-bottom: 24px;
    }

    .hero-tag {
        color: #60a5fa;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .hero h1 {
        color: #f8fafc;
        font-size: clamp(28px, 4vw, 43px);
        line-height: 1.15;
        margin: 12px 0;
        font-weight: 800;
    }

    .hero p {
        color: #aab8cc;
        font-size: 15px;
        max-width: 720px;
        line-height: 1.7;
        margin-bottom: 0;
    }

    .section-heading {
        color: #f8fafc;
        font-size: 20px;
        font-weight: 700;
        margin: 12px 0 15px 0;
    }

    .info-card {
        background: #111b2d;
        border: 1px solid #293750;
        border-radius: 16px;
        padding: 20px;
        min-height: 120px;
    }

    .info-label {
        color: #94a3b8;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .info-value {
        color: #f8fafc;
        font-size: 25px;
        font-weight: 800;
        margin-top: 10px;
    }

    .info-sub {
        color: #93a4bb;
        font-size: 12px;
        margin-top: 5px;
    }

    .truck-card {
        background: linear-gradient(135deg, #111d30, #0f1726);
        border: 1px solid #2b3a53;
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0;
    }

    .truck-title {
        color: #f8fafc;
        font-size: 19px;
        font-weight: 700;
    }

    .truck-id {
        color: #60a5fa;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
    }

    .truck-detail {
        color: #bdc9da;
        font-size: 14px;
        margin-top: 8px;
        line-height: 1.7;
    }

    .status-pill {
        display: inline-block;
        color: #86efac;
        background: #123326;
        border: 1px solid #236345;
        border-radius: 20px;
        padding: 5px 10px;
        font-size: 11px;
        font-weight: 700;
    }

    .ai-card {
        background: #111b2d;
        border-left: 4px solid #60a5fa;
        border-radius: 12px;
        padding: 20px;
        color: #dbeafe;
        line-height: 1.8;
        margin-top: 12px;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid #3b82f6;
        background: linear-gradient(90deg, #2563eb, #3b82f6);
        color: white;
        font-weight: 700;
        min-height: 45px;
        transition: 0.2s ease;
    }

    div.stButton > button:hover {
        border-color: #93c5fd;
        background: #1d4ed8;
        color: white;
    }

    div[data-testid="stMetric"] {
        background: #111b2d;
        border: 1px solid #293750;
        border-radius: 14px;
        padding: 16px;
    }

    div[data-testid="stMetricLabel"] {
        color: #aab8cc;
    }

    div[data-testid="stMetricValue"] {
        color: #f8fafc;
    }

    .footer {
        text-align: center;
        color: #718096;
        font-size: 12px;
        padding: 28px 0 10px 0;
    }

    .stCaption {
        color: #94a3b8;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "search_history" not in st.session_state:
    st.session_state.search_history = []

if "search_result" not in st.session_state:
    st.session_state.search_result = None


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.markdown("## 🚚 Logistics AI")
    st.caption("Graph-powered transport discovery")

    st.divider()

    st.markdown("### 🔎 Route Search")
    st.caption("Choose your shipment requirements.")

    cities = [
        "Coimbatore",
        "Chennai",
        "Bengaluru",
        "Madurai",
    ]

    origin = st.selectbox(
        "Origin city",
        cities,
        index=0,
        key="origin_city",
    )

    destination_options = [
        city for city in cities if city != origin
    ]

    destination = st.selectbox(
        "Destination city",
        destination_options,
        index=0,
        key="destination_city",
    )

    min_capacity = st.slider(
        "Minimum truck capacity (tons)",
        min_value=0,
        max_value=20,
        value=5,
        step=1,
    )

    st.markdown("")
    search_clicked = st.button(
        "🔍 Find Available Trucks",
        use_container_width=True,
    )

    st.divider()

    st.markdown("### 🧠 How it works")
    st.markdown(
        """
        1. **Your request** — select a route and capacity.
        2. **Neo4j Graph** — finds matching trucks and partners.
        3. **Groq AI** — explains the retrieved information.
        4. **Results** — review the matching transport options.
        """
    )

    st.divider()
    st.caption("Powered by Neo4j Aura + Groq")


# --------------------------------------------------
# HERO SECTION
# --------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div class="hero-tag">Intelligent Logistics Platform</div>
        <h1>Find the right truck.<br>Move your business forward.</h1>
        <p>
            Discover transport partners using Graph RAG.
            Search routes, compare truck capacity, and get
            AI-assisted answers grounded in your Neo4j graph data.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# TOP METRICS
# --------------------------------------------------
metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.markdown(
        """
        <div class="info-card">
            <div class="info-label">Graph Database</div>
            <div class="info-value">Neo4j</div>
            <div class="info-sub">Connected transport relationships</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with metric2:
    st.markdown(
        """
        <div class="info-card">
            <div class="info-label">AI Assistant</div>
            <div class="info-value">Groq AI</div>
            <div class="info-sub">Natural-language explanations</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with metric3:
    st.markdown(
        """
        <div class="info-card">
            <div class="info-label">Retrieval Method</div>
            <div class="info-value">Graph RAG</div>
            <div class="info-sub">Answers grounded in graph records</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# SEARCH RESULTS
# --------------------------------------------------
st.markdown(
    '<div class="section-heading">📍 Transport Search Results</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Select your route in the sidebar, then click Find Available Trucks."
)


if search_clicked:
    if origin == destination:
        st.error("Origin and destination must be different.")
    else:
        with st.spinner("Searching Neo4j and preparing your results..."):
            try:
                records = find_transport_partners(
                    origin=origin,
                    destination=destination,
                    min_capacity=min_capacity,
                )

                if records:
                    answer = ask_logistics_question(
                        origin=origin,
                        destination=destination,
                        min_capacity=min_capacity,
                    )
                else:
                    answer = (
                        f"No matching truck was found for {origin} "
                        f"to {destination} with at least "
                        f"{min_capacity} tons of capacity."
                    )

                result = {
                    "origin": origin,
                    "destination": destination,
                    "min_capacity": min_capacity,
                    "records": records,
                    "answer": answer,
                    "time": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                }

                st.session_state.search_result = result
                st.session_state.search_history.insert(0, result)
                st.session_state.search_history = (
                    st.session_state.search_history[:10]
                )

            except Exception as error:
                st.error(
                    "The search could not be completed. "
                    "Check your Neo4j connection, Groq API key, "
                    "and terminal error."
                )
                with st.expander("Technical error details"):
                    st.code(str(error))


# --------------------------------------------------
# DISPLAY CURRENT RESULT
# --------------------------------------------------
result = st.session_state.search_result

if result:
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Matching Trucks", len(result["records"]))

    with col2:
        st.metric("Minimum Capacity", f'{result["min_capacity"]} tons')

    with col3:
        st.metric(
            "Route",
            f'{result["origin"]} → {result["destination"]}',
        )

    st.markdown(
        '<div class="section-heading">🚛 Matching Transport Partners</div>',
        unsafe_allow_html=True,
    )

    if result["records"]:
        for truck in result["records"]:
            st.markdown(
                f"""
                <div class="truck-card">
                    <div class="truck-id">{truck.get('truck_id', 'Truck ID unavailable')}</div>
                    <div class="truck-title">🚚 {truck.get('partner', 'Unknown partner')}</div>
                    <div class="truck-detail">
                        <b>Truck type:</b> {truck.get('truck_type', 'Not specified')}<br>
                        <b>Capacity:</b> {truck.get('capacity_tons', 'N/A')} tons<br>
                        <b>Route:</b> {truck.get('origin', result['origin'])}
                        → {truck.get('destination', result['destination'])}<br>
                        <b>Distance:</b> {truck.get('distance_km', 'N/A')} km
                    </div>
                    <br>
                    <span class="status-pill">✓ Available in graph data</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with st.expander("📊 View retrieved graph records"):
            st.dataframe(
                pd.DataFrame(result["records"]),
                use_container_width=True,
                hide_index=True,
            )

    else:
        st.warning(
            "No trucks match this route and capacity in the current "
            "graph data. Try another route or a lower capacity."
        )

    st.markdown(
        '<div class="section-heading">🤖 AI Logistics Assistant</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="ai-card">
            <b>Route request:</b> {result['origin']} → {result['destination']}<br>
            <b>Minimum capacity:</b> {result['min_capacity']} tons<br><br>
            {result['answer']}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        f"Last searched: {result['time']}. "
        "Availability reflects your graph records and may not represent "
        "live fleet availability."
    )

else:
    st.info(
        "👈 Choose an origin, destination, and minimum capacity in the "
        "sidebar to start your first search."
    )


# --------------------------------------------------
# SEARCH HISTORY
# --------------------------------------------------
st.markdown("---")
st.markdown(
    '<div class="section-heading">🕘 Recent Searches</div>',
    unsafe_allow_html=True,
)

if st.session_state.search_history:
    history_rows = []

    for item in st.session_state.search_history:
        history_rows.append(
            {
                "Time": item["time"],
                "Origin": item["origin"],
                "Destination": item["destination"],
                "Minimum Capacity (tons)": item["min_capacity"],
                "Matching Trucks": len(item["records"]),
            }
        )

    st.dataframe(
        pd.DataFrame(history_rows),
        use_container_width=True,
        hide_index=True,
    )

    if st.button("🗑️ Clear Search History"):
        st.session_state.search_history = []
        st.session_state.search_result = None
        st.rerun()

else:
    st.caption("Your searches will appear here during this session.")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown(
    """
    <div class="footer">
        LOGISTICS GRAPH RAG · Neo4j Aura · Groq AI · Streamlit
        <br><br>
        Demo application using sample transport data.
    </div>
    """,
    unsafe_allow_html=True,
)
