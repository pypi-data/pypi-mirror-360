"""
Chatbot Builder Module
Tools for creating intelligent chatbots with DieAI
"""

import json
import time
from typing import Dict, List, Any, Optional, Callable
from .client import DieAI

class ChatBot:
    """
    Intelligent chatbot builder using DieAI
    Perfect for creating educational, math, science, and general purpose chatbots
    """
    
    def __init__(self, name: str = "DieAI Bot", personality: str = "helpful", knowledge_domains: List[str] = None):
        """
        Initialize chatbot
        
        Args:
            name: Chatbot name
            personality: Bot personality (helpful, friendly, professional, educational)
            knowledge_domains: Domains of expertise (math, science, general, etc.)
        """
        self.name = name
        self.personality = personality
        self.knowledge_domains = knowledge_domains or ["math", "science", "general"]
        self.client = DieAI()
        self.conversation_history = []
        self.user_context = {}
        self.custom_responses = {}
        self.plugins = []
        
        # Personality templates
        self.personality_prompts = {
            "helpful": "I'm a helpful AI assistant specializing in mathematics and science.",
            "friendly": "Hi there! I'm a friendly AI who loves helping with math and science questions.",
            "professional": "I am a professional AI assistant with expertise in mathematical and scientific domains.",
            "educational": "I'm an educational AI tutor here to help you learn math and science concepts.",
            "creative": "I'm a creative AI assistant who makes learning math and science fun and engaging!",
            "patient": "I'm a patient AI tutor who will work with you step by step to understand concepts."
        }
    
    def set_system_prompt(self, prompt: str):
        """Set custom system prompt for the chatbot"""
        self.system_prompt = prompt
    
    def add_custom_response(self, trigger: str, response: str):
        """Add custom responses for specific triggers"""
        self.custom_responses[trigger.lower()] = response
    
    def add_plugin(self, plugin: Callable):
        """Add custom plugin functionality"""
        self.plugins.append(plugin)
    
    def chat(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """
        Process user input and generate response
        
        Args:
            user_input: User's message
            context: Additional context for the conversation
        
        Returns:
            Bot's response
        """
        # Update user context
        if context:
            self.user_context.update(context)
        
        # Check for custom responses first
        for trigger, response in self.custom_responses.items():
            if trigger in user_input.lower():
                return response
        
        # Run plugins
        for plugin in self.plugins:
            try:
                plugin_response = plugin(user_input, self.user_context)
                if plugin_response:
                    return plugin_response
            except:
                continue
        
        # Add personality context to conversation
        system_message = self._get_system_message()
        
        # Build messages for API
        messages = [{"role": "system", "content": system_message}]
        
        # Add recent conversation history (last 10 messages)
        recent_history = self.conversation_history[-10:] if len(self.conversation_history) > 10 else self.conversation_history
        messages.extend(recent_history)
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        try:
            # Get response from DieAI
            response = self.client.chat.completions.create(
                model="dieai-1.0",
                messages=messages
            )
            
            bot_response = response.choices[0].message.content
            
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": bot_response})
            
            return bot_response
            
        except Exception as e:
            return f"I encountered an issue: {str(e)}. Please try rephrasing your question."
    
    def _get_system_message(self) -> str:
        """Generate system message based on personality and domains"""
        base_prompt = self.personality_prompts.get(self.personality, self.personality_prompts["helpful"])
        
        domain_info = ""
        if "math" in self.knowledge_domains:
            domain_info += " I can solve equations, calculate geometry, and help with statistics."
        if "science" in self.knowledge_domains:
            domain_info += " I know physics, chemistry, biology, and scientific constants."
        if "general" in self.knowledge_domains:
            domain_info += " I can help with general knowledge and unit conversions."
        
        return f"{base_prompt}{domain_info} My name is {self.name}."
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation"""
        return {
            "total_messages": len(self.conversation_history),
            "user_messages": len([msg for msg in self.conversation_history if msg["role"] == "user"]),
            "bot_messages": len([msg for msg in self.conversation_history if msg["role"] == "assistant"]),
            "last_interaction": self.conversation_history[-1] if self.conversation_history else None
        }
    
    def save_conversation(self, filename: str):
        """Save conversation to file"""
        conversation_data = {
            "bot_name": self.name,
            "personality": self.personality,
            "knowledge_domains": self.knowledge_domains,
            "conversation": self.conversation_history,
            "timestamp": time.time()
        }
        
        with open(filename, 'w') as f:
            json.dump(conversation_data, f, indent=2)
    
    def load_conversation(self, filename: str):
        """Load conversation from file"""
        try:
            with open(filename, 'r') as f:
                conversation_data = json.load(f)
            
            self.conversation_history = conversation_data.get("conversation", [])
            return True
        except:
            return False

class AIRobot:
    """
    AI Robot controller using DieAI for intelligent decision making
    Perfect for educational robots, smart home systems, and autonomous devices
    """
    
    def __init__(self, robot_name: str = "DieAI Robot", capabilities: List[str] = None):
        """
        Initialize AI Robot
        
        Args:
            robot_name: Name of the robot
            capabilities: List of robot capabilities (movement, sensors, speech, etc.)
        """
        self.robot_name = robot_name
        self.capabilities = capabilities or ["speech", "calculation", "problem_solving"]
        self.client = DieAI()
        self.state = {
            "mode": "idle",
            "last_command": None,
            "sensor_data": {},
            "memory": []
        }
        self.command_handlers = {}
        self.sensor_processors = {}
    
    def register_command_handler(self, command: str, handler: Callable):
        """Register a command handler for robot actions"""
        self.command_handlers[command.lower()] = handler
    
    def register_sensor_processor(self, sensor_type: str, processor: Callable):
        """Register a sensor data processor"""
        self.sensor_processors[sensor_type] = processor
    
    def process_voice_command(self, voice_input: str) -> Dict[str, Any]:
        """
        Process voice commands and generate intelligent responses
        
        Args:
            voice_input: Voice command from user
        
        Returns:
            Response with action and speech
        """
        # Analyze command using DieAI
        messages = [
            {
                "role": "system", 
                "content": f"You are {self.robot_name}, an intelligent robot with capabilities: {', '.join(self.capabilities)}. "
                          "Analyze voice commands and suggest appropriate actions. "
                          "For math/science questions, provide detailed answers. "
                          "For robot commands, suggest specific actions."
            },
            {"role": "user", "content": voice_input}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="dieai-1.0",
                messages=messages
            )
            
            ai_response = response.choices[0].message.content
            
            # Extract potential commands
            command_type = self._classify_command(voice_input)
            
            result = {
                "speech_response": ai_response,
                "command_type": command_type,
                "confidence": 0.8,
                "suggested_action": self._suggest_action(command_type, voice_input),
                "timestamp": time.time()
            }
            
            # Store in memory
            self.state["memory"].append({
                "input": voice_input,
                "response": ai_response,
                "timestamp": time.time()
            })
            
            # Keep memory manageable
            if len(self.state["memory"]) > 50:
                self.state["memory"] = self.state["memory"][-30:]
            
            return result
            
        except Exception as e:
            return {
                "speech_response": f"I encountered an error processing your command: {str(e)}",
                "command_type": "error",
                "confidence": 0.0,
                "suggested_action": None,
                "timestamp": time.time()
            }
    
    def process_sensor_data(self, sensor_type: str, data: Any) -> Dict[str, Any]:
        """Process sensor data and make intelligent decisions"""
        if sensor_type in self.sensor_processors:
            return self.sensor_processors[sensor_type](data)
        
        # Default processing - store and analyze
        self.state["sensor_data"][sensor_type] = {
            "value": data,
            "timestamp": time.time()
        }
        
        return {
            "status": "stored",
            "sensor_type": sensor_type,
            "data": data,
            "analysis": self._analyze_sensor_data(sensor_type, data)
        }
    
    def make_decision(self, situation: str, options: List[str] = None) -> Dict[str, Any]:
        """
        Make intelligent decisions based on current situation
        
        Args:
            situation: Description of current situation
            options: Available options (optional)
        
        Returns:
            Decision with reasoning
        """
        # Build context message
        context = f"Robot: {self.robot_name}\n"
        context += f"Capabilities: {', '.join(self.capabilities)}\n"
        context += f"Current situation: {situation}\n"
        
        if options:
            context += f"Available options: {', '.join(options)}\n"
        
        if self.state["sensor_data"]:
            context += f"Sensor data: {self.state['sensor_data']}\n"
        
        messages = [
            {
                "role": "system",
                "content": "You are an intelligent robot making decisions. Consider safety, efficiency, and the robot's capabilities. "
                          "Provide clear reasoning for your decisions."
            },
            {"role": "user", "content": f"Help me decide what to do: {context}"}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="dieai-1.0",
                messages=messages
            )
            
            decision_text = response.choices[0].message.content
            
            return {
                "decision": decision_text,
                "situation": situation,
                "available_options": options,
                "reasoning": decision_text,
                "confidence": 0.85,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "decision": "Unable to make decision due to error",
                "error": str(e),
                "confidence": 0.0,
                "timestamp": time.time()
            }
    
    def _classify_command(self, command: str) -> str:
        """Classify the type of command"""
        command_lower = command.lower()
        
        if any(word in command_lower for word in ["move", "go", "turn", "stop", "walk"]):
            return "movement"
        elif any(word in command_lower for word in ["calculate", "what is", "solve", "compute"]):
            return "calculation"
        elif any(word in command_lower for word in ["tell me", "explain", "what", "how", "why"]):
            return "information"
        elif any(word in command_lower for word in ["hello", "hi", "good morning", "good afternoon"]):
            return "greeting"
        else:
            return "general"
    
    def _suggest_action(self, command_type: str, command: str) -> Optional[str]:
        """Suggest specific action based on command type"""
        suggestions = {
            "movement": "Execute movement command using motor controls",
            "calculation": "Process mathematical calculation and speak result",
            "information": "Retrieve and speak requested information",
            "greeting": "Respond with friendly greeting",
            "general": "Process command and provide appropriate response"
        }
        
        return suggestions.get(command_type)
    
    def _analyze_sensor_data(self, sensor_type: str, data: Any) -> str:
        """Analyze sensor data and provide insights"""
        analysis_templates = {
            "temperature": f"Temperature reading: {data}°C",
            "distance": f"Object detected at {data}cm distance",
            "light": f"Light level: {data} lux",
            "sound": f"Sound level: {data} dB",
            "motion": f"Motion detected: {data}",
            "camera": "Visual data received for processing"
        }
        
        return analysis_templates.get(sensor_type, f"Sensor data received: {data}")
    
    def get_robot_status(self) -> Dict[str, Any]:
        """Get current robot status"""
        return {
            "name": self.robot_name,
            "capabilities": self.capabilities,
            "current_state": self.state,
            "memory_items": len(self.state["memory"]),
            "active_sensors": list(self.state["sensor_data"].keys()),
            "registered_commands": list(self.command_handlers.keys())
        }

class ConversationAnalyzer:
    """
    Analyze conversations for insights and improvements
    """
    
    def __init__(self):
        self.client = DieAI()
    
    def analyze_conversation(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Analyze conversation for patterns and insights"""
        if not conversation_history:
            return {"error": "No conversation data provided"}
        
        user_messages = [msg for msg in conversation_history if msg["role"] == "user"]
        assistant_messages = [msg for msg in conversation_history if msg["role"] == "assistant"]
        
        # Analyze conversation content
        conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-10:]])
        
        analysis_prompt = f"""
        Analyze this conversation and provide insights:
        
        {conversation_text}
        
        Please analyze:
        1. Main topics discussed
        2. Types of questions asked
        3. User's learning progress
        4. Suggestions for improvement
        """
        
        try:
            response = self.client.chat.completions.create(
                model="dieai-1.0",
                messages=[
                    {"role": "system", "content": "You are an expert conversation analyst. Provide detailed insights about educational conversations."},
                    {"role": "user", "content": analysis_prompt}
                ]
            )
            
            insights = response.choices[0].message.content
            
            return {
                "total_messages": len(conversation_history),
                "user_messages": len(user_messages),
                "assistant_messages": len(assistant_messages),
                "insights": insights,
                "conversation_length": len(conversation_text),
                "analysis_timestamp": time.time()
            }
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}