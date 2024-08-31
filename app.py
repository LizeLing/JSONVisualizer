import streamlit as st
import json
import re
from typing import Any, Dict, List

# Set page config
st.set_page_config(page_title="JSON Tree Visualizer", layout="wide", page_icon="🌳")

# Load external CSS
def load_css(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        return f"<style>{f.read()}</style>"

# Load and apply CSS
st.markdown(load_css("styles.css"), unsafe_allow_html=True)

# Add custom font
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

def remove_comments(json_string: str) -> str:
    pattern = r'(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)'
    regex = re.compile(pattern, re.MULTILINE | re.DOTALL)
    def _replacer(match):
        if match.group(2) is not None:
            return ""
        else:
            return match.group(1)
    return regex.sub(_replacer, json_string)

def parse_json_file(file_content: str) -> Dict[str, Any]:
    try:
        json_content = remove_comments(file_content)
        return json.loads(json_content)
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON file: {str(e)}")
        return None

def get_value_type(value: Any) -> str:
    if isinstance(value, str):
        return "string"
    elif isinstance(value, (int, float)):
        return "number"
    elif isinstance(value, bool):
        return "boolean"
    elif value is None:
        return "null"
    elif isinstance(value, dict):
        return "object"
    elif isinstance(value, list):
        return "array"
    else:
        return "unknown"

def render_json_tree(data: Any, key: str = "root", search_term: str = "", level: int = 0) -> str:
    value_type = get_value_type(data)
    
    if value_type in ["object", "array"]:
        content = "<ul>"
        if value_type == "object":
            for k, v in data.items():
                content += f"<li>{render_json_tree(v, k, search_term, level + 1)}</li>"
        else:
            for i, item in enumerate(data):
                content += f"<li>{render_json_tree(item, f'[{i}]', search_term, level + 1)}</li>"
        content += "</ul>"
        
        highlight_class = "json-highlight" if search_term and search_term.lower() in str(data).lower() else ""
        open_bracket = "{" if value_type == "object" else "["
        close_bracket = "}" if value_type == "object" else "]"
        return f"""
        <div class="tree-node {highlight_class}">
            <details {'open' if level < 2 else ''}>
                <summary>
                    <span class="json-key">{key}</span><span class="bracket">{open_bracket}</span>
                </summary>
                <div class="tree-content">
                    {content}
                </div>
            </details>
            <span class="bracket">{close_bracket}</span>
        </div>
        """
    else:
        highlight_class = "json-highlight" if search_term and search_term.lower() in str(data).lower() else ""
        if value_type == "string":
            value = f'<span class="json-string">"{data}"</span>'
        elif value_type == "number":
            value = f'<span class="json-number">{data}</span>'
        elif value_type == "boolean":
            value = f'<span class="json-boolean">{str(data).lower()}</span>'
        elif value_type == "null":
            value = f'<span class="json-null">null</span>'
        else:
            value = str(data)
        return f'<div class="tree-node {highlight_class}"><span class="json-key">{key}</span>: {value}</div>'

def search_json(data: Any, term: str, path: str = "") -> List[Dict[str, str]]:
    results = []
    if isinstance(data, dict):
        for k, v in data.items():
            new_path = f"{path}.{k}" if path else k
            if term.lower() in k.lower() or term.lower() in json.dumps(v).lower():
                results.append({"path": new_path, "key": k, "value": v})
            results.extend(search_json(v, term, new_path))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            new_path = f"{path}[{i}]"
            results.extend(search_json(item, term, new_path))
    return results

def main():
    st.title("JSON Tree Visualizer")

    # Create two columns
    left_column, right_column = st.columns([1, 2])

    with left_column:
        st.header("Upload and Search")
        # File uploader
        uploaded_file = st.file_uploader("Choose a JSON file", type="json", key="file_uploader")

        if uploaded_file is not None:
            file_content = uploaded_file.getvalue().decode("utf-8")
            json_data = parse_json_file(file_content)
            
            if json_data:
                st.success("✅ File uploaded and parsed successfully.")
                st.info(f"📁 {uploaded_file.name} ({len(file_content)} bytes)")
                
                # Search functionality
                search_term = st.text_input("🔍 Search in JSON:", key="search_input")
                
                if search_term:
                    search_results = search_json(json_data, search_term)
                    st.write(f"Found {len(search_results)} results:")
                    for result in search_results:
                        with st.expander(f"Path: {result['path']}"):
                            st.write(f"**Key:** {result['key']}")
                            st.json(result['value'])
                
                # Copy to clipboard functionality
                if st.button("📋 Copy to Clipboard"):
                    st.code(json.dumps(json_data, indent=2))
                    st.success("✅ JSON copied to clipboard! (Use Ctrl+C to copy)")
                    
    with right_column:
        st.header("JSON Tree View")
        if 'json_data' in locals():
            # JSON tree visualization
            json_tree = render_json_tree(json_data, search_term=search_term if 'search_term' in locals() else "")
            st.markdown(f"""
                <div class="json-container">
                    <div class="tree">{json_tree}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Upload a JSON file to view the tree structure.")

if __name__ == "__main__":
    main()