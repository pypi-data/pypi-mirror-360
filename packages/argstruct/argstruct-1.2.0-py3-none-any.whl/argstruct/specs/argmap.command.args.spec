{
    "type": {
        "type": "str",
        "required": true,
        "comment": "Argument value type",
        "values": [ "any", "str", "int", "list", "dict", "float", "bool" ]
    },
    "required": {
        "type": "bool",
        "required": true,
        "default": false,
        "comment": "Whether or not Argument is required"
    },
    "default": {
        "type": "any",
        "required": false,
        "comment": "Default Argument Value"
    },
    "help": {
        "type": "str",
        "required": true,
        "comment": "Argument Help Text"
    },
    "cli_flag_names": {
        "type": "list",
        "required": true,
        "comment": "Commandline Flag Name(s)",
        "example": [
            "--my-arg", "-M"
        ]
    },
    "multi": {
        "type": "bool",
        "required": false,
        "default": false,
        "comment": "Whether or not to set `nargs='+'`"
    },
    "any_arg": {
        "type": "bool",
        "required": false,
        "default": false,
        "comment": "Used when multi=true, allows for `--<arg_name> k=v` and breaking `args[arg_name] = [ 'k=v' ]` to dict"
    },
    "values": {
        "type": "list",
        "required": false,
        "default": null,
        "comment": "Allowable values for argument",
        "example": [
            "a", "foo", "bar"
        ]
    }
}