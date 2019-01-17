import functools
import json
import os
import re
import shutil
import threading
import time
import win32clipboard

import PIL.Image
import win32con
import wx

from Classes import Threads, FrameClasses, noname, InfoClasses
from Functions import function, tools


class BaseWorkClass:
    def __init__(self, frame):
        self.frame = frame


class PaintingWork(BaseWorkClass):
    """a class only to deal with the tex for azur lane"""

    def __init__(self,
                 form: noname.MyFrame1 = ...,
                 setting: dict = ...,
                 default: dict = ...,
                 start_path: str = os.getcwd()):

        super(PaintingWork, self).__init__(form)

        self.tex_type = 1
        self.mesh_type = 2

        self.start_path = start_path
        self.form = self.frame

        self.__dialog = None
        # infomation
        self.info: InfoClasses.PerInfoList = InfoClasses.PerInfoList()

        self.unable: InfoClasses.PerInfoList = InfoClasses.PerInfoList()

        self.skip: InfoClasses.PerInfoList = InfoClasses.PerInfoList()

        self.able: InfoClasses.PerInfoList = InfoClasses.PerInfoList()

        # search

        self.search_mesh_val: InfoClasses.PerInfoList = InfoClasses.PerInfoList()
        self.search_tex_val: InfoClasses.PerInfoList = InfoClasses.PerInfoList()
        self.search_skip_val: InfoClasses.PerInfoList = InfoClasses.PerInfoList()
        self.search_unable_val: InfoClasses.PerInfoList = InfoClasses.PerInfoList()
        # choice
        self.choice: InfoClasses.PerInfoList = InfoClasses.PerInfoList()

        try:
            with open('%s\\files\\names.json' % self.start_path, 'r')as file:
                self.names = json.load(file)
        except FileNotFoundError:
            self.names = {}

        self.save_path = ''
        self.save_path_list = []

        self.form.m_choice_pass.Enable(False)
        self.form.m_choice_unable.Enable(False)

        self.tex_search = False
        self.mesh_search = False
        self.skip_search = False
        self.unable_search = False

        self.error_list = []

        self.setting = setting["azur_lane"]

        self.full = setting["full"]

        self.default = default["azur_lane"]

        self.lock = default['lock']

        self.pattern_tex = re.compile(self.setting['tex_limit'])
        self.pattern_mesh = re.compile(self.setting['mesh_limit'])

        self.restore: Threads.RestoreThread = threading.Thread()

        self.able_add = False

        # file load method

    def any_error(self):
        return self.error_list != []

    def is_able_add(self):
        return self.able_add

    def is_choice(self):
        return self.choice

    def is_able(self):
        return bool(self.able)

    # load
    def load_tex(self):
        self.form.m_gauge_tex_load.SetValue(0)
        if self.lock:
            address = self.default['default_tex_dir']
        else:
            address = os.getcwd()
        self.__dialog = wx.FileDialog(self.form, "打开", address, "AzurLane.png",
                                      "*.PNG", style=wx.FD_MULTIPLE | wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST)

        if self.__dialog.ShowModal() == wx.ID_OK:

            self.form.m_staticText_load_tex.SetLabel("开始")
            self.form.m_gauge_tex_load.SetValue(0)
            paths = self.__dialog.GetPaths()

            if self.full['clear_list']:
                self.info.clear()

            returned = tools.file_deal2(paths, self.info, self.full['clear_list'], self.pattern_tex, True, '',
                                        self.names, self.tex_type)
            if returned[0]:
                self.form.m_gauge_tex_load.SetValue(100)

                self.form.m_listBox_tex.Set(
                    self.info.for_show)
            self.form.m_staticText_load_tex.SetLabel(returned[1])
            address = paths
        else:
            address = ''
        self.info_check()

        return address

    def load_mesh(self):
        self.form.m_gauge_tex_load.SetValue(0)
        if self.lock:
            address = self.default['default_mesh_dir']
        else:
            address = os.getcwd()
        self.__dialog = wx.FileDialog(self.form, "打开", address,
                                      wildcard="*.OBJ", style=wx.FD_MULTIPLE | wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST)

        if self.__dialog.ShowModal() == wx.ID_OK:
            self.form.m_staticText_mesh_load.SetLabel("开始")
            self.form.m_gauge_mesh_load.SetValue(0)
            paths = self.__dialog.GetPaths()

            if self.full['clear_list']:
                self.info.clear()

            returned = tools.file_deal2(paths, self.info, self.full['clear_list'], self.pattern_mesh, True, "-mesh",
                                        self.names, self.mesh_type)

            if returned[0]:
                self.form.m_gauge_mesh_load.SetValue(function.re_int(100))

                self.form.m_listBox_mesh.Set(
                    self.info.for_show)
            self.form.m_staticText_mesh_load.SetLabel(returned[1])

            address = paths
        else:
            address = ''

        self.info_check()

        return address

    def load_mesh_fold(self):
        self.form.m_gauge_tex_load.SetValue(0)
        if self.lock:
            address = self.default['default_mesh_dir']
        else:
            address = os.getcwd()

        self.__dialog = wx.DirDialog(self.form, "打开", address,
                                     style=wx.DD_NEW_DIR_BUTTON | wx.DD_CHANGE_DIR | wx.DD_DEFAULT_STYLE |
                                           wx.DD_DIR_MUST_EXIST)

        if self.__dialog.ShowModal() == wx.ID_OK:
            paths = self.__dialog.GetPath()
            self.form.m_staticText_mesh_load.SetLabel("开始")
            self.form.m_gauge_mesh_load.SetValue(0)

            paths = function.all_file_path(paths)[1]

            if self.full['clear_list']:
                self.info.clear()

            returned, info = tools.file_deal2(paths, self.info, self.full['clear_list'],
                                              self.pattern_mesh, False, "-mesh", self.names, self.mesh_type)
            if returned:
                self.form.m_gauge_mesh_load.SetValue(100)
                self.form.m_staticText_mesh_load.SetLabel(info)
                self.form.m_listBox_mesh.Set(
                    self.info.for_show)
            self.form.m_staticText_mesh_load.SetLabel(info)
            address = self.__dialog.GetPath()
        else:
            address = 'None'

        self.info_check()

        return address

    def load_tex_fold(self):
        self.form.m_gauge_tex_load.SetValue(0)
        if self.lock:
            address = self.default['default_tex_dir']
        else:
            address = os.getcwd()

        self.__dialog = wx.DirDialog(self.form, "打开", address,
                                     style=wx.DD_NEW_DIR_BUTTON | wx.DD_CHANGE_DIR | wx.DD_DEFAULT_STYLE
                                           | wx.DD_DIR_MUST_EXIST)
        info = self.__dialog.ShowModal()
        if info == wx.ID_OK:
            self.form.m_staticText_load_tex.SetLabel("开始")
            paths = self.__dialog.GetPath()

            paths = function.all_file_path(paths)[1]

            if self.full['clear_list']:
                self.info.clear()

            returned, info = tools.file_deal2(paths, self.info, self.full['clear_list'], self.pattern_tex, False, '',
                                              self.names, self.tex_type)
            if returned:
                self.form.m_gauge_tex_load.SetValue(100)

                self.form.m_listBox_tex.Set(
                    self.info.for_show)
            self.form.m_staticText_load_tex.SetLabel(info)

            address = self.__dialog.GetPath()
        else:
            address = 'None'

        self.info_check()

        return address

    def load_tex_and_mesh(self):
        self.form.m_gauge_tex_load.SetValue(0)
        self.__dialog = wx.DirDialog(self.form, "打开", os.getcwd(),
                                     style=wx.DD_NEW_DIR_BUTTON | wx.DD_CHANGE_DIR | wx.DD_DEFAULT_STYLE |
                                           wx.DD_DIR_MUST_EXIST)

        if self.__dialog.ShowModal() == wx.ID_OK:
            paths = self.__dialog.GetPath()
            self.form.m_staticText_load_tex.SetLabel('开始')
            self.form.m_staticText_mesh_load.SetLabel('开始')

            paths = function.all_file_path(paths)[1]

            if self.full['clear_list']:
                self.info.clear()

            returned_tex, tex_info = tools.file_deal2(paths, self.info, self.full['clear_list'], self.pattern_tex,
                                                      False, '',
                                                      self.names, self.tex_type)

            returned_mesh, mesh_info = tools.file_deal2(paths, self.info, self.full['clear_list'],
                                                        self.pattern_mesh, False, "-mesh", self.names, self.mesh_type)
            if returned_tex:
                self.form.m_gauge_tex_load.SetValue(100)

                self.form.m_listBox_tex.Set(
                    self.info.for_show)
            self.form.m_staticText_load_tex.SetLabel(tex_info)
            if returned_mesh:
                self.form.m_gauge_mesh_load.SetValue(100)

                self.form.m_listBox_mesh.Set(
                    self.info.for_show)
            self.form.m_staticText_mesh_load.SetLabel(mesh_info)

            address = self.__dialog.GetPath()
        else:
            address = 'None'

        self.info_check()

        return address

    def drop_work(self, file_names, ):
        try:
            file_names = list(file_names)
            self.form.m_staticText_load_tex.SetLabel('开始')
            self.form.m_staticText_mesh_load.SetLabel('开始')

            dir_name = (filter(lambda x: not os.path.isfile(x), file_names))
            dir_name = map(lambda x: function.all_file_path(x)[1].values(), dir_name)
            list(map(lambda x: file_names.extend(x), dir_name))

            file_names = (filter(lambda x: os.path.isfile(x), file_names))

            if self.full['clear_list']:
                self.info.clear()

            paths = list(filter(lambda x: re.match(r'^UISprite\s#\d+\.png$', os.path.basename(x)) is None, file_names))

            returned_tex, tex_info = tools.file_deal2(paths, self.info, self.full['clear_list'], self.pattern_tex,
                                                      True, '', self.names, self.tex_type)

            returned_mesh, mesh_info = tools.file_deal2(paths, self.info, self.full['clear_list'],
                                                        self.pattern_mesh, True, "-mesh", self.names, self.mesh_type)
            if returned_tex:
                self.form.m_gauge_tex_load.SetValue(100)

                self.form.m_listBox_tex.Set(
                    self.info.for_show)
            self.form.m_staticText_load_tex.SetLabel(tex_info)
            if returned_mesh:
                self.form.m_gauge_mesh_load.SetValue(100)

                self.form.m_listBox_mesh.Set(self.info.for_show)
            self.form.m_staticText_mesh_load.SetLabel(mesh_info)

            self.info_check()

        except RuntimeError as info:
            return False, info

        else:
            return True, ''

    def open_give(self, dir_address):

        files = function.all_file_path(dir_address)[1].values()
        # print(files)
        self.drop_work(files)

    # choice
    def mesh_choice(self):

        indexes = self.frame.m_listBox_mesh.GetSelections()

        last = self.choice
        if self.mesh_search:
            self.choice = self.search_mesh_val.build_search(indexes)
        else:
            self.choice = self.info.build_search(indexes)

        last = last.get_new(self.choice)

        if len(last) > 0:
            if last.is_all_able():
                self.form.m_menuItem_choice.Enable(True)
            show = Threads.QuickRestore(last[-1], self.form, self.start_path, self.full)
            show.start()

    def tex_choice(self):
        indexes = self.frame.m_listBox_tex.GetSelections()

        last = self.choice
        if self.tex_search:
            self.choice = self.search_tex_val.build_search(indexes)
        else:
            self.choice = self.info.build_search(indexes)

        last = last.get_new(self.choice)

        if len(last) > 0:
            if last.is_all_able():
                self.form.m_menuItem_choice.Enable(True)
            show = Threads.QuickRestore(last[-1], self.form, self.start_path, self.full)
            show.start()

    def open_file(self):
        indexes = self.frame.m_listBox_unable.GetSelections()

        last = self.choice
        if self.unable_search:
            self.choice = self.search_unable_val.build_search(indexes)
        else:
            self.choice = self.unable.build_search(indexes)

        last = last.get_new(self.choice)

        if len(last) > 0:
            show = Threads.QuickRestore(last[-1], self.form, self.start_path, self.full)
            show.start()
        # os.system("start %s" % path)

    def open_pass(self):
        indexes = self.frame.m_listBox_skip.GetSelections()

        last = self.choice
        if self.skip_search:
            self.choice = self.search_skip_val.build_search(indexes)
        else:
            self.choice = self.skip.build_search(indexes)

        last = last.get_new(self.choice)

        if len(last) > 0:
            show = Threads.QuickRestore(last[-1], self.form, self.start_path, self.full)
            show.start()

        # export

    # export
    def export_choice(self):
        self.__dialog = wx.FileDialog(self.form, "保存", os.getcwd(), self.names[self.choice], "*.png", style=wx.FD_SAVE)

        if self.__dialog.ShowModal() == wx.ID_OK:
            self.form.m_gauge_all.SetValue(0)
            self.save_path = self.__dialog.GetPath()

            shutil.copy(f"{self.start_path}\\temp.png", self.save_path)

        self.form.m_gauge_all.SetValue(100)
        if self.full['auto_open']:
            os.system(r'"start %s"' % self.save_path)

    def export_all(self, path, for_work: InfoClasses.PerInfoList = None, for_unable: InfoClasses.PerInfoList = None):
        if self.setting["new_dir"]:
            path += r"\碧蓝航线-导出"

        os.makedirs(path, exist_ok=True)

        self.restart()
        self.save_path = path
        self.form.m_gauge_all.SetValue(0)

        if isinstance(for_work, InfoClasses.PerInfoList):
            for_work = for_work
            for_work = for_work.build_able()
        else:
            for_work = self.able
        if isinstance(for_work, InfoClasses.PerInfoList):
            for_work = for_work
            for_work = for_work.build_able()
        else:
            for_work = self.able
            for_unable = self.able

        if self.full["skip_had"]:
            self.save_path_list = function.all_file_path(self.save_path)

            self.skip = for_work.build_skip(self.save_path_list[1])
            able = for_work.remove(self.skip)

        else:
            able = for_work

        self.form.m_listBox_skip.Clear()
        self.form.m_listBox_skip.Set(self.skip.for_show)

        self.restore.add_save_path(self.save_path)
        self.restore.update_value(able, self.unable)
        if self.restore.is_alive():
            self.restore.stop_(True)
            while self.restore.is_alive():
                time.sleep(1)
            self.restore.start()
        else:
            self.restore.start()

    def copy_file(self):
        self.__dialog = wx.DirDialog(self.form, "保存", os.getcwd(),
                                     style=wx.DD_DIR_MUST_EXIST | wx.DD_CHANGE_DIR | wx.DD_NEW_DIR_BUTTON
                                           | wx.DD_DEFAULT_STYLE)
        if self.__dialog.ShowModal() == wx.ID_OK:
            path = self.__dialog.GetPath()
            num = 0
            self.form.m_gauge_all.SetValue(0)
            for name in self.unable:
                num += 1
                name.add_save(path)
                shutil.copyfile(name.tex_path, name.save_path)

                self.form.m_gauge_all.SetValue(function.re_int(100 * (num / len(self.unable))))

            if self.full['auto_open']:
                os.system(r'"%s"' % self.save_path)

        # search

    # search
    def search_mesh(self):
        value = self.form.m_searchCtrl_mesh.GetValue()
        self.search_mesh_val.clear()
        if value != '':
            indexes = function.find(value, self.info.for_search)

            self.mesh_search = True

            self.search_mesh_val.extend(self.info.build_search(indexes))

            self.frame.m_menuItem_mesh_search.Enable(True)

            self.form.m_listBox_mesh.Clear()
            self.form.m_listBox_mesh.Set(self.search_mesh_val.for_show)
        else:
            self.mesh_search = False
            self.frame.m_menuItem_tex_search.Enable(False)
            self.form.m_listBox_mesh.Clear()
            self.form.m_listBox_mesh.Set(self.info.for_show)

    def search_tex(self):
        value = self.form.m_searchCtrl_tex.GetValue()
        self.search_tex_val.clear()
        if value != '':
            indexes = function.find(value, self.info.for_search)
            self.tex_search = True

            self.search_tex_val.extend(self.info.build_search(indexes))

            self.frame.m_menuItem_tex_search.Enable(True)

            self.form.m_listBox_tex.Clear()
            self.form.m_listBox_tex.Set(self.search_tex_val.for_show)
        else:
            self.tex_search = False
            self.frame.m_menuItem_tex_search.Enable(False)
            self.form.m_listBox_tex.Clear()
            self.form.m_listBox_tex.Set(self.info.for_show)

    def search_pass(self):
        value = self.form.m_searchCtrl_pass.GetValue()
        self.search_skip_val.clear()
        if value != '':
            indexes = function.find(value, self.skip.for_search)

            self.skip_search = True

            self.search_skip_val.extend(self.skip.build_search(indexes))

            self.form.m_listBox_skip.Clear()
            self.form.m_listBox_skip.Set(self.search_skip_val.for_show)
        else:
            self.skip_search = False
            self.form.m_listBox_skip.Clear()
            self.form.m_listBox_skip.Set(self.skip.for_show)

    def search_unable(self):
        value = self.form.m_searchCtrl_unable.GetValue()
        self.search_unable_val.clear()
        if value != "":
            indexes = function.find(value, self.unable.for_search)

            self.unable_search = True

            self.search_unable_val.extend(self.info.build_search(indexes))

            self.form.m_listBox_unable.Clear()
            self.form.m_listBox_unable.Set(self.search_unable_val.for_show)
        else:
            self.unable_search = False
            self.form.m_listBox_unable.Clear()
            self.form.m_listBox_unable.Set(self.unable.for_show)

        # else

    # else
    def able_export(self):
        self.able.extend(self.info.build_able())

        self.unable.extend(self.info.build_unable())

        self.form.m_listBox_unable.Clear()
        self.form.m_listBox_unable.Set(self.unable.for_show)

        if len(self.info) >= 1:
            self.able_add = True
        else:
            self.able_add = False

        return bool(self.able)

    def restart(self):

        self.skip.clear()

        self.restore = Threads.RestoreThread(1, 'restore', self.able, self.unable, self.frame, self.setting, self.full,
                                             self.names, self.save_path)
        self.form.m_staticText_all.SetLabel("总进度：%s %%" % '0')
        self.form.m_gauge_all.SetValue(0)

    def update_setting(self, setting, default):
        self.setting = setting["azur_lane"]

        self.full = setting["full"]

        self.default = default["azur_lane"]

        self.lock = default['lock']

        self.pattern_tex = re.compile(self.setting['tex_limit'])
        self.pattern_mesh = re.compile(self.setting['mesh_limit'])

    def update_names(self):
        with open("%s\\files\\names.json" % self.start_path, 'r')as file:
            names = json.load(file)
        self.names = names

        self.info.up_date_name_cn(self.names)
        self.unable.up_date_name_cn(self.names)
        self.able.up_date_name_cn(self.names)
        self.skip.up_date_name_cn(self.names)

        self.form.m_listBox_mesh.Set(self.info.for_show)
        self.form.m_listBox_tex.Set(self.info.for_show)
        self.form.m_listBox_skip.Set(self.skip.for_show)
        self.form.m_listBox_unable.Set(self.unable.for_show)

    def info_check(self):
        if self.able_export():
            self.form.m_menuItem_all.Enable(True)
        else:
            self.form.m_menuItem_all.Enable(False)

        if len(self.unable) >= 1:
            self.form.m_menuItem_copy_only.Enable(True)
        else:
            self.form.m_menuItem_copy_only.Enable(False)


