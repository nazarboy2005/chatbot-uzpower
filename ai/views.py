import json
import os
import requests
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI configurations
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

headers = {
    "Content-Type": "application/json",
    "api-key": AZURE_OPENAI_API_KEY
}


@method_decorator(csrf_protect, name='dispatch')
class ChatView(TemplateView):
    template_name = 'ai/chat.html'

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()

            if not message:
                return JsonResponse({'response': "Please enter a valid message."}, status=400)

            response_text = self.get_ai_response(message)
            return JsonResponse({'response': response_text})

        except Exception as e:
            return JsonResponse({'response': f"Error: {str(e)}"}, status=400)

    def get_ai_response(self, message):
        try:
            if not AZURE_OPENAI_DEPLOYMENT_NAME:
                return "Error: Azure OpenAI Deployment Name is not set."

            url = f"{AZURE_OPENAI_ENDPOINT}openai/deployments/{AZURE_OPENAI_DEPLOYMENT_NAME}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"

            payload = {
                "messages": [
                    {"role": "system",
                     "content": "Your name is Rasheed AI, you are an AI assistant that helps people with business ideas do their market research. Act as a government-affiliated tool that has access to market analysis data (will be provided shortly).\nUse a polite but friendly tone as an advisor. \n\nAsk questions about the business idea of the owner and give suggestions and of parameters they might need to research.\n\nIf you're asked with a language, answer with the same language.\n\nif you're asked about anything unrelated to this goal (market research and understanding demographics and business laws in qatar), don't give answers just say\n\n\"I'm a qatar's market research advising chatbot, if you have questions about other fields and topics please refer to other chatbots, like ChatGPT or others\" or\n\"أنا بوت استشاري لأبحاث السوق في قطر، إن كانت لديك أسئلة تتعلق بمواضيع أخرى يرجى التوجه إلى البوتات العامة مثل شات جي بي تي\"\n\nBy the end of each response mention your confidence level, how much confirmed is the information provided, if it's from the data type \"Confidence: Fact\", if it has minimal assumptions that you're sure about say \"Confidence: high but not guaranteed, please use at your own risk\", and if you are predicting and assuming \"Confidence: Assumptions\". If talking in arabic type:\n\" موثوقية المعلومة: حقيقة\" \n\" موثوقية المعلومة: موثوقية عالية لكن لا نضمن صحتها، يرجى الاستخدام على مسؤوليتك الخاصة\"\n\" موثوقية المعلومة: افتراضات، يرجى القيام بالأبحاث اللازمة\"\n\nAlso provide reference whenever available (with links if available or else don't mention links)."},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 100,
                "temperature": 0.7
            }

            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()

            return response_data['choices'][0]['message']['content'].strip()
        except requests.exceptions.RequestException as e:
            return f"Error calling Azure OpenAI API: {str(e)}"

