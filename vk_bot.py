import requests
import vk_api
from random import randint
import string
import re
import dataset
import os
import sys
import wikipedia
wikipedia.set_lang("ru")
import time
import glob
import ntpath
try:
    import cfg_my as cfg
except Exception:
    import cfg

path = os.getcwd() + '\\logs'
from colorama import Fore, Back, Style, init
init(autoreset=True)
print(Fore.GREEN + 'BOT IS STARTING...')
GROUP_ID = cfg.GROUP_ID
GROUP_API_KEY = cfg.GROUP_API_KEY
USER_API_KEY =  cfg.USER_API_KEY
API_VER = cfg.API_VER
ADMINS = cfg.ADMINS

print(Fore.YELLOW + 'GROUP ID: ' + str(GROUP_ID))
print(Fore.YELLOW + 'API VER.' + API_VER)
st = "ADMINS: "
for i in ADMINS:
    st+=str(i) + ', '
print(Fore.YELLOW + st)


def help():
    a = "Справка по коммандам бота:\n"
    a+="💠.рег - зарегистрироваться\n"
    a+="💠.упоминание - включить/выключить упоминания\n"
    a+="💠.позвать <>- упомянуть всех c сообщением <>\n"
    a+="💠.вики <>- сводка информации по <>\n"
    a+="💠.рандомвики - случайная страница вики\n"
    a+="💠.гей - тест на гея\n"
    a+="💠.баланс - узнать баланс\n"
    a+="💠.топ n - топ n пользователей по балансу\n"
    a+="💠.инвентарь - показать содержимое инвентаря\n"
    a+="💠.заплатить @пользователь- заплатить @\n"
    a+="💠.залог @пользователь- внести залог за @\n"
    a+="💠.работа устроиться - устроиться на работу\n"
    a+="💠.работа уволиться - уволиться с работы\n"
    a+="💠.работать - пойти на работу\n"
    a+="💠.гулять - выйти на улицу\n"
    a+="💠.товары - список товаров\n"
    a+="💠.купить <>-купить товар\n"
    a+="💠.топ - топ пользователей по балансу\n"
    a+="💠.казна - узнать баланс казны\n"
    a+="💠.казна ограбить - попытаться ограбить казну\n"
    a+="💠.самоубийство - самоубийство\n"
    a+="💠.взорвать - взорвать всех\n"
    a+="💠.выстрелить @пользователь- выстрелить в @\n"
    a+="💠.выстрелить рандом - выстрелить в кого-то\n"
    a+="💠.выстрелить рандом - выстрелить в кого-то\n"
    a+="💠.помощь - показать справку\n"
    a+="ТОЛЬКО АДМИНЫ:\n"
    a+="⚙.set <> <> - установить значение(без 2 аргумента - узнать значение)\n"
    return a


settings = None
def initialize_settings():
    global settingst
    global settings
    class settings_class:
        min_salary=settingst.find_one(name="min_salary")['val']
        max_salary=settingst.find_one(name="max_salary")['val']
        salary_cooldown=settingst.find_one(name="salary_cooldown")['val']
        hit_chance=settingst.find_one(name="hit_chance")['val']
        rob_chance=settingst.find_one(name="rob_chance")['val']
        wiki_cost=settingst.find_one(name="wiki_cost")['val']
        random_wiki_cost=settingst.find_one(name="random_wiki_cost")['val']
        nds=settingst.find_one(name="nds")['val']
        zalog_cost=settingst.find_one(name="zalog_cost")['val']
    settings = settings_class()

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

if not os.path.exists("logs"):
    os.mkdir('logs')

logs = [f for f in glob.glob(path + "**/*.txt", recursive=False)]
if logs == []:
    main_log_name = 'logs\\log1.txt'
else:
    logs = [path_leaf(path) for path in logs]
    logs = [i.replace('log', '') for i in logs]
    logs = [i[:-4] for i in logs]
    logs = [int(i) for i in logs]
    log_max = max(logs) + 1
    main_log_name = 'logs\\log' + str(log_max) + '.txt'
