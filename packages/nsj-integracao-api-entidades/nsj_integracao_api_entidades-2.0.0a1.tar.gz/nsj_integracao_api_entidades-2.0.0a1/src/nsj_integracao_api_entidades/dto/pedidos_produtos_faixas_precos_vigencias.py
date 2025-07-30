
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase

# Imports Lista
from nsj_rest_lib.descriptor.dto_list_field import DTOListField

from nsj_integracao_api_entidades.dto.pedidos_produtos_faixas_precos import ProdutoFaixaPrecoDTO
from nsj_integracao_api_entidades.entity.pedidos_produtos_faixas_precos import ProdutoFaixaPrecoEntity
from nsj_integracao_api_entidades.dto.pedidos_produtos_faixas_precos_segmentos import ProdutoFaixaPrecoSegmentoDTO
from nsj_integracao_api_entidades.entity.pedidos_produtos_faixas_precos_segmentos import  ProdutoFaixaPrecoSegmentoEntity


# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class ProdutoFaixaPrecoVigenciaDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='produto_faixa_preco_vigencia',
      resume=True,
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tenant: int = DTOField(
      partition_data=tenant_is_partition_data,
      resume=True,
      not_null=True,)
    produto: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    data_inicio: datetime.datetime = DTOField()
    data_fim: datetime.datetime = DTOField()
    qualificacao: int = DTOField()
    # Atributos de lista
    produtos_faixas_precos: list = DTOListField(
      dto_type=ProdutoFaixaPrecoDTO,
      entity_type=ProdutoFaixaPrecoEntity,
      related_entity_field='produto_faixa_preco_vigencia',
    )
    produtos_faixas_precos_segmentos: list = DTOListField(
      dto_type=ProdutoFaixaPrecoSegmentoDTO,
      entity_type=ProdutoFaixaPrecoSegmentoEntity,
      related_entity_field='produto_faixa_preco_vigencia',
    )

