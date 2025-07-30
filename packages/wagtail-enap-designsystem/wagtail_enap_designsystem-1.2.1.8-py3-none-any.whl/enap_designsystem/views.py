import uuid
import requests
import time
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest
from .utils.decorators import aluno_login_required
from .utils.sso import get_valid_access_token
from wagtail.models import Page
from django.shortcuts import redirect
from django.contrib import messages
from .models import Contato
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse 
from django.core.mail import send_mail
from .models import Contato, FormularioSnippet, RespostaFormulario
from django.shortcuts import redirect, get_object_or_404, render
import csv
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import uuid

from .services.chatbot_service import ChatbotService
from .models import ChatbotConfig, ChatbotWidget




def teste_login_sso(request):
	return render(request, "teste_login_sso.html")

def login_sso(request):
	redirect_uri = request.build_absolute_uri(settings.SSO_REDIRECT_PATH)

	# Gera state único para segurança (proteção CSRF)
	state = str(uuid.uuid4())

	# print("Redirect URI gerado:", redirect_uri)
	# Monta query com todos os parâmetros
	query = {
		"client_id": settings.SSO_CLIENT_ID,
		"redirect_uri": redirect_uri,
		"response_type": "code",
		"scope": "openid",
		"state": state,
	}

	# Monta URL final do SSO
	sso_login_url = f"{settings.SSO_AUTH_URL}?{'&'.join(f'{k}={v}' for k, v in query.items())}"
	return redirect(sso_login_url)

def callback_sso(request):
	code = request.GET.get("code")
	if not code:
		return HttpResponseBadRequest("Código de autorização ausente.")

	# 🛑 IMPORTANTE: esta URL precisa ser exatamente igual à registrada no Keycloak
	redirect_uri = request.build_absolute_uri(settings.SSO_REDIRECT_PATH)

	data = {
		"grant_type": "authorization_code",
		"code": code,
		"redirect_uri": redirect_uri,
		"client_id": settings.SSO_CLIENT_ID,
		"client_secret": settings.SSO_CLIENT_SECRET,
	}
	headers = {
		"Content-Type": "application/x-www-form-urlencoded"
	}

	# ⚠️ Desativa verificação SSL apenas em DEV
	verify_ssl = not settings.DEBUG

	# 🔐 Solicita o token
	print("📥 Enviando para /token:", data)
	token_response = requests.post(
		settings.SSO_TOKEN_URL,
		data=data,
		headers=headers,
		verify=verify_ssl
	)
	print("🧾 TOKEN RESPONSE:", token_response.status_code, token_response.text)

	if token_response.status_code != 200:
		return HttpResponse("Erro ao obter token", status=token_response.status_code)

	access_token = token_response.json().get("access_token")
	if not access_token:
		return HttpResponse("Token de acesso não recebido.", status=400)

	# 🔍 Pega dados do usuário
	userinfo_headers = {
		"Authorization": f"Bearer {access_token}"
	}
	user_info_response = requests.get(
		settings.SSO_USERINFO_URL,
		headers=userinfo_headers,
		verify=verify_ssl
	)

	if user_info_response.status_code != 200:
		return HttpResponse("Erro ao obter informações do usuário.", status=400)

	user_info = user_info_response.json()
	email = user_info.get("email")
	nome = user_info.get("name")
	cpf = user_info.get("cpf")
	print("user_info", user_info)
	if not email or not nome:
		return HttpResponse("Informações essenciais ausentes no SSO.", status=400)

	# 🧠 Armazena na sessão para uso em /area-do-aluno
	request.session["aluno_sso"] = {
		"email": email,
		"nome": nome,
		"cpf": cpf,
		"access_token": access_token,
		"refresh_token": token_response.json().get("refresh_token"),
		"access_token_expires_at": int(time.time()) + token_response.json().get("expires_in", 300),
	}

	return redirect(get_area_do_aluno_url())

def logout_view(request):
	request.session.flush()
	return render(request, "logout_intermediario.html")

def get_area_do_aluno_url():
	try:
		page = Page.objects.get(slug="area-do-aluno").specific
		return page.url
	except Page.DoesNotExist:
		return "/"
	
@aluno_login_required
def area_do_aluno(request):
	token = get_valid_access_token(request.session)
	if not token:
		return redirect("/")

	# Exemplo: usar o token para chamar API externa
	response = requests.get("https://api.enap.gov.br/aluno", headers={
		"Authorization": f"Bearer {token}"
	})
	aluno_dados = response.json()

	return render(request, "area_do_aluno.html", {
		"aluno": request.session["aluno_sso"],
		"dados": aluno_dados,
	})






