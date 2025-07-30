import re
import os
import sys
import importlib
from copy import copy
from inspect import getfullargspec

__version__ = "0.0.11"

def extracted_arg_name(arg):
        if arg.startswith('--'):
            return arg[2:]
        elif arg.startswith('-'):
            return arg[1:]
        else:
            return arg

def is_help(value):
    return value in ('h', 'help')

def is_setting(value):
    return value in ('s', 'setting')

def is_quiet(value):
    return value in ('q', 'quiet')

def is_optional(arg):
    return arg.startswith('-')


ENDC = '\033[0m'
BOLD = '\033[1m'
RED = '\033[91m'

RST_PARAM_RE = re.compile(r"^([\t ]*):param (.*?): (.*\n(\1[ \t]+.*\n*)*)", re.MULTILINE)
PYTHON_MAIN = "__main__"

class ZExitException(Exception):
    def __init__(self, exit_code):
        self.exit_code = exit_code

def zexit(exit_code):
    raise ZExitException(exit_code)

class ArgumentException(Exception):
    def __init__(self, error_msg=None):
        self.error_msg = error_msg

class TaskAlreadyExistOnThisPluginException(Exception):
    def __init__(self, plugin_name, task_name):
        self.plugin_name = plugin_name
        self.task_name = task_name
        self.message = f"ERROR: Plugin {plugin_name} already has a task called {task_name}."
        super().__init__(self.message)

class Helper:
    def __init__(self):
        self.help = ""

    def usage(self):
        pass

    def print_help(self, error_msg=None):
        if error_msg:
            print(BOLD + RED + error_msg + ENDC)
            print('-'*80)
        self.usage()
        if error_msg:
            zexit(1)

    @property
    def short_help(self):
        try:
            return self.help.strip().splitlines()[0]
        except IndexError:
            return ""


