"""
Entity recognition engine for extracting people, projects, topics, and tasks
"""
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class EntityMatch:
    """Represents a matched entity in text"""
    entity_type: str  # person, project, topic, task
    name: str
    confidence: float
    context: str
    start_pos: int
    end_pos: int
    original_text: str


@dataclass
class TaskMatch:
    """Represents a matched task in text"""
    content: str
    confidence: float
    context: str
    start_pos: int
    end_pos: int
    original_text: str


class EntityRecognitionEngine:
    """Engine for recognizing entities and tasks in natural language text"""
    
    def __init__(self):
        # Entity patterns from CLAUDE.md demo validation
        self.person_patterns = [
            r"@(\w+)",  # @mentions - High confidence (90%)
            r"(?:meeting\s+with|talk\s+to|contact|call|email)\s+(\w+)",  # Natural mentions
            r"(?:from|by|with)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",  # Name patterns
        ]
        
        self.project_patterns = [
            r"#([\w-]+)",  # #hashtags - Very high confidence (95%)
            r"(?:project|initiative)[\s\-:]*([a-zA-Z][\w\s-]+?)(?:\s|$|\.|,)",  # Project mentions
            r"([A-Z][\w\s]+?)\s+(?:project|integration|platform|system)",  # Named projects
        ]
        
        self.topic_patterns = [
            r"(?:research|study|learn\s+about|understand)\s+([a-zA-Z][\w\s]+?)(?:\s|$|\.|,)",  # Research topics
            r"([a-z]+\s+(?:learning|models?|analysis|optimization|design))",  # Technical topics
            r"(statistical\s+[\w\s]+|machine\s+learning|quantum\s+computing)",  # Academic topics
        ]
        
        # Task patterns from CLAUDE.md demo validation
        self.task_patterns = [
            r"(?:follow up|follow-up)\s+(?:with\s+|on\s+|about\s+)(.+?)(?:\.|$)",
            r"(?:need to|should|must|will)\s+(.+?)(?:\.|$)", 
            r"(?:todo|to-do|task):\s*(.+?)(?:\.|$)",
            r"^TODO:?\s*(.+?)(?:\.|$)",  # TODO at start of line
            r"^-\s*TODO:?\s*(.+?)(?:\.|$)",  # Bullet point TODO
            r"^\*\s*TODO:?\s*(.+?)(?:\.|$)",  # Asterisk bullet TODO
            r"(?<=\s)TODO:?\s*(.+?)(?:\.|$)",  # TODO after whitespace
        ]
    
    def extract_entities(self, text: str) -> List[EntityMatch]:
        """Extract all entities from text"""
        entities = []
        
        # Extract people (@mentions and natural language)
        entities.extend(self._extract_people(text))
        
        # Extract projects (#hashtags and natural language)
        entities.extend(self._extract_projects(text))
        
        # Extract topics (research and technical concepts)
        entities.extend(self._extract_topics(text))
        
        return entities
    
    def extract_tasks(self, text: str) -> List[TaskMatch]:
        """Extract tasks from text"""
        tasks = []
        
        for pattern in self.task_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                task_content = match.group(1).strip()
                if len(task_content) > 3:  # Filter out very short matches
                    context = self._get_context(text, match.start(), match.end())
                    tasks.append(TaskMatch(
                        content=task_content,
                        confidence=0.8,  # High confidence for pattern-based extraction
                        context=context,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        original_text=match.group(0)
                    ))
        
        return tasks
    
    def _extract_people(self, text: str) -> List[EntityMatch]:
        """Extract person entities from text"""
        people = []
        
        # @mentions - High confidence (90%)
        mentions = re.finditer(r"@(\w+)", text)
        for match in mentions:
            name = match.group(1)
            context = self._get_context(text, match.start(), match.end())
            people.append(EntityMatch(
                entity_type="person",
                name=name,
                confidence=0.9,
                context=context,
                start_pos=match.start(),
                end_pos=match.end(),
                original_text=match.group(0)
            ))
        
        # Natural language mentions - Medium confidence (70%)
        natural_patterns = [
            r"(?:meeting\s+with|talk\s+to|contact|call|email)\s+(\w+)",
            r"(?:from|by|with)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)"
        ]
        
        for pattern in natural_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.group(1)
                context = self._get_context(text, match.start(), match.end())
                people.append(EntityMatch(
                    entity_type="person",
                    name=name,
                    confidence=0.7,
                    context=context,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    original_text=match.group(0)
                ))
        
        return people
    
    def _extract_projects(self, text: str) -> List[EntityMatch]:
        """Extract project entities from text"""
        projects = []
        
        # #hashtags - Very high confidence (95%)
        hashtags = re.finditer(r"#([\w-]+)", text)
        for match in hashtags:
            name = match.group(1).replace("-", " ").replace("_", " ").title()
            context = self._get_context(text, match.start(), match.end())
            projects.append(EntityMatch(
                entity_type="project",
                name=name,
                confidence=0.95,
                context=context,
                start_pos=match.start(),
                end_pos=match.end(),
                original_text=match.group(0)
            ))
        
        # Natural project mentions - Medium confidence (70%)
        project_patterns = [
            r"(?:project|initiative)[\s\-:]*([a-zA-Z][\w\s-]+?)(?:\s|$|\.|,)",
            r"([A-Z][\w\s]+?)\s+(?:project|integration|platform|system)"
        ]
        
        for pattern in project_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.group(1).strip()
                if len(name) > 2:  # Filter out very short matches
                    context = self._get_context(text, match.start(), match.end())
                    projects.append(EntityMatch(
                        entity_type="project",
                        name=name,
                        confidence=0.7,
                        context=context,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        original_text=match.group(0)
                    ))
        
        return projects
    
    def _extract_topics(self, text: str) -> List[EntityMatch]:
        """Extract topic entities from text"""
        topics = []
        
        # Research and academic topics - Medium confidence (60-80%)
        topic_patterns = [
            (r"(?:research|study|learn\s+about|understand)\s+([a-zA-Z][\w\s]+?)(?:\s|$|\.|,)", 0.7),
            (r"([a-z]+\s+(?:learning|models?|analysis|optimization|design))", 0.8),
            (r"(statistical\s+[\w\s]+|machine\s+learning|quantum\s+computing)", 0.9),
        ]
        
        for pattern, confidence in topic_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.group(1).strip()
                if len(name) > 3:  # Filter out very short matches
                    context = self._get_context(text, match.start(), match.end())
                    topics.append(EntityMatch(
                        entity_type="topic",
                        name=name,
                        confidence=confidence,
                        context=context,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        original_text=match.group(0)
                    ))
        
        return topics
    
    def _get_context(self, text: str, start: int, end: int, context_length: int = 50) -> str:
        """Get surrounding context for a match"""
        context_start = max(0, start - context_length)
        context_end = min(len(text), end + context_length)
        return text[context_start:context_end].strip()
    
    def process_text(self, text: str) -> Dict[str, Any]:
        """Process text and return all extracted entities and tasks"""
        entities = self.extract_entities(text)
        tasks = self.extract_tasks(text)
        
        # Group entities by type
        entities_by_type = {
            "people": [e for e in entities if e.entity_type == "person"],
            "projects": [e for e in entities if e.entity_type == "project"], 
            "topics": [e for e in entities if e.entity_type == "topic"],
        }
        
        return {
            "entities": entities_by_type,
            "tasks": tasks,
            "total_entities": len(entities),
            "total_tasks": len(tasks)
        }