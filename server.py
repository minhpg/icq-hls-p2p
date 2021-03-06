from flask import Blueprint, Flask,redirect, session, g, render_template, url_for,request, send_from_directory  ,Response #imports
import requests
import os
import sys
from flask_celery import make_celery
from flask_pymongo import PyMongo
import random
from random import choice,randint
import time
import datetime 
from multiprocessing.pool import ThreadPool
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import GoogleDriveFile
from os import path
from uuid import uuid4
import uuid
import hashlib
import io
import json
from bson.objectid import ObjectId
from bot.bot import Bot
from tqdm import tqdm
import base64
import urllib
import shutil


def getid(link):
    id = link.replace("https://drive.google.com","").replace("/file/d/","").replace("open?id=","").replace("/view","").replace("/edit","").replace("?usp=sharing","")
    return id

def create_credential():
    from GoogleAuthV1 import auth_and_save_credential
    auth_and_save_credential()


# Authentication + token creation
def create_drive_manager():
    gAuth = GoogleAuth()
    typeOfAuth = None
    if not path.exists("credentials.txt"):
        typeOfAuth = input("type save if you want to keep a credential file, else type nothing")
    bool = True if typeOfAuth == "save" or path.exists("credentials.txt") else False
    authorize_from_credential(gAuth, bool)
    drive: GoogleDrive = GoogleDrive(gAuth)
    return drive


def authorize_from_credential(gAuth, isSaved):
    if not isSaved: #no credential.txt wanted
        from GoogleAuthV1 import auth_no_save
        auth_no_save(gAuth)
    if isSaved and not path.exists("credentials.txt"):
        create_credential()
        gAuth.LoadCredentialsFile("credentials.txt")
    if isSaved and gAuth.access_token_expired:
        gAuth.LoadCredentialsFile("credentials.txt")
        gAuth.Refresh()
        print("token refreshed!")
        gAuth.SaveCredentialsFile("credentials.txt")
    gAuth.Authorize()
    print("authorized access to google drive API!")
    
def MediaToBaseDownloader(fileid):
    file = driver.CreateFile({"id":fileid})
    local_fd = open(fileid,"wb")
    request = driver.auth.service.files().get_media(fileId=fileid)
    media_request = http.MediaIoBaseDownload(local_fd, request)
    while True:
        try:
            download_progress, done = media_request.next_chunk()
        except errors.HttpError as error:
            print ('An error occurred: %s' % error)
            return None
        if download_progress:
            print ('Download Progress: %d%%' % int(download_progress.progress() * 100))
        if done:
            print ('Download Complete')
            return fileid

def getuploadbucket(file):
    TOKEN= ["001.1115661691.2258642599:755801211","001.1032535767.3154515394:755824209","001.0427632945.3959524149:755788118","001.1706165490.2035534611:754584161","001.1263987544.3387987021:754638082","001.2157201741.4154929238:754657309"]
    aimsid=choice(TOKEN)
    size = str(os.stat(file).st_size)
    response = requests.get("https://u.icq.net/api/v14/files/init?aimsid="+aimsid+"&ts="+str(time.time)+"&size="+size+"&filename="+os.path.basename(file)+"&client=icq")
    return("https://"+response.json()["result"]["host"]+response.json()["result"]["url"]+"?aimsid="+aimsid)

def read_in_chunks(file_object, chunk_size=1048576):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def split(path):
    if not os.path.isdir(path.strip(".mp4")):
        os.mkdir(path.strip(".mp4"))
    os.system("ffmpeg -i "+path+" -codec: copy -start_number 0 -hls_time 10 -hls_list_size 0 -hls_segment_filename "+path.strip(".mp4")+"/chunk_%03d.html "+path.strip(".mp4")+".m3u8")

def createplaylist(fileid,i):
        url = upload_icq("./"+fileid+"/"+i)
        os.remove("./"+fileid+"/"+i)
        return [i,"/proxy?id="+url]
        
