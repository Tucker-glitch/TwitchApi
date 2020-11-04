import urllib2, json, os, subprocess, webbrowser, tkMessageBox
import numpy as np
__author__ = 'Pascal'
from Queue import Queue

def getTwitchJSON(limit="", game="", offset=""):
    try:
        urlApi = "https://api.twitch.tv/kraken/streams" + "?" + "limit=" + str(limit) + "&game=" + game + "&offset=" + str(offset) + "&client_id=b2ggkkveabiywjrhcqgj04wffilt53p"
        req = urllib2.Request(url=urlApi)
        json_streams = urllib2.urlopen(req)
        string_streams = json_streams.read()
        dict_streams = json.loads(string_streams)
        return dict_streams
    except urllib2.HTTPError as connectError:
        dict_streams = {"_total": 0}
        print(connectError)
        tkMessageBox.showerror("HTTP Error", "Couldn't connect to Twitch API. This may be due to problems with your Internet connection or the Twitch API being overloaded")
        return dict_streams

def requestStream(dict_streams, tkQueue, streamID=0):
    batFile = open(os.path.join("c:", "\users" , "Pascal", "desktop", "stream.bat") , "w")
    selectedStream = dict_streams['streams'][streamID]['channel']['name']
    batFile.write("livestreamer twitch.tv/" + selectedStream)
    batFile.close()
    try:
        qualityOptionsProcess = subprocess.Popen(os.path.join("c:", "\users" , "Pascal", "desktop", "stream.bat"),stdin=None, stdout=subprocess.PIPE, stderr=None, shell=True)
        subprocessStdOut = qualityOptionsProcess.communicate()[0]
        subprocessStdOut = subprocessStdOut.replace(" (worst)", "")
        subprocessStdOut = subprocessStdOut.replace(" (best)", "")
        tkQueue.put_nowait("ChooseOption")
        streamQualityOptions = subprocessStdOut.split("Available streams:", 1)[1]
        streamQualityOptions = streamQualityOptions.replace("\n", "")
        streamQualityArray = streamQualityOptions.split(',')
        for i in streamQualityArray:
            tkQueue.put_nowait(i)
        tkQueue.join()
        tkItem = tkQueue.get(True)
        if tkItem != "QuitOnWindow":
            batFile = open(os.path.join("c:", "\users" , "Pascal", "desktop", "stream.bat") , "w")
            selectedStream = dict_streams['streams'][streamID]['channel']['name']
            batFile.write("livestreamer twitch.tv/" + selectedStream + tkItem)
            batFile.close()
            subprocess.Popen(os.path.join("c:", "\users" , "Pascal", "desktop", "stream.bat"),stdin=None, stdout=None, stderr=None, shell=True)
        else:
            print("OH MAN!")
        tkQueue.task_done()
    except subprocess.CalledProcessError as twitchError:
        print(twitchError.output)


def requestChat(dict_streams, streamID=0):
    selectedStream = dict_streams['streams'][streamID]['channel']['name']
    webbrowser.open_new("https://www.twitch.tv/" + selectedStream + "/chat?popout=")

def requestStreamByName(name):
    if str(name).isspace() == False:
        name = str(name).replace(" ", "+")
        urlApi = "https://api.twitch.tv/kraken/search/streams?q=" + str(name) + "&client_id=b2ggkkveabiywjrhcqgj04wffilt53p"
        req = urllib2.Request(url=urlApi)
        json_streams = urllib2.urlopen(req)
        string_streams = json_streams.read()
        dict_streams = json.loads(string_streams)
        if str(dict_streams['streams']) == '[]':
            dict_streams = {"_total": 0}
    else:
        dict_streams = {"_total": 0}
    return dict_streams