log_file = open(main_log_name,"w")
log_file.close()

def log(text,log_file):
    with open(log_file, "a") as file_object:
        file_object.write(str(text) + '\n')

def cr(name):
    if not os.path.exists(name):
        global db
        db = dataset.connect('sqlite:///' + name)
        global table
        table = db['users']
        table.insert(dict(id=0))
        print(Fore.YELLOW + "база данных " + name + " создана")
        table.delete(id=0)
        db.executable.close()
        return True

cr("settings.sqlite")
sdb = dataset.connect('sqlite:///settings.sqlite')
settingst = sdb['users']
if not settingst.find_one(name="created"):
    settingst.insert(dict(name="created",val=0,flag=False))
    settingst.insert(dict(name="min_salary",val=5,flag=False))
    settingst.insert(dict(name="max_salary",val=50,flag=False))
    settingst.insert(dict(name="salary_cooldown",val=30,flag=False))
    settingst.insert(dict(name="hit_chance",val=30,flag=False))
    settingst.insert(dict(name="rob_chance",val=40,flag=False))
    settingst.insert(dict(name="wiki_cost",val=50,flag=False))
    settingst.insert(dict(name="random_wiki_cost",val=20,flag=False))
    settingst.insert(dict(name="nds",val=17,flag=False))
    settingst.insert(dict(name="kazna",val=0,flag=False))
    settingst.insert(dict(name="zalog_cost",val=1500,flag=False))
initialize_settings()


cr("users.sqlite")
dbmon = dataset.connect('sqlite:///users.sqlite')
montable = dbmon['users']
montable.insert(dict(id=0,vid=0,balance=100,q=1.1,last=0,job=False,gay=0,mention=True,worked_num=0,work_rank=1,name="",sname="",jail=False))
montable.delete(id=0)


cr("inventory.sqlite")
dbinv = dataset.connect('sqlite:///inventory.sqlite')
inventory = dbinv['users']
inventory.insert(dict(id=0,vid=0,пистолет=0,патрон=0,слиток999=0,бомба=0))
inventory.delete(id=0)


f = cr("tovary.sqlite")
dbtov = dataset.connect('sqlite:///tovary.sqlite')
tovary = dbtov['list']
tovary.insert(dict(id=0,name="тестовый товар",cnt=0,cost=999,act=0,exp="тестовый ответ"))
tovary.delete(id=0)
if f:
    tovary.insert(dict(name="шава",cnt=0,cost=150,act=0,exp="вы купили шаву за 150₽ и съели ее\nбыло очень вкусно"))
    tovary.insert(dict(name="пистолет",cnt=0,cost=73649,act=1,exp="вы купили Smith & Wesson .500 S&W Magnum за 73649₽"))
    tovary.insert(dict(name="патрон",cnt=0,cost=147,act=2,exp="вы купили один патрон для Smith & Wesson .500 S&W Magnum за 147₽"))
    tovary.insert(dict(name="волк",cnt=0,cost=50,act=3,exp="вы купили волка за 50₽"))
    tovary.insert(dict(name="мем",cnt=0,cost=50,act=4,exp="вы купили мем за 50₽"))
    tovary.insert(dict(name="английский мем",cnt=0,cost=50,act=5,exp="вы купили английский мем за 50₽"))
    tovary.insert(dict(name="видосик",cnt=0,cost=100,act=6,exp="вы купили видосик за 100₽"))
    tovary.insert(dict(name="золотой слиток",cnt=0,cost=4000000,act=7,exp="вы купили 1 кг золота 999 пробы за 4000000₽"))
    tovary.insert(dict(name="водородная бомба",cnt=0,cost=30000000,act=8,exp="вы купили бомбу за 30000000₽"))
    tovary.insert(dict(name="машина",cnt=0,cost=1000000,act=0,exp="вы купили машину за 1000000₽"))
    tovary.insert(dict(name="квартира",cnt=0,cost=2000000,act=0,exp="вы купили квартиру за 2000000₽"))

