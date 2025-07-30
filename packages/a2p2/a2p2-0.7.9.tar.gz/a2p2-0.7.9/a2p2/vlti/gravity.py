
#!/usr/bin/env python

__all__ = []

import re

import numpy as np

from a2p2.vlti.instrument import OBConstraints
from a2p2.vlti.instrument import OBTarget
from a2p2.vlti.instrument import TSF
from a2p2.vlti.instrument import VltiInstrument

HELPTEXT = """
Please define Gravity instrument help in a2p2/vlti/gravity.py
"""


class Gravity(VltiInstrument):

    def __init__(self, facility):
        VltiInstrument.__init__(self, facility, "GRAVITY")

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

        if "COMBINED" in instrumentMode:
            ins_spec_pol = "OUT"
        else:
            ins_spec_pol = 'IN'

        for observationConfiguration in self.getSequence(ob):

            # define top level variable
            if 'SCIENCE' in observationConfiguration.type:
                OBJTYPE = 'SCIENCE'
            else:
                OBJTYPE = 'CALIBRATOR'

            wideMode = self.getAcquisitionType() == "wide"
            onaxisMode = self.isCalibrator(OBJTYPE) or self.getAcquisitionType() == "onaxis"
            offaxisMode = self.isScience(OBJTYPE) and self.getAcquisitionType() == "offaxis"

            # skip calib with wide mode
            # According to templat manual P112 : Calibrations of the interferometric transfer function are thus not needed and not offered for this mode
            if OBJTYPE == 'CALIBRATOR' and wideMode:
                ui.addToLog("Calibrator ignored with wide mode")
            else:

                # dualField is true if FT Target is defined, else false
                ftTarget = ob.get(observationConfiguration, "FTTarget")
                if ftTarget:
                    dualField = True
                else:
                    dualField = False

                # create keywords storage objects
                acqTSF = TSF(self, self.getGravityAcqTemplateName(
                    ob, OBJTYPE, dualField))
                obsTSF = TSF(self, self.getGravityObsTemplateName(
                    ob, OBJTYPE, dualField))

                obConstraints = OBConstraints(self)

                # Check SPEC_RES from instrumentMode and set SPEC_POL except for single_offaxis ( missing keyword INS_SPEC_RES)
                if offaxisMode and not dualField:
                    for res in ("LOW","MED","HIGH"):
                        if res in instrumentMode[0:len(res)]:
                            ins_spec_res = res
                else:
                    ins_spec_res = instrumentMode
                    for res in self.getRange(acqTSF.getName(), "INS.SPEC.RES"):
                        if res in instrumentMode[0:len(res)]:
                            ins_spec_res = res
                    acqTSF.INS_SPEC_RES = ins_spec_res
                    acqTSF.INS_SPEC_POL = ins_spec_pol

                acqTSF.INS_FT_POL = ins_spec_pol

                scienceTarget = observationConfiguration.SCTarget

                obTarget = OBTarget(self, scienceTarget)

                # define target
                acqTSF.SEQ_INS_SOBJ_NAME = obTarget.name

                # Set baseline  interferometric array code (should be a keywordlist)
                acqTSF.ISS_BASELINE = [self.getBaselineCode(ob)]

                self.checkIssVltiType(acqTSF)

                # define some default values
                acqTSF.SEQ_INS_SOBJ_DIAMETER = float(
                    self.get(scienceTarget, "DIAMETER", 0.0))

                # Retrieve Fluxes
                acqTSF.COU_GS_MAG = self.getFlux(scienceTarget, "V")
                acqTSF.SEQ_INS_SOBJ_MAG = self.getFlux(scienceTarget, "K")
                if not dualField or wideMode:
                    acqTSF.SEQ_INS_SOBJ_HMAG = self.getFlux(scienceTarget, "H")

                # setup some default values, to be changed below
                GSRA = '00:00:00.000'
                GSDEC = '00:00:00.000'

                # if FT Target is not ScTarget, we are in dual-field (TBD)
                ftTarget = ob.get(observationConfiguration, "FTTarget")
                if ftTarget != None:
                    acqTSF.SEQ_FT_ROBJ_NAME = ftTarget.name
                    acqTSF.SEQ_FT_ROBJ_MAG = self.getFlux(ftTarget, "K")
                    acqTSF.SEQ_FT_ROBJ_HMAG = self.getFlux(ftTarget, "H")

                    # test arcseconds distance in dual field or wide mode (GRAVITY_TemplateManual_P112 values)
                    if tel == "UT":
                        if wideMode:
                            SCtoREFmaxDist = 30
                            SCtoREFminDist = 2
                        elif offaxisMode:
                            SCtoREFmaxDist = 2
                            SCtoREFminDist = .27
                        else:
                            SCtoREFmaxDist = .6
                            SCtoREFminDist = 0
                    else:
                        if wideMode:
                            SCtoREFmaxDist = 30
                            SCtoREFminDist = 4
                        elif offaxisMode:
                            SCtoREFmaxDist = 4
                            SCtoREFminDist = 1.17
                        else:
                            SCtoREFmaxDist = 2.7
                            SCtoREFminDist = 0

                    FTRA, FTDEC = self.getCoords(ftTarget)
                    dualFieldSeparation = self.getSkySeparation(obTarget.ra, obTarget.dec, FTRA, FTDEC)
                    dualFieldSeparation = dualFieldSeparation.arcsec
                    if dualFieldSeparation <= SCtoREFminDist or dualFieldSeparation >= SCtoREFmaxDist:
                        raise ValueError(f"Dual-Field separation of two stars {dualFieldSeparation:.3f}'' is out of range [{SCtoREFminDist}'', {SCtoREFmaxDist}''], Please correct.")
                    else:
                        ui.addToLog(f"Dual-Field separation of two stars is {dualFieldSeparation:.3f}''")

                    # Provide FT position
                    if wideMode:
                        acqTSF.SEQ_FT_ROBJ_ALPHA = FTRA
                        acqTSF.SEQ_FT_ROBJ_DELTA = FTDEC
                    else:
                        # compute x,y between science and ref beams and set X,Y (mas) keywords:
                        dualFieldOffset = self.getSkyOffset(obTarget.ra, obTarget.dec, FTRA, FTDEC)
                        acqTSF.SEQ_INS_SOBJ_X = dualFieldOffset[0].mas
                        acqTSF.SEQ_INS_SOBJ_Y = dualFieldOffset[1].mas

                    FTPMA, FTPMD = self.getPMCoords(ftTarget)
                    acqTSF.SEQ_FT_ROBJ_PMA = FTPMA
                    acqTSF.SEQ_FT_ROBJ_PMD = FTPMD

                    FTPARALLAX = self.getPARALLAX(ftTarget)
                    acqTSF.SEQ_FT_ROBJ_PARALLAX = FTPARALLAX

                    acqTSF.SEQ_FT_MODE = "AUTO"

                # AO target
                aoTarget = ob.get(observationConfiguration, "AOTarget")
                if aoTarget != None:
                    AONAME = aoTarget.name
                    acqTSF.COU_AG_GSSOURCE = 'SETUPFILE'  # since we have an AO
                    acqTSF.COU_AG_ALPHA, acqTSF.COU_AG_DELTA = self.getCoords(
                        aoTarget, requirePrecision=False)
                    acqTSF.COU_AG_PMA, acqTSF.COU_AG_PMD = self.getPMCoords(
                        aoTarget)
                    # Case of CIAO to be implemented...based on v and k magnitudes?
                    acqTSF.COU_GS_MAG = float(aoTarget.FLUX_V)

                # Guide Star
                gsTarget = ob.get(observationConfiguration, 'GSTarget')
                if gsTarget != None and aoTarget == None:
                    acqTSF.COU_AG_SOURCE = 'SETUPFILE'  # since we have an GS
                    acqTSF.COU_AG_ALPHA, acqTSF.COU_AG_DELTA = self.getCoords(
                        gsTarget, requirePrecision=False)
                    acqTSF.COU_AG_PMA, acqTSF.COU_AG_PMD = self.getPMCoords(
                        gsTarget)
                    acqTSF.COU_GS_MAG = float(gsTarget.FLUX_V)

                # LST interval
                try:
                    obsConstraint = observationConfiguration.observationConstraints
                    LSTINTERVAL = obsConstraint.LSTinterval
                except:
                    LSTINTERVAL = None

                # Constraints
                obConstraints.name = 'Aspro-created constraints'
                skyTransparencyMagLimits = {"AT": 3, "UT": 5}
                if acqTSF.SEQ_INS_SOBJ_MAG < skyTransparencyMagLimits[tel]:
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
                dit = self.getDit(tel, ins_spec_res, ins_spec_pol,
                                acqTSF.SEQ_INS_SOBJ_MAG, dualField, targetName=scienceTarget.name.strip(),  showWarning=(p2container == None))
                ndit = 300 / dit
                if ndit < 10:
                    ndit = 10
                if ndit > 300:
                    ndit = 300
                ndit = int(ndit)  # must be integer
                exptime = int(ndit * dit + 40)  # 40 sec overhead by exp
                nexp = (1800 - 900) / exptime
                nexp = int(nexp)
                ui.addToLog(
                    'number of exposures to reach 1800 s per OB is ' + str(nexp))
                if nexp < 3:
                    nexp = 3  # min is O S O
                    # recompute ndit
                    exptime = (1800 - 900) / nexp
                    ndit = (exptime - 40) / dit
                    ndit = int(ndit)
                    if ndit < 10:
                        ndit = 10
                        ui.addToLog(
                            "**Warning**, OB NDIT has been set to min value=%d, but OB will take longer than 1800 s" % (
                                ndit))
                nexp %= 40
                sequence = 'O S O O S O O S O O S O O S O O S O O S O O S O O S O O S O O S O O S O O S O O'
                my_sequence = sequence[0:2 * nexp]
                # and store computed values in obsTSF
                obsTSF.DET2_DIT = str(dit)
                obsTSF.DET2_NDIT_OBJECT = ndit
                obsTSF.DET2_NDIT_SKY = ndit
                obsTSF.SEQ_OBSSEQ = my_sequence

                obsTSF.SEQ_SKY_X = 2000
                obsTSF.SEQ_SKY_Y = 2000

                # then call the ob-creation using the API if p2container exists.
                if p2container == None:
                    ui.addToLog(obTarget.name +
                                " ready for p2 upload (details logged)")
                    ui.addToLog(obTarget, False)
                    ui.addToLog(obConstraints, False)
                    ui.addToLog(acqTSF, False)
                    ui.addToLog(obsTSF, False)
                else:
                    self.createOB(p2container, obTarget, obConstraints, OBJTYPE, instrumentMode,
                                  LSTINTERVAL, [acqTSF, obsTSF])

    def formatDitTable(self):
        ditTable = self.getDitTable()
        buffer = '    Mode     |Spec |  Pol  |Tel |       K       | DIT(s)\n'
        buffer += '--------------------------------------------------------\n'
        for tel in ['AT']:
            for spec in ['LOW', 'MED', 'HIGH']:
                for pol in ['OUT', 'IN']:
                    for i in range(len(ditTable[tel][spec][pol]['DIT'])):
                        buffer += 'Single Field | %4s | %3s | %2s |' % (
                            spec, pol, tel)
                        buffer += ' %4.1f <K<= %3.1f | %4.1f' % (ditTable[tel][spec][pol]['MAG'][i],
                                                                 ditTable[tel][spec][
                                                                     pol]['MAG'][i + 1],
                                                                 ditTable[tel][spec][pol]['DIT'][i])
                        buffer += "\n"
            Kdf = ditTable[tel]['Kdf']
            Kut = ditTable[tel]['Kut']
            buffer += ' Dual Field  |  all | all | %2s | Kdf = K - %.1f |  -\n' % (
                tel, Kdf)
            tel = "UT"
            buffer += 'Single Field |  all | all | %2s | Kdf = K - %.1f |  -\n' % (
                tel, Kut)
            buffer += ' Dual Field  |  all | all | %2s | Kdf = K - %.1f |  -\n' % (
                tel, Kut + Kdf)
        return buffer

    def getGravityObsTemplateName(self, ob, OBJTYPE, dualField):
        return self.getGravityTemplateName("obs", ob, OBJTYPE, dualField)

    def getGravityAcqTemplateName(self, ob, OBJTYPE, dualField):
        return self.getGravityTemplateName("acq", ob, OBJTYPE, dualField)

    def getGravityTemplateName(self, templateType, ob, OBJTYPE, dualField):

        dualValue = {True: "dual", False: "single"}
        objValue = {"SCIENCE": "exp", "CALIBRATOR": "calibrator"}

        # Add : name , <dual|single>, <obs|acq>, [objValue]
        items = [self.getName()]
        # Add dual or single for SCIENCE or single for other OBJTYPES
        items.append(dualValue[dualField and self.isScience(OBJTYPE)])
        # Add acquisitionType (or onaxis for CAL) after P112 if acq
        if templateType == "acq" and ob.getPeriod() >= 112:
            if self.isScience(OBJTYPE):
                items.append(self.getAcquisitionType())
            else:
                items.append("onaxis")
        # Add acq or obs
        items.append(templateType)
        # Add objValue if obs
        if templateType == "obs":
            items.append(objValue[OBJTYPE])

        return "_".join([i for i in items if i is not None])+".tsf"
