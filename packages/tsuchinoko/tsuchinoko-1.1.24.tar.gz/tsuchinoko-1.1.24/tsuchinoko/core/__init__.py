import os
import threading
import time
from asyncio import events
from enum import Enum, auto
from pickle import UnpicklingError
from queue import Queue
from appdirs import user_state_dir

from loguru import logger
from yaml import dump

from .messages import FullDataRequest, FullDataResponse, PartialDataRequest, PartialDataResponse, StartRequest, \
    UnknownResponse, PauseRequest, StateRequest, GetParametersRequest, SetParameterRequest, GetParametersResponse, \
    SetParameterResponse, StopRequest, StateResponse, MeasureRequest, \
    MeasureResponse, ConnectRequest, ConnectResponse, ExceptionResponse, PushDataRequest, PushDataResponse, \
    GraphsResponse, ReplayResponse
from ..adaptive import Engine as AdaptiveEngine, Data
from ..execution import Engine as ExecutionEngine
from ..utils.logging import log_time

user_state_dir = user_state_dir('tsuchinoko','camera')

class CoreState(Enum):
    Connecting = auto()
    Inactive = auto()
    Starting = auto()
    Running = auto()
    Pausing = auto()
    Paused = auto()
    Resuming = auto()
    Stopping = auto()
    Restarting = auto()
    Exiting = auto()


SLEEP_FOR_FRESH_DATA_TIME = .1


