from tortoise.functions import Min
from x_model.func import ArrayAgg
from xync_schema import models

from xync_bot.routers.pay.dep import flags


class SingleStore(type):
    _store = None

    async def __call__(cls):
        if not cls._store:
            cls._store = super(SingleStore, cls).__call__()
            cls._store.coins = {k: v for k, v in await models.Coin.all().order_by("ticker").values_list("id", "ticker")}
            curs = {
                k: v
                for k, v in await models.Cur.filter(ticker__in=flags.keys())
                .order_by("ticker")
                .values_list("id", "ticker")
            }
            cls._store.curs = curs
            cls._store.exs = {k: v for k, v in await models.Ex.all().values_list("id", "name")}
            cls._store.pms = {
                k: v
                for k, v in await models.Pmex.filter(pm__pmcurs__cur_id__in=cls._store.curs.keys())
                .annotate(sname=Min("name"))
                .group_by("pm__pmcurs__id")
                .values_list("pm__pmcurs__id", "sname")
            }
            cls._store.coinexs = {
                c.id: [ex.ex_id for ex in c.coinexs] for c in await models.Coin.all().prefetch_related("coinexs")
            }
            cls._store.curpms = {
                cur_id: ids
                for cur_id, ids in await models.Pmcur.filter(cur_id__in=curs.keys())
                .annotate(ids=ArrayAgg("id"))
                .group_by("cur_id")
                .values_list("cur_id", "ids")
            }

        return cls._store


class Store:
    class Global(metaclass=SingleStore):
        coins: dict[int, str]  # id:ticker
        curs: dict[int, str]  # id:ticker
        exs: dict[int, str]  # id:name
        coinexs: dict[int, list[int]]  # id:[ex_ids]
        pms: dict[int, str]  # pmcur_id:name
        curpms: dict[int, list[int]]  # id:[pmcur_ids]

    class Permanent:
        msg_id: int = None
        user: models.User = None
        actors: dict[int, models.Actor] = None  # key=ex_id

    class Current:
        is_target: bool = None
        is_fiat: bool = None

    class Payment:
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
    pay: Payment = Payment()
    curr: Current = Current()
