import os
import time
import logging
import sys
import traceback

import pandas as pd

from browser import BrowserSession
import data_map
from db import Connection
from mailer import notify


logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S%p",
)


def create_df(filename):
    df = pd.read_csv(filename, sep="\t")
    df.rename(columns=data_map.column_names, inplace=True)
    return df


def read_logs(filename):
    with open(filename) as f:
        return f.read()


def insert_table(df, tablename):
    df_len = len(df.index)
    conn = Connection()
    conn.insert_into(tablename, df)
    logging.info(f"Loaded {df_len} students into {tablename} table")


def main():
    try:
        with BrowserSession() as b:
            b.search_students()
            b.quick_export_gpa()

        df = create_df("student.export.text")
        insert_table(df, "PS_GPA")

        success_message = read_logs("app.log")
        notify(success_message=success_message)
    except Exception as e:
        logging.error(e)
        stack_trace = traceback.format_exc()
        log_info = read_logs("app.log")
        error_message = f"{log_info}\n\n{stack_trace}"
        notify(error=True, error_message=error_message)


if __name__ == "__main__":
    main()