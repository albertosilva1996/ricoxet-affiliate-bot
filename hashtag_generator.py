"""
Módulo gerador de hashtags e legendas para produtos
"""
from typing import List, Dict
import re

class HashtagGenerator:
    """Gerador de hashtags e legendas para produtos Shopee"""
    
    # Dicionário de categorias e hashtags relacionadas
    CATEGORY_HASHTAGS = {
        'tênis': [
            '#TênisEsportivo', '#TênisBranco', '#TênisConfortável',
            '#AcademiaTênis', '#TênisBarato', '#TênisPromoção',
            '#CalçadoEsportivo', '#TênisQualidade', '#ComprarTênis',
            '#ShopeeAfiliado', '#OfertaTênis', '#TênisDesconto'
        ],
        'sapato': [
            '#SapatoConfortável', '#SapatoBarato', '#SapatoPromoção',
            '#CalçadoQualidade', '#SapatoEstilo', '#ComprarSapato',
            '#ShopeeAfiliado', '#OfertaSapato', '#SapatoDesconto'
        ],
        'roupa': [
            '#RoupaBarata', '#RoupaPromoção', '#RoupaQualidade',
            '#EstiloRoupa', '#ComprarRoupa', '#ShopeeAfiliado',
            '#OfertaRoupa', '#RoupaDesconto', '#MódaAfiliada'
        ],
        'eletrônico': [
            '#EletrônicoBarato', '#EletrônicoPromoção', '#TecnologiaAfiliada',
            '#ComprarEletrônico', '#ShopeeAfiliado', '#OfertaEletrônico',
            '#EletrônicoDesconto', '#GadgetBarato', '#TechPromoção'
        ],
        'beleza': [
            '#BelezaBarata', '#BelezaPromoção', '#CuidadosPele',
            '#CosméticoBarato', '#ComprarBeleza', '#ShopeeAfiliado',
            '#OfertaBeleza', '#BelezaDesconto', '#AutocuidadoPromoção'
        ],
        'casa': [
            '#CasaBarata', '#CasaPromoção', '#DecoraçãoBarata',
            '#ComprarCasa', '#ShopeeAfiliado', '#OfertaCasa',
            '#CasaDesconto', '#DecoraçãoPromoção', '#MóvelBarato'
        ],
        'esporte': [
            '#EsporteBarato', '#EsportePromoção', '#AcademiaBaço',
            '#FitnessBaço', '#ComprarEsporte', '#ShopeeAfiliado',
            '#OfertaEsporte', '#EsporteDesconto', '#TreinoBarato'
        ],
        'infantil': [
            '#BrinquedoBarato', '#BrinquedoPromoção', '#InfantilBarato',
            '#ComprarInfantil', '#ShopeeAfiliado', '#OfertaInfantil',
            '#InfantilDesconto', '#BrinquedoDesconto', '#CriançaPromoção'
        ],
    }
    
    # Hashtags genéricas sempre úteis
    GENERIC_HASHTAGS = [
        '#ShopeeAfiliado', '#ComprarAgora', '#Promoção',
        '#Desconto', '#OfertaDoDia', '#Imperdível',
        '#CompraSegura', '#EntregaRápida', '#MelhorPreço',
        '#ShopeeOferta', '#ValeAPena', '#Recomendo'
    ]
    
    def __init__(self):
        pass
    
    def extract_category(self, product_name: str) -> str:
        """Extrai a categoria do produto pelo nome"""
        product_lower = product_name.lower()
        
        for category, _ in self.CATEGORY_HASHTAGS.items():
            if category in product_lower:
                return category
        
        return 'geral'
    
    def generate_hashtags(self, product_name: str, max_hashtags: int = 15) -> List[str]:
        """
        Gera lista de hashtags relevantes para o produto
        
        Args:
            product_name: Nome do produto
            max_hashtags: Número máximo de hashtags
        
        Returns:
            Lista de hashtags
        """
        category = self.extract_category(product_name)
        
        # Pegar hashtags específicas da categoria
        if category in self.CATEGORY_HASHTAGS:
            category_tags = self.CATEGORY_HASHTAGS[category][:8]
        else:
            category_tags = []
        
        # Combinar com hashtags genéricas
        all_tags = category_tags + self.GENERIC_HASHTAGS
        
        # Remover duplicatas e limitar ao máximo
        unique_tags = list(dict.fromkeys(all_tags))[:max_hashtags]
        
        return unique_tags
    
    def generate_caption(
        self,
        product_name: str,
        current_price: float,
        discount_percent: int = 0
    ) -> str:
        """
        Gera uma legenda persuasiva para o produto
        
        Args:
            product_name: Nome do produto
            current_price: Preço atual
            discount_percent: Percentual de desconto
        
        Returns:
            Legenda formatada
        """
        discount_text = f"com {discount_percent}% OFF" if discount_percent > 0 else "em promoção"
        
        captions = [
            f"🔥 {product_name} {discount_text}!\n\nPor apenas R$ {current_price:.2f}\n\nClique no link para aproveitar! 👇",
            f"💰 Achado! {product_name} {discount_text}!\n\nR$ {current_price:.2f}\n\nVai faltar! Corre lá! 🏃‍♂️",
            f"✨ Olha que oferta! {product_name}\n\nSaiu por R$ {current_price:.2f} {discount_text}\n\nNão perca! 🛍️",
            f"🎉 PROMOÇÃO! {product_name}\n\nR$ {current_price:.2f}\n\nVale muito a pena! Confira! ⬇️",
            f"💎 Qualidade com preço bom!\n\n{product_name}\n\nR$ {current_price:.2f} {discount_text}\n\nLink na bio! 👆"
        ]
        
        # Selecionar caption baseado no hash do nome (para variedade)
        return captions[hash(product_name) % len(captions)]
    
    def generate_full_post(
        self,
        product_name: str,
        current_price: float,
        original_price: float,
        max_hashtags: int = 15
    ) -> Dict[str, str]:
        """
        Gera um pacote completo com legenda e hashtags
        
        Args:
            product_name: Nome do produto
            current_price: Preço atual
            original_price: Preço original
            max_hashtags: Número máximo de hashtags
        
        Returns:
            Dicionário com caption e hashtags
        """
        discount_percent = int(((original_price - current_price) / original_price) * 100) if original_price > 0 else 0
        
        caption = self.generate_caption(product_name, current_price, discount_percent)
        hashtags = self.generate_hashtags(product_name, max_hashtags)
        
        return {
            'caption': caption,
            'hashtags': hashtags,
            'full_text': f"{caption}\n\n{' '.join(hashtags)}",
            'discount_percent': discount_percent
        }


if __name__ == "__main__":
    generator = HashtagGenerator()
    
    # Teste
    result = generator.generate_full_post(
        product_name="Tênis Esportivo Confortável Academia",
        current_price=59.90,
        original_price=89.00
    )
    
    print("=== LEGENDA ===")
    print(result['caption'])
    print("\n=== HASHTAGS ===")
    print(' '.join(result['hashtags']))
    print("\n=== DESCONTO ===")
    print(f"{result['discount_percent']}% OFF")
