from aiohttp.web import View
from asyncpgsa import PG  # type: ignore


class BaseView(View):
    @property
    def pg(self) -> PG:
        return self.request.app["pg"]


class BaseCreateView(BaseView):

    pass
