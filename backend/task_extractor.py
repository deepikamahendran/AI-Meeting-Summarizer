"""
Task and action item extraction module
"""

import re
from typing import List, Dict, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Try to load spaCy model
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    logger.info("spaCy model loaded successfully")
except (OSError, ImportError) as e:
    logger.warning(f"spaCy model not available: {e}")
    nlp = None


class TaskExtractor:
    def __init__(self):
        logger.info("Initializing TaskExtractor")
        
        try:
            # Initialize NER pipeline for person extraction
            logger.info("Loading NER model for entity recognition")
            self.ner_pipeline = pipeline(
                "ner",
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                tokenizer="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple",
                device=-1  # Use CPU
            )
            logger.info("NER model loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load NER model: {e}")
            self.ner_pipeline = None
        
        # Common task-related keywords
        self.task_keywords = [
            'will', 'should', 'need to', 'has to', 'must', 'responsible for',
            'assigned to', 'take care of', 'handle', 'complete', 'finish',
            'deliver', 'submit', 'prepare', 'create', 'develop', 'review',
            'update', 'follow up', 'contact', 'schedule', 'organize',
            'implement', 'design', 'test', 'deploy', 'coordinate', 'manage'
        ]
        
        # Time-related keywords for deadline extraction
        self.time_keywords = [
            'by', 'before', 'until', 'deadline', 'due', 'end of week',
            'next week', 'next month', 'tomorrow', 'friday', 'monday',
            'asap', 'immediately', 'soon', 'this week', 'this month',
            'tuesday', 'wednesday', 'thursday', 'saturday', 'sunday'
        ]
        
        # Action verbs for better task detection
        self.action_verbs = [
            'send', 'call', 'email', 'write', 'draft', 'finalize',
            'approve', 'check', 'verify', 'confirm', 'analyze',
            'research', 'investigate', 'plan', 'book', 'reserve'
        ]
    
    async def extract_tasks(self, text: str) -> List[Dict]:
        """
        Extract assigned tasks from meeting transcript
        """
        try:
            logger.info("Starting task extraction")
            
            # Method 1: Rule-based extraction
            rule_based_tasks = self._rule_based_task_extraction(text)
            
            # Method 2: NLP-based extraction (if available)
            nlp_based_tasks = []
            if self.ner_pipeline:
                nlp_based_tasks = self._nlp_based_task_extraction(text)
            
            # Method 3: Pattern-based extraction for common task structures
            pattern_based_tasks = self._pattern_based_task_extraction(text)
            
            # Combine and deduplicate tasks
            all_tasks = rule_based_tasks + nlp_based_tasks + pattern_based_tasks
            unique_tasks = self._deduplicate_tasks(all_tasks)
            
            logger.info(f"Extracted {len(unique_tasks)} unique tasks")
            return unique_tasks[:15]  # Limit to top 15 tasks
        
        except Exception as e:
            logger.error(f"Task extraction failed: {e}")
            return []
    
    async def extract_action_points(self, text: str) -> List[str]:
        """
        Extract action points from meeting transcript
        """
        try:
            logger.info("Starting action point extraction")
            
            action_points = []
            
            # Look for explicit action items
            action_patterns = [
                r'action item[s]?:?\s*([^.!?\n]+)',
                r'action[s]?:?\s*([^.!?\n]+)',
                r'next step[s]?:?\s*([^.!?\n]+)',
                r'follow[- ]?up:?\s*([^.!?\n]+)',
                r'to[- ]?do:?\s*([^.!?\n]+)',
                r'we need to\s+([^.!?\n]+)',
                r'we should\s+([^.!?\n]+)',
                r'let\'s\s+([^.!?\n]+)',
                r'someone should\s+([^.!?\n]+)',
                r'we must\s+([^.!?\n]+)',
                r'it would be good to\s+([^.!?\n]+)'
            ]
            
            for pattern in action_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    cleaned_action = match.strip()
                    if len(cleaned_action) > 10:  # Filter out very short matches
                        action_points.append(cleaned_action.capitalize())
            
            # Extract sentences with imperative mood
            sentences = self._split_into_sentences(text)
            for sentence in sentences:
                if self._is_action_sentence(sentence):
                    action_points.append(sentence.strip())
            
            # Look for decision-based action points
            decision_patterns = [
                r'decided to\s+([^.!?\n]+)',
                r'agreed to\s+([^.!?\n]+)',
                r'committed to\s+([^.!?\n]+)',
                r'will proceed with\s+([^.!?\n]+)'
            ]
            
            for pattern in decision_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    cleaned_action = match.strip()
                    if len(cleaned_action) > 10:
                        action_points.append(f"Decision: {cleaned_action.capitalize()}")
            
            # Remove duplicates and clean up
            unique_actions = list(set(action_points))
            filtered_actions = [action for action in unique_actions if len(action) > 15]
            
            logger.info(f"Extracted {len(filtered_actions)} action points")
            return filtered_actions[:12]  # Limit to 12 action points
        
        except Exception as e:
            logger.error(f"Action point extraction failed: {e}")
            return []
    
    async def extract_participants(self, text: str) -> List[str]:
        """
        Extract participant names from meeting transcript
        """
        try:
            logger.info("Starting participant extraction")
            
            participants = set()
            
            # Method 1: Use NER pipeline if available
            if self.ner_pipeline:
                entities = self.ner_pipeline(text)
                for entity in entities:
                    if entity['entity_group'] == 'PER':
                        name = entity['word'].replace('##', '')
                        if len(name) > 2:
                            participants.add(name.title())
            
            # Method 2: Use spaCy if available
            if nlp:
                doc = nlp(text)
                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        participants.add(ent.text.title())
            
            # Method 3: Pattern matching for speaker labels
            speaker_patterns = [
                r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?):',  # "John Smith:"
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+said',  # "John said"
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+mentioned',  # "John mentioned"
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+will',  # "John will"
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+can',  # "John can"
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+should',  # "John should"
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+needs? to',  # "John needs to"
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+is responsible',  # "John is responsible"
            ]
            
            for pattern in speaker_patterns:
                matches = re.findall(pattern, text, re.MULTILINE)
                for match in matches:
                    if isinstance(match, tuple):
                        name = match[0]
                    else:
                        name = match
                    
                    # Filter out common words that might be matched
                    excluded_words = ['the', 'and', 'but', 'for', 'you', 'this', 'that', 'we', 'they', 'it', 'meeting', 'team']
                    if name.lower() not in excluded_words and len(name) > 2:
                        participants.add(name.title())
            
            # Filter out very common false positives
            filtered_participants = []
            for participant in participants:
                if not any(word in participant.lower() for word in ['meeting', 'team', 'group', 'everyone', 'somebody', 'anyone']):
                    filtered_participants.append(participant)
            
            logger.info(f"Extracted {len(filtered_participants)} participants")
            return filtered_participants[:12]  # Limit to 12 participants
        
        except Exception as e:
            logger.error(f"Participant extraction failed: {e}")
            return []
    
    def _rule_based_task_extraction(self, text: str) -> List[Dict]:
        """
        Extract tasks using rule-based approach
        """
        tasks = []
        sentences = self._split_into_sentences(text)
        
        for sentence in sentences:
            # Look for assignment patterns
            assignment_patterns = [
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+will\s+([^.!?\n]+)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+should\s+([^.!?\n]+)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+needs? to\s+([^.!?\n]+)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+is responsible for\s+([^.!?\n]+)',
                r'assign(?:ed)?\s+([^.!?\n]+?)\s+to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+can\s+([^.!?\n]+)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+must\s+([^.!?\n]+)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+has to\s+([^.!?\n]+)',
            ]
            
            for pattern in assignment_patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    if len(match) == 2:
                        if 'assign' in pattern:
                            task_desc, assignee = match  # Reversed for "assign X to Y" pattern
                        else:
                            assignee, task_desc = match
                            
                        deadline = self._extract_deadline(sentence)
                        priority = self._determine_priority(sentence)
                        
                        tasks.append({
                            "assignee": assignee.title(),
                            "task": task_desc.strip(),
                            "deadline": deadline,
                            "priority": priority
                        })
        
        return tasks
    
    def _pattern_based_task_extraction(self, text: str) -> List[Dict]:
        """
        Extract tasks using common meeting patterns
        """
        tasks = []
        sentences = self._split_into_sentences(text)
        
        for sentence in sentences:
            # Look for action verb patterns
            for verb in self.action_verbs:
                pattern = rf'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:will|should|can|must)?\s*{verb}\s+([^.!?\n]+)'
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    assignee, task_desc = match
                    deadline = self._extract_deadline(sentence)
                    priority = self._determine_priority(sentence)
                    
                    tasks.append({
                        "assignee": assignee.title(),
                        "task": f"{verb.capitalize()} {task_desc.strip()}",
                        "deadline": deadline,
                        "priority": priority
                    })
        
        return tasks
    
    def _nlp_based_task_extraction(self, text: str) -> List[Dict]:
        """
        Extract tasks using NLP-based approach
        """
        # Advanced NLP-based extraction could be implemented here
        # For now, we rely on rule-based and pattern-based methods
        return []
    
    def _extract_deadline(self, sentence: str) -> str:
        """
        Extract deadline information from sentence
        """
        # Look for explicit dates
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{4}',
            r'\d{4}-\d{2}-\d{2}',
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}',
            r'\d{1,2}(?:st|nd|rd|th)?\s+(january|february|march|april|may|june|july|august|september|october|november|december)',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                return match.group()
        
        # Look for relative time expressions
        relative_patterns = [
            r'by\s+(next\s+week|this\s+week|friday|monday|tuesday|wednesday|thursday|saturday|sunday)',
            r'(end of\s+week|end of\s+month)',
            r'(tomorrow|asap|immediately|soon)',
            r'(next\s+monday|next\s+tuesday|next\s+wednesday|next\s+thursday|next\s+friday)',
            r'by\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
        ]
        
        for pattern in relative_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                return self._convert_relative_date(match.group())
        
        # Default to next week if no specific deadline found
        next_week = datetime.now() + timedelta(days=7)
        return next_week.strftime("%Y-%m-%d")
    
    def _convert_relative_date(self, relative_date: str) -> str:
        """
        Convert relative date expressions to actual dates
        """
        relative_date = relative_date.lower()
        today = datetime.now()
        
        if 'tomorrow' in relative_date:
            target_date = today + timedelta(days=1)
        elif 'next week' in relative_date:
            target_date = today + timedelta(days=7)
        elif 'end of week' in relative_date:
            days_until_friday = 4 - today.weekday()
            if days_until_friday < 0:
                days_until_friday += 7
            target_date = today + timedelta(days=days_until_friday)
        elif any(day in relative_date for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']):
            # Map day names to weekday numbers
            day_map = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
            for day_name, day_num in day_map.items():
                if day_name in relative_date:
                    days_ahead = day_num - today.weekday()
                    if days_ahead <= 0:  # Target day already happened this week
                        days_ahead += 7
                    target_date = today + timedelta(days=days_ahead)
                    break
        else:
            target_date = today + timedelta(days=7)  # Default to next week
        
        return target_date.strftime("%Y-%m-%d")
    
    def _determine_priority(self, sentence: str) -> str:
        """
        Determine task priority based on keywords
        """
        sentence_lower = sentence.lower()
        
        high_priority_keywords = ['urgent', 'asap', 'immediately', 'critical', 'high priority', 'deadline', 'must', 'emergency']
        medium_priority_keywords = ['important', 'soon', 'this week', 'next week', 'should', 'needs to']
        
        for keyword in high_priority_keywords:
            if keyword in sentence_lower:
                return 'high'
        
        for keyword in medium_priority_keywords:
            if keyword in sentence_lower:
                return 'medium'
        
        return 'low'
    
    def _is_action_sentence(self, sentence: str) -> bool:
        """
        Determine if a sentence describes an action item
        """
        sentence_lower = sentence.lower().strip()
        
        # Check for imperative mood indicators
        imperative_starters = [
            'we need to', 'we should', 'let\'s', 'please', 'make sure',
            'don\'t forget', 'remember to', 'ensure that', 'follow up'
            'someone should', 'we must', 'it would be good to', 'we have to'
        ]
        
        for starter in imperative_starters:
            if sentence_lower.startswith(starter):
                return True
        
        # Check for action keywords
        for keyword in self.task_keywords:
            if keyword in sentence_lower:
                return True
        
        # Check for action verbs
        for verb in self.action_verbs:
            if verb in sentence_lower:
                return True
        
        return False
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences
        """
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _deduplicate_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """
        Remove duplicate tasks based on similarity
        """
        unique_tasks = []
        
        for task in tasks:
            is_duplicate = False
            for existing_task in unique_tasks:
                # Simple similarity check based on task description
                if self._are_tasks_similar(task['task'], existing_task['task']):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_tasks.append(task)
        
        return unique_tasks
    
    def _are_tasks_similar(self, task1: str, task2: str, threshold: float = 0.7) -> bool:
        """
        Check if two tasks are similar
        """
        # Simple word overlap similarity
        words1 = set(task1.lower().split())
        words2 = set(task2.lower().split())
        
        if not words1 or not words2:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union)
        return similarity >= threshold