"""Contains shared data and functions"""

from pickle import load
from os import listdir, mkdir
from os.path import join, isdir
from time import time
from scipy.stats import chi2_contingency, pearsonr, f_oneway
from numpy import array
from pandas import DataFrame
from tqdm import tqdm


NUMERIC_TYPE: str = 'numeric'
NOMINAL_TYPE: str = 'nominal'
COL_TYPES_PATH: str = 'data/col-types.csv'
COL_TYPES_PICKLE_PATH: str = 'data/col-types.p'
START_IDX_KEY: str = 'Start Index'
STOP_IDX_KEY: str = 'Stop Index'
N_ROWS_KEY: str = 'Number of Rows'
ALPHAS_PATH: str = 'data/alphas.p'
INTER_COUNTS_TABLE_DIR: str = 'data/inter-counts-tables/{}'
COUNTS_TABLE_PATH: str = 'data/counts-tables/{}.csv'
ALPHA_FILTERED_DIR: str = 'data/alpha-filtered-{}'
INSIGNIFICANT_KEY: str = 'No Significance'
UNCORRECTED_ALPHA_KEY: str = 'Below Uncorrected Alpha'
CORRECTED_ALPHA_KEY: str = 'Below Bonferroni Corrected Alpha'
SUPER_ALPHA_KEY: str = 'Below Super Alpha'
MAX_SIGNIFICANCE_KEY: str = 'Maximum Significance'
IDX_COL: str = 'idx'
NUM_NUM_KEY: str = 'Numerical Numerical'
NOM_NOM_KEY: str = 'Categorical Categorical'
NUM_NOM_KEY: str = 'Numerical Categorical'
MRI_MRI_KEY: str = 'MRI MRI'
EXPRESSION_EXPRESSION_KEY: str = 'Expression Expression'
ADNIMERGE_ADNIMERGE_KEY: str = 'ADNIMERGE ADNIMERGE'
MRI_EXPRESSION_KEY: str = 'MRI Expression'
MRI_ADNIMERGE_KEY: str = 'MRI ADNIMERGE'
EXPRESSION_ADNIMERGE_KEY: str = 'Expression ADNIMERGE'
DATA_TYPE_TABLE_TYPE: str = 'data-type'
DOMAIN_TABLE_TYPE: str = 'domain'
MIN_ALPHA: float = 5e-324
BONFERRONI_ALPHA: str = 'bonferroni'
MAXIMUM_ALPHA: str = 'maximum'
SUBSET_PATH: str = 'data/{}-data.csv'
SUBSET_COMP_DICTS_PATH: str = 'data/{}-comp-dicts'
SIGNIFICANT_FREQUENCIES_CSV_PATH: str = 'data/significance-frequencies-{}.csv'
ADNIMERGE_KEY: str = 'ADNIMERGE'
EXPRESSION_KEY: str = 'Gene Expression'
MRI_KEY: str = 'MRI'
FREQ_KEY: str = 'Frequency'
DOMAIN_KEY: str = 'Domain'


def get_inter_counts_tables_dir(table_type: str, subset: str) -> str:
    """Gets the sub directory of the inter-counts-tables directory to store the inter counts tables"""

    if subset is None:
        sub_dir: str = table_type
    else:
        sub_dir: str = subset + '-' + table_type

    inter_counts_tables_dir: str = INTER_COUNTS_TABLE_DIR.format(sub_dir)

    if not isdir(inter_counts_tables_dir):
        mkdir(inter_counts_tables_dir)

    return inter_counts_tables_dir


def get_significant_alpha(alpha: str) -> float:
    """Gets the alpha for either bonferroni or maximum significance"""

    assert alpha == BONFERRONI_ALPHA or alpha == MAXIMUM_ALPHA

    if alpha == BONFERRONI_ALPHA:
        _, alpha = load(open(ALPHAS_PATH, 'rb'))
    elif alpha == MAXIMUM_ALPHA:
        alpha: float = MIN_ALPHA

    return alpha


def get_type(header: str, col_types: dict) -> str:
    """Gets the data type of a column given its header"""

    # All the MRI and expression data is numeric and thus does not need to be included in the column types
    if header not in col_types:
        return NUMERIC_TYPE

    return col_types[header]


def get_domain(feat: str, col_types: dict) -> str:
    """Gets the domain of a feature, either ADNIMERGE, Expression, or MRI"""

    if feat in col_types:
        return ADNIMERGE_KEY

    if 'MRI_' in feat:
        return MRI_KEY

    return EXPRESSION_KEY


def iterate_filtered_dicts(alpha: str, func: callable, use_p: bool = False, **kwargs) -> str:
    """Iterates through the comparisons that were filtered for a given alpha"""

    alpha: float = get_significant_alpha(alpha=alpha)
    alpha_filtered_dir: str = ALPHA_FILTERED_DIR.format(alpha)
    filtered_dicts: list = (listdir(alpha_filtered_dir))

    for filtered_dict in tqdm(filtered_dicts):
        filtered_dict: str = join(alpha_filtered_dir, filtered_dict)
        filtered_dict: dict = load(open(filtered_dict, 'rb'))

        for (feat1, feat2), p in filtered_dict.items():
            assert p < alpha

            if use_p:
                func(feat1=feat1, feat2=feat2, p=p, **kwargs)
            else:
                func(feat1=feat1, feat2=feat2, **kwargs)

    return alpha_filtered_dir


