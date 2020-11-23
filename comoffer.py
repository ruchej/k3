# -*- coding: cp1251 -*-
__author__ = "���������� �.�. �.��������  ������ 2015"

# ������ ������ ����� "������������ �����������"

import k3
from pyRep.MReports import *
import datetime
import configparser

import time


def detali(namesheet, data=None, tabcolor=1):
    """������ �������� �����������"""
    fnum = "0,00"  # �������� ������
    frub = "# ##0,00_ �."  # �������� ������
    fgen = ""  # ����� ������
    txt = "@"  # ��������� ������
    xlDic = {}  # �������, ���������� ������ ����� �� ������������
    object = data[0]  # id �������, �� ������� ����� �����������
    xldic = data[1]  # ������� ������ �� �������� ���������� �� ����� ������������
    if xldic is None:
        object = None
        unobj = data[0]
    xl.sheetorient = xl.xlconst["xlPortrait"]
    xl.rightmargin = 0.6
    xl.leftmargin = 0.6
    xl.bottommargin = 1.6
    xl.topmargin = 1.6
    xl.centerhorizontally = 0
    xl.new_sheet(namesheet, tabcolor)
    DetTab = [2.4, 50, 5, 5, 5, 6, 10, 10]
    xl.columnsize(1, DetTab)
    nm = Nomenclature(db)
    bs = Base(db)
    pf = Profile(db)
    ln = Longs(db)
    rw = 1
    if object:
        name = bs.telems(object)["Name"]
        article = bs.tobjects(object)[0]["Article"]
        val = (
            "�"
            + namesheet.replace("���.", "")
            + " "
            + name
            + (" ���. " + article if article else "")
        )
        xl.header2(rw, 1, val, 8, halign="c", tc=7, ink=2, tas=3)
        rw += 2
    head = ["�", "������������", "", "", "��.���", "���-��", "����", "���������"]
    xl.header(rw, 1, head, tc=9, tas=0)
    xl.txtformat(rw, 1, "llcccccc")
    rwsumf = rw + 2  # ������ ������ ��� ������� �����
    objcnt = 1
    if object:
        objcnt = bs.telems(object)["Count"]  # ���������� ������ �������
    # --------------------------------------------- ������� �������� ����������
    matid = nm.matbyuid(2, object)
    if matid:
        xl.header2(rw + 1, 1, "�������� ���������", 8, tc=9, ink=2, tas=3)
        rw += 2
        rwgrid = rw
        j = 0
        for i in matid:
            j += 1
            prop = nm.properties(i)
            name = prop["Name"] if not xldic else "=" + xldic[prop["Name"]][0]
            price = eval(prop["Price"]) if not xldic else "=" + xldic[prop["Name"]][1]
            val = [
                j,
                name,
                "",
                "",
                prop["UnitsName"],
                nm.matcount(i, object) / objcnt,
                price,
                "=RC[-2]*RC[-1]",
            ]
            xl.putval(rw, 1, val)
            xl.txtformat(
                rw,
                1,
                "llccrrrr",
                "c",
                "f",
                [fgen, txt, txt, txt, txt, fnum, frub, frub],
            )
            if not xldic:
                xlDic[prop["Name"]] = [
                    ("'" + namesheet + "'" + "!" + xl.num2col(2) + str(rw)),
                    ("'" + namesheet + "'" + "!" + xl.num2col(7) + str(rw)),
                ]
            rw += 1
        xl.gridset(tc=5)
        xl.grid(rwgrid, 1, len(val), rw - rwgrid, "lrudvh")
    # --------------------------------------------- ������� �������������
    acc = nm.accbyuid(tpp=object)
    j = 0
    kompl = False
    if acc:
        xl.header2(rw, 1, "�������������", 8, tc=9, ink=2, tas=3)
        kompl = True
        rw += 1
        rwgrid = rw
        for i in acc:
            j += 1
            name1 = i[1] + (" ���." + i[2] if i[2] else "")
            name = name1 if not xldic else "=" + xldic[name1][0]
            price = i[5] if not xldic else "=" + xldic[name1][1]
            val = [j, name, "", "", i[3], i[4] / objcnt, price, "=RC[-2]*RC[-1]"]
            xl.putval(rw, 1, val)
            xl.txtformat(
                rw, 1, "llccrrrr", "c", "f", [fgen, txt, txt, txt, txt, "", frub, frub]
            )
            if not xldic:
                xlDic[name] = [
                    ("'" + namesheet + "'" + "!" + xl.num2col(2) + str(rw)),
                    ("'" + namesheet + "'" + "!" + xl.num2col(7) + str(rw)),
                ]
            rw += 1
        xl.gridset(tc=5)
        xl.grid(rwgrid, 1, len(val), rw - rwgrid, "lrudvh")
    accl = nm.acclong(tpp=object)
    if accl:
        if not kompl:
            xl.header2(rw, 1, "�������������", 8, tc=9, ink=2, tas=3)
            rw += 1
            rwgrid = rw
        for i in accl:
            j += 1
            name1 = i[1] + (" ���." + i[2] if i[2] else "")
            name = name1 if not xldic else "=" + xldic[name1][0]
            price = i[6] if not xldic else "=" + xldic[name1][1]
            val = [
                j,
                name,
                i[3],
                i[4] / objcnt,
                "��",
                i[5],
                price,
                "=RC[-4]*RC[-2]*RC[-1]",
            ]
            xl.putval(rw, 1, val)
            xl.txtformat(
                rw, 1, "llccrrrr", "c", "f", [fgen, txt, txt, fnum, txt, "", frub, frub]
            )
            if not xldic:
                xlDic[name] = [
                    ("'" + namesheet + "'" + "!" + xl.num2col(2) + str(rw)),
                    ("'" + namesheet + "'" + "!" + xl.num2col(7) + str(rw)),
                ]
            rw += 1
        xl.gridset(tc=5)
        xl.grid(rwgrid, 1, len(val), rw - rwgrid, "lrudvh")
    # --------------------------------------------- ������� ��������
    prof = pf.sumcount(tpp=object)
    if prof:
        xl.header2(rw, 1, "�������", 8, tc=9, ink=2, tas=3)
        rw += 1
        rwgrid = rw
        j = 0
        for i in prof:
            j += 1
            prop = nm.properties(i[0])
            name1 = prop["Name"] + (
                " ���." + prop["Article"] if prop["Article"] else ""
            )
            name = name1 if not xldic else "=" + xldic[name1][0]
            price = eval(prop["Price"]) if not xldic else "=" + xldic[name1][1]
            val = [
                j,
                name,
                "",
                "",
                prop["UnitsName"],
                (i[1] / 10 ** 3) / objcnt,
                price,
                "=RC[-2]*RC[-1]",
            ]
            xl.putval(rw, 1, val)
            xl.txtformat(
                rw,
                1,
                "llccrrrr",
                "c",
                "f",
                [fgen, txt, txt, txt, txt, fnum, frub, frub],
            )
            if not xldic:
                xlDic[name] = [
                    ("'" + namesheet + "'" + "!" + xl.num2col(2) + str(rw)),
                    ("'" + namesheet + "'" + "!" + xl.num2col(7) + str(rw)),
                ]
            rw += 1
        xl.gridset(tc=5)
        xl.grid(rwgrid, 1, len(val), rw - rwgrid, "lrudvh")

    # --------------------------------------------- ������� ����������
    longs = ln.sumcount(tpp=object)
    # ��������� �� ���������� �������� � ������ ��������, ����� �� �������
    for i in range(len(longs)):
        for j in longs:
            if j[1] in matid:
                ix = longs.index(j)
                del longs[ix]
    if longs:
        xl.header2(rw, 1, "���������", 8, tc=9, ink=2, tas=3)
        rw += 1
        rwgrid = rw
        j = 0
        for i in longs:
            j += 1
            prop = nm.properties(i[1])
            tng = bs.tngoods(i[3])[0]
            name0 = tng["GroupName"] + " " + tng["Name"] + " "
            name1 = (
                name0
                + prop["Name"]
                + (" ���." + prop["Article"] if prop["Article"] else "")
            )
            name = name1 if not xldic else "=" + xldic[name1][0]
            price = eval(prop["Price"]) if not xldic else "=" + xldic[name1][1]
            val = [j, name, "", "", prop["UnitsName"], i[2], price, "=RC[-2]*RC[-1]"]
            xl.putval(rw, 1, val)
            xl.txtformat(
                rw,
                1,
                "llccrrrr",
                "c",
                "f",
                [fgen, txt, txt, txt, txt, fnum, frub, frub],
            )
            if not xldic:
                xlDic[name] = [
                    ("'" + namesheet + "'" + "!" + xl.num2col(2) + str(rw)),
                    ("'" + namesheet + "'" + "!" + xl.num2col(7) + str(rw)),
                ]
            rw += 1
        xl.gridset(tc=5)
        xl.grid(rwgrid, 1, len(val), rw - rwgrid, "lrudvh")

    # --------------------------------------------- ������� ������
    bands = nm.bands(tpp=object)
    if bands:
        xl.header2(rw, 1, "������", 8, tc=9, ink=2, tas=3)
        rw += 1
        head = ["�", "������", "", "�-��", "�-��", "�.���.", "����", "���������"]
        xl.header(rw, 1, head, tc=9, tas=0)
        xl.txtformat(rw, 1, "llc")
        rw += 1
        rwgrid = rw
        j = 0
        for i in bands:
            j += 1
            prop = nm.properties(i[2])
            name1 = prop["Name"] + (
                " ���." + prop["Article"] if prop["Article"] else ""
            )
            name = name1 if not xldic else "=" + xldic[name1][0]
            price = eval(prop["Price"]) if not xldic else "=" + xldic[name1][1]
            val = [
                j,
                name,
                "",
                i[1],
                (i[0] / 10 ** 3) / objcnt,
                eval(prop.get("WasteCoeff", "1")),
                price,
                "=RC[-3]*RC[-2]*RC[-1]",
            ]
            xl.putval(rw, 1, val)
            xl.txtformat(
                rw,
                1,
                "llccrrrr",
                "c",
                "f",
                [fgen, txt, txt, "", fnum, fnum, frub, frub],
            )
            if not xldic:
                xlDic[name] = [
                    ("'" + namesheet + "'" + "!" + xl.num2col(2) + str(rw)),
                    ("'" + namesheet + "'" + "!" + xl.num2col(7) + str(rw)),
                ]
            rw += 1
        xl.gridset(tc=5)
        xl.grid(rwgrid, 1, len(val), rw - rwgrid, "lrudvh")
    rwsume = rw - 1  # ��������� ������ ��� ������� �����
    cells = xl.num2col(8) + str(rwsumf) + ":" + xl.num2col(8) + str(rwsume)
    xl.header(rw + 1, 7, ["�����:", "=SUM({})".format(cells)], tc=10, tas=0)
    unobj = unobj if object is None else object
    prlst[unobj] = "'" + namesheet + "'" + "!" + xl.num2col(8) + str(rw + 1)

    return xlDic


