# Copyright 2025-2025 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of NextGen Argument Parser,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing
from sys import argv, stderr
from sys import exit as sys_exit

from argparser_ng.parts import ArgumentBase,ArgumentItemRepeat,ArgumentParserCommand,ArgumentParserGroup,ArgumentParserItem

def _tabs(count:int) -> str:
    """Dirty Tab builder
    @param count int number of tabs
    @retval string of tabs
    """
    return ''.join(["\t" for _ in range(0,count)])

class ParsedArgumentsNG:
    """Parsed Arguments Container"""
    _subargs:dict[str,"ParsedArgumentsNG"]
    _subitems:list[str]
    _args:dict[str,typing.Any]
    _types:dict[str,typing.Type]
    _original:dict[str,typing.Any]

    def __init__(self,args:dict[str,typing.Any]) -> None:
        """Init
        @param args dict[str,Any] Dictionary of arguments
        """
        self._subargs = {}
        self._args = {}
        self._subitems = []
        self._types = {}
        self._original = args
        for k,v in args.items():
            if isinstance(v,dict):
                self._subitems.append(k)
                self._subargs[k] = ParsedArgumentsNG(v)
            else:
                self._types[k] = type(v)
                self._args[k] = v

    def as_dict(self) -> dict[str,typing.Any]:
        """Return Arguments as the original dictionary
        @retval dict[str,Any]
        """
        return self._original

    def get_type(self,parameter:str) -> typing.Union[typing.Type,None]:
        """Get Parameter Type
        @param parameter str Parameter for to get. Use "foo.bar.baz" to get the value of `{ "foo": { "bar": { "baz": "boooo" } } }`
        @raises KeyError Ending must be an item, subsections arent allowed to be returned
        """
        if "." in parameter:
            parts:list[str] = parameter.split(".")
            this_param:str = parts.pop(0)
            return self._subargs[this_param].get_type('.'.join(parts))
        if parameter not in self._args.keys():
            e:str = f"No such parameter '{parameter}'; Available parameters: {', '.join(list(self._args.keys()))}; Available subsections: {', '.join(self._subitems)}"
            raise KeyError(e)
        return self._types[parameter]

    def has_value(self,parameter:str) -> bool:
        """Check if parameter exists
        @param parameter str Parameter for to get. Use "foo.bar.baz" to get the value of `{ "foo": { "bar": { "baz": "boooo" } } }`
        @retval bool Whether or not parameter exists
        """
        if "." in parameter:
            parts:list[str] = parameter.split(".")
            this_param:str = parts.pop(0)
            return self._subargs[this_param].has_value('.'.join(parts))
        if parameter not in self._args.keys():
            return False
        return True

    def get_value(self,parameter:str) -> typing.Any:
        """Get Value of parameter
        @param parameter str Parameter for to get. Use "foo.bar.baz" to get the value of `{ "foo": { "bar": { "baz": "boooo" } } }`
        @raises KeyError Ending must be an item, subsections arent allowed to be returned
        @retval Any Item discovered
        """
        if "." in parameter:
            parts:list[str] = parameter.split(".")
            this_param:str = parts.pop(0)
            return self._subargs[this_param].get_value('.'.join(parts))
        if parameter not in self._args.keys():
            e:str = f"No such parameter '{parameter}'; Available parameters: {', '.join(list(self._args.keys()))}; Available subsections: {', '.join(self._subitems)}"
            raise KeyError(e)
        return self._args[parameter]

