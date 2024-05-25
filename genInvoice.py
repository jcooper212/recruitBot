import os
import shutil
import requests
import sys
import json
from dotenv import load_dotenv

load_dotenv()

from pathlib import Path
from bs4 import BeautifulSoup as Soup

PATH_TO_BLOG = Path('/Users/jcooper/py/genAi/recruitBot')
PATH_TO_CONTENT = PATH_TO_BLOG/"content"
PATH_TO_CONTENT.mkdir(exist_ok=True, parents=True)

###Load Json
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def extract_values(json_data):
    if "title" in json_data and "tags" in json_data and "summary" in json_data:
        return {
            "title": json_data["title"],
            "tags": json_data["tags"],
            "summary": json_data["summary"]
        }
    else:
        print("Error: JSON file is missing one or more required fields.")
        return None



#use this version - will create an article and a cover image (uses story template)
def create_invoice(json_data):
    #new article file
    files = len(list(PATH_TO_CONTENT.glob('*.html')))
    new_title = f"Inv_{json_data['client_name']}_{json_data['invoice_num']}.html"

    path_to_new_content = PATH_TO_CONTENT/new_title
    path_to_template = "{}/invoice_template.html".format(PATH_TO_CONTENT)



    #read the template
    html_content=""
    with open(path_to_template, 'r') as file:
        html_content = file.read()
        html_content = html_content.replace("total_due", json_data['total_due'])
        html_content = html_content.replace("due_date", json_data['due_date'])
        html_content = html_content.replace("invoice_title", json_data['invoice_title'])
        html_content = html_content.replace("invoice_num", json_data['invoice_num'])
        html_content = html_content.replace("invoice_date", json_data['invoice_date'])
        html_content = html_content.replace("client_name", json_data['client_name'])
        html_content = html_content.replace("client_contact", json_data['client_contact'])
        html_content = html_content.replace("invoice_table", json_data['invoice_table'])
        html_content = html_content.replace("rayze_logo", json_data['rayze_logo'])


    print("html_content is ", html_content)

    #write new invoice
    if not os.path.exists(path_to_new_content):
        with open(path_to_new_content,"w") as f:
            f.write(html_content)
            return path_to_new_content
    else:
        raise FileExistsError('file already exists')

#main
if len(sys.argv) != 2:
    print("Usage: python3 genInvoice.py <json_file>  {|} you passed in: ", sys.argv)
    sys.exit(1)

# Read json input
json_data = read_json_file(sys.argv[1])
print(json_data)
prompt_str = ""
if "title" in json_data and "tags" in json_data and "heading" in json_data:
    prompt_str = f"{json_data['heading']} "
    prompt_str = prompt_str + f"Title: {json_data['title']}  "
    prompt_str = prompt_str + f"Tags: {json_data['tags']}  "
else:
    print("Error: JSON file is missing one or more required fields.")

path_to_new_content = create_invoice(json_data)
print(path_to_new_content)