def process(i):
    value = createplaylist(i[0],i[1])
    open("./"+i[0]+"/"+i[1],"w").write(value[1])

def upload(path):
    TOKEN= ["001.1706165490.2035534611:754584161","001.1263987544.3387987021:754638082","001.2157201741.4154929238:754657309"] #yourtokenhere    
    bot=Bot(token=random.choice(TOKEN))
    chats=["AoLF1ZUEDaObf4npLlU"]
    for chat in chats:
        while True:
            try:
                a = bot.send_file(chat_id=chat,file=open(path,"rb"))
                response = a.json()
                if not "fileId" in response:
                    continue
                else:
                    print(response["fileId"])
                    return response["fileId"]
            except:
                return None

def playlist(path):
    try:
        files = os.listdir(path.strip(".mp4"))
        tslist = open(path.strip(".mp4")+".m3u8","r").readlines()
        converted_list = []
        for element in tslist:
            converted_list.append(element.strip())
        print(converted_list)
        tslist = converted_list
        newfile = []
        for i in files:
            newfile.append([path.strip(".mp4"),i])
        files = newfile
        p = ThreadPool(10)
        p.map(process,files)
        p.close()
        for i in files:
            tslist = [sub.replace(i[1], open("./"+path.strip(".mp4")+"/"+i[1],"r").readlines()[0]) for sub in tslist] 
        playlist = "$".join(tslist)
        return playlist
    except Exception as e:
        print(e)
        files = os.listdir(path.strip(".mp4"))
        for i in files:
            os.remove("./"+path.strip(".mp4")+"/"+i)
        os.rmdir(path.strip(".mp4"))
        return None
    
def transcode_upload(file):
    split(file)
    data = playlist(file)
    print(data)
    return data

def upload_icq(file):
    url = getuploadbucket(file)
    content_name = str(file)
    content_path = os.path.abspath(file)
    content_size = str(os.stat(content_path).st_size)
    print ("Path: "+content_path,"Size: "+ str(round(int(content_size)/1000000,1))+" MB")
    f = open(content_path,"rb")
    index = 0
    offset = 0
    headers = {}
    list = []
    for chunk in read_in_chunks(f):
        offset = index + len(chunk)
        headers['Content-Length'] = str(len(chunk))
        headers['Content-Range'] = 'bytes %s-%s/%s' % (index, offset-1, content_size)
        headers['Content-Disposition'] = 'attachment; filename="'+os.path.basename(file)+'"'
        list.append({
            "range":headers['Content-Range'],
            "disposition": headers['Content-Disposition'],
            "length": str(len(chunk)),
            "chunk":chunk,
            "url":url
        })
        index = offset
    p=ThreadPool(20)
    p.map(uploadicq,list[0:len(list)-1])
    p.close()
    p.join()
    icqid = uploadicq(list[-1],True)
    return icqid

def uploadicq(dict,lastchunk=False):
    url = dict["url"]
    chunk = dict["chunk"]
    headers = {
    'Content-Range': dict["range"],
    'Content-Length': dict["length"],
    'DNT': '1',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Disposition': dict["disposition"],
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
    'Content-Type': 'application/octet-stream',
    'Accept': '*/*'
    }
    while True:
        try:
            r = requests.post(url, data=chunk, headers=headers)
            if lastchunk==True:
                print ("File: /get?id="+r.json()["result"]["fileid"])
                break
            elif not "fileid" in r.json()["result"]:
                print(headers["Content-Range"])
                break
        except Exception as e:
            continue
    if lastchunk==True:
        return r.json()["result"]["fileid"]

