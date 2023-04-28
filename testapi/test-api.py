from fastapi import FastAPI
from pyspark.sql import SparkSession
from sklearn.metrics.pairwise import cosine_similarity
import uvicorn
import numpy as np

app = FastAPI()

WAREHOUSE_PATH = "/opt/warehouse"

# Load TF-IDF matrix from Parquet file
# spark = SparkSession.builder \
#     .appName("RestAPI: Load TF-IDF matrix from Parquet") \
#     .getOrCreate()

spark = SparkSession.builder \
        .appName("RestAPI: Load TF-IDF matrix from Parquet") \
        .master("spark://spark-master:7077") \
        .config("spark.executor.instances", 1) \
        .config("spark.cores.max", 2) \
        .config("spark.sql.warehouse.dir", WAREHOUSE_PATH) \
        .getOrCreate()

tfidf_df = spark.read.parquet(WAREHOUSE_PATH)

# Convert TF-IDF matrix to Pandas DataFrame for easier manipulation
tfidf_pd = tfidf_df.toPandas()

# http://localhost:8000/api/v1/accounts/
@app.get("/api/v1/accounts/")
def get_accounts():
    accounts = tfidf_pd[['username', 'id']].to_dict(orient='records')
    return accounts

# http://localhost:8000/api/v1/tf-idf/user-ids/109429260801289174
@app.get("/api/v1/tf-idf/user-ids/{user_id}")
def get_tfidf_for_user(user_id: str):
    target_row = tfidf_pd.loc[tfidf_pd['id'] == user_id]
    if target_row.empty:
        return {}
    vocabulary = target_row['filtered'].values[0]
    tfidf_values = target_row['tf_idf'].values[0]
    tfidf_dict = dict(zip(vocabulary, tfidf_values))
    return tfidf_dict

# http://localhost:8000/api/v1/tf-idf/user-ids/109429260801289174/neighbors
@app.get("/api/v1/tf-idf/user-ids/{user_id}/neighbors")
def get_nearest_neighbors(user_id: str, k: int = 10):
    target_row = tfidf_pd.loc[tfidf_pd['id'] == user_id]
    target_tfidf = target_row['tf_idf'].values[0]
    target_tfidf_array = np.array(target_tfidf).reshape(1, -1)
    all_tfidf_matrix = np.vstack(tfidf_pd['tf_idf'].values)
    cosine_distances = cosine_similarity(target_tfidf_array, all_tfidf_matrix)
    neighbor_ids = tfidf_pd.loc[np.argsort(cosine_distances.squeeze())[-k:], 'id'].values
    return neighbor_ids.tolist()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)