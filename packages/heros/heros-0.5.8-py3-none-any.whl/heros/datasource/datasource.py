import asyncio

from heros import HEROPeer, LocalHERO
from heros.event import event
from heros.helper import log, object_name_from_keyexpr
from .types import DatasourceReturnSet, DatasourceReturnValue
from .observables import ObservableProcessor


class LocalDatasourceHERO(LocalHERO):
    """
    A datasource is a HERO that can provide information on a standardized interface.
    This interface is the event `new_data`. Instances in the zenoh network interested in the data provided
    by data sources can simply subscribe to the key expression `@objects/realm/*/new_data` or use
    the :class:`DatasourceObserver`.

    To make your class a LocalDatasourceHERO make it inherit this class.
    This class is meant for datasources that create asynchronous events on their own. When processing such an event
    call `new_data` to publish the data from this datasource.

    Args:
        name: name/identifier under which the object is available. Make sure this name is unique in the realm.
        realm: realm the HERO should exist in. default is "heros"
    """

    def __init__(self, *args, observables: dict | None = None, **kwargs):
        observables = {} if observables is None else observables
        LocalHERO.__init__(self, *args, **kwargs)
        self.observable_processor = ObservableProcessor(observables)

    def _process_data(self, data):
        return self.observable_processor(DatasourceReturnSet.from_data(data))

    @event
    def new_data(self, data):
        return self._process_data(data)


class DatasourceObserver(HEROPeer):
    """
    A class that can observe and handle the data emitted by one or more datasource HEROs.
    In particular, this class provides an efficient way to listen to the data emitted by all datasource HEROs in
    the realm. By not instantiating the HEROs themselves but just subscribing to the topics for the datasource, this
    reduces the pressure on the backing zenoh network. If, however, only the data of a few HEROs should be observed,
    it might make more sense to just instantiate the according RemoteHEROs and connect a callback to their `new_data`
    signal.

    Args:
        object_selector: selector to specify which objects to observe. This becomes part of a zenoh selector and thus
        can be anything that makes sense in the selector. Defaults to * to observe all HEROs in the realm.
    """
    def __init__(self, object_selector: str = "*", *args, **kwargs):
        HEROPeer.__init__(self, *args, **kwargs)
        self._object_selector = object_selector

        self._new_data_callbacks = []

        zenoh_selector = "/".join([self._ns_objects, self._realm, object_selector, "new_data"])
        self._subscription = self._subscribe_selector(zenoh_selector, self._handle_new_data)

    def _handle_new_data(self, key_expr: str, data):
        for cb in self._new_data_callbacks:
            try:
                object_name = object_name_from_keyexpr(str(key_expr), self._ns_objects, self._realm, "new_data")
                try:
                    data = DatasourceReturnSet([DatasourceReturnValue(**d) for d in data])
                except Exception:
                    pass
                cb(object_name, data)
            except Exception as e:
                log.error(f"Could not call callback {cb} for new data: {e}")

    def register_new_data_callback(self, func: callable):
        """
        Register a callback that should be called when a new HERO joins the realm.

        Args:
            func: function to call when a new HERO joins the realm
        """
        if func not in self._new_data_callbacks:
            self._new_data_callbacks.append(func)


class PolledLocalDatasourceHERO(LocalDatasourceHERO):
    """
    This local HERO periodically triggers the event "new_data" to poll and publish data.
    This class is meant for datasources that do not generate events on their own an thus should be polled
    on a periodical basis.

    To make your class a PolledLocalDatasourceHERO make it inherit this class an implement the method `_new_data`.
    The method will get called periodically and the return value will be published as an event.

    Note:
        The periodic calling is realized via asyncio and will thus only work if the asyncio mainloop is
        started.

    Args:
        name: name/identifier under which the object is available. Make sure this name is unique in the realm.
        realm: realm the HERO should exist in. default is "heros"
        interval: time interval in seconds between consecutive calls of `new_data` event
    """
    def __init__(self, *args, loop, interval: float = 5, **kwargs):
        LocalDatasourceHERO.__init__(self, *args, **kwargs)
        self.datasource_interval = interval
        self._loop = loop

        self._loop.create_task(self._trigger_datasource())

    async def _trigger_datasource(self):
        while True:
            self.new_data()
            await asyncio.sleep(self.datasource_interval)

    @event
    def new_data(self):
        return self._process_data(self._new_data())

    def _new_data(self):
        raise NotImplementedError("Implement _new_data() in a subclass of PolledLocalDatasourceHERO")
