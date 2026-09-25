import asyncio
import json
import os
import random
import threading
import time
import warnings
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from flask import Flask, jsonify, request
from google.protobuf.internal.decoder import _DecodeVarint32
import aiohttp
import requests
import telebot
from telebot import types

warnings.filterwarnings("ignore")

# ==================== إعدادات التليجرام ====================
TELEGRAM_TOKEN = ""
try:
  if os.path.exists("config.json"):
    with open("config.json", "r", encoding="utf-8") as f:
      conf = json.load(f)
      TELEGRAM_TOKEN = conf.get("telegram_token", "").strip()
  else:
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
except Exception as e:
  print(f"Error reading config.json: {e}")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ==================== إعدادات الإحصائيات والأهداف ====================
TARGETS_FILE = "active_targets.json"
REQUEST_STATS = {"total_sent": 0, "start_time": time.time()}
stats_lock = threading.Lock()
active_loops = {}


def load_saved_targets():
  if os.path.exists(TARGETS_FILE):
    try:
      with open(TARGETS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      return []
  return []


def save_targets_to_file():
  try:
    with open(TARGETS_FILE, "w", encoding="utf-8") as f:
      json.dump(list(active_loops.keys()), f)
  except:
    pass


# ==================== التشفير والدوال الأساسية ====================
k = b"Yg&tc%DEuh6%Zc^8"
iv = b"6oyZDr22E3ychjM%"


def eNc(d):
  cipher = AES.new(k, AES.MODE_CBC, iv)
  return cipher.encrypt(pad(d, AES.block_size))


def pB(d):
  i, out = 0, {}
  while i < len(d):
    try:
      key, i = _DecodeVarint32(d, i)
    except:
      break
    fn, wt = key >> 3, key & 0x7
    if fn == 0:
      break
    if wt == 0:
      try:
        v, i = _DecodeVarint32(d, i)
      except:
        break
      out[str(fn)] = {"t": "int", "v": v}
    elif wt == 2:
      try:
        ln, i = _DecodeVarint32(d, i)
      except:
        break
      if i + ln > len(d):
        break
      v = d[i : i + ln]
      i += ln
      try:
        out[str(fn)] = {"t": "str", "v": v.decode()}
      except:
        out[str(fn)] = {"t": "hex", "v": v.hex()}
    else:
      break
  return out


def eI(x):
  x = int(x)
  dec = [
      "80",
      "81",
      "82",
      "83",
      "84",
      "85",
      "86",
      "87",
      "88",
      "89",
      "8a",
      "8b",
      "8c",
      "8d",
      "8e",
      "8f",
      "90",
      "91",
      "92",
      "93",
      "94",
      "95",
      "96",
      "97",
      "98",
      "99",
      "9a",
      "9b",
      "9c",
      "9d",
      "9e",
      "9f",
      "a0",
      "a1",
      "a2",
      "a3",
      "a4",
      "a5",
      "a6",
      "a7",
      "a8",
      "a9",
      "aa",
      "ab",
      "ac",
      "ad",
      "ae",
      "af",
      "b0",
      "b1",
      "b2",
      "b3",
      "b4",
      "b5",
      "b6",
      "b7",
      "b8",
      "b9",
      "ba",
      "bb",
      "bc",
      "bd",
      "be",
      "bf",
      "c0",
      "c1",
      "c2",
      "c3",
      "c4",
      "c5",
      "c6",
      "c7",
      "c8",
      "c9",
      "ca",
      "cb",
      "cc",
      "cd",
      "ce",
      "cf",
      "d0",
      "d1",
      "d2",
      "d3",
      "d4",
      "d5",
      "d6",
      "d7",
      "d8",
      "d9",
      "da",
      "db",
      "dc",
      "dd",
      "de",
      "df",
      "e0",
      "e1",
      "e2",
      "e3",
      "e4",
      "e5",
      "e6",
      "e7",
      "e8",
      "e9",
      "ea",
      "eb",
      "ec",
      "ed",
      "ee",
      "ef",
      "f0",
      "f1",
      "f2",
      "f3",
      "f4",
      "f5",
      "f6",
      "f7",
      "f8",
      "f9",
      "fa",
      "fb",
      "fc",
      "fd",
      "fe",
      "ff",
  ]
  xxx = [
      "1",
      "01",
      "02",
      "03",
      "04",
      "05",
      "06",
      "07",
      "08",
      "09",
      "0a",
      "0b",
      "0c",
      "0d",
      "0e",
      "0f",
      "10",
      "11",
      "12",
      "13",
      "14",
      "15",
      "16",
      "17",
      "18",
      "19",
      "1a",
      "1b",
      "1c",
      "1d",
      "1e",
      "1f",
      "20",
      "21",
      "22",
      "23",
      "24",
      "25",
      "26",
      "27",
      "28",
      "29",
      "2a",
      "2b",
      "2c",
      "2d",
      "2e",
      "2f",
      "30",
      "31",
      "32",
      "33",
      "34",
      "35",
      "36",
      "37",
      "38",
      "39",
      "3a",
      "3b",
      "3c",
      "3d",
      "3e",
      "3f",
      "40",
      "41",
      "42",
      "43",
      "44",
      "45",
      "46",
      "47",
      "48",
      "49",
      "4a",
      "4b",
      "4c",
      "4d",
      "4e",
      "4f",
      "50",
      "51",
      "52",
      "53",
      "54",
      "55",
      "56",
      "57",
      "58",
      "59",
      "5a",
      "5b",
      "5c",
      "5d",
      "5e",
      "5f",
      "60",
      "61",
      "62",
      "63",
      "64",
      "65",
      "66",
      "67",
      "68",
      "69",
      "6a",
      "6b",
      "6c",
      "6d",
      "6e",
      "6f",
      "70",
      "71",
      "72",
      "73",
      "74",
      "75",
      "76",
      "77",
      "78",
      "79",
      "7a",
      "7b",
      "7c",
      "7d",
      "7e",
      "7f",
  ]
  x = x / 128
  if x > 128:
    x = x / 128
    if x > 128:
      x = x / 128
      if x > 128:
        x = x / 128
        sx, y = int(x), (x - int(x)) * 128
        sy, z = int(y), (y - int(y)) * 128
        sz, n = int(z), (z - int(z)) * 128
        sn, m = int(n), (n - int(n)) * 128
        return dec[int(m)] + dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]
      else:
        sx, y = int(x), (x - int(x)) * 128
        sy, z = int(y), (y - int(y)) * 128
        sz, n = int(z), (z - int(z)) * 128
        return dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]
  r = bytearray()
  n = int(x)
  while True:
    p = n & 0x7F
    n >>= 7
    if n:
      p |= 0x80
    r.append(p)
    if not n:
      break
  return r.hex()


