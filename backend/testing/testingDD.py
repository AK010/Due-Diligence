import os
from pprint import pprint
import bson
from dotenv import load_dotenv
import pymongo
from bson.objectid import ObjectId
import datetime
import time


mongodb_pass = '4v38Z9oFAxnKm6SG'
# db_name = "Main"
# DB_URI = "mongodb+srv://s3kim2018:{}@cluster0.xfm8y.mongodb.net/{}?retryWrites=true&w=majority".format(mongodb_pass, db_name)
# load_dotenv(verbose=True)

friend_id = ObjectId("60690138e111b60d31e227a4")
print(type(friend_id))
email = "hacker@princeton"
db_uri = "mongodb+srv://princetonHacker:4v38Z9oFAxnKm6SG@princetonunihack.rvwct.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

def find_userid(email):
    pipeline = []
    client = pymongo.MongoClient(db_uri)
    db = client["Main"]
    coll = db["user"]
    if email == "hacker@princeton":
        pipeline = [
            {
                    "$match": {
                        "email": email,
                        "username": "princetonhacker"
                    },
                },
    ]
    elif email =="hacker@cambridge":
        pipeline = [
            {
                    "$match": {
                        "email": email,
                        "username": "cambridgehacker"
                    },
                },
    ]
    
    fetched_record = coll.aggregate(pipeline)
    for search in fetched_record:
        pprint(search)
        dd2_id = search["_id"]
        print("\n")
        print(dd2_id)
        return dd2_id

