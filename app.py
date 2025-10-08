import streamlit as st
import pandas as pd

# ===============================
# 1️⃣ Load Dataset from GitHub
# ===============================
DATA_URL = "https://raw.githubusercontent.com/AnuragPhatak/smartphones_dataset_cleanning/main/smartphones_new.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    df.columns = [c.strip().lower() for c in df.columns]

    # --- Create brand column from model ---
    df["brand"] = df["model"].apply(lambda x: str(x).split()[0] if isinstance(x, str) else None)

    # --- Clean numeric values ---
    df["price"] = df["price"].replace('[₹,]', '', regex=True).astype(float)
    df["ram"] = df["ram"].str.extract('(\d+)').astype(float)
    df["battery"] = df["battery"].str.extract('(\d+)').astype(float)

    return df

df = load_data()

# ===============================
# 2️⃣ App Layout
# ===============================
st.set_page_config(page_title="AI-Powered Mobile Recommender", layout="centered")

st.title("📱 SmartPhone Recommender (Agentic AI Concept)")
st.markdown("""
Welcome to the **AI-based Mobile Recommendation System**!  
Describe your needs or select your preferences to get top matching phones.
""")

# ===============================
# 3️⃣ User Inputs
# ===============================
st.subheader("🎯 Tell us your needs")

user_text = st.text_input("Type your requirement (e.g., 'I need a gaming phone under 20000 with good battery')")

price_range = st.slider("💰 Budget (in ₹)", 5000, 100000, (10000, 30000))
priority = st.selectbox("🎮 Main Priority", ["Performance", "Camera", "Battery", "Display", "Balanced"])
brand_pref = st.multiselect("🏷️ Preferred Brands", sorted(df["brand"].dropna().unique().tolist()))

# ===============================
# 4️⃣ Agentic Scoring Logic
# ===============================
def score_phone(row, priority, budget_min, budget_max):
    score = 0

    # Budget Agent
    if budget_min <= row["price"] <= budget_max:
        score += 1.0
    else:
        score -= 0.5  # penalty if outside range

    # Performance Agent (RAM)
    if not pd.isna(row["ram"]):
        score += (row["ram"] / df["ram"].max()) * 2

    # Battery Agent
    if not pd.isna(row["battery"]):
        score += (row["battery"] / df["battery"].max())

    # Camera Agent
    if "camera" in row and isinstance(row["camera"], str):
        try:
            cam_vals = [float(c.split('MP')[0].strip()) for c in row["camera"].split('+')]
            cam_val = sum(cam_vals) / len(cam_vals)
            score += cam_val / 100
        except:
            pass

    # Adjust based on user priority
    if priority == "Performance":
        score *= 1.2
    elif priority == "Camera":
        score *= 1.1
    elif priority == "Battery":
        score *= 1.15

    return score

# ===============================
# 5️⃣ Recommendation Function
# ===============================
def recommend(df, priority, price_range, brand_pref):
    df["score"] = df.apply(lambda x: score_phone(x, priority, price_range[0], price_range[1]), axis=1)

    # Filter by selected brands if any
    if brand_pref:
        df = df[df["brand"].isin(brand_pref)]

    top_df = df.sort_values(by="score", ascending=False).head(3)
    return top_df[["brand", "model", "price", "ram", "battery", "camera", "score"]]

# ===============================
# 6️⃣ Display Recommendations
# ===============================
if st.button("🔍 Find My Phone"):
    with st.spinner("Analyzing your preferences..."):
        recommendations = recommend(df.copy(), priority, price_range, brand_pref)

        if not recommendations.empty:
            st.success("Here are your top recommended phones:")
            st.dataframe(recommendations.reset_index(drop=True))

            for _, row in recommendations.iterrows():
                st.markdown(f"""
                **{row['brand']} {row['model']}**  
                💰 ₹{int(row['price'])}  
                ⚡ RAM: {int(row['ram'])} GB | 🔋 Battery: {int(row['battery'])} mAh | 📸 Camera: {row['camera']}  
                ⭐ Score: {round(row['score'],2)}
                """)
        else:
            st.warning("No phones found matching your preferences. Try adjusting filters.")

# ===============================
# 7️⃣ About Section
# ===============================
st.markdown("---")
st.markdown("""
**About this Project:**  
This app demonstrates an *Agentic AI* approach for personalized product recommendations.  
Different “agents” (Budget, Performance, Battery, Camera) evaluate products independently  
and collaborate to produce a final ranked result.  

Built using **Streamlit + Pandas**, powered by the *Smartphones Dataset from GitHub*.  
""")