def download_file_hydrax(url,slug,dst):
    if not os.path.isfile(dst):   # Streaming, so we can iterate over the response.
        response =requests.get(url,headers={"Referer":"https://playhydrax.com/?v="+slug}, stream=True,verify=False)
        total_size_in_bytes= int(response.headers.get('content-length', 0))
        block_size = 1024*1024
        progress_bar = tqdm(total=total_size_in_bytes, unit='B', unit_scale=True)
        with open(dst, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        return total_size_in_bytes
    else:
        return os.stat(dst).st_size

def hydrax_extract(slug):
    try:
        metadata = hydrax_check(slug)
        if metadata:
            if metadata["status"] == False:
                return None
            else:
                headers = {}
                baseurl = get_url(metadata["url"])
                if "hd" in metadata["sources"]:
                    headers["hd"] = "https://www."+baseurl
                if "sd" in metadata["sources"]:
                    headers["sd"] = "https://"+baseurl    
                headers["slug"] = slug
                headers["baseurl"] = baseurl
                return headers
        else:
            return None
    except:
        return None

def get_proxies():
    response = requests.get("")
    print(response.json())
    list_proxies = response.json()
    return(choice(list_proxies).split(";"))

def hydrax_check(slug):
    proxy = get_proxies()
    proxy = "http://"+proxy[1]+":"+proxy[2]+"@"+proxy[0]
    print(proxy)
    proxies ={
            "http": proxy,
    "https": proxy
    }
    response = requests.post("https://ping.iamcdn.net/",data={"slug":slug},proxies=proxies)
    try:
        word = response.json()
        return word
    except:
        return {"status":True,"url":"DRtMDY0MHNiYy5tb25zdGVyN",'sources': ['sd', 'hd']}

def get_url(word):
    url_decode= word[-1]+word[:-1]
    baseurl = str(base64.b64decode(url_decode).decode("utf-8"))
    return baseurl

def hydrax_api(slug,sd=True,hd=True):
    metadata = hydrax_extract(slug)
    print(metadata)
    if metadata:
        qualities = []
        dst = slug+"_sd.mp4"
        status = download_check_integrity("https://www."+metadata["baseurl"],slug,dst)
        return dst
    else:
        return None

def upload_api(quality):
    id = transcode_upload(quality)
    return id
 
def download_check_integrity(url,slug,dst):
    while True:
        file_size = download_file_hydrax(url,slug,dst)
        return True
      


def remote_hydrax(fileid):
    proxy = get_proxies()
    proxy = "http://"+proxy[1]+":"+proxy[2]+"@"+proxy[0]
    print(proxy)
    proxies ={
            "http": proxy,
    "https": proxy
    }
    response = requests.get("https://api.hydrax.net/e4ebc346d651c655442b3461ef48d8eb/drive/"+fileid,proxies=proxies)
    print(response.text)
    try:
        return response.json()
    except:
        return None
    

def generate(link):
    if link == None:
        return None
    s = link.replace("https://drive.google.com","").replace("/file/d/","").replace("open?id=","").replace("/view","").replace("/edit","").replace("?usp=sharing","").replace(" ","").replace("\n","")
    drive = s[::-1]
    cdn = "https://hls.kyunkyun.net/stream?id="+drive
    return cdn+"\n"

main = Flask(__name__) #setup vaariables
main.config["MONGO_URI"] = 
main.config["CELERY_RESULT_BACKEND"] = 
main.config["CELERY_BROKER_URL"]="amqp://localhost//"
main.config["SECRET_KEY"] = 
method_requests_mapping = {
    'GET': requests.get,
    'HEAD': requests.head,
    'POST': requests.post,
    'PUT': requests.put,
    'DELETE': requests.delete,
    'PATCH': requests.patch,
    'OPTIONS': requests.options,
}
#inits

celery = make_celery(main)
mongo = PyMongo()
mongo.init_app(main)
video_db = mongo.db.hls
user_collection = mongo.db.users
driver=create_drive_manager()


@celery.task(name="hydrax") #celery implementation for queueing
def hydrax(fileid):
    try:
        video_db = mongo.db.hls
        slug = remote_hydrax(fileid)
        if "slug" in slug.keys():
            slug=slug["slug"]
        else:
            myquery = video_db.find_one({"drive":str(fileid)})
            video_db.delete_one(myquery)
            return "Processing"
        if slug:
            try:
                qualities = hydrax_api(slug)
                id = upload_api(qualities)
                if id:
                    name = driver.CreateFile({"id":fileid})["title"]
                    myquery ={"drive":str(fileid)}
                    newvalues = { "$set": {"playlist":id}}
                    video_db.update_one(myquery,newvalues)
                    os.system("sudo rm -r "+slug+"*")
                    return "Successful"
                else:
                    os.system("sudo rm -r "+slug+"*")
                    myquery = video_db.find_one({"drive":str(fileid)})
                    video_db.delete_one(myquery)
                    return "Unsuccessful"

            except:
                os.system("sudo rm -r "+slug+"*")
                myquery = video_db.find_one({"drive":str(fileid)})
                video_db.delete_one(myquery)
                return "Unsuccessful"

        else:
            myquery = video_db.find_one({"drive":str(fileid)})
            video_db.delete_one(myquery)
            return "Unsuccessful"
    except:
        myquery = video_db.find_one({"drive":str(fileid)})
        video_db.delete_one(myquery)
        return "Unsuccessful"

@main.route("/api") #main engine
def hydraxgate():
    video_db = mongo.db.hls
    if request.args:
        args = request.args
        fileid = args.get("drive").replace("https://drive.google.com","").replace("/file/d/","").replace("open?id=","").replace("/view","").replace("/edit","").replace("?usp=sharing","")
        check = video_db.find_one({"drive":str(fileid)})
        if check:
            encrypt =str(check["_id"])
            if "playlist" in check.keys():
                dict ={"status":"done","embed": "https://hls.kyunkyun.net/?v="+str(encrypt),"playlist":"https://hls.kyunkyun.net/playlist/"+str(encrypt)+".m3u8"}
            else:
                dict ={"status":"processing","embed": "https://hls.kyunkyun.net/?v="+str(encrypt)}
            return json.dumps(dict)
        else:
            video_db.insert_one({"drive":fileid,"key":"kyunkyun"})
            encrypt = video_db.find_one({"drive":str(fileid)})["_id"]
            hydrax.delay(fileid)
            dict ={"status":"processing","embed": "https://hls.kyunkyun.net/?v="+str(encrypt)}
            return json.dumps(dict)
    else:
        return json.dumps({"status":"unavailable"}),404

@main.route("/")
def hlsstream():
    video_db = mongo.db.hls
    if request.args:
        args = request.args
        drive= args.get("v")
        direct= args.get("direct")
        query = video_db.find_one({"_id":ObjectId(drive)})
        if query:
            if "playlist" in query.keys():
                return render_template("p2p.html",hd = "/playlist/"+drive+".m3u8", type="application/x-mpegURL")
            else:
                return json.dumps({"status":"processing"})
        else:
            return json.dumps({"status":"unavailable"}),404
    else:
        return json.dumps({"status":"unavailable"}),404

@main.route("/playlist")
def getPlaylist():
    video_db = mongo.db.hls
    if request.args:
        args = request.args
        drive= args.get("id")
        query = video_db.find_one({"_id":ObjectId(drive)})
        if query:
            if "playlist" in query.keys():
                query = query["playlist"]
                return query.replace("$","\n")
            else:
                return json.dumps({"status":"processing"})
        else:
            return json.dumps({"status":"unavailable"}),404
    else:
        return json.dumps({"status":"unavailable"}),404

def getStreamUrl(fileid):
    TOKEN = "001.3617003158.0151996798:754693810"
    bot = Bot(token=TOKEN)
    while True:
        try:
            response = bot.get_file_info(fileid).json()
            url = response["url"]
            return url
        except Exception as e:
            continue

@main.route("/playlist/<path:path>")
def files(path):
    video_db = mongo.db.hls
    if path:
        query = video_db.find_one({"_id":ObjectId(path.replace(".m3u8",""))})
        if query:
            if "playlist" in query.keys():
                query = query["playlist"]
                return query.replace("$","\n")
            else:
                return json.dumps({"status":"processing"})
        else:
            return json.dumps({"status":"unavailable"}),404
    else:
        return json.dumps({"status":"unavailable"}),404

def download_file(streamable):
    with streamable as stream:
        stream.raise_for_status()
        for chunk in stream.iter_content(chunk_size=100000):
            yield chunk


# def _proxy(request,requestsurl,fileid):
#     while True:
#         resp = requests.request(method=request.method,url=requestsurl,headers={key: value for (key, value) in request.headers if key != 'Host'},data=request.get_data(), cookies=request.cookies,allow_redirects=False,stream=True)
#         headers = [(name, value) for (name, value) in resp.raw.headers.items()]
#         if resp.status_code == 404 or resp.status_code == 403:
#             requestsurl = writeCache(fileid)
#             continue
#         else:   
#             return Response(download_file(resp), resp.status_code, headers)

def _proxy(request,requestsurl,fileid):
    resp = requests.request(method=request.method,url=requestsurl,headers={key: value for (key, value) in request.headers if key != 'Host'},data=request.get_data(), cookies=request.cookies,allow_redirects=False,stream=True)
    headers = [(name, value) for (name, value) in resp.raw.headers.items()]
    return Response(download_file(resp), resp.status_code, headers)


def writeCache(fileid):
    if not os.path.isdir("cache"):
        os.mkdir("cache")
    f = open("cache/"+fileid,"w")
    TOKEN = "001.3617003158.0151996798:754693810"
    bot = Bot(token=TOKEN)
    while True:
        try:
            response = bot.get_file_info(fileid).json()
            url = response["url"]
            f.write(str(time.time())+"|"+url)
            return url
        except:
            continue

def readCache(fileid):
    try:
        f = open("cache/"+fileid,"r").readlines()
        data = f[0]
        data = data.split("|")
        ts  = data[0]
        url = data[1]
        if float(ts)+1200 > time.time():
            url = writeCache(fileid)
            return url
        else:
            return url
    except:
        url = writeCache(fileid)
        return url

# @main.route("/proxy")
# def proxied():
#     if request.args:
#         args = request.args
#         fileid= args.get("id")
#         if not os.path.isfile(os.path.join("cache",fileid)):
#             url = writeCache(fileid)
#             if url:
#                 return _proxy(request,url,fileid)
#             else:
#                 return json.dumps({"status":"unavailable"}),404
#         else:
#             url = readCache(fileid)
#             if url:
#                 return _proxy(request,url,fileid)
#             else:
#                 return json.dumps({"status":"unavailable"}),404
#     else:
#         return json.dumps({"status":"unavailable"}),404

@main.route("/proxy")
def proxied():
    if request.args:
        args = request.args
        fileid= args.get("id")
        try:
            response = requests.get("https://api.icq.net/bot/v1/files/getInfo?token=001.3617003158.0151996798:754693810&fileId="+fileid)
            print(response)
            response = response.json()
            print(response)
            url = response["url"]
            return _proxy(request,url,fileid)
        except:
            return json.dumps({"status":"unavailable"}),404
    else:
        return json.dumps({"status":"unavailable"}),404

@main.route("/video")
def directvideo():
    if request.args:
        args = request.args
        fileid= args.get("id")
        try:
            response = requests.get("https://api.icq.net/bot/v1/files/getInfo?token=001.3617003158.0151996798:754693810&fileId="+fileid)
            url = response["url"]
            return redirect(url)
        except Exception as e:
            print(e)
            return json.dumps({"status":"unavailable"}),404
    else:
        return json.dumps({"status":"unavailable"}),404


if __name__ == "__main__":
    main.run(debug=True,port=8000)
    


