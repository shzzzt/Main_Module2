# Import necessary modules from PyQt6 for UI components, core functionalities, and graphics
from PyQt6.QtWidgets import (
    QWidget, QApplication, QVBoxLayout, QHBoxLayout, QMainWindow,
    QLabel, QPushButton, QHeaderView, QSpacerItem, QSizePolicy,
    QFrame, QComboBox, QTreeWidget, QTreeWidgetItem, QLineEdit,
    QMenu, QCheckBox, QToolButton
)
# Import core Qt functionalities for signals, enums, and objects
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QObject
# Import GUI utilities for colors, palettes, fonts, icons, actions, painters, and pens
from PyQt6.QtGui import QColor, QPalette, QFont, QIcon, QAction, QPainter, QPen
# Import system module for accessing command-line arguments
import sys

# --- Controller and Data Model Layer ---

# --- GradeDataModel Class ---
# This class manages the application's data independently of the UI.
# It acts as the single source of truth for all grade-related information.
class GradeDataModel(QObject):
    """
    Holds the application's data and state, independent of the UI.
    Acts as the single source of truth for the grade data.
    """
    # --- Signals ---
    # Define Qt signals to notify the UI when data changes occur.
    # data_reset: Emitted when the entire dataset is reloaded (e.g., new data).
    data_reset = pyqtSignal()
    # data_updated: Emitted when individual grades are modified.
    data_updated = pyqtSignal()
    # columns_changed: Emitted when the state of columns (expanded/collapsed) changes.
    columns_changed = pyqtSignal()

    # --- Constructor ---
    # Initializes the model's attributes and data structures.
    def __init__(self):
        super().__init__()
        # List to store student information: [{'id': '101', 'name': 'Castro, Carlos Fidel'}, ...]
        self.students = []
        # Dictionary defining the available grade components and their items.
        self.components = {
            'performance_tasks': ['PT1', 'PT2', 'PT3'],
            'quizzes': ['Quiz 1', 'Quiz 2', 'Quiz 3', 'Quiz 4'],
            'exams': ['Prelim Exam', 'Final Exam']
        }
        # Dictionary to track the expanded/collapsed state of various column groups.
        self.column_states = {
            'midterm_expanded': False,
            'finalterm_expanded': False,
            'performance_task_midterm_expanded': False,
            'quiz_midterm_expanded': False,
            'exam_midterm_expanded': False,
            'performance_task_finalterm_expanded': False,
            'quiz_finalterm_expanded': False,
            'exam_finalterm_expanded': False,
        }
        # Nested dictionary to store actual grade values: {student_id: {component_key: grade_str}}.
        # Example component_key: 'pt1_midterm', 'quiz1_finalterm'.
        self.grades = {}

    # --- Data Loading ---
    # Loads sample student data into the model for demonstration purposes.
    def load_sample_data(self):
        """Loads initial sample data into the model."""
        # Populate the students list with sample data.
        self.students = [
            {'id': '101', 'name': "Castro, Carlos Fidel"},
            {'id': '102', 'name': "Santos, Maria Elena"},
            {'id': '103', 'name': "Garcia, Juan Pablo"},
            {'id': '104', 'name': "Rodriguez, Ana Sofia"}
        ]
        # Initialize an empty grades dictionary for each student.
        for student in self.students:
            self.grades[student['id']] = {}
        # Emit the data_reset signal to inform the UI that the data structure is ready.
        self.data_reset.emit()

    # --- State Accessors/Mutators ---
    # Retrieves the current state (True/False) of a specific column group.
    def get_column_state(self, key):
        return self.column_states.get(key, False)

    # Updates the state of a column group and notifies the UI if it changed.
    def set_column_state(self, key, value):
        """Updates a column state and emits a signal."""
        # Check if the new value is different from the current state.
        if self.column_states.get(key) != value:
            # Update the internal state dictionary.
            self.column_states[key] = value
            # Emit the columns_changed signal to trigger UI updates.
            self.columns_changed.emit()

    # Sets or updates a specific grade for a student and component, then notifies the UI.
    def set_grade(self, student_id, component_key, grade_text):
        """Sets a grade for a student and component."""
        # Check if the student ID exists in the grades dictionary.
        if student_id in self.grades:
            # Update the grade for the specific student and component.
            self.grades[student_id][component_key] = grade_text
            # Emit the data_updated signal to inform the UI of the change.
            self.data_updated.emit()

    # Retrieves a specific grade for a student and component.
    def get_grade(self, student_id, component_key):
        """Gets a grade for a student and component."""
        # Safely retrieve the grade, returning an empty string if not found.
        return self.grades.get(student_id, {}).get(component_key, "")

    # Generates a list of all possible component keys based on the defined structure.
    def get_all_component_keys(self):
        """Generates a list of all possible component keys based on structure."""
        keys = []
        # Iterate through Performance Tasks for both terms.
        for pt in self.components['performance_tasks']:
            keys.append(f"{pt.lower().replace(' ', '')}_midterm")
            keys.append(f"{pt.lower().replace(' ', '')}_finalterm")
        # Iterate through Quizzes for both terms.
        for q in self.components['quizzes']:
            keys.append(f"{q.lower().replace(' ', '')}_midterm")
            keys.append(f"{q.lower().replace(' ', '')}_finalterm")
        # Iterate through Exams for both terms.
        for e in self.components['exams']:
            keys.append(f"{e.lower().replace(' ', '')}_midterm")
            keys.append(f"{e.lower().replace(' ', '')}_finalterm")
        return keys

