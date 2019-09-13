from .resource import Resource

resources = {
    _type: type(_type, (Resource,), {}) for _type in
    ['Patient']
}
