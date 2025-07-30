#!/usr/bin/env python3

"""Fix and regenerate complete type stubs with all tags from the checklist."""

# All tags from HTML_TAGS_CHECKLIST.md that should be implemented
html_tags = [
    # A-C Tags
    ('A', 'Hyperlink'),
    ('Abbr', 'Abbreviation'),
    ('Address', 'Contact information'),
    ('Area', 'Image map area'),
    ('Article', 'Article content'),
    ('Aside', 'Sidebar content'),
    ('Audio', 'Audio content'),
    ('B', 'Bold text'),
    ('Base', 'Document base URL'),
    ('Bdi', 'Bidirectional text isolation'),
    ('Bdo', 'Bidirectional text override'),
    ('Blockquote', 'Block quotation'),
    ('Body', 'Document body'),
    ('Br', 'Line break'),
    ('Button', 'Clickable button'),
    ('Canvas', 'Graphics canvas'),
    ('Caption', 'Table caption'),
    ('Cite', 'Citation'),
    ('Code', 'Computer code'),
    ('Col', 'Table column'),
    ('Colgroup', 'Table column group'),
    
    # D-H Tags
    ('Data', 'Machine-readable data'),
    ('Datalist', 'Input options list'),
    ('Dd', 'Description list description'),
    ('Del', 'Deleted text'),
    ('Details', 'Disclosure widget'),
    ('Dfn', 'Definition term'),
    ('Dialog', 'Dialog box'),
    ('Div', 'Division/section'),
    ('Dl', 'Description list'),
    ('Dt', 'Description list term'),
    ('Em', 'Emphasized text'),
    ('Embed', 'External content'),
    ('Fieldset', 'Form field grouping'),
    ('Figcaption', 'Figure caption'),
    ('Figure', 'Figure with caption'),
    ('Footer', 'Page/section footer'),
    ('Form', 'HTML form'),
    ('H1', 'Level 1 heading'),
    ('H2', 'Level 2 heading'),
    ('H3', 'Level 3 heading'),
    ('H4', 'Level 4 heading'),
    ('H5', 'Level 5 heading'),
    ('H6', 'Level 6 heading'),
    ('Head', 'Document head'),
    ('Header', 'Page/section header'),
    ('Hgroup', 'Heading group'),
    ('Hr', 'Horizontal rule'),
    ('Html', 'HTML document'),
    
    # I-O Tags
    ('I', 'Italic text'),
    ('Iframe', 'Inline frame'),
    ('Img', 'Image'),
    ('Input', 'Input field'),
    ('Ins', 'Inserted text'),
    ('Kbd', 'Keyboard input'),
    ('Label', 'Form label'),
    ('Legend', 'Fieldset legend'),
    ('Li', 'List item'),
    ('Link', 'External resource link'),
    ('Main', 'Main content'),
    ('Map', 'Image map'),
    ('Mark', 'Highlighted text'),
    ('Menu', 'Menu list'),
    ('Meta', 'Metadata'),
    ('Meter', 'Scalar measurement'),
    ('Nav', 'Navigation links'),
    ('Noscript', 'No script fallback'),
    ('Object', 'Embedded object'),
    ('Ol', 'Ordered list'),
    ('Optgroup', 'Option group'),
    ('OptionEl', 'Select option'),  # Note: OptionEl instead of Option
    
    # P-S Tags
    ('P', 'Paragraph'),
    ('Picture', 'Picture container'),
    ('Pre', 'Preformatted text'),
    ('Progress', 'Progress indicator'),
    ('Q', 'Short quotation'),
    ('Rp', 'Ruby parentheses'),
    ('Rt', 'Ruby text'),
    ('Ruby', 'Ruby annotation'),
    ('S', 'Strikethrough text'),
    ('Samp', 'Sample output'),
    ('Script', 'Client-side script'),
    ('Section', 'Document section'),
    ('Select', 'Dropdown list'),
    ('Small', 'Small text'),
    ('Source', 'Media resource'),
    ('Span', 'Inline section'),
    ('Strong', 'Important text'),
    ('Style', 'Style information'),
    ('Sub', 'Subscript'),
    ('Summary', 'Details summary'),
    ('Sup', 'Superscript'),
    
    # T-Z Tags
    ('Table', 'Table'),
    ('Tbody', 'Table body'),
    ('Td', 'Table cell'),
    ('Template', 'Template container'),
    ('Textarea', 'Multiline text input'),
    ('Tfoot', 'Table footer'),
    ('Th', 'Table header cell'),
    ('Thead', 'Table header'),
    ('Time', 'Date/time'),
    ('Title', 'Document title'),
    ('Tr', 'Table row'),
    ('Track', 'Media track'),
    ('U', 'Underlined text'),
    ('Ul', 'Unordered list'),
    ('Var', 'Variable'),
    ('Video', 'Video content'),
    ('Wbr', 'Word break opportunity'),
]

