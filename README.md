# Ivoox-Downloader
Download a list or audiobook from www.ivoox.com easily

## Requirements:
1. Python 3.6.4+
2. Beautiful Soup 4

## Instructions

`python ivoox.py [-r] url name_of_program path_to_save`

Files will be save in path_to_save/name_of_program with name_of_program + number as a name (ex. Game_of_Thrones_001)
The order will be in reverse order to url (programs usually the last is the first in the page)
The flag -r name the files in order reversed , in this case normal order
The script supports url with multiple pages
