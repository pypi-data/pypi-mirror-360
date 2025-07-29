# Copyright 2025-2025 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of NextGen Argument Parser,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###

import enum
import typing

# pylint: disable=unused-argument
class ArgumentBase:
    """Base Object"""
    _unnamed:int
    arguments:dict[str,typing.Union["ArgumentParserItem","ArgumentParserGroup"]]
    commands:dict[str,"ArgumentParserCommand"]
    required:bool
    help:typing.Union[str,list[str],None]
    parent:"ArgumentBase"
    _argument_indicator:str

    @property
    def argument_indicator(self) -> str:
        """Argument Indicator, Run up the parent chain
        @retval str Argument Indicator (such as a dash ('-'))
        @note property
        """
        if hasattr(self,"parent"):
            return self.parent.argument_indicator
        return self._argument_indicator

    @property
    def name(self) -> str:
        """Object Name
        @retval str Object Name
        @note property
        """
        raise NotImplementedError("Must be defined my subclasses")

    def __init__(self,
                 required:bool=False,
                 help:typing.Union[str,list[str],None]=None,
                 parent:typing.Union["ArgumentBase",None]=None
                ) -> None:
        """Init
        @param required bool Whether or not group is required
        @param help Union[str,list[str],None] Help String
        @param parent ArgumentBase Parent Argument Parser Object
        """
        self.required = required
        self.help = help
        self.arguments = {}
        self.commands = {}
        self._unnamed = 0
        if parent is not None:
            self.parent = parent

    def add_command(self,
                    name:str,
                    help:typing.Union[str,list[str],None]=None,
                   ) -> "ArgumentParserCommand":
        """Add a New Command / Section
        @param name str Command Name / Command
        @param help Union[str,list[str],None] Help String
        @retval ArgumentParserCommand Command Object
        """
        if isinstance(self,(ArgumentParserItem, ArgumentParserCommand, ArgumentParserGroup)):
            raise SyntaxError(f"{type(self).__qualname__} Objects cannot have child commands")
        v:dict[str,typing.Any] = locals()
        v["command_name"] = v.pop("name")
        v.pop("self")
        v["parent"] = self
        command:ArgumentParserCommand = ArgumentParserCommand(**v)
        self.commands[command.name] = command
        return command

    def add_reusable(self,group:"ArgumentParserGroup") -> None:
        """Add a 'reusable' Argument Group
        @param group ArgumentParserGroup Argument Group
        """
        if isinstance(self,ArgumentParserItem):
            raise SyntaxError(f"{type(self).__qualname__} Objects cannot have child commands")
        self.arguments[group.name] = group

    def reusable_argument_group(self,
                                name:typing.Union[str,None]=None,
                                help:typing.Union[str,list[str],None]=None,
                                required:bool=False,
                                exclusive:bool=False
                               ) -> "ArgumentParserGroup":
        """Create a reusable Group that can be attached many times
        @param name str Name of Group to create
        @param help Union[str,list[str],None] Help String
        @param required bool Whether or not group is required
        @param exclusive bool Whether parameters in group are exclusive to eachother (only one can be set)
        @retval ArgumentParserGroup Group Object
        """
        v:dict[str,typing.Any] = locals()
        v.pop("self")
        v["parent"] = self
        if name is None:
            name = f"group{self._unnamed}"
            self._unnamed += 1
        v.pop("name")
        v["group_name"] = name
        if "." in name:
            raise SyntaxError("item_name cannot contain '.'")
        return ArgumentParserGroup(**v)

    def add_argument_group(self,
                           name:typing.Union[str,None]=None,
                           help:typing.Union[str,list[str],None]=None,
                           required:bool=False,
                           exclusive:bool=False
                          ) -> "ArgumentParserGroup":
        """Add a new Argument Group
        @param name str Name of Group to create
        @param help Union[str,list[str],None] Help String
        @param required bool Whether or not group is required
        @param exclusive bool Whether parameters in group are exclusive to eachother (only one can be set)
        @retval ArgumentParserGroup Group Object
        """
        # if isinstance(self,ArgumentParserItem) or isinstance(self,ArgumentParserGroup):
        if isinstance(self,ArgumentParserItem):
            raise SyntaxError(f"{type(self).__qualname__} Objects cannot have child groups")
        v:dict[str,typing.Any] = locals()
        v.pop("self")
        group:ArgumentParserGroup = self.reusable_argument_group(**v)
        self.arguments[group.name] = group
        return group

    def add_argument_item(self,
                          flags:typing.Union[str,list[str]],
                          name:typing.Union[str,None]=None,
                          help:typing.Union[str,list[str],None]=None,
                          store_type:typing.Union[typing.Type,None]=None,
                          values:typing.Union[list[typing.Any],None]=None,
                          default:typing.Any=None,
                          required:bool=False,
                          repeatable:typing.Union["ArgumentItemRepeat",None]=None
                         ) -> None:
        """Add a new Argument Item
        @param flags Union[str,list[str]] List of Flags Argument will listen to, do not include the argument indicators (dashes, for example)
        @param name str Name of parameter
        @param help Union[str,list[str],None] Help string
        @param store_type Union[Type,None] Type of value to store as
        @param values Union[list[Any],None] Acceptable Value list
        @param default Any Default value
        @param required bool Whether or not parameter is required
        @param repeatable ArgumentItemRepeat Whether or not this item can repeat, and if so, how its handled
        """
        if isinstance(self,ArgumentParserItem):
            raise SyntaxError(f"{type(self).__qualname__} Objects cannot have child items")
        v:dict[str,typing.Any] = locals()
        v["item_name"] = v.pop("name")
        v.pop("self")
        if repeatable is None:
            v["repeatable"] = ArgumentItemRepeat.REPEAT_NO
        v["parent"] = self
        g:str
        if not isinstance(flags,(list,str)):
            raise ValueError("Flags must either be a str or list[str]")
        if name is None:
            if isinstance(flags,str):
                g = flags.split(' ')[0].lstrip(self.argument_indicator)
            elif isinstance(flags,list):
                g = flags[0].lstrip(self.argument_indicator)
            v["item_name"] = g
        else:
            g = v["item_name"]
        if "." in g:
            raise SyntaxError(f"item_name '{g}' cannot contain '.'")
        item = ArgumentParserItem(**v)
        self.arguments[g] = item

