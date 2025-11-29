import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
MODEL_FILE = "blinkit_zepto_model.pkl"
DATA_FILE = "grocery_orders.csv"

st.set_page_config(page_title="Blinkit vs Zepto", page_icon="🛒")
st.title("Blinkit vs Zepto Predictor")

if os.path.exists(DATA_FILE):
    df_ref = pd.read_csv(DATA_FILE)
    df_ref.columns = df_ref.columns.str.strip()
else:
    st.error("CSV file missing")
    st.stop()

# Load Model
if os.path.exists(MODEL_FILE):
    try:
        model = joblib.load(MODEL_FILE)
    except Exception as e:
        st.error(f"Model Error: {e}. Please run 'python train_model.py' again.")
        st.stop()
else:
    st.warning("Model not found. Please run 'python train_model.py' in your terminal first.")
    st.stop()

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    product_input = st.text_input("Product Name", value="Milk")
    quantity = st.number_input("Quantity", min_value=1, value=1)

with col2:
    city_input = st.text_input("City", value="Mumbai")

if st.button("Predict Best Platform", use_container_width=True):
    if not product_input or not city_input:
        st.warning("Please fill in all fields.")
        st.stop()

    prod_matches = df_ref[df_ref["Product"].str.lower() == product_input.lower()]
    if not prod_matches.empty:
        est_price = prod_matches["Price"].mean()
        category = prod_matches["Category"].mode()[0]
    else:
        est_price = df_ref["Price"].median()
        category = "Unknown"

    total_amount = est_price * quantity

    city_matches = df_ref[df_ref["City"].str.lower() == city_input.lower()]
    if not city_matches.empty:
        base_time = city_matches["DeliveryTime(min)"].median()
    else:
        base_time = df_ref["DeliveryTime(min)"].median()
    
    est_time = base_time + np.random.randint(-2, 3) 

    if est_time < 15: speed = "Superfast"
    elif est_time < 30: speed = "Fast"
    else: speed = "Normal"

    input_data = pd.DataFrame([{
        "Price": est_price,
        "Quantity": quantity,
        "TotalAmount": total_amount,
        "DeliveryTime(min)": est_time,
        "Rating": 4.0, 
        "DeliverySpeed": speed,
        "Product": product_input,
        "City": city_input,
        "IsWeekend": False,
        "Category": category,
        "PaymentMode": "UPI",
        "OrderWeekday": "Wednesday"
    }])

    prediction = model.predict(input_data)[0]
    probabilities = model.predict_proba(input_data)[0]
    classes = model.classes_

    st.markdown("Results:")
    
    winner_color = "green" if prediction == "Blinkit" else "blue"
    st.markdown(f"Recommended: :{winner_color}[{prediction}]")

    st.write("Confidence:")
    for label, prob in zip(classes, probabilities):
        st.progress(prob, text=f"{label}: {prob:.1%}")

    with st.expander("See Calculation Details"):
        st.write(f"**Estimated Price:** ₹{est_price:.2f}")
        st.write(f"**Estimated Time:** {est_time} mins ({speed})")