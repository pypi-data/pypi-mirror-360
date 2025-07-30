from django.urls import path
from . import views
from .views import chatbot_conversar, chatbot_config, chatbot_status

urlpatterns = [
	# ...
	path("teste-login-sso/", views.teste_login_sso, name="teste_login_sso"),
	path("login-sso/", views.login_sso, name="login_sso"),
	path("pt/elasticsearch/callback/", views.callback_sso, name="callback_sso"),
	path("logout/", views.logout_view, name="logout"),
    path('salvar-contato/', views.salvar_contato, name='salvar_contato'),
    path('salvar-resposta-formulario/', views.salvar_resposta_formulario, name='salvar_resposta_formulario'),
    path('exportar-respostas/', views.exportar_respostas_csv, name='exportar_respostas_csv'),
    
	path('chatbot/api/conversar/', chatbot_conversar, name='chatbot_conversar'),
    path('chatbot/api/config/', chatbot_config, name='chatbot_config'),
    path('chatbot/api/status/', chatbot_status, name='chatbot_status'),
]
