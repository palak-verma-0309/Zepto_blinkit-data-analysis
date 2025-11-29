import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import ai
from gtts import gTTS
import io

MODEL_FILE = "blinkit_zepto_model.pkl"
DATA_FILE = "grocery_orders.csv"

st.set_page_config(page_title="Blinkit vs Zepto Predictor", layout="wide")

if 'voice_text' not in st.session_state:
    st.session_state.voice_text = ""

def play_voice_response(text):
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        st.audio(audio_bytes, format='audio/mp3', start_time=0)
    except Exception as e:
        st.warning(f"Audio error: {e}")

if not os.path.exists(MODEL_FILE):
    st.error("Model missing!")
    st.stop()

model = joblib.load(MODEL_FILE)
df_ref = pd.read_csv(DATA_FILE)
df_ref.columns = df_ref.columns.str.strip()
unique_cities = df_ref["City"].unique().tolist()

st.title("Blinkit vs Zepto Predictor")

mode = st.radio("Input Mode:", ["Manual Entry", "AI Voice/Text Command"], horizontal=True)

final_product = ""
final_quantity = 1
final_city = "Mumbai"

if mode == "AI Voice/Text Command":
    st.info("Speak or Type: 'I want 5 packets of Maggi in Delhi'")
    
    col_mic, col_text = st.columns([1, 4])
    
    with col_mic:
        if st.button("Speak"):
            with st.spinner("Listening..."):
                text = ai.listen()
                if text:
                    st.session_state.voice_text = text 
                    st.rerun()
                else:
                    st.warning("No audio detected.")
    
    with col_text:
        user_text = st.text_input("Order Text:", value=st.session_state.voice_text)

    if user_text:
        p, q, c = ai.parse_order_text(user_text, unique_cities)
        
        if p == "Unknown" or not p:
            st.warning("Product name not clear. Please type it manually.")
            final_product = ""
        else:
            st.success(f"AI Detected: {q} x {p} ({c})")
            final_product, final_quantity, final_city = p, q, c
        
else:
    col1, col2, col3 = st.columns(3)
    final_product = col1.text_input("Product Name", "Milk")
    final_quantity = col2.number_input("Quantity", min_value=1, value=1)
    final_city = col3.selectbox("City", unique_cities)

if st.button("Predict & Speak", use_container_width=True):
    if not final_product:
        st.error("Please enter a valid product name.")
        st.stop()

    prod_data = df_ref[df_ref["Product"].str.lower() == final_product.lower()]
    est_price = prod_data["Price"].mean() if not prod_data.empty else df_ref["Price"].median()
    total_amt = est_price * final_quantity
    
    city_data = df_ref[df_ref["City"].str.lower() == final_city.lower()]
    base_time = city_data["DeliveryTime(min)"].median() if not city_data.empty else 20
    eta = base_time + np.random.randint(-2, 3)
    speed = "Superfast" if eta < 15 else "Fast" if eta < 30 else "Normal"

    input_df = pd.DataFrame([{
        "Price": est_price, "Quantity": final_quantity, "TotalAmount": total_amt,
        "DeliveryTime(min)": eta, "Rating": 4.0, "DeliverySpeed": speed,
        "Product": final_product, "City": final_city, "IsWeekend": False,
        "Category": "Unknown", "PaymentMode": "UPI", "OrderWeekday": "Friday"
    }])

    prediction = model.predict(input_df)[0]
    
    explanation_text = ai.explain_prediction(prediction, total_amt, eta, final_city)
    
    speech_text = f"The best choice is {prediction}. Total price is {total_amt:.0f} rupees. {explanation_text}"
    st.markdown("---")

    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric("Winner", prediction)
    with c2:
        st.metric("Total Price", f"₹{total_amt:.0f}")
    with c3:
        st.metric("Est. Time", f"{eta} mins")
    
    st.write(f"**AI Reasoning:** {explanation_text}")
    
    st.markdown("### AI Response:")
    play_voice_response(speech_text)