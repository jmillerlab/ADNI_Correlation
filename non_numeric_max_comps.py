"""Creates a CSV containing the non numeric-numeric comparisons of maximum significance"""

from pandas import DataFrame

from utils import NUM_NUM_KEY, get_comp_key, iterate_filtered_dicts, get_comparison_type, get_col_types, MAXIMUM_ALPHA

FEAT1_KEY: str = 'Feature 1'
FEAT2_KEY: str = 'Feature 2'


def main():
    """Main method"""

    comps: list = []
    col_types: dict = get_col_types()
    iterate_filtered_dicts(alpha=MAXIMUM_ALPHA, func=add_non_numeric_comp, col_types=col_types, comps=comps)
    print('Number Of Non Numeric-Numeric Maximally Significant Comparisons:', len(comps))

    table: DataFrame = DataFrame(columns=[FEAT1_KEY, FEAT2_KEY])

    for feat1, feat2 in comps:
        row: dict = {
            FEAT1_KEY: feat1,
            FEAT2_KEY: feat2,
        }
        table: DataFrame = table.append(row, ignore_index=True)

    table_path: str = 'data/non-numeric-max-comps.csv'
    table.to_csv(table_path, index=False)


def add_non_numeric_comp(feat1: str, feat2: str, col_types: dict, comps: list):
    """Conditionally adds a comparison if it is not a numeric-numeric type"""

    comp_type: str = get_comparison_type(feat1=feat1, feat2=feat2, col_types=col_types)

    if comp_type != NUM_NUM_KEY:
        key: tuple = get_comp_key(feat1=feat1, feat2=feat2)
        comps.append(key)


if __name__ == '__main__':
    main()
