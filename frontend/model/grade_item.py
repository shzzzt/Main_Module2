
class GradeItem:
    """Represents a single grade entry with metadata"""
    def __init__(self, value="", is_draft=True):
        self.value = value  # "35/40" or "87.5"
        self.is_draft = is_draft
    
    def get_numeric_score(self):
        """Convert value to percentage"""
        if not self.value:
            return 0.0
        try:
            if '/' in self.value:
                parts = self.value.split('/')
                score = float(parts[0])
                total = float(parts[1])
                return (score / total * 100) if total > 0 else 0.0
            return float(self.value)
        except (ValueError, IndexError):
            return 0.0