# --- GradeController Class ---
# This class handles the application's business logic.
# It acts as an intermediary between the GradeDataModel and the UI (CollapsibleGradesTable).
class GradeController(QObject):
    """
    Handles the application logic.
    Interacts with the GradeDataModel and sends updates to the UI.
    Future home for API calls to Django backend.
    """
    # --- Signals ---
    # Define Qt signals to trigger UI updates from the controller.
    # data_changed: Emitted when underlying data (grades) changes.
    data_changed = pyqtSignal()
    # columns_changed: Emitted when column structure/expansion state changes.
    columns_changed = pyqtSignal()

    # --- Constructor ---
    # Initializes the controller and establishes connections with the model.
    def __init__(self, model: GradeDataModel):
        super().__init__()
        # Store a reference to the GradeDataModel instance.
        self.model = model
        # Connect the model's signals to the controller's internal handler methods.
        # This ensures the controller reacts to changes in the model.
        self.model.data_reset.connect(self.on_model_data_reset)
        self.model.data_updated.connect(self.on_model_data_updated)
        self.model.columns_changed.connect(self.on_model_columns_changed)

    # --- Model Signal Handlers ---
    # Internal methods that respond to signals emitted by the GradeDataModel.
    # They re-emit controller-specific signals to the UI.
    def on_model_data_reset(self):
        # When the model emits data_reset, the controller emits data_changed.
        self.data_changed.emit()

    def on_model_data_updated(self):
        # When the model emits data_updated, the controller emits data_changed.
        self.data_changed.emit()

    def on_model_columns_changed(self):
        # When the model emits columns_changed, the controller emits columns_changed.
        self.columns_changed.emit()

    # --- UI Interaction Handler ---
    # Processes user actions related to header expansion/collapse.
    def handle_header_expand_clicked(self, column_info):
        """
        Logic for handling header clicks to expand/collapse.
        """
        # Extract information from the column_info dictionary.
        col_type = column_info.get('type')
        col_name = column_info.get('name')
        term = column_info.get('term')
        component = column_info.get('component')
        target = column_info.get('target')

        # Determine the specific key in the model's column_states dictionary
        # that corresponds to the clicked header.
        key = None
        if col_type == 'expandable_main':
            # For main headers (Midterm Grade, Final Term Grade), determine the key.
            if target == 'midterm':
                key = 'midterm_expanded'
            elif target == 'finalterm':
                key = 'finalterm_expanded'
        elif col_type == 'expandable_component':
            # For component headers (Quiz, PT, Exam), determine the key.
            if component == 'performance_task' and term:
                key = f'performance_task_{term}_expanded'
            elif component == 'quiz' and term:
                key = f'quiz_{term}_expanded'
            elif component == 'exam' and term:
                key = f'exam_{term}_expanded'

        # If a valid key was determined, toggle its state in the model.
        if key:
            # Get the current state from the model.
            current_state = self.model.get_column_state(key)
            # Invert the state (expand if collapsed, collapse if expanded).
            # The model's set_column_state method will emit columns_changed if the state changes.
            self.model.set_column_state(key, not current_state)

    # --- Calculation Logic ---
    # Performs calculations for student grades based on the data in the model.
    def calculate_grades_for_student(self, student_id):
        """
        Calculates midterm, finalterm, and final grades for a student.
        Returns a dictionary of calculated grades.
        """
        # Initialize accumulators for midterm and final term grades.
        midterm_total = 0
        midterm_count = 0
        finalterm_total = 0
        finalterm_count = 0

        # Iterate through all possible component keys.
        for component_key in self.model.get_all_component_keys():
            # Get the grade text for the current student and component.
            grade_text = self.model.get_grade(student_id, component_key)
            # Skip empty grades.
            if not grade_text:
                continue

            try:
                # Determine the term (midterm or finalterm) based on the component key.
                term = 'midterm' if '_midterm' in component_key else 'finalterm'
                # Parse the grade text. If it's in "score/total" format, calculate percentage.
                if '/' in grade_text:
                    parts = grade_text.split('/', 1)
                    score = float(parts[0]) if parts[0] else 0
                    total = float(parts[1]) if parts[1] else 1
                    # Calculate percentage, avoiding division by zero.
                    grade = score / total * 100 if total != 0 else 0
                else:
                    # If not in "score/total" format, treat as a direct numerical grade.
                    grade = float(grade_text) if grade_text else 0

                # Accumulate grades based on the term.
                if term == 'midterm':
                    midterm_total += grade
                    midterm_count += 1
                elif term == 'finalterm':
                    finalterm_total += grade
                    finalterm_count += 1
            # Handle cases where the grade text is not a valid number.
            except ValueError:
                continue

        # Calculate average grades for midterm and final term.
        # Avoid division by zero by checking the count.
        midterm_avg = midterm_total / midterm_count if midterm_count > 0 else 0
        finalterm_avg = finalterm_total / finalterm_count if finalterm_count > 0 else 0
        # Calculate the overall final grade using a weighted average.
        # Midterm contributes 1/3, Final Term contributes 2/3.
        final_grade = (midterm_avg * 1/3) + (finalterm_avg * 2/3) if (midterm_count > 0 or finalterm_count > 0) else 0

        # Return the calculated grades formatted as strings with two decimal places.
        return {
            'midterm_avg': f"{midterm_avg:.2f}",
            'finalterm_avg': f"{finalterm_avg:.2f}",
            'final_grade': f"{final_grade:.2f}"
        }


