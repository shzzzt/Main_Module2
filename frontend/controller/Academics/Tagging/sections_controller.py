from ....views.Academics.Tagging.create_section_dialog import CreateSectionDialog 
from ....services.Academics.Tagging.section_service import SectionService
from PyQt6.QtWidgets import QDialog

class SectionController:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        # self.token = token 
        self.service = SectionService() 


    def open_dialog(self):
        dialog = CreateSectionDialog(self.view)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # pass 
            # validate dialog.get_data() 
            # if all data is valid, call self.service.create_section()
            # if create_section() is successful, execute self.update_model() 
            # print("Dialog accepted!")
            input_data = dialog.get_input_data() 

            if self.validate_data(input_data):
                current_section = self.service.create_section(input_data)

                if current_section: 
                    self.update_model(current_section)
                    # refresh table 

            else: 
                print("Data invalid")

    
    def update_model(self, data: dict):
        self.model._data.append(data) 

    def validate_data(self, data: dict) -> bool: 
        if not data: 
            return False 
        print("Data valid")
        return True 
        