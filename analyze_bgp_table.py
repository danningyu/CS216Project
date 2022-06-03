import pandas as pd

df = pd.read_csv("bgptable.csv", names=['prefix', 'mask', 'next_hop'])

df.info()

print(df['next_hop'].nunique())
