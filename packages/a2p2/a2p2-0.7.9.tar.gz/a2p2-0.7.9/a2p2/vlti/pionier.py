#!/usr/bin/env python

__all__ = []

import re

from a2p2.vlti.instrument import OBConstraints
from a2p2.vlti.instrument import OBTarget
from a2p2.vlti.instrument import TSF
from a2p2.vlti.instrument import VltiInstrument

HELPTEXT = """
Please define PIONIER instrument help in a2p2/vlti/pionier.py
"""


class Pionier(VltiInstrument):

    def __init__(self, facility):
        VltiInstrument.__init__(self, facility, "PIONIER")

    def checkOB(self, ob, p2container=None):
        ui = self.ui

        instrumentConfiguration = ob.instrumentConfiguration
        BASELINE = ob.interferometerConfiguration.stations
        # Compute tel = UT or AT
        # TODO move code into common part
        if "U" in BASELINE:
            tel = "UT"
        else:
            tel = "AT"

        instrumentMode = instrumentConfiguration.instrumentMode

        # Retrieve GRISM or FREE info from instrumentMode
        for disp in self.getRange("PIONIER_acq.tsf", "INS.DISP.NAME"):
            if disp in instrumentMode[0:len(disp)]:
                ins_disp = disp

        for observationConfiguration in self.getSequence(ob):

            # create keywords storage objects
            acqTSF = TSF(self, "PIONIER_acq.tsf")

            # alias for PIONIER_obs_calibrator.tsf and
            # PIONIER_obs_science.tsf")
            kappaTSF = TSF(self, "PIONIER_gen_cal_kappa.tsf")
            darkTSF = TSF(self, "PIONIER_gen_cal_dark.tsf")


            obConstraints = OBConstraints(self)

            # set common properties
            acqTSF.INS_DISP_NAME = ins_disp

            if 'SCIENCE' in observationConfiguration.type:
                OBJTYPE = 'SCIENCE'
                obsTSF = TSF(self, "PIONIER_obs_science.tsf")
            else:
                OBJTYPE = 'CALIBRATOR'
                obsTSF = TSF(self, "PIONIER_obs_calibrator.tsf")

            scienceTarget = observationConfiguration.SCTarget

            obTarget = OBTarget(self, scienceTarget)

            # Set baseline  interferometric array code (should be a keywordlist)
            acqTSF.ISS_BASELINE = [self.getBaselineCode(ob)]

            self.checkIssVltiType(acqTSF)

            # define some default values
            DIAMETER = float(self.get(scienceTarget, "DIAMETER", 0.0))
            VIS = 1.0  # FIXME

            # Retrieve Fluxes
            TEL_COU_MAG = self.getFlux(scienceTarget, "V")
            acqTSF.ISS_IAS_HMAG = self.getFlux(scienceTarget, "H")

            # setup some default values, to be changed below
            TEL_COU_GSSOURCE = 'SCIENCE'  # by default
            GSRA = '00:00:00.000'
            GSDEC = '00:00:00.000'

            # initialize FT variables (must exist)

            # AO target
            aoTarget = ob.get(observationConfiguration, "AOTarget")
            if aoTarget != None:
                AONAME = aoTarget.name
                TEL_COU_GSSOURCE = 'SETUPFILE'  # since we have an AO
                # TODO check if AO coords should be required by template
                # AORA, AODEC  = self.getCoords(aoTarget,
                # requirePrecision=False)
                acqTSF.TEL_COU_PMA, acqTSF.TEL_COU_PMD = self.getPMCoords(
                    aoTarget)

            # Guide Star
            gsTarget = ob.get(observationConfiguration, 'GSTarget')
            if gsTarget != None:
                TEL_COU_GSSOURCE = 'SETUPFILE'  # since we have an GS
                GSRA, GSDEC = self.getCoords(gsTarget, requirePrecision=False)
                # no PMRA, PMDE for GS !!
                TEL_COU_MAG = float(gsTarget.FLUX_V)

            acqTSF.TEL_COU_GSSOURCE = TEL_COU_GSSOURCE
            acqTSF.TEL_COU_ALPHA = GSRA
            acqTSF.TEL_COU_DELTA = GSDEC
            acqTSF.TEL_COU_MAG = round(TEL_COU_MAG, 3)

            # LST interval
            try:
                obsConstraint = observationConfiguration.observationConstraints
                LSTINTERVAL = obsConstraint.LSTinterval
            except:
                LSTINTERVAL = None

            # Constraints
            obConstraints.name = 'Aspro-created constraints'
            skyTransparencyMagLimits = {"AT": 3, "UT": 5}
            if acqTSF.ISS_IAS_HMAG < skyTransparencyMagLimits[tel]:
                obConstraints.skyTransparency = 'Variable, thin cirrus'
            else:
                obConstraints.skyTransparency = 'Clear'

            # FIXME: error (OB): "Phase 2 constraints must closely follow what was requested in the Phase 1 proposal.
            # The seeing value allowed for this OB is >= java0x0 arcsec."
            # FIXME REPLACE SEEING THAT IS NO MORE SUPPORTED
            # obConstraints.seeing = 1.0
            # FIXME: default values NOT IN ASPRO!
            # constaints.airmass = 5.0
            # constaints.fli = 1

            # compute dit, ndit, nexp

            # and store computed values in obsTSF
            obsTSF.SEQ_NEXPO = 5
            # obsTSF.NSCANS = 100
            # kappaTSF.SEQ_DOIT=False
            # darkTSF.SEQ_DOIT=True

            # then call the ob-creation using the API if p2container exists.
            if p2container == None:
                ui.addToLog(obTarget.name +
                            " ready for p2 upload (details logged)")
                ui.addToLog(obTarget, False)
                ui.addToLog(obConstraints, False)
                ui.addToLog(acqTSF, False)
                ui.addToLog(obsTSF, False)
                ui.addToLog(kappaTSF, False)
                ui.addToLog(darkTSF, False)
            else:
                self.createOB(p2container, obTarget, obConstraints, OBJTYPE, instrumentMode,
                              LSTINTERVAL, [acqTSF, obsTSF, kappaTSF, darkTSF])

    def formatDitTable(self):
        buffer = ' No dit table in use \n'

#        ditTable = self.getDitTable()
#        buffer = '   Tel | Spec |  Pol  |     H   | DIT(s)\n'
#        buffer += '--------------------------------------------------------\n'
#        for tel in ['AT']:
#           for spec in ['GRISM', 'FREE']:
#                for pol in ['IN', 'OUT']:
#                    for i in range(len(ditTable[tel][spec][pol]['DIT'])):
#                        buffer += ' %3s | %4s | %3s | %2s |' % (tel,
#                                                                spec, pol, tel)
#                        buffer += ' %4.1f <K<= %3.1f | %4.1f' % (ditTable[tel][spec][pol]['MAG'][i],
#                                                                 ditTable[tel][spec][
#                                                                     pol]['MAG'][i + 1],
#                                                                 ditTable[tel][spec][pol]['DIT'][i])
#                        buffer += "\n"
#            Hut = ditTable[tel]['Hut']
        return buffer
