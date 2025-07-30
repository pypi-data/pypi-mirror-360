
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase

# Imports Lista
from nsj_rest_lib.descriptor.dto_list_field import DTOListField

from nsj_integracao_api_entidades.dto.estoque_tabelasdeprecoscategorias import TabelasdeprecoscategoriaDTO
from nsj_integracao_api_entidades.entity.estoque_tabelasdeprecoscategorias import TabelasdeprecoscategoriaEntity

from nsj_integracao_api_entidades.dto.estoque_tabelasdeprecosentidades import TabelasdeprecosentidadeDTO
from nsj_integracao_api_entidades.entity.estoque_tabelasdeprecosentidades import TabelasdeprecosentidadeEntity

from nsj_integracao_api_entidades.dto.estoque_tabelasdeprecosestabelecimentos import TabelasdeprecosestabelecimentoDTO
from nsj_integracao_api_entidades.entity.estoque_tabelasdeprecosestabelecimentos import TabelasdeprecosestabelecimentoEntity

from nsj_integracao_api_entidades.dto.estoque_tabelasdeprecosfamilias import TabelasdeprecosfamiliaDTO
from nsj_integracao_api_entidades.entity.estoque_tabelasdeprecosfamilias import TabelasdeprecosfamiliaEntity

from nsj_integracao_api_entidades.dto.estoque_tabelasdeprecositens import TabelasdeprecositenDTO
from nsj_integracao_api_entidades.entity.estoque_tabelasdeprecositens import TabelasdeprecositenEntity

from nsj_integracao_api_entidades.dto.estoque_tabelasdeprecosuf import TabelasdeprecosufDTO
from nsj_integracao_api_entidades.entity.estoque_tabelasdeprecosuf import TabelasdeprecosufEntity

# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class TabelasdeprecoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='tabeladepreco',
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
    descricao: str = DTOField(
      not_null=True,)
    desconto: int = DTOField(
      not_null=True,)
    reajuste: float = DTOField(
      not_null=True,)
    id_estabelecimento: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    finalidade: int = DTOField(
      not_null=True,)
    bloqueada: bool = DTOField(
      not_null=True,)
    id_empresa: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    inicioperiodo: datetime.datetime = DTOField()
    fimperiodo: datetime.datetime = DTOField()
    lastupdate: datetime.datetime = DTOField()
    datahoraaplicacaoreajuste: datetime.datetime = DTOField()
    dataagendamentoreajuste: datetime.datetime = DTOField()
    percentualfatorcomissao: float = DTOField()
    descontosobreprecovenda: bool = DTOField(
      not_null=True,)
    descontovalorproduto: bool = DTOField(
      not_null=True,)
    # Atributos de lista
    tabelasdeprecoscategorias: list = DTOListField(
      dto_type=TabelasdeprecoscategoriaDTO,
      entity_type=TabelasdeprecoscategoriaEntity,
      related_entity_field='id_tabeladepreco',
    )
    tabelasdeprecosentidades: list = DTOListField(
      dto_type=TabelasdeprecosentidadeDTO,
      entity_type=TabelasdeprecosentidadeEntity,
      related_entity_field='id_tabeladepreco',
    )
    tabelasdeprecosestabelecimentos: list = DTOListField(
      dto_type=TabelasdeprecosestabelecimentoDTO,
      entity_type=TabelasdeprecosestabelecimentoEntity,
      related_entity_field='id_tabeladepreco',
    )
    tabelasdeprecosfamilias: list = DTOListField(
      dto_type=TabelasdeprecosfamiliaDTO,
      entity_type=TabelasdeprecosfamiliaEntity,
      related_entity_field='id_tabeladepreco',
    )
    tabelasdeprecositens: list = DTOListField(
      dto_type=TabelasdeprecositenDTO,
      entity_type=TabelasdeprecositenEntity,
      related_entity_field='id_tabeladepreco',
    )
    tabelasdeprecosuf: list = DTOListField(
      dto_type=TabelasdeprecosufDTO,
      entity_type=TabelasdeprecosufEntity,
      related_entity_field='id_tabeladepreco',
    )

