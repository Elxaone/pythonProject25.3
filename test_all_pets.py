import pytest
import hashlib
import datetime
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By



email = "elhaelha@yandex.ru"
password = "franella"


def wait(driver, sec):
    return WebDriverWait(driver, sec)

@pytest.fixture(scope="session")
def get_data():
    """Возвращает элементы: инфо_пользователя, таблицу с питомцами и дату для логирования"""
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=chrome_options)
    # открываем страницу
    driver.get("https://petfriends.skillfactory.ru/")
    # жмем на зарегистрироваться
    driver.implicitly_wait(2)
    wait(driver, 2).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button[class$='btn-success']"))).click()
    # жмем на у меня уже есть аккаунт
    wait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//a[@href='/login']"))).click()
    # вводим email
    input_email = wait(driver, 2).until(EC.presence_of_element_located((By.ID, 'email')))
    input_email.send_keys(email)
    # вводим пароль
    input_pass = driver.find_element(By.ID, "pass")
    input_pass.send_keys(password)
    # нажимаем на "Enter" для входа в систему

    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    # кликаем по моим питомцам
    my_pets = wait(driver, 2).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/my_pets')]")))
    my_pets.click()
    # получим информацию о пользователе
    my_info = driver.find_elements(By.XPATH, "//div[contains(@class, 'left')]")
    # получим web объект строк тела списка питомцев
    tr_table_my_pets = driver.find_elements(By.XPATH, "//tbody//tr")
    # вернем количество питомцев у пользователя и тело данных петов (строки в таблице)
    # и время для логирования
    data = datetime.datetime.now().strftime('%H_%M_%S')
    yield my_info, tr_table_my_pets, data
    driver.quit()

class TestPetFriends():

    # 1. Получаем информацию о количестве моих питомцев.
    def test_compare_my_info_and_data_my_pets(self, get_data):
        my_info, tr_table_my_pets, date = get_data
        to_list_my_info = my_info[0].text.split("\n")
        count_my_pets_in_my_info = to_list_my_info[1]
        # обрежем строку до ":" включительно, удалим пробельные символы, и преобразуем данные в целое число
        count_my_pets_in_my_info = int(
            count_my_pets_in_my_info[count_my_pets_in_my_info.find(":") + 1:].replace(" ", ""))
        # запишем результаты в файл
        with open(f"log{date}.txt", "a") as file:
            print("="*80, file=file)
            print(f"Тест: {self.test_compare_my_info_and_data_my_pets.__name__}", file=file)
            print(f'Питомцев в инфо: {count_my_pets_in_my_info}\nв таблице: {len(tr_table_my_pets)}', file=file)
        # сверим всех питомцев
        assert count_my_pets_in_my_info == len(tr_table_my_pets)

    # 2. Получаем количество моих питомцев с фото и без
    def test_only_half_without_photos(self, get_data):
        _, tr_table_my_pets, date = get_data
        # получим фото
        count_with_a_foto = 0
        count_without_photos = 0
        for item in tr_table_my_pets:
            if item.find_element(By.XPATH, "th//img").get_attribute('src') == "":
                count_without_photos += 1
            else:
                count_with_a_foto += 1
        # запишем результаты в файл
        with open(f"log{date}.txt", "a") as file:
            print("="*80, file=file)
            print(f"Тест: {self.test_only_half_without_photos.__name__}", file=file)
            print(f"с фото = {count_with_a_foto}", f"без фото = {count_without_photos}", sep="\n", file=file)
        assert count_with_a_foto > count_without_photos


    # 3. Проверяем, что у всех моих питомцев есть имя, возраст, порода.
    def test_there_is_a_name_breed_age(self, get_data):
        _, tr_table_my_pets, date = get_data
        there_is_a_name_breed_age = True
        for i in range(len(tr_table_my_pets)):
            if not there_is_a_name_breed_age:
                break
            for j in range(1, 4):
                if tr_table_my_pets[i].find_element(By.XPATH, "td[{}]".format(j)).text == "":
                    there_is_a_name_breed_age = False
                    break
        # запишем результаты в файл
        with open(f"log{date}.txt", "a") as file:
            print("="*80, file=file)
            print(u"Тест: {}".format(self.test_there_is_a_name_breed_age.__name__), file=file)
            print(u"У всех питомцев есть имя, возраст и порода = {}".format(there_is_a_name_breed_age), file=file)

        assert there_is_a_name_breed_age

    # 4. Проверяем, что у всех питомцев разные имена.
    def test_all_names_are_different(self, get_data):
        _, tr_table_my_pets, date = get_data
        all_names_are_different = True
        list_names = []
        for i in range(len(tr_table_my_pets)):
            name = tr_table_my_pets[i].find_element(By.XPATH, "td[1]").text
            if name in list_names:
                all_names_are_different = False
                break
            list_names.append(name)
        # запишем результаты в файл
        with open(f"log{date}.txt", "a") as file:
            print("="*80, file=file)
            print(f"Тест: {self.test_all_names_are_different.__name__}", file=file)
            print(f"У всех питомцев разные имена = {all_names_are_different}", file=file)
        assert all_names_are_different

    # 5. Проверим, что среди моих питомцев нет повторяющихся.
    def test_there_are_no_duplicate_pets_in_the_list(self, get_data):
        _, tr_table_my_pets, date = get_data
        there_are_no_duplicate_pets_in_the_list = True
        list_data = []
        # собираем данные каждого питомца в одну строку
        for i in range(len(tr_table_my_pets)):
            if not there_are_no_duplicate_pets_in_the_list:
                break
            string = tr_table_my_pets[i].find_element(By.XPATH, "th//img").get_attribute('src')
            for j in range(1, 4):
                string += tr_table_my_pets[i].find_element(By.XPATH, "td[{}]".format(j)).text
            hash_string = hashlib.md5(string.encode())
            hash_dig = hash_string.hexdigest()
            if hash_dig in list_data:
                there_are_no_duplicate_pets_in_the_list = False
                list_data.append(hash_dig)
                break
            list_data.append(hash_dig)
        # запишем результаты в файл
        with open(f"log{date}.txt", "a") as file:
            print("="*80, file=file)
            print(f"Тест: {self.test_there_are_no_duplicate_pets_in_the_list.__name__}", file=file)
            print(f"Нет повторяющихся питомцев. = {there_are_no_duplicate_pets_in_the_list}", file=file)
        assert there_are_no_duplicate_pets_in_the_list


# pytest -v --driver Chrome --driver-path E:\chromedriver test_all_pets.py