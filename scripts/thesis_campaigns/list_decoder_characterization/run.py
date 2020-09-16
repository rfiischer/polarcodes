"""


Created on 10/03/2020 20:58

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

from tcc.main import main

if __name__ == "__main__":
    main("parameters/batch_0.ini", {'POLAR': {'construction_method': '"{}"'.format('tahir'),
                                              'encoding_mode': '"non-systematic"',
                                              'decoding_algorithm': '"ssc"'},
                                    'GENERAL': {'log_file': '"log/{}_log.log"'.format('curve_1'),
                                                'results_dir': '"results/{}/"'.format('curve_1')},
                                    'RUN': {'num_workers': 16,
                                            'frame_pack_size': 16}})

    main("parameters/batch_0.ini", {'POLAR': {'construction_method': '"{}"'.format('tahir'),
                                              'encoding_mode': '"non-systematic"',
                                              'decoding_algorithm': '"sscl-spc"',
                                              'list_size': 32},
                                    'GENERAL': {'log_file': '"log/{}_log.log"'.format('curve_2'),
                                                'results_dir': '"results/{}/"'.format('curve_2')},
                                    'RUN': {'num_workers': 16,
                                            'frame_pack_size': 16}})

    main("parameters/batch_0.ini", {'POLAR': {'construction_method': '"{}"'.format('tahir'),
                                              'encoding_mode': '"non-systematic"',
                                              'decoding_algorithm': '"sscl-spc-crc"',
                                              'list_size': 32,
                                              'crc_id': '"crc-16"'},
                                    'GENERAL': {'log_file': '"log/{}_log.log"'.format('curve_3'),
                                                'results_dir': '"results/{}/"'.format('curve_3')},
                                    'RUN': {'num_workers': 16,
                                            'frame_pack_size': 16}})

    main("parameters/batch_0.ini", {'POLAR': {'construction_method': '"{}"'.format('tahir'),
                                              'encoding_mode': '"systematic"',
                                              'decoding_algorithm': '"sscl-spc-crc"',
                                              'list_size': 32,
                                              'crc_id': '"crc-16"'},
                                    'GENERAL': {'log_file': '"log/{}_log.log"'.format('curve_4'),
                                                'results_dir': '"results/{}/"'.format('curve_4')},
                                    'RUN': {'num_workers': 16,
                                            'frame_pack_size': 16}})
