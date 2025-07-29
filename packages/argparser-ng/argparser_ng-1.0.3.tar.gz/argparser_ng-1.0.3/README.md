# Argparser-NG

NextGen Argument Parser

Processes commandline arguments similar to the built-in `argparse`

- [Argparser-NG](#argparser-ng)
  - [Features](#features)
  - [Usage](#usage)
    - [Example Parameter Output](#example-parameter-output)
    - [Example Help Output](#example-help-output)
  - [Controlling Repeatability](#controlling-repeatability)
  - [Functions - Quick](#functions---quick)
  - [Functions - Deep](#functions---deep)
    - [`ArgumentParserNG()`](#argumentparserng)
      - [`ArgumentParserNG.enable_double_dash()`](#argumentparserngenable_double_dash)
      - [`<object>.add_argument_group()`](#objectadd_argument_group)
      - [`<object>.add_argument_item()`](#objectadd_argument_item)
      - [`ArgumentParserNG.add_command()`](#argumentparserngadd_command)
      - [`ArgumentParserNG.reusable_argument_group()`](#argumentparserngreusable_argument_group)
      - [`ArgumentParserNG.parse()`](#argumentparserngparse)
    - [`ParsedArgumentsNG()`](#parsedargumentsng)
      - [`ParsedArgumentsNG.has_value()`](#parsedargumentsnghas_value)
      - [`ParsedArgumentsNG.get_type()`](#parsedargumentsngget_type)
      - [`ParsedArgumentsNG.get_value()`](#parsedargumentsngget_value)
      - [`ParsedArgumentsNG.as_dict()`](#parsedargumentsngas_dict)
      - [`ArgumentParserNG.show_help()`](#argumentparserngshow_help)
      - [`ArgumentParserNG.args`](#argumentparserngargs)
      - [`ArgumentParserNG.command`](#argumentparserngcommand)
  - [Notes](#notes)


## Features

- **TYPED**; Arguments typed, easy to get the type of a parameter
- DoubleDash Argument processing (ex: `foobar.py -- bash`)
- Reusable Argument Groups
- Mutually Exclusive Argument Groups
- Arugment Repeatability Control
- Argument Types can be Any class that accepts a single string parameter (EX: `MyType('foobar')`)
- Command functionality (ex: `foobar.py mycommand --foo`)
- Configurable Argument Indicator (ex: `foobar.py --foo` or `foobar.py /foo`, etc)

## Usage

Create a new ArgumentParser
```python
    parser:ArgumentParserNG = ArgumentParserNG(description="My Cool Program")
```

Add Individual program-level arguments
```python
    parser.add_argument_item(name="baz",flags="baz",help="bazbar",store_type=str,repeatable=ArgumentItemRepeat.REPEAT_APPEND)
    parser.add_argument_item(name="bar",flags="bar",help="barbar",store_type=int)
```

Add an argument with a custom type
```python
    class CustomType:
        __value:str
        def __init__(self,value:str) -> None:
            self.__value = value

    parser.add_argument_item(name="custom",flags="z",help="Custom Flag",store_type=CustomType)
```

Enable Double Dash argument
```python
    parser.enable_double_dash(name="dasharg",help="Shell data",default="/bin/bash")
```

Create a mutually exclusive Argument Group
```python
    arggroup:ArgumentParserGroup = parser.add_argument_group("groupA",exclusive=True,help="An Argument Group")
    arggroup.add_argument_item(name="foo",default=True,flags="foo",help="foobar",store_type=bool)
    arggroup.add_argument_item(name="blam",default=False,flags="bam",help="blambam",store_type=bool)
```

Create a reusable Argument group
```python
    arggroup = parser.reusable_argument_group(name="booflags",help="Flags that go boo in the night",required=True)
    arggroup.add_argument_item(name="boo",flags="boo",help="booooooo",store_type=float)
    arggroup.add_argument_item(name="woo",flags="woo",required=True,help="wooooo",store_type=int)
```

Enable Commands, and add command-specific arguments
```python
    ccommand:ArgumentParserCommand = parser.add_command("coolcommand",help="A Command that does cool things")
    ccommand.add_argument_item(name="coolparam",flags=["cool","C"],help="Cool parameter for cool command")
```

Attach the reusable group to the `coolcommand` command
```python
    ccommand.add_reusable(arggroup)
```

Create another Command, and add the reusable group to it
```python
    ccommand = parser.add_command("neat",help="A Neat command")
    ccommand.add_reusable(arggroup)
```

Process The commandline
```python
    parser.parse()
    args:typing.Union[argparser_ng.ParsedArgumentsNG,None] = parser.args
    if args is None:
        raise SyntaxError("Somethings gone wrong")
```

Get Some Parameters and info about them
```python
    print(args.get_type("booflags.boo"))
    print(args.get_type("custom"))
    print(args.get_value("groupA.subgroupA.subblamA"))
```

Show the Command that was selected, Print the parsed arguments as a dictionary
```python
    print(parser.command)
    print(args.as_dict())
```

### Example Parameter Output

```shell
parsertest.py coolcommand --cool 'cmd commander command' --baz=boo --baz bro --foo --bar 31 -z customarg
# <class 'float'>
# <class '__main__.CustomType'>
# False
# coolcommand
# {'coolparam': 'cmd commander command', 'booflags': {'boo': 90.0, 'wooo': 40}, 'baz': '', 'bar': None, 'custom': <__main__.CustomType object at 0x76c52a430af0>, 'dasharg': '/bin/bash', 'groupA': {'subgroupA': {'subfooA': True, 'subblamA': False}, 'subgroupB': {'subfooB': False, 'subblamB': False}}}
```

### Example Help Output

```text
$: parsertest.py --help
parsertest.py - My Cool Program:

Usage: parsertest.py <command> [flags]
Commands: coolcommand neat
        Use --help <command> for more help

Common Arguments:
                -h      <str>                   None
                        alternatives: --help
                --baz   <str>                   bazbar
                --bar   <int>                   barbar
                -z      <str>                   Custom Flag
                --      <str>                   Shell data
                        default: /bin/bash
                        must be last argument
                Group: groupA, exclusive: yes
                        Sub Group: subgroupA, exclusive: yes
                                --afoo  <bool>                  foobar
                                        default: True
                                --abam  <bool>                  blambam
                                        default: False
                        Sub Group: subgroupB, exclusive: yes
                                --bfoo  <bool>                  foobar
                                        default: True
                                        alternatives: --boo-foo
                                --bbam  <bool>                  blambam
                                        default: False
```

```text
$: parsertest.py --help coolcommand
parsertest.py - My Cool Program:

Usage: parsertest.py coolcommand [common-flags] [flags]
See --help for common-flags
Help for command coolcommand
        --cool  <str>                   Cool parameter for cool command
                alternatives: -C
        Group: booflags, exclusive: no
                --boo   <float>                 booooooo
                        required
                --wooo  <int>                   woooo
                        required
```
## Controlling Repeatability

Argument Items can be repeatable, if enabled. The `repeatable` flag of `ArgumentParserNG.add_argument_item()` accepts one of the values below:

- `ArgumentItemRepeat.REPEAT_NO`: Do not allow repeats, complain if found
- `ArgumentItemRepeat.REPEAT_REPLACE`: Replace the value with the subsequent values
- `ArgumentItemRepeat.REPEAT_APPEND`: Turn the value into a list, and append subsequent values.

## Functions - Quick

- `ArgumentParserNG()` - Main Class
  - `<object>.add_argument_item()` - Create an Argument Item
    - Supported for `ArgumentParserNG()`, `ArgumentParserCommand()`, `ArgumentParserGroup()`
    - ***Nested Items are NOT supported***; They never will be.
  - `<object>.add_argument_group()` - Create an Argument Group
    - Supported for `ArgumentParserNG()`, `ArgumentParserCommand()`, `ArgumentParserGroup()`
  - `<object>.add_reusable()` - Add Reusable Group
    - Reusable Groups can be added to `ArgumentParserCommand()`, `ArgumentParserGroup()`
    - Technically also supported for `ArgumentParserNG()`, but theres no reason to do this
  - `ArgumentParserNG().enable_double_dash()` - Enable DoubleDash Argument
  - `ArgumentParserNG().reusable_argument_group()` - Create a Reusable Argument Group
    - Reusable Groups can be added to `ArgumentParserNG()`, `ArgumentParserCommand()`
    - Must be attached via `<object>.add_reusable()`
  - `ArgumentParserNG().add_command()` - Enable and Create a Command
  - `ArgumentParserNG().parse()` - Parse Commandline and make Arguments available
  - `ArgumentParserNG().args` - Processed Arguments, only available after `parse()` is called
  - `ArgumentParserNG().command` - Name of Command called, if Commands have been added
    - ***Nested Commands are NOT supported currently***; They may succeed in being added, but processing will fail
  - `ArgumentParserNG().show_help()` - Show Help Menu
- `ParsedArgumentsNG()` - Parsed Arguments Container
  - `ParsedArgumentsNG().has_value()` - Check whether parameter exists
  - `ParsedArgumentsNG().get_type()` - Get Type of parameter
  - `ParsedArgumentsNG().get_value()` - Get Value of parameter
  - `ParsedArgumentsNG().as_dict()` - Get Parsed Arguments as Dictionary

## Functions - Deep

Documents are also available via Doxygen

### `ArgumentParserNG()`
```python
ArgumentParserNG(
    typing.Union[str,None]  	    program_name = None,
    typing.Union[str,None]  	    description = None,
    str   	                        argument_indicator = "-",
    bool  	                        sort_commands = True
)
```

Create a New Parser

Parameters
```
    program_name	    Union[str,None]     Name of Program (default to $0)
    description 	    Union[str,None]     Program Description
    argument_indicator	str                 Flag Indicator single will be used for len = 1 flags, double for len > 1
    sort_commands       bool                Whether or not to sort Commands, default True 
```

#### `ArgumentParserNG.enable_double_dash()`
```python
ArgumentParserNG.enable_double_dash (
    str  	                            name,
    typing.Union[str,list[str],None]  	help = None,
    typing.Union[list[typing.Any],None] values = None,
    typing.Any  	                    default = None,
    bool  	                            required = False
) -> None
```
Enable Double Dash commands (ex: `foobar.py -- bash`)

Value is always stored as a string

Parameters
```
    name	    str                         Name of parameter
    help        Union[str,list[str],None]   Help string
    values	    Union[list[Any],None]       Acceptable Value list
    default	    Any                         Default value
    required	bool                        Whether or not parameter is required
```
#### `<object>.add_argument_group()`
```python
<object>.add_argument_group (
    typing.Union[str,None]              name = None,
    typing.Union[str,list[str],None]  	help = None,
    bool                                required = False,
    bool                                exclusive = False
) -> ArgumentParserGroup
```
Add a new Argument Group, returns the created Group.

Parameters
```
    name	    str                         Name of Group to create
    help	    Union[str,list[str],None]   Help String
    required	bool                        Whether or not group is required
    exclusive	bool                        Whether parameters in group are exclusive to eachother (only one can be set)
```

#### `<object>.add_argument_item()`
```python
<object>.add_argument_item (
    typing.Union[str,list[str]]  	    flags,
    typing.Union[str,None]  	        name = None,
    typing.Union[str,list[str],None]  	help = None,
    typing.Union[typing.Type,None]  	store_type = None,
    typing.Union[list[typing.Any],None] values = None,
    typing.Any  	                    default = None,
    bool  	                            required = False,
    typing.Union["ArgumentItemRepeat",None] repeatable = None
) -> None
```

Add a new Argument Item.

`store_type` may be any Type, but the Type must accept a string as its only input; ex: `MyType(value:str)`

Parameters
```
    name	    str                         Name of parameter
    flags	    Union[str,list[str]]        List of Flags Argument will listen to, do not include the argument indicators (dashes, for example)
    help	    Union[str,list[str],None]   Help string
    store_type	Union[Type,None]            Type of value to store as
    values	    Union[list[Any],None]       Acceptable Value list
    default	    Any                         Default value
    required	bool                        Whether or not parameter is required
    repeatable	ArgumentItemRepeat          Whether or not this item can repeat, and if so, how its handled
```

#### `ArgumentParserNG.add_command()`
```python
ArgumentParserNG.add_command (
    str  	                            name,
    typing.Union[str,list[str],None]  	help = None
) -> ArgumentParserCommand
```

Add a New Command / Section, returns the created Command.

Parameters
```
    name         str                        Command Name / Command
    help	     Union[str,list[str],None]  Help String
```

#### `ArgumentParserNG.reusable_argument_group()`
```python
ArgumentParserNG.reusable_argument_group (
    typing.Union[str,None]  	        name = None,
    typing.Union[str,list[str],None]  	help = None,
    bool  	                            required = False,
    bool  	                            exclusive = False
) -> ArgumentParserGroup
```

Create a reusable Group that can be attached many times, returns the created Group.

Parameters
```
    name	    str                         Name of Group to create
    help	    Union[str,list[str],None]   Help String
    required	bool                        Whether or not group is required
    exclusive	bool                        Whether parameters in group are exclusive to eachother (only one can be set)
```

#### `ArgumentParserNG.parse()`
```python
ArgumentParserNG.parse()
```

Process Commandline arguments using the configured parser data

No Parameters

### `ParsedArgumentsNG()`
```python
ParsedArgumentsNG(
    dict[str,Any]                       args    Argument dictionary
)
```

Parameters
```
    args   dict[str,Any]                         Argument Dictionary from ArgumentParserNG
```

#### `ParsedArgumentsNG.has_value()`
```python
ParsedArgumentsNG.has_value(
    str                                 parameter
)
```

Parameters
```
    parameter   str                         Parameter for to get. Use "foo.bar.baz" to the existence of `{ "foo": { "bar": { "baz": "boooo" } } }`
```

#### `ParsedArgumentsNG.get_type()`
```python
ParsedArgumentsNG.get_type(
    str                                 parameter
) -> Type
```

Get Type of Parameter

Parameters
```
    parameter   str                         Parameter for to get. Use "foo.bar.baz" to get the type of `{ "foo": { "bar": { "baz": "boooo" } } }`
```

#### `ParsedArgumentsNG.get_value()`
```python
ParsedArgumentsNG.get_value(
    str                                 parameter
) -> Any
```

Get Parameter

Parameters
```
    parameter   str                         Parameter for to get. Use "foo.bar.baz" to get the value of `{ "foo": { "bar": { "baz": "boooo" } } }`
```

#### `ParsedArgumentsNG.as_dict()`
```python
ParsedArgumentsNG.as_dict() -> dict[str,Any]
```

Get Parsed Arguments as dictionary

No Parameters
#### `ArgumentParserNG.show_help()`
```python
ArgumentParserNG.show_help(
    str  	                            section = "help_short" 
)
```

HelpMenu Generator.

Parameters
```
    section	    str                         Help Section to show, default 'help_short' shows command list, and command parameters 
```

#### `ArgumentParserNG.args`
Property - Type: `dict[str,Any]`
Property which provides the parsed arguments. Only available after `ArgumentParserNG.parse()` has been called.

#### `ArgumentParserNG.command`
Property - Type: `str`
Property which provides the parsed command. Only available after `ArgumentParserNG.parse()`, and only if an `ArgumentParserNG.add_command()` has been used

## Notes

- Arguments are displayed in help in the order that they are provided. To make it easier on the end user, program-specific arguments should be defined before group arguments.
- When using `enable_double_dash()`, the argument is added at the time of function call. To make it easier on the end user, this should be defined after program-specific arguments, but before group arguments
- Flags automatically get their argument indicators. Single character flags get a single indicator (ex: `-f`), and Word flags get a double indicator (ex: `--foo`)
