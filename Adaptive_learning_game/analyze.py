# analyze.py
import mysql.connector
import pandas as pd

def fetch_scores():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='adaptive1'
        )
        query = "SELECT username, subject, score FROM scores"
        df = pd.read_sql(query, connection)
        return df

    except mysql.connector.Error as err:
        print(f"[ERROR] Database connection failed: {err}")
        return pd.DataFrame()

    finally:
        try:
            if connection.is_connected():
                connection.close()
        except:
            pass

def get_weak_subjects(username):
    df = fetch_scores()

    if df.empty:
        print("[INFO] No data fetched from database.")
        return []

    # Filter for the specific user and scores less than 4
    user_weak_df = df[(df['username'] == username) & (df['score'] < 4)]

    # Get the minimum score for each weak subject (you can change this logic if needed)
    weak_subjects = user_weak_df.groupby('subject')['score'].min().reset_index()

    return weak_subjects.to_dict(orient='records')



if __name__ == "__main__":
    # Example: replace this with dynamic username from login system
    logged_in_user = "john_doe"
    print(f"[INFO] Fetching weak subjects for {logged_in_user}...")
    result = get_weak_subjects(logged_in_user)
    print("Weak Subjects:", result)


