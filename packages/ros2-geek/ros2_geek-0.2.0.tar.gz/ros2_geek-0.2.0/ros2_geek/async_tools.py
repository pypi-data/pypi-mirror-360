import math


class AsyncSleeper:
    def __init__(self, frequency):
        self._added = []
        self.reset_frequency(frequency)

    def add(self, time, handle_name, function, *args, **kwargs):
        """
        time: second
        """
        assert (
            isinstance(handle_name, str) or handle_name is None
        ), "handle_name must be a string or None"
        self._added.append((time, handle_name, function, args, kwargs))
        # 4 drop 5 accept
        cnt = int(time * self._frequency + 0.5)
        self._lcm_cnt = self.lcm(self._lcm_cnt, max(cnt, 0))
        function = function if function else lambda *args, **kwargs: None
        self._sleepers.append((self._cum_cnt + cnt, function, args, kwargs))
        self._names.append(handle_name)
        self._cum_cnt += cnt

    def remove(self, handle_names):
        if isinstance(handle_names, str) or handle_names is None:
            handle_names = [handle_names]
        for name in handle_names:
            while name in self._names:
                index = self._names.index(name)
                self._names.pop(index)
                self._sleepers.pop(index)

    def reset_time(self):
        self._cnt = 0

    def reset_frequency(self, frequency):
        self._frequency = frequency
        added = self._added
        self.clear()
        for time, handle_name, function, args, kwargs in added:
            self.add(time, handle_name, function, *args, **kwargs)

    def update(self):
        self._cnt += 1
        for time, function, args, kwargs in self._sleepers.copy():
            if self._cnt == time:
                function(*args, **kwargs)
        if self._cnt == self._cum_cnt:
            self.reset_time()

    def clear(self):
        self._added = []
        self._sleepers = []
        self._names = []
        self._cum_cnt = 1
        self._cnt = 0
        self._lcm_cnt = 1

    @staticmethod
    def lcm(a, b):
        return abs(a * b) // math.gcd(a, b)

    @classmethod
    def lcm_multiple(cls, *numbers):
        lcm_result = numbers[0]
        for num in numbers[1:]:
            lcm_result = cls.lcm(lcm_result, num)
        return lcm_result


class AsyncTimer(AsyncSleeper):

    def add(self, time, handle_name, function, *args, **kwargs):
        self._cum_cnt = 0
        ret = super().add(time, handle_name, function, *args, **kwargs)
        return ret

    def update(self):
        # print("update")
        self._cnt += 1
        for cnt, function, args, kwargs in self._sleepers.copy():
            if self._cnt % cnt == 0:
                # print(
                #     f"update: tar_cnt={cnt} cur_cnt={self._cnt} lcm_cnt={self._lcm_cnt} stamp={time.time()}"
                # )
                function(*args, **kwargs)
        # print()
        if self._cnt == self._lcm_cnt:
            self.reset_time()

