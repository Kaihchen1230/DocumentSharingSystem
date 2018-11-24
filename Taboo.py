import DB


#For SU
"================================================="

def addTaboo(listoftaboo):
    try:
        for word in listoftaboo:
            DB.tabooWord.update({
                DB.tolower(word): DB.tolower(word)
            })

        return True

    except Exception as e:
        print("addTaboo()")
        print(e)

def getTaboo():
    try:
        listoftaboo = DB.tabooWord.get()
        listoftaboo.pop(0)
        return listoftaboo

    except Exception as e:
        print("getTaboo()")
        print(e)


def deleteTaboo(listofword):
    try:
        ref = DB.tabooWord
        for word in listofword:
           ref.child(DB.tolower(word)).delete()

        return True

    except Exception as e:
        print("deleteTaboo()")
        print(e)

"================================================"

def suggestTaboo(email, listofword):
    try:
        ref = DB.user.child(DB.removeIllegalChar(email)).child('Suggest_taboo')
        for word in listofword:
            ref.update({
                word:word
            })

    except Exception as e:
        print("suggestTaboo()")
        print(e)

def deleteSuggestTaboo(email, listofword):
    try:
        ref = DB.user.child(DB.removeIllegalChar(email)).child('Suggest_taboo')

        for word in listofword:
            ref.child(DB.tolower(word)).delete()

        return True

    except Exception as e:
        print("deleteSuggestTaboo")
        print(e)


if __name__ == '__main__':
    deleteSuggestTaboo('viewtest2',['test','benzhou'])