import random
from datetime import timedelta
from decimal import Decimal

import factory
from faker import Faker
from pandas._libs.tslibs.offsets import BDay

from wbportfolio.models import Trade, TradeProposal

fake = Faker()


class TradeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Trade

    currency_fx_rate = Decimal(1.0)
    fees = Decimal(0.0)
    portfolio = factory.SubFactory("wbportfolio.factories.PortfolioFactory")
    underlying_instrument = factory.SubFactory("wbfdm.factories.InstrumentFactory")
    currency = factory.SubFactory("wbcore.contrib.currency.factories.CurrencyFactory")
    transaction_date = factory.Faker("date_object")
    value_date = factory.LazyAttribute(lambda o: o.transaction_date + timedelta(days=1))
    bank = factory.Faker("company")
    marked_for_deletion = False
    shares = factory.Faker("pydecimal", min_value=10, max_value=1000, right_digits=4)
    price = factory.LazyAttribute(lambda o: random.randint(10, 10000))
    # trade_proposal = factory.SubFactory("wbportfolio.factories.TradeProposalFactory")


class TradeProposalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TradeProposal

    trade_date = factory.LazyAttribute(lambda o: (fake.date_object() + BDay(1)).date())
    comment = factory.Faker("paragraph")
    portfolio = factory.SubFactory("wbportfolio.factories.PortfolioFactory")
    creator = factory.SubFactory("wbcore.contrib.directory.factories.PersonFactory")


class CustomerTradeFactory(TradeFactory):
    transaction_subtype = factory.LazyAttribute(
        lambda o: Trade.Type.REDEMPTION if o.shares < 0 else Trade.Type.SUBSCRIPTION
    )
    underlying_instrument = factory.SubFactory("wbportfolio.factories.ProductFactory")
    portfolio = factory.LazyAttribute(lambda x: x.underlying_instrument.primary_portfolio)