class SpineDivideWork(BaseWorkClass):
    def __init__(self, frame: noname.MyFrame1, start_path=os.getcwd()):
        super(SpineDivideWork, self).__init__(frame)

        self.path = start_path

        self.dialog = wx.Dialog

        self.cuter = ''

        self.body: PIL.Image = None

        self.bodies = []

        self.name = ''

        self.root = self.frame.m_treeCtrl_boys.AddRoot("娃娃")

        self.frame.m_bpButton_ex_spine.Enable(False)

    def need_work(self):

        if self.body is not None and len(self.cuter) >= 1:
            self.work()

    def load_body(self):
        self.dialog = wx.FileDialog(self.frame, 'body', os.getcwd(), '', "*.png",
                                    wx.FD_FILE_MUST_EXIST | wx.FD_OPEN | wx.FD_CHANGE_DIR)

        if self.dialog.ShowModal() == wx.ID_OK:
            self.body = None
            self.body = function.body_enter(self.dialog.GetFilename())

            self.need_work()

    def load_cuter(self):
        self.dialog = wx.FileDialog(self.frame, 'divide', os.getcwd(), '', "*.atlas.txt",
                                    wx.FD_FILE_MUST_EXIST | wx.FD_OPEN | wx.FD_CHANGE_DIR)
        if self.dialog.ShowModal() == wx.ID_OK:
            with open(self.dialog.GetFilename(), 'r')as file:
                self.cuter = file.read()

            self.need_work()

    def work(self):
        self.bodies.clear()

        pattern = re.compile(r'.+?\.png\nsize: \d+,\d+\nformat: \w+\nfilter: Linear,Linear\nrepeat: none')
        cuter = pattern.findall(self.cuter)

        cuter = cuter[0].replace('\\n', '\n')

        name = re.findall(r'.+\.png', cuter)[0]
        self.name = os.path.splitext(name)[0]
        name = self.name

        self.cuter = self.cuter.replace(cuter, '')

        pattern = re.compile(r'\w+\n\s\s[ \S,]+\n\s\s[ \S,]+\n\s\s[ \S,]+\n\s\s[ \S,]+\n\s\s[ \S,]+\n\s\s[ \S,]+')
        bodies = pattern.findall(self.cuter)
        root = self.frame.m_treeCtrl_boys.AppendItem(self.root, name)
        self.frame.m_treeCtrl_boys.Expand(self.root)
        for body in bodies:
            body = body.split("\n  ")

            pattern = re.compile(r'[0-9]+')
            xy = [int(info) for info in pattern.findall(body[2])]
            size = [int(info) for info in pattern.findall(body[3])]
            rotate = json.loads(body[1].split(' ')[-1])
            cuter = function.cuter(self.body, xy, size, rotate)
            self.bodies.append({'name': body[0],
                                'xy': xy,
                                'size': size,
                                'rotate': rotate,
                                'pic': cuter})
            body = self.frame.m_treeCtrl_boys.AppendItem(root, 'name: ' + body[0])
            xy_item = self.frame.m_treeCtrl_boys.AppendItem(body, "[X，Y]: " + json.dumps(xy))
            self.frame.m_treeCtrl_boys.AppendItem(xy_item, "X：%d" % (xy[0]))
            self.frame.m_treeCtrl_boys.AppendItem(xy_item, "Y：%d" % (xy[1]))
            size_item = self.frame.m_treeCtrl_boys.AppendItem(body, 'size: ' + json.dumps(size))
            self.frame.m_treeCtrl_boys.AppendItem(size_item, "wide：%d" % (size[0]))
            self.frame.m_treeCtrl_boys.AppendItem(size_item, "high：%d" % (size[1]))

            self.frame.m_treeCtrl_boys.AppendItem(body, 'rotate: ' + json.dumps(rotate))

            self.frame.m_bpButton_ex_spine.Enable(True)
            self.frame.m_bpButton_cut_way.Enable(False)
            self.frame.m_bpButton_body.Enable(False)

            self.frame.m_staticText_now.SetLabel("OK")

    def pic_open(self):
        print(self.frame.m_treeCtrl_boys.GetSelection())

    def export_pic(self):
        self.dialog = wx.DirDialog(self.frame, 'divide', os.getcwd(),
                                   wx.DD_DIR_MUST_EXIST | wx.DD_NEW_DIR_BUTTON | wx.DD_CHANGE_DIR)

        if self.dialog.ShowModal() == wx.ID_OK:
            path = os.path.join(self.dialog.GetPath(), self.name)
            os.makedirs(path, exist_ok=True)
            for val in self.bodies:
                path_save = os.path.join(path, f"{val['name']}.png")
                val['pic'].save(path_save)

            self.frame.m_gauge_ex_spine.SetValue(100)
            self.frame.m_bpButton_ex_spine.Enable(False)

    def reset(self):

        self.cuter = ''

        self.body: PIL.Image = None

        self.bodies = []

        self.name = ''

        self.frame.m_bpButton_ex_spine.Enable(False)
        self.frame.m_bpButton_cut_way.Enable(True)
        self.frame.m_bpButton_body.Enable(True)


