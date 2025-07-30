from .request import request
from .session import BaseSession
from ..types import Object


class SteamAccount:
    __client: 'Client'
    __item_id: int

    def __init__(self, client: 'Client', account_id: int):
        self.__item_id = account_id
        self.__client = client
    
    def get_inventory(self, game: int, currency: str, ignore_cache: bool = False) -> Object:
        return self.__client.request("get", f"/{self.__item_id}/inventory-value", app_id=game,
                                     currency=currency, ignore_cache=ignore_cache)
    
    def get_mafile(self) -> Object:
        return self.__client.request("get", f"/{self.__item_id}/mafile")
    
    def remove_mafile(self) -> Object:
        return self.__client.request("delete", f"/{self.__item_id}/mafile")
    
    def confirm_sda(self, cid: int, nonce: int) -> Object:
        return self.__client.request("post", f"/{self.__item_id}/confirm-sda", id=cid, nonce=nonce)
    
    def get_mafile_login_code(self) -> Object:
        return self.__client.request("get", f"/{self.__item_id}/guard-code").item


class TelegramAccount:
    __client: 'Client'
    __item_id: int

    def __init__(self, client: 'Client', account_id: int):
        self.__item_id = account_id
        self.__client = client
    
    def get_login_code(self) -> Object:
        return self.__client.request("get", f"/{self.__item_id}/telegram-login-code")
    
    def reset_authorizations(self) -> Object:
        return self.__client.request("post", f"/{self.__item_id}/telegram-reset-authorizations")


class User:
    __client: 'Client'
    
    def __init__(self, client: 'Client', obj: Object):
        self.__client = client
        self.__dict__.update(obj.to_dict())

    def edit(self, **kwargs) -> Object:
        return self.__client.request("put", "/me", **kwargs)
    
    def payments_history(self, **kwargs) -> dict[Object]:
        return self.__client.request("get", "/user/payments", **kwargs).payments


class Account:
    __client: 'Client'
    steam: SteamAccount
    telegram: TelegramAccount

    def __init__(self, client: 'Client', obj: Object):
        self.__client = client
        self.__dict__.update(obj.to_dict())
        self.steam = SteamAccount(self.__client, self.item_id)
        self.telegram = TelegramAccount(self.__client, self.item_id)
    
    def edit(self, **kwargs):
        json = {}

        if "description" in kwargs:
            json["description"] = kwargs["description"]
            del kwargs["description"]
        
        if "information" in kwargs:
            json["information"] = kwargs["information"]
            del kwargs["information"]
        
        return self.__client.request("put", f"/{self.item_id}/edit", **kwargs, _body=json)
    
    def delete(self, reason: str):
        return self.__client.request("delete", f"/{self.item_id}", reason=reason)
    
    def bump(self):
        return self.__client.request("post", f"/{self.item_id}/bump")
    
    def open(self):
        return self.__client.request("post", f"/{self.item_id}/open")
    
    def close(self):
        return self.__client.request("post", f"/{self.item_id}/close")
    
    def claims(self, post_body: str) -> Object:
        return self.__client.request("post", f"/{self.item_id}/claims", _body={"post_body": post_body})
    
    def edit_note(self, text: str) -> Object:
        return self.__client.request("post", f"/{self.item_id}/note-save", _body={"text": text})
    
    def get_image(self, itype: str) -> bytes:
        import base64
        b64 = self.__client.request("get", f"/{self.item_id}/image", type=itype).base64
        return base64.b64decode(b64)
    
    def get_letters(self, login: str, password: str, limit: int) -> list[Object]:
        return self.__client.request("get", "/letters2", item_id=self.item_id,
                                     login=login, password=password, limit=limit).letters
    
    def get_email_code(self, login: str, password: str) -> Object:
        return self.__client.request("get", "/email-code", item_id=self.item_id,
                                     login=login, password=password)
    
    def check_guarantee(self) -> str:
        return self.__client.request("post", f"/{self.item_id}/check-guarantee").message
    
    def cancel_guarantee(self) -> Object:
        return self.__client.request("post", f"/{self.item_id}/refuse-guarantee")
    
    def change_password(self, password: str) -> Object:
        return self.__client.request("post", f"/{self.item_id}/change-password", password=password)
    
    def get_temp_email_password(self) -> str:
        return self.__client.request("get", f"/{self.item_id}/temp-email-password").account
    
    def tag(self, tag_id: int) -> Object:
        return self.__client.request("post", f"/{self.item_id}/tag", tag_id=tag_id)
    
    def untag(self, tag_id: int) -> Object:
        return self.__client.request("delete", f"/{self.item_id}/tag", tag_id=tag_id)
    
    def favorite(self) -> Object:
        return self.__client.request("post", f"/{self.item_id}/star")
    
    def unfavorite(self) -> Object:
        return self.__client.request("delete", f"/{self.item_id}/star")
    
    def stick(self) -> Object:
        return self.__client.request("post", f"/{self.item_id}/stick")
    
    def unstick(self) -> Object:
        return self.__client.request("delete", f"/{self.item_id}/stick")
    
    def change_owner(self, username: str, secret_answer: str) -> Object:
        return self.__client.request("post", f"/{self.item_id}/change-owner",
                                     username=username, secret_answer=secret_answer)
    
    def get_ai_price(self) -> int:
        return self.__client.request("get", f"/{self.item_id}/ai-price").price
    
    def get_auto_buy_price(self) -> int:
        return self.__client.request("get", f"/{self.item_id}/auto-buy-price").price

    def fast_buy(self, price: int) -> Object:
        return self.__client.request("post", f"/{self.item_id}/fast-buy", price=price)

    def check(self) -> Object:
        return self.__client.request("post", f"/{self.item_id}/check-account")
    
    def confirm_buy(self, price: int) -> Object:
        return self.__client.request("post", f"/{self.item_id}/confirm-buy", price=price)


