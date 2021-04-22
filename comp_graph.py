"""Creates a graph for a comparisons based on the data types of the features being compared"""

from sys import argv
from pandas import DataFrame, read_csv, Series, unique
from matplotlib.pyplot import subplots, savefig, setp
from os import mkdir
from os.path import isdir, join

from utils import (
    get_col_types, NUM_NUM_KEY, NUM_NOM_KEY, NOM_NOM_KEY, get_comparison_type, get_type, NOMINAL_TYPE,
    split_numbers_by_category
)

COMP_GRAPHS_DIR: str = 'data/comp-graphs'


def main():
    """Main method"""

    feat1: str = argv[1]
    feat2: str = argv[2]
    data_path: str = argv[3]

    if not isdir(COMP_GRAPHS_DIR):
        mkdir(COMP_GRAPHS_DIR)

    feat1: str = feat1.upper()
    feat2: str = feat2.upper()
    comparison_type: str = get_comparison_type(feat1=feat1, feat2=feat2, col_types=get_col_types())
    cols: DataFrame = read_csv(data_path, usecols=[feat1, feat2])
    col1: Series = cols[feat1]
    col2: Series = cols[feat2]

    if comparison_type == NUM_NUM_KEY:
        num_num_plot(col1=col1, col2=col2)
    elif comparison_type == NUM_NOM_KEY:
        assert get_type(feat1, get_col_types()) == NOMINAL_TYPE
        num_nom_plot(col1=col1, col2=col2)
    elif comparison_type == NOM_NOM_KEY:
        nom_nom_plot(col1=col1, col2=col2)

    save_path: str = join(COMP_GRAPHS_DIR, '{}-{}'.format(feat1, feat2))
    savefig(save_path)


def num_num_plot(col1: Series, col2: Series):
    """Creates a graph for a numeric to numeric comparison"""
    pass


def num_nom_plot(col1: Series, col2: Series):
    """Creates a graph for a numeric to nominal comparison"""

    categories: list = sorted(unique(col1))
    split_by_category: list = split_numbers_by_category(numbers=list(col2), categories=list(col1))

    _, ax = subplots()
    ax.violinplot(split_by_category, showmeans=True, showextrema=True, showmedians=True)
    xticks: list = list(range(1, len(categories) + 1))
    setp(ax, xticks=xticks, xticklabels=['Cat' + str(x) for x in xticks])


def nom_nom_plot(col1: Series, col2: Series):
    """Creates a graph for a nominal to nominal comparison"""
    pass


if __name__ == '__main__':
    main()
