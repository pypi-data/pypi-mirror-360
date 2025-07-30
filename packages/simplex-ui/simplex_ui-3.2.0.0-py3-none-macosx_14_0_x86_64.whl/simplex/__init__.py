import json, os, stat, subprocess, sys, shutil
import signal, traceback, asyncio
from os.path import abspath
from os.path import sep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import (WebDriverException, UnexpectedAlertPresentException)

import pexpect
import threading
import time
import wx

import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(True)
except:
    pass

if os.name == "nt":
    from pexpect.popen_spawn import PopenSpawn as spawn
else:
    from pexpect import spawn

APPNAME = "simplex"
HTML_SRC_DIR = os.path.join(abspath(os.path.dirname(__file__)), "src")
SOLVER_NOMPI_PATH = os.path.join(abspath(os.path.dirname(__file__)), "bin", APPNAME+"_solver_nompi")
SOLVER_PATH = os.path.join(abspath(os.path.dirname(__file__)), "bin", APPNAME+"_solver")
VERSION = "3.2"

def HandleLocalFile(path, mode, type, data, result):
    path = abspath(path)
    result["msg"] = ""
    result["data"] = ""
    try:
        with open(path, mode=mode, encoding="utf-8") as f:
            try:
                if mode == "w":
                    if(type == "json"):
                        f.write(json.dumps(data, indent=2))
                    else:
                        f.write(data)
                else:
                    if(type == "json"):
                        result["data"] = json.load(f)
                    else:
                        result["data"] = f.read()
            except json.JSONDecodeError:
                result["msg"] = 'Invalid JSON format in "'+path+'".'
            except Exception as e:
                print(e)
                result["msg"] = "Failed to "+('write in "' if mode=="w" else 'read from "')+path+'".'
    except FileNotFoundError:
        result["msg"] = 'Path "'+path+'" not found or created.'
    return result["msg"] == ""

def GetSerialFilenames(n, filename):
    paths = os.path.splitext(filename)
    files = []
    for i in range(n):
        filen = filename
        if i > 0 or n > 1:
            base = paths[0]+"-"+str(i+1)
            filen = base+paths[1]
        files.append(filen)
    return files

def ExecuteFile(filename):
    with open(filename) as f:
        src = f.read()
        src = src.replace(APPNAME+".", "")
        exec(src)

def LocateSourceFiles(rootpath, srcname):
    if os.path.isdir(rootpath) == False:
        print(f"{rootpath} is not a directory")
        return False
    path_info = os.stat(rootpath)
    mode = stat.filemode(path_info.st_mode)
    usermode = mode[1:4]
    if usermode != "rwx":
        print(f"{rootpath} is not accessible")
        return False
    rootpath = os.path.join(rootpath, srcname)
    try:
        shutil.copytree(HTML_SRC_DIR, rootpath, dirs_exist_ok=True)
    except Exception as e:
        print(e)
        return False    
    return True

def copy_docstring_from(original):
    def wrapper(target):
        target.__doc__ = original.__doc__
        return target
    return wrapper

class SIMPLEX:
    def __init__(self, src, browser):
        self.displaysize = None
        self.wxapp = None
        self.browser = "c"
        self.htmlroot = "https://spectrax.org/"+APPNAME+"/app/"+VERSION+"/index.html"
        self.browser = browser
        if src == "l":
            if browser == "f":
                self.htmlroot = None
            else:
                self.htmlroot = GetHTMLRoot("")
        self.currfile = ""
        self.mode = ""
        self.cancelproc = {}
        self.threads = []
        self.databuffer = {}
        self.datanames = []
        self.fresult = {}
        self.settings = {}
        self.datalimit = 1e7 # limit data transfer within 10MB
        self.homedir = os.path.join(os.path.expanduser("~"), "Documents")
        if os.path.isdir(self.homedir) == False:
            self.homedir = os.getcwd()

    def __udloadFile(self, filename, oprid = None, mode="download", direct=False):
        filename = abspath(filename)
        if mode == "upload":
            if os.path.exists(filename) == False:
                return False
            id = "file-main"
            if self.menulabels["menuitems"]["postproc"] in oprid:
                id = "file-postproc"
            if oprid is not None:
                self.driver.execute_script('SetFromPython("fileid", arguments[0]);', oprid)
            self.driver.execute_script('SetFromPython("loading", true);')
            element = self.driver.find_element(By.ID, id)
            try:
                element.send_keys(filename)
            except Exception as e:
                print(e.msg)
                return                
            while self.driver.execute_script("return GUIConf.loading"):
                time.sleep(0.1)
        else:
            data = self.driver.execute_script("return GetBufferData(arguments[0], arguments[1]);", self.datalimit, direct)
            if data is None:
                self.__clearTmpFile()
                self.driver.execute_script("ExportObjects(null, null);")
                tmppath = os.path.join(os.getcwd(), "tmp.txt")
                while os.path.exists(tmppath) == False:
                    time.sleep(0.5)
                if os.path.exists(filename):
                    os.remove(filename)
                os.rename(tmppath, filename)
            else:
                if HandleLocalFile(filename, "w", "ascii", data, self.fresult) == False:
                    print(self.fresult["msg"])
                    return False
        return True
        
    def __clearTmpFile(self):
        tmppath = os.path.join(os.getcwd(), "tmp.txt")
        if os.path.exists(tmppath):
            os.remove(tmppath)

    def __loadSaveConfiguration(self, mode):
        configfile = os.path.join(self.homedir, APPNAME+"_ui_config.json")
        if mode == "r" and os.path.isfile(configfile) == False:
            return
        if HandleLocalFile(configfile, mode, "json", self.settings, self.fresult) == False:
            print(self.fresult["msg"])
        if mode == "r":
            self.settings = self.fresult["data"]
    
    def __getID(self, target, prefix = ""):
        if isinstance(target, list):
            items = target
        else:
            items = target.split(self.menulabels["separator"])
        if prefix != "" and prefix not in items:
            items.insert(0, prefix)
        ids = []
        for item in items:
            if item in self.menulabels["menuitems"]:
                ids.append(self.menulabels["menuitems"][item])
            else:
                ids.append(item)
        id = self.menulabels["separator"].join(ids)
        return id     

    def __open(self, filename, isopen):
        self.__readFile(filename, isopen)
        self.driver.execute_script('SetFromPython("filename", arguments[0]);', filename)
            
    def __readFile(self, filename, isopen):
        if HandleLocalFile(filename, "r", "ascii", None, self.fresult) == False:
            print(self.fresult["msg"])
            return
        self.currfile = filename