class AccountKey:
    __client: 'Client'

    category: str
    item_id: int

    def __init__(self, client: 'Client', category: str, item_id: int):
        self.__client = client
        self.category = category
        self.item_id = item_id

    def fetch(self):
        rv = self.__client.request("get", f"/{self.item_id}").item
        rv["category_name"] = self.category
        return rv
    
    def get(self):
        return Account(self.__client, self.fetch())


class Search:
    __client: 'Client'

    def __init__(self, client: 'Client'):
        self.__client = client

    def __call__(self, category: str, **kwargs) -> list[Account]:
        return [AccountKey(self.__client, category, i.item_id).get()
                for i in self.__client.request
                ("get", "/" + category, **kwargs).items]


class Steam:
    __client: 'Client'

    def __init__(self, client: 'Client'):
        self.__client = client

    def get_inventory(self, link: str, currency: str, ignore_cache: bool = False) -> Object:
        return self.__client.request("get", "/steam-value", link=link, currency=currency,
                                     ignore_cache=ignore_cache)


class PayProvider:
    __client: 'Client'

    title: str
    is_unavailable: bool

    def __init__(self, client: 'Client', obj: Object):
        self.__client = client

        self.title = obj.title
        self.is_available = obj.isUnavailable


class PayService:
    __client: 'Client'

    def __init__(self, client: 'Client', obj: Object):
        self.__client = client
        self.__dict__.update(obj.to_dict())

        for i in range(len(self.providers)):
            self.providers[i] = PayProvider(self.__client, self.providers[i])


class Payments:
    __client: 'Client'

    def __init__(self, client: 'Client'):
        self.__client = client
    
    def get_services(self) -> list[PayService]:
        return [PayService(self.__client, i) for i in
                self.__client.request("get", "/payment-services").systems]


class Invoices:
    __client: 'Client'

    def __init__(self, client: 'Client'):
        self.__client = client
    
    def get(self) -> list[Object]:
        return self.__client.request("get", "/invoices").invoices
    
    def add(self, currency: str, amount: int, payment_id: int,
            url_success: str, url_callback: str, merchant_id: int,
            comment: str = "", **kwargs) -> Object:
        return self.__client.request("post", "/invoice", currency=currency,
                                     amount=amount, payment_id=payment_id,
                                     url_success=url_success,
                                     url_callback=url_callback,
                                     merchant_id=merchant_id, comment=comment,
                                     **kwargs).invoice


class Proxies:
    __client: 'Client'

    def __init__(self, client: 'Client'):
        self.__client = client
    
    def get(self) -> list[Object]:
        return self.__client.request("get", "/proxy").proxies
    
    def add(self, ip: str, port: int, user: str, password: str, row: str) -> Object:
        return self.__client.request("post", "/proxy", ip=ip, port=port)
    
    def delete(self, proxy_id: int) -> Object:
        return self.__client.request("delete", "/proxy", proxy_id=proxy_id)
    
    def delete_all(self) -> Object:
        return self.__client.request("delete", "/proxy", delete_all=True)


class Client:
    __session: BaseSession
    search: Search
    steam: Steam
    invoices: Invoices
    proxies: Proxies

    def __init__(self, auth_token: str):
        self.__session = BaseSession(auth_token)
        self.search = Search(self)
        self.steam = Steam(self)
        self.invoices = Invoices(self)
        self.proxies = Proxies(self)
    
    def request(self, method, path, **kwargs):
        return request(self.__session, method, path, **kwargs)
    
    def fast_upload(self, **kwargs):
        return Account(self, self.request("post", "/fast-sell", **kwargs).item)
    
    def add_account(self, **kwargs):
        return Account(self, self.request("post", "/item/add", **kwargs).item)
    
    def get_me(self) -> User:
        return User(self, self.request("get", "/me").item)
    
    def edit_me(self, **kwargs) -> Object:
        return self.request("put", "/me", **kwargs)
    
    def create_payout(self, service: str | PayService, wallet: str,
                      amount: int, currency: str, fee: bool = False) -> Object:
        return self.request("post", "/balance/payout", service=service, wallet=wallet,
                            amount=amount, currency=currency, fee=fee)
    
    def transfer_money(self, receiver: int | str, amount: int,
                       currency: str, comment: str = "",
                       hold: bool = False, hold_length: int = 0,
                       hold_period: str = "hour") -> Object:
        return self.request("post", "/balance/transfer", receiver=receiver,
                            amount=amount, currency=currency, comment=comment,
                            hold=hold, hold_length=hold_length, hold_period=hold_period)
    
    def cancel_transfer(self, payment_id: int) -> Object:
        return self.request("post", "/balance/transfer/cancel", payment_id=payment_id)
    
    def fee(self, amount: int) -> Object:
        return self.request("get", "/transfer/fee", amount=amount)
    
    def currency(self) -> dict[str, dict[str, object]]:
        return self.request("get", "/currency").currencyList
    
    def get_auto_payments(self) -> list[Object]:
        return self.request("get", "/auto-payments").payments
    
    def create_auto_payment(self, secret_answer: str, receiver: str,
                            day: int, amount: int, currency: str,
                            description: str = "") -> Object:
        return self.request("post", "/auto-payment", secret_answer=secret_answer,
                            receiver=receiver, day=day, amount=amount,
                            currency=currency, description=description)
    
    def delete_auto_payment(self, payment_id: int) -> Object:
        return self.request("delete", "/auto-payment", auto_payment_id=payment_id)