class EncryptImage(BaseWorkClass):
    def __init__(self, frame: noname.MyDialog_Setting):
        super(EncryptImage, self).__init__(frame)
        self.dialog = None
        self.in_show = []
        self.path = {}

    def in_file(self):
        self.frame.m_gauge_file.SetValue(0)
        self.dialog = wx.FileDialog(self.frame, "打开", wildcard="*.png",
                                    style=wx.FD_OPEN | wx.FD_CHANGE_DIR | wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST)

        if self.dialog.ShowModal() == wx.ID_OK:
            returned = tools.file_deal(self.dialog.GetPaths(), self.in_show, [], [], self.path,
                                       pattern=r'^.+\.[Pp][Nn][Gg]$')

            if returned:
                self.frame.m_gauge_file.SetValue(100)
                self.frame.m_listBox_pics.Clear()
                self.frame.m_listBox_pics.Set(self.in_show)

    def in_folder(self):
        self.frame.m_gauge_dir.SetValue(0)
        self.dialog = wx.DirDialog(self.frame, "打开",
                                   style=wx.DD_CHANGE_DIR | wx.DD_NEW_DIR_BUTTON | wx.DD_DIR_MUST_EXIST)

        if self.dialog.ShowModal() == wx.ID_OK:
            path = function.all_file_path(self.dialog.GetPath())[1]

            returned = tools.file_deal(path, self.in_show, [], [], self.path,
                                       pattern=r'^.+\.[Pp][Nn][Gg]$', is_file=False)

            if returned:
                self.frame.m_gauge_dir.SetValue(100)
                self.frame.m_listBox_pics.Clear()
                self.frame.m_listBox_pics.Set(self.in_show)

    def start(self):
        self.dialog = wx.DirDialog(self.frame, "保存",
                                   style=wx.DD_CHANGE_DIR | wx.DD_NEW_DIR_BUTTON | wx.DD_DIR_MUST_EXIST)
        if self.dialog.ShowModal() == wx.ID_OK:
            thread = Threads.EncryptTread(self.in_show, self.frame.m_choice_type.GetSelection(), self.path,
                                          self.dialog.GetPath(), self.frame)
            thread.start()
            self.frame.m_button_star.Enable(False)


