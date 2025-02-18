import json
import os
import openai
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from dotenv import load_dotenv


load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


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
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": message}
                ]
            )
            response_text = response.choices[0].message.content.strip()
            return response_text
        except Exception as e:
            return f"Error calling OpenAI API: {str(e)}"
