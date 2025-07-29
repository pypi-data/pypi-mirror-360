# ArgStruct - Reusable Argument Structure

- [ArgStruct - Reusable Argument Structure](#argstruct---reusable-argument-structure)
  - [About](#about)
  - [Usage](#usage)
  - [Examples](#examples)
    - [Example Structure](#example-structure)
    - [Loading ArgStruct for Console Processing](#loading-argstruct-for-console-processing)
    - [Loading ArgStruct for API / Misc Processing](#loading-argstruct-for-api--misc-processing)
  - [Internals](#internals)
  - [Additional Notes](#additional-notes)
    - [Example; Documentation generation with additional data](#example-documentation-generation-with-additional-data)

## About

This library is intended to provide a structure for Arguments and API/ABI processing in a way that allows for the same structure to be reused for other things without duplication. This allows the same structure to generate documentation, code blocks, and other things, without having to duplicate data elsewhere. 

This library uses the [ArgStruct Specification](https://gitlab.com/accidentallythecable-public/argstruct-spec)

**ArgStruct Specification: 1.1**

## Usage

First, an [ArgStruct](https://gitlab.com/accidentallythecable-public/argstruct-spec) Map must be created. an ArgStruct is made up of many ArgStructCommands.

Each `ArgStructCommand` requires [some options](SPECS.md#spec-for-argmapcommand) in order to build up a Command. Within each `ArgStructCommand` is a dictionary of arguments (can be converted to a `ArgStructArgument`) and their configurations. Once the [ArgStruct](https://gitlab.com/accidentallythecable-public/argstruct-spec) Map is built, it can be utilized by loading the file (or its contents) into an `ArgStruct` object.

This library provides 3 methods for processing:

 - `console`: Build CLI/Console arguments via `argparse`. A top level `argparse.ArgumentParser` must be created first.
 - `api`: Build API/Misc arguments via callback methods. Callback methods must be created for command processing and argument processing.
 - `parse`: Process either an `argparse.ArgumentParser` or a dictionary, validate and return the built values, including defaults from the ArgStruct Map

Additionally, this library provides a script, `argstruct-doc` to generate Markdown documentation from an [ArgStruct](https://gitlab.com/accidentallythecable-public/argstruct-spec). The `api` method can be utilized for generating code or other structures that are not console specific. 

## Examples

### Example Structure

```toml
# These Arguments are automatically appended to any command which has `auth_required=True`
[auth_args.some_argument]
required = false
type = "str"
cli_flag_names = [ "-s", "--some-argument" ]
help = "My Argument Help info"
[auth_args.other_argument]
required = false
type = "str"
cli_flag_names = [ "-o", "--other-argument" ]
help = "My Other Help Info"
[auth_args.choice_argument]
required = false
type = "str"
cli_flag_names = [ "-c", "--choice-argument" ]
help = "An argument with allowable values"
values = [ "a", "foo", "bar" ]

# A new Command with Arguments
[commands.mycommand]
auth_required = false
cli_hidden = true
api_hidden = false
help = "My Command Level Help"
group = "My Group Label"
ui_label = "My UI/Documentation Label"
[commands.mycommand.args.mycommand_first_arg]
cli_flag_names = [ "-f", "--my-first-arg" ]
type = "int"
required = false
default = 5
help = "My First Arg Help"
[commands.mycommand.args.second_arg]
cli_flag_names = [ "-a", "--some-second-arg" ]
type = "str"
required = true
help = "My Second Arg Help"

[commands.othercommand]
....
```

### Loading ArgStruct for Console Processing

```python
# Create a Path object pointing to the ArgMap
commandmap_file:Path = Path("./testmap.toml").resolve()

# Load the ArgMap, if the file has a non-standard file extension (ex not `json`, `yml`, `yaml` or `toml`),
#   then you need to specify the second argument accordingly. Default is `auto` and automatically determines
#   based on file extension
argstruct_obj:ArgStruct = ArgStruct(commandmap_file,ArgStruct.OVERRIDE_TYPE_TOML)

# Create a new argparse.ArgumentParser to serve as the root of all commands and arguments
parser:argparse.ArgumentParser = argparse.ArgumentParser(description="My CLI App")
# Add any top level arguments, if required
parser.add_argument("-v","--verbose",help="Turn on Debugging",action="store_true")

# Create and utilize the Console(CLI)-specific Commands via argparse, creating a new subparser whose `dest="command"` and is `required`
console(argstruct_obj,parser,True,{ "dest": "command", "required": True })

# Parse arguments, set defaults, validate and return back a dictionary of CLI Arguments
request:typing.Union[dict[str,typing.Any],None] = parse(argstruct_obj,parser)

# Output the Arguments
print(request)
```

### Loading ArgStruct for API / Misc Processing

Unlike the Console example, Not all API/ABIs are the same, so, you will need to define some callback methods that will be utilized.

```python

# Create a per-command Callback, this will be called for each Command in the ArgStruct. `result` and the return value 'should' be the same object
def command_cb(command:str,command_config:ArgStructCommand,cb_args:typing.Any,result:typing.Any) -> typing.Any:
    if result is None:
        result = []
    print(f"Hello I am Command {command}")
    result.append({
        "command": command,
        "auth": command_config.get("auth_required"),
        "args": {}
    })
    return result

# Create a per-argument Callback, this will be called for Each Argument in each Command in the ArgStruct. `result` and the return value 'should' be the same object
def arg_cb(command:str,command_config:ArgStructCommand,argument:str,arg_config:dict[str,typing.Any],cb_args:typing.Any,result:typing.Any) -> typing.Any:
    argtype:str = arg_config["type"]
    print(f" - Command {command} Argument: {argument}, type: {argtype}")
    cmd_idx:int = len(result) - 1
    if "args" not in result[cmd_idx].keys():
        result[cmd_idx]["args"] = {}
    result[cmd_idx]["args"][argument] = {
        "argument": argument,
        "default": arg_config["default"]
    }
    return result


# Create a Path object pointing to the ArgMap
commandmap_file:Path = Path("./testmap.toml").resolve()

# Load the ArgMap, if the file has a non-standard file extension (ex not `json`, `yml`, `yaml` or `toml`),
#   then you need to specify the second argument accordingly. Default is `auto` and automatically determines
#   based on file extension
argstruct_obj:ArgStruct = ArgStruct(commandmap_file,ArgStruct.OVERRIDE_TYPE_TOML)

# Build some Argument Structure for your API using the command and argument callbacks
api_argdata:dict[str,typing.Any] = api(argstruct_obj,command_cb,arg_cb,None,None)
print(api_argdata)

# Generate your API Request Data
my_request_data:dict[str,typing.Any] = ... # Do something to generate your API data

# Parse arguments, set defaults, validate and return back a dictionary of API Arguments
request:typing.Union[dict[str,typing.Any],None] = parse(argstruct_obj,my_request_data)
print(request)
```

## Internals

This library utilizes `argparse`, or `argparser-ng` at the core for its CLI/Console processing. `specker` manages the argmap structure, validation and, defaults. Additionally uses `tabulate` in order to generate markdown tables.

`argparser-ng` is the default CLI parser, if available

## Additional Notes

If you wish to add additional required values, etc, you can override any of the specs in the `argstruct/specs/` directory, and then load them when creating the `ArgStruct` object via `additional_argmap_specs`. These values will not be documented through `argstruct-doc`, and will need to run `markdown_documentation()` after creating some callback methods to include your additional data.

### Example; Documentation generation with additional data

```python
# Create a per-command Callback, this will be called for each Command in the ArgStruct. `result` and the return value 'should' be the same object.
# This callbacks input `result` will be a str, and its return type should also be the same str with appended data
def command_cb(command:str,command_config:ArgStructCommand,cb_args:typing.Any,result:typing.Any) -> typing.Any:
    if result is None:
        result = ""
    result += f"Hello I am Command {command}\n"
    result += "'command': command\n"
    result += "'auth': " + ("Y\n" if command_config.get("auth_required") else "N\n")
    return result

# Create a per-argument Callback, this will be called for Each Argument in each Command in the ArgStruct. `result` and the return value 'should' be the same object
# This callbacks input `result` will be a list[str], and its return type should be the same list, with additional columns.
def arg_cb(command:str,command_config:ArgStructCommand,argument:str,arg_config:dict[str,typing.Any],cb_args:typing.Any,result:typing.Any) -> typing.Any:
    argtype:str = arg_config["type"]
    result.append(f" - Command {command} Argument: {argument}, type: {argtype}\n")
    result.append(f"'argument': {argument}\n")
    result.append(f"'default': {arg_config['default']}\n")
    return result

# A List of additional argument columns
extra_cols:list[str] = ["Rand 1","Rand 2","Rand 3"]

print(markdown_documentation(argstruct_file,True,True,extra_cols,command_cb,None,arg_cb,None))
```
