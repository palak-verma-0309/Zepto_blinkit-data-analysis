import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score

df = pd.read_csv("grocery_orders.csv")
df.columns = df.columns.str.strip()

features = [
    "Price", "Quantity", "TotalAmount", "DeliveryTime(min)", "Rating",
    "DeliverySpeed", "Product", "City", "IsWeekend",
    "Category", "PaymentMode", "OrderWeekday"
]

X = df[features]
y = df["Brand"].str.strip()

numeric_features = ["Price", "Quantity", "TotalAmount", "DeliveryTime(min)", "Rating"]
categorical_features = ["DeliverySpeed", "Product", "City", "IsWeekend", "Category", "PaymentMode", "OrderWeekday"]

numeric_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer([
    ("num", numeric_transformer, numeric_features),
    ("cat", categorical_transformer, categorical_features)
])

model = Pipeline([
    ("preprocess", preprocessor),
    ("rf", RandomForestClassifier(n_estimators=100, random_state=42))
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print("Model Accuracy:", acc)

joblib.dump(model, "blinkit_zepto_model.pkl")
