
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase

# Imports Lista
from nsj_rest_lib.descriptor.dto_list_field import DTOListField

from nsj_integracao_api_entidades.dto.estoque_perfiltrib_fed_validades_impostos import PerfiltribFedValidadeImpostoDTO
from nsj_integracao_api_entidades.entity.estoque_perfiltrib_fed_validades_impostos import PerfiltribFedValidadeImpostoEntity

# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class PerfiltribFedValidadeDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='perfiltrib_fed_validade',
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
    perfiltrib_fed: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    data: datetime.datetime = DTOField()
    lastupdate: datetime.datetime = DTOField()
    # Atributos de lista
    perfiltribvalidadesimpostos: list = DTOListField(
      dto_type=PerfiltribFedValidadeImpostoDTO,
      entity_type=PerfiltribFedValidadeImpostoEntity,
      related_entity_field='perfiltrib_fed_validade'
    )

