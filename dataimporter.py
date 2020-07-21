#!/usr/bin/env python3

"""
Datum,Kategori,Underkategori,Utgift Belopp,Konto,Mottagare,Anteckningar,Device
2020-07-01,"Hus/Hyra","Datortjänster","    199.00","Gemensamt","","SvD 18-20","M Iphone 8"

"""

import io
import requests
import pandas as pd
from pathlib import Path


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
    expenses.columns = [
        "date",
        "category",
        "subcategory",
        "amount",
        "account",
        "recipient",
        "notes",
        "device",
    ]

    expenses["date"] = pd.to_datetime(expenses["date"])
    expenses["year"] = expenses["date"].dt.year
    expenses["month"] = expenses["date"].dt.month
    expenses["week"] = expenses["date"].dt.week
    expenses_pd.to_feather(Path.joinpath(Path(output_directory), "expenses.feather"))
    return expenses_pd


if __name__ == "__main__":
    expenses = pd.read_feather("expenses.feather")



    #expenses.to_feather("expenses.feather")

    print(expenses)
    categories = expenses.category.unique()
    print(list(categories))
    cat_subcat = expenses[["category", "subcategory"]].drop_duplicates()
    hus = "Hus/Hyra"
    # print(cat_subcat[cat_subcat.category==hus])
    print(cat_subcat.query("category=='Hus/Hyra'"))

    print(expenses.dtypes)
    expenses_grouped = expenses[["year","month","category", "subcategory","amount"]]
    print(expenses_grouped.groupby(["year","month","category", "subcategory"]).sum())


    #print(expenses)