# cmu_112_graphics.py
# version 0.8.7

# Pre-release for CMU 15-112-s20

# Require Python 3.6 or later
import traceback
import copy
import os
import inspect
from io import BytesIO
from tkinter import (
    messagebox, simpledialog, filedialog,
    Canvas, Event, Tk, BOTH, YES, ALL
)
from types import SimpleNamespace
# from tkinter import *
import sys
if ((sys.version_info[0] != 3) or (sys.version_info[1] < 6)):
    raise Exception(
        'cmu_112_graphics.py requires Python version 3.6 or later.')
# NOTE: increase this number to be able to mousedrag for longer!
sys.setrecursionlimit(10000)
# Track version and file update timestamp
import datetime
MAJOR_VERSION = 0
MINOR_VERSION = 9.3
LAST_UPDATED = datetime.date(year=2020, month=7, day=27)

# Pending changes:
#   * Fix Windows-only bug: Position popup dialog box over app window (already works fine on Macs)
#   * Add documentation
#   * integrate sounds (probably from pyGame)
#   * Improved methodIsOverridden to TopLevelApp and ModalApp
#   * Save to animated gif and/or mp4 (with audio capture?)

# Deferred changes:
#   * replace/augment tkinter canvas with PIL/Pillow imageDraw (perhaps with our own fn names)
#   * use snake_case and CapWords

# Chages in v0.8.6
#   * s20

# Chages in v0.8.5
#   * Support loadImage from Modes

# Chages in v0.8.3 + v0.8.4
#   * Use default empty Mode if none is provided
#   * Add KeyRelease event binding
#   * Drop user32.SetProcessDPIAware (caused window to be really tiny on some Windows machines)

# Changes in v0.8.1 + v0.8.2
#   * print version number and last-updated date on load
#   * restrict modifiers to just control key (was confusing with NumLock, etc)
#   * replace hasModifiers with 'control-' prefix, as in 'control-A'
#   * replace app._paused with app.paused, etc (use app._ for private variables)
#   * use improved ImageGrabber import for linux

# Changes in v0.8.0
#   * suppress more modifier keys (Super_L, Super_R, ...)
#   * raise exception on event.keysym or event.char + works with key = 'Enter'
#   * remove tryToInstall

# Changes in v0.7.4
#   * renamed drawAll back to redrawAll :-)

# Changes in v0.7.3
#   * Ignore mousepress-drag-release and defer configure events for drags in titlebar
#   * Extend deferredRedrawAll to 100ms with replace=True and do not draw while deferred
#     (together these hopefully fix Windows-only bug: file dialog makes window not moveable)
#   * changed sizeChanged to not take event (use app.width and app.height)

# Changes in v0.7.2
#   * Singleton App._theRoot instance (hopefully fixes all those pesky Tkinter errors-on-exit)
#   * Use user32.SetProcessDPIAware to get resolution of screen grabs right on Windows-only (fine on Macs)
#   * Replaces showGraphics() with runApp(...), which is a veneer for App(...) [more intuitive for pre-OOP part of course]
#   * Fixes/updates images:
#       * disallows loading images in redrawAll (raises exception)
#       * eliminates cache from loadImage
#       * eliminates app.getTkinterImage, so user now directly calls ImageTk.PhotoImage(image))
#       * also create_image allows magic pilImage=image instead of image=ImageTk.PhotoImage(app.image)

# Changes in v0.7.1
#   * Added keyboard shortcut:
#       * cmd/ctrl/alt-x: hard exit (uses os._exit() to exit shell without tkinter error messages)
#   * Fixed bug: shortcut keys stopped working after an MVC violation (or other exception)
#   * In app.saveSnapshot(), add .png to path if missing
#   * Added: Print scripts to copy-paste into shell to install missing modules (more automated approaches proved too brittle)

# Changes in v0.7
#   * Added some image handling (requires PIL (retained) and pyscreenshot (later removed):
#       * app.loadImage()       # loads PIL/Pillow image from file, with file dialog, or from URL (http or https)
#       * app.scaleImage()      # scales a PIL/Pillow image
#       * app.getTkinterImage() # converts PIL/Pillow image to Tkinter PhotoImage for use in create_image(...)
#       * app.getSnapshot()     # get a snapshot of the canvas as a PIL/Pillow image
#       * app.saveSnapshot()    # get and save a snapshot
#   * Added app._paused, app.togglePaused(), and paused highlighting (red outline around canvas when paused)
#   * Added keyboard shortcuts:
#       * cmd/ctrl/alt-s: save a snapshot
#       * cmd/ctrl/alt-p: pause/unpause
#       * cmd/ctrl/alt-q: quit

# Changes in v0.6:
#   * Added fnPrefix option to TopLevelApp (so multiple TopLevelApp's can be in one file)
#   * Added showGraphics(drawFn) (for graphics-only drawings before we introduce animations)

# Changes in v0.5:
#   * Added:
#       * app.winx and app.winy (and add winx,winy parameters to app.__init__, and sets these on configure events)
#       * app.setSize(width, height)
#       * app.setPosition(x, y)
#       * app.quit()
#       * app.showMessage(message)
#       * app.getUserInput(prompt)
#       * App.lastUpdated (instance of datetime.date)
#   * Show popup dialog box on all exceptions (not just for MVC violations)
#   * Draw (in canvas) "Exception!  App Stopped! (See console for details)" for any exception
#   * Replace callUserMethod() with more-general @_safeMethod decorator (also handles exceptions outside user methods)
#   * Only include lines from user's code (and not our framework nor tkinter) in stack traces
#   * Require Python version (3.6 or greater)

