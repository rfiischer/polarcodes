"""
Verifies the generated matrixes

Created on 12/02/2020 11:58

@author: Rodrigo Fischer (rodrigoarfischer@gmail.com)
"""

from polarcoding import PolarCoding


p4 = PolarCoding(2)
p8 = PolarCoding(3)

print("G_4 = \n")
print(p4.Fn)
print("\nG_8 = \n")
print(p8.Fn)
