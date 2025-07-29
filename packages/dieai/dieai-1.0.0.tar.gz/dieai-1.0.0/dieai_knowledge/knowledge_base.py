"""
Knowledge Base Module
Main interface for accessing mathematical and scientific knowledge
"""
import os
import re
from typing import Dict, List, Optional, Any

class KnowledgeBase:
    """
    Central knowledge base for mathematics and science facts
    """
    
    def __init__(self, data_file: str = None):
        """Initialize knowledge base with data file"""
        if data_file is None:
            # Default to data.txt in parent directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            data_file = os.path.join(parent_dir, 'data.txt')
        
        self.data_file = data_file
        self.knowledge = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict[str, str]:
        """Load knowledge from data file"""
        knowledge = {}
        current_section = None
        current_content = []
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('## '):
                        # Save previous section
                        if current_section:
                            knowledge[current_section] = '\n'.join(current_content)
                        # Start new section
                        current_section = line[3:].strip()
                        current_content = []
                    elif line.startswith('### '):
                        # Subsection
                        current_content.append(line)
                    elif line and not line.startswith('#'):
                        # Content line
                        current_content.append(line)
                
                # Save last section
                if current_section:
                    knowledge[current_section] = '\n'.join(current_content)
        
        except FileNotFoundError:
            print(f"Warning: Knowledge file {self.data_file} not found")
            knowledge = self._get_default_knowledge()
        
        return knowledge
    
    def _get_default_knowledge(self) -> Dict[str, str]:
        """Fallback knowledge if file not found"""
        return {
            "MATHEMATICS": "Basic arithmetic, algebra, geometry, calculus, and statistics",
            "PHYSICS": "Mechanics, thermodynamics, electromagnetism, and quantum physics",
            "CHEMISTRY": "Atomic structure, bonding, reactions, and thermochemistry",
            "BIOLOGY": "Cell biology, genetics, evolution, and ecology"
        }
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search knowledge base for relevant information"""
        results = []
        query_lower = query.lower()
        
        for section, content in self.knowledge.items():
            content_lower = content.lower()
            if query_lower in content_lower:
                # Find sentences containing the query
                sentences = content.split('.')
                relevant_sentences = [s.strip() for s in sentences if query_lower in s.lower()]
                
                if relevant_sentences:
                    results.append({
                        'section': section,
                        'content': relevant_sentences[:3],  # Top 3 relevant sentences
                        'relevance_score': self._calculate_relevance(query_lower, content_lower)
                    })
        
        # Sort by relevance
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:5]  # Top 5 results
    
    def _calculate_relevance(self, query: str, content: str) -> float:
        """Calculate relevance score for search results"""
        # Simple relevance based on frequency of query terms
        query_words = query.split()
        total_score = 0
        
        for word in query_words:
            if len(word) > 2:  # Ignore very short words
                count = content.count(word)
                total_score += count
        
        return total_score / len(content) if content else 0
    
    def get_section(self, section_name: str) -> Optional[str]:
        """Get content from a specific section"""
        return self.knowledge.get(section_name.upper())
    
    def get_all_sections(self) -> List[str]:
        """Get all available section names"""
        return list(self.knowledge.keys())
    
    def find_formulas(self, subject: str = None) -> List[str]:
        """Extract mathematical and scientific formulas"""
        formulas = []
        
        # Patterns for common formula formats
        formula_patterns = [
            r'[A-Za-z]+\s*=\s*[^.]+',  # Basic equations like F = ma
            r'[A-Za-z]+²\s*[+\-]\s*[A-Za-z]+²\s*=\s*[A-Za-z]+²',  # Pythagorean type
            r'∫[^∫]+dx',  # Integrals
            r'd/dx\([^)]+\)',  # Derivatives
        ]
        
        search_sections = [subject.upper()] if subject else self.knowledge.keys()
        
        for section in search_sections:
            if section in self.knowledge:
                content = self.knowledge[section]
                for pattern in formula_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        formulas.append({
                            'formula': match.strip(),
                            'section': section
                        })
        
        return formulas
    
    def get_constants(self) -> Dict[str, float]:
        """Get mathematical and scientific constants"""
        constants = {
            'pi': 3.14159265359,
            'e': 2.71828182846,
            'c': 299792458,  # Speed of light m/s
            'h': 6.62607015e-34,  # Planck constant
            'G': 6.67430e-11,  # Gravitational constant
            'Na': 6.02214076e23,  # Avogadro number
            'k': 1.380649e-23,  # Boltzmann constant
            'R': 8.314462618,  # Gas constant J/(mol·K)
        }
        return constants
    
    def explain_concept(self, concept: str) -> str:
        """Get explanation for a mathematical or scientific concept"""
        results = self.search(concept)
        
        if results:
            explanation = f"# {concept.title()}\n\n"
            for result in results[:2]:  # Top 2 results
                explanation += f"## From {result['section']}:\n"
                for sentence in result['content']:
                    explanation += f"- {sentence.strip()}\n"
                explanation += "\n"
            return explanation
        else:
            return f"No specific information found for '{concept}'. Try searching for related terms."