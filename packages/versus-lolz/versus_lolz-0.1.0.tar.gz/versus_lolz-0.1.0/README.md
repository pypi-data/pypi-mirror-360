# pylolzteamapi
Unofficial Python client for Lolzteam API

## Installation
```bash
pip install pylolzteamapi
```

## Usage

```python
import lolz.eh

from lolz.sync import Client
import lolz


lolz.eh.hook()

client = Client("token (you can omit `Bearer ` from the beginning)")

steam_accs = client.search(lolz.CAT_STEAM,
                           trade_limit="nomatter",
                           page=2, pmin=30,
                           currency="rub"
)

for acc in steam_accs[:3]:
    print(acc.title)
    print("Price:", acc.price)
    print("Seller:", acc.seller.username)
    print()
```

## Issues and pull requests

Please, feel free to open issues and pull requests.

Pull requests must be made on [Твой Гит](https://tvoygit.ru/vi_is_lonely/versus.lolz).
Issues can be made both on Твой Гит and GitHub.

**LICENSE** (AGPL-v3.0-only)
