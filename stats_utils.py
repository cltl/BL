import pandas
import operator

def show_top_n(a_dict,
               id_to_class_instance=None,
               label_attr_name=None,
               n=10):
    headers = ['Item', 'Count']
    list_of_lists = []

    index = 0
    for key, value in sorted(a_dict.items(),
                             key=operator.itemgetter(1),
                             reverse=True):
        label = key
        if all([id_to_class_instance,
                label_attr_name]):
            class_instance = id_to_class_instance[key]
            label = getattr(class_instance, label_attr_name)

        one_row = [label, value]
        list_of_lists.append(one_row)

        if index == n:
            break
        index += 1

    df = pandas.DataFrame(list_of_lists, columns=headers)

    return df.sort_values('Count', ascending=False)

example = show_top_n({'1': 3, '2': 7, '3' : 3})

