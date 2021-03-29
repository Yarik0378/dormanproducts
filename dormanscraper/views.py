import threading
from django.shortcuts import redirect
from django.shortcuts import render
from .forms import UploadFileForm
from .models import Project
import datetime
import os

long = ''
completed = 0


def handle_uploaded_file(f, pr):
    with open(f'media/documents/{pr}.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def delete_project_file(id):
    try:
        os.remove(f"media/documents/{id}.txt")
        os.remove(f"media/documents/{id}result.csv")
    except OSError:
        pass


def index(request):
    global long
    projects = Project.objects.all()
    return render(request, 'index.html', {"projects": projects, 'begin': long})


def delete(request, projectid):
    project = Project.objects.get(id=projectid)
    delete_project_file(project.id)
    project.delete()

    return redirect('/')



def upload_file(request):
    if request.method == 'POST':

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            project = Project(uploaded_file=file.name, status="processing", date=datetime.datetime.now(),   )
            project.save()
            handle_uploaded_file(file, project.id)
            ProcessProject(project)
    return redirect('/')


lock = threading.Lock()


def ProcessProject(project):
    x = threading.Thread(target=ThreadFunction, args=(project,))
    x.start()


def ThreadFunction(project):
    with lock:
        path = f"media/documents/{project.id}.txt"
        start_parse(path, f"media/documents/{project.id}result.csv", project)
        project.status = "done"
        project.result_file = f"{project.id}result.csv"
        project.save()



# Product Name
# Suspension Lateral Link
# Application Summary -----------------------------------------------------------------------------------------------
import csv
import requests
from bs4 import BeautifulSoup
from nordvpn_switcher import initialize_VPN, rotate_VPN

# settings = initialize_VPN(save=1, area_input=['complete rotation'])

header = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41',
    'host': "www.dormanproducts.com",
    'referer': 'https://www.dormanproducts.com/',
    'Accept-Language': 'en-US;q=0.6,en;q=0.5',
}


def write_csv(data, path_to_save):
    with open(path_to_save, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow((data['code'],
                         data['product name'],
                         data['product info'],
                         data['application summary'],
                         data['cross'],
                         data['part no'],
                         data['mrf name'],
                         data['oe numbers']
                         ))


def write_header_csv(path_to_save):
    data = {
        'code': 'Original part number',
        'product name': 'Product Name',
        'product info': 'Product Info',
        'application summary': 'Application Summary',
        'cross': 'Cross',
        'part no': 'Part No',
        'mrf name': 'Mfr Name',
        'oe numbers': 'OE Numbers'
    }
    with open(path_to_save, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow((data['code'],
                         data['product name'],
                         data['product info'],
                         data['application summary'],
                         data['cross'],
                         data['part no'],
                         data['mrf name'],
                         data['oe numbers']
                         ))


def get_html(code):
    return requests.get(f'https://www.dormanproducts.com/gsearch.aspx?type=oesearch&origin=oesearch&q={code}',
                        headers=header).text


def check_captcha(soup, code):
    global header
    captcha = soup.find('div', id='divSecurityForm')
    if captcha is None:
        print('Каптчи нету')
        return None
    else:
        print('Есть каптча')
        rotate_VPN()
        new_html = get_html(code)
        new_soup = BeautifulSoup(new_html, 'lxml')
        new_soup_ = new_soup.find('div', id='divSecurityForm')
        if new_soup_:
            rotate_VPN()
            new_html = get_html(code)
        return new_html


def found_item(soup, code):
    found_items = soup.find('p', id='searchFoundZeroItem')
    if found_items:
        print('Items not found: ', code)
        return True


def check_captcha_oem(html, link):
    captcha = html.find('div', id='divSecurityForm')
    if captcha is None:
        return None
    else:
        print('Есть каптча')
        rotate_VPN()
        new_html = requests.get(f'https://www.dormanproducts.com/{link}').text
        new_soup = BeautifulSoup(new_html, 'lxml')
        new_soup_ = new_soup.find('div', id='divSecurityForm')
        if new_soup_:
            rotate_VPN()
            new_html = check_captcha_oem(new_html, link)
        return new_html


def get_oem(link):
    html = requests.get(f'https://www.dormanproducts.com/{link}').text
    soup = BeautifulSoup(html, 'lxml')
    captcha = check_captcha_oem(soup, link)
    if captcha is not None:
        print('New HTML')
        soup = BeautifulSoup(captcha, 'lxml')
    table = soup.find('section', id='productOE').find('table').select('tr')
    data = ''
    for tr in table[1:]:
        th = tr.find('th').text
        td = tr.find('td').text
        data += f'{td}:{th}, '
    return data


def get_data(html, code, path_to_save):
    soup = BeautifulSoup(html, 'lxml')
    captcha = check_captcha(soup, code)
    if captcha is not None:
        print('New HTML')
        soup = BeautifulSoup(captcha, 'lxml')
    if found_item(soup, code) is True:
        return None
    products = soup.find_all('div', class_='row searchResults')
    for product in products:
        product_n = product.find('h2', class_='item-headline')
        link_details = product_n.find('a').get('href')
        print(link_details)
        product_name = product_n.find('span', class_='item-name').text
        print(product_name)
        products_info = product.find_all('div')
        product_info = products_info[1].find('h4').text
        print(product_info)
        application_summary = product.find('div', class_='searchItems-info').find('p').text.replace('\n', '')
        print(application_summary)
        table = product.find('table', class_='table table-hover table-dorman table-striped')
        cross = table.find('thead').find('tr').find('th').text.strip()
        print(cross)
        part_no = table.find('tbody').find('tr').find('th').text
        print(part_no)
        mrf_name = table.find('tbody').find('tr').find('td').text
        print(mrf_name)
        oem_numbers = get_oem(link_details)
        print(oem_numbers)
        data = {
            'code': code,
            'product name': product_name,
            'product info': product_info,
            'application summary': application_summary,
            'cross': cross,
            'part no': part_no,
            'mrf name': mrf_name,
            'oe numbers': oem_numbers
        }
        write_csv(data, path_to_save)


def start_parse(path, path_to_save, project):
    global long, completed
    my_file = open(path, "r")
    content_list = my_file.readlines()

    long = len(content_list)
    project.len_codes = long
    project.save()
    write_header_csv(path_to_save)
    for code in content_list:
        completed += 1
        code = code.replace('\n', '')
        print(code)
        get_data(get_html(code), code, path_to_save)
        project.finished_codes = completed
        project.save()
    completed -= int(long)
    long = ''
