import streamlit as st
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime


def importer(address, port, output_directory="."):
    # download csv-file
    # split file
    # read expenses as pandas file
    # clean up data
    # create feather file
    url = f"http://{address}:{port}/Report.csv"
    report = requests.get(url)
    expenses, *incomes_and_sources = report.text.split("\n\n")
    with open("/tmp/expenses.csv", "w") as expenses_csv:
        expenses_csv.write(expenses)
    with open("/tmp/expenses.csv", "r") as expenses_csv:
        expenses_pd = pd.read_csv(expenses_csv)
    #data cleaning
    expenses_pd.columns = [
        "date",
        "category",
        "subcategory",
        "amount",
        "account",
        "recipient",
        "notes",
        "device",
    ]

    expenses_pd["date"] = pd.to_datetime(expenses_pd["date"])
    expenses_pd["year"] = expenses_pd["date"].dt.year
    expenses_pd["month"] = expenses_pd["date"].dt.month
    expenses_pd["week"] = expenses_pd["date"].dt.week
    expenses_pd.to_feather(Path.joinpath(Path(output_directory), "expenses.feather"))
    return expenses_pd




###################
### main script ###
###################

st.title("Expenses")

#############
## sidebar ##
#############

port = st.sidebar.text_input("Host port")
import_button = st.sidebar.button("Import")

if import_button:
    expenses = importer("woland.moutakis.name",port)
    #import_button = st.sidebar.button("Import again")
else:
    expenses = pd.read_feather("expenses.feather")

categories = ["ALL"] + list(expenses.category.unique())

chosen_category = st.sidebar.selectbox("Choose a category",
                                       categories)

aggregate_over = st.sidebar.radio("Aggregate over",["years","months"])

###########
## main ###
###########
today = datetime.now()
this_year = today.year
last_year = this_year-1
this_month = today.month

expenses = expenses.query(f"year>={last_year}").query(f"month<{this_month}")
min_date = min(expenses.date)
max_date = max(expenses.date)

if chosen_category!="ALL":
    expenses = expenses.query(f"category=='{chosen_category}'")

if aggregate_over=="years":
    expenses_grouped = expenses[["year", "category", "subcategory", "amount"]]
    totals = expenses_grouped.groupby(["year", "category", "subcategory"]).sum().round(0)
else:
    expenses_grouped = expenses[["year", "month", "category", "subcategory", "amount"]]
    totals = expenses_grouped.groupby(["year", "month","category", "subcategory"]).sum().round(0)




totals2 = totals.unstack("year",fill_value=0)

#print(totals2.dtypes)
#print(totals2.diff(axis=1))



#### presentation ####
st.info(f"Data from {min_date} to {max_date}")
st.dataframe(totals2)