# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel

__all__ = ["ManagementRetrieveTokioResponse", "Worker"]


class Worker(BaseModel):
    worker_id: int

    worker_local_schedule_count: int
    """
    Returns the number of tasks scheduled from within the runtime on the given
    worker’s local queue.

    The local schedule count starts at zero when the runtime is created and
    increases by one each time a task is woken from inside of the runtime on the
    given worker. This usually means that a task is spawned or notified from within
    a runtime thread and will be queued on the worker-local queue.

    The counter is monotonically increasing. It is never decremented or reset to
    zero.
    """

    worker_noop_count: int
    """
    Returns the number of times the given worker thread unparked but performed no
    work before parking again.

    The worker no-op count starts at zero when the runtime is created and increases
    by one each time the worker unparks the thread but finds no new work and goes
    back to sleep. This indicates a false-positive wake up.

    The counter is monotonically increasing. It is never decremented or reset to
    zero.
    """

    worker_overflow_count: int
    """Returns the number of times the given worker thread saturated its local queue.

    This metric only applies to the multi-threaded scheduler.

    The worker overflow count starts at zero when the runtime is created and
    increases by one each time the worker attempts to schedule a task locally, but
    its local queue is full. When this happens, half of the local queue is moved to
    the injection queue.

    The counter is monotonically increasing. It is never decremented or reset to
    zero.
    """

    worker_park_count: int
    """Returns the total number of times the given worker thread has parked.

    The worker park count starts at zero when the runtime is created and increases
    by one each time the worker parks the thread waiting for new inbound events to
    process. This usually means the worker has processed all pending work and is
    currently idle.

    The counter is monotonically increasing. It is never decremented or reset to
    zero.
    """

    worker_park_unpark_count: int
    """
    Returns the total number of times the given worker thread has parked and
    unparked.

    The worker park/unpark count starts at zero when the runtime is created and
    increases by one each time the worker parks the thread waiting for new inbound
    events to process. This usually means the worker has processed all pending work
    and is currently idle. When new work becomes available, the worker is unparked
    and the park/unpark count is again increased by one.

    An odd count means that the worker is currently parked. An even count means that
    the worker is currently active.

    The counter is monotonically increasing. It is never decremented or reset to
    zero.
    """

    worker_poll_count: int
    """Returns the number of tasks the given worker thread has polled.

    The worker poll count starts at zero when the runtime is created and increases
    by one each time the worker polls a scheduled task.

    The counter is monotonically increasing. It is never decremented or reset to
    zero.
    """

    worker_steal_count: int
    """
    Returns the number of tasks the given worker thread stole from another worker
    thread.

    This metric only applies to the multi-threaded runtime and will always return 0
    when using the current thread runtime.

    The worker steal count starts at zero when the runtime is created and increases
    by N each time the worker has processed its scheduled queue and successfully
    steals N more pending tasks from another worker.

    The counter is monotonically increasing. It is never decremented or reset to
    zero.
    """

    worker_steal_operations: int
    """
    Returns the number of times the given worker thread stole tasks from another
    worker thread.

    This metric only applies to the multi-threaded runtime and will always return 0
    when using the current thread runtime.

    The worker steal count starts at zero when the runtime is created and increases
    by one each time the worker has processed its scheduled queue and successfully
    steals more pending tasks from another worker.

    The counter is monotonically increasing. It is never decremented or reset to
    zero.
    """


class ManagementRetrieveTokioResponse(BaseModel):
    budget_forced_yield_count: int
    """
    Returns the number of times that tasks have been forced to yield back to the
    scheduler after exhausting their task budgets.

    This count starts at zero when the runtime is created and increases by one each
    time a task yields due to exhausting its budget.

    The counter is monotonically increasing. It is never decremented or reset to
    zero.
    """

    dump: List[str]

    global_queue_depth: int
    """Returns the number of tasks currently scheduled in the runtime’s global queue.

    Tasks that are spawned or notified from a non-runtime thread are scheduled using
    the runtime’s global queue. This metric returns the current number of tasks
    pending in the global queue. As such, the returned value may increase or
    decrease as new tasks are scheduled and processed.
    """

    io_driver_fd_deregistered_count: int
    """
    Returns the number of file descriptors that have been deregistered by the
    runtime’s I/O driver.
    """

    io_driver_fd_registered_count: int
    """
    Returns the number of file descriptors that have been registered with the
    runtime’s I/O driver.
    """

    io_driver_ready_count: int
    """Returns the number of ready events processed by the runtime’s I/O driver."""

    num_alive_tasks: int
    """Returns the current number of alive tasks in the runtime.

    This counter increases when a task is spawned and decreases when a task exits.
    """

    num_blocking_threads: int
    """Returns the number of additional threads spawned by the runtime.

    The number of workers is set by configuring max_blocking_threads on
    runtime::Builder.
    """

    num_workers: int
    """Returns the number of worker threads used by the runtime.

    The number of workers is set by configuring worker_threads on runtime::Builder.
    When using the current_thread runtime, the return value is always 1.
    """

    remote_schedule_count: int
    """Returns the number of tasks scheduled from outside of the runtime.

    The remote schedule count starts at zero when the runtime is created and
    increases by one each time a task is woken from outside of the runtime. This
    usually means that a task is spawned or notified from a non-runtime thread and
    must be queued using the Runtime’s injection queue, which tends to be slower.

    The counter is monotonically increasing. It is never decremented or reset to
    zero.
    """

    spawned_tasks_count: int
    """Returns the number of tasks spawned in this runtime since it was created.

    This count starts at zero when the runtime is created and increases by one each
    time a task is spawned.

    The counter is monotonically increasing. It is never decremented or reset to
    zero.
    """

    workers: List[Worker]
