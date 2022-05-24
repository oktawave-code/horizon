export function flattenValidationErrors (validationDataStructure) {
  const flattenedErrors = {}

  function flattenErrors (errors, out, prefix) {
    errors.forEach(err => {
      out[prefix + '-' + err.property] = Object.values(
        err.constraints || {}
      )
      flattenErrors(err.children, out, prefix + '-' + err.property)
    })
  }
  flattenErrors(validationDataStructure || [], flattenedErrors, 'error')
  return flattenedErrors
}
