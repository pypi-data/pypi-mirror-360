if __name__ == '__main__':
    import pandas as pd

    # Read tmp.csv and convert to tmp.parquet
    df = pd.read_csv('tmp.csv', encoding='utf-8')
    df.to_parquet('topic_raw_data.parquet', index=False)
