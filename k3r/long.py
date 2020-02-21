# -*- coding: utf-8 -*-


from collections import namedtuple
from functools import lru_cache

__author__ = 'Виноградов А.Г. г.Белгород  август 2015'


class Long:
    """Класс работы с длиномерами"""

    def __init__(self, db):
        self.db = db

    def form(self, up):
        """Возвращает форму длиномера
        Входные данные: up - UnitPos в таблице TLongs
        Выходные данные:
        0 - линейная
        1 - дуга по хорде
        2 - два отрезка и дуга
        """
        sql = "SELECT tl.LongTable, te.UnitPos FROM TLongs AS tl LEFT JOIN TElems AS te " \
              "ON tl.UnitPos = te.ParentPos WHERE tl.UnitPos={}".format(up)
        res = self.db.rs(sql)
        table = res[0][0]
        unit_pos = res[0][1] if res[0][1] else up
        sql = "SELECT FormType FROM {0} AS tb WHERE tb.UnitPos={1}".format(table, unit_pos)
        res = self.db.rs(sql)
        if res:
            return res[0][0]
        else:
            return 0

    @lru_cache(maxsize=6)
    def long_list(self, lt=None, tpp=None):
        """Возвращает список длиномеров именованым кортежем
        Входные данные:
        lt - LongType тип длиномера
        tpp - TopParentPos хозяин
        Вывод: 'unitpos', 'type', 'table', 'matid', 'goodsid', 'length', 'width', 'depth', 'cnt', 'form'
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
        keys = ('unitpos', 'type', 'table', 'matid', 'goodsid', 'length', 'width', 'height', 'cnt', 'form')
        filter_lt = "WHERE LongType={}".format(lt) if lt else ""
        pref = " AND" if lt else "WHERE"
        filter_tpp = "{} te.TopParentPos={}".format(pref, tpp) if tpp else ""
        sql = "SELECT tl.UnitPos, tl.LongType AS lt, tl.LongTable, te.PriceID, tl.LongGoodsID, " \
              "te.XUnit, te.YUnit, te.ZUnit, te.Count FROM TLongs AS tl INNER JOIN TElems AS te " \
              "ON tl.UnitPos = te.UnitPos {} ORDER BY tl.LongType".format(filter_lt + filter_tpp)
        res = self.db.rs(sql)
        d_res = []
        for i in res:
            long = namedtuple('Long', keys)
            i += (self.form(i[0]),)
            d_res.append(long(*i))
        return d_res

    @lru_cache(maxsize=6)
    def total(self, lt=None, tpp=None):
        """Суммарное колличество длиномеров согласно единицам измерения материалов
        LongType, LongMatID, Length, LongGoodsID
        Входные данные:
        lt - LongType тип длиномера
        tpp - TopParentPos хозяин
        Вывод: 'type', 'matid', 'length', 'goodsid'
        """
        keys = ('type', 'matid', 'length', 'goodsid')
        longs = self.long_list(lt, tpp)
        nlst = {}
        sc = []
        for i in longs:
            if not i[1:5] in list(nlst.keys()):
                nlst[i[1:5]] = []
            nlst[i[1:5]].append(i[0])
        for i in nlst.items():
            sql_pan = "SELECT Round(Sum([tp].[Length]*[tp].[Width]/10^6*[te].[Count]), 2) AS Cnt FROM TElems AS te " \
                      "INNER JOIN TPanels AS tp ON te.UnitPos = tp.UnitPos WHERE te.ParentPos in {}".format(tuple(i[1]))

            sql_pf = "SELECT Round(Sum([tpf].[Length]/10^3*[te].[Count]), 2) AS Cnt " \
                     "FROM TElems AS te INNER JOIN TProfiles AS tpf ON te.UnitPos = tpf.UnitPos " \
                     "WHERE te.ParentPos in {}".format(tuple(i[1]))

            sql_bl = "SELECT Round(Sum([tbl].[Length]/10^3*[te].[Count]), 2) AS Cnt " \
                     "FROM TElems AS te INNER JOIN TBalusters AS tbl ON te.UnitPos = tbl.UnitPos " \
                     "WHERE tbl.UnitPos in {}".format(tuple(i[1]))

            d_sql = {'TPanels': sql_pan, 'TProfiles': sql_pf, 'TBalusters': sql_bl}
            sql = d_sql[i[0][1]]
            res = self.db.rs(sql)[0][0]
            long = namedtuple('Long', keys)
            sc.append(long(*[i[0][0], i[0][2], res, i[0][3]]))
        return sc

    def long(self):
        pass