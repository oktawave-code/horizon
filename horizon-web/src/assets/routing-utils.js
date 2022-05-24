export class CollectorRule {
  constructor ({ source, filter, topic, final }) {
    this.source = source
    this.filter = filter
    this.topic = topic
    this.final = final || false
    this.isSourceDisabled = false
    this.isFilterDiabled = false
  }

  getData () {
    return {
      source: this.source,
      filter: this.filter,
      topic: this.topic,
      final: this.final
    }
  }

  getSourceName () {
    if (this.source === 'url') {
      return 'url'
    }
    if (!this.source) {
      return 'any'
    }
    return 'header'
  }
}

export class UrlRule extends CollectorRule {
  constructor (rule = {}) {
    super(rule)
    this.source = 'url'
    this.isSourceDisabled = true
  }
}

export class HeaderRule extends CollectorRule {
  constructor (rule = {}) {
    super(rule)
  }
}

export class AnyRule extends CollectorRule {
  constructor (rule = {}) {
    super(rule)
    this.isSourceDisabled = true
    this.isFilterDisabled = true
  }
}

export class MetadataRule {
  constructor ({ source, meta }) {
    this.source = source
    this.meta = meta
    this.isSourceDisabled = false
  }

  getData () {
    return {
      source: this.source,
      meta: this.meta
    }
  }

  getSourceName () {
    if (this.source === 'url') {
      return 'url'
    }
    return 'header'
  }
}

export class UrlMetadataRule extends MetadataRule {
  constructor (rule = {}) {
    super(rule)
    this.source = 'url'
    this.isSourceDisabled = true
  }
}

export class HeaderMetadataRule extends MetadataRule {
  constructor (rule = {}) {
    super(rule)
  }
}

export function mapRoutingRuleToObject (rule) {
  if (rule.source === 'url') {
    return new UrlRule(rule)
  }
  if (!rule.source) {
    return new AnyRule(rule)
  }
  return new HeaderRule(rule)
}

export function mapMetaRuleToObject (rule) {
  if (rule.source === 'url') {
    return new UrlMetadataRule(rule)
  }
  return new HeaderMetadataRule(rule)
}