def kompred(xlDic, tabcolor=1):
    """�������� ������������� �����������"""
    fnum = "0,00"  # �������� ������
    frub = "# ##0_ �."  # �������� ������
    fgen = ""  # ����� ������
    txt = "@"  # ��������� ������
    xl.sheetorient = xl.xlconst["xlLandscape"]
    xl.rightmargin = 0.6
    xl.leftmargin = 0.6
    xl.bottommargin = 1.6
    xl.topmargin = 1.6
    xl.centerhorizontally = 0
    xl.new_sheet("��", tabcolor)
    DetTab = [6.5, 21, 35.6, 10, 6.57, 11, 44, 11, 6]
    xl.columnsize(1, DetTab)
    rw = 1
    # �������� �����
    nm = Nomenclature(db)
    bs = Base(db)
    pf = Profile(db)
    ln = Longs(db)
    firm = bs.torderinfo()["Firm"]
    try:
        conf = configparser.SafeConfigParser()
        conf.read(datafile)
        datafirm = firm + "\n" + conf.get(firm, "str")
        logo = conf.get(firm, "logo")
        xl.mergecells(rw, 1, 7)
        xl.putval(rw, 1, datafirm)
        xl.rowsize(rw, 63)
        logopath = os.path.join(reportpath, logo)
        xl.picinsert(rw, 7, 1, 1, logopath, hor="r", ver="c")
        rw += 1
    except:
        pass
    head = "������������ ����������� �� {}".format(
        datetime.date.today().strftime("%d.%m.%Y")
    )
    xl.header(rw, 1, head, tc=1, tas=0)
    xl.mergecells(rw, 1, 7, 1)
    xl.gridset(wt="xlMedium", tc=5)
    xl.grid(1, 1, 7, 2, "lrudh")
    rw += 2
    head = [
        "� �/�",
        "�������",
        "����������� ��������",
        "����",
        "���-��",
        "���������",
        "�����",
        "�-���",
        3,
    ]
    xl.header(rw, 1, head, tas=0)
    xl.txtformat(rw, 1, "ccccccclc")
    k = "=" + xl.num2col(9) + str(rw)
    rw += 1
    j = 0
    price = "=RC[4]*RC[5]"
    sumcost = "=RC[-2]*RC[-1]"
    rwsumf = rw  # ������ ������ ��� ������� �����
    picxy = {}  # ������� ��������� ����� ��� ������� ��������
    for i in lstobj:
        j += 1
        up = i[0]
        iobj = bs.tobjects(up)[0]
        elems = bs.telems(up)
        name = elems["Name"] + (" ���." + iobj["Article"] if iobj["Article"] else "")
        cnt = elems["Count"]
        cost = "=" + prlst[up]
        tech_over = (
            '="'
            + "������ (�����) "
            + str(round(elems["XUnit"]))
            + "x"
            + str(round(elems["YUnit"]))
            + "x"
            + str(round(elems["ZUnit"]))
            + " ��"
            + '; "'
        )
        # ��������� � �������� ���������
        matid = nm.matbyuid(2, up)
        if matid:
            tech_over += '&"���������: "'
            for i in matid:
                prop = nm.properties(i)
                if prop.get("NoKP") != 1:
                    title = prop["Name"]
                    adr = xlDic[title][0]
                    tech_over += "&" + 'IF(OFFSET({0},0,-1)>0,{0}&"; ","")'.format(adr)
        # ��������� � �������� �������������
        acc = nm.accbyuid(tpp=up)
        kompl = False
        if acc:
            kompl = True
            tech_over += '&"�������������: "'
            for i in acc:
                prop = nm.properties(i[0])
                if prop.get("NoKP") != 1:
                    title = i[1] + (" ���." + i[2] if i[2] else "")
                    adr = xlDic[title][0]
                    tech_over += "&" + 'IF(OFFSET({0},0,-1)>0,{0}&"; ","")'.format(adr)
        accl = nm.acclong(tpp=up)
        if accl:
            if not kompl:
                tech_over += '&"�������������: "'
            for i in accl:
                prop = nm.properties(i[0])
                if prop.get("NoKP") != 1:
                    title = i[1] + (" ���." + i[2] if i[2] else "")
                    adr = xlDic[title][0]
                    tech_over += "&" + 'IF(OFFSET({0},0,-1)>0,{0}&"; ","")'.format(adr)

        # ��������� � �������� �������
        prof = pf.sumcount(tpp=up)
        if prof:
            tech_over += '&"�������: "'
            for i in prof:
                prop = nm.properties(i[0])
                if prop.get("NoKP") != 1:
                    title = prop["Name"] + (
                        " ���." + prop["Article"] if prop["Article"] else ""
                    )
                    adr = xlDic[title][0]
                    tech_over += "&" + 'IF(OFFSET({0},0,-1)>0,{0}&"; ","")'.format(adr)

        # ��������� � �������� ���������
        longs = ln.sumcount(tpp=up)
        # ��������� �� ���������� �������� � ������ ��������, ����� �� �������
        for i in range(len(longs)):
            for ji in longs:
                if ji[1] in matid:
                    ix = longs.index(ji)
                    del longs[ix]
        if longs:
            tech_over += '&"���������: "'
            for i in longs:
                prop = nm.properties(i[1])
                tng = bs.tngoods(i[3])[0]
                name0 = tng["GroupName"] + " " + tng["Name"] + " "
                title = (
                    name0
                    + prop["Name"]
                    + (" ���." + prop["Article"] if prop["Article"] else "")
                )
                adr = xlDic[title][0]
                tech_over += "&" + 'IF(OFFSET({0},0,-1)>0,{0}&"; ","")'.format(adr)

        # ��������� � �������� ������
        bands = nm.bands(tpp=up)
        if bands:
            tech_over += '&"������: "'
            for i in bands:
                prop = nm.properties(i[2])
                if prop.get("NoKP") != 1:
                    title = prop["Name"] + (
                        " ���." + prop["Article"] if prop["Article"] else ""
                    )
                    adr = xlDic[title][0]
                    tech_over += "&" + 'IF(OFFSET({0},0,-1)>0,{0}&"; ","")'.format(adr)

        val = [j, name, tech_over, price, cnt, sumcost, "", cost, k]
        xl.putval(rw, 1, val)
        picxy[up] = [rw, 7]
        xl.txtformat(
            rw,
            1,
            "rllrrrrrr",
            "cttc",
            "ft",
            [fgen, txt, txt, frub, fgen, frub, fgen, frub, fgen],
        )
        rowheight = xl.wb.ActiveSheet.Rows(rw).RowHeight
        if rowheight < 200:
            xl.wb.ActiveSheet.Rows(rw).RowHeight = 200
        rwsume = rw  # ��������� ������ ��� ������� �����
        rw += 1

    xl.gridset(tc=5)
    xl.grid(rwsumf, 1, len(val), rw - rwsumf, "lrudvh")
    cells = xl.num2col(6) + str(rwsumf) + ":" + xl.num2col(6) + str(rwsume)
    xl.header(rw + 1, 4, ["�����:", "", "=SUM({})".format(cells)], tc=10, tas=0)
    cells = xl.num2col(8) + str(rwsumf) + ":" + xl.num2col(8) + str(rwsume)
    xl.header(rw + 1, 8, ["=SUM({})".format(cells)], tc=10, tas=0)
    # ������� ��� �������� � ���� ������
    for i in bs.tdrawings():
        file = i["DrawingName"]
        up = i["UnitPos"]
        row = picxy[up][0]
        column = picxy[up][1]
        pict = os.path.join(projreppath, file)
        xl.picinsert(row, column, 1, 1, pict)
    xl.printarea(1, 1, 7, rw + 1)


