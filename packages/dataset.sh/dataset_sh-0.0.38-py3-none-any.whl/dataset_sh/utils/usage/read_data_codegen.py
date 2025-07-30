def get_read_data_code(dataset_fullname, collection_name, tag=None, version=None, model=None):
    import_line = 'import dataset_sh as dsh'
    dataset_line = f'with dsh.dataset("{dataset_fullname}")'
    if tag:
        dataset_line += f'.tag("{tag}")'
    elif version:
        dataset_line += f'.version("{version}")'
    else:
        dataset_line += f'.latest()'

    dataset_line += '.open() as reader:'

    print_collections_line = '    # print(reader.collections())'
    if model:
        for_items_line = f'    for item in reader.coll("{collection_name}", model={model})'
    else:
        for_items_line = f'    for item in reader.coll("{collection_name}")'
    for_items_line_print = '        print(item)'
    for_items_line_break = '        break'

    lines = [
        import_line, dataset_line, print_collections_line, for_items_line, for_items_line_print,
        for_items_line_break]
    return '\n'.join(lines)
