# Streamlit Kanban Board Component

A powerful, interactive Kanban board component for Streamlit applications, designed for deal pipeline management, project tracking, and workflow visualization. Features drag-and-drop functionality, role-based permissions, detailed dialogs, and source-based styling.

![Kanban Board Preview](https://via.placeholder.com/800x400?text=Kanban+Board+Component)

## ✨ Features

### Core Functionality
- **Drag & Drop Interface**: Native HTML5 drag-and-drop with smooth animations
- **Interactive Deal Cards**: Click cards to open detailed dialogs with full Streamlit widget support
- **Customizable Stages**: Define pipeline stages with custom names and colors
- **Source-Based Styling**: Automatic card styling based on data source (VV=blue, OF=orange)
- **Role-Based Permissions**: Control drag/drop access and stage visibility by user role

### Advanced Capabilities
- **Permission System**: Granular control over user actions (drag, approve, reject, edit)
- **Visual Feedback**: Dynamic column highlighting and lock icons during drag operations
- **Responsive Design**: Mobile-friendly layout with touch support
- **Custom HTML**: Embed custom HTML content in deal cards
- **Session State Integration**: Seamless integration with Streamlit's session state

### User Experience
- **Smooth Animations**: CSS transitions for professional feel
- **Loading States**: Visual feedback during operations
- **Error Prevention**: Permission validation before allowing actions
- **Accessibility**: Keyboard navigation and screen reader support

## 🚀 Installation

### From PyPI
```bash
pip install streamlit-kanban-board-goviceversa
```

### From Test PyPI (for testing)
```bash
pip install -i https://test.pypi.org/simple/ streamlit-kanban-board-goviceversa
```

### From Source
```bash
git clone https://github.com/goviceversa-com/streamlit_kanban_board.git
cd streamlit_kanban_board
pip install -e .
```

## 🎯 Quick Start

### Basic Usage

```python
import streamlit as st
from streamlit_kanban_board import kanban_board

# Define your pipeline stages
stages = [
    {"id": "todo", "name": "To Do", "color": "#3498db"},
    {"id": "in_progress", "name": "In Progress", "color": "#f39c12"},
    {"id": "done", "name": "Done", "color": "#27ae60"}
]

# Define your deals/items
deals = [
    {
        "id": "deal_001",
        "stage": "todo",
        "deal_id": "D-2024-001",
        "company_name": "Acme Corp",
        "product_type": "Term Loan",
        "date": "2024-01-15",
        "underwriter": "John Smith",
        "source": "VV"
    }
]

# Display the kanban board
result = kanban_board(
    board=stages,
    data=deals,
    key="my_kanban_board"
)

# Handle interactions
if result:
    if result.get("type") == "card_move":
        st.success(f"Deal moved to: {result['stage']}")
    elif result.get("type") == "card_click":
        st.info(f"Deal clicked: {result['data']['company_name']}")
```

## 📋 API Reference

### `kanban_board()`

Creates a Kanban board component with drag-and-drop functionality.

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `board` | `list[dict]` | Required | Stage definitions with id, name, and color |
| `data` | `list[dict]` | Required | Deal/item data with required fields |
| `key` | `str` | `None` | Unique component key for Streamlit |
| `draggable_stages` | `list[str]` | `None` | Stages user can drag to (None = all) |

#### Stage Format

Stages are defined as dictionaries with id, name, and optional color:

```python
stages = [
    {"id": "todo", "name": "To Do", "color": "#3498db"},
    {"id": "in_progress", "name": "In Progress", "color": "#f39c12"},
    {"id": "done", "name": "Done", "color": "#27ae60"}
]
```

#### Data Format

Each item must include these required fields:

```python
item = {
    "id": "unique_item_id",           # Required: Unique identifier
    "stage": "current_stage_id",      # Required: Current stage
    "deal_id": "D-2024-001",         # Required: Display ID
    "company_name": "Company Name",   # Required: Company name
    
    # Optional fields
    "product_type": "Term Loan",      # Product type (shown as badge)
    "date": "2024-01-15",            # Relevant date
    "underwriter": "John Smith",      # Underwriter name
    "amount": 1000000,               # Deal amount
    "risk_rating": "A",              # Risk rating
    "source": "VV",                  # Source (VV=blue, OF=orange)
    "custom_html": "<div>...</div>"   # Custom HTML content
}
```

#### Return Value

Returns a dictionary with interaction data:

```python
{
    "type": "card_move" | "card_click",  # Type of interaction
    "data": {...},                       # Item data
    "stage": "stage_id"                  # Target stage (for moves)
}
```

## 🔐 Role-Based Permissions

### Permission System

Define user roles with granular permissions:

```python
USER_ROLES = {
    "admin": {
        "name": "Administrator",
        "can_drag_to": ["stage1", "stage2", "stage3"],
        "can_view_stages": ["stage1", "stage2", "stage3"],
        "can_approve": True,
        "can_reject": True,
        "can_hold": True,
        "can_edit_deal": True
    },
    "viewer": {
        "name": "Viewer",
        "can_drag_to": [],              # No drag permissions
        "can_view_stages": ["stage1"],  # Limited visibility
        "can_approve": False,
        "can_reject": False,
        "can_hold": False,
        "can_edit_deal": False
    }
}
```

### Implementation Example

```python
# Get current user permissions
def get_user_permissions():
    return USER_ROLES[st.session_state.current_user_role]

def get_draggable_stages_for_user():
    permissions = get_user_permissions()
    return permissions["can_drag_to"]

# Apply permissions to component
result = kanban_board(
    board=visible_stages,
    data=filtered_deals,
    draggable_stages=get_draggable_stages_for_user(),
    key=f"kanban_{st.session_state.current_user_role}"
)
```

## 🎨 Styling and Customization

### Source-Based Card Colors

Cards automatically style based on the `source` field:

- **VV Source**: Light blue background
- **OF Source**: Light orange background
- **Default**: Standard white background

### Custom HTML Content

Add rich content to deal cards:

```python
deal = {
    "id": "deal_001",
    "stage": "review",
    "deal_id": "D-2024-001",
    "company_name": "Acme Corp",
    "custom_html": '''
        <div class="priority-high">High Priority</div>
        <div class="status-urgent">Urgent Review</div>
        <div>Additional custom content</div>
    '''
}
```

### CSS Classes

The component includes these CSS classes for styling:

- `.kanban-board` - Main container
- `.kanban-column` - Stage columns
- `.kanban-card` - Individual deal cards
- `.kanban-card[data-source="VV"]` - VV source cards
- `.kanban-card[data-source="OF"]` - OF source cards
- `.drop-disabled` - Disabled drop zones
- `.not-draggable` - Non-draggable cards

## 🔄 Advanced Usage

### Dialog Integration

Handle card clicks to show detailed dialogs:

```python
# Handle card clicks
if result and result.get("type") == "card_click":
    st.session_state.selected_deal = result["data"]
    st.session_state.show_deal_dialog = True

# Show dialog
if st.session_state.get("show_deal_dialog") and st.session_state.get("selected_deal"):
    @st.dialog(f"Deal Details: {st.session_state.selected_deal['deal_id']}")
    def show_deal_details():
        deal = st.session_state.selected_deal
        
        # Display deal information
        st.write(f"**Company:** {deal['company_name']}")
        st.write(f"**Product:** {deal['product_type']}")
        st.write(f"**Amount:** ${deal.get('amount', 0):,.2f}")
        
        # Add interactive elements
        if st.button("Approve Deal"):
            # Handle approval logic
            pass
            
        if st.button("Close"):
            st.session_state.show_deal_dialog = False
            st.rerun()
    
    show_deal_details()
```

### Real-time Updates

Integrate with session state for real-time updates:

```python
# Initialize deals in session state
if "deals" not in st.session_state:
    st.session_state.deals = load_deals_from_database()

# Handle deal movements
if result and result.get("type") == "card_move":
    moved_data = result["data"]
    new_stage = result["stage"]
    
    # Update database
    update_deal_stage(moved_data["id"], new_stage)
    
    # Update session state
    for deal in st.session_state.deals:
        if deal["id"] == moved_data["id"]:
            deal["stage"] = new_stage
            break
```

### Filtering and Search

Combine with Streamlit widgets for filtering:

```python
# Filter controls
col1, col2, col3 = st.columns(3)

with col1:
    selected_stages = st.multiselect("Stages", stage_options)

with col2:
    search_term = st.text_input("Search companies")

with col3:
    selected_sources = st.multiselect("Sources", ["VV", "OF"])

# Apply filters
filtered_deals = [
    deal for deal in st.session_state.deals
    if (not selected_stages or deal["stage"] in selected_stages)
    and (not search_term or search_term.lower() in deal["company_name"].lower())
    and (not selected_sources or deal.get("source") in selected_sources)
]

# Display filtered board
result = kanban_board(
    board=stages,
    data=filtered_deals,
    key="filtered_kanban"
)
```

## 📊 Example Use Cases

### Deal Pipeline Management
- Track loan applications through approval stages
- Role-based access for underwriters, risk managers, and administrators
- Source-specific workflows (VV vs OF deals)

### Project Management
- Kanban-style project tracking
- Team member assignments and permissions
- Custom project metadata

### Sales Pipeline
- Lead qualification and progression
- Sales team collaboration
- Customer interaction tracking

### Content Workflow
- Editorial content approval process
- Multi-stage review workflows
- Publication pipeline management

## 🧪 Testing

### Quick Test
Run the simple demo to test basic functionality:

```bash
streamlit run simple_demo.py
```

### Full Demo
Run the comprehensive sample application:

```bash
streamlit run sample.py
```

## 🔧 Development

### Building from Source

```bash
# Clone repository
git clone https://github.com/goviceversa-com/streamlit_kanban_board.git
cd streamlit_kanban_board

# Install development dependencies
cd streamlit_kanban_board/frontend
npm install

# Build component
npm run build

# Install Python package
cd ..
pip install -e .
```

### Project Structure

```
streamlit_kanban_board/
├── streamlit_kanban_board/
│   ├── __init__.py              # Python component wrapper
│   └── frontend/
│       ├── src/
│       │   ├── StreamlitKanbanBoard.tsx  # Main React component
│       │   ├── DealCard.tsx              # Individual card component
│       │   ├── KanbanComponent.css       # Styling
│       │   ├── types.ts                  # TypeScript types
│       │   └── index.tsx                 # Entry point
│       ├── public/
│       ├── package.json
│       └── build/               # Built component files
├── sample.py                    # Full demo application
├── simple_demo.py               # Simple demo
├── pyproject.toml              # Python package configuration
├── setup.py                    # Package setup
└── README.md
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Guidelines
1. Follow TypeScript best practices for React components
2. Maintain backwards compatibility for Python API
3. Add tests for new features
4. Update documentation for API changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 Check the API documentation above
- 🧪 Run the sample applications for examples
- 🐛 Report issues on GitHub
- 💬 Ask questions in discussions

## 🙏 Acknowledgments

- Built with [Streamlit Components](https://docs.streamlit.io/library/components)
- Drag and drop functionality using native HTML5 APIs
- Styled with modern CSS animations and transitions
