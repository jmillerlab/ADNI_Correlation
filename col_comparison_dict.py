"""Creates a column comparison dictionary, a mapping of a tuple of 2 column headers to a p-value which is the result of
a statistical test between those 2 columns. This dictionary represents and is more efficient than a comparison matrix"""

from os import popen
from pandas import DataFrame, read_csv
from pickle import dump
from time import time
from sys import argv, stdout
from multiprocessing import Pool, freeze_support
from math import ceil
from pickle import load

from utils.utils import (
	get_type, NUMERIC_TYPE, get_col_types, START_IDX_KEY, STOP_IDX_KEY, N_ROWS_KEY, compare, get_comp_key,
	ALPHAS_PATH
)

"""
Real Data:
Stop Index: 842889
Base Number Of Rows: 66

Debug Data:
Stop Index: 1049
Base Number Of Rows: 55
"""

dataset_cols: dict = {}
col_types: dict = {}
headers: list = []
PTID_COL: str = 'PTID'
CSV_DELIMINATOR: str = ','
FILTER_ALPHA = load(open(ALPHAS_PATH, 'rb'))[1]

assert type(FILTER_ALPHA) is float


def main():
	"""Main method"""

	global col_types
	global headers

	data_path, start_idx, stop_idx, n_rows, n_cores, out_dir = get_args()

	# We don't want to begin at the PTID column
	assert start_idx >= 2

	assert stop_idx > start_idx
	assert n_rows <= stop_idx - start_idx

	print('Start Column Index:', start_idx)
	print('Stop Column Index:', stop_idx)
	print('Number Of Rows:', n_rows)
	print('Number of Cores and Threads:', n_cores)

	start_time: float = time()

	# Construct the data set from the input file as a mapping from a header to its corresponding column
	df: str = get_cut_command_result(
		start_idx=start_idx, stop_idx=stop_idx, data_path=data_path
	)
	df: list = df.split('\n')

	# Separate the headers from the rest of the data frame
	headers = df[0].split(CSV_DELIMINATOR)
	df: list = df[1:]
	df.remove('')
	assert '' not in df

	# Load in the column types which will indicate whether a column is numeric or nominal
	col_types = get_col_types()

	# Construct the data set from which this process's section of the column comparison dictionary will be computed
	for i, row in enumerate(df):
		row = row.split(CSV_DELIMINATOR)

		assert len(row) == len(headers)

		# Add each value of the current row to its respective column
		for j, val in enumerate(row):
			header: str = headers[j]

			if header not in dataset_cols:
				dataset_cols[header] = []

			col: list = dataset_cols[header]

			if get_type(header=header, col_types=col_types) == NUMERIC_TYPE:
				val: float = float(val)

			col.append(val)

		# Validate that the row was added correctly to the data set's columns
		for j, header in enumerate(headers):
			if get_type(header=header, col_types=col_types) == NUMERIC_TYPE:
				assert dataset_cols[header][i] == float(row[j])
			else:
				assert dataset_cols[header][i] == row[j]

		# Free the memory usage from the current row that has been saved in the columns dictionary
		df[i] = None
		del row

	# Free the memory usage from the cut command result and ensure the dataset columns were created from it correctly
	del df
	assert len(dataset_cols) == len(headers)
	assert set(dataset_cols.keys()) == set(headers)

	print('Setup Time: {}'.format(time() - start_time))
	freeze_support()

	comparison_dict: dict = col_comparison_dict(n_rows=n_rows, n_threads=n_cores)

	with open('data/{}/{}.p'.format(out_dir, str(start_idx).zfill(7)), 'wb') as f:
		dump(comparison_dict, f)


def get_args() -> tuple:
	"""Gets the arguments for this job's section of the conceptual matrix"""

	data_path: str = argv[1]
	inputs: DataFrame = read_csv(argv[2])
	job_n: int = int(argv[3])

	assert job_n < len(inputs)

	start_idx: int = inputs.loc[job_n][START_IDX_KEY]
	stop_idx: int = inputs.loc[job_n][STOP_IDX_KEY]
	n_rows: int = inputs.loc[job_n][N_ROWS_KEY]
	n_cores: int = int(argv[4])
	out_dir: str = argv[5]

	return data_path, start_idx, stop_idx, n_rows, n_cores, out_dir