# Changes in v0.4:
#   * Added __setattr__ to enforce Type 1A MVC Violations (setting app.x in redrawAll) with better stack trace
#   * Added app._deferredRedrawAll() (avoids resizing drawing/crashing bug on some platforms)
#   * Added deferredMethodCall() and app._afterIdMap to generalize afterId handling
#   * Use (_ is None) instead of (_ == None)

# Changes in v0.3:
#   * Fixed "event not defined" bug in sizeChanged handlers.
#   * draw "MVC Violation" on Type 2 violation (calling draw methods outside redrawAll)

# Changes in v0.2:
#   * Handles another MVC violation (now detects drawing on canvas outside of redrawAll)
#   * App stops running when an exception occurs (in user code) (stops cascading errors)

# Changes in v0.1:
#   * OOPy + supports inheritance + supports multiple apps in one file + etc
#        * uses import instead of copy-paste-edit starter code + no "do not edit code below here!"
#        * no longer uses Struct (which was non-Pythonic and a confusing way to sort-of use OOP)
#   * Includes an early version of MVC violation handling (detects model changes in redrawAll)
#   * added events:
#       * appStarted (no init-vs-__init__ confusion)
#       * appStopped (for cleanup)
#       * keyReleased (well, sort of works) + mouseReleased
#       * mouseMoved + mouseDragged
#       * sizeChanged (when resizing window)
#   * improved key names (just use event.key instead of event.char and/or event.keysym + use names for 'Enter', 'Escape', ...)
#   * improved function names (renamed redrawAll to drawAll)
#   * improved (if not perfect) exiting without that irksome Tkinter error/bug
#   * app has a title in the titlebar (also shows window's dimensions)
#   * supports Modes and ModalApp (see ModalApp and Mode, and also see TestModalApp example)
#   * supports TopLevelApp (using top-level functions instead of subclasses and methods)
#   * supports version checking with App.majorVersion, App.minorVersion, and App.version
#   * logs drawing calls to support autograding views (still must write that autograder, but this is a very helpful first step)


def failedImport(importName, installName=None):
    installName = installName or importName
    print('**********************************************************')
    print(f"** Cannot import {importName} -- it seems you need to install {installName}")
    print("** This may result in limited functionality or even a runtime error.")
    print('**********************************************************')
    print()


try:
    from PIL import Image, ImageTk
except ModuleNotFoundError:
    failedImport('PIL', 'pillow')

if sys.platform.startswith('linux'):
    try:
        import pyscreenshot as ImageGrabber
    except ModuleNotFoundError:
        failedImport('pyscreenshot')
else:
    try:
        from PIL import ImageGrab as ImageGrabber
    except ModuleNotFoundError:
        pass  # Our PIL warning is already printed above

try:
    import requests
except ModuleNotFoundError:
    failedImport('requests')


def getHash(obj):
    # This is used to detect MVC violations in redrawAll
    # @TODO: Make this more robust and efficient
    try:
        return getHash(obj.__dict__)
    except BaseException:
        if (isinstance(obj, list)):
            return getHash(tuple([getHash(v) for v in obj]))
        elif (isinstance(obj, set)):
            return getHash(sorted(obj))
        elif (isinstance(obj, dict)):
            return getHash(tuple([obj[key] for key in sorted(obj)]))
        else:
            try:
                return hash(obj)
            except BaseException:
                return getHash(repr(obj))


def isSubset(a, b):
    for k, v in a.items():
        if k not in b or b[k] != v:
            return False
    return True


