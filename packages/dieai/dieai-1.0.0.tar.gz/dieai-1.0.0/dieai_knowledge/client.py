"""
DieAI Client - Main API Interface
OpenAI-like API for building AI chatbots and intelligent applications
"""

import json
import re
from typing import Dict, List, Any, Optional, Union, Iterator
from .knowledge_base import KnowledgeBase
from .math_solver import MathSolver
from .science_facts import ScienceFacts
from .unit_converter import UnitConverter

class ChatCompletion:
    """Chat completion response object similar to OpenAI's format"""
    def __init__(self, response_data: Dict[str, Any]):
        self.id = response_data.get('id', 'dieai-chat-completion')
        self.object = 'chat.completion'
        self.created = response_data.get('created', 0)
        self.model = response_data.get('model', 'dieai-1.0')
        self.choices = response_data.get('choices', [])
        self.usage = response_data.get('usage', {})

class ChatCompletionChoice:
    """Individual choice in chat completion"""
    def __init__(self, message: Dict[str, Any], finish_reason: str = 'stop'):
        self.index = 0
        self.message = ChatMessage(message)
        self.finish_reason = finish_reason

class ChatMessage:
    """Chat message object"""
    def __init__(self, message_data: Dict[str, Any]):
        self.role = message_data.get('role', 'assistant')
        self.content = message_data.get('content', '')