sRv = "https://clientbp.ppmainecoonghj.com"


def gT(uid, pw):
  r = requests.post(
      "https://100067.connect.garena.com/oauth/guest/token/grant",
      headers={
          "Host": "100067.connect.garena.com",
          "Content-Type": "application/x-www-form-urlencoded",
      },
      data={
          "uid": uid,
          "password": pw,
          "response_type": "token",
          "client_type": "2",
          "client_secret": (
              "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
          ),
          "client_id": "100067",
      },
      verify=False,
      timeout=5,
  )
  d = r.json()
  return d["access_token"], d["open_id"]


def bL(at, oid):
  dT = bytes.fromhex(
      "1a13323032352d30382d33302030353a31393a3231220966726565206669726528013a08312e3131342e31334232416e64726f6964204f532039202f204150492d3238202850492f72656c2e636a772e32303232303531382e313134313333294a0848616e6468656c64520a41544d204d6f62696c735a045749464960b60a68ee0572033330307a1f41524d7637205646507633204e454f4e20564d48207c2032343030207c20328001c90f8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e329a012b476f6f676c657c64666134616234622d396463342d343534652d383036352d653730633733336661353366a2010e3130352e3233352e3133392e3931aa01026172b201203164386563303234306564653130393937336633333231623933353462343464ba010134c2010848616e6468656c64ca01104173757320415355535f493030354441ea014061666366626631333333346265343230333665346637343263383062393536333434626564373630616339316233616666396236303761363130616234333930f00101ca020a41544d204d6f62696c73d2020457494649ca03203734323862323533646566633136343031386336303461316562626665626466e003a88102e803f6e501f003af13f80384078004e7f0018804a881029004e7f0019804a88102c80401d2043d2f646174612f6170702f636f6d2e6474732e667265656669726574682d506465446e4f696c4353466e3337703141485f464c673d3d2f6c69622f61726de00401ea045f32303837663631633139663537663261663465376665666630623234643964397c2f646174612f6170702f636f6d2e6474732e667265656669726574682d506465446e4f696c4353466e3337703141485f464c673d3d2f626173652e61706bf00403f804018a050233329a050a32303139313138363933b205094f70656e474c455332b805ff7fc00504e005f346ea0507616e64726f6964f205704b71734854355a4c5772596c6a4e62355671682f2f7946526c615048534f394e5753517356764f6d646845456e37572b56484e554b2b512b666475413370744e724742304c6c304c527a335757306a4f7765734c6a3661695537735a34307038426655452f46492f6a7a535477526532f805fbe4068806019006019a060134a2060134b206224751404f000e5e00440655410e504d0d13685a0754060c6d5c560e6a59563b0b5535"
  )
  ts = str(time.strftime("%Y-%m-%d %H:%M:%S")).encode()
  dT = dT.replace(b"2025-08-30 05:19:21", ts)
  dT = dT.replace(
      b"afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390",
      at.encode(),
  )
  dT = dT.replace(b"1d8ec0240ede109973f3321b9354b44d", oid.encode())
  return eNc(dT)


