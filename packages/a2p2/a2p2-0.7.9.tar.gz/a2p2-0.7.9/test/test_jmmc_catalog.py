#!/usr/bin/env python
# Tested on GITHub/Travis
# on your machine, just run pytest in this directory or execute it to get outputs
#

import pytest

from a2p2.jmmc import Catalog

oidbValidId = 38681

spicaCatName = "spica"
spicaCatName = "spica_2022_03_30"
spicaValidId = 8


class CustomCatalog(Catalog):
    def __init__(self, catalogName, username=None, password=None):
        Catalog.__init__(self, catalogName,username=username, password=password,
#                         apiUrl="https://oidb.jmmc.fr/restxq/catalogs")
#                         apiUrl="https://oidb-beta.jmmc.fr/restxq/catalogs")
                         apiUrl="http://localhost:8080/exist/restxq/catalogs")
#                )


def test_same_id():
    has_same_id("oidb", oidbValidId)


def test_same_id2():
    has_same_id("oidb", oidbValidId)


def has_same_id(catname, id):
    c = CustomCatalog(catname)
    r = c.getRow(id)
    assert r["id"] == id
    print("We are ok with catalog %s id %s" % (catname, id))
    return

def test_protected():
    spica = CustomCatalog(spicaCatName, username="u", password="p")
    try:
        spica.getRow(spicaValidId)
        spicaIsProtected = False
    except:
        spicaIsProtected = True

    assert spicaIsProtected


def test_public():
    oidb = CustomCatalog("oidb")
    try:
        oidb.getRow(oidbValidId)
        oidbIsPublic = True
    except:
        oidbIsPublic = False
    assert oidbIsPublic

def test_simple_update():
    c = CustomCatalog(spicaCatName)
    priority_org = c.getRow(spicaValidId)["priority_pi"]
    v=2
    c.updateRow(spicaValidId, { "priority_pi" : v } )
    priority = c.getRow(spicaValidId)["priority_pi"]
    c.updateRow(spicaValidId, { "priority_pi" : priority_org } )
    assert priority==v

def test_simple_update_with_str_as_json_input():
    c = CustomCatalog(spicaCatName)
    priority_org = c.getRow(spicaValidId)["priority_pi"]
    v=2
    c.updateRow(spicaValidId, '{"priority_pi":%d}'%v)
    priority = c.getRow(spicaValidId)["priority_pi"]
    c.updateRow(spicaValidId, { "priority_pi" : priority_org } )
    assert priority==v


def test_duplicated_col_update():
    c = CustomCatalog(spicaCatName)

    c.updateRow(spicaValidId, {"priority_pi":1, "priority_pi":2})
    priority = c.getRow(spicaValidId)["priority_pi"]
    assert priority==2

    # because sql certainly is case insensitive....
    try:
        c.updateRow(spicaValidId, {"priority_pi":1, "PRIORITY_PI":2})
        assert False
    except:
        pass

def test_reject_bad_col():
    c = CustomCatalog(spicaCatName)
    try:
        c.updateRow(spicaValidId,{"wrong_key":42})
        assert False
    except:
        pass
