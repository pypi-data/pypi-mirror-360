import wx
import wx.lib.filebrowsebutton as filebrowse
import os
import shutil
import time
import epics

from epics.wx.utils import  pack

FileBrowser = filebrowse.FileBrowseButtonWithHistory

ALL_EXP  = wx.ALL|wx.EXPAND
MDB_WILDCARD = 'Motors DB Files (*.mdb)|*.mdb|All files (*.*)|*.*'
       
def get_pvdesc(pvname):
    desc = pref = pvname
    if '.' in pvname:
        pref = pvname[:pvname.find('.')]
    t0 = time.time()
    descpv = epics.PV(pref + '.DESC')
    if descpv.connect():
        desc = descpv.get()
    return desc
        


def dumpsql(dbname, fname=None):
    """ dump SQL statements for an sqlite db"""
    if fname is None:
        fname =  '%s_dump.sql' % dbname
    os.system('echo .dump | sqlite3 %s > %s' % (dbname, fname))
    
def backup_versions(fname, max=5):
    """keep backups of a file -- up to 'max', in order"""
    if not os.path.exists(fname):
        return
    base, ext = os.path.splitext(fname)
    for i in range(max-1, 0, -1):
        fb0 = "%s_%i%s" % (base, i, ext)
        fb1 = "%s_%i%s" % (base, i+1, ext)
        if os.path.exists(fb0):
            try:
                shutil.move(fb0, fb1)
            except:
                pass 
    shutil.move(fname, "%s_1%s" % (base, ext))

    
def save_backup(fname, outfile=None):
    """make a copy of fname"""
    if not os.path.exists(fname):
        return
    if outfile is None:
        base, ext = os.path.splitext(fname)
        outfile = "%s_BAK%s" % (base, ext)
    return shutil.copy(fname, outfile)

def set_font_with_children(widget, font, dsize=None):
    cfont = widget.GetFont()
    font.SetWeight(cfont.GetWeight())
    if dsize == None:
        dsize = font.PointSize - cfont.PointSize
    else:
        font.PointSize = cfont.PointSize + dsize
    widget.SetFont(font)
    for child in widget.GetChildren():
        set_font_with_children(child, font, dsize=dsize)


class GUIColors(object):
    def __init__(self):
        self.bg = wx.Colour(240,240,230)
        self.nb_active = wx.Colour(254,254,195)
        self.nb_area   = wx.Colour(250,250,245)
        self.nb_text = wx.Colour(10,10,180)
        self.nb_activetext = wx.Colour(80,10,10)
        self.title  = wx.Colour(80,10,10)
        self.pvname = wx.Colour(10,10,80)

class HideShow(wx.Choice):
    def __init__(self, parent, default=True, size=(100, -1)):
        wx.Choice.__init__(self, parent, -1, size=size)
        self.choices = ('Hide', 'Show')
        self.Clear()
        self.SetItems(self.choices)
        self.SetSelection({False:0, True:1}[default])

class YesNo(wx.Choice):
    def __init__(self, parent, defaultyes=True, size=(75, -1)):
        wx.Choice.__init__(self, parent, -1, size=size)
        self.choices = ('No', 'Yes')
        self.Clear()
        self.SetItems(self.choices)
        self.SetSelection({False:0, True:1}[defaultyes])

    def SetChoices(self, choices):
        self.Clear()
        self.SetItems(choices)
        self.choices = choices
        
    def Select(self, choice):
        if isinstance(choice, int):
            self.SetSelection(0)
        elif choice in self.choices:
            self.SetSelection(self.choices.index(choice))

class ConnectDialog(wx.Dialog):
    """Connect to a recent or existing DB File, or create a new one"""
    msg = '''Select Motor DB File, or type a new file name to create a new Motor DB File'''
    def __init__(self, parent=None, filelist=None,
                 title='Select a Motor DB File'):

        wx.Dialog.__init__(self, parent, wx.ID_ANY, title=title)

        panel = wx.Panel(self)
        self.colors = GUIColors()
        panel.SetBackgroundColour(self.colors.bg)
        if parent is not None:
            self.SetFont(parent.GetFont())

        flist = []
        if filelist is not None:
            for fname in filelist:
                if os.path.exists(fname):
                    flist.append(fname)

        self.filebrowser = FileBrowser(panel, size=(600, -1))
        self.filebrowser.SetHistory(flist)
        self.filebrowser.SetLabel('File:')
        self.filebrowser.fileMask = MDB_WILDCARD

        if filelist is not None:
            self.filebrowser.SetValue(filelist[0])
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(panel, label=self.msg),
                  0, wx.ALIGN_CENTER|wx.ALL|wx.GROW, 1)
        sizer.Add(self.filebrowser, 1, wx.ALIGN_CENTER|wx.ALL|wx.GROW, 1)
        sizer.Add(self.CreateButtonSizer(wx.OK| wx.CANCEL),
                 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 1)
        pack(panel, sizer)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 0, 0, 0)
        pack(self, sizer)
        
