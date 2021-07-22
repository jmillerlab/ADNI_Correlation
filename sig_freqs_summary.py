"""Counts the number of features from each domain that were in significant comparisons above and below a threshold"""

from sys import argv
from pandas import DataFrame, Series, read_csv
from matplotlib.pyplot import subplots, savefig, title as set_title, xlabel, ylabel, legend
from os import mkdir
from os.path import join, isdir
from numpy import mean, std, min, max

from utils.utils import (
    ADNIMERGE_KEY, EXPRESSION_KEY, MRI_KEY, ADNIMERGE_FREQ_KEY, EXPRESSION_FREQ_KEY, MRI_FREQ_KEY, TOTAL_FREQ_KEY,
    DOMAIN_KEY, IDX_COL
)

SUMMARY_DIR: str = 'data/sig-freqs-summary/'
AVG_KEY: str = 'Average'
STD_KEY: str = 'Standard Deviation'
MIN_KEY: str = 'Minimum'
MAX_KEY: str = 'Maximum'


def main():
    """Main method"""

    analysis_name: str = argv[1]
    n_histogram_bins: int = int(argv[2])
    sig_freq_table_path: str = argv[3]

    if not isdir(SUMMARY_DIR):
        mkdir(SUMMARY_DIR)

    significance_frequencies: DataFrame = read_csv(sig_freq_table_path)

    print('Number Of Features That Show Up In At Least One Significance Comparison: {} | For Analysis: {}'.format(
        len(significance_frequencies), analysis_name
    ))

    save_histograms(
        significance_frequencies=significance_frequencies, n_histogram_bins=n_histogram_bins,
        analysis_name=analysis_name
    )

    for freq_key in [ADNIMERGE_FREQ_KEY, EXPRESSION_FREQ_KEY, MRI_FREQ_KEY, TOTAL_FREQ_KEY]:
        save_tables(significance_frequencies=significance_frequencies, analysis_name=analysis_name, freq_key=freq_key)


def save_histograms(significance_frequencies: DataFrame, n_histogram_bins: int, analysis_name: str):
    """Saves the histograms for the total set of frequencies and the set for each domain"""

    save_histogram(
        significance_frequencies=significance_frequencies, n_histogram_bins=n_histogram_bins,
        analysis_name=analysis_name, title='Total', break_y=True, start_break_count=8000, end_break_count=70000,
        max_count=78000
    )

    adnimerge_frequencies: DataFrame = significance_frequencies.loc[
        significance_frequencies[DOMAIN_KEY] == ADNIMERGE_KEY
        ]

    save_histogram(
        significance_frequencies=adnimerge_frequencies, n_histogram_bins=n_histogram_bins, analysis_name=analysis_name,
        title='ADNIMERGE', break_y=False
    )

    expression_frequencies: DataFrame = significance_frequencies.loc[
        significance_frequencies[DOMAIN_KEY] == EXPRESSION_KEY
    ]

    save_histogram(
        significance_frequencies=expression_frequencies, n_histogram_bins=n_histogram_bins, analysis_name=analysis_name,
        title='Gene Expression', break_y=False
    )

    mri_frequencies: DataFrame = significance_frequencies.loc[
        significance_frequencies[DOMAIN_KEY] == MRI_KEY
    ]

    save_histogram(
        significance_frequencies=mri_frequencies, n_histogram_bins=n_histogram_bins, analysis_name=analysis_name,
        title='MRI', break_y=True, start_break_count=7000, end_break_count=70000, max_count=77000
    )


