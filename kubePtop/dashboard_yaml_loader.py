import os
import yaml
import json
from cerberus import Validator
import rich
class dashboardYamlLoader:
    def __init__(self) -> None:
        self.allowed_metric_unit_types = [
            'None',
            'kb',
            'byte',
            'mb',
            'gb',
            'tb',
            'seconds',
            'percentage'
        ]
        self.allowed_data_types = [
            'asciiGraph',
            'progressBarList',
            'simpleTable',
            'advancedTable',
        ]

    def validate_dashboard_schema(self, dashboard_yaml_data):
        schema_dct = {

            "dashboard": {
                'type': 'dict',
                'required': True,
                'schema': {
                    "name": {
                        'type': 'string',
                        'required': True,
                    },
                    "description": {
                        'type': 'string',
                        'required': False,
                        'default': ""
                    },
                    "layout": {
                        'type': 'dict',
                        'required': True,
                        'schema': {
                            'splitMode': {
                                "type": "string",
                                'required': False,
                                'default': 'row',
                                'allowed': [
                                    'row',
                                    'column'
                                ]
                            },
                            'fullScreen': {
                                "type": "boolean",
                                'required': False,
                                'default': True,
                                'allowed': [
                                    True,
                                    False
                                ]
                            },
                            "header": {
                                'type': 'dict',
                                'required': False,
                                'schema': {
                                    'enable': {
                                        "type": "boolean",
                                        'required': False,
                                        'default': False
                                    },
                                    'size': {
                                        "type": "integer",
                                        'required': False,
                                        'default': 0
                                    },
                                    'ratio': {
                                        "type": "integer",
                                        'required': True,
                                        'default': 1
                                    },
                                }
                            },
                            'body': {
                                    'type': 'dict',
                                    'schema': {
                                        'boxes': {
                                            'type': 'dict',
                                            'schema': {
                                                'left': {
                                                    'type': 'dict',
                                                    'required': True,
                                                    'schema': {
                                                        'enable': {
                                                            'type': 'boolean',
                                                            'required': False,
                                                            'default': False,
                                                        },
                                                        'size': {
                                                            'type': 'integer',
                                                            'required': False,
                                                            'default': 0
                                                        },
                                                        'ratio': {
                                                            'type': 'integer',
                                                            'required': False,
                                                            'default': 1
                                                        },
                                                        'split_mode': {
                                                            'type': 'string',
                                                            'required': False,
                                                            'default': 'row',
                                                            'allowed': [
                                                                'row',
                                                                'column'
                                                            ]
                                                        },
                                                        'split': {
                                                            'type': 'dict',
                                                            'required': False,
                                                            'allow_unknown': True,
                                                            'schema': {
                                                                'size': {
                                                                    'type': 'integer',
                                                                    'required': False,
                                                                    'default': 0
                                                                },
                                                                'ratio': {
                                                                    'type': 'integer',
                                                                    'required': False,
                                                                    'default': 1
                                                                }
                                                            }
                                                        }
                                                    }
                                                },
                                                'middle': {
                                                    'type': 'dict',
                                                    'required': True,
                                                    'schema': {
                                                        'enable': {
                                                            'type': 'boolean',
                                                            'required': False,
                                                            'default': False
                                                        },
                                                        'size': {
                                                            'type': 'integer',
                                                            'required': False,
                                                            'default': 0
                                                        },
                                                        'ratio': {
                                                            'type': 'integer',
                                                            'required': False,
                                                            'default': 1
                                                        },
                                                        'split_mode': {
                                                            'type': 'string',
                                                            'required': False,
                                                            'default': 'row',
                                                            'allowed': [
                                                                'row',
                                                                'column'
                                                            ]
                                                        },
                                                        'split': {
                                                            'type': 'dict',
                                                            'required': False,
                                                            'allow_unknown': True,
                                                            'schema': {
                                                                'size': {
                                                                    'type': 'integer',
                                                                    'required': False,
                                                                    'default': 0
                                                                },
                                                                'ratio': {
                                                                    'type': 'integer',
                                                                    'required': False,
                                                                    'default': 1
                                                                }
                                                            }
                                                        }
                                                    }
                                                },
                                                'right': {
                                                    'type': 'dict',
                                                    'required': True,
                                                    'schema': {
                                                        'enable': {
                                                            'type': 'boolean',
                                                            'required': False,
                                                            'default': False,
                                                        },
                                                        'size': {
                                                            'type': 'integer',
                                                            'required': False,
                                                            'default': 0
                                                        },
                                                        'ratio': {
                                                            'type': 'integer',
                                                            'required': False,
                                                            'default': 1
                                                        },
                                                        'split_mode': {
                                                            'type': 'string',
                                                            'required': False,
                                                            'default': 'row',
                                                            'allowed': [
                                                                'row',
                                                                'column'
                                                            ]
                                                        },
                                                        'split': {
                                                            'type': 'dict',
                                                            'required': False,
                                                            'allow_unknown': True,
                                                            'schema': {
                                                                'size': {
                                                                    'type': 'integer',
                                                                    'required': False,
                                                                    'default': 0
                                                                },
                                                                'ratio': {
                                                                    'type': 'integer',
                                                                    'required': False,
                                                                    'default': 1
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                },
                        }
                    },
                    'variables': {
                        'type': 'list',
                        'schema': {
                            'type': 'dict',
                            'schema': {
                                'name': {
                                    'type': 'string',
                                    'required': True
                                },
                                'default': {
                                    'type': 'string',
                                    'required': True,
                                },
                                'cliArgument': {
                                    'type': 'dict',
                                    'schema': {
                                        'enable': {
                                            'type': 'boolean',
                                            'required': True
                                        },
                                        'short': {
                                            'type': 'string',
                                            'required': True,
                                            'regex': r'^-\w{1,2}$'
                                        },
                                        'required': {
                                            'type': 'boolean',
                                            'default': True,
                                            'required': False
                                        },
                                        'description': {
                                            'type': 'string',
                                            'required': False
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'visualization': {
                            'type': 'list',
                            'schema': {
                                'type': 'dict',
                                'allow_unknown': False,
                                'schema': {
                                    'name': {
                                        'type': 'string',
                                        'required': True
                                    },
                                    'box': {
                                        'type': 'string',
                                        'required': True
                                    },
                                    'enable': {
                                        'type': 'boolean',
                                        'required': False,
                                        'default': True
                                    },
                                    'type': {
                                        'type': 'string',
                                        'required': True,
                                        'allowed': self.allowed_data_types
                                    },
                                    'metricUnit': {
                                        'type': 'string',
                                        'required': False,
                                        'default': 'None',
                                        'allowed': self.allowed_metric_unit_types
                                    },
                                    'asciiGraphMetric': {
                                        'type': 'string',
                                        'required': False
                                    },
                                    'progressBarListMetrics': {
                                        'type': 'dict',
                                        'required': False
                                    },
                                    'simpleTableMetric': {
                                        'type': 'string',
                                        'required': False
                                    },
                                    'customKey': {
                                        'type': 'string',
                                        'default': '',
                                        'required': False,
                                    },
                                    'asciiGraphOptions': {
                                        'type': 'dict',
                                        'schema': {
                                            'height': {
                                                'type': 'integer',
                                                'required': False,
                                                'default': 0,
                                            },
                                            'width': {
                                                'type': 'integer',
                                                'required': False,
                                                'default': 80,
                                            },
                                            'maxHeight': {
                                                'type': 'integer',
                                                'required': False,
                                                'default': 17,
                                            },
                                            'maxWidth': {
                                                'type': 'integer',
                                                'required': False,
                                                'default': 45,
                                            },
                                            'updateIntervalSeconds': {
                                                'type': 'integer',
                                                'required': False,
                                                'default': 5,
                                            }
                                        }
                                    },
                                    'progressBarListOptions': {
                                        'type': 'dict',
                                        'schema': {
                                            'maxItemsCount': {
                                                'type': 'integer',
                                                'required': False,
                                                'default': 0,
                                            },
                                            'lineBreak': {
                                                'type': 'boolean',
                                                'required': False,
                                                'default': True,
                                            },
                                            'showBarPercentage': {
                                                'type': 'boolean',
                                                'required': False,
                                                'default': True,
                                            },
                                            'barWidth': {
                                                'type': 'integer',
                                                'required': False,
                                                'default': 25,
                                            },
                                            'updateIntervalSeconds': {
                                                'type': 'integer',
                                                'required': False,
                                                'default': 5,
                                            }
                                        }
                                    },
                                    'simpleTableOptions': {
                                        'type': 'dict',
                                        'schema': {
                                            'tableType': {
                                                'type': 'string',
                                                'required': False,
                                                'default': 'plain',
                                                'allowed': [
                                                    'plain',
                                                    'simple',
                                                    'github',
                                                    'grid',
                                                    'simple_grid',
                                                    'rounded_grid',
                                                    'heavy_grid',
                                                    'mixed_grid',
                                                    'double_grid',
                                                    'fancy_grid',
                                                    'outline',
                                                    'simple_outline',
                                                    'rounded_outline',
                                                    'heavy_outline',
                                                    'mixed_outline',
                                                    'double_outline',
                                                    'fancy_outline',
                                                    'pipe',
                                                    'orgtbl',
                                                    'asciidoc',
                                                    'jira',
                                                    'presto',
                                                    'pretty',
                                                    'psql',
                                                    'rst',
                                                    'mediawiki',
                                                    'moinmoin',
                                                    'youtrack',
                                                    'html',
                                                    'unsafehtml',
                                                    'latex',
                                                    'latex_raw',
                                                    'latex_booktabs',
                                                    'latex_longtable',
                                                    'textile',
                                                    'tsv',
                                                ]
                                            },
                                            'showValue': {
                                                'type': 'boolean',
                                                'required': True,
                                                'default': True,
                                            },
                                            'headersUppercase': {
                                                'type': 'boolean',
                                                'required': True,
                                                'default': True,
                                            },
                                            'autoConvertValue': {
                                                'type': 'boolean',
                                                'required': True,
                                                'default': False,
                                            },
                                            'showTableIndex': {
                                                'type': 'boolean',
                                                'required': True,
                                                'default': False,
                                            },
                                            'updateIntervalSeconds': {
                                                'type': 'integer',
                                                'required': True,
                                                'default': 5,
                                            }
                                        }
                                    },
                                    'advancedTableColumns': {
                                        'type': 'list',
                                        'required': False,
                                        'schema': {
                                            'type': 'dict',
                                            'required': True,
                                            'allow_unknown': True,
                                            'schema': {
                                                'metric': {
                                                    'type': 'string',
                                                    'required': True
                                                },
                                                'metricUnit': {
                                                    'type': 'string',
                                                    'required': False,
                                                    'default': 'None',
                                                    'allowed': self.allowed_metric_unit_types
                                                },
                                                'valueFromLabel': {
                                                    'type': 'string',
                                                    'required': False,
                                                    'default': "",
                                                }
                                            }
                                        }
                                    },
                                    'advancedTableOptions': {
                                        'type': 'dict',
                                        'allow_unknown': False,
                                        'schema': {
                                            'tableType': {
                                                'type': 'string',
                                                'required': False,
                                                'default': 'plain',
                                                'allowed': [
                                                    'plain',
                                                    'simple',
                                                    'github',
                                                    'grid',
                                                    'simple_grid',
                                                    'rounded_grid',
                                                    'heavy_grid',
                                                    'mixed_grid',
                                                    'double_grid',
                                                    'fancy_grid',
                                                    'outline',
                                                    'simple_outline',
                                                    'rounded_outline',
                                                    'heavy_outline',
                                                    'mixed_outline',
                                                    'double_outline',
                                                    'fancy_outline',
                                                    'pipe',
                                                    'orgtbl',
                                                    'asciidoc',
                                                    'jira',
                                                    'presto',
                                                    'pretty',
                                                    'psql',
                                                    'rst',
                                                    'mediawiki',
                                                    'moinmoin',
                                                    'youtrack',
                                                    'html',
                                                    'unsafehtml',
                                                    'latex',
                                                    'latex_raw',
                                                    'latex_booktabs',
                                                    'latex_longtable',
                                                    'textile',
                                                    'tsv',
                                                ]
                                            },
                                            'headersUppercase': {
                                                'type': 'boolean',
                                                'required': True,
                                                'default': True,
                                            },
                                            'showTableIndex': {
                                                'type': 'boolean',
                                                'required': True,
                                                'default': False,
                                            },
                                            'updateIntervalSeconds': {
                                                'type': 'integer',
                                                'required': True,
                                                'default': 5,
                                            }
                                        }
                                    }
                                }
                            }
                        }
                }
            },
        }

        v = Validator(schema_dct)
        v.validate(dashboard_yaml_data)
        if v.errors:
            import re
            yaml_errors = yaml.dump(v.errors, default_flow_style=False)

            # Regex to find "unknown field" and "must be of"
            yaml_errors = re.sub(r'(unknown field)', '[red]\\1[/red]', yaml_errors)
            yaml_errors = re.sub(r'(must be of.*)', '[red]\\1[/red]', yaml_errors)
            yaml_errors = re.sub(r'(unallowed value.*)', '[red]\\1[/red]', yaml_errors)
            yaml_errors = re.sub(r'(required field.*)', '[red]\\1[/red]', yaml_errors)
            yaml_errors = re.sub(r'(null value not allowe.*)', '[red]\\1[/red]', yaml_errors)

            print("ERROR -- Please fix the following in the dashboard YAML file:\n")
            rich.print("[bold]" + yaml_errors)
            exit(1)


    def load_dashboard_data(self, command_content_content):
        out = {
            "success": False,
            "data": None,
            "fail_reason": ""
        }
        # Read the file
        try:
            # with open(yaml_file, 'r') as file:
                # content = file.read()
            out['data'] = yaml.safe_load(command_content_content)
        except Exception as e:
            out['fail_reason'] = f"Failed to open the dashboard file content > {e}"
            return out

        # Yaml Schema validation
        self.validate_dashboard_schema(out['data'])


        out['success'] = True
        return out
