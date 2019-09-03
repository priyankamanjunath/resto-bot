# -*- coding: utf-8 -*-
#from textblob import TextBlob
#from attributegetter import *
from generatengrams import ngrammatch
from Contexts import *
import json
from Intents import *
from ReadJSON import *
import random
import os
import re

def check_actions(current_intent, attributes, context):
    '''This function performs the action for the intent
    as mentioned in the intent config file'''
    '''Performs actions pertaining to current intent
    for action in current_intent.actions:
        if action.contexts_satisfied(active_contexts):
            return perform_action()
    '''
    #{'costtypes': 'cheap', 'location': 'east', 'cuisines': 'chinese'}
    print(current_intent.action)
    if (current_intent.action=='RestroBook'):
        #print("check actions working")
        #print(attributes)
        location = attributes['location']
        cuisine = attributes['cuisines']
        category = attributes['costtypes']
        finalchoice = getRestaurantData(location, cuisine, category)
        if(finalchoice==None):
            print("Sorry ! Unable to find Restaurant with this combination")
        else:
             print("Your choice is " + finalchoice + " for "+ cuisine + " falling in " + category + " cost type")
        context= IntentComplete()
        return 'action: ' + current_intent.action, context
    if(current_intent.action=='BuyABook'):
        #print("BuyaBook log")
        genre = attributes['genre']
        authors = attributes['authors']
        publisher = attributes['publisher']
        #print(genre + authors + publisher)
        finalchoice = getBooksData(genre.lower(), authors.lower(), publisher.lower())
        if(finalchoice==None):
            print("Sorry ! Unable to find Book with this combination")
        else:
             print("You have ordered " + finalchoice + " in "+ genre + " authored by "+ authors + " and published by " + publisher)
        context= IntentComplete()
        return 'action: ' + current_intent.action, context
    else:
        print('this is default')
        return 'action: ' + current_intent.action, context
        

def check_required_params(current_intent, attributes, context):
    '''Collects attributes pertaining to the current intent'''
    #print(attributes)
    for para in current_intent.params:
        #print(para.name)
        if para.required:
            if para.name not in attributes:
                #Example of where the context is born, implemented in Contexts.py
                #print(para.name)
                if para.name=='RegNo':
                    context = GetRegNo()
                #returning a random prompt frmo available choices.
                return random.choice(para.prompts), context

    return None, context


def input_processor(user_input, context, attributes, intent):
    '''Spellcheck and entity extraction functions go here'''
    
    #uinput = TextBlob(user_input).correct().string
    
    #update the attributes, abstract over the entities in user input
    attributes, cleaned_input = getattributes(user_input, context, attributes)
    
    return attributes, cleaned_input

def loadIntent(path, intent):
    with open(path) as fil:
        dat = json.load(fil)
        intent = dat[intent]
        return Intent(intent['intentname'],intent['Parameters'], intent['actions'])

def intentIdentifier(clean_input, context,current_intent):
    clean_input = clean_input.lower()
    
    #Scoring Algorithm, can be changed.
    scores = ngrammatch(clean_input)
    
    #choosing here the intent with the highest score
    scores = sorted_by_second = sorted(scores, key=lambda tup: tup[1])
    # print clean_input
    #print 'scores', scores
    

    if(current_intent==None):
        #if(clean_input=="search"):
         #   return loadIntent('params/newparams.cfg', 'SearchStore')
        if(clean_input=='selectrestro'):
            print('selectrestro intent')
            return loadIntent('params/newparams.cfg','RestroSelect')
        if(clean_input=='BuyBook'):
            #print('BuyBook intent')
            return loadIntent('params/newparams.cfg','BuyBook')                
        else:
            #print('ngrams intent')
            return loadIntent('params/newparams.cfg',scores[-1][0])
            #return loadIntent('params/newparams.cfg','BuyBook')   
    else:
        #If current intent is not none, stick with the ongoing intent
        return current_intent

def getattributes(uinput,context,attributes):
    '''This function marks the entities in user input, and updates
    the attributes dictionary'''
    #print ("Line 74")
    #print(attributes)
    myinput = uinput
    #Can use context to context specific attribute fetching
    if context.name.startswith('IntentComplete'):
        return attributes, uinput
    else:
        #Code can be optimised here, loading the same files each time suboptimal 
        files = os.listdir('./entities/')
        #print(files)
        entities = {}
        for fil in files:
            if fil != '.DS_Store':
                #print(fil)
                lines = open('./entities/'+fil).readlines()
                for i, line in enumerate(lines):
                    lines[i] = line[:-1]
                entities[fil[:-4]] = '|'.join(lines)
        #print ("Line 88")
        #print(attributes)
        #Extract entity and update it in attributes dict
        #print(entities)
        #print(uinput)
        for entity in entities:
            for i in entities[entity].split('|'):
                if i.lower() in uinput.lower():
                    attributes[entity] = i
        for entity in entities:
                uinput = re.sub(entities[entity],r'$'+entity,uinput,flags=re.IGNORECASE)
        #print(attributes)
        #Example of where the context is being used to do conditional branching.
        if context.name=='GetRegNo' and context.active:
            #print (attributes)
            match = re.search('[0-9]+', uinput)
            if match:
                uinput = re.sub('[0-9]+', '$regno', uinput)
                attributes['RegNo'] = match.group()
                context.active = False

        return attributes, uinput
        #return attributes,myinput
        

class Session:
    def __init__(self, attributes=None, active_contexts=[FirstGreeting(), IntentComplete() ]):
        
        '''Initialise a default session'''
        
        #Active contexts not used yet, can use it to have multiple contexts
        self.active_contexts = active_contexts
        
        #Contexts are flags which control dialogue flow, see Contexts.py        
        self.context = FirstGreeting()
        
        #Intent tracks the current state of dialogue
        #self.current_intent = First_Greeting()
        self.current_intent = None
        
        #attributes hold the information collected over the conversation
        self.attributes = {}
        
    def update_contexts(self):
        '''Not used yet, but is intended to maintain active contexts'''
        for context in self.active_contexts:
            if context.active:
                context.decrease_lifespan()

    def reply(self, user_input):
        '''Generate response to user input'''
        #print(self.context.name)
        #print(user_input)
        
        self.attributes, clean_input = input_processor(user_input, self.context, self.attributes, self.current_intent)
        
        self.current_intent = intentIdentifier(clean_input, self.context, self.current_intent)
        
        prompt, self.context = check_required_params(self.current_intent, self.attributes, self.context)

        #prompt being None means all parameters satisfied, perform the intent action
        if prompt is None:
            if self.context.name!='IntentComplete':
                prompt, self.context = check_actions(self.current_intent, self.attributes, self.context)
        
        #Resets the state after the Intent is complete
        if self.context.name=='IntentComplete':
            #print('intent is now complete')
            self.attributes = {}
            self.context = FirstGreeting()
            self.current_intent = None
        
        return prompt
    

session = Session()

print ('BOT: Hi, Do you want to search a restaurant or buy a book ?')

while True:
    
    inp = input('User: ')
    if(inp == 'exit'):
        print('Thank you please visit again!')
        break;
    print ('BOT:', session.reply(inp))
    