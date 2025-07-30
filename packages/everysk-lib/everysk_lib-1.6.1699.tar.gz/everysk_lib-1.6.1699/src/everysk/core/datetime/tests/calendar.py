###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.core.datetime.calendar import get_holidays
from everysk.core.datetime.date import Date
from everysk.core.unittests import TestCase


class CalendarTestCase(TestCase):

    def test_get_holidays_BVMF(self):
        ret = get_holidays('BVMF', years=[2020, 2021, 2022, 2023])
        self.assertIsInstance(ret, dict)
        self.assertIsInstance(list(ret.keys())[0], Date)
        self.assertDictEqual(ret, {
            Date(2020, 1, 1): 'Confraternização Universal',
            Date(2020, 4, 10): 'Sexta-feira Santa',
            Date(2020, 4, 21): 'Tiradentes',
            Date(2020, 5, 1): 'Dia do Trabalhador',
            Date(2020, 9, 7): 'Independência do Brasil',
            Date(2020, 10, 12): 'Nossa Senhora Aparecida',
            Date(2020, 11, 2): 'Finados',
            Date(2020, 11, 15): 'Proclamação da República',
            Date(2020, 12, 25): 'Natal',
            Date(2020, 2, 24): 'Carnaval',
            Date(2020, 2, 25): 'Carnaval',
            Date(2020, 6, 11): 'Corpus Christi',
            Date(2020, 1, 25): 'Aniversário de São Paulo',
            Date(2020, 11, 20): 'Dia da Consciência Negra',
            Date(2021, 1, 1): 'Confraternização Universal',
            Date(2021, 4, 2): 'Sexta-feira Santa',
            Date(2021, 4, 21): 'Tiradentes',
            Date(2021, 5, 1): 'Dia do Trabalhador',
            Date(2021, 9, 7): 'Independência do Brasil',
            Date(2021, 10, 12): 'Nossa Senhora Aparecida',
            Date(2021, 11, 2): 'Finados',
            Date(2021, 11, 15): 'Proclamação da República',
            Date(2021, 12, 25): 'Natal',
            Date(2021, 2, 15): 'Carnaval',
            Date(2021, 2, 16): 'Carnaval',
            Date(2021, 6, 3): 'Corpus Christi',
            Date(2021, 1, 25): 'Aniversário de São Paulo',
            Date(2021, 11, 20): 'Dia da Consciência Negra',
            Date(2022, 1, 1): 'Confraternização Universal',
            Date(2022, 4, 15): 'Sexta-feira Santa',
            Date(2022, 4, 21): 'Tiradentes',
            Date(2022, 5, 1): 'Dia do Trabalhador',
            Date(2022, 9, 7): 'Independência do Brasil',
            Date(2022, 10, 12): 'Nossa Senhora Aparecida',
            Date(2022, 11, 2): 'Finados',
            Date(2022, 11, 15): 'Proclamação da República',
            Date(2022, 12, 25): 'Natal',
            Date(2022, 2, 28): 'Carnaval',
            Date(2022, 3, 1): 'Carnaval',
            Date(2022, 6, 16): 'Corpus Christi',
            Date(2023, 1, 1): 'Confraternização Universal',
            Date(2023, 4, 7): 'Sexta-feira Santa',
            Date(2023, 4, 21): 'Tiradentes',
            Date(2023, 5, 1): 'Dia do Trabalhador',
            Date(2023, 9, 7): 'Independência do Brasil',
            Date(2023, 10, 12): 'Nossa Senhora Aparecida',
            Date(2023, 11, 2): 'Finados',
            Date(2023, 11, 15): 'Proclamação da República',
            Date(2023, 12, 25): 'Natal',
            Date(2023, 2, 20): 'Carnaval',
            Date(2023, 2, 21): 'Carnaval',
            Date(2023, 6, 8): 'Corpus Christi'
        })

    def test_get_holidays_ANBIMA(self):
        ret = get_holidays('ANBIMA', years=[2020, 2021, 2022, 2023])
        self.assertIsInstance(ret, dict)
        self.assertIsInstance(list(ret.keys())[0], Date)
        self.assertDictEqual(dict(ret), {
            Date(2020, 1, 1): 'Confraternização Universal',
            Date(2020, 4, 10): 'Sexta-feira Santa',
            Date(2020, 4, 21): 'Tiradentes',
            Date(2020, 5, 1): 'Dia do Trabalhador',
            Date(2020, 9, 7): 'Independência do Brasil',
            Date(2020, 10, 12): 'Nossa Senhora Aparecida',
            Date(2020, 11, 2): 'Finados',
            Date(2020, 11, 15): 'Proclamação da República',
            Date(2020, 12, 25): 'Natal',
            Date(2020, 2, 24): 'Carnaval',
            Date(2020, 2, 25): 'Carnaval',
            Date(2020, 6, 11): 'Corpus Christi',
            Date(2021, 1, 1): 'Confraternização Universal',
            Date(2021, 4, 2): 'Sexta-feira Santa',
            Date(2021, 4, 21): 'Tiradentes',
            Date(2021, 5, 1): 'Dia do Trabalhador',
            Date(2021, 9, 7): 'Independência do Brasil',
            Date(2021, 10, 12): 'Nossa Senhora Aparecida',
            Date(2021, 11, 2): 'Finados',
            Date(2021, 11, 15): 'Proclamação da República',
            Date(2021, 12, 25): 'Natal',
            Date(2021, 2, 15): 'Carnaval',
            Date(2021, 2, 16): 'Carnaval',
            Date(2021, 6, 3): 'Corpus Christi',
            Date(2022, 1, 1): 'Confraternização Universal',
            Date(2022, 4, 15): 'Sexta-feira Santa',
            Date(2022, 4, 21): 'Tiradentes',
            Date(2022, 5, 1): 'Dia do Trabalhador',
            Date(2022, 9, 7): 'Independência do Brasil',
            Date(2022, 10, 12): 'Nossa Senhora Aparecida',
            Date(2022, 11, 2): 'Finados',
            Date(2022, 11, 15): 'Proclamação da República',
            Date(2022, 12, 25): 'Natal',
            Date(2022, 2, 28): 'Carnaval',
            Date(2022, 3, 1): 'Carnaval',
            Date(2022, 6, 16): 'Corpus Christi',
            Date(2023, 1, 1): 'Confraternização Universal',
            Date(2023, 4, 7): 'Sexta-feira Santa',
            Date(2023, 4, 21): 'Tiradentes',
            Date(2023, 5, 1): 'Dia do Trabalhador',
            Date(2023, 9, 7): 'Independência do Brasil',
            Date(2023, 10, 12): 'Nossa Senhora Aparecida',
            Date(2023, 11, 2): 'Finados',
            Date(2023, 11, 15): 'Proclamação da República',
            Date(2023, 12, 25): 'Natal',
            Date(2023, 2, 20): 'Carnaval',
            Date(2023, 2, 21): 'Carnaval',
            Date(2023, 6, 8): 'Corpus Christi'
        })

    def test_get_holidays_2024_BR(self):
        self.maxDiff = None
        ret = get_holidays('BR', years=[2024])
        self.assertIsInstance(ret, dict)
        self.assertIsInstance(list(ret.keys())[0], Date)
        self.assertDictEqual(dict(ret), {
            Date(2024, 1, 1): 'Confraternização Universal',
            Date(2024, 2, 12): 'Carnaval',
            Date(2024, 2, 13): 'Carnaval',
            Date(2024, 3, 29): 'Sexta-feira Santa',
            Date(2024, 4, 21): 'Tiradentes',
            Date(2024, 5, 1): 'Dia do Trabalhador',
            Date(2024, 5, 30): 'Corpus Christi',
            Date(2024, 9, 7): 'Independência do Brasil',
            Date(2024, 10, 12): 'Nossa Senhora Aparecida',
            Date(2024, 11, 2): 'Finados',
            Date(2024, 11, 15): 'Proclamação da República',
            Date(2024, 11, 20): 'Dia Nacional de Zumbi e da Consciência Negra',
            Date(2024, 12, 25): 'Natal'
        })
