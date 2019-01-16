import collections.abc
import functools
import os

import wx


class PerInfo(object):
    def __init__(self, name, name_cn):

        self.tex_path = ''
        self.mesh_path = ''
        self.save_path = ''

        self.lay_in = ''

        self.name = name
        if name == name_cn:
            self.has_cn = False
        else:
            self.has_cn = True

        self.name_cn = name_cn
        self.is_able_work = False

        self.is_skip = False

        self.set_ex_as_cn = True

    def __str__(self):
        return f'Key:{self.name}\n' \
            f'Name:{self.name_cn}\n' \
            f'Tex:{self.tex_path}\n' \
            f'Mesh:{self.mesh_path}\n' \
            f'Save at:{self.save_path}\n'

    def _able_work(self):
        if os.path.exists(self.tex_path) and os.path.exists(self.mesh_path):
            self.is_able_work = True
        else:
            self.is_able_work = False

    def add_tex(self, tex_path):
        self.tex_path = tex_path
        self._able_work()

    def add_mesh(self, mesh_path):
        self.mesh_path = mesh_path
        self._able_work()

    def need_skip(self, path_files: dict):
        keys = path_files.keys()
        files = path_files
        name_cn = self.name_cn + '.png'
        name = self.name + '.png'

        if name_cn in keys:
            self.is_skip = True
            self.lay_in = files[name_cn]
            return True
        elif name in keys:
            self.is_skip = True
            self.lay_in = files[name]
            return True
        else:
            self.is_skip = False
            return False

    def add_save(self, save_path):
        if self.set_ex_as_cn:
            self.save_path = os.path.join(save_path, self.name_cn + ".png")
        else:
            self.save_path = os.path.join(save_path, self.name + ".png")

    def get_show(self, index=0):
        return f'{index}）:{self.name_cn}——{self.name};(@_@)'

    def get_search(self):
        if self.has_cn:
            return f'{self.name}{self.name_cn}'
        else:
            return self.name

    def set_name_cn(self, name):
        if name != self.name_cn and name != '':
            self.name_cn = name
            self.has_cn = True
        else:
            self.has_cn = False

    def update_name(self, names: dict):
        if self.name in names.keys():
            self.name_cn = names[self.name]
        else:
            self.name_cn = self.name

    def rebuild_self(self, value):

        if isinstance(value, PerInfo):
            self.tex_path = value.tex_path
            self.mesh_path = value.mesh_path
            self.save_path = value.save_path

            self.lay_in = value.lay_in

            self.name = value.name

            self.has_cn = value.has_cn
            self.name_cn = value.name_cn
            self.is_able_work = value.is_able_work

            self.is_skip = value.is_skip

            self.set_ex_as_cn = value.set_ex_as_cn

        else:
            raise ValueError


class KeyExistError(KeyError):
    def __init__(self, arg):
        self.arg = arg


