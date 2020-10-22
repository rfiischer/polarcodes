import numpy as np
from abc import abstractmethod, ABC


class SnrConfig(object):
    """Setup class for the SnrManager class"""

    def __init__(self, *args):
        """
        :param args: dict {counter_name: ,counter_specs: {[min_relative_accuracy:
                                                          ,max_counter:
                                                          ,min_counter:
                                                          ,max_stats_gap:
                                                          ,target_stats: ]}}
        """

        self.config = dict()
        for config in args:
            self.config[config['counter_name']] = config['counter_specs']


class SnrManager(ABC):
    def __init__(self, statistics, config_cls):
        self.statistics = statistics
        self.config_cls = config_cls.config

    def snr_stop(self):
        max_stop = self._check_max()
        min_stop = self._check_min()
        min_num_events = self._check_min_events()
        all_event = not self._check_any_empty()

        return max_stop or (all_event and min_num_events and min_stop)

    def _check_any_empty(self):
        at_least_one_empty = False
        for counter_name in self.config_cls:
            if not self.statistics.last_snr['data'][counter_name]['any']:
                at_least_one_empty = True

        return at_least_one_empty

    def _check_all_empty(self):
        all_empty = True
        for counter_name in self.config_cls:
            if self.statistics.last_snr['data'][counter_name]['any']:
                all_empty = False

        return all_empty

    def _check_max(self):
        max_stop = False
        for counter_name in self.config_cls:
            if self.config_cls[counter_name].get('max_counter') is not None:
                if self.statistics.last_snr['data'][counter_name]['sum_total'] >= \
                        self.config_cls[counter_name]['max_counter']:
                    max_stop = True

        return max_stop

    def _check_min(self):
        min_stop = True
        for counter_name in self.config_cls:
            if self.config_cls[counter_name].get('min_counter') is not None:
                if self.statistics.last_snr['data'][counter_name]['sum_total'] < \
                        self.config_cls[counter_name]['min_counter']:
                    min_stop = False

        return min_stop

    def _check_min_events(self):
        min_event_stop = True
        for counter_name in self.config_cls:
            if self.config_cls[counter_name].get('min_event_counter') is not None:
                if self.statistics.last_snr['data'][counter_name]['sum_counter'] < \
                        self.config_cls[counter_name]['min_event_counter']:
                    min_event_stop = False

        return min_event_stop

    @abstractmethod
    def sim_stop(self):
        pass

    @abstractmethod
    def __iter__(self):
        pass


class SnrRangeManager(SnrManager):
    """
    Class that controlls the SNR sweep in range mode
    """

    def __init__(self, statistics, config_cls, **kwargs):
        super().__init__(statistics, config_cls)

        try:
            self.min_snr_db = kwargs['min_snr_db']
            self.max_snr_db = kwargs['max_snr_db']
            self.snr_db_step = kwargs['snr_db_step']

        except KeyError:
            raise ValueError("For range type 'range', 'min_snr_db', 'max_snr_db', 'snr_db_step' should be set")

        self.iter = self.Range(self.min_snr_db, self.max_snr_db, self.snr_db_step)

    def sim_stop(self):
        self.iter.stop = self._check_all_empty()

    def __iter__(self):
        return self.iter.__iter__()

    class Range(object):
        """Implements the range iteration"""

        def __init__(self, min_db, max_db, step_db):
            self.min_db = min_db
            self.max_db = max_db
            self.step_db = step_db

        def __iter__(self):
            self.stop = False
            self.range = np.arange(self.min_db, self.max_db + self.step_db, step=self.step_db)
            self.snrrange = self.range.__iter__()
            self.snr_id = np.arange(0, len(self.range)).__iter__()
            self.snr_list = []
            return self

        def __next__(self):
            if not self.stop:
                next_snr = next(self.snrrange)
                next_id = next(self.snr_id)
                self.snr_list.append(next_snr)

            else:
                raise StopIteration

            return next_snr, next_id


