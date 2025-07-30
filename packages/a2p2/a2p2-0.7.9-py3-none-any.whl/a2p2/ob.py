#!/usr/bin/env python

__all__ = []

import logging
import json
import xml.etree.ElementTree as ET
from collections import defaultdict, namedtuple, OrderedDict
import re

import copy


logger = logging.getLogger(__name__)

# https://stackoverflow.com/questions/2148119/how-to-convert-an-xml-string-to-a-dictionary-in-python
# see comment below for our custom mods on attributes naming
def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
        # print("add d=%s"%str(d))
    if t.attrib:
        attrs = {}
        for k, v in t.attrib.items():
            if not "{" in k[0]: # ignore elementName with prefix
                attrs[k]=v
        d[t.tag].update(attrs)
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d

def normalizeObj(obj):
    """
    Modify in place the structure if required.
    Note:
        dict key must be valid identifier (only tested for EXTRA_INFORMATIONS created fields)
    """
    otype=type(obj)
    if otype is dict:
        for k,v in obj.items():

            if k in ['observationConfiguration', 'HAinterval', 'LSTinterval'] and not isinstance(v, list):
                # always defines observationConfiguration as a list
                normalizeObj(v)
                obj[k]=[v]
            elif k=='EXTRA_INFORMATIONS':
                #print(f"Updating dict {k} was : {obj[k]}")
                # normalize input that may have various form on list of dict
                try:
                    fields=[]
                    funits={}
                    for fk in ["parameter","field"]:
                        if fk in obj[k]:
                            l=obj[k][fk].copy()
                            #print(f"'{fk}' => {l}\n({type(l)})\n")
                            if type(l) is dict:
                                fields.append(l)
                            else:
                                fields+=l

                    #print(f"Fields to update: {fields}")
                    #store new fields
                    for vn in fields:
                        fname=vn["name"]
                        # test if we have to normalize field name that will become a python field
                        if not fname.isidentifier():
                            # replace unvalid chars by _ and append F to avoid starting by _
                            fname=re.sub('^_','F_', re.sub('\W|^(?=\d)','_', fname))
                        obj[k][fname]=vn["value"]
                        if "unit" in vn:
                            funits[fname]=vn["unit"]
                    #store units
                    obj[k]["field_units"]=funits
                    # remove old arrays or dicts
                    for fk in ["parameter","field"]:
                        if fk in obj[k]:
                            del obj[k][fk]
                            pass
                except:
                    import traceback
                    print (traceback.format_exc())
                    print(f"\nCan't read {v}")
                    pass
            else:
                normalizeObj(v)
        return obj
    elif otype is list:
        for e in obj:
            normalizeObj(e)
    else:
        pass

class OB():
    """
    Give access to OBs sent by Aspro2 and provide some helper functions.
    You can use attributes to walk to associated configurations values, e.g.:
    - ob.interferometerConfiguration.name
    - ob.instrumentConfiguration
    - ob.observationConfiguration[]
    - ob.observationSchedule

    every values are string (must be converted for numeric values).

    Following fields are converted to list even if the list get a single element. The OB code can then handle such multiples values.
    ['observationConfiguration', 'HAinterval', 'LSTinterval']

    """

    def __init__(self, url):
        # extract XML in elementTree
        e = ET.parse(url)
        # convert data to dict structure
        d = etree_to_dict(e.getroot())
        # keep only content of subelement to avoid schema version change
        # '{http://www.jmmc.fr/aspro-ob/0.1}observingBlockDefinition'
        ds = d[list(d)[0]]  # -> version and name are lost

        #self.srcDict  = copy.deepcopy(ds)
        normalizeObj(ds)
        #self.normDict = ds
        #self.srcObj  = toObject(self.srcDict,inputName="OB")
        #self.normObj  = toObject(self.normDict,inputName="OB")

        # store subelements as attributes
        for e in ds.keys():
            # parse JSON into an object with attributes corresponding to dict keys.
            # We should probably avoid json use...
            o = json.loads(
                json.dumps(ds[e]), object_hook=lambda d: namedtuple(e, d.keys())(*d.values()))
            setattr(self, e, o)

        # store normalized source for str repr
        self.ds = ds

    def as_dict(self):
        return self.ds

    def getFluxes(self, target):
        """
        Return a flux mesurements as dict (ordered dict by BVRIJHK ).
        """
        order = "BVRIJHK"
        fluxes = {}
        els = target._asdict()
        for k in els.keys():
            if k.startswith("FLUX_"):
                fluxes[k[5:]] = els[k]  # remove FLUX_ prefix for dict key

        return OrderedDict(sorted(fluxes.items(), key=lambda t: order.find(t[0])))

    def getPeriod(self):
        """
        Return period given by Aspro2 as integer.
        """
        # use re to remove alpha characters from "Period 109" and make.
        return int(re.sub(r"\D", "", self.interferometerConfiguration.version))


    def get(self, obj, fieldname, defaultvalue=None):
        if fieldname in obj._fields:
            return getattr(obj, fieldname)
        else:
            return defaultvalue

    def __str__(self):
        if True:
            import json
            return json.dumps(self.ds, indent=2)
        else:
            return str(self.ds)
