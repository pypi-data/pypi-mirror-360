#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from pymeili.beautifyplot import (default,)
#from pymeili import beautifyplot as bp

__version__: str = '1.0.16'

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# 獲取當前檔案位址
currentfilepath = __file__

# 刪去__file__中最後面自"\"開始的字串(刪除檔名)
motherpath = currentfilepath[:-len(currentfilepath.split('/')[-1])]
ident = '/'

if motherpath == '': # 如果是空路徑，試著改成反斜線
    motherpath = currentfilepath[:-len(currentfilepath.split('\\')[-1])]
    ident = '\\'

# 檢查是否為空路徑
if motherpath == '':
    print(bcolors.FAIL+'[ERROR] Invalid installed module path. \nPlease install this module in a directory with no Chinese characters.'+bcolors.ENDC)
    motherpath = '.'

#print(bcolors.BOLD+'Expected clone destination path: '+bcolors.OKBLUE+f'{motherpath}  \\pymeili_resources'+bcolors.ENDC)


import os
# go to motherpath
os.chdir(motherpath)
# check if resources exists
if ident == '/':
    print(f'[HINT] Check if font files have been installed in '+bcolors.OKBLUE+f'{motherpath}/pymeili_resource'+bcolors.ENDC+' already.')
    if os.path.exists(f'{motherpath}/pymeili_resource'):
        pass
        print(f'[HINT] Font files have been installed in '+bcolors.OKBLUE+f'{motherpath}/pymeili_resource'+bcolors.ENDC+' already.')
    else:
    # clone github respository
        try:
            os.system(f'git clone https://github.com/VVVICTORZHOU/pymeili_resource.git')
            print(f'[HINT] Try to clone github font respository into {motherpath}.')
            print(f'[HINT] Make sure the font files are in the directory:\n\t 1. {motherpath}/pymeili_resource/futura medium bt.ttf\n\t 2. {motherpath}/pymeili_resource/Futura Heavy font.ttf\n\t 3. {motherpath}/pymeili_resource/Futura Extra Black font.ttf\n\t 4. {motherpath}/pymeili_resource/OCR-A Regular.ttf')
            print(bcolors.WARNING + f'[HINT] If no, please install all files in "pymeili_resource" manually from github: https://github.com/VVVICTORZHOU/pymeili_resource'+bcolors.ENDC)
        except:
            print(bcolors.FAIL+'[FATAL ERROR] Fail to clone github font respository into '+bcolors.OKBLUE+f'{motherpath}'+bcolors.ENDC)
            print(bcolors.WARNING + +'[FATAL ERROR] Please install all files in "pymeili_resource" manually from github: https://github.com/VVVICTORZHOU/pymeili_resource into'+bcolors.OKBLUE+f'{motherpath}'+bcolors.ENDC)
elif ident == '\\':
    print(f'[HINT] Check if font files have been installed in '+bcolors.OKBLUE+f'{motherpath}pymeili_resource'+bcolors.ENDC+' already.')
    if os.path.exists(f'{motherpath}pymeili_resource'):
        pass
        print(f'[HINT] Font files have been installed in '+bcolors.OKBLUE+f'{motherpath}pymeili_resource'+bcolors.ENDC+' already.')
    else:
    # clone github respository
        try:
            os.system(f'git clone https://github.com/VVVICTORZHOU/pymeili_resource.git')
            print(f'[HINT] Try to clone github font respository into {motherpath}.')
            print(f'[HINT] Make sure the font files are in the directory:\n\t 1. {motherpath}pymeili_resource\\futura medium bt.ttf\n\t 2. {motherpath}pymeili_resource\\Futura Heavy font.ttf\n\t 3. {motherpath}pymeili_resource\\Futura Extra Black font.ttf\n\t 4. {motherpath}pymeili_resource\\OCR-A Regular.ttf')
            print(bcolors.WARNING + f'[HINT] If no, please install all files in "pymeili_resource" manually from github: https://github.com/VVVICTORZHOU/pymeili_resource.git'+bcolors.ENDC)
        except:
            print(bcolors.FAIL+'[FATAL ERROR] Fail to clone github font respository into '+bcolors.OKBLUE+f'{motherpath}'+bcolors.ENDC)
            print(bcolors.WARNING + +'[FATAL ERROR] Please install all files in "pymeili_resource" manually from github:  https://github.com/VVVICTORZHOU/pymeili_resource.git'+bcolors.ENDC)    
else:
    print(bcolors.FAIL+'[inner FATAL ERROR] Invalid installed module path. \nPlease install this module in a directory with no Chinese characters.'+bcolors.ENDC)

from pymeili import beautifyplot as bp
