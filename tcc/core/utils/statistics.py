import numpy as np
import datetime
import os
import logging
from scipy.stats import bayes_mvs
from queue import Empty


class Statistics:
    def __init__(self, parameters):
        """
        Statistics object initialization
        :param parameters: ParameterHandler class
        """

        self.logger = logging.getLogger(__name__)
        self.results_dir = parameters.results_dir
        self.extension = parameters.results_file_extension
        self.results_file_path = ""
        self.overwrite_output = parameters.overwrite_output
        self.bit_stats_header = '{} \t Length \t Conf. \t Errors'.format(parameters.snr_unit)
        self.rate_stats_header = '{} \t Error rate'.format(parameters.snr_unit)

        self.samples = []
        self.write = dict()

        self._create_folder()

        self.key_list = []

        self.last_snr = None

    def add_categories(self, cat_list):
        """
        :param cat_list: List of tuples containing the categories names (name, write_on_file)
        :return: None
        """
        for cat_tuple in cat_list:
            self.key_list.append(cat_tuple[0])
            self.write[cat_tuple[0]] = cat_tuple[1]

    def add_snr(self, value):
        """
        :param value: SNR value
        :return: None
        """

        self.last_snr = dict()
        self.last_snr['val'] = value
        self.last_snr['data'] = dict()
        for cat in self.key_list:
            self.last_snr['data'][cat] = {'counter': [], 'total': [], 'stats': {'mean': -1, 'conf': -1},
                                          'any': False}

    def update_stats(self, *args):
        """
        Update the statistics per drop for the last inserted SNR value
        After adding an SNR, you can't update previous SNR's
        :param args: Each parameter should be a tuple (category, num_events, num_total)
        :return: None
        """
        for event_tuple in args:
            current_snr = self.last_snr['data'][event_tuple[0]]
            current_snr['counter'].append(event_tuple[1])
            current_snr['total'].append(event_tuple[2])

    def gen_stats(self):
        for key in self.key_list:
            current_snr = self.last_snr['data'][key]
            current_snr['length'] = len(current_snr['total'])
            if current_snr['length'] > 2:
                if not any(np.array(current_snr['counter']) - current_snr['counter'][0]):
                    current_snr['stats']['mean'] = current_snr['counter'][0]
                    current_snr['stats']['conf'] = 0

                else:
                    stats = bayes_mvs(current_snr['counter'])
                    current_snr['stats']['mean'] = stats[0][0]
                    current_snr['stats']['conf'] = (stats[0][1][1] - stats[0][1][0]) / stats[0][0]

            if any(current_snr['counter']):
                current_snr['any'] = True

    def update_from_queue(self, queue):
        while True:
            try:
                args = queue.get(block=False)
                self.update_stats(*args)
                queue.task_done()

            except Empty:
                break

    def write_to_file(self):
        """
        Writes the statistics to file
        :return: None
        """

        for stats_name in self.key_list:
            if self.write[stats_name]:
                stats_file_name = os.path.join(self.results_file_path, stats_name + '_data' + self.extension)
                with open(stats_file_name, "wb") as file:
                    file.write(("# " + self.bit_stats_header).encode('ascii'))
                    file.write(b'\n')
                    for snr in self.samples:
                        np.savetxt(file, np.array([snr['val']]).reshape((1, -1)),
                                   fmt='%.4f', delimiter='', newline='\t')
                        np.savetxt(file, np.array([snr['data'][stats_name]['length']]).reshape((1, -1)),
                                   fmt='%d', delimiter='', newline='\t')
                        np.savetxt(file, np.array([snr['data'][stats_name]['stats']['conf']]).reshape((1, -1)),
                                   fmt='%.3e', delimiter='', newline='\t')
                        np.savetxt(file, np.array(snr['data'][stats_name]['counter']).reshape((1, -1)),
                                   fmt='%d', delimiter='\t')

        for stats_name in self.key_list:
            rate_file_name = os.path.join(self.results_file_path, stats_name + self.extension)
            with open(rate_file_name, "wb") as file:
                file.write(("# " + self.rate_stats_header).encode('ascii'))
                file.write(b'\n')
                for snr in self.samples:
                    np.savetxt(file, np.array([snr['val']]).reshape((1, -1)),
                               fmt='%.4f', delimiter='', newline='\t')
                    np.savetxt(file, np.array(snr['data'][stats_name]['rate']).reshape((1, -1)),
                               fmt='%.6e', delimiter='\t')

    def gen_rate(self):
        for cat in self.key_list:
            snr_data = self.last_snr['data'][cat]
            sum_total = np.sum(snr_data['total'])
            if sum_total:
                snr_data['rate'] = np.sum(snr_data['counter']) / sum_total

            else:
                snr_data['rate'] = -1

        self.samples.append(self.last_snr)
        self._sort_snr()
        self.write_to_file()

    def _sort_snr(self):
        self.samples = [snr_data for snr_data in sorted(self.samples, key=lambda item: item['val'])]

    def _create_folder(self):
        # Create results folder
        new_sub_dir_name = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-results")
        if not self.overwrite_output:
            self.results_file_path = os.path.join(os.path.dirname(self.results_dir), new_sub_dir_name)
        else:
            self.results_file_path = os.path.dirname(self.results_dir)

        if not os.path.exists(self.results_file_path):
            os.makedirs(self.results_file_path)
