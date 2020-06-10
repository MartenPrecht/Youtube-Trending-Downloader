import requests
import urllib

from PIL import Image
from io import BytesIO

import re

from os import makedirs, getcwd, listdir
from os.path import isdir, join, exists
from shutil import copyfile

import json

import warnings

with open('config.json') as file:
    config = json.load(file)

data_path = join(getcwd(), config['data_path']) if not config['data_path'].startswith('/') else config['data_path']
countries = config['countries']

headers = {"Accept-Language": "en-US,en;q=0.5"}
video_re = 'data-context-item-id="([a-z A-Z 0-9 _ -]{11})"'

proerties = {
    'title': ('<title>', ' - YouTube</title>'),
    'chanel_id': ('<meta itemprop="channelId" content="', '">\n'),
    'chanel': ('Unsubscribe from ', '?')
}


def make_dir(path):
    try:
        makedirs(path)
    except FileExistsError:
        pass


def get_image(id) -> Image:
    """
    returns the videos thumbnails as Image for a given youtube video id
    """
    r = requests.get(f'https://i.ytimg.com/vi/{id}/hqdefault.jpg', headers=headers)
    img = Image.open(BytesIO(r.content))
    return img


def download_image(id, path=join(data_path, 'videos', 'thumbnails')):
    for i in range(2):
        try:
            urllib.request.urlretrieve(f'https://i.ytimg.com/vi/{id}/hqdefault.jpg', join(path, f'{id}.jpg'))
        except FileNotFoundError:
            makedirs(path)
        else:
            break


def get_tags(source):
    """
    returns a videos tags
    """
    return re.findall('<meta property="og:video:tag" content="([^\"]*)">', source)


def get_description(source) -> str:
    """
    returns the description of the video, if it is available in the given source
    """
    start_str = '<div id="watch-description-text" class=""><p id="eow-description" class="" >'
    end_str = '</p></div>'

    idx = source.find(start_str) + len(start_str)
    end = idx
    for _ in range(10000):
        if source[end: end + len(end_str)] != end_str:
            end += 1
        else:
            break
    else:
        return ''

    res = ''
    remove = False
    for e in source[idx: end]:
        if remove:
            if e == '>':
                remove = False
        else:
            if e == '<':
                remove = True
            else:
                res += e
    return res


def get_property(source, key):
    """
    returns the property the given source
    key in {'title', 'chanel_id', 'chanel'}
    """

    start_str, end_str = proerties[key]

    idx = source.find(start_str) + len(start_str)
    end = idx
    for _ in range(10000):
        if source[end: end + len(end_str)] != end_str:
            end += 1
        else:
            return source[idx: end]
    return None


def get_vid_info(id) -> dict:
    """
    returns the information of a given video
    """
    r = requests.get(f'https://www.youtube.com/watch?v={id}', headers=headers)
    source = r.content.decode('utf-8')

    info = {k: get_property(source, k) for k in proerties.keys()}
    info['tags'] = get_tags(source)
    info['description'] = get_description(source)
    return info


def save_vid_info(id, path=join(data_path, 'videos', 'info')):
    """
    saves the information of a given video in an id.json file
    """
    info = get_vid_info(id)
    for _ in range(2):
        try:
            with open(join(path, f'{id}.json'), 'w+') as file:
                json.dump(info, file)
        except FileNotFoundError:
            makedirs(path)
        else:
            break


def save_info_and_thumbnail(id):
    """
    saves information and thumbnail of a given video
    """
    try:
        download_image(id)
        save_vid_info(id)
    # somehow requests.exceptions.HTTPError cannot be caught differently TODO
    except Exception:
        pass


def save_new_info(ids, verbose=False):
    """
    saves the information fo videos that are in ids and have no stored information
    """
    for id in ids:
        if not exists(join(data_path, 'videos', 'info', f'{id}.json')):
            if verbose: print(f'\t{id}')
            save_info_and_thumbnail(id)


def save_ids_from_file(path_to_file, verbose=False):
    """
    reads a file of ids and saves their information if it is not already stored
    """
    with open(path_to_file) as file:
        ids = file.read().split(', ')
    save_new_info(ids, verbose=verbose)


def save_ids_from_folder(folder_path, verbose=False):
    """
    saves the information converning the video ods of all files in a given folder if it is not already saved
    """
    for filename in listdir(folder_path):
        if filename.endswith('.txt'):
            if verbose: print(join(folder_path, filename))
            save_ids_from_file(join(folder_path, filename), verbose=verbose)


def download_subscriptions_saves(root_path='data', verbose=False):
    """
    downloads the information of all videos-ids stored in subs.json
    """
    try:
        with open(join(root_path, 'subscriptions', 'subs.json')) as file:
            subs = json.load(file)
    except FileNotFoundError:
        # TODO create list of subs automatically once it is implemented
        warnings.warn('subs.json not found. Skipping the download of subscribed video information.'
                      '\n\tA future version will try to generate this data automatically.')
        return None

    for channel, ids in subs.items():
        if verbose: print(channel)
        for id in ids:
            if verbose: print('\t', id)
            save_new_info(id)


def update_video_saves(root_path='data', countries=None, verbose=False):
    """
    saves the video information for all countries and dates
    """
    countries = listdir(join(root_path, 'trending')) if countries is None else countries
    for id_type in {'trending', 'trending_recently'}:
        if exists(join(root_path, id_type)):
            for country in countries:
                for day in sorted(listdir(join(root_path, id_type, country))):
                    if verbose: print(f'{country}\t{day}')
                    save_ids_from_folder(join(root_path, id_type, country, day), verbose=verbose)
    download_subscriptions_saves(root_path=root_path, verbose=verbose)