# SVG tags
svg_tags = [
    ('Svg', 'SVG graphics container'),
    ('Circle', 'Circle in SVG'),
    ('Rect', 'Rectangle in SVG'),
    ('Line', 'Line in SVG'),
    ('Path', 'Path in SVG'),
    ('Polygon', 'Polygon in SVG'),
    ('Polyline', 'Polyline in SVG'),
    ('Ellipse', 'Ellipse in SVG'),
    ('Text', 'Text in SVG'),
    ('G', 'Group in SVG'),
    ('Defs', 'Reusable SVG elements'),
    ('Use', 'Reusable SVG element instance'),
    ('Symbol', 'Reusable SVG symbol'),
    ('Marker', 'Marker for SVG shapes'),
    ('LinearGradient', 'Linear gradient in SVG'),
    ('RadialGradient', 'Radial gradient in SVG'),
    ('Stop', 'Gradient stop in SVG'),
    ('Pattern', 'Pattern in SVG'),
    ('ClipPath', 'Clipping path in SVG'),
    ('Mask', 'Mask in SVG'),
    ('Image', 'Image in SVG'),
    ('ForeignObject', 'Foreign content in SVG'),
]

# Header content
header = '''"""
Type stubs for RustyTags - High-performance HTML generation library
"""

from typing import Any, Union, overload

# Type aliases for better type hints
AttributeValue = Union[str, int, float, bool]
Child = Union[str, int, float, bool, "HtmlString", "TagBuilder", Any]

class HtmlString:
    """Core HTML content container with optimized memory layout"""
    content: str
    
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    def render(self) -> str: ...
    def _repr_html_(self) -> str: ...
    def __html__(self) -> str: ...

class TagBuilder:
    """Callable tag builder for FastHTML-style chaining"""
    
    def __call__(self, *children: Child, **kwargs: AttributeValue) -> HtmlString:
        """Add children and attributes to create final HTML"""
        ...
    
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    def render(self) -> str: ...
    def _repr_html_(self) -> str: ...
    def __html__(self) -> str: ...


# HTML Tag Functions with overloads for callable functionality

'''

# Generate all tag functions
content = header

# HTML tags
for tag_name, doc in html_tags:
    content += f'''@overload
def {tag_name}(**kwargs: AttributeValue) -> TagBuilder: ...
@overload  
def {tag_name}(*children: Child, **kwargs: AttributeValue) -> HtmlString: ...
def {tag_name}(*children: Child, **kwargs: AttributeValue) -> Union[TagBuilder, HtmlString]:
    """Defines a {doc.lower()}"""
    ...

'''

# SVG tags  
content += "# SVG Tag Functions\n\n"
for tag_name, doc in svg_tags:
    content += f'''@overload
def {tag_name}(**kwargs: AttributeValue) -> TagBuilder: ...
@overload  
def {tag_name}(*children: Child, **kwargs: AttributeValue) -> HtmlString: ...
def {tag_name}(*children: Child, **kwargs: AttributeValue) -> Union[TagBuilder, HtmlString]:
    """Defines a {doc.lower()}"""
    ...

'''

# Custom tag function
content += '''# Custom tag function
@overload
def CustomTag(tag_name: str, **kwargs: AttributeValue) -> TagBuilder: ...
@overload  
def CustomTag(tag_name: str, *children: Child, **kwargs: AttributeValue) -> HtmlString: ...
def CustomTag(tag_name: str, *children: Child, **kwargs: AttributeValue) -> Union[TagBuilder, HtmlString]:
    """Creates a custom HTML tag with any tag name"""
    ...

'''

# Add footer
content += '''__version__: str
__author__: str 
__description__: str
'''

# Write updated stubs
with open('rusty_tags/__init__.pyi', 'w') as f:
    f.write(content)

print(f"Generated complete type stubs with {len(html_tags)} HTML tags and {len(svg_tags)} SVG tags")
print("Added missing methods: __html__, _repr_html_, render to TagBuilder")
print("Added missing method: __html__ to HtmlString")