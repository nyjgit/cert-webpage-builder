from data_loader import load_json_data
import os


def create_table_of_IDs(cert_data: dict, subject_list):
    # desired result (example):
    # [['b5cd5d58f52a', 'ec4dd82ae391', 'ec4dd82ae391', 'ec4dd82ae391', 'af44e522baea', '3fe39b08566a'],
    #  ['d56302cf909d', '38f3195d8e12', '8b6b6aef7e7f',        0      , '22bf915fb77b', '28af076388fa'],
    #  ['c982ccd03f72',      None     , 'a4e087750081', 'a4e087750081', 'fd82262e7de5', '5f1af6b4172d'],
    #  ['aa7ca360c0c5',      None     ,      None     ,      None     , 'e2da90c7e22d',      None     ],
    #  [     None     ,      None     ,      None     ,      None     , '3baef89032e9',      None     ]]
    max_row_index = 0
    for item in cert_data.values():
        max_row_index = max(max_row_index, item["rowIndex"])

    table_of_IDs = []
    for row_index in range(max_row_index+1):
        row = []
        for subject in subject_list:
            something_found = False         # for each subject we are checking if there is an item which has that subject with a matching row index
            for item_id, item in cert_data.items():
                for cert_subject in item["subjects"]:
                    if cert_subject == subject and item["rowIndex"] == row_index:
                        row.append(item_id)
                        something_found = True
            if not something_found:
                row.append(0)
        table_of_IDs.append(row)

    for column_index in range(len(subject_list)):  # replacing the last contiguous block of empty (0) cells in each column with None
        for row in reversed(table_of_IDs):
            if row[column_index] != 0:
                break
            
            row[column_index] = None
    
    return table_of_IDs


def find_indent(html_content: str):
    body_tag_pos = html_content.find("<body")
    table_tag_pos = html_content.find("<table")

    newline_pos_before_body = html_content[:body_tag_pos].rfind("\n")
    newline_pos_before_table = html_content[:table_tag_pos].rfind("\n")

    proper_indent_before_body = not html_content[newline_pos_before_body:body_tag_pos].strip()
    proper_indent_before_table = not html_content[newline_pos_before_table:table_tag_pos].strip()

    if newline_pos_before_table == -1 or not proper_indent_before_table:
        newline = False
        indent = 0
        table_indent_level = 0
        return newline, indent, table_indent_level
    
    newline = True
    
    body_indent = html_content[newline_pos_before_body:body_tag_pos].count(" ")
    table_indent = html_content[newline_pos_before_table:table_tag_pos].count(" ")

    if newline_pos_before_body == -1 or not proper_indent_before_body:
        indent = table_indent // 2      # Because of <div class="table-container">, <table> is indented 2 levels more than <body>.
    else:
        indent = (table_indent - body_indent) // 2

    table_indent_level = table_indent//indent if indent != 0 else 0

    return newline, indent, table_indent_level


def get_html_table_context(filename):
    with open(filename, "r", encoding="utf-8") as input_html:
        input_html_content = input_html.read()

    newline, indent_spaces, table_indent_level = find_indent(input_html_content)

    content_before_table = input_html_content[:input_html_content.find("<table>")]
    content_after_table = input_html_content[input_html_content.find("</table>")+8:]

    return newline, indent_spaces, content_before_table, table_indent_level, content_after_table


def create_indent_function(newline: bool, indent_spaces: int, table_indent_level: int):
    def get_indentation(indent_level: int):
        return newline*"\n" + (table_indent_level + indent_level) * indent_spaces*" "
    return get_indentation


def build_table_header(svg_data: dict, all_subjects_ordered: dict, get_indentation):
    table_header = [get_indentation(1) + "<thead>"]
    table_header.append(get_indentation(2) + "<tr>")
    for header, subject in all_subjects_ordered.items():
        table_header.append(get_indentation(3) + '<th>')

        if subject in svg_data:
            table_header.append(get_indentation(4) + '<div class="svg-container">')
            for url in svg_data[subject]["URLs"]:
                table_header.append(get_indentation(5) + f'<img src="{url}">')
            table_header.append(get_indentation(4) + '</div>')

            table_header.append(get_indentation(4) + f'<div class="text-container">{header}</div>')

        else:
            table_header.append(get_indentation(4) + header)

        table_header.append(get_indentation(3) + "</th>")
    table_header.append(get_indentation(2) + "</tr>")
    table_header.append(get_indentation(1) + "</thead>")

    return "".join(table_header)