# --- UI Layer ---

# --- ExpandableHeaderView Class ---
# A custom header view that handles painting for expandable columns
# and manages their expanded/collapsed states visually.
class ExpandableHeaderView(QHeaderView):
    # --- Constructor ---
    # Initializes the header view and sets up basic configurations.
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        # Dictionary to store information about expandable columns.
        # Key: visual index, Value: {'info': column_info_dict, 'expanded': bool}.
        self.expandable_columns = {}
        # Connect the internal section clicked signal to a handler for repainting.
        self.sectionClicked.connect(self._on_section_clicked_internally)

    # --- Internal Event Handler ---
    # Triggers a repaint of the clicked section when a header is clicked.
    def _on_section_clicked_internally(self, logical_index):
        self.updateSection(logical_index) # Update only the clicked section.
        self.viewport().update() # Ensure the viewport updates correctly.

    # --- Public Method for Setting Column Info ---
    # Allows the parent widget (CollapsibleGradesTable) to register expandable columns.
    def set_expandable_column(self, visual_index, column_info, is_expanded=False):
        # Store the column information and its expanded state.
        self.expandable_columns[visual_index] = {
            'info': column_info,
            'expanded': is_expanded
        }
        # Get the logical index and trigger an update for that section.
        logical_index = self.logicalIndex(visual_index)
        if logical_index >= 0:
            self.updateSection(logical_index)

    # --- Mouse Event Handling ---
    # Overrides the default mouse press event to handle clicks on expandable columns.
    def mousePressEvent(self, event):
        # Check for a left mouse button click.
        if event.button() == Qt.MouseButton.LeftButton:
            # Determine the logical index of the section that was clicked.
            logical_index = self.logicalIndexAt(event.pos())
            if logical_index >= 0:
                # Get the visual index.
                visual_index = self.visualIndex(logical_index)
                # Check if the clicked section is registered as expandable.
                if visual_index in self.expandable_columns:
                    # Emit the standard sectionClicked signal.
                    self.sectionClicked.emit(logical_index)
                    return # Consume the event.
        # If not handled, call the parent class's mousePressEvent.
        super().mousePressEvent(event)

    # --- Custom Painting ---
    # Overrides the default painting for header sections to provide custom visuals.
    def paintSection(self, painter, rect, logicalIndex):
        # Get the visual index of the section being painted.
        visual_index = self.visualIndex(logicalIndex)
        # Retrieve the stored information for this expandable column.
        column_data = self.expandable_columns.get(visual_index)

        # --- Default Painting for Non-Expandable Columns ---
        # If there's no custom data for this section, fall back to default painting.
        if not column_data:
            # Save the painter's current state.
            painter.save()
            # Set the brush to the default background color.
            painter.setBrush(QColor("#084924"))
            # Set the pen to NoPen to avoid drawing borders here.
            painter.setPen(Qt.PenStyle.NoPen)
            # Draw the background rectangle.
            painter.drawRect(rect)
            # Restore the painter's state.
            painter.restore()

            # Draw a right border for the section.
            painter.save()
            painter.setPen(QPen(QColor("#0A5A2A"), 1))
            painter.drawLine(rect.topRight(), rect.bottomRight())
            painter.restore()

            # Let Qt draw the standard header text on top.
            super().paintSection(painter, rect, logicalIndex)
            return # Exit early for non-expandable columns.

        # --- Extract Column Information ---
        # Get the details of the column being painted.
        col_info = column_data['info']
        is_expanded = column_data['expanded']
        col_type = col_info.get('type')
        col_term = col_info.get('term') # Term for sub-components and grade inputs.
        target_term = col_info.get('target') # Target term for main headers.

        # --- Determine Visual Context ---
        # Determine if this column belongs to an expanded main section.
        is_in_expanded_main_section = False
        is_main_header_expanded = False
        expanded_term = None

        # Check all registered expandable columns to find expanded main headers.
        for check_visual_index, data in self.expandable_columns.items():
            info = data['info']
            # Look for expandable_main columns that are currently expanded.
            if info.get('type') == 'expandable_main' and data['expanded']:
                main_target = info.get('target')
                # Check if this column's term matches the expanded main header's target.
                if (col_term and col_term == main_target) or \
                   (target_term and target_term == main_target) or \
                   (col_type == 'expandable_main' and target_term == main_target):
                    is_in_expanded_main_section = True
                    expanded_term = main_target
                    # Special case: if this column is the main header itself.
                    if col_type == 'expandable_main' and target_term == main_target:
                        is_main_header_expanded = True
                    break # Found the relevant main header.

        # --- Define Visual Colors ---
        # Define the color palette used for painting.
        default_bg_color = QColor("#084924")      # Base header color.
        expanded_main_bg_color = QColor("#036800") # Background for expanded main headers & components.
        sub_header_text_color = QColor("#FFC000")  # Text color for component headers (Quiz, PT).
        white_text_color = QColor("white")         # Default text color.

        # --- Determine Final Painting Colors ---
        # Decide the background and text colors based on the column's state and type.
        bg_color = default_bg_color
        text_color = white_text_color

        # 1. Main Header (Expandable Main) - e.g., "Midterm Grade", "Final Term Grade"
        if col_type == 'expandable_main':
            if is_main_header_expanded:
                # Use the expanded background color if this main header is expanded.
                bg_color = expanded_main_bg_color
            # Text color for main headers is always white.

        # 2. Sub-Header (Expandable Component) - e.g., "Performance Task", "Quiz"
        elif col_type == 'expandable_component':
            if is_in_expanded_main_section:
                # Change text color to yellow/orange if it's under an expanded main section.
                text_color = sub_header_text_color
                # Also give it the expanded background color.
                bg_color = expanded_main_bg_color
            # Else, use default colors.

        # 3. Grade Input Component Columns - e.g., "PT1 (M)", "Quiz 1 (F)"
        elif col_type == 'grade_input':
            if is_in_expanded_main_section:
                # Give grade input columns the expanded background color.
                bg_color = expanded_main_bg_color
                # Text color for grade inputs is always white when in an expanded section.
            # Else, default background, white text.

        # --- Painting Sequence ---
        # 1. Draw Background
        # Save painter state, set brush to the determined background color, and draw the rectangle.
        painter.save()
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen) # No border for the fill.
        painter.drawRect(rect)
        painter.restore()

        # 2. Draw Right Border
        # Save painter state, set pen for the border, and draw the vertical line.
        painter.save()
        painter.setPen(QPen(QColor("#0A5A2A"), 1)) # Dark green border.
        painter.drawLine(rect.topRight(), rect.bottomRight())
        painter.restore()

        # 3. Draw Text
        # Save painter state, set pen to the determined text color and font, then draw the text.
        painter.save()
        painter.setPen(text_color)
        painter.setFont(self.font())

        # Get the text to draw from the model's header data.
        text = self.model().headerData(logicalIndex, self.orientation(), Qt.ItemDataRole.DisplayRole)
        if text is not None:
            # Adjust the rectangle for padding and space reserved for the indicator.
            text_rect = rect.adjusted(4, 0, -25, 0)
            # Draw the text aligned to the left and vertically centered.
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(text))
        painter.restore()

        # 4. Draw Expand/Collapse Indicator (only for expandable columns)
        # Check if the column type qualifies for an expand/collapse indicator.
        if col_type in ['expandable_main', 'expandable_component']:
            # Save painter state, set pen to white for the indicator.
            painter.save()
            painter.setPen(white_text_color)
            # Set a bold Arial font for the indicator.
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))

            # Determine the indicator character: ">" for collapsed, "<" for expanded.
            indicator = " >" if not is_expanded else " <"
            # Define the rectangle for the indicator on the right side of the section.
            indicator_rect = rect.adjusted(rect.width() - 20, 0, -5, 0)
            # Draw the indicator text centered in its rectangle.
            painter.drawText(indicator_rect, Qt.AlignmentFlag.AlignCenter, indicator)

            painter.restore() # Restore painter state.


