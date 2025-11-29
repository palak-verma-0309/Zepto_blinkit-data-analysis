import re
import speech_recognition as sr

def parse_order_text(text, known_cities):
    text = text.lower()
    
    qty_match = re.search(r'\b(\d+)\b', text)
    quantity = int(qty_match.group(1)) if qty_match else 1
    
    found_city = "Mumbai"
    for city in known_cities:
        if city.lower() in text:
            found_city = city
            break
            
    ignore_words = ["i", "want", "need", "buy", "order", "packets", "of", "in", "at", "please", "kg", "pcs", "the", "a"]
    words = text.split()
    clean_words = [w for w in words if w not in ignore_words and not w.isdigit() and w != found_city.lower()]
    product = " ".join(clean_words).title() if clean_words else "Unknown"
    
    return product, quantity, found_city

def explain_prediction(brand, total_amount, eta, city):
    reason = f"Based on historical data in {city}..."
    
    if total_amount > 500:
        reason += f" Since your order value is high ({total_amount}), {brand} is preferred for better reliability."
    else:
        reason += f" For small quick orders, {brand} tends to have better availability here."
        
    if eta < 20:
        reason += f" Also, current traffic suggests a superfast delivery ({eta} mins)."
    else:
        reason += f" Delivery load is high, but {brand} manages this timeframe efficiently."
        
    return reason

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = r.listen(source, timeout=5)
            text = r.recognize_google(audio)
            return text
        except:
            return ""