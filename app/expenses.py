#!/home/mikael/.local/bin/streamlit run
import streamlit as st
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import configparser
import numpy as np
import sys


def importer(address, port, priorities, feather_file_path):
    """Downloads the Report.csv file from the HomeBudget
    app, extracts the list of expenses and saves them to a
    feather file in the data/ directory"""
    url = f"http://{address}:{port}/Report.csv"
    report = requests.get(url)
    expenses, *incomes_and_sources = report.text.split("\n\n")
    with open("/tmp/expenses.csv", "w") as expenses_csv:
        expenses_csv.write(expenses)
    with open("/tmp/expenses.csv", "r") as expenses_csv:
        expenses_pd = pd.read_csv(expenses_csv)
    # data cleaning
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
    expenses_pd["subcategory_lower"] = expenses_pd.subcategory.str.lower()
    expenses_pd = expenses_pd.merge(
        priorities, on="subcategory_lower"
    )
    expenses_pd.to_feather(feather_file_path)
    return expenses_pd


def agg_over_categories(df_org):
    """Aggregates expenses over categories"""
    pivot = pd.pivot_table(
        df_org,
        values="amount",
        columns="year",
        index="category",
        fill_value=0,
        margins=True,
        aggfunc=np.sum,
    ).iloc[:, :-1]
    pivot["Change (%)"] = (pivot.iloc[:, 1] / pivot.iloc[:, 0] - 1) * 100
    return pivot.round(0),df_org


def agg_over_subcategories(df_org, selected_subcategories):
    """Aggregates expenses over subcategories"""
    df = df_org.set_index("subcategory").loc[selected_subcategories].reset_index()
    pivot = pd.pivot_table(
        df,
        values="amount",
        columns="year",
        index="subcategory",
        fill_value=0,
        margins=True,
        aggfunc=np.sum,
    ).iloc[:, :-1]
    pivot["Change (%)"] = (pivot.iloc[:, 1] / pivot.iloc[:, 0] - 1) * 100
    return pivot.round(0),df


def agg_over_prio(df_org, selected_priorities):
    """Aggregates expenses over priorities"""
    df = df_org.set_index("priority").loc[selected_priorities].reset_index()
    pivot = pd.pivot_table(
        df,
        values="amount",
        columns="year",
        index="priority",
        fill_value=0,
        margins=True,
        aggfunc=np.sum,
    ).iloc[:, :-1]
    pivot["Change (%)"] = (pivot.iloc[:, 1] / pivot.iloc[:, 0] - 1) * 100
    return pivot.round(0),df


###################
### main script ###
###################

if __name__ == "__main__":
    try:
        config_file = sys.argv[1]
    except IndexError:
        print("Error: run 'streamlit expenses.py path-to-config.ini'")
        sys.exit(1)
    ### configs ###
    config_file = Path(config_file)
    if not config_file.exists():
        print(f"Error: {config_file} does not exist")
        sys.exit(1)
    config = configparser.ConfigParser()
    config.read(config_file)

    #############
    st.title("Expenses")

    #############
    ## sidebar ##
    #############
    host = st.sidebar.text_input("Smartphone address", config["CONFIGS"]["host"])
    port = st.sidebar.text_input("HomeBudget port")
    import_button = st.sidebar.button("Import from phone")

    #### data import ###
    expenses_feather_file = Path.joinpath(
        Path(config["CONFIGS"]["datadir"]), "expenses.feather"
    )
    if import_button:
        priorities = pd.DataFrame(
            {
                "subcategory_lower": list(config["SUBCATEGORIES"].keys()),
                "priority": list(config["SUBCATEGORIES"].values()),
            }
        )
        expenses = importer(host, port, priorities, expenses_feather_file)
        st.sidebar.info("Updated database")
    elif not expenses_feather_file.exists():
        st.info("Could not find any previous data. Please upload. ")
    else:
        expenses = pd.read_feather(expenses_feather_file)
        ####################

        ######################
        ##### side menue #####
        ######################
        today = datetime.now()
        expenses_years = list(expenses["year"].unique())
        year_index_1 = len(expenses_years) - 2
        year_index_2 = year_index_1 + 1
        last_year = int(st.sidebar.selectbox("First year", expenses_years, year_index_1))
        this_year = int(st.sidebar.selectbox("Second year", expenses_years, year_index_2))

        this_month = today.month
        current_months = range(
            1, 13#,this_month
        )  # todo: range(min_month_current_year, max_month_current_year)
        month_list = st.sidebar.multiselect(
            "Months:", current_months, default=current_months
        )

        agg_type = st.sidebar.radio(
            "Aggregate over: ", ["categories", "subcategories", "priorities"], index=0
        )

        expenses = expenses.set_index("year").loc[[last_year, this_year]].reset_index()
        expenses = expenses.set_index("month").loc[month_list].reset_index()

        # dynamic menue
        if agg_type == "subcategories":
            subcat_list = list(expenses.subcategory.unique())
            agg_list = st.sidebar.multiselect(
                "Subcategories:", subcat_list, default=subcat_list
            )
        elif agg_type == "priorities":
            prio_list = list(set(config["SUBCATEGORIES"].values()))
            agg_list = st.sidebar.multiselect(
                "Priority levels:", prio_list, default=prio_list
            )
        else:
            #agg_type == "categories":
            agg_list = None
        show_raw_data = st.sidebar.checkbox("Show original data",)
        ###########
        ## main ###
        ###########
        min_date = min(expenses.date)
        max_date = max(expenses.date)

        #### presentation ####
        st.info(
            f"Data from {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
        )

        if agg_type == "subcategories":
            out_table,raw_data = agg_over_subcategories(
                df_org=expenses, selected_subcategories=agg_list
            )
        elif agg_type == "priorities":
            out_table,raw_data = agg_over_prio(df_org=expenses, selected_priorities=agg_list)
        else:
            out_table,raw_data = agg_over_categories(df_org=expenses)
        st.table(out_table)
        if show_raw_data:
            raw_data = raw_data[["date","subcategory","amount","notes"]].round(0)
            st.dataframe(raw_data)