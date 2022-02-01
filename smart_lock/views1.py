from django.shortcuts import render
from json import dumps
import nltk
import io
import numpy as np
import random
import string
import warnings
import pandas as pd
from nltk.corpus import stopwords
import datetime
from .models import logs
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from iot_project.settings import BASE_DIR

warnings.filterwarnings('ignore')
df = pd.read_csv(str(BASE_DIR) +"/smart_lock/ML/qna.txt")
f = open(str(BASE_DIR) +"/smart_lock/ML/q.txt", 'r', errors='ignore') #open the file
raw=f.read()  #read the file
raw=raw.lower()  #convert to lower case

sent_tokens=nltk.sent_tokenize(raw) #converts to list of sentences (sentence tokenizer punkt)
word_tokens=nltk.word_tokenize(raw)  #converts to list of words     (wordnet is the dictionary for english language)

lemmer=nltk.stem.WordNetLemmatizer()
#wordnet is a semantically-oriented dictionary of English included in nltk
#lematizer converts to its root word


#takes tokens(words) and converts to their root form
def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

remove_punct_dict=dict((ord(punct),None) for punct in string.punctuation)

#string.punctuations contains all the punctuations
#ord(punct) converts the punctuations to their ascii or unicode value
#create a dictionary such as punctuation ascii number : None




#This function takes the response from user and tokenizes it to words ,converts it to lower case, translate will replace the ascii value matching characters in the user response with the dictionary values.
def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))


greeting_inputs=("hello","hi","greetings","sup","what's up","hey","hii")
greeting_responses=["hii","hey","hi there","hello"]


#check whether greeting words are present in user response and answer accordingly
def greeting(sentence):
    for word in sentence.split():
        if word.lower() in greeting_inputs:
            return random.choice(greeting_responses)

#TfidfVectorizer
#creates a document term matrix
#columns are individual unique words
#cells contain a weight which signifies how important a word is for an individual text message
#weight will be high if the word occurs multiple times in a document but very rare in other documents.

#cosine similarity is used to find similarity between user question and text stored in the document

def response(user_response):
    chatbot_response=""
    sent_tokens.append(user_response)
    l=user_response.split(" ")
    #append the user response to the list of sentences
    if len(l)<=4:
        TfidfVec = TfidfVectorizer(tokenizer=LemNormalize)
    else:
        TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words="english")



    #use tokenizer as the LemNormalize function
    #stop words removes commonly used words that do not have any value in the sentence
    tfidf = TfidfVec.fit_transform(sent_tokens)


    #It will learn from the sent_tokens and transform into vector form (bag of wordd)
    #basically columns will be of words and each row represents the document


    vals=cosine_similarity(tfidf[-1],tfidf)
    #it will try to find the similarity between the last appended user response and the sent tokens vectorized matrix and it will return an array having similarity with each document.

    idx=vals.argsort()[0][-2]
    #arg returns indexes sorted on the values that is present on that index
    #basically idx has indexes sorted in ascending oreder of the values they hold
    #-2 because last value is one as it is the same sentence so second last is taken
    #idx has the index value of the response

    flat=vals.flatten()   #this converts multidimentional array [[]] to one dimentional array []
    flat.sort()           #this is done to check whether the matching value is not zero
    req_tfidf=flat[-2]
    print(req_tfidf)
    if(req_tfidf==0 or req_tfidf<=0.38):
        chatbot_response=chatbot_response+"I am sorry! I didn't understand you"
        return chatbot_response
    else:
        chatbot_response=chatbot_response+sent_tokens[idx]
        return chatbot_response



l=[]

flag=1

def chatbot(request): 

#while(flag==True):
    global flag    
 
    user_response=request.GET.get("res")
    print(user_response)
    if user_response==None:
        user_response=""
    else:    
        user_response=user_response.lower()

    for i in user_response.split(" "):
        if i in ["amazon","flipkart"]:
            user_response="I am a delivery guy"
    if user_response!="bye":
        if(user_response=="thanks" or user_response=="thank you" or user_response=="okay thank you"):
            data="You are Welcome"

        elif(user_response=="yes"):
            data="okay,thank you"

        elif (user_response == "no" or user_response=="okay"):
            data="okay"

        elif("time" in user_response):
            time=datetime.datetime.now()
            data= str(time.hour)+":"+str(time.minute)+":"+str(time.second)

        elif("date" in user_response or "month" in user_response or "year" in user_response or "day" in user_response):
            time = datetime.datetime.now()
            data=str(time.day)+"/"+str(time.month)+"/"+str(time.year)



        else:
            if(greeting(user_response)!=None):
                data=greeting(user_response)

            else:

                if flag==0:
                    stop_words=set(stopwords.words("english"))
                    l=user_response.split(" ")
                    l1=[]
                    for i in range(len(l)):
                        if l[i] not in stop_words and l[i]!="name":
                            l1.append(l[i])

                    name1 = logs(NAME=l1[0])
                    name1.save()

                    data="Hello "+str(l1[0])+" how can i help you"
                    flag=2
                elif flag==1:
                    data="MY name is Flash. What is your name"
                    flag=0



                else:
                    q=response(user_response)
                    if q=="I am sorry! I didn't understand you":
                        data=q

                    elif(q=="when will the owners return." or q== "when will they come back."):
                        data="value taken from database"

                    elif(q=="money not received." or q=="payment is yet to be done." or q=="payment is remaining."):
                        data="Owner will return by (database value) can you come again by that time."

                    
                    else:
                        

                        try:
                            data=df[df["question"] == str(q)]["answer"].values[0]
                        except:
                            data="I am sorry! I didn't understand you"


                    sent_tokens.remove(user_response)
                    

    else:
        data="Bye take care"
        flag=1

    return render(request, "smart_lock/index.html",{"response":data})