"""
Módulo
"""

import pprint
import time

import pandas as pd
from selenium.webdriver.common.by import By

# from selenium.webdriver.common.action_chains import ActionChains
# from .webdriver import Chrome, Firefox


class FBDS:
    def __init__(self, driver, uf) -> None:
        self.driver = driver
        self.uf = uf

        # Vai pro Site
        self._go_fbds()

    def _go_fbds(self):
        URL = f"https://geo.fbds.org.br/{self.uf}/"
        self.driver.get(url=URL)

    def click_back(self):
        """
        Voltar

        :return: _description_
        :rtype: _type_
        """
        content_xpath = self.driver.find_element(By.XPATH, "//*[@id='content']")
        back_xpath = content_xpath.find_element(
            By.XPATH,
            ".//*[@class='item folder folder-parent']",
        )
        back_xpath.click()
        time.sleep(1)
        return 0

    def click_download(self):
        """
        _summary_

        :return: _description_
        :rtype: _type_
        """
        content_xpath = self.driver.find_element(By.XPATH, "//*[@id='topbar']")
        down_xpath = content_xpath.find_element(By.XPATH, ".//*[@id='download']")
        down_xpath.click()
        time.sleep(1)
        return 0

    def get_dict(self, folder):
        """
        XPATH dos folders
        :param folder: _description_
        :type folder: _type_
        """
        # URL
        href_xpath = folder.find_element(By.XPATH, ".//a")
        href_value = href_xpath.get_attribute("href")
        # print(href_value)

        # Tipo
        icon_xpath = folder.find_element(
            By.XPATH, ".//a//span[@class='icon square']//img"
        )
        icon_value = icon_xpath.get_attribute("alt")
        # print(icon_value)

        # Nome
        label_xpath = folder.find_element(By.XPATH, ".//a//span[@class='label']")
        label_value = label_xpath.text
        # print(label_value)

        # Data
        date_xpath = folder.find_element(By.XPATH, ".//a//span[@class='date']")
        date_value = date_xpath.text
        # print(date_value)

        # Size
        size_xpath = folder.find_element(By.XPATH, ".//a//span[@class='size']")
        size_value = size_xpath.text
        # print(size_value)

        #
        dict_data = {
            "url": href_value,
            "type": icon_value,
            "name": label_value,
            "date": date_value,
            "size": size_value,
        }
        # print(dict_data)
        return dict_data

    def list_folders_h5ai(self):
        """
        Lista as Pastas

        :return: _description_
        :rtype: _type_
        """
        # Conteúdo Principal
        content_xpath = self.driver.find_element(By.XPATH, "//*[@id='content']")

        # Lista
        list_folders = content_xpath.find_elements(
            By.XPATH, ".//*[@class='item folder']"
        )

        list_data = []
        for folder in list_folders:
            dict_data = self.get_dict(folder)
            list_data.append(dict_data)
        return list_data

    def list_itens_h5ai(self):
        """
        _summary_

        :return: _description_
        :rtype: _type_
        """
        # Conteúdo Principal
        content_xpath = self.driver.find_element(By.XPATH, "//*[@id='content']")

        # Lista
        list_itens = content_xpath.find_elements(By.XPATH, ".//*[@class='item file']")

        list_data = []
        for folder in list_itens:
            dict_data = self.get_dict(folder)
            list_data.append(dict_data)
        return list_data

    def find_folder_by_name(self, name, click=True):
        """
        _summary_
        find_folder_by_name('ADAMANTINA')

        :param name: _description_
        :type name: _type_
        :param click: _description_, defaults to True
        :type click: bool, optional
        :raises ValueError: _description_
        :return: _description_
        :rtype: _type_
        """
        # Conteúdo Principal
        content_xpath = self.driver.find_element(By.XPATH, "//*[@id='content']")

        try:
            foldername_xpath = content_xpath.find_element(
                By.XPATH, f".//span[text()='{name}']"
            )
            if click:
                foldername_xpath.click()
                time.sleep(1)
            return foldername_xpath

        except RuntimeError as e:
            raise ValueError(f"A very specific bad thing happened\n{e}")

    def save_dataframe(self, my_list, my_path):
        """
        _summary_

        :param my_list: _description_
        :type my_list: _type_
        :param my_path: _description_
        :type my_path: _type_
        """
        # Cria e Salva Tabela
        df = pd.DataFrame(my_list)
        df.to_csv(my_path / "links.csv", encoding="utf-8", index=False)
        return 0

    def get_list_municipios(self):
        list_subfolders = self.list_folders_h5ai()
        print(f"São  {len(list_subfolders)} pastas")
        pprint.pprint(list_subfolders[:5])

        list_municipios = [i["name"] for i in list_subfolders]
        list_municipios.sort()
        print(f"São {len(list_municipios)} municípios")
        pprint.pprint(list_municipios[:5])
        return list_municipios