class ArgumentParserNG(ArgumentBase):
    """Argument Parser, NextGeneration
    Read Commandline Arguments from sys.argv and process them into a usable dictionary
    """
    program:str
    description:typing.Union[str,None]
    sort_commands:bool

    __arglist:list[str]
    _argument_indicator:str
    _allow_double_dash:bool
    _double_dash_name:str

    _requested_command:typing.Union[str,None]
    __defaults:dict[str,typing.Any]
    _parsed:typing.Union[ParsedArgumentsNG,None]

    @property
    def name(self) -> str:
        """Object Name
        @retval str Object Name
        @note property
        """
        return self.program

    @property
    def command(self) -> typing.Union[str,None]:
        """Parsed Commandline Command
        @retval Union[str,None] Command Name parsed from Commandline, None if no parsing has been performed
        @note property
        """
        return self._requested_command

    @property
    def args(self) -> typing.Union[ParsedArgumentsNG,None]:
        """Parsed Commandline Arguments.
        @retval Union[dict[str,Any],None] Parsed Arguments, or None if no parsing has been performed
        @note property
        """
        return self._parsed

    def __init__(self, program_name:typing.Union[str,None]=None, description:typing.Union[str,None]=None,argument_indicator:str = "-",sort_commands:bool=True) -> None:
        """Init
        @param program_name Union[str,None] Name of Program (default to $0)
        @param description Union[str,None] Program Description
        @param argument_indicator str Argument Flag Indicator single will be used for len = 1 flags, double for len > 1
        @param sort_commands bool Whether or not to sort Commands, default True
        """
        super().__init__(required=False,help=description)
        if program_name is None:
            program_name = argv[0]
        self.__defaults = {}
        self.program = program_name
        self.sort_commands = sort_commands
        self._requested_command = None
        self._parsed = None
        self._argument_indicator = argument_indicator
        self.description = description
        self._allow_double_dash = False
        self.add_argument_item(flags=["h","help"],name="help_flag",store_type=str)


    def __generate_defaults(self,arguments:dict[str,typing.Union[ArgumentParserGroup,ArgumentParserItem]]) -> dict[str,typing.Any]:
        """Build Default Values
        @param arguments dict[str,Union[ArgumentParserGroup,ArgumentParserItem]]
        @retval dict[str,Any] Defaults
        """
        defaults:dict[str,typing.Any] = {}
        for argblock in arguments.values():
            if isinstance(argblock,ArgumentParserGroup):
                defaults[argblock.name] = self.__generate_defaults(argblock.arguments)
            else:
                defaults[argblock.name] = argblock.default
        return defaults

    def parse(self) -> None:
        """Parse Commandline Arguments, results available in self.args and command name, if used, from self.command
        """
        self.__arglist = argv.copy()
        self.__arglist.pop(0)
        process_args:dict[str,typing.Union[ArgumentParserGroup,ArgumentParserItem]] = self.__generate_arguments()
        self.__defaults = self.__generate_defaults(process_args)
        self.__defaults.pop("help_flag")
        for argblock in process_args.values():
            self.__check(argblock)
        processing:list[dict[str,typing.Any]] = self.__first_pass(process_args)
        self._parsed = ParsedArgumentsNG(self.__second_pass(processing))
        if self._parsed.has_value("help_flag"):
            self.show_help(self._parsed.get_value("help_flag"))
            sys_exit(1)

    # pylint: disable=unused-argument
    def enable_double_dash(self,
                           name:str,
                           help:typing.Union[str,list[str],None]=None,
                           values:typing.Union[list[typing.Any],None]=None,
                           default:typing.Any=None,
                           required:bool=False,
                          ) -> None:
        """Enable Double Dash commands (ex: foobar.py -- bash)
        @param item_name str Name of parameter
        @param help Union[str,list[str],None] Help string
        @param values Union[list[Any],None] Acceptable Value list
        @param default Any Default value
        @param required bool Whether or not parameter is required
        """
        v:dict[str,typing.Any] = locals()
        v.pop("self")
        self._double_dash_name = name
        self._allow_double_dash = True
        v["flags"] = []
        v["repeatable"] = ArgumentItemRepeat.REPEAT_NO
        v["store_type"] = str
        self.add_argument_item(**v)
    # pylint: enable=unused-argument

    def show_help(self,section:str="help_short") -> None:
        """HelpMenu Generator
        @param section str Help Section to show, default 'help_short' shows command list, and command parameters
        """
        self._p(f"{self.program}{ (' - ' + self.description) if self.description is not None else ''}:")
        self._p("")
        tab_count:int = 0
        if section == "help_short" or len(section) == 0:
            if len(self.commands) > 0:
                commandlist:list[str] = list(self.commands.keys())
                if self.sort_commands:
                    commandlist.sort()
                self._p(f"Usage: {self.program} <command> [flags]")
                self._p(f"Commands: {' '.join(commandlist)}")
                self._p(f"{_tabs(1)}Use --help <command> for more help\n")
                tab_count += 1
                self._p("Common Arguments:")
            else:
                self._p(f"Usage: {self.program} [flags]")
            self.__show_help_arguments(self.arguments,tab_count)
        else:
            if len(self.commands) == 0 or section not in self.commands.keys():
                self._p(f"No such help section '{section}'")
                self.show_help()
                sys_exit(1)
            self._p(f"Usage: {self.program} {section} [common-flags] [flags]")
            self._p("See --help for common-flags")
            self._p(f"Help for command {section}")
            self.__show_help_arguments(self.commands[section].arguments)

    def __show_help_arguments(self,arguments:dict[str,typing.Any],indent:int=0) -> None:
        """Process list of Arguments and generate Help lines for them
        @param arguments dict[str,Any] Arguments to process
        @param indent int Number of Tabs to indent lines
        """
        argblock:typing.Union[ArgumentParserGroup,ArgumentParserItem]
        for argblock in arguments.values():
            if isinstance(argblock,ArgumentParserGroup):
                self._p(f"{_tabs(1+indent)}Group: {argblock.name}, exclusive: {'yes' if argblock.exclusive else 'no'}")
                for gargblock in argblock.arguments.values():
                    if isinstance(gargblock,ArgumentParserGroup):
                        self._p(f"{_tabs(2+indent)}Sub Group: {gargblock.name}, exclusive: {'yes' if gargblock.exclusive or argblock.exclusive else 'no'}")
                        self.__show_help_arguments(gargblock.arguments,indent+2)
                        continue
                    self._p(f"{_tabs(2+indent)}{' '.join(gargblock.flags)}{_tabs(1)}<{ gargblock.store_type.__qualname__ if gargblock.store_type is not None else None }>{_tabs(3)}{gargblock.help}") # type: ignore[union-attr]
                    if gargblock.required or argblock.required:
                        self._p(f"{_tabs(3+indent)}required")
                    if gargblock.default not in [ '', None ]:
                        self._p(f"{_tabs(3+indent)}'default: '{str(gargblock.default)}") # type: ignore[union-attr]
            else:
                field:str
                alts:str = ""
                store_type:str = "str"
                if self._allow_double_dash and self._double_dash_name == argblock.name:
                    field = "--"
                else:
                    field = argblock.flags[0]
                    alts = ', '.join([ f for f in argblock.flags if f != argblock.flags[0] ])
                if argblock.store_type in [ bool, int, float, str ]:
                    store_type = argblock.store_type.__qualname__
                self._p(f"{_tabs(1+indent)}{field}{_tabs(1)}<{store_type}>{_tabs(3)}{argblock.help}")
                if argblock.required:
                    self._p(f"{_tabs(2+indent)}required")
                if argblock.default not in [ '', None ]:
                    self._p(f"{_tabs(2+indent)}'default: '{str(argblock.default)}")
                if len(alts) > 0:
                    self._p(f"{_tabs(2+indent)}alternatives: {alts}")
                if self._allow_double_dash and self._double_dash_name == argblock.name:
                    self._p(f"{_tabs(2+indent)}must be last argument")

    def __generate_arguments(self) -> dict[str,typing.Union[ArgumentParserGroup,ArgumentParserItem]]:
        """Determine Arguments to utilize based on whether commands are available / used
        @retval dict[str,Union[ArgumentParserGroup,ArgumentParserItem]] All argument parameters to process
        """
        progargs:dict[str,typing.Union[ArgumentParserItem,ArgumentParserGroup]] = self.arguments
        process_args:dict[str,typing.Union[ArgumentParserGroup,ArgumentParserItem]] = progargs
        if len(self.__arglist) > 0 and self.__arglist[0] in [ "-h", "--help" ]:
            if len(self.__arglist) >= 2:
                self.show_help(self.__arglist[1])
            else:
                self.show_help()
            sys_exit(1)
        if len(self.commands) > 0:
            if len(self.__arglist) == 0:
                self._p("You must provide a Command")
                self.show_help()
                sys_exit(1)
            commandlist:list[str] = [ c.name for c in self.commands.values() ]
            req_command:str = self.__arglist.pop(0)
            if req_command.startswith(self.argument_indicator):
                self._p("You must provide a Command")
                self.show_help()
                sys_exit(1)
            if req_command not in commandlist:
                self._p(f"Invalid Command '{req_command}'")
                self.show_help()
                sys_exit(1)
            self._requested_command = req_command
            cmdargs:dict[str,typing.Union[ArgumentParserGroup,ArgumentParserItem]] = self.commands[req_command].arguments
            for k,v in progargs.items():
                cmdargs[k] = v
            process_args = cmdargs
        else:
            if not self.__arglist[0].startswith(self.argument_indicator):
                self._p(f"Argumment flags must start with a '{self.argument_indicator}'")
                self.show_help()
                sys_exit(1)
        return process_args

    def __check(self,argblock:typing.Union[ArgumentParserGroup,ArgumentParserItem]) -> None:
        """Check for required parameters
        @param argblock Union[ArgumentParserGroup,ArgumentParserItem]
        """
        found:bool = False
        argline:str = f";;{';;'.join(self.__arglist)};;"
        if isinstance(argblock,ArgumentParserGroup):
            for gargblock in argblock.arguments.values():
                if argblock.required and not gargblock.required:
                    gargblock.required = argblock.required
                self.__check(gargblock)
            return
        if argblock.required:
            for flag in argblock.flags:
                found = f";;{flag};;" in argline or f";;{flag}=" in argline
                if found:
                    return
            if not found:
                self._p(f"Argument {argblock.name} is required, but not defined")
                self.show_help()
                sys_exit(1)

    def __first_pass(self,process_args:dict[str,typing.Union[ArgumentParserGroup,ArgumentParserItem]]) -> list[dict[str,typing.Any]]:
        """First Pass Argument Processing - Match Commandline Args to Values and Values to Argument Parameter blocks
        @param process_args dict[str,Union[ArgumentParserGroup,ArgumentParserItem]] Arguments to process, selected from __generate_arguments
        @retval list[dict[str,typing.Any]] List of parameters in dict form { value, parameter }
        """
        pos:int = 0
        processing:list[dict[str,typing.Any]] = []
        argblock:typing.Union[ArgumentParserGroup,ArgumentParserItem,None]
        while pos < len(self.__arglist):
            found:bool = False
            n:int = 1
            k:str = self.__arglist[pos]
            v:typing.Union[str,None] = None
            if k == "--":
                if not self._allow_double_dash:
                    self._p("Double Dash argument is not allowed here")
                    self.show_help()
                    sys_exit(1)
                found = True
                argblock = process_args[self._double_dash_name]
                v = ' '.join(self.__arglist[pos+1:-1])
            if k.startswith(self.argument_indicator):
                if "=" in k:
                    parts:list[str] = k.split("=",1)
                    k = parts[0]
                    v = parts[1]
                else:
                    if pos+1 >= len(self.__arglist):
                        v = ""
                    elif self.__arglist[pos+1].startswith(self.argument_indicator):
                        v = ""
                    else:
                        n = 2
                        v = self.__arglist[pos+1]
            else:
                pos += n
                continue
            if not found:
                argblock = self.__arg_processor(search_flag=k,process_args=process_args)
            if argblock is not None:
                found = True
                if not hasattr(argblock,"exclusive"):
                    argblock.exclusive = False
            if not found:
                self._p(f"Invalid Argument {k}")
                self.show_help()
                sys_exit(1)
            processing.append({ "value": v, "argblock": argblock })
            pos += n
        return processing

    def __arg_processor(self,search_flag:str,process_args:dict[str,typing.Union[ArgumentParserGroup,ArgumentParserItem]]) -> typing.Union[ArgumentParserGroup,ArgumentParserItem,None]:
        """Argument Block locator - Match Commandline Flags to Argument Blocks
        @param search_flag str Commandline Flag to search
        @param process_args dict[str,Union[ArgumentParserGroup,ArgumentParserItem]] Arguments to process, selected from __generate_arguments
        @retval Union[ArgumentParserGroup,ArgumentParserItem,None] Argument block that matched Commandline Flag
        """
        argblock:typing.Union[ArgumentParserItem,None] = None
        subblock:typing.Union[ArgumentParserItem,None] = None
        pargblock:typing.Union[ArgumentParserGroup,ArgumentParserItem,None] = None
        gargblock:typing.Union[ArgumentParserGroup,ArgumentParserItem,None] = None
        for pargblock in process_args.values():
            if isinstance(pargblock,ArgumentParserGroup):
                groups:list[ArgumentParserGroup] = [ v for v in pargblock.arguments.values() if isinstance(v,ArgumentParserGroup) ]
                for gargblock in pargblock.arguments.values():
                    if isinstance(gargblock,ArgumentParserGroup):
                        subblock = self.__arg_processor(search_flag,gargblock.arguments) # type: ignore[assignment]
                        if subblock is not None:
                            if gargblock.name not in subblock.name:
                                subblock.item_name = f"{pargblock.name}.{gargblock.name}.{subblock.name}"
                            subblock.required = gargblock.required
                            subblock.exclusive = (gargblock.exclusive or pargblock.exclusive)
                            if subblock.exclusive:
                                subblock.exclusive_params = [ f"{pargblock.name}.{gargblock.name}.{e}" for e in gargblock.arguments.keys() if f"{pargblock.name}.{gargblock.name}.{e}" not in [ subblock.name ] ]
                            if subblock.exclusive and pargblock.exclusive:
                                for g in groups:
                                    if g.name == subblock.name:
                                        continue
                                    subblock.exclusive_params += [ f"{pargblock.name}.{g.name}.{e}" for e in g.arguments.keys() if f"{pargblock.name}.{g.name}.{e}" not in [ subblock.name ] and f"{pargblock.name}.{g.name}.{e}" not in subblock.exclusive_params ]
                            return subblock
                    else:
                        if pargblock.name not in gargblock.name:
                            gargblock.item_name = f"{pargblock.name}.{gargblock.name}"
                        if search_flag in gargblock.flags:
                            argblock = gargblock
                            argblock.required = pargblock.required
                            argblock.exclusive = pargblock.exclusive
                            if argblock.exclusive:
                                argblock.exclusive_params = [ f"{pargblock.name}.{e}" for e in pargblock.arguments.keys() if f"{pargblock.name}.{e}" not in [ gargblock.name ] ]
                            return argblock
            else:
                if search_flag in pargblock.flags:
                    return pargblock
        return argblock

    def __second_pass(self,processing:list[dict[str,typing.Any]]) -> dict[str,typing.Any]:
        """Second Pass Argument Processing - Defaults, Conversion, Validation
        @param processing list[dict[str,Any]] Value to Argument Parameter block map from __first_pass
        @retval dict[str,Any] Final result, Parameter name to value map
        """
        result:dict[str,typing.Any] = {}
        for argdata in processing:
            argblock:ArgumentParserItem = argdata["argblock"]
            if argblock.store_type == bool:
                if argdata["value"] == "":
                    argdata["value"] = not argblock.default
                else:
                    argdata["value"] = argdata["value"] in [ "true", "True", "T", "Y", "Yes", "Y", "TRUE", "YES" ]
            repeat:bool = False
            if argblock.name in result.keys() and argblock.repeatable == ArgumentItemRepeat.REPEAT_NO:
                self._p(f"Parameter {argblock.name} cannot be used more than once")
                self.show_help()
                sys_exit(1)
            if argblock.repeatable == ArgumentItemRepeat.REPEAT_APPEND:
                if argblock.name not in result.keys():
                    result[argblock.name] = []
                repeat = True
            res_val:typing.Any
            res_val = argblock.default
            if not isinstance(argdata["value"],argblock.store_type):
                try:
                    t:typing.Type = argblock.store_type
                    res_val = t(argdata["value"])
                except BaseException as e:
                    self._p(f"Error during conversion of parameter {argblock.name} to {t.__qualname__} - {e}")
                    sys_exit(1)
            if argblock.values is not None:
                if argdata["value"] not in argblock.values:
                    self._p(f"Invalid value '{argdata['value']}' for parameter {argblock.name}, must be one of: {','.join(argblock.values)}")
                    self.show_help()
                    sys_exit(1)
            if repeat:
                result[argblock.name].append(res_val)
            else:
                result[argblock.name] = res_val
            if argblock.name not in result.keys():
                result[argblock.name] = argblock.default
        for k,v in result.items():
            if isinstance(v,list) and len(v) == 1:
                result[k] = v[0]
        for argdata in processing:
            argblock = argdata["argblock"]
            if argblock.exclusive:
                for k in argblock.exclusive_params:
                    if k in result.keys():
                        all_p:str = ', '.join(argblock.exclusive_params)
                        self._p(f"Parameter {argblock.name} cannot be used, a related exclusive parameter from ({all_p}) is already defined")
                        self.show_help()
                        sys_exit(1)
        return self.__result_to_dict(result)

    def __result_to_dict(self,in_result:dict[str,typing.Any]) -> dict[str,typing.Any]:
        """Convert single-layer dict of results into multi-level dict by groups, using '.' as key separator
        @param in_result dict[str,Any] Input results dictionary
        @retval dict[str,Any] Multi-level dictionary
        """
        result:dict[str,typing.Any] = self.__defaults.copy()
        _r:dict[str,typing.Any] = result
        for k,v in in_result.items():
            if "." in k:
                _r = result
                k_parts:list[str] = k.split('.')
                for part in k_parts:
                    if part == k_parts[-1]:
                        _r[part] = v
                        break
                    if part not in _r.keys():
                        _r[part] = {}
                    _r = _r[part]
            else:
                result[k] = v
        return result

    def _p(self,v:str) -> None:
        """Help Printer helper (print to stderr)
        @param v str Print String
        """
        print(v,file=stderr)

ArgParserNG:typing.Type = ArgumentParserNG

#### CHECKSUM 9e7dda83f9966179c963f7ec68b7fef136e16bed5c28f44a5412e1f98c83cb7b
