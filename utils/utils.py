"""Contains shared data and functions"""

from pickle import load
from os import mkdir
from os.path import isdir
from scipy.stats import chi2_contingency, pearsonr, f_oneway, kruskal, spearmanr, normaltest
from numpy import array
from pandas import DataFrame

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
SUBSET_PATH: str = 'data/{}-data.csv'
SUBSET_COMP_DICTS_PATH: str = 'data/{}-comp-dicts'
SIGNIFICANT_FREQUENCIES_CSV_PATH: str = 'data/significance-frequencies-{}.csv'
ADNIMERGE_KEY: str = 'ADNIMERGE'
EXPRESSION_KEY: str = 'Gene Expression'
MRI_KEY: str = 'MRI'
TOTAL_FREQ_KEY: str = 'Total Frequency'
ADNIMERGE_FREQ_KEY: str = 'ADNIMERGE Frequency'
EXPRESSION_FREQ_KEY: str = 'Gene Expression Frequency'
MRI_FREQ_KEY: str = 'MRI Frequency'
DOMAIN_KEY: str = 'Domain'
MIN_CHISQ_FREQ: int = 5
MIN_CAT_SIZE: int = 20
NORMALITY_ALPHA: float = 0.05


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
        stat: float = nom_nom_test(list1=list1, list2=list2)
    elif type1 == NOMINAL_TYPE and type2 == NUMERIC_TYPE:
        stat: float = num_nom_test(numbers=list2, categories=list1)
    elif type2 == NOMINAL_TYPE and type1 == NUMERIC_TYPE:
        stat: float = num_nom_test(numbers=list1, categories=list2)
    elif type1 == NUMERIC_TYPE and type2 == NUMERIC_TYPE:
        stat: float = num_num_test(list1=list1, list2=list2)
    else:
        print("ERROR: Non-specified type at " + header1 + " x " + header2)
        exit(1)

    return stat


def nom_nom_test(list1: list, list2: list) -> float:
    """Runs a comparison of two nominal columns using a chi squared test if the table frequencies are high enough"""

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

    if (contig_table < MIN_CHISQ_FREQ).any().any():
        return float('inf')

    p: float = chi2_contingency(contig_table)[1]
    return p


def num_nom_test(numbers: list, categories) -> float:
    """Computes correlation between a numeric and nominal variable using ANOVA or kruskal-wallis"""

    table: list = split_numbers_by_category(numbers=numbers, categories=categories)

    not_normal: bool = False

    for group in table:
        assert len(group) >= MIN_CAT_SIZE

        if not_normal_distribution(group):
            not_normal: bool = True
            break

    if not_normal:
        p: float = kruskal(*table)[1]
    else:
        p: float = f_oneway(*table)[1]

    return p


def split_numbers_by_category(numbers: list, categories: list) -> list:
    """Splits a numerical variable by corresponding categories"""

    unique_categories: list = list(set(categories))
    table: list = []

    for c in unique_categories:
        table.append([numbers[i] for i in range(len(numbers)) if categories[i] == c])

    return table


def not_normal_distribution(data: list) -> bool:
    """Checks if a numeric variable follows a normal distribution"""

    p: float = normaltest(data)[1]

    if p < NORMALITY_ALPHA:
        return True
    else:
        return False


def num_num_test(list1: list, list2: list) -> float:
    """Computes a correlation coefficient between two numeric columns"""

    if not_normal_distribution(data=list1) or not_normal_distribution(data=list2):
        p: float = spearmanr(array(list1), array(list2))[1]
    else:
        p: float = pearsonr(array(list1), array(list2))[1]

    return p
