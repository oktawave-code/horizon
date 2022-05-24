import kubernetes

class ResourceMetrics(object):
    """
    Simple patch for missing metrics.k8s.io python api
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = kubernetes.client.ApiClient()
        self.api_client = api_client

    def getAllNodeMetrics(self):
        (data) = self.api_client.call_api('/apis/metrics.k8s.io/v1beta1/nodes',
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
        return data

    def getAllPodMetrics(self):
        (data) = self.api_client.call_api('/apis/metrics.k8s.io/v1beta1/pods',
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
        return data

    def getNamespacePodMetrics(self, namespace):
        (data) = self.api_client.call_api('/apis/metrics.k8s.io/v1beta1/namespaces/{namespace}/pods',
                'GET',
                {'namespace':namespace}, # path_params
                [], # query_params
                {}, # header_params
                body=None,
                post_params=[],
                files={},
                response_type='object',
                auth_settings=['BearerToken'],
                async_req=False,
                _return_http_data_only=True)
        return data

class CustomMetrics(object):
    """
    Simple patch for missing custom.metrics.k8s.io python api
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = kubernetes.client.ApiClient()
        self.api_client = api_client

    def getNamespacePodMetrics(self, namespace, metric):
        (data) = self.api_client.call_api('/apis/custom.metrics.k8s.io/v1beta1/namespaces/{namespace}/pods/*/{metric}',
                'GET',
                {
                    'namespace': namespace,
                    'metric': metric,
                }, # path_params
                [], # query_params
                {}, # header_params
                body=None,
                post_params=[],
                files={},
                response_type='object',
                auth_settings=['BearerToken'],
                async_req=False,
                _return_http_data_only=True)
        return data

    def getNamespacedRawMetrics(self, namespace, path):
        (data) = self.api_client.call_api('/apis/custom.metrics.k8s.io/v1beta1/namespaces/{namespace}/'+path,
                'GET',
                {
                    'namespace': namespace,
                }, # path_params
                [], # query_params
                {}, # header_params
                body=None,
                post_params=[],
                files={},
                response_type='object',
                auth_settings=['BearerToken'],
                async_req=False,
                _return_http_data_only=True)
        return data

    def getRawMetrics(self, path):
        (data) = self.api_client.call_api('/apis/custom.metrics.k8s.io/v1beta1/'+path,
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
        return data
