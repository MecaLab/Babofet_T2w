import pandas as pd


if __name__ == "__main__":
    df = pd.read_csv("table_data/sessions_to_days.csv")

    print(df.head())