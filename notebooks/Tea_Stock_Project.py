import pandas as pd
import numpy as np
import pdfplumber
import os
import streamlit

stock_df = pd.read_csv("stock_ceaiuri.csv")
stock_df.head(5)

def stock_status(row):
    if row['Stoc'] <= 0:
        return "CRITIC"
    elif row['Stoc'] <= row['Prag_minim']:
        return "LOW"
    else:
        return "OK"

def color_status(val):
    if val == "CRITIC":
        return "background-color: #ff4d4d"   # roșu
    elif val == "LOW":
        return "background-color: #ffd24d"   # galben
    elif val == "OK":
        return "background-color: #85e085"   # verde

def reset_stock(row , value = 5):
    row['Stoc'] = value
    return row["Stoc"]

def extract_tea_sales(pdf_path):
    all_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split("\n")
            all_lines.extend(lines)

    tea_sales = []
    for line in all_lines:
        if '100 G Buc' in line:
            parts = line.split()
            
         # găsim poziția unde apare '100'
            idx_100 = parts.index('100')
         # numele produsului = cuvintele dintre 1 și '100'
            name = ' '.join(parts[1:idx_100])
            
        # cantitatea e după 'Buc'
            qty = parts[parts.index("Buc")+1]
            qty=int(float(qty))
            
            tea_sales.append((name,qty))
    sales_df = pd.DataFrame(tea_sales, columns=["Produs", "Vandut"])
    return sales_df


# In[73]:


def load_all_sales(report_folder):
    all_sales = []
    for file in os.listdir(report_folder):
        if file.lower().endswith('.pdf'):
            path = '../reports/' + file
            date = file.split(" ")[-1].replace('.pdf',"")
            
            sales = extract_tea_sales(path)
            sales['Data'] = date
            
            all_sales.append(sales)
    all_sales = pd.concat(all_sales, ignore_index=True)
    return all_sales

all_sales = load_all_sales('../reports')


def aggregate_sales(all_sales):
    
    all_sales= (all_sales.groupby('Produs')['Vandut'].sum().reset_index())
    all_sales['Produs'] = all_sales['Produs'].str.lower()
    return all_sales

def update_inventory(stock_df,all_sales):
    stock_df['Produs'] = stock_df['Produs'].str.lower()
    merged = stock_df.merge(all_sales,on = 'Produs' , how = "left")
    merged['Vandut'] = merged['Vandut'].fillna(0).astype(int)
    merged['Stoc'] = merged['Stoc'] - merged['Vandut']
    merged['Status'] = merged.apply(stock_status, axis = 1)
    return merged


#update_inventory(stock_df=stock_df,all_sales=all_sales)

def run_inventory_pipeline(stock_df,report_folder):
    all_sales = load_all_sales(report_folder)
    sales_total = aggregate_sales(all_sales)
    updated_stock = update_inventory(stock_df , sales_total)
    updated_stock['Status'] = updated_stock.apply(stock_status,axis=1)
    return updated_stock

final_report = run_inventory_pipeline(stock_df,'../reports')
final_report.to_csv("inventory_report.csv", index=False)