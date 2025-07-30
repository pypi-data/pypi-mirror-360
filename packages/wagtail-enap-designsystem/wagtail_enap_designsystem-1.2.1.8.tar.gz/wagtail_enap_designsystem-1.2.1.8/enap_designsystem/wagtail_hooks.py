from wagtail import hooks
from django.utils.html import format_html
from django.templatetags.static import static
from enap_designsystem.blocks import ENAPNoticia
from django.urls import reverse

@hooks.register('insert_global_admin_css')
def global_admin_css():
	return format_html(
		'<link rel="stylesheet" href="{}"><link rel="stylesheet" href="{}">',
		static('css/main_layout.css'),
		static('css/mid_layout.css')
	)

@hooks.register('insert_global_admin_js')
def global_admin_js():
	return format_html(
		'<script src="{}"></script><script src="{}"></script>',
		static('js/main_layout.js'),
		static('js/mid_layout.js')
	)

@hooks.register("before_create_page")
def set_default_author_on_create(request, parent_page, page_class):
	if page_class == ENAPNoticia:
		def set_author(instance):
			instance.author = request.user
		return set_author
	




@hooks.register('register_admin_menu_item')
def register_export_menu_item():
    from wagtail.admin.menu import MenuItem
    
    return MenuItem(
        '📊 Exportar Respostas', 
        '/exportar-respostas/',
        icon_name='download',
        order=1000
    )

# Hook para adicionar botão na página de snippets
@hooks.register('insert_global_admin_js')
def add_export_button():
    return format_html(
        """
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Adiciona botão de exportar na página de respostas
            if (window.location.href.includes('/admin/snippets/enap_designsystem/respostaformulario/')) {{
                const header = document.querySelector('.content-wrapper h1, .content-wrapper h2');
                if (header) {{
                    const exportBtn = document.createElement('a');
                    exportBtn.href = '/admin/exportar-respostas/';
                    exportBtn.className = 'button button-small button-secondary';
                    exportBtn.style.marginLeft = '10px';
                    exportBtn.innerHTML = '📊 Exportar CSV';
                    exportBtn.target = '_blank';
                    header.appendChild(exportBtn);
                }}
            }}
        }});
        </script>
        """
    )