class Setting(BaseWorkClass):

    def __init__(self, parent, setting_dic, default, def_path, info, able_add, setting_select):
        super().__init__(frame=parent)

        self.info = info
        self.path = def_path

        self.default_tex_pattern = "^.+\\.[pP][Nn][Gg]$"
        self.default_mesh_pattern = "^.+-mesh\\.[oO][Bb][jJ]$"

        self.azur_lane_setting = InfoClasses.SettingHolder(setting_dic["azur_lane"])
        self.full_setting = InfoClasses.SettingHolder(setting_dic["full"])

        az_dict = {
            'div_type': [self.frame.m_radioBox_az_div.SetSelection, self.frame.m_radioBox_az_div.GetSelection],
            'export_type': [self.frame.m_radioBox_az_type.SetSelection, self.frame.m_radioBox_az_type.GetSelection],
            'div_use': [self.frame.m_radioBox_type_use.SetSelection, self.frame.m_radioBox_type_use.GetSelection],

            'new_dir': [self.frame.m_checkBox_az_dir.SetValue, self.frame.m_checkBox_az_dir.GetValue],
            'export_with_cn': [self.frame.m_checkBox_in_cn.SetValue, self.frame.m_checkBox_in_cn.GetValue],

            'tex_limit': [self.frame.m_textCtrl_tex_limit.SetLabel, self.frame.m_textCtrl_tex_limit.GetLabel],
            'mesh_limit': [self.frame.m_textCtrl_mesh_limit.SetLabel, self.frame.m_textCtrl_mesh_limit.SetLabel],
            'divide_list': [self.frame.m_checkList_az_limits.Set, None],

            'input_use': [self.frame.m_radioBox_im.SetSelection, self.frame.m_radioBox_im.GetSelection]
        }

        full_dict = {
            'open_dir': [self.frame.m_checkBox_autoopen.SetValue,
                         self.frame.m_checkBox_autoopen.GetValue],
            'skip_had': [self.frame.m_checkBox_pass_finished.SetValue,
                         self.frame.m_checkBox_pass_finished.GetValue],
            'auto_open': [self.frame.m_checkBox_open_temp.SetValue,
                          self.frame.m_checkBox_open_temp.GetValue],
            'finish_exit': [self.frame.m_checkBox4_finish_exit.SetValue,
                            self.frame.m_checkBox4_finish_exit.GetValue],
            'clear_list': [self.frame.m_checkBox_clear.SetValue,
                           self.frame.m_checkBox_clear.GetValue],
            'save_all': [self.frame.m_checkBox_save_all.SetValue,
                         self.frame.m_checkBox_save_all.GetValue],
        }

        self.azur_lane_setting.link_dict(az_dict)
        self.full_setting.link_dict(full_dict)

        print(self.azur_lane_setting)
        print(self.full_setting)

        group_1 = [
            self.frame.m_bpButton_del,
            self.frame.m_bpButton_add,

            self.frame.m_bpButton_up,
            self.frame.m_bpButton_down,

            self.frame.m_bpButton6_default_mesh,
            self.frame.m_bpButton_defualt_tex,

            self.frame.m_checkList_az_limits,
            self.frame.m_staticText15,
            self.frame.m_staticText161,
            self.frame.m_staticText171,

            self.frame.m_textCtrl_mesh_limit,
            self.frame.m_textCtrl_tex_limit,
        ]
        group_2 = [
            self.frame.m_radioBox_im,
            self.frame.m_radioBox_az_div,
        ]

        self.work_group_1 = InfoClasses.TeamWork(group_1,
                                                 [functools.partial(self.frame.m_textCtrl_mesh_limit.SetLabel,
                                                                    self.default_mesh_pattern),
                                                  functools.partial(self.frame.m_textCtrl_mesh_limit.SetLabel,
                                                                    self.azur_lane_setting.mesh_limit)],
                                                 [functools.partial(self.frame.m_textCtrl_tex_limit.SetLabel,
                                                                    self.default_tex_pattern),
                                                  functools.partial(self.frame.m_textCtrl_tex_limit.SetLabel,
                                                                    self.azur_lane_setting.tex_limit)],
                                                 )

        self.change_input()
        self.change_div()

        self.setting = setting_dic
        self.default = default

        self.IsChange = False
        self.lock = self.default["lock"]
        self.export = self.default["export"]

        self.az_div_list = []
        self.reset_az_pattern()
        self.index = len(self.az_div_list) + 1

        self.__choice = -1
        self.frame.m_bpButton_del.Enable(False)
        self.frame.m_bpButton_up.Enable(False)
        self.frame.m_bpButton_down.Enable(False)

        self.frame.m_bpButton6_default_mesh.Enable(False)
        #self.frame.m_bpButton_default_tex.Enable(False)



        self.tex_work = False
        self.mesh_work = False

        self.able_add = able_add
        self.able_work()
        self.setting_select = setting_select

        self.frame.m_notebook3.SetSelection(self.setting_select)

        self.frame.m_radioBox_im.Enable(False)

        self.frame.m_choice_type_in.Enable(False)
        self.frame.m_choice_type.Enable(False)

        self.names = {}

        print(self.azur_lane_setting)

    def ok_click(self, ):
        self.change_work()
        self.IsChange = True
        self.frame.Destroy()

    def apply_click(self, ):
        self.change_work()
        self.IsChange = True
        self.frame.m_sdbSizer4Apply.Enable(False)

    def change(self, ):
        self.frame.m_sdbSizer4Apply.Enable(True)

    def cancel_click(self, ):
        self.IsChange = False
        self.frame.Destroy()

    def show_choice(self):
        self.az_show()

        self.frame.m_checkBox_autoopen.SetValue(self.full_setting.open_dir)
        self.frame.m_checkBox_pass_finished.SetValue(self.full_setting.skip_had)
        self.frame.m_checkBox_open_temp.SetValue(self.full_setting.auto_open)
        self.frame.m_checkBox4_finish_exit.SetValue(self.full_setting.finish_exit)
        self.frame.m_checkBox_clear.SetValue(self.full_setting.clear_list)

        self.frame.m_checkBox_save_all.SetValue(not self.full_setting.save_all)

        self.frame.m_dirPicker_export.SetPath(self.export)

        self.frame.m_toggleBtn_lock.SetValue(self.lock)

        self.change_div()



    def change_work(self):
        self.azur_lane_setting.div_type = self.frame.m_radioBox_az_div.GetSelection()
        self.azur_lane_setting.export_type = self.frame.m_radioBox_az_type.GetSelection()
        self.azur_lane_setting.div_use = self.frame.m_radioBox_type_use.GetSelection()

        self.azur_lane_setting.new_dir = self.frame.m_checkBox_az_dir.GetValue()
        self.azur_lane_setting.export_with_cn = self.frame.m_checkBox_in_cn.GetValue()

        self.azur_lane_setting.tex_limit = self.frame.m_textCtrl_tex_limit.GetValue()
        self.azur_lane_setting.mesh_limit = self.frame.m_textCtrl_mesh_limit.GetValue()
        self.azur_lane_setting.divide_list = self.frame.azur_lane_divide_list

        self.azur_lane_setting.input_use = self.frame.m_radioBox_im.GetSelection()

        self.full_setting.open_dir = self.frame.m_checkBox_autoopen.GetValue()
        self.full_setting.skip_had = self.frame.m_checkBox_pass_finished.GetValue()
        self.full_setting.auto_open = self.frame.m_checkBox_open_temp.GetValue()
        self.full_setting.finish_exit = self.frame.m_checkBox4_finish_exit.GetValue()
        self.full_setting.clear_list = self.frame.m_checkBox_clear.GetValue()

        self.full_setting.save_all = self.frame.m_checkBox_save_all.GetValue()

        self.lock = self.default['lock'] = self.frame.m_toggleBtn_lock.GetValue()

        if self.lock:
            self.default["azur_lane"]['default_tex_dir'] = self.frame.m_dirPicker_az_tex_dir.GetPath()
            self.default["azur_lane"]['default_mesh_dir'] = self.frame.m_dirPicker_az_mesh_dir.GetPath()

            self.default['export'] = self.frame.m_dirPicker_export.GetPath()




        with open(self.path + "\\files\\names.json", 'w')as file:
            json.dump(self.names, file)

        self.setting_select = self.frame.m_notebook3.GetSelection()

    def lock_address(self):
        self.change()
        self.IsChange = True
        self.lock = self.default['lock'] = self.frame.m_toggleBtn_lock.GetValue()

        self.frame.m_dirPicker_export.Enable(not self.lock)

        self.frame.m_dirPicker_az_mesh_dir.Enable(not self.lock)
        self.frame.m_dirPicker_az_tex_dir.Enable(not self.lock)

    def az_add(self):
        self.change()
        dialog = FrameClasses.AddPattern(self, self.index)

        dialog.ShowModal()
        if dialog.is_ok:
            self.index += 1
            index, name, dir_path, pattern = dialog.get()
            self.azur_lane_setting.divide_list.append({'name': name, 'dir': dir_path, 'pattern': pattern})

            self.frame.m_checkList_az_limits.Clear()
            self.reset_az_pattern()
            self.frame.m_checkList_az_limits.Set(self.az_div_list)

    def az_del(self):
        self.change()
        self.frame.m_checkList_az_limits.Clear()
        if self.azur_lane_setting.divide_list[self.__choice]['name'] == 'else':
            pass
        else:
            del self.azur_lane_setting.divide_list[self.__choice]

        self.frame.m_bpButton_del.Enable(False)
        self.frame.m_bpButton_up.Enable(False)
        self.frame.m_bpButton_down.Enable(False)
        self.reset_az_pattern()
        self.frame.m_checkList_az_limits.Set(self.az_div_list)

    def choice(self, ):
        self.__choice = self.frame.m_checkList_az_limits.GetSelection()

        if self.__choice != 0:
            self.frame.m_bpButton_del.Enable(True)
        if self.__choice <= 1:
            self.frame.m_bpButton_up.Enable(False)
        else:
            self.frame.m_bpButton_up.Enable(True)
        if self.__choice == len(self.azur_lane_setting.divide_list) - 1 or self.__choice == 0:
            self.frame.m_bpButton_down.Enable(False)
        else:
            self.frame.m_bpButton_down.Enable(True)

    def change_type(self, ):
        self.change()

        self.az_type_use()

    def change_div(self, ):
        self.change()
        if self.frame.m_radioBox_type_use.GetSelection() == 0:
            if self.frame.m_radioBox_az_div.GetSelection() == 2:
                self.change()
                self.frame.m_checkList_az_limits.Clear()
                self.frame.m_checkList_az_limits.Set([
                    r'1）其他：^.+$',
                    r'2）皮肤：^[a-zA-Z0-9_]+_\d$',
                    r'3）改造：^[a-zA-Z0-9_]+_[gG]$',
                    r'4）婚纱：^[a-zA-Z0-9_]+_[hH]$',
                    r'5）原皮：^[a-zA-Z0-9_]+$',
                ])
            else:
                self.frame.m_checkList_az_limits.Clear()

    def change_pattern(self, ):
        self.change()

        index_2 = self.frame.m_checkList_az_limits.GetSelection()
        dialog = FrameClasses.AddPattern(self, index_2 + 1, self.azur_lane_setting.divide_list[index_2]['name'],
                                         self.azur_lane_setting.divide_list[index_2]['pattern'],
                                         self.azur_lane_setting.divide_list[index_2]['dir'])
        dialog.ShowModal()
        if dialog.is_ok:
            index, name, dir_path, pattern = dialog.get()
            self.azur_lane_setting.divide_list[index_2] = ({'name': name, 'dir': dir_path, 'pattern': pattern})

            self.frame.m_checkList_az_limits.Clear()
            self.reset_az_pattern()
            self.frame.m_checkList_az_limits.Set(self.az_div_list)

    def az_up(self, ):

        temp = self.azur_lane_setting.divide_list[self.__choice - 1]

        self.azur_lane_setting.divide_list[self.__choice - 1] = self.azur_lane_setting.divide_list[self.__choice]

        self.azur_lane_setting.divide_list[self.__choice] = temp

        self.change()

        self.reset_az_pattern()
        self.frame.m_checkList_az_limits.Clear()
        self.frame.m_checkList_az_limits.Set(self.az_div_list)

        self.__choice -= 1
        self.frame.m_checkList_az_limits.SetSelection(self.__choice)

        self.choice()

    def az_down(self, ):
        temp = self.azur_lane_setting.divide_list[self.__choice + 1]

        self.azur_lane_setting.divide_list[self.__choice + 1] = self.azur_lane_setting.divide_list[self.__choice]

        self.azur_lane_setting.divide_list[self.__choice] = temp

        self.change()

        self.reset_az_pattern()
        self.frame.m_checkList_az_limits.Clear()
        self.frame.m_checkList_az_limits.Set(self.az_div_list)

        self.__choice += 1
        self.frame.m_checkList_az_limits.SetSelection(self.__choice)

        self.choice()

    def default_mesh(self, ):
        self.change()

        self.frame.m_textCtrl_mesh_limit.SetLabel(self.default_mesh_pattern)
        self.mesh_work = True

    def default_tex(self, ):
        self.change()

        self.frame.m_textCtrl_tex_limit.SetLabel(self.default_tex_pattern)
        self.tex_work = True

    def change_reset_mesh(self, ):
        self.change()
        if self.mesh_work:
            self.mesh_work = False
        else:
            self.frame.m_bpButton6_default_mesh.Enable(True)

    def change_reset_tex(self, ):
        self.change()
        if self.tex_work:
            self.tex_work = False
        else:
            self.frame.m_bpButton_defualt_tex.Enable(True)

    def change_page(self, ):
        self.setting_select = self.frame.m_notebook3.GetSelection()

    def change_input(self, ):
        self.change()
        if self.frame.m_radioBox_type_use.GetSelection() == 0:
            choice = self.frame.m_radioBox_im.GetSelection()
            tex = [
                r'^.+\.[Pp][Nn][Gg]$',
                r'^[^_\s]+_\d\.[Pp][Nn][Gg]$',
                r'^[^_\s]+_[Hh]\.[Pp][Nn][Gg]$',
                r'^[^_\s]+_[Gg]\.[Pp][Nn][Gg]$',
                r'^[^_\s]+(_younv){0,1}\.[Pp][Nn][Gg]$',
            ]
            mesh = [
                r'^.+-mesh\.[oO][Bb][Jj]$',
                r'^[^_\s]+_\d-mesh\.[oO][Bb][Jj]$',
                r'^[^_\s]+_[Hh]-mesh\.[oO][Bb][Jj]$',
                r'^[^_\s]+_[Gg]-mesh\.[oO][Bb][Jj]$',
                r'^[^_\s]+(_younv){0,1}-mesh\.[oO][Bb][Jj]$',
            ]
            if choice == 0:
                self.frame.m_textCtrl_tex_limit.SetLabel(tex[0])
                self.frame.m_textCtrl_mesh_limit.SetLabel(mesh[0])
            elif choice == 1:
                self.frame.m_textCtrl_tex_limit.SetLabel(tex[1])
                self.frame.m_textCtrl_mesh_limit.SetLabel(mesh[1])
            elif choice == 2:
                self.frame.m_textCtrl_tex_limit.SetLabel(tex[2])
                self.frame.m_textCtrl_mesh_limit.SetLabel(mesh[2])
            elif choice == 3:
                self.frame.m_textCtrl_tex_limit.SetLabel(tex[3])
                self.frame.m_textCtrl_mesh_limit.SetLabel(mesh[3])
            elif choice == 4:
                self.frame.m_textCtrl_tex_limit.SetLabel(tex[4])
                self.frame.m_textCtrl_mesh_limit.SetLabel(mesh[4])
            else:
                pass
        self.frame.m_bpButton_defualt_tex.Enable(False)
        self.frame.m_bpButton6_default_mesh.Enable(False)

    def type_ch(self, ):
        if self.frame.m_simplebook4.GetSelection() == 0:
            self.frame.m_simplebook4.SetSelection(1)

        elif self.frame.m_simplebook4.GetSelection() == 1:
            self.frame.m_simplebook4.SetSelection(0)

    def menu_setting(self):
        dialog = FrameClasses.MenuChoice(self, self.path)

        dialog.Show()

        # self.dir_menu, self.dir_bg = dialog.gets()

    def GetValue(self):
        return self.setting

    def GetDefault(self):
        return self.default

    def az_show(self, ):
        self.frame.m_radioBox_az_div.SetSelection(self.azur_lane_setting.div_type)
        self.frame.m_radioBox_az_type.SetSelection(self.azur_lane_setting.export_type)

        self.frame.m_radioBox_type_use.SetSelection(self.azur_lane_use_default)

        self.frame.m_checkBox_az_dir.SetValue(self.azur_lane_new_dir)
        self.frame.m_checkBox_in_cn.SetValue(self.azur_lane_with_cn)

        self.frame.m_dirPicker_az_tex_dir.SetPath(self.azur_lane_default_tex_dir)
        self.frame.m_dirPicker_az_mesh_dir.SetPath(self.azur_lane_default_mesh_dir)

        self.frame.m_textCtrl_tex_limit.SetLabel(self.azur_lane_tex_limit)
        self.frame.m_textCtrl_mesh_limit.SetLabel(self.azur_lane_mesh_limit)

        self.frame.m_checkList_az_limits.Set(self.az_div_list)

        self.frame.m_radioBox_im.SetSelection(self.azur_lane_input_use)

        self.az_type_use()

    def az_type_use(self, ):
        if self.frame.m_radioBox_type_use.GetSelection() == 0:
            self.frame.m_staticText15.Enable(False)
            self.frame.m_staticText161.Enable(False)
            self.frame.m_staticText171.Enable(False)

            self.frame.m_textCtrl_mesh_limit.Enable(False)
            self.frame.m_textCtrl_tex_limit.Enable(False)

            self.frame.m_textCtrl_mesh_limit.SetLabel(self.default_mesh_pattern)
            self.frame.m_textCtrl_tex_limit.SetLabel(self.default_tex_pattern)

            self.frame.m_radioBox_im.Enable(True)
            self.change_input()

            self.frame.m_bpButton_del.Enable(False)
            self.frame.m_bpButton_add.Enable(False)

            self.frame.m_bpButton_up.Enable(False)
            self.frame.m_bpButton_down.Enable(False)

            self.frame.m_bpButton6_default_mesh.Enable(False)
            self.frame.m_bpButton_defualt_tex.Enable(False)

            self.frame.m_checkList_az_limits.Enable(False)

            ####

            self.frame.m_radioBox_az_div.Enable(True)

            self.change_div()

        else:
            self.frame.m_staticText15.Enable(True)
            self.frame.m_staticText161.Enable(True)
            self.frame.m_staticText171.Enable(True)

            self.frame.m_textCtrl_mesh_limit.Enable(True)
            self.frame.m_textCtrl_tex_limit.Enable(True)

            self.frame.m_bpButton_del.Enable(False)
            self.frame.m_bpButton_add.Enable(True)

            self.frame.m_bpButton_up.Enable(False)
            self.frame.m_bpButton_down.Enable(False)

            self.frame.m_textCtrl_mesh_limit.SetLabel(self.azur_lane_mesh_limit)
            self.frame.m_textCtrl_tex_limit.SetLabel(self.azur_lane_tex_limit)

            self.frame.m_radioBox_im.Enable(False)

            if self.frame.m_textCtrl_tex_limit.GetValue() != self.default_tex_pattern:
                self.frame.m_bpButton_defualt_tex.Enable(True)
            else:
                self.frame.m_bpButton_defualt_tex.Enable(False)
            if self.frame.m_textCtrl_mesh_limit.GetValue() != self.default_mesh_pattern:
                self.frame.m_bpButton6_default_mesh.Enable(True)
            else:
                self.frame.m_bpButton6_default_mesh.Enable(False)

            self.frame.m_checkList_az_limits.Enable(True)

            ####

            self.frame.m_radioBox_az_div.Enable(False)

            self.reset_az_pattern()
            self.frame.m_checkList_az_limits.Clear()
            self.frame.m_checkList_az_limits.Set(self.az_div_list)

    def reset_az_pattern(self):
        self.az_div_list.clear()
        for value in range(len(self.azur_lane_setting.divide_list.value)):
            val_key = str(value + 1)
            value = self.azur_lane_setting.divide_list.value[value]
            self.az_div_list.append(
                '%s)%s:\t%s' % (val_key, value['dir'], value['pattern']))

    def able_work(self):
        if not self.able_add:
            self.frame.m_listBox_new.Enable(False)
            self.frame.m_gauge5.Enable(False)
        else:
            self.frame.m_listBox_new.Enable(True)
            self.frame.m_gauge5.Enable(True)