class ArgumentParserCommand(ArgumentBase):
    """Argument Parser Command / Subsection
    """
    command_name:str

    @property
    def name(self) -> str:
        return self.command_name

    def __init__(self,
                 command_name:str,
                 parent:"ArgumentBase",
                 help:typing.Union[str,list[str],None]=None
                ) -> None:
        """Init
        @param name str Command Name / Command
        @param parent ArgumentBase Parent Argument Parser Object
        @param help Union[str,list[str],None] Help string
        """
        super().__init__(parent=parent,required=False,help=help)
        self.command_name = command_name

class ArgumentItemRepeat(enum.Enum):
    """Argument Item Repeat Enum
    REPEAT_NO = Do not allow repeats, complain if found
    REPEAT_REPLACE = Replace the value with the subsequent values
    REPEAT_APPEND = Turn the value into a list, and append subsequent values
    """
    REPEAT_NO = 0
    REPEAT_REPLACE = 1
    REPEAT_APPEND = 2

class ArgumentParserItem(ArgumentBase):
    """Argument Item - Individual Argument Item
    """
    item_name:str
    values:typing.Union[list[typing.Any],None]
    flags:list[str]
    store_type:typing.Type
    default:typing.Any
    repeatable:ArgumentItemRepeat
    exclusive:bool
    exclusive_params:list[str]

    @property
    def name(self) -> str:
        """Item Name
        @retval str Item Name
        """
        return self.item_name

    def __init__(self,
                 item_name:str,
                 flags:typing.Union[str,list[str]],
                 parent:"ArgumentBase",
                 help:typing.Union[str,list[str],None]=None,
                 store_type:typing.Union[typing.Type,None]=None,
                 values:typing.Union[list[typing.Any],None]=None,
                 default:typing.Any=None,
                 required:bool=False,
                 repeatable:ArgumentItemRepeat=ArgumentItemRepeat.REPEAT_NO,
                ) -> None:
        """
        @param name str Name of parameter
        @param flags Union[str,list[str]] List of Flags Argument will listen to, do not include the argument indicators (dashes, for example)
        @param parent ArgumentBase Parent Argument Parser Object
        @param help Union[str,list[str],None] Help string
        @param store_type Union[Type,None] Type of value to store as. May be any type that accepts 1 string parameter only; ex `MyType(<value>)`
        @param values Union[list[Any],None] Acceptable Value list
        @param default Any Default value
        @param required bool Whether or not parameter is required
        @param repeatable ArgumentItemRepeat Whether or not this item can repeat, and if so, how its handled
        """
        super().__init__(parent=parent,required=required,help=help)
        if isinstance(flags,str):
            flags = flags.split(" ")
        f:list[str] = []
        for v in flags:
            if v.startswith("-"):
                raise ValueError(f"Flag '{v}' for item '{item_name}' should not start with the argument indicator '{self.argument_indicator}'")
            if len(v) == 1:
                f.append(f"{self.argument_indicator}{v}")
            else:
                f.append(f"{self.argument_indicator}{self.argument_indicator}{v}")
        self.flags = f
        if store_type is None:
            if default is not None:
                store_type = type(default)
            elif values is not None:
                store_type = type(values[0])
            else:
                store_type = str
        if default is None:
            if store_type == bool:
                default = False
            elif store_type == str:
                default = ""
        self.item_name = item_name
        self.values = values
        self.store_type = store_type
        self.default = default
        self.repeatable = repeatable


class ArgumentParserGroup(ArgumentBase):
    """Argument Group - Grouped section of arguments
    """
    group_name:str
    exclusive:bool

    @property
    def name(self) -> str:
        """Group Name
        @retval str Group Name
        """
        return self.group_name

    def __init__(self,
                 group_name:str,
                 parent:"ArgumentBase",
                 help:typing.Union[str,list[str],None]=None,
                 required:bool=False,
                 exclusive:bool=False
                ) -> None:
        """Init
        @param name str Name of Group to create
        @param parent ArgumentBase Parent ArgumentParser Object
        @param help Union[str,list[str],None] Help String
        @param required bool Whether or not group is required
        @param exclusive bool Whether parameters in group are exclusive to eachother (only one can be set)
        """
        self.group_name = group_name
        self.exclusive = exclusive
        super().__init__(parent=parent,required=required,help=help)
# pylint: enable=unused-argument

ArgParserNGCommand:typing.Type = ArgumentParserCommand
ArgParserNGGroup:typing.Type = ArgumentParserGroup
ArgParserNGItem:typing.Type = ArgumentParserItem
ArgParserNGRepeat:typing.Type = ArgumentItemRepeat

#### CHECKSUM bf0b9e833ceccb4348a15f401c38c9d87d9479c5bef55e7442ba82ebf338e1b1