vk_session = vk_api.VkApi(token=GROUP_API_KEY, api_version=API_VER)
vk_user_session = vk_api.VkApi(token=USER_API_KEY, api_version=API_VER)

def nr():
    snd("Вы еще не зарегистрированы ⚠\nнапишите .рег",event,True)

def nr_other():
    snd("Этот пользователь не зарегистрирован ⚠",event,True)

def goods():
    global tovary
    goods = tovary.distinct('name','cost')
    st = "Товары:\n"
    for i in goods:
        st += i['name'] + ". Цена: " + str(i['cost']) + '₽\n'
    return st


def top(n):
    global montable
    users = montable.distinct('balance','name','sname')
    users_tuple = []
    for i in users:
        users_tuple.append((i['name']+" "+i['sname'],int(i['balance'])))
    users_tuple = sorted(users_tuple, key=lambda balance: balance[1],reverse=True)[:n]
    st = "Топ " + str(len(users_tuple)) + ":\n"
    for i in users_tuple:
        st += i[0] + ': ' + str(i[1]) + '₽\n'
    return st


def random_user(event,usr):
    global montable
    info = vk.messages.getConversationMembers(peer_id=event.message["peer_id"],group_id=GROUP_ID)
    user = int(info['items'][randint(0,info['count']-1  )]['member_id'])
    while not montable.find_one(vid=user) and user==usr:
        user = int(info['items'][randint(0,info['count']-1  )]['member_id'])

    return user


def ask_money(n,usr,tusr):
    bal = int(tusr['balance'])
    if bal>=n:
        bal = take_money(n,bal,usr)
        snd("Списано " + str(n) + "₽\nваш баланс: " + str(bal)+'₽',event,True)
        return True
    else:
        snd("вам не хватает денег 💰\nваш баланс: " + str(bal)+'₽',event,True)
        return False

def take_money(n,bal,usr):
    global montable
    bal = int(bal) - int(n)
    data = dict(vid=usr, balance=bal)
    montable.update(data, ['vid'])
    return bal

def give_money(n,bal,usr):
    global montable
    bal = int(bal) + int(n)
    data = dict(vid=usr, balance=bal)
    montable.update(data, ['vid'])
    return bal

def pict(group_id):
    suc = False
    vk_user = vk_user_session.get_api()
    pid=None
    while not suc and pid=="" or pid==None:
        try:
            p = vk_user.wall.get(owner_id=group_id,count=1,offset=randint(0,500))
            pid = p['items'][0]['attachments'][0]['photo']['id']
            suc = True
        except Exception:
            print(Fore.YELLOW + 'Картинка не найдена')
            time.sleep(0.5)
    vk.messages.send(chat_id=event.chat_id, random_id = randint(-2147483648, 2147483647),attachment='photo' + str(group_id) + '_' + str(pid))


def vid(group_id):
    suc = False
    vk_user = vk_user_session.get_api()
    pid=None
    while not suc and pid=="" or pid==None:
        try:
            p = vk_user.wall.get(owner_id=group_id,count=1,offset=randint(0,500))
            pid = p['items'][0]['attachments'][0]['video']['id']
            suc = True
        except Exception:
            print(Fore.YELLOW + 'Видео не найдено')
            time.sleep(0.5)
    vk.messages.send(chat_id=event.chat_id, random_id = randint(-2147483648, 2147483647),attachment='video' + str(group_id) + '_' + str(pid))


def kill(usr):
    global montable
    global inventory
    if usr == "kill everybody":
        montable.delete()
        inventory.delete()
    else:
        montable.delete(vid=usr)
        inventory.delete(vid=usr)

def jail(usr):
    global montable
    data = dict(vid=usr, jail=True)
    montable.update(data, ['vid'])

def unjail(usr):
    global montable
    data = dict(vid=usr, jail=False)
    montable.update(data, ['vid'])

