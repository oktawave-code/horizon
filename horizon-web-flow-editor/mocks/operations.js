module.exports = [
  {
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
      // text input
      {
        label: 'Input input',
        description: 'Some long text input description',
        internalName: 'textInput',
        required: true,
        predefined: false,
        elementId: 'inputUniqueId',
        staticPropertyType: 'text',
        requiredDataType: 'String',
        multiline: false,
        htmlAllowed: false,
        mapsTo: 'String'
      },
      // textarea
      {
        label: 'Textarea input',
        description: 'Some long textarea description',
        internalName: 'textareaInput',
        required: false,
        predefined: false,
        elementId: 'textareaUniqueId',
        staticPropertyType: 'text',
        requiredDataType: 'String',
        multiline: true,
        htmlAllowed: false,
        mapsTo: 'String'
      },
      // integer input
      {
        label: 'Integer input',
        description: 'Some long integer input description',
        internalName: 'integerInput',
        required: true,
        predefined: false,
        elementId: 'integerNumberUniqueId',
        staticPropertyType: 'integer',
        requiredDataType: 'Integer',
        multiline: false,
        htmlAllowed: false,
        minValue: 1,
        maxValue: 10,
        step: 1,
        mapsTo: 'Integer'
      },
      // double input
      {
        label: 'Double input',
        description: 'Some long double input description',
        internalName: 'doubleInput',
        required: true,
        predefined: false,
        elementId: 'doubleNumberUniqueId',
        staticPropertyType: 'float',
        requiredDataType: 'Double',
        multiline: false,
        htmlAllowed: false,
        minValue: -5.0,
        maxValue: 5.0,
        step: 0.5,
        mapsTo: 'Float'
      },
      // select input
      {
        label: 'Select input',
        description: 'Some long select input description',
        internalName: 'selectInput',
        required: true,
        predefined: false,
        elementId: 'selectUniqueId',
        staticPropertyType: 'singleValueSelection',
        options: [
          {
            name: 'Option 1',
            selected: false,
            internalName: 'option1'
          },
          {
            name: 'Option 2',
            selected: true,
            internalName: 'option2'
          },
          {
            name: 'Option 3',
            selected: false,
            internalName: 'option3'
          }
        ]
      },
      // checkbox input
      {
        label: 'Checkbox input',
        description: 'Some long checkbox input description',
        internalName: 'checkboxInput',
        required: true,
        predefined: false,
        elementId: 'checkboxUniqueId',
        staticPropertyType: 'multiValueSelection',
        options: [
          {
            name: 'Checkbox 1',
            selected: false,
            internalName: 'checkbox1'
          },
          {
            name: 'Checkbox 2',
            selected: true,
            internalName: 'checkbox2'
          },
          {
            name: 'Checkbox 3',
            selected: true,
            internalName: 'checkbox3'
          }
        ]
      }
    ]
  },
  {
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
  }
]
