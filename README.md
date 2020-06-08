# Youtube-Trending-Downloader

The code in this repository can be used for the following two tasks:
- periodically download a list of (video IDs) of the current trending YouTube videos in a country of your choice
- download the video-description and thumbnail for a given video ID.

This project is the first part of youtube video rating algorithm. Once the project is in a presentable state I will link it here.

I have already gathered a couple of month worth of data using this tool and I am happy to share it with anyone interested in using it for their own projects.

## Downloader

The video-id downloader is provided in the download_trending.py file.
The target download folder and countries are stored in the config.json file.
If the file is run it will download the trending video-ids every hour until it is stopped.
It is recommended to run this file in a tmux shell when run for extended periods of time.

