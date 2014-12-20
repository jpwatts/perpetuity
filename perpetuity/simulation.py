import csv
import sys


class CD:
    def __init__(self, year, maturity, rate, price):
        self.year = year
        self.maturity = maturity
        self.rate = rate
        self.price = price

    def __repr__(self):
        return "{0.__name__}({1.year!r}, {1.maturity!r}, {1.rate!r}, {1.price!r})".format(type(self), self)

    def future_value(self, future_year=None):
        year = self.year
        maturity = self.maturity
        if future_year is None:
            future_year = year + maturity
        return self.price * (1 + self.rate) ** min(maturity, future_year - year)


class Simulator:
    def __init__(self, endowment, desired_income, desired_cd_years, cd_rate, investment_return):
        self.endowment = endowment
        self.desired_income = desired_income
        self.desired_cd_years = desired_cd_years
        self.cd_rate = cd_rate
        self.investment_return = investment_return

    def __repr__(self):
        return "{0.__name__}({1.endowment!r}, {1.desired_income!r}, {1.desired_cd_years!r}, {1.cd_rate!r}, {1.investment_return!r})".format(type(self), self)

    def __iter__(self):
        return self._run()

    def _run(self):
        year = 0
        balance = self.endowment
        desired_income = self.desired_income

        income = min(balance, desired_income)
        balance -= income

        cd_rate = self.cd_rate
        cd_portfolio = []
        for cd_maturity in range(1, 1 + self.desired_cd_years):
            current_cd_rate = 0.2 * cd_maturity * cd_rate
            current_cd_price = min(
                balance,
                desired_income * (1 - current_cd_rate) ** cd_maturity
            )
            balance -= current_cd_price
            cd_portfolio.append(CD(
                year,
                cd_maturity,
                current_cd_rate,
                current_cd_price
            ))
            if not balance:
                break

        yield year, balance, income, cd_portfolio

        cd_maturity = 5
        cd_price = desired_income * (1 - cd_rate) ** cd_maturity
        investment_return = self.investment_return

        while True:
            year += 1

            income = cd_portfolio.pop(0).future_value(year)
            balance *= 1 + investment_return

            current_cd_price = min(balance, cd_price)
            balance -= current_cd_price
            cd_portfolio.append(CD(
                year,
                cd_maturity,
                cd_rate,
                current_cd_price
            ))

            yield year, balance, income, cd_portfolio
            if not balance:
                break

        while True:
            year += 1
            try:
                cd = cd_portfolio.pop(0)
            except IndexError:
                break
            yield year, balance, cd.future_value(year), cd_portfolio

    def run(self, max_years):
        g = self._run()
        for i in range(max_years):
            try:
                yield next(g)
            except StopIteration:
                break

    def dump(self, max_years, stream=sys.stdout, format_money=None):
        if format_money is None:
            format_money = lambda n: "{:.02f}".format(n)
        writer = csv.writer(stream)
        writer.writerows(
            (
                year,
                format_money(balance),
                format_money(income),
                format_money(sum(cd.future_value(year) for cd in cd_portfolio))
            )
            for (year, balance, income, cd_portfolio) in self.run(max_years)
        )


def main():
    simulator = Simulator(3000000, 120000, 5, 0.01, 0.05)
    format_money = None
    # format_money = lambda n: int(round(n, -3))
    simulator.dump(100, format_money=format_money)


if __name__ == '__main__':
    main()
