import operator
import random

import pandas


def show_top_n(a_dict,
               id_to_class_instance=None,
               label_attr_name=None,
               n=10,
               add_rel_freq=False):
    headers = ['Item', 'Value']

    if add_rel_freq:
        headers.append('Rel Freq')
        headers.append('Cum Rel Freq')
    list_of_lists = []

    index = 0
    total = sum(a_dict.values())
    total_rel_freq = 0
    for key, value in sorted(a_dict.items(),
                             key=operator.itemgetter(1),
                             reverse=True):
        label = key
        if all([id_to_class_instance,
                label_attr_name]):
            class_instance = id_to_class_instance[key]
            label = getattr(class_instance, label_attr_name)

        one_row = [label, value]

        if add_rel_freq:
            rel_freq = (value / total) * 100
            total_rel_freq += rel_freq

            rel_freq = round(rel_freq, 2)
            rel_freq = f'{rel_freq}%'
            one_row.append(rel_freq)

            one_row.append(f'{round(total_rel_freq, 2)}%')

        list_of_lists.append(one_row)

        if index == n:
            break
        index += 1

    df = pandas.DataFrame(list_of_lists, columns=headers)

    return df.sort_values('Value', ascending=False)


def get_sample(iterable, number_of_items):

    if len(iterable) < number_of_items:
        number_of_items = len(iterable)

    the_sample = random.sample(iterable, number_of_items)

    return the_sample

example = show_top_n({'1': 3, '2': 7, '3': 3})