class Core:
    def __init__(self,
                 execution_engine: ExecutionEngine = None,
                 adaptive_engine: AdaptiveEngine = None,
                 compute_metrics: bool = True):
        self.execution_engine = execution_engine
        self.adaptive_engine = adaptive_engine

        self.iteration = 0

        self._state = CoreState.Inactive
        self._exception_queue = Queue()
        self._forced_position_queue = Queue()
        self._forced_measurement_queue = Queue()
        self._has_fresh_data = True
        self.compute_metrics = compute_metrics
        self.checkpoint_template = 'checkpoint_{n}.yml'
        self.checkpoint_at = []
        self.pause_at = []
        self.stop_at = []
        self.exit_at = []
        self.compute_metrics_at = []

        self.data = Data()
        self._graphs = []

        self.experiment_thread = None

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        logger.info(f'Changing core state to {value}')
        self._state = value

    def set_execution_engine(self, engine: ExecutionEngine):
        self.execution_engine = engine

    def set_adaptive_engine(self, engine: AdaptiveEngine):
        self.adaptive_engine = engine

    def main(self, debug=False):
        loop = events.new_event_loop()  # <---- this ensures the current loop is replaced
        try:
            events.set_event_loop(loop)
            loop.set_debug(debug)
            return loop.run_until_complete(self._main())
        finally:
            try:
                # _cancel_all_tasks(loop)
                loop.run_until_complete(loop.shutdown_asyncgens())
            finally:
                events.set_event_loop(None)
                loop.close()

    async def _main(self, min_response_sleep=.1):
        while self.state != CoreState.Exiting:

            if self.state == CoreState.Running:
                pass
                # await sleep(min_response_sleep)  # short-circuit case
            elif self.state == CoreState.Starting:
                if not len(self.data):
                    self.data = Data(dimensionality=self.adaptive_engine.dimensionality)
                self.adaptive_engine.reset()
                self.experiment_thread = threading.Thread(target=self.experiment_loop, args=())  # must hold ref
                self.experiment_thread.start()
                self.state = CoreState.Running

            elif self.state == CoreState.Inactive:
                pass
                # await sleep(min_response_sleep)

            elif self.state == CoreState.Paused:
                pass
                # await sleep(min_response_sleep)

            elif self.state == CoreState.Pausing:
                self.state = CoreState.Paused

            elif self.state == CoreState.Resuming:
                self.state = CoreState.Running

            elif self.state == CoreState.Stopping:
                self.state = CoreState.Inactive
                self.data = Data()
                # await sleep(min_response_sleep)

            if self.state not in [CoreState.Stopping, CoreState.Exiting, CoreState.Resuming, CoreState.Restarting]:
                await self.notify_clients()

    def experiment_loop(self):
        while True:
            if self.state == CoreState.Running:
                logger.info(f'Iteration: {self.data._completed_iterations}, Data count: {len(self.data)}')
                if self.data._completed_iterations in self.checkpoint_at:
                    self.save_checkpoint()
                if self.data._completed_iterations in self.pause_at:
                    self.state = CoreState.Pausing
                    continue
                if self.data._completed_iterations in self.stop_at:
                    self.state = CoreState.Stopping
                    return
                if self.data._completed_iterations in self.exit_at:
                    self.state = CoreState.Exiting
                    return
                try:
                    self.experiment_iteration()
                except Exception as ex:
                    self._exception_queue.put(ex)
                    self.state = CoreState.Pausing
                    logger.exception(ex)
            elif self.state in [CoreState.Stopping, CoreState.Inactive, CoreState.Exiting]:
                return
            else:
                time.sleep(.1)

    def experiment_iteration(self):
        with self.data.iteration():
            if self._has_fresh_data:
                with log_time('getting position', cumulative_key='getting position'):
                    position = self.execution_engine.get_position()
                    logger.info(f'position: {position}')
                    if position is None:
                        position = [0] * self.data.dimensionality
                    position = tuple(position)
                if self._forced_position_queue.empty():
                    with log_time('getting targets', cumulative_key='getting targets'):
                        targets = self.adaptive_engine.request_targets(position)
                    logger.info(f'targets: {targets}')
                else:
                    targets = [self._forced_position_queue.get()]

            if self._forced_measurement_queue.empty():
                if self._has_fresh_data:
                    with log_time('updating targets', cumulative_key='updating targets'):
                        self.execution_engine.update_targets(targets)
                    self._has_fresh_data = False
                with log_time('getting measurements', cumulative_key='getting measurements'):
                    new_measurements = self.execution_engine.get_measurements()
                logger.info(f'new measurements: {new_measurements}')
            else:
                new_measurements = [self._forced_measurement_queue.get()]
            if len(new_measurements):
                self._has_fresh_data = True
                with log_time('stashing new measurements', cumulative_key='injecting new measurements'):
                    self.data.inject_new(new_measurements)
                with log_time('updating engine with new measurements', cumulative_key='updating engine with new measurements'):
                    self.adaptive_engine.update_measurements(self.data)
                if self.compute_metrics or len(self.data) in self.compute_metrics_at:
                    with log_time('updating metrics', cumulative_key='updating metrics'):
                        self.adaptive_engine.update_metrics(self.data)
            else:
                time.sleep(SLEEP_FOR_FRESH_DATA_TIME)
            if self._has_fresh_data:
                with log_time('training', cumulative_key='training'):
                    self.adaptive_engine.train()
            else:
                logger.info('Current data is stale. Waiting for an update with fresh data.')

    async def notify_clients(self):
        ...

    @property
    def graphs(self):
        execution_graphs = getattr(self.execution_engine, 'graphs', []) or []
        adaptive_graphs = getattr(self.adaptive_engine, 'graphs', []) or []
        return execution_graphs + adaptive_graphs + self._graphs

    @graphs.setter
    def graphs(self, graphs):
        raise NotImplementedError('Updating graphs on server not supported yet.')

    def update_graph(self, new_graph):
        execution_graphs = getattr(self.execution_engine, 'graphs', []) or []
        adaptive_graphs = getattr(self.adaptive_engine, 'graphs', []) or []
        self_graphs = self._graphs

        for graph_list in [execution_graphs, adaptive_graphs, self_graphs]:
            for i, old_graph in enumerate(graph_list):
                if old_graph.id == new_graph.id:
                    graph_list[i] = new_graph
                    return
        else:
            raise ValueError('Graph not found in graphs lists.')

    def initialize_data(self, x, y, v):
        with log_time('updating engine with initial measurements'):
            self.data = Data(dimensionality=len(x[0]), positions=x, scores=y, variances=v)
            self.adaptive_engine.update_measurements(self.data)

    def save_checkpoint(self, directory=user_state_dir):
        checkpoint_file_path = os.path.join(directory,
                                            self.checkpoint_template.format(n=self.data._completed_iterations))
        os.makedirs(os.path.dirname(checkpoint_file_path), exist_ok=True)
        dump(self.data.as_dict(), open(checkpoint_file_path, 'w'))


