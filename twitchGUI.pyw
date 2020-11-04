__author__ = 'Pascal'
import Tkinter as Tk
import Queue
import io, urllib2
from PIL import ImageTk, Image
import getTwitchLogic
import VerticalScrolledFrame
import tkMessageBox
import thread


streamImgList = []
streamOffset = 0
dict_streams = {}
limit = 50
tkQueue = Queue.Queue()
rootWindow = Tk.Tk()

def getJPGLink(url):
    image_bytes = urllib2.urlopen(url).read()
    data_stream = io.BytesIO(image_bytes)
    img = ImageTk.PhotoImage(Image.open(data_stream))
    return img

def drawStreamInfo(rootWindow, hitTopBttn=0):
    global streamOffset
    global streamImgList
    global scrollFrame

    if hitTopBttn == 1:
        streamOffset = 0
        streamImgList = []
        scrollFrame.destroy()
        scrollFrame = VerticalScrolledFrame.VerticalScrolledFrame(rootWindow)
        scrollFrame.pack()

    moreStreamsBttn = Tk.Button(scrollFrame.interior, text="More...", command=lambda: getMoreStreams(rootWindow, moreStreamsBttn))

    for i in xrange(streamOffset, len(dict_streams['streams'])):
        try:
            streamImgList.append(getJPGLink(dict_streams['streams'][i]['preview']['medium']))
        except urllib2.URLError:
            tkMessageBox.showerror("URLError", "Couldn't load preview images!")
            break

    for i in xrange(streamOffset, len(dict_streams['streams'])):
        try:
            Tk.Label(scrollFrame.interior, image=streamImgList[streamOffset]).pack()
        except IndexError:
            Tk.Label(scrollFrame.interior, text="ERROR").pack()
        Tk.Button(scrollFrame.interior, text=dict_streams['streams'][i]['channel']['name'], width="25", command=lambda streamID=streamOffset: thread.start_new_thread(getTwitchLogic.requestStream, (dict_streams, tkQueue, streamID))).pack()
        Tk.Button(scrollFrame.interior, text="Chat", width="25", command=lambda streamID=streamOffset: getTwitchLogic.requestChat(dict_streams, streamID)).pack()
        Tk.Label(scrollFrame.interior, text="Viewers: " + str(dict_streams['streams'][i]['viewers'])).pack()
        Tk.Label(scrollFrame.interior, text=dict_streams['streams'][i]['game']).pack()
        streamOffset += 1
    moreStreamsBttn.pack()

def drawNameRequestStreamInfo(rootWindow):
    global streamOffset
    global streamImgList
    global scrollFrame
    streamOffset = 0
    streamImgList = []
    scrollFrame.destroy()
    scrollFrame = VerticalScrolledFrame.VerticalScrolledFrame(rootWindow)
    scrollFrame.pack()
    for i in xrange(streamOffset, len(dict_streams['streams'])):
        try:
            streamImgList.append(getJPGLink(dict_streams['streams'][i]['preview']['medium']))
        except urllib2.URLError:
            tkMessageBox.showerror("URLError", "Couldn't load preview images!")
            break

    for i in xrange(streamOffset, len(dict_streams['streams'])):
        try:
            Tk.Label(scrollFrame.interior, image=streamImgList[streamOffset]).pack()
        except IndexError:
            Tk.Label(scrollFrame.interior, text="ERROR").pack()
        Tk.Button(scrollFrame.interior, text=dict_streams['streams'][i]['channel']['name'], width="25", command=lambda streamID=streamOffset: thread.start_new_thread(getTwitchLogic.requestStream, (dict_streams, tkQueue, streamID))).pack()
        Tk.Button(scrollFrame.interior, text="Chat", width="25", command=lambda streamID=streamOffset: getTwitchLogic.requestChat(dict_streams, streamID)).pack()
        Tk.Label(scrollFrame.interior, text="Viewers: " + str(dict_streams['streams'][i]['viewers'])).pack()
        Tk.Label(scrollFrame.interior, text=dict_streams['streams'][i]['game']).pack()
        streamOffset += 1