def start():
    xldic = detali("�-��", [obj[0]["UnitPos"], None], 7)
    objcount = 1
    if len(obj) > 1:
        for i in lstobj:
            up = i[0]
            shname = "�." + str(objcount)
            shname = shname[:31]
            detali(shname, [up, xldic])
            endsheet = shname
            objcount += 1
    tmp = kompred(xldic, tabcolor=7)
    if len(obj) > 1:
        xl.movesheet("�-��", endsheet)
    xl.save(os.path.join(projreppath, "������������ �����������"))


if __name__ == "__main__":
    # file = (r'D:\PKMProjects73\12\12.mdb')
    # datafile = (r"c:\Program Files (86)\GeoS\K3-������ ��� 7.3\Bin\Reports\PyReports\FirmInfo.ini")
    starttime = time.time()
    params = k3.getpar()
    file = params[0]
    datafile = params[1]
    projpath = os.path.dirname(file)
    reportpath = os.path.dirname(datafile)
    projreppath = os.path.join(projpath, "Reports")
    db = DB()
    tmp = db.connect(file)  # ������������ � ���� ��������
    if tmp == "NoFile":
        print("������ ����������� � ���� ������")
        raise SystemExit(1)

    xl = ExcelDoc()  # ������ ������ excel
    xl.Excel.Application.ScreenUpdating = False
    prlst = {}  # ������� ������ �� ������ �������� ����
    nm = Nomenclature(db)
    bs = Base(db)
    obj = bs.tobjects()
    lstobj = []
    for i in obj:
        up = i["UnitPos"]
        pos = eval(bs.tattributes(up)["Position"])
        lstobj.append([up, pos])
    lstobj = sorted(lstobj, key=lambda x: x[::-1])
    try:
        start()
    except:
        print("��������� ������ �� ����� �������� ������")
    xl.Excel.Application.ScreenUpdating = True
    xl.Excel.Visible = 1
    db.disconnect()
    endtime = time.time()
    print(endtime - starttime)
