"""Спецификации функций подсистемы аварийной диагностики (Вариант Б, N=18)."""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.well_design import config

def validate_telemetry(q_liq: float, w_pct: float, p_res: float, p_bhp: float) -> tuple[bool, str]:
    """Проверяет вхождение всех параметров телеметрии в допустимые физические границы."""
    if not (config.Q_LIMITS[0] <= q_liq <= config.Q_LIMITS[1]):
        return False, f"Дебит жидкости {q_liq} вне диапазона"
    if not (config.W_LIMITS[0] <= w_pct <= config.W_LIMITS[1]):
        return False, f"Обводненность {w_pct} вне диапазона"
    if not (config.P_RES_LIMITS[0] <= p_res <= config.P_RES_LIMITS[1]):
        return False, f"Пластовое давление {p_res} вне диапазона"
    if not (config.P_BHP_LIMITS[0] <= p_bhp <= config.P_BHP_LIMITS[1]):
        return False, f"Забойное давление {p_bhp} вне диапазона"
    return True, "Параметры в норме"

def calc_hydraulics(q_liq: float, p_res: float, p_bhp: float) -> tuple[float, float]:
    """
    Вычисляет депрессию на пласт (dP) и коэффициент продуктивности (J).
    Бизнес-правило (BR-02): Если dP <= 0, коэффициент J принимается равным 0.0.
    """
    dp = p_res - p_bhp
    if dp <= 0:
        return dp, 0.0
    
    j = q_liq / dp
    return dp, j

def determine_status_code(drawdown: float, w_pct: float, prod_index: float, p_bhp: float, j_norm: float = config.J_NORM_DEFAULT) -> str:
    if p_bhp > config.P_LIMIT_OVERPRESSURE:
        return "OVERPRESSURE"  # Экстренный код по Упражнению 4
    if drawdown < 0.0: 
        return "BLOWOUT"
    if drawdown < 0.0:
        return "BLOWOUT"
    elif drawdown <= config.DP_MIN_ACTIVE:
        return "IDLE"
    elif w_pct >= config.W_CRITICAL:
        return "WATERED"
    elif prod_index < j_norm:
        return "CLOGGED"
    else:
        return "NORMAL"

def route_dispatcher_action(status_code: str) -> tuple[str, int]:
    """Маршрутизирует код состояния в конкретную директиву диспетчеру через match-case."""
    match status_code:
        case "OVERPRESSURE":
            return "КРИТИЧЕСКИЙ СБОЙ: Давление выше 50 МПа! Мгновенно стравить давление в коллектор!", 3
        case "BLOWOUT":
            return "МАРШРУТ АВАРИЙНЫЙ: Закрыть коренную задвижку, объявить тревогу!", 3
        case "BLOWOUT":
            return "МАРШРУТ АВАРИЙНЫЙ: Закрыть коренную задвижку, объявить тревогу!", 3
        case "IDLE":
            return "МАРШРУТ ТЕХНИЧЕСКИЙ: Перевести скважину в ожидание ремонта", 1
        case "WATERED":
            return "МАРШРУТ ТЕХНОЛОГИЧЕСКИЙ: Ограничить отбор, направить на водоотделение", 2
        case "CLOGGED":
            return "МАРШРУТ ОЧИСТКИ: Запланировать промывку призабойной зоны", 2
        case "NORMAL":
            return "МАРШРУТ СТАНДАРТНЫЙ: Продолжить работу в штатном режиме", 0
        case _:
            return "Неизвестный статус", 0

if __name__ == "__main__":
    print("ПРОВЕРКА АВАРИЙНОЙ ДИАГНОСТИКИ (Вариант Б, Вариант №18)")
    print("-" * 55)
    
    v_q_liq, v_p_res, v_p_bhp = 112.0, 23.5, 14.0
    v_w_pct = 74.0
    
    is_valid, msg = validate_telemetry(v_q_liq, v_w_pct, v_p_res, v_p_bhp)
    print(f"Статус валидации телеметрии: {msg}")
    
    my_dp, my_j = calc_hydraulics(v_q_liq, v_p_res, v_p_bhp)
    
    code = determine_status_code(my_dp, v_w_pct, my_j, v_p_bhp)
    
    directive, level = route_dispatcher_action(code)

    print("\n" + "="*40)
    print(f"РАСЧЁТНЫЕ ДАННЫЕ ПАРЫ (Вариант №18):")
    print(f"-> Депрессия на пласт (dP): {my_dp:.2f} МПа")
    print(f"-> Коэфф. продуктивности (J): {my_j:.2f} м³/(сут·МПа)")
    print(f"-> Диагностический код скважины: {code}")
    print(f"-> Директива диспетчеру: {directive}")
    print(f"-> Уровень критичности (0-3): {level}")
    print("="*40)
