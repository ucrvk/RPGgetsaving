import wx
from wget import download
from apihandle import *
from settings import *
from filehandle import *


def activitySign(activity: dict):
    ans = [
        "检测到活动：\n",
        "活动名称：",
        activity["themeName"],
        "\n起点：",
        activity["startingPoint"],
        "\n终点：",
        activity["terminalPoint"],
        "\n长度：",
        str(activity["distance"]),
        "km\n服务器名称：",
        activity["serverName"],
        "\n开始时间：",
        activity["startTime"],
        "\n是否安装存档？",
    ]
    return "".join(ans)


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(
            None,
            title="简易接档器",
            size=(500, 300),
            style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX,
        )
        self.SetSizeHints(500, 300, 500, 300)
        self.SetMaxSize((500, 300))
        icon = wx.Icon(get_resource_path("fengmian.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.panel = wx.Panel(self)
        self.accountText = wx.TextCtrl(self.panel, pos=(50, 10), size=(200, -1))
        self.accountText.SetHint("账号")
        self.passwdText = wx.TextCtrl(
            self.panel,
            style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER,
            pos=(50, 40),
            size=(200, -1),
        )
        self.passwdText.SetHint("密码或token")
        self.passwdText.Bind(wx.EVT_TEXT_ENTER, self.onLoadButtonClicked)
        loadButton = wx.Button(self.panel, label="安装", pos=(60, 70))
        loadButton.Bind(wx.EVT_BUTTON, self.onLoadButtonClicked)
        unloadButton = wx.Button(self.panel, label="卸载", pos=(150, 70))
        unloadButton.Bind(wx.EVT_BUTTON, self.onUnloadButtonClicked)
        cleanButton = wx.Button(self.panel, label="清理", pos=(240, 70))
        cleanButton.Bind(wx.EVT_BUTTON, self.onCleanButtonClicked)
        authorText = wx.StaticText(
            self.panel, label="作者：wenwen12\n我是神里绫华的狗", pos=(380, 220)
        )
        authorText.SetForegroundColour(wx.Colour(102, 209, 255))
        self.gamedirText = wx.TextCtrl(self.panel, pos=(50, 100), size=(300, -1))
        self.gamedirText.SetHint("游戏目录")
        GameDirChooserButton = wx.Button(self.panel, label="选择游戏目录", pos=(350, 100))
        GameDirChooserButton.Bind(wx.EVT_BUTTON, self.onGameDirChooserButtonClicked)
        self.savingdirText = wx.TextCtrl(self.panel, pos=(50, 130), size=(300, -1))
        self.savingdirText.SetHint("存档目录")
        SavingDirChooserButton = wx.Button(self.panel, label="选择存档目录", pos=(350, 130))
        SavingDirChooserButton.Bind(wx.EVT_BUTTON, self.onSavingDirChooserButtonClicked)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.ShowSetting()

    def onLoadButtonClicked(self, event):
        DOCUMENTS_DIR=self.savingdirText.GetValue()
        GAME_DIR=self.gamedirText.GetValue()
        if len(self.passwdText.GetValue()) < 12:
            token = logIn(self.accountText.GetValue(), self.passwdText.GetValue())
            self.passwdText.SetValue(token)
            if type(token) == int:
                wx.MessageBox(loginErrorCompose(token), "发生错误", wx.OK | wx.ICON_ERROR)
        token = self.passwdText.GetValue()
        if type(token) == str:
            activity = getActivity(token)
            if not activity:
                wx.MessageBox(
                    "登录成功，但现在暂时没有活动，请等等再来吧", "暂时没有活动", wx.OK | wx.ICON_INFORMATION
                )
            elif type(activity) == int:
                wx.MessageBox(
                    loginErrorCompose(activity), "发生错误", wx.OK | wx.ICON_ERROR
                )
            else:
                dlg = wx.MessageDialog(
                    None,
                    activitySign(activity),
                    "检测到活动",
                    wx.YES_NO | wx.ICON_QUESTION | wx.CENTRE,
                )
                result = dlg.ShowModal()
                dlg.Destroy()

                if result == wx.ID_YES:
                    if os.path.exists(GAME_DIR + "changed.json"):
                        wx.MessageBox(
                            "请先卸载再安装\n如果卸载没用，请尝试清理", "请先卸载", wx.OK | wx.ICON_ERROR
                        )
                    else:
                        processBar = wx.Gauge(self.panel)
                        processBar.SetPosition((50, 100))
                        print("1")
                        processContent = wx.StaticText(self.panel)
                        processContent.SetPosition((50, 120))
                        processContent.SetLabel("正在下载存档文件")
                        url = activity["profileFile"]
                        File = download(url)
                        processBar.SetValue(25)
                        processContent.SetLabel("正在解压")
                        with ZipFile(
                            os.path.abspath(".") + "\\" + File, "r"
                        ) as zip_ref:
                            zip_ref.extractall(DOCUMENTS_DIR)
                        processBar.SetValue(50)
                        processContent.SetLabel("正在隐藏dlc")
                        sig = {
                            "savingPosition": get_recently_modified_folder(
                                DOCUMENTS_DIR
                            )
                        }
                        changedDLC = []
                        for dlc in activity["unloadDlcList"]:
                            if os.path.exists(GAME_DIR + dlc):
                                os.rename(GAME_DIR + dlc, GAME_DIR + dlc + ".disabled")
                                changedDLC.append(GAME_DIR + dlc + ".disabled")
                        sig.update(changedDLC=changedDLC)
                        with open(GAME_DIR + "changed.json", "w") as cre:
                            json.dump(sig, cre)
                        processBar.SetValue(75)
                        processContent.SetLabel("正在删除缓存")
                        os.remove(os.path.abspath(".") + "\\" + File)
                        processBar.SetValue(100)
                        processContent.SetLabel("安装完成")

    def onUnloadButtonClicked(self, event):
        GAME_DIR=self.gamedirText.GetValue()
        if os.path.exists(GAME_DIR + "changed.json"):
            with open(GAME_DIR + "changed.json") as sigFile:
                sig = json.load(sigFile)
            if os.path.exists(sig["savingPosition"]):
                rmtree(sig["savingPosition"])
            for DLC in sig["changedDLC"]:
                os.rename(DLC, DLC[:-8])
            os.remove(GAME_DIR + "changed.json")
            wx.MessageBox("已完成卸载", "卸载成功", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox(
                "发生错误，未找到卸载指示文件\n可能是因为你没有安装就卸载\n请检查游戏目录下是否存在changed.json\n若实在无法解决，请删除游戏文件夹中所有.disabled的文件，并检查完整性",
                "未找到文件",
                wx.OK | wx.ICON_ERROR,
            )

    def onCleanButtonClicked(self, event):
        GAME_DIR=self.gamedirText.GetValue()
        dlg = wx.MessageDialog(
            None,
            "执行清理操作后，将删除本程序对游戏的全部更改\n请注意，在清理完成后，您可能需要检查完整性才能继续使用",
            "清理提示",
            wx.YES_NO | wx.ICON_QUESTION | wx.CENTRE,
        )
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_YES:
            dlg = wx.MessageDialog(
                None,
                "这是最后一次提示，您确定要清理吗?",
                "清理提示",
                wx.YES_NO | wx.ICON_QUESTION | wx.CENTRE,
            )
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_YES:
                delDisabled(GAME_DIR)
            if os.path.exists(GAME_DIR + "changed.json"):
                os.remove(GAME_DIR + "changed.json")
            wx.MessageBox("清理完成", "清理完成", wx.OK | wx.ICON_INFORMATION)

    def onSavingDirChooserButtonClicked(self, event):
        dialog = wx.DirDialog(
            self.panel,
            "选择游戏存档文件夹，通常位置是文档/euro truck simulator2",
            "",
            wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
        )
        if dialog.ShowModal() == wx.ID_OK:
            folder_path = dialog.GetPath()
            self.savingdirText.SetValue(folder_path)
        dialog.Destroy()

    def onGameDirChooserButtonClicked(self, event):
        dialog = wx.DirDialog(
            self.panel,
            "选择游戏路径文件夹，通常位置是Steam/steamapps/common/Euro Truck Simulator 2",
            "",
            wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
        )
        if dialog.ShowModal() == wx.ID_OK:
            folder_path = dialog.GetPath()
            self.gamedirText.SetValue(folder_path)
        dialog.Destroy()


    def ShowSetting(self):
        setting = settingLoad()
        if isinstance(setting,Exception):
            wx.MessageBox(f"设置读取错误，详细信息:{setting}", "错误", wx.OK | wx.ICON_ERROR)
            setting = defaultJson
        self.accountText.SetValue(setting["user"]["id"])
        self.passwdText.SetValue(setting["user"]["token"])
        self.savingdirText.SetValue(setting["gameDirectory"]["saving"])
        self.gamedirText.SetValue(setting["gameDirectory"]["game"])

    def TextLoad(self):
        return {
            "user": {
                "token": self.passwdText.GetValue(),
                "id": self.accountText.GetValue(),
            },
            "gameDirectory": {
                "saving": self.savingdirText.GetValue(),
                "game": self.gamedirText.GetValue(),
            },
        }
    def onClose(self,event):
        settingSave(self.TextLoad())
        self.Destroy()

    

if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame()
    frame.Show()
    app.MainLoop()
