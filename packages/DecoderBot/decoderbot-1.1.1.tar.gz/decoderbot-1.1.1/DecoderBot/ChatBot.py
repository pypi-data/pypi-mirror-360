import difflib
import random

class ChatBot:

    class ResponseTypeError(Exception):
        pass
    
    def __init__(self, name="My ChatBot", threshold=0.2):
        self.name = name
        self.nameResponse = f"My name is {self.name}"
        self._responses = {
            "hello" : "Hey there, how are you?",
            "bye" : "Goodbye! You can come here whenever you want."
        }
        
        self._imp_responses  = {
            "name" : self.nameResponse
        }
        self.threshold = threshold
        
        self._responses.update(self._imp_responses )

    def train_for(self, message, reply):
        self._responses[message.lower()] = reply.capitalize()

    def set_training(self, responses):
        if not isinstance(responses, dict):
            raise self.ResponseTypeError("a dictionary value must be passed through set_responses")
        self._responses = {}
        
        for message, reply in responses.items():
            self._responses[message.lower()] = reply.capitalize()
        
        self._responses.update(self._imp_responses )
    
    def train(self, responses):
        if not isinstance(responses, dict):
            raise self.ResponseTypeError("a dictionary value must be passed through add_responses_dict")
        
        self._responses.update(responses)
    
    def get_response(self, message, m = "Sorry, I can't give the answer to that message right now"):
        return self._responses.get(message.lower(), m)
    
    def get_closest_response(self, message, m = "Sorry, I can't give the answer to that message right now"):
        a = difflib.get_close_matches(message.lower(), self._responses.keys(), n=1, cutoff=self.threshold)
        return self._responses.get(a[0]) if a else m
    
    def reset_training(self):
        self._responses = {}
        self._responses.update(self._imp_responses)

    def get_random_response(self, message, m = "Sorry, I can't give the answer to that message right now"):
        r = self.get_closest_response(message)
        if isinstance(r, (list, tuple, set)):
            return random.choice(r)
        return r

    def reset_bot(self, name="My Chatbot", threshold=0.2):
        self.name = name
        self.nameResponse = f"My name is {self.name}"
        self._responses = {
            "hello" : "Hey there, how are you?",
            "bye" : "Goodbye! You can come here whenever you want."
        }
        
        self._imp_responses  = {
            "name" : self.nameResponse
        }
        
        self.threshold = threshold
        
        self._responses.update(self._imp_responses)



class Data:
    def __init__(self):
        self.conversations = {
            "hello": "Hey there!",
            "hi": "Hello!",
            "hey": "Hi there!",
            "yo": "What's up?",
            "good morning": "Good morning to you!",
            "good afternoon": "Good afternoon!",
            "good evening": "Good evening!",
            "howdy": "Howdy! How can I help you?",
            "namaste": "Namaste! 🙏",
            "hola": "Hola amigo!",
            "bonjour": "Bonjour! Well… I don't know French that much 😅",
            "how are you": "I'm just a bot, but I'm doing great!",
            "how are you doing": "I'm functioning as expected!",
            "what's up": "Just waiting for your message!",
            "hru": "All good, thanks! What about you?",
            "sup": "All good here!",
            "how’s it going": "Going smooth, thanks!"
        }

        self.thanks_and_bye = {
            "thank you": "You're welcome!",
            "thanks": "No problem!",
            "thanks a lot": "Happy to help!",
            "bye": "Goodbye! Take care!",
            "see you": "See you soon!",
            "later": "Catch you later!"
        }

        self.famous_people = {
            "who is elon musk": "CEO of Tesla and SpaceX. Also plays with rockets 😅",
            "who is bill gates": "Co-founder of Microsoft and now a philanthropist.",
            "who is narendra modi": "Prime Minister of India.",
            "who is albert einstein": "One of the greatest physicists who ever lived.",
            "who is taylor swift": "A popular American singer-songwriter."
        }

        self.brands = {
            "what is apple": "A tech company known for the iPhone and Mac.",
            "what is samsung": "A South Korean company making phones, TVs, and more.",
            "what is google": "The world's biggest search engine, and more.",
            "what is microsoft": "Creators of Windows, Office, and Xbox.",
            "what is starlink": "Elon Musk's satellite internet service."
        }

        # Merged data
        self.all_data = {}
        self.all_data.update(self.conversations)
        self.all_data.update(self.thanks_and_bye)
        self.all_data.update(self.famous_people)
        self.all_data.update(self.brands)