class PerInfoList(object):
    def __init__(self, item: collections.abc.Iterable = None):

        self._info_dict = {}

        self._info_key_list = []

        self.for_search = []

        self.for_show = []

        self.start = 0
        self.index = 0

        if isinstance(item, collections.Iterable):
            self.extend(item)

    def __delitem__(self, key):
        if isinstance(key, int):
            key = self._info_key_list[key]
        else:
            pass
        del self._info_dict[key]
        index = self._info_key_list.index(key)
        del self.for_show[index]
        del self.for_search[index]

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._info_dict[self._info_key_list[item]]
        else:
            return self._info_dict[item]

    def __setitem__(self, key: str, value: PerInfo):
        if key in self._info_dict.keys():
            raise KeyExistError("KeyExist!")

        else:
            self._info_dict[key] = value
            self._info_key_list.append(key)
            self.for_show.append(value.get_show(len(self)))
            self.for_search.append(value.get_search())

    def __iter__(self):
        self.index = self.start
        return self

    def __next__(self):
        if self.index >= len(self._info_key_list):
            raise StopIteration
        else:
            val = self._info_dict[self._info_key_list[self.index]]

            self.index += 1

            return val

    def __str__(self):
        return str(list(zip(self._info_key_list, self._info_dict.values())))

    def __len__(self):
        return len(self._info_key_list)

    def __bool__(self):
        if len(self) <= 0:
            return False
        else:
            return True

    def __contains__(self, item):
        if isinstance(item, str):
            return item in self._info_key_list
        if isinstance(item, PerInfo):
            return item in self._info_dict.values()
        else:
            return False

    def is_all_able(self):
        return not bool(self.build_unable())

    def remove(self, item: collections.abc.Iterable):
        return PerInfoList(filter(lambda x: x not in item, self))

    def get_new(self, item: collections.abc.Iterable):
        return PerInfoList(filter(lambda x: x not in self, item))

    def append_name(self, name, names_key):

        if name in names_key.keys():
            name_cn = names_key[name]
        else:
            name_cn = name
        if name not in self._info_dict:
            self[name] = PerInfo(name, name_cn)
        else:
            pass

        return name

    def append_self(self, value):
        if isinstance(value, PerInfo):
            self[value.name] = value
        else:
            raise ValueError(f'{type(value)}is not able')

    def extend(self, values):
        if isinstance(values, collections.Iterable):
            list(map(lambda _x: self.append_self(_x), values))

    def set_tex(self, key, path):
        self._info_dict[key].add_tex(path)

    def set_mesh(self, key, path):
        self._info_dict[key].add_mesh(path)

    def set_save(self, key, path):
        self._info_dict[key].add_save(path)

    def set_self(self, key, value):
        self._info_dict[key].rebuild_self(value)
        index = self.get_index(key)
        value = self._info_dict[key]
        self.for_show[index] = value.get_show(index + 1)
        self.for_search[index] = value.get_search()

    def clear(self):
        self._info_key_list.clear()
        self._info_dict.clear()
        self.for_search.clear()
        self.for_show.clear()

    def get_index(self, value):
        if isinstance(value, PerInfo):
            try:
                return self._info_key_list.index(value.name)
            except ValueError:
                return None
        if isinstance(value, str):
            try:
                return self._info_key_list.index(value)
            except ValueError:
                return None

    def up_date_name_cn(self, name_cn: dict):
        list(map(lambda _x: _x.update_name(name_cn), self))

    def is_in_dict(self, item):
        return item not in self._info_dict.keys()

    def build_no_cn(self):
        val = (filter(lambda _x: not _x.has_cn, self))
        cla = PerInfoList(val)
        return cla

    def build_unable(self):
        val = (filter(lambda _x: not _x.is_able_work, self))
        cla = PerInfoList()

        list(map(lambda _x: cla.append_self(_x), val))

        return cla

    def build_able(self):
        val = (filter(lambda _x: _x.is_able_work, self))
        cla = PerInfoList(val)

        return cla

    def build_no_skip(self, filename):
        val = (filter(lambda _x: not _x.need_skip(filename), self))

        cla = PerInfoList(val)

        return cla

    def build_search(self, indexes):
        val = (map(lambda _x: self[_x], indexes))
        cla = PerInfoList()

        list(map(lambda _x: cla.append_self(_x), val))

        return cla

    def build_skip(self, filename):
        val = (filter(lambda _x: _x.need_skip(filename), self))

        cla = PerInfoList(val)

        return cla


class PerHolder(object):
    def __init__(self, name, val):
        self.name = name
        self.val = val

        self._link_set: collections.Callable = None
        self._link_get: collections.Callable = None

    def __str__(self):
        return f"\n" \
            f"\tclass:PerHolder" \
            f"\tname：{self.name}\n" \
            f"\tval：{self.val}\n" \
            f"\tset_link：{self.set_link}\n" \
            f"\tset_link：{self.get_link}\n"

    @property
    def set_link(self):
        return self._link_set

    @set_link.setter
    def set_link(self, func: collections.abc.Callable):
        if isinstance(func, collections.abc.Callable):
            self._link_set = func

    @property
    def get_link(self):
        return self._link_get

    @get_link.setter
    def get_link(self, func):
        if isinstance(func, collections.abc.Callable):
            self._link_get = func

    @property
    def value(self):
        return self.val

    def set_value(self):
        if isinstance(self.set_link, collections.abc.Callable):
            self.set_link(self.val)

    def get_value(self):
        if isinstance(self.get_link, collections.abc.Callable):
            self.val = self.get_link()


class PattenEdit(PerHolder):
    def __init__(self, name, val):
        super(PattenEdit, self).__init__(name, val)
        if not isinstance(val, list):
            raise TypeError
        self.format_work = lambda x: f'文件夹：{x["dir"]},格式：{x["pattern"]}'
        self._value = list(map(self.format_work, val))

    def __str__(self):
        return f"\n" \
            f"\tclass:PattenEdit\n" \
            f"\tname：{self.name}\n" \
            f"\tval：{self.val}\n" \
            f"\tset_link：{self.set_link}\n" \
            f"\tset_link：{self.get_link}\n"

    def set_value(self):
        if isinstance(self.set_link, collections.abc.Callable):
            self.set_link(self._value)

    def append(self, info_dict):
        index = len(self.val)
        self.val.append(info_dict)
        self._value.append(self.format_work(info_dict))
        return index

    def delete(self, index):
        del self.val[index]
        del self._value[index]

    def move_up(self, index):
        if index > 1:
            temp = self.val[index - 1]
            self.val[index - 1] = self.val[index]
            self.val[index] = temp

            self._value[index - 1] = self.format_work(self.val[index - 1])
            self._value[index] = self.format_work(self.val[index])
            return index - 1
        else:
            return index

    def move_down(self, index):
        if index < len(self.val):
            temp = self.val[index + 1]
            self.val[index + 1] = self.val[index]
            self.val[index] = temp

            self._value[index + 1] = self.format_work(self.val[index + 1])
            self._value[index] = self.format_work(self.val[index])
            return index + 1
        else:
            return index


