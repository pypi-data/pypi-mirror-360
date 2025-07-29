import enum
from typing import Any, Dict, List, Optional, Union
import halogen
import halogen.schema
import uri_template

class HALFormsMethod(str, enum.Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    
class HALFormsPropertyType(str, enum.Enum):
    # Basic input types
    hidden = "hidden"
    text = "text"
    textarea = "textarea"
    search = "search"
    tel = "tel"
    url = "url"
    email = "email"
    password = "password"
    
    # Date and time inputs
    date = "date"
    month = "month"
    week = "week"
    time = "time"
    datetime = "datetime"
    datetime_local = "datetime-local"
    
    # Numeric inputs
    number = "number"
    range = "range"
    
    # Color picker
    color = "color"
    
    # Selection inputs
    checkbox = "checkbox"
    radio = "radio"
    
    # File inputs
    file = "file"
    
    # Button inputs
    button = "button"
    submit = "submit"
    reset = "reset"
    
    # Image input
    image = "image"
    
    # Selection lists (not strictly input types but related)
    select = "select"
    datalist = "datalist"
    
    # Non-standard but useful types
    dropdown = "dropdown"  # Custom type for dropdown menus

class HALFormsOptionsLink:
    """
    Represents a link attribute in the options object that points to an external resource
    containing possible values for a property.
    """
    def __init__(self, href: str, templated: bool = False, type: str = "application/json"):
        """
        Initialize a HALFormsOptionsLink.
        
        Args:
            href: The URL associated with the link. Required.
            templated: Boolean indicating if the href contains a URI Template. Default is False.
            type: A hint indicating the media type expected when dereferencing the resource. Default is "application/json".
        """
        self.href = href
        self.templated = templated
        
        # Validate URI template if templated is True
        if templated:
            if not uri_template.validate(template=href):
                raise ValueError(f"Invalid URI template: {href}")
        
        self.type = type
    
    def expand_template(self, **kwargs) -> str:
        """
        Expand the URI template with the provided variables.
        
        Args:
            **kwargs: Variables to use for template expansion
            
        Returns:
            The expanded URI
        """
        if not self.templated:
            return self.href
        
        return str(uri_template.URITemplate(self.href).expand(**kwargs))
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize the link to a dictionary."""
        return HALFormsOptionsLinkSchema.serialize(self)
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'HALFormsOptionsLink':
        """
        Deserialize a dictionary to a HALFormsOptionsLink object.
        
        Args:
            data: Dictionary containing link data
            
        Returns:
            A new HALFormsOptionsLink instance
        """
        return cls(
            href=data['href'],
            templated=data.get('templated', False),
            type=data.get('type', 'application/json')
        )

class HALFormsOptionsValueItem:
    """
    Represents a single value item in the options.inline array.
    Can be a simple string or a prompt/value pair.
    """
    def __init__(self, value: str, prompt: Optional[str] = None, **additional_fields):
        """
        Initialize a HALFormsOptionsValueItem.
        
        Args:
            value: The value of the option
            prompt: The display text for the option (if None, value is used as prompt)
            **additional_fields: Any additional fields to include
        """
        self.value = value
        self.prompt = prompt if prompt is not None else value
        self.additional_fields = additional_fields
    
    def serialize(self) -> Union[str, Dict[str, Any]]:
        """
        Serialize the value item to either a string (if only value is set)
        or a dictionary (if prompt is different from value or additional fields exist).
        """
        if not self.additional_fields and self.prompt == self.value:
            return self.value
        
        result = {"prompt": self.prompt, "value": self.value}
        result.update(self.additional_fields)
        return result
    
    @classmethod
    def deserialize(cls, data: Union[str, Dict[str, Any]]) -> 'HALFormsOptionsValueItem':
        """
        Deserialize a string or dictionary to a HALFormsOptionsValueItem.
        
        Args:
            data: String or dictionary representing the value item
            
        Returns:
            A new HALFormsOptionsValueItem instance
        """
        if isinstance(data, str):
            return cls(value=data)
        
        value = data.get("value", "")
        prompt = data.get("prompt", None)
        
        # Extract additional fields (anything that's not prompt or value)
        additional_fields = {k: v for k, v in data.items() if k not in ["prompt", "value"]}
        
        return cls(value=value, prompt=prompt, **additional_fields)

class HALFormsOptions:
    """
    Represents the options object that provides a list of possible values for a property.
    """
    def __init__(
        self,
        inline: Optional[List[Union[str, Dict[str, Any], HALFormsOptionsValueItem]]] = None,
        link: Optional[HALFormsOptionsLink] = None,
        maxItems: Optional[int] = None,
        minItems: Optional[int] = None,
        promptField: str = "prompt",
        selectedValues: Optional[List[str]] = None,
        valueField: str = "value"
    ):
        """
        Initialize a HALFormsOptions object.
        
        Args:
            inline: A list of possible values. Optional.
            link: A link object pointing to an external resource with possible values. Optional.
            maxItems: Maximum number of items to return in selectedValues. Optional.
            minItems: Minimum number of items to return in selectedValues. Optional.
            promptField: Name of the field to use as the prompt. Default is "prompt".
            selectedValues: Array of pre-selected values. Optional.
            valueField: Name of the field to use as the value. Default is "value".
        """
        # Process inline values to ensure they're all HALFormsOptionsValueItem objects
        self._inline_items : Optional[List[HALFormsOptionsValueItem]] = None
        if inline:
            self._inline_items = []
            for item in inline:
                if isinstance(item, HALFormsOptionsValueItem):
                    self._inline_items.append(item)
                else:
                    self._inline_items.append(HALFormsOptionsValueItem.deserialize(item))
        
        self.link = link
        self.maxItems = maxItems
        self.minItems = minItems
        self.promptField = promptField
        self.selectedValues = selectedValues or []
        self.valueField = valueField
    
    @property
    def inline(self) -> Optional[List[Union[str, Dict[str, Any]]]]:
        """
        Get the serialized inline values.
        
        Returns:
            A list of serialized value items
        """
        return [item.serialize() for item in self._inline_items] if self._inline_items else None
    
    def add_inline_value(self, value: str, prompt: Optional[str] = None, **additional_fields) -> None:
        """
        Add a value to the inline list.
        
        Args:
            value: The value to add
            prompt: The display text for the value (if None, value is used)
            **additional_fields: Any additional fields to include
        """
        if not self._inline_items:
            self._inline_items = []
        self._inline_items.append(HALFormsOptionsValueItem(
            value=value, 
            prompt=prompt, 
            **additional_fields
        ))
    
    def serialize(self) -> Dict[str, Any]:
        """Serialize the options to a dictionary."""
        result: Dict[str, Any] = {}
        
        # Only include inline if there are items
        if self._inline_items:
            result["inline"] = self.inline
        
        # Include link if present
        if self.link:
            result["link"] = self.link.serialize()
        
        # Include other fields if they have values
        if self.maxItems is not None:
            result["maxItems"] = self.maxItems
        
        if self.minItems is not None:
            result["minItems"] = self.minItems
        
        if self.promptField != "prompt":
            result["promptField"] = self.promptField
            
        if self.selectedValues:
            result["selectedValues"] = self.selectedValues
            
        if self.valueField != "value":
            result["valueField"] = self.valueField
            
        return result
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'HALFormsOptions':
        """
        Deserialize a dictionary to a HALFormsOptions object.
        
        Args:
            data: Dictionary containing options data
            
        Returns:
            A new HALFormsOptions instance
        """
        # Process link if present
        link_data = data.get('link')
        link = HALFormsOptionsLink.deserialize(link_data) if link_data else None
        
        # Process inline values if present
        inline_data = data.get('inline', [])
        
        return cls(
            inline=inline_data,  # Will be processed in __init__
            link=link,
            maxItems=data.get('maxItems'),
            minItems=data.get('minItems'),
            promptField=data.get('promptField', 'prompt'),
            selectedValues=data.get('selectedValues'),
            valueField=data.get('valueField', 'value')
        )
    
class HALFormsProperty(object):
    def __init__(self, name: str, type: Optional[HALFormsPropertyType] = None, prompt: Optional[str] = None, readOnly: Optional[bool] = None,
                 regex: Optional[str] = None, required: Optional[bool] = None, templated: Optional[bool] = None,
                 value: Optional[str] = None, cols: Optional[int] = None, max: Optional[int] = None,
                 maxLength: Optional[int] = None, min: Optional[int] = None, minLength: Optional[int] = None,
                 options: Optional[HALFormsOptions] = None, placeholder: Optional[str] = None,
                 rows: Optional[int] = None, step: Optional[int] = None):
        self.name: str = name
        self.type: Optional[HALFormsPropertyType] = type
        self.prompt: Optional[str] = prompt
        self.readOnly: Optional[bool] = readOnly
        self.regex: Optional[str] = regex
        self.required: Optional[bool] = required
        self.templated: Optional[bool] = templated
        self.value: Optional[str] = value
        self.cols: Optional[int] = cols
        self.max: Optional[int] = max
        self.maxLength: Optional[int] = maxLength
        self.min: Optional[int] = min
        self.minLength: Optional[int] = minLength
        self.options: Optional[HALFormsOptions] = options
        self.placeholder: Optional[str] = placeholder
        self.rows: Optional[int] = rows
        self.step: Optional[int] = step
    
    def serialize(self) -> Dict[str, Any]:
        result = HALFormsPropertySchema.serialize(self)
        
        # Special handling for options to ensure proper serialization
        if self.options:
            result["options"] = self.options.serialize()
            
        return result
    
    @classmethod
    def deserialize(self, data: Dict[str, Any]) -> 'HALFormsProperty':
        # Convert property type string to enum if present
        if 'type' in data and data['type'] is not None and data['type'] in [e.value for e in HALFormsPropertyType]:
            data['type'] = HALFormsPropertyType(data['type'])
        else:
            # If the type value is not supported by the document consumer, contains a value not understood by the consumer, and/or is missing, the
            # document consumer SHOULD assume the type attribute is set to the default value: "text" and render the display input as a simple text box.
            data['type'] = HALFormsPropertyType.text
        
        # Process options if present
        options_data = data.get('options')
        options = HALFormsOptions.deserialize(options_data) if options_data else None
            
        # Create property object
        prop = HALFormsProperty(
            name=data['name'],
            type=data.get('type', None),
            prompt=data.get('prompt', None),
            readOnly=data.get('readOnly', None),
            regex=data.get('regex', None),
            required=data.get('required', None),
            templated=data.get('templated', None),
            value=data.get('value', None),
            cols=data.get('cols', None),
            max=data.get('max', None),
            maxLength=data.get('maxLength', None),
            min=data.get('min', None),
            minLength=data.get('minLength', None),
            options=options,
            placeholder=data.get('placeholder', None),
            rows=data.get('rows', None),
            step=data.get('step', None),
        )
        return prop
    
class HALFormsTemplate(object):
    def __init__(self, method: HALFormsMethod, contentType: Optional[str] = "application/json", properties: List[HALFormsProperty]=[], target: Optional[str] = None, title: Optional[str] = None):
        self.method: HALFormsMethod = method
        self.contentType: Optional[str] = contentType
        self.properties: List[HALFormsProperty] = properties
        self.target: Optional[str] = target
        self.title: Optional[str] = title

    def serialize(self) -> Dict[str, Any]:
        result = HALFormsTemplateSchema.serialize(self)
            
        return result
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'HALFormsTemplate':
        """
        Convert a dictionary to a HALFormsTemplate object.
        
        Args:
            data: Dictionary containing template data
            
        Returns:
            A new HALFormsTemplate instance
        """
        # Extract required fields
        method = HALFormsMethod(data['method'])
        
        # Extract optional fields with defaults
        content_type = data.get('contentType', 'application/json')
        target = data.get('target')
        title = data.get('title')
        
        # Process properties
        properties = []
        for prop_data in data.get('properties', []):
            properties.append(HALFormsProperty.deserialize(prop_data))
        
        # Create and return template object
        return cls(
            method=method,
            contentType=content_type,
            properties=properties,
            target=target,
            title=title
        )

class HALFormsOptionsLinkSchema(halogen.Schema):
    href = halogen.Attr(required=True)
    templated = halogen.Attr(required=False, default=False)
    type = halogen.Attr(required=False, default="application/json")
    
    @classmethod
    def serialize(self, value, **kwargs):
        if value is None:
            return None
        return super().serialize(value, **kwargs)


class NullableEnum(halogen.types.Enum):
    def __init__(self, enum_type, use_values = False, *args, **kwargs):
        super().__init__(enum_type, use_values, *args, **kwargs)
        
    def serialize(self, value: Optional[enum.Enum], **kwargs) -> Optional[str]:
        if value is None:
            return None
        return value.value if self.use_values else value.name
    
class NullableList(halogen.types.List):
    def serialize(self, value, **kwargs):
        """Serialize every item of the list."""
        if value is None:
            return None
        return [self.item_type.serialize(val, **kwargs) for val in value]
    
class HALFormsOptionsSchema(halogen.Schema):
    inline = halogen.Attr(attr_type=NullableList(), required=False, exclude=[None])
    link = halogen.Attr(attr_type=HALFormsOptionsLinkSchema, required=False, exclude=[None], default=None)
    maxItems = halogen.Attr(required=False, exclude=[None])
    minItems = halogen.Attr(required=False, exclude=[None])
    promptField = halogen.Attr(required=False, default="prompt", exclude=[None, "prompt"])
    selectedValues = halogen.Attr(attr_type=NullableList(), required=False, exclude=[None])
    valueField = halogen.Attr(required=False, default="value", exclude=[None, "value"])
    
    @classmethod
    def serialize(self, value, **kwargs):
        if value is None:
            return None
        return super().serialize(value, **kwargs)

    
class HALFormsPropertySchema(halogen.Schema):
    name = halogen.Attr(exclude=[None],)
    type = halogen.Attr(exclude=[None], required=False, default=None, attr_type=NullableEnum(enum_type=HALFormsPropertyType))
    prompt = halogen.Attr(exclude=[None], required=False, default=None)
    readOnly = halogen.Attr(exclude=[None], required=False, default=None)
    regex = halogen.Attr(exclude=[None], required=False, default=None)
    required = halogen.Attr(exclude=[None], required=False, default=None)
    templated = halogen.Attr(exclude=[None], required=False, default=None)
    value = halogen.Attr(exclude=[None], required=False, default=None)
    cols = halogen.Attr(exclude=[None], required=False, default=None)
    max = halogen.Attr(exclude=[None], required=False, default=None)
    maxLength = halogen.Attr(exclude=[None], required=False, default=None)
    min = halogen.Attr(exclude=[None], required=False, default=None)
    minLength = halogen.Attr(exclude=[None], required=False, default=None)
    options = halogen.Attr(exclude=[None], required=False, default=None, attr_type=HALFormsOptionsSchema)
    placeholder = halogen.Attr(exclude=[None], required=False, default=None)
    rows = halogen.Attr(exclude=[None], required=False, default=None)
    step = halogen.Attr(exclude=[None], required=False, default=None)

class HALFormsTemplateSchema(halogen.Schema):
    method = halogen.Attr(required=True, attr_type=halogen.types.Enum(enum_type=HALFormsMethod))
    contentType = halogen.Attr(required=False, default=None)
    properties = halogen.Attr(attr_type=halogen.types.List(item_type=HALFormsPropertySchema))
    target = halogen.Attr(required=False, default=None, exclude=[None])
    title = halogen.Attr(required=False, exclude=[None])
    
class HalogenTemplate(halogen.Attr):
    def __init__(self, attr_type=HALFormsTemplateSchema, attr=None, required = True, exclude = None, **kwargs):
        super().__init__(attr_type, attr, required, exclude, **kwargs)
    
    @property
    def compartment(self):
        return "_templates"
    
    @property
    def key(self):
        # instead of basic_extract we want key basic-extract
        return self.name.replace("_","-")
    