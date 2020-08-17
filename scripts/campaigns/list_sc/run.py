"""


Created on 10/03/2020 20:58

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

from tcc.main import main

if __name__ == "__main__":
    list_sizes = [1, 2, 4, 8, 16, 32]
    for list_size in list_sizes:
        main("parameters/batch_0.ini", {'POLAR': {'construction_method': '"{}"'.format('tahir'),
                                                  'list_size': list_size,
                                                  'encoding_mode': '"systematic"'},
                                        'GENERAL': {'log_file': '"log/{}_log.log"'.format('s_l' +
                                                                                          str(list_size)),
                                                    'results_dir': '"results/{}/"'.format('s_l' +
                                                                                          str(list_size))},
                                        'RUN': {'num_workers': 16,
                                                'frame_pack_size': 16}})

        main("parameters/batch_0.ini", {'POLAR': {'construction_method': '"{}"'.format('tahir'),
                                                  'list_size': list_size,
                                                  'encoding_mode': '"non-systematic"'},
                                        'GENERAL': {'log_file': '"log/{}_log.log"'.format('n_l' +
                                                                                          str(list_size)),
                                                    'results_dir': '"results/{}/"'.format('n_l' +
                                                                                          str(list_size))},
                                        'RUN': {'num_workers': 16,
                                                'frame_pack_size': 16}})