class WrappedCanvas(Canvas):
    customKwargs = ['onClick', 'tag']

    def __init__(self, app, isTest=False):
        # Logs draw calls (for autograder) in canvas.loggedDrawingCalls
        self.loggedDrawingCalls = []
        self.logDrawingCalls = True
        self.inRedrawAll = False
        self.app = app
        self.minHandleID = 0
        self.isTest = isTest
        if not isTest:
            super().__init__(app._root, width=app.width, height=app.height)

    def log(self, methodName, args, kwargs):
        if not self.inRedrawAll:
            self.app._mvcViolation(
                'you may not use the canvas (the view) outside of redrawAll')
        if self.logDrawingCalls:
            newArgs = []
            for arg in args:
                if isinstance(arg, tuple):
                    for elem in arg:
                        newArgs.append(elem)
                else:
                    newArgs.append(arg)
            self.loggedDrawingCalls.append((methodName, newArgs, kwargs))

    def objectExists(self, methodName, position, kwargs):
        # top elements will be last, so we go reversed
        for elem in reversed(self.loggedDrawingCalls):
            elemMethodName, elemArgs, elemKwargs = elem
            if ((methodName == elemMethodName) and
               (position == elemArgs) and
               isSubset(kwargs, elemKwargs)):
                return True
        return False

    def findAndTriggerOverlappingElements(self, x, y):
        ids = self.find_overlapping(x-1, y-1, x+1, y+1)
        # first element is always the last rendered element
        # even if it doesnt collide
        ids = ids[1:]
        # go through in reverse order (the top element)
        for eid in reversed(ids):
            i = eid - self.minHandleID - 1
            name, pos, kwargs = self.loggedDrawingCalls[i]
            if 'onClick' in kwargs:
                kwargs['onClick']()
                # only click the top element
                return

    @staticmethod
    def _getCenter(pos):
        if len(pos) == 2:
            return pos
        if len(pos) == 4:
            x0, y0, x1, y1 = pos
            return (x0 + x1)//2, (y0 + y1)//2
        # is polygon
        x0, y0, x1, y1 = WrappedCanvas._getPolygonBoundingBox(pos)
        return (x0 + x1)//2, (y0+y1)//2

    @staticmethod
    def _getPolygonBoundingBox(pos):
        xs = [pos[i] for i in range(0, len(pos), 2)]
        ys = [pos[i] for i in range(1, len(pos), 2)]
        assert len(xs) == len(ys)
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)
        return x0, y0, x1, y1

    def findElementWithTag(self, tag):
        elems = []
        for name, pos, kwargs in self.loggedDrawingCalls:
            if 'tags' in kwargs and tag in kwargs['tags']:
                elems.append((name, pos, kwargs))
        if len(elems) != 1:
            raise Exception(f'Expected one element with tag {tag} but found {len(elems)} instead')
        return elems[0]

    def getCenterOfElementWithTag(self, tag):
        elem = self.findElementWithTag(tag)
        _, pos, _ = elem
        return WrappedCanvas._getCenter(pos)

    def clickElementWithTag(self, tag):
        elem = self.findElementWithTag(tag)
        _, _, kwargs = elem
        if 'onClick' not in kwargs:
            raise Exception('Element with tag {tag} does not have an onClick callback!')
        kwargs['onClick']()

    def manuallyTriggerCallbacksOnCoordinate(self, x, y):
        margin = 10
        for _, pos, kwargs in reversed(self.loggedDrawingCalls):
            if len(pos) == 4:
                x0, y0, x1, y1 = pos
            elif len(pos) == 2:
                cx, cy = WrappedCanvas._getCenter(pos)
                x0, x1 = cx - margin, cx + margin
                y0, y1 = cy - margin, cy + margin
            else:
                x0, y0, x1, y1 = WrappedCanvas._getPolygonBoundingBox(pos)
            if x0 <= x <= x1 and y0 <= y <= y1:
                if 'onClick' in kwargs:
                    kwargs['onClick']()
                    # only do one onClick
                    return

    def _callWithTestBlock(self, fnName, *args, **kwargs):
        if not self.isTest:
            for key in WrappedCanvas.customKwargs:
                if key in kwargs:
                    del kwargs[key]
            return getattr(super(), fnName)(*args, **kwargs)

    def _callWithLogAndTestBlock(self, fnName, *args, **kwargs):
        if 'tag' in kwargs and 'tags' not in kwargs and kwargs['tag']:
            kwargs['tags'] = (kwargs['tag'],)
        if 'onClick' in kwargs and not callable(kwargs['onClick']):
            raise Exception(f'onClick is expected to be a function but instead got {type(kwargs["onClick"])}')
        self.log(fnName, args, kwargs)
        return self._callWithTestBlock(fnName, *args, **kwargs)

    def create_arc(self, *args, **kwargs):
        return self._callWithLogAndTestBlock('create_arc', *args, **kwargs)

    def create_bitmap(self, *args, **kwargs):
        return self._callWithLogAndTestBlock('create_bitmap', *args, **kwargs)

    def create_line(self, *args, **kwargs):
        return self._callWithLogAndTestBlock('create_line', *args, **kwargs)

    def create_oval(self, *args, **kwargs):
        return self._callWithLogAndTestBlock('create_oval', *args, **kwargs)

    def create_polygon(self, *args, **kwargs):
        return self._callWithLogAndTestBlock('create_polygon', *args, **kwargs)

    def create_rectangle(self, *args, **kwargs):
        return self._callWithLogAndTestBlock('create_rectangle', *args, **kwargs)

    def create_text(self, *args, **kwargs):
        return self._callWithLogAndTestBlock('create_text', *args, **kwargs)

    def create_window(self, *args, **kwargs):
        return self._callWithLogAndTestBlock('create_window', *args, **kwargs)

    def create_image(self, *args, **kwargs):
        self.log('create_image', args, kwargs)
        usesImage = 'image' in kwargs
        usesPilImage = 'pilImage' in kwargs
        if ((not usesImage) and (not usesPilImage)):
            raise Exception('create_image requires an image to draw')
        elif (usesImage and usesPilImage):
            raise Exception(
                'create_image cannot use both an image and a pilImage')
        elif (usesPilImage):
            pilImage = kwargs['pilImage']
            del kwargs['pilImage']
            if (not isinstance(pilImage, Image.Image)):
                raise Exception(
                    'create_image: pilImage value is not an instance of a PIL/Pillow image')
            image = ImageTk.PhotoImage(pilImage)
        else:
            image = kwargs['image']
            if (isinstance(image, Image.Image)):
                raise Exception(
                    'create_image: image must not be an instance of a PIL/Pillow image\n' +
                    'You perhaps meant to convert from PIL to Tkinter, like so:\n' +
                    '     canvas.create_image(x, y, image=ImageTk.PhotoImage(image))')
        kwargs['image'] = image
        if not self.isTest:
            return super().create_image(*args, **kwargs)

    def delete(self, opt):
        return self._callWithTestBlock('delete', opt)

    def update(self):
        return self._callWithTestBlock('update')

    def pack(self, *args, **kwargs):
        return self._callWithTestBlock('pack', *args, **kwargs)

    def winfo_x(self):
        return self._callWithTestBlock('winfo_x')

    def winfo_y(self):
        return self._callWithTestBlock('winfo_y')