class ZParser(Helper):
    def __init__(self, plugin_module=None):
        if plugin_module is None:
            plugin_module = []

        super(ZParser, self).__init__()

        self.plugin_module = None
        self.plugins = {}
        self.set_plugin_module(plugin_module)
        self.settings = {}
        self.quiet = False
        self.runner = None

    def __repr__(self):
        return self.plugins

    def set_plugin_module(self, plugin_module):
        self.plugin_module = plugin_module

        for module in self.plugin_module:
            loaded = importlib.import_module(module)
            if loaded.__file__ is None:
                print("bin")
                print(module)
                continue
            plugin_dir = os.path.dirname(loaded.__file__)
            plugin_list = [filename[:-3] for filename in os.listdir(plugin_dir) if filename[-3:] == '.py'
                           and filename != '__init__.py']
            # create dict entry before loading them
            for plugin_name in plugin_list:
                self.plugins[plugin_name] = Plugin(plugin_name)

            for plugin_name in plugin_list:
                # loaded_plugin = importlib.import_module("{}.{}".format(module, plugin))

                try:
                    loaded_plugin = importlib.import_module("{}.{}".format(module, plugin_name))
                except ImportError as e:
                    del self.plugins[plugin_name]
                    print("Failed to load plugin {}.{} [{}]".format(module, plugin_name, e))
                    raise
                else:
                    try:
                        self.plugins[plugin_name].alias = loaded_plugin.alias
                    except AttributeError:
                        self.plugins[plugin_name].alias = []
                    self.plugins[plugin_name].help = loaded_plugin.__doc__ or ""
        return self

    def task(self, function=None, name=None, overwrite=None, short=None):
        if overwrite is None:
            overwrite = {}

        if short is None:
            short = {}

        if not function:
            return lambda function: self.task(function, name=name, overwrite=overwrite, short=short)

        plugin_name = function.__module__.split('.')[-1]
        self._register(plugin_name, function, name, overwrite, short)
        return function

    def _register(self, plugin_name, function, name=None, overwrite=None, short=None):
        if overwrite is None:
            overwrite = {}

        if short is None:
            short = {}

        task = Task(function, name, overwrite, short)
        if plugin_name not in self.plugins:
            self.plugins[plugin_name] = Plugin(plugin_name)
            self.plugins[plugin_name].alias = sys.modules[function.__module__].__dict__.get("alias", [])
            self.plugins[plugin_name].help = sys.modules[function.__module__].__doc__ or ""
        self.plugins[plugin_name].add_task(task)


    def usage(self):
        has_main = PYTHON_MAIN in self.plugins
        if has_main:
            if len(self.plugins[PYTHON_MAIN].help) > 0:
                print(self.plugins[PYTHON_MAIN].help)
            print("{} <task>".format(self.prog_name))

        if len(self.plugins) > 2 or ( has_main == False and len(self.plugins) > 1):
            print("{} <plugin_name> <task>".format(self.prog_name))
            print("Plugin list:")
            for plugin in [value for (key, value) in sorted(self.plugins.items())]:
                if plugin.name != PYTHON_MAIN:
                    print("  {:20} - {}".format(plugin.name, plugin.short_help))

        if has_main:
            print("Tasks:")
            self.plugins[PYTHON_MAIN].list_tasks()

    def parse(self, argv=None, prog_name=None):
        if argv is None:
            argv = sys.argv

        self.prog_name = prog_name if prog_name else argv[0]

        argv = argv[1:]
        if not argv or (argv and is_optional(argv[0]) and is_help(extracted_arg_name(argv[0]))):
            self.print_help()
            zexit(0)

        # parse global argument
        argv = self.parse_global(argv)

        if is_optional(argv[0]):
            self.print_help("This argument is unexpected {}".format(argv[0]))

        plugin, self.runner = self._load_plugin_and_runner_from_arg(argv)
        return self.runner

    def _load_plugin_and_runner_from_arg(self, argv):
        arg = argv[0]
        for plugin in self.plugins.values():
            if arg == plugin.name or arg in plugin.alias:
                runner = plugin.parse(argv[1:])
                return plugin, runner
        if PYTHON_MAIN in self.plugins:
            plugin = self.plugins[PYTHON_MAIN]
            runner = plugin.parse(argv[0:])
            return plugin, runner

        plugin = self.print_help("Plugin with name {} doesn't exist".format(arg))
        return plugin, None

    def parse_global(self, argv=None):
        pos = 0
        need_setting_key = False
        current_setting = None
        for arg in argv:
            if need_setting_key:
                if is_optional(arg):
                    self.print_help("Need setting key")
                else:
                    if current_setting:
                        self.settings[current_setting] = arg
                        need_setting_key = False
                        current_setting = None
                    else:
                        current_setting = arg
                    pos += 1

            else:
                if is_optional(arg):
                    if is_quiet(extracted_arg_name(arg)):
                        self.quiet = True
                        pos += 1
                    elif is_setting(extracted_arg_name(arg)):
                        pos += 1
                        need_setting_key = True
                    else:
                        self.print_help("Unexpected argument {}".format(arg))
                else:
                    break
        return argv[pos:]


class Plugin(Helper):
    def __init__(self, name):
        super(Plugin, self).__init__()
        self.name = name
        self.alias = []
        self.tasks = {}
        self.help = ""

    def add_task(self, task):
        if task.name in self.tasks:
            raise TaskAlreadyExistOnThisPluginException(self.name, task.name)
        self.tasks[task.name] = task

    def __repr__(self):
        return "{}".format(self.tasks)

    def usage(self):
        print(self.help)

        if self.name == PYTHON_MAIN:
            print("{} <task>".format(z.prog_name))
        else:
            print("{} {} <task>".format(z.prog_name, self.name))
        print("Plugin alias: {}".format(self.alias))
        print("Tasks:")
        self.list_tasks()

    def list_tasks(self):
        for task in [value for (key, value) in sorted(self.tasks.items())]:
            print("  {:20} - {}".format(task.name, task.short_help))

    def parse(self, argv=None):
        if not argv:
            self.print_help("You need to specify a task")
            zexit(0)

        arg = argv[0]
        if is_optional(arg):
            if is_help(extracted_arg_name(arg)):
                self.print_help()
                zexit(0)
            else:
                self.print_help("We don't expect this option here: {}".format(arg))
        else:
            task = self._load_task_from_arg(arg)
            task.parse(argv[1:])
            return task

    def _load_task_from_arg(self, arg):
        for task in self.tasks.values():
            if arg == task.name:
                return task
        self.print_help("Task with name {} doesn't exist".format(arg))