def iterate_comp_dicts(comp_dict_dir: str, idx: int, section_size: int, func: callable, **kwargs) -> tuple:
    """Iterates through the comparison dictionaries in a given section and performs a given function on them"""

    comp_dict_dir: str = join('data', comp_dict_dir)
    comp_dicts: list = listdir(comp_dict_dir)

    # Remove the files that aren't comparison dictionaries
    new_comp_dicts: list = []

    for comp_dict in comp_dicts:
        if comp_dict.endswith('.p'):
            new_comp_dicts.append(comp_dict)

    comp_dicts: list = sorted(new_comp_dicts)
    del new_comp_dicts

    n_dicts: int = len(comp_dicts)
    print('Total Number Of Comparison Dictionaries:', n_dicts)
    start_idx: int = idx * section_size

    if start_idx >= n_dicts:
        print(
            'ERROR: Start index of {} is greater than or equal to the number of comparison dictionaries {}'.format(
                start_idx, n_dicts
            )
        )
        exit(1)

    print('Start Index:', start_idx)
    stop_idx: int = min(start_idx + section_size, n_dicts)
    print('Stop Index:', stop_idx)
    comp_dicts: list = comp_dicts[start_idx:stop_idx]

    for comp_dict in comp_dicts:
        comp_dict: str = join(comp_dict_dir, comp_dict)
        print('Loading Comparison Dictionary At:', comp_dict)
        time1: float = time()
        comp_dict: dict = load(open(comp_dict, 'rb'))
        time2: float = time()
        print('Load Time: {:.2f} minutes'.format((time2 - time1) / 60))

        n_comparisons: int = len(comp_dict)
        print('Total Number Of Comparisons:', n_comparisons)
        time1: float = time()

        for (feat1, feat2), p in comp_dict.items():
            func(feat1=feat1, feat2=feat2, p=p, **kwargs)

        time2: float = time()
        print('Time Iterating Through Comparisons: {:.2f} minutes'.format((time2 - time1) / 60))

    return start_idx, stop_idx


def get_col_types() -> dict:
    """Gets the dictionary mapping a column header name to its corresponding data type"""

    return load(open(COL_TYPES_PICKLE_PATH, 'rb'))


def get_comparison_type(feat1: str, feat2: str, col_types: dict) -> str:
    """Returns the type of the comparison which is the data type of the first feature and that of the other feature"""

    type1: str = get_type(header=feat1, col_types=col_types)
    type2: str = get_type(header=feat2, col_types=col_types)

    if type1 == NOMINAL_TYPE and type2 == NOMINAL_TYPE:
        comp_type: str = NOM_NOM_KEY
    elif type1 == NUMERIC_TYPE and type2 == NUMERIC_TYPE:
        comp_type: str = NUM_NUM_KEY
    else:
        comp_type: str = NUM_NOM_KEY

    return comp_type


def get_comp_key(feat1: str, feat2: str) -> tuple:
    """Creates the key for a comparison mapping"""

    return tuple(sorted([feat1, feat2]))


def compare(header1: str, header2: str, dataset_cols: dict, col_types: dict) -> float:
    """Computes a correlation between two columns in the data set, given their headers"""

    list1: list = dataset_cols[header1]
    list2: list = dataset_cols[header2]
    assert len(list1) == len(list2)
    type1: str = get_type(header=header1, col_types=col_types)
    type2: str = get_type(header=header2, col_types=col_types)
    stat = None

    if type1 == NOMINAL_TYPE and type2 == NOMINAL_TYPE:
        stat: float = run_contingency(list1=list1, list2=list2)
    elif type1 == NOMINAL_TYPE and type2 == NUMERIC_TYPE:
        stat: float = anova(numbers=list2, categories=list1)
    elif type2 == NOMINAL_TYPE and type1 == NUMERIC_TYPE:
        stat: float = anova(numbers=list1, categories=list2)
    elif type1 == NUMERIC_TYPE and type2 == NUMERIC_TYPE:
        stat: float = run_corr(list1=list1, list2=list2)
    else:
        print("ERROR: Non-specified type at " + header1 + " x " + header2)
        exit(1)

    return stat


def run_contingency(list1: list, list2: list) -> float:
    """Runs a comparison of two nominal columns"""

    idx: list = list(set(list1))
    cols: list = list(set(list2))
    n_cols: int = len(cols)
    n_rows: int = len(idx)
    contig_table: list = [[0 for _ in range(n_cols)] for _ in range(n_rows)]

    for i in range(len(list1)):
        row_num: int = idx.index(list1[i])
        col_num: int = cols.index(list2[i])
        contig_table[row_num][col_num] += 1

    contig_table: DataFrame = DataFrame(contig_table, index=idx, columns=cols)
    p: float = chi2_contingency(contig_table)[1]
    return p


def anova(numbers: list, categories) -> float:
    """Computes a correlation using analysis of variance where one column is numeric and the other is nominal"""

    unique_categories: list = list(set(categories))
    table: list = []

    for c in unique_categories:
        table.append([numbers[i] for i in range(len(numbers)) if categories[i] == c])

    p: float = f_oneway(*table)[1]
    return p


def run_corr(list1: list, list2: list) -> float:
    """Computes a correlation coefficient between two numeric columns"""

    results: tuple = pearsonr(array(list1), array(list2))
    p: float = results[1]
    return p