def getMoreStreams(rootWindow, moreStreamsBttn):
    global dict_streams
    moreStreamsBttn.destroy()
    add_streams = getTwitchLogic.getTwitchJSON(limit=limit, offset=streamOffset)
    for stream in add_streams['streams']:
        dict_streams['streams'].append(stream)
    drawStreamInfo(rootWindow)

def drawNoStreamFoundError(rootWindow):
    global streamOffset
    global streamImgList
    global scrollFrame
    streamOffset = 0
    streamImgList = []
    scrollFrame.destroy()
    scrollFrame = VerticalScrolledFrame.VerticalScrolledFrame(rootWindow)
    scrollFrame.pack()
    Tk.Label(scrollFrame.interior, text="Sorry, We couldn't find any Streams for your query! :( ").pack()

def getStreamsByName(entryField, rootWindow):
    global dict_streams
    streamName = entryField.get()
    if len(streamName) != 0:
        dict_streams.clear()
        dict_streams = getTwitchLogic.requestStreamByName(streamName)
        if dict_streams['_total'] != 0:
            drawNameRequestStreamInfo(rootWindow)
        else:
            drawNoStreamFoundError(rootWindow)

#is called when the top Button gets hit, gives back the normal top streams list after a search query
def drawLaterTop(rootWindow):
    global dict_streams
    streamOffset=0
    dict_streams = getTwitchLogic.getTwitchJSON(limit=limit, offset=streamOffset)
    if dict_streams['_total'] != 0:
        drawStreamInfo(rootWindow, hitTopBttn=1)
    else:
        drawNoStreamFoundError(rootWindow)

def enterEvent(entryField, rootWindow):
    getStreamsByName(entryField, rootWindow)

def queueHandler(name, top):
    tkQueue.put_nowait(name)
    top.grab_release()
    top.destroy()

def quitOnQualityChooseWindow(top):
    tkQueue.put_nowait("QuitOnWindow")
    top.grab_release()
    top.destroy()


def processQueue():
    try:
        tkItem = tkQueue.get_nowait()
        tkQueue.task_done()
        if "ChooseOption" in tkItem:
            topQualityQuestion = Tk.Toplevel(rootWindow)
            topQualityQuestion.grab_set()
            topQualityQuestion.protocol('WM_DELETE_WINDOW' ,lambda top=topQualityQuestion: quitOnQualityChooseWindow(top))

            topMsg = Tk.Message(topQualityQuestion, text="Choose a quality option!")
            topMsg.pack()

            while tkQueue.empty() == False:
                tkItem = tkQueue.get_nowait()
                Tk.Button(topQualityQuestion, text=str(tkItem), width=20, command=lambda name=str(tkItem), top = topQualityQuestion: queueHandler(name, top)).pack()
                tkQueue.task_done()
            rootWindow.after(100, processQueue())
    except Queue.Empty:
        rootWindow.after(100, processQueue)

def gui():
    global dict_streams
    global scrollFrame

    rootWindow.title("Sweet Cat")

    dict_streams = getTwitchLogic.getTwitchJSON(limit=limit, offset=streamOffset)

    entryField = Tk.Entry(rootWindow)
    entryField.pack()


    scrollFrame = VerticalScrolledFrame.VerticalScrolledFrame(rootWindow)


    searchButton = Tk.Button(rootWindow, text="Search", width="10", command=lambda entryFieldDummy=entryField: getStreamsByName(entryFieldDummy, rootWindow))
    searchButton.pack()

    topStreamsBttn = Tk.Button(rootWindow, text="TOP", width="10", command=lambda rootWindow=rootWindow: drawLaterTop(rootWindow))
    topStreamsBttn.pack()

    scrollFrame.pack()

    if dict_streams['_total'] != 0:
        drawStreamInfo(rootWindow)
    else:
        drawNoStreamFoundError(rootWindow)

    rootWindow.bind('<Return>', lambda event: enterEvent(entryField, rootWindow))
    rootWindow.after(100, processQueue)
    rootWindow.mainloop()



gui()