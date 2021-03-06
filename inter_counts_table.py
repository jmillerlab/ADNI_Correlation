"""Creates a table with counts of the comparisons with p-values that reach various significance levels"""

from sys import argv
from os.path import join
from pickle import load
from pandas import DataFrame

from utils.utils import (
    ALPHAS_PATH, CORRECTED_ALPHA_KEY, SUPER_ALPHA_KEY, MAX_SIGNIFICANCE_KEY, get_col_types, IDX_COL,
    get_comparison_type, NUM_NUM_KEY, NOM_NOM_KEY, NUM_NOM_KEY, MRI_MRI_KEY, EXPRESSION_EXPRESSION_KEY,
    ADNIMERGE_ADNIMERGE_KEY, MRI_EXPRESSION_KEY, MRI_ADNIMERGE_KEY, EXPRESSION_ADNIMERGE_KEY, DATA_TYPE_TABLE_TYPE,
    DOMAIN_TABLE_TYPE, MIN_ALPHA, get_inter_counts_tables_dir, get_domain, ADNIMERGE_KEY, EXPRESSION_KEY, MRI_KEY
)

from utils.iterate_comp_dicts import IterByIdx

TOTAL_KEY: str = 'Total'


def main():
    """Main method"""

    comp_dict_dir: str = argv[1]
    super_alpha: float = float(argv[2])
    idx: int = int(argv[3])
    section_size: int = int(argv[4])
    table_type: str = argv[5]
    subset: str = argv[6] if len(argv) == 7 else None

    table: DataFrame = make_table(table_type=table_type)

    assert table is not None

    _, corrected_alpha = load(open(ALPHAS_PATH, 'rb'))
    col_types: dict = get_col_types()

    comp_dict_iter: IterByIdx = IterByIdx(
        comp_dict_dir=comp_dict_dir, func=count_comparisons, idx=idx, section_size=section_size, col_types=col_types,
        table=table, super_alpha=super_alpha, corrected_alpha=corrected_alpha, table_type=table_type
    )

    start_idx: int = comp_dict_iter.start_idx
    stop_idx: int = comp_dict_iter.stop_idx
    comp_dict_iter()
    print(table)
    inter_counts_tables_dir: str = get_inter_counts_tables_dir(table_type=table_type, subset=subset)
    counts_table_path: str = join(inter_counts_tables_dir, '{}-{}.csv'.format(start_idx, stop_idx))
    print(counts_table_path)
    table.to_csv(counts_table_path)


def make_table(table_type: str) -> DataFrame:
    """Creates the counts table of the given type"""

    if table_type == DATA_TYPE_TABLE_TYPE:
        idx_col: list = [NUM_NUM_KEY, NOM_NOM_KEY, NUM_NOM_KEY]
    elif table_type == DOMAIN_TABLE_TYPE:
        idx_col: list = [
            MRI_MRI_KEY, EXPRESSION_EXPRESSION_KEY, ADNIMERGE_ADNIMERGE_KEY, MRI_EXPRESSION_KEY, MRI_ADNIMERGE_KEY,
            EXPRESSION_ADNIMERGE_KEY
        ]
    else:
        return None

    idx_col += [TOTAL_KEY]
    empty_col: list = [0] * len(idx_col)

    table: DataFrame = DataFrame(
        {
            IDX_COL: idx_col,
            CORRECTED_ALPHA_KEY: empty_col,
            SUPER_ALPHA_KEY: empty_col,
            MAX_SIGNIFICANCE_KEY: empty_col,
            TOTAL_KEY: empty_col
        }
    )

    table: DataFrame = table.set_index(IDX_COL)
    return table


def count_comparisons(
    feat1: str, feat2: str, p: float, col_types: dict, table: DataFrame, super_alpha: float, corrected_alpha: float,
    table_type: str
):
    """Determines the type of comparison and the alpha it is lower than and updates the counts table accordingly"""

    if table_type == DATA_TYPE_TABLE_TYPE:
        row_key: str = get_comparison_type(feat1=feat1, feat2=feat2, col_types=col_types)
    else:
        row_key: str = get_comparison_domains(feat1=feat1, feat2=feat2, col_types=col_types)

    if p < MIN_ALPHA:
        col_key: str = MAX_SIGNIFICANCE_KEY
    elif p < super_alpha:
        col_key: str = SUPER_ALPHA_KEY
    else:
        assert p <= corrected_alpha

        col_key: str = CORRECTED_ALPHA_KEY

    table[col_key][row_key] += 1
    table[TOTAL_KEY][row_key] += 1
    table[col_key][TOTAL_KEY] += 1
    table[TOTAL_KEY][TOTAL_KEY] += 1


def get_comparison_domains(feat1: str, feat2: str, col_types: dict) -> str:
    """Indicates which domains the two features of a comparison come from"""

    domain1: str = get_domain(feat=feat1, col_types=col_types)
    domain2: str = get_domain(feat=feat2, col_types=col_types)

    if domain1 == MRI_KEY and domain2 == MRI_KEY:
        return MRI_MRI_KEY

    if domain1 == EXPRESSION_KEY and domain2 == EXPRESSION_KEY:
        return EXPRESSION_EXPRESSION_KEY

    if domain1 == ADNIMERGE_KEY and domain2 == ADNIMERGE_KEY:
        return ADNIMERGE_ADNIMERGE_KEY

    if (domain1 == MRI_KEY and domain2 == EXPRESSION_KEY) or (domain1 == EXPRESSION_KEY and domain2 == MRI_KEY):
        return MRI_EXPRESSION_KEY

    if (domain1 == MRI_KEY and domain2 == ADNIMERGE_KEY) or (domain1 == ADNIMERGE_KEY and domain2 == MRI_KEY):
        return MRI_ADNIMERGE_KEY

    assert (domain1 == EXPRESSION_KEY and domain2 == ADNIMERGE_KEY) or\
           (domain1 == ADNIMERGE_KEY and domain2 == EXPRESSION_KEY)

    return EXPRESSION_ADNIMERGE_KEY


if __name__ == '__main__':
    main()
