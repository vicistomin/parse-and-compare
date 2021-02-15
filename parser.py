import requests
from bs4 import BeautifulSoup
import csv
from datetime import date
import os
from filecmp import dircmp
import pandas as pd
from shutil import copytree, rmtree


def get_html(url):
        r = requests.get(url)
        return r.text


def write_csv(data, url):
    today = str(date.today())
    vendor = url.split('/')[2].split('.')[1]
    filename = url.split('/')[4].split('?')[0]
    with open(today+'/'+vendor+'-'+filename+'.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f,dialect='excel')
        if data == 'header':
            writer.writerow(['order','url','name'])
        else:
            writer.writerow([data['order'],data['url'],data['name']+' - размер '+data['size']+'. Цена: '+data['price']+'. '+data['stock']])


def ell_scrape(url):
        html = get_html(url)
        soup = BeautifulSoup(html, 'lxml')

        try:
                prods = soup.find('div', class_='grid-list').find_all('div', class_='ty-grid-body')
        except:
                prods = {}

        write_csv('header', url)

        order = 0

        for prod in prods:
                name = prod.find('a', class_='product-title').text
                price = prod.find('span', class_='ty-price').find('span', class_='ty-price-num').text
                size = ''
                writed = 0

                try:
                        if prod.find('span', class_='ty-qty-out-of-stock').text == 'Поступление ожидается':
                                stock = 'Нет в наличии.'
                except:
                        stock = 'В наличии.'

                href = prod.find('a', class_='product-title').get('href')
                new_soup = BeautifulSoup(get_html(href), 'lxml')
                try:
                        options = new_soup.find('ul', class_="ty-product-options__elem").find_all('li')
                except:
                        options=''

                for option in options:
                        size = option.find('label').text.strip()
                        order = order + 1

                        data = {'name': name,
                                        'price': price,
                                        'stock': stock,
                                        'order':order,
                                        'url':href,
                                        'size': size}

                        write_csv(data, url)
                        writed = 1

                if writed == 0:
                        order = order + 1
                        size = 'единый'
                        data = {'name': name,
                                        'price': price,
                                        'stock': stock,
                                        'order':order,
                                        'url':href,
                                        'size': size}
                        write_csv(data, url)


def mam_scrape(url):
        html = get_html(url)
        soup = BeautifulSoup(html, 'lxml')

        try:
                prods = soup.find('div', class_='products-grid').find_all('div', class_='productBox')
        except:
                prods = {}

        write_csv('header', url)

        order = 0

        for prod in prods:
                name = prod.find('a', class_='title').text
                price = prod.find('div', class_='price').text
                size = ''
                writed = 0

                try:
                        if prod.find('input', class_='addtocart').get('value') == 'В корзину':
                                stock = 'В наличии.'
                except:
                        stock = 'Нет в наличии.'

                href = url.split('collection')[0]+prod.find('a', class_='title').get('href')
                new_soup = BeautifulSoup(get_html(href), 'lxml')
                options = new_soup.find('form', id="buy_form").find_all('span', class_='commas')

                for option in options:
                        size = option.previous_sibling.text
                        order = order + 1

                        data = {'name': name,
                                        'price': price,
                                        'stock': stock,
                                        'order':order,
                                        'url':href,
                                        'size': size}

                        write_csv(data, url)
                        writed = 1

                if writed == 0:
                        order = order + 1
                        size = 'единый'
                        data = {'name': name,
                                        'price': price,
                                        'stock': stock,
                                        'order':order,
                                        'url':href,
                                        'size': size}
                        write_csv(data, url)


def compare(old_dir, new_dir):
    dirComp = dircmp(old_dir, new_dir)
    #здесь храним перечень всех различающихся файлов:
    diff_list = dirComp.diff_files
    file_out = open(str(date.today())+'-difference.txt', 'w', encoding='utf-8')
    #ищем разницу для каждого из файлов:
    for diff_file in diff_list:
        # Read in the original and new file
        orig = open(old_dir+'/'+diff_file, 'r', encoding='utf-8')
        new = open(new_dir+'/'+diff_file, 'r', encoding='utf-8')

        orig_text = pd.read_csv(orig).name
        new_text = pd.read_csv(new).name

        orig_set = sorted(set(orig_text))
        new_set = sorted(set(new_text))

        added = [x for x in new_set if x not in orig_set]
        removed = [y for y in orig_set if y not in new_set]

        # Write to output file
        file_out.write("\n----------------------\n")
        file_out.write(diff_file+"\n")
        file_out.write("----------------------\n")
        if added:
            file_out.write("Добавили:\n")
            for idx, line in enumerate(added, start=1):
                file_out.write(str(idx)+': '+line+'\n')
        if removed:
            file_out.write("\nУбрали:\n")
            for idx, line in enumerate(removed, start=1):
                file_out.write(str(idx)+': '+line+'\n')
        orig.close()
        new.close()
    file_out.close()


def main():
    today = str(date.today())
    try:
        rmtree(today)
    except FileNotFoundError:
        pass

    try:
        os.mkdir(today)
    except FileExistsError:
        pass

    try:
        copytree("Today", "Previous", dirs_exist_ok=True)
    except:
        pass

    try:
        rmtree("Today")
    except FileNotFoundError:
        pass

    ell_urls = {
        'http://www.ellevill.org/category/slingi-mayki/?items_per_page=128',
        'http://www.ellevill.org/category/slingi-sharfy-tkanye/?features_hash=12-451-437&items_per_page=128',
        'http://www.ellevill.org/category/slingi-s-kolcami/?features_hash=12-451-437&items_per_page=128',
        'http://www.ellevill.org/category/ergorukzak/?features_hash=12-60-451-437&items_per_page=128',
        'http://www.ellevill.org/category/may-slingi/?features_hash=12-437-451&items_per_page=128',
        'http://www.ellevill.org/category/slingokurtki/?features_hash=12-535-767&items_per_page=128',
        'http://www.ellevill.org/category/podushka-loona-baby/?items_per_page=128',
            }

    mam_urls = {
            'https://www.mamidea.ru/collection/trikotazhnye-slingi?order=&page_size=100',
                        'https://www.mamidea.ru/collection/slingi-sharfy?order=&page_size=100',
                        'https://www.mamidea.ru/collection/kurtki?order=&page_size=100',
                        'https://www.mamidea.ru/collection/ergonomichnye-ryukzaki?order=&page_size=100',
                        'https://www.mamidea.ru/collection/slingi-s-koltsami?order=&page_size=100',
                        'https://www.mamidea.ru/collection/may-slingi?order=&page_size=100',
                        'https://www.mamidea.ru/collection/slingonakidki?order=&page_size=100',
                        'https://www.mamidea.ru/collection/busy?order=&page_size=100',
                }

    for url in ell_urls:
        ell_scrape(url)

    for url in mam_urls:
        mam_scrape(url)

    copytree(today, "Today", dirs_exist_ok=True)

    compare("Previous", "Today")


if __name__ == '__main__':
        main()
