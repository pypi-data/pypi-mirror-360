
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase

# Imports Lista
from nsj_rest_lib.descriptor.dto_list_field import DTOListField

from nsj_integracao_api_entidades.dto.estoque_perfiltrib_est_validades import PerfiltribEstValidadeDTO
from nsj_integracao_api_entidades.entity.estoque_perfiltrib_est_validades import PerfiltribEstValidadeEntity

# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class PerfiltribEstDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='perfiltrib_est',
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
    codigo: str = DTOField(
      candidate_key=True,
      strip=False,
      resume=True,
      not_null=True,)
    descricao: str = DTOField()
    uf_origem: str = DTOField(
      not_null=True,)
    icms_aliquotainterna: float = DTOField()
    lastupdate: datetime.datetime = DTOField()
    id_grupo_empresarial: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_empresa: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    situacao: int = DTOField()
    motivo: str = DTOField()
    # Atributos de lista
    perfiltribestvalidades: list = DTOListField(
      dto_type=PerfiltribEstValidadeDTO,
      entity_type=PerfiltribEstValidadeEntity,
      related_entity_field='perfiltrib_est'
    )