def act(n,usr,tusr,event):
    global tovary
    global inventory
    if n == 1:
        num = inventory.find_one(vid=usr)['пистолет']
        data = dict(vid=usr, пистолет=num+1)
        inventory.update(data, ['vid'])
    elif n == 2:
        num = inventory.find_one(vid=usr)['патрон'] + 1
        data = dict(vid=usr, патрон=num)
        inventory.update(data, ['vid'])

    elif n == 3:
        pict(-173649272)

    elif n == 4:
        pict(-163452344)

    elif n == 5:
        pict(-150550417)

    elif n == 6:
        vid(-30316056)

    elif n == 7:
        num = inventory.find_one(vid=usr)['слиток999']
        if num:
            num+=1
        else:
            num = 1
        data = dict(vid=usr, слиток999=num)
        inventory.update(data, ['vid'])

    elif n == 8:
        num = inventory.find_one(vid=usr)['бомба']
        if num:
            num+=1
        else:
            num = 1
        data = dict(vid=usr, бомба=num)
        inventory.update(data, ['vid'])



def get_nick(usr,dog):
    global tusr
    if dog:
        nick = "@" + vk.users.get(user_ids=int(usr),fields="screen_name")[0]["screen_name"]
    else:
        if tusr:
            nick = tusr['name']
    return nick

def snd(text,event,tag):
    global mention
    global main_log_name
    if tag:
        text =get_nick(event.message['from_id'],mention) + ", " + text
    vk.messages.send(chat_id=event.chat_id, message=text, random_id = randint(-2147483648, 2147483647))
    try:
        log(text,main_log_name)
    except Exception:
        pass

