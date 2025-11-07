import pandas as pd

y_train = pd.read_csv("y_train.csv").squeeze()
print(y_train.value_counts())