def _safeMethod(appMethod):
    def m(*args, **kwargs):
        app = args[0]
        try:
            return appMethod(*args, **kwargs)
        except Exception as e:
            app._running = False
            App._printUserTraceback(e, sys.exc_info()[2])
            if ('_canvas' in app.__dict__):
                # not really, but stops recursive MVC Violations!
                app._canvas.inRedrawAll = True
                app._canvas.create_rectangle(
                    0, 0, app.width, app.height, fill=None, width=10, outline='red')
                app._canvas.create_rectangle(
                    10,
                    app.height - 50,
                    app.width - 10,
                    app.height - 10,
                    fill='white',
                    outline='red',
                    width=4)
                app._canvas.create_text(
                    app.width / 2,
                    app.height - 40,
                    text=f'Exception! App Stopped!',
                    fill='red',
                    font='Arial 12 bold')
                app._canvas.create_text(
                    app.width / 2,
                    app.height - 20,
                    text=f'See console for details',
                    fill='red',
                    font='Arial 12 bold')
                app._canvas.update()
            app.showMessage(
                f'Exception: {e}\nClick ok then see console for details.')
    return m


def _withTestControllerArgs(fn):
    def g(*args, controllerArgs=None):
        self = args[0]
        args = args[1:]
        if controllerArgs is not None:
            self._testControllerArgs = controllerArgs
        return fn(self, *args)
    return g


def _blockIfTest(fn):
    def g(*args, **kwargs):
        self = args[0]
        args = args[1:]
        if self._isTest:
            return
        return fn(self, *args, **kwargs)
    return g