def fS(raw):
  me_idx = raw.find(b"\x12\x02ME")
  if me_idx != -1:
    for i in range(me_idx - 1, max(me_idx - 30, -1), -1):
      if raw[i] == 0x08:
        return i
  return 0


def gJ(uid, pw):
  try:
    at, oid = gT(uid, pw)
    pay = bL(at, oid)
    r = requests.post(
        "https://loginbp.ppmainecoonghj.com/MajorLogin",
        headers={
            "User-Agent": (
                "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0,"
                " libcurl/8.5.0-DEV)"
            ),
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "loginbp.ppmainecoonghj.com",
        },
        data=pay,
        verify=False,
        timeout=5,
    )
    start = fS(r.content)
    x = pB(r.content[start:])
    for fn in ("8", "20", "9"):
      f = x.get(fn)
      if f and f.get("t") == "str" and len(f.get("v", "")) > 50:
        return f["v"].strip()
  except:
    pass
  return None


def fetch_player_info(jwt, to):
  try:
    raw = "08c8b5cfea1810" + eI(to) + "18012008"
    data = bytes.fromhex(eNc(bytes.fromhex(raw)).hex())
    r = requests.post(
        f"{sRv}/GetPlayerPersonalCard",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {jwt}",
        },
        data=data,
        verify=False,
        timeout=3,
    )
    if r.status_code == 200:
      parsed = pB(r.content)
      for key in parsed:
        if parsed[key].get("t") == "str" and len(parsed[key].get("v", "")) > 1:
          val = parsed[key]["v"]
          if not val.startswith("http"):
            return val
  except:
    pass
  return "مقاتل فري فاير"


# قراءة الحسابات
aCcs = {}
if os.path.exists("accs.txt"):
  with open("accs.txt", "r", encoding="utf-8") as f:
    for line in f:
      if ":" in line:
        u, p = line.strip().split(":", 1)
        aCcs[u.strip()] = p.strip()

tOkens = {}
for uid, pw in aCcs.items():
  tok = gJ(uid, pw)
  if tok:
    tOkens[uid] = tok


