from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
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

if not TELEGRAM_TOKEN:
  print("⚠️ تنبيه: توكن البوت مفقود، تأكد من ملف config.json!")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ==================== نظام حفظ الأهداف ====================
TARGETS_FILE = "active_targets.json"
REQUEST_STATS = {"total_sent": 0}
stats_lock = threading.Lock()


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
      json.dump(list(aCtive.keys()), f)
  except:
    pass


# ==================== التشفير والدوال الأساسية ====================
k = b"Yg&tc%DEuh6%Zc^8"
iv = b"6oyZDr22E3ychjM%"


def eNc(d):
  cipher = AES.new(k, AES.MODE_CBC, iv)
  return cipher.encrypt(pad(d, AES.block_size))


def dEc(d):
  cipher = AES.new(k, AES.MODE_CBC, iv)
  return unpad(cipher.decrypt(d), AES.block_size)


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
    elif wt == 1:
      if i + 8 > len(d):
        break
      out[str(fn)] = {"t": "64b", "v": d[i : i + 8].hex()}
      i += 8
    elif wt == 5:
      if i + 4 > len(d):
        break
      out[str(fn)] = {"t": "32b", "v": d[i : i + 4].hex()}
      i += 4
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
  ua = [
      "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)",
      "GarenaMSDK/4.0.18P6(SM-A125F ;Android 11;en;IN;)",
      "GarenaMSDK/4.1.0P3(Redmi 9A ;Android 10;en;ID;)",
  ]
  r = requests.post(
      "https://100067.connect.garena.com/oauth/guest/token/grant",
      headers={
          "Host": "100067.connect.garena.com",
          "User-Agent": random.choice(ua),
          "Content-Type": "application/x-www-form-urlencoded",
          "Accept-Encoding": "gzip, deflate, br",
          "Connection": "close",
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
      timeout=10,
  )
  if r.status_code != 200:
    raise Exception(f"garena {r.status_code}")
  d = r.json()
  return d["access_token"], d["open_id"]


def bL(at, oid):
  dT = bytes.fromhex(
      "1a13323032352d30382d33302030353a31393a3231220966726565206669726528013a08312e3131342e31334232416e64726f6964204f532039202f204150492d3238202850492f72656c2e636a772e32303232303531382e313134313333294a0848616e6468656c64520a41544d204d6f62696c735a045749464960b60a68ee0572033330307a1f41524d7637205646507633204e454f4e20564d48207c2032343030207c20328001c90f8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e329a012b476f6f676c657c64666134616234622d396463342d343534652d383036352d653730633733336661353366a2010e3130352e3233352e3133392e3931aa01026172b201203164386563303234306564653130393937336633333231623933353462343464ba010134c2010848616e6468656c64ca01104173757320415355535f493030354441ea014061666366626631333333346265343230333665346637343263383062393536333434626564373630616339316233616666396236303761363130616234333930f00101ca020a41544d204d6f62696c73d2020457494649ca03203734323862323533646566633136343031386336303461316562626665626466e003a88102e803f6e501f003af13f80384078004e7f0018804a881029004e7f0019804a88102c80401d2043d2f646174612f6170702f636f6d2e6474732e667265656669726574682d506465446e4f696c4353466e3337703141485f464c673d3d2f6c69622f61726de00401ea045f32303837663631633139663537663261663465376665666630623234643964397c2f646174612f6170702f636f6d2e6474732e667265656669726574682d506465446e4f696c4353466e3337703141485f464c673d3d2f626173652e61706bf00403f804018a050233329a050a32303139313138363933b205094f70656e474c455332b805ff7fc00504e005f346ea0507616e64726f6964f205704b71734854355a4c5772596c6a4e62355671682f2f7946526c615048534f394e5753517356764f6d646845456e37572b56484e554b2b512b666475413370744e724742304c6c304c527a335757306a4f7765734c6a3661695537735a34307038426655452f46492f6a7a535477526532f805fbe4068806019006019a060134a2060134b206224751404f000e5e00440655410e504d0d13685a0754060c6d5c560e6a59563b0b5535"
  )
  ts = str(datetime.now())[:-7].encode()
  dT = dT.replace(b"2025-08-30 05:19:21", ts)
  dT = dT.replace(
      b"afcfbf13334be42036e4f742c80b956344bed760ac91b3aff9b607a610ab4390",
      at.encode(),
  )
  dT = dT.replace(b"1d8ec0240ede109973f3321b9354b44d", oid.encode())
  return eNc(dT)


def fS(raw):
  for start in range(min(8, len(raw))):
    fields = pB(raw[start:])
    if "8" in fields and fields["8"].get("t") == "str":
      return start
  idx = 0
  while True:
    idx = raw.find(b"\x08", idx)
    if idx == -1:
      break
    fields = pB(raw[idx:])
    if "8" in fields and fields["8"].get("t") == "str":
      return idx
    idx += 1
  me_idx = raw.find(b"\x12\x02ME")
  if me_idx != -1:
    for i in range(me_idx - 1, max(me_idx - 30, -1), -1):
      if raw[i] == 0x08:
        return i
  return 0


def xT(fields):
  for fn in ("8", "20", "9"):
    f = fields.get(fn)
    if f and f.get("t") == "str" and f.get("v"):
      v = f["v"]
      if v.startswith("eyJ") or len(v) > 50:
        return v
  return ""


def gJ(uid, pw):
  at, oid = gT(uid, pw)
  pay = bL(at, oid)
  r = requests.post(
      "https://loginbp.ppmainecoonghj.com/MajorLogin",
      headers={
          "User-Agent": (
              "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0,"
              " libcurl/8.5.0-DEV)"
          ),
          "Accept": "*/*",
          "Accept-Encoding": "deflate, gzip",
          "X-Ga-Sv": "1789534056",
          "Authorization": "Bearer",
          "X-Ga": "v1 1",
          "Releaseversion": "OB55",
          "Ob_VeR": "OB55",
          "PlAy_VeR": "1.132.1",
          "Content-Type": "application/x-www-form-urlencoded",
          "X-Unity-Version": "2018.4.12f1",
          "Host": "loginbp.ppmainecoonghj.com",
      },
      data=pay,
      verify=False,
      timeout=15,
  )
  if r.status_code != 200:
    raise Exception(f"MajorLogin {r.status_code}")
  start = fS(r.content)
  x = pB(r.content[start:])
  tok = xT(x)
  if not tok:
    raise Exception("no token")
  return tok.strip()


def hDr(tok):
  return {
      "Content-Type": "application/x-www-form-urlencoded",
      "X-GA": "v1 1",
      "ReleaseVersion": "OB55",
      "Host": "clientbp.ggpolarbear.com",
      "Accept-Encoding": "gzip, deflate, br",
      "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
      "User-Agent": "Free%20Fire/2019117061 CFNetwork/1399 Darwin/22.1.0",
      "Connection": "keep-alive",
      "Authorization": f"Bearer {tok}",
      "X-Unity-Version": "2018.4.11f1",
      "Accept": "*/*",
  }


def fetch_player_info(jwt, to):
  try:
    raw = "08c8b5cfea1810" + eI(to) + "18012008"
    data = bytes.fromhex(eNc(bytes.fromhex(raw)).hex())
    r = requests.post(
        f"{sRv}/GetPlayerPersonalCard",
        headers=hDr(jwt),
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


def aF(jwt, to):
  raw = "08c8b5cfea1810" + eI(to) + "18012008"
  data = bytes.fromhex(eNc(bytes.fromhex(raw)).hex())
  r = requests.post(
      f"{sRv}/RequestAddingFriend",
      headers=hDr(jwt),
      data=data,
      verify=False,
      timeout=2,
  )
  return r.status_code


# ==================== قراءة الحسابات ====================
aCcs = {}
try:
  with open("accs.txt", "r", encoding="utf-8") as f:
    for line in f:
      line = line.strip()
      if ":" in line:
        uid, pw = line.split(":", 1)
        aCcs[uid.strip()] = pw.strip()
except Exception as e:
  print(f"Error reading accs.txt: {e}")

aCtive = {}
tOkens = {}


# ==================== محرك الإرسال فائق السرعة (ThreadPool) ====================
def worker_task(uid, pw, tgt, ev):
  global tOkens
  while not ev.is_set():
    try:
      if uid not in tOkens:
        tOkens[uid] = gJ(uid, pw)
      jwt = tOkens[uid]
      code = aF(jwt, tgt)
      if code in (401, 403):
        tOkens[uid] = gJ(uid, pw)  # تجديد التوكن فوراً إذا انتهى
        jwt = tOkens[uid]
        aF(jwt, tgt)

      with stats_lock:
        REQUEST_STATS["total_sent"] += 1
    except:
      tOkens.pop(uid, None)
    # لا يوجد أي وقت انتظار (Zero Delay) لضمان أقصى سرعة


def sPam(tgt):
  ev = aCtive[tgt]
  # استخدام ThreadPoolExecutor لتشغيل جميع الحسابات في نفس اللحظة بدون تأخير
  with ThreadPoolExecutor(max_workers=max(1, len(aCcs))) as executor:
    futures = [
        executor.submit(worker_task, uid, pw, tgt, ev)
        for uid, pw in aCcs.items()
    ]
    while not ev.is_set():
      time.sleep(0.5)
    for f in futures:
      f.cancel()
  aCtive.pop(tgt, None)
  save_targets_to_file()


def restore_targets():
  saved_list = load_saved_targets()
  for uid in saved_list:
    if uid not in aCtive:
      ev = threading.Event()
      aCtive[uid] = ev
      threading.Thread(target=sPam, args=(uid,), daemon=True).start()
  if saved_list:
    print(
        f"⚡ تم استعادة واستئناف الهجوم فائق السرعة لـ {len(saved_list)} أهداف بنجاح!"
    )


# ==================== الأوامر والواجهة الجديدة ====================


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
  hide_keyboard = types.ReplyKeyboardRemove()
  help_text = (
      "⚡ **لوحة السيطرة والدمار الشامل (SKIP ULTRA PANEL)** 🔥\n\n"
      "🚀 **قائمة الأوامر السريعة:**\n"
      "🎯 `/spam <UID>` - إطلاق الهجوم فائق السرعة بكل الحسابات\n"
      "🛑 `/stop <UID>` - إيقاف الهجوم عن الآيدي فوراً\n"
      "📊 `/speed` - عرض عدد الطلبات التي تم إرسالها وسرعة الخادم\n"
      "📋 `/status` - عرض الأهداف المشتعلة حالياً\n"
      "📂 `/accounts` - عدد الحسابات وجاهزيتها\n"
      "📶 `/ping` - قياس البينج الحقيقي للسيرفر\n"
      "👑 `/dev` - معلومات المطور (skip)\n"
      "🔄 `/restart` - تنظيف الذاكرة وتصفير النظام\n\n"
      "✨ *ميزة جديدة: السكربت يعمل بدون أي فواصل زمنية وبقوة تدميرية قصوى.*"
  )
  bot.reply_to(
      message, help_text, reply_markup=hide_keyboard, parse_mode="Markdown"
  )


@bot.message_handler(commands=["ping"])
def cmd_ping(message):
  start_time = time.time()
  msg = bot.reply_to(
      message, "📡 **جاري قياس البينج الحقيقي وسرعة الاستجابة...**", parse_mode="Markdown"
  )
  end_time = time.time()
  latency = int((end_time - start_time) * 1000)

  api_ping_start = time.time()
  try:
    requests.get(sRv, timeout=2, verify=False)
    api_latency = int((time.time() - api_ping_start) * 1000)
  except:
    api_latency = "غير متصل"

  response_text = (
      "📶 **تقرير مؤشر السرعة الحقيقي:**\n\n"
      f"🤖 **استجابة البوت (Telegram):** `{latency} ms`\n"
      f"🌐 **استجابة سيرفر اللعبة (API):** `{api_latency} ms`\n"
      "⚡ **الحالة:** السرعة قصوى ولا يوجد أي تأخير!"
  )
  bot.edit_message_text(
      response_text,
      chat_id=message.chat.id,
      message_id=msg.message_id,
      parse_mode="Markdown",
  )


@bot.message_handler(commands=["speed"])
def cmd_speed(message):
  with stats_lock:
    total = REQUEST_STATS["total_sent"]
  text = (
      "🚀 **مؤشر السرعة والأداء اللحظي:**\n\n"
      f"🔥 **إجمالي الطلبات المرسلة للهدف:** `{total}` طلب ناجح\n"
      f"⚡ **معدل الإرسال:** بلا حدود (Zero-Delay Threading)\n"
      f"👥 **الحسابات النشطة في الهجوم:** `{len(aCcs)}` حساب"
  )
  bot.reply_to(message, text, parse_mode="Markdown")


@bot.message_handler(commands=["dev"])
def cmd_dev(message):
  text = (
      "👑 **معلومات المطور:**\n\n"
      "👤 **المطور الصانع:** skip\n"
      "🔥 **الإصدار:** Turbo Multi-Threaded v4.0\n"
      "🛡️ **الحالة:** يعمل بكامل القوة والتوزيع المتوازي."
  )
  bot.reply_to(message, text, parse_mode="Markdown")


@bot.message_handler(commands=["restart"])
def cmd_restart_bot(message):
  aCtive.clear()
  tOkens.clear()
  if os.path.exists(TARGETS_FILE):
    os.remove(TARGETS_FILE)
  bot.reply_to(
      message,
      "🔄 **تم إعادة تشغيل وتصفير النظام بالكامل!**\n🧹 تم مسح كافة الأهداف والذاكرة بنجاح.",
      parse_mode="Markdown",
  )


@bot.message_handler(commands=["accounts"])
def cmd_accounts(message):
  total = len(aCcs)
  active = len([uid for uid in aCcs if uid in tOkens])

  text = (
      "📊 **إحصائيات الحسابات المتاحة:**\n\n"
      f"📂 **إجمالي الحسابات:** `{total}`\n"
      f"🟢 **الحسابات المفعلة وجاهزة للضرب:** `{active}`\n"
      "⚡ **جميع الحسابات تطلق الطلبات معاً في نفس اللحظة.**"
  )
  bot.reply_to(message, text, parse_mode="Markdown")


@bot.message_handler(commands=["status"])
def cmd_status(message):
  if not aCtive:
    bot.reply_to(
        message,
        "💤 **لا توجد أي أهداف مستهدفة حالياً.**",
        parse_mode="Markdown",
    )
    return

  text = "🎯 **قائمة الأهداف المشتعلة حالياً:**\n\n"
  for uid in aCtive.keys():
    text += f"🔥 `الآيدي : {uid}`\n"
  bot.reply_to(message, text, parse_mode="Markdown")


@bot.message_handler(commands=["spam"])
def cmd_spam(message):
  parts = message.text.split()
  if len(parts) < 2:
    bot.reply_to(
        message,
        "⚠️ **خطأ في الاستخدام:** يرجى كتابة الآيدي بالشكل الصحيح:\n`/spam <UID>`",
        parse_mode="Markdown",
    )
    return

  uid = parts[1].strip()
  start_spam_process(message, uid)


def start_spam_process(message, uid):
  if not uid.isdigit():
    bot.reply_to(
        message, "❌ **خطأ:** عذراً، آيدي اللاعب يجب أن يكون أرقاماً فقط!"
    )
    return

  if uid in aCtive:
    bot.reply_to(
        message,
        f"⚠️ **تنبيه:** الآيدي `{uid}` تحت الهجوم الفائق بالفعل حالياً!",
        parse_mode="Markdown",
    )
    return

  if not aCcs:
    bot.reply_to(
        message,
        "❌ **خطأ:** ملف الحسابات `accs.txt` فارغ أو غير موجود!",
        parse_mode="Markdown",
    )
    return

  wait_msg = bot.reply_to(
      message,
      f"🔍 **جاري فحص وجلب بيانات اللاعب `{uid}` وبدء الهجوم الخارق...**",
      parse_mode="Markdown",
  )

  player_name = "مقاتل مجهول"
  try:
    first_uid = list(aCcs.keys())[0]
    if first_uid not in tOkens:
      tOkens[first_uid] = gJ(first_uid, aCcs[first_uid])
    player_name = fetch_player_info(tOkens[first_uid], uid)
  except:
    player_name = "مقاتل فري فاير (الآيدي صحيح)"

  ev = threading.Event()
  aCtive[uid] = ev
  threading.Thread(target=sPam, args=(uid,), daemon=True).start()
  save_targets_to_file()

  success_text = (
      f"🚀 **تم إطلاق الهجوم الفائق بنجاح تام!**\n\n"
      f"👤 **اسم اللاعب:** `{player_name}`\n"
      f"🎯 **الآيدي المستهدف:** `{uid}`\n"
      f"🔥 **الحالة:** مئات الطلبات تُرسل الآن بلا توقف من كافة الحسابات!"
  )

  try:
    bot.edit_message_text(
        success_text,
        chat_id=message.chat.id,
        message_id=wait_msg.message_id,
        parse_mode="Markdown",
    )
  except:
    bot.reply_to(message, success_text, parse_mode="Markdown")


@bot.message_handler(commands=["stop"])
def cmd_stop(message):
  parts = message.text.split()
  if len(parts) < 2:
    bot.reply_to(
        message,
        "⚠️ **خطأ في الاستخدام:** يرجى كتابة الآيدي المراد إيقافه هكذا:\n`/stop <UID>`",
        parse_mode="Markdown",
    )
    return

  uid = parts[1].strip()
  stop_spam_process(message, uid)


def stop_spam_process(message, uid):
  if not uid.isdigit():
    bot.reply_to(
        message, "❌ **خطأ:** عذراً، الآيدي يجب أن يكون أرقاماً فقط!"
    )
    return

  if uid in aCtive:
    aCtive[uid].set()
    save_targets_to_file()
    bot.reply_to(
        message,
        f"🛑 **تم إيقاف الهجوم بنجاح وتأمين السيرفر!**\n\n🎯 **الهدف المتوقف:** `{uid}`",
        parse_mode="Markdown",
    )
  else:
    bot.reply_to(
        message,
        f"⚠️ **تنبيه:** الآيدي `{uid}` ليس عليه أي هجوم نشط حالياً.",
        parse_mode="Markdown",
    )


# ==================== مسارات الـ Flask ====================
app = Flask(__name__)


@app.get("/spam")
def sTart():
  uid = request.args.get("user_id", "").strip()
  if not uid:
    return (
        jsonify({"status": False, "msg": "UID required", "DEV": "skip"}),
        400,
    )
  if uid in aCtive:
    return jsonify({"status": True, "msg": "Already spamming", "DEV": "skip"})
  ev = threading.Event()
  aCtive[uid] = ev
  threading.Thread(target=sPam, args=(uid,), daemon=True).start()
  save_targets_to_file()
  return jsonify(
      {"status": True, "msg": "Turbo Attack Started Successfully", "DEV": "skip"}
  )


@app.get("/stop")
def sTop():
  uid = request.args.get("user_id", "").strip()
  if not uid:
    return (
        jsonify({"status": False, "msg": "UID required", "DEV": "skip"}),
        400,
    )
  if uid in aCtive:
    aCtive[uid].set()
    save_targets_to_file()
    return jsonify({"status": True, "msg": "Attack Stopped", "DEV": "skip"})
  return jsonify({"status": False, "msg": "Target not found", "DEV": "skip"})


def run_telegram_bot():
  print("🚀 Turbo Telegram Bot is running live with Skip modifications...")
  bot.infinity_polling()


if __name__ == "__main__":
  if not TELEGRAM_TOKEN:
    print("❌ خطأ: التوكن غير موجود. يرجى ضبطه أولاً.")
  else:
    restore_targets()
    t = threading.Thread(target=run_telegram_bot, daemon=True)
    t.start()
    app.run(debug=False, host="0.0.0.0", port=5000)
