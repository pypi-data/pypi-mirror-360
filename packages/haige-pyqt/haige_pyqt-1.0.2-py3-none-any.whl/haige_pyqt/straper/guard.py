from PyQt5.QtCore import QSharedMemory, QSystemSemaphore


class SingleApplicationGuard:
    def __init__(self, key, data_buffer_size=1024):
        self.key = key
        self.shared_memory = QSharedMemory(self.key)
        self.semaphore = QSystemSemaphore(self.key + "_sem", 1)
        self.buffer_size = data_buffer_size

    def is_used(self):
        # 使用信号量确保线程安全
        self.semaphore.acquire()

        # 尝试附加到共享内存
        is_attached = self.shared_memory.attach()
        if is_attached:
            self.shared_memory.detach()

        # 尝试创建共享内存
        is_created = self.shared_memory.create(self.buffer_size)

        self.semaphore.release()

        # 如果无法创建且不是因为已经存在，则可能是其他错误
        if not is_created and self.shared_memory.error() == QSharedMemory.AlreadyExists:
            return True

        return not is_created

    def set_data(self, data: bytes):
        msg_length = len(data)
        if msg_length > self.buffer_size:
            raise Exception("Message Data Length [{0}] Over Buffer Size [{1}]".format(msg_length, self.buffer_size))
        is_lock = False
        try:
            is_lock = self.shared_memory.lock()
            if is_lock:
                dt_ptr = self.shared_memory.data()
                dt_ptr[:msg_length] = data
                return True
            return False
        except Exception as ex:
            raise ex
        finally:
            if is_lock:
                self.shared_memory.unlock()

    def get_data(self) -> bytes:
        is_attached = False
        try:
            is_attached = self.shared_memory.attach()
            if is_attached:
                dt_ptr = self.shared_memory.data()
                return bytes(dt_ptr).split(b'\x00')[0]
        except Exception as ex:
            raise ex
        finally:
            if is_attached:
                self.shared_memory.detach()

