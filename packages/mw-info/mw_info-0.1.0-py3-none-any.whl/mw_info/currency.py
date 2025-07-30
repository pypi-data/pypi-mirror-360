import os
import yaml
  
class CurrencyConverter:
    def __init__(self, rates_file=None):
        if rates_file is None:
            rates_file = os.path.join(os.path.dirname(__file__), "data/currency_rates.yml")
        self.rates = {}
        self.base_currency = None
        self.load_rates(rates_file)

    def load_rates(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        self.base_currency = data.get("base_currency", "MWK")
        self.rates = data.get("rates", {})

    def convert_from_base(self, amount, to_currency):
        to_currency = to_currency.upper()
        rate = self.rates.get(to_currency)
        if not rate:
            raise ValueError(f"Currency '{to_currency}' not supported.")
        return round(amount * rate, 2)

    def convert_to_base(self, amount, from_currency):
        from_currency = from_currency.upper()
        rate = self.rates.get(from_currency)
        if not rate:
            raise ValueError(f"Currency '{from_currency}' not supported.")
        return round(amount / rate, 2)

    def available_currencies(self):
        return list(self.rates.keys())
