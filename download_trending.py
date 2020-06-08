
import requests
import re

from os import makedirs, getcwd
from os.path import isdir, join
import time

from util import countries, data_path

# if you dont want to use the config file specify it here
# countries = ['US', 'GB', 'DE', 'RU', 'AU', 'CA']
# data_path = join(getcwd(), 'data')

headers = {"Accept-Language": "en-US,en;q=0.5"}
video_re = 'data-context-item-id="([a-z A-Z 0-9 _ -]{11})"'


def remaining():
    """
    Calculate the time in seconds that is needed to reach the next full hour
    """
    return (60 - int(time.strftime('%M')))*60 - int(time.strftime('%S'))


def store(folder_name, data, country, data_path=data_path):
    """
    Writes a datum in the correct folder using the following structure (and creates the folders if necessary):
    data_path - folder_name - country - date - current_time.txt
    """
    try:
        with open(join(data_path, folder_name, country, time.strftime('%y%m%d'), time.strftime('%H')+'.txt'), 'w+') as file:
            file.write(', '.join(data))
    except FileNotFoundError:
        makedirs(join(data_path, folder_name, country, time.strftime('%y%m%d')))
        with open(join(data_path, folder_name, country, time.strftime('%y%m%d'), time.strftime('%H')+'.txt'), 'w+') as file:
            file.write(', '.join(data))
 
           
def store_trending(country, data_path=data_path, store_trending=True, store_trending_recently=False):
    """
    stores the trending data of a single country
    :param country:
    :return:
    """
    r = requests.get(f'https://www.youtube.com/feed/trending/?gl={country}', headers=headers)
    new, recently = r.content.decode('utf-8').split('Recently trending')

    if store_trending:
        new_vids = re.findall(video_re,  new)
        store('trending', new_vids, country, data_path=data_path)

    if store_trending_recently:
        recent_vids = re.findall(video_re, recently)
        store('trending_recently', recent_vids, country, data_path=data_path)


# stores the trending videos of the configured countries every full hour
if __name__ == "__main__":
    while True:
        for c in countries:
            store_trending(c)
        print(f'Saved at {time.strftime("%c")}')
        time.sleep(remaining())

