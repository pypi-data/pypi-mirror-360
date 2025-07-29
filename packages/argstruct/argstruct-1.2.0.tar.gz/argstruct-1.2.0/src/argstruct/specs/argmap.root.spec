{
    "commands": {
        "type": "dict",
        "required": true,
        "default": {},
        "comment": "Command Map Information",
        "spec_chain": "argmap.commands",
        "example": {
            "a_command": {},
            "some_command": {}
        }
    },
    "auth_args": {
        "type": "dict",
        "required": false,
        "default": {},
        "comment": "Arguments required when `auth_required=True`",
        "spec_chain": "argmap.command.args-root"
    }
}
