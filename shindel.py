import os
from flask import Blueprint, send_file, make_response, request, session, render_template, redirect, url_for, abort
import json
from helper import from_log,update_log,sessionvalidated,next_element,del_log,update_element_using_index,formattime
import json
import base64
from datetime import datetime, date
import csv

ui = Blueprint('ui', __name__, url_prefix='/ui')

@ui.route('/login',methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        important = json.load(open("important.json"))
        if username == important["shindelUsername"] and password == important["shindelPassword"]:
            session["loggedIn"] = True
        else: 
            session["loggedIn"] = False
        return redirect(url_for("ui.home"))
    elif request.method  == "GET":
        if "loggedIn" in session and session["loggedIn"] == True:
            return redirect(url_for("ui.home"))
        else:
            return render_template("login.html")

@ui.route('/')
@sessionvalidated
def home():
    return render_template("main.html")

@ui.route('/<lang>/announcements',methods=["GET"])
@sessionvalidated
def announcements(lang):
    page=int(request.args.get('page',0))
    announcementlog=json.loads(from_log('data/'+lang+'/announcements',0,'end'))['data']
    if page <= 0:
        page = 0
    elif page > (len(announcementlog)-1) // 5:
        page = (len(announcementlog)-1)//5
    return render_template('announcements.html',page=page,names=announcementlog[page*5:page*5+5],lang=lang)

@ui.route('/<lang>/announcements/add',methods=["POST"])
@sessionvalidated
def addannounce(lang):
    page=int(request.args.get('page',0))
    name = next_element(lang,'announcements')
    requestform = request.form.to_dict()
    currenttime = datetime.now()
    requestform['date'] = "{}/{}/{}".format(currenttime.month,currenttime.day,currenttime.year)
    requestform['time'] = formattime(currenttime)
    content = json.dumps(requestform)
    with open('data/'+lang+'/announcements/'+name,'w') as f:
        f.write(content)
    update_log('data/'+lang+'/announcements',name)
    return redirect(url_for('ui.announcements',lang=lang,page=page))

@ui.route('/<lang>/announcements/del',methods=["POST"])
@sessionvalidated
def delannounce(lang):
    announcement=json.loads(from_log('data/'+lang+'/announcements',0,'end'))['data'][int(request.form['num'])]
    if str(announcement) == str(request.form['value']):
        del_log('data/'+lang+'/announcements',int(request.form['num']))
        return redirect(url_for("ui.announcements",lang=lang))
    else:
        return "Please do not use this API incorrectly"

@ui.route('/<lang>/announcements/update',methods=["POST"])
@sessionvalidated
def updannounce(lang):
    clone = request.form.to_dict()
    num = int(clone['num'])
    del clone['num']
    update_element_using_index('data/'+lang+'/announcements',num,clone)
    return redirect(url_for("ui.announcements",lang=lang))

@ui.route('/<lang>/announcements/import',methods=["POST"])
@sessionvalidated
def importannounce(lang):
    page=int(request.args.get('page',0))
    f = request.files['data']
    f.save('uploads/announcements.csv')
    with open('data/'+lang+'/announcements/timelog.txt') as f:
        line = f.readline()
        if len(line) > 0:
            firstTime = datetime.strptime(line,'%m/%d/%Y %H:%M:%S')
        else:
            firstTime = datetime.min
    with open('uploads/announcements.csv') as f:
        data = list(csv.reader(f,delimiter=","))[1:]
    for line in data:
        nextFileName = next_element(lang,'announcements')
        content = {'message':line[1],'teacher':line[2]}
        currenttime = datetime.strptime(line[0],'%m/%d/%Y %H:%M:%S')
        if currenttime <= firstTime:
            continue
        content['date'] = "{}/{}/{}".format(currenttime.month,currenttime.day,currenttime.year)
        content['time'] = formattime(currenttime)
        with open('data/'+lang+'/announcements/'+nextFileName,"w") as f:
            json.dump(content,f)
        update_log('data/'+lang+'/announcements',nextFileName)
    with open('data/'+lang+'/announcements/timelog.txt', "w") as timelog:
        timelog.write(data[-1][0])
    return redirect(url_for('ui.announcements',lang=lang,page=page))

@ui.route('/<lang>/events')
@sessionvalidated
def events(lang):
    page=int(request.args.get('page',0))
    eventlog=json.loads(from_log('data/'+lang+'/events',0,'end'))['data']
    if page <= 0:
        page = 0
    elif page > (len(eventlog)-1) // 5:
        page = (len(eventlog)-1)//5
    return render_template('events.html',events=eventlog[page*5:page*5+5],lang=lang,page=page)

@ui.route('/<lang>/events/add',methods=["POST"])
@sessionvalidated
def addevent(lang):
    name = next_element(lang,'events')
    content = json.dumps(request.form.to_dict())
    with open('data/'+lang+'/events/'+name,'w') as f:
        f.write(content)
    update_log('data/'+lang+'/events',name)
    page=int(request.args.get('page',0))
    return redirect(url_for('ui.events',lang=lang,page=page))

@ui.route('/<lang>/events/del',methods=["POST"])
@sessionvalidated
def delevent(lang):
    event=json.loads(from_log('data/'+lang+'/events',0,'end'))['data'][int(request.form['num'])]
    if str(event) == str(request.form['value']):
        del_log('data/'+lang+'/events',int(request.form['num']))
        return redirect(url_for("ui.events",lang=lang))
    else:
        return "Please do not use this API incorrectly"

@ui.route('/<lang>/events/update',methods=["POST"])
@sessionvalidated
def updevent(lang):
    clone = request.form.to_dict();
    num = int(clone['num'])
    del clone['num']
    update_element_using_index('data/'+lang+'/events',num,clone)
    return redirect(url_for("ui.events",lang=lang))

@ui.route('/<lang>/new',methods=["GET"])
@sessionvalidated
def new(lang):
    page=int(request.args.get('page',0))
    newlog=json.loads(from_log('data/'+lang+'/new',0,'end'))['data']
    if page <= 0:
        page = 0
    elif page > (len(newlog)-1) // 5:
        page = (len(newlog)-1)//5
    return render_template('new.html',news=newlog[page*5:page*5+5],page=page,lang=lang)
    
@ui.route('<lang>/new/add',methods=["POST"])
@sessionvalidated
def addnew(lang):
    name = next_element(lang,'new')
    content = {
        'icon':base64.b64encode(request.files['icon'].read()).decode(),
        'name':request.form['name'],
        'date':request.form['date']
    }
    with open('data/'+lang+'/new/'+name,'w') as f:
        f.write(json.dumps(content))
    update_log('data/'+lang+'/new',name)
    return redirect(url_for('ui.new',lang=lang))

@ui.route('/<lang>/new/del',methods=["POST"])
@sessionvalidated
def delnew(lang):
    newitem=json.loads(from_log('data/'+lang+'/new',0,'end'))['data'][int(request.form['num'])]
    if str(newitem) == str(request.form['value']):
        del_log('data/'+lang+'/new',int(request.form['num']))
        return redirect(url_for('ui.new',lang=lang))
    else:
        return "Please do not use this API incorrectly"

@ui.route('<lang>/new/update',methods=["POST"])
@sessionvalidated
def updnew(lang):
    clone = request.form.to_dict();
    num = int(clone['num'])
    del clone['num']
    clone['icon'] = base64.b64encode(request.files['icon'].read()).decode()
    update_element_using_index('data/'+lang+'/new',num,clone)
    return redirect(url_for("ui.new",lang=lang))

@ui.route('<lang>/clubs')
@sessionvalidated
def clubs(lang):
    with open('data/'+lang+'/clubs.json') as f:
        clubdata = json.load(f)['clubs']
    return render_template('clubs.html',clubs=clubdata,lang=lang)

@ui.route('<lang>/clubs/add',methods=["POST"])
@sessionvalidated
def addclub(lang):
    with open('data/'+lang+'/clubs.json') as f:
        clubdata = json.load(f)['clubs']
    clubdata.append(request.form.to_dict())
    clubdata=sorted(clubdata,key=lambda x:x['name'])
    with open('data/'+lang+'/clubs.json','w') as f:
        json.dump({'clubs':clubdata},f)
    return redirect(url_for('ui.clubs',lang=lang))

@ui.route('<lang>/clubs/del',methods=["POST"])
@sessionvalidated
def delclub(lang):
    index=int(request.form['index'])
    clubname=request.form['club']
    with open('data/'+lang+'/clubs.json') as f:
        clubdata = json.load(f)['clubs']
    if str(clubdata[index]) == str(clubname):
        del clubdata[index]
    with open('data/'+lang+'/clubs.json','w') as f:
        json.dump({'clubs':clubdata},f)
    return redirect(url_for('ui.clubs',lang=lang))

@ui.route('<lang>/sslOps')
@sessionvalidated
def sslOps(lang):
    with open('data/'+lang+'/sslOps.json') as f:
        opdata = json.load(f)['ops']
    return render_template('sslOps.html',ops=opdata,lang=lang)

@ui.route('<lang>/sslOps/add',methods=["POST"])
@sessionvalidated
def addSslOp(lang):
    with open('data/'+lang+'/sslOps.json') as f:
        opdata = json.load(f)['ops']
    opdata.insert(0,request.form.to_dict())
    with open('data/'+lang+'/sslOps.json','w') as f:
        json.dump({'ops':opdata},f)
    return redirect(url_for('ui.sslOps',lang=lang))

@ui.route('<lang>/sslOps/del',methods=["POST"])
@sessionvalidated
def delSslOp(lang):
    index=int(request.form['index'])
    op=request.form['op']
    with open('data/'+lang+'/sslOps.json') as f:
        opdata = json.load(f)['ops']
    if str(opdata[index]) == str(op):
        del opdata[index]
    with open('data/'+lang+'/sslOps.json','w') as f:
        json.dump({'ops':opdata},f)
    return redirect(url_for('ui.sslOps',lang=lang))

@ui.route('<lang>/lunchEvents')
@sessionvalidated
def lunchevents(lang):
    with open('data/'+lang+'/lunchEvents.json') as f:
        lunchdata = json.load(f)
    return render_template('lunchEvents.html',lang=lang,events=lunchdata)

@ui.route('<lang>/lunchEvents/add',methods=["POST"])
@sessionvalidated
def addlunchevent(lang):
    with open('data/'+lang+'/lunchEvents.json') as f:
        lunchdata = json.load(f)
    lunchdata.insert(0,request.form.to_dict())
    with open('data/'+lang+'/lunchEvents.json','w') as f:
        json.dump(lunchdata,f)
    return redirect(url_for('ui.lunchevents',lang=lang))

@ui.route('<lang>/teachers')
@sessionvalidated
def teachers(lang):
    teacherdata=json.loads(from_log('data/'+lang+'/teachers',0,'end'))['data']
    return render_template('teachers.html',lang=lang,teachers=teacherdata)

@ui.route('<lang>/teachers/add',methods=["POST"])
@sessionvalidated
def addteacher(lang):
    formdict = request.form.to_dict(flat=False)
    content = {'name':formdict['name'][0],'emails':formdict['emails']}
    name = next_element(lang,'teachers')
    with open('data/'+lang+'/teachers/'+name,'w') as f:
        f.write(json.dumps(content))
    update_log('data/'+lang+'/teachers',name)
    return redirect(url_for('ui.teachers',lang=lang))

@ui.route('<lang>/teachers/del',methods=["POST"])
@sessionvalidated
def delteacher(lang):
    newitem=json.loads(from_log('data/'+lang+'/teachers',0,'end'))['data'][int(request.form['num'])]
    if str(newitem) == str(request.form['value']):
        del_log('data/'+lang+'/teachers',int(request.form['num']))
        return redirect(url_for('ui.teachers',lang=lang))
    else:
        return "Please do not use this API incorrectly"

@ui.route('<lang>/teachers/update',methods=["POST"])
@sessionvalidated
def updteacher(lang):
    clone = request.form.to_dict(flat=False);
    num = int(clone['num'][0])
    clone['name']=clone['name'][0]
    del clone['num']
    update_element_using_index('data/'+lang+'/teachers',num,clone)
    return redirect(url_for("ui.teachers",lang=lang))
