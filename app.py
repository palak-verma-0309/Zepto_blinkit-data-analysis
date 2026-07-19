import io
import os

import joblib
import numpy as np
import pandas as pd
import streamlit as st
from gtts import gTTS

import ai


MODEL_FILE = "blinkit_zepto_model.pkl"
DATA_FILE = "grocery_orders.csv"

st.set_page_config(
    page_title="Blinkit vs Zepto | Order Predictor",
    page_icon="🛒",
    layout="wide",
)

st.markdown(
    """
    <style>
      .stApp { background: #fbfaf7; color: #20241f; }
      .block-container { max-width: 1120px; padding-top: 3.2rem; padding-bottom: 3rem; }
      h1, h2, h3 { letter-spacing: -0.035em; }
      .eyebrow { color: #5c6b58; font-size: .78rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
      .hero { margin: .35rem 0 2rem; }
      .hero h1 { margin: 0; font-size: clamp(2.1rem, 5vw, 3.7rem); line-height: 1.02; }
      .hero p { color: #60665e; font-size: 1.05rem; margin: .65rem 0 0; }
      .result-card { background: #202b20; border-radius: 18px; color: #f8f7f2; padding: 1.5rem 1.7rem; margin-top: 1.5rem; }
      .result-card .label { color: #bcc7b7; font-size: .75rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }
      .result-card .winner { font-size: 2rem; font-weight: 750; letter-spacing: -.04em; margin-top: .1rem; }
      div[data-testid="stMetric"] { background: #f2f1ec; border: 1px solid #e5e2d9; border-radius: 12px; padding: .85rem 1rem; }
      div[data-testid="stMetricLabel"] { color: #697066; }
      div.stButton > button { background: #28663b; border: 0; border-radius: 10px; color: white; font-weight: 650; min-height: 2.8rem; }
      div.stButton > button:hover { background: #1f5130; color: white; }
      div[data-baseweb="input"] > div, div[data-baseweb="select"] > div { border-radius: 9px; }
    </style>
    """,
    unsafe_allow_html=True,
)


if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""


def play_voice_response(text):
    try:
        audio_bytes = io.BytesIO()
        gTTS(text=text, lang="en", slow=False).write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        st.audio(audio_bytes, format="audio/mp3", start_time=0)
    except Exception as error:
        st.warning(f"Couldn't generate audio: {error}")


if not os.path.exists(MODEL_FILE):
    st.error("Prediction model is missing. Add `blinkit_zepto_model.pkl` and restart the app.")
    st.stop()

model = joblib.load(MODEL_FILE)
df_ref = pd.read_csv(DATA_FILE)
df_ref.columns = df_ref.columns.str.strip()
unique_cities = sorted(df_ref["City"].dropna().unique().tolist())

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Quick-commerce order planner</div>
      <h1>Which app fits this order?</h1>
      <p>Compare the likely pick for your basket using price, quantity, delivery time, and city.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

mode = st.radio("How would you like to enter the order?", ["Enter manually", "Use voice or text"], horizontal=True)

final_product, final_quantity, final_city = "", 1, "Mumbai"
if mode == "Use voice or text":
    st.caption('Try: “I want 5 packets of Maggi in Delhi.”')
    mic_col, text_col = st.columns([1, 4], vertical_alignment="bottom")
    with mic_col:
        if st.button("🎙 Speak", use_container_width=True):
            with st.spinner("Listening…"):
                heard_text = ai.listen()
            if heard_text:
                st.session_state.voice_text = heard_text
                st.rerun()
            st.warning("No audio detected.") if not heard_text else None
    with text_col:
        user_text = st.text_input("Describe your order", value=st.session_state.voice_text, placeholder="e.g. 2 bread in Mumbai")

    if user_text:
        product, quantity, city = ai.parse_order_text(user_text, unique_cities)
        if product == "Unknown" or not product:
            st.warning("I couldn't identify the product. Try a more specific name.")
        else:
            st.success(f"Detected: {quantity} × {product} · {city}")
            final_product, final_quantity, final_city = product, quantity, city
else:
    product_col, quantity_col, city_col = st.columns([2.2, 1, 1.4])
    with product_col:
        final_product = st.text_input("Product", "Milk", placeholder="e.g. Milk")
    with quantity_col:
        final_quantity = st.number_input("Quantity", min_value=1, value=1)
    with city_col:
        final_city = st.selectbox("City", unique_cities, index=unique_cities.index("Mumbai") if "Mumbai" in unique_cities else 0)

if st.button("Compare this order", type="primary", use_container_width=True):
    if not final_product:
        st.error("Enter a product before comparing.")
        st.stop()

    product_data = df_ref[df_ref["Product"].str.lower() == final_product.lower()]
    estimated_price = product_data["Price"].mean() if not product_data.empty else df_ref["Price"].median()
    total_amount = estimated_price * final_quantity

    city_data = df_ref[df_ref["City"].str.lower() == final_city.lower()]
    base_time = city_data["DeliveryTime(min)"].median() if not city_data.empty else 20
    eta = max(1, base_time + np.random.randint(-2, 3))
    speed = "Superfast" if eta < 15 else "Fast" if eta < 30 else "Normal"

    input_df = pd.DataFrame([{
        "Price": estimated_price, "Quantity": final_quantity, "TotalAmount": total_amount,
        "DeliveryTime(min)": eta, "Rating": 4.0, "DeliverySpeed": speed,
        "Product": final_product, "City": final_city, "IsWeekend": False,
        "Category": "Unknown", "PaymentMode": "UPI", "OrderWeekday": "Friday",
    }])
    prediction = model.predict(input_df)[0]
    explanation = ai.explain_prediction(prediction, total_amount, eta, final_city)

    st.markdown(
        f'<div class="result-card"><div class="label">Recommended for this order</div><div class="winner">{prediction}</div><div style="color:#d4ddd1; margin-top:.4rem;">{explanation}</div></div>',
        unsafe_allow_html=True,
    )
    price_col, eta_col, city_result_col = st.columns(3)
    price_col.metric("Estimated basket", f"₹{total_amount:,.0f}")
    eta_col.metric("Estimated delivery", f"{eta:.0f} min")
    city_result_col.metric("Delivery area", final_city)

    with st.expander("Listen to the recommendation"):
        play_voice_response(f"The best choice is {prediction}. Estimated basket total is {total_amount:.0f} rupees. {explanation}")