class App(object):
    majorVersion = MAJOR_VERSION
    minorVersion = MINOR_VERSION
    version = f'{majorVersion}.{minorVersion}'
    lastUpdated = LAST_UPDATED
    _theRoot = None  # singleton Tkinter root object

    ####################################
    # User Methods:
    ####################################
    def redrawAll(self, canvas): pass          # draw the model in the canvas
    def appStarted(self, *initialState): pass  # initialize the model (self.xyz)
    def appStopped(self): pass                 # cleanup after app is done running
    def keyPressed(self, event): pass          # use event.key
    def keyReleased(self, event): pass         # use event.key
    def mousePressed(self, event): pass        # use event.x and event.y
    def mouseReleased(self, event): pass       # use event.x and event.y
    def mouseMoved(self, event): pass          # use event.x and event.y
    def mouseDragged(self, event): pass        # use event.x and event.y
    def timerFired(self): pass                 # respond to timer events
    def sizeChanged(self): pass                # respond to window size changes
    def getState(self): pass                   # return state for autograding

    ####################################
    # Implementation:
    ####################################

    def __init__(
            self,
            *initialState,
            width=300,
            height=300,
            x=0,
            y=0,
            title=None,
            autorun=True,
            isTest=False,
            mvcCheck=True,
            logDrawingCalls=True):
        self.winx, self.winy, self.width, self.height = x, y, width, height
        self.timerDelay = 100      # milliseconds
        self.mouseMovedDelay = 50  # ditto
        self._title = title
        self._mvcCheck = mvcCheck
        self._logDrawingCalls = logDrawingCalls
        self._running = self._paused = False
        self._mousePressedOutsideWindow = False
        self._isTest = isTest
        self._initialState = initialState
        self._testControllerArgs = []
        if autorun and not isTest:
            self.run(*initialState)
        if isTest:
            self.initTest()

    @_safeMethod
    def initTest(self):
        self._lastWindowDims = None  # set in sizeChangedWrapper
        self._afterIdMap = dict()
        self._canvas = WrappedCanvas(self, isTest=True)
        self._running = True
        self._paused = False
        self._appStartedWrapper(*self._initialState)
        self.isTest = True

    def objectExists(self, shape, position, kwargs):
        return self._canvas.objectExists('create_' + shape, position, kwargs)

    def triggerCallbacksOnCoordinate(self, x, y):
        if self._isTest:
            return
        self._canvas.findAndTriggerOverlappingElements(x, y)

    def clickElementWithTag(self, tag):
        '''clicks element if found'''
        x, y = self.getCenterOfElementWithTag(tag)
        if 0 <= x < self.width and 0 <= y < self.height:
            self._canvas.clickElementWithTag(tag)

    def getCenterOfElementWithTag(self, tag):
        '''finds element with tag tag and returns the center point
        of its bounding box'''
        return self._canvas.getCenterOfElementWithTag(tag)

    def findElementWithTag(self, tag):
        return self._canvas.findElementWithTag(tag)

    @_withTestControllerArgs
    def simulateMousePress(self, x, y):
        event = SimpleNamespace()
        event.x, event.y = x, y
        if 0 <= x < self.width and 0 <= y < self.height:
            self._mousePressedWrapper(event)

    @_withTestControllerArgs
    def simulateMouseRelease(self, x, y):
        event = SimpleNamespace()
        event.x, event.y = x, y
        if 0 <= x < self.width and 0 <= y < self.height:
            self._mouseReleasedWrapper(event)

    @_withTestControllerArgs
    def simulateMouseMotion(self, x, y):
        event = SimpleNamespace()
        event.x, event.y = x, y
        if 0 <= x < self.width and 0 <= y < self.height:
            self._mouseMovedWrapper(event)

    @_withTestControllerArgs
    def simulateMouseDrag(self, x, y):
        event = SimpleNamespace()
        event.x, event.y = x, y
        if 0 <= x < self.width and 0 <= y < self.height:
            self._mouseDraggedWrapper(event)

    @_withTestControllerArgs
    def simulateKeyPress(self, key):
        # TODO: does it need to work for modifier keys?
        event = SimpleNamespace()
        event.keysym = event.char = key
        event.state = 42
        self._keyPressedWrapper(event)

    @_withTestControllerArgs
    def simulateKeyRelease(self, key):
        # TODO: does it need to work for modifier keys?
        event = SimpleNamespace()
        event.keysym = event.char = key
        event.state = 42
        self._keyReleasedWrapper(event)

    @_withTestControllerArgs
    def simulateTimerFire(self, duration):
        times = duration // self.timerDelay
        for _ in range(times):
            self.timerFired()
        self._redrawAllWrapper()

    @_blockIfTest
    def setSize(self, width, height):
        self._root.geometry(f'{width}x{height}')

    @_blockIfTest
    def setPosition(self, x, y):
        self._root.geometry(f'+{x}+{y}')

    @_blockIfTest
    def showMessage(self, message):
        if '_root' in self.__dict__:
            messagebox.showinfo('showMessage', message, parent=self._root)

    def getUserInput(self, prompt):
        if self._isTest:
            if len(self._testControllerArgs) > 0:
                return str(self._testControllerArgs.pop(0))
            raise Exception('expected argument for getUserInput to be provided in simulate function but none provided!')
        else:
            return simpledialog.askstring('getUserInput', prompt)

    def loadImage(self, path=None):
        if self._canvas.inRedrawAll:
            raise Exception('Cannot call loadImage in redrawAll')
        if path is None:
            if self._isTest:
                if len(self._testControllerArgs) > 0:
                    path = self._testControllerArgs.pop(0)
                raise Exception('expected argument for loadImage to be provided in simulate function but none provided!')
            else:
                path = filedialog.askopenfilename(
                    initialdir=os.getcwd(), title='Select file: ', filetypes=(
                        ('Image files', '*.png *.gif *.jpg'), ('all files', '*.*')))
                if not path:
                    return None
        if path.startswith('http'):
            response = requests.request('GET', path)  # path is a URL!
            image = Image.open(BytesIO(response.content))
        else:
            image = Image.open(path)
        return image

    def scaleImage(self, image, scale, antialias=False):
        # antialiasing is higher-quality but slower
        resample = Image.ANTIALIAS if antialias else Image.NEAREST
        return image.resize(
            (round(
                image.width *
                scale),
                round(
                image.height *
                scale)),
            resample=resample)

    @_blockIfTest
    def getSnapshot(self):
        self._showRootWindow()
        x0 = self._root.winfo_rootx() + self._canvas.winfo_x()
        y0 = self._root.winfo_rooty() + self._canvas.winfo_y()
        result = ImageGrabber.grab((x0, y0, x0 + self.width, y0 + self.height))
        return result

    @_blockIfTest
    def saveSnapshot(self):
        path = filedialog.asksaveasfilename(
            initialdir=os.getcwd(), title='Select file: ', filetypes=(
                ('png files', '*.png'), ('all files', '*.*')))
        if path:
            # defer call to let filedialog close (and not grab those pixels)
            if not path.endswith('.png'):
                path += '.png'
            self._deferredMethodCall(
                afterId='saveSnapshot',
                afterDelay=0,
                afterFn=lambda: self.getSnapshot().save(path))

    def _togglePaused(self):
        self._paused = not self._paused

    @_blockIfTest
    def quit(self):
        self._running = False
        # break out of root.mainloop() without closing window!
        self._root.quit()

    def __setattr__(self, attr, val):
        d = self.__dict__
        d[attr] = val
        canvas = d.get('_canvas', None)
        if (d.get('running', False) and
            d.get('mvcCheck', False) and
            (canvas is not None) and
                canvas.inRedrawAll):
            self._mvcViolation(
                f'you may not change app.{attr} in the model while in redrawAll (the view)')

    @staticmethod
    def _printUserTraceback(exception, tb):
        stack = traceback.extract_tb(tb)
        lines = traceback.format_list(stack)
        inRedrawAllWrapper = False
        printLines = []
        for line in lines:
            if (('"cmu_112_graphics.py"' not in line) and
                ('/cmu_112_graphics.py' not in line) and
                ('\\cmu_112_graphics.py' not in line) and
                ('/tkinter/' not in line) and
                    ('\\tkinter\\' not in line)):
                printLines.append(line)
            if ('redrawAllWrapper' in line):
                inRedrawAllWrapper = True
        if len(printLines) == 0:
            # No user code in trace, so we have to use all the code (bummer),
            # but not if we are in a redrawAllWrapper...
            if inRedrawAllWrapper:
                printLines = [
                    '    No traceback available. Error occurred in redrawAll.\n']
            else:
                printLines = lines
        print('Traceback (most recent call last):')
        for line in printLines:
            print(line, end='')
        print(f'Exception: {exception}')

    def _methodIsOverridden(self, methodName):
        return (
            getattr(
                type(self),
                methodName) is not getattr(
                App,
                methodName))

    def _mvcViolation(self, errMsg):
        self._running = False
        raise Exception('MVC Violation: ' + errMsg)

    @_safeMethod
    def _redrawAllWrapper(self):
        if not self._running:
            return
        if 'deferredRedrawAll' in self._afterIdMap:
            return  # wait for pending call
        self._canvas.inRedrawAll = True
        self._canvas.delete(ALL)
        width, outline = (10, 'red') if self._paused else (0, 'white')
        minHandleID = self._canvas.create_rectangle(
            0,
            0,
            self.width,
            self.height,
            fill='white',
            width=width,
            outline=outline)
        self._canvas.minHandleID = minHandleID or 0
        self._canvas.loggedDrawingCalls = []
        self._canvas.logDrawingCalls = self._logDrawingCalls
        hash1 = getHash(self) if self._mvcCheck else None
        try:
            self.redrawAll(self._canvas)
            hash2 = getHash(self) if self._mvcCheck else None
            if (hash1 != hash2):
                self._mvcViolation(
                    'you may not change the app state (the model) in redrawAll (the view)')
        finally:
            self._canvas.inRedrawAll = False
        self._canvas.update()

    @_blockIfTest
    def _deferredMethodCall(self, afterId, afterDelay, afterFn, replace=False):
        def afterFnWrapper():
            self._afterIdMap.pop(afterId, None)
            afterFn()
        id = self._afterIdMap.get(afterId, None)
        if (id is None) or replace:
            if id:
                self._root.after_cancel(id)
            self._afterIdMap[afterId] = self._root.after(
                afterDelay, afterFnWrapper)

    @_blockIfTest
    def _deferredRedrawAll(self):
        self._deferredMethodCall(
            afterId='deferredRedrawAll',
            afterDelay=100,
            afterFn=self._redrawAllWrapper,
            replace=True)

    @_safeMethod
    def _appStartedWrapper(self, *initialState):
        if initialState != self._initialState:
            initialState = initialState + self._initialState
        self.appStarted(*initialState)
        self._redrawAllWrapper()

    _keyNameMap = {
        '\t': 'Tab',
        '\n': 'Enter',
        '\r': 'Enter',
        '\b': 'Backspace',
        chr(127): 'Delete',
        chr(27): 'Escape',
        ' ': 'Space'
    }

    @staticmethod
    def _useEventKey(attr):
        raise Exception(f'Use event.key instead of event.{attr}')

    @staticmethod
    def _getEventKeyInfo(event, keysym, char):
        key = c = char
        hasControlKey = (event.state & 0x4 != 0)
        if (c in [None, '']) or (len(c) > 1) or (ord(c) > 255):
            key = keysym
            if (key.endswith('_L') or
                key.endswith('_R') or
                    key.endswith('_Lock')):
                key = 'Modifier_Key'
        elif c in App._keyNameMap:
            key = App._keyNameMap[c]
        elif (len(c) == 1) and (1 <= ord(c) <= 26):
            key = chr(ord('a') - 1 + ord(c))
            hasControlKey = True
        if hasControlKey and (len(key) == 1):
            # don't add control- prefix to Enter, Tab, Escape, ...
            key = 'control-' + key
        return key

    class KeyEventWrapper(Event):
        def __init__(self, event):
            keysym, char = event.keysym, event.char
            del event.keysym
            del event.char
            for key in event.__dict__:
                if (not key.startswith('__')):
                    self.__dict__[key] = event.__dict__[key]
            self.key = App._getEventKeyInfo(event, keysym, char)
        keysym = property(lambda *args: App._useEventKey('keysym'),
                          lambda *args: App._useEventKey('keysym'))
        char = property(lambda *args: App._useEventKey('char'),
                        lambda *args: App._useEventKey('char'))

    @_safeMethod
    def _keyPressedWrapper(self, event):
        event = App.KeyEventWrapper(event)
        if event.key == 'control-s':
            self.saveSnapshot()
        elif event.key == 'control-p':
            self._togglePaused()
            self._redrawAllWrapper()
        elif event.key == 'control-q':
            self.quit()
        elif event.key == 'control-x':
            os._exit(0)  # hard exit avoids tkinter error messages
        elif (self._running and
              (not self._paused) and
              self._methodIsOverridden('keyPressed') and
              (event.key != 'Modifier_Key')):
            self.keyPressed(event)
            self._redrawAllWrapper()

    @_safeMethod
    def _keyReleasedWrapper(self, event):
        if (not self._running) or self._paused or (
                not self._methodIsOverridden('keyReleased')):
            return
        event = App.KeyEventWrapper(event)
        if event.key != 'Modifier_Key':
            self.keyReleased(event)
            self._redrawAllWrapper()

    @_safeMethod
    def _mousePressedWrapper(self, event):
        if (not self._running) or self._paused:
            return
        if ((event.x < 0) or (event.x > self.width) or
                (event.y < 0) or (event.y > self.height)):
            self._mousePressedOutsideWindow = True
        else:
            self._mousePressedOutsideWindow = False
            if self._isTest:
                self._canvas.manuallyTriggerCallbacksOnCoordinate(
                    event.x,
                    event.y
                )
            else:
                self.triggerCallbacksOnCoordinate(
                    event.x,
                    event.y
                )
            if self._methodIsOverridden('mousePressed'):
                self.mousePressed(event)
                # should we call mousedragged here? otherwise it
                # doesn't get called on the initial click
            self._redrawAllWrapper()

    @_safeMethod
    def _mouseReleasedWrapper(self, event):
        if (not self._running) or self._paused:
            return
        if self._mousePressedOutsideWindow:
            self._mousePressedOutsideWindow = False
            self._sizeChangedWrapper()
        else:
            if (self._methodIsOverridden('mouseReleased')):
                self.mouseReleased(event)
                self._redrawAllWrapper()

    @_safeMethod
    def _timerFiredWrapper(self):
        if (not self._running) or (not self._methodIsOverridden('timerFired')):
            return
        if not self._paused:
            self.timerFired()
            self._redrawAllWrapper()
        self._deferredMethodCall(
            afterId='_timerFiredWrapper',
            afterDelay=self.timerDelay,
            afterFn=self._timerFiredWrapper)

    @_safeMethod
    def _sizeChangedWrapper(self, event=None):
        if not self._running:
            return
        if event and ((event.width < 2) or (event.height < 2)):
            return
        if self._mousePressedOutsideWindow:
            return
        self.width, self.height, self.winx, self.winy = [
            int(v) for v in self._root.winfo_geometry().replace(
                'x', '+').split('+')]
        if self._lastWindowDims is None:
            self._lastWindowDims = (
                self.width, self.height, self.winx, self.winy)
        else:
            newDims = (self.width, self.height, self.winx, self.winy)
            if self._lastWindowDims != newDims:
                self._lastWindowDims = newDims
                self.updateTitle()
                self.sizeChanged()
                # avoid resize crashing on some platforms
                self._deferredRedrawAll()

    @_safeMethod
    def _mouseMovedWrapper(self, event):
        if not self._running or self._paused or self._mousePressedOutsideWindow:
            return
        if self._methodIsOverridden('mouseMoved'):
            self.mouseMoved(event)
            self._redrawAllWrapper()

    @_safeMethod
    def _mouseDraggedWrapper(self, event):
        if not self._running or self._paused or self._mousePressedOutsideWindow:
            return
        if self._methodIsOverridden('mouseDragged'):
            self.mouseDragged(event)
            self._redrawAllWrapper()

    @_blockIfTest
    def updateTitle(self):
        self._title = self._title or type(self).__name__
        self._root.title(f'{self._title} ({self.width} x {self.height})')

    def getQuitMessage(self):
        appLabel = type(self).__name__
        if self._title != appLabel:
            if self._title.startswith(appLabel):
                appLabel = self._title
            else:
                appLabel += f" '{self._title}'"
        return f"*** Closing {appLabel}.  Bye! ***\n"

    @_blockIfTest
    def _showRootWindow(self):
        root = self._root
        root.update()
        root.deiconify()
        root.lift()
        root.focus()

    @_blockIfTest
    def _hideRootWindow(self):
        root = self._root
        root.withdraw()

    @_blockIfTest
    @_safeMethod
    def run(self, *initialState):
        self._mouseIsPressed = False
        self._lastWindowDims = None  # set in sizeChangedWrapper
        self._afterIdMap = dict()
        # create the singleton root window
        if (App._theRoot is None):
            App._theRoot = Tk()
            # when user enters cmd-q, ignore here (handled in keyPressed)
            App._theRoot.createcommand('exit', lambda: '')
            # when user presses 'x' in title bar
            App._theRoot.protocol(
                'WM_DELETE_WINDOW',
                lambda: App._theRoot.app.quit())
            App._theRoot.bind(
                "<Button-1>",
                lambda event: App._theRoot.app._mousePressedWrapper(event))
            App._theRoot.bind(
                "<B1-ButtonRelease>",
                lambda event: App._theRoot.app._mouseReleasedWrapper(event))
            App._theRoot.bind(
                "<KeyPress>",
                lambda event: App._theRoot.app._keyPressedWrapper(event))
            App._theRoot.bind(
                "<KeyRelease>",
                lambda event: App._theRoot.app._keyReleasedWrapper(event))
            App._theRoot.bind(
                "<Configure>",
                lambda event: App._theRoot.app._sizeChangedWrapper(event))
            App._theRoot.bind(
                '<Motion>',
                lambda event: App._theRoot.app._mouseMovedWrapper(event))
            App._theRoot.bind(
                "<B1-Motion>",
                lambda event: App._theRoot.app._mouseDraggedWrapper(event))
        else:
            App._theRoot.canvas.destroy()
        self._root = root = App._theRoot  # singleton root!
        root.app = self
        root.geometry(f'{self.width}x{self.height}+{self.winx}+{self.winy}')
        self.updateTitle()
        # create the canvas
        root.canvas = self._canvas = WrappedCanvas(self)
        self._canvas.pack(fill=BOTH, expand=YES)
        # initialize, start the timer, and launch the app
        self._running = True
        self._paused = False
        self._appStartedWrapper(*initialState)
        self._timerFiredWrapper()
        self._showRootWindow()
        root.mainloop()
        self._hideRootWindow()
        self._running = False
        for afterId in self._afterIdMap:
            self._root.after_cancel(self._afterIdMap[afterId])
        self._afterIdMap.clear()  # for safety
        self.appStopped()
        print(self.getQuitMessage())