class DieAI:
    """
    Main DieAI client class - OpenAI-like API for building AI applications
    
    Usage:
        client = DieAI()
        response = client.chat.completions.create(
            model="dieai-1.0",
            messages=[{"role": "user", "content": "What is 2+2?"}]
        )
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize DieAI client
        
        Args:
            api_key: API key (optional for this version)
            base_url: Base URL for API (optional for this version)
        """
        self.api_key = api_key
        self.base_url = base_url
        
        # Initialize knowledge components
        self.knowledge_base = KnowledgeBase()
        self.math_solver = MathSolver()
        self.science_facts = ScienceFacts()
        self.unit_converter = UnitConverter()
        
        # Create chat interface
        self.chat = ChatInterface(self)
    
    def _analyze_query(self, content: str) -> Dict[str, Any]:
        """Analyze user query to determine the best response strategy"""
        content_lower = content.lower()
        
        # Math patterns
        math_patterns = [
            r'\d+\s*[\+\-\*\/]\s*\d+',  # Basic arithmetic
            r'solve|equation|calculate|compute',
            r'what is \d+',
            r'area|perimeter|volume|circumference',
            r'statistics|mean|median|mode|standard deviation'
        ]
        
        # Science patterns
        science_patterns = [
            r'physics|chemistry|biology|force|energy|mass|velocity',
            r'periodic table|element|atom|molecule',
            r'constant|speed of light|avogadro|planck',
            r'formula|law of|newton|einstein'
        ]
        
        # Unit conversion patterns
        conversion_patterns = [
            r'convert|conversion|to|from',
            r'meters?|feet|inches|kilometers?|miles?',
            r'celsius|fahrenheit|kelvin',
            r'pounds?|kilograms?|grams?',
            r'liters?|gallons?|cups?'
        ]
        
        query_type = 'general'
        confidence = 0.5
        
        # Check for math queries
        if any(re.search(pattern, content_lower) for pattern in math_patterns):
            query_type = 'math'
            confidence = 0.8
        
        # Check for science queries
        elif any(re.search(pattern, content_lower) for pattern in science_patterns):
            query_type = 'science'
            confidence = 0.8
        
        # Check for conversion queries
        elif any(re.search(pattern, content_lower) for pattern in conversion_patterns):
            query_type = 'conversion'
            confidence = 0.9
        
        # Check for knowledge base queries
        elif any(word in content_lower for word in ['what', 'how', 'why', 'explain', 'define']):
            query_type = 'knowledge'
            confidence = 0.7
        
        return {
            'type': query_type,
            'confidence': confidence,
            'original_content': content
        }
    
    def _generate_response(self, messages: List[Dict[str, Any]], model: str) -> str:
        """Generate intelligent response based on conversation context"""
        if not messages:
            return "Hello! I'm DieAI, your AI assistant for mathematics, science, and general knowledge. How can I help you today?"
        
        # Get the last user message
        user_message = None
        for message in reversed(messages):
            if message.get('role') == 'user':
                user_message = message.get('content', '')
                break
        
        if not user_message:
            return "I'm here to help with mathematics, science, unit conversions, and general knowledge questions. What would you like to know?"
        
        # Analyze the query
        analysis = self._analyze_query(user_message)
        
        try:
            if analysis['type'] == 'math':
                return self._handle_math_query(user_message)
            elif analysis['type'] == 'science':
                return self._handle_science_query(user_message)
            elif analysis['type'] == 'conversion':
                return self._handle_conversion_query(user_message)
            elif analysis['type'] == 'knowledge':
                return self._handle_knowledge_query(user_message)
            else:
                return self._handle_general_query(user_message)
        except Exception as e:
            return f"I encountered an issue processing your request: {str(e)}. Please try rephrasing your question."
    
    def _handle_math_query(self, query: str) -> str:
        """Handle mathematical queries"""
        # Check for basic arithmetic
        arithmetic_match = re.search(r'(\d+(?:\.\d+)?)\s*([\+\-\*\/])\s*(\d+(?:\.\d+)?)', query)
        if arithmetic_match:
            num1, op, num2 = arithmetic_match.groups()
            try:
                result = self.math_solver.evaluate(f"{num1} {op} {num2}")
                return f"{num1} {op} {num2} = {result}"
            except:
                pass
        
        # Check for equations
        if 'solve' in query.lower() or '=' in query:
            # Extract equation
            equation_match = re.search(r'([^=]+=[^=]+)', query)
            if equation_match:
                equation = equation_match.group(1).strip()
                result = self.math_solver.solve_equation(equation)
                if 'solution' in result:
                    return f"Solution: {result['solution']}"
                elif 'error' in result:
                    return f"I couldn't solve that equation: {result['error']}"
        
        # Check for geometry
        if any(word in query.lower() for word in ['area', 'perimeter', 'volume', 'circumference']):
            if 'circle' in query.lower():
                radius_match = re.search(r'radius\s*(?:of|is|=)?\s*(\d+(?:\.\d+)?)', query)
                if radius_match:
                    radius = float(radius_match.group(1))
                    result = self.math_solver.geometry_calculator('circle', radius=radius)
                    return f"Circle with radius {radius}: Area = {result['area']:.2f}, Circumference = {result['circumference']:.2f}"
        
        # Fallback to knowledge base
        results = self.knowledge_base.search(query)
        if results:
            return f"Here's what I found about your math question:\n\n{results[0]['content'][0]}"
        
        return "I can help with arithmetic, algebra, geometry, and statistics. Could you please provide more specific details about your math problem?"
    
    def _handle_science_query(self, query: str) -> str:
        """Handle science-related queries"""
        # Check for physics calculations
        if 'force' in query.lower() and ('mass' in query.lower() or 'acceleration' in query.lower()):
            mass_match = re.search(r'mass\s*(?:of|is|=)?\s*(\d+(?:\.\d+)?)', query)
            acc_match = re.search(r'acceleration\s*(?:of|is|=)?\s*(\d+(?:\.\d+)?)', query)
            if mass_match and acc_match:
                mass = float(mass_match.group(1))
                acc = float(acc_match.group(1))
                result = self.science_facts.calculate_physics('force', mass=mass, acceleration=acc)
                return f"Force = {result['force']} N (using F = ma with mass = {mass} kg, acceleration = {acc} m/s²)"
        
        # Check for constants
        if 'constant' in query.lower() or 'speed of light' in query.lower():
            constant = self.science_facts.get_constant('c', 'physics')
            if constant:
                return f"Speed of light: {constant['value']} {constant['unit']}"
        
        # Check for periodic table
        element_match = re.search(r'element\s+(\w+)', query, re.IGNORECASE)
        if element_match:
            element = element_match.group(1)
            result = self.science_facts.get_periodic_element(element)
            if result:
                return f"{result['name']} ({result['symbol']}): Atomic number {result['atomic_number']}, Atomic mass {result['atomic_mass']}"
        
        # Search knowledge base
        results = self.knowledge_base.search(query)
        if results:
            return f"Here's what I found:\n\n{results[0]['content'][0]}"
        
        return "I can help with physics, chemistry, biology, and scientific calculations. What specific science topic would you like to explore?"
    
    def _handle_conversion_query(self, query: str) -> str:
        """Handle unit conversion queries"""
        # Pattern: convert X unit1 to unit2
        convert_match = re.search(r'convert\s+(\d+(?:\.\d+)?)\s+(\w+)\s+to\s+(\w+)', query, re.IGNORECASE)
        if convert_match:
            value, from_unit, to_unit = convert_match.groups()
            result = self.unit_converter.convert(float(value), from_unit, to_unit)
            if 'converted_value' in result:
                return f"{value} {from_unit} = {result['converted_value']:.2f} {to_unit}"
            else:
                return f"I couldn't convert {from_unit} to {to_unit}. {result.get('error', '')}"
        
        # Pattern: X unit1 in unit2
        in_match = re.search(r'(\d+(?:\.\d+)?)\s+(\w+)\s+in\s+(\w+)', query, re.IGNORECASE)
        if in_match:
            value, from_unit, to_unit = in_match.groups()
            result = self.unit_converter.convert(float(value), from_unit, to_unit)
            if 'converted_value' in result:
                return f"{value} {from_unit} = {result['converted_value']:.2f} {to_unit}"
        
        return "I can convert between various units (length, mass, temperature, etc.). Try asking 'convert 100 meters to feet' or '25 celsius to fahrenheit'."
    
    def _handle_knowledge_query(self, query: str) -> str:
        """Handle general knowledge queries"""
        results = self.knowledge_base.search(query)
        if results and results[0]['content']:
            # Return the first relevant result
            return results[0]['content'][0]
        
        return "I have comprehensive knowledge in mathematics, science, physics, chemistry, and biology. Could you please be more specific about what you'd like to know?"
    
    def _handle_general_query(self, query: str) -> str:
        """Handle general conversation"""
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        
        if any(greeting in query.lower() for greeting in greetings):
            return "Hello! I'm DieAI, your AI assistant specialized in mathematics, science, and intelligent problem-solving. How can I help you today?"
        
        # Try knowledge base search as fallback
        results = self.knowledge_base.search(query)
        if results and results[0]['content']:
            return results[0]['content'][0]
        
        return "I specialize in mathematics, science, unit conversions, and problem-solving. Feel free to ask me about equations, scientific concepts, or any calculations you need help with!"

