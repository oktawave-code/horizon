export class StaticPropertyBase {
  constructor (model) {
    Object.assign(this, model)
  }

  getLabel () {
    return this.label
  }

  getDescription () {
    return this.description
  }

  getFieldName () {
    return this.internalName
  }

  isRequired () {
    return this.required
  }

  getId () {
    return this.elementId
  }

  getValue () {
    return this.value
  }

  setValue (value) {
    this.value = value
  }
}

export class TextStaticProperty extends StaticPropertyBase {
  constructor (model) {
    super(model)
    // set initial value from definition
    if (!this.getValue()) {
      this.setValue('')
    }
  }

  isMultiline () {
    return this.multiline
  }

  isHtmlAllowed () {
    return this.isHtmlAllowed
  }
}

export class NumberStaticProperty extends StaticPropertyBase {
  constructor (model) {
    super(model)
    // set initial value from definition
    if (!this.getValue()) {
      this.setValue(this.getMinValue())
    }
  }

  getMinValue () {
    return this.minValue
  }

  getMaxValue () {
    return this.maxValue
  }

  getStep () {
    return this.step
  }
}

export class ListStaticProperty extends StaticPropertyBase {
  constructor (model) {
    super(model)
    // set initial value from definition
    if (!this.getValue()) {
      this.setValue((this.getOptions().find(val => val.selected) || {}).internalName)
    }
  }

  getOptions () {
    return this.options
  }
}

export class CheckboxStaticProperty extends StaticPropertyBase {
  constructor (model) {
    super(model)
    // set initial value from definition
    if (!this.getValue()) {
      this.setValue((this.getOptions() || [])
        .filter(option => option.selected)
        .map(option => option.internalName))
    }
  }

  getOptions () {
    return this.options
  }
}

export function buildStaticProperty (model) {
  switch (model.staticPropertyType) {
    case 'text': return new TextStaticProperty(model)
    case 'integer':
    case 'float':
      return new NumberStaticProperty(model)
    case 'singleValueSelection': return new ListStaticProperty(model)
    case 'multiValueSelection': return new CheckboxStaticProperty(model)
    default: throw new Error('Unknown static property type')
  }
}
