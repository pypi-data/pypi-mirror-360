
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase

# Imports Lista
from nsj_rest_lib.descriptor.dto_list_field import DTOListField

from nsj_integracao_api_entidades.dto.workflow_acoes import AcoDTO
from nsj_integracao_api_entidades.entity.workflow_acoes import AcoEntity

from nsj_integracao_api_entidades.dto.workflow_diagramas import DiagramaDTO
from nsj_integracao_api_entidades.entity.workflow_diagramas import DiagramaEntity

from nsj_integracao_api_entidades.dto.workflow_equipes import EquipeDTO
from nsj_integracao_api_entidades.entity.workflow_equipes import EquipeEntity

from nsj_integracao_api_entidades.dto.workflow_equipesusuarios import EquipesusuarioDTO
from nsj_integracao_api_entidades.entity.workflow_equipesusuarios import EquipesusuarioEntity

from nsj_integracao_api_entidades.dto.workflow_estados import EstadoDTO
from nsj_integracao_api_entidades.entity.workflow_estados import EstadoEntity

from nsj_integracao_api_entidades.dto.workflow_papeis import PapeiDTO
from nsj_integracao_api_entidades.entity.workflow_papeis import PapeiEntity

from nsj_integracao_api_entidades.dto.workflow_papeisequipes import PapeisequipeDTO
from nsj_integracao_api_entidades.entity.workflow_papeisequipes import PapeisequipeEntity

from nsj_integracao_api_entidades.dto.workflow_processos import ProcessoDTO
from nsj_integracao_api_entidades.entity.workflow_processos import ProcessoEntity

# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class EscopoDTO(DTOBase):
    # Atributos da entidade
    id: int = DTOField(
      pk=True,
      entity_field='escopoworkflow',
      resume=True,
      not_null=True,)
    tenant: int = DTOField(
      partition_data=tenant_is_partition_data,
      resume=True,
      not_null=True,)
    nome: str = DTOField()
    codigo: str = DTOField()
    lastupdate: datetime.datetime = DTOField()
    # Atributos de lista
    processos: list = DTOListField(
      dto_type=ProcessoDTO,
      entity_type=ProcessoEntity,
      related_entity_field='escopoworkflow',
    )
    equipes: list = DTOListField(
      dto_type=EquipeDTO,
      entity_type=EquipeEntity,
      related_entity_field='escopoworkflow',
    )
    equipesusuarios: list = DTOListField(
      dto_type=EquipesusuarioDTO,
      entity_type=EquipesusuarioEntity,
      related_entity_field='escopoworkflow',
    )
    diagramas: list = DTOListField(
      dto_type=DiagramaDTO,
      entity_type=DiagramaEntity,
      related_entity_field='escopoworkflow',
    )
    papeis: list = DTOListField(
      dto_type=PapeiDTO,
      entity_type=PapeiEntity,
      related_entity_field='escopoworkflow',
    )
    papeisequipes: list = DTOListField(
      dto_type=PapeisequipeDTO,
      entity_type=PapeisequipeEntity,
      related_entity_field='escopoworkflow',
    )
    estados: list = DTOListField(
      dto_type=EstadoDTO,
      entity_type=EstadoEntity,
      related_entity_field='escopoworkflow',
    )
    acoes: list = DTOListField(
      dto_type=AcoDTO,
      entity_type=AcoEntity,
      related_entity_field='escopoworkflow',
    )

