from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages

from network.views.utils.DB import DB

db = DB()


def user_test(user):
    if user.is_authenticated():
        if not db.get_current_user():
            db.set_current_user(user.id)
        return True
    else:
        return False


@user_passes_test(user_test)
def user_page(request, usr_id=""):

    print usr_id
    path = "/socnet/userpage/"
    user_info = {"authorized": True}
    is_friends = False
    if request.method == "POST":
        pass
    else:
        if usr_id != "" and request.user.id == usr_id:
            # This is page of user that requested page, content will be different
            request_page_info = db.get_user_by_id(usr_id)
            if request_page_info["name"]:
                path += usr_id
                user_info.update(request_page_info.copy())
            else:
                return render(request, "Error-Page.html", {"user_info": user_info, "msg": "User doesn't exist"})
        else:
            request_page_info = db.get_user_by_id(usr_id)
            if request_page_info["name"]:
                path += usr_id
                user_info.update(request_page_info.copy())
                if db.is_friend(usr_id):
                    is_friends = True

                user_info["id"] = usr_id
                print "adsasda"
            else:
                return render(request, "Error-Page.html", {"user_info": user_info, "msg": "User doesn't exist"})
    user_info["path_to_page"] = path
    return render(request, "User-Page.html", {"user_info": user_info, "is_friends": is_friends})


@user_passes_test(user_test) 
def error_page(request):
    msg = "Something bad was wrong"
    user_info = {"authorized": True, "user_page": "/socnet/userpage/" + str(request.user.id)}
    if request.method == "GET":
        return render(request, "Error-Page.html", {"user_info": user_info, "msg": msg})


@user_passes_test(user_test) 
def mail_page(request):
    user = request.user
    path = "/socnet/userpage/" + str(user.id)
    user_info = {"authorized": True, "id": user.id, "user_page": path}
    msgs = db.get_current_user_mail()

    return render(request, "User-Msgs-Page.html", {"user_info": user_info, "msgs": msgs})


@user_passes_test(user_test) 
def send_msg(request, user_id=""):
    user = request.user
    path = "/socnet/userpage/" + str(user.id)
    user_info = {"authorized": True, "user_page": path}
    if request.method == "POST":
        receiver = request.POST["receiver"]
        content = request.POST["content"]
        sender = user.id
        if db.send_message(receiver, content):
            return HttpResponseRedirect("/socnet/im")
    else:
        receiver = user_id
        return render(request, "Send-Message-Page.html", {"user_info": user_info, "receiver": receiver})


@user_passes_test(user_test) 
def user_friends(request):
    user_info = {"user_page": db.get_user_path(), "authorized": True}
    if request.method == "GET":
        friends = db.get_current_user_friends()
        return render(request, "My-Friends-Page.html", {"user_info": user_info, "friends": friends})


@user_passes_test(user_test)
def send_friend_request(request):
    if request.method == "POST":
        print request.POST["receiver"]
        db.send_friend_request(request.POST["receiver"])
        return HttpResponseRedirect("/socnet/friends/")


@user_passes_test(user_test)
def user_requests(request):
    user = request.user
    user_info = {"authorized": True, "user_page": db.get_user_path()}
    if request.method == "GET":
        requests = db.get_current_user_requests()
        return render(request, "Friend-Requests-Page.html", {"user_info": user_info, "requests": requests})


@user_passes_test(user_test)
def accept_request(request):
    if request.method == "POST":
        db.accept_friend_request(request.POST["request_id"])
        messages.add_message(request, messages.INFO, "Successfully added")

    return HttpResponseRedirect('/socnet/requests')


def decline_request(request):
    if request.method == "POST":
        db.cancel_friend_request(request.POST["request_id"])
        messages.add_message(request, messages.INFO, "Successfully declined")
    return HttpResponseRedirect('/socnet/requests')


def delete_friend(request):
    if request.method == "POST":
        db.delete_friend(request.POST["receiver"])
        messages.add_message(request, messages.INFO, "Successfully deleted")

        return HttpResponseRedirect('/socnet/userpage/'+request.POST["receiver"])


@user_passes_test(user_test)
def user_sent_msgs(request):
    user = request.user
    user_info = {"authorized": True, "user_page": db.get_user_path()}
    print user_info
    if request.method == "GET":
        msgs = db.get_current_user_sent_msgs()
        return render(request, "User-Sent-Mail.html", {"msgs": msgs, "user_info": user_info})