#        
#
#
#       space for compatibility with spectra
#
#
#
        self.driver.execute_script(\
            "HandleFile(arguments[0], arguments[1], true);", self.fresult["data"], filename)
        self.CheckParticleData()

    def __end(self):
        for thread in self.threads:
            if thread["thread"].is_alive():
                self.cancelproc[thread["id"]] = True
                thread["thread"].join()
        try:
            self.driver.execute_script("GatherSettings();")
            guisettings = self.driver.execute_script("return Settings;")
            settingkeys = ["defpaths", "lastloaded", "lastid", "window"]
            for key in settingkeys:
                if key in guisettings:
                    del guisettings[key]
            self.settings.update(guisettings)
            winsize = self.driver.get_window_size()
            self.settings["window"] = {"width": winsize["width"], "height": winsize["height"]}
            winpos = self.driver.get_window_position()
            self.settings["position"] = {"x": winpos["x"], "y": winpos["y"]}
            self.__loadSaveConfiguration("w")
            self.driver.quit()
        except WebDriverException:
            print("WARNING: main window may have been closed before GUI configurations are saved.")
    
    def __getFilenameFromDialog(self, title, id, isopen, istext = False, isdir = False, ismulti = False):
        fTyp = "JSON file (*.json)|*.json|All files (*.*)|*.*"
        if istext:
            fTyp = "All files (*.*)|*.*"
        iDir = self.homedir.replace("\\", "/")
        if self.menulabels["menuitems"]["saveas"] in id:
            id = self.menulabels["separator"].join([self.menulabels["menuitems"]["file"], self.menulabels["menuitems"]["open"]])
        if "defpaths" in self.settings:
            if id in self.settings["defpaths"]:
                iDir = self.settings["defpaths"][id]
        else:
            self.settings["defpaths"] = {}

        if self.wxapp == None:
            self.wxapp = wx.App()

        if isopen:
            if ismulti:
                dstyle = wx.FD_OPEN|wx.FD_MULTIPLE|wx.FD_FILE_MUST_EXIST
            else:
                dstyle = wx.FD_OPEN|wx.FD_FILE_MUST_EXIST
            dlg = wx.FileDialog(None, message=title, defaultDir=iDir, defaultFile="", wildcard=fTyp, style=dstyle)
        elif isdir:
            dlg = wx.DirDialog(None, message=title, defaultPath=iDir)
        else:
            dstyle = wx.FD_SAVE|wx.FD_CHANGE_DIR
            dlg = wx.FileDialog(None, message=title, defaultDir=iDir, defaultFile="", wildcard=fTyp, style=dstyle)

        filename = ""
        if dlg.ShowModal() == wx.ID_OK:
            if isopen and ismulti:
                filename = dlg.GetPaths()
            else:
                filename = dlg.GetPath()

        if filename != "":
            if isinstance(filename, tuple):
                if len(filename) > 0:
                    filepaths = filename
                    filename = []
                    for filen in filepaths:
                        filen = filen.replace('/', sep)
                        filename.append(filen)
                    self.settings["defpaths"][id] = os.path.dirname(filename[0])
                else:
                    filename = ""
            else:
                filename = filename.replace('/', sep)
                self.settings["defpaths"][id] = os.path.dirname(filename)
        return filename

    def __select(self, id, item):
        element = self.driver.find_element(By.ID, id)
        select = Select(element)
        if isinstance(item, list):
            if select.is_multiple:
                select.deselect_all()
            for el in item:
                try:
                    select.select_by_visible_text(el)
                except WebDriverException as e:
                    print(f'Target item "{el}" does not exist.')
                    return False
        else:
            try:
                select.select_by_visible_text(item)
            except WebDriverException as e:
                print(f'Target item "{item}" does not exist.')
                return False
        return True

    def __optionTexts(self, id):
        element = self.driver.find_element(By.ID, id)
        select = Select(element)
        options = select.options
        texts = []
        for option in options:
            texts.append(option.text)
        return texts

    def __runPreProcess(self, obj):
        dataname = os.path.join(self.homedir, ".preproc.json")
        if HandleLocalFile(dataname, "w", "json", obj, self.fresult) == False:
            print(self.fresult["msg"])

        ismb = False
        if "runid" in obj:
            ismb = obj["runid"] == self.menulabels["mblabel"]
            
        command = [SOLVER_NOMPI_PATH, "-f", dataname]
        try:
            proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            proc.wait(timeout=5)
            if HandleLocalFile(dataname, "r", "json", None, self.fresult) == False:
                print("Pre-processing failed: "+self.fresult["msg"])
            else:
                if "data" in self.fresult:
                    obj = self.fresult["data"]
                    if ismb:
                        self.driver.execute_script("ApplyMicroBunch(arguments[0]);", obj)
                    elif "Input" in obj and "runid" in obj["Input"]:
                        item = obj["Input"]["runid"]
                        self.driver.execute_script("DrawPreprocObj(arguments[0], arguments[1]);", item, obj[item])
        except Exception as e:
            print("Pre-processing failed.")
        os.remove(dataname)

    def __run(self, procid, nompi=False):
        self.__clearTmpFile()
        prmobj = self.driver.execute_script(\
            "return GUIConf.simproc[arguments[0]].GeneratePrmObject();", procid)
        dataname = prmobj["dataname"]
        isfixed = prmobj["isfixed"]
        if self.__udloadFile(dataname) == False:
            self.__finishProcess(procid, "Failed to start")
            return

        mpisetting = self.driver.execute_script("return GetMPISetting();")
        if nompi:
            mpisetting["enable"] = False

        pathfile = dataname
        if " " in pathfile:
            pathfile = '"'+pathfile+'"'
        command = "\""+SOLVER_NOMPI_PATH+"\" -f "+pathfile
        if mpisetting["enable"]:
            command = "mpiexec -n "+str(mpisetting["processes"])+" \""+SOLVER_PATH+"\" -f "+pathfile

        self.cancelproc[procid] = False
        try:
            child = spawn(command)
            while True:
                index = child.expect(["\r", "\n", pexpect.TIMEOUT, pexpect.EOF], timeout=1)
                if index == 0 or index == 1:
                    data = child.before.decode("utf-8")
                    if self.menulabels["menuitems"]["scanout"] in data:
                        sdata = data.replace(self.menulabels["menuitems"]["scanout"], "").strip()
                        self.LoadOutput(sdata)
                    else:
                        print(data, end="\r")
                        self.driver.execute_script(\
                            "SetProcStatus(arguments[0], arguments[1]);", procid, data)
                elif index == 3:
                    print("\nDone")
                    self.__finishProcess(procid, "Done")
                    if isfixed and self.mode != "c":
                        if HandleLocalFile(dataname, "r", "ascii", None, self.fresult) == False:
                            print(self.fresult["msg"])
                            return
                        self.driver.execute_script(\
                            "GUIConf.GUIpanels[arguments[0]].ShowFixedPointResult(arguments[1]);", \
                            self.menulabels["outfile"], self.fresult["data"])
                    else:
                        self.LoadOutput(dataname)
                    break
                if self.cancelproc[procid] == True:
                    child.kill(signal.SIGINT)
                    self.driver.execute_script(\
                        "SetProcStatus(arguments[0], arguments[1], arguments[2]);", procid, "Canceled", True)
                    break
        except Exception as e:
            self.__finishProcess(procid, traceback.format_exception_only(type(e), e))

    def __finishProcess(self, procid, msg):
        try:
            self.driver.execute_script(\
                "GUIConf.simproc[arguments[0]].FinishSingle(arguments[1])", procid, msg)
        except Exception as e:
            print("Window has been closed.")

    def __watchCommand(self):
        while True:
            time.sleep(0.5)
            try:
                response = self.driver.execute_script("return PyQue.Get();")
            except UnexpectedAlertPresentException as e:
                time.sleep(1)
                continue
            except WebDriverException:
                break

            if isinstance(response, list):
                if response[0] == self.menulabels["menuitems"]["preproc"]:
                    self.__runPreProcess(response[1])
                elif self.menulabels["menuitems"]["cancel"] in response[0]:
                    self.cancelproc[response[1]] = True
            elif self.menulabels["menuitems"]["exit"] in response:
                break

    def Start(self, filename = "", mode = "g"):
        """
        mode: "g" = GUI mode, "c" = CUI mode, "i" = Interactive mode
        """
        self.mode = mode
        addopt = True        
        if self.browser == "e":
            options = webdriver.EdgeOptions()
        elif self.browser == "f":
            addopt = False
            options = webdriver.FirefoxOptions()
        elif self.browser == "s":
            addopt = False
            options = webdriver.SafariOptions()
        else:
            options = webdriver.ChromeOptions()
        if addopt:
            options.add_argument("--disable-features=DownloadBubble") 
            options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            options.add_experimental_option("prefs", {\
                "download.default_directory":os.getcwd(), \
                "download_bubble.partial_view_enabled": False, \
                "download.prompt_for_download": False, \
                "profile.default_content_setting_values.automatic_downloads": 1})
        if self.mode == "c":
            options.add_argument("--headless")
            options.add_argument("--window-position=-10000,-10000")
            options.add_argument("--no-default-browser-check")           

        try:
            if self.browser == "e":
                self.driver = webdriver.Edge(options=options)
            elif self.browser == "f":
                self.driver = webdriver.Firefox(options=options)
            elif self.browser == "s":
                self.driver = webdriver.Safari(options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
        except Exception as e:
            print(e)
            return False

        self.__loadSaveConfiguration("r")
        if self.htmlroot is None:
            if "htmlroot" in self.settings:
                self.htmlroot = self.settings["htmlroot"]
            else:
                locdir = self.__getFilenameFromDialog("Set a directory to locate GUI source files", "htmlroot", False, True, True)
                if locdir == "":
                    return False
                else:
                    if LocateSourceFiles(locdir, "src") == False:
                        return False
                    self.htmlroot = os.path.join(locdir, "src", "index.html")
                    self.settings["htmlroot"] = self.htmlroot
            self.htmlroot = GetHTMLRoot(self.htmlroot)
        self.driver.get(self.htmlroot)

#       space for compatibility with spectra
        defsetting = self.driver.execute_script("return Settings;")
        if len(self.settings) == 0:
            self.settings = defsetting
        else:
            self.settings = {**defsetting, **self.settings}
            self.driver.execute_script('SetFromPython("Settings", arguments[0]);', self.settings)
        self.driver.execute_script("SetSettingsGUI();")
        if "window" in self.settings:
            winsize = self.settings["window"]
        else:
            winsize = {"width": 880, "height": 780}
        self.driver.set_window_size(winsize["width"], winsize["height"])        
        if "position" in self.settings:
            winpos = self.settings["position"]
            self.driver.set_window_position(winpos["x"], winpos["y"])        
        if "lastid" in self.settings:
            self.driver.execute_script('SetFromPython("fileid", arguments[0]);', self.settings["lastid"])
        self.menulabels = self.driver.execute_script("return GetMenuItems();")
        self.pymode = self.menulabels["modes"]["gui"] if self.mode == "g" else self.menulabels["modes"]["script"]
        self.driver.execute_script('SetFromPython("Framework", arguments[0]);', self.pymode)
        self.driver.execute_script("ArrangeMenus();")
        self.driver.execute_script("GUIConf.GUIpanels[arguments[0]].SetPanel();", self.menulabels["outfile"])
        if self.pymode == self.menulabels["modes"]["gui"]:
            self.driver.execute_script("AddMenuPython();")
        if filename != "":
            self.__open(filename, True)
        else:
            if "lastloaded" in self.settings:
                filename = self.settings["lastloaded"]
                id = self.menulabels["separator"].join([self.menulabels["menuitems"]["file"], self.menulabels["menuitems"]["open"]])
                self.FileMenu(id, filename)
        if self.mode == "i":
            self.driver.execute_script("GUIConf.postprocessor.DisableRun();")
            self.watch = threading.Thread(target=self.__watchCommand)
            self.watch.start()
        return True

    def Exit(self):
        if self.mode == "i":
            self.driver.execute_script(\
                "PyQue.Put(arguments[0]);", self.menulabels["menuitems"]["exit"])
            self.watch.join()
        self.__end()

    def FileMenu(self, id, filename = None):
        issaveas = self.menulabels["menuitems"]["saveas"] in id
#       space for compatibility with spectra        
        issave = issaveas or self.menulabels["menuitems"]["save"] in id
        if issave and self.currfile == "":
            issaveas = True
        if self.menulabels["menuitems"]["new"] in id:
            self.currfile = ""
        elif self.menulabels["menuitems"]["exit"] in id:
            self.__end()
        elif self.menulabels["menuitems"]["open"] in id \
                or self.menulabels["menuitems"]["outpostp"] in id\
                or self.menulabels["menuitems"]["loadf"] in id:
            if filename is None:
                filename = self.__getFilenameFromDialog("Open", id, True)
            if filename == "":
                return
            self.__udloadFile(filename, id, "upload")
            if not self.menulabels["menuitems"]["outpostp"] in id:
                self.currfile = filename
                self.settings["lastloaded"] = filename
                self.settings["lastid"] = id
        elif issave:
            if issaveas:
                if filename is None:
                    filename = self.__getFilenameFromDialog("Save", id, False)
                if filename == "":
                    return
                self.currfile = filename
                self.settings["lastloaded"] = filename
            if self.currfile != "":
                if issaveas:
                    self.driver.execute_script("SetWindowTitle(arguments[0]);", self.currfile)
                self.driver.execute_script("SetObjectScript(arguments[0]);", id)
                self.__udloadFile(self.currfile)
   
    def Show(self, tablabel):
        if self.mode == "c":
            return
        if tablabel in self.menulabels["tablabels"]:
            tablabel = self.menulabels["tablabels"][tablabel]
        if tablabel in self.menulabels["tabs"]:
            id = self.menulabels["tabs"][tablabel]
            msg = self.driver.execute_script("return CommandScript(arguments[0]);", id)
            if msg != "":
                print(msg)
        else:
            category = self.__getID(tablabel)
            isok = self.driver.execute_script("return SelectTab(arguments[0]);", category)
            if isok == False:
                print(f'Invalid category "{tablabel}".')

    def GetLabel(self, categ):
        categid = self.__getID(categ)
        return self.driver.execute_script("return GetPrmLabels(arguments[0]);", categid)

    def Get(self, category, label):
        categid = self.__getID(category)
        return self.driver.execute_script("return GetGUIShown(arguments[0], arguments[1]);", categid, label)

    def Set(self, category, label, value):
        ischk = category == "ebeam" and label == "bmprofile"
        categid = self.__getID(category)
        self.Show(categid)
#       space for compatibility with spectra
        prmlabels = self.driver.execute_script("return GetPrmLabels(arguments[0]);", categid)

        if label in prmlabels["label"]:
            label = prmlabels["label"][label]

        if (label in prmlabels["format"]) == False:
            print(f'Error: "{label}" is invalid or currently not available.')
            return
    
        format = prmlabels["format"][label]
        if format == "directory" or format == "filename":
            value = abspath(value)

        islist = False
        isobj = False
        isbool = False
        isselect = False
        isfile = False
        if isinstance(format, list):
            if (value in format) == False:
                print(f'Error: "{label}" should be selected from {format}.')
                return
            isselect = True
        elif format == "list":
            if isinstance(value, list) == False:
                print(f'Error: "{label}" should be a list.')
                return
            elif len(value) != 2:
                print(f'Error: "{label}" should be a list with 2 items.')
                return
            islist = True
        elif format == "bool":
            if type(value) != bool:
                print(f'Error: "{label}" should be a boolean (True or False).')
                return
            isbool = True
        elif format == "dict":
            if isinstance(value, dict) == False:
                print(f'Error: "{label}" should be an object (dict).')
                return
            isobj = True
        elif format == "spreadsheet":
            if isinstance(value, list) == False:
                print(f'Error: "{label}" should be a 2D list.')
                return
            if len(value) > 0:
                if isinstance(value[0], list) == False:
                    print(f'Error: "{label}" should be a 2D list.')
                    return
            isobj = True
        elif format == "filename":
            if os.path.isfile(value) == False:
                print(f'Error: "{value}" should be an existing file.')
                return
            isfile = True
        elif format == "directory":
            if os.path.isdir(value) == False:
                print(f'Error: "{value}" should be an existing directory.')
                return
            isfile = True

        if islist:
            for j in range(2):
                id = self.menulabels["separator"].join([categid, label, str(j)])
                element = self.driver.find_element(By.ID, id)
                self.driver.execute_script('SetFromPython("element", arguments);', id, "")
                element.send_keys(value[j])
                element.send_keys(Keys.RETURN)
        else:
            if isobj:
                self.driver.execute_script('SetFromPython("guipanel", arguments);', categid, label, value)
#                
#           space for compatibility with spectra
#
            else:
                id = self.menulabels["separator"].join([categid, label])
                element = self.driver.find_element(By.ID, id)
                if isbool:
                    if value != element.is_selected():
                        element.click()
                else:
                    if isselect:
                        select = Select(element)
                        select.select_by_visible_text(value)
                        if ischk:
                            self.CheckParticleData()
                    else:
                        if category == "spxout":
                            isspx = self.driver.execute_script("return IsSPXOut();")
                            if isspx == False:
                                print('This parameter is not available. Select "SIMPLEX Output" for the electron beam and/or seed light.')
                                return
                            if prmlabels["label"]["spxfile"] in id:
                                if HandleLocalFile(value, "r", "json", None, self.fresult) == False:
                                    print("Cannot load "+value+" : "+self.fresult["msg"])
                                    return
                                self.driver.execute_script('SetFromPython("spxout", arguments[0]);', self.fresult["data"])
                        self.driver.execute_script('SetFromPython("element", arguments);', id, "")
                        element.send_keys(value)
                        if isfile:
                            self.driver.execute_script("GUIConf.GUIpanels[arguments[0]].SetPanel();", categid)
                        else:
                            if format == "string":
                                element.send_keys(Keys.TAB)
                            else:
                                element.send_keys(Keys.RETURN)

    def SetFromPython(self, command, object):
        self.driver.execute_script('SetFromPython(arguments[0], arguments[1]);', command, object)

    def CheckParticleData(self):
        if self.Get("ebeam", "bmprofile") != self.menulabels["partdata"]:
            return
        partfile = self.driver.execute_script("return GetParticleDatapath();")
        if partfile != "":
            self.PreProcess("click", "load", partfile)

    def CreateScanProcess(self, category, label, dim, method2d, objrange, jxy = -1, bundle = True):      
#        calctype = self.driver.execute_script("return GUIConf.GUIpanels[ConfigLabel].JSONObj[TypeLabel];")
#        if calctype == "":
#            print("Select the calculation type before scanning a parameter.")
#            return False
#
        categid = self.__getID(category)
        prmlabels = self.driver.execute_script("return GetPrmLabels(arguments[0]);", categid)
        if label in prmlabels["label"]:
            label = prmlabels["label"][label]

        availability = self.driver.execute_script(\
            "return GetScanAvailability(arguments[0], arguments[1]);", categid, label)
        if availability["dimension"] == 0:
            print(f'Error: "{categid} - {label}" cannot be scanned under the current condition.')
            return False
        if availability["dimension"] != dim:
            print(f'Error: dimension of "{categid} - {label}" is inconsistent.')
            return False
        
        srange = [
            objrange["initial"],
            objrange["final"],
            objrange["interval"] if availability["integer"] else objrange["points"],
            objrange["iniSN"]
        ]

        scanobj = {}
        scanobj["dimension"] = availability["dimension"]
        scanobj["integer"] = availability["integer"]
#        scanobj["bundle"] = bundle ; not allowed in simplex
        scanobj["range"] = srange

        methods = [
            self.menulabels["scan2ds"],
            self.menulabels["scan2dl"],
            self.menulabels["scan2dm"]
        ]
        if method2d < 0 or method2d >= len(methods):
            scanobj["method"] = None
        else:
            scanobj["method"] = methods[method2d]

        self.driver.execute_script(\
            "CreateScanDirect(arguments[0], arguments[1], arguments[2], arguments[3]);", \
            categid, label, jxy, scanobj)
        return True

    def Command(self, *items):
        if(len(items) > 1):            
            id = self.__getID(list(items))
        else:
            id = items[0]
        if self.menulabels["menuitems"]["file"] in id:
            if self.menulabels["menuitems"]["exit"] in id:
                self.Exit()
            else:
                self.FileMenu(id)
        elif self.menulabels["menuitems"]["run"] in id:
            if self.menulabels["menuitems"]["export"] in id:
                filename = self.__getFilenameFromDialog("Export", id, False)
                if filename == "":
                    return
                self.driver.execute_script("ExportCommand();")
                self.__udloadFile(filename)
            elif self.menulabels["menuitems"]["python"] in id:
                filename = self.__getFilenameFromDialog("Open a python scrict file", id, True, True)
                if filename == "":
                    return        
                ExecuteFile(filename)
                self.driver.execute_script("PyQue.Clear();")
            elif self.menulabels["menuitems"]["start"] in id:
                self.driver.execute_script("RunCommand(arguments[0]);", id)
                objid = self.driver.execute_script("return GUIConf.simproc.length-1;")
                while self.driver.execute_script("return GUIConf.simproc[arguments[0]].Status();", objid) == 1:
                    self.__run(objid)
            elif self.menulabels["menuitems"]["runpostp"] in id:
                objid = self.driver.execute_script("return GUIConf.simproc.length-1;")
                self.__run(objid, True)
            else:
                self.driver.execute_script("return CommandScript(arguments[0]);", id)
        elif self.menulabels["dialogs"]["grid"] in id:
            filename = self.__getFilenameFromDialog("Import a data file", id, False, True)
            if filename == "":
                return
            self.__udloadFile(filename, None, "download", True)
        elif self.menulabels["menuitems"]["postproc"] in id:
            self.PostProcess("click", id)
        elif self.menulabels["menuitems"]["preproc"] in id:
            self.PreProcess("click", id)
        elif self.menulabels["menuitems"]["duplicate"] in id:
            issave = self.menulabels["menuitems"]["save"] in id
            filename = self.__getFilenameFromDialog("Save", id, False, issave == False)
            if filename == "":
                return
            if issave:
                self.__udloadFile(filename)
                return
            data = self.driver.execute_script("return GetBufferData(arguments[0], true);", self.datalimit)
            files = GetSerialFilenames(len(data), filename)
            for i, datum in enumerate(data):
                if HandleLocalFile(files[i], "w", "ascii", datum, self.fresult) == False:
                    print(self.fresult["msg"])            
        else:
            msg = self.driver.execute_script("return CommandScript(arguments[0]);", id)
            if msg != "":
                print(msg)
    
    def GetDataNames(self):
        outfiles = self.datanames[:]
        return outfiles

    def SetSettings(self, categ, item, value):
        settings = self.driver.execute_script("return Settings;")
        categid = self.__getID(categ)
        prmlabels = self.driver.execute_script("return GetSettingLabels(arguments[0]);", categid)
        if prmlabels is None:
            print(f'Invalid category name "{categ}".')
            return
        if item in prmlabels:
            item = prmlabels[item][0]
        if not item in settings[categid]:
            print(f'Invalid item name "{item}".')
            return
        settings[categid][item] = value
        settings["categ"] = categid
        self.driver.execute_script('SetFromPython("Settings", arguments[0]);', settings)

    def SetOutputFile(self, **kwargs):
        prmobjs = self.GetLabel("outfile")["label"]
        labels = [*prmobjs.keys(), *prmobjs.values()]
        for key in kwargs:
            if key in labels:
                self.Set("outfile", key, kwargs[key])

    def PlotScale(self, postproc, **kwargs):
        options = {}
        for xy, key in (("x", "xscale"), ("y", "yscale")): 
            if xy in kwargs:
                if kwargs[xy] == "log":
                    scale = self.menulabels["log"]
                else:
                    scale = self.menulabels["linear"]
                options[key] = scale
        if postproc:
            self.PostProcess("plotoption", options)
        else:
            self.PreProcess("plotoption", options)

    def PlotRange(self, postproc, **kwargs):
        options = {}
        for xy, key in (("x", "xrange"), ("y", "yrange")): 
            if xy in kwargs:
                if isinstance(kwargs[xy], list):
                    options[key] = kwargs[xy]
        if postproc:
            self.PostProcess("plotoption", options)
        else:
            self.PreProcess("plotoption", options)

    def NormalizePlot(self, postproc, normalize):
        options = {}
        options["normalize"] = self.menulabels["foreach"] if normalize else self.menulabels["bymax"]
        if postproc:
            self.PostProcess("plotoption", options)
        else:
            self.PreProcess("plotoption", options)

    def Plot1DType(self, postproc, **kwargs):
        options = {}
        opt1ds = ["type", "size", "width"]
        ptypes = [self.menulabels["line"], self.menulabels["linesymbol"], self.menulabels["symbol"]]
        for opt1d in opt1ds:
            if opt1d in kwargs:
                if opt1d == "type":
                    options[opt1d] = ptypes[kwargs[opt1d]]
                else:
                    options[opt1d] = kwargs[opt1d]

        if postproc:
            self.PostProcess("plotoption", options)
        else:
            self.PreProcess("plotoption", options)

    def Plot2DType(self, postproc, ptype, wireframe = False):
        plottypes = [
            self.menulabels["contour"],
            self.menulabels["surface"],
            self.menulabels["shade"]
        ]
        options = {}
        options["type2d"] = plottypes[ptype]
        options["wireframe"] = wireframe
        if postproc:
            self.PostProcess("plotoption", options)
        else:
            self.PreProcess("plotoption", options)

    def DuplicatePlot(self, ispreproc, *titles):
        if ispreproc:
            self.driver.execute_script("ExportPreProcess(1, arguments[0]);", titles)
        else:
            self.driver.execute_script("GUIConf.postprocessor.DuplicatePlot(arguments[0]);", titles)
        while self.driver.execute_script("return PlotRunning();"):
            time.sleep(0.5)

    def PreProcess(self, command, item, filename = None):
        if self.mode == "c":
            print("Pre-processing not available in CUI mode.")
            return
        self.Show("preproc")
        if command == "select":
            if self.__select("preproc-select", item):
                command = self.driver.execute_script("return PyQue.Get();")
                if command != "":
                    obj = self.driver.execute_script("return GetPPObject();")
                    self.__runPreProcess(obj)
        elif command == "partplot":
            if item[0] == "slice":
                self.Set("partplot", "type", self.menulabels["partslice"])
                self.Set("partplot", "item", item[1])
            elif item[0] == "bins":
                self.Set("partplot", "item", item[1])            
            else:
                self.Set("partplot", "type", self.menulabels["partdata"])
                for key in item[1]:
                    if key == "x":
                        self.Set("partplot", "xaxis", item[1]["x"])
                    elif key == "y":
                        self.Set("partplot", "yaxis", item[1]["y"] )
                    elif key == "max":
                        self.Set("partplot", "plotparts", item[1]["max"])
        elif command == "click":
            id = self.__getID(item, self.menulabels["menuitems"]["preproc"])
            if self.menulabels["menuitems"]["ascii"] in id:
                if filename is None:
                    filename = self.__getFilenameFromDialog("Export", id, False, True)
                if filename == "":
                    return
                data = self.driver.execute_script("return GUIConf.plotly.GetASCIIData();")
                if HandleLocalFile(filename, "w", "ascii", data, self.fresult) == False:
                    print(self.fresult["msg"])
            elif self.menulabels["menuitems"]["import"] in id:
                if filename is None:
                    filename = self.__getFilenameFromDialog("Import", id, True, True)
                if filename == "":
                    return
                self.__udloadFile(filename, id, "upload")
            elif self.menulabels["menuitems"]["load"] in id:
                btype = self.Get("ebeam", "bmprofile")
                if btype != self.menulabels["partdata"]:
                    print('"'+self.menulabels["partdata"]+'"'+" should be chosen for the bunch profile.")
                    return
                self.PreProcess("select", self.menulabels["partana"])
                if filename is None:
                    filename = self.driver.execute_script("return GetParticleDatapath();")
                    if filename == "":
                        filename = self.__getFilenameFromDialog("Load", id, True, True)
                        if filename == "":
                            return
                        self.Set("ebeam", "partfile", filename)
                else:
                    self.Set("ebeam", "partfile", filename)                    
                self.__udloadFile(filename, id, "upload")
                self.Show("preproc")
            elif self.menulabels["menuitems"]["optimize"] in id or \
                    self.menulabels["menuitems"]["seedrun"] in id:
                obj = self.driver.execute_script("return GetPPObject();")
                self.__runPreProcess(obj)
            else:
                self.driver.execute_script("return CommandScript(arguments[0]);", id)
        elif command == "plotoption":
            self.driver.execute_script("ChangePlotOptions(arguments[0]);", item)
     
    def PostProcess(self, command, items, filename = None):
        if self.mode == "c":
            print("Post-processing not available in CUI mode.")
            return False
        self.Show("postproc")

        if command == "plotoption":
            self.driver.execute_script("GUIConf.postprocessor.ChangePlotOptions(arguments[0]);", items)
            return True
        if command == "startanim":
            self.driver.execute_script("GUIConf.postprocessor.StartAnimation();")
            return True
        if command == "slide":
            self.driver.execute_script("GUIConf.postprocessor.SwitchSlide(arguments[0]);", items)
            return True
        if command == "set":
            self.Set("dataprocess", *items)
            return True
        if command == "select":
            if isinstance(items, list) == False:
                print("Invalid command. Item must be a list with more than 2 elements.")
                return False
            id = self.driver.execute_script(\
                "return GUIConf.postprocessor.GetSelectID(arguments[0]);", items[0])
            if id == "":
                print(f'Invalid command. "{items[0]}" not found.')
                return False
            itemok = items[1:] 
            if items[0] == "comparative" or items[0] == "multiplot":
                categ = self.driver.execute_script("return GUIConf.postprocessor.GetCurrentCategory();")
                options = self.__optionTexts(id)
                itemok = []
                for item in items[1:]:
                    if items[0] == "comparative" and categ != "":
                        item = self.menulabels["separator"].join([item, categ])
                    if item in options:
                        itemok.append(item)                
            return self.__select(id, itemok)
        if command == "subcols":
            if isinstance(items, list) == False:
                print("Invalid command. Item must be a list with more than 2 elements.")
                return False
            id = self.driver.execute_script(\
                "return GUIConf.postprocessor.GetColumnsID(arguments[0]);", items[0] == "sub")
            element = self.driver.find_element(By.ID, id)            
            self.driver.execute_script('SetFromPython("element", arguments);', id, "")
            element.send_keys(int(items[1]))
            element.send_keys(Keys.RETURN)
            return True
        
        if isinstance(items, str) == False:
            print("Invalid command. Item must be a string.")
            return False

        if command == "click":
            id = self.__getID(items, self.menulabels["menuitems"]["postproc"])
            isascii = self.menulabels["menuitems"]["ascii"] in id
            issave = self.menulabels["menuitems"]["save"] in id
            if isascii or issave:
                if filename is None:
                    filename = self.__getFilenameFromDialog("Export", id, False, isascii)
                if filename == "":
                    return False
                if isascii:
                    data = self.driver.execute_script("return GUIConf.postprocessor.GetASCIIData();")
                    files = GetSerialFilenames(len(data), filename)
                    for i, datum in enumerate(data):
                        if HandleLocalFile(files[i], "w", "ascii", datum, self.fresult) == False:
                            print(self.fresult["msg"])
                else:
                    id = self.menulabels["separator"].join([self.menulabels["menuitems"]["postproc"], id])
                    self.driver.execute_script("SetObjectScript(arguments[0]);", id)
                    self.__udloadFile(filename)
            elif self.menulabels["menuitems"]["import"] in id:
                filename = self.__getFilenameFromDialog("Import", id, True, False, False, True)
                if filename == "":
                    return False
                for filen in filename:
                    self.__udloadFile(filen, id, "upload")
            else:
                self.driver.execute_script(\
                    "GUIConf.postprocessor.Click(arguments[0]);", items)
        else:
            id = self.driver.execute_script(\
                "return GUIConf.postprocessor.GetCheckID(arguments[0]);", items)
            if id == "":
                print(f'Invalid command. "{items}" not found.')
                return False
            element = self.driver.find_element(By.ID, id)
            if (command == "enable" and element.is_selected() == False) \
                    or (command == "disable" and element.is_selected() == True):
                element.click()
        return True

    def LoadOutput(self, datapath):
        if self.mode == "c":
            if HandleLocalFile(datapath, "r", "json", None, self.fresult) == False:
                print(self.fresult["msg"])
                return
            if self.menulabels["output"] in self.fresult["data"]:
                dataname = os.path.splitext(os.path.basename(datapath))[0]
                self.databuffer[dataname] = self.fresult["data"][self.menulabels["output"]]
                self.datanames.append(dataname)
        else:
            id = self.menulabels["separator"].join([self.menulabels["menuitems"]["postproc"], self.menulabels["menuitems"]["import"]])
            self.__udloadFile(datapath, id, "upload")

    def GetObj(self, dataname, type = None, index = 0, detail = None):
        if not self.mode == "c":
            print("Not available in GUI and interactive modes.")
            return None
        if not dataname in self.databuffer:
            print(f'No data named "{dataname}" found.')
            return None
        
        obj = self.databuffer[dataname]
        if type is None:
            return obj
        elif type == "title":
            return obj[self.menulabels["titles"]]
        elif type == "unit":
            return obj[self.menulabels["units"]]
        elif type == "dimension":
            return obj[self.menulabels["dimension"]]
        elif type == "detail":
            if not self.menulabels["details"] in obj:
                print('"details" object not available in this data.')
                return None
            return obj[self.menulabels["details"]]

        data = obj[self.menulabels["data"]]
        dim = obj[self.menulabels["dimension"]]
        if self.menulabels["details"] in obj:
            if detail is None:
                print('"details" index should be specified in this data.')
                return None
            if detail >= len(obj[self.menulabels["data"]]):
                print("Too large detail index.")
                return None
            data = obj[self.menulabels["data"]][detail]
        items = len(data)-dim

        if type == "data":
            if index >= items:
                print("Too large data index.")
                return None
            return data[index+dim]
        elif type == "axis":
            return data[0:dim]
        return None

    def ClearBuffer(self):
        self.databuffer.clear()
        self.datanames.clear()

    def OpenFile(self, file, *items):
        file = abspath(file)
        if not os.path.exists(file):
            print(f'File "{file}" does not exist.')
            return
        menuitems = []
        for item in items:
            menuitems.append(self.menulabels["menuitems"][item])
        id = self.menulabels["separator"].join(menuitems)
        self.FileMenu(id, file)

    def FitWindow(self):
        if self.mode == "c":
            return
        winsize = self.driver.execute_script("return RelativeFitWindowSize();")
        currsize = self.driver.get_window_size()
        currpos = self.driver.get_window_position()
        self.driver.set_window_size(currsize["width"]+winsize[0], currsize["height"]+winsize[1])
        self.driver.set_window_position(currpos["x"], currpos["y"])
    
    def ExpandWindow(self, **kwargs):
        if self.mode == "c":
            return
        height = 1
        width = 1
        if "h" in kwargs:
            height = kwargs["h"]
        if "height" in kwargs:
            height = kwargs["height"]
        if "w" in kwargs:
            width = kwargs["w"]
        if "width" in kwargs:
            width = kwargs["width"]
        currsize = self.driver.get_window_size()
        width = min(10, max(0.1, width))
        height = min(10, max(0.1, height))
        self.driver.set_window_size(currsize["width"]*width, currsize["height"]*height)
    
    def GetDisplaySize(self):
        currsize = self.driver.get_window_size()
        self.driver.maximize_window()
        self.displaysize = self.driver.get_window_size()
        self.driver.set_window_size(currsize["width"], currsize["height"])

    def Move(self, **kwargs):
        if self.displaysize is None:
            self.GetDisplaySize()
        currsize = self.driver.get_window_size()
        currpos = self.driver.get_window_position()
        width = self.displaysize["width"]
        height = self.displaysize["height"]
        px = currpos["x"]
        py = currpos["y"]
        if "x" in kwargs:
            if kwargs["x"] == "r":
                px = width-currsize["width"]
            elif kwargs["x"] == "c":
                px = width/2-currsize["width"]/2
            elif  kwargs["x"] == "l":
                px = 0
            elif isinstance(kwargs["x"], int) or isinstance(kwargs["x"], float):
                px = kwargs["x"]
        if "y" in kwargs:
            if kwargs["y"] == "b":
                py = height-currsize["height"]
            elif kwargs["y"] == "c":
                py = height/2-currsize["height"]/2
            elif  kwargs["y"] == "t":
                py = 0
            elif isinstance(kwargs["y"], int) or isinstance(kwargs["y"], float):
                py = kwargs["y"]
        self.driver.set_window_position(px, py)
        cr = self.driver.get_window_position()

    async def RunGUI(self, filename = ""):
        if self.browser == "s":
            print("Cannot run as a GUI application with Safari! Select other browsers.")
        else:
            if self.Start(filename, "g"):
                await self.LoopGUI()
                self.__end()

    async def LoopGUI(self):
        self.driver.execute_script("GUIConf.GUIpanels[arguments[0]].SetPanel();", self.menulabels["outfile"])
        while True:
            await asyncio.sleep(0.5)
            try:
                response = self.driver.execute_script("return PyQue.Get();")
            except UnexpectedAlertPresentException:
                await asyncio.sleep(1)
                continue
            except WebDriverException:
                break

            if response is None:
                break
            elif response == "":
                continue
            elif isinstance(response, list):
                filename = ""
                if self.menulabels["menuitems"]["start"] in response[0] or \
                        self.menulabels["menuitems"]["runpostp"] in response[0]:
                    nompi = self.menulabels["menuitems"]["runpostp"] in response[0]
                    solverthread = threading.Thread(target=self.__run, args=(response[1], nompi))
                    solverthread.start()
                    self.threads.append({"thread": solverthread, "id":response[1]})
                elif self.menulabels["menuitems"]["cancel"] in response[0]:
                    self.cancelproc[response[1]] = True
                elif response[0] == self.menulabels["menuitems"]["preproc"]:
                    self.__runPreProcess(response[1])
                elif self.menulabels["dialogs"]["file"] in response[0]:
                    filename = self.__getFilenameFromDialog("Set data file", response[1], True, True)
                elif self.menulabels["dialogs"]["dir"] in response[0]:
                    filename = self.__getFilenameFromDialog("Set directory", response[1], False, True, True)
                if filename != "":
                    items = self.driver.execute_script("return GetItemFromID(arguments[0]);", response[1])
                    if items["item"] == self.menulabels["partdata"]:
                        self.PreProcess("click", "load", filename)
                        self.Show(self.__getID("ebeam"))
                    else:
                        self.Set(items["categ"], items["item"], filename)
            elif self.menulabels["menuitems"]["exit"] in response:
                break
            else:
                self.Command(response)

    def MenuLabels(self, label):
        return self.menulabels["menuitems"][label]

def GetHTMLRoot(htmlroot):
    if htmlroot == "":
        htmlroot = os.path.join(HTML_SRC_DIR, "index.html")
    if os.path.isfile(htmlroot) == False:
        return ""
    htmlroot = "file:///"+htmlroot.replace("\\", "/")
    return htmlroot

def ScanSingle(category, label, initial, final, points, jxy, dim, method, **kwargs):
    rangeobj = {
        "interval": 1,
        "iniSN": 0
    }
    for key in rangeobj.keys():
        if key in kwargs:
            rangeobj[key] = kwargs[key]   
    rangeobj["initial"] = initial
    rangeobj["final"] = final
    rangeobj["points"] = points

    bundle = False
#    if "bundle" in kwargs:
#        bundle = kwargs["bundle"]

    ui_main.SetOutputFile(**kwargs)
    isok = ui_main.CreateScanProcess(category, label, dim, method, rangeobj, jxy, bundle)
    if not isok:
        print("Failed to create a parameter scan process.")
    else:
        ui_main.Command("run", "start")

# functions available in simplex moodule
def Start(**kwargs):
    """Launch SIMPLEX with options

    Args:
        **kwargs (dict): parameters to specify the configurations. See below for possible keys and their meanings.
        src (str): specify the location of the source files; "r" = remote (default), "l" = local
        browser (str): specify the browser; "c" = Chrome (default), "e" = Edge, "f" = Firefox, "s" = Safari
        file (str): path to the parameter file to open (default = "")
    
    Returns:
        None
    
    Examples:
        >>> simplex.Start(src="l", file="./sample.json") 
        # open the source files in the local repository with the Chrome browser, 
        # with the parameter file "sample.json"
    """
    src = "r"
    browser = "c"
    mode = "i"
    prmfile= ""
    if "src" in kwargs:
        src = kwargs["src"]
    if "browser" in kwargs:
        browser = kwargs["browser"]
    if "mode" in kwargs:
        mode = kwargs["mode"]
    if "file" in kwargs:
        prmfile = kwargs["file"]
    global ui_main
    ui_main = SIMPLEX(src, browser)
    if mode == "g":
        asyncio.run(ui_main.RunGUI())
    else:
        ui_main.Start(prmfile, mode)

def Exit():
    """Finish SIMPLEX and exit

    Args:
        None
    
    Returns:
        None
    """
    ui_main.Exit()

def Open(file):
    """Opens a SIMPLEX parameter file.

    Args:
        file (str): path to the parameter file
    
    Returns:
        None
    
    Examples:
        >>> simplex.Open("./sample.json") 
        # open a parameter file "sample.json" in the current directory
    """
    ui_main.OpenFile(file, "file", "open")

def Set(category, label, value):
    """Set a parameter or an option

    Args:
        category (string): specify the category of the target parameter
        label (string): name of the target parameter
        value (any): value to be set

    Returns:
        None

    Examples:
        >>> simplex.Set("ebeam", "eenergy", 6.0) 
        # set the electron energy to 6.0 GeV

    Note:
        Refer to the `keyword list <parameters.html#main-input-parameters>`__ for the name of the target parameter.
    """
    ui_main.Set(category, label, value)

def Get(category, label):
    """Get a value of a parameter automatically evaluated and being shown in the GUI

    Args:
        category (string): specify the category of the target parameter
        label (string): name of the target parameter

    Returns:
        value of the specified parameter

    Examples:
        >>> simplex.Get("felprm", "rho") 
        # Get the FEL parameter

    Note:
        Refer to the `keyword list <parameters.html#main-input-parameters>`__ for the name of the target parameter.
    """
    return ui_main.Get(category, label)

#
#
#
#   space for compatibility with spectra
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#   space for compatibility with spectra
#
#
#

def StartSimulation(**kwargs):
    """Start the calculation process

    Args:
        kwargs["folder"] (str): directory to put the output file
        kwargs["prefix"] (str): name of the output file
        kwargs["serial"] (str): serial number of the output file


    Returns:
        None

    Examples:
        >>> simplex.StartSimulation(folder=".", prefix="sample", serial=1) 
        # start the calculation to generate an output file "./sample-1.json"

    Note:
        If more than one calculation process is created before, this funcion simply launches the existing processes and the arguments are not functional.
    """
    ui_main.SetOutputFile(**kwargs)
    ui_main.Command("run", "start")

def CreateProcess(**kwargs):
    """Create a calculation process with the current parameters

    Args:
        kwargs["folder"] (str): directory to put the output file
        kwargs["prefix"] (str): name of the output file
        kwargs["serial"] (str): serial number of the output file
        

    Returns:
        None

    Examples:
        >>> simplex.CreateProcess(folder=".", prefix="sample", serial=1) 
        # create a calculation process to generate an output file "./sample-1.json"

    """
    ui_main.SetOutputFile(**kwargs)
    ui_main.Command("run", "process")

def LoadOutput(file):
    """Load an output file generated in the former calculation for post-processing.

    Args:
        file (str): path to the output file
    
    Returns:
        None
    
    Examples:
        >>> simplex.LoadOutput("./output.json") # load the output file "output.json" in the current directory
    """
    ui_main.OpenFile(id, file, "file", "loadf")

def ShowPreProcessor():
    """Switch the tabbled panel to "Pre-Processing".

    Args:
        None
    
    Returns:
        None
    
    """
    ui_main.Show("preproc")

def ShowPostProcessor():
    """Switch the tabbled panel to "Post-Processing".

    Args:
        None
    
    Returns:
        None
    
    """
    ui_main.Show("postproc")

def Scan(category, label, initial, final, points = 11, **kwargs):
    """Create a parameter-scan process (1D).

    Args:
        category (string): specify the category of the target parameter
        label (string): name of the target parameter
        initial (number): initial value for scanning
        final (number): final value for scanning
        points (number): number of points for scanning
        kwargs["folder"] (str): directory to put the output file
        kwargs["prefix"] (str): name of the output file
        kwargs["serial"] (number): serial number of the output file
        kwargs["iniSN"] (number): initial suffix number for scan
        kwargs["interval"] (number): step interval if the target parameter is an integer
    
    Returns:
        None

    Examples:
        >>> simplex.Scan("ebeam", "eenergy", 6, 8, folder=".", prefix="scan") 
            # scan the electron energy from 6 to 8 GeV with an interval of 0.2 GeV (11 points); 
            # the output files are "./scan-1.json" etc.
    
    """
    ScanSingle(category, label, initial, final, points, -1, 1, -1, **kwargs)
#       
#   space for compatibility with spectra

def ScanX(category, label, initial, final, points = 11, **kwargs):
    """Create a parameter-scan process (1D, along x axis).

    Args:
        category (string): specify the category of the target parameter, should be either of "acc" (Accelerator), "src" (Light Source) or "config" (Configurations)
        label (string): name of the target parameter
        initial (number): initial value for scanning
        final (number): final value for scanning
        points (number): number of points for scanning
        kwargs["folder"] (str): directory to put the output file
        kwargs["prefix"] (str): name of the output file
        kwargs["serial"] (str): serial number of the output file
        kwargs["iniSN"] (number): initial suffix number for scan
        kwargs["interval"] (number): step interval if the target parameter is an integer
    
    Returns:
        None

    Examples:
        >>> simplex.ScanX("ebeam", "emitt", 0.5, 1, 6, folder=".", prefix="scanx") 
            # scan the horizontal emittance from 0.5 to 1 mm.mrad with an interval of 0.1 mm.mrad (6 points); 
            # the output files are "./scanx-1.json" etc.
    
    """
    ScanSingle(category, label, initial, final, points, 0, 2, 0, **kwargs)
#
#   space for compatibility with spectra

def ScanY(category, label, initial, final, points = 11, **kwargs):
    """Create a parameter-scan process (1D, along y axis).

    Args:
        category (string): specify the category of the target parameter, should be either of "acc" (Accelerator), "src" (Light Source) or "config" (Configurations)
        label (string): name of the target parameter
        initial (number): initial value for scanning
        final (number): final value for scanning
        points (number): number of points for scanning
        kwargs["folder"] (str): directory to put the output file
        kwargs["prefix"] (str): name of the output file
        kwargs["serial"] (str): serial number of the output file
        kwargs["iniSN"] (number): initial suffix number for scan
        kwargs["interval"] (number): step interval if the target parameter is an integer
    
    Returns:
        None

    Examples:
        >>> simplex.ScanY("ebeam", "emitt", 0.5, 1, 6, folder=".", prefix="scany") 
            # scan the vertical emittance from 0.5 to 1 mm.mrad with an interval of 0.1 mm.mrad (6 points); 
            # the output files are "./scany-1.json" etc.
    
    """
    ScanSingle(category, label, initial, final, points, 1, 2, 0, **kwargs)
#   space for compatibility with spectra
#

def ScanXY(category, label, initial, final, points = [11, 11], **kwargs):
    """Create a parameter-scan process (2D over x-y plane).

    Args:
        category (string): specify the category of the target parameter, should be either of "acc" (Accelerator), "src" (Light Source) or "config" (Configurations)
        label (string): name of the target parameter
        initial (list): initial value for scanning
        final (list): final value for scanning
        points (list): number of points for scanning in x and y directions
        kwargs["folder"] (str): directory to put the output file
        kwargs["prefix"] (str): name of the output file
        kwargs["serial"] (str): serial number of the output file
        kwargs["iniSN"] (number): initial suffix number for scan
        kwargs["interval"] (list): step interval if the target parameter is an integer
        kwargs["link"] (bool): if enabled, X and Y prameters are scanned at the same time
    
    Returns:
        None

    Examples:
        >>> simplex.ScanXY("ebeam", "emitt", [0.5, 0.5], [1, 1], [5, 5], folder=".", prefix="scanxy") 
            # scan the observation position in the 2D rectangular grid points defined by 
            # (0.5,0.5) and (1,1) with an interval of 0.1 mm.mrad in both directions (6x6 points); 
            # the output files are "./scanxy-1-1.json" etc.
    
    """
    method = 2
    if "link" in kwargs:
        method = 1 if kwargs["link"] else 2    
    if not isinstance(initial, list):
        initial = [initial, initial]
    if not isinstance(final, list):
        final = [final, final]
    if method == 2 and not isinstance(points, list):
        points = [points, points]
        return
    if "iniSN" in kwargs:
        serial = kwargs["iniSN"]
        if not isinstance(serial, list):
            kwargs["iniSN"] = [serial, serial]
    if "interval" in kwargs:
        interval = kwargs["interval"]
        if not isinstance(interval, list):
            kwargs["interval"] = [interval, interval]     
    ScanSingle(category, label, initial, final, points, 0, 2, method, **kwargs)
#
#   space for compatibility with spectra

def FitWindow():
    """Adjust the size of the browser to show the whole parameters in the Main window. Not effective when Pre-Processing or Post-Processing windows are shown.

    Args:
        None
    
    Returns:
        None
    """
    ui_main.FitWindow()

def ExpandWindow(**kwargs):
    """Expand or shrink the size of the browser.

    Args:
        kwargs["w"] or kwargs["width"] (number): scaling factor in the horizontal direction
        kwargs["h"] or kwargs["height"] (number): scaling factor in the vertical direction
    
    Returns:
        None

    Examples:
        >>> simplex.ExpandWindow("w"=1.2, "h"=0.8) 
            # expand/shrink the window size by 1.2 (horizontal) and 0.8 (vertical)
    """
    ui_main.ExpandWindow(**kwargs)

def MoveWindowX(pos):
    """Move the browser horizontally.

    Args:
        pos (str or number): "l" (left), "c" (center), "r" (right), or a pixel number to specify the horizontal position
    
    Returns:
        None

    Examples:
        >>> simplex.MoveWindowX("l") # move to the left
        >>> simplex.MoveWindowX(100) # move to x = 100px
    """
    ui_main.Move(x=pos)

def MoveWindowY(pos):
    """Move the browser vertically.

    Args:
        pos (str or number): "t" (top), "c" (center), "b" (bottom), or a pixel number to specify the vertical position
    
    Returns:
        None

    Examples:
        >>> simplex.MoveWindowY("t") # move to the top
        >>> simplex.MoveWindowY(100) # move to y = 100px
    """
    ui_main.Move(y=pos)

def MoveWindowXY(x, y):
    """Move the browser in both directions.

    Args:
        x (str or number): "l" (left), "c" (center), "r" (right), or a pixel number to specify the horizontal position
        y (str or number): "t" (top), "c" (center), "b" (bottom), or a pixel number to specify the vertical position
    
    Returns:
        None

    Examples:
        >>> simplex.MoveWindowXY("l", "t") # move to the left & top
        >>> simplex.MoveWindowXY(100, 100) # move to (x, y) = (100px, 100px)
    """
    ui_main.Move(x=x, y=y)

# functions specific to spectra
def LoadPostProcessed(file):
    """Load an output file generated by post-processing the raw data generated in a former simulation.

    Args:
        file (str): path to the output file
    
    Returns:
        None
    
    Examples:
        >>> simplex.LoadPostProcessed("./output.json") # load the output file "output.json" in the current directory
    """
    ui_main.OpenFile(id, file, "file", "outpostp")

# classes available in simplex moodule
class CLI:
    """
    CLI class is available only in the CLI mode and is basically a collection of functions to manage the output data that cannot be imported for visualization (because of no GUI).
    """

    @staticmethod
    def GetDataNames():
        """Get the names of the output data stored in the buffer.

        Args:
            None
    
        Returns:
            list of the data names

        Examples:
            >>> simplex.CLI.GetDataNames()
            ["sample-1", "sample-2"]
        """
        return ui_main.GetDataNames()

    @staticmethod
    def GetLatestDataName():
        """Get the name of the latest output data stored in the buffer.

        Args:
            None
    
        Returns:
            string of the data name

        Examples:
            >>> simplex.CLI.GetLatestDataName()
            "sample-2"
        """
        datanames = ui_main.GetDataNames()
        if len(datanames) == 0:
            return None
        return datanames[-1]

    @staticmethod
    def GetDimension(dataname):
        """Get the dimension of the output data, which means the number of independent variables of the target output data.

        Args:
            dataname: name of the output data
    
        Returns:
            dimension

        Examples:
            >>> simplex.CLI.GetDimension("sample-1")
            1
        """
        return ui_main.GetObj(dataname, "dimension")

    @staticmethod
    def GetTitle(dataname):
        """Get the titles of items in the output data.

        Args:
            dataname: name of the output data
    
        Returns:
            list of the titles

        Examples:
            >>> simplex.CLI.GetTitle("sample-1")
            ["Energy","Flux Density","GA. Brilliance","PL(s1/s0)","PC(s3/s0)","PL45(s2/s0)"]
        """
        return ui_main.GetObj(dataname, "title")

    @staticmethod
    def GetUnit(dataname):
        """Get the units of items in the output data.

        Args:
            dataname: name of the output data
    
        Returns:
            list of the titles

        Examples:
            >>> simplex.CLI.GetUnit("sample-1")
            ["eV","ph/s/mr^2/0.1%B.W.","ph/s/mm^2/mr^2/0.1%B.W.","","",""]
        """
        return ui_main.GetObj(dataname, "unit")
    
    @staticmethod
    def GetDetail(dataname):
        """Available when the output data is composed of more than two independent data sets; for example, spatial dependence calculations along the x and y axes generate 2 independent data sets. In such a case, this function helps to retrieve keywords (=details) to specify each data set.

        Args:
            dataname: name of the output data
    
        Returns:
            list of the details (of respective data sets)

        Examples:
            >>> simplex.CLI.GetDetail("sample-2")
            ["Along x","Along y"]
        """
        return ui_main.GetObj(dataname, "detail")

    @staticmethod
    def GetData(dataname, index, detail = None):
        """Retrieve the desired item from the output data.

        Args:
            dataname: name of the output data
            index: index (starting from 0) of the target item
            detail: keyword to specify the dataset when more than two independent data sets are contained in the output data
    
        Returns:
            list of the data

        Examples:
            >>> simplex.CLI.GetData("sample-1", 1) # Get "GA. Brilliance"
            [4.02638e+14,3.98914e+14,...] 
            >>> simplex.GetData("sample-2", 0, "Along x") # Get "Flux Density"
            [4.02638e+14,3.98914e+14,...]
        """
        return ui_main.GetObj(dataname, "data", index, detail)

    @staticmethod
    def GetAxis(dataname, detail = None):
        """Retrieve the independent variables from the output data.

        Args:
            dataname: name of the output data
            detail: keyword to specify the dataset when more than two independent data sets are contained in the output data
    
        Returns:
            list of the independent variables

        Examples:
            >>> simplex.CLI.GetAxis("sample-1")
            [5000,5005,5010,...]  "Energy"
            >>> simplex.GetAxis("sample-2", "Along x")
            [-0.2,-0.18,-0.16,-0.14,...]  "Position" ("Along x")
        """
        return ui_main.GetObj(dataname, "axis", 0, detail)

    @staticmethod
    def ClearBuffer():
        """Clear the buffer data to reduce the memory consumption. Recommended to call this function if the exsiting output data (stored in the memory buffer) are no more necessary.

        Args:
            None
    
        Returns:
            None

        """
        ui_main.ClearBuffer()

class PreProcess:
    """
    PreProcess class bundles various functions for the operation of pre-processor.
    """

    @staticmethod
    def Import(item, filename):
        """Import the data for the target item from a file.

        Args:
            item (str): name of the target item
            filename (str): name of the data file
    
        Returns:
            None

        Examples:
            >>> simplex.PreProcess.Import("Field Profile", "./uerror_model.dat")
            # import the data file "uerror_model.dat" in the current directory as the field distribution
        """
        ui_main.PreProcess("select", item)
        ui_main.PreProcess("click", "import", filename)

    @staticmethod
    def LoadParticle(filename = None):
        """Load the particle data

        Args:
            filename (str): name of the data file, load "Particle Data" path if not specified
    
        Returns:
            None

        Examples:
            >>> simplex.PreProcess.LoadParticle("./particles.dat")
            # load the particle data from "particles.dat" in the current directory
        """
        ui_main.PreProcess("click", "load", filename)

    @staticmethod
    def ParticleDataFormat(**kwargs):
        """Set the particle data format

        Args:
            kwargs["unitxy"] (str) : unit for x and y (m, mm)
            kwargs["unitxyp"] (str) : unit for x' and y' (rad, mrad)
            kwargs["unitt"] (str) :  unit for time (s, ps, fs, m, mm)
            kwargs["unitE"] (str) : unit for energy (GeV, MeV, gamma)
            kwargs["index"] (list) : column indices for x, x', y, y', t, E
            kwargs["pcharge"] (number) : charge/particle (C)
            kwargs["bins"] (number) : number of bins/RMS bunch length to evaluate slice parameters
    
        Returns:
            None

        Examples:
            >>> spectra.PreProcess.ParticleDataFormat(index=[2,3,4,5,1,6], unitE="gamma")
            # the particle data is arranged as t, x, x', y, y', E
            # the energy is given in gamma (Lorentz factor)
        """
        obj = {}
        if "index" in kwargs:
            if not isinstance(kwargs["index"], list) or len(kwargs["index"]) != 6:
                print("Invalid format: \"index\" parameter should be a list with 6 elements")
                return
            items = ["colx", "colxp", "coly", "colyp", "colt", "colE"]
            for i in range(6):
                obj[items[i]] = kwargs["index"][i]
        units = ["unitxy", "unitxyp", "unitt", "unitE", "pcharge", "bins"]
        for unit in units:
            if unit in kwargs:
                obj[unit] = kwargs[unit]
        ui_main.Show("preproc")
        ui_main.SetFromPython("pformat", obj)

    @staticmethod
    def PlotSliceParameter(item):
        """Plot the slice parameter along the electron bunch

        Args:
            item (str): name of the target parameter
    
        Returns:
            None

        Examples:
            >>> simplex.PreProcess.PlotSliceParameter("Current Profile")
            # plot the current profile of the electron bunch
        """
        ui_main.PreProcess("partplot", ["slice", item])

    @staticmethod
    def PlotParticles(**kwargs):
        """Plot the particle distribution in a given 2D phase space

        Args:
            kwargs["x"] (str) : 
            kwargs["y"] (str) :
            kwargs["max"] (number): maximum particles to plot
    
        Returns:
            None

        Examples:
            >>> simplex.PreProcess.PlotParticles(x="s (m)",y="Energy (GeV)",max=10000)
            # plot E-t phase space distribution with maximum number of 10000
        """
        ui_main.PreProcess("partplot", ["particle", kwargs])

    @staticmethod
    def Plot(item):
        """Calculate and plot the target item.

        Args:
            item (str): name of the target item
    
        Returns:
            None

        Examples:
            >>> simplex.PreProcess.Plot("2nd Integral")
            # calculate and plot the 2nd field integral (electron orbit)
        """
        ui_main.PreProcess("select", item)

    @staticmethod
    def Export(dataname):
        """Export the pre-processed (and currently plotted) result as an ASCII file.

        Args:
            dataname (str): file name to export the data
    
        Returns:
            None

        Examples:
            >>> simplex.PreProcess.Export("./export.txt")
            # export the data to an ASCI file "export.txt"
        """
        ui_main.PreProcess("click", "ascii", dataname)

    @staticmethod
    def PlotScale(**kwargs):
        """Change the axis scale of the 1D plot.

        Args:
            kwargs["x"] or kwargs["xscale"]: select the scale of abscissa, "linear" or "log"
            kwargs["y"] or kwargs["yscale"]: select the scale of ordinate, "linear" or "log"
    
        Returns:
            None

        Examples:
            >>> simplex.PreProcess.PlotScale(x="log",y="log")
            # Switch to the log-log plot
        """
        ui_main.PlotScale(False, **kwargs)

    @staticmethod
    def PlotRange(**kwargs):
        """Specify the plotting range of the 1D or contour plot.

        Args:
            kwargs["x"] or kwargs["xrange"] (list): specify the x range
            kwargs["y"] or kwargs["yrange"] (list): specify the y range
    
        Returns:
            None

        Examples:
            >>> simplex.PreProcess.PlotRange(x=[1,10],y=[-1,1])
            # Specify the x range as [1, 10] and y range as [-1, 1] 
        """
        ui_main.PlotRange(False, **kwargs)

    @staticmethod
    def LinePlot(width, size):
        """Switch to the line plot.

        Args:
            width: width of lines (should be > 0)
            size: size of symbols (if 0, simple line plot)
    
        Returns:
            None
        """
        width = max(1, width)
        if size == 0:
            ui_main.Plot1DType(False, width=width, type=0)
        else:
            ui_main.Plot1DType(False, width=width, size=size, type=1)

    @staticmethod
    def SymbolPlot(size):
        """Switch to the symbol plot.

        Args:
            size: size of symbols (should be > 0)
    
        Returns:
            None
        """
        size = max(1, size)
        ui_main.Plot1DType(False, size=size, type=2)

    @staticmethod
    def ContourPlot():
        """Switch to the contour plot.

        Args:
            None
    
        Returns:
            None
        """
        ui_main.Plot2DType(False, 0, False)

    @staticmethod
    def SurfacePlot(**kwargs):
        """Switch to the surface plot.

        Args:
            kwargs["type"]: select the type of the surface plot; "shade" for a shaded surface plot, "color" for a surface plot with a color map
            kwargs["wireframe"]: if True, wireframe is drawn on the surface
    
        Returns:
            None

        Examples:
            >>> simplex.PreProcess.SurfacePlot(type=shade, wireframe=True)
            # Switch to the surface plot with "shading" and "wireframe"
            
        """
        stype = 1
        wireframe = True
        if "type" in kwargs:
            stype = 2 if kwargs["type"] == "shade" else 1
        if "wireframe" in kwargs:
            wireframe = kwargs["wireframe"]
        ui_main.Plot2DType(False, stype, wireframe)

    @staticmethod
    def SetUnit(item, unit):
        """Select the unit of the data to be imported.

        Args:
            item (str): name of the target item
            unit (str): "unit" of the target item
    
        Returns:
            None

        Examples:
            >>> simplex.PreProcess.SetUnit("zpos", "mm")
            # The longitudinal position is given in mm in the data file to be imported.

        Note:
            Refer to the `keyword list <parameters.html#unit-for-data-import>`__ for the name of the target parameter.
        """
        ui_main.SetSettings("unit", item, unit)

    @staticmethod
    def DuplicatePlot(*titles):
        """Open a new window to duplicate the current plot with the same configuration.

        Args:
            titles (variable length list): titles of the plot
    
        Returns:
            None
        """
        ui_main.DuplicatePlot(True, *titles)

    @staticmethod
    def OptimizeLattice(betaxy):
        """Optimize the Twiss parameters and focusing magnets for betatron matching.

        Args:
            betaxy (list): average betatron functions in horizontal and vertical directions
    
        Returns:
            None

        Examples:
            >>> simplex.PreProcess.OptimizeLattice([10, 10])
            # try optimization with the average betatron functions of 10 m in both directions.
        """
        ui_main.PreProcess("select", "Optimization")
        ui_main.Set("preproc", "avbetaxy", betaxy)
        ui_main.PreProcess("click", "optimize")

class PostProcess:
    """
    PostProcess class bundles various functions for the operation of post-processor.
    """

    @staticmethod
    def Import(filename):
        """Import the output data for post-processing (visualization).

        Args:
            filename (str): name of the output data file
    
        Returns:
            None
        """
        ui_main.Show("postproc")
        ui_main.LoadOutput(filename)
    
    @staticmethod
    def SelectData(dataname):
        """Select the data name for post-processing from those already imported.

        Args:
            dataname (str): name of the output data to be selected
    
        Returns:
            None
        """
        ui_main.PostProcess("select", ["dataname", dataname])
    
    @staticmethod
    def Clear():
        """Clear all the output data that have been imported.

        Args:
            None
    
        Returns:
            None
        """
        ui_main.PostProcess("click", "clear")

    @staticmethod
    def Remove(dataname):
        """Remove the output data from the list.

        Args:
            dataname (str): name of the output data to be removed
    
        Returns:
            None
        """
        if not ui_main.PostProcess("select", ["dataname", dataname]):
            return
        ui_main.PostProcess("click", "remove")

    @staticmethod
    def Export(dataname):
        """Export the current plot as an ASCII file.

        Args:
            dataname (str): file name to export the data
    
        Returns:
            None
        """
        ui_main.PostProcess("click", "ascii", dataname)

    @staticmethod
    def Save(dataname):
        """Save the current plot as an JSON file, which can be imported later to reproduce the plot.

        Args:
            dataname (str): file name to save the data
    
        Returns:
            None
        """
        ui_main.PostProcess("click", "save", dataname)

    @staticmethod
    def ComparativePlot(*datanames):
        """Create a comparative plot of an item currently selected; more than one data set is retrieved from the specified output data and plotted in the same graph

        Args:
            datanames (variable length list): names of the output data to be plotted
    
        Returns:
            None

        Examples:
            >>> simplex.PostProcess.PlotGainCurve("Pulse Energy") # specify "Pulse Energy" as the target item before creating a comparative plot
            >>> simplex.PostProcess.ComparativePlot("sample-1", "sample-2")
            # plot the simplex of flux density retrieved from two output data "sample-1" and "sample-2"
        """
        ui_main.PostProcess("enable", "comparative")
        ui_main.PostProcess("select", ["comparative", *datanames])

    @staticmethod
    def MultiPlot(*datanames):
        """Create a multiple plot; more than one data set is retrieved from the specified output data and plotted in the same window

        Args:
            datanames (variable length list): names of the output data to be plotted
    
        Returns:
            None

        Examples:
            >>> simplex.PostProcess.PlotGainCurve("Pulse Energy") # specify "Pulse Energy" as the target item before creating a comparative plot
            >>> simplex.PostProcess.ComparativePlot("sample-1", "sample-2")
            # plot the simplex of flux density retrieved from two output data "sample-1" and "sample-2"
        """
        ui_main.PostProcess("enable", "multiplot")
        ui_main.PostProcess("select", ["multiplot", *datanames])

    @staticmethod
    def SetSlide(*slideno):
        """Set the slide number in the animation plot

        Args:
            slideno (variable length list): slide number(s) to show
    
        Returns:
            None

        Examples:
            >>> simplex.PostProcess.SetSlide(0) # show the 0th slide
        """
        if len(slideno) == 0:
            slideno = (0, 0)
        elif len(slideno) == 1:
            slideno = (slideno[0], 0)
        ui_main.PostProcess("slide", *slideno)

    @staticmethod
    def ComparativePlotCols(columns):
        """Define the number of columns for comparative plot with more than one plot area. This is effective for 2D plots or 1D plots with more than one target items.

        Args:
            columns (integer): column number of comparative plot areas
    
        Returns:
            None

        """
        if not isinstance(columns, int):
            print("Number of columns should be an integer")
            return
        ui_main.PostProcess("subcols", ["sub", str(columns)])

    @staticmethod
    def MultiPlotCols(columns):
        """Define the number of columns for multiplot.

        Args:
            columns (integer): column number of multiplot windows
    
        Returns:
            None

        """
        if not isinstance(columns, int):
            print("Number of columns should be an integer")
            return
        ui_main.PostProcess("subcols", ["win", str(columns)])

    @staticmethod
    @copy_docstring_from(PreProcess.PlotScale)
    def PlotScale(**kwargs):
        ui_main.PlotScale(True, **kwargs)

    def NormalizePlot(normalize):
        """Specify if the plot is normalized for each slide.

        Args:
            normalize (bool): boolean to specify the method of normalization
    
        Returns:
            None

        """
        ui_main.NormalizePlot(True, normalize)

    @staticmethod
    @copy_docstring_from(PreProcess.PlotRange)
    def PlotRange(**kwargs):
        ui_main.PlotRange(True, **kwargs)

    @staticmethod
    @copy_docstring_from(PreProcess.LinePlot)
    def LinePlot(width, size):
        width = max(1, width)
        if size == 0:
            ui_main.Plot1DType(True, width=width, type=0)
        else:
            ui_main.Plot1DType(True, width=width, size=size, type=1)

    @staticmethod
    @copy_docstring_from(PreProcess.SymbolPlot)
    def SymbolPlot(size):
        size = max(1, size)
        ui_main.Plot1DType(True, size=size, type=2)

    @staticmethod
    @copy_docstring_from(PreProcess.ContourPlot)
    def ContourPlot():
        ui_main.Plot2DType(True, 0, False)

    @staticmethod
    @copy_docstring_from(PreProcess.SurfacePlot)
    def SurfacePlot(**kwargs):
        stype = 1
        wireframe = True
        if "type" in kwargs:
            stype = 2 if kwargs["type"] == "shade" else 1
        if "wireframe" in kwargs:
            wireframe = kwargs["wireframe"]
        ui_main.Plot2DType(True, stype, wireframe)

    @staticmethod
    @copy_docstring_from(PreProcess.DuplicatePlot)
    def DuplicatePlot(*titles):
        ui_main.DuplicatePlot(False, *titles)

    @staticmethod
    def StartAnimation():
        """Start an animation with the current plot (if available).

        Args:
            None
    
        Returns:
            None

        """
        ui_main.PostProcess("startanim", None)

    @staticmethod
    def PlotGainCurve(item):
        """Plot an item in "Gain Curve" data.

        Args:
            item (str): name of the target item
    
        Returns:
            None

        Examples:
            >>> simplex.PostProcess.PlotGainCurve("Pulse Energy")
            # plot "pulse energy vs. undulator length"
        """
        ui_main.PostProcess("select", ["datatype", ui_main.MenuLabels("gcurve")])
        ui_main.PostProcess("select", ["item", item])

    @staticmethod
    def PlotCharacteristics(item):
        """Plot an item in "Characteristics" data.

        Args:
            item (str): name of the target item
    
        Returns:
            None

        Examples:
            >>> simplex.PostProcess.PlotCharacteristics("Pulse Length")
            # plot "pulse length vs. undulator length"
        """
        ui_main.PostProcess("select", ["datatype", ui_main.MenuLabels("radchar")])
        ui_main.PostProcess("select", ["item", item])

    @staticmethod
    def PlotKTrend():
        """Plot the K value variation along the undulator line.

        Args:
            None
    
        Returns:
            None
        """
        ui_main.PostProcess("select", ["datatype", ui_main.MenuLabels("ktrend")])

    @staticmethod
    def TemporalProfile():
        """Plot temporal profile of radiation

        Args:
            None
    
        Returns:
            None
        """
        ui_main.PostProcess("select", ["datatype", ui_main.MenuLabels("timeprof")])

    @staticmethod
    def SpectralProfile():
        """Plot spectrum of radiation

        Args:
            None
    
        Returns:
            None
        """
        ui_main.PostProcess("select", ["datatype", ui_main.MenuLabels("specprof")])

    @staticmethod
    def SpatialProfile():
        """Plot spatial profile of radiation

        Args:
            None
    
        Returns:
            None
        """
        ui_main.PostProcess("select", ["datatype", ui_main.MenuLabels("spatprof")])

    @staticmethod
    def AngularProfile():
        """Plot angular profile of radiation

        Args:
            None
    
        Returns:
            None
        """
        ui_main.PostProcess("select", ["datatype", ui_main.MenuLabels("angprof")])

    @staticmethod
    def SetDataProcessing(label, value):
        """Set a parameter or an option for "Raw Data Processing"

        Args:
            label (string): name of the target parameter
            value (any): value to be set

        Returns:
            None

        Examples:
            >>> simplex.PostProcess.SetDataProcessing("item", "Radiation Power") 
            # specify "Radiation Power" as a target item for data processing

        Note:
            Refer to the `keyword list <parameters.html#parameters-for-processing-the-raw-data>`__ for the name of the target parameter.
        """
        ui_main.PostProcess("click", "postp-rproc-btn")
        ui_main.PostProcess("set", [label, value])
        ui_main.PostProcess("click", "postp-view-btn")

    @staticmethod
    def RunDataProcessing():
        """Run Raw Data Processing

        Args:
            None
    
        Returns:
            None
        """
        ui_main.PostProcess("click", "postp-rproc-btn")
        ui_main.PostProcess("click", "runpostp")
        ui_main.Command("run", "runpostp")
        ui_main.PostProcess("click", "postp-view-btn")

if __name__ == "__main__":
    HTML_SRC_DIR = abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
    bin_dir =  abspath(os.path.join(os.path.dirname(__file__), "..", "..", "bin"))
    SOLVER_NOMPI_PATH = os.path.join(bin_dir, "simplex_solver_nompi")
    SOLVER_PATH = os.path.join(bin_dir, "simplex_solver")

    Start(mode="g", src="l") 
#    Open("sample_sase.json")
#    StartSimulation(folder="./output", prefix="sample1", serial=-1)
#    PostProcess.PlotGainCurve("Pulse Energy")
