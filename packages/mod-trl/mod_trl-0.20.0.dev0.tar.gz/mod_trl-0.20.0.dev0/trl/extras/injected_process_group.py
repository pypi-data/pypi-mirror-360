import pickle
import sys
import time
import traceback
import uuid
import socket
from datetime import timedelta
from typing import Optional, Any

from torch._C._distributed_c10d import TCPStore
from vllm.distributed import sched_yield, StatelessProcessGroup


class InjectedStatelessProcessGroup(StatelessProcessGroup):
    def __post_init__(self):
        self.flag_broadcast_obj_called = 0
        assert self.rank < self.world_size
        self.send_dst_counter = {i: 0 for i in range(self.world_size)}
        self.recv_src_counter = {i: 0 for i in range(self.world_size)}
        self.broadcast_recv_src_counter = {
            i: 0
            for i in range(self.world_size)
        }

    def expire_data(self):
        """Expire data that is older than `data_expiration_seconds` seconds."""
        while self.entries:
            # check the oldest entry
            key, timestamp = self.entries[0]
            if time.time() - timestamp > self.data_expiration_seconds:
                self.store.delete_key(key)
                self.entries.popleft()
            else:
                break

    def broadcast_obj(self, obj: Optional[Any], src: int) -> Any:
        """Broadcast an object from a source rank to all other ranks.
        It does not clean up after all ranks have received the object.
        Use it for limited times, e.g., for initialization.
        """
        self.flag_broadcast_obj_called += 1
        if self.rank == src:
            self.expire_data()
            key = (f"broadcast_from/{src}/"
                   f"{self.broadcast_send_counter}")
            self.store.set(key, pickle.dumps(obj))
            self.broadcast_send_counter += 1
            self.entries.append((key, time.time()))
            return obj
        else:
            key = (f"broadcast_from/{src}/"
                   f"{self.broadcast_recv_src_counter[src]}")  # TODO: why 0/1
            store_get_key = self.store.get(key)
            recv_obj = pickle.loads(store_get_key)
            self.broadcast_recv_src_counter[src] += 1
            return recv_obj
    @staticmethod
    def create(
            host: str,
            port: int,
            rank: int,
            world_size: int,
            data_expiration_seconds: int = 3600,
            store_timeout: int = 300,
    ) -> "InjectedStatelessProcessGroup":
        """A replacement for `torch.distributed.init_process_group` that does not
        pollute the global state.

        If we have process A and process B called `torch.distributed.init_process_group`
        to form a group, and then we want to form another group with process A, B, C,
        D, it is not possible in PyTorch, because process A and process B have already
        formed a group, and process C and process D cannot join that group. This
        function is a workaround for this issue.

        `torch.distributed.init_process_group` is a global call, while this function
        is a stateless call. It will return a `StatelessProcessGroup` object that can be
        used for exchanging metadata. With this function, process A and process B
        can call `StatelessProcessGroup.create` to form a group, and then process A, B,
        C, and D can call `StatelessProcessGroup.create` to form another group.
        """  # noqa
        launch_server = rank == 0
        if launch_server:
            # listen on the specified interface (instead of 0.0.0.0)
            listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listen_socket.bind((host, port))
            listen_socket.listen()
            listen_fd = listen_socket.fileno()
        else:
            listen_socket = None
            listen_fd = None
        store = TCPStore(
            host_name=host,
            port=port,
            world_size=world_size,
            is_master=launch_server,
            timeout=timedelta(seconds=store_timeout),
            use_libuv=False,  # for now: github.com/pytorch/pytorch/pull/150215
            master_listen_fd=listen_fd,
        )

        return InjectedStatelessProcessGroup(
            rank=rank,
            world_size=world_size,
            store=store,
            socket=listen_socket,
            data_expiration_seconds=data_expiration_seconds)

    def barrier(self, timeout: float = 30.0):
        """A robust barrier to synchronize all ranks."""

        try:
            # 阶段1: 广播barrier_id
            if self.rank == 0:
                barrier_id = f"barrier_{uuid.uuid4()}"
                self.broadcast_obj(barrier_id, src=0)
            else:
                barrier_id = self.broadcast_obj(None, src=0)


            # 阶段2: 到达信号处理
            arrival_key = f"arrival_{barrier_id}_{self.rank}"

            self.store.set(arrival_key, b"1")

            start_time = time.time()
            processes_arrived = set()
            poll_count = 0  # 新增轮询计数器

            while len(processes_arrived) < self.world_size:
                cur_time = time.time()
                if cur_time - start_time > timeout:
                    print(f'[ERROR] Phase1 timeout! Current arrived: {processes_arrived}')  # 新增错误日志
                    raise RuntimeError(f"Barrier timed out after {timeout} seconds")

                new_processes = False  # 新增标志位检测本轮是否有新进程加入
                for i in range(self.world_size):
                    if i in processes_arrived:
                        continue

                    key = f"arrival_{barrier_id}_{i}"
                    try:
                        self.store.get(key)
                        processes_arrived.add(i)
                        new_processes = True
                    except KeyError:
                        pass
                    except Exception as check_e:
                        sched_yield()


                if len(processes_arrived) < self.world_size:
                    poll_count += 1
                    sched_yield()


            # 阶段3: 离开信号处理
            departure_key = f"departure_{barrier_id}_{self.rank}"
            self.store.set(departure_key, b"1")
            if self.rank != 0:
                return

            # 阶段4: Rank0等待所有离开信号
            start_time = time.time()
            processes_departed = set()
            poll_count = 0

            while len(processes_departed) < self.world_size:
                if time.time() - start_time > timeout:
                    print(f'[ERROR] Phase2 timeout! Departed: {processes_departed}')  # 新增错误日志
                    raise RuntimeError(f"Barrier departure timed out after {timeout} s")

                new_departures = False
                for i in range(self.world_size):
                    if i in processes_departed:
                        continue

                    key = f"departure_{barrier_id}_{i}"
                    try:
                        self.store.get(key)
                        processes_departed.add(i)
                        new_departures = True
                    except KeyError:
                        pass
                    except Exception as check_e:

                        sched_yield()


                if len(processes_departed) < self.world_size:
                    poll_count += 1
                    sched_yield()

            # 阶段5: 清理存储
            for i in range(self.world_size):
                try:
                    self.store.delete_key(f"arrival_{barrier_id}_{i}")
                except Exception as e:
                    ...
                try:
                    self.store.delete_key(f"departure_{barrier_id}_{i}")
                except Exception as e:
                    ...

        except Exception as e:
            print(f'[FATAL] Exception in barrier: {str(e)}', exc_info=True)  # 新增全局异常捕获
            raise
