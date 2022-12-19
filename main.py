from time import sleep
from time import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pyautogui
from selenium.common.exceptions import TimeoutException
import os
import pandas as pd
from datetime import datetime
import shutil
from tkinter import *
import pickle
import json
import logging


# загрузка браузера и запуск
def Chrome_start():
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()))  # всегда подгружает актуальную версию браузера
    driver.get('https://vk.com/feed')
    driver.maximize_window()
    return driver


# вход в аккаунт
def VKform(driver, login, password):
    try:
        WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.CLASS_NAME, 'VkIdForm__input')))
        driver.find_element(By.CLASS_NAME, 'VkIdForm__input').send_keys(login)
        driver.find_element(By.CLASS_NAME, 'VkIdForm__button').click()

        WebDriverWait(driver, 7).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'vkc__EnterPasswordNoUserInfo__buttonWrap')))
        driver.find_element(By.NAME, 'password').send_keys(password)
        driver.find_element(By.CSS_SELECTOR,
                            "#root > div > div > div > div > div > div > div > div > form > div.vkc__EnterPasswordNoUserInfo__buttonWrap > button").send_keys(
            Keys.ENTER)

    except TimeoutException:
        quit()


# создаём новую директорую для сохранения файлов. Проверяем на наличие дубликатов у создаваемой папки
def folder_making_screenshots():
    try:
        parent_dir = (r'%s\Desktop' % os.path.expanduser('~'))
        dirct = r'VK Screenshots'
        path = os.path.join(parent_dir, dirct)
        os.mkdir(path)

    except:
        try:
            parent_dir = (r'%s\Desktop\VK Screenshots' % os.path.expanduser('~'))
            dpath = r'%s' % datetime.now().date().strftime('%d.%m.%Y')
            path = os.path.join(parent_dir, dpath)
            os.mkdir(path)

        except FileExistsError:
            path = (r'%s\Desktop\VK Screenshots\%s' % (os.path.expanduser('~'),
                                                       datetime.now().date().strftime('%d.%m.%Y')))
            shutil.rmtree(path)  # удаляет папку и далее создаём её снова
            parent_dir = (r'%s\Desktop\VK Screenshots' % os.path.expanduser('~'))
            dpath = r'%s' % datetime.now().date().strftime('%d.%m.%Y')
            path = os.path.join(parent_dir, dpath)
            os.mkdir(path)

    return path


# собираем адреса аккаунтов
def accounts(driver):
    # открываем выпадающее меню с аккаунтами
    WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.CLASS_NAME,
                                                                   'Header')))
    driver.find_element(By.XPATH, '//*[@id="ads-app-header"]/div[1]/div/button').click()

    # передаём HTML страницу рекламного кабинета в супчик
    WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.CLASS_NAME,
                                                                   'Table__wrapper')))
    page = driver.page_source  # это должно обновляться, отдельный класс под него можно
    soup = BeautifulSoup(page, features='html.parser')

    # вытаскиваем ссылки на имеющиеся кабинеты
    urls_accounts = {}
    for i in soup.find_all(attrs={'class': 'HeaderSectionSwitcherDropdown__listItemLink'}):
        urls_accounts[i.text] = 'https://vk.com' + i['href']

    return urls_accounts


# создаёт словари со ссылками и соответствием
def list_maker(driver, link, class_name):
    driver.get(str(link))
    WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.CLASS_NAME,
                                                                   class_name)))

    headers = BS_headers(driver.page_source)
    data = BS_data(driver.page_source)
    links = BS_links(driver.page_source)

    df = df_maker(data, headers, links)

    stts = status(headers)
    dictionary = lvl(stts, df)
    return dictionary


# выбираем дату "сегодня" в периоде, чтобы активировать условие "активности" кампаний / клиента
def today_button(driver):
    WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.CLASS_NAME, 'SideOfficeMenu__body')))
    driver.find_element(By.XPATH, '//*[@id="ads_union_table"]/div/div[2]/div[1]/div[1]/button').click()
    sleep(0.5)
    driver.find_element(By.XPATH, '//*[@id="ads_union_table"]/div/div[2]/div[1]/div[1]/div/ul/li[2]').click()
    sleep(1)


