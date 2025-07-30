from cubicweb.entities import AnyEntity, adapters, fetch_config
from cubicweb.predicates import is_instance


class AuthToken(AnyEntity):
    __regid__ = "AuthToken"
    fetch_attrs, cw_fetch_order = fetch_config(["id", "enabled", "expiration_date"])


class AuthTokenDublinCoreAdapter(adapters.IDublinCoreAdapter):
    __select__ = is_instance("AuthToken")

    def title(self):
        return self.entity.id

    def description(self, format="text/plain"):
        return (
            f"{self.entity.id} ({self.entity.enabled and 'enabled' or 'disabled'}) "
            f"expires on {self.entity.expiration_date}"
        )
