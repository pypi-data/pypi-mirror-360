"""Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

"""
OrchestraAdapter aims at implementeng all the standard Orchestra behavior of an
adapter and take care of the boilerplate code.
See documentation of the `OrchestraAdapter` class
"""

import inspect
from threading import Thread
import time
from dataclasses import dataclass
import traceback
from typing import Callable

from dotenv import find_dotenv, load_dotenv

import avesterra as av
from avesterra.avesterra import AdapterError
from orchestra import env, _hns, _log_publisher
from orchestra._hns import Health
from orchestra.adapter import Adapter
from orchestra.adapter_interface import Interface, Method, ValueType
from orchestra import mount


class _OrchestraAdapter(Adapter):
    def __init__(
        self,
        mount_key: str,
        socket_count: int,
        adapting_threads: int,
    ):
        load_dotenv(find_dotenv())
        self._mount_key = mount_key
        self.interface: Interface | None = None
        self._forced_outlet = None
        self._on_shutdown: Callable | None = None
        super().__init__(
            server=env.get_or_raise(env.AVESTERRA_HOST),
            directory=env.get_or_default(
                env.AVESTERRA_CERTIFICATE_DIR_PATH, "/AvesTerra/Certificates/"
            ),
            auth=env.get_or_raise(env.AVESTERRA_AUTH, av.AvAuthorization),
            socket_count=socket_count,
            adapting_threads=adapting_threads,
        )

    def init_outlet(self, forced_outlet: av.AvEntity | None):
        assert self.interface is not None, "Interface not set"

        if forced_outlet is not None:
            self.outlet = forced_outlet
        else:
            self.outlet = mount.mount_outlet(
                self._mount_key, self.auth, self.auth, self.interface
            )
            av.av_log.success(f"Mounted outlet: {self.outlet}")

        av.exclude_fact(self.outlet, av.AvAttribute.METHOD, authorization=self.auth)
        av.store_entity(
            self.outlet,
            av.AvMode.INTERCHANGE,
            self.interface.to_avialmodel().to_interchange(),
            0,
            self.auth,
        )
        av.av_log.success("Successfully stored interface in outlet")

    def run(self):
        super().run()

    def on_shutdown(self):
        if self._on_shutdown is not None:
            self._on_shutdown()
        return super().on_shutdown()


@dataclass
class OARoute:
    _method: Method
    callback: Callable[..., av.AvValue]
    name_set: bool
    value_out_set: bool
    print_exc_trace: bool = False

class OrchestraAdapter:
    def __init__(
        self,
        mount_key: str,
        version: str,
        description: str,
        adapting_threads: int = 1,
        socket_count: int = 32,
    ):
        """
        Utility class to implement Orchestra adapters respecting the Orchestra
        adapter standard, including the declaration of the adapter's interface
        see:
        - <https://gitlab.com/ledr/core/dev-platform/developer-resources/-/wikis/The-Orchestra-Platform/Adapters-standard>
        - <https://gitlab.com/groups/ledr/-/wikis/Standard-Adapter-Interface>

        Creating an instance of an OrchestraAdapter will call the `av.initialize`
        function, and will call `av.finalize` when the adapter is stopped.
        You can interract with the Orchestra server as soon as the adapter
        is created.
        Creating multiple instances of OrchestraAdaptre in the same process is
        not supported and will result in undefined behavior. Adding support for
        it is possible future improvement, but it's unlikely to be useful.

        To make the `adapt` call to the Orchestra server and publish the
        interface of the adapter, remember to call the method `run()` of the
        adapter after you are done declaring all of the routes.

        # Routes definition

        After creating an instance of OrchestraAdapter, you should define all
        the routes the adapter will handle.
        Each route is defined by a function with a decorator
        `@adapter.route("<Route name>")`. The name used in the public interface
        of the adapter and acts as documentation.
        Other decorators are used to indicate how a invoker can invoke that
        route.
        for example:
        ```py
        adapter = OrchestraAdapter(
            mount_key="math adapter",
            name="Math adapter",
            version="1.0.0",
            description="Basic math utilities",
        )


        @adapter.route("Echo")
        @adapter.method(av.AvMethod.ECHO)
        @adapter.value_out(ValueType.null()) # doesnt support this use case well
        def echo(value: av.AvValue) -> av.AvValue:
            \"""
            Echoes the given value
            \"""
            return value

        adapter.run()
        ```
        The decorator `@adapter.method(av.AvMethod.ECHO)` indicates that this
        route is reponsible for handling any invoke call whose 'method'
        parameter is `av.AvMethod.ECHO`.
        The argument `value` of the function `echo` signifies that the route is
        expecting a single parameter of the invoke to be filled, the 'value'
        parameter.
        Knowing which arguments the route expects is needed to advertize the
        interface of the adapter, it acts as extra documentation.

        A route can have multiple decorators indicating that this route is
        responsible for handling any invoke call whose combination of multiple
        parameters matches.
        for example:
        ```py
        adapter = OrchestraAdapter(
            mount_key="pokemon_adapter",
            name="Pokémon adapter",
            version="1.0.0",
            description="Represents a Pokémon",
        )


        @adapter.route("Get name")
        @adapter.method(av.AvMethod.GET)
        @adapter.attribute(av.AvAttribute.NAME)
        @adapter.value_out(ValueType.text())
        def get_name(entity: av.AvEntity) -> av.AvValue:
            \"""
            Get the english name of the pokemon
            \"""
            return av.AvValue.encode_text(av.entity_name(entity))


        @adapter.route("Get pokedex number")
        @adapter.method(av.AvMethod.GET)
        @adapter.attribute(av.AvAttribute.NUMBER)
        @adapter.value_out(ValueType.integer())
        def get_pokedex_number(entity: av.AvEntity) -> av.AvValue:
            \"""
            Get the pokedex number of the pokemon
            \"""
            return av.AvValue.encode_integer(42)

        adapter.run()
        ```

        The `get_name` function will be called to handle any invoke to method
        `AvMethod.GET` and attribute `AvAttribute.NAME`, and the
        `get_pokedex_number` function will be called to handle any invoke to
        method `AvMethod.GET` and attribute `AvAttribute.NUMBER`.

        # Routes function parameters

        Functions can also take parameters using the regular python parameter
        list. In this example, both `get_name` and `get_pokedex_number`
        functions will receive the 'entity' parameter of the invoke call.
        The mapping of the parameter is done using their names. Possible name
        for arguments are:

        entity, outlet, method, attribute, name, key, value, parameter, index,
        instance, count, aspect, context, category, klass, event, mode,
        precedence, time, timeout, auxiliary, ancillary, authorization

        Any argument whose name doesn't match any of these will result in an
        error being raised during initialization of the adapter.
        Each argument should also be of the correct type otherwise an error will
        be raised during initialization.

        It is possible to have multiple routes matching a single request or get
        into situation where it's ambiguous which route will handle the invoke
        call.
        The rule is that the first route matching the incoming invoke
        parameters will be the one handling it, even if some other routes also
        match the incoming invoke parameters.
        The order follows the order of declaration of the function, the first
        function declared will take precedence over the following.

        # Routes function documentation

        All route must have a docstring and that docstring will be used to
        document what the route does in the interface declaration of the
        adapter.
        The syntax to create the docsring is the regular python syntax to create
        a function docstring. See examples above

        # System monitoring

        If the standard 'sysmon' adapter is running, the adapter will
        automatically periodically report its health status to it.
        The decorator @adapter.health_reporter can be used to provide a custom
        function reporting the current healthlthRepHealthReport status of the adapter.
        The performance, success rate and frequency of invoke of the different
        routes of the adapters will automatically be monitored and updated in
        the adapter's outlet model.

        :param mount_key: The key with which the adapter will be registered in the mount adapter. If an outlet of that key is already mounted, it will use it, otherwise it will create a new outlet.
        :param name: The human-friendly name of the adapter as it will appear in the interface.
        :param version: The version of the adapter as it will appear in the interface. It should follow the semantic versioning standard. (<https://semver.org/>)
        :param description: A description of the adapter as it will appear in the interface.
        :param adapting_threads: The number of threads the adapter will use to handle requests. Default is 1. More thread thread can be used to handle more requests concurrently, but then be careful about concurrency issues. If the adapter performs CPU-heavy tasks, increasing the number of thread is not useful. If the adapter takes time to respond without using much CPU (such as waiting for network calls), then increasing the number of thread could increase performance when responding to multiple invokes at the same time.
        """

        self._adapter = _OrchestraAdapter(mount_key, socket_count, adapting_threads)
        self._adapter.invoke_callback = self.invoke_callback
        self._routes: dict[str, OARoute] = {}
        self._mount_key = mount_key
        self._version = version
        self._description = description
        self._on_outlet_init: Callable | None = None
        self.auth = self._adapter.auth
        self._health_reporter = lambda: Health.green()

    @property
    def outlet(self):
        return self._adapter.outlet

    def _route(self, fn: Callable[..., av.AvValue]):
        if fn.__name__ not in self._routes:
            if fn.__doc__ is None:
                raise ValueError(f"Method {fn.__name__} is missing a docstring")

            args = []
            signature = inspect.signature(fn)

            if signature.return_annotation != inspect._empty and not issubclass(
                signature.return_annotation, av.AvValue
            ):
                raise ValueError(
                    f"Function '{fn.__name__}': Return value must be a AvValue but is {signature.return_annotation}"
                )

            for param in signature.parameters.values():
                if param.name == "entity":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvEntity
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvEntity but is {param.annotation}"
                        )
                    args.append(av.AvAspect.ENTITY)
                elif param.name == "outlet":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvEntity
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvEntity but is {param.annotation}"
                        )
                    args.append(av.AvAspect.OUTLET)
                elif param.name == "method":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvMethod
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvMethod but is {param.annotation}"
                        )
                    args.append(av.AvAspect.METHOD)
                elif param.name == "attribute":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvAttribute
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvAttribute but is {param.annotation}"
                        )
                    args.append(av.AvAspect.ATTRIBUTE)
                elif param.name == "name":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvName
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvName but is {param.annotation}"
                        )
                    args.append(av.AvAspect.NAME)
                elif param.name == "key":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvKey
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvKey but is {param.annotation}"
                        )
                    args.append(av.AvAspect.KEY)
                elif param.name == "value":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvValue
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvValue but is {param.annotation}"
                        )
                    args.append(av.AvAspect.VALUE)
                elif param.name == "parameter":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvParameter
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvParameter but is {param.annotation}"
                        )
                    args.append(av.AvAspect.PARAMETER)
                elif param.name == "resultant":
                    raise ValueError(
                        f"Function '{fn.__name__}': '{param.name}' argument is not supported yet"
                    )
                elif param.name == "index":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvIndex
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvIndex but is {param.annotation}"
                        )
                    args.append(av.AvAspect.INDEX)
                elif param.name == "instance":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvInstance
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvInstance but is {param.annotation}"
                        )
                    args.append(av.AvAspect.INSTANCE)
                elif param.name == "offset":
                    raise ValueError(
                        f"Function '{fn.__name__}': '{param.name}' argument is not supported yet"
                    )
                elif param.name == "count":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvCount
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvCount but is {param.annotation}"
                        )
                    args.append(av.AvAspect.COUNT)
                elif param.name == "aspect":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvAspect
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvAspect but is {param.annotation}"
                        )
                    args.append(av.AvAspect.ASPECT)
                elif param.name == "context":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvContext
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvContext but is {param.annotation}"
                        )
                    args.append(av.AvAspect.CONTEXT)
                elif param.name == "category":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvCategory
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvCategory but is {param.annotation}"
                        )
                    args.append(av.AvAspect.CATEGORY)
                elif param.name == "klass":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvClass
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvClass but is {param.annotation}"
                        )
                    args.append(av.AvAspect.CLASS)
                elif param.name == "event":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvEvent
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvEvent but is {param.annotation}"
                        )
                    args.append(av.AvAspect.EVENT)
                elif param.name == "mode":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvMode
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvMode but is {param.annotation}"
                        )
                    args.append(av.AvAspect.MODE)
                elif param.name == "state":
                    raise ValueError(
                        f"Function '{fn.__name__}': '{param.name}' argument is not supported yet"
                    )
                elif param.name == "condition":
                    raise ValueError(
                        f"Function '{fn.__name__}': '{param.name}' argument is not supported yet"
                    )
                elif param.name == "precedence":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, int
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a int but is {param.annotation}"
                        )
                    args.append(av.AvAspect.PRECEDENCE)
                elif param.name == "time":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvTime
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvTime but is {param.annotation}"
                        )
                    args.append(av.AvAspect.TIME)
                elif param.name == "timeout":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvTimeout
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvTimeout but is {param.annotation}"
                        )
                    args.append(av.AvAspect.TIMEOUT)
                elif param.name == "mask":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvMask
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvMask but is {param.annotation}"
                        )
                elif param.name == "auxiliary":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvEntity
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvEntity but is {param.annotation}"
                        )
                    args.append(av.AvAspect.AUXILIARY)
                elif param.name == "ancillary":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvEntity
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvEntity but is {param.annotation}"
                        )
                    args.append(av.AvAspect.ANCILLARY)
                elif param.name == "credential":
                    raise ValueError(
                        f"Function '{fn.__name__}': '{param.name}' argument is not supported yet"
                    )
                elif param.name == "authorization":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvAuthorization
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvAuthorization but is {param.annotation}"
                        )
                    args.append(av.AvAspect.AUTHORIZATION)
                elif param.name == "authority":
                    if param.annotation != inspect._empty and not issubclass(
                        param.annotation, av.AvAuthorization
                    ):
                        raise ValueError(
                            f"Function '{fn.__name__}': Argument {param.name} must be a AvAuthorization but is {param.annotation}"
                        )
                    args.append(av.AvAspect.AUTHORITY)
                else:
                    raise ValueError(
                        f"Function '{fn.__name__}': Argument {param.name} is not supported"
                    )

            self._routes[fn.__name__] = OARoute(
                Method(
                    name="",
                    description=fn.__doc__.strip(),
                    base=av.AvLocutorOpt(),
                    args=args,
                ),
                callback=fn,
                name_set=False,
                value_out_set=False,
            )

        return self._routes[fn.__name__]

    def route(self, name: str):
        """Declare a new route"""

        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.name = name
            route.name_set = True
            return fn

        return decorator

    def print_exc_trace(self):
        """Decorator to print the exception trace when an error occurs in the route callback"""
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route.print_exc_trace = True
            return fn

        return decorator

    def method(self, method: av.AvMethod):
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.base.method = method
            return fn

        return decorator

    def attribute(self, attribute: av.AvAttribute):
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.base.attribute = attribute
            return fn

        return decorator

    def key(self, key: av.AvKey):
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.base.key = key
            return fn

        return decorator

    def name(self, name: av.AvName):
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.base.name = name
            return fn

        return decorator

    def parameter(self, parameter: av.AvParameter):
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.base.parameter = parameter
            return fn

        return decorator

    def resultant(self, resultant: int):
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.base.resultant = resultant
            return fn

        return decorator

    def index(self, index: av.AvIndex):
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.base.index = index
            return fn

        return decorator

    def instance(self, instance: av.AvInstance):
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.base.instance = instance
            return fn

        return decorator

    def offset(self, offset: av.AvOffset):
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.base.offset = offset
            return fn

        return decorator

    def count(self, count: av.AvCount):
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.base.count = count
            return fn

        return decorator

    def aspect(self, aspect: av.AvAspect):
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.base.aspect = aspect
            return fn

        return decorator

    def context(self, context: av.AvContext):
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.base.context = context
            return fn

        return decorator

    def category(self, category: av.AvCategory):
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.base.category = category
            return fn

        return decorator

    def klass(self, klass: av.AvClass):
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.base.klass = klass
            return fn

        return decorator

    def event(self, event: av.AvEvent):
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.base.event = event
            return fn

        return decorator

    def mode(self, mode: av.AvMode):
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.base.mode = mode
            return fn

        return decorator

    def state(self, state: av.AvState):
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.base.state = state
            return fn

        return decorator

    def condition(self, condition: av.AxCondition):
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.base.condition = condition
            return fn

        return decorator

    def value_in(self, value_type: ValueType):
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.value_in = value_type
            return fn

        return decorator

    def value_out(self, value_type: ValueType):
        def decorator(fn: Callable[..., av.AvValue]):
            route = self._route(fn)
            route._method.value_out = value_type
            route.value_out_set = True
            return fn

        return decorator

    def on_outlet_init(self, fn: Callable):
        """
        This function will be called after the outlet of the adapter is fully
        initialized, but before we call adapt on it.
        Use this function to do any modication to the outlet
        """
        self._on_outlet_init = fn
        return fn

    def on_shutdown(self, fn: Callable):
        """
        This function will be called when the adapter shuts down, no matter what.
        Use that for whatever cleanup you need to ensure happens.
        This function is called before calling `av.finalize()`.

        This function should NOT take more than 10s to execute. When running in
        docker, if a container isn't shutdown 10s after the SIGTERM, it gets
        SIGKILL, therefore the execution risk being abruptly killed after 10s.
        """
        self._adapter._on_shutdown = fn
        return fn

    def health_reporter(self, fn: Callable[[], Health]):
        """
        This function will be called regularly to report the health of the
        adapter.
        The function should return a string that will be used as the health
        report of the adapter.

        "GREEN" means the adapter is healthy.
        "YELLOW" means the adapter can function, but a human should investigate
        why it's not green. Do not report "YELLOW" if the adapter does not
        require human investigation.
        "RED" means the adapter is not healthy and cannot function.
        """
        self._health_reporter = fn
        return fn

    def generate_interface(self):
        """
        Only safe to call once all the routes are properly declared
        """
        for fnname, route in self._routes.items():
            if not route.name_set:
                raise ValueError(
                    f'{fnname}: Name not set, did you forgot to add the decorator `@adapter.route("<Route name>")` ?'
                )

            if not route.value_out_set:
                raise ValueError(
                    f"{fnname}: value_out is not set, did you forgot to add the decorator eg. `@adapter.value_out(<value type>)` ?"
                )

            if av.AvAspect.VALUE in route._method.args:
                if route._method.value_in.tag == av.AvTag.NULL:
                    raise ValueError(
                        f"{fnname}: Takes value as parameter but value_in is not set, did you forgot to add the decorator eg. `@adapter.value_in(<value type>)` ?"
                    )

        return Interface(
            self._mount_key,
            self._version,
            self._description,
            [r._method for r in self._routes.values()],
        )

    def call_history(self, route: Callable) -> list[_hns.CallStat]:
        """
        Returns the list of recent calls made to the given route

        ```py
        call_history = adapter.call_history(mymethod) # `mymethod` is a function with the @adapter.route("...") decorator
        # If call history isn't empty
        if call_history:
            last_call = call_history[-1]
            print("Last call for lookup_dns:")
            print(f"  On: {last_call.timestamp}")
            print(f"  Took: {last_call.restime} seconds")
            print(f"  Exception raised: {last_call.exception}")
        ```
        """
        if route.__name__ not in self._routes:
            raise KeyError(f"'{route.__name__}' is not a valid route. Valid routes are {list(self._routes.keys())}")
        method_name = self._routes[route.__name__]._method.name
        return list(_hns.g_routes.get(method_name, []))

    def run(self, _forced_outlet: av.AvEntity | None = None):
        self._adapter.interface = self.generate_interface()
        self._adapter.init_outlet(_forced_outlet)
        if self._on_outlet_init is not None:
            self._on_outlet_init()
        Thread(
            target=_hns.health_n_status_thread,
            args=(self.outlet, self.auth, self._health_reporter),
            daemon=True,
        ).start()
        _log_publisher.clear_log(self.outlet, self.auth)
        Thread(
            target=_log_publisher.log_publisher_thread,
            args=(self.outlet, self.auth),
            daemon=True,
        ).start()
        self._adapter.run()

    def shutdown(self):
        """Will call av.finalize()"""
        self._adapter.shutdown()

    def invoke_callback(self, args: av.InvokeArgs) -> av.AvValue:
        for route in self._routes.values():
            base = route._method.base
            if base.method is not None and base.method != args.method:
                continue
            if base.attribute is not None and base.attribute != args.attribute:
                continue
            if base.key is not None and base.key != args.key:
                continue
            if base.name is not None and base.name != args.name:
                continue
            if base.parameter is not None and base.parameter != args.parameter:
                continue
            if base.resultant is not None and base.resultant != args.resultant:
                continue
            if base.index is not None and base.index != args.index:
                continue
            if base.instance is not None and base.instance != args.instance:
                continue
            if base.offset is not None and base.offset != args.offset:
                continue
            if base.count is not None and base.count != args.count:
                continue
            if base.aspect is not None and base.aspect != args.aspect:
                continue
            if base.context is not None and base.context != args.context:
                continue
            if base.category is not None and base.category != args.category:
                continue
            if base.klass is not None and base.klass != args.klass:
                continue
            if base.event is not None and base.event != args.event:
                continue
            if base.mode is not None and base.mode != args.mode:
                continue
            if base.state is not None and base.state != args.state:
                continue
            if base.condition is not None and base.condition != args.condition:
                continue

            kwargs = {}
            if "mask" in inspect.signature(route.callback).parameters:
                kwargs["mask"] = args.mask

            for arg in route._method.args:
                match arg:
                    case av.AvAspect.ENTITY:
                        kwargs["entity"] = args.entity
                    case av.AvAspect.OUTLET:
                        kwargs["outlet"] = args.outlet
                    case av.AvAspect.METHOD:
                        kwargs["method"] = args.method
                    case av.AvAspect.ATTRIBUTE:
                        kwargs["attribute"] = args.attribute
                    case av.AvAspect.NAME:
                        kwargs["name"] = args.name
                    case av.AvAspect.KEY:
                        kwargs["key"] = args.key
                    case av.AvAspect.VALUE:
                        kwargs["value"] = args.value
                    case av.AvAspect.PARAMETER:
                        kwargs["parameter"] = args.parameter
                    case av.AvAspect.INDEX:
                        kwargs["index"] = args.index
                    case av.AvAspect.INSTANCE:
                        kwargs["instance"] = args.instance
                    case av.AvAspect.COUNT:
                        kwargs["count"] = args.count
                    case av.AvAspect.ASPECT:
                        kwargs["aspect"] = args.aspect
                    case av.AvAspect.CONTEXT:
                        kwargs["context"] = args.context
                    case av.AvAspect.CATEGORY:
                        kwargs["category"] = args.category
                    case av.AvAspect.CLASS:
                        kwargs["klass"] = args.klass
                    case av.AvAspect.EVENT:
                        kwargs["event"] = args.event
                    case av.AvAspect.MODE:
                        kwargs["mode"] = args.mode
                    case av.AvAspect.PRECEDENCE:
                        kwargs["precedence"] = args.precedence
                    case av.AvAspect.TIME:
                        kwargs["time"] = args.time
                    case av.AvAspect.TIMEOUT:
                        kwargs["timeout"] = args.timeout
                    case av.AvAspect.AUXILIARY:
                        kwargs["auxiliary"] = args.auxiliary
                    case av.AvAspect.ANCILLARY:
                        kwargs["ancillary"] = args.ancillary
                    case av.AvAspect.AUTHORIZATION:
                        kwargs["authorization"] = args.authorization
                    case av.AvAspect.AUTHORITY:
                        kwargs["authority"] = args.authority

            start_time = time.time()
            try:
                with _hns.MonitorStats(route._method.name):
                    res = route.callback(**kwargs)
            except Exception as e:
                dt = time.time() - start_time
                av.av_log.debug(
                    f"calltimer {route._method.name}: Error in {dt:.3f}s: {repr(e)}"
                )
                if route.print_exc_trace:
                    av.av_log.debug(traceback.format_exc())
                raise
            dt = time.time() - start_time
            av.av_log.debug(f"calltimer {route._method.name}: Success in {dt:.3f}s")
            return res

        raise AdapterError(f"No matching route found for request {args=}")