class SettingHolder(object):
    def __init__(self, setting: dict = None):
        self._sys_dic = {}
        self._sys_list = []
        self.able = []

        if type(setting) is dict:
            self.from_dict(setting)

    def __getattr__(self, item):
        if item in self._sys_list:
            return self._sys_dic[item]
        else:
            raise AttributeError

    def __setattr__(self, key, value):

        if key in ['_sys_list', '_sys_dic', 'able']:
            super(SettingHolder, self).__setattr__(key, value)
        else:
            if key not in self._sys_list:
                self._sys_list.append(key)
                if isinstance(value, list):
                    self._sys_dic[key] = PattenEdit(key, value)
                else:
                    self._sys_dic[key] = PerHolder(key, value)

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __setitem__(self, key, value):
        return self.__setattr__(key, value)

    def __str__(self):
        val = functools.reduce(lambda x, y: f'{x}\n\t{y.name}：{y}', self._sys_dic.values(), f'class:\tSettingHolder')

        return val

    def to_dict(self):
        val = self.__dict__.copy()
        del val['_sys_dic']
        del val['_sys_list']
        return val

    def from_dict(self, setting: dict):
        keys = setting.keys()
        values = setting.values()
        list(map(self.__setattr__, keys, values))

    def link_val(self, key, link_set, link_get):
        if key in self._sys_list:
            self._sys_dic[key].set_link = link_set
            self._sys_dic[key].get_link = link_get

    def link_dict(self, val: dict):
        list(map(lambda x: self.link_val(x, val[x][0], val[x][1]), val.keys()))

    def initial_val(self):
        val = self._sys_list
        list(map(lambda x: self._sys_dic[x].set_value(), val))

    def get_value(self):
        val = self._sys_list
        list(map(lambda x: self._sys_dic[x].get_value(), val))


class TeamWork(object):
    def __init__(self, group_t, *args):
        """

        :param group: set able work
        :param args: else need else work method keys and values
            ->key1=[method1-t,method1-f], key2=[method2-t,method2-f], ...
        """
        self.group_t = group_t

        self.args = args

    def __call__(self, val: bool):
        list(map(lambda x: x.Enable(val), self.group_t))

        if val:
            list(map(lambda x: x[0](), self.args))
        else:
            list(map(lambda x: x[1](), self.args))


class NamesEdit(collections.OrderedDict):
    def __init__(self, names):
        super().__init__(names)

    def __getattr__(self, item):
        if item in self.keys():
            return self[item]
        else:
            raise AttributeError

    def __getitem__(self, item):
        if isinstance(item, str):
            return super(NamesEdit, self).__getitem__(item)
        if isinstance(item, int):
            it = list(self.keys())
            return self[it[item]]

    def __delitem__(self, key):
        if isinstance(key, str):
            super(NamesEdit, self).__delitem__(key)
        if isinstance(key, int):
            it = list(self.keys())
            del self[it[key]]

    def append(self, key, value):
        if key not in self.keys():
            var = wx.MessageBox(f"该键：{key}已经存在了，继续将会覆盖原有值！", '提示', wx.YES_NO)
            if var == wx.YES:
                self[key] = value
        else:
            self[key] = value

    def edit(self, index, value):
        self[index] = value

    def del_name(self, index):
        del self[index]

    def build_show(self):

        return list(map(lambda x: f"key:{x},value：{self[x]}", self.keys()))


if __name__ == '__main__' and False:
    a = PerInfoList()
    d = ['ass', 'asss', 'assss', 'asssss', 'assssss']
    a.append_name('ass', {})
    a.append_name('asss', {})
    a.append_name('assss', {})
    a.append_name('asssss', {})
    a.append_name('assssss', {})

    # for x in a:
    #    print(x)
    print()
    # print(a.for_search)
    # print(a.for_show)
    # print(list(filter(lambda x: x.name[0:2] == "as", a)))
    c = a.build_skip(d, )
    for gg in c:
        print(gg)

if __name__ == '__main__' and False:
    # print(dict == list)
    b = {"open_dir": True, "skip_had": True, "auto_open": True, "finish_exit": False, "clear_list": True,
         "save_all": False, "dir_menu": False, "dir_bg": False}
    a = SettingHolder(b)
    # print(a.to_dict())
    # print(a.__dict__)
    a.skip_had.set_link = lambda x: print(x)
    a.skip_had.get_value()

    print(a.skip_had)
    # print(a)

if __name__ == '__main__':
    n = {'a': 1, 'b': 2, 'n': 3, 'c': 4, 'd': 5, }
    a = NamesEdit(n)
    print(a['a'])
    print(a.build_show())
