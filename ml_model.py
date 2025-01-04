import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# load container dataset
container_dataset = pd.read_csv("./ContainerData.csv")

# defining target and features
target = ["Priority"]
features = ["Height", "Width", "Hue", "Times moved"]

selected_data = target + features
container_dataset_subset = container_dataset[selected_data]

# defining the test size
train, test = train_test_split(container_dataset_subset, test_size=0.25)

# instantiating encoder, so we can turn target ("low", "high") to binary value ("0", "1")
encoder = LabelEncoder()
# separating features from target (defined as X and Y axis)
train_X = train[features]
train_Y = train[target].to_numpy()

test_X = test[features]
test_Y = test[target].to_numpy()


train_Y_encoded = encoder.fit_transform(train_Y.ravel())
test_Y_encoded = encoder.transform(test_Y.ravel())
# instantiating the ml model
LR_model = LogisticRegression()

# training and testing the model
LR_model.fit(train_X, train_Y_encoded)
predictions = LR_model.predict(test_X)

decoded_predictions = encoder.inverse_transform(predictions)

for i in range(min(20, len(train_Y), len(decoded_predictions))):
    print(f"Actual value {i}: {train_Y[i][0]}\nPredicted value {i}: {decoded_predictions[i]}")

# Accuracy
accuracy = accuracy_score(test_Y, decoded_predictions)
print(f"\nAccuracy: {accuracy:.2f}")

# the following metrics are used to offer more insights than accuracy alone, they are performed on both "high" and "low"
# this metrics (along with accuracy) work on a % basis, so the closer to 1, or 100% (>0.75 being acceptable) the better


# Precision
precision_high = precision_score(test_Y, decoded_predictions, pos_label='high')
print(f""
      f"Precision (high): {precision_high:.2f}")
precision_low = precision_score(test_Y, decoded_predictions, pos_label='low')
print(f"Precision (low): {precision_low:.2f}")

# Recall
recall_high = recall_score(test_Y, decoded_predictions, pos_label='high')
print(f"Recall (high): {recall_high:.2f}")
recall_low = recall_score(test_Y, decoded_predictions, pos_label='low')
print(f"Recall (low): {recall_low:.2f}")

# F1-Score
f1_high = f1_score(test_Y, decoded_predictions, pos_label='high')
print(f"F1-Score (high): {f1_high:.2f}")
f1_low = f1_score(test_Y, decoded_predictions, pos_label='low')
print(f"F1-Score (low): {f1_low:.2f}")
