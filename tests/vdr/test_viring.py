# -*- encoding: utf-8 -*-
"""
tests.db.dbing module

"""
import json
import os

import lmdb

from keri.core.coring import Diger, Versify, Serials
from keri.db.dbing import openLMDB, dgKey, snKey
from keri.vdr.viring import Issuer, regKey, vcKey


def test_issuer():
    """
    Test Issuer Class
    """
    issuer = Issuer()

    assert isinstance(issuer, Issuer)
    assert issuer.name == "main"
    assert issuer.temp is False
    assert isinstance(issuer.env, lmdb.Environment)
    assert issuer.path.endswith("keri/db/main")
    assert issuer.env.path() == issuer.path
    assert os.path.exists(issuer.path)

    assert isinstance(issuer.tvts, lmdb._Database)

    issuer.close(clear=True)
    assert not os.path.exists(issuer.path)
    assert not issuer.opened

    # test not opened on init
    issuer = Issuer(reopen=False)
    assert isinstance(issuer, Issuer)
    assert issuer.name == "main"
    assert issuer.temp is False
    assert issuer.opened is False
    assert issuer.path is None
    assert issuer.env is None

    issuer.reopen()
    assert issuer.opened
    assert issuer.path is not None
    assert isinstance(issuer.env, lmdb.Environment)
    assert issuer.path.endswith("keri/db/main")
    assert issuer.env.path() == issuer.path
    assert os.path.exists(issuer.path)

    issuer.close(clear=True)
    assert not os.path.exists(issuer.path)
    assert not issuer.opened

    assert isinstance(issuer.tvts, lmdb._Database)

    with openLMDB(cls=Issuer) as issuer:
        assert isinstance(issuer, Issuer)
        assert issuer.name == "test"
        assert issuer.temp is True
        assert isinstance(issuer.env, lmdb.Environment)
        assert issuer.path.startswith("/tmp/keri_lmdb_")
        assert issuer.path.endswith("_test/keri/db/test")
        assert issuer.env.path() == issuer.path
        assert os.path.exists(issuer.path)

        assert isinstance(issuer.tvts, lmdb._Database)

    assert not os.path.exists(issuer.path)

    ipreb = "DYmJApMvMb8mgiG20BPlPcKLWSfNIUCC21DP0i2_BLjo".encode("utf-8")
    regb = "EOWdT7a7fZwRz0jiZ0DJxZEM3vsNbLDPEUk-ODnif3O0".encode("utf-8")
    rarb = "BijzaUuRMwh1ivT5BQrqNhbvx82lB-ofrHVHjL3WADbA".encode("utf-8")

    #  test with registry inception (vcp) event
    regk = regKey(ipreb, regb)
    assert regk == b'DYmJApMvMb8mgiG20BPlPcKLWSfNIUCC21DP0i2_BLjo:EOWdT7a7fZwRz0jiZ0DJxZEM3vsNbLDPEUk-ODnif3O0'
    sn = 0
    vs = Versify(kind=Serials.json, size=20)

    vcp = dict(v=vs, i=regk.decode("utf-8"),
               s="{:x}".format(sn), b=[rarb.decode("utf-8")],
               t="vcp")

    vcpb = json.dumps(vcp, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    assert vcpb == (b'{"v":"KERI10JSON000014_",'
                    b'"i":"DYmJApMvMb8mgiG20BPlPcKLWSfNIUCC21DP0i2_BLjo:EOWdT7a7fZwRz0jiZ0DJxZEM3vsNbLDPEUk-ODnif3O0",'
                    b'"s":"0","b":["BijzaUuRMwh1ivT5BQrqNhbvx82lB-ofrHVHjL3WADbA"],"t":"vcp"}')
    vdig = Diger(ser=vcpb)


    with openLMDB(cls=Issuer) as issuer:
        key = dgKey(regk, vdig.qb64b)

        assert issuer.getTvt(key) is None
        assert issuer.delTvt(key) is False
        assert issuer.putTvt(key, val=vcpb) is True
        assert issuer.getTvt(key) == vcpb
        assert issuer.putTvt(key, val=vcpb) is False
        assert issuer.setTvt(key, val=vcpb) is True
        assert issuer.getTvt(key) == vcpb
        assert issuer.delTvt(key) is True
        assert issuer.getTvt(key) is None

        telKey = snKey(regk, sn)
        assert issuer.getTel(telKey) is None
        assert issuer.delTel(telKey) is False
        assert issuer.putTel(telKey, val=vdig.qb64b)
        assert issuer.getTel(telKey) == vdig.qb64b
        assert issuer.putTel(telKey, val=vdig.qb64b) is False
        assert issuer.setTel(telKey, val=vdig.qb64b) is True
        assert issuer.getTel(telKey) == vdig.qb64b
        assert issuer.delTel(telKey) is True
        assert issuer.getTel(telKey) is None

        coupl01 = ("BPVuWC4Hc0izqPKn2LIwhp72SHJSRgfaL1RhtuiavIy4AAfiKvopJ0O2afOmxb5A6JtdY7Wkl_1uNx1Z8xQkg_"
                   "gMzf-vTfEHDylFdgn2e_u_ppaFajIdvEvONX6dcSYzlfBQ").encode("utf-8")
        coupl02 = ("BW1gbapuOJ4TJKwLfKZs5cXEIs9k8EtBqxR1psVxnD7IABrSkjrgPGXdhBiOy6LUZpiqtsHkKHhfLGj_LhT1n6"
                   "EqCIdDjrihzrdM1bm0ZNJDwbDGXoeeZujd7ZYsOsBPzRCw").encode("utf-8")
        coupl03 = ("BklrMm7GlYzNrPQunLJHFn_1wWjlUslGkXfs0KyoNOEAAC_6PB5Zre_E_7YLkM9OtRo-uYmwRyFmOH3Xo4JDiP"
                   "jioY7Ycna6ouhSSH0QcKsEjce10HCXIW_XtmEYr9SrB5BA").encode("utf-8")
        coups = [coupl01, coupl02, coupl03]

        key = dgKey(regk, vdig.qb64b)
        assert issuer.getTibs(key) == []
        assert issuer.cntTibs(key) == 0
        assert issuer.delTibs(key) is False
        assert issuer.putTibs(key, vals=[coupl01]) is True
        assert issuer.getTibs(key) == [coupl01]
        assert issuer.cntTibs(key) == 1
        assert issuer.putTibs(key, vals=[coupl01]) is True  # add duplicate
        assert issuer.cntTibs(key) == 1
        assert issuer.addTib(key, coupl01) is False
        assert issuer.addTib(key, coupl02) is True
        assert issuer.cntTibs(key) == 2
        assert issuer.putTibs(key, vals=[coupl02, coupl03]) is True
        assert issuer.cntTibs(key) == 3
        assert issuer.delTibs(key) is True
        assert issuer.getTibs(key) == []
        for c in coups:
            assert issuer.addTib(key, c) is True
        assert issuer.cntTibs(key) == 3
        assert issuer.getTibs(key) == [coupl01, coupl02, coupl03]
        for c in issuer.getTibsIter(key):
            assert issuer.delTibs(key, c) is True
        assert issuer.getTibs(key) == []

        tweKey = snKey(regk, sn)
        assert issuer.getTwe(tweKey) is None
        assert issuer.delTwe(tweKey) is False
        assert issuer.putTwe(tweKey, val=vdig.qb64b)
        assert issuer.getTwe(tweKey) == vdig.qb64b
        assert issuer.putTwe(tweKey, val=vdig.qb64b) is False
        assert issuer.setTwe(tweKey, val=vdig.qb64b) is True
        assert issuer.getTwe(tweKey) == vdig.qb64b
        assert issuer.delTwe(tweKey) is True
        assert issuer.getTwe(tweKey) is None

        quad01 = ("DYmJApMvMb8mgiG20BPlPcKLWSfNIUCC21DP0i2_BLjo"
                  "0AAAAAAAAAAAAAAAAAAAAABA"
                  "rot"
                  "Ezpq06UecHwzy-K9FpNoRxCJp2wIGM9u2Edk-PLMZ1H4").encode("utf-8")
        quad02 = ("DYmJApMvMb8mgiG20BPlPcKLWSfNIUCC21DP0i2_BLjo"
                  "0AAAAAAAAAAAAAAAAAAAAABg"
                  "rot"
                  "EOWdT7a7fZwRz0jiZ0DJxZEM3vsNbLDPEUk-ODnif3O0").encode("utf-8")
        quad03 = ("DYmJApMvMb8mgiG20BPlPcKLWSfNIUCC21DP0i2_BLjo"
                  "0AAAAAAAAAAAAAAAAAAAAABw"
                  "rot"
                  "EXvR3p8V95W8J7Ui4-mEzZ79S-A1esAnJo1Kmzq80Jkc").encode("utf-8")
        quads = [quad01, quad02, quad03]

        key = dgKey(regk, vdig.qb64b)
        assert issuer.getAncs(key) == []
        assert issuer.cntAncs(key) == 0
        assert issuer.delAncs(key) is False
        assert issuer.putAncs(key, vals=[quad01]) is True
        assert issuer.getAncs(key) == [quad01]
        assert issuer.cntAncs(key) == 1
        assert issuer.putAncs(key, vals=[quad01]) is True  # add duplicate
        assert issuer.cntAncs(key) == 1
        assert issuer.addAnc(key, quad01) is False
        assert issuer.addAnc(key, quad02) is True
        assert issuer.cntAncs(key) == 2
        assert issuer.putAncs(key, vals=[quad02, quad03]) is True
        assert issuer.cntAncs(key) == 3
        assert issuer.delAncs(key) is True
        assert issuer.getAncs(key) == []
        for c in quads:
            assert issuer.addAnc(key, c) is True
        assert issuer.cntAncs(key) == 3
        assert issuer.getAncs(key) == [quad01, quad02, quad03]
        for c in issuer.getAncsIter(key):
            assert issuer.delAncs(key, c) is True
        assert issuer.getAncs(key) == []

        #  test with verifiable credential issuance (iss) event
        vcdig = b'EXvR3p8V95W8J7Ui4-mEzZ79S-A1esAnJo1Kmzq80Jkc'
        vck = vcKey(ipreb, regb, vcdig)
        assert vck == (b'DYmJApMvMb8mgiG20BPlPcKLWSfNIUCC21DP0i2_BLjo:EOWdT7a7fZwRz0jiZ0DJxZEM3vsNbLDPEUk-ODnif3O0'
                       b':EXvR3p8V95W8J7Ui4-mEzZ79S-A1esAnJo1Kmzq80Jkc')
        sn = 0
        vs = Versify(kind=Serials.json, size=20)

        vcp = dict(v=vs, i=vck.decode("utf-8"),
                   s="{:x}".format(sn),
                   t="iss")

        issb = json.dumps(vcp, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        assert issb == (b'{"v":"KERI10JSON000014_",'
                        b'"i":"DYmJApMvMb8mgiG20BPlPcKLWSfNIUCC21DP0i2_BLjo:'
                        b'EOWdT7a7fZwRz0jiZ0DJxZEM3vsNbLDPEUk-ODnif3O0:EXvR3p8V95W8J7Ui4-mEzZ79S-A1esAnJo1Kmzq80Jkc",'
                        b''b'"s":"0","t":"iss"}')
        idig = Diger(ser=issb)

        key = dgKey(vck, idig.qb64b)
        assert issuer.getTvt(key) is None
        assert issuer.delTvt(key) is False
        assert issuer.putTvt(key, val=issb) is True
        assert issuer.getTvt(key) == issb
        assert issuer.putTvt(key, val=issb) is False
        assert issuer.setTvt(key, val=issb) is True
        assert issuer.getTvt(key) == issb
        assert issuer.delTvt(key) is True
        assert issuer.getTvt(key) is None

        telKey = snKey(vck, sn)
        assert issuer.getTel(telKey) is None
        assert issuer.delTel(telKey) is False
        assert issuer.putTel(telKey, val=idig.qb64b)
        assert issuer.getTel(telKey) == idig.qb64b
        assert issuer.putTel(telKey, val=idig.qb64b) is False
        assert issuer.setTel(telKey, val=idig.qb64b) is True
        assert issuer.getTel(telKey) == idig.qb64b
        assert issuer.delTel(telKey) is True
        assert issuer.getTel(telKey) is None



    """End Test"""


if __name__ == "__main__":
    test_issuer()
