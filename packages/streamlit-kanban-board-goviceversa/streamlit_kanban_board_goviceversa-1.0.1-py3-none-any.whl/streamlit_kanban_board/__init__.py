import os
import streamlit.components.v1 as components

__version__ = "1.0.0"
__author__ = "Pierluigi Segatto"
__email__ = "pier@goviceversa.com"

# Export the main function
__all__ = ["kanban_board"]

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "streamlit_kanban_board",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("streamlit_kanban_board", path=build_dir)

def kanban_board(
    stages,
    deals,
    key=None,
    height=600,
    allow_empty_stages=True,
    draggable_stages=None
):
    """
    Create a Kanban board for deal pipeline management.
    
    Parameters
    ----------
    stages : list of str or list of dict
        Column definitions. Can be:
        - List of strings: ["Stage 1", "Stage 2", "Stage 3"]
        - List of dicts: [{"id": "stage1", "name": "Initial Review", "color": "#e3f2fd"}]
    
    deals : list of dict
        Deal data. Each deal should have:
        - id: unique identifier
        - stage: current stage (must match stage id/name)
        - deal_id: deal identifier for display
        - company_name: company name
        - product_type: product type (shown as badge)
        - date: relevant date (e.g., submission date)
        - underwriter: underwriter name
        - custom_html: (optional) additional HTML content below defaults
        
        Example:
        {
            "id": "deal_123",
            "stage": "initial_review", 
            "deal_id": "D-2024-001",
            "company_name": "Acme Corp",
            "product_type": "Term Loan",
            "date": "2024-01-15",
            "underwriter": "John Smith",
            "custom_html": "<div class='priority-high'>High Priority</div>"
        }
    
    key : str
        Unique key for the component
    
    height : int
        Height of the kanban board in pixels
        
    allow_empty_stages : bool
        Whether to show stages with no deals
        
    draggable_stages : list of str, optional
        List of stage IDs that the current user can drag deals to/from.
        If None, all stages are draggable (default behavior).
        Use empty list [] to disable all dragging.
    
    Returns
    -------
    dict
        Component state with:
        - deals: updated deals list with new stages
        - moved_deal: info about last moved deal (if any)
        - clicked_deal: info about last clicked deal (if any)
    """
    
    # Normalize stages format
    normalized_stages = []
    for stage in stages:
        if isinstance(stage, str):
            normalized_stages.append({"id": stage, "name": stage, "color": None})
        else:
            normalized_stages.append({
                "id": stage.get("id", stage.get("name", "")),
                "name": stage.get("name", stage.get("id", "")),
                "color": stage.get("color", None)
            })
    
    # Validate deals have required fields
    for deal in deals:
        required_fields = ["id", "stage", "deal_id", "company_name"]
        missing_fields = [field for field in required_fields if field not in deal]
        if missing_fields:
            raise ValueError(f"Deal {deal.get('id', 'unknown')} missing required fields: {missing_fields}")
    
    # Handle draggable_stages parameter
    if draggable_stages is None:
        # Default behavior - all stages are draggable
        draggable_stages = [stage["id"] for stage in normalized_stages]
    elif draggable_stages == []:
        # Explicitly disable all dragging
        draggable_stages = []
    
    component_value = _component_func(
        stages=normalized_stages,
        deals=deals,
        height=height,
        allow_empty_stages=allow_empty_stages,
        draggable_stages=draggable_stages,
        key=key,
        default={"deals": deals, "moved_deal": None, "clicked_deal": None}
    )
    
    return component_value 