import json
from typing import List, Any, Union
import requests
from bs4 import BeautifulSoup


def get_NPS_VRO():
    """
        no input parameter
        returns a list with plan category, pension management firm and latest NAV
        :rtype: list
        VRO's link works better since we can get all the data in one shot.
        But it does not contain scheme codes, and NAV is rounded to 2 decimals (4 decimals in NSDL)
    """
    # URL to be used. Might need to validate this from time to time if this moves.
    url = 'https://www.valueresearchonline.com/nps/selector-data/?output=html-data'
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}
    r = requests.get(url=url, headers=headers)
    content = json.loads(r.content)['html_data']
    soup = BeautifulSoup(content, features='lxml')
    # Get the table data from the extracted HTML and create a list.
    table = [[cell.text for cell in row("td")] for row in soup("tr")]
    nav_list = []
    # Adding the common header
    nav_list.append(['Scheme Type', 'Scheme Name', 'NAV'])
    for row in table:
        # Remove rows with no data
        if len(row) == 0:
            continue
        elif row[2] == '':
            # These rows have the scheme types.
            # Get the scheme type value in header to add to other rows.
            header = row[1]
            continue
        else:
            # These rows have the relevant data.
            row[0] = header
        # Adding the Scheme Type, Scheme Name & NPS.
        nav_list.append([row[0], str.replace(row[1], '\xa0#', ''), row[2]])

    return nav_list


def get_NAV_NSDL():
    """
        no input parameter
        returns a list with plan category, pension management firm and latest NAV
        :rtype: list
        We need multiple requests to get the data for each pension manager.
        NSDL offers scheme codes, and NAV with 4 decimals
    """
    # URL to be used. Might need to validate this from time to time if this moves.
    url = 'https://npscra.nsdl.co.in/nav-search.php'
    # Parameter used in the POST request is select_pfm
    key = 'select_pfm'
    # values = ['PFM001']
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}
    # List of pension fund managers
    # This needs to be updated from time to time
    values = ['PFM001', 'PFM002','PFM003','PFM005','PFM006','PFM007','PFM008', 'PFM010']
    nav_list= []
    # Adding the common header
    nav_list.append(['Date', 'Scheme Code', 'Scheme Name', 'Scheme NAV']) 
    for value in values:
        param = {key: value}
        r = requests.post(url, data = param, headers = headers)
        soup = BeautifulSoup(r.content, features = 'lxml')
        table = [[cell.text for cell in row("td")] for row in soup("tr")]
        for row in table:
            # Skip rows with headers
            if row[0] == 'SNo.':
                continue
            # Add rows with relevant data (scheme NAVs)
            else:
                nav_list.append([row[1], row[2], row[3], row[4]])

    return nav_list