class Task(Helper):
    def __init__(self, function, name, overwrite, short):
        super(Task, self).__init__()
        if name is None:
            name = function.__name__
        self.function = function
        self.name = name
        self.overwrite = overwrite
        self.short = short
        self.args = []
        self.optional_args = []
        self.varargs = None
        self.annotations = {}
        self._init_args()
        self._use_docstring()

    @property
    def all_args(self):
        return self.args + self.optional_args

    def _use_docstring(self):
        docstring = self.function.__doc__ or ""
        for match in RST_PARAM_RE.finditer(docstring):
            name = match.group(2)
            value = match.group(3)
            for arg in self.all_args:
                if arg.arg_python == name:
                    arg.help = value
        docstring = RST_PARAM_RE.sub("", docstring)
        self.help = docstring

    def _init_args(self):
        argdata = getfullargspec(self.function)

        args = argdata.args
        defaults = argdata.defaults


        args2 = copy(args)
        if defaults:
            for arg, default in zip(args[0 - len(defaults):], defaults):
                args2.remove(arg)
                short = self.short.get(arg, None)
                name = self.overwrite.get(arg, None)
                self.optional_args.append(ArgumentOptional(arg, default, name, short))
        for arg in args2:
            self.args.append(Argument(arg))

        if argdata.varargs:
            self.varargs = Varargs(argdata.varargs)

        if argdata.annotations:
            self.annotations = argdata.annotations


    def _clean_args(self):
        for arg in self.optional_args:
            arg.is_set = False
        if self.varargs:
            self.varargs.value = []

    def parse(self, argv=None):
        self._clean_args()
        if argv and is_optional(argv[0]) and is_help(extracted_arg_name(argv[0])):
            self.print_help()
            zexit(0)
        arg_pos = 0
        if not argv and not self.args:
            pass
        elif len(argv) < len(self.args):
            self.print_help("You need to specify the required arguments {}".format(self.args))
        else:
            current_arg = None
            in_optional = False
            for value in argv:
                if arg_pos < len(self.all_args):
                    valid = False
                    if not is_optional(value):
                        if current_arg:
                            current_arg.value = value
                            current_arg = None
                        else:
                            if in_optional:
                                self.print_help("Error we don't expect a positional argument after an optional "
                                                "declaration")
                            self.all_args[arg_pos].value = value
                        arg_pos += 1
                        valid = True
                    else:
                        if current_arg:
                            self.print_help("Except value for: {}".format(current_arg.name))
                        arg_name = extracted_arg_name(value)
                        for argument in self.optional_args:
                            if argument.name == arg_name or argument.short == arg_name:
                                if not isinstance(argument.default, bool):
                                    current_arg = argument
                                    valid = True
                                else:
                                    argument.value = not argument.default
                                    valid = True
                        in_optional = True
                    if not valid:
                        self.print_help("Invalid argument {}".format(value))
                else:
                    if self.varargs:
                        self.varargs.value.append(value)
                    else:
                        self.print_help("too many arguments")
            if arg_pos < len(self.args):
                self.print_help("You need to give data for each positional argument")

        # set optional argument not set to default
        for arg in self.optional_args:
            arg.use_default()

    @property
    def plugin(self):
        return self.function.__module__.split('.')[-1]

    def usage(self):
        print(self.help)
        print("Usage:")
        parameters = []
        for arg in self.all_args:
            if isinstance(arg, ArgumentOptional):
                if isinstance(arg.default, bool):
                    parameter = "[--{p}]"
                else:
                    parameter = "[--{p} {p}]"
            else:
                parameter = "{p}"
            parameters.append(parameter.format(p=arg.name))
        if self.varargs:
            parameters.append("[{p}, [{p}...]".format(p=self.varargs.name))

        if self.plugin == PYTHON_MAIN:
            print("  {} {} {}".format(z.prog_name, self.name, " ".join(parameters)))
        else:
            print("  {} {} {} {}".format(z.prog_name, self.plugin, self.name, " ".join(parameters)))
        if self.args:
            print("Positional arguments:")
            for arg in self.args:
                print("  {} - {} {}".format(arg.name, arg.short_help, self.annotations.get(arg.name, "")))

        if self.optional_args:
            print("Optional arguments:")
            for arg in self.optional_args:
                arg_name = "--{}".format(arg.name)
                if arg.short:
                    arg_name = "{}/-{}".format(arg_name, arg.short)
                print("  {} (Default: {}) {} - {}".format(arg_name, arg.default, self.annotations.get(arg.name, ""), arg.short_help))

        if self.varargs:
            print("  {} - {}".format(self.varargs.name, self.varargs.short_help))

    def _args_value(self):
        only_string_parameters = [arg.value for arg in self.all_args] + ([] if not self.varargs else self.varargs.value)
        parsed_paramenters = self._parse_floats_and_ints_in_a_list(only_string_parameters)
        self._enforce_variable_annotations(parsed_paramenters)
        return parsed_paramenters

    def _enforce_variable_annotations(self, parsed_paramenters):
        if len(parsed_paramenters) <= len(self.all_args):
            for i in range(len(parsed_paramenters)):
                param_name = str(self.all_args[i])
                param_class = self.annotations.get(param_name)
                if param_class is not None:
                    param_value = parsed_paramenters[i]
                    if isinstance(param_value, param_class) or param_value.__class__ == int and param_class == float:
                        continue
                    else:
                        raise ArgumentException(f"Invalid value for paramter {param_name}. A {param_class} is expected, not {param_value.__class__}")

    def _parse_floats_and_ints_in_a_list(self, the_list):
        size = len(the_list)
        for i in range(0, size):
            elem = the_list[i]
            if isinstance(elem, str):
                if "." in elem:
                    try:
                        new_elem = float(elem)
                    except ValueError:
                        continue
                else:
                    try:
                        new_elem = int(elem)
                    except ValueError:
                        continue
                the_list[i] = new_elem

        return the_list

    def run(self):
        try:
            result = self.function(*self._args_value())
        except ArgumentException as e:
            self.print_help(e.error_msg)
        else:
            if result or result is False:
                if isinstance(result, list):
                    if isinstance(result[0], str):
                        x = []
                        for r in result:
                            if " " in r:
                                x.append('"{}"'.format(r))
                            else:
                                x.append(r)
                        output = " ".join(x)
                        print(output)
                    else:
                        for r in result:
                            print(r)
                elif isinstance(result, dict):
                    for key, value in result.iteritems():
                        print("{}\t{}".format(key, value))
                else:
                    print(result)

    def __repr__(self):
        return self.name


