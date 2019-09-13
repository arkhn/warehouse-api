from .resource import Resource
from models import resources

resource_list = ['Patient', 'Encounter', 'Practitioner',
                 'Organization', 'Observation', 'Subscription',
                 'Procedure']
resources_models = {}
for r in resource_list:
    if r in dir(resources):
        resources_models[r] = getattr(resources, r)
    else:
        resources_models[r] = type(r, (Resource,), {})
