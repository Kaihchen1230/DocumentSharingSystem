import json
from time import strftime, localtime
import urllib
from collections import OrderedDict

import DB


def saveDoc(email, doc, fileName, permission):
    """
        CITED FROM https://github.com/PhantomInsights/firebase-python/blob/master/storage/README.md
        CREATOR: https://github.com/agentphantom
        upload docs to cloud
    :param email: unique ID
    :param doc: location of the file
    :return: True for load successfully
    """
    timeCode = strftime("%Y-%m-%d-%H-%M-%S", localtime())
    userID = DB.removeIllegalChar(email)
    file = open(doc, "rb")
    file_in = file.read()
    target = "https://firebasestorage.googleapis.com/v0/b/llhc-db662.appspot.com/o/savedocs%2F" + userID + "%2F" + fileName + "%2F" + timeCode
    head = {'Content-Type': 'text/plain'}

    req = urllib.request.Request(target, data=file_in, headers=head, method="POST")

    try:
        urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        msg = json.loads(e.read())
        print(msg['error']['message'])
    else:
        fileHisotry = DB.root.child('User').child(DB.removeIllegalChar(email)).child('Document_history')
        fileHisotry.update({
            timeCode: {
                'Name': fileName,
                'Locked': False,
                'Permission': permission
            }
        })

        ref = DB.root.child("View_counter").child(DB.removeIllegalChar(email))
        viewchecker = ref.child(fileName).get()
        if viewchecker is None:
            ref.update({
                fileName: 0
            })

        return True


def listallfiles(email):
    """

    :param email:
    :return:     list of all the current user documents
    """
    try:
        data = DB.user.child(DB.removeIllegalChar(email)).child("Document_history").order_by_child('Name').get()
        if data is None:
            return 0
        else:
            result = []
            for key in data:
                result.append(data[key]["Name"])

            return list(OrderedDict.fromkeys(result))

    except Exception as e:
        print('listallfiles()')
        print(e)


def listallhistory(email, filename):
    """

    :param filename:
    :return: list of edit history for a file
    """
    try:
        ref = DB.user.child(DB.removeIllegalChar(email)).child("Document_history").order_by_child("Name").equal_to(
            filename)
        snapshot = ref.get()
        result = []
        if ref is not None:
            for key in snapshot:
                result.append(key)

        return result

    except Exception as e:
        print("listallhistory()")
        print(e)


def getLastestVersion(email, filename):
    result = listallhistory(email, filename)
    return result[len(result) - 1]


def openfile(email, fileOwner, filename, version):
    """

        :param email:
        :param filename:
        :param version: if blank then open the newest one, use listallhistory to get one of the version
        :return: return the content of a file
        """

    print(email,fileOwner)
    if DB.removeIllegalChar(email) == DB.removeIllegalChar(fileOwner) and not email=="":
        if version == "":
            target = getLastestVersion(fileOwner, filename)
            print(target)
            url = "https://firebasestorage.googleapis.com/v0/b/llhc-db662.appspot.com/o/savedocs%2F" + DB.removeIllegalChar(
                email) + "%2F" + filename + "%2F" + target + "?alt=media"

        else:
            url = "https://firebasestorage.googleapis.com/v0/b/llhc-db662.appspot.com/o/savedocs%2F" + DB.removeIllegalChar(
                email) + "%2F" + filename + "%2F" + version + "?alt=media"

        urllib.request.urlretrieve(url, "../cache")
        #file = open('../cache', "r")
        #fileout = file.read()
        #file.close()

    else:
        print(fileOwner, filename)
        if version == "":
            target = getLastestVersion(fileOwner, filename)
            print(target)
            url = "https://firebasestorage.googleapis.com/v0/b/llhc-db662.appspot.com/o/savedocs%2F" + DB.removeIllegalChar(
                fileOwner) + "%2F" + filename + "%2F" + target + "?alt=media"

        else:
            url = "https://firebasestorage.googleapis.com/v0/b/llhc-db662.appspot.com/o/savedocs%2F" + DB.removeIllegalChar(
                fileOwner) + "%2F" + filename + "%2F" + version + "?alt=media"

        urllib.request.urlretrieve(url, "../cache")

        ref = DB.root.child("View_counter")
        getref = ref.get()
        print(getref)
        views = getref[fileOwner][filename] + 1
        ref.child(fileOwner).update({
            filename: views
        })

    #return fileout


