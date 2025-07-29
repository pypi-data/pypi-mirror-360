{
    "auth_required": {
        "type": "bool",
        "required": true,
        "default": true,
        "comment": "Whether or not Command requires to be authorized"
    },
    "ui_label": {
        "type": "str",
        "required": true,
        "default": " ",
        "comment": "UI Label"
    },
    "help": {
        "type": "str",
        "required": true,
        "comment": "Command Help"
    },
    "cli_hidden": {
        "required": false,
        "type": "bool",
        "default": false,
        "comment": "Hide from CLI"
    },
    "api_hidden": {
        "required": false,
        "type": "bool",
        "default": true,
        "comment": "Hide from API"
    },
    "args": {
        "type": "dict",
        "required": false,
        "default": {},
        "comment": "Command Argument configurations",
        "spec_chain": "argmap.command.args-root",
        "example": {
            "myarg": {},
            "otherarg": {}
        }
    },
    "group": {
        "type": "str",
        "required": false,
        "default": "",
        "comment": "Command 'group' name for organization"
    }
}