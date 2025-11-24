import streamlit as st
from find_product import get_data, d_prompt
import re
import pandas as pd
import plotly.express as px

# ---------------------------------- CONFIG -------------------------------
st.set_page_config(page_title="SMART PRODUCT FINDER", page_icon="🛍️", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');

/* Gradient background */
[data-testid=stAppViewContainer] {
    background: linear-gradient(120deg, #2d3250 0%, #6c47d9 80%, #1e1b32 100%);
    min-height: 100vh;
}

/* Glass effect for main panel */
.stApp {
    background: rgba(255,255,255,0.07);
    border-radius: 30px;
    box-shadow: 0 10px 30px rgba(40,0,90,0.12);
    padding: 36px;
    margin: 50px 80px;
    backdrop-filter: blur(8px);
}

/* Neon blue glowing main title */
h1, .main-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 68px;
    color: #00e4fa;
    text-align: center;
    text-shadow: 0 0 36px #00e4fa, 0 0 54px #6c47d9;
    margin-top: 60px;
}

/* Subtitle styling */
.sub-title {
    font-family: 'Orbitron', sans-serif;
    color: #fff;
    font-size: 28px;
    text-align: center;
    margin-bottom: 32px;
    letter-spacing: 2px;
}

/* Sidebar: dark with glowing line */
[data-testid=stSidebar] {
    background: #171630;
    border-right: 4px solid #00e4fa;
    box-shadow: 4px 0 16px #00e4fa55;
    color: #fff;
}

/* Neon buttons */
.stButton>button {
    background: #22216a;
    color: #00e4fa;
    border: 2px solid #00e4fa;
    font-weight: 700;
    border-radius: 12px;
    font-size: 20px;
    padding: 10px 34px;
    box-shadow: 0 2px 12px #00e4fa44;
    margin-bottom: 14px;
    transition: background 0.3s;
}
.stButton>button:hover {
    background: #00e4fa;
    color: #22216a;
    border-color: #fff;
}

/* Neon inputs */
.stTextInput>div>input, .stTextArea>div>textarea {
    background: #232048;
    color: #00e4fa;
    border-radius: 10px;
    border: 1.5px solid #6c47d9;
    font-size: 18px;
    box-shadow: 0 2px 10px #00e4fa22;
}
</style>
""", unsafe_allow_html=True)


st.markdown("<h1 class='main-title'>🛍️ Product OptiChoice</h1>", unsafe_allow_html=True)
st.markdown('<h4 class="sub-title">Find the best product using smart comparison 🔎✨</h4>', unsafe_allow_html=True)

# ---------------------------- API STATUS ----------------------------
try:
    from find_product import check_scrapingbee_status
    status = check_scrapingbee_status()
    if status['status'] == 'connected':
        st.sidebar.success("✅ APP Connected")
    else:
        st.sidebar.error(f"❌ API Error: {status.get('message', 'Unknown error')}")
except:
    st.sidebar.warning("⚠️ ScrapingBee API not configured")

# ---------------------------- SESSION INIT ----------------------------
if "urls" not in st.session_state:
    st.session_state.urls = ["", ""]
if "content" not in st.session_state:
    st.session_state.content = []
if "figure" not in st.session_state:
    st.session_state.figure = []
# ---------------------------- ADD INPUT ----------------------------
def add_text_input():
    st.session_state.urls.append("")

st.sidebar.title("🔗 Paste Amazon URLs")

for i, url in enumerate(st.session_state.urls):
    st.session_state.urls[i] = st.sidebar.text_input(f"URL {i+1}", url, key=f"url_{i}")

# ---------------------------- PROCESSING FUNCTION ----------------------------
def generate():
    lst, title, rate, keys, values, urls = [], [], [], [], [], []

    for url in st.session_state.urls:
        if url:
            details, tit, rank = get_data(url)
            urls.append(url)
            title.append(tit)

            match = re.search(r"(\d\.\d) out of 5", rank)
            rate.append(float(match.group(1)) if match else 0)
            
            with open("specify.txt", "r+", encoding="utf-8") as ps:
                content = re.sub(r"â€Ž|â|€|Ž", "", ps.read())
                ps.truncate(0)
                lst.append(content)

                for k, v in details.items():
                    keys.append(k)
                    values.append(v)

                df = pd.DataFrame({'Name': keys, 'Value': values})
                st.session_state.content.append(("📦 " + tit, df))
                keys.clear()
                values.clear()
    my_text, _, sim = d_prompt(lst)

    st.session_state.content.append(("✅ Best Specifications", json_to_df(my_text)))

    df = pd.DataFrame(
        {'Percentage': sim, 'Text': title, 'urls': urls}
    ).sort_values(by='Percentage', ascending=False)

    df1 = pd.DataFrame(
        {'rating': rate, 'Text': title, 'urls': urls}
    ).sort_values(by='rating', ascending=False)

    st.session_state.content.append(("🏆 Ranking by Specifications", format_ranking(df)))
    st.session_state.content.append(("⭐ Ranking by Rating", format_ranking(df1)))

    fig1 = px.pie(values=rate, names=title, title="🌟 Rating Pie Chart")
    fig2 = px.pie(values=sim, names=title, title="📊 Specifications Pie Chart")

    st.session_state.figure.extend([fig1, fig2])

def json_to_df(data):
    import json
    try:
        if isinstance(data, str):
            data = json.loads(data)
        return pd.DataFrame(list(data.items()), columns=["Feature", "Value"])
    except:
        return pd.DataFrame([["Parse Error", str(data)]], columns=["Feature", "Value"])

def format_ranking(df):
    output = ""
    for i, row in enumerate(df.itertuples()):
        output += f"{i+1}) [{row.Text}]({row.urls})  \n"
    return output

# ---------------------------- BUTTONS (HORIZONTAL) ----------------------------
with st.sidebar:

    if st.button("➕ Add URL", width='stretch'):
        add_text_input()

    st.write("")  # spacer

    if st.button("🔁 Rerun", width='stretch'):
        generate()

    st.write("")  # spacer

    if st.button("🚀 Compare", width='stretch'):
        generate()

# ---------------------------- DISPLAY OUTPUT ----------------------------
# --------- METRICS (RIGHT AFTER HEADER, BEFORE TABS) ----------
# Calculate these based on your real data -- placeholder logic here:
if st.session_state.content:
    top_rating = 0
    max_similarity = 0
    num_products = len(st.session_state.urls)
    for header, df in st.session_state.content:
        if "Ranking by Rating" in header and not isinstance(df, str):
            if not df.empty and "rating" in df:
                top_rating = df["rating"].max()
        if "Ranking by Specifications" in header and not isinstance(df, str):
            if not df.empty and "Percentage" in df:
                max_similarity = df["Percentage"].max()
    col1, col2, col3 = st.columns(3)
    col1.metric("Top Rating", f"{top_rating} ⭐")
    col2.metric("Max Similarity", f"{max_similarity}%")
    col3.metric("Products Compared", f"{num_products}")

# ---------- TABS FOR OUTPUT ----------
tab1, tab2, tab3 = st.tabs(["Overview", "Compare Table", "Details"])


with tab1:
    st.subheader("Quick Summary")
    # Pie/Bar charts
    for fig in st.session_state.figure:
        st.plotly_chart(fig, width='stretch')

with tab2:
    st.subheader("Comparison Table")
    # Show summary DataFrames (e.g., best/worst ranking etc.)
    for header, content in st.session_state.content:
        if "Ranking" in header and isinstance(content, str):
            st.markdown(f"**{header}:**")
            st.markdown(content)

with tab3:
    st.subheader("All Product Details")
    for header, content in st.session_state.content:
        if not ("Ranking" in header or "Best Specifications" in header):
            with st.expander(header):
                content = content.astype(str)  # <--- modification
                st.dataframe(content, width='stretch')
    for header, content in st.session_state.content:
        if "Best Specifications" in header:
            with st.expander(header):
                content = content.astype(str)  # <--- modification
                st.dataframe(content, width='stretch')

# Clear session state
st.session_state.content.clear()
st.session_state.figure.clear()