# создаем функции получения структурированных данных из страницы для принятия решений
def BS_headers(page):
    soup = BeautifulSoup(page, features='html.parser')
    headers = []
    for i in soup.find(attrs={'class': 'Table__Row'}).find_all('td'):
        headers.append(i.text)
    return headers


def BS_data(page):
    soup = BeautifulSoup(page, features='html.parser')
    data = []
    for i in soup.find_all(attrs={'class': 'Table__Row Table__Row--body'}):
        for line in i.find_all('td'):
            data.append(line.text)
    return data


def BS_links(page):
    soup = BeautifulSoup(page, features='html.parser')
    links = []
    for i in soup.find('table', attrs={'class': 'Table__Grid'}).find_all('a'):
        if i.text:
            links.append('https://vk.com' + i['href'])
    return links


# Создаём функцию, которая собираем DataFrame из структурированных данных выше
def df_maker(data, headers, links):
    # разбиваем список на строки (чтобы создать DF)
    new_data = []
    start = 0
    finish = len(headers)

    for i in range(int(len(data) / len(headers))):
        new_data.append(data[start:finish])
        start = finish
        finish = finish + len(headers)

    # создаём DF
    df = pd.DataFrame(data=new_data, columns=headers)
    df_links = pd.DataFrame(data={'Ссылка': links})

    df = df.join(df_links)

    # Переводим колонку "Показы" в целые числа, чтобы проводить мат. операции
    df['Показы'] = df['Показы'].str.replace(' ', '').astype(str).astype(int)

    return df


# составляет словарь клиентского уровня / уровня кампании по условию
def status(headers):
    status = None
    while not status:
        if 'Клиент' in headers:
            status = 'Клиент'
        elif 'Кампания' in headers:
            status = 'Кампания'
        else:
            status = 'Объявление'
    return status


def lvl(status, df):
    if status == 'Клиент':
        df_xtrct = df.query('Показы > 100')
        clients_lst = df_xtrct['Клиент'].tolist()
        links_lst = df_xtrct['Ссылка'].tolist()
        dct = dict(
            zip(clients_lst, links_lst))  # Словарь - чтобы иметь возможность сопоставить ссылку и клиента
        return dct

    elif status == 'Кампания':
        df_xtrct = df.query('Показы > 100')
        campaigns_lst = df_xtrct['Кампания'].tolist()
        links_lst = df_xtrct['Ссылка'].tolist()
        dct = dict(
            zip(campaigns_lst, links_lst))  # Словарь - чтобы иметь возможность сопоставить ссылку и кампанию
        return dct

    elif status == 'Объявление':
        df_xtrct = df.query('Показы > 100')
        campaigns_lst = df_xtrct['Объявление'].tolist()
        links_lst = df_xtrct['Ссылка'].tolist()
        dct = dict(
            zip(campaigns_lst, links_lst))  # Словарь - чтобы иметь возможность сопоставить ссылку и кампанию
        return dct


# Создаёт новое, корректное название файла. Заменяет всё запрещённые и спорные символы на (.)
def correct_naming(file_name):
    FORBIDDEN_SMBLS = ('<', '>', '/', '\\', '|', '^', '*', "'", ':', ';', '?', '$', '%', '@', '+')
    correct_name = ''
    for letter in file_name:
        if letter in FORBIDDEN_SMBLS:
            correct_name += '.'
        else:
            correct_name += letter
    return correct_name


# Создаём внутренние папки
def inner_folders_making(name, parent_path):
    name = correct_naming(name)
    dir_path = r'%s' % name
    path = os.path.join(parent_path, dir_path)
    os.mkdir(path)
    return path


