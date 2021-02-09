"""Combines all the intermediate counts tables into one"""

from os import listdir
from os.path import join
from pandas import read_csv, DataFrame
from sys import argv

from utils import IDX_COL, COUNTS_TABLE_PATH, get_inter_counts_tables_dir


def main():
    """Main method"""

    table_type: str = argv[1]
    subset: str = argv[2] if len(argv) == 3 else None

    inter_counts_table_dir: str = get_inter_counts_tables_dir(table_type=table_type, subset=subset)
    inter_counts_tables: list = listdir(inter_counts_table_dir)
    counts_table: DataFrame = None

    for inter_counts_table in inter_counts_tables:
        assert inter_counts_table.endswith('.csv')

        inter_counts_table: str = join(inter_counts_table_dir, inter_counts_table)
        inter_counts_table: DataFrame = read_csv(inter_counts_table, index_col=IDX_COL)

        if counts_table is None:
            counts_table: DataFrame = inter_counts_table
        else:
            counts_table: DataFrame = counts_table + inter_counts_table

    print(counts_table)

    if subset is None:
        table_name: str = table_type
    else:
        table_name: str = subset + '-' + table_type

    counts_table_path: str = COUNTS_TABLE_PATH.format(table_name)
    counts_table.to_csv(counts_table_path)


if __name__ == '__main__':
    main()
