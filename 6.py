# -*- coding: utf-8 -*-
from linepy import *
from datetime import datetime
from time import sleep
from bs4 import BeautifulSoup
from humanfriendly import format_timespan, format_size, format_number, format_length
import time, random, sys, json, codecs, threading, glob, re, string, os, requests, subprocess, six, urllib, urllib.parse, ast, pytz

client = LineClient(authToken='token kalian')
client.log("Auth Token : " + str(client.authToken))

channel = LineChannel(client)
client.log("Channel Access Token : " + str(channel.channelAccessToken))

poll = LinePoll(client)

readOpen = codecs.open("read.json","r","utf-8")
settingsOpen = codecs.open("temp.json","r","utf-8")

#GetInfo
clientProfile = client.getProfile()
clientSettings = client.getSettings()
clientPoll = LinePoll(client)
clientMID = client.profile.mid
call = LineCall(client)

read = json.load(readOpen)
settings = json.load(settingsOpen)

if settings["restartPoint"] != None:
    client.sendMessage(settings["restartPoint"], "Bot kembali aktif")
    settings["restartBot"] = None

def restartBot():
    print ("[ INFO ] BOT RESETTED")
    backupData()
    time.sleep(10)
    python = sys.executable
    os.execl(python, python, *sys.argv)

def autoRestart():
    if time.time() - botStart > int(settings["timeRestart"]):
        backupData()
        time.sleep(5)
        restartBot()

def logError(text):
    client.log("[ INFO ] ERROR : " + str(text))
    time_ = datetime.now()
    with open("errorLog.txt","a") as error:
        error.write("\n[%s] %s" % (str(time_), text))

def translate(to_translate, to_language="auto"):
    bahasa_awal = "auto"
    bahasa_tujuan = to_language
    kata = to_translate
    url = 'https://translate.google.com/m?sl=%s&tl=%s&ie=UTF-8&prev=_m&q=%s' % (bahasa_awal, bahasa_tujuan, kata.replace(" ", "+"))
    agent = {'User-Agent':random.choice(settings["userAgent"])}
    cari_hasil = 'class="t0">'
    request = urllib.parse.Request(url, headers=agent)
    page = urllib.parse.urlopen(request).read()
    result = page[page.find(cari_hasil)+len(cari_hasil):]
    result = result.split("<")[0]
    return result

def sendMention(to, mid, firstmessage, lastmessage):
    try:
        arrData = ""
        text = "%s " %(str(firstmessage))
        arr = []
        mention = "@x "
        slen = str(len(text))
        elen = str(len(text) + len(mention) - 1)
        arrData = {'S':slen, 'E':elen, 'M':mid}
        arr.append(arrData)
        text += mention + str(lastmessage)
        client.sendMessage(to, text, {'MENTION': str('{"MENTIONEES":' + json.dumps(arr) + '}')}, 0)
    except Exception as error:
        logError(error)
        client.sendMessage(to, "[ INFO ] Error :\n" + str(error))

def mentionMembers(to, mid):
    try:
        arrData = ""
        textx = "╔══[Mention {} User]\n╠ ".format(str(len(mid)))
        arr = []
        no = 1
        for i in mid:
            mention = "@x\n"
            slen = str(len(textx))
            elen = str(len(textx) + len(mention) - 1)
            arrData = {'S':slen, 'E':elen, 'M':i}
            arr.append(arrData)
            textx += mention
            if int(no) < int(len(mid)):
                no += 1
                textx += "╠ "
            else:
                textx += "\n╚══[ Success ]"
        client.sendMessage(to, textx, {'MENTION': str('{"MENTIONEES":' + json.dumps(arr) + '}')}, 0)
    except Exception as error:
        logError(error)
        client.sendMessage(to, "[ INFO ] Error :\n" + str(error))

def command(text):
    pesan = text.lower()
    if pesan.startswith(settings["keyCommand"]):
        cmd = pesan.replace(settings["keyCommand"],"")
    else:
        cmd = "Undefined command"
    return cmd