# основной код программы
def main():
    start = time()

    # стартуем
    driver = Chrome_start()
    VKform(driver, login, password)

    # заходим в рекламный кабинет
    WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.CLASS_NAME, 'page_header_cont')))
    driver.get('https://vk.com/ads?act=office&union_id=')  # может сразу сюда переходить без \feed страницы?

    # собираем адреса аккаунтов
    urls_accounts = accounts(driver)

    for account, alink in urls_accounts.items():
        try:
            driver.get(alink)
            today_button(driver)
            headers = BS_headers(driver.page_source)
            data = BS_data(driver.page_source)
            links = BS_links(driver.page_source)

            df = df_maker(data, headers, links)

            dict_clients = {}  # созданы во избежание ошибок при вызове несуществующего словаря
            dict_campaigns = {}  # созданы во избежание ошибок при вызове несуществующего словаря
            url_to_screen = []

            stts = status(headers)

            if stts == 'Клиент':
                dict_clients = lvl(stts, df)
            else:
                dict_campaigns = lvl(stts, df)

            path = folder_making_screenshots()

            # создаем файл с результатами работы скрипта
            result = open(r'%s\result.txt' % path, 'x')
            result.close()

            # открываем файл с данными из CheckBox по клиентам
            with open(r"%s\Desktop\VK Screenshots\settings\clients_to_screen.json" % os.path.expanduser('~'),
                      'r') as f:
                clients = json.load(f)

            for client, cllink in dict_clients.items():

                # создаём словарь "кампания:ссылка"
                dict_campaigns = list_maker(driver, cllink, 'Table__wrapper')

                # создаем нужную директорую
                path_clnt = inner_folders_making(client, path)

                # записываем в log
                result = open(r'%s\result.txt' % path, 'a')
                result.writelines((client, ' : ', cllink, '\n'))

                for campaign, calinks in dict_campaigns.items():

                    # создаём словарь "креатив:ссылка"
                    dict_ads = list_maker(driver, calinks, 'Table__wrapper')

                    # создаём проверку True-False (из CheckBox) по клиенту
                    if not clients[client]:
                        for key, value in dict_ads.items():
                            # создаём словарь "креатив:ссылка"
                            dict_ads = {key: value}
                            break
                    else:
                        print('True')

                    # создаем нужную директорую
                    path_camp = inner_folders_making(campaign, path_clnt)

                    # записываем в results
                    result.writelines(('\t', campaign, ' : ', calinks, '\n'))

                    for creative, crlinks in dict_ads.items():
                        driver.get(str(crlinks))
                        WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.CLASS_NAME,
                                                                                       'clear_fix')))

                        page = driver.page_source  # это должно обновляться, отдельный класс под него можно
                        soup = BeautifulSoup(page, features='html.parser')

                        # Собирает ссылки на предпросмотр. Проходит проверку есть / нет ссылка на странице
                        if soup.find(attrs={'class': 'ads_union_title_add'}).find_all('a'):
                            for a in soup.find(attrs={'class': 'ads_union_title_add'}).find_all('a'):
                                if a.text:
                                    url_to_screen = ('https://vk.com' + a['href'])
                        else:
                            url_to_screen = 0

                        # Проходим верхнеуровневую проверку на наличие ссылки для скрина.
                        # К примеру, в сторис ссылки не будет
                        try:
                            driver.get(str(url_to_screen))
                            sleep(2)  # заменить на явное ожидание?

                            # чек на тему защиты аккаунта (НЕ РАБОТАЕТ вроде как)
                            try:
                                if driver.find_element(By.CLASS_NAME, 'box_layout').is_displayed() is True:
                                    print('ALERT: Find this bastard. Click it! CLICK!!')
                                    driver.find_element(By.CLASS_NAME,
                                                        '//*[@id="box_layer"]/div[2]/div/div[1]/div[1]').click()
                                    print('Yeah, we got it')
                                    sleep(0.5)
                            except:
                                pass

                            # нацеливаемся на креатив (Классы разные у разных типов креатива)
                            soup = BeautifulSoup(driver.page_source, features='html.parser')
                            list = []
                            for i in soup.find_all('div', attrs='post_date'):
                                try:  # не везде текст лежит в 'a'
                                    for a in i.find('a'):
                                        list.append(a.text)

                                except:
                                    list.append(i.text)

                            counter = 0
                            for element in driver.find_elements(By.CLASS_NAME, 'post_date'):
                                if 'Реклама' in list[counter]:
                                    driver.execute_script('arguments[0].scrollIntoView();', element)
                                    sleep(1)
                                    driver.execute_script('window.scrollBy(0,-200)', '')
                                    sleep(1)
                                    break
                                else:
                                    counter += 1
                                    continue

                            # снимаем и сохраняем
                            screenshot = pyautogui.screenshot()
                            file_name = correct_naming(creative)
                            screenshot.save(r'%s\%s' % (path_camp, file_name + '.png'))

                            # записываем в результаты работы
                            result.writelines(('\t\t', creative, ' : ', crlinks, '\n'))

                        except:
                            logging.exception('Возникла следующая ошибка: ')
                            continue
        except AttributeError:
            logging.exception('В кабинете отсутствуют данные, перебираем кабинеты дальше')
            continue

    result.write('\n\nВремя работы скрипта: ~%s минут' % round((time() - start) / 60))
    result.close()


