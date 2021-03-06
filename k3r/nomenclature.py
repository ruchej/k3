# -*- coding: utf-8 -*-

from collections import namedtuple
from functools import lru_cache
from . import utils

__author__ = "Виноградов А.Г. г.Белгород  август 2015"


class Nomenclature:
    """Класс работы с номенклатурой"""

    def __init__(self, db):

        self.db = db

    @lru_cache(maxsize=6)
    def acc_by_uid(self, uid=None, tpp=None):
        """Выводит список аксессуаров
        uid - int|list id единицы измерения (список)
        tpp = TopParentPos ID верхнего хозяина аксессуара
        Вывод:
            priceid, cnt
        """
        if uid:
            if uid not in (list, tuple):
                uid = (uid,)
            filter_uid = "AND tnn.UnitsID in {}".format(uid)
        else:
            filter_uid = ""
        filter_tpp = "AND te.TopParentPos={}".format(tpp) if tpp else ""
        where = " ".join(["tnn.UnitsID<>11", filter_uid, filter_tpp])
        keys = ("priceid", "cnt")

        sql = (
            "SELECT tnn.ID, SUM(te.Count) AS cnt FROM (TNNomenclature AS tnn RIGHT JOIN TAccessories AS ta "
            "ON tnn.ID = ta.AccMatID) LEFT JOIN TElems AS te ON ta.UnitPos = te.UnitPos "
            "WHERE {0} GROUP BY ID".format(where)
        )
        sql2 = (
            "SELECT ta.AccMatID, Count(ta.AccType) FROM "
            "(SELECT DISTINCT ta.AccMatID, ta.AccType FROM (TNNomenclature AS tnn RIGHT JOIN TAccessories AS ta "
            "ON tnn.ID = ta.AccMatID) LEFT JOIN TElems AS te ON ta.UnitPos = te.UnitPos "
            "WHERE {} ) GROUP BY AccMatID".format(where)
        )
        res = self.db.rs(sql)
        res2 = self.db.rs(sql2)
        if res and res2:
            res2 = dict(res2)
            for i, val in enumerate(res):
                cnt = val[1] / res2[val[0]]
                res[i] = (val[0], cnt)
        l_res = []
        for i in res:
            Ac = namedtuple("Ac", keys)
            l_res.append(Ac(*i))
        return l_res

    def acc_long(self, tpp=None):
        """Список погонажных комплектующих, таких как сетки
        tpp = TopParentPos ID верхнего хозяина аксессуара
        ID, Название, артикль, ед.изм., длина, кол-во, цена
        Вывод:
         priceid - из номенклатуры
         len - длина в мм
         cnt - количество
        """
        filter_tpp = "WHERE te.TopParentPos={}".format(tpp) if tpp else ""
        keys = ("priceid", "len", "cnt")
        sql = (
            "SELECT tnn.ID, te.XUnit, te.Count "
            "FROM TElems AS te INNER JOIN TNNomenclature AS tnn ON te.PriceID = tnn.ID "
            "WHERE te.FurnType Like '07%' {0} ORDER BY te.Name".format(filter_tpp)
        )
        res = self.db.rs(sql)
        l_res = []
        for i in res:
            Ac = namedtuple("Ac", keys)
            l_res.append(Ac(*i))
        l_res = utils.group_by_keys(l_res, ("priceid", "len"), "cnt")
        return l_res

    def mat_by_uid(self, uid=2, tpp=None, mattypeid=None, ex_mtid=None):
        """Выводит список ID материалов
        Keyword arguments:
            uid -- int id единицы измерения
            tpp -- int TopParentPos ID верхнего хозяина материала
            mattypeid -- int|list|tuple Список типов материалов, которые надо включить
            ex_mtid -- int|list|tuple Список типов материалов, которые надо исключить
        Returns:
            [id 1, id 2, ..., id n]
        """
        if mattypeid:
            if type(mattypeid) not in (list, tuple):
                mattypeid = (mattypeid,)
            else:
                mattypeid = tuple(mattypeid)
        if ex_mtid:
            if type(ex_mtid) not in (list, tuple):
                ex_mtid = (ex_mtid,)
            else:
                ex_mtid = tuple(ex_mtid)
        and_tpp = "AND te.TopParentPos={0}".format(tpp) if tpp else ""
        and_mattype = "AND tnn.MatTypeId in {0}".format(mattypeid) if mattypeid else ""
        and_ex_mtid = "AND tnn.MatTypeId not in {0}".format(ex_mtid) if ex_mtid else ""
        where = " ".join(
            ["WHERE tnn.UnitsID={}".format(uid), and_tpp, and_mattype, and_ex_mtid]
        )
        sql = (
            "SELECT tnn.ID FROM TElems AS te INNER JOIN TNNomenclature AS tnn ON te.PriceID = tnn.ID "
            "{} GROUP BY tnn.ID".format(where)
        )

        res = self.db.rs(sql)
        if res:
            ids = []
            for i in res:
                ids.append(i[0])
            return ids
        else:
            return res

    def properties(self, mat_id):
        """Возвращает именованный кортеж свойств номенклатурной единицы
        properties.name
        properties.article
        properties.unitsid
        properties.unitsname
        properties.price
        properties.mattypeid
        properties.
        """
        keys = (
            "priceid",
            "name",
            "article",
            "unitsid",
            "unitsname",
            "price",
            "mattypeid",
        )
        frm = "TNProperties AS tnp INNER JOIN TNPropertyValues AS tnpv ON tnp.ID = tnpv.PropertyID"
        sql1 = (
            "SELECT LCase(tnp.Ident), tnpv.DValue FROM {0} WHERE (tnp.TypeID in (1,7) "
            "AND tnpv.EntityID={1})".format(frm, mat_id)
        )
        sql2 = (
            "SELECT LCase(tnp.Ident), tnpv.IValue FROM {0} WHERE (tnp.TypeID in (3,6,11,17,18) "
            "AND tnpv.EntityID={1})".format(frm, mat_id)
        )
        sql3 = (
            "SELECT LCase(tnp.Ident), tnpv.SValue FROM {0} WHERE (tnp.TypeID in (5,12,13,14,15,16) "
            "AND tnpv.EntityID={1})".format(frm, mat_id)
        )
        sql4 = (
            "SELECT ID, Name, Article, UnitsID, UnitsName, Price, MatTypeID FROM TNNomenclature AS tnn "
            "WHERE tnn.ID={0}".format(mat_id)
        )
        res1 = self.db.rs(sql1)
        res2 = self.db.rs(sql2)
        res3 = self.db.rs(sql3)
        res4 = self.db.rs(sql4)
        if res4:
            res4 = list(zip(keys, self.db.rs(sql4)[0]))
        res = utils.norm_key_prop(res1 + res2 + res3 + res4)
        if res:
            res_keys = dict(res).keys()
            if "wastecoeff" not in res_keys:
                res.append(("wastecoeff", 1))
            if "pricecoeff" not in res_keys:
                res.append(("pricecoeff", 1))
            Prop = namedtuple("Prop", [x[0] for x in res])
            return Prop(**dict(res))
        else:
            return None

    @lru_cache(maxsize=6)
    def property_name(self, mat_id, prop):
        """Получить значение именованного сво-ва
        mat_id - номер материала
        prop - имя свойства
        """
        keys = (
            "id",
            "name",
            "mattypeid",
            "mattypename",
            "groupid",
            "groupname",
            "kindid",
            "kindname",
            "article",
            "unitsid",
            "unitsname",
            "price",
            "parentid",
            "glevel",
        )
        sql1 = (
            "SELECT Switch([tnp].[TypeID]=1,[tnpv].[DValue],[tnp].[TypeID]=3,[tnpv].[IValue],"
            "[tnp].[TypeID]=5,[tnpv].[SValue],[tnp].[TypeID]=6,[tnpv].[IValue],[tnp].[TypeID]=7,[tnpv].[DValue],"
            "[tnp].[TypeID]=11,[tnpv].[IValue],[tnp].[TypeID]=12,[tnpv].[SValue],[tnp].[TypeID]=13,[tnpv].[SValue],"
            "[tnp].[TypeID]=14,[tnpv].[SValue],[tnp].[TypeID]=15,[tnpv].[SValue],[tnp].[TypeID]=16,[tnpv].[SValue],"
            "[tnp].[TypeID]=17,[tnpv].[IValue],[tnp].[TypeID]=18,[tnpv].[IValue]) AS val "
            "FROM TNProperties AS tnp INNER JOIN TNPropertyValues AS tnpv ON tnp.ID = tnpv.PropertyID "
            "WHERE tnpv.EntityID={0} AND tnp.Ident='{1}'".format(mat_id, prop)
        )
        sql2 = "SELECT tnn.{1} FROM TNNomenclature AS tnn WHERE tnn.ID={0}".format(
            mat_id, prop
        )
        if prop in keys:
            sql = sql2
        else:
            sql = sql1
        res = self.db.rs(sql)
        if res:
            return res[0][0]
        else:
            return None

    @lru_cache(maxsize=6)
    def sqm(self, mat_id, tpp=None):
        """Определяем кол-во площадного материала"""

        where = (
            "{0} AND te.TopParentPos={1}".format(mat_id, tpp)
            if tpp
            else "{}".format(mat_id)
        )
        sql = "SELECT Round(Sum((XUnit*YUnit*Count)/10^6), 2) AS sqr FROM TElems AS te WHERE te.PriceID={}".format(
            where
        )
        res = self.db.rs(sql)
        if res:
            return res[0][0]
        else:
            return 0

    def mat_count(self, mat_id, tpp=None):
        """Выводит кол-во материала"""

        cnt = 0
        # Проверим, является ли материал аксессуаром
        sql = "SELECT Count(AccMatID) FROM TAccessories WHERE TAccessories.AccMatID={}".format(
            mat_id
        )
        res = self.db.rs(sql)
        if res:
            if res[0][0] > 0:
                cnt = self.acc_by_uid(mat_id, tpp)
            else:
                unit = self.property_name(mat_id, "UnitsID")
                if unit == 2:  # Квадратные метры
                    cnt = self.sqm(mat_id, tpp)
        return cnt

    def bands(self, add=0, tpp=None, by_thick=True):
        """Информация по кромке.
        Входные данные:
        add - добавочная длина кромки в мм на торец для отходов
        tpp - ID хозяина кромки
        by_thick - разделять по толщине торца
        Выходные данные:
        priceid - ID материала
        len - длина
        thick - толщина торца
        """
        filter_tpp = "WHERE te.TopParentPos={}".format(tpp) if tpp else ""
        keys_by_thick = ("len", "thick", "priceid")
        sql_by_thick = (
            "SELECT Round(Sum((tb.Length+{0})*(te.Count))/10^3, 2), tb.Width, te.PriceID "
            "FROM TBands AS tb INNER JOIN TElems AS te ON tb.UnitPos = te.UnitPos {1} "
            "GROUP BY tb.Width, te.PriceID".format(add, filter_tpp)
        )
        keys_not_thick = ("len", "priceid")
        sql_not_thick = (
            "SELECT Round(Sum((tb.Length+{0})*(te.Count))/10^3, 2), te.PriceID "
            "FROM TBands AS tb INNER JOIN TElems AS te ON tb.UnitPos = te.UnitPos {1} "
            "GROUP BY te.PriceID".format(add, filter_tpp)
        )
        if by_thick:
            sql = sql_by_thick
            keys = keys_by_thick
        else:
            sql = sql_not_thick
            keys = keys_not_thick
        res = self.db.rs(sql)
        l_res = []
        if res:
            for i in res:
                Band = namedtuple("Band", keys)
                l_res.append(Band(*i))
        return l_res

    @lru_cache(maxsize=6)
    def _get_bands(self, tpp=None):
        """Возвращает список имён кромок в заказе"""
        filter_tpp = "WHERE te.TopParentPos={}".format(tpp) if tpp else ""
        sql = (
            "SELECT DISTINCT tnn.Name "
            "FROM (TBands AS tb INNER JOIN TElems AS te ON tb.UnitPos = te.UnitPos) "
            "INNER JOIN TNNomenclature AS tnn ON te.PriceID = tnn.ID {} ORDER BY tnn.Name".format(
                filter_tpp
            )
        )
        res = self.db.rs(sql)
        return [i[0] for i in res]

    @lru_cache(maxsize=6)
    def bands_abc(self, tpp=None):
        """Возвращает словарь буквенных псевдонимов наименований кромок,
        где название кромки это ключ, например:
        {'ПВХ19х0.4 Lamarty Жёлтый': 'A', 'ПВХ19х0.4 Белый': 'B', 'Полировка 4мм': 'C'}
        """

        res = self._get_bands()
        alias = {}
        for i, val in enumerate(res):
            alias.update({val: chr(65 + i)})
        if tpp:
            res = self._get_bands(tpp)
            new_alias = {}
            for key in res:
                new_alias.update({key: alias[key]})
            alias = new_alias
        return alias