def fetch_search_history(email):
    # connect to mongo cluster using pymongo
    search_history_arr = []
    client = pymongo.MongoClient("mongodb+srv://princetonHacker:4v38Z9oFAxnKm6SG@princetonunihack.rvwct.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = client["Main"]
    coll = db["histories"]
    dd_id = find_userid(email)
    pipeline = [
        {
            "$match": {
                "dd_id": dd_id
            },
        },
    {
        "$sort": {
            "timestamp":-1
            }
    }, 
    {
        "$limit":3
        }, 
    ]


    fetched_searches = coll.aggregate(pipeline)
    ## here we need to return rather than print
    for search in fetched_searches:
        search_history_arr.append(search)
    return search_history_arr

def find_record(record_id, db_uri):
    client = pymongo.MongoClient(db_uri)
    db = client["Main"]
    coll = db["user"]
    pipeline = [
    {
            "$match": {
                "_id": record_id
            },
        },
    ]
    fetched_records = coll.aggregate(pipeline)
    for record in fetched_records:
        dd_record = record
        return dd_record


def fetch_friends_list(user_id, db_uri):
    friendsIDs = []
    friends_list =[]
    client = pymongo.MongoClient(db_uri)
    db = client["Main"]
    coll = db["user"]
    pipeline = [
    {
            "$match": {
                "_id": user_id
            },
        },
    ]

    fetched_records = coll.aggregate(pipeline)
    for record in fetched_records:
                #check if the field friends exist first 
        if "friends" in record:
            friendsIDs = record["friends"]

    for dd_id in friendsIDs:
        friend_record = find_record(dd_id, db_uri)
        friends_list.append(friend_record)

    return friends_list
# when updating profile, the front end should send a payload containing all the fields that have been filled
# it must have an _id!
def edit_profile(payload, db_uri):
    client = pymongo.MongoClient(db_uri)
    db = client["Main"]
    coll = db["user"]
    if "_id" in payload:
        user_id = payload["_id"]    
        # if type(user_id) == str:
        #     user_id = ObjectId(payload["_id"])
        # elif type(user_id) == bson.objectid.ObjectId: 
        #     user_id = payload["_id"]
        query = {"_id": user_id}
        chck_existance = check_record_exist(query, db_uri)
        if chck_existance == "exists":
            test_query = coll.find(query)
            if "favourites" in payload:
                favourites = payload["favourites"]
                print("- Updating favourites")
                newvalues = {"$set":{ "favourites": favourites}}
                coll.update_one(query, newvalues)
                check_status(test_query, "favourites", favourites)
            if "investmenthorizon" in payload: 
                horizon = payload["investmenthorizon"]
                print("- Updating investment horizon")
                newvalues = {"$set":{ "investmenthorizon": horizon}}
                coll.update_one(query, newvalues)
                check_status(test_query, "investmenthorizon", horizon)
            if  "investmentstyle" in payload:
                style = payload["investmentstyle"]
                print("- Updating investment style")
                newvalues = {"$set":{ "investmentstyle": style}}
                coll.update_one(query, newvalues)
                check_status(test_query, "investmentstyle", style)
                
            else: 
                print("ERR!! NO _id in the payload!")
        else:
            print("RECORD DOES NOT EXIST!")


def check_status(db_query, key, value ):
    for records in db_query:
        if key  in records:
            field = records[key]
            if field == value:
                print("RECORD UPDATED!")
            else: 
                print("RECORD NOT UPDATED")

def check_record_exist(query, db_uri):
    client = pymongo.MongoClient(db_uri)
    db = client["Main"]
    coll = db["user"]
    fetched_records = coll.find(query)
    for record in fetched_records:
        dd_record = record
        if dd_record != None: 
            return "exists"
        else:
            return "does not exist"

# When the user with user_id clicks on `add` or `connect` the list of friends is updated 
# and a new friend with id = friend_id is added to the list

def add_friend(user_id, friend_id, db_uri):
    client = pymongo.MongoClient(db_uri)
    db = client["Main"]
    coll = db["user"]
    #check type for user_id
    # if type(user_id) == str:
    #     user_id = ObjectId(user_id)
    # elif type(user_id) == bson.objectid.ObjectId: 
    #     user_id = user_id

    #check type for friend_id
    # if type(friend_id) == str:
    #     friend_id = ObjectId(user_id)
    # elif type(friend_id) == bson.objectid.ObjectId: 
    #     friend_id = user_id
    query = {"_id": user_id}
    # I use the method $addToSet rather than $push, if the id already exists it will not be added
    # to the set.
    friend_id = ObjectId("60690138e111b60d31e227a4")
    newvalues = {"$addToSet":{ "friends": friend_id}}
    # update user record with _id =user_id with a new friend by appending
    # an dd_id = friend_id to the friends array
    coll.update_one(query, newvalues)
    #confirmation 
    for records in coll.find(query):
            if "friends" in records:
                friends = records["friends"]
                if contains(friends, friend_id) == 0:
                    print("Friend added!")
                    return friend_id
                else: 
                    return "FRIEND ALREADY EXIST IN THE LIST"



def contains(arr, element):
    if element in arr: 
        return 1 #true
    else:
        return 0 #false

def check_user_credentials(payload, db_uri):
    client = pymongo.MongoClient(db_uri)
    db = client["Main"]
    coll = db["user"]
    # print("TEST CHECK")
    if "_id" in payload and "username" in payload and "password" in payload:
        print("TEST CHECK")
        user_id = payload["_id"]    
        if type(user_id) == str:
            user_id = ObjectId(payload["_id"])
        elif type(user_id) == bson.objectid.ObjectId: 
            user_id = payload["_id"]
        username = payload["username"]
        password = payload["password"]
        query = {"_id": user_id, "password": password, "username": username}
        fetched_records = coll.find(query)
        # print("RECORD FETCHED")
        for record in fetched_records:
            dd_record = record
            if dd_record != None: 
                # print(dd_record["_id"])
                return dd_record["_id"]
            else:
                # print('STATUS 400, RECORD NOT FOUND')
                return  'STATUS 400, RECORD NOT FOUND'
    else: 
        # print('STATUS 400, PROVIDE BOTH USERNAME, PASSWORD')
        return 'STATUS 400, PROVIDE BOTH USERNAME, PASSWORD'


# insert user at sign up
# username and email must be unique
def create_user(payload, db_uri):
    client = pymongo.MongoClient(db_uri)
    non_unique_rec_arr = []
    db = client["Main"]
    coll = db["user"]
    if "email" in payload and "username" in payload and "password" in payload:
        # check if email is unique 
        email = payload["email"]
        pipeline_1 =  [{
                "$match": {
                    "email":  email
                },
        }]
        fetched_records = coll.aggregate(pipeline_1)
        for search in fetched_records:
            print(search)
            non_unique_rec_arr.append(search)
        print(non_unique_rec_arr)
        if non_unique_rec_arr != []: 
                print("Email or Username already used. Sign Up with a different email or Log In")
                return "Email or Username already used. Sign Up with a different email or Log In"
        else: 
            print("CREATING A RECORD FOR HACKPRINCETON....")
            query = {"email": payload["email"], "username": payload["username"], "password": payload["password"], "investmentstyle": payload["investmentstyle"], "investmenthorizon": payload["investmenthorizon"], "friends":payload["friends"], "favourites": payload["favourites"]}
            insert_record = coll.insert_one(query)
            print("SUCCESS, new record has been created!")
            return insert_record


def create_history(payload, db_uri):
        client = pymongo.MongoClient(db_uri)
        db = client["Main"]
        coll = db["histories"]
        ## passing the stock payload
        if type(payload) == list:
            for p in payload: 
                p["timestamp"] = datetime.datetime.now()
                if "_id" in p: 
                    dd_id = p["_id"]
                    del p["_id"]
                elif "id" in p: 
                    dd_id = p["id"]
                    del p["id"]
                # if type(dd_id) == str:
                #     dd_id = ObjectId(dd_id)
                # elif type(dd_id) == bson.objectid.ObjectId: 
                #     dd_id = dd_id
                p["dd_id"] = dd_id
                insert_search_id = coll.insert_one(p)
                if insert_search_id != None:
                    print("Search succesfully saved")
                    pprint(insert_search_id)
                    return insert_search_id
                else:
                    # print('STATUS 400, RECORD NOT FOUND')
                    return  'ERROR! HISTORY RECORD NOT SAVED'

        if type(payload) == dict:
            payload["timestamp"] = datetime.datetime.now()
            if "_id" in payload: 
                dd_id = payload["_id"]
                del payload["_id"]
            elif "id" in payload: 
                dd_id = payload["id"]
                del payload["id"]
            # if type(dd_id) == str:
            #     dd_id = ObjectId(dd_id)
            # elif type(dd_id) == bson.objectid.ObjectId: 
            #     dd_id = dd_id
            payload["dd_id"] = dd_id
            insert_search_id = coll.insert_one(payload)
            if insert_search_id != None:
                print("Search succesfully saved")
                print(insert_search_id)
                return insert_search_id
            else:
                # print('STATUS 400, RECORD NOT FOUND')
                return  'ERROR! HISTORY RECORD NOT SAVED'

if __name__ == "__main__":
    print("1: SIGN UP, username: princetonhacker, email: hacker@princeton, password: `hack1234`}'")
    payload = {
        "username": "princetonhacker",
        "email": "hacker@princeton",
        "password": "hack1234",
        "investmentstyle": "growth term",
        "investmenthorizon": "long term",
        "friends":[],
        "favourites":[
            {
                "0": "TSL",
                "1": "AAPL",
                "2": "HPQ"
            }
        ]
    }
    create_user(payload, db_uri)
    cambridge_id =  ObjectId("606a02a9abdc3533093955ec")
    print("\n")
    print("2: CHECKING CREDENTIALS AT LOG IN for username: cambridgehacker")
    payload = {
        "_id": cambridge_id,
        "username": "cambridgehacker",
        "password" : "hack1234"
    }
    check_user_credentials(payload, db_uri)
    print("\n")
    print("3: SAVE TESLA STOCK SEARCH HISTORY FOR username:cambridgehacker...")
    
    payload = {
        "_id":  ObjectId("606a02a9abdc3533093955ec"),
        "symbol": "TSL",
        "stock":"Tesla",
        "price": "661.75 USD" #HPQ - Hewlett-Packard
    }
    create_history(payload, db_uri)
    print("\n")
    print("Wait for 10 seconds before searching for another stock")
    time.sleep(10)
    print(" -  ADDING A NEW SEARCH FOR HPQ - Hewlett-Packard. ")
    payload2 = {
        "_id": ObjectId("606a02a9abdc3533093955ec"),
        "symbol": "HPQ",
        "stock":"Hewlett-Packard",
        "price": "32.05 USD" #HPQ - Hewlett-Packard
    }
    create_history(payload2, db_uri)
    print("\n")
    print("Wait for 10 seconds before searching for another stock")
    time.sleep(10)
    print(" -  ADDING A NEW SEARCH FOR APPL - Apple Inc. ")
    payload3 = {
        "_id": ObjectId("606a02a9abdc3533093955ec"),
        "symbol": "AAPL",
        "stock":"Apple Inc",
        "price": "123.00 USD" #HPQ - Hewlett-Packard
    }
    create_history(payload3, db_uri)
    print("\n")
    print("4: SEARCH FOR HISTORY...")
    email = "hacker@cambridge"
    searches =  fetch_search_history(email)
    pprint(searches)
    print("\n")
    princeton_id = find_userid("hacker@princeton")
    print("5: ADD FRIEND - cambridgehacker for username: princetonhacker..")
    added_friend = add_friend(princeton_id, cambridge_id, db_uri)
    print(added_friend)
    print("\n")
    print("6: FETCH FRIENDS for username: princetonhacker..")
    friends = fetch_friends_list(princeton_id, db_uri)
    print("Success. Look up updated record...")
    updated_record = find_record(princeton_id, db_uri)
    pprint(updated_record)
    print("\n")
    print("7: UPDATE PROFILE for username: cambridgehacker.. with payload: 'investmentstyle': 'value',  'investmenthorizon': 'short term' ")
    test_payload = {
        "_id": cambridge_id,
        "investmentstyle": "value",
        "investmenthorizon": "short term"
    }
    print("\n")
    edit_profile(test_payload,db_uri)
    updated_record = find_record(cambridge_id, db_uri)
    pprint(updated_record)
    
    print("\n")
    print("hacker@princeton SUCCESS!! ")