def help():
    key = settings["keyCommand"]
    key = key.title()
    helpMessage = "╔══[ Help Message ]" + "\n" + \
                  "╠ Use [" + key + "] for the Prefix" + "\n" + \
                  "╠ " + key + "Help" + "\n" + \
                  "╠ " + key + "Me" + "\n" + \
                  "╠ " + key + "Restart" + "\n" + \
                  "╠ " + key + "Speed" + "\n" + \
                  "╠ " + key + "Leave" + "\n" + \
                  "╠ " + key + "Checkmid 「tag」" + "\n" + \
                  "╠ " + key + "Kickout 「tag」" + "\n" + \
                  "╠ " + key + "Stealprofile 「tag」" + "\n" + \
                  "╠ " + key + "Stealcover 「tag」" + "\n" + \
                  "╠ " + key + "Stealbio 「tag」" + "\n" + \
                  "╠ " + key + "ChangePictureProfile" + "\n" + \
                  "╠ " + key + "ChangeGroupPicture" + "\n" + \
                  "╠ " + key + "Mention" + "\n" + \
                  "╠ " + key + "GroupPicture" + "\n" + \
                  "╠ " + key + "gBroadcast 「text」" + "\n" + \
                  "╠ " + key + "fBroadcast 「text」" + "\n" + \
                  "╠ " + key + "allBroadcast 「text」" + "\n" + \
                  "╠ " + key + "Grouplist" + "\n" + \
                  "╠ " + key + "Rejectall" + "\n" + \
                  "╠ " + key + "Invgroupcall" + "\n" + \
                  "╠ " + key + "Removeallchat" + "\n" + \
                  "╠ " + key + "Changekey 「new key」" + "\n" + \
                  "╠ Mykey" + "\n" + \
                  "╠ " + key + "Runtime" + "\n" + \
                  "╠ " + key + "Time" + "\n" + \
                  "╠══[ Cctv Command ]\n" + \
                  "╠ " + key + "Cctv on" + "\n" + \
                  "╠ " + key + "Cctv off" + "\n" + \
                  "╠ " + key + "Cctv reset" + "\n" + \
                  "╠ " + key + "Cctv result" + "\n" + \
                  "╠══[ Remote Command ]\n" + \
                  "╠ " + key + "Autoread on" + "\n" + \
                  "╠ " + key + "Autoread off" + "\n" + \
                  "╠══[ Fun Command ]\n" + \
                  "╠ " + key + "Searchimage 「query」" + "\n" + \
                  "╠ " + key + "Liststicker" + "\n" + \
                  "╠ " + key + "Spamsticker 「total」 「key sticker」" + "\n" + \
                  "╠ " + key + "Checkpraytime 「location」" + "\n" + \
                  "╠ " + key + "Checkweather 「location」" + "\n" + \
                  "╠ " + key + "Checklocation 「location」" + "\n" + \
                  "╚══[ Jangan Typo ]"
    return helpMessage