class SnrDynamicManager(SnrManager):
    def __init__(self, statistics, config_cls, **kwargs):
        super().__init__(statistics, config_cls)

        try:
            self.start_db = kwargs['start_snr_db']
            self.min_step_db = kwargs['min_snr_step_db']
            self.start_level = kwargs['start_level']

        except KeyError:
            raise ValueError("For range type 'dynamic', 'start_snr_db', 'min_snr_step_db' and "
                             "'start_level' should be set")

        self.iter = self.Dynamic(self.start_db, self.min_step_db, self.start_level)

    def sim_stop(self):
        self.iter.any = not self._check_all_empty()
        self.iter.min_stats = self._check_min_stats()
        self.iter.max_stats = self._check_max_stats()
        self.iter.lm = self.iter.level_min()

        self.iter.state_transition()

        self.iter.store_snr(self.iter.any)

    def _check_min_stats(self):
        min_stats = True
        for counter_name in self.config_cls:
            if self.statistics.last_snr['data'][counter_name]['rate'] < \
                    self.config_cls[counter_name]['target_stats'][0]:
                min_stats = False

        return min_stats

    def _check_max_stats(self):
        max_stats = True
        for counter_name in self.config_cls:
            if self.statistics.last_snr['data'][counter_name]['rate'] > \
                    self.config_cls[counter_name]['target_stats'][1]:
                max_stats = False

        return max_stats

    def __iter__(self):
        return self.iter.__iter__()

    class Dynamic:
        """Implements the dynamic SNR search"""

        def __init__(self, start_db, min_step_db, start_level):
            self.start_db = start_db
            self.step_db = min_step_db
            self.start_level = start_level

            # Iter variables
            self.state = None
            self.curr_snr = None
            self.sb_snr = None
            self.counter = None
            self.sb_counter = None
            self.last_counter = None
            self.any = None
            self.min_stats = None
            self.max_stats = None

            # Memory
            self.memory = []

        def __iter__(self):
            # Init state
            self.state = "start"
            self.curr_snr = self.start_db
            self.sb_snr = None
            self.counter = 0
            self.sb_counter = None
            self.last_counter = None
            self.end_counter = None
            self._resetstep()

            # Iter variables
            self.any = None
            self.min_stats = None
            self.max_stats = None
            self.lm = None

            # Memory
            self.memory = []

            return self

        def __next__(self):
            if self.state == "start":
                pass

            elif self.state == "exponentialback":
                self._fallback()
                self._levelup()
                self._updatestep()

            elif self.state == "searchback":
                self._fallback()

            elif self.state == "searchforward":
                self._goforward()

            elif self.state == "goforward":
                self._goforward()

            elif self.state == "stop":
                raise StopIteration

            self.last_counter = self.counter
            return self.curr_snr, self.counter

        def state_transition(self):
            if self.state == "start":
                if self.any and self.min_stats and self.max_stats:
                    self.state = "stop"

                elif self.any and self.min_stats and (not self.max_stats):
                    self.state = "searchforward"

                elif self.any and (not self.min_stats):
                    self.state = "searchback"
                    self._searchback_store()

                else:
                    self.state = "exponentialback"

            elif self.state == "exponentialback":
                if self.any:
                    self._resetstep()
                    if not self.min_stats:
                        self.state = "searchback"
                        self._searchback_store()

                    elif self.min_stats and (not self.max_stats):
                        self.state = "searchforward"

                    else:
                        self.state = "stop"

            elif self.state == "searchback":
                if self.min_stats and (not self.max_stats):
                    self.state = "searchforward"
                    self._searchback_restore()

                elif self.min_stats and self.max_stats:
                    self.state = "stop"

            elif self.state == "searchforward":
                if self.any and self.max_stats:
                    self.state = "stop"

                elif not self.any:
                    self._store_end()
                    self._leveldown()
                    self._updatestep()
                    self._curr_last_any()
                    self.state = "goforward"

            elif self.state == "goforward":
                if (self.any and self.max_stats) or ((not self.any) and self.lm):
                    self.state = "stop"

                elif self.any and not self.max_stats:
                    self._leveldown()
                    self._updatestep()
                    if self._next_is_end():
                        self.state = "stop"

                elif (not self.any) and (not self.lm):
                    self._store_end()
                    self._leveldown()
                    self._updatestep()
                    self._curr_last_any()

        def store_snr(self, any_event):
            """

            :param any_event: boolean
            :return:
            """

            if self.state in ['searchback', 'searchforward', 'stop', 'goforward']:
                self.memory.append([self.last_counter, any_event])

        def _fallback(self):
            self.curr_snr -= self.snr_step
            self.counter -= 2 ** self.level

        def _goforward(self):
            self.curr_snr += self.snr_step
            self.counter += 2 ** self.level

        def _levelup(self):
            self.level += 1

        def _leveldown(self):
            if self.level > 0:
                self.level -= 1

        def _updatestep(self):
            self.snr_step = self.step_db * 2 ** self.level

        def _resetstep(self):
            self.snr_step = self.step_db * 2 ** self.start_level
            self.level = self.start_level

        def _searchback_store(self):
            self.sb_snr = self.curr_snr
            self.sb_counter = self.counter

        def _searchback_restore(self):
            self.curr_snr = self.sb_snr
            self.counter = self.sb_counter

        def _curr_last_any(self):
            sort0 = [item for item in sorted(self.memory, key=lambda item: item[0])]
            sort1 = [item for item in sorted(sort0, key=lambda item: 1 if item[1] else 0)]
            last_counter_any = sort1[-1][0]

            self.curr_snr = self.start_db + last_counter_any * self.step_db
            self.counter = last_counter_any

        def _store_end(self):
            self.end_counter = self.counter

        def level_min(self):
            if self.level == 0:
                res = True

            else:
                res = False

            return res

        def _next_is_end(self):
            if self.counter + 2 ** self.level == self.end_counter:
                res = True

            else:
                res = False

            return res


def snr_manager_builder(rantype, statistics, config_cls, **kwargs):
    if rantype == 'range':
        obj = SnrRangeManager(statistics, config_cls, **kwargs)

    elif rantype == 'dynamic':
        obj = SnrDynamicManager(statistics, config_cls, **kwargs)

    else:
        raise ValueError("The range type 'rantype' should be defined as 'range' or 'dynamic'")

    return obj