def save_histogram(
    significance_frequencies: DataFrame, n_histogram_bins: int, analysis_name: str, title: str, break_y: bool,
    start_break_count: int = None, end_break_count: int = None, max_count: int = None
):
    """Saves a histogram with a broken y-axis"""

    adnimerge_frequencies: Series = significance_frequencies[ADNIMERGE_FREQ_KEY]
    expression_frequencies: Series = significance_frequencies[EXPRESSION_FREQ_KEY]
    mri_frequencies: Series = significance_frequencies[MRI_FREQ_KEY]
    frequencies: list = [adnimerge_frequencies, expression_frequencies, mri_frequencies]

    if break_y:
        broken_y_histogram(
            frequencies=frequencies, n_histogram_bins=n_histogram_bins, title=title, end_break_count=end_break_count,
            max_count=max_count, start_break_count=start_break_count
        )
    else:
        regular_histogram(frequencies=frequencies, n_histogram_bins=n_histogram_bins, title=title)

    xlabel('Comparison Frequency')
    ylabel('Number of Features')

    save_path: str = join(
        SUMMARY_DIR, 'significant-frequencies-{}-{}.png'.format(title.lower().replace(' ', ''), analysis_name)
    )

    savefig(save_path)


def broken_y_histogram(
    frequencies: list, n_histogram_bins: int, title: str, end_break_count: int, max_count: int, start_break_count: int
):
    """Creates a histogram graph with a broken y-axis"""

    fig, (ax1, ax2) = subplots(2, 1, sharex=True)
    fig.subplots_adjust(hspace=0.08)
    ax1.hist(frequencies, bins=n_histogram_bins, stacked=True, density=False)
    ax2.hist(frequencies, bins=n_histogram_bins, stacked=True, density=False)
    ax1.set_ylim(end_break_count, max_count)
    ax1.set_title(title)
    ax2.set_ylim(0, start_break_count)


def regular_histogram(frequencies: list, n_histogram_bins: int, title: str):
    """Creates a histogram without a broken y-axis"""

    _, ax = subplots()
    ax.hist(frequencies, bins=n_histogram_bins, stacked=True)
    set_title(title)
    legend({ADNIMERGE_KEY: "red", EXPRESSION_KEY: "blue", MRI_KEY: "violet"})


def save_tables(significance_frequencies: DataFrame, analysis_name: str, freq_key: str):
    """Creates the tables that complement the histograms"""

    idx_col: list = [ADNIMERGE_KEY, EXPRESSION_KEY, MRI_KEY]

    table: dict = {
        IDX_COL: idx_col,
        AVG_KEY: [0.0] * len(idx_col),
        STD_KEY: [0.0] * len(idx_col),
        MIN_KEY: [0.0] * len(idx_col),
        MAX_KEY: [0.0] * len(idx_col)
    }

    table: DataFrame = DataFrame(table)
    table: DataFrame = table.set_index(IDX_COL)

    for domain in [ADNIMERGE_KEY, EXPRESSION_KEY, MRI_KEY]:
        set_val(
            table=table, domain=domain, op=mean, header=AVG_KEY, significance_frequencies=significance_frequencies,
            freq_key=freq_key
        )

        set_val(
            table=table, domain=domain, op=std, header=STD_KEY, significance_frequencies=significance_frequencies,
            freq_key=freq_key
        )

        set_val(
            table=table, domain=domain, op=min, header=MIN_KEY, significance_frequencies=significance_frequencies,
            freq_key=freq_key
        )

        set_val(
            table=table, domain=domain, op=max, header=MAX_KEY, significance_frequencies=significance_frequencies,
            freq_key=freq_key
        )

    save_path: str = join(SUMMARY_DIR, 'basic-stats-{}-{}.csv'.format(freq_key.replace(' ', '').lower(), analysis_name))
    table.to_csv(save_path)


def set_val(
    table: DataFrame, domain: str, op: callable, header: str, significance_frequencies: DataFrame, freq_key: str
):
    """Computes a value in the table with basic stats"""

    frequencies: DataFrame = significance_frequencies.loc[
        significance_frequencies[DOMAIN_KEY] == domain
        ]

    frequencies: Series = frequencies[freq_key]
    val: float = op(frequencies)
    table[header][domain] = val


if __name__ == '__main__':
    main()