def backupData():
    try:
        backup = settings
        f = codecs.open('temp.json','w','utf-8')
        json.dump(backup, f, sort_keys=True, indent=4, ensure_ascii=False)
        backup = read
        f = codecs.open('read.json','w','utf-8')
        json.dump(backup, f, sort_keys=True, indent=4, ensure_ascii=False)
        return True
    except Exception as error:
        logError(error)
        return False

        if op.type == 5:
            print ("[ 5 ] NOTIFIED ADD CONTACT")
            if settings["autoAdd"] == True:
                client.findAndAddContactsByMid(op.param1)
            client.sendMessage(op.param1, "Halo {} terimakasih telah menambahkan saya sebagai teman :3".format(str(client.getContact(op.param1).displayName)))
            arg = "   New Friend : {}".format(str(client.getContact(op.param1).displayName))
            print (arg)

        if op.type == 11:
            print ("[ 11 ] NOTIFIED UPDATE GROUP")
            if op.param3 == "1":
                group = client.getGroup(op.param1)
                contact = client.getContact(op.param2)
                arg = "   Changed : Group Name"
                arg += "\n   New Group Name : {}".format(str(group.name))
                arg += "\n   Executor : {}".format(str(contact.displayName))
                print (arg)
            elif op.param3 == "4":
                group = client.getGroup(op.param1)
                contact = client.getContact(op.param2)
                if group.preventedJoinByTicket == False:
                    gQr = "Opened"
                else:
                    gQr = "Closed"
                arg = "   Changed : Group Qr"
                arg += "\n   Group Name : {}".format(str(group.name))
                arg += "\n   New Group Qr Status : {}".format(gQr)
                arg += "\n   Executor : {}".format(str(contact.displayName))
                print (arg)

        if op.type == 13:
            print ("[ 13 ] NOTIFIED INVITE INTO GROUP")
            group = client.getGroup(op.param1)
            contact = client.getContact(op.param2)
            if settings["autoJoin"] == True:
                if settings["autoReject"]["status"] == True:
                    if len(group.members) > settings["autoReject"]["members"]:
                        client.acceptGroupInvitation(op.param1)
                    else:
                        client.rejectGroupInvitation(op.param1)
                else:
                    client.acceptGroupInvitation(op.param1)
            gInviMids = []
            for z in group.invitee:
                if z.mid in op.param3:
                    gInviMids.append(z.mid)
            listContact = ""
            if gInviMids != []:
                for j in gInviMids:
                    name_ = client.getContact(j).displayName
                    listContact += "\n      + {}".format(str(name_))

            arg = "   Group Name : {}".format(str(group.name))
            arg += "\n   Executor : {}".format(str(contact.displayName))
            arg += "\n   List User Invited : {}".format(str(listContact))
            print (arg)

        if op.type == 17:
            print ("[ 17 ]  NOTIFIED ACCEPT GROUP INVITATION")
            group = client.getGroup(op.param1)
            contact = client.getContact(op.param2)
            arg = "   Group Name : {}".format(str(group.name))
            arg += "\n   User Join : {}".format(str(contact.displayName))
            print (arg)

        if op.type == 19:
            print ("[ 19 ] NOTIFIED KICKOUT FROM GROUP")
            group = client.getGroup(op.param1)
            contact = client.getContact(op.param2)
            victim = client.getContact(op.param3)
            arg = "   Group Name : {}".format(str(group.name))
            arg += "\n   Executor : {}".format(str(contact.displayName))
            arg += "\n   Victim : {}".format(str(victim.displayName))
            print (arg)

        if op.type == 22:
            print ("[ 22 ] NOTIFIED INVITE INTO ROOM")
            if settings["autoLeave"] == True:
                client.sendMessage(op.param1, "Dadah, see you next time")
                client.leaveRoom(op.param1)

        if op.type == 24:
            print ("[ 24 ] NOTIFIED LEAVE ROOM")
            if settings["autoLeave"] == True:
                client.sendMessage(op.param1, "Dadah, see you next time")
                client.leaveRoom(op.param1)

        if op.type == 25:
            print ("[ 25 ] SEND MESSAGE")
            msg = op.message
            text = msg.text
            msg_id = msg.id
            receiver = msg.to
            sender = msg._from
    #        try:
     #            if msg.contentType == 0:
             #        if msg.toType == 2:
                  #       client.sendChatChecked(receiver, msg_id)

            # Check if in group chat or personal chat
            if msg.toType == 0 or msg.toType == 2:
                if msg.toType == 0:
                    to = receiver
                elif msg.toType == 2:
                    to = receiver
                # Check if only text message
                if msg.contentType == 0:
                    if settings["autoRead"] == True:
                        client.sendChatChecked(to, msg_id)
                    if text is None:
                        return
                    else:
                        cmd = command(text)
                    if cmd != "Undefined command":
                        # Basic command
                        if cmd == "help":
                            helpMessage = help()
                            client.sendMessage(to, str(helpMessage))
                            client.sendContact(to, "mid kamu")
                        elif cmd == "me":
                            client.sendContact(to, sender)
                        elif cmd == "restart":
                            client.sendMessage(to, "Mencoba restart...")
                            client.sendMessage(to, "Mohon tunggu beberapa saat...")
                            settings["restartPoint"] = to
                            restartBot()
                        elif cmd == "speed":
                            start = time.time()
                            client.sendMessage(to, "Menghitung kecepatan...")
                            elapsed_time = time.time() - start
                            client.sendMessage(to, "[ Speed ]\nKecepatan mengirim pesan {} detik".format(str(elapsed_time)))
                        elif cmd == "leave":
                            if msg.toType == 2:
                                client.sendMessage(to, "Mencoba keluar dari group")
                                client.leaveGroup(to)
                        elif cmd.startswith("checkmid "):
                            if 'MENTION' in msg.contentMetadata.keys()!= None:
                                names = re.findall(r'@(\w+)', text)
                                mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                                mentionees = mention['MENTIONEES']
                                lists = []
                                for mention in mentionees:
                                    if mention["M"] not in lists:
                                        lists.append(mention["M"])
                                ret_ = "[ Mid User ]"
                                for ls in lists:
                                    ret_ += "\n{}".format(str(ls))
                                client.sendMessage(to, str(ret_))
                        elif cmd.startswith("kickout "):
                            if 'MENTION' in msg.contentMetadata.keys()!= None:
                                names = re.findall(r'@(\w+)', text)
                                mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                                mentionees = mention['MENTIONEES']
                                lists = []
                                for mention in mentionees:
                                    if mention["M"] not in lists:
                                        lists.append(mention["M"])
                                for ls in lists:
                                    try:
                                        client.kickoutFromGroup(to, ls)
                                    except:
                                        client.sendMessage(to, "Mungkin limit atau membernya gak ada")
                                client.sendMessage(to, "Berhasil kickout {} members".format(str(len(lists))))
                        elif cmd.startswith("stealprofile "):
                            if 'MENTION' in msg.contentMetadata.keys()!= None:
                                names = re.findall(r'@(\w+)', text)
                                mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                                mentionees = mention['MENTIONEES']
                                lists = []
                                for mention in mentionees:
                                    if mention["M"] not in lists:
                                        lists.append(mention["M"])
                                for ls in lists:
                                    path = "http://dl.profile.line.naver.jp/" + client.getContact(ls).pictureStatus
                                    if settings["server"] == "VPS":
                                        client.sendImageWithURL(to, str(path))
                                    else:
                                        urllib.urlretrieve(path, "steal.jpg")
                                        client.sendImage(to, "steal.jpg")
                        elif cmd.startswith("stealcover "):
                            if channel != None:
                                if 'MENTION' in msg.contentMetadata.keys()!= None:
                                    names = re.findall(r'@(\w+)', text)
                                    mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                                    mentionees = mention['MENTIONEES']
                                    lists = []
                                    for mention in mentionees:
                                        if mention["M"] not in lists:
                                            lists.append(mention["M"])
                                    for ls in lists:
                                        path = channel.getProfileCoverURL(ls)
                                        path = str(path)
                                        if settings["server"] == "VPS":
                                            client.sendImageWithURL(to, str(path))
                                        else:
                                            urllib.urlretrieve(path, "steal.jpg")
                                            client.sendImage(to, "steal.jpg")
                            else:
                                client.sendMessage(to, "Tidak dapat masuk di line channel")
                        elif cmd.startswith("stealbio "):
                            if 'MENTION' in msg.contentMetadata.keys()!= None:
                                names = re.findall(r'@(\w+)', text)
                                mention = ast.literal_eval(msg.contentMetadata['MENTION'])
                                mentionees = mention['MENTIONEES']
                                lists = []
                                for mention in mentionees:
                                    if mention["M"] not in lists:
                                        lists.append(mention["M"])
                                for ls in lists:
                                    contact = client.getContact(ls)
                                    client.sendMessage(to, "[ Status Message ]\n{}".format(str(contact.statusMessage)))
                        elif cmd == "changepictureprofile":
                            settings["changePicture"] = True
                            client.sendMessage(to, "Silahkan kirim gambarnya")
                        elif cmd == "changegrouppicture":
                            if msg.toType == 2:
                                if to not in settings["changeGroupPicture"]:
                                    settings["changeGroupPicture"].append(to)
                                client.sendMessage(to, "Silahkan kirim gambarnya")
                        elif cmd == "mention":
                            if msg.toType == 0:
                                mentionMembers(to, to)
                            elif msg.toType == 2:
                                group = client.getGroup(to)
                                contact = [mem.mid for mem in group.members]
                                mentionMembers(to, contact)
                        elif cmd == "grouppicture":
                            if msg.toType == 2:
                                group = client.getGroup(to)
                                path = "http://dl.profile.line-cdn.net/" + group.pictureStatus
                                if settings["server"] == "VPS":
                                    client.sendImageWithURL(to, str(path))
                                else:
                                    urllib.urlretrieve(path, "gpict.jpg")
                                    client.sendImage(to, "gpict.jpg")
                        elif cmd.startswith("gbroadcast "):
                            sep = text.split(" ")
                            txt = text.replace(sep[0] + " ","")
                            groups = client.groups
                            for group in groups:
                                client.sendMessage(group, "[ Broadcast ]\n{}".format(str(txt)))
                            client.sendMessage(to, "Berhasil broadcast ke {} group".format(str(len(groups))))
                        elif cmd.startswith("fbroadcast "):
                            sep = text.split(" ")
                            txt = text.replace(sep[0] + " ","")
                            friends = client.friends
                            for friend in friends:
                                client.sendMessage(friend, "[ Broadcast ]\n{}".format(str(txt)))
                            client.sendMessage(to, "Berhasil broadcast ke {} teman".format(str(len(friends))))
                        elif cmd.startswith("allbroadcast "):
                            sep = text.split(" ")
                            txt = text.replace(sep[0] + " ","")
                            friends = client.friends
                            groups = client.groups
                            for group in groups:
                                client.sendMessage(group, "[ Broadcast ]\n{}".format(str(txt)))
                            client.sendMessage(to, "Berhasil broadcast ke {} group".format(str(len(groups))))
                            for friend in friends:
                                client.sendMessage(friend, "[ Broadcast ]\n{}".format(str(txt)))
                            client.sendMessage(to, "Berhasil broadcast ke {} teman".format(str(len(friends))))
                        elif cmd == "grouplist":
                            groups = client.groups
                            ret_ = "╔══[ Group List ]"
                            no = 0
                            for gid in groups:
                                group = client.getGroup(gid)
                                ret_ += "\n╠ {}. {} | {}".format(str(no), str(group.name), str(len(group.members)))
                                no += 1
                            ret_ += "\n╚══[ Total {} Groups ]".format(str(len(groups)))
                            client.sendMessage(to, str(ret_))
                        elif cmd == "rejectall":
                            ginvited = client.ginvited
                            if ginvited != [] and ginvited != None:
                                for gid in ginvited:
                                    client.rejectGroupInvitation(gid)
                                client.sendMessage(to, "Berhasil tolak sebanyak {} undangan".format(str(len(ginvited))))
                            else:
                                client.sendMessage(to, "Tidak ada undangan yang tertunda")
                        elif cmd == "invgroupcall":
                            if msg.toType == 2:
                                group = client.getGroup(to)
                                members = [mem.mid for mem in group.members]
                                call.acquireGroupCallRoute(to)
                                call.inviteIntoGroupCall(to, contactIds=members)
                                client.sendMessage(to, "Berhasil mengundang kedalam telponan group")
                        elif cmd == "removeallchat":
                            client.removeAllMessages(op.param2)
                            client.sendMessage(to, "Berhasil hapus semua chat")
                        elif cmd.startswith("changekey "):
                            sep = text.split(" ")
                            key = text.replace(sep[0] + " ","")
                            if " " in key:
                                client.sendMessage(to, "Key tidak bisa menggunakan spasi")
                            else:
                                settings["keyCommand"] = str(key).lower()
                                client.sendMessage(to, "Berhasil mengganti key menjadi {}".format(str(key).lower()))
                        elif text.lower() == "mykey":
                            client.sendMessage(to, str(settings["keyCommand"]))
                        elif cmd == "runtime":
                            timeNow = time.time()
                            runtime = timeNow - botStart
                            runtime = format_timespan(runtime)
                            resetTime = timeNow - int(settings["timeRestart"])
                            resetTime = format_timespan(resetTime)
                            client.sendMessage(to, "Bot sudah berjalan selama {}. Bot akan refresh otomatis pada {}".format(str(runtime), str(resetTime)))
                        elif cmd == "time":
                            client.sendMessage(to, "cek sendiri di tanggal")
                        elif "/ti/g/" in msg.text.lower():
                            if settings["autoJoinTicket"] == True:
                                link_re = re.compile('(?:line\:\/|line\.me\/R)\/ti\/g\/([a-zA-Z0-9_-]+)?')
                                links = link_re.findall(text)
                                n_links = []
                                for l in links:
                                    if l not in n_links:
                                        n_links.append(l)
                                for ticket_id in n_links:
                                    group = client.findGroupByTicket(ticket_id)
                                    client.acceptGroupInvitationByTicket(group.id,ticket_id)
                                    client.sendMessage(to, "Berhasil masuk ke group %s" % str(group.name))
                        # Check viewers command
                        elif cmd == "cctv on":
                            tz = pytz.timezone("Asia/Jakarta")
                            timeNow = datetime.now(tz=tz)
                            day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday","Friday", "Saturday"]
                            hari = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
                            bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
                            hr = timeNow.strftime("%A")
                            bln = timeNow.strftime("%m")
                            for i in range(len(day)):
                                if hr == day[i]: hasil = hari[i]
                            for k in range(0, len(bulan)):
                                if bln == str(k): bln = bulan[k-1]
                            readTime = hasil + ", " + timeNow.strftime('%d') + " - " + bln + " - " + timeNow.strftime('%Y') + "\nJam : [ " + timeNow.strftime('%H:%M:%S') + " ]"
                            if to in read["readPoint"]:
                                client.sendMessage(to, "Cctv sudah aktif ketik {}Cctv result untuk menampilkan hasil".format(str(settings["keyCommand"])))
                            else:
                                try:
                                    read["readPoint"][to] = True
                                    read["readMember"][to] = {}
                                    read["readTime"][to] = readTime
                                    read["ROM"][to] = {}
                                except:
                                    pass
                                client.sendMessage(to, "Cctv diaktifkan ketik {}Cctv")
                        elif cmd == "cctv off":
                            if to in read["readPoint"]:
                                try:
                                    del read["readPoint"][to]
                                    del read["readMember"][to]
                                    del read["readTime"][to]
                                    del read["ROM"][to]
                                    client.sendMessage(to, "Berhasil matikan cctv")
                                except:
                                    pass
                            else:
                                client.sendMessage(to, "Cctv belum diaktifkan ngapain di matikan?")
                        elif cmd == "cctv reset":
                            tz = pytz.timezone("Asia/Jakarta")
                            timeNow = datetime.now(tz=tz)
                            day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday","Friday", "Saturday"]
                            hari = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
                            bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
                            hr = timeNow.strftime("%A")
                            bln = timeNow.strftime("%m")
                            for i in range(len(day)):
                                if hr == day[i]: hasil = hari[i]
                            for k in range(0, len(bulan)):
                                if bln == str(k): bln = bulan[k-1]
                            readTime = hasil + ", " + timeNow.strftime('%d') + " - " + bln + " - " + timeNow.strftime('%Y') + "\nJam : [ " + timeNow.strftime('%H:%M:%S') + " ]"
                            if to in read["readPoint"]:
                                try:
                                    read["readPoint"][to] = True
                                    read["readMember"][to] = {}
                                    read["readTime"][to] = readTime
                                    read["ROM"][to] = {}
                                except:
                                    pass
                                client.sendMessage(to, "Cctv di reset")
                            else:
                                client.sendMessage(to, "Cctv belum diaktifkan?")
                        elif cmd == "cctv result":
                            if to not in read["readPoint"]:
                                client.sendMessage(to, "Cctv belum diaktifkan")
                            else:
                                ret_ = "╔══[ Reader ]"
                                reader = {}
                                reader["name"] = ""
                                if read["readMember"][to] == {}:
                                    reader["name"] += "\n╠ Belum ada yang membaca chat"
                                else:
                                    for a in read["readMember"][to]:
                                        reader["name"] += "\n╠ {}".format(str(read["readMember"][to][a]))
                                time_ = read["readTime"][to]
                                ret_ += reader["name"]
                                ret_ += "\n╠══[ Siders ]"
                                sider = {}
                                sider["name"] = ""
                                if read["ROM"][to] == {} and read["readMember"][to] != {}:
                                    for ar in read["readMember"][to]:
                                        contact = client.getContact(ar)
                                        sider["name"] += "\n╠ {}".format(str(contact.displayName))
                                elif read["ROM"][to] == {} and read["readMember"][to] == {}:
                                    pass
                                else:
                                    for ars in read["readMember"][to]:
                                        if ars not in read["ROM"][to]:
                                            contact = client.getContact(ars)
                                            sider["name"] += "\n╠ {}".format(str(contact.displayName))
                                tota = len(read["readMember"][to]) - len(read["ROM"][to])
                                totb = len(read["readMember"][to])
                                ret_ += sider["name"]
                                ret_ += "\n╚══[ Total {} Siders From {} Viewers ]".format(str(tota), str(totb))
                                ret_ += "\nPoint Set On : \n{}".format(str(time_))
                                client.sendMessage(to, str(ret_))
                        # Example remote command
                        elif cmd == "autoread on":
                            settings["autoRead"] = True
                            client.sendMessage(to, "Berhasil mengaktifkan auto read")
                        elif cmd == "autoread off":
                            settings["autoRead"] = False
                            client.sendMessage(to, "Berhasil menonaktifkan auto read")
                        # Bonus fun command
                        elif cmd.startswith("searchimage "):
                            start = time.time()
                            sep = msg.text.split(" ")
                            search = msg.text.replace(sep[0] + " ","")
                            url = "https://api.xeonwz.ga/api/image/google?q=" + urllib.parse.quote(search)
                            with requests.session() as web:
                                web.headers["User-Agent"] = random.choice(settings["userAgent"])
                                r = web.get(url)
                                data = r.text
                                data = json.loads(data)
                                if data["data"] != []:
                                    items = data["data"]
                                    path = random.choice(items)
                                    a = items.index(path)
                                    b = len(items)
                                    if settings["server"] == "VPS":
                                        client.sendImageWithURL(to, str(path))
                                    else:
                                        urllib.urlretrieve(path, "imgresult.jpg")
                                        client.sendImage(to, "imgresult.jpg")
                                    elapsed_time = time.time() - start
                                    client.sendMessage(msg.to, "[Image Result]\nImage #%s from #%s\nURL : %s\nDuration : %s" %(str(a),str(b),str(path),str(elapsed_time)))
                                else:
                                    client.sendMessage(msg.to, "[Image Result] Error : Image not found")
                        elif cmd == "liststicker":
                            with open('sticker.json','r') as fp:
                                stickers = json.load(fp)
                            ret_ = "╔══[ List Sticker ]"
                            for sticker in stickers:
                                ret_ += "\n╠ " + sticker.title()
                            ret_ += "\n╚══[ Total {} Stickers ]".format(str(len(stickers)))
                            client.sendMessage(to, ret_)
                        elif cmd.startswith("spamsticker "):
                            sep = text.split(" ")
                            text = text.replace(sep[0] + " ","")
                            cond = text.split(" ")
                            jml = int(cond[0])
                            stickername = str(cond[1]).lower()
                            with open('sticker.json','r') as fp:
                                stickers = json.load(fp)
                            if stickername in stickers:
                                sid = stickers[stickername]["STKID"]
                                spkg = stickers[stickername]["STKPKGID"]
                            else:
                                return
                            for x in range(jml):
                                client.sendSticker(to, spkg, sid)
                        elif cmd.startswith("checkpraytime "):
                            sep = text.split(" ")
                            location = text.replace(sep[0] + " ","")
                            with requests.session() as web:
                                web.headers["user-agent"] = random.choice(settings["userAgent"])
                                r = web.get("http://api.corrykalam.net/apisholat.php?lokasi={}".format(urllib.parse.quote(location)))
                                data = r.text
                                data = json.loads(data)
                                if data[1] != "Subuh : " and data[2] != "Dzuhur : " and data[3] != "Ashr : " and data[4] != "Maghrib : " and data[5] != "Isha : ":
                                    ret_ = "╔══[ Prayer Schedule ]"
                                    ret_ += "\n╠ Lokasi : " + data[0]
                                    ret_ += "\n╠ " + data[1]
                                    ret_ += "\n╠ " + data[2]
                                    ret_ += "\n╠ " + data[3]
                                    ret_ += "\n╠ " + data[4]
                                    ret_ += "\n╠ " + data[5]
                                    ret_ += "\n╚══[ Complete ]"
                                else:
                                    ret_ = "[ Prayer Schedule ] Error : Lokasi tidak ditemukan" 
                                client.sendMessage(to, str(ret_))
                        elif cmd.startswith("checkweather "):
                            sep = text.split(" ")
                            location = text.replace(sep[0] + " ","")
                            with requests.session() as web:
                                web.headers["user-agent"] = random.choice(settings["userAgent"])
                                r = web.get("http://api.corrykalam.net/apicuaca.php?kota={}".format(urllib.parse.quote(location)))
                                data = r.text
                                data = json.loads(data)
                                if "result" not in data:
                                    ret_ = "╔══[ Weather Status ]"
                                    ret_ += "\n╠ Lokasi : " + data[0].replace("Temperatur di kota ","")
                                    ret_ += "\n╠ Suhu : " + data[1].replace("Suhu : ","")
                                    ret_ += "\n╠ Kelembaban : " + data[2].replace("Kelembaban : ","")
                                    ret_ += "\n╠ Tekanan Udara : " + data[3].replace("Tekanan udara : ","")
                                    ret_ += "\n╠ Kecepatan Angin : " + data[4].replace("Kecepatan angin : ","")
                                    ret_ += "\n╚══[ Complete ]"
                                else:
                                    ret_ = "[ Weather Status ] Error : Lokasi tidak ditemukan"
                                client.sendMessage(to, str(ret_))
                        elif cmd.startswith("checklocation "):
                            sep = text.split(" ")
                            location = text.replace(sep[0] + " ","")
                            with requests.session() as web:
                                web.headers["user-agent"] = random.choice(settings["userAgent"])
                                r = web.get("http://api.corrykalam.net/apiloc.php?lokasi={}".format(urllib.parse.quote(location)))
                                data = r.text
                                data = json.loads(data)
                                if data[0] != "" and data[1] != "" and data[2] != "":
                                    link = "https://www.google.co.id/maps/@{},{},15z".format(str(data[1]), str(data[2]))
                                    ret_ = "╔══[ Details Location ]"
                                    ret_ += "\n╠ Lokasi : " + data[0]
                                    ret_ += "\n╠ Google Maps : " + link
                                    ret_ += "\n╚══[ Complete ]"
                                else:
                                    ret_ = "[ Details Location ] Error : Lokasi tidak ditemukan"
                                client.sendMessage(to,str(ret_))
                # Check if only image
                elif msg.contentType == 1:
                    if settings["changePicture"] == True:
                        path = client.downloadObjectMsg(msg_id)
                        settings["changePicture"] = False
                        client.updateProfilePicture(path)
                        client.sendMessage(to, "Berhasil mengubah foto profile")
                    if msg.toType == 2:
                        if to in settings["changeGroupPicture"]:
                            path = client.downloadObjectMsg(msg_id)
                            settings["changeGroupPicture"].remove(to)
                            client.updateGroupPicture(to, path)
                            client.sendMessage(to, "Berhasil mengubah foto group")

        if op.type == 26:
            print ("[ 26 ] RECEIVE MESSAGE")
            msg = op.message
            text = msg.text
            msg_id = msg.id
            receiver = msg.to
            sender = msg._from
            if msg.toType == 0 or msg.toType == 2:
                if msg.toType == 0:
                    to = sender
                elif msg.toType == 2:
                    to = receiver
                if settings["autoRead"] == True:
                    client.sendChatChecked(to, msg_id)
                if to in read["readPoint"]:
                    if sender not in read["ROM"][to]:
                        read["ROM"][to][sender] = True

        if op.type == 55:
            print ("[ 55 ] NOTIFIED READ MESSAGE")
            if op.param1 in read["readPoint"]:
                _name = client.getContact(op.param2).displayName
                tz = pytz.timezone("Asia/Jakarta")
                timeNow = datetime.now(tz=tz)
                timeHours = datetime.strftime(timeNow," (%H:%M)")
                read["readMember"][op.param1][op.param2] = str(_name) + str(timeHours)
        backupData()
    except Exception as error:
        logError(error)
while True:
    try:
        autoRestart()
        ops = clientPoll.singleTrace(count=50)
        if ops is not None:
            for op in ops:
                clientBot(op)
                # Don't remove this line, if you wan't get error soon!
                clientPoll.setRevision(op.revision)
    except Exception as e:
        logError(e)
