CHECKBOX = {
    "type": "object",
    "properties": {
        "type": {
            "description": "The type must be 'checkbox'.",
            "type": "string",
            "pattern": "checkbox",
        },
        "is_mandatory": {
            "description": "This field indicates whether this text fragment is mandatory.",
            "type": "boolean",
        },
        "properties": {
            "description": "The checkbox has the following properties.",
            "type": "object",
            "properties": {
                "text": {
                    "description": ("This property contains the displayed text of the "
                                    "checkbox."),
                    "type": "string",
                },
                "required": {
                    "description": ("This property indicates whether checking the checkbox "
                                    "is mandatory."),
                    "type": "boolean",
                },
            },
            "required": ["text", "required"],
        },
    },
    "required": ["properties", "type"],
}


MARKDOWN = {
    "type": "object",
    "properties": {
        "type": {
            "description": "The type must be 'markdown'",
            "type": "string",
            "pattern": "markdown",
        },
        "properties": {
            "description": "The markdown text has the following properties.",
            "type": "object",
            "properties": {
                "text": {
                    "description": ("This property contains the displayed text as "
                                    "markdown text"),
                    "type": "string",
                },
            },
            "required": ["text"],
        },
    },
    "required": ["properties", "type"],
}


PAGE_BREAK = {
    "type": "object",
    "properties": {
        "type": {
            "description": "Should force the renderer to add a page break",
            "type": "string",
            "pattern": "page-break",
        },
        "properties": {
            "description": "This node has no properties.",
            "type": "object",
            "properties": {},
        },
    },
    "required": ["type"],
}


TEXT_FRAGMENTS_SCHEMA = {
    "$defs": {
        "checkbox": CHECKBOX,
        "markdown": MARKDOWN,
        "page-break": PAGE_BREAK,
    },

    "type": "array",
    "items": {
        "anyOf": [
            {"$ref": "#/$defs/checkbox"},
            {"$ref": "#/$defs/markdown"},
            {"$ref": "#/$defs/page-break"},
        ],
    },
    "minItems": 1,
}
