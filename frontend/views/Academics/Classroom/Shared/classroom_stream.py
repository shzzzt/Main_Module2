# classroom_stream.py
from PyQt6.QtWidgets import QWidget, QLabel, QFrame, QVBoxLayout, QHBoxLayout, QPushButton,QSizePolicy
from PyQt6.QtCore import pyqtSignal, Qt
from widgets.stream_post_ui import Ui_ClassroomStreamContent

class ClassroomStream(QWidget):
    post_selected = pyqtSignal(dict)

    def __init__(self, cls, username, roles, primary_role, token, controller, parent=None):
        super().__init__(parent)
        self.cls = cls
        self.controller = controller
        self.controller.set_class(cls["id"])
        self.username = username
        self.roles = roles
        self.primary_role = primary_role
        self.token = token
        
        # Setup the UI from the .ui file
        self.ui = Ui_ClassroomStreamContent()
        self.ui.setupUi(self)
        
        # Set class information in the header
        self.setup_class_info()
        
        # Setup the existing template widgets
        self.setup_existing_widgets()
        
        self.load_posts()

    def setup_class_info(self):
        """Set the class information in the header"""
        self.ui.courseCode_label.setText(self.cls.get("code", ""))
        self.ui.courseTitle_label.setText(self.cls.get("title", ""))
        section_text = f"{self.cls.get('section', '')}\n{self.cls.get('schedule', '')}"
        self.ui.courseSection_label.setText(section_text)

    def setup_existing_widgets(self):
        """Setup the existing syllabus frame and template post"""
        # Setup syllabus frame
        if hasattr(self.ui, 'syllabusFrame') and self.ui.syllabusFrame:
            # Update syllabus text if needed
            if hasattr(self.ui, 'label_2') and self.ui.label_2:
                self.ui.label_2.setText("Syllabus")
            if hasattr(self.ui, 'pushButton') and self.ui.pushButton:
                self.ui.pushButton.setText("View")
                # Connect syllabus button click
                self.ui.pushButton.clicked.connect(self.on_syllabus_click)
        
        # Hide the template post initially (we'll use it as a template)
        if hasattr(self.ui, 'postTemplate') and self.ui.postTemplate:
            self.ui.postTemplate.setVisible(False)

    def on_syllabus_click(self):
        """Handle syllabus view button click"""
        # Find syllabus post in the data
        posts = self.controller.get_posts()
        syllabus_posts = [p for p in posts if p.get("title") == "Syllabus"]
        if syllabus_posts:
            self.post_selected.emit(syllabus_posts[0])

    def load_posts(self):
        posts = self.controller.get_posts()
        print(f"Loading {len(posts)} posts in stream")
        
        # Get the stream items layout - this is the correct layout from UI
        stream_layout = self.get_stream_layout()
        if not stream_layout:
            print("Error: Could not find stream layout!")
            return
        
        # Clear existing posts (except the template)
        self.clear_stream_layout(stream_layout)
        
        if not posts:
            no_posts_label = QLabel("No posts available")
            no_posts_label.setStyleSheet("""
                QLabel {
                    color: #666;
                    font-size: 14px;
                    padding: 20px;
                    text-align: center;
                }
            """)
            stream_layout.addWidget(no_posts_label)
            return
        
        # Add regular posts (excluding syllabus which is handled separately)
        regular_posts = [p for p in posts if p.get("title") != "Syllabus"]
        for post in regular_posts:
            self.create_post_widget(post, stream_layout)

    def get_stream_layout(self):
        """Find the correct stream layout from the UI structure"""
        try:
            # The stream items layout is in: scrollArea -> scrollAreaWidgetContents -> verticalLayout_5 -> horizontalLayout_5 -> stream_item_container -> verticalLayout_6 -> stream_items_layout
            if (hasattr(self.ui, 'scrollArea') and self.ui.scrollArea and
                hasattr(self.ui, 'scrollAreaWidgetContents') and self.ui.scrollAreaWidgetContents):
                
                # Try to find the stream_items_layout
                stream_container = self.ui.scrollAreaWidgetContents.findChild(QWidget, "stream_item_container")
                if stream_container:
                    stream_layout = stream_container.findChild(QVBoxLayout, "stream_items_layout")
                    if stream_layout:
                        return stream_layout
                
                # Fallback: try to access directly through attributes
                if hasattr(self.ui, 'stream_items_layout'):
                    return self.ui.stream_items_layout
                    
        except Exception as e:
            print(f"Error finding stream layout: {e}")
        
        # Ultimate fallback: create a new layout
        print("Creating fallback layout")
        fallback_widget = QWidget()
        fallback_layout = QVBoxLayout(fallback_widget)
        self.ui.scrollArea.setWidget(fallback_widget)
        return fallback_layout

    def clear_stream_layout(self, stream_layout):
        """Clear the stream layout while preserving the template"""
        if not stream_layout:
            return
            
        # Remove all widgets except the template
        for i in range(stream_layout.count() - 1, -1, -1):
            item = stream_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                # Don't remove the template post
                if widget != getattr(self.ui, 'postTemplate', None):
                    widget.setParent(None)
                    widget.deleteLater()

                    

    def create_post_widget(self, post, stream_layout):
        """Create a post widget based on the template with proper spacing and document icon"""
        try:
            # Use the template as a base if it exists
            if hasattr(self.ui, 'postTemplate') and self.ui.postTemplate:
                # Clone the template structure
                post_frame = QFrame()
                post_frame.setStyleSheet(self.ui.postTemplate.styleSheet())
                post_frame.setFrameShape(self.ui.postTemplate.frameShape())
                post_frame.setFrameShadow(self.ui.postTemplate.frameShadow())
                
                # Create the same layout structure with better spacing
                layout = QHBoxLayout(post_frame)
                layout.setContentsMargins(15, 12, 15, 12)  # Increased padding
                layout.setSpacing(15)  # Increased spacing between icon and content
                
                # Icon with document.svg
                icon_label = QLabel()
                icon_label.setFixedSize(42, 42)  # Fixed size instead of maximum
                icon_label.setStyleSheet("""
                    QLabel {
                        background-color: #084924;
                        border-radius: 23px;
                        border: 2px solid white;
                        min-width: 42px;
                        min-height: 42px;
                    }
                """)
                icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Load and set the document icon
                try:
                    from PyQt6.QtGui import QPixmap
                    icon_path = "frontend/assets/icons/document.svg"
                    pixmap = QPixmap(icon_path)
                    if not pixmap.isNull():
                        # Scale the icon to fit within the circle
                        scaled_pixmap = pixmap.scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, 
                                                    Qt.TransformationMode.SmoothTransformation)
                        icon_label.setPixmap(scaled_pixmap)
                    else:
                        # Fallback: use text if icon not found
                        icon_label.setText("📄")
                        icon_label.setStyleSheet(icon_label.styleSheet() + """
                            QLabel {
                                color: white;
                                font-size: 16px;
                            }
                        """)
                except Exception as icon_error:
                    print(f"Error loading icon: {icon_error}")
                    # Fallback to text icon
                    icon_label.setText("📄")
                    icon_label.setStyleSheet(icon_label.styleSheet() + """
                        QLabel {
                            color: white;
                            font-size: 16px;
                        }
                    """)
                
                layout.addWidget(icon_label)
                
                # Content area with proper spacing
                content_layout = QVBoxLayout()
                content_layout.setSpacing(8)  # Increased spacing between title and date
                content_layout.setContentsMargins(0, 0, 0, 0)
                
                # Title ONLY - no author mentioned
                title = post.get("title", "")
                title_label = QLabel(title)
                title_label.setStyleSheet("""
                    QLabel {
                        font-size: 16px;
                        border: none;
                        color: #333;
                        margin: 0px;
                        padding: 0px;
                    }
                """)
                title_label.setWordWrap(True)
                title_label.setMinimumHeight(20)  # Ensure minimum height
                title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                content_layout.addWidget(title_label)
                
                # Date
                date_text = self.format_date(post.get("date", ""))
                date_label = QLabel(date_text)
                date_label.setStyleSheet("""
                    QLabel {
                        font-size: 14px;
                        border: none;
                        color: #666;
                        margin: 0px;
                        padding: 0px;
                    }
                """)
                date_label.setMinimumHeight(16)  # Ensure minimum height
                content_layout.addWidget(date_label)
                
                # Add stretch to push content to top and prevent squishing
                content_layout.addStretch()
                
                layout.addLayout(content_layout)
                layout.addStretch()
                
                # Make clickable
                post_frame.mousePressEvent = lambda event, p=post: self.handle_post_click(event, p)
                post_frame.setCursor(Qt.CursorShape.PointingHandCursor)
                
                stream_layout.addWidget(post_frame)
                
            else:
                # Fallback: simple widget
                self.create_simple_post_widget(post, stream_layout)
                
        except Exception as e:
            print(f"Error creating post widget: {e}")
            # Fallback to simple widget
            self.create_simple_post_widget(post, stream_layout)

    def create_simple_post_widget(self, post, stream_layout):
        """Create a simple post widget as fallback with proper spacing and icon"""
        try:
            # Create a frame instead of just a QLabel for better layout control
            post_frame = QFrame()
            post_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    margin: 5px;
                }
            """)
            
            layout = QHBoxLayout(post_frame)
            layout.setContentsMargins(12, 8, 12, 8)
            layout.setSpacing(10)
            
            # Icon with document.svg
            icon_label = QLabel()
            icon_label.setFixedSize(30, 30)
            icon_label.setStyleSheet("""
                QLabel {
                    background-color: #084924;
                    border-radius: 15px;
                    border: 2px solid white;
                }
            """)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Load and set the document icon
            try:
                from PyQt6.QtGui import QPixmap
                icon_path = "frontend/assets/icons/document.svg"
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, 
                                                Qt.TransformationMode.SmoothTransformation)
                    icon_label.setPixmap(scaled_pixmap)
                else:
                    icon_label.setText("📄")
                    icon_label.setStyleSheet(icon_label.styleSheet() + """
                        QLabel {
                            color: white;
                            font-size: 12px;
                        }
                    """)
            except Exception as icon_error:
                icon_label.setText("📄")
                icon_label.setStyleSheet(icon_label.styleSheet() + """
                    QLabel {
                        color: white;
                        font-size: 12px;
                    }
                """)
            
            layout.addWidget(icon_label)
            
            # Content area
            content_layout = QVBoxLayout()
            content_layout.setSpacing(4)
            content_layout.setContentsMargins(0, 0, 0, 0)
            
            # Title only
            title_label = QLabel(post.get('title', ''))
            title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
            title_label.setWordWrap(True)
            title_label.setMinimumHeight(18)
            content_layout.addWidget(title_label)
            
            # Date
            date_label = QLabel(self.format_date(post.get('date', '')))
            date_label.setStyleSheet("font-size: 12px; color: #666;")
            date_label.setMinimumHeight(14)
            content_layout.addWidget(date_label)
            
            layout.addLayout(content_layout, 1)  # Set stretch factor
            layout.addStretch()
            
            post_frame.mousePressEvent = lambda event, p=post: self.handle_post_click(event, p)
            post_frame.setCursor(Qt.CursorShape.PointingHandCursor)
            stream_layout.addWidget(post_frame)
            
        except Exception as e:
            print(f"Error creating simple post widget: {e}")

    def format_date(self, date_str):
        """Format date string for display"""
        if not date_str:
            return ""
        try:
            # Convert "2025-08-18 10:00:00" to "Aug 18"
            from datetime import datetime
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%b %d")
        except:
            return date_str.split(" ")[0] if " " in date_str else date_str

    def handle_post_click(self, event, post):
        if event.button() == Qt.MouseButton.LeftButton:
            print(f"Stream post clicked: {post['title']}")
            self.post_selected.emit(post)

    def clear(self):
        """Clear the stream layout"""
        stream_layout = self.get_stream_layout()
        if stream_layout:
            self.clear_stream_layout(stream_layout)