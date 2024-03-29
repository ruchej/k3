import math
import k3r


class Specific:
    """Получение спецификации"""

    def __init__(self, db):
        self.bs = k3r.base.Base(db)
        self.ln = k3r.long.Long(db)
        self.nm = k3r.nomenclature.Nomenclature(db)
        self.pn = k3r.panel.Panel(db)
        self.pf = k3r.prof.Profile(db)
        self.bs = k3r.base.Base(db)

    def t_sheets(self, tpp=None):
        """Таблица листовыйх материалов
        Входные данные:
            tpp - int TopParentPos id объекта (шкафа)
        Возвращает:
            sqm - количество в кв.м
            ... - набор свойств присущих номенклатурному материалу
        """
        mat_id = self.nm.mat_by_uid(2, tpp, ex_mtid=(48, 99))
        sh = []
        for i in mat_id:
            prop = self.nm.properties(i)
            sqm = self.nm.sqm(i, tpp)
            obj = k3r.utils.tuple_append(prop, {"sqm": sqm}, "Sheets")
            sh.append(obj)
        if sh:
            sh.sort(key=lambda x: [int(x.mattypeid), int(x.thickness)], reverse=True)
        return sh

    def t_glass(self, tpp=None):
        """Таблица стёкло и зеркал
        Входные данные:
            tpp - int TopParentPos id объекта (шкафа)
        Возвращает:
            sqm - количество в кв.м
            ... - набор свойств присущих номенклатурному материалу
        """
        mat_id = self.nm.mat_by_uid(2, tpp, mattypeid=(48, 99))
        sh = []
        for i in mat_id:
            prop = self.nm.properties(i)
            sqm = self.nm.sqm(i, tpp)
            obj = k3r.utils.tuple_append(prop, {"sqm": sqm}, "Sheets")
            sh.append(obj)
        if sh:
            sh.sort(key=lambda x: [int(x.mattypeid), int(x.thickness)], reverse=True)
        return sh

    def t_acc(self, tpp=None, uid=None):
        """Таблица комлпектующих. Не включает погонажные изделия типа сеток
        Возвращает:
            priceid - из номенклатуры
            cnt - количество
            ... - набор свойств присущих номенклатурному материалу
        """
        acc_list = self.nm.acc_by_uid(uid, tpp)
        acc = []
        for i in acc_list:
            prop = self.nm.properties(i.priceid)
            obj = k3r.utils.tuple_append(prop, {"cnt": i.cnt}, "Acc")
            if not hasattr(obj, "supplier"):
                obj = k3r.utils.tuple_append(obj, {"supplier": ""}, "Acc")
            acc.append(obj)
        acc.sort(key=lambda x: [x.supplier, x.name, x.unitsid])
        return acc

    def t_acc_long(self, tpp=None):
        """Таблица погонажных комлпектующих.
        Возвращает:
            priceid - из номенклатуры
            len - длина в мм
            cnt - количество
            ... - набор свойств присущих номенклатурному материалу
        """
        acc_list = self.nm.acc_long(tpp)
        acc = []
        for i in acc_list:
            prop = self.nm.properties(i.priceid)
            obj = k3r.utils.tuple_append(prop, {"len": i.len, "cnt": i.cnt}, "Acc")
            acc.append(obj)
        return acc

    def t_bands(self, add=0, tpp=None, by_thick=True):
        """Таблица кромок
        Входные данные:
           add - добавочная длина кромки в мм на торец для отходов
           tpp - ID хозяина кромки
           by_thick - разделять по толщине торца
       Выходные данные:
           len - длина
           thick - толщина торца
           ... - набор свойств присущих номенклатурному материалу
        """
        bands = self.nm.bands(add, tpp, by_thick)
        t_bands = []
        for i in bands:
            prop = self.nm.properties(i.priceid)
            if by_thick:
                obj = k3r.utils.tuple_append(prop, {"len": i.len, "thick": i.thick})
            else:
                obj = k3r.utils.tuple_append(prop, {"len": i.len})
            t_bands.append(obj)
        return t_bands

    def t_profiles(self, tpp=None):
        """Таблица кусков профилей
        Возвращает:
            priceid - из номенклатуры
            len - длина в метрах
            cnt - количество
            formtype - тип формы профиля
            ... - набор свойств присущих номенклатурному материалу
        """
        pf_list = self.pf.profiles(tpp)
        prof = []
        for i in pf_list:
            prop = self.nm.properties(i.priceid)
            notcutpc = getattr(prop, "notcutpc", 0)
            obj = k3r.utils.tuple_append(
                prop,
                {
                    "len": i.len,
                    "formtype": i.formtype,
                    "notcutpc": notcutpc,
                    "cnt": i.cnt,
                    "elemname": i.elemname,
                },
                "Prof",
            )
            prof.append(obj)
        return prof

    def t_total_prof(self, tpp=None):
        """Таблица профилей
        Возвращает:
            priceid - из номенклатуры
            len - длина в метрах с учётом кратности нарезки
            net_len - длина в местрах в чистом виде
            ... - набор свойств присущих номенклатурному материалу
        """
        pr_list = self.pf.total(tpp)
        prof = []
        for i in pr_list:
            prop = self.nm.properties(i.priceid)
            notcutpc = getattr(prop, "notcutpc", 0)
            stepcut = getattr(prop, "stepcut", 1)
            len = math.ceil(i.len / stepcut) * stepcut
            obj = k3r.utils.tuple_append(
                prop, {"len": len, "net_len": i.len, "notcutpc": notcutpc}, "Prof"
            )
            prof.append(obj)
        return prof

    def t_longs(self, tpp=None):
        """Таблица длиномеров
        Вывод: 'type', 'priceid', 'length', 'width', 'height', 'cnt', 'form
        Типы длиномеров:
            0	Столешница
            1	Карниз
            2	Стеновая панель
            3	Водоотбойник
            4	Профиль карниза
            5	Цоколь
            6	Нижний профиль
            7	Балюстрада
        """
        return self.ln.long_list(tpp)