# --- CollapsibleGradesTable Class ---
# The main table widget that displays student grades and manages the UI logic.
class CollapsibleGradesTable(QTreeWidget):
    # --- Constructor ---
    # Initializes the table, sets up the custom header, and connects signals.
    def __init__(self, model: GradeDataModel, controller: GradeController, parent=None):
        super().__init__(parent)
        # Store references to the model and controller.
        self.model = model
        self.controller = controller
        # Dictionary mapping logical column indices to their information dictionaries.
        self.column_info_map = {}

        # Perform initial table setup.
        self.setup_table()
        # Connect controller signals to UI update methods.
        self.controller.data_changed.connect(self.refresh_data_display)
        self.controller.columns_changed.connect(self.rebuild_table_structure)

        # Load initial data into the model and build the initial table structure/UI.
        self.model.load_sample_data()
        self.rebuild_table_structure()

    # --- Table Setup ---
    # Configures the table's appearance, header, and initial styles.
    def setup_table(self):
        # Create an instance of our custom header view.
        self.custom_header = ExpandableHeaderView(Qt.Orientation.Horizontal, self)
        # Set the custom header as the table's header.
        self.setHeader(self.custom_header)
        # Connect the custom header's sectionClicked signal to the table's handler.
        self.custom_header.sectionClicked.connect(self.on_header_section_clicked)

        # Apply general styling to the table using CSS-like syntax.
        self.setStyleSheet("""
            QTreeWidget {
                background-color: white;
                alternate-background-color: #F8F9FA;
                border: none;
                font-family: 'Inter';
                gridline-color: #E0E0E0;
                color: #000000;
            }
            QTreeWidget::item {
                padding: 8px 4px;
                border-bottom: 1px solid #E0E0E0;
                min-height: 35px;
                color: #000000;
            }
            QTreeWidget::item:selected {
                background-color: #E8F5E8;
                color: #000000;
            }
            QTreeWidget::item:hover {
                background-color: #F0F8F0;
                color: #000000;
            }
        """)

        # Configure table properties.
        self.setRootIsDecorated(False) # Hide root decoration (tree lines).
        self.setAlternatingRowColors(True) # Alternate row background colors.
        self.setSortingEnabled(False) # Disable sorting for simplicity.

        # Apply styling specifically to the header.
        self.custom_header.setStyleSheet("""
            QHeaderView::section {
                background-color: #084924; /* Enforce default background */
                color: white;
                padding: 8px 4px;
                font-weight: bold;
                font-size: 11px;
                border: none;
                border-right: 1px solid #0A5A2A;
                min-height: 40px;
                text-align: left;
            }
        """)

    # --- Header Click Handler ---
    # Responds to clicks on the custom header sections.
    def on_header_section_clicked(self, logical_index):
        """Handle clicks on the header sections."""
        # Validate the logical index.
        if logical_index < 0 or logical_index >= len(self.column_info_map):
            return

        # Get the information for the clicked column.
        col_info = self.column_info_map.get(logical_index)
        if not col_info:
            return

        # Get the column type.
        col_type = col_info.get('type')
        # If it's an expandable column, delegate the action to the controller.
        if col_type in ['expandable_main', 'expandable_component']:
            self.controller.handle_header_expand_clicked(col_info)

    # --- Table Structure Rebuilding ---
    # Clears the table and rebuilds its columns and data based on the model's current state.
    def rebuild_table_structure(self):
        """Rebuilds the table columns based on model state."""
        self.clear() # Clear existing items and data.
        self.build_column_structure() # Build the column structure.
        self.populate_table_with_data() # Populate the table with student data.

    # --- Column Structure Definition ---
    # Defines the columns of the table based on the model's column_states.
    def build_column_structure(self):
        """Builds the column structure based on the model's column_states."""
        # Start with fixed columns (ID, Name).
        columns = [
            {'name': 'No.', 'type': 'fixed', 'width': 50},
            {'name': 'Sort by Last Name', 'type': 'fixed', 'width': 200}
        ]

        # --- Midterm Section ---
        # Add the "Midterm Grade" main header column.
        columns.append({
            'name': 'Midterm Grade',
            'type': 'expandable_main',
            'width': 120,
            'target': 'midterm' # Indicates this header controls midterm columns.
        })

        # Check if the midterm section is expanded in the model.
        if self.model.get_column_state('midterm_expanded'):
            # Add "Performance Task" component header.
            columns.append({
                'name': 'Performance Task',
                'type': 'expandable_component',
                'width': 120,
                'term': 'midterm',
                'component': 'performance_task'
            })
            # Check if the Performance Task component is expanded.
            if self.model.get_column_state('performance_task_midterm_expanded'):
                # Add individual Performance Task columns (PT1 (M), PT2 (M), etc.).
                for pt in self.model.components['performance_tasks']:
                    columns.append({
                        'name': f'{pt} (M)', # Display name.
                        'type': 'grade_input', # Type of column.
                        'width': 80, # Width in pixels.
                        'term': 'midterm', # Term it belongs to.
                        'component': 'performance_task', # Component group.
                        'component_key': f"{pt.lower().replace(' ', '')}_midterm" # Unique key.
                    })

            # Add "Quiz" component header.
            columns.append({
                'name': 'Quiz',
                'type': 'expandable_component',
                'width': 80,
                'term': 'midterm',
                'component': 'quiz'
            })
            # Check if the Quiz component is expanded.
            if self.model.get_column_state('quiz_midterm_expanded'):
                # Add individual Quiz columns (Quiz 1 (M), Quiz 2 (M), etc.).
                for quiz in self.model.components['quizzes']:
                    columns.append({
                        'name': f'{quiz} (M)',
                        'type': 'grade_input',
                        'width': 80,
                        'term': 'midterm',
                        'component': 'quiz',
                        'component_key': f"{quiz.lower().replace(' ', '')}_midterm"
                    })

            # Add "Exam" component header.
            columns.append({
                'name': 'Exam',
                'type': 'expandable_component',
                'width': 80,
                'term': 'midterm',
                'component': 'exam'
            })
            # Check if the Exam component is expanded.
            if self.model.get_column_state('exam_midterm_expanded'):
                # Add individual Exam columns (Prelim Exam (M), Final Exam (M), etc.).
                for exam in self.model.components['exams']:
                    columns.append({
                        'name': f'{exam} (M)',
                        'type': 'grade_input',
                        'width': 100,
                        'term': 'midterm',
                        'component': 'exam',
                        'component_key': f"{exam.lower().replace(' ', '')}_midterm"
                    })

        # --- Final Term Section ---
        # Add the "Final Term Grade" main header column.
        columns.append({
            'name': 'Final Term Grade',
            'type': 'expandable_main',
            'width': 130,
            'target': 'finalterm' # Indicates this header controls finalterm columns.
        })

        # Check if the final term section is expanded in the model.
        if self.model.get_column_state('finalterm_expanded'):
            # Add "Performance Task" component header for final term.
            columns.append({
                'name': 'Performance Task',
                'type': 'expandable_component',
                'width': 120,
                'term': 'finalterm',
                'component': 'performance_task'
            })
            # Check if the Performance Task component is expanded.
            if self.model.get_column_state('performance_task_finalterm_expanded'):
                # Add individual Performance Task columns (PT1 (F), PT2 (F), etc.).
                for pt in self.model.components['performance_tasks']:
                    columns.append({
                        'name': f'{pt} (F)',
                        'type': 'grade_input',
                        'width': 80,
                        'term': 'finalterm',
                        'component': 'performance_task',
                        'component_key': f"{pt.lower().replace(' ', '')}_finalterm"
                    })

            # Add "Quiz" component header for final term.
            columns.append({
                'name': 'Quiz',
                'type': 'expandable_component',
                'width': 80,
                'term': 'finalterm',
                'component': 'quiz'
            })
            # Check if the Quiz component is expanded.
            if self.model.get_column_state('quiz_finalterm_expanded'):
                # Add individual Quiz columns (Quiz 1 (F), Quiz 2 (F), etc.).
                for quiz in self.model.components['quizzes']:
                    columns.append({
                        'name': f'{quiz} (F)',
                        'type': 'grade_input',
                        'width': 80,
                        'term': 'finalterm',
                        'component': 'quiz',
                        'component_key': f"{quiz.lower().replace(' ', '')}_finalterm"
                    })

            # Add "Exam" component header for final term.
            columns.append({
                'name': 'Exam',
                'type': 'expandable_component',
                'width': 80,
                'term': 'finalterm',
                'component': 'exam'
            })
            # Check if the Exam component is expanded.
            if self.model.get_column_state('exam_finalterm_expanded'):
                # Add individual Exam columns (Prelim Exam (F), Final Exam (F), etc.).
                for exam in self.model.components['exams']:
                    columns.append({
                        'name': f'{exam} (F)',
                        'type': 'grade_input',
                        'width': 100,
                        'term': 'finalterm',
                        'component': 'exam',
                        'component_key': f"{exam.lower().replace(' ', '')}_finalterm"
                    })

        # Add the "Final Grade" column for the overall calculated grade.
        columns.append({'name': 'Final Grade', 'type': 'calculated', 'width': 100})

        # --- Apply Structure to QTreeWidget ---
        # Set the number of columns in the table.
        self.setColumnCount(len(columns))
        # Create a map from logical index to column information.
        self.column_info_map = {i: col for i, col in enumerate(columns)}
        # Extract column labels.
        labels = [col['name'] for col in columns]
        # Set the width for each column.
        for i, col in enumerate(columns):
            self.setColumnWidth(i, col['width'])
        # Set the header labels for all columns.
        self.setHeaderLabels(labels)

        # --- Update Custom Header with Column Info ---
        # Reset the expandable columns dictionary in the custom header.
        self.custom_header.expandable_columns = {}

        # Iterate through the defined columns to register expandable ones with the header.
        for i, col in enumerate(columns):
            # Check if the column type is expandable.
            if col['type'] in ['expandable_main', 'expandable_component']:
                # Determine the initial expanded state based on the model.
                is_expanded = False
                if col['type'] == 'expandable_main':
                    # For main headers, check the corresponding state key.
                    if col['target'] == 'midterm':
                        is_expanded = self.model.get_column_state('midterm_expanded')
                    elif col['target'] == 'finalterm':
                        is_expanded = self.model.get_column_state('finalterm_expanded')
                elif col['type'] == 'expandable_component':
                    # For component headers, check the corresponding state key.
                    component = col['component']
                    term = col['term']
                    if component == 'performance_task':
                        is_expanded = self.model.get_column_state(f'performance_task_{term}_expanded')
                    elif component == 'quiz':
                        is_expanded = self.model.get_column_state(f'quiz_{term}_expanded')
                    elif component == 'exam':
                        is_expanded = self.model.get_column_state(f'exam_{term}_expanded')

                # Get the visual index of the column.
                visual_index = self.custom_header.visualIndex(i)
                # Register the column with the custom header view.
                self.custom_header.set_expandable_column(visual_index, col, is_expanded)

    # --- Data Population ---
    # Fills the table with student data and creates input/display widgets for each cell.
    def populate_table_with_data(self):
        """Populates the table with student data from the model."""
        # Iterate through the list of students in the model.
        for i, student in enumerate(self.model.students):
            # Create a new tree widget item (representing a row) for the student.
            item = QTreeWidgetItem(self)
            # Set the student's ID and name in the first two columns.
            item.setText(0, student['id'])
            item.setText(1, student['name'])
            # Set the text color for the ID and name columns.
            item.setForeground(0, QColor("#000000"))
            item.setForeground(1, QColor("#000000"))

            # Iterate through the remaining columns (starting from index 2).
            for col_index in range(2, self.columnCount()):
                # Get the information for the current column.
                col_info = self.column_info_map.get(col_index, {})
                # Get the column type.
                col_type = col_info.get('type', '')
                # Get the unique component key for grade input columns.
                component_key = col_info.get('component_key', '')

                # --- Grade Input Columns ---
                # If the column is for grade input...
                if col_type == 'grade_input':
                    # Create a QLineEdit widget for grade entry.
                    input_field = self.create_grade_input()
                    # Get the existing grade value from the model for this student and component.
                    grade_value = self.model.get_grade(student['id'], component_key)
                    # Set the text of the input field to the existing grade value.
                    input_field.setText(grade_value)
                    # --- Signal Connection ---
                    # Capture the student ID and component key in default arguments
                    # to avoid closure issues in the lambda function.
                    sid, key = student['id'], component_key
                    # Connect the textChanged signal of the input field to the handler method.
                    # The lambda captures the specific sid and key for this iteration.
                    input_field.textChanged.connect(
                        lambda text, s_id=sid, c_key=key: self.on_grade_input_changed(s_id, c_key, text)
                    )
                    # Set the input field as the widget for this specific cell.
                    self.setItemWidget(item, col_index, input_field)

                # --- Calculated/Expandable Header Columns ---
                # If the column is for calculated grades or expandable headers...
                elif col_type in ['calculated', 'expandable_main', 'expandable_component']:
                    # Create a QLabel widget for displaying calculated grades or header text.
                    label = self.create_grade_display()
                    # Set the label as the widget for this specific cell.
                    self.setItemWidget(item, col_index, label)

        # Refresh the display to show calculated grades for all students.
        self.refresh_data_display()

    # --- Grade Input Handler ---
    # Handles changes made in the grade input fields.
    def on_grade_input_changed(self, student_id, component_key, text):
        """Handle grade input changes."""
        # Delegate the task of setting the grade to the model.
        # The model will update its internal state and emit a signal if the data changes.
        self.model.set_grade(student_id, component_key, text)

    # --- Data Display Refresh ---
    # Updates the calculated grade displays for all students.
    def refresh_data_display(self):
        """Refreshes the calculated grade displays for all students."""
        # Iterate through all top-level items (student rows) in the table.
        for i in range(self.topLevelItemCount()):
            # Get the current item (student row).
            item = self.topLevelItem(i)
            # Get the student ID from the first column of the row.
            student_id = item.text(0)
            # Ask the controller to calculate grades for this specific student.
            calculated_grades = self.controller.calculate_grades_for_student(student_id)

            # Iterate through all columns in the row.
            for col_index in range(self.columnCount()):
                # Get the column information.
                col_info = self.column_info_map.get(col_index, {})
                # Get the column name.
                col_name = col_info.get('name', '')
                # Get the widget currently set for this cell.
                widget = self.itemWidget(item, col_index)
                # If the widget is a QLabel (used for displaying calculated grades)...
                if isinstance(widget, QLabel):
                    # Update the label's text based on the column name.
                    if 'Midterm Grade' in col_name:
                        widget.setText(calculated_grades['midterm_avg'])
                    elif 'Final Term Grade' in col_name:
                        widget.setText(calculated_grades['finalterm_avg'])
                    elif 'Final Grade' in col_name:
                        widget.setText(calculated_grades['final_grade'])

    # --- Widget Creation Helpers ---
    # Helper methods to create standardized input and display widgets.
    def create_grade_input(self, value=""):
        # Create a QLineEdit widget.
        input_field = QLineEdit()
        # Set its initial text/value.
        input_field.setText(value)
        # Align the text in the center.
        input_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Set a placeholder text to guide the user.
        input_field.setPlaceholderText("e.g., 50/100")
        # Apply styling using CSS-like syntax.
        input_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 3px;
                padding: 6px;
                background-color: white;
                font-size: 11px;
                color: #000000;
            }
            QLineEdit:focus {
                border: 2px solid #084924;
                background-color: #F9FFF9;
                color: #000000;
            }
            QLineEdit:hover {
                border: 1px solid #084924;
                color: #000000;
            }
        """)
        return input_field

    def create_grade_display(self, value="0.00"):
        # Create a QLabel widget.
        label = QLabel(value)
        # Align the text in the center.
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Apply styling using CSS-like syntax.
        label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-weight: bold;
                font-size: 11px;
                padding: 6px;
                background-color: #F8F9FA;
                border-radius: 3px;
                border: 1px solid #E0E0E0;
            }
        """)
        return label