class CryptImage(EncryptImage):
    def __init__(self, frame: noname.MyDialog_Setting):
        super(CryptImage, self).__init__(frame)

    def in_file(self):
        self.frame.m_gauge_file_in.SetValue(0)
        self.dialog = wx.FileDialog(self.frame, "打开", wildcard="*.png",
                                    style=wx.FD_OPEN | wx.FD_CHANGE_DIR | wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST)

        if self.dialog.ShowModal() == wx.ID_OK:
            returned = tools.file_deal(self.dialog.GetPaths(), self.in_show, [], [], self.path,
                                       pattern=r'^.+\.[Pp][Nn][Gg]$')

            if returned:
                self.frame.m_gauge_file_in.SetValue(100)
                self.frame.m_listBox_pic_in.Clear()
                self.frame.m_listBox_pic_in.Set(self.in_show)

    def in_folder(self):
        self.frame.m_gauge_fold_in.SetValue(0)
        self.dialog = wx.DirDialog(self.frame, "打开",
                                   style=wx.DD_CHANGE_DIR | wx.DD_NEW_DIR_BUTTON | wx.DD_DIR_MUST_EXIST)

        if self.dialog.ShowModal() == wx.ID_OK:
            path = function.all_file_path(self.dialog.GetPath())[1]

            returned = tools.file_deal(path, self.in_show, [], [], self.path,
                                       pattern=r'^.+\.[Pp][Nn][Gg]$', is_file=False)

            if returned:
                self.frame.m_gauge_fold_in.SetValue(100)
                self.frame.m_listBox_pic_in.Clear()
                self.frame.m_listBox_pic_in.Set(self.in_show)

    def start(self):
        self.dialog = wx.DirDialog(self.frame, "保存",
                                   style=wx.DD_CHANGE_DIR | wx.DD_NEW_DIR_BUTTON | wx.DD_DIR_MUST_EXIST)
        if self.dialog.ShowModal() == wx.ID_OK:
            thread = Threads.CryptTread(self.in_show, self.frame.m_choice_type_in.GetSelection(), self.path,
                                        self.dialog.GetPath(), self.frame)
            thread.start()
            self.frame.m_button_star_in.Enable(False)