####################################
# TopLevelApp:
# (with top-level functions not subclassses and methods)
####################################


class TopLevelApp(App):
    _apps = dict()  # maps fnPrefix to app

    def __init__(self, *initialState, fnPrefix='', **kwargs):
        if fnPrefix in TopLevelApp._apps:
            print(f'Quitting previous version of {fnPrefix} TopLevelApp.')
            TopLevelApp._apps[fnPrefix].quit()
        if (fnPrefix != '') and ('title' not in kwargs):
            kwargs['title'] = f"TopLevelApp '{fnPrefix}'"
        if not kwargs.get('isTest', False):
            TopLevelApp._apps[fnPrefix] = self
        self._fnPrefix = fnPrefix
        self._callersGlobals = inspect.stack()[1][0].f_globals
        super().__init__(*initialState, **kwargs)

    def _callFn(self, fn, *args):
        fn = self._fnPrefix + fn
        if fn in self._callersGlobals:
            return self._callersGlobals[fn](*args)

    def redrawAll(self, canvas): self._callFn('redrawAll', self, canvas)
    def appStarted(self, *initialState): self._callFn('appStarted', self, *initialState)
    def appStopped(self): self._callFn('appStopped', self)
    def keyPressed(self, event): self._callFn('keyPressed', self, event)
    def keyReleased(self, event): self._callFn('keyReleased', self, event)
    def mousePressed(self, event): self._callFn('mousePressed', self, event)
    def mouseReleased(self, event): self._callFn('mouseReleased', self, event)
    def mouseMoved(self, event): self._callFn('mouseMoved', self, event)
    def mouseDragged(self, event): self._callFn('mouseDragged', self, event)
    def timerFired(self): self._callFn('timerFired', self)
    def sizeChanged(self): self._callFn('sizeChanged', self)
    def getState(self): return self._callFn('getState', self)

