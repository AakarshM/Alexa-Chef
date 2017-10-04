from __future__ import print_function
import json
import urllib




# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to  Aakarsh's recipe cookbook. " \
                    "Please tell me what you want to make by saying: I want pizza, for example"
    reprompt_text = "Please tell me what you want by saying, " \
                    "I want pizza for example"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying out Aakarsh's cookbook. " \
                    "Have a nice day! "
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()

def create_food_attribute(food):
    return {"desiredFood": food}

def set_food_in_session(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Food' in intent['slots']:
        food = intent['slots']['Food']['value']
        session['attributes']['desiredFood'] = food
        session_attributes = create_food_attribute(food)
        session_attributes = modifyAttrs(intent, session, getRecipe(food))
        speech_output = "I now know you want to make " + \
                        food + \
                        ". You can ask me the first recipe I found by simply saying next"
        reprompt_text = "You can ask me your recipe, "
    else:
        speech_output = "No food has been registered. " \
                        "Please try again."
        reprompt_text = "No food has been registered. " \
                        "Please try again."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_food_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "desiredFood" in session.get('attributes', {}):
        food = session['attributes']['desiredFood']
        speech_output = "Your desired food is: " + food + \
                        ". Goodbye."
        should_end_session = False
    else:
        speech_output = "I'm not sure what your desired food is. " \
                        "You can say, I want pizza"
        should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def getRecipe(food):
    #make http request to flask here
    serverURL='https://alexa123c1.herokuapp.com/?food='
    food = food.replace(" ", "%20")
    serverURL = serverURL + food
    response = json.loads(urllib.urlopen(serverURL).read())
    return response["steps"]

def modifyAttrs(intent, session, recipeList):
    params = \
        {"desiredFood": session['attributes']['desiredFood'],
         "steps": recipeList,
         "cur": recipeList[len(recipeList) - 1],
         "div": []} #no division yet
    return params


def next_step_from_session(intent, session):
    recipeList = session['attributes']['steps']
    if(len(recipeList) <= 0):
        should_end_session = True
        attrs = session['attributes']
        speech_output = "Steps finished, enjoy your meal!"
        reprompt_text = "I am not sure what the next step is"
        return build_response(attrs, build_speechlet_response(
            intent['name'], speech_output, reprompt_text, should_end_session))

    #ELSE
    step = recipeList[len(recipeList) - 1]
    session['attributes']['steps'].pop()
    session['attributes']['cur'] = step
    should_end_session = False
    attrs = session['attributes']
    speech_output = "Now, " + step
    reprompt_text = "I am not sure what the next step is"
    return build_response(attrs, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))



def repeat_step_from_session(intent, session):
    step = session['attributes']['cur']
    should_end_session = False
    attrs = session['attributes']
    speech_output = step
    reprompt_text = "I am not sure what the step is"
    return build_response(attrs, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def divide_step_from_session(intent, session):
    step = session['attributes']['cur']
    should_end_session = False
    attrs = session['attributes']
    speech_output = step
    reprompt_text = "I am not sure what the step is"
    return build_response(attrs, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "WhatsMyFoodIntent":
        return get_food_from_session(intent, session)
    elif intent_name == "NextStepIntent":
        return next_step_from_session(intent, session)
    elif intent_name == "RepeatStepIntent":
        return repeat_step_from_session(intent, session)
    elif intent_name == "DivideIntoIntent":
        return divide_step_from_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    elif intent_name == "MyFoodIsIntent":
        return set_food_in_session(intent, session)
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

  
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
