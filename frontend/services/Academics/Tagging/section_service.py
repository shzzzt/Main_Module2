import json
import os
from typing import List, Dict

class SectionService:
    def __init__(self):
        self.data = data = [
            {'no': 1, 'section': 'A', 'program': 'BS Computer Science', 
             'year': 1, 'type': 'Lecture', 'capacity': 40, 'remarks': 'Regular'},
            {'no': 2, 'section': 'B', 'program': 'BS Information Technology', 
             'year': 2, 'type': 'Lecture', 'capacity': 50, 'remarks': 'Regular'}
        ]

    def get_sections(self) -> List[Dict]:
        return self.data 

    # def __init__(self, json_file: str = "mock_sections.json"):
    #     self.json_file = json_file
    #     self.sections: List[Dict] = self._load_data()
    #     # self.next_id = max((s.get('id', 0) for s in self.sections), default=0) + 1

    # def _load_data(self) -> List[Dict]:
    #     if os.path.exists(self.json_file):
    #         with open(self.json_file, 'r') as f:
    #             return json.load(f)
    #     return []  # Or seed with sample data

    # def _save_data(self):
    #     with open(self.json_file, 'w') as f:
    #         json.dump(self.sections, f, indent=4)

    # def get_sections(self, token: str) -> List[Dict]:
    #     # Token ignored in mock
    #     return self.sections.copy()

    # def create_section(self, data: Dict) -> Dict:
    #     new_section = {
    #         'id': self.next_id,
    #         **data  # Merge input data (e.g., section, program, etc.)
    #     }
    #     self.sections.append(new_section)
    #     self.next_id += 1
    #     self._save_data()
    #     return new_section

    # def update_section(self, data: Dict, token: str) -> Dict:
    #     section_id = data.get('id')
    #     for section in self.sections:
    #         if section['id'] == section_id:
    #             section.update(data)  # Merge updates
    #             self._save_data()
    #             return section
    #     raise ValueError(f"Section with ID {section_id} not found")

    # def delete_section(self, section_id: int, token: str) -> None:
    #     self.sections = [s for s in self.sections if s['id'] != section_id]
    #     self._save_data()

# class SectionService: 
#     def __init__(self, json_file: str = "mock_db.json"):
#         self.file = json_file
#         self._load_data()

#     def _load_data(self):
#         if not os.path.exists(self.file):
#             print("Error")
#         else:
#             print("Success")
       

#     def create_section(self, data: dict) -> bool:
#         pass 
#         # send data to mock backend by calling self.backend.post_section()
#         # if post_section():
#             # return true else return false 

#         self.backend.post_section(data)

# if __name__ == "__main__":
#     service = SectionService()