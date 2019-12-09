import pandas
import pickle
from glob import glob
import random



def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def get_overview_table(input_folder,
                       suffix="*.p",
                       only_average=True,
                       excel_path=None,
                       new_headers=None):
    """

    :param str input_folder: folder where BLCollection objects are stored
    :param str suffix: suffix to query, e.g., *p
    :param bool only_average: if True, only show average, else also minimum and maximum
    :param str excel_path: if provided, write table to excel file

    :rtype:
    :return: pandas Dataframe (one row for each table)
    """
    list_of_lists = []

    attrs = ['# of nodes with bl',
             #'# of nodes without bl',
             '# of unique bls',
             #'weight_value',
             'node_depth',
             'num_descendants',
             'cumulative_weight']

    headers = ['TH'] + attrs

    for bl_coll_path in glob(f'{input_folder}/{suffix}'):

        bl_coll = pickle.load(open(bl_coll_path, 'rb'))

        one_row = [bl_coll.subsumer_threshold]

        bl_coll.stats = bl_coll.get_stats()
        stats = bl_coll.stats

        for attr in attrs:

            value = stats[attr]

            if type(value) == int:
                stat_string = value
            elif type(value) == tuple:
                minimum, mean, maximum = stats[attr]
                if only_average:
                    stat_string = mean
                else:
                    stat_string = f'mean: {mean} (min: {minimum}, max: {maximum})'

            one_row.append(stat_string)

        list_of_lists.append(one_row)

    if new_headers:
        headers = ['TH'] + new_headers
    df = pandas.DataFrame(list_of_lists, columns=headers)

    if excel_path is not None:
        df.to_excel(excel_path, index=False)

    return df.sort_values('TH')


def get_sample(iterable, number_of_items):

    if len(iterable) < number_of_items:
        number_of_items = len(iterable)

    the_sample = random.sample(iterable, number_of_items)

    return the_sample

if __name__ == '__main__':
    new_headers = ['# of BL',
                   '# of unique BL',
                   'Avg Depth',
                   'Avg Desc',
                   'Avg Cum Freq']
    df = get_overview_table(input_folder='output',
                            suffix="*.p",
                            new_headers=new_headers)

    print(df.to_latex(index=False))