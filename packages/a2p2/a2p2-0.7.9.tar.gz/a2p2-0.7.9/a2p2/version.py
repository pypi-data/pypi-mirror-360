__version__ = "0.7.9"

__release_notes__ = {
    # "0.1.6": {
    #    "A2P2": [
    #        ],
    #    "VLTI": [
    #        ],
    #    "CHARA": [
    #        ],
    #    },
#
#       "TODO-SCIENCE": [
#           "Merge AO or GS in a same code section for every instruments",
#          "Check DIT table from the last template user manuals (especially MATISSE) and remove PIONIER's one",
#           "flag ~important~ keywords which MUST be set in a2p2 code and not leaved to there default values?",
#       ],
#       "TODO-DEV": [
#           "Support multiple period version (two major at least)",
#           "Support numlist keyword : eg. SEQ.HWPOFF (done in conf but must be range check compatible)",
#          "Unify ob name creation in vlti instrument createOB()",
#          "Complete test suite with more real p2 submissions",
#          "Try to read OB in P2 and send them back to Aspro2 as a new obs",
#      ],

    "0.7.9": {
       "A2P2": [
           "catalogs : remove duplicated code and force auth on POST requests",
        ],
    },"0.7.8": {
       "A2P2": [
           "catalogs : use cache for dataFrame() so we can modify it (was recreated from astropy table on each call)",
        ],
    },"0.7.7": {
       "A2P2": [
           "catalogs : save some data retrieval until update or force request occurs",
        ],
    },"0.7.6": {
       "A2P2": [
           "add getDataFrame() to a2p2.jmmc.Catalog to provide remote data with pandas format",
        ],
    },"0.7.5": {
       "A2P2": [
           "Add support for join and filter in a2p2.jmmc.Catalog wrapper",
        ],
    },"0.7.4": {
       "A2P2": [
           "Use pyproject.toml for python installation",
        ],"VLTI": [
            "Do not switch PIONIER mode to FREE when the magnitude of the IAS star is too high : an error may be provided by p2"
        ],
    },"0.7.3": {
       "CHARA": [
            "Better reuse of last working queueserver"
       ],
    },"0.7.2": {
       "A2P2": [
           "Auto update chara queueserver preference",
           "a2p2 -r generates release-notes.md (rendered on a2p2 repository)"
       ],
       "VLTI": [
            "Bugfix to support missin preference file"
       ],
       "CHARA": [
            "Support and try every queueserver's Urls comma separated from the queuserver user preference"
       ],
    },"0.7.1": {
       "A2P2": [
           "Fix ttk import on MacOS",
       ],
       "VLTI": [
            "Add first P112 support using radiobutton to select proper onaxis offaxis or wide GRAVITY templates",
            "Improve coordinate's checks and computations",
            "Add FT's propermotions and parallax"
       ],
       "CHARA": [
            "Display log of received OB also for calibrators"
       ]
    },"0.6.9": {
       "A2P2": [
            "ctrl-c support improved to qui a2p2 from terminal",
       ],
       "VLTI": [
            "OB's tree list selection mode limited to a single selection",
            "OB are stacked if Aspro2 send an OB without proper tree selection. stacked OB can be submitted after proper container selection or cancelled",
            "Provide checkboxes of types of interferometric observations to complete full OB"
       ],
       "CHARA": [
       ],
    },"0.6.8": {
       "A2P2": [
           "increase astropy version to avoid a dependency issue with numy"
       ],
    },"0.6.7": {
       "CHARA": [
           "Enhance information  while using OB2 server prototype",
       ]
     }, "0.6.6": {
       "CHARA": [
           "Fix formating of OB supporting array of observability time intervals",
       ],
    },"0.6.5": {
        "CHARA": [
            "Experimental: forward OBs through json payload to the location defined in preference",
        ],
    },"0.6.4": {
        "A2P2": [
            "Fix import that may break run on windows..."
        ],
    },"0.6.3": {
        "VLTI": [
            "Always use GRAVITY acqTSF.SEQ_INS_SOBJ_HMAG after P110",
        ],
    },"0.6.2": {
        "VLTI": [
            "Fix GRAVITY gen acq tsf",
        ],
    },"0.6.1": {
        "VLTI": [
            "Updated configuration for ESO P111",
        ]
    },"0.6.0": {
        "A2P2": [
            "Read Extra_informations from last Aspro2 OBXML"
        ],
    },"0.5.3": {
        "VLTI": [
            "Update DIT tables to last instrument template (version is stored in the table config to report warning)",
            "Do not stop OB creation if K mag is out of range during DIT calculation but show a warning and ask to proceed or abort",
        ]
    },"0.4.6": {
        "A2P2": [
            "Huge speedup of ESO P2 runs treeview",
            "Explicit SAMP unregister reduce risk of SAMP ghosts",
        ],
        "VLTI": [
            "Check consistency between Aspro2 inteferometer period and RUN's IP version",
            "Handle use SEQ.INS.SOBJ.HMAG after P110 instead of SEQ.FI.HMAG",
        ],
    },"0.4.5": {
        "A2P2": [
            "clarify some text in the default generated preference file",
        ],
        "VLTI": [
            "Change log message : Run filled -> OB transmitted",
            "Missing flux error message enhanced : show associated target name",
            "Handle ALPHA DELTA coordinates of associated guide star",
            "MATISSE: handle Aspro2's frindge tracker mode : None or GRA4MAT",
            "MATISSE: define DPR.CATG  (always was CALIB)",
            "MATISSE: use V band for COU.GS.MAG or try G one on ATs.",
            "GRAVITY: include dual keywords in gravity_rangeTable",
        ],
    },"0.4.4": {
        "A2P2": [
            "add Catalog.piname() to get a pi name for a given jmmc account looking at a given catalog (jmmc.login preference is used without parameter)",
            "Add new preference to put jmmc account credentials",
        ],
    },"0.4.3": {
        "A2P2": [
            "Enhance a2p2.jmmc.models._model so it automagically computes component names >{(())>",
        ],
    },"0.4.2": {
        "A2P2": [
            "Add option to select public CatalogAPI server",
        ],
    },"0.4.1": {
        "A2P2": [
            "Add version alpha of a2p2.fr.webservices.Calliper client",
        ],
    }, "0.4.0": {
        "A2P2": [
            "First basic support of SAMP messages from Aspro for models",
            "Support model compositions in models module",
        ],
    }, "0.3.10": {

        "A2P2": [
            "Fix bug that occurs when user has no preference file",
            "Add new serialisation of a2p2.jmmc.Models"
        ],
    }, "0.3.9": {
        "VLTI": [
            "Bugfix for single CAL SCI",
        ],
    }, "0.3.8": {
        "VLTI": [
            "Enhance CAL SCI sequence : [CAL1] SCI [CAL2 [SCI CAL3 [...] ] ] ",
            "Fix COU_AG_PMA and COU_AG_PMD for MATISSE acq template",
            "Do not throw a dialog for every submitted OBs",
            "Enhance some messages",
            # "BugFix to create a folder on non tutorial accounts"
        ],

    }, "0.3.7": {
        "VLTI": [
            "Revert SEQ.RELOFF.X/Y = 0.0 (same as default) for GRAVITY dual_obs_exp template"
        ],
    }, "0.3.6": {
        "VLTI": [
            "Disable SEQ.RELOFF.X for GRAVITY dual to make OB compliant"
        ],
    }, "0.3.5": {
        "VLTI": [
            "Accept to add calibrator inside a Concatenation container",
            "Use p2.iss.vltitype preference keys to set supported value of instrument's acquisition templates. ( run 'a2p2 -c' )"
        ],
    },
    "0.3.4": {
        "VLTI": [
            "Sync templates with P109",
            "Create OB in selected folder: do not create anymore a folder but create a concatenation for SM if a Run's root is selected."
        ],
    },
    "0.3.3": {
        "A2P2": [
            "Add basic support of Aspro2's model for SAMP interoperability",
        ],
        "VLTI": [
            "Fix missing import for p2api module"
        ],
    },
    "0.3.2": {
        "A2P2": [
            "Improve setup.py that now requires python 3+ and a fresh version of astropy",
        ],
        "VLTI": [
            #            "revert back to p2 requests use which now reuses connections",
        ],
    },
    "0.3.1": {
        "A2P2": [
            "Bug fix for authenticated Catalog access",
        ],
    },
    "0.3.0": {
        "A2P2": [
            "Give a try to embedd some code to interact with JMMC services",
        ],
        "VLTI": [
            #            "revert back to p2 requests use which now reuses connections",
        ],
    },
    "0.2.15": {
        "VLTI": [
            #            "add a wrapper on p2 to make run's tree faster (~2.5x)",
        ],
    },
    "0.2.14": {
        "A2P2": [
            "BugFix: ask for container Name only if one is selected"
        ],
    },
    "0.2.13": {
        "A2P2": [
            "A2P2 is no longer python2 compatible. Hope it will be ok for everybody ? Send an issue else ;)",
            "Fix generated release note order according to semver values",
            "Dry tests done looping on a few OBXML files"
            "Added -c option to a2p2 so we generated a config file ( helps to automatically fill P2 login info & autologin : )"
        ],
        "VLTI": [
            "Conf updated with IPs 106.25",
            "BugFix: OB no more sent to P2 if OB's instrument is not the same than p2 selected container"
        ],
    },
    "0.2.12": {
        "A2P2": [
            "Fix import in main console script"
        ],
    },
    "0.2.11": {
        "A2P2": [
            "enhance setup.py so it install Windows special-cases .exe files"
        ],
    },
    "0.2.10": {
        "A2P2": [
            "Patch bad SAMP url handling on Windows"
        ],
    },
    "0.2.9": {
        "VLTI": [
            "Fix bug that prevent to create any folder or concatenation at RUNS's root"
        ],
    },
    "0.2.8": {
        "A2P2": [
            "Fix release notes order in the GUI",
            "Handle special jmmc account, kindly set by ESO colleagues to perfom future tests as closed as possible to the real UX"
        ],
        "VLTI": [
            "Display instrument package version in the container table",
            "Limit keyword set on P2 only to the modified ones. No more default values from our static config are sent so it enhances compatibility accross multiple Period versions",
        ],
        "CHARA": [
        ],
    }, "0.2.7": {
        "STATUS": [
            "This version get lot of changes and may contain bugs or missing features, please provide any feedback to improve and prepare a better future release !"
        ],
        "A2P2": [
            "Refactor code accross vlti instruments",
            "Fix container selection in P2 tree"
            "Add release notes in the GUI"
        ],
        "VLTI": [
            "Conf updated with IPs 105.18",
            "Add MATISSE support",
            "Change GRAVITY DIT computation",
            "OB constraints autochecked using an instrumentConstraints TSF",
            "Support Concatenations (also shown in the tree panel)",
            "Show type in the container chooser instead of containerID"
        ],
    }, "0.2.6": {
        "VLTI": [
            "Support baseline back again (single one at present)"
        ],
    },
    "0.2.5": {
        "VLTI": [
            "Add missing template name in log",
            "Fix error removing baseline after constraint changes on P2 side. Next a2p2 version should add them back in acq templates"
        ],
    },
    "0.2.4": {
        "VLTI": [
            "Fix bug / wrong keys"
        ],
    },
    "0.2.3": {
        "VLTI": [
            "Hide password in login frame"
        ],
    },
    "0.2.2": {
        "VLTI": [
            "ignore default time constraints computed by Aspro"
        ],
    },
    "0.2.1": {
        "VLTI": [
            "fix support for a list of multiples time constraints"
        ],
    },
    "0.2.0": {
        "VLTI": [
            "bug fix"
        ],
    },
    "0.1.6": {
        "A2P2": [
            "Major code reformating - pep8 compliant"
        ],
        "VLTI": [
            "general config updates",
            "add PIONIER"
        ],
    },
    "0.1.5": {
        "VLTI": [
            "bugfix for dualfield cases"
        ],
    },
    "0.1.4": {
        "A2P2": [
            "fix order of returned fluxes in OB.getFluxes()"
        ]
    },
    "0.1.3": {
        "VLTI": [
            "fix telescope mode computation"
        ]
    },
    "0.1.2": {
        "A2P2": [
            "bugfix for SPLIT polarisation mode detection on GRAVITY",
            "bugfix that displays warning message during DIT calculation in GRAVITY LR mode",
            "enhancement of out of bound exception message of DIT calculation method"
        ]
    },
    "0.1.1": {
        "A2P2": [
            "muti-faciliy",
            "multi-VltiInstruments",
            "json VltiConfig (templates+dit tables)"
        ]
    }
}
