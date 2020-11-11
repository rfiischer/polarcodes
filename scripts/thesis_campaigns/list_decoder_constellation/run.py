"""


Created on 10/03/2020 20:58

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

from tcc.main import main

if __name__ == "__main__":

    main("parameters/batch_0.ini", {'POLAR': {'list_size': 8,
                                              'construction_method': '"dega"',
                                              'decoding_algorithm': '"sscl-spc-crc"',
                                              'crc_id': '"crc-16"'},
                                    'GENERAL': {'log_file': '"log/{}_log.log"'.format('l_dega_8'),
                                                'results_dir': '"results/{}/"'.format('l_dega_8')},
                                    'RUN': {'num_workers': 16,
                                            'frame_pack_size': 16}})

    main("parameters/batch_0.ini", {'POLAR': {'list_size': 8,
                                              'construction_method': '"mdega"',
                                              'decoding_algorithm': '"sscl-spc-crc"',
                                              'crc_id': '"crc-16"'},
                                    'GENERAL': {'log_file': '"log/{}_log.log"'.format('l_mdega_8'),
                                                'results_dir': '"results/{}/"'.format('l_mdega_8')},
                                    'RUN': {'num_workers': 16,
                                            'frame_pack_size': 16}})

    main("parameters/batch_0.ini", {'POLAR': {'construction_method': '"dega"',
                                              'decoding_algorithm': '"fast-ssc"'},
                                    'GENERAL': {'log_file': '"log/{}_log.log"'.format('f_dega'),
                                                'results_dir': '"results/{}/"'.format('f_dega')},
                                    'RUN': {'num_workers': 16,
                                            'frame_pack_size': 16}})

    main("parameters/batch_0.ini", {'POLAR': {'construction_method': '"mdega"',
                                              'decoding_algorithm': '"fast-ssc"'},
                                    'GENERAL': {'log_file': '"log/{}_log.log"'.format('f_mdega'),
                                                'results_dir': '"results/{}/"'.format('f_mdega')},
                                    'RUN': {'num_workers': 16,
                                            'frame_pack_size': 16}})
