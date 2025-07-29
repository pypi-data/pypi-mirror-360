{
    "__any_item__": {
        "type": "any",
        "required": false,
        "comment": "Data Definition",
        "spec_chain": "argmap.command.args",
        "example": {
            "myarg": {
                "type": "str",
                "cli_flag_names": [ "-M", "--my-arg" ],
                "required": true,
                "help": "My Argument"
            },
            "otherarg": {
                "type": "str",
                "cli_flag_names": [ "-z", "--other-arg" ],
                "required": true,
                "help": "My Other Argument"
            }
        }
    }
}
