# Copyright (c) 2025 Prachi Sheth
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
This script is part of uncertainty quantification code in repository (https://github.com/prachi0711/Stress-Management-using-Physiological-Signals-and-conversational-agents/)

Source: 
    https://github.com/prachi0711/Stress-Management-using-Physiological-Signals-and-conversational-agents/blob/main/uncertainty_quantification/dialogue_manager.py

Author: 
    Prachi Sheth (https://github.com/prachi0711)
"""

class DialogueManager:
    def __init__(self, entropy_threshold=0.45, use_time=True):
        self.entropy_threshold = entropy_threshold
        self.use_time = use_time
        self.user_states = {}  
    
    def _init_user_state(self, user_id):
        self.user_states[user_id] = {
            "last_timestamp": None,
            "dialogue_history": [],
            "uncertain_count": 0,
            "feedback_history": [],
            "awaiting_feedback": False,
            "last_response": None,
            "response_type": None  
        }
    
    def _handle_feedback(self, user_state, feedback):
        """Process feedback and generate adaptive response."""
        user_state["feedback_history"].append(feedback)
        user_state["awaiting_feedback"] = False
        
        if user_state["response_type"] == "offer_help":
            if feedback == "yes":
                return "Great! Let's begin with a 30-second breathing exercise. Breathe in... and out..."
            elif feedback == "no":
                return "Okay, no problem. Let me know if you change your mind."
            else:
                return "I didn't understand your response. Please say 'yes' or 'no' if you'd like a breathing exercise."
        
        # uncertainty feedback
        if feedback == "stressed":
            return "Thanks for telling me. Let's try a short breathing exercise together. Would you like to try it?"
        elif feedback == "calm":
            return "Good to hear that you feel calm. Keep it up!"
        elif feedback == "need_help":
            return "Alright, I'll suggest a quick stress-relief activity. Would you like a breathing exercise?"
        elif feedback == "no_help":
            return "Okay, I'll give you some space. Let me know if you need support later."
        else:
            return "Thanks for sharing. I'll keep that in mind."

    def get_response(self, user_id, entropy_val, pred_label, timestamp=None, user_feedback=None, sample_idx=None):
        if user_id not in self.user_states:
            self._init_user_state(user_id)
        
        user_state = self.user_states[user_id]

        if user_feedback is not None:
            response = self._handle_feedback(user_state, user_feedback)
            user_state["dialogue_history"].append((timestamp, pred_label, entropy_val, response, user_feedback, sample_idx))
            
            if "Would you like" in response or "breathing exercise" in response.lower():
                user_state["awaiting_feedback"] = True
                user_state["response_type"] = "offer_help"
                user_state["last_response"] = response
                
            return response, user_state["uncertain_count"]

        if user_state["awaiting_feedback"]:
            return user_state["last_response"], user_state["uncertain_count"]

        if entropy_val > self.entropy_threshold:
            user_state["uncertain_count"] += 1
            
            if user_state["uncertain_count"] >= 5:
                response = "I am uncertain about your stress level. Can you please tell me how you feel?"
                user_state["awaiting_feedback"] = True
                user_state["last_response"] = response
                user_state["response_type"] = "uncertainty"
            else:
                response = "I'm getting mixed signals about your stress level. Let me observe a bit more."
        else:
            user_state["uncertain_count"] = 0
            if pred_label == 1:
                response = "You seem stressed. Would you like a short breathing exercise?"
                user_state["awaiting_feedback"] = True
                user_state["response_type"] = "offer_help"
            else:
                response = "You seem calm - nice. Keep doing what you're doing!"
            
        user_state["last_response"] = response
        user_state["dialogue_history"].append((timestamp, pred_label, entropy_val, response, user_feedback, sample_idx))
        return response, user_state["uncertain_count"]

    def reset_feedback_state(self, user_id):
        if user_id in self.user_states:
            self.user_states[user_id]["awaiting_feedback"] = False
            self.user_states[user_id]["last_response"] = None
            self.user_states[user_id]["response_type"] = None