class Add(object):
    def __init__(self, parent: noname.MyDialog_Setting, info: InfoClasses.PerInfoList, names, start_path):
        self.parent = parent
        self.info = info
        self.need_add = InfoClasses.PerInfoList()

        self.finish_num = 0

        self.start_path = start_path

        self.names = names

    def get_new_dic(self):
        return self.names

    def show_info(self):
        self.need_add = self.info.build_no_cn()

        self.parent.m_listBox_new.Set(self.need_add.for_show)

    def open_add_name(self):
        index = self.parent.m_listBox_new.GetSelection()
        value = self.need_add[index]

        writer = FrameClasses.Writer(self.parent, value)
        writer.ShowModal()
        if writer.is_able():
            value = writer.GetValue()
            self.finish_num += 1
            self.need_add.set_self(value.name, value)
            index = self.need_add.get_index(value)

            self.parent.m_listBox_new.SetString(index, self.need_add[index].get_show(index + 1))
        else:
            self.finish_num -= 1

        scale = function.re_int(100 * (self.finish_num / len(self.need_add)))
        self.parent.m_gauge5.SetValue(scale)


class Compare:
    def __init__(self, parent: noname.MyDialog_Setting):
        self.frame = parent
        self.thread = Threads.CompareThread(self)

        self.old_fold = ''
        self.new_fold = ''

        self.old_fold_list = []
        self.new_fold_list = []

        self._new_add = []
        self._new_add_show = []

    def writer_into(self):
        index = self.frame.m_listBox_deffer.GetSelection()

        info = self._new_add[index]

        win32clipboard.OpenClipboard()

        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, info)
        win32clipboard.CloseClipboard()

    def test(self):
        if self.frame.m_dirPicker6.GetPath() != '':
            self.new_fold = self.frame.m_dirPicker6.Path
            self.new_fold_list = function.all_file_path(self.new_fold)
        if self.frame.m_dirPicker_old.GetPath() != '':
            self.old_fold = self.frame.m_dirPicker_old.GetPath()
            self.old_fold_list = function.all_file_path(self.old_fold)

        if self.new_fold != '' and self.old_fold != '':
            self.start()

    def start(self):
        self.thread.start()