class ZMQCore(Core):
    def __init__(self, *args, **kwargs):
        super(ZMQCore, self).__init__(*args, **kwargs)
        # self.start_server()
        self.context = None
        self.poller = None

    def start_server(self):
        import zmq
        from zmq.asyncio import Context, Poller
        self.poller = Poller()
        self.context = Context()
        socket = self.context.socket(zmq.REP)
        socket.bind("tcp://*:5555")
        self.poller.register(socket, zmq.POLLIN)

    def respond_FullDataRequest(self, request):
        with self.data.r_lock():
            return FullDataResponse(self.data.as_dict())

    def respond_PartialDataRequest(self, request):
        if self.data and request.iteration <= len(self.data) and self.state == CoreState.Running:
            with self.data.r_lock():
                partial_data = self.data[request.iteration:]
            return PartialDataResponse(partial_data.as_dict(), request.iteration)
        else:
            return StateResponse(self.state, self.compute_metrics)

    def respond_PushDataRequest(self, request):
        self.data = Data(**request.data)
        return PushDataResponse()

    def respond_StartRequest(self, request):
        if self.state == CoreState.Paused:
            self.state = CoreState.Resuming
        elif self.state == CoreState.Inactive:
            self.state = CoreState.Starting
        return StateResponse(self.state, self.compute_metrics)

    def respond_StopRequest(self, request):
        self.state = CoreState.Stopping
        self.experiment_thread.join()
        return StateResponse(self.state, self.compute_metrics)

    def respond_ExitRequest(self, request):
        self.state = CoreState.Exiting
        return StateResponse(self.state, self.compute_metrics)

    def respond_PauseRequest(self, request):
        self.state = CoreState.Pausing
        return StateResponse(self.state, self.compute_metrics)

    def respond_StateRequest(self, request):
        if not self._exception_queue.empty():
            return ExceptionResponse(self._exception_queue.get())
        else:
            return StateResponse(self.state, self.compute_metrics)

    def respond_GetParametersRequest(self, request):
        return GetParametersResponse(self.adaptive_engine.parameters.saveState())

    def respond_SetParameterRequest(self, request):
        self.adaptive_engine.parameters.child(*request.child_path).setValue(request.value)
        return SetParameterResponse(True)

    def respond_MeasureRequest(self, request):
        self._forced_position_queue.put(request.position)
        return MeasureResponse(True)

    def respond_ConnectRequest(self, request):
        return ConnectResponse(self.state, self.compute_metrics)

    def respond_PullGraphsRequest(self, request):
        return GraphsResponse(self.graphs)

    def respond_PushGraphsRequest(self, request):
        for graph in request.graphs:
            try:
                self.update_graph(graph)
            except ValueError as ex:
                return ExceptionResponse("Graph ID not found in server's graphs.")
        # self.graphs = request.graphs
        return StateResponse(self.state, self.compute_metrics)

    def respond_SetComputeMetricsRequest(self, request):
        self.compute_metrics = request.compute_metrics
        return StateResponse(self.state, self.compute_metrics)

    def respond_ReplayRequest(self, request):
        self._forced_measurement_queue.queue.clear()
        self._forced_position_queue.queue.clear()

        for position in request.positions:
            self._forced_position_queue.put(position)
        for measurement in request.measurements:
            self._forced_measurement_queue.put(measurement)
        logger.critical(f'Queue lengths: {len(self._forced_measurement_queue.queue)} {len(self._forced_position_queue.queue)}')
        return ReplayResponse(True)

    async def notify_clients(self):
        import zmq
        if not self.poller:
            self.start_server()

        sockets = dict(await self.poller.poll(timeout=.1))
        for socket in sockets:
            try:
                request = await socket.recv_pyobj(zmq.NOBLOCK)
            except (zmq.ZMQError, zmq.error.Again) as ex:
                logger.exception(ex)
            except UnpicklingError as ex:
                logger.exception(ex)
                logger.critical('The above error prevented unpacking data from the client.')
            else:
                if not request:
                    time.sleep(.1)
                    continue

                logger.info(f"Received request: {request}")
                with log_time('preparing response', cumulative_key='preparing response'):
                    responder = getattr(self, f'respond_{request.__class__.__name__}', None)
                    if responder:
                        try:
                            response = responder(request)
                        except Exception as ex:
                            response = ExceptionResponse(ex)
                    else:
                        response = UnknownResponse()

                logger.info(f'Sending response: {response}')
                await socket.send_pyobj(response)

                if isinstance(response, UnknownResponse):
                    logger.exception(ValueError(f'Unknown request received: {request}'))
                    time.sleep(.1)

    def exit_later(self):
        self.state = CoreState.Exiting

    def exit(self):
        self.exit_later()
        self.experiment_thread.join()