# ==================== محرك الإرسال غير المتزامن الخارق ====================
async def async_worker(session, jwt, tgt):
  headers = {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-GA": "v1 1",
      "ReleaseVersion": "OB55",
      "Host": "clientbp.ggpolarbear.com",
      "Authorization": f"Bearer {jwt}",
      "User-Agent": "Free%20Fire/2019117061 CFNetwork/1399 Darwin/22.1.0",
  }
  raw = "08c8b5cfea1810" + eI(tgt) + "18012008"
  try:
    data = bytes.fromhex(eNc(bytes.fromhex(raw)).hex())
    async with session.post(
        f"{sRv}/RequestAddingFriend",
        headers=headers,
        data=data,
        ssl=False,
        timeout=2,
    ) as resp:
      if resp.status == 200:
        with stats_lock:
          REQUEST_STATS["total_sent"] += 1
  except:
    pass


async def main_attack_loop(tgt, event):
  connector = aiohttp.TCPConnector(limit=0, ssl=False)
  async with aiohttp.ClientSession(connector=connector) as session:
    while not event.is_set():
      tasks = [
          async_worker(session, jwt, tgt) for uid, jwt in tOkens.items()
      ]
      if tasks:
        await asyncio.gather(*tasks)
      await asyncio.sleep(0)


def run_async_loop(tgt, event):
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  loop.run_until_complete(main_attack_loop(tgt, event))


def sPam(tgt):
  ev = threading.Event()
  active_loops[tgt] = ev
  t = threading.Thread(target=run_async_loop, args=(tgt, ev), daemon=True)
  t.start()
  save_targets_to_file()


def restore_targets():
  saved = load_saved_targets()
  for uid in saved:
    if uid not in active_loops:
      sPam(uid)


# ==================== لوحة تحكم تليجرام الكاملة والمطورة ====================
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
  help_text = (
      "⚡ **لوحة السيطرة والدمار الشامل (Async Hyper-Turbo)** 🔥\n\n"
      "🚀 **الأوامر المتاحة:**\n"
      "🎯 `/spam <UID>` - إطلاق الهجوم الخارق (كل الحسابات معاً)\n"
      "🛑 `/stop <UID>` - إيقاف الهجوم عن الهدف\n"
      "🚀 `/turbo` - عرض مؤشر الطلبات في الثانية والسرعة\n"
      "📊 `/stats` - تقرير شامل لحالة العمليات والنظام\n"
      "📋 `/status` - الأهداف المشتعلة حالياً\n"
      "📂 `/accounts` - إحصائيات الحسابات وجاهزيتها المتوازية\n"
      "📶 `/ping` - قياس سرعة الاستجابة الحقيقية للسيرفر\n"
      "👑 `/dev` - معلومات المطور (skip)\n"
      "🔄 `/restart` - تصفير الذاكرة وإعادة ضبط النظام بالكامل"
  )
  bot.reply_to(message, help_text, parse_mode="Markdown")


@bot.message_handler(commands=["ping"])
def cmd_ping(message):
  start_time = time.time()
  msg = bot.reply_to(message, "📡 جاري فحص سرعة الاستجابة...")
  latency = int((time.time() - start_time) * 1000)
  bot.edit_message_text(
      f"📶 **استجابة البوت:** `{latency} ms`\n⚡ **النظام يعمل بكفاءة قصوى!**",
      chat_id=message.chat.id,
      message_id=msg.message_id,
      parse_mode="Markdown",
  )


@bot.message_handler(commands=["turbo"])
def cmd_turbo(message):
  with stats_lock:
    total = REQUEST_STATS["total_sent"]
    elapsed = time.time() - REQUEST_STATS["start_time"]
    rate = int(total / elapsed) if elapsed > 0 else 0
  bot.reply_to(
      message,
      f"🚀 **معدل السرعة الخارق:** `~{rate} طلب/ثانية`\n🔥 **إجمالي الناجح:** `{total}`",
      parse_mode="Markdown",
  )


