import os
import sys
import unittest

# Корень проекта и каталог src/ в путях поиска модулей — чтобы тесты
# запускались любым способом: python tests\test_delivery.py,
# python -m unittest discover, python run_tests.py или из PyCharm.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "..", "src"))
sys.path.insert(0, os.path.join(BASE_DIR, ".."))

try:
    from src.delivery import calculate_delivery_cost
except ImportError:  # запасной вариант, если каталог src не пакет (нет __init__.py)
    from delivery import calculate_delivery_cost

# ---------------------------------------------------------------------------
# Восстановленные бизнес-требования (по контексту исходного кода):
#   1. Валидные входные данные: вес 0.1–50 кг включительно, дистанция 1–5000 км,
#      тип посылки — "обычный", "хрупкий" или "опасный".
#   2. Ошибочные параметры -> (-1, "0000-00-00"), без исключений.
#   3. Базовый тариф: 200 руб. + 5 руб. за каждый километр.
#   4. Весовой коэффициент: до 5 кг включительно — без надбавки,
#      5–20 кг — x1.2, 20 кг и более — x1.5.
#   5. Надбавка за тип: хрупкий +300 руб., опасный +1000 руб. (фиксированная).
#   6. Экспресс-доставка — премиум-услуга: ускоряет доставку и ДОРОЖЕ
#      обычной (x1.5), дешеветь она не может.
#   7. Срок доставки: каждые полные 500 км пути — 1 день, но не менее 1 дня.
#      Экспресс в 2 раза быстрее, однако доставить посылку в день отправки
#      (0 дней) невозможно.
#   8. Отправка — фиксированная дата 2026-09-03, результат в формате
#      YYYY-MM-DD.
# ---------------------------------------------------------------------------

ERROR_RESULT = (-1, "0000-00-00")
SHIP_DATE = "2026-09-03"


class TestDeliveryValidation(unittest.TestCase):
    """Проверки валидации входных параметров расчёта доставки."""

    def test_weight_below_100g_returns_error(self):
        """Вес меньше 0.1 кг -> код ошибки (-1, '0000-00-00')."""
        self.assertEqual(
            calculate_delivery_cost(0.05, 100, "обычный"), ERROR_RESULT
        )

    def test_weight_over_50kg_returns_error(self):
        """Вес больше 50 кг -> код ошибки (-1, '0000-00-00')."""
        self.assertEqual(
            calculate_delivery_cost(50.5, 100, "обычный"), ERROR_RESULT
        )

    def test_negative_weight_returns_error(self):
        """Отрицательный вес -> код ошибки (-1, '0000-00-00')."""
        self.assertEqual(
            calculate_delivery_cost(-3.0, 100, "обычный"), ERROR_RESULT
        )

    def test_minimum_valid_weight_100g_passes(self):
        """Граница веса 0.1 кг включительно -> расчёт успешен."""
        self.assertNotEqual(
            calculate_delivery_cost(0.1, 1, "обычный"), ERROR_RESULT
        )

    def test_zero_distance_returns_error(self):
        """Дистанция 0 км -> код ошибки (-1, '0000-00-00')."""
        self.assertEqual(
            calculate_delivery_cost(1.0, 0, "обычный"), ERROR_RESULT
        )

    def test_distance_over_5000km_returns_error(self):
        """Дистанция больше 5000 км -> код ошибки (-1, '0000-00-00')."""
        self.assertEqual(
            calculate_delivery_cost(1.0, 5001, "обычный"), ERROR_RESULT
        )

    def test_maximum_distance_5000km_is_still_valid(self):
        """Граница дистанции 5000 км включительно -> расчёт успешен."""
        self.assertEqual(
            calculate_delivery_cost(1.0, 5000, "обычный"),
            (25200, "2026-09-13"),
        )

    def test_unknown_package_type_returns_error(self):
        """Несуществующий тип посылки -> код ошибки (-1, '0000-00-00')."""
        self.assertEqual(
            calculate_delivery_cost(1.0, 100, "неизвестный"), ERROR_RESULT
        )


