# Wolfx Client

Websocketを使用したPython用のWolfxクライアントです。

## Usage

```py
from wolfx_client import Client

client = Client()

@client.event
async def on_ready():
    print('Connected!')

@client.event
async def on_eew(data):
    print(f'EEW Detected! MaxScale: {data.MaxIntensity}')

client.run()
```

## イベント関数

| 型名           | 説明                      | 備考         |
|------------   |-------------------------- |--------------|
| `Client`      | Websocketクライアント       | 必須         |
| `on_ready`    | 接続完了時のイベント         | 非同期関数   |
| `on_eew`      | 緊急地震速報受信時のイベント  | 非同期関数   |
| `on_eqlist`   | 地震情報受信時のイベント      | 非同期関数 |
| `on_heartbeat`| 生存確認                    | 非同期関数 |

### クライアントオプション

`Client(isEQL=True)`といったように設定することはできますが、jma_eqlistの使用はこのライブラリでは非推奨となっています。(型が不安定。)  
標準ではEEWのwebsocketに接続されます。

型はwolfxAPIドキュメントを参照してください。 (一応型の説明はつけてあります。)
