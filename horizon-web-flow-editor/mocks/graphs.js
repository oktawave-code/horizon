module.exports = [
  {
    id: 1,
    name: 'Example configuration',
    createdAt: '2018-10-11',
    updatedAt: '2018-12-01',
    graph: [{
      'value': {
        'name': 'Aggregate',
        'description': 'Some descriptive description of this operation.',
        'iconUri': 'mocks/filter.png',
        'elementId': 'horizon.mocks.filter',
        'category': 'AGGREGATE',
        'requiredStreams': [
          {
            'staticPropertyId': 0,
            'runtimeType': 0,
            'required': false
          }
        ],
        'outputStrategy': {
          'type': 'keep',
          'keepBoth': false
        },
        'staticProperties': []
      },
      'id': '2',
      'geometry': {
        'x': 44,
        'y': 13,
        'width': 100,
        'height': 40
      }
    },
    {
      'value': {
        'name': 'Filter',
        'description': 'Some descriptive description of this operation.',
        'iconUri': 'mocks/filter.png',
        'elementId': 'horizon.mocks.filter',
        'category': 'FILTER',
        'requiredStreams': [
          {
            'staticPropertyId': 0,
            'runtimeType': 0,
            'required': false
          },
          {
            'staticPropertyId': 1,
            'runtimeType': 1,
            'required': false
          }
        ],
        'outputStrategy': {
          'type': 'keep',
          'keepBoth': false
        },
        'staticProperties': [
          {
            'value': 'aaa',
            'label': 'Input input',
            'description': 'Some long text input description',
            'internalName': 'textInput',
            'required': true,
            'predefined': false,
            'elementId': 'inputUniqueId',
            'staticPropertyType': 'text',
            'requiredDataType': 'String',
            'multiline': false,
            'htmlAllowed': false,
            'mapsTo': 'String'
          },
          {
            'value': '',
            'label': 'Textarea input',
            'description': 'Some long textarea description',
            'internalName': 'textareaInput',
            'required': false,
            'predefined': false,
            'elementId': 'textareaUniqueId',
            'staticPropertyType': 'text',
            'requiredDataType': 'String',
            'multiline': true,
            'htmlAllowed': false,
            'mapsTo': 'String'
          },
          {
            'value': 1,
            'label': 'Integer input',
            'description': 'Some long integer input description',
            'internalName': 'integerInput',
            'required': true,
            'predefined': false,
            'elementId': 'integerNumberUniqueId',
            'staticPropertyType': 'integer',
            'requiredDataType': 'Integer',
            'multiline': false,
            'htmlAllowed': false,
            'minValue': 1,
            'maxValue': 10,
            'step': 1,
            'mapsTo': 'Integer'
          },
          {
            'value': -5,
            'label': 'Double input',
            'description': 'Some long double input description',
            'internalName': 'doubleInput',
            'required': true,
            'predefined': false,
            'elementId': 'doubleNumberUniqueId',
            'staticPropertyType': 'float',
            'requiredDataType': 'Double',
            'multiline': false,
            'htmlAllowed': false,
            'minValue': -5,
            'maxValue': 5,
            'step': 0.5,
            'mapsTo': 'Float'
          },
          {
            'value': 'option2',
            'label': 'Select input',
            'description': 'Some long select input description',
            'internalName': 'selectInput',
            'required': true,
            'predefined': false,
            'elementId': 'selectUniqueId',
            'staticPropertyType': 'singleValueSelection',
            'options': [
              {
                'name': 'Option 1',
                'selected': false,
                'internalName': 'option1'
              },
              {
                'name': 'Option 2',
                'selected': true,
                'internalName': 'option2'
              },
              {
                'name': 'Option 3',
                'selected': false,
                'internalName': 'option3'
              }
            ]
          },
          {
            'value': [
              'checkbox2',
              'checkbox3'
            ],
            'label': 'Checkbox input',
            'description': 'Some long checkbox input description',
            'internalName': 'checkboxInput',
            'required': true,
            'predefined': false,
            'elementId': 'checkboxUniqueId',
            'staticPropertyType': 'multiValueSelection',
            'options': [
              {
                'name': 'Checkbox 1',
                'selected': false,
                'internalName': 'checkbox1'
              },
              {
                'name': 'Checkbox 2',
                'selected': true,
                'internalName': 'checkbox2'
              },
              {
                'name': 'Checkbox 3',
                'selected': true,
                'internalName': 'checkbox3'
              }
            ]
          }
        ]
      },
      'id': '3',
      'geometry': {
        'x': 69,
        'y': 147,
        'width': 100,
        'height': 40
      }
    },
    {
      'value': {
        'name': 'Filter',
        'description': 'Some descriptive description of this operation.',
        'iconUri': 'mocks/filter.png',
        'elementId': 'horizon.mocks.filter',
        'category': 'FILTER',
        'requiredStreams': [
          {
            'staticPropertyId': 0,
            'runtimeType': 0,
            'required': false
          },
          {
            'staticPropertyId': 1,
            'runtimeType': 1,
            'required': false
          }
        ],
        'outputStrategy': {
          'type': 'keep',
          'keepBoth': false
        },
        'staticProperties': [
          {
            'value': 'test',
            'label': 'Input input',
            'description': 'Some long text input description',
            'internalName': 'textInput',
            'required': true,
            'predefined': false,
            'elementId': 'inputUniqueId',
            'staticPropertyType': 'text',
            'requiredDataType': 'String',
            'multiline': false,
            'htmlAllowed': false,
            'mapsTo': 'String'
          },
          {
            'value': '',
            'label': 'Textarea input',
            'description': 'Some long textarea description',
            'internalName': 'textareaInput',
            'required': false,
            'predefined': false,
            'elementId': 'textareaUniqueId',
            'staticPropertyType': 'text',
            'requiredDataType': 'String',
            'multiline': true,
            'htmlAllowed': false,
            'mapsTo': 'String'
          },
          {
            'value': 1,
            'label': 'Integer input',
            'description': 'Some long integer input description',
            'internalName': 'integerInput',
            'required': true,
            'predefined': false,
            'elementId': 'integerNumberUniqueId',
            'staticPropertyType': 'integer',
            'requiredDataType': 'Integer',
            'multiline': false,
            'htmlAllowed': false,
            'minValue': 1,
            'maxValue': 10,
            'step': 1,
            'mapsTo': 'Integer'
          },
          {
            'value': -5,
            'label': 'Double input',
            'description': 'Some long double input description',
            'internalName': 'doubleInput',
            'required': true,
            'predefined': false,
            'elementId': 'doubleNumberUniqueId',
            'staticPropertyType': 'float',
            'requiredDataType': 'Double',
            'multiline': false,
            'htmlAllowed': false,
            'minValue': -5,
            'maxValue': 5,
            'step': 0.5,
            'mapsTo': 'Float'
          },
          {
            'value': 'option2',
            'label': 'Select input',
            'description': 'Some long select input description',
            'internalName': 'selectInput',
            'required': true,
            'predefined': false,
            'elementId': 'selectUniqueId',
            'staticPropertyType': 'singleValueSelection',
            'options': [
              {
                'name': 'Option 1',
                'selected': false,
                'internalName': 'option1'
              },
              {
                'name': 'Option 2',
                'selected': true,
                'internalName': 'option2'
              },
              {
                'name': 'Option 3',
                'selected': false,
                'internalName': 'option3'
              }
            ]
          },
          {
            'value': [
              'checkbox2',
              'checkbox3'
            ],
            'label': 'Checkbox input',
            'description': 'Some long checkbox input description',
            'internalName': 'checkboxInput',
            'required': true,
            'predefined': false,
            'elementId': 'checkboxUniqueId',
            'staticPropertyType': 'multiValueSelection',
            'options': [
              {
                'name': 'Checkbox 1',
                'selected': false,
                'internalName': 'checkbox1'
              },
              {
                'name': 'Checkbox 2',
                'selected': true,
                'internalName': 'checkbox2'
              },
              {
                'name': 'Checkbox 3',
                'selected': true,
                'internalName': 'checkbox3'
              }
            ]
          }
        ]
      },
      'id': '4',
      'geometry': {
        'x': 210,
        'y': 33,
        'width': 100,
        'height': 40
      }
    },
    {
      'value': {
        'name': 'Aggregate',
        'description': 'Some descriptive description of this operation.',
        'iconUri': 'mocks/filter.png',
        'elementId': 'horizon.mocks.filter',
        'category': 'AGGREGATE',
        'requiredStreams': [
          {
            'staticPropertyId': 0,
            'runtimeType': 0,
            'required': false
          }
        ],
        'outputStrategy': {
          'type': 'keep',
          'keepBoth': false
        },
        'staticProperties': []
      },
      'id': '5',
      'geometry': {
        'x': 287,
        'y': 196,
        'width': 100,
        'height': 40
      }
    },
    {
      'value': '',
      'edge': true,
      'source': '2',
      'target': '4'
    },
    {
      'value': '',
      'edge': true,
      'source': '3',
      'target': '4'
    },
    {
      'value': '',
      'edge': true,
      'source': '4',
      'target': '5'
    }
    ]
  }
]
