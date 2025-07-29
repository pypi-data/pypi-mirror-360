import difflib

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
