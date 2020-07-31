"""
Campaing to simulate different decoding schemes using the same construction

Created on 10/03/2020 20:58

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

from tcc.main import main

decoders = ['sscl-spc', 'ssc', 'fast-ssc']

if __name__ == '__main__':
    for decoder in decoders:
        main("parameters/batch_0.ini",
             {'POLAR': {'construction_method': '"{}"'.format('bhattacharyya'),
                        'decoding_algorithm': '"{}"'.format(decoder)},
              'GENERAL': {'log_file': '"log/{}_log.log"'.format(decoder),
                          'results_dir': '"results/{}/"'.format(decoder)}})
