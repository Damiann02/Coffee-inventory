
import streamlit as st
from streamlit import columns

from Tea_Stock_Project import color_status

st.title("Tea Inventory Dashboard")
st.write("Welcome to the tea inventory system")

import streamlit as st
import pandas as pd

# importă funcția ta din proiect
from Tea_Stock_Project import run_inventory_pipeline   # schimbă numele dacă fișierul tău se numește altfel

st.title("Tea Inventory Dashboard")

# încarcă stocul inițial
stock_df = pd.read_csv("Stock_ceaiuri.csv")       # sau fișierul tău real

# rulează pipeline-ul
final_report = run_inventory_pipeline(stock_df, "../reports")
final_report = final_report.style.map(color_status,subset = ["Status"] )

# afișează tabelul
st.dataframe(final_report)

