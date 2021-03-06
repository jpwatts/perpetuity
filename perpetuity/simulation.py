import csv
import locale
import logging
import sys

import click


locale.setlocale(locale.LC_ALL, '')


logger = logging.getLogger(__name__)


class CD:
    """A certificate of deposit"""

    def __init__(self, year, maturity, rate, price):
        self.year = year
        self.maturity = maturity
        self.rate = rate
        self.price = price

    def __repr__(self):
        return "{0.__name__}({1.year!r}, {1.maturity!r}, {1.rate!r}, {1.price!r})".format(type(self), self)

    def __str__(self):
        return "{0.maturity}-year CD {1} @ {0.rate:.02%} ({2})".format(
            self,
            locale.currency(self.price, grouping=True),
            locale.currency(self.future_value(), grouping=True)
        )

    def future_value(self, future_year=None):
        """Return the value of this CD in a given year."""
        year = self.year
        maturity = self.maturity
        if future_year is None:
            future_year = year + maturity
        return self.price * (1 + self.rate) ** min(maturity, future_year - year)


class Simulator:
    """A retirement simulator"""

    def __init__(self, initial_balance, desired_income, desired_cd_maturity, cd_rate, investment_return, inflation_rate):
        self.initial_balance = initial_balance
        self.desired_income = desired_income
        self.desired_cd_maturity = desired_cd_maturity
        self.cd_rate = cd_rate
        self.investment_return = investment_return
        self.inflation_rate = inflation_rate

    def __repr__(self):
        return "{0.__name__}({1.initial_balance!r}, {1.desired_income!r}, {1.desired_cd_maturity!r}, {1.cd_rate!r}, {1.investment_return!r}, {1.inflation_rate!r})".format(type(self), self)

    def __iter__(self):
        return self._run()

    def _run(self):
        """Yield annual results until all funds are depleted.

        Because funds may grow at a rate faster than they are consumed, this generator may never stop.
        This is a good problem to have.
        """
        year = 0
        desired_income = self.desired_income
        desired_cd_maturity = self.desired_cd_maturity
        cd_rate = self.cd_rate
        inflation_rate = self.inflation_rate

        balance = self.initial_balance
        income = min(balance, desired_income)
        balance -= income

        cd_portfolio = []

        # Create a ladder to get to the desired CD maturity.
        for cd_maturity in range(1, 1 + desired_cd_maturity):
            current_cd_rate = 0.2 * cd_maturity * cd_rate
            current_cd_price = min(
                balance,
                (desired_income * (1 + inflation_rate) ** cd_maturity) / (1 + current_cd_rate) ** cd_maturity
            )
            balance -= current_cd_price
            cd = CD(year, cd_maturity, current_cd_rate, current_cd_price)
            logger.info("Buy %s", cd)
            cd_portfolio.append(cd)
            if not balance:
                break

        # Year 0
        yield year, income, cd_portfolio, balance

        cd_maturity = desired_cd_maturity
        current_cd_rate = 0.2 * cd_maturity * cd_rate
        investment_return = self.investment_return

        # Keep buying CDs at the desired maturity until the investment balance is depleted.
        while True:
            year += 1

            balance *= 1 + investment_return
            try:
                income = cd_portfolio.pop(0).future_value(year)
            except IndexError:
                income = min(balance, desired_income)
                balance -= income
            else:
                current_cd_price = min(
                    balance,
                    (desired_income * (1 + inflation_rate) ** (year + cd_maturity)) / (1 + current_cd_rate) ** cd_maturity
                )
                balance -= current_cd_price
                cd = CD(year, cd_maturity, cd_rate, current_cd_price)
                logger.info("Buy %s", cd)
                cd_portfolio.append(cd)

            yield year, income, cd_portfolio, balance
            if not balance:
                break

        # Use any remaining CDs after the investment balance is depleted.
        while True:
            year += 1
            try:
                cd = cd_portfolio.pop(0)
            except IndexError:
                break
            yield year, cd.future_value(year), cd_portfolio, balance

    def run(self, max_years=100):
        """Yield annual results for the specified number of years, or until all funds are depleted."""
        g = self._run()
        for i in range(max_years):
            try:
                yield next(g)
            except StopIteration:
                break

    def dump(self, max_years=100, include_header=False, stream=sys.stdout):
        """Dump annual results as CSV for the specified number of years, or until all funds are depleted."""
        writer = csv.writer(stream)
        if include_header:
            writer.writerow((
                "Year",
                "Income",
                "CD Value",
                "Balance"
            ))
        writer.writerows(
            (
                year,
                locale.currency(income, grouping=True),
                locale.currency(sum(cd.future_value(year) for cd in cd_portfolio), grouping=True),
                locale.currency(balance, grouping=True)
            )
            for (year, income, cd_portfolio, balance) in self.run(max_years)
        )


@click.command()
@click.option("--initial-balance", default=1000000.0, help="Initial balance (default: 1000000)")
@click.option("--desired-income", default=100000.0, help="Desired annual income (default: 100000)")
@click.option("--desired-cd-maturity", default=5, help="Desired CD maturity (default: 5)")
@click.option("--cd-rate", default=0.01, help="Expected 5-year CD rate (default: 0.01)")
@click.option("--investment-return", default=0.05, help="Expected investment return (default: 0.05)")
@click.option("--inflation-rate", default=0.025, help="Expected inflation rate (default: 0.025)")
@click.option("--max-years", default=100, help="Maximum number of years to simulate (default: 100)")
@click.option("--include-header", is_flag=True, help="Include CSV header")
@click.option("--logging", default="warning", type=click.Choice(["debug", "info", "warning", "error", "critical"]), help="Log level (default: warning)")
def main(**options):
    logging.basicConfig(level=getattr(logging, options['logging'].upper()))
    simulator = Simulator(
        options['initial_balance'],
        options['desired_income'],
        options['desired_cd_maturity'],
        options['cd_rate'],
        options['investment_return'],
        options['inflation_rate']
    )
    simulator.dump(options['max_years'], include_header=options['include_header'])


if __name__ == '__main__':
    main()