class Argument(Helper):
    def __init__(self, arg_python, name=None, short=None):
        super(Argument, self).__init__()
        self.arg_python = arg_python
        self.name = name or arg_python
        self.short = short
        self._value = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def __repr__(self):
        return self.name


class ArgumentOptional(Argument):
    def __init__(self, arg_python, default, name=None, short=None):
        if isinstance(default, bool) and default:
            if not name:
                name = "no-{}".format(arg_python)

        super(ArgumentOptional, self).__init__(arg_python, name, short)
        self.default = default
        self.is_set = False

    def use_default(self):
        if not self.is_set:
            self._value = self.default

    @Argument.value.getter
    def value(self):
        if type(self._value) == type(self.default):
            return self._value
        if isinstance(self.default, bool):
            if self._value.lower() in ['true', '1']:
                return True
            elif self._value.lower() in ['false', '0']:
                return False
            else:
                self.print_help("Invalid data, expect boolean for arg: {}".format(self.name))
        elif isinstance(self.default, int):
            return int(self._value)
        elif isinstance(self.default, list):
            result = []
            for i in self._value.split(','):
                result.append(i)
            return result
        return self._value

    @value.setter
    def value(self, value):
        self.is_set = True
        self._value = value


class Varargs(Argument):
    def __init__(self, arg_python, name=None, short=None):
        super(Varargs, self).__init__(arg_python, name, short)
        self._value = []


def init(plugin_list: list=[]) -> int:
    return zparser2_init(plugin_list)

def zparser2_init(plugin_list: list=[]) -> int:
    global z
    try:
        z.set_plugin_module(plugin_list).parse().run()
    except ZExitException as exit_exception:
        sys.exit(exit_exception.exit_code)
    sys.exit(0)

z = ZParser()