class ChangeName:
    def __init__(self, parent: noname.MyDialog_Setting, start_path):
        self.frame = parent

        self.start_path = start_path

        with open("%s\\files\\names.json" % self.start_path, 'r')as file:
            self.names = json.load(file)

        self.info = InfoClasses.PerInfoList()

        self.search = InfoClasses.PerInfoList()

        self.search_list = []
        self.searched = False

    def show_all(self):
        num = 0
        for index in self.names.keys():
            num += 1
            self.info.append_name(index, self.names)
        self.frame.m_listBox_change.Clear()
        self.frame.m_listBox_change.Set(self.info.for_show)

    def change_name(self):
        index = self.frame.m_listBox_change.GetSelection()
        if not self.searched:
            name = self.info[index]
        else:
            name = self.search[index]

        writer = FrameClasses.Writer(self.frame, name)
        writer.ShowModal()
        if writer.is_able():
            value = writer.GetValue()

            self.info.set_self(value.name, value)
            self.search.set_self(value.name, value)

            self.names[value.name] = value.name_cn
            if not self.searched:
                index = self.info.get_index(value)
            else:
                index = self.search.get_index(value)

            self.frame.m_listBox_change.SetString(index, value.get_show(index))

    def searching(self):
        value = self.frame.m_searchCtrl2.GetValue()
        if value != '':
            self.searched = True
            indexes = function.find(value, self.info.for_search)

            self.search = self.info.build_search(indexes)
            self.frame.m_listBox_change.Clear()
            self.frame.m_listBox_change.Set(self.search.for_show)
        else:
            self.searched = False

            self.frame.m_listBox_change.Clear()
            self.frame.m_listBox_change.Set(self.info.for_show)

    def get_change(self):
        return self.names


class FileDropLoad(wx.FileDropTarget):
    def __init__(self, work, parent):
        super(FileDropLoad, self).__init__()
        self.work = work
        self.parent = parent

    def OnDropFiles(self, x, y, filenames):
        try:
            func = functools.partial(self.work.drop_work, filenames)
            thread = threading.Thread(target=func)

            thread.start()
        except:
            return False
        else:
            return True
