# classwork_controller.py (refactored)
from typing import List, Dict, Optional
from frontend.services.classwork_service import ClassworkService

class ClassworkController:
    def __init__(self, service: Optional[ClassworkService] = None):
        """Initialize with dependency injection support."""
        self.service = service or ClassworkService("data/classroom_data.json")
        self.class_id = None
        self.filter_type = None
        self.topic_name = None
    
    def set_class(self, class_id: int) -> None:
        """Set the current class context."""
        self.class_id = class_id
    
    def set_filter(self, filter_type: Optional[str] = None, topic_name: Optional[str] = None) -> None:
        """Set current filters."""
        self.filter_type = filter_type
        self.topic_name = topic_name
    
    def get_available_topics(self) -> List[str]:
        """Get available topics for current class."""
        if self.class_id is None:
            return []
        
        topics = self.service.get_topics_by_class_id(self.class_id)
        topic_titles = [t["title"] for t in topics if t.get("title")]
        return sorted(list(set(topic_titles)))  # Remove duplicates and sort
    
    def get_classwork_items(self) -> List[Dict]:
        """Get filtered classwork items."""
        if self.class_id is None:
            return []
        
        return self.service.filter_classwork(
            class_id=self.class_id,
            filter_type=self.filter_type,
            topic_name=self.topic_name
        )
    
    def create_topic(self, title: str, type_: str) -> bool:
        """Create a new topic."""
        if not title or self.class_id is None:
            return False
        
        result = self.service.create_topic(
            class_id=self.class_id,
            title=title,
            type_=type_
        )
        
        return result is not None
    
    def create_post(self, title: str, content: str, type_: str, 
                   topic_name: Optional[str] = None) -> bool:
        """Create a new post."""
        if not all([title, content, type_]) or self.class_id is None:
            return False
        
        result = self.service.create_post(
            class_id=self.class_id,
            title=title,
            content=content,
            type_=type_,
            topic_name=topic_name
        )
        
        return result is not None
    
    def edit_post(self, post_id: int, updates: Dict) -> bool:
        """Edit an existing post."""
        return self.service.update_post(post_id, updates)
    
    def delete_post(self, post_id: int) -> bool:
        """Delete a post."""
        return self.service.delete_post(post_id)