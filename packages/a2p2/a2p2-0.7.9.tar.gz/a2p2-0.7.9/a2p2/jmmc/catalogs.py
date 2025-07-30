#!/usr/bin/env python

__all__ = []

import logging

import pyvo
import astropy.table.table

from ..client import A2P2ClientPreferences

from .utils import JmmcAPI
from . import PRODLABEL

logger = logging.getLogger(__name__)


class Catalog():
    """ Get remote access to read and update catalogs exposed through JMMC's API.
        Credential can be explicitly given for method that require an authentication, else:
        - a2p2 preferences login will be used if present (see a2p2 -c)
        - or uses .netrc file
        A where clause can be added to limit on rows of interest (adql syntax)
        A joins list of dictionnary can be provided to combine this catalog to other ones ( format is: [{"name":"cattojoin","id":"commonkey"},...] )
    """

    def __init__(self, catalogName, username=None, password=None, prod=False, apiUrl=None, tapUrl=None, where=None, joins=None):
        self.catalogName = catalogName
        self.updated = False
        self.lastTable = None
        self.lastDataFrame = None
        self.where = where
        self.joins = joins
        self.prod = prod
        self.colDelimiterName = "coldelimiter___"

        # Manage prod & preprod or user provided access points
        if apiUrl:
            self.apiUrl = apiUrl  # trust given url as catalogAPI if value is provided
        if tapUrl:
            self.tapUrl = tapUrl  # trust given url as TAP server if value is provided

        if not(apiUrl):
            if self.prod:
                self.apiUrl = "https://oidb.jmmc.fr/restxq/catalogs"
            else:
                self.apiUrl = "https://oidb-beta.jmmc.fr/restxq/catalogs"

        if not(tapUrl):
            if self.prod:
                self.tapUrl = "https://tap.jmmc.fr/vollt/tap"
            else:
                self.tapUrl = "https://tap-preprod.jmmc.fr/vollt/tap"

        self.tap = pyvo.dal.TAPService(self.tapUrl)
        self.api = JmmcAPI(self.apiUrl, username, password)

        logger.info(f"Create catalog wrapper to access '{catalogName}' ({PRODLABEL[self.prod]} API at {self.api.rootURL})")

    def list(self):
        """ Get list of exposed catalogs on API associated to this catalog. """
        return self.api._get("")

    def metadata(self):
        """ Get catalog metadata"""
        return self.api._get(f"/meta/{self.catalogName}")

    def pis(self):
        """ Get PIs from catalog and check for associated JMMC login in OiDB datapi table."""
        return self.api._get(f"/accounts/{self.catalogName}")["pi"]

    def piname(self, jmmcLogin=None):
        """ Get the piname associated to the given jmmcLogin.
            If jmmcLogin parameter is not provided, try to get jmmc.login preferences.
            Only pi names returned by pis() can be retrieved.

            usage: piname()
        """
        if not jmmcLogin:
            prefs = A2P2ClientPreferences()
            jmmcLogin = prefs.getJmmcLogin()
        if not jmmcLogin:
            raise Exception(
                "missing login parameter or jmmc.login preference.")
        pis = self.pis()
        for pi in pis:
            if "login" in pi and pi["login"] == jmmcLogin:
                return pi["name"]

    def getRow(self, id):
        """ Get a single catalog record for the given id on the main catalog.

            usage: cat.getRow(42)
        """
        return self.api._get(f"/{self.catalogName}/{id}")

    def getDataFrame(self, forceUpdate=False):
        """ Get a pandas DataFrame from the main catalog joined the other if provided in constructor.

            usage: cat.getDataFrame()
        """
        if not ( self.updated or forceUpdate or self.lastDataFrame is None):
            return self.lastDataFrame
        self.lastDataFrame = self.getTable(forceUpdate=forceUpdate).to_pandas()
        return self.lastDataFrame

    def getTable(self, maxrec=10000, forceUpdate=False):
        """ Get an astropy table from the main catalog joined the other if provided in constructor.

            usage: cat.getTable()
        """
        # using SELECT TOP N below to workarround astroquery.utils.tap BUG

        if not ( self.updated or forceUpdate or self.lastTable is None ):
            return self.lastTable

        clauses = []
        if self.joins :
            joinedCatalogNames = []
            for join in self.joins:
                joinedCatalogNames.append(join["name"] + ".*")

            # colDelimiterName is added so we can keep the mainCatalog colnames for later updates (using rowsToDict)
            clauses.append(f"SELECT TOP {maxrec} {self.catalogName}.*, '' as {self.colDelimiterName}, {', '.join(joinedCatalogNames)} FROM {self.catalogName}" )

            for join in self.joins:
                if "catalogKey" in join.keys():
                    catalogKey=join["catalogKey"]
                else:
                    # we could use the (cached) metadata key, but this would add a additional remote call.A2P2ClientPreferences
                    # let's try with this convention using the same key name
                    catalogKey=join["id"]
                name=join["name"]
                id=join["id"]
                # LEFT JOIN may be an option provided by join key ?
                clauses.append (f" LEFT JOIN {name} ON {self.catalogName}.{catalogKey} = {name}.{id}")

            if self.where:
                clauses.append(f" WHERE {self.catalogName}.{self.where}")
        else:
            clauses.append(f"SELECT TOP {maxrec} * FROM {self.catalogName}")
            if self.where:
                clauses.append(f" WHERE {self.where}")

        query = "  ".join(clauses)
        logger.info(f"Querying remote catalog : {query}")
        self.lastTable = self.tap.search(query,maxrec=maxrec).to_table()
        self.updated=False
        return self.lastTable

    def tableToDict(self, table):
        """ Convert table (astropy.table or row) to a list of dict so we can modify content and update remote catalog using updateRows().

            usage: cat.tableToDict(table)
        """
        colnames = table.colnames
        if "coldelimiter___" in colnames:
            colnames = colnames[0:colnames.index("coldelimiter___")]
        dicts=[]
        # handle single row case
        table = table if isinstance(table, astropy.table.table.Table ) else [table]
        for row in table:
            dict = {}
            for colname in colnames:
                v=row[colname]
                if isinstance(v,str):
                    dict[colname] = v
                else:
                    # avoid np.numeric type to make it json serializable
                    dict[colname] = v.item()
            dicts.append(dict)
        return dicts

    def updateRow(self, id, values):
        """ Update record identified by given id and associated values.

            usage: cat.updateRows(42, {"col_a":"a", "col_b":"b" })
        """
        self.updated = True
        return self.api._put(f"/{self.catalogName}/{id}", values)

    def updateRows(self, values):
        """ Update multiple rows.
            Values must contain a list of dictionnary and each entry must contains id key among other columns.

            usage: updateRows([ { "id":42, "col_a":"a" }, { "id":24, "col_b":"b" } ])
        """
        self.updated = True
        # We may check befere sending payload that we always provide an id for every record
        # What is the behaviour if we provide various data assosiated to the same id ?
        return self.api._put(f"/{self.catalogName}", values)

    def addRows(self, values):
        """ Add multiple rows.
            Values is an array of row to add. id column values will be ignored.

            usage: addCatalogRows([ { "id":42, "col_a":"a" }, { "id":24, "col_b":"b" } ])
        """
        self.updated = True
        return self.api._post(f"/{self.catalogName}", json=values)


    def getDelegations(self, pi=None):
        """ Get -all- delegations.
            A specific pi parameter may be given but requires admin priviledges. Else use current piname will be used by remote service.

            usage: getDelegations()
        """
        res = self.api._get(f"/delegations?pi={pi}")
        if "delegations" in res:
            return res["delegations"] # login and pi values not returned

        return []

    def updateDelegations(self, delegations):
        """ Update delegations according given array of delegations.
            A specific "pi" key may be given in delegations dict but requires admin privileges. Else current piname will be used by remote service.
            "action" may be provided with "add" or "remove" value to set proper delegations (default add given delegation).

            usage: addDelegations([{"pi":"mypiname", "catalogs":"mycats", "coi":["alice","bob"]}])

        """
        return self.api._put("/delegations", json=delegations)

    def removeDelegations(self, delegations):
        """ Remove delegations according given array of delegations.
            A specific pi key may be given but requires admin privileges. Else current piname will be used by remote service.
            usage: removeDelegations([{}, {}])
        """
        return "TODO"