class ChatInterface:
    """Chat interface similar to OpenAI's chat API"""
    
    def __init__(self, client: DieAI):
        self.client = client
        self.completions = ChatCompletions(client)

class ChatCompletions:
    """Chat completions endpoint"""
    
    def __init__(self, client: DieAI):
        self.client = client
    
    def create(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[ChatCompletion, Iterator[Dict[str, Any]]]:
        """
        Create a chat completion
        
        Args:
            model: Model name (e.g., 'dieai-1.0')
            messages: List of message objects
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional parameters
        
        Returns:
            ChatCompletion object or stream iterator
        """
        if stream:
            return self._create_stream(model, messages, temperature, max_tokens, **kwargs)
        
        # Generate response
        response_content = self.client._generate_response(messages, model)
        
        # Create response object
        response_data = {
            'id': 'dieai-chat-completion',
            'model': model,
            'choices': [{
                'message': {
                    'role': 'assistant',
                    'content': response_content
                },
                'finish_reason': 'stop'
            }],
            'usage': {
                'prompt_tokens': sum(len(msg.get('content', '').split()) for msg in messages),
                'completion_tokens': len(response_content.split()),
                'total_tokens': sum(len(msg.get('content', '').split()) for msg in messages) + len(response_content.split())
            }
        }
        
        return ChatCompletion(response_data)
    
    def _create_stream(self, model: str, messages: List[Dict[str, Any]], temperature: float, max_tokens: Optional[int], **kwargs) -> Iterator[Dict[str, Any]]:
        """Create streaming response"""
        response_content = self.client._generate_response(messages, model)
        
        # Split response into chunks for streaming
        words = response_content.split()
        for i, word in enumerate(words):
            chunk = {
                'id': 'dieai-chat-completion',
                'object': 'chat.completion.chunk',
                'model': model,
                'choices': [{
                    'index': 0,
                    'delta': {'content': word + ' ' if i < len(words) - 1 else word},
                    'finish_reason': None if i < len(words) - 1 else 'stop'
                }]
            }
            yield chunk