@bot.message_handler(commands=["stats"])
def cmd_stats(message):
  bot.reply_to(
      message,
      (
          "📊 **تقرير نظام العمليات:**\n\n📂 الحسابات المحملة:"
          f" `{len(aCcs)}`\n🎯 الأهداف النشطة: `{len(active_loops)}`"
      ),
      parse_mode="Markdown",
  )


@bot.message_handler(commands=["dev"])
def cmd_dev(message):
  bot.reply_to(
      message,
      "👑 **المطور:** skip\n🔥 **الإصدار:** Async Hyper-Turbo v6.0",
      parse_mode="Markdown",
  )


@bot.message_handler(commands=["restart"])
def cmd_restart(message):
  active_loops.clear()
  if os.path.exists(TARGETS_FILE):
    os.remove(TARGETS_FILE)
  bot.reply_to(message, "🔄 تم إعادة ضبط وتصفير النظام بالكامل!", parse_mode="Markdown")


@bot.message_handler(commands=["accounts"])
def cmd_accounts(message):
  bot.reply_to(
      message,
      (
          "📊 **إحصائيات الحسابات:**\n\n📂 إجمالي الحسابات:"
          f" `{len(aCcs)}`\n🟢 المتصلة الآن: `{len(tOkens)}`"
      ),
      parse_mode="Markdown",
  )


@bot.message_handler(commands=["status"])
def cmd_status(message):
  if not active_loops:
    bot.reply_to(message, "💤 لا توجد أهداف نشطة حالياً.")
    return
  text = "🎯 **الأهداف المستهدفة حالياً:**\n"
  for uid in active_loops.keys():
    text += f"🔥 `{uid}`\n"
  bot.reply_to(message, text, parse_mode="Markdown")


@bot.message_handler(commands=["spam"])
def cmd_spam(message):
  parts = message.text.split()
  if len(parts) < 2:
    bot.reply_to(message, "⚠️ الاستخدام: `/spam <UID>`", parse_mode="Markdown")
    return
  uid = parts[1].strip()
  if uid in active_loops:
    bot.reply_to(message, "⚠️ الهدف تحت الهجوم بالفعل!", parse_mode="Markdown")
    return

  player_name = "مقاتل فري فاير"
  if tOkens:
    first_jwt = list(tOkens.values())[0]
    player_name = fetch_player_info(first_jwt, uid)

  sPam(uid)
  bot.reply_to(
      message,
      (
          f"🚀 **تم إطلاق الهجوم الخارق بنجاح!**\n👤 الاسم: `{player_name}`\n🎯"
          f" الآيدي: `{uid}`"
      ),
      parse_mode="Markdown",
  )


@bot.message_handler(commands=["stop"])
def cmd_stop(message):
  parts = message.text.split()
  if len(parts) < 2:
    return
  uid = parts[1].strip()
  if uid in active_loops:
    active_loops[uid].set()
    active_loops.pop(uid, None)
    save_targets_to_file()
    bot.reply_to(message, f"🛑 تم إيقاف الهجوم عن: `{uid}`", parse_mode="Markdown")
  else:
    bot.reply_to(message, "⚠️ الهدف غير موجود في قائمة الهجوم.")


# ==================== Flask API ====================
app = Flask(__name__)


@app.get("/spam")
def api_spam():
  uid = request.args.get("user_id", "").strip()
  if uid and uid not in active_loops:
    sPam(uid)
    return jsonify({"status": True, "msg": "Async Attack Started"})
  return jsonify({"status": False})


@app.get("/stop")
def api_stop():
  uid = request.args.get("user_id", "").strip()
  if uid in active_loops:
    active_loops[uid].set()
    active_loops.pop(uid, None)
    save_targets_to_file()
    return jsonify({"status": True, "msg": "Stopped"})
  return jsonify({"status": False})


def run_telegram_bot():
  print("🚀 Async Hyper-Turbo Bot is running...")
  bot.remove_webhook()
  bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
  restore_targets()
  threading.Thread(target=run_telegram_bot, daemon=True).start()
  app.run(host="0.0.0.0", port=5000)
