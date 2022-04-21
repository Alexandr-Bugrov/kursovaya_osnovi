import requests
import os
from pprint import pprint
import json


class YaUploader:
    def __init__(self, Yandextoken: str):
        self.Yandextoken = Yandextoken

    def get_headers(self):
        return {'Content-Type': 'application/json',
                'Authorization': f'OAuth {self.Yandextoken}'
                }

    def create_folder(self, file_folderYa: str):
        """Метод создает папку на яндекс диске по ее названию"""
        folder_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        folder_params = {'path': file_folderYa,
                         'overwrite': 'True'
                         }
        requests.put(folder_url, params=folder_params, headers=headers)


    def upload(self, file_pathYa: str, file):
        """Метод загружает фото на яндекс диск, используя название папки на яндекс диске и само фото.
        Возвращает HTTP код запроса"""
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'path': file_pathYa,
                  'overwrite': 'True'
                  }
        response = requests.get(upload_url, params=params, headers=headers)
        href_json = response.json()
        href = href_json['href']
        response = requests.put(href, data=file.content)
        response.raise_for_status()
        if response.status_code == 201:
            print('Загружено')
        return response.status_code


class VKuser:
    url = 'https://api.vk.com/method/'

    def __init__(self):
        self.VKtoken = 'a67f00c673c3d4b12800dd0ba29579ec56d804f3c5f3bbcef5328d4b3981fa5987b951cf2c8d8b24b9abd'
        self.version_API = '5.131'
        self.params = {
            'access_token': self.VKtoken,
            'v': self.version_API
        }

    def get_photos_json(self, user_id: str, count: str):
        """Метод получает фото из ВК по id пользователя и загружает их на яндекс диск"""
        get_photos_params = {'owner_id': user_id,
                             'extended': '1',
                             'album_id': 'profile',
                             'count': count,
                             'rev': '0'
                             }
        get_photos_url = self.url + 'photos.get'
        photos_params_json = requests.get(get_photos_url, params={**self.params, **get_photos_params}).json()
        pprint(photos_params_json)
        return photos_params_json


def get_photo_and_params(photos_params):
    '''Функция получает параметры фото из VK в формате json и возвращает фото наибольших размер из VK, его имя, и тип размера'''
    likes = photos_params['likes']['count']
    photo_url = photos_params['sizes'][-1]['url']
    photo_size = photos_params['sizes'][-1]['type']
    for size in photos_params['sizes']:
        if 'w' in size['type']:
            photo_url = size['url']
            photo_size = size['type']
    photo = requests.get(photo_url)
    FILE_NAME = f'{likes}.jpg'
    print(likes)
    print(photo_url)
    return {'name': FILE_NAME, 'content': photo, 'size': photo_size}


def upload_photos(photos_params_json, file_folderYa):
    '''Получает объект json из VK по методу photos.get, загружает фото на яндекс диск в указанную папку и
    создает json файл с параметрами фотографий, которые удалось загрузить'''
    i = 0
    uploaded_files_list = []
    for photo in photos_params_json['response']['items']:
        photo_items = get_photo_and_params(photo)
        i += 1
        downloading_status_code = userYa.upload(os.path.join(f'{file_folderYa}/', f'({i}){photo_items["name"]}'),
                                                photo_items['content'])
        if downloading_status_code == 201:
            show_uploaded_files(f'({i}){photo_items["name"]}', photo_items['size'], uploaded_files_list)
    uploaded_files_writer(uploaded_files_list)


def show_uploaded_files(photo_name, photo_size, uploaded_files_list):
    '''Помещает параметры фотографии в список, для последующего создания файла json'''
    photo_items = {}
    photo_items['file_name'] = photo_name
    photo_items['size'] = photo_size
    uploaded_files_list.append(photo_items)


def uploaded_files_writer(uploaded_files_list):
    '''Записывает подготовленный список в json файл'''
    with open('show_uploaded_files.json', 'w') as file:
        json.dump(uploaded_files_list, file, indent=2)


if __name__ == '__main__':
    user_id = '552934290'
    photos_count = '5'
    file_folderYa = 'photos'
    Yandextoken = ''
    userVK = VKuser()
    userYa = YaUploader(Yandextoken)
    userYa.create_folder(file_folderYa)
    upload_photos(userVK.get_photos_json(user_id, photos_count), file_folderYa)