def isFileLocked(email, filename):
    docID = getLastestVersion(email, filename)
    ref = DB.user.child(DB.removeIllegalChar(email)).child("Document_history").child(docID).get()
    return ref["Locked"]

def getAllLockFile():
    alluser = DB.allUsers()
    result = {}
    files = []
    if alluser:
        for user in alluser:
            userFile = listallfiles(user)
            if userFile:
                for eachFile in userFile:
                    if isFileLocked(user, eachFile):
                        files.append(eachFile)
                if files:
                    result.update({user: files})
                    files = []

    return result


def changeLock(email, filename, status):
    """
        Lock a document
    :param email:
    :param filename:
    :return:
    """
    print('called')
    ref = DB.user.child(DB.removeIllegalChar(email)).child("Document_history").order_by_child("Name").equal_to(
        filename).get()

    if ref is not None:
        result = []
        for key in ref:
            result.append(key)


        for doc in result:
                snapshot = DB.user.child(DB.removeIllegalChar(email)).child("Document_history").child(doc)
                snapshot.update({
                    'Locked': status
            })


def getMostview():
    """

    :return: the three of the most viewed docs
    """


    ref = DB.root.child("View_counter")
    viewcount = ref.get()
    lst = []
    if viewcount is not None:
        for key, val in viewcount.items():
            for j in val:
                if checkFilePermission(key,j) == 'public'or checkFilePermission(key,j)=='restricted':
                    lst.append((key, j, val[j]))

        lst = sorted(lst, key=lambda tup: tup[2], reverse=True)
        return lst[:3]


def setPermission(email, filename, permission):
    ref = DB.user.child(DB.removeIllegalChar(email)).child("Document_history").order_by_child("Name").equal_to(
        filename).get()
    result = []
    for key in ref:
        result.append(key)

    for doc in result:
        snapshot = DB.user.child(DB.removeIllegalChar(email)).child("Document_history").child(doc)
        snapshot.update({
            'Permission': permission
        })

    return True

def getPermissionFiles(permissionType):
    ref = DB.user.get()

    result = {}

    for key in ref:
        if "Document_history" in ref[key]:
            qry = []
            for timecode in ref[key]['Document_history']:
                if ref[key]['Document_history'][timecode]['Permission'] == permissionType:
                    qry.append(ref[key]['Document_history'][timecode]['Name'])
            result[key] = list(OrderedDict.fromkeys(qry))

    return result

def checkFilePermission(user,filename):
    ref = DB.user.child(DB.removeIllegalChar(user)).child('Document_history').get()
    #print(ref)
    if ref is None:
        return None
    for key in ref:
        if ref[key]['Name'] == filename:
            return ref[key]['Permission']

def notPrivateFile():
    ref = DB.user.get()

    result = {}

    for key in ref:
        if "Document_history" in ref[key]:
            qry = []
            for timecode in ref[key]['Document_history']:
                if ref[key]['Document_history'][timecode]['Permission'] == 'public' or ref[key]['Document_history'][timecode]['Permission']=='restricted':
                    qry.append(ref[key]['Document_history'][timecode]['Name'])
            result[key] = list(OrderedDict.fromkeys(qry))

    return result

if __name__ == '__main__':
    # saveDoc('viewtest','test.txt','again')
    #print(getMostview())
    #print(listallfiles('guest'))
    #setPermission('viewtest','test1','public')
    #print(getMostview())
    #saveDoc('hrgutou@gmail.com','test.txt','test2')
    #print(checkFilePermission('hrgutou@gmail.com','tasdft1'))
    getAllLockFile()