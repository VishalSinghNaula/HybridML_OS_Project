
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Load and prepare data
data = pd.read_csv("thread_data.csv")
X = data.drop('label', axis=1)
y = data['label']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=8,
    class_weight='balanced',
    random_state=42
)
model.fit(X_train, y_train)

# Evaluate
print("Accuracy:", model.score(X_test, y_test))
joblib.dump(model, "thread_predictor.pkl")