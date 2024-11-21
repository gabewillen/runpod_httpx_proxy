"""
This module defines custom types and type hints for the RunPod Serverless Worker.
It includes:
- Custom TypedDict classes for job and configuration data structures
- Type aliases for different handler function signatures
- Type variables and parameter specifications for generic typing
Note: These types are intentionally verbose and explicit to make them understanble and prevent conflicts with other types.
      Additionally, you can use these with `Unpack` to accept them as keyword arguments.
"""

import typing

try:
    # For Python 3.8 and newer versions
    from typing import TypedDict
except ImportError:
    # For Python 3.7 and older versions
    from typing_extensions import TypedDict


JSONPrimitive = typing.Union[str, int, float, bool, None]
JSONArray = typing.Annotated[
    typing.List[typing.Union[JSONPrimitive, "JSONArray", "JSONObject"]], "JSON Array"
]


JSONObject = typing.Annotated[
    typing.Dict[
        str,
        typing.Union[
            JSONPrimitive,
            JSONArray,
            typing.Dict[str, typing.Union[JSONPrimitive, JSONArray]],
        ],
    ],
    "JSON Object",
]
JSON = typing.Annotated[
    typing.Union[JSONPrimitive, JSONArray, JSONObject],
    "JSON",
]
JobInput = typing.TypeVar("JobInput")


# job type add any job related info here alternatively you can extend this type for custom job types. This is purely for type hinting and to improve developer experience.
class JobDict(typing.Generic[JobInput], TypedDict):
    id: typing.Annotated[str, "Unique identifier for the job"]
    input: typing.Annotated[JobInput, "the input for the job"]


# handler types
SyncFunctionHandler = typing.Annotated[
    typing.Callable[[JobDict[typing.Any]], JSON],
    "Synchronous handler function that returns an Iterable",
]
AsyncFunctionHandler = typing.Annotated[
    typing.Callable[[JobDict[typing.Any]], typing.Generator[JSON, None, None]],
    "Asynchronous handler function that returns an AsyncIterable",
]
GeneratorFunctionHandler = typing.Annotated[
    typing.Callable[[JobDict[typing.Any]], typing.Generator[JSON, None, None]],
    "Generator handler function that yields Iterables",
]
AsyncGeneratorFunctionHandler = typing.Annotated[
    typing.Callable[[JobDict[typing.Any]], typing.AsyncGenerator[JSON, None]],
    "Async generator handler function that yields JSON",
]

Handler = typing.Annotated[
    typing.Union[
        JSON,
        typing.Generator[JSON, None, None],
        typing.AsyncGenerator[JSON, None],
        typing.Coroutine[None, None, JSON],
    ],
    "Handler function",
]


class RunpodArgsDict(TypedDict):
    rp_log_level: typing.Annotated[typing.Optional[str], "Log level for the worker"]
    rp_debugger: typing.Annotated[typing.Optional[bool], "Flag to enable debugger"]
    rp_serve_api: typing.Annotated[typing.Optional[bool], "Flag to serve API"]
    rp_api_port: typing.Annotated[typing.Optional[int], "Port for API server"]
    rp_api_concurrency: typing.Annotated[
        typing.Optional[int], "Concurrency for API server"
    ]
    rp_api_host: typing.Annotated[typing.Optional[str], "Host for API server"]
    test_input: typing.Annotated[typing.Optional[str], "Test input for the worker"]


class StartConfigDict(TypedDict):
    handler: Handler
    return_aggregate_stream: typing.Annotated[
        typing.Optional[bool], "Flag to return aggregate stream"
    ]
    concurrency_modifier: typing.Annotated[
        typing.Optional[typing.Callable[[int], int]],
        "Function to modify concurrency",
    ]
    rp_args: typing.Annotated[
        typing.Optional[RunpodArgsDict],
        "RunPod specific arguments",
    ]


class WorkerConfigDict(StartConfigDict):
    reference_counter_start: typing.Annotated[
        typing.Optional[float], "Start time of the worker"
    ]


class Singleton:
    """Singleton class."""

    _instance: typing.ClassVar[typing.Optional[typing.Self]] = None

    @classmethod
    def __new__(cls: typing.Type[typing.Self]) -> typing.Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return typing.cast(typing.Self, cls._instance)


Status = typing.Annotated[
    typing.Literal[
        typing.Annotated[
            typing.Literal["IN_QUEUE"],
            "Job is waiting in endpoint queue for an available worker",
        ],
        typing.Annotated[
            typing.Literal["IN_PROGRESS"],
            "Job is actively being processed by a worker",
        ],
        typing.Annotated[
            typing.Literal["COMPLETED"],
            "Job finished processing successfully with a result",
        ],
        typing.Annotated[
            typing.Literal["FAILED"],
            "Job encountered an error during execution",
        ],
        typing.Annotated[
            typing.Literal["CANCELLED"],
            "Job was manually cancelled before completion",
        ],
        typing.Annotated[
            typing.Literal["TIMED_OUT"],
            "Job expired in queue or worker failed to report result in time",
        ],
    ],
    "Status of the job",
]


class StatusDict(TypedDict):
    id: typing.Annotated[str, "Unique identifier for the job"]
    status: Status


class RunResponseDict(StatusDict):
    pass


class JobHealthDict(TypedDict):
    completed: typing.Annotated[int, "Number of completed jobs"]
    failed: typing.Annotated[int, "Number of failed jobs"]
    cancelled: typing.Annotated[int, "Number of cancelled jobs"]
    timedOut: typing.Annotated[int, "Number of timed out jobs"]
    inQueue: typing.Annotated[int, "Number of jobs in queue"]
    retried: typing.Annotated[int, "Number of retried jobs"]


class CancelResponseDict(StatusDict):
    pass


class PurgeQueueResponseDict(StatusDict):
    removed: typing.Annotated[int, "Number of jobs removed from queue"]


class WorkerHealthDict(TypedDict):
    idle: typing.Annotated[int, "Number of idle workers"]
    running: typing.Annotated[int, "Number of running workers"]


class HealthResponseDict(TypedDict):
    jobs: typing.Annotated[JobHealthDict, "Job health metrics"]
    workers: typing.Annotated[WorkerHealthDict, "Worker health metrics"]


class RunSyncResponseDict(StatusDict):
    delayTime: typing.Annotated[int, "Delay time in seconds"]
    executionTime: typing.Annotated[int, "Execution time in seconds"]
    output: typing.Annotated[JSON, "Output of the job"]


class JobOutputDict(TypedDict):
    output: typing.Annotated[JSON, "Output of the job"]


class JobErrorDict(TypedDict):
    error: typing.Annotated[JSON, "Error from the job"]
