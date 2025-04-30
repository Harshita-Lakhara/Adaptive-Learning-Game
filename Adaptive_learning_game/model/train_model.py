import pandas as pd
import mysql.connector
import pickle
from sklearn.tree import DecisionTreeClassifier

# Connect to MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='adaptive'
)
cursor = conn.cursor()

# Fetch data
query = "SELECT username, subject, score, total_questions FROM scores"
cursor.execute(query)
rows = cursor.fetchall()
df = pd.DataFrame(rows, columns=['username', 'subject', 'score', 'total_questions'])

# Feature engineering
df['percentage'] = df['score'] / df['total_questions'] * 100

# Updated logic: Score < 3 is weak (label = 1), Score >= 3 is strong (label = 0)
df['is_weak'] = df['score'].apply(lambda x: 1 if x < 3 else 0)

# Aggregate features per user & subject
agg_df = df.groupby(['username', 'subject']).agg({
    'percentage': 'mean',
    'score': 'count',
    'is_weak': 'mean'
}).reset_index()

agg_df.rename(columns={'score': 'quiz_count', 'is_weak': 'weak_ratio'}, inplace=True)

# Label: weak if >= 50% of quizzes are weak
agg_df['label'] = agg_df['weak_ratio'].apply(lambda x: 1 if x >= 0.5 else 0)

# Train model
X = agg_df[['percentage', 'quiz_count']]
y = agg_df['label']

model = DecisionTreeClassifier()
model.fit(X, y)

# Save model and features
with open('model/ml_model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('model/feature_columns.pkl', 'wb') as f:
    pickle.dump(['percentage', 'quiz_count'], f)

# Save mapping for user-subject
agg_df[['username', 'subject', 'percentage', 'quiz_count', 'label']].to_csv("model/user_subjects.csv", index=False)

print("[✅] ML Model trained and saved.")
