import pandas as pd
import numpy as np

# Original data (ordered) for simulation purposes
data = {
    's_id': np.arange(1, 101),
    'average_exam_score': np.random.uniform(70, 82, 100).round(1),
    'ranking': np.random.randint(1, 100, 100),
    'passing_percentage': np.random.uniform(80, 95, 100).round(1),
    'top_score': np.random.uniform(93, 100, 100).round(1)
}

# Create DataFrame
df_original = pd.DataFrame(data)

# Introduce missing values randomly
df_with_missing = df_original.copy()
for col in df_with_missing.columns[1:]:  # Skip school_id
    df_with_missing.loc[df_with_missing.sample(frac=0.1).index, col] = np.nan

# Shuffle the rows to create unordered data
df_shuffled = df_with_missing.sample(frac=1).reset_index(drop=True)

# Save this as a CSV file
csv_file_path = "updated_academic_data.csv"
df_shuffled.to_csv(csv_file_path, index=False)

csv_file_path
