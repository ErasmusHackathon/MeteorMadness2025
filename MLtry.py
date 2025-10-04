import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt

# === Load CSV ===
file_name = "processed_meteors.csv"
df = pd.read_csv(file_name)
print("CSV loaded successfully!")
print("HEAD:\n", df.head())
print("\nINFO:\n", df.info())
print("\nDescription:\n", df.describe())

# === Preprocess ===
df['is_potentially_hazardous'] = df['is_potentially_hazardous'].astype(int)

# Check for missing values
print("\nMissing values:\n", df.isnull().sum())

# Remove extremely rare classes (less than 2 samples)
class_counts = df['is_potentially_hazardous'].value_counts()
rare_classes = class_counts[class_counts < 2].index
df = df[~df['is_potentially_hazardous'].isin(rare_classes)]

# Features and target
features = ['diameter_min_km', 'diameter_max_km', 'miss_distance_km', 'relative_velocity_kph']
X = df[features]
y = df['is_potentially_hazardous']

# Optional: Scale features (Random Forest doesn't require it, but good habit)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# === Split train/test safely with stratification ===
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y,
    test_size=0.2,
    random_state=42,
    stratify=y  # preserves class proportions
)

# === Train Random Forest with balanced class weights ===
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight='balanced'  # helps with imbalanced data
)
model.fit(X_train, y_train)

# === Evaluate model ===
y_pred = model.predict(X_test)
print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred, zero_division=0))

# === Feature importance ===
importances = model.feature_importances_
plt.bar(features, importances)
plt.title("Feature Importance")
plt.show()
print("\nFeature Importances:", dict(zip(features, importances)))

# === Save predictions ===
predictions = pd.DataFrame({
    "name": df.loc[y_test.index, "name"],
    "true_hazardous": y_test,
    "predicted_hazardous": y_pred
})
predictions.to_csv("predicted_hazardous_asteroids.csv", index=False)
print("\nPredictions saved to predicted_hazardous_asteroids.csv")