def call(event):
    user_msg = "{0}".format(event.message["text"]) 
    msg = user_msg.replace('.позвать', '')
    try:
        msg = msg[1:]
    except Exception:
        pass
    ni = vk.messages.getConversationmembers(peer_id=event.message["peer_id"],fields="screen_name")["profiles"]
    ustr = ""
    for user in ni:
        ustr += "@" + user["screen_name"] + " "
    if msg != "":
        ustr += "\n" + msg
    snd(ustr,event,False)

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
while True:
 try:
    print(Fore.MAGENTA + "LONG POLL GET")
    longpoll = VkBotLongPoll(vk_session,group_id=GROUP_ID)
    print(Fore.MAGENTA + "LONG POLL SET")
    vk = vk_session.get_api()
    print(Fore.GREEN + "CONNECTED")
    for event in longpoll.listen():
        #print(event)
        try:
            try:
                #print(event)
                if event.message['action']['type']=='chat_invite_user':
                    usr = event.message['action']['member_id']
                    
                    if usr == -GROUP_ID:
                        snd("Здравствуйте, я бот😎\nчтобы я мог видеть ваши сообщения, сделайте меня админом.",event,False)
                        snd(help(),event,False)
                    else:
                        user = vk.users.get(user_ids=usr)[0]
                        name = user['first_name']
                        snd("Здравствуйте, " + name + '.',event,False)
                        snd(help(),event,False)
                if event.message['action']['type']=='chat_invite_user_by_link':
                    snd("Здравствуйте, вот вам справка по моим коммандам😋",event,False)
                    snd(help(),event,False)


            except Exception:
                pass
            if event.type == VkBotEventType.MESSAGE_NEW and event.message["text"]!="":
                if event.from_user:
                    from_chat = False
                    vk.messages.send(user_id=event.message['from_id'], message="Этот бот предназначен для бесед\nне пишите сюда, ничего не изменится", random_id = randint(-2147483648, 2147483647))   
                if event.from_chat:
                    from_chat = True
                    mes =  event.message["text"].lower()
                    if mes.startswith('.'):
                        ctime = time.time()
                        usr = int(event.message['from_id'])
                        tusr = montable.find_one(vid=usr)
                        inv = inventory.find_one(vid=usr)
                        log_simple = Fore.CYAN + 'vk.com/id' + str(usr) + ' --> ' + Style.BRIGHT + Fore.WHITE + event.message["text"]
                        log_string = str(ctime)+ '  ' + 'vk.com/id' + str(usr) + ' --> ' + event.message["text"]
                        print(log_simple)
                        #print(event)
                        log(log_string,main_log_name)
                        if tusr:
                            mention = tusr['mention']
                            if tusr['jail']:
                                mes = ".JAILED"
                        else:
                            mention = True


                        try:
                            (cmd, args) = mes.split(maxsplit=1)
                        except:
                            cmd = mes
                            args = None

                        if cmd == '.позвать':
                            call(event)

                        if cmd == '.взорвать':
                            if tusr:
                                if inv['бомба']:
                                    snd("вы активировали водородную бомбу",event,True)
                                    time.sleep(2)
                                    snd("обратный отсчет запущен",event,False)
                                    time.sleep(2)
                                    for i in reversed(range(1,11)):
                                        snd(str(i),event,False)
                                        time.sleep(1)
                                    snd("ВЗРЫВ",event,False)
                                    snd("В результате взрыва водородной бомбы все пользователи погибли\nобъявляется минута молчания",event,False)
                                    kill('kill everybody')
                                    time.sleep(60)
                                    snd("минута молчания окончена",event,False)
                                else:
                                    snd("у вас нет водородной бомбы.",event,True)
                            else:
                                nr()

                        elif cmd == '.JAILED':
                            snd("вы в тюрьме\nдругие пользователи могут внести за вас залог",event,True)

                        elif cmd == '.топ':
                            if args:
                                try:
                                    n = int(args)
                                    st = top(n)
                                    snd(st,event,False)
                                except Exception:
                                    st = 'неверное число'
                                    snd(st,event,True)
                            else:
                                st = top(10)
                                snd(st,event,False)


                        elif cmd == '.инвентарь':
                            if tusr:    
                                inv.pop('vid')
                                inv.pop('id')
                                st = "ваш инвентарь:\n"
                                count = 0
                                for i in inv:
                                    val = inv[i]
                                    if val:
                                        if val > 0:
                                            st += str(i) + ': ' + str(val) + '\n'
                                            count+=1
                                if count > 0:
                                    snd(st,event,True)
                                else:
                                    snd("ваш инвентарь пуст",event,True)
                            else:
                                nr()

                        elif cmd == '.упоминание':
                            if tusr:
                                mention = not bool(tusr['mention'])
                                data = dict(vid=usr, mention=mention)
                                montable.update(data, ['vid'])
                                if mention:
                                    snd("упоминание включено",event,True)
                                else:
                                    snd("упоминание выключено",event,True)
                            else:
                                nr()


                        elif cmd == '.самоубийство':
                            snd(get_nick(usr,mention) + " убил себя\nтакова жизнь\nу него было " + str(tusr['balance']) +'₽',event,False)
                            kill(usr)


                        elif cmd == '.выстрелить':
                            if tusr:
                                f = False
                                if args == 'рандом':
                                    reciever = random_user(event,usr)
                                elif args:
                                    reciever = re.findall(r'\[id(\d*)\|.*]', args)[0]
                                else:
                                    snd(".выстрелить @пользователь",event,True)
                                    f = True
                                if not f:
                                    reciever_t = montable.find_one(vid=reciever)
                                    if reciever_t: 
                                        if inv['пистолет']:
                                            if inv['патрон']>0:
                                                money_killer = tusr['balance']
                                                money_killed = reciever_t['balance']
                                                chance = randint(0,100)
                                                data = dict(vid=usr, патрон=inv['патрон']-1)
                                                inventory.update(data, ['vid'])
                                                if chance < settings.hit_chance:
                                                    kill(reciever)
                                                    money_killer = give_money(money_killed,money_killer,usr)
                                                    snd(get_nick(usr,mention) + " убил " + get_nick(reciever,True) + ' 💀\nваш баланс: ' + str(money_killer)+'₽',event,False)
                                                else:
                                                    snd(get_nick(usr,mention) + " промахнулся\nпатронов осталось: " + str(inv['патрон']-1),event,False)
                                            else:
                                                snd("у вас нет патронов.",event,True)
                                        else:
                                            snd("у вас нет пистолета.",event,True)
                                    elif not f:
                                        nr_other()
                            else:
                                nr()


                        elif cmd == '.вики':
                            if tusr:
                                if args:
                                    if ask_money(settings.wiki_cost,usr,tusr):
                                        snd(wikipedia.summary(args),event,False)
                                else:
                                    snd(".вики <название>",event,True)
                            else:
                                nr()
                        elif cmd == '.работать':
                            if tusr:
                                if tusr['job']:
                                    if (int(tusr['last']) + settings.salary_cooldown) <= ctime:
                                        bal = tusr['balance']
                                        q = tusr['q']
                                        worked_num = int(tusr['worked_num']) + int(q)
                                        work_rank = int(tusr['work_rank'])
                                        money = randint(settings.min_salary,settings.max_salary)
                                        prem = None
                                        if worked_num > work_rank ** 2:
                                            work_rank +=1
                                            prem = work_rank ** 4
                                            money += prem
                                        money = money + (2  ** work_rank)
                                        money*=q
                                        money = int(money)
                                        nalog = int(money / 100 * settings.nds)
                                        was = int(settingst.find_one(name="kazna")['val'])
                                        data = dict(name='kazna',val=was+nalog)
                                        settingst.update(data, ['name'])
                                        res = money - nalog
                                        bal = give_money(res,bal,usr)
                                        data = dict(vid=usr, last=ctime,worked_num=worked_num,work_rank=work_rank)
                                        montable.update(data, ['vid'])
                                        st = "вы поработали\nуровень:" + str(work_rank) 
                                        st += "\nваш заработок: " + str(money) + '₽'
                                        if prem:
                                            st += "\nвы повышены, премия: " + str(prem) + '₽' 
                                        st +='\nналог:' + str(nalog) + '₽'
                                        st += '\nваш баланс: ' + str(bal) + '₽'
                                        snd(st,event,True)
                                    else:
                                        snd("кд не прошел\nработать можно раз в " + str(settings.salary_cooldown) + " секунд",event,True)
                                else:
                                    snd("вы безработный\n.работа устроиться - получить работу",event,True)
                            else:
                                nr()


                        elif cmd == '.рандомвики':
                            if tusr:
                                if ask_money(settings.random_wiki_cost,usr,tusr):
                                    r = wikipedia.random(pages=1)
                                    snd(wikipedia.summary(r),event,False)
                            else:
                                nr()


                        elif cmd == '.гулять':
                            if tusr:
                                money_user = tusr['balance']
                                money_kazna = int(settingst.find_one(name="kazna")['val'])
                                chance = randint(0,100)
                                if chance < settings.rob_chance:
                                    snd("вы вышли на улицу и безнаказанно погуляли🤡",event,True)
                                else:
                                    if money_user > 5000:
                                        data = dict(vid=usr,balance=money_user-5000)
                                        montable.update(data, ['vid'])
                                        was = settingst.find_one(name="kazna")['val']
                                        data = dict(name='kazna',val=int(was)+5000)
                                        settingst.update(data, ['name'])
                                        snd("у вас не получилось безнаказанно погулять\nвы заплатили 5000₽ штрафа\nваш баланс: " + str(money_user-5000) + "₽",event,True)
                                    else:
                                        jail(usr)
                                        data = dict(vid=usr,balance=0)
                                        montable.update(data, ['vid'])
                                        snd("у вас не получилось безнаказанно погулять\nвам не хватило денег на уплату штрафа\nвас посадили\nваш баланс: 0₽",event,True)
                            else:
                                nr()




                        elif cmd == '.казна':
                            if args:
                                if tusr:
                                    if args=="ограбить":
                                        if inv['пистолет']:
                                            if inv['патрон']>=5:
                                                money_user = tusr['balance']
                                                money_kazna = int(settingst.find_one(name="kazna")['val'])
                                                chance = randint(0,100)
                                                data = dict(vid=usr, патрон=inv['патрон']-5)
                                                inventory.update(data, ['vid'])
                                                if chance < settings.rob_chance:
                                                    money_user=give_money(money_kazna,money_user,usr)
                                                    data = dict(name='kazna',val=0)
                                                    settingst.update(data, ['name'])
                                                    snd("вы ограбили казну\nваш баланс: "+str(money_user)+'₽',event,True)
                                                else:
                                                    data = dict(vid=usr,balance=0,last=0,job=False,worked_num=0,work_rank=1)
                                                    montable.update(data, ['vid'])
                                                    was = settingst.find_one(name="kazna")['val']
                                                    data = dict(name='kazna',val=int(was)+int(money_user))
                                                    settingst.update(data, ['name'])
                                                    jail(usr)
                                                    snd("у вас не получилось ограбить казну\nвас посадили\nвы уволены с работы\nоружие конфисковано\nваш баланс: 0₽",event,True)
                                            else:
                                                snd("у вас меньше 5 патронов.",event,True)
                                        else:
                                            snd("у вас нет пистолета.",event,True)
                                    else:
                                        snd("нет такой комманды",event,True)
                                else:
                                    nr()
                            else:
                                was = settingst.find_one(name="kazna")['val']
                                st = "В казне " + str(was) + '₽'
                                snd(st,event,False)



                        elif cmd == '.помощь':
                            snd(help(),event,False)
                            snd(goods(),event,False)

                        elif cmd == '.залог':
                            if tusr:
                                if args:
                                    reciever = re.findall(r'\[id(\d*)\|.*]', args)[0]
                                    reciever_t = montable.find_one(vid=reciever)
                                    if reciever_t:
                                        if reciever_t['jail']:
                                            if ask_money(settings.zalog_cost,usr,tusr):
                                                unjail(reciever)
                                                snd("залог внесен\nпользователь освобождён",event,False)
                                        else:
                                            snd("этот пользователь не в тюрьме",event,True)
                                    else:
                                        nr_other()
                                else:
                                    snd(".залог @пользователь",event,True)

                            else:
                                nr()

                        elif cmd == '.рег':
                            if tusr:
                                snd("вы уже зарегистрированы ⚠",event,True)
                            else:
                                user = vk.users.get(user_ids=usr)[0]
                                name = user['first_name']
                                sname = user['last_name']
                                montable.insert(dict(vid=usr,balance=0,q=1.0,last=0,job=False,gay=1337,mention=True,worked_num=0,work_rank=1,name=name,sname=sname,jail=False))
                                inventory.insert(dict(vid=usr,пистолет=0,патрон=0,слиток999=0))
                                snd("Вы были зарегистрированы ✅",event,True)

                        elif cmd == '.заплатить':
                            if tusr:
                                if args:
                                    
                                    reciever = re.findall(r'\[id(\d*)\|.*]', args)[0]
                                    reciever_t = montable.find_one(vid=reciever)
                                    try:
                                        money = int(args.split(" ", 1)[1])
                                    except Exception as e:
                                        money = None
                                    if money:
                                        bal_sender = tusr['balance']
                                        bal_reciever = reciever_t['balance']
                                        if reciever:
                                            if bal_sender >= money: 
                                                bal_sender = take_money(money,bal_sender,usr)
                                                give_money(money,bal_reciever,reciever)
                                                snd("вы заплатили " + str(money) + "₽\nваш баланс: " + str(bal_sender)+'₽',event,False)
                                            else:
                                                snd("вам не хватает денег 💰\nваш баланс: " + str(bal_sender)+'₽',event,True)
                                        else:
                                            nr_other()
                                    else:
                                        snd(".заплатить @пользователь <сумма>",event,True)
                                else:
                                    snd(".заплатить @пользователь <сумма>",event,True)
                            else:
                                nr()


                        elif cmd == '.товары':
                                st = goods()
                                snd(st,event,True)

                        elif cmd == '.купить':
                            if tusr:
                                if args:
                                    tovar = tovary.find_one(name=args)
                                    if tovar:
                                        cost = tovar["cost"]
                                        bal = tusr['balance']
                                        if bal>=cost:
                                            bal = take_money(cost,bal,usr)
                                            snd(tovar["exp"] + "\nваш баланс: " + str(bal)+'₽',event,True)
                                            if tovar['act']>0:
                                                act(int(tovar['act']),usr,tusr,event)
                                        else:
                                            snd("вам не хватает денег 💰\nваш баланс: " + str(bal)+'₽',event,True)
                                    else:
                                        snd("Товар не найден ⚠",event,True)
                                else:
                                    snd(".купить <название товара>",event,True)
                            else:
                                nr()


                        elif cmd == '.гей':
                            tusr
                            if tusr:
                                if tusr["gay"] == 1337:
                                    gay = randint(0,101)
                                    data = dict(vid=usr, gay=gay)
                                    montable.update(data, ['vid'])
                                    snd("вы гей на " + str(gay) + "%",event,True)
                                else:
                                    snd("ничего не поменялось вы гей на " + str(tusr['gay']) + "%",event,True)
                            else:
                                nr()


                        elif cmd == '.баланс':
                            if tusr:
                                snd("ваш баланс: " + str(tusr['balance']) + "₽",event,True)
                            else:
                                nr()

                        elif cmd == '.работа':
                            if args:
                                if tusr:
                                    if args == "устроиться":
                                        if montable.find_one(vid=usr)["job"] == True:
                                            snd("Вы уже работаете ⚠",event,True)
                                        else:
                                            data = dict(vid=usr, job=True,worked_num=0,work_rank=1)
                                            montable.update(data, ['vid'])
                                            snd("Вы устроились на работу 💼",event,True)

                                    elif args == "уволиться":
                                        if montable.find_one(vid=usr)["job"] == False:
                                            snd("Вы еще не работаете ⚠",event,True)
                                        else:
                                            data = dict(vid=usr, job=False, worked_num=0, work_rank=1)
                                            montable.update(data, ['vid'])
                                            snd("Вы уволились с работы 🗽",event,True)
                                    else:
                                        snd("\n.работа устроиться\n.работа уволиться",event,True)
                                else:
                                    nr()
                            else:
                                snd("\n.работа устроиться\n.работа уволиться",event,True)
    
                        elif cmd == '.set':
                            if int(usr) in ADMINS:
                                if args:
                                    if " " in args:
                                        var,val = args.split(" ",1)
                                        if settingst.find_one(name=var):
                                            data = dict(name=var, val=val)
                                            settingst.update(data, ['name'])
                                            initialize_settings()
                                            snd("настройки изменены",event,True)
                                            print(Fore.GREEN + 'Значение переменной ' + var + ' установлено на ' + val)
                                        else:
                                            snd("нет такой настройки",event,True)
                                    else:
                                        var = settingst.find_one(name=args)
                                        if var:
                                            snd("значение: " + str(var['val']),event,True)
                                        else:
                                            snd("нет такой настройки",event,True)
                                else:
                                    snd(".set <> <>",event,True)

                        else:
                            snd('комманды "' + cmd + '" не существует\nотправьте .помощь',event,True)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            if from_chat:
                log(str(e),main_log_name)
                snd("ошибка при выполнении комманды 🐞\n" + str(e) +'\n' + fname + '\nстрока: ' + str(exc_tb.tb_lineno), event,True)
            print(Fore.RED + str(e) + '\n' + fname + '\nстрока: ' + str(exc_tb.tb_lineno))
 except Exception as e:
    print(Back.WHITE + Fore.RED + str(e))
    log(str(e),main_log_name)
    time.sleep(1)
