from decimal import Decimal

def set_stop_loss(entry_price: Decimal, stop_loss_percentage: float) -> Decimal:

    return entry_price * (Decimal(1) - Decimal(stop_loss_percentage) / Decimal(100))


def calculate_position_size(account_balance: Decimal,
                            risk_percentage: float,
                            stop_loss_price: Decimal,
                            current_price: Decimal) -> Decimal:
    risk_amount = account_balance * (Decimal(risk_percentage) / Decimal(100))
    price_diff = abs(current_price - stop_loss_price)
    if price_diff == 0:
        return Decimal(0)
    return risk_amount / price_diff