####################################
# ModalApp + Mode:
####################################


class ModalApp(App):
    def __init__(self, *initialState, modes=None, activeMode=None, **kwargs):
        self._modes = dict()  # key = mode.name, value = Mode instance
        if modes is None:
            modes = []
        for mode in modes:
            self.addMode(mode)
        self._running = False
        self._activeMode = None
        self.setActiveMode(
            (isinstance(activeMode, Mode) and activeMode) or
            (isinstance(activeMode, str) and self._modes[activeMode]) or
            (len(modes) > 0 and modes[0]) or
            None
        )
        super().__init__(*initialState, **kwargs)

    def addMode(self, mode):
        mode.app = self
        mode.isTest = mode.app._isTest
        mode.modes = self._modes
        if mode.name in self._modes:
            raise Exception(f'modename {mode.name} is already taken!')
        self._modes[mode.name] = mode
    
    def getMode(self, modeName):
        if modeName not in self._modes:
            raise Exception(f'modename {modeName} is not found--make sure you have a mode named {modeName}!')
        return self._modes[modeName]
    
    def getActiveMode(self):
        return self._activeMode

    def setActiveMode(self, mode):
        if mode is None:
            mode = Mode(name='defaultMode')  # default empty mode
        if isinstance(mode, str):
            if mode not in self._modes:
                raise Exception(f'mode {mode} does not exist!')
            mode = self._modes[mode]
        if not isinstance(mode, Mode):
            raise Exception('activeMode must be a mode!')
        if mode.app not in [None, self]:
            raise Exception('Modes cannot be added to two different apps!')
        if self._activeMode != mode:
            mode.app = self
            if self._activeMode is not None:
                self._activeMode.modeDeactivated()
            self._activeMode = mode
            if self._running:
                self.startActiveMode()

    def startActiveMode(self):
        self._activeMode.width, self._activeMode.height = self.width, self.height
        if not self._activeMode._appStartedCalled:
            self._activeMode._appStartedWrapper()  # called once per mode
            self._activeMode._appStartedCalled = True
        self._activeMode.modeActivated()  # called each time a mode is activated
        self._redrawAllWrapper()

    def redrawAll(self, canvas):
        if self._activeMode is not None:
            self._activeMode.redrawAll(canvas)

    def appStarted(self):
        if self._activeMode is not None:
            self.startActiveMode()

    def appStopped(self):
        if self._activeMode is not None:
            self._activeMode.modeDeactivated()

    def keyPressed(self, event):
        if self._activeMode is not None:
            self._activeMode.keyPressed(event)

    def keyReleased(self, event):
        if self._activeMode is not None:
            self._activeMode.keyReleased(event)

    def mousePressed(self, event):
        if self._activeMode is not None:
            self._activeMode.mousePressed(event)

    def mouseReleased(self, event):
        if self._activeMode is not None:
            self._activeMode.mouseReleased(event)

    def mouseMoved(self, event):
        if self._activeMode is not None:
            self._activeMode.mouseMoved(event)

    def mouseDragged(self, event):
        if self._activeMode is not None:
            self._activeMode.mouseDragged(event)

    def timerFired(self):
        if self._activeMode is not None:
            self._activeMode.timerFired()

    def getState(self):
        if self._activeMode is not None:
            return self._activeMode.getState()

    def sizeChanged(self):
        if self._activeMode is not None:
            self._activeMode.width = self.width
            self._activeMode.height = self.height
            self._activeMode.sizeChanged()