class TestDeliveryCostCalculation(unittest.TestCase):
    """Проверки тарифной сетки: база, весовые и типовые коэффициенты."""

    def test_base_tariff_for_light_small_parcel(self):
        """Лёгкая посылка на 1 км = 200 руб. база + 5 руб. за км = 205 руб."""
        self.assertEqual(calculate_delivery_cost(1.0, 1, "обычный")[0], 205)

    def test_each_kilometer_adds_five_rubles(self):
        """Каждый километр добавляет 5 руб.: 100 км -> 200 + 500 = 700 руб."""
        self.assertEqual(calculate_delivery_cost(1.0, 100, "обычный")[0], 700)

    def test_parcel_up_to_5kg_has_no_weight_surcharge(self):
        """Вес до 5 кг включительно -> без весового коэффициента (205 руб.)."""
        self.assertEqual(calculate_delivery_cost(5.0, 1, "обычный")[0], 205)

    def test_medium_weight_5_to_20kg_adds_20_percent(self):
        """Вес в диапазоне 5–20 кг -> наценка x1.2: (200+10)*1.2 = 252 руб."""
        self.assertEqual(calculate_delivery_cost(10.0, 2, "обычный")[0], 252)

    def test_weight_boundary_19_9kg_counts_as_medium(self):
        """Граница 19.9 кг ещё относится к среднему весу -> x1.2 = 246 руб."""
        self.assertEqual(calculate_delivery_cost(19.9, 1, "обычный")[0], 246)

    def test_heavy_weight_from_20kg_adds_50_percent(self):
        """Вес от 20 кг -> наценка x1.5: 205*1.5 = 307 руб."""
        self.assertEqual(calculate_delivery_cost(20.0, 1, "обычный")[0], 307)

    def test_fragile_package_adds_300_rubles(self):
        """Хрупкая посылка -> фиксированная надбавка 300 руб.: 205+300 = 505."""
        self.assertEqual(calculate_delivery_cost(1.0, 1, "хрупкий")[0], 505)

    def test_hazardous_package_adds_1000_rubles(self):
        """Опасная посылка -> фиксированная надбавка 1000 руб.: 205+1000=1205."""
        self.assertEqual(calculate_delivery_cost(1.0, 1, "опасный")[0], 1205)


class TestExpressDelivery(unittest.TestCase):
    """Проверки экспресс-доставки: премиум-наценка и ускорение сроков.

    Экспресс-доставка не может быть дешевле обычной — это противоречит
    бизнес-логике: клиент платит за срочность.
    """

    def test_express_delivery_costs_50_percent_more(self):
        """Экспресс x1.5: 205*1.5 = 307 руб., а не в 2 раза дешевле."""
        self.assertEqual(
            calculate_delivery_cost(2.0, 1, "обычный", is_express=True)[0], 307
        )

    def test_express_surcharge_applies_after_weight_and_type(self):
        """Экспресс умножает уже полную стоимость: 700*1.2*1.5 = 1260 руб."""
        self.assertEqual(
            calculate_delivery_cost(10.0, 100, "обычный", is_express=True)[0],
            1260,
        )

    def test_express_fragile_parcel_total(self):
        """Экспресс хрупкой посылки: (205+300)*1.5 = 757 руб."""
        self.assertEqual(
            calculate_delivery_cost(1.0, 1, "хрупкий", is_express=True)[0], 757
        )

    def test_express_short_distance_delivers_next_day(self):
        """Экспресс на короткой дистанции — день доставки, но не день отправки.

        Полный срок 1 день, экспресс в 2 раза быстрее, после деления срок
        не может стать 0 дней -> 2026-09-04 (наблюдаемое)."""
        self.assertEqual(
            calculate_delivery_cost(1.0, 60, "обычный", is_express=True)[1],
            "2026-09-04",
        )

    def test_express_long_distance_3000km_is_three_days(self):
        """Экспресс на 3000 км: 6 дней полной доставки -> 3 -> 2026-09-06."""
        self.assertEqual(
            calculate_delivery_cost(1.0, 3000, "обычный", is_express=True)[1],
            "2026-09-06",
        )


class TestDeliveryDate(unittest.TestCase):
    """Проверки расчёта даты доставки."""

    def test_short_distance_delivers_next_day(self):
        """Дистанция меньше 500 км -> 1 день -> 2026-09-04."""
        self.assertEqual(calculate_delivery_cost(1.0, 1, "обычный")[1], "2026-09-04")

    def test_delivery_date_for_499km_is_next_day(self):
        """499 км — ещё нет полной 500-километровой секции -> 2026-09-04."""
        self.assertEqual(calculate_delivery_cost(1.0, 499, "обычный")[1], "2026-09-04")

    def test_one_extra_day_per_500km(self):
        """1000 км — две 500-километровые секции -> 2026-09-05."""
        self.assertEqual(calculate_delivery_cost(1.0, 1000, "обычный")[1], "2026-09-05")

    def test_delivery_date_for_1500km_is_three_days(self):
        """1500 км — три секции -> 3 дня -> 2026-09-06."""
        self.assertEqual(calculate_delivery_cost(1.0, 1500, "обычный")[1], "2026-09-06")

    def test_delivery_date_format_is_iso(self):
        """Дата доставки возвращается в формате YYYY-MM-DD."""
        result = calculate_delivery_cost(1.0, 100, "обычный")
        self.assertRegex(str(result[1]), r"^\d{4}-\d{2}-\d{2}$")


if __name__ == "__main__":
    unittest.main()
