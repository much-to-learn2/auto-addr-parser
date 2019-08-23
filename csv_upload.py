#!/usr/bin/python3

import pandas as pd

uri = 'postgresql://postgres:postgres@localhost:5432/mydb'
df = pd.read_csv('us-500.csv')

try:
	df.to_sql('addr_dim', uri)
except ValueError:
	print('table ADDR_DIM already exists.')

