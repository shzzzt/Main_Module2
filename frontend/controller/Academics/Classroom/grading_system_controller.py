import os
import sys
import requests
from PyQt6.QtCore import QObject, pyqtSignal

# Navigate to project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the project root to the system path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from frontend.services.Academics.model.Academics.Classroom.grading_system_model import GradingSystemModel      # noqa: E402
from frontend.services.Academics.model.Academics.Classroom.component_item import ComponentItem # noqa: E402


class GradingSystemController(QObject):
    """Controller for grading system operations - Integrated with Django Backend"""
    validation_error = pyqtSignal(str)
    save_success = pyqtSignal()
    api_error = pyqtSignal(str)
    
    def __init__(self, model: GradingSystemModel, class_id: int = None, token: str = None):
        super().__init__()
        self.model = model
        self.class_id = class_id
        self.token = token
        self.api_base_url = "http://127.0.0.1:8000/api/academics"
        
    def set_class_and_token(self, class_id: int, token: str):
        """Set the class ID and authentication token"""
        self.class_id = class_id
        self.token = token
        
    def load_rubrics_from_backend(self):
        """Load existing grading rubrics from Django backend"""
        if not self.class_id or not self.token:
            print("[GRADING CONTROLLER] No class_id or token set, using default rubrics")
            return False
            
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            url = f"{self.api_base_url}/classes/{self.class_id}/grading-rubrics/"
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                rubrics_data = response.json()
                print(f"[GRADING CONTROLLER] Loaded {len(rubrics_data)} rubrics from backend")
                
                # Parse and load rubrics into model
                self._parse_backend_rubrics(rubrics_data)
                return True
            elif response.status_code == 404:
                print("[GRADING CONTROLLER] No rubrics found, will use defaults")
                return False
            else:
                print(f"[GRADING CONTROLLER] API error: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"[GRADING CONTROLLER] Failed to load rubrics: {e}")
            return False
    
    def _parse_backend_rubrics(self, rubrics_data):
        """Parse rubrics from Django backend format and load into model"""
        midterm_rubric = None
        final_rubric = None
        
        for rubric in rubrics_data:
            academic_period = rubric.get('academic_period', '')
            term_percentage = float(rubric.get('term_percentage', 0))
            components = rubric.get('components', [])
            
            if academic_period == 'midterm':
                # Clear existing midterm components
                self.model.midterm_rubric.components = []
                self.model.midterm_rubric.term_percentage = int(term_percentage)
                
                # Add components
                for comp in components:
                    component_item = ComponentItem(
                        name=comp['name'],
                        percentage=int(float(comp['percentage'])),
                        component_id=comp['id']
                    )
                    self.model.midterm_rubric.add_component(component_item)
                    
                midterm_rubric = rubric
                
            elif academic_period == 'finals':
                # Clear existing final components
                self.model.final_rubric.components = []
                self.model.final_rubric.term_percentage = int(term_percentage)
                
                # Add components
                for comp in components:
                    component_item = ComponentItem(
                        name=comp['name'],
                        percentage=int(float(comp['percentage'])),
                        component_id=comp['id']
                    )
                    self.model.final_rubric.add_component(component_item)
                    
                final_rubric = rubric
        
        self.model.data_changed.emit()
        print(f"[GRADING CONTROLLER] Parsed rubrics - Midterm: {len(self.model.midterm_rubric.components)} components, Final: {len(self.model.final_rubric.components)} components")
    
    def add_component(self, term: str, name: str, percentage: int):
        rubric = self.model.get_rubric(term)
        if rubric:
            rubric.add_component(ComponentItem(name, percentage))
            self.model.data_changed.emit()
            return True
        return False
    
    def remove_component(self, term: str, index: int):
        rubric = self.model.get_rubric(term)
        if rubric:
            rubric.remove_component(index)
            self.model.data_changed.emit()
            return True
        return False
    
    def update_component(self, term: str, index: int, name: str, percentage: int):
        rubric = self.model.get_rubric(term)
        if rubric:
            rubric.update_component(index, name, percentage)
            self.model.data_changed.emit()
            return True
        return False
    
    def validate_and_save(self):
        """Validate rubrics and save to Django backend"""
        if not self.model.validate_all():
            errors = []
            if not self.model.midterm_rubric.is_valid():
                total = self.model.midterm_rubric.get_total_percentage()
                errors.append(f"Midterm components total {total}% (must be 100%)")
            if not self.model.final_rubric.is_valid():
                total = self.model.final_rubric.get_total_percentage()
                errors.append(f"Final components total {total}% (must be 100%)")
            
            self.validation_error.emit("\n".join(errors))
            return False
        
        # Save to backend if class_id and token are available
        if self.class_id and self.token:
            return self._save_to_backend()
        else:
            # Just emit success if no backend connection
            print("[GRADING CONTROLLER] No backend connection, saving locally only")
            self.save_success.emit()
            return True
    
    def _save_to_backend(self):
        """Save rubrics to Django backend"""
        try:
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            # Prepare midterm rubric data
            midterm_data = {
                'class_instance': self.class_id,
                'academic_period': 'midterm',
                'term_percentage': str(self.model.midterm_rubric.term_percentage),
                'components': [
                    {
                        'name': comp.name,
                        'percentage': str(comp.percentage)
                    }
                    for comp in self.model.midterm_rubric.components
                ]
            }
            
            # Prepare final rubric data
            final_data = {
                'class_instance': self.class_id,
                'academic_period': 'finals',
                'term_percentage': str(self.model.final_rubric.term_percentage),
                'components': [
                    {
                        'name': comp.name,
                        'percentage': str(comp.percentage)
                    }
                    for comp in self.model.final_rubric.components
                ]
            }
            
            # Check if rubrics exist (GET first)
            get_url = f"{self.api_base_url}/classes/{self.class_id}/grading-rubrics/"
            get_response = requests.get(get_url, headers=headers, timeout=5)
            
            existing_rubrics = {}
            if get_response.status_code == 200:
                for rubric in get_response.json():
                    existing_rubrics[rubric['academic_period']] = rubric['id']
            
            # Save or update midterm rubric
            if 'midterm' in existing_rubrics:
                # Update existing rubric
                update_url = f"{self.api_base_url}/grading-rubrics/{existing_rubrics['midterm']}/"
                midterm_response = requests.patch(
                    update_url,
                    json={'term_percentage': str(self.model.midterm_rubric.term_percentage)},
                    headers=headers,
                    timeout=5
                )
                print(f"[GRADING CONTROLLER] Updated midterm rubric: {midterm_response.status_code}")
                
                # Update components (delete old, create new for simplicity)
                self._update_rubric_components(
                    existing_rubrics['midterm'],
                    self.model.midterm_rubric.components,
                    headers
                )
            else:
                # Create new rubric
                post_url = f"{self.api_base_url}/classes/{self.class_id}/grading-rubrics/"
                midterm_response = requests.post(
                    post_url,
                    json=midterm_data,
                    headers=headers,
                    timeout=5
                )
                print(f"[GRADING CONTROLLER] Created midterm rubric: {midterm_response.status_code}")
                
                if midterm_response.status_code not in [200, 201]:
                    error_msg = f"Failed to save midterm rubric: {midterm_response.text}"
                    self.api_error.emit(error_msg)
                    return False
            
            # Save or update final rubric
            if 'finals' in existing_rubrics:
                # Update existing rubric
                update_url = f"{self.api_base_url}/grading-rubrics/{existing_rubrics['finals']}/"
                final_response = requests.patch(
                    update_url,
                    json={'term_percentage': str(self.model.final_rubric.term_percentage)},
                    headers=headers,
                    timeout=5
                )
                print(f"[GRADING CONTROLLER] Updated final rubric: {final_response.status_code}")
                
                # Update components
                self._update_rubric_components(
                    existing_rubrics['finals'],
                    self.model.final_rubric.components,
                    headers
                )
            else:
                # Create new rubric
                post_url = f"{self.api_base_url}/classes/{self.class_id}/grading-rubrics/"
                final_response = requests.post(
                    post_url,
                    json=final_data,
                    headers=headers,
                    timeout=5
                )
                print(f"[GRADING CONTROLLER] Created final rubric: {final_response.status_code}")
                
                if final_response.status_code not in [200, 201]:
                    error_msg = f"Failed to save final rubric: {final_response.text}"
                    self.api_error.emit(error_msg)
                    return False
            
            print("[GRADING CONTROLLER] Successfully saved rubrics to backend")
            self.save_success.emit()
            return True
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error saving rubrics: {str(e)}"
            print(f"[GRADING CONTROLLER] {error_msg}")
            self.api_error.emit(error_msg)
            return False
    
    def _update_rubric_components(self, rubric_id, components, headers):
        """Update components for a rubric (delete old, create new)"""
        try:
            # Get existing components
            get_url = f"{self.api_base_url}/grading-rubrics/{rubric_id}/components/"
            get_response = requests.get(get_url, headers=headers, timeout=5)
            
            if get_response.status_code == 200:
                existing_components = get_response.json()
                
                # Delete existing components
                for comp in existing_components:
                    delete_url = f"{self.api_base_url}/rubric-components/{comp['id']}/"
                    requests.delete(delete_url, headers=headers, timeout=5)
            
            # Create new components
            for comp in components:
                comp_data = {
                    'rubric': rubric_id,
                    'name': comp.name,
                    'percentage': str(comp.percentage)
                }
                post_url = f"{self.api_base_url}/grading-rubrics/{rubric_id}/components/"
                requests.post(post_url, json=comp_data, headers=headers, timeout=5)
            
            print(f"[GRADING CONTROLLER] Updated {len(components)} components for rubric {rubric_id}")
            
        except requests.exceptions.RequestException as e:
            print(f"[GRADING CONTROLLER] Error updating components: {e}")