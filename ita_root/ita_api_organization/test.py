from common_libs.conductor.classes.util import ConductorCommonLibs

data = {
    "config": {
        "nodeNumber": 17,
        "terminalNumber": 33,
        "edgeNumber": 20
    },
    "conductor": {
        "id": None,
        "conductor_name": "TEST_CONDUCTOR",
        "note": None,
        "last_update_date_time": None
    },
    # "conductor": {
    #     "id": None,
    #     "conductor_name": "TEST_CONDUCTOR",
    #     "note": None,
    #     "LUT4U": None,
    #     "ACCESS_AUTH": ""
    # },
    "node-1": {
        "type": "start",
        "id": "node-1",
        "terminal": {
            "terminal-1": {
                "id": "terminal-1",
                "type": "out",
                # "x": 7691,
                # "y": 7758,
                "targetNode": "node-9",
                "edge": "line-1"
            }
        },
        "x": 7510,
        "y": 7729,
        "w": 198,
        "h": 58
    },
    "node-2": {
        "type": "end",
        "id": "node-2",
        "terminal": {
            "terminal-2": {
                "id": "terminal-2",
                "type": "in",
                "x": 8700,
                "y": 8068,
                "targetNode": "node-3",
                "edge": "line-14"
            }
        },
        "end_type": "5",
        "x": 8683,
        "y": 8039,
        "w": 198,
        "h": 58
    },
    "node-3": {
        "type": "status-file-branch",
        "id": "node-3",
        "terminal": {
            "terminal-3": {
                "id": "terminal-3",
                "type": "in",
                "x": 8355,
                "y": 8122,
                "targetNode": "node-13",
                "edge": "line-13"
            },
            "terminal-4": {
                "id": "terminal-4",
                "type": "out",
                "case": 1,
                "x": 8631,
                "y": 8069,
                "targetNode": "node-2",
                "edge": "line-14",
                "condition": [
                    "1"
                ]
            },
            "terminal-5": {
                "id": "terminal-5",
                "type": "out",
                "case": "else",
                "x": 8631,
                "y": 8175,
                "targetNode": "node-14",
                "edge": "line-15"
            }
        },
        "x": 8338,
        "y": 8040,
        "w": 310,
        "h": 164
    },
    "node-4": {
        "type": "merge",
        "id": "node-4",
        "terminal": {
            "terminal-6": {
                "id": "terminal-6",
                "type": "in",
                "case": 1,
                "x": 8030,
                "y": 7899,
                "targetNode": "node-10",
                "edge": "line-6"
            },
            "terminal-7": {
                "id": "terminal-7",
                "type": "in",
                "case": 2,
                "x": 8030,
                "y": 7981,
                "targetNode": "node-11",
                "edge": "line-7"
            },
            "terminal-8": {
                "id": "terminal-8",
                "type": "out",
                "x": 8207,
                "y": 7940,
                "targetNode": "node-7",
                "edge": "line-8"
            }
        },
        "x": 8013,
        "y": 7882,
        "w": 211,
        "h": 116
    },
    "node-5": {
        "type": "parallel-branch",
        "id": "node-5",
        "terminal": {
            "terminal-9": {
                "id": "terminal-9",
                "type": "in",
                "x": 7571,
                "y": 7940,
                "targetNode": "node-9",
                "edge": "line-2"
            },
            "terminal-10": {
                "id": "terminal-10",
                "type": "out",
                "case": 1,
                "x": 7671,
                "y": 7899,
                "targetNode": "node-10",
                "edge": "line-3"
            },
            "terminal-11": {
                "id": "terminal-11",
                "type": "out",
                "case": 2,
                "x": 7671,
                "y": 7981,
                "targetNode": "node-11",
                "edge": "line-5"
            }
        },
        "x": 7554,
        "y": 7882,
        "w": 134,
        "h": 116
    },
    "node-6": {
        "type": "conditional-branch",
        "id": "node-6",
        "terminal": {
            "terminal-12": {
                "id": "terminal-12",
                "type": "in",
                "x": 7834,
                "y": 8112,
                "targetNode": "node-12",
                "edge": "line-16"
            },
            "terminal-13": {
                "id": "terminal-13",
                "type": "out",
                "condition": [
                    "9"
                ],
                "case": 1,
                "x": 8010,
                "y": 8070,
                "targetNode": "node-13",
                "edge": "line-12"
            },
            "terminal-14": {
                "id": "terminal-14",
                "type": "out",
                "condition": [
                    "9999"
                ],
                "case": 2,
                "x": 8010,
                "y": 8154,
                "targetNode": "node-16",
                "edge": "line-18"
            }
        },
        "x": 7817,
        "y": 8052,
        "w": 210,
        "h": 120
    },
    "node-7": {
        "type": "call",
        "id": "node-7",
        "terminal": {
            "terminal-15": {
                "id": "terminal-15",
                "type": "in",
                "x": 8271,
                "y": 7940,
                "targetNode": "node-4",
                "edge": "line-8"
            },
            "terminal-16": {
                "id": "terminal-16",
                "type": "out",
                "x": 8482,
                "y": 7940,
                "targetNode": "node-8",
                "edge": "line-9"
            }
        },
        "SKIP_FLAG": 0,
        "CALL_CONDUCTOR_ID": 1,
        "OPERATION_NO_IDBH": None,
        "x": 8254,
        "y": 7909,
        "w": 245,
        "h": 62
    },
    "node-8": {
        "type": "pause",
        "id": "node-8",
        "terminal": {
            "terminal-17": {
                "id": "terminal-17",
                "type": "in",
                "x": 8554,
                "y": 7947,
                "targetNode": "node-7",
                "edge": "line-9"
            },
            "terminal-18": {
                "id": "terminal-18",
                "type": "out",
                "x": 8684,
                "y": 7947,
                "targetNode": "node-12",
                "edge": "line-10"
            }
        },
        "x": 8537,
        "y": 7930,
        "w": 164,
        "h": 34
    },
    "node-9": {
        "type": "movement",
        "id": "node-9",
        "terminal": {
            "terminal-19": {
                "id": "terminal-19",
                "type": "in",
                "x": 7771,
                "y": 7760,
                "targetNode": "node-1",
                "edge": "line-1"
            },
            "terminal-20": {
                "id": "terminal-20",
                "type": "out",
                "x": 7982,
                "y": 7760,
                "targetNode": "node-5",
                "edge": "line-2"
            }
        },
        "PATTERN_ID": "1",
        "SKIP_FLAG": 0,
        "OPERATION_NO_IDBH": None,
        "ORCHESTRATOR_ID": "3",
        "Name": "NULL",
        "x": 7754,
        "y": 7731,
        "w": 245,
        "h": 58
    },
    "line-1": {
        "type": "edge",
        "id": "line-1",
        "outNode": "node-1",
        "outTerminal": "terminal-1",
        "inNode": "node-9",
        "inTerminal": "terminal-19"
    },
    "line-2": {
        "type": "edge",
        "id": "line-2",
        "outNode": "node-9",
        "outTerminal": "terminal-20",
        "inNode": "node-5",
        "inTerminal": "terminal-9"
    },
    "node-10": {
        "type": "movement",
        "id": "node-10",
        "terminal": {
            "terminal-21": {
                "id": "terminal-21",
                "type": "in",
                "x": 7747,
                "y": 7901,
                "targetNode": "node-5",
                "edge": "line-3"
            },
            "terminal-22": {
                "id": "terminal-22",
                "type": "out",
                "x": 7958,
                "y": 7901,
                "targetNode": "node-4",
                "edge": "line-6"
            }
        },
        "PATTERN_ID": "1",
        "SKIP_FLAG": 0,
        "OPERATION_NO_IDBH": None,
        "ORCHESTRATOR_ID": "3",
        "Name": "NULL",
        "x": 7730,
        "y": 7872,
        "w": 245,
        "h": 58
    },
    "node-11": {
        "type": "movement",
        "id": "node-11",
        "terminal": {
            "terminal-23": {
                "id": "terminal-23",
                "type": "in",
                "x": 7745,
                "y": 7983,
                "targetNode": "node-5",
                "edge": "line-5"
            },
            "terminal-24": {
                "id": "terminal-24",
                "type": "out",
                "x": 7956,
                "y": 7983,
                "targetNode": "node-4",
                "edge": "line-7"
            }
        },
        "PATTERN_ID": "1",
        "SKIP_FLAG": 0,
        "OPERATION_NO_IDBH": None,
        "ORCHESTRATOR_ID": "3",
        "Name": "NULL",
        "x": 7728,
        "y": 7954,
        "w": 245,
        "h": 58
    },
    "line-3": {
        "type": "edge",
        "id": "line-3",
        "outNode": "node-5",
        "outTerminal": "terminal-10",
        "inNode": "node-10",
        "inTerminal": "terminal-21"
    },
    "line-5": {
        "type": "edge",
        "id": "line-5",
        "outNode": "node-5",
        "outTerminal": "terminal-11",
        "inNode": "node-11",
        "inTerminal": "terminal-23"
    },
    "line-6": {
        "type": "edge",
        "id": "line-6",
        "outNode": "node-10",
        "outTerminal": "terminal-22",
        "inNode": "node-4",
        "inTerminal": "terminal-6"
    },
    "line-7": {
        "type": "edge",
        "id": "line-7",
        "outNode": "node-11",
        "outTerminal": "terminal-24",
        "inNode": "node-4",
        "inTerminal": "terminal-7"
    },
    "line-8": {
        "type": "edge",
        "id": "line-8",
        "outNode": "node-4",
        "outTerminal": "terminal-8",
        "inNode": "node-7",
        "inTerminal": "terminal-15"
    },
    "line-9": {
        "type": "edge",
        "id": "line-9",
        "outNode": "node-7",
        "outTerminal": "terminal-16",
        "inNode": "node-8",
        "inTerminal": "terminal-17"
    },
    "node-12": {
        "type": "movement",
        "id": "node-12",
        "terminal": {
            "terminal-25": {
                "id": "terminal-25",
                "type": "in",
                "x": 7560,
                "y": 8110,
                "targetNode": "node-8",
                "edge": "line-10"
            },
            "terminal-26": {
                "id": "terminal-26",
                "type": "out",
                "x": 7771,
                "y": 8110,
                "targetNode": "node-6",
                "edge": "line-16"
            }
        },
        "PATTERN_ID": "1",
        "SKIP_FLAG": 0,
        "OPERATION_NO_IDBH": None,
        "ORCHESTRATOR_ID": "3",
        "Name": "NULL",
        "x": 7543,
        "y": 8081,
        "w": 245,
        "h": 58
    },
    "line-10": {
        "type": "edge",
        "id": "line-10",
        "outNode": "node-8",
        "outTerminal": "terminal-18",
        "inNode": "node-12",
        "inTerminal": "terminal-25"
    },
    "node-13": {
        "type": "movement",
        "id": "node-13",
        "terminal": {
            "terminal-27": {
                "id": "terminal-27",
                "type": "in",
                # "x": 8072,
                "y": 8071,
                "targetNode": "node-6",
                "edge": "line-12"
            },
            "terminal-28": {
                "id": "terminal-28",
                "type": "out",
                "x": 8283,
                # "y": 8071,
                "targetNode": "node-3",
                "edge": "line-13"
            }
        },
        "PATTERN_ID": "1",
        "SKIP_FLAG": 0,
        "OPERATION_NO_IDBH": None,
        "ORCHESTRATOR_ID": "3",
        "Name": "NULL",
        "x": 8055,
        "y": 8042,
        "w": 245,
        "h": 58
    },
    "line-12": {
        "type": "edge",
        "id": "line-12",
        "outNode": "node-6",
        "outTerminal": "terminal-13",
        "inNode": "node-13",
        "inTerminal": "terminal-27"
    },
    "line-13": {
        "type": "edge",
        "id": "line-13",
        "outNode": "node-13",
        "outTerminal": "terminal-28",
        "inNode": "node-3",
        "inTerminal": "terminal-3"
    },
    "line-14": {
        "type": "edge",
        "id": "line-14",
        "outNode": "node-3",
        "outTerminal": "terminal-4",
        "inNode": "node-2",
        "inTerminal": "terminal-2"
    },
    "node-14": {
        "type": "end",
        "id": "node-14",
        "terminal": {
            "terminal-29": {
                "id": "terminal-29",
                "type": "in",
                "x": 8707,
                "y": 8177,
                "targetNode": "node-3",
                "edge": "line-15"
            }
        },
        "end_type": "11",
        "x": 8690,
        "y": 8148,
        "w": 246,
        "h": 58
    },
    "line-15": {
        "type": "edge",
        "id": "line-15",
        "outNode": "node-3",
        "outTerminal": "terminal-5",
        "inNode": "node-14",
        "inTerminal": "terminal-29"
    },
    "line-16": {
        "type": "edge",
        "id": "line-16",
        "outNode": "node-12",
        "outTerminal": "terminal-26",
        "inNode": "node-6",
        "inTerminal": "terminal-12"
    },
    "node-16": {
        "type": "end",
        "id": "node-16",
        "terminal": {
            "terminal-32": {
                "id": "terminal-32",
                "type": "in",
                "x": 8067,
                "y": 8152,
                "targetNode": "node-6",
                "edge": "line-18"
            }
        },
        "end_type": "7",
        "x": 8050,
        "y": 8123,
        "w": 246,
        "h": 58
    },
    "line-18": {
        "type": "edge",
        "id": "line-18",
        "outNode": "node-6",
        "outTerminal": "terminal-14",
        "inNode": "node-16",
        "inTerminal": "terminal-32"
    }
}
# data = {
#     "config": {
#         "nodeNumber": 17,
#         "terminalNumber": 33,
#         "edgeNumber": 20
#     },
#     "conductor": {
#         # "id": None,
#         "conductor_name": "TEST_CONDUCTOR",
#         "note": None,
#         "LUT4U": None,
#         "ACCESS_AUTH": ""
#     },
#     "node-15": {},
#     # "node-15xx": {},
#     "line-1": {},
#     "line-12": {
#         "type": "edge",
#         "id": "line-12",
#     },
#     "line-18": {
#         "type": "edged",
#         "id": "line-18",
#         "outNode": "node-6",
#         "outTerminal": "terminal-14",
#         "inNode": "node-16",
#         "inTerminal": "terminal-32"
#     }
# }
# data = {
# 	"conductor": {
# 		"conductor_name": "C1",
# 		"note": None,
# 		"id": 1,
# 		"LUT4U": "20220720092625.552688",
# 		"ACCESS_AUTH": "",
# 		"NOTICE_INFO": []
# 	},
# 	"config": {
# 		"editorVersion": "1.0.2",
# 		"nodeNumber": 4,
# 		"terminalNumber": 5,
# 		"edgeNumber": 3
# 	},
# 	"line-1": {
# 		"id": "line-1",
# 		"inNode": "node-3",
# 		"inTerminal": "terminal-3",
# 		"outNode": "node-1",
# 		"outTerminal": "terminal-1",
# 		"type": "egde"
# 	},
# 	"line-2": {
# 		"id": "line-2",
# 		"inNode": "node-2",
# 		"inTerminal": "terminal-2",
# 		"outNode": "node-3",
# 		"outTerminal": "terminal-4",
# 		"type": "egde"
# 	},
# 	"node-1": {
# 		"h": 58,
# 		"id": "node-1",
# 		"terminal": {
# 			"terminal-1": {
# 				"edge": "line-1",
# 				"id": "terminal-1",
# 				"targetNode": "node-3",
# 				"type": "out",
# 				"x": 7706,
# 				"y": 8000
# 			}
# 		},
# 		"type": "start",
# 		"note": None,
# 		"w": 198,
# 		"x": 7525,
# 		"y": 7971
# 	},
# 	"node-2": {
# 		"h": 58,
# 		"id": "node-2",
# 		"terminal": {
# 			"terminal-2": {
# 				"edge": "line-2",
# 				"id": "terminal-2",
# 				"targetNode": "node-3",
# 				"type": "in",
# 				"x": 8294,
# 				"y": 8000
# 			}
# 		},
# 		"type": "end",
# 		"end_type": "5",
# 		"note": None,
# 		"w": 198,
# 		"x": 8277,
# 		"y": 7971
# 	},
# 	"node-3": {
# 		"h": 58,
# 		"id": "node-3",
# 		"terminal": {
# 			"terminal-3": {
# 				"edge": "line-1",
# 				"id": "terminal-3",
# 				"targetNode": "node-1",
# 				"type": "in",
# 				"x": 7895,
# 				"y": 8001
# 			},
# 			"terminal-4": {
# 				"edge": "line-2",
# 				"id": "terminal-4",
# 				"targetNode": "node-2",
# 				"type": "out",
# 				"x": 8106,
# 				"y": 8001
# 			}
# 		},
# 		"type": "movement",
# 		"PATTERN_ID": "1",
# 		"ORCHESTRATOR_ID": "3",
# 		"Name": "NULL",
# 		"OPERATION_NO_IDBH": None,
# 		"SKIP_FLAG": "1",
# 		"OPERATION_NAME": "",
# 		"note": None,
# 		"w": 245,
# 		"x": 7878,
# 		"y": 7972
# 	}
# }
con_class = ConductorCommonLibs()
res = con_class.chk_format_all(data)
print(res)