def build_table_body(cert_data: dict, table_of_IDs: list, get_indentation):
    table_body = [get_indentation(1) + "<tbody>"]
    for row in table_of_IDs:
        table_body.append(get_indentation(2) + "<tr>")
        column_index = 0
        while column_index < len(row):          # using while instead of forEach/enumerate because we need to skip some iteration steps based on colspan (column_index += colspan)
            id = row[column_index]
            colspan = 1
            if id == None:
                table_body.append(get_indentation(3) + '<td class="missing"></td>')
            elif id == 0:
                table_body.append(get_indentation(3) + '<td class="empty"></td>')
            else:
                while column_index+colspan < len(row) and row[column_index+colspan] == id:
                    colspan += 1

                if colspan == 1:
                    table_body.append(get_indentation(3) + '<td>')
                else:
                    table_body.append(get_indentation(3) + f'<td colspan="{colspan}">')

                table_body.append(build_cell_content(cert_data[id], id, get_indentation))

                table_body.append(get_indentation(3) + '</td>')
            column_index += colspan
        table_body.append(get_indentation(2) + "</tr>")
    table_body.append(get_indentation(1) + "</tbody>")

    return "".join(table_body)


def build_cell_content(item: dict, id: str, get_indentation):
    cell_content = [get_indentation(4) + f'<a href="{item["imgURL"]}" target="_blank">']
    cell_content.append(get_indentation(5) + '<div class="image-container">')
    if item["name"].startswith("AZ-"):
        cell_content.append(get_indentation(6) + f'<img src="assets/thumbnails/{id}.svg">')
    else:
        cell_content.append(get_indentation(6) + f'<img src="assets/thumbnails/{id}.png">')
    cell_content.append(get_indentation(5) + '</div>')
    cell_content.append(get_indentation(4) + '</a>')

    cell_content.append(get_indentation(4) + '<div class="text-container">')
    cell_content.append(get_indentation(5) + f'<a href="{item["textURL"]}" target="_blank">')
    cell_content.append(get_indentation(6) + item["name"] + '')
    cell_content.append(get_indentation(5) + '</a>')
    cell_content.append(get_indentation(4) + '</div>')

    return "".join(cell_content)


def write_file(out_file: str, html_content: str):
    parent_dir = os.path.dirname(out_file)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    with open(out_file, "w", encoding="utf-8") as out_file_obj:
        out_file_obj.write(html_content)




def main(cert_data_filename, svg_data_filename, header_data_filename, base_html):
    cert_data = load_json_data(cert_data_filename)
    svg_data = load_json_data(svg_data_filename)
    header_data = load_json_data(header_data_filename)

    cert_data = {item_id:item for item_id,item in cert_data.items() if item["display"]}

    all_subjects_ordered = {header_subject_pair[0]:header_subject_pair[1] for header_subject_pair in header_data["order"]}
    subject_list = list(all_subjects_ordered.values())

    table_of_IDs = create_table_of_IDs(cert_data, subject_list)       # representing the content of the final HTML table with the IDs

    newline, indent_spaces, content_before_table, table_indent_level, content_after_table = get_html_table_context(base_html)
    get_indentation = create_indent_function(newline, indent_spaces, table_indent_level)

    table = "<table>"
    table += build_table_header(svg_data, all_subjects_ordered, get_indentation)
    table += build_table_body(cert_data, table_of_IDs, get_indentation)
    table += get_indentation(0) + "</table>"

    html_content = content_before_table + table + content_after_table

    return html_content


if __name__ == "__main__":
    cert_data_file = "../data/cert_data.json"
    svg_data_file = "../data/svg_data.json"
    header_data_file = "../data/header_data.json"

    base_html = "../templates/indented.html"
    
    out_file = "../output/skills.html"

    html_content = main(cert_data_file, svg_data_file, header_data_file, base_html)
    write_file(out_file, html_content)