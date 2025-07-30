import os


def build_llm(model):
    provider, model_name = model.split(':', 1)
    provider = provider.strip().lower()
    model_name = model_name.strip()

    if provider in ['deepseek', 'baichuan', 'doubao', 'moonshot', 'openai', 'xai', 'aliyun', 'open-source']:
        from docapi.llm.openai_llm import OpenAILLM

        if provider == 'deepseek':
            api_key = os.getenv('DEEPSEEK_API_KEY')
            base_url = 'https://api.deepseek.com'
        elif provider == 'baichuan':
            api_key = os.getenv('BAICHUAN_API_KEY')
            base_url = 'https://api.baichuan-ai.com/v1'
        elif provider == 'doubao':
            api_key = os.getenv('DOUBAO_API_KEY')
            base_url = 'https://ark.cn-beijing.volces.com/api/v3'
        elif provider == 'moonshot':
            api_key = os.getenv('MOONSHOT_API_KEY')
            base_url = 'https://api.moonshot.cn/v1'
        elif provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            base_url = None
        elif provider == 'aliyun':
            api_key = os.getenv('DASHSCOPE_API_KEY')
            base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
        elif provider == 'xai':
            api_key = os.getenv('XAI_API_KEY')
            base_url = 'https://api.x.ai/v1'
        else:
            api_key = os.getenv('OPENAI_API_KEY', 'default')
            base_url = os.getenv('OPENAI_API_BASE')

        if not api_key:
            raise ValueError(f'No API key found for {provider}')

        return OpenAILLM(api_key=api_key, base_url=base_url, model=model_name)

    elif provider == 'azure-openai':
        from docapi.llm.azure_openai_llm import AzureOpenAILLM

        api_key = os.getenv('AZURE_OPENAI_API_KEY')
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        api_version = os.getenv('OPENAI_API_VERSION')
        return AzureOpenAILLM(api_key=api_key, endpoint=endpoint, api_version=api_version, model=model_name)

    elif provider == 'baidu':
        from docapi.llm.baidu_llm import BaiduLLM

        access_key = os.getenv('QIANFAN_ACCESS_KEY')
        secret_key = os.getenv('QIANFAN_SECRET_KEY')
        return BaiduLLM(access_key=access_key, secret_key=secret_key, model=model_name)

    elif provider == 'zhipu':
        from docapi.llm.zhipu_llm import ZhipuLLM

        api_key = os.getenv('ZHIPUAI_API_KEY')
        return ZhipuLLM(api_key=api_key, model=model_name)

    else:
        raise ValueError('No LLM provider found')
