import kubernetes

class ResourceScanner(object):

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = kubernetes.client.ApiClient()
        self.api_client = api_client

    def getAllAPIs(self, preferredOnly=False):
        result = ['api/v1'] # "api/v1" is a special case
        try:
            (data) = self.api_client.call_api('/apis',
                'GET',
                {}, # path_params
                [], # query_params
                {}, # header_params
                body=None,
                post_params=[],
                files={},
                response_type='object',
                auth_settings=['BearerToken'],
                async_req=False,
                _return_http_data_only=True)
        except kubernetes.client.rest.ApiException as e:
            if e.status!=404:
                raise
            return result
        for api in data['groups']:
            if preferredOnly:
                result.append('apis/'+api['preferredVersion']['groupVersion'])
            else:
                for version in api['versions']:
                    result.append('apis/'+version['groupVersion'])
        return result

    def getAllAPIKinds(self, api, namespaced=None, onlyTopLevel=False, onlyGettable=True, excludedKinds=None):
        result = []
        try:
            (data) = self.api_client.call_api('/{api}',
                'GET',
                {'api':api}, # path_params
                [], # query_params
                {}, # header_params
                body=None,
                post_params=[],
                files={},
                response_type='object',
                auth_settings=['BearerToken'],
                async_req=False,
                _return_http_data_only=True)
        except kubernetes.client.rest.ApiException as e:
            if e.status!=404:
                raise
            return result
        for resGroup in data['resources']:
            if (excludedKinds is None) or (resGroup['kind'] not in excludedKinds):
                if (namespaced is None) or (resGroup['namespaced']==namespaced):
                    if (not onlyTopLevel) or ('/' not in resGroup['name']):
                        if (not onlyGettable) or ('get' in resGroup['verbs']):
                            result.append((resGroup['kind'], resGroup['name']))
        return result

    def getAllResources(self, api, kind, queryParams=None):
        if queryParams is None:
            queryParams = []
        try:
            (data) = self.api_client.call_api('/{api}/{kind}',
                'GET',
                {
                    'api': api,
                    'kind': kind,
                },
                queryParams,
                {}, # header_params
                body=None,
                post_params=[],
                files={},
                response_type='object',
                auth_settings=['BearerToken'],
                async_req=False,
                _return_http_data_only=True)
        except kubernetes.client.rest.ApiException as e:
            if e.status!=404:
                raise
            return []
        return data['items']