# парсим список клиентов
def clients():
    # стартуем
    driver = Chrome_start()
    VKform(driver, login, password)

    # заходим в рекламный кабинет
    WebDriverWait(driver, 7).until(EC.presence_of_element_located((By.CLASS_NAME, 'page_header_cont')))
    driver.get('https://vk.com/ads?act=office&union_id=')

    urls_accounts = accounts(driver)

    dict_clients = {}
    for account, alink in urls_accounts.items():
        try:
            driver.get(alink)
            today_button(driver)
            headers = BS_headers(driver.page_source)
            data = BS_data(driver.page_source)
            links = BS_links(driver.page_source)

            df = df_maker(data, headers, links)
            stts = status(headers)

            if stts == 'Клиент':
                dict_clients = lvl(stts, df)
            else:
                dict_campaigns = lvl(stts, df)

        except AttributeError:
            logging.exception('В кабинете отсутствуют данные, перебираем кабинеты дальше')
            continue

        dict_clients.update(dict_clients)

    # записываем в файл
    with open(r'%s\Desktop\VK Screenshots\settings\clients.json' % os.path.expanduser('~'), 'w') as clients:
        clients.write(json.dumps(dict_clients))
        clients.close()


# создаём класс для работы с интрефейсом
class Application(Frame):
    """Вызывает интерфейс работы с программой"""

    def __init__(self, master):
        super(Application, self).__init__(master)
        self.grid()
        self.__logging()
        self.__create_upper_widget()
        self.__create_middle_widget()
        self.__create_lower_widget()

    @staticmethod
    def __folder_making_settings():
        """ Создаёт корневую папку и папку 'settings', проверяя их на первоначальное наличие """
        parent = r'%s\Desktop\VK Screenshots' % os.path.expanduser('~')

        while not os.path.exists(r'%s\settings' % parent):

            try:
                parent_dir = (r'%s\Desktop' % os.path.expanduser('~'))
                dirct = r'VK Screenshots'
                path = os.path.join(parent_dir, dirct)
                os.mkdir(path)

            except FileExistsError:
                parent_dir = parent
                dirct = r'settings'
                path = os.path.join(parent_dir, dirct)
                os.mkdir(path)

        path = (r'%s\settings' % parent)
        return path

    def __logging(self):
        """ Создаёт log-файл """
        path = self.__folder_making_settings()

        logging.basicConfig(filename=r'%s\logs' % path,
                            format='\n---- %(asctime)s %(levelname)-s ----',
                            datefmt='%d.%m.%Y %H:%M:%S')

    def __create_upper_widget(self):
        """ Создаёт поля верхнего блока окна: Логин / Пароль """
        login, password = self.__load_data()

        Label(self, text='Данные для входа во Вконтакте:'). \
            grid(row=0, column=0, columnspan=2, sticky=W)

        # Блок "Логин"
        Label(self, text='Логин:'). \
            grid(row=1, column=0, sticky=W)

        self.login = Entry(self)
        self.login.insert(0, login)
        self.login.grid(row=1, column=1, sticky=W)

        # Блок "Пароль"
        Label(self, text='Пароль') \
            .grid(row=2, column=0, sticky=W)

        self.password = Entry(self, textvariable=StringVar(), show='*')
        self.password.insert(0, password)
        self.password.grid(row=2, column=1, sticky=W)

        Button(self, text='Старт', command=self.__start). \
            grid(row=3, column=0, sticky=E)

        Button(self, text='Клиенты', command=self.__clients). \
            grid(row=3, column=1, sticky=W)

    @staticmethod
    def clients_list():
        """ Загружает уже полученный ранее список клиентов """
        try:
            with open(fr'{os.path.expanduser("~")}\Desktop\VK Screenshots\settings\clients.json') as f:
                clients = json.load(f).keys()
                clients = list(clients)
                f.close()
                return clients
        except FileNotFoundError:
            pass

    def __create_middle_widget(self):
        """ Создаёт средний динамический блок окна со списком клиентов """
        path = r"%s\Desktop\VK Screenshots\settings\clients_to_screen.json" % os.path.expanduser('~')
        if os.path.exists(path):
            with open(path, 'r') as f:
                clients_dict = json.load(f)
                clients = list(clients_dict.keys())

                self.client = clients
                counter = 0
                for client in clients:
                    self.client[counter] = BooleanVar(value=clients_dict.get(client))
                    Checkbutton(self, text=client, variable=self.client[counter]). \
                        grid(row=5 + counter, column=0, sticky=W)
                    counter += 1
        else:
            try:
                Label(self, text='Список клиентов: ').grid(row=4, column=0, sticky=W)

                clients = self.clients_list()
                self.client = clients

                counter = 0
                for client in clients:
                    self.client[counter] = BooleanVar()
                    Checkbutton(self, text=client, variable=self.client[counter]). \
                        grid(row=5 + counter, column=0, sticky=W)
                    counter += 1
            except TypeError:
                pass

    def __create_lower_widget(self):
        """ Создаём нижний блок окна """
        self.info = Text(self, width=30, height=3, wrap=WORD)
        self.info.grid(row=100, column=0, columnspan=10, sticky=W)

    def lossword(self):
        """ Передаёт введённый пароль / логин по запросу """
        global login
        login = self.login.get()
        global password
        password = self.password.get()
        return login, password

    @staticmethod
    def __save_data():
        """ Сохраняет логин / пароль в *bat файл  """
        lossword_f = open(r'%s\Desktop\VK Screenshots\settings\to_log_in.dat' % os.path.expanduser('~'), 'wb')
        pickle.dump(login, lossword_f)
        pickle.dump(password, lossword_f)
        lossword_f.close()

    @staticmethod
    def __load_data():
        """ Подгружает Логин / Пароль из ранее созданного файла """
        try:
            # сохранить в settings
            with open(r'%s\Desktop\VK Screenshots\settings\to_log_in.dat' % os.path.expanduser('~'), 'rb') \
                    as lossword_f:
                login = pickle.load(lossword_f)
                password = pickle.load(lossword_f)
                return login, password
        except FileNotFoundError:
            login, password = '', ''
            return login, password

    def __save_checkbox(self):
        """ Сохраняем в словарь заполненные галочки и список клиентов """
        try:
            clients_list = self.clients_list()
            counter = 0
            scrnshts_sttngs = {}
            for client in clients_list:
                value = self.client[counter].get()
                scrnshts_sttngs[client] = value
                counter += 1

            with open(fr'%s\Desktop\VK Screenshots\settings\clients_to_screen.json' % os.path.expanduser('~'), 'w') \
                    as f:
                f.write(json.dumps(scrnshts_sttngs))

        except TypeError:
            pass

    def __clients(self):
        """ Собирает список клиентов """
        self.lossword()
        self.__save_data()
        self.__save_checkbox()

        self.info.delete(0.0, END)
        self.info.insert(0.0, 'Список клиентов получен. Необходимо произвести рестарт программы ручным путем')

        try:
            clients()
        except:
            logging.exception('Возникла следующая ошибка: ')

    def __start(self):
        """ Запускает основной код программы """
        self.lossword()
        self.__save_data()
        self.__save_checkbox()
        self.info.delete(0.0, END)
        self.info.insert(0.0, 'Скриншоты и файл с результатами в папке на рабочем столе')

        try:
            main()
        except:
            logging.exception('Возникла следующая ошибка: ')


# запускаем и настраиваем интерфейс
root = Tk()
root.title('Вконтакте. Автоматическое снятие скриншотов')
root.geometry('300x300')

app = Application(root)
root.mainloop()