class Mode(App):
    def __init__(self, *initialState, name=None, **kwargs):
        if name is None:
            raise Exception('name is required in Mode instances')
        self.name = name
        self.app = None  # this will be set later
        self.modes = dict() # this too
        self._appStartedCalled = False
        super().__init__(*initialState, autorun=False, **kwargs)

    def modeActivated(self): pass
    def modeDeactivated(self): pass
    def setActiveMode(self, mode): self.app.setActiveMode(mode)
    def getActiveMode(self): return self.app.getActiveMode()
    def getMode(self, modeName):
        return self.app.getMode(modeName)
    def loadImage(self, path=None): return self.app.loadImage(path)

####################################
# runApp()
####################################


'''
def showGraphics(drawFn, **kwargs):
    class GraphicsApp(App):
        def __init__(app, **kwargs):
            if ('title' not in kwargs):
                kwargs['title'] = drawFn.__name__
            super().__init__(**kwargs)
        def redrawAll(app, canvas):
            drawFn(app, canvas)
    app = GraphicsApp(**kwargs)
'''
runApp = TopLevelApp

print(
    f'Loaded cmu_112_graphics version {App.version} (last updated {App.lastUpdated})')

if (__name__ == '__main__'):
    try:
        import cmu_112_graphics_tests
    except BaseException:
        pass