def salvar_contato(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        mensagem = request.POST.get('mensagem')
        
        # Salva no banco
        Contato.objects.create(
            nome=nome,
            email=email,
            mensagem=mensagem
        )
        
        messages.success(request, 'Mensagem enviada com sucesso!')
        return redirect(request.META.get('HTTP_REFERER', '/'))
	



def salvar_resposta_formulario(request):
    """Salva resposta do formulário snippet"""
    if request.method == 'POST':
        try:
            formulario_id = request.POST.get('formulario_id')
            nome = request.POST.get('nome', '').strip()
            email = request.POST.get('email', '').strip()
            telefone = request.POST.get('telefone', '').strip()
            assunto = request.POST.get('assunto', '').strip()
            mensagem = request.POST.get('mensagem', '').strip()
            
            # Validação básica
            if not formulario_id or not nome or not email or not assunto or not mensagem:
                return JsonResponse({
                    'success': False,
                    'message': 'Por favor, preencha todos os campos obrigatórios.'
                })
            
            # Busca o formulário
            formulario = get_object_or_404(FormularioSnippet, id=formulario_id, ativo=True)
            
            # Função para pegar IP
            def get_client_ip(request):
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')
                return ip
            
            # Salva no banco
            resposta = RespostaFormulario.objects.create(
                formulario=formulario,
                nome=nome,
                email=email,
                telefone=telefone,
                assunto=assunto,
                mensagem=mensagem,
                ip_address=get_client_ip(request)
            )
            
            # Envia email (opcional - pode comentar se não quiser)
            try:
                send_mail(
                    subject=f"[{formulario.nome}] {assunto}",
                    message=f"""
Nova mensagem recebida através do formulário "{formulario.nome}":

Nome: {nome}
Email: {email}
Telefone: {telefone}
Assunto: {assunto}

Mensagem:
{mensagem}

---
Enviado em: {resposta.data.strftime('%d/%m/%Y às %H:%M')}
IP: {resposta.ip_address}
                    """,
                    from_email='noreply@enap.gov.br',  # Ajuste conforme necessário
                    recipient_list=[formulario.email_destino],
                    fail_silently=True,
                )
            except Exception as email_error:
                print(f"Erro ao enviar email: {email_error}")
                # Não quebra o formulário se der erro no email
                pass
            
            return JsonResponse({
                'success': True,
                'message': 'Mensagem enviada com sucesso! Entraremos em contato em breve.'
            })
            
        except FormularioSnippet.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Formulário não encontrado ou inativo.'
            })
        except Exception as e:
            print(f"Erro ao salvar formulário: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Erro interno. Tente novamente.'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido.'
    })







@staff_member_required
def exportar_respostas_csv(request):
    """View para exportar respostas em CSV"""
    
    # Pega filtro de formulário se houver
    formulario_id = request.GET.get('formulario')
    
    if formulario_id:
        respostas = RespostaFormulario.objects.filter(formulario_id=formulario_id)
        filename = f"respostas_formulario_{formulario_id}_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
    else:
        respostas = RespostaFormulario.objects.all()
        filename = f"todas_respostas_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
    
    # Cria resposta CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # BOM para UTF-8
    response.write('\ufeff')
    writer = csv.writer(response)
    
    # Cabeçalho
    writer.writerow([
        'Formulário',
        'Nome', 
        'Email',
        'Telefone',
        'Assunto',
        'Mensagem',
        'Data/Hora',
        'IP'
    ])
    
    # Dados
    for resposta in respostas:
        writer.writerow([
            resposta.formulario.nome,
            resposta.nome,
            resposta.email,
            resposta.telefone,
            resposta.assunto,
            resposta.mensagem,
            resposta.data.strftime('%d/%m/%Y %H:%M'),
            resposta.ip_address or ''
        ])
    
    return response





