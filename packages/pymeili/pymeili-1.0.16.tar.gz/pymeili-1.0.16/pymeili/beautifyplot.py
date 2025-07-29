# -*- coding:utf-8 -*-
'''
TODO 1: 檢查3D繪圖
'''
try:
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from pathlib import Path
    import matplotlib.font_manager as fm
    import matplotlib.tri as tri
    from matplotlib.colors import LinearSegmentedColormap
    from mpl_toolkits.basemap import Basemap
    from mpl_toolkits.mplot3d.axes3d import Axes3D
    import seaborn as sns
    import numpy as np
    import os
    from pymeili.cmapdict import cmaplist
    import cartopy
    import cartopy.feature as cfeature
    import cartopy.crs as ccrs
    from windrose import WindroseAxes
    from pymeili.richTable import printTable, getTableTime
    import imageio, glob

    # global variables
    global production_name, production_time
    production_name = []
    production_time = []
    

    # Fundamental Config
    currentfilepath = __file__
    
    # config.txt path
    motherpath = currentfilepath[:-len(currentfilepath.split('/')[-1])]
    if motherpath == '': # 使用反斜線
        motherpath = currentfilepath[:-len(currentfilepath.split('\\')[-1])]
        # if last character is '\', delete it
        if motherpath[-1] == '\\': motherpath = motherpath[:-1]
        configpath = motherpath + "\\pymeili_resource\\config.txt"
    else:
        configpath = motherpath + "/pymeili_resource/config.txt"
    
    
    #print(motherpath)
    if not os.path.isfile(configpath):
        raise FileNotFoundError(f"\033[41m[pymeili Error]\033[0m Config file not found: '{configpath}'; reinstall pymeili or manually move config file from github: https://github.com/VVVICTORZHOU/pymeili_resource into {motherpath}.")
    
    def inspect_resource():
        # print resource path
        if __file__[:-len(__file__.split('/')[-1])] == '':
            motherpath = __file__[:-len(__file__.split('\\')[-1])]
            # if last character is '\', delete it
            if motherpath[-1] == '\\': motherpath = motherpath[:-1]
            print(f"\033[44m[pymeili Info]\033[0m Resource path: {motherpath}\\pymeili_resource")
            #if not os.path.isfile(motherpath + "\\pymeili_resource"):
            #    # print warning
            #    print(f"\033[41m[pymeili Error]\033[0m Resource path not found: {motherpath}\\pymeili_resource; reinstall pymeili or manually move resource folder from github: https://github.com/VVVICTORZHOU/pymeili_resource into {motherpath}.")

        else:
            motherpath = __file__[:-len(__file__.split('/')[-1])]
            print(f"\033[44m[pymeili Info]\033[0m Resource path: {motherpath}/pymeili_resource")
            #if not os.path.isfile(motherpath + "/pymeili_resource"):
            #    # print warning
            #    print(f"\033[41m[pymeili Error]\033[0m Resource path not found: {motherpath}/pymeili_resource; reinstall pymeili or manually move resource folder from github:  https://github.com/VVVICTORZHOU/pymeili_resource into {motherpath}.")
                
    
    def read_config(line):
        content = np.loadtxt(configpath, dtype=str)
        try:
            if content[line][0:5] == "-----":
                raise TypeError(f"\033[45m[pymeili inner Error]\033[0m Config file error: get line number: {line+1} is a split line.")
            else: raise Exception
        except Exception:
            if content[line] == "one": return 1
            elif content[line] == "zero": return 0
            # 判斷是否為布林值
            if content[line] == "True" or content[line] == "1": return True
            elif content[line] == "False" or content[line] == "0": return False
            # 判斷是否為數字
            try:
                return int(content[line])
            except:
                # 如果開頭為@，則替換成#
                if content[line][0] == "@": content[line] = "#"+content[line][1:]
                # 如果含有空格的字串，將空格換成_
                if "_" in content[line]:
                    content[line] = content[line].replace("_", " ")
                return content[line]
            
    def save_config(line, newcontent):  
        content = np.loadtxt(configpath, dtype=str, delimiter=",")
        # 檢查長度
        if len(content) < line+1:
            raise TypeError(f"\033[45m[pymeili inner Error]\033[0m Config file error: get line number: {line+1} is out of range.")
        # 檢查是否為分隔線
        if content[line][0:5] == "-----":
            raise TypeError(f"\033[45m[pymeili inner Error]\033[0m Config file error: get line number: {line+1} is a split line.")
        # 檢查是否為布林值
        elif newcontent is True:
            content[line] = "True"
        elif newcontent is False:
            content[line] = "False"
        elif newcontent == 1:
            content[line] = "one"
        elif newcontent == 0:
            content[line] = "zero"
        # 檢查是否為數字
        elif type(newcontent) == int:
            content[line] = str(newcontent)
        elif type(newcontent) == float:
            # 如果小數點後為0，則轉成整數
            if newcontent % 1 == 0:
                newcontent = int(newcontent)
            else:
                content[line] = str(newcontent)
        # 檢查開頭是否為@，如果是，則替換成#
        elif newcontent[0] == "#":
            newcontent = "@"+newcontent[1:]
            content[line] = str(newcontent)       
        else:
            # 如果含有空格的字串，將空格換成_
            if " " in newcontent:
                newcontent = newcontent.replace(" ", "_")
            content[line] = str(newcontent)
            
        # 寫入
        np.savetxt(configpath, content, fmt="%s")

    def default():
        # set default config
        Mute().default()
        FontSize().default()
        FontScale().default()
        FontFamily().default()
        Theme().default()
        Linewidth().default()
        Color().default()
        if read_config(1) == False:
            print("\033[44m[pymeili Info]\033[0m All Configs are set to default.")
        return None
    
    # pymeili Info / Warning Mute
    class Mute:
        def __init__(self):
            self.info = read_config(1)
            self.warning = read_config(2)
            
        def __get__(self):
            return self
        
        def change(self, info=None, warning=None):
            if info:
                self.info = info
                save_config(1, info)
            if warning:
                self.warning = warning
                save_config(2, warning)
            
        def inspect(self):
            if read_config(1) == False:
                print("\033[44m[pymeili Info]\033[0m Mute Config: ")
                print(f"\tMute.info:\t\t{read_config(1)}")
                print(f"\tMute.warning:\t\t{read_config(2)}")
                
            
        def default(self):
            self.info = False
            self.warning = False
            save_config(1, False)
            save_config(2, False)
            
        def get(self, key):
            if key == "info": return read_config(1)
            elif key == "warning": return read_config(2)
            else: raise TypeError(f"\033[41m[pymeili Error]\033[0m Mute.get() got an unexpected keyword argument: '{key}'")

    # Fontsize Config
    class FontSize:
        def __init__(self):
            # Config default font size
            self.title = read_config(4)
            self.subtitle = read_config(5)
            self.label = read_config(6)
            self.ticklabel = read_config(7)
            self.clabel = read_config(8)
            self.legend = read_config(9)
            self.text = read_config(10)

        def change(self, title=None, subtitle=None, label=None, ticklabel=None, clabel=None, legend=None, text=None):
            if title:
                self.title = title
                save_config(4, title)
            if subtitle:
                self.subtitle = subtitle
                save_config(5, subtitle)
            if label:
                self.label = label
                save_config(6, label)
            if ticklabel:
                self.ticklabel = ticklabel
                save_config(7, ticklabel)
            if clabel:
                self.clabel = clabel
                save_config(8, clabel)
            if legend:
                self.legend = legend
                save_config(9, legend)
            if text:
                self.text = text
                save_config(10, text)

        def default(self):
            self.title = 30
            self.subtitle = 24
            self.label = 20
            self.ticklabel = 18
            self.clabel = 15
            self.legend = 20
            self.text = 20
            save_config(4, 30)
            save_config(5, 24)
            save_config(6, 20)
            save_config(7, 18)
            save_config(8, 18)
            save_config(9, 20)
            save_config(10, 20)

        def __getitem__(self):
            return self
        
        def get(self, key):
            if key == "title": return read_config(4)
            elif key == "subtitle": return read_config(5)
            elif key == "label": return read_config(6)
            elif key == "ticklabel": return read_config(7)
            elif key == "clabel": return read_config(8)
            elif key == "legend": return read_config(9)
            elif key == "text": return read_config(10)
            else: raise TypeError(f"\033[41m[pymeili Error]\033[0m FontSize.get() got an unexpected keyword argument: '{key}'")

        def inspect(self):
            if read_config(1) == False:
                print("\033[44m[pymeili Info]\033[0m Font Size Config: ")
                print(f"\tFontSize.title:\t\t{read_config(4)}")
                print(f"\tFontSize.subtitle:\t{read_config(5)}")
                print(f"\tFontSize.label:\t\t{read_config(6)}")
                print(f"\tFontSize.ticklabel:\t{read_config(7)}")
                print(f"\tFontSize.clabel:\t{read_config(8)}")
                print(f"\tFontSize.legend:\t{read_config(9)}")
                print(f"\tFontSize.text:\t\t{read_config(10)}")

    # Fontscale Config
    class FontScale:
        def __init__(self):
            self.scale = read_config(12)

        def __getitem__(self):
            return self

        def default(self):
            self.scale = 1.0
            save_config(12, 1.0)

        def change(self, scale):
            self.scale = scale
            save_config(12, scale)
        
        def get(self):
            return read_config(12)

        def inspect(self):
            if read_config(1) == False:
                print(f"\033[44m[pymeili Info]\033[0m Font Scale Config: {read_config(12)}")
    
    # True Fontsize = Fontsize * Fontscale
    def _GetFontSize_(key):
        if key in ["title", "subtitle", "label", "ticklabel", "clabel", "legend", "text"]:
            return FontSize().get(key) * FontScale().get()
        else: raise TypeError(f"\033[45m[pymeili inner Error]\033[0m GetFontSize() got an unexpected keyword argument: '{key}'")
    
    # Fontfamily Config
    class FontFamily:
        def __init__(self):
            # default fontpath
            motherpath = currentfilepath[:-len(currentfilepath.split('/')[-1])]
            if motherpath == '':
                motherpath = currentfilepath[:-len(currentfilepath.split('\\')[-1])]
                # if last character is '\', delete it
                if motherpath[-1] == '\\': motherpath = motherpath[:-1]
                fontfolder = motherpath + "\\pymeili_resource"
                self.fontpath_medium = Path(mpl.get_data_path(), fontfolder+"\\"+read_config(14))
                self.fontpath_bold = Path(mpl.get_data_path(), fontfolder+"\\"+read_config(15))
                self.fontpath_black = Path(mpl.get_data_path(), fontfolder+"\\"+read_config(16))
                self.fontpath_zh = Path(mpl.get_data_path(), fontfolder+"\\"+read_config(46))
                self.fontpath_special = Path(mpl.get_data_path(), fontfolder+"\\"+read_config(47))
                self.fontpath_zhbold = Path(mpl.get_data_path(), fontfolder+"\\"+read_config(48))
                self.fontpath_kl = Path(mpl.get_data_path(), fontfolder+"\\"+read_config(49))
                
            else:
                fontfolder = motherpath + "/pymeili_resource"
                self.fontpath_medium = Path(mpl.get_data_path(), fontfolder+"/"+read_config(14))
                self.fontpath_bold = Path(mpl.get_data_path(), fontfolder+"/"+read_config(15))
                self.fontpath_black = Path(mpl.get_data_path(), fontfolder+"/"+read_config(16))
                self.fontpath_zh = Path(mpl.get_data_path(), fontfolder+"/"+read_config(46))
                self.fontpath_special = Path(mpl.get_data_path(), fontfolder+"/"+read_config(47))
                self.fontpath_zhbold = Path(mpl.get_data_path(), fontfolder+"/"+read_config(48))
                self.fontpath_kl = Path(mpl.get_data_path(), fontfolder+"/"+read_config(49))

                
        def __getitem__(self):
            return self
        
        def default(self):
            save_config(14, "futura medium bt.ttf")
            save_config(15, "Futura Heavy font.ttf")
            save_config(16, "Futura_Extra_Black_font.ttf")
            save_config(46, "HarmonyOS_Sans_TC_Regular.ttf")
            save_config(47, "OCR-A Regular.ttf")
            save_config(48, "HarmonyOS_Sans_TC_Bold.ttf")
            save_config(49, "KleinCondensed-Medium.ttf")

        def get(self, key="medium"):
            motherpath = currentfilepath[:-len(currentfilepath.split('/')[-1])]
            if motherpath == '':
                motherpath = currentfilepath[:-len(currentfilepath.split('\\')[-1])]
                if motherpath[-1] == '\\': motherpath = motherpath[:-1]
                fontfolder = motherpath + "\\pymeili_resource"
                if key == "medium": return Path(mpl.get_data_path(), fontfolder+"\\"+read_config(14))
                elif key == "bold": return Path(mpl.get_data_path(), fontfolder+"\\"+read_config(15))
                elif key == "black": return Path(mpl.get_data_path(), fontfolder+"\\"+read_config(16))
                elif key == "zh": return Path(mpl.get_data_path(), fontfolder+"\\"+read_config(46))
                elif key == "special": return Path(mpl.get_data_path(), fontfolder+"\\"+read_config(47))
                elif key == "zhbold": return Path(mpl.get_data_path(), fontfolder+"\\"+read_config(48))
                elif key == "kl": return Path(mpl.get_data_path(), fontfolder+"\\"+read_config(49))
                else: raise TypeError(f"\033[41m[pymeili Error]\033[0m FontFamily.get() got an unexpected keyword argument: '{key}'. 'medium', 'bold', 'black', 'zh', 'special', 'zhbold' or 'kl' is valid.")
            else:
                fontfolder = motherpath + "/pymeili_resource"
                if key == "medium": return Path(mpl.get_data_path(), fontfolder+"/"+read_config(14))
                elif key == "bold": return Path(mpl.get_data_path(), fontfolder+"/"+read_config(15))
                elif key == "black": return Path(mpl.get_data_path(), fontfolder+"/"+read_config(16))
                elif key == "zh": return Path(mpl.get_data_path(), fontfolder+"/"+read_config(46))
                elif key == "special": return Path(mpl.get_data_path(), fontfolder+"/"+read_config(47))
                elif key == "zhbold": return Path(mpl.get_data_path(), fontfolder+"/"+read_config(48))
                elif key == "kl": return Path(mpl.get_data_path(), fontfolder+"/"+read_config(49))
                else: raise TypeError(f"\033[41m[pymeili Error]\033[0m FontFamily.get() got an unexpected keyword argument: '{key}'. 'medium', 'bold', 'black', 'zh', 'special', 'zhbold' or 'kl' is valid.")
        
        def change(self, medium=None, bold=None, black=None, zh=None, special=None):
            if medium:
                if not os.path.isfile(medium):
                    raise FileNotFoundError(f"\033[41m[pymeili Error]\033[0m FontFamily.change() got an invalid font path: '{medium}'. Full pathname of font file is required.")
                save_config(14, medium)
                self.fontpath_medium = Path(mpl.get_data_path(), medium)
            if bold:
                if not os.path.isfile(bold):
                    raise FileNotFoundError(f"\033[41m[pymeili Error]\033[0m FontFamily.change() got an invalid font path: '{bold}'. Full pathname of font file is required.")
                save_config(15, bold)
                self.fontpath_bold = Path(mpl.get_data_path(), bold)
            if black:
                if not os.path.isfile(black):
                    raise FileNotFoundError(f"\033[41m[pymeili Error]\033[0m FontFamily.change() got an invalid font path: '{black}'. Full pathname of font file is required.")
                save_config(16, black)
                self.fontpath_black = Path(mpl.get_data_path(), black)
            if zh:
                if not os.path.isfile(zh):
                    raise FileNotFoundError(f"\033[41m[pymeili Error]\033[0m FontFamily.change() got an invalid font path: '{zh}'. Full pathname of font file is required.")
                save_config(46, zh)
                self.fontpath_zh = Path(mpl.get_data_path(), zh)
            
    
        def inspect(self):
            if read_config(1) == False:
                print("\033[44m[pymeili Info]\033[0m Font Family Config: ")
                print(f"\tFontFamily.medium:\t{read_config(14)}")
                print(f"\tFontFamily.bold:\t{read_config(15)}")
                print(f"\tFontFamily.black:\t{read_config(16)}")
                print(f"\tFontFamily.zh:\t\t{read_config(46)}")
                print(f"\tFontFamily.special:\t{read_config(47)}")

    # Theme Config
    class Theme:
        def __init__(self):
            self.theme = read_config(18)
            
        def __getitem__(self):
            return self
        
        def default(self):
            self.theme = "light"
            save_config(18, "light")
            
        def switch(self):
            if self.theme == "light":
                self.theme = "dark"
                save_config(18, "dark")
            elif self.theme == "dark":
                self.theme = "light"
                save_config(18, "light")
        
        def get(self):
            return read_config(18)
        
        def change(self, theme):
            if theme == "light" or theme == "l" or theme == "white" or theme == "w" or theme == "default":
                self.theme = "light"
                save_config(18, "light")
            elif theme == "dark" or theme == "d" or theme == "black" or theme == "b":
                self.theme = "dark"
                save_config(18, "dark")
            else: raise TypeError(f"\033[41m[pymeili Error]\033[0m Theme.change() got an unexpected keyword argument: '{theme}'. 'light' or 'dark' is valid.")
    
        def inspect(self):
            if read_config(1) == False:
                print(f"\033[44m[pymeili Info]\033[0m Theme Config:{read_config(18)}")

    # Linewidth Config
    class Linewidth:
        def __init__(self):
            self.width = read_config(44)
        
        def __getitem__(self):
            return self
        
        def default(self):
            self.width = 2
            save_config(44, 2)
            
        def change(self, width):
            # make sure width is a int
            if type(width) != int:
                raise TypeError(f"\033[41m[pymeili Error]\033[0m Linewidth.change() got an unexpected keyword argument: '{width}'. int type is required.")
            self.width = width
            save_config(44, width)
        
        def get(self):
            return read_config(44)
        
        def inspect(self):
            if read_config(1) == False:
                print(f"\033[44m[pymeili Info]\033[0m Linewidth Config:{read_config(44)}")
            
    # Color Config
    class Color:
        def __init__(self):
            if Theme().get() == "light":
                self.bg = read_config(20)
                self.fg = read_config(21)
                self.bg2 = read_config(22)
                self.fg2 = read_config(23)
                self.fg3 = read_config(24)
                self.fg4 = read_config(25)
                self.fg5 = read_config(26)
                self.fg6 = read_config(27)
                self.fg7 = read_config(28)
                self.fg8 = read_config(29)
                self.fg9 = read_config(30)
            elif Theme().get() == "dark":
                self.bg = read_config(32)
                self.fg = read_config(33)
                self.bg2 = read_config(34)
                self.fg2 = read_config(35)
                self.fg3 = read_config(36)
                self.fg4 = read_config(37)
                self.fg5 = read_config(38)
                self.fg6 = read_config(39)
                self.fg7 = read_config(40)
                self.fg8 = read_config(41)
                self.fg9 = read_config(42)
                
        def __getitem__(self):
            return self
        
        def default(self):
            save_config(20, "#FFFFFF")
            save_config(21, "#000000")
            save_config(22, "#D7F0FB")
            save_config(23, "#10A0D0")
            save_config(24, "#AD025B")
            save_config(25, "#B59457")
            save_config(26, "#933318")
            save_config(27, "#007F00")
            save_config(28, "#FFA500")
            save_config(29, "#C0C1C0")
            save_config(30, "#000000")
            save_config(32, "#000000")
            save_config(33, "#FFFFFF")
            save_config(34, "#003264")
            save_config(35, "#10A0D0")
            save_config(36, "#AD025B")
            save_config(37, "#B59457")
            save_config(38, "#933318")
            save_config(39, "#007F00")
            save_config(40, "#FFA500")
            save_config(41, "#777777")
            save_config(42, "#FFFFFF")
            
        def change(self, bg=None, fg=None, bg2=None, fg2=None, fg3=None, fg4=None, fg5=None, fg6=None, fg7=None, fg8=None, fg9=None, theme=Theme().get()):
            if theme == "light" or theme == "l" or theme == "white" or theme == "w" or theme == "default":
                if bg:
                    self.bg = bg
                    save_config(20, bg)
                if fg:
                    self.fg = fg
                    save_config(21, fg)
                if bg2:
                    self.bg2 = bg2
                    save_config(22, bg2)
                if fg2:
                    self.fg2 = fg2
                    save_config(23, fg2)
                if fg3:
                    self.fg3 = fg3
                    save_config(24, fg3)
                if fg4:
                    self.fg4 = fg4
                    save_config(25, fg4)
                if fg5:
                    self.fg5 = fg5
                    save_config(26, fg5)
                if fg6:
                    self.fg6 = fg6
                    save_config(27, fg6)
                if fg7:
                    self.fg7 = fg7
                    save_config(28, fg7)
                if fg8:
                    self.fg8 = fg8
                    save_config(29, fg8)
                if fg9:
                    self.fg9 = fg9
                    save_config(30, fg9)
            elif theme == "dark" or theme == "d" or theme == "black" or theme == "b":
                if bg:
                    self.bg = bg
                    save_config(32, bg)
                if fg:
                    self.fg = fg
                    save_config(33, fg)
                if bg2:
                    self.bg2 = bg2
                    save_config(34, bg2)
                if fg2:
                    self.fg2 = fg2
                    save_config(35, fg2)
                if fg3:
                    self.fg3 = fg3
                    save_config(36, fg3)
                if fg4:
                    self.fg4 = fg4
                    save_config(37, fg4)
                if fg5:
                    self.fg5 = fg5
                    save_config(38, fg5)
                if fg6:
                    self.fg6 = fg6
                    save_config(39, fg6)
                if fg7:
                    self.fg7 = fg7
                    save_config(40, fg7)
                if fg8:
                    self.fg8 = fg8
                    save_config(41, fg8)
                if fg9:
                    self.fg9 = fg9
                    save_config(42, fg9)
            else: raise TypeError(f"\033[41m[pymeili Error]\033[0m Color.change() got an unexpected keyword argument: '{theme}'. 'light' or 'dark' is valid.")
            
        def inspect(self):
            if read_config(1) == False:
                print("\033[44m[pymeili Info]\033[0m Color Config: ")
                print("\tTheme:\t\t", 'Light(default):')
                print(f"\tColor.bg:\t{read_config(20)}")
                print(f"\tColor.fg:\t{read_config(21)}")
                print(f"\tColor.bg2:\t{read_config(22)}")
                print(f"\tColor.fg2:\t{read_config(23)}")
                print(f"\tColor.fg3:\t{read_config(24)}")
                print(f"\tColor.fg4:\t{read_config(25)}")
                print(f"\tColor.fg5:\t{read_config(26)}")
                print(f"\tColor.fg6:\t{read_config(27)}")
                print(f"\tColor.fg7:\t{read_config(28)}")
                print(f"\tColor.fg8:\t{read_config(29)}")
                print(f"\tColor.fg9:\t{read_config(30)}")
                print("\tTheme:\t\t", 'Dark:')
                print(f"\tColor.bg:\t{read_config(32)}")
                print(f"\tColor.fg:\t{read_config(33)}")
                print(f"\tColor.bg2:\t{read_config(34)}")
                print(f"\tColor.fg2:\t{read_config(35)}")
                print(f"\tColor.fg3:\t{read_config(36)}")
                print(f"\tColor.fg4:\t{read_config(37)}")
                print(f"\tColor.fg5:\t{read_config(38)}")
                print(f"\tColor.fg6:\t{read_config(39)}")
                print(f"\tColor.fg7:\t{read_config(40)}")
                print(f"\tColor.fg8:\t{read_config(41)}")
                print(f"\tColor.fg9:\t{read_config(42)}")
        
        def get(self, key):
            if key in ["bg", "fg", "bg2", "fg2", "fg3", "fg4", "fg5", "fg6", "fg7", "fg8", "fg9"]:
                if Theme().get() == "light":
                    return read_config(20+["bg", "fg", "bg2", "fg2", "fg3", "fg4", "fg5", "fg6", "fg7", "fg8", "fg9"].index(key))
                elif Theme().get() == "dark":
                    return read_config(32+["bg", "fg", "bg2", "fg2", "fg3", "fg4", "fg5", "fg6", "fg7", "fg8", "fg9"].index(key))
                
        def get_keys(self):
            return ["bg", "fg", "bg2", "fg2", "fg3", "fg4", "fg5", "fg6", "fg7", "fg8", "fg9"]
    
    # True Color
    def _GetColorCode_(key):
        # 檢查key的類型
        if type(key) == str:
            if key in ["bg", "fg", "bg2", "fg2", "fg3", "fg4", "fg5", "fg6", "fg7", "fg8", "fg9"]:
                return Color().get(key)
            elif key[0] == '#' and len(key) == 7:
                return key
            else: raise TypeError(f"\033[45m[pymeili inner Error]\033[0m GetColorCode() got an unexpected keyword argument: '{key}'")
        elif type(key) == list:
            for i in range(len(key)):
                if key[i] in ["bg", "fg", "bg2", "fg2", "fg3", "fg4", "fg5", "fg6", "fg7", "fg8", "fg9"]:
                    key[i] = Color().get(key[i])
                elif key[i][0] == '#' and len(key[i]) == 7:
                    pass
                else: raise TypeError(f"\033[45m[pymeili inner Error]\033[0m GetColorCode() got an unexpected keyword argument: '{key}'")
            return key
        else: raise TypeError(f"\033[45m[pymeili inner Error]\033[0m GetColorCode() got an unexpected keyword argument: '{key}'")
                
    
    # Initialize plot
    def initplot(ax=None, figsize=None, theme=Theme().get(), background=True):
        # set theme
        Theme().change(theme)
        
        # 如果沒有指定ax，則新增一個figure
        if ax is None: ax = plt.figure()
        
        # 檢查ax是否為plt.figure還是plt.subplot
        # 如果是plt.figure，則新增一個subplot
        if isinstance(ax, plt.Figure):
            # set figure.facecolor to bg
            ax.set_facecolor(_GetColorCode_("bg"))
            ax = ax.add_subplot(111)
            # 設定尺寸
            if figsize is not None:
                ax.figure.set_size_inches(figsize)

        # 如果是plt.Axes3D，則不做任何事
        elif isinstance(ax, Axes3D):
            # set facecolor to bg
            ax.figure.set_facecolor(_GetColorCode_("bg"))
            # 設定尺寸
            if figsize is not None:
                ax.figure.set_size_inches(figsize)

        # 如果是plt.subplot，則不做任何事
        elif isinstance(ax, plt.Axes):
            # set facecolor to bg
            ax.figure.set_facecolor(_GetColorCode_("bg"))
            # 設定尺寸
            if figsize is not None:
                ax.figure.set_size_inches(figsize)
                
        # 如果是windrose.WindroseAxes.則不做任何事        
        elif isinstance(ax, WindroseAxes):
            ax.figure.set_facecolor(_GetColorCode_("bg"))
        # 如果是mpl_toolkits.basemap.Basemap，則不做任何事
        elif type(ax) == Basemap:
            # 設定尺寸
            if figsize is not None:
                pass
                #plt.figure(figsize=figsize, facecolor=_GetColorCode_("bg"))
        # 如果是cartopy.mpl.geoaxes.GeoAxes，則不做任何事
        elif isinstance(ax, cartopy.mpl.geoaxes.GeoAxesSubplot):
            # set facecolor to bg
            ax.figure.set_facecolor(_GetColorCode_("bg"))
            # 設定尺寸
            if figsize is not None:
                pass
                #plt.figure(figsize=figsize, facecolor=_GetColorCode_("bg"))
        else:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m initplot() got an unexpected keyword argument: ax='{ax}'. plt.figure, plt.subplot, cartopy, Basemap or Windrose are allowed.")

        # set ax to global
        global _ax_
        _ax_ = ax
        
        # set facecolor to bg2
        if isinstance(ax, Axes3D):
            if background:
                ax.xaxis.pane.set_facecolor(_GetColorCode_("bg2"))
                ax.yaxis.pane.set_facecolor(_GetColorCode_("bg2"))
                ax.zaxis.pane.set_facecolor(_GetColorCode_("bg2"))
        elif isinstance(ax, plt.Axes):
            if background: _ax_.set_facecolor(_GetColorCode_("bg2"))
        elif isinstance(ax, WindroseAxes):
            ax.set_facecolor(_GetColorCode_("bg2"))
        elif type(ax) == Basemap:
            if background:
                # set ocean background color in basemap
                _ax_.drawmapboundary(fill_color=_GetColorCode_("bg2"))
                # set land background color in basemap
                _ax_.fillcontinents(color=_GetColorCode_("bg"), lake_color=_GetColorCode_("bg2"))       
        elif type(ax) == cartopy.mpl.geoaxes.GeoAxesSubplot:
            if background:
                # set ocean background color in cartopy
                ax.add_feature(cfeature.NaturalEarthFeature(category='physical', name='ocean', scale='50m', facecolor=_GetColorCode_("bg2")))
                # set land background color in cartopy
                ax.add_feature(cfeature.NaturalEarthFeature(category='physical', name='land', scale='50m', facecolor=_GetColorCode_("bg")))
        else:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m initplot() got an unexpected type of argument: ax='{ax}'. plt.figure, plt.subplot, cartopy, Basemap or Windrose are allowed.")

        return _ax_
    
    # Subplot
    def subplot(*args, **kwargs):
        global _ax_
        _ax_ = plt.subplot(*args, **kwargs)
        return _ax_
    
    # 更改當前預設Axes
    def setax(ax):
        global _ax_
        _ax_ = ax
        return _ax_
    
    # Basic Function for plot
    def plot(x=0, y=0, ax=None, color="fg", linestyle="-", linewidth=None, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        ax.plot(x, y, color=_GetColorCode_(color), linestyle=linestyle, linewidth=linewidth, **kwargs)
        return ax
    
    def contour(x=0, y=0, z=0, ax=None, color="fg", colors=None, linewidth=None, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        if colors==None:
                colors = _GetColorCode_(color)
        else:
            colors = _GetColorCode_(colors)
        
        global CT
        CT = ax.contour(x, y, z, colors=colors, linewidths=linewidth, **kwargs)
        return ax
    
    def clabel(ax=None, fontsize=None, **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("clabel")
        global _ax_
        if ax is None: ax = _ax_
        CL = ax.clabel(CT, **kwargs)
        for t in CL:
            t.set_font_properties(fm.FontProperties(fname=FontFamily().get("medium"), size=fontsize))
        return ax
    
    def contourf(x=0, y=0, z=0, ax=None, cmap=None, colors=None, returnCTF=False, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if colors is None:
            if cmap is None:
                cmap = _GetColorCode_("fg") # 什麼都沒說，就用fg
            else:
                cmap = cmaplist(cmap) # cmap可為字串(關鍵字)或是list(自定義)，colors為None，則使用cmap
        else:
            if cmap is None:
                colors = _GetColorCode_(colors) # cmap為None，colors不為None，則使用colors
            else: # 同時指定cmap和colors，則報錯
                raise TypeError(f"\033[41m[pymeili Error]\033[0m contourf() got an unexpected keyword argument: 'cmap' and 'colors' cannot be specified at the same time.")
        
        global CTF
        if cmap is None:
            CTF = ax.contourf(x, y, z, colors=colors, **kwargs)
        if colors is None:
            CTF = ax.contourf(x, y, z, cmap=cmap, **kwargs)
        if returnCTF:
            return CTF
        else:
            return ax
    def tricontour(x=0, y=0, z=0, ax=None, color="fg", colors=None, linewidth=None, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        if colors is None:
            colors = _GetColorCode_(color)
        else:
            colors = _GetColorCode_(colors)
        
        global CT
        CT = ax.tricontour(x, y, z, colors=colors, linewidths=linewidth, **kwargs)
        return ax
    
    def tricontourf(x=0, y=0, z=0, ax=None, cmap=None, colors=None, linewidth=None, returnCTF=False, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        if colors is None:
            if cmap is None:
                cmap = _GetColorCode_("fg") # 什麼都沒說，就用fg
            else:
                cmap = cmaplist(cmap)
        else:
            if cmap is None:
                colors = _GetColorCode_(colors)
            else: # 同時指定cmap和colors，則報錯
                raise TypeError(f"\033[41m[pymeili Error]\033[0m tricontourf() got an unexpected keyword argument: 'cmap' and 'colors' cannot be specified at the same time.")
        global CTF
        if cmap is None:
            CTF = ax.tricontourf(x, y, z, colors=colors, linewidths=linewidth, **kwargs)
        if colors is None:
            CTF = ax.tricontourf(x, y, z, cmap=cmap, linewidths=linewidth, **kwargs)
        if returnCTF:
            return CTF
        else:
            return ax
    
    def colorbar(ax=None, label='', ticks=None, labelsize=None, ticklabelsize=None, color=None, linewidth=None, shrink=0.95, aspect=15, fraction=0.05, pad=0.04, inputCTF=False, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if labelsize is None: labelsize=_GetFontSize_("clabel")
        if ticklabelsize is None: ticklabelsize=_GetFontSize_("ticklabel")
        if color is None: color=_GetColorCode_("fg")
        if linewidth is None: linewidth=Linewidth().get()
        if ticks is None: ticks = np.linspace(CTF.get_clim()[0], CTF.get_clim()[1], 5)
        # 檢測ax是否為Basemap，如果是，則報錯；這裡只能用plt.axes()或plt.subplot()來生成ax
        if type(ax) == Basemap:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m colorbar() got an unexpected keyword argument: 'ax' cannot be Basemap, use plt.axes() or plt.subplot() instead.")
        if inputCTF:
            try:
                CB = plt.colorbar(inputCTF, ax=ax, shrink=shrink, aspect=aspect, fraction=fraction, pad=pad, ticks=ticks,  **kwargs)
            except:
                raise TypeError(f"\033[41m[pymeili Error]\033[0m colorbar() got an unexpected keyword argument: 'inputCTF'. inputCTF must be a return value of contourf(returnCTF=True); otherwise, set inputCTF to False.")
        else:
            CB = plt.colorbar(CTF, ax=ax, shrink=shrink, aspect=aspect, fraction=fraction, pad=pad, ticks=ticks,  **kwargs)
        CB.set_label(label, fontproperties=fm.FontProperties(fname=FontFamily().get("medium"), size=labelsize), color=color)
        CB.ax.xaxis.set_tick_params(color=color, labelsize=ticklabelsize, width=linewidth)
        CB.ax.yaxis.set_tick_params(color=color, labelsize=ticklabelsize, width=linewidth)
        CB.outline.set_edgecolor(color)
        CB.ax.xaxis.label.set_font_properties(fm.FontProperties(fname=FontFamily().get("medium"), size=labelsize))
        CB.ax.xaxis.label.set_color(color)
        CB.outline.set_linewidth(linewidth)
        CB.ax.yaxis.label.set_font_properties(fm.FontProperties(fname=FontFamily().get("medium"), size=labelsize))
        CB.ax.yaxis.label.set_color(color)
        CB.ax.set_yticklabels(CB.ax.get_yticklabels(), color=color)
        for l in CB.ax.yaxis.get_ticklabels():
            l.set_font_properties(fm.FontProperties(fname=FontFamily().get("medium"), size=ticklabelsize))
        for l in CB.ax.xaxis.get_ticklabels():
            l.set_font_properties(fm.FontProperties(fname=FontFamily().get("medium"), size=ticklabelsize))
        
        return ax
    
    def bar(x=0, y=0, ax=None, color="fg", width=0.8, edgewidth=Linewidth().get(), edgecolor="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.bar(x, y, color=_GetColorCode_(color), width=width, edgecolor=_GetColorCode_(edgecolor), linewidth=edgewidth, **kwargs)
        return ax
    
    def barh(x=0, y=0, ax=None, color="fg", height=0.8, edgewidth=Linewidth().get(), edgecolor="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.barh(x, y, color=_GetColorCode_(color), height=height, edgecolor=_GetColorCode_(edgecolor), linewidth=edgewidth, **kwargs)
        return ax
    
    def hist(x=0, ax=None, color="fg", bins=10, linewidth=None, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        ax.hist(x, color=_GetColorCode_(color), bins=bins, linewidth=linewidth, **kwargs)
        return ax
    
    def hist2d(x=0, y=0, ax=None, color="fg", bins=10, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.hist2d(x, y, color=_GetColorCode_(color), bins=bins, **kwargs)
        return ax
    
    def scatter(x=0, y=0, ax=None, color="fg", marker="o", s=20, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.scatter(x, y, color=_GetColorCode_(color), marker=marker, s=s, **kwargs)
        return ax
    
    def pie(x=0, ax=None, startangle=90, pctdistance=0.6, labeldistance=1.1, radius=1, labelsize=None, labelcolor="fg", widgesize=None, widgescolor="fg", counterclock=True, edgewidth=Linewidth().get(), edgecolor="bg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if labelsize is None: labelsize=_GetFontSize_("label")
        if widgesize is None: widgesize=_GetFontSize_("label")
        ax.pie(x, startangle=startangle, pctdistance=pctdistance, labeldistance=labeldistance, radius=radius, counterclock=counterclock, wedgeprops={'linewidth':edgewidth, 'edgecolor':_GetColorCode_(edgecolor)}, textprops={'fontsize':labelsize, 'color':_GetColorCode_(labelcolor)}, **kwargs)
        ax.axis('equal')
        return ax
    
    def polar(theta=0, r=0, ax=None, color="fg", linewidth=None, linestyle="-", **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        ax.plot(theta, r, color=_GetColorCode_(color), linewidth=linewidth, linestyle=linestyle, **kwargs)
        return ax
    
    def boxplot(x=0, ax=None, vert=True, patch_artist=True, showmeans = True, showcaps = True, showbox = True, widths = 0.5, boxfacecolor="fg8", boxedgecolor="fg", boxlinewidth=Linewidth().get(), mediancolor="fg2", medianlinewidth=Linewidth().get(), meanmarker="o", meanmarkersize=5, meanmarkercolor="fg3", meanmarkeredgecolor="fg3", meanmarkerlinewidth=Linewidth().get(), whiskercolor="fg4", whiskerlinewidth=Linewidth().get(), capsize=3, capthick=Linewidth().get(), fliermarker="o", fliermarkersize=5, fliermarkercolor="fg5", fliermarkeredgecolor="fg5", fliermarkerlinewidth=Linewidth().get(), **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        boxprops = dict(linewidth=boxlinewidth, edgecolor=_GetColorCode_(boxedgecolor), facecolor=_GetColorCode_(boxfacecolor))
        medianprops = dict(linewidth=medianlinewidth, color=_GetColorCode_(mediancolor))
        meanprops = dict(marker=meanmarker, markerfacecolor=_GetColorCode_(meanmarkercolor), markeredgecolor=_GetColorCode_(meanmarkeredgecolor), markeredgewidth=meanmarkerlinewidth, markersize=meanmarkersize)
        whiskerprops = dict(linewidth=whiskerlinewidth, color=_GetColorCode_(whiskercolor))
        capprops = dict(linewidth=capthick, color=_GetColorCode_(whiskercolor))
        flierprops = dict(marker=fliermarker, markerfacecolor=_GetColorCode_(fliermarkercolor), markeredgecolor=_GetColorCode_(fliermarkeredgecolor), markeredgewidth=fliermarkerlinewidth, markersize=fliermarkersize)
        ax.boxplot(x, vert=vert, patch_artist=patch_artist, showmeans=showmeans, showcaps=showcaps, showbox=showbox, widths=widths, boxprops=boxprops, medianprops=medianprops, meanprops=meanprops, whiskerprops=whiskerprops, capprops=capprops, flierprops=flierprops, **kwargs)
        return ax
    
    def text(x=0, y=0, s='', ax=None, fontsize=None, color="fg", fonttype="medium", **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("text")
        if fonttype not in ["medium", "bold", "black", "zh", "special", "zhbold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'medium', 'bold', 'black', 'zh', 'special', 'zhbold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        ax.text(x, y, s, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        return ax
    
    def textbox(x=0, y=0, s='', ax=None, fontsize=None, color="fg", fonttype="medium", boxcolor="bg", boxalpha=1, boxpad=0.3, fill=True, edgewidth=None, mutation_aspect=None, **kwargs):
        if edgewidth is None: edgewidth=Linewidth().get()
        if fontsize is None: fontsize=_GetFontSize_("text")
        if fonttype not in ["medium", "bold", "black", "zh", "special", "zhbold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'medium', 'bold', 'black', 'zh', 'special', 'zhbold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        if mutation_aspect is None:
            boxstyle="square"
            ax.text(x, y, s, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), bbox=dict(boxstyle=boxstyle, facecolor=_GetColorCode_(boxcolor), alpha=boxalpha, pad=boxpad, linewidth=edgewidth, fill=fill), **kwargs)
        else:
            boxstyle="round"
            ax.text(x, y, s, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), bbox=dict(boxstyle=boxstyle, facecolor=_GetColorCode_(boxcolor), alpha=boxalpha, pad=boxpad, linewidth=edgewidth, fill=fill, mutation_aspect=mutation_aspect), **kwargs)
    
    def annotate_wedge(s='', xy=(0, 0), xytext=(0, 0), ax=None, fontsize=None, color="fg", arrowcolor="fg", fonttype="medium", boxcolor="bg", boxalpha=1, boxpad=0.3, fill=True, edgewidth=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if edgewidth is None: edgewidth=Linewidth().get()
        if fontsize is None: fontsize=_GetFontSize_("text")
        if fonttype not in ["medium", "bold", "black", "zh", "special", "zhbold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'medium', 'bold', 'black', 'zh', 'special', 'zhbold' or 'kl' is valid.")
        ax.annotate(s, xy=xy, xytext=xytext, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), arrowprops=dict(arrowstyle="wedge", color=_GetColorCode_(arrowcolor), linewidth=edgewidth), bbox=dict(boxstyle="square", facecolor=_GetColorCode_(boxcolor), alpha=boxalpha, pad=boxpad, linewidth=edgewidth, fill=fill), **kwargs)
    
    def fill_between(x=0, y1=0, y2=0, ax=None, color="fg", alpha=0.5, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.fill_between(x, y1, y2, color=_GetColorCode_(color), alpha=alpha, **kwargs)
        return ax
    
    def fill_betweenx(x1=0, x2=0, y=0, ax=None, color="fg", alpha=0.5, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.fill_betweenx(x1, x2, y, color=_GetColorCode_(color), alpha=alpha, **kwargs)
        return ax
    
    def axhline(y=0, ax=None, color="fg", linestyle="-", linewidth=None, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        ax.axhline(y, color=_GetColorCode_(color), linestyle=linestyle, linewidth=linewidth, **kwargs)
        return ax
    
    def axvline(x=0, ax=None, color="fg", linestyle="-", linewidth=None, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        ax.axvline(x, color=_GetColorCode_(color), linestyle=linestyle, linewidth=linewidth, **kwargs)
        return ax
    
    def legend(label=None ,ax=None, fontsize=None, color="fg", frameon=True, framealpha=1, facecolor="bg", edgecolor="fg", edgewidth=None, **kwargs):
        if edgewidth is None: edgewidth=Linewidth().get()
        if fontsize is None: fontsize=_GetFontSize_("legend")
        global _ax_
        if ax is None: ax = _ax_
        if label is None:
            if 'zorder' in kwargs:
                print("\033[43m[pymeili Warning]\033[0m legend() got an unexpected keyword argument: 'zorder' is not recommended in legend().")
                zorder = kwargs['zorder']
                kwargs.pop('zorder')
                LG = ax.legend(fontsize=fontsize, labelcolor=_GetColorCode_(color), frameon=frameon, framealpha=framealpha, facecolor=_GetColorCode_(facecolor), edgecolor=_GetColorCode_(edgecolor), prop=fm.FontProperties(fname=FontFamily().get("medium"), size=fontsize), **kwargs)
                LG.set_zorder(zorder)
            else:
                LG = ax.legend(fontsize=fontsize, labelcolor=_GetColorCode_(color), frameon=frameon, framealpha=framealpha, facecolor=_GetColorCode_(facecolor), edgecolor=_GetColorCode_(edgecolor), prop=fm.FontProperties(fname=FontFamily().get("medium"), size=fontsize), **kwargs)
            
        else:
            if 'zorder' in kwargs:
                print("\033[43m[pymeili Warning]\033[0m legend() got an unexpected keyword argument: 'zorder' is not recommended in legend().")
                zorder = kwargs['zorder']
                kwargs.pop('zorder')
                LG = ax.legend(label, fontsize=fontsize, labelcolor=_GetColorCode_(color), frameon=frameon, framealpha=framealpha, facecolor=_GetColorCode_(facecolor), edgecolor=_GetColorCode_(edgecolor), prop=fm.FontProperties(fname=FontFamily().get("medium"), size=fontsize), **kwargs)
                LG.set_zorder(zorder)
            else:
                LG = ax.legend(label, fontsize=fontsize, labelcolor=_GetColorCode_(color), frameon=frameon, framealpha=framealpha, facecolor=_GetColorCode_(facecolor), edgecolor=_GetColorCode_(edgecolor), prop=fm.FontProperties(fname=FontFamily().get("medium"), size=fontsize), **kwargs)
        
        LG.get_frame().set_boxstyle('Round', pad=0.2, rounding_size=-0.01)
        LG.get_frame().set_linewidth(edgewidth)

        return ax
    
    def addlogo(logopath, x, y, width, height, alpha=1, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.imshow(logopath, extent=[x, x+width, y, y+height], alpha=alpha, **kwargs)
        return ax
    
    def barbs(x=0, y=0, u=0, v=0, ax=None, length=7, pivot='tip', c=None, barbcolor="fg", flagcolor="fg", cmap=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if c == 'auto':
            c = np.sqrt(u**2+v**2)
        if cmap is not None:
            global CTF
            cmap = cmaplist(cmap)
            CTF = ax.barbs(x, y, u, v, length=length, pivot=pivot, color=_GetColorCode_(barbcolor), flagcolor=_GetColorCode_(flagcolor), cmap=cmap, **kwargs)
            return ax
        if cmap is None:
            ax.barbs(x, y, u, v, length=length, pivot=pivot, color=_GetColorCode_(barbcolor), flagcolor=_GetColorCode_(flagcolor), **kwargs)
            return ax
        
    def quiver(x=0, y=0, u=0, v=0, ax=None, color="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if 'cmap' in kwargs:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m quiver() got an unexpected keyword argument: 'cmap' is not allowed in quiver(), use barbs() instead.")
        ax.quiver(x, y, u, v, color=_GetColorCode_(color), **kwargs)
        return ax
    
    def streamplot(x=0, y=0, u=0, v=0, ax=None, color="fg", linewidth=None, arrowstyle="-|>", arrowsize=1, density=1, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        ax.streamplot(x, y, u, v, color=_GetColorCode_(color), linewidth=linewidth, arrowstyle=arrowstyle, arrowsize=arrowsize, density=density, **kwargs)
        return ax
    
    # Addtional Function for plot
    def inset_axes(bound, ax=None, **kwargs):
        global _ax_
        if bound==None: bound=[0.05, 0.05, 0.9, 0.9]
        if ax is None: ax = _ax_
        axins = ax.inset_axes(bound, **kwargs)
        return axins  
    
    def title(s='', ax=None, fontsize=None, color="fg", fonttype="bold", **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("title")
        if fonttype not in ["medium", "bold", "black", "zh", "special", "zhbold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'medium', 'bold', 'black', 'zh', 'special', 'zhbold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        ax.figure.suptitle(s, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        return ax
    
    def lefttitle(s='', ax=None, fontsize=None, color="fg2", fonttype="bold", loc='left', **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("title")
        if fonttype not in ["medium", "bold", "black", "zh", "special", "zhbold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'medium', 'bold', 'black', 'zh', 'special', 'zhbold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        ax.set_title(s, loc=loc, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        return ax
    
    def centertitle(s='', ax=None, fontsize=None, color="fg", fonttype="bold", loc='center', **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("title")
        if fonttype not in ["medium", "bold", "black", "zh", "special", "zhbold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'medium', 'bold', 'black', 'zh', 'special', 'zhbold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        ax.set_title(s, loc=loc, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        return ax
    
    def righttitle(s='', ax=None, fontsize=None, color="fg3", fonttype="bold", loc='right', **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("title")
        if fonttype not in ["medium", "bold", "black", "zh", "special", "zhbold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'medium', 'bold', 'black', 'zh', 'special', 'zhbold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        ax.set_title(s, loc=loc, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        return ax
    
    def xlabel(s='', ax=None, fontsize=None, color="fg", fonttype="medium", top=False, **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("label")
        if fonttype not in ["medium", "bold", "black", "zh", "special"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m xlabel() got an unexpected keyword argument: fonttype='{fonttype}'.'medium', 'bold', 'black', 'zh' or 'special' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        ax.set_xlabel(s, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        if top:
            ax.tick_params(axis='x', labeltop=True)
            ax.xaxis.set_label_position('top')
            ax.xaxis.set_ticks_position('top')
        return ax
    
    def ylabel(s='', ax=None, fontsize=None, color="fg", fonttype="medium", right=False, **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("label")
        if fonttype not in ["medium", "bold", "black", "zh", "special"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m ylabel() got an unexpected keyword argument: fonttype='{fonttype}'. 'medium', 'bold', 'black', 'zh' or 'special' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        ax.set_ylabel(s, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        if right:
            ax.tick_params(axis='y', labelright=True)
            ax.yaxis.set_label_position('right')
            ax.yaxis.set_ticks_position('right')
        return ax
    
    def spines(top=True, right=True, bottom=True, left=True, ax=None, color='fg', linewidth=Linewidth().get(), **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if top:
            ax.spines['top'].set_color(_GetColorCode_(color))
            ax.spines['top'].set_linewidth(linewidth)
            ax.spines['top'].set_visible(True)
        if right:
            ax.spines['right'].set_color(_GetColorCode_(color))
            ax.spines['right'].set_linewidth(linewidth)
            ax.spines['right'].set_visible(True)
        if bottom:
            ax.spines['bottom'].set_color(_GetColorCode_(color))
            ax.spines['bottom'].set_linewidth(linewidth)
            ax.spines['bottom'].set_visible(True)
        if left:
            ax.spines['left'].set_color(_GetColorCode_(color))
            ax.spines['left'].set_linewidth(linewidth)
            ax.spines['left'].set_visible(True)
            
    def grid(ax=None, which='major', axis='both', color='fg8', linestyle=':', linewidth=Linewidth().get(), **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.grid(which=which, axis=axis, color=_GetColorCode_(color), linestyle=linestyle, linewidth=linewidth, **kwargs)
        return ax 
            
    def xticks(ticks=None, labels='auto', ax=None, fontsize=None, color="fg", fonttype="medium", linewidth=Linewidth().get(), linelengths=5, top=False, direction='out', which='both', pad=5, **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("ticklabel")
        if fonttype not in ["medium", "bold", "black", "zh", "special", "zhbold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'medium', 'bold', 'black', 'zh', 'special', 'zhbold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        if ticks is None:
            ax.set_xticks([])
        else:
            ax.set_xticks(ticks)
        if labels is None:
            ax.set_xticklabels([])
        elif labels == 'auto':
            labels = [tick for tick in ticks]
            # transform ticks to str
            for i in range(len(labels)):
                labels[i] = str(labels[i])
            ax.set_xticklabels(labels, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
            ax.tick_params(axis='x', which=which, direction=direction, length=linelengths, width=linewidth, color=_GetColorCode_(color), top=top, pad=pad)
        else:
            ax.set_xticklabels(labels, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
            ax.tick_params(axis='x', which=which, direction=direction, length=linelengths, width=linewidth, color=_GetColorCode_(color), top=top, pad=pad)
        return ax
    
    def yticks(ticks=None, labels='auto', ax=None, fontsize=None, color="fg", fonttype="medium", linewidth=Linewidth().get(), linelengths=5, right=False, direction='out', which='both', pad=5, **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("ticklabel")
        if fonttype not in ["medium", "bold", "black", "zh", "special", "zhbold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'medium', 'bold', 'black', 'zh', 'special', 'zhbold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        if ticks is None:
            ax.set_yticks([])
        else:
            ax.set_yticks(ticks)
        if labels is None:
            ax.set_yticklabels([])
        elif labels == 'auto':
            labels = [tick for tick in ticks]
            # transform ticks to str
            for i in range(len(labels)):
                labels[i] = str(labels[i])
            ax.set_yticklabels(labels, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
            ax.tick_params(axis='y', which=which, direction=direction, length=linelengths, width=linewidth, color=_GetColorCode_(color), right=right, pad=pad)
        else:
            ax.set_yticklabels(labels, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
            ax.tick_params(axis='y', which=which, direction=direction, length=linelengths, width=linewidth, color=_GetColorCode_(color), right=right, pad=pad)
        return ax
    
    def xscale(scale='log', base=10, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.set_xscale(scale, base, **kwargs)
        return ax
    
    def yscale(scale='log', base=10, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.set_yscale(scale, base, **kwargs)
        return ax
    
    def xlim(xmin=None, xmax=None, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.set_xlim(xmin, xmax, **kwargs)
        return ax
    
    def ylim(ymin=None, ymax=None, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.set_ylim(ymin, ymax, **kwargs)
        return ax
    
    def invert_xaxis(ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.invert_xaxis(**kwargs)
        return ax

    def invert_yaxis(ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.invert_yaxis(**kwargs)
        return ax
    
    def hidespines(ax=None, top=True, right=True, bottom=True, left=True):
        global _ax_
        if ax is None: ax = _ax_
        if top:
            ax.spines['top'].set_visible(False)
        if right:
            ax.spines['right'].set_visible(False)
        if bottom:
            ax.spines['bottom'].set_visible(False)
        if left:
            ax.spines['left'].set_visible(False)
        return ax
    
    def hideticks(ax=None, x=True, y=True):
        global _ax_
        if ax is None: ax = _ax_
        if x:
            ax.set_xticks([])
            ax.set_xticklabels([])
        if y:
            ax.set_yticks([])
            ax.set_yticklabels([])
        return ax
    
    def twinx(ax=None, label='', fontsize=None, color="fg", fonttype="medium", **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("label")
        if fonttype not in ["medium", "bold", "black", "zh", "special", "zhbold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'medium', 'bold', 'black', 'zh', 'special', 'zhbold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        ax2 = ax.twinx()
        ax2.set_ylabel(label, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        return ax2
    
    def twiny(ax=None, label='', fontsize=None, color="fg", fonttype="medium", **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("label")
        if fonttype not in ["medium", "bold", "black", "zh", "special", "zhbold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'medium', 'bold', 'black', 'zh', 'special', 'zhbold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        ax2 = ax.twiny()
        ax2.set_xlabel(label, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        return ax2

    def figsize(width=6.4, height=4.8, ax=None):
        global _ax_
        if ax is None: ax = _ax_
        ax.figure.set_size_inches(width, height)
        return ax

    def aspect(aspect='auto', adjustable=None, anchor=None, share=False, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.set_aspect(aspect, adjustable, anchor, share, **kwargs)
        return ax
    
    def axis(arg=None, ax=None):
        global _ax_
        if ax is None: ax = _ax_
        ax.axis(arg)
    
    def margin(ax=None, left=None, bottom=None, right=None, top=None, wspace=None, hspace=None):
        global _ax_
        if ax is None: ax = _ax_
        ax.figure.subplots_adjust(left=left, bottom=bottom, right=right, top=top, wspace=wspace, hspace=hspace)
        return ax
    
    # 3D Axes Functions
    def plot3d(x=0, y=0, z=0, ax=None, color="fg", linewidth=None, linestyle="-", **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m plot3d() got an unexpected Axes type: ax is not a 3D Axes instance."
        ax.plot(x, y, z, color=_GetColorCode_(color), linewidth=linewidth, linestyle=linestyle, **kwargs)
        return ax
    
    def scatter3d(x=0, y=0, z=0, ax=None, color="fg", marker="o", s=20, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m scatter3d() got an unexpected Axes type: ax is not a 3D Axes instance."
        ax.scatter(x, y, z, color=_GetColorCode_(color), marker=marker, s=s, **kwargs)
        return ax
    
    def bar3d(x=0, y=0, z=0, dx=0.5, dy=0.5, dz=0, ax=None, color="fg8", alpha=1, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m bar3d() got an unexpected Axes type: ax is not a 3D Axes instance."
        ax.bar3d(x, y, z, dx, dy, dz, color=_GetColorCode_(color), alpha=alpha, **kwargs)
        return ax
    
    def contour3d(x=0, y=0, z=0, ax=None, cmap=None, linewidth=None, zdir='z', offset=0, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m contour3d() got an unexpected Axes type: ax is not a 3D Axes instance."
        ax.contour3D(x, y, z, color=cmaplist(cmap), linewidth=linewidth, zdir=zdir, offset=offset, **kwargs)
        return ax
    
    def contourf3d(x=0, y=0, z=0, ax=None, cmap=None, zdir='z', offset=0, returnCTF=False, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m contourf3d() got an unexpected Axes type: ax is not a 3D Axes instance."
        global CTF
        CTF = ax.contourf3D(x, y, z, cmap=cmaplist(cmap), zdir=zdir, offset=offset, **kwargs)
        if returnCTF:
            return CTF
        else:
            return ax
    
    def plot_surface(x=0, y=0, z=0, ax=None,linewidth=None, rstride=1, cstride=1, cmap=None, antialiased=False, shade=False, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m plot_surface() got an unexpected Axes type: ax is not a 3D Axes instance."
        global CTF
        if type(cmap) is None:
            CTF = ax.plot_surface(x, y, z, linewidth=linewidth, rstride=rstride, cstride=cstride, antialiased=False, shade=False, **kwargs)
        else:
            CTF = ax.plot_surface(x, y, z, cmap=cmaplist(cmap), linewidth=linewidth, rstride=rstride, cstride=cstride, antialiased=False, shade=False, **kwargs)
        return ax
    
    def quiver3d(x=0, y=0, z=0, u=0, v=0, w=0, ax=None, color="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m quiver3d() got an unexpected Axes type: ax is not a 3D Axes instance."
        ax.quiver(x, y, z, u, v, w, color=_GetColorCode_(color), **kwargs)
        return ax
    
    def voxels(voxels, facecolors='fg8', edgecolor='fg', alpha=1, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m voxels() got an unexpected Axes type: ax is not a 3D Axes instance."
        if type(facecolors) is str:
            ax.voxels(voxels, facecolors=facecolors, edgecolor=_GetColorCode_(edgecolor), alpha=alpha, **kwargs)
        elif type(facecolors) is list:
            facecolorlist = []
            for i in range(len(facecolors)):
                facecolorlist.append(_GetColorCode_(facecolors[i]))
            ax.voxels(voxels, facecolors=facecolorlist, edgecolor=_GetColorCode_(edgecolor), alpha=alpha, **kwargs)
        elif type(facecolors) is np.ndarray:
            ax.voxels(voxels, facecolors=facecolors, edgecolor=_GetColorCode_(edgecolor), alpha=alpha, **kwargs)
        else:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m voxels() got an unexpected keyword argument: facecolors='{facecolors}'. 'fg8' or list of color is valid.")
        return ax
    
    def zticks(ticks=None, labels='auto', ax=None, fontsize=None, color="fg", fonttype="medium", linewidth=Linewidth().get(), linelengths=5, right=False, direction='out', which='both', pad=5, **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("ticklabel")
        if fonttype not in ["medium", "bold", "black", "zh", "special", "zhbold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'medium', 'bold', 'black', 'zh', 'special', 'zhbold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m zticks() got an unexpected Axes type: ax is not a 3D Axes instance."
        if ticks is None:
            ax.set_zticks([])
        else:
            ax.set_zticks(ticks)
        if labels is None:
            ax.set_zticklabels([])
        elif labels == 'auto':
            labels = [tick for tick in ticks]
            # transform ticks to str
            for i in range(len(labels)):
                labels[i] = str(labels[i])
            ax.set_zticklabels(labels, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
            ax.tick_params(axis='z', which=which, direction=direction, length=linelengths, width=linewidth, color=_GetColorCode_(color), right=right, pad=pad)
        else:
            ax.set_zticklabels(labels, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
            ax.tick_params(axis='z', which=which, direction=direction, length=linelengths, width=linewidth, color=_GetColorCode_(color), right=right, pad=pad)
        return ax
    
    def zscale(scale='log', base=10, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m zscale() got an unexpected Axes type: ax is not a 3D Axes instance."
        ax.set_zscale(scale, base, **kwargs)
        return ax
    
    def zlim(zmin=None, zmax=None, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m zlim() got an unexpected Axes type: ax is not a 3D Axes instance."
        ax.set_zlim(zmin, zmax, **kwargs)
        return ax
    
    def zlabel(s='', ax=None, fontsize=None, color="fg", fonttype="medium", right=False, **kwargs):
        if fontsize is None: fontsize=_GetFontSize_("label")
        if fonttype not in ["medium", "bold", "black", "zh", "special", "zhbold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'medium', 'bold', 'black', 'zh', 'special', 'zhbold' or 'kl' is valid.")
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m zlabel() got an unexpected Axes type: ax is not a 3D Axes instance."
        ax.set_zlabel(s, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        if right:
            ax.tick_params(axis='z', labelright=True)
        return ax
    
    # set 3d pane color
    def set_pane_color(color=False, grid=False, ax=None):
        global _ax_
        if ax is None: ax = _ax_
        assert isinstance(ax, Axes3D), "\033[41m[pymeili Error]\033[0m set_pane_color() got an unexpected Axes type: ax is not a 3D Axes instance."
        if color==False:
            ax.xaxis.pane.fill = False
            ax.yaxis.pane.fill = False
            ax.zaxis.pane.fill = False
        else:
            ax.xaxis.pane.set_facecolor(_GetColorCode_(color))
            ax.yaxis.pane.set_facecolor(_GetColorCode_(color))
            ax.zaxis.pane.set_facecolor(_GetColorCode_(color))
        if grid==False:
            ax.xaxis.pane.set_edgecolor('w')
            ax.yaxis.pane.set_edgecolor('w')
            ax.zaxis.pane.set_edgecolor('w')
        return ax
    
    
    
    
    # windrose config fxn
    def rbar(wd, ws, normed=True, opening=0.8, edgecolor='fg', linewidth=Linewidth().get(), ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if not isinstance(ax, WindroseAxes):
            print("\033[43m[pymeili Warning]\033[0m rbar() got an unexpected Axes type: ax is not a WindroseAxes instance.")
        ax.bar(wd, ws, normed=normed, opening=opening, edgecolor=_GetColorCode_(edgecolor), linewidth=linewidth, **kwargs)
        return ax
    
    def rbox(wd, ws, bins=5, normed=True, edgecolor='fg', linewidth=Linewidth().get(), ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if not isinstance(ax, WindroseAxes):
            print("\033[43m[pymeili Warning]\033[0m rbox() got an unexpected Axes type: ax is not a WindroseAxes instance.")
        ax.box(wd, ws, bins=bins, normed=normed, edgecolor=_GetColorCode_(edgecolor), linewidth=linewidth, **kwargs)
        return ax
    
    def rcontour(wd, ws, bins=5, ax=None, color="fg", colors=None, linewidth=None, **kwargs):
        if linewidth is None: linewidth=Linewidth().get()
        global _ax_
        if ax is None: ax = _ax_
        if not isinstance(ax, WindroseAxes):
            print("\033[43m[pymeili Warning]\033[0m rcontour() got an unexpected Axes type: ax is not a WindroseAxes instance.")
        if colors==None:
                colors = _GetColorCode_(color)
        else:
            colors = _GetColorCode_(colors)
        
        global CT
        ax.contour(wd, ws, bins=bins, colors=colors, linewidth=linewidth, **kwargs)
        return ax
        
    
    def rcontourf(wd, ws, bins=5, ax=None, cmap=None, colors=None, returnCTF=False,**kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if not isinstance(ax, WindroseAxes):
            print("\033[43m[pymeili Warning]\033[0m rcontourf() got an unexpected Axes type: ax is not a WindroseAxes instance.")
        if colors is None:
            if cmap is None:
                cmap = _GetColorCode_("fg") # 什麼都沒說，就用fg
            else:
                cmap = cmaplist(cmap) # cmap可為字串(關鍵字)或是list(自定義)，colors為None，則使用cmap
        else:
            if cmap is None:
                colors = _GetColorCode_(colors) # cmap為None，colors不為None，則使用colors
            else: # 同時指定cmap和colors，則報錯
                raise TypeError(f"\033[41m[pymeili Error]\033[0m rcontourf() got an unexpected keyword argument: 'cmap' and 'colors' cannot be specified at the same time.")
        
        global CTF
        ax.contourf(wd, ws, bins=bins, cmap=cmap, colors=colors, **kwargs)
        if returnCTF:
            return CTF
        else:
            return ax
            
    def set_rlabel_position(position='auto', ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if not isinstance(ax, WindroseAxes):
            print("\033[43m[pymeili Warning]\033[0m set_rlabel_position() got an unexpected Axes type: ax is not a WindroseAxes instance.")
        ax.set_rlabel_position(position, **kwargs)
        return ax
    
    def set_theta_zero_location(location='N', ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if not isinstance(ax, WindroseAxes):
            print("\033[43m[pymeili Warning]\033[0m set_theta_zero_location() got an unexpected Axes type: ax is not a WindroseAxes instance.")
        ax.set_theta_zero_location(location, **kwargs)
        return ax
    
    def set_theta_direction(direction='clockwise', ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if not isinstance(ax, WindroseAxes):
            print("\033[43m[pymeili Warning]\033[0m set_theta_direction() got an unexpected Axes type: ax is not a WindroseAxes instance.")
        ax.set_theta_direction(direction, **kwargs)
        return ax
    
    def rgrids(ax=None, linewidth=Linewidth().get(), linestyle=':', xcolor='fg', ycolor="fg8", xgrid=True, ygrid=True, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if not isinstance(ax, WindroseAxes):
            print("\033[43m[pymeili Warning]\033[0m rgrids() got an unexpected Axes type: ax is not a WindroseAxes instance.")
        ax.xaxis.grid(xgrid, linestyle='-', linewidth=linewidth, color=_GetColorCode_(xcolor), **kwargs)
        ax.yaxis.grid(ygrid, linestyle=linestyle, linewidth=linewidth, color=_GetColorCode_(ycolor), **kwargs)
        return ax
    
    def rspines(ax=None, color='fg', linewidth=Linewidth().get(), **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if not isinstance(ax, WindroseAxes):
            print("\033[43m[pymeili Warning]\033[0m rspines() got an unexpected Axes type: ax is not a WindroseAxes instance.")
        ax.spines['polar'].set_color(_GetColorCode_(color))
        ax.spines['polar'].set_linewidth(linewidth)
    
    def rticklabels(label=[], ax=None, fontsize=None, color="fg", fonttype="medium", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if fontsize is None: fontsize=_GetFontSize_("ticklabel")
        if fonttype not in ["medium", "bold", "black", "zh", "special", "zhbold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'medium', 'bold', 'black', 'zh', 'special', 'zhbold' or 'kl' is valid.")
        ax.set_xticklabels(label, fontproperties=fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize), color=_GetColorCode_(color), **kwargs)
        return ax
    # Basemap config fxn
    def basemap(ax=None, projection='cyl', resolution='c', **kwargs):
        ax = Basemap(ax=ax, projection=projection, resolution=resolution, **kwargs)
        return ax
    
    def drawcoastlines(ax=None, linewidth=Linewidth().get()/2, color="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m drawcoastlines() got an unexpected Axes type: ax is not a Basemap instance.")
        #if type(ax) == cartopy.mpl.geoaxes.GeoAxesSubplot:
        #    print("\033[43m[pymeili Warning]\033[0m Mismatched function: drawcoastlines() is not supported in cartopy. Use coastlines() instead.")
        ax.drawcoastlines(linewidth=linewidth, color=_GetColorCode_(color), **kwargs)
        return ax
    
    def drawcountries(ax=None, linewidth=Linewidth().get()/2, color="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m drawcountries() got an unexpected Axes type: ax is not a Basemap instance.")
        #if type(ax) == cartopy.mpl.geoaxes.GeoAxesSubplot:
        #    print("\033[43m[pymeili Warning]\033[0m Mismatched function: drawcountries() is not supported in cartopy. Use countries() instead.")
        ax.drawcountries(linewidth=linewidth, color=_GetColorCode_(color), **kwargs)
        return ax

    def drawstates(ax=None, linewidth=Linewidth().get()/2, color="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m drawstates() got an unexpected Axes type: ax is not a Basemap instance.")
        ax.drawstates(linewidth=linewidth, color=_GetColorCode_(color), **kwargs)
        return ax
    
    def drawrivers(ax=None, linewidth=Linewidth().get()/2, color="bg2", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m drawrivers() got an unexpected Axes type: ax is not a Basemap instance.")
        ax.drawrivers(linewidth=linewidth, color=_GetColorCode_(color), **kwargs)
        return ax
    
    def drawlsmask(ax=None, land_color='rfg', ocean_color='bg', lakes=True, resolution='c', grid=5, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m drawlsmask() got an unexpected Axes type: ax is not a Basemap instance.")
        _ax_.drawlsmask(land_color=_GetColorCode_(land_color), ocean_color=_GetColorCode_(ocean_color), lakes=lakes, resolution=resolution, grid=grid, **kwargs)
        return _ax_
    
    def fillcontinents(ax=None, color="fg", lake_color="bg2", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m fillcontinents() got an unexpected Axes type: ax is not a Basemap instance.")
        #if type(ax) == cartopy.mpl.geoaxes.GeoAxesSubplot:
        #    print("\033[43m[pymeili Warning]\033[0m Mismatched function: fillcontinents() is not supported in cartopy. Use add_fillcontinents() instead.")
        _ax_.fillcontinents(color=_GetColorCode_(color), lake_color=_GetColorCode_(lake_color), **kwargs)
        return _ax_
    
    def drawmapboundary(ax=None, color="fg", linewidth=Linewidth().get()/2, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m drawmapboundary() got an unexpected Axes type: ax is not a Basemap instance.")
        #if type(ax) == cartopy.mpl.geoaxes.GeoAxesSubplot:
        #    print("\033[43m[pymeili Warning]\033[0m Mismatched function: drawmapboundary() is not supported in cartopy. Use add_mapboundary() instead.")
        AXB = _ax_.drawmapboundary(color=_GetColorCode_(color), linewidth=linewidth, **kwargs)
        AXB.set_clip_on(False)
        return _ax_
    
    def readshapefile(shapefile=f'{motherpath}\pymeili_resource\\shapefile.shp', ax=None, name='states', drawbounds=True, linewidth=Linewidth().get()/2, color="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m readshapefile() got an unexpected Axes type: ax is not a Basemap instance.")
        #if type(ax) == cartopy.mpl.geoaxes.GeoAxesSubplot:
        #    print("\033[43m[pymeili Warning]\033[0m Mismatched function: readshapefile() is not supported in cartopy. Use add_shapefile() instead.")
        _ax_.readshapefile(shapefile, name=name, drawbounds=drawbounds, linewidth=linewidth, color=_GetColorCode_(color), **kwargs)
        if read_config(1) == False:
            print(f"\033[44m[pymeili Info]\033[0m Shapefile: {shapefile} is loaded.")
        return _ax_

    def drawmeridians(meridians, ax=None, linewidth=Linewidth().get()/2, color="fg", labels=[0,0,0,1], labelsize=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m drawmeridians() got an unexpected Axes type: ax is not a Basemap instance.")
        if labelsize is None: labelsize=_GetFontSize_("ticklabel")
        _meridians_ = _ax_.drawmeridians(meridians, linewidth=linewidth, color=_GetColorCode_(color), labels=labels, fontsize=labelsize, **kwargs)
        # set label fonttype
        fonttype = "medium"
        for label in _meridians_:
            try:
                _meridians_[label][1][0].set_fontproperties(fm.FontProperties(fname=FontFamily().get(fonttype), size=labelsize))
            except IndexError:
                pass # no label available
        return _ax_
    
    def drawparallels(parallels, ax=None, linewidth=Linewidth().get()/2, color="fg", labels=[1,0,0,0], labelsize=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m drawparallels() got an unexpected Axes type: ax is not a Basemap instance.")
        if labelsize is None: labelsize=_GetFontSize_("ticklabel")
        _parallels_ = _ax_.drawparallels(parallels, linewidth=linewidth, color=_GetColorCode_(color), labels=labels, fontsize=labelsize, **kwargs)
        fonttype = "medium"
        for label in _parallels_:
            try:
                _parallels_[label][1][0].set_fontproperties(fm.FontProperties(fname=FontFamily().get(fonttype), size=labelsize))
            except IndexError:
                pass
        return _ax_

    def shaderelief(ax=None, scale=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != Basemap: 
            print("\033[43m[pymeili Warning]\033[0m shaderelief() got an unexpected Axes type: ax is not a Basemap instance.")
        _ax_.shaderelief(scale=scale, **kwargs)
        return _ax_

    # Cartopy config fxn
    def coastlines(ax=None, linewidth=Linewidth().get()/2, color="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m coastlines() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.coastlines(linewidth=linewidth, color=_GetColorCode_(color), **kwargs)
        return ax
    
    def countries(ax=None, linewidth=Linewidth().get()/2, color="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m countries() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        if type(ax) == Basemap:
            print("\033[43m[pymeili Warning]\033[0m Mismatched function: countries() is not supported in Basemap. Use drawcountries() instead.")
        ax.add_feature(cfeature.BORDERS, linewidth=linewidth, color=_GetColorCode_(color), **kwargs)
        return ax
    
    def stock_img(ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m stock_img() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.stock_img(**kwargs)
        return ax
    
    def gridlines(ax=None, linewidth=Linewidth().get()/2, color="fg", draw_labels=True, dms=False, x_inline=False, y_inline=False, labelsize=None, linestyle='--', **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m gridlines() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        if type(ax) == Basemap:
            print("\033[43m[pymeili Warning]\033[0m Mismatched function: gridlines() is not supported in Basemap. Use drawparallels() and drawmeridians() instead.")
        gl = ax.gridlines(linewidth=linewidth, color=_GetColorCode_(color), draw_labels=draw_labels, dms=dms, x_inline=x_inline, y_inline=y_inline, linestyle=linestyle, **kwargs)
        # set fontsize, fontcolor, fonttype
        if labelsize is None: labelsize=_GetFontSize_("ticklabel")
        gl.xlabel_style = {'color': _GetColorCode_(color), 'fontsize': labelsize}
        gl.ylabel_style = {'color': _GetColorCode_(color), 'fontsize': labelsize}
        # set fonttype
        fonttype = "medium"
        gl.xlabel_style['fontproperties'] = fm.FontProperties(fname=FontFamily().get(fonttype), size=labelsize)
        gl.ylabel_style['fontproperties'] = fm.FontProperties(fname=FontFamily().get(fonttype), size=labelsize)
        # Turn off right and top tick marks
        gl.right_labels = False
        gl.top_labels = False
        return ax
    
    def add_mapboundary(ax=None, linewidth=Linewidth().get(), color="fg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m add_mapboundary() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        if type(ax) == Basemap:
            print("\033[43m[pymeili Warning]\033[0m Mismatched function: add_mapboundary() is not supported in Basemap. Use drawmapboundary() instead.")
        _ax_.add_patch(plt.Rectangle((ax.get_xlim()[0], ax.get_ylim()[0]),
                           ax.get_xlim()[1] - ax.get_xlim()[0],
                           ax.get_ylim()[1] - ax.get_ylim()[0],
                           fill=None, edgecolor=_GetColorCode_(color), linewidth=linewidth, **kwargs))
    
    def add_fillcontinents(ax=None, color="fg", lake_color="bg2", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m add_fillcontinents() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        if type(ax) == Basemap:
            print("\033[43m[pymeili Warning]\033[0m Mismatched function: add_fillcontinents() is not supported in Basemap. Use fillcontinents() instead.") 
        ax.add_feature(cfeature.LAND, color=_GetColorCode_(color), **kwargs)
        ax.add_feature(cfeature.LAKES, color=_GetColorCode_(lake_color), **kwargs)
        return ax
    
    def add_filloceans(ax=None, color="bg", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m add_filloceans() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.add_feature(cfeature.OCEAN, color=_GetColorCode_(color), **kwargs)
        return ax

    def add_feature(feature, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m add_feature() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.add_feature(feature, **kwargs)
        return ax
    
    def add_geometries(geoms, crs, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m add_geometries() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.add_geometries(geoms, crs, **kwargs)
        return ax
    
    def add_image(factory, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m add_image() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.add_image(factory, **kwargs)
        return ax
    
    def add_raster(raster, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m add_raster() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.add_raster(raster, **kwargs)
        return ax
    
    def add_wmts(wmts, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m add_wmts() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.add_wmts(wmts, **kwargs)
        return ax
    
    def add_wms(wms, layers, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m add_wms() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.add_wms(wms, layers, **kwargs)
        return ax
    
    def autoscale_view(ax=None, tight=None, scalex=True, scaley=True):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m autoscale_view() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.autoscale_view(tight=tight, scalex=scalex, scaley=scaley)
        return ax
    
    def background_img(name='ne_shaded', resolution='low', extent=None, cache=False, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m background_img() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.background_img(name=name, resolution=resolution, extent=extent, cache=cache, **kwargs)
        return ax
    
    def set_extent(extent=None, crs=None, ax=None):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m set_extent() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.set_extent(extent, crs=crs)
        return ax
    
    def set_global(ax=None):
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m set_global() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        ax.set_global()
        return ax
    
    def add_shapefile(filename, ax=None, crs=ccrs.PlateCarree(), edgecolor='fg', facecolor=None, linewidth=Linewidth().get()/2, **kwargs):
        from cartopy.io.shapereader import Reader
        from cartopy.feature import ShapelyFeature
        global _ax_
        if ax is None: ax = _ax_
        if type(ax) != cartopy.mpl.geoaxes.GeoAxesSubplot: 
            print("\033[43m[pymeili Warning]\033[0m add_shapefile() got an unexpected Axes type: ax is not a cartopy's GeoAxesSubplot instance.")
        # make sure the file exists
        if not os.path.exists(filename): raise FileNotFoundError(f"\033[41m[pymeili Error]\033[0m Shapefile: {filename} not found.")
        if facecolor is None: facecolor = "#00000000"
        else: facecolor = _GetColorCode_(facecolor)
        SF = ShapelyFeature(Reader(filename).geometries(), crs=crs, edgecolor=_GetColorCode_(edgecolor), facecolor=facecolor, linewidth=linewidth, **kwargs)
        print(f"\033[44m[pymeili Info]\033[0m Shapefile: {filename} is loaded.")
        _ax_.add_feature(SF)
        return _ax_
    
    # Image config fxn
    def imread(filename, **kwargs):
        return plt.imread(filename, **kwargs)
    
    def imshow(X, ax=None, axis='off', cmap=None, colors=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        ax.axis(axis)
        if cmap is None and colors is None: return ax.imshow(X, **kwargs)
        else:
            global CTF
            if cmap is not None and colors is not None:
                raise TypeError(f"\033[41m[pymeili Error]\033[0m imshow() got an unexpected keyword argument: cmap and colors cannot be None at the same time.")
            elif cmap is None and colors is not None:
                # support in contourf, not in imshow
                raise TypeError(f"\033[41m[pymeili Error]\033[0m colors is not supported in imshow(), use cmap instead.")
            elif cmap is not None and colors is None:
                CTF = ax.imshow(X, cmap=cmaplist(cmap), **kwargs)
                return ax

    def pcolor(x, y, z, ax=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        return ax.pcolor(x, y, z, **kwargs)

    def pcolormesh(x, y, z, ax=None, cmap=None, **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if cmap is not None: return ax.pcolormesh(x, y, z, cmap=cmaplist(cmap), **kwargs)
        else: return ax.pcolormesh(x, y, z, **kwargs)
    
    
    



    # Advanced Addtional Function for plot
    from matplotlib.widgets import Button
    from mpl_toolkits.axes_grid1.inset_locator import InsetPosition
    
    def button(ax=None, pos=(0.5,-0.12) ,width=0.4, height=0.1, label='', color="bg", hovercolor="fg8", fontsize=None, fonttype="medium", **kwargs):
        global _ax_
        if ax is None: ax = _ax_
        if fontsize is None: fontsize=_GetFontSize_("text")
        if fonttype not in ["medium", "bold", "black", "zh", "special", "zhbold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'medium', 'bold', 'black', 'zh', 'special', 'zhbold' or 'kl' is valid.")
        
        # Create a button axes
        ax_btn = plt.axes([0, 0, 1, 1])
        # Create a button
        ip = InsetPosition(ax, [pos[0], pos[1], width, height])
        ax_btn.set_axes_locator(ip)
        axbutton = Button(ax_btn, label, color=_GetColorCode_(color), hovercolor=_GetColorCode_(hovercolor), **kwargs)
        axbutton.label.set_fontproperties(fm.FontProperties(fname=FontFamily().get(fonttype), size=fontsize))
        return axbutton


    # Miscellaneous Process
    def show(**kwargs):
        plt.show(**kwargs)
        
    def pause(interval):
        plt.pause(interval)
        
    def close():
        plt.close()
        
        
    def savefig(filename, dpi=300, transparent=False, bbox_inches='tight', pad_inches=0.1, record=True, **kwargs):
        plt.savefig(filename, dpi=dpi, transparent=transparent, bbox_inches=bbox_inches, pad_inches=pad_inches, **kwargs)
        if record:
            save_name = filename
            save_time = getTableTime()
            global production_name, production_time
            production_name.append(save_name)
            production_time.append(save_time)

        
    def clf():
        plt.clf()
        
    def cla():
        plt.cla()

    def gcf(ax=None):
        global _ax_
        if ax is None: ax = _ax_
        return ax.figure
    
    def gca(ax=None):
        global _ax_
        if ax is None: ax = _ax_
        return ax

    def tight_layout(ax=None, pad=1.08, h_pad=None, w_pad=None, rect=None):
        global _ax_
        if ax is None: ax = _ax_
        try:
            ax.figure.tight_layout(pad=pad, h_pad=h_pad, w_pad=w_pad, rect=rect)
        except AttributeError: # AttributeError: 'NoneType' object has no attribute 'xmin', this bug cause by basemap.drawmeridians() or basemap.drawparallels()
            raise AttributeError(f"\033[41m[pymeili Error]\033[0m tight_layout() got an unexpected keyword argument: 'NoneType' object has no attribute 'xmin', this bug might caused by basemap.drawmeridians() or basemap.drawparallels(), use cartopy instead to avoid this bug.")
        return ax

    def ion():
        plt.ion()
        
    def ioff():
        plt.ioff()
        
    def isinteractive():
        plt.isinteractive()
        
    def record(title=None):
        table = printTable(production_name, production_time, title)
        return table

    # POST-PROCESSING
    def add_watermark(filepath, text="pymeili", fontsize=20, color="fg", fonttype="medium", margin=10):
        if filepath is None: raise FileNotFoundError(f"\033[41m[pymeili Error]\033[0m add_watermark() got an unassigned keyword argument: filepath='{filepath}'.")
        if fontsize is None: fontsize=_GetFontSize_("text")
        if fonttype not in ["medium", "bold", "black", "zh", "special", "zhbold", "kl"]:
            raise TypeError(f"\033[41m[pymeili Error]\033[0m text() got an unexpected keyword argument: fonttype='{fonttype}'. 'medium', 'bold', 'black', 'zh', 'special', 'zhbold' or 'kl' is valid.")
        from PIL import Image, ImageDraw, ImageFont
        from pathlib import Path
        # add watermark at the bottom right of the image
        img = Image.open(filepath)
        draw = ImageDraw.Draw(img)
        fontpath = FontFamily().get(fonttype)
        # 將所有fontpath中的' '換成'_'
        if fonttype == "zh":
            fontpath = str(fontpath).replace(' ', '_')
        font = ImageFont.truetype(str(Path(fontpath)), fontsize)
        textwidth, textheight = draw.textsize(text, font)
        width, height = img.size
        # calculate position
        margin = margin
        x = width - textwidth - margin
        y = height - textheight - margin
        # draw watermark
        draw.text((x, y), text, font=font, fill=_GetColorCode_(color))
        # save the image
        img.save(filepath)
        return img
    
    def convertgif(inputfolder, outputfolder, filename='output.gif', format='png', duration=0.5, loop=0, downresorate=1):
        if not os.path.exists(inputfolder): raise FileNotFoundError(f"\033[41m[pymeili Error]\033[0m convertgif() got an unexpected keyword argument: inputfolder='{inputfolder}' not found.")
        if not os.path.exists(outputfolder): os.makedirs(outputfolder)
        if filename.split('.')[-1] != 'gif': raise ValueError(f"\033[41m[pymeili Error]\033[0m convertgif() got an unexpected keyword argument: filename='{filename}'. The output filename should be a gif file.")
        if format not in ['png', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff', 'gif']: raise TypeError(f"\033[41m[pymeili Error]\033[0m convertgif() got an unexpected keyword argument: format='{format}'. 'png', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff' or 'gif' is valid.")
        if duration <= 0: raise ValueError(f"\033[41m[pymeili Error]\033[0m convertgif() got an unexpected keyword argument: duration='{duration}'. duration should be greater than 0.")
        if loop < 0: raise ValueError(f"\033[41m[pymeili Error]\033[0m convertgif() got an unexpected keyword argument: loop='{loop}'. loop should be greater than or equal to 0.")
        if downresorate <= 0: raise ValueError(f"\033[41m[pymeili Error]\033[0m convertgif() got an unexpected keyword argument: downresorate='{downresorate}'. downresorate should be greater than 0.")
        # get all images in the inputfolder
        images = glob.glob(f"{inputfolder}/*.{format}")
        # sort the images
        images.sort()
        # read images
        images = [imageio.v2.imread(image) for image in images]
        # downresorate
        images = [image[::downresorate, ::downresorate] for image in images]
        # save as gif
        imageio.mimsave(f"{outputfolder}/{filename}", images, duration=duration, loop=loop)
        return images

except Exception as e:
    print("\033[41m[pymeili Exception]\033[0m ", e)
    exit()