import unittest
from mensajes.hola import Saludar


class PruebasHola(unittest.TestCase):

    def test_saludar(self):
        self.assertEqual(Saludar.prueba(), "Esto es una prueba desde la nueva version")