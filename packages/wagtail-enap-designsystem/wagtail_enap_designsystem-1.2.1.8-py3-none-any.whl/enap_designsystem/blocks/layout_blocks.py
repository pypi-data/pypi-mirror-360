"""
Os blocos de layout são essencialmente um wrapper em torno do conteúdo.
e.g. rows, columns, hero units, etc.
"""

from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from django.db import models

from coderedcms.settings import crx_settings


from .base_blocks import BaseLayoutBlock
from .base_blocks import CoderedAdvColumnSettings
from .content_blocks import EnapAccordionBlock
from .content_blocks import EnapBannerBlock

from .content_blocks import EnapAccordionBlock, EnapBannerBlock, EnapFooterLinkBlock, EnapFooterSocialBlock

from wagtail.blocks import StructBlock, CharBlock, ListBlock, ChoiceBlock
from wagtail.fields import StreamField


class ColumnBlock(BaseLayoutBlock):
    """
    Renders content in a column.
    """

    column_size = blocks.ChoiceBlock(
        choices=crx_settings.CRX_FRONTEND_COL_SIZE_CHOICES,
        default=crx_settings.CRX_FRONTEND_COL_SIZE_DEFAULT,
        required=False,
        label=_("Column size"),
    )

    advsettings_class = CoderedAdvColumnSettings

    class Meta:
        template = "coderedcms/blocks/column_block.html"
        icon = "placeholder"
        label = "Column"


class GridBlock(BaseLayoutBlock):
    """
    Renders a row of columns.
    """

    fluid = blocks.BooleanBlock(
        required=False,
        label=_("Full width"),
    )

    class Meta:
        template = "coderedcms/blocks/grid_block.html"
        icon = "cr-columns"
        label = _("Responsive Grid Row")

    def __init__(self, local_blocks=None, **kwargs):
        super().__init__(local_blocks=[("content", ColumnBlock(local_blocks))])


class EnapFooterGridBlock(BaseLayoutBlock):
    """
    Renders a row of cards.
    """

    title = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Titulo"),
    )

    links = blocks.ListBlock(
		EnapFooterLinkBlock(),
		label=_("Links do Footer"),
	)
    class Meta:
        template = "enap_designsystem/blocks/footer_grid_block.html"
        icon = "cr-th-large"
        label = _("Footer Grid")


class EnapFooterSocialGridBlock(BaseLayoutBlock):
	"""
	Bloco para agrupar redes sociais no footer.
	"""

	social_links = blocks.ListBlock(
		EnapFooterSocialBlock(),
		label=_("Redes Sociais"),
	)

	class Meta:
		template = "enap_designsystem/blocks/footer/footer_social_grid_block.html"
		icon = "cr-site"
		label = _("Social Grid")


class CardGridBlock(BaseLayoutBlock):
    """
    Renders a row of cards.
    """

    fluid = blocks.BooleanBlock(
        required=False,
        label=_("Full width"),
    )
    class Meta:
        template = "coderedcms/blocks/cardgrid_deck.html"
        icon = "cr-th-large"
        label = _("Card Grid")

class EnapCardGridBlock(BaseLayoutBlock):
    """
    Renderiza uma linha de cards
    """
    grid = blocks.ChoiceBlock(
		choices=[
            ('cards-gri-1', '1 card por linha'),
			('cards-gri-2', 'Até 2 cards'),
			('cards-gri-3', 'Até 3 cards'),
			('cards-gri-4', 'Até 4 cards')
		],
		default='cards-gri-2',
		help_text="Escolha os limites de card por linha para essa grid.",
		label="Card por linha"
	)
    class Meta:
        template = "enap_designsystem/blocks/cardgrid_block.html"
        icon = "cr-th-large"
        label = _("Enap Card 1, 2, 3 ou 4 por linha")


class EnapSectionBlock(BaseLayoutBlock):
    """
    Renderiza uma seção com titulo-subtitulo permitindo componentes dentro
    """

    id_slug = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("#ID da seção"),
    )

    custom_class = blocks.ChoiceBlock(
		choices=[
			('bg-white', 'Fundo branco'),
			('bg-blue', 'Fundo blue'),
			('bg-gray', 'Fundo cinza'),
            ('bg-whitetwo', 'Fundo branco alternativo'),
            ('bg-darkgreen', 'Fundo verde escuro')
		],
		default='bg-white',
		help_text="Escolha a cor de fundo para a seção",
		label="Cor de fundo"
	)

    title = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Titulo"),
    )

    subtitle = blocks.RichTextBlock(
        required=False,
        features=["bold", "italic", "ol", "ul", "hr", "link", "document-link"],
        label=_("Subtitulo"),
    )
    class Meta:
        template = "enap_designsystem/blocks/section_block.html"
        icon = "cr-th-large"
        label = _("Enap Section Block")


class HeroBlock(BaseLayoutBlock):
    """
    Wrapper with color and image background options.
    """

    fluid = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Full width"),
    )
    is_parallax = blocks.BooleanBlock(
        required=False,
        label=_("Parallax Effect"),
        help_text=_(
            "Background images scroll slower than foreground images, creating an illusion of depth."
        ),
    )
    background_image = ImageChooserBlock(required=False)
    tile_image = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Tile background image"),
    )
    background_color = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Background color"),
        help_text=_("Hexadecimal, rgba, or CSS color notation (e.g. #ff0011)"),
    )
    foreground_color = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_("Text color"),
        help_text=_("Hexadecimal, rgba, or CSS color notation (e.g. #ff0011)"),
    )

    class Meta:
        template = "coderedcms/blocks/hero_block.html"
        icon = "cr-newspaper-o"
        label = "Bloco Hero"


class AccordionWrapperBlock(BaseLayoutBlock):
    """
    Wrapper for the AccordionBlock.
    """
    accordion = EnapAccordionBlock()

    class Meta:
        template = "enap_designsystem/blocks/accordions.html" 
        icon = "bars"

        label = "Accordion Wrapper"




class HeroBlock(BaseLayoutBlock):
    """
    Wrapper with color and image background options.
    """

    fluid = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_("Full width"),
    )
    is_parallax = blocks.BooleanBlock(
        required=False,
        label=_("Parallax Effect"),
        help_text=_(
            "Background images scroll slower than foreground images, creating an illusion of depth."
        ),
    )
    background_image = ImageChooserBlock(required=True) 
    tile_image = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_("Tile background image"),
    )
    content = blocks.StreamBlock([
        ('enap_banner', EnapBannerBlock()),
    ], label="Content")

    class Meta:
        template = "enap_designsystem/blocks/banner.html" 
        icon = "cr-newspaper-o"
        label = _("Banner Hero")




class HeroVideoBlock(BaseLayoutBlock):
    """
    Wrapper with color and image background options.
    """

    video_background = models.FileField(
        upload_to='media/videos',
        null=True, 
        blank=True, 
        verbose_name="Vídeo de Fundo"
    )
    content = blocks.StreamBlock([
        ('enap_banner', EnapBannerBlock()),
    ], label="Content")

    class Meta:
        template = "enap_designsystem/blocks/banner-video.html" 
        icon = "cr-newspaper-o"
        label = _("Banner video Hero")




class FeatureImageTextBlock(blocks.StructBlock):
    background_image = ImageChooserBlock(required=True)
    title = blocks.CharBlock(required=True, max_length=255)
    description = blocks.RichTextBlock(required=True)

    class Meta:
        template = "enap_designsystem/blocks/feature-img-texts.html"
        label = _("Feature Image and Text")



