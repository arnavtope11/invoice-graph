from grakn.client import GraknClient
import json, ijson 
     
def build_phone_call_graph(inputs):
    with GraknClient(uri="localhost:48555") as client:
        with client.session(keyspace = "invoice_rep") as session:
            for input in inputs:
                print("Loading from [" + input["data_path"] + "] into Grakn ...")
                load_data_into_grakn(input, session)

def load_data_into_grakn(input, session):
    items = parse_data_to_dictionaries(input)

    for item in items:
        with session.transaction().write() as transaction:
            graql_insert_query = input["template"](item)
            print("Executing Graql Query: " + graql_insert_query)
            transaction.query(graql_insert_query)
            transaction.commit()

    print("\nInserted " + str(len(items)) + " items from [ " + input["data_path"] + "] into Grakn.\n")

def line_items_schema(invoice):
    line_items_header = invoice["line_items_header"]
    graql_insert_query = "define"
    graql_insert_query += " line_item sub entity, plays sub_item"
    for row_col in line_items_header.values():
        attrib = row_col["text"].replace(' ', '_')
        attrib = attrib.lower()
        graql_insert_query += ', has ' + attrib
    graql_insert_query += ";"
    for row_col in line_items_header.values():
        attrib = row_col["text"].replace(' ', '_')
        attrib = attrib.lower()
        graql_insert_query += ' ' + attrib + ' sub attribute, value string;'
    return graql_insert_query

def invoice_template(invoice):
    entities = invoice["entities"]
    graql_insert_query = 'insert $invoice isa invoice;'
    i = 1
    for attrib_name in entities:
        graql_insert_query += ' $attrib-' + str(i) + ' isa attrib, has name "' + attrib_name  + '";'
        i += 1
    i = 1
    for attrib_value in entities.values():
        graql_insert_query += ' $attrib-' + str(i) + ' has value "' + attrib_value["text"]  + '";'
        i += 1
    graql_insert_query += ' $attrib-' + str(i) + ' isa attrib, has name "line_items", has value "None";'
    return graql_insert_query

def line_items_template(invoice):
    line_items = invoice["line_items"]
    line_items_header = invoice["line_items_header"]
    columns = []
    for row_col in line_items_header.values():
        attrib = row_col["text"].replace(' ', '_')
        attrib = attrib.lower()
        columns.append(attrib)
    for row_col in line_items.values():
        if row_col["column_id"] == 1:
            item_no = row_col["row_id"]
            is_query_present = "graql_insert_query" in locals()
            if is_query_present == False:
                graql_insert_query = ' insert $line-item-' + str(item_no-1) + ' isa line_item, has ' + columns[0] + ' "' + row_col["text"] + '"'
            else:
                graql_insert_query += ' $line-item-' + str(item_no-1) + ' isa line_item, has ' + columns[0] + ' "' + row_col["text"] + '"'   
        elif row_col["column_id"] == len(columns):
            graql_insert_query += ', has ' + columns[len(columns)-1] + ' "' + row_col["text"] + '"'
            graql_insert_query += ";"        
        else:
            graql_insert_query += ', has ' + columns[row_col["column_id"]-1] + ' "' + row_col["text"] + '"'
    return graql_insert_query

def includes_template_1(invoice):
    entities = invoice["entities"]
    graql_insert_query = 'match $invoice isa invoice;'
    i = 1
    for attrib_name in entities:
        graql_insert_query += ' $attrib-' + str(i) + ' isa attrib, has name "' + attrib_name  + '";'
        is_relation_present = "relation_insert_query" in locals()
        if is_relation_present == False:
            relation_insert_query = " insert (main_item: $invoice, sub_item: $attrib-" + str(i) + ") isa includes;"
        else:
            relation_insert_query += " (main_item: $invoice, sub_item: $attrib-" + str(i) + ") isa includes;"
        i += 1
    graql_insert_query += ' $attrib-' + str(i) + ' isa attrib, has name "line_items";'            
    relation_insert_query += " (main_item: $invoice, sub_item: $attrib-" + str(i) + ") isa includes;"
    graql_insert_query += relation_insert_query
    return graql_insert_query

def includes_template_2(invoice):
    line_items = invoice["line_items"]
    line_items_header = invoice["line_items_header"]
    graql_insert_query = 'match $attrib isa attrib, has name "line_items";'
    columns = []
    for row_col in line_items_header.values():
        attrib = row_col["text"].replace(' ', '_')
        attrib = attrib.lower()
        columns.append(attrib)
    for row_col in line_items.values():
        if row_col["column_id"] == len(columns):
            item_no = row_col["row_id"]
            graql_insert_query += ' $line-item-' + str(item_no-1) + ' isa line_item, has ' + columns[len(columns)-1] + ' "' + row_col["text"] + '";'
    for row_col in line_items.values():
        if row_col["column_id"] == len(columns):
            item_no = row_col["row_id"]
            is_relation_present = "relation_insert_query" in locals()
            if is_relation_present == False:
                relation_insert_query = " insert (main_item: $attrib, sub_item: $line-item-" + str(item_no-1) + ") isa includes;"
            else:
                relation_insert_query += " (main_item: $attrib, sub_item: $line-item-" + str(item_no-1) + ") isa includes;"
    graql_insert_query += relation_insert_query
    return graql_insert_query

def parse_data_to_dictionaries(input):
    items = []
    data_json = input["data_path"] + ".json"
    f = open(data_json)
    obj = json.load(f)
    invoice_image = "predict_output." + obj["file_name"]
    with open(input["data_path"] + ".json") as data:
        for item in ijson.items(data, invoice_image):
            items.append(item)
    return items

inputs = [ 
    {
        "data_path": "entities_output",
        "template": line_items_schema   
    },
    {
        "data_path": "entities_output",
        "template": invoice_template   
    },
    {
        "data_path": "entities_output",
        "template": line_items_template   
    },
    {
        "data_path": "entities_output",
        "template": includes_template_1   
    },
    {
        "data_path": "entities_output",
        "template": includes_template_2   
    }
]

build_phone_call_graph(inputs=inputs)