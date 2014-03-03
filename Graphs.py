import wx
from Data import Data
from matplotlib import pyplot as plt
from Dialogues import ColumnSelect
from scipy import stats
import numpy as np

class GraphMenu(wx.Menu):
    def __init__(self, parent):
        wx.Menu.__init__(self)
        self.parent = parent
        hist = self.Append(wx.NewId(), 'Histogram')
        parent.Bind(wx.EVT_MENU, self.createHist, hist)

        boxplot = self.Append(wx.NewId(), 'Boxplot')
        parent.Bind(wx.EVT_MENU, self.createBoxplot, boxplot)

        scatter = self.Append(wx.NewId(), "Scatter Plot")
        parent.Bind(wx.EVT_MENU, self.createScatter, scatter)

        time = self.Append(wx.NewId(), "Time Series")
        parent.Bind(wx.EVT_MENU, self.createTime, time)

    def createHist(self, event):
        # TODO avoid hardcoding sizes. Find smart way to decide on sizes 
        dlg = wx.Dialog(self.parent, title="Histogram input", size=(500, 200))
        cs = ColumnSelect(dlg, self.parent.data, ("Select Data",))
        hsize = wx.BoxSizer(wx.HORIZONTAL)

        # options
        vsize1 = wx.BoxSizer(wx.VERTICAL)

        hsize1 = wx.BoxSizer(wx.HORIZONTAL)
        bars = wx.CheckBox(dlg, label="Bars")
        density = wx.CheckBox(dlg, label="Density")
        bars.SetValue(True)
        hsize1.Add(bars)
        hsize1.Add(density)
        vsize1.Add(hsize1)

        hsize2 = wx.BoxSizer(wx.HORIZONTAL)
        hsize2.Add(wx.StaticText(dlg, label="# of Bins"))
        numBins = wx.SpinCtrl(dlg, min=1, max=999, size=(50, -1))
        # default numBins = sqrt(Num of data points)
        numBins.SetValue(np.sqrt(len(self.parent.data)))
        hsize2.Add(numBins)
        vsize1.Add(hsize2)

        hsize3 = wx.BoxSizer(wx.HORIZONTAL)
        hsize3.Add(wx.StaticText(dlg, label="Density Bandwidth"))
        bandwidth = wx.SpinCtrl(dlg, value="0", min=-10, max=10, size=(50, -1))
        bandwidth.SetRange(-10, 10)
        hsize3.Add(bandwidth)
        vsize1.Add(hsize3)

        subplots = wx.CheckBox(dlg, label="Subplots? (Only for bars)")
        vsize1.Add(subplots)

        hsize.Add(vsize1)
        hsize.AddSpacer(20)
        hsize.Add(cs, flag=wx.EXPAND)

        vsize = wx.BoxSizer(wx.VERTICAL)
        vsize.Add(hsize, 1, flag=wx.EXPAND) #don't know why the 1 is necessary

        
        ok = wx.Button(dlg, -1, "OK")
        ok.Bind(wx.EVT_BUTTON, lambda x: dlg.Close())
        vsize.Add(ok)


        dlg.SetSizer(vsize)
        dlg.ShowModal()
        ds = list(zip(*cs.GetValue())[0])
        dlg.Destroy()

        # TODO legend

        a = np.nanmin(self.parent.data[ds])
        b = np.nanmax(self.parent.data[ds])
        x = np.arange(a, b, (b-a) / 1000.0)
        bins = np.arange(a, b, float(b-a) / numBins.GetValue())

        if subplots.GetValue():
            self.parent.data[ds].hist()
        else:
            for d in ds:
                data = self.parent.data[d]
                data = data[np.isfinite(data)]

                if bars.GetValue():
                    plt.hist(data, bins=bins, alpha=0.7/len(ds), normed=density.GetValue())
                if density.GetValue():
                    dens = stats.kde.gaussian_kde(data)
                    dens.set_bandwidth(bw_method=dens.factor * 
                            np.exp(-0.2*bandwidth.GetValue()))
                    plt.plot(x, dens(x), color="b")
        plt.show()

    def createBoxplot(self, event):
        dlg = wx.Dialog(self.parent, title="Boxplot Input", size=(500, 200))
        cs = ColumnSelect(dlg, self.parent.data, ("Select Data",))
        vsize = wx.BoxSizer(wx.VERTICAL)
        vsize.Add(cs, 1, wx.EXPAND)

        ok = wx.Button(dlg, -1, "OK")
        ok.Bind(wx.EVT_BUTTON, lambda x: dlg.Close())
        vsize.Add(ok)

        dlg.SetSizer(vsize)

        dlg.ShowModal()
        ds = list(zip(*cs.GetValue())[0])
        dlg.Destroy()

        self.parent.data[ds].boxplot()
        plt.show()

    def createScatter(self, event):
        dlg = wx.Dialog(self.parent, title="Scatterplot Input", size=(700, 200))
        cs = ColumnSelect(dlg, self.parent.data, ("X","Y"))
        vsize = wx.BoxSizer(wx.VERTICAL)

        hsize = wx.BoxSizer(wx.HORIZONTAL)
        regress = wx.CheckBox(dlg, label="Add Regression Lines?")
        hsize.Add(regress)
        hsize.AddSpacer(20)
        hsize.Add(cs)

        vsize.Add(hsize, 1, wx.EXPAND)

        ok = wx.Button(dlg, -1, "OK")
        ok.Bind(wx.EVT_BUTTON, lambda x: dlg.Close())
        vsize.Add(ok)

        dlg.SetSizer(vsize)

        dlg.ShowModal()
        ds = cs.GetValue()
        dlg.Destroy()

        fig = plt.figure()
        ax = fig.add_subplot(111)

        # TODO get better color scheme
        colors = "rgby"

        for i, (x, y) in enumerate(ds):
            ax.scatter(self.parent.data[x], self.parent.data[y], marker="o", 
                    color = colors[i % len(colors)], label=y)
            if regress.GetValue():
                line = np.poly1d(np.polyfit(self.parent.data[x], self.parent.data[y], 1))
                ax.plot(self.parent.data[x], line(self.parent.data[x]))
        ax.legend(loc='best')
        ax.figure.show()

    def createTime(self, event):
        dlg = wx.Dialog(self.parent, title="Time Series Input", size=(500, 200))
        cs = ColumnSelect(dlg, self.parent.data, ("Select Data",))
        vsize = wx.BoxSizer(wx.VERTICAL)
        vsize.Add(cs, 1, wx.EXPAND)

        ok = wx.Button(dlg, -1, "OK")
        ok.Bind(wx.EVT_BUTTON, lambda x: dlg.Close())
        vsize.Add(ok)

        dlg.SetSizer(vsize)

        dlg.ShowModal()
        ds = list(zip(*cs.GetValue())[0])
        dlg.Destroy()

        self.parent.data[ds].plot()
        plt.legend(loc='best')
        plt.show()

