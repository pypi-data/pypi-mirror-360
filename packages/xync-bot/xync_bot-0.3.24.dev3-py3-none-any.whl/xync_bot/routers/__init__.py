from tortoise.functions import Min
from xync_schema import models

from xync_bot.routers.pay.dep import flags


class SingleStore(type):
    _store = None

    async def __call__(cls):
        if not cls._store:
            cls._store = super(SingleStore, cls).__call__()
            cls._store.coins = {k: v for k, v in await models.Coin.all().order_by("ticker").values_list("id", "ticker")}
            cls._store.curs = {
                k: v
                for k, v in await models.Cur.filter(ticker__in=flags.keys())
                .order_by("ticker")
                .values_list("id", "ticker")
            }
            cls._store.exs = {k: v for k, v in await models.Ex.all().values_list("id", "name")}
            cls._store.pms = {
                k: v
                for k, v in await models.Pmex.filter(pm__pmcurs__id__in=cls._store.curs.keys())
                .annotate(sname=Min("name"))
                .group_by("pm_id")
                .values_list("pm_id", "sname")
            }
            cls._store.coinexs = {
                c.id: [ex.ex_id for ex in c.coinexs] for c in await models.Coin.all().prefetch_related("coinexs")
            }
            cls._store.curpms = {
                c.id: [pmc.pm_id for pmc in c.pmcurs]
                for c in await models.Cur.filter(id__in=cls._store.curs.keys()).prefetch_related("pmcurs")
            }

        return cls._store


class Store:
    class Global(metaclass=SingleStore):
        coins: dict[int, str]  # id:ticker
        curs: dict[int, str]  # id:ticker
        exs: dict[int, str]  # id:name
        pms: dict[int, models.Pm]  # id:name

    class Permanent:
        user: models.User
        actors: dict[int, models.Actor]  # key=ex_id

    class Current:
        t_cur_id: int = None
        s_cur_id: int = None
        t_coin_id: int = None
        s_coin_id: int = None
        t_pm_id: int = None
        s_pm_id: int = None
        t_ex_id: int = None
        s_ex_id: int = None
        addr: models.Addr = None
        cred: models.Cred = None

    glob: Global
    perm: Permanent = Permanent()
    curr: Current = Current()