# --- MainWindow Class ---
# The main application window that contains the UI elements.
class MainWindow(QMainWindow):
    # --- Constructor ---
    # Initializes the main window, its layout, and child widgets.
    def __init__(self):
        super().__init__()

        # Set window properties.
        self.setWindowTitle("Classroom Grades")
        self.setAutoFillBackground(True)
        self.setFixedSize(QSize(1400, 700)) # Fixed window size.

        # --- Initialize Model and Controller ---
        # Create instances of the data model and controller.
        self.grade_model = GradeDataModel()
        self.grade_controller = GradeController(self.grade_model)

        # --- Main Container Setup ---
        # Create a central widget to hold the main layout.
        container = QWidget()
        container.setAutoFillBackground(True)
        # Set the background color of the container to white.
        pal = container.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor("white"))
        container.setPalette(pal)

        # --- Main Layout Setup ---
        # Create the main vertical layout manager.
        main_layout = QVBoxLayout()
        # Set margins around the main layout.
        main_layout.setContentsMargins(30, 30, 30, 30)
        # Set spacing between items in the main layout.
        main_layout.setSpacing(20)

        # --- Header Layout Setup ---
        # Create a horizontal layout for the top bar elements.
        header_layout = QHBoxLayout()

        # --- Rubrics Dropdown ---
        # Create a combo box for selecting rubrics.
        self.rubrics_combo = QComboBox()
        # Add items to the combo box.
        self.rubrics_combo.addItems([
            "Overall Lecture",
            "Performance Task",
            "Quiz",
            "Exam"
        ])
        # Set a fixed width for the combo box.
        self.rubrics_combo.setFixedWidth(150)
        # Apply styling to the combo box.
        self.rubrics_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 5px;
                font-size: 12px;
                color: #084924;
                background-color: white;
                font-weight: bold;
            }
            QComboBox:focus {
                border: 2px solid #084924;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #084924;
                selection-background-color: #E8F5E8;
            }
        """)

        # --- Spacer ---
        # Add a spacer item to push elements to the sides.
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # --- Info Label ---
        # Create a label for informational text.
        info_label = QLabel("💡 Click column headers with < to expand/collapse")
        # Apply styling to the info label.
        info_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 11px;
                font-style: italic;
            }
        """)

        # --- Grading System Label ---
        # Create a label for the grading system.
        grading_label = QLabel("Grading System")
        # Apply styling to the grading system label.
        grading_label.setStyleSheet("""
            QLabel {
                background-color: #FDC601;
                color: white;
                border-radius: 3px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 12px;
            }
        """)

        # --- Download Button ---
        # Create a download button.
        download_button = QPushButton("📥 Download")
        # Apply styling to the download button.
        download_button.setStyleSheet("""
            QPushButton {
                background-color: #084924;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0A5A2A;
            }
        """)

        # --- Add Header Elements to Layout ---
        # Add the rubrics combo box to the header layout.
        header_layout.addWidget(self.rubrics_combo)
        # Add the spacer to the header layout.
        header_layout.addItem(spacer)
        # Add the info label to the header layout.
        header_layout.addWidget(info_label)
        # Add the grading system label to the header layout.
        header_layout.addWidget(grading_label)
        # Add the download button to the header layout.
        header_layout.addWidget(download_button)

        # --- Create Grades Table ---
        # Create an instance of the main table widget, passing the model and controller.
        self.grades_table = CollapsibleGradesTable(self.grade_model, self.grade_controller)

        # --- Add Elements to Main Layout ---
        # Add the header layout to the main vertical layout.
        main_layout.addLayout(header_layout)
        # Add the grades table to the main vertical layout.
        main_layout.addWidget(self.grades_table)

        # --- Finalize Window Setup ---
        # Set the main layout on the container widget.
        container.setLayout(main_layout)
        # Set the container widget as the central widget of the main window.
        self.setCentralWidget(container)


# --- Application Entry Point ---
# The standard Python idiom for running the application.
if __name__ == "__main__":
    # Create the QApplication instance (required for any Qt application).
    app = QApplication(sys.argv)
    # Create an instance of the main window.
    window = MainWindow()
    # Show the main window.
    window.show()
    # Execute the application's event loop.
    # The program will run here until the window is closed.
    app.exec()
