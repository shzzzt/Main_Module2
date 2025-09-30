import json, os

MOCK_FILE = os.path.join(os.path.dirname(__file__), "../..", "data", "sections.json")

class MockService:
    def __init__(self): 
        self.sections = []
        self.load_mock_data() 

    def load_mock_data(self) -> None: 
        """Loads mock data from JSON file"""
        with open(MOCK_FILE, "r") as file:
            self.sections = json.load(file)
        
    def get_sections(self) -> list:
        """Simulate GET API call"""
        return self.sections
    
    def create_section(self, section_data: dict) -> None:
        self.sections.append(section_data)

        with open(MOCK_FILE, "r") as file:
            sections = json.load(file) #python list of dict

        sections.append(section_data)

        with open(MOCK_FILE, "w") as file:
            json.dump(sections, file, indent=4)