def get_cut_command_result(start_idx: int, stop_idx: int, data_path: str) -> str:
	"""Gets the portion of the data set needed for this section of the column comparison dictionary"""

	# Computation of the comparison dictionary is divided into sections, each of which is performed by its own process
	# Each section of the comparison dictionary represents a number of rows in its equivalent comparison matrix
	# The cut command will load in the section of the data set for this process
	command: str = 'cut -f {}-{} -d \',\' {}'.format(start_idx, stop_idx, data_path)
	return popen(command).read()


def col_comparison_dict(n_rows: int, n_threads: int) -> dict:
	"""Constructs the column comparison dictionary with comparisons of each column in a dataset to every other column.
	This dictionary represents the portion of a square matrix up and to the right of the diagonal, considering the
	diagonal itself is useless and everything below and to the left of it is redundant"""

	n_cols: int = len(headers)
	comparison_dict: dict = {}

	# Initialize the thread pool
	p = Pool(processes=n_threads)

	# Get the list of arguments for each thread which has its own batch of arguments
	arg_list: list = get_arg_list(n_rows=n_rows, n_cols=n_cols, n_threads=n_threads)

	start_time: float = time()

	# Compute the sub dictionary in each thread according to that thread's batch
	sub_dicts: list = p.map(compare_batch, arg_list)

	stdout.write('Time Threading: ' + str(time() - start_time))

	p.close()
	start_time: float = time()
	n_comps_skipped: int = 0

	# Add all the sub-dictionaries to the main column comparison dictionary
	for sub_dict, n_skipped in sub_dicts:
		comparison_dict.update(sub_dict)
		n_comps_skipped += n_skipped
		del sub_dict

	stdout.write('Time Stitching Batch Threads: ' + str(time() - start_time))

	# Ensure the dictionary represents the number of cells that would be in this process's section of the matrix
	n_cells_left_and_below_diagonal: int = (n_rows ** 2 - n_rows) // 2
	n_cells_in_diagonal: int = n_rows
	n_total_cells: int = n_rows * n_cols - n_cells_left_and_below_diagonal - n_cells_in_diagonal
	assert len(comparison_dict) == n_total_cells - n_comps_skipped

	return comparison_dict


def get_arg_list(n_rows: int, n_cols: int, n_threads: int) -> list:
	"""Creates the list of arguments for each thread"""

	all_indices: list = []

	for i in range(n_rows):
		# Create the row indices and the start and stop column indices for this row in the conceptual matrix
		# We say conceptual because this will result in a comparison dictionary that represents a comparison matrix
		# We do not want to include the conceptual diagonal nor the conceptual cells to the left and below it
		indices: tuple = (i, (i + 1, n_cols))
		all_indices.append(indices)

	batch_size: int = ceil(n_rows / n_threads)
	args: list = []
	start: int = 0

	for i in range(n_threads):
		# If on the last batch, only use the indices that go to the last conceptual row
		if n_rows - start < batch_size:
			stop: int = n_rows
			assert i == n_threads - 1
		else:
			stop: int = start + batch_size

		args.append(all_indices[start:stop])
		start: int = stop

	assert sum(args, []) == all_indices

	return args


def compare_batch(args: tuple) -> dict:
	"""Runs the correlation algorithm on all the columns in a thread's batch"""

	n_comps_skipped: int = 0
	result_dict: dict = {}
	batch_size: int = len(args)

	for i, (row_idx, (col_start, col_stop)) in enumerate(args):
		if i % 10 == 0:
			print('Thread Progress of Batch Beginning at {}: {:.2f}%'.format(args[0][0], i / batch_size * 100))

		for col_idx in range(col_start, col_stop):
			header1: str = headers[row_idx]
			header2: str = headers[col_idx]
			key: tuple = get_comp_key(feat1=header1, feat2=header2)
			p: float = compare(header1, header2, dataset_cols=dataset_cols, col_types=col_types)

			if p > FILTER_ALPHA:
				n_comps_skipped += 1
				continue

			assert key not in result_dict
			result_dict[key] = p

	return result_dict, n_comps_skipped


if __name__ == '__main__':
	main()
