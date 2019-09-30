import pandas
import pickle
from glob import glob



def get_overview_table(input_folder, suffix="*.p", excel_path=None):
    """

    :param str input_folder: folder where BLCollection objects are stored
    :param str suffix: suffix to query, e.g., *p
    :param str excel_path: if provided, write table to excel file

    :rtype:
    :return: pandas Dataframe (one row for each table)
    """
    list_of_lists = []

    attrs = ['# of nodes with bl',
             '# of nodes without bl',
             '# of unique bls',
             'weight_value',
             'node_depth',
             'num_descendants',
             'cumulative_weight']

    headers = ['Threshold'] + attrs

    for bl_coll_path in glob(f'{input_folder}/{suffix}'):

        bl_coll = pickle.load(open(bl_coll_path, 'rb'))

        one_row = [bl_coll.subsumer_threshold]

        stats = bl_coll.stats

        for attr in attrs:
            one_row.append(stats[attr])

        list_of_lists.append(one_row)

    df = pandas.DataFrame(list_of_lists, columns=headers)

    if excel_path is not None:
        df.to_excel(excel_path, index=False)

    return df


if __name__ == '__main__':
    df = get_overview_table(input_folder='output', excel_path='output/overview.xlsx')
    print(df)