@staff_member_required
def exportar_respostas_csv(request):
    """View para exportar respostas em CSV com filtro de formulário"""
    
    # Se é GET, mostra página de escolha
    if request.method == 'GET' and not request.GET.get('formulario'):
        formularios = FormularioSnippet.objects.filter(ativo=True)
        context = {
            'formularios': formularios,
            'total_respostas': RespostaFormulario.objects.count()
        }
        return render(request, 'admin/exportar_respostas.html', context)
    
    # Se tem filtro ou é POST, exporta
    formulario_id = request.GET.get('formulario') or request.POST.get('formulario')
    
    if formulario_id:
        formulario = FormularioSnippet.objects.get(id=formulario_id)
        respostas = RespostaFormulario.objects.filter(formulario_id=formulario_id)
        filename = f"respostas_{formulario.nome.replace(' ', '_')}_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
    else:
        respostas = RespostaFormulario.objects.all()
        filename = f"todas_respostas_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
    
    # Cria resposta CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # BOM para UTF-8
    response.write('\ufeff')
    writer = csv.writer(response)
    
    # Cabeçalho
    writer.writerow([
        'Formulário',
        'Nome', 
        'Email',
        'Telefone',
        'Assunto',
        'Mensagem',
        'Data/Hora',
        'IP'
    ])
    
    # Dados
    for resposta in respostas.order_by('-data'):
        writer.writerow([
            resposta.formulario.nome,
            resposta.nome,
            resposta.email,
            resposta.telefone,
            resposta.assunto,
            resposta.mensagem,
            resposta.data.strftime('%d/%m/%Y %H:%M'),
            resposta.ip_address or ''
        ])
    
    return response










@csrf_exempt
@require_http_methods(["POST"])
def chatbot_conversar(request):
    """API endpoint para conversar com o chatbot"""
    try:
        data = json.loads(request.body)
        pergunta = data.get('pergunta', '').strip()
        sessao_id = data.get('sessao_id') or str(uuid.uuid4())
        
        if not pergunta:
            return JsonResponse({
                'erro': 'Pergunta não pode estar vazia'
            }, status=400)
        
        if len(pergunta) > 500:
            return JsonResponse({
                'erro': 'Pergunta muito longa. Máximo 500 caracteres.'
            }, status=400)
        
        # Pega IP do usuário
        user_ip = request.META.get('REMOTE_ADDR')
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            user_ip = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
        
        # Inicializa serviço do chatbot
        chatbot_service = ChatbotService()
        
        # Gera resposta
        resultado = chatbot_service.gerar_resposta(pergunta, sessao_id, user_ip)
        
        return JsonResponse({
            'resposta': resultado['resposta'],
            'paginas_relacionadas': resultado['paginas'],
            'sessao_id': sessao_id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'erro': 'JSON inválido'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'erro': 'Erro interno do servidor'
        }, status=500)


@require_http_methods(["GET"])
def chatbot_config(request):
    """Retorna configurações do chatbot para o frontend"""
    try:
        config = ChatbotConfig.objects.first()
        chatbot_widget = ChatbotWidget.objects.filter(ativo=True).first()
        
        if not config or not config.ativo:
            return JsonResponse({'ativo': False})
        
        return JsonResponse({
            'ativo': True,
            'nome': config.nome,
            'mensagem_boas_vindas': config.mensagem_boas_vindas,
            'widget': {
                'titulo': chatbot_widget.titulo_widget if chatbot_widget else 'Assistente Virtual ENAP',
                'cor_primaria': chatbot_widget.cor_primaria if chatbot_widget else '#0066cc',
                'cor_secundaria': chatbot_widget.cor_secundaria if chatbot_widget else '#ffffff',
                'posicao': chatbot_widget.posicao if chatbot_widget else 'bottom-right',
                'icone': chatbot_widget.icone_chatbot if chatbot_widget else '🤖',
                'mobile': chatbot_widget.mostrar_em_mobile if chatbot_widget else True,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'ativo': False, 
            'erro': 'Erro ao carregar configurações'
        })


@require_http_methods(["GET"]) 
def chatbot_status(request):
    """Status do chatbot para debugging"""
    try:
        from .models import PaginaIndexada, ConversaChatbot
        
        config = ChatbotConfig.objects.first()
        total_paginas = PaginaIndexada.objects.count()
        total_conversas = ConversaChatbot.objects.count()
        
        return JsonResponse({
            'configurado': bool(config and config.api_key_google),
            'ativo': bool(config and config.ativo),
            'paginas_indexadas': total_paginas,
            'total_conversas': total_conversas,
            'modelo_ia': config.modelo_ia if config else None,
        })
        
    except Exception as e:
        return JsonResponse({
            'erro': str(e)
        })