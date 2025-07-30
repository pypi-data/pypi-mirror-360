# coding: utf-8
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Iterator
from typing import List
from typing import Optional

from lxml import etree
from requests.exceptions import RequestException
from zeep import Client
from zeep.exceptions import Fault
from zeep.plugins import HistoryPlugin
from zeep.transports import Transport
from zeep.xsd.valueobjects import CompoundValue

from adapter_client.core.domain import model

from ..base import AbstractInterface
from ..base import ExchangeResult


FAULTS_NS = (
    'urn://x-artefacts-smev-gov-ru/services/service-adapter/types/faults'
)
SYSTEM_FAULT = '{%s}SystemFault' % FAULTS_NS
VALIDATION_FAULT = '{%s}ValidationFault' % FAULTS_NS


class Interface(AbstractInterface):

    """SOAP-интерфейс для взаимодействия с Адаптером СМЭВ."""

    def _init_service(self):

        history = HistoryPlugin()

        service = Client(
            (
                Path(__file__).parent / 'schema/adapter.wsdl'
            ).absolute().as_posix(),
            transport=Transport(timeout=self._config.request_timeout_sec),
            plugins=[history]
        ).create_service(
            '{urn://x-artefacts-smev-gov-ru/services/service-adapter}'
            'SMEVServiceAdapterSoapBinding',
            self._config.adapter_address
        )

        service.history = history

        return service

    def send(
        self,
        *outgoing_messages: model.OutgoingMessage
    ) -> Iterator[ExchangeResult]:
        with ThreadPoolExecutor() as executor:
            return executor.map(self._send_one, outgoing_messages)

    def find(
        self,
        *outgoing_messages: model.OutgoingMessage
    ) -> Iterator[ExchangeResult]:
        with ThreadPoolExecutor() as executor:
            return executor.map(self._find_one, outgoing_messages)

    def get(self) -> ExchangeResult:
        exchange_result = ExchangeResult(request_type=model.RequestType.get)

        try:
            self._config.validate()

        except model.ConfigNotValid as e:
            exchange_result.error = e
            return exchange_result

        service = self._init_service()
        exchange_result.address = service._binding_options['address']

        try:
            exchange_result.result = service.Get(
                **self._prepare_get_params()
            )

        except RequestException as e:
            exchange_result.error = e

        except Fault as e:
            exchange_result.error = e

        except Exception as e:  # pylint: disable=broad-except
            exchange_result.error = e
        else:
            exchange_result.message_metadata = (
                self._extract_incoming_message_data(exchange_result.result)
            )

        history = service.history

        try:
            exchange_result.request = (
                etree.tostring(
                    history.last_sent['envelope'], encoding='utf-8'
                ).decode('utf-8')
                if history and history.last_sent else None
            )
        except IndexError:  # deque index out of range == no history
            exchange_result.request = None

        try:
            exchange_result.response = (
                etree.tostring(
                    history.last_received['envelope'], encoding='utf-8'
                ).decode('utf-8')
                if history and history.last_received else None
            )
        except IndexError:  # deque index out of range == no history
            exchange_result.response = None

        return exchange_result

    def _prepare_send_params(self, message: model.Message) -> dict:

        content = {
            'MessagePrimaryContent': etree.fromstring(message.body),
        }
        metadata = {
            'clientId': message.client_id,
            'testMessage': message.test
        }

        if message.attachments:
            content['AttachmentHeaderList'] = [
                {'AttachmentHeader': {
                    'filePath': path,
                    'TransferMethod': 'REFERENCE'
                }}
                for path in message.attachments
            ]

        message_direction = 'Request'

        # если есть reply_to, то это сообщение — ответ
        if message.reply_to:
            message_direction = 'Response'
            metadata.update(replyToClientId=message.reply_to.client_id)

        if self._config.node_mnemonics:
            metadata.update(nodeId=self._config.node_mnemonics)

        result = {
            'itSystem': self._config.app_mnemonics,
            f'{message_direction}Message': {
                f'{message_direction}Metadata': metadata,
                f'{message_direction}Content': {'content': content}
            }
        }
        return result

    def _send_one(
        self,
        outgoing_message: model.OutgoingMessage
    ) -> ExchangeResult:

        exchange_result = ExchangeResult(
            message_metadata=outgoing_message,
            request_type=model.RequestType.send,
        )

        try:
            self._config.validate()

        except model.ConfigNotValid as e:
            exchange_result.error = e
            return exchange_result

        service = self._init_service()
        exchange_result.address = service._binding_options['address']

        outgoing_message.attempts += 1
        try:
            exchange_result.result = service.Send(
                **self._prepare_send_params(outgoing_message.message)
            )

        except RequestException as e:
            exchange_result.error = e
            outgoing_message.status = model.OutgoingStatus.retry

        except Fault as e:
            exchange_result.error = e
            outgoing_message.status = model.OutgoingStatus.error

            if hasattr(e, 'detail'):
                fault_type: etree._Element = e.detail.getchildren()[0].tag

                if fault_type == SYSTEM_FAULT:
                    outgoing_message.status = model.OutgoingStatus.retry

        except Exception as e:  # pylint: disable=broad-except
            exchange_result.error = e
            outgoing_message.status = model.OutgoingStatus.error

        else:
            assert exchange_result.result['itSystem'] == (
                self._config.app_mnemonics
            )

            outgoing_message.message.message_id = (
                exchange_result.result['MessageId']
            )
            outgoing_message.status = model.OutgoingStatus.sent

        history = service.history

        try:
            exchange_result.request = (
                etree.tostring(
                    history.last_sent['envelope'], encoding='utf-8'
                ).decode('utf-8')
                if history and history.last_sent else None
            )
        except IndexError:  # deque index out of range == no history
            exchange_result.request = None

        try:
            exchange_result.response = (
                etree.tostring(
                    history.last_received['envelope'], encoding='utf-8'
                ).decode('utf-8')
                if history and history.last_received else None
            )
        except IndexError:  # deque index out of range == no history
            exchange_result.response = None

        return exchange_result

    def _prepare_find_params(self, message: model.Message) -> dict:

        result = {
            'itSystem': self._config.app_mnemonics,
            'specificQuery': {
                'messageClientIdCriteria': {
                    'clientId': message.client_id,
                    'clientIdCriteria': 'GET_RESPONSE_BY_REQUEST_CLIENTID'
                },
            }
        }
        return result

    def _find_one(
        self,
        outgoing_message: model.OutgoingMessage
    ) -> ExchangeResult:
        exchange_result = ExchangeResult(request_type=model.RequestType.find)

        try:
            self._config.validate()

        except model.ConfigNotValid as e:
            exchange_result.error = e
            return exchange_result

        service = self._init_service()
        exchange_result.address = service._binding_options['address']

        try:
            exchange_result.result = service.Find(
                **self._prepare_find_params(outgoing_message.message)
            )

        except RequestException as e:
            exchange_result.error = e

        except Fault as e:
            exchange_result.error = e

        except Exception as e:  # pylint: disable=broad-except
            exchange_result.error = e
        else:
            primary_adapter_message = next(
                filter(
                    lambda x: x.Message.messageType == 'PrimaryMessage',
                    exchange_result.result
                ),
                None
            )
            if primary_adapter_message:
                exchange_result.message_metadata = (
                    self._extract_incoming_message_data(
                        primary_adapter_message
                    )
                )
                exchange_result.message_metadata.message.reply_to = (
                    outgoing_message.message
                )

        history = service.history

        try:
            exchange_result.request = (
                etree.tostring(
                    history.last_sent['envelope'], encoding='utf-8'
                ).decode('utf-8')
                if history and history.last_sent else None
            )
        except IndexError:  # deque index out of range == no history
            exchange_result.request = None

        try:
            exchange_result.response = (
                etree.tostring(
                    history.last_received['envelope'], encoding='utf-8'
                ).decode('utf-8')
                if history and history.last_received else None
            )
        except IndexError:  # deque index out of range == no history
            exchange_result.response = None

        return exchange_result

    def _prepare_get_params(self) -> dict:
        result = {
            'itSystem': self._config.app_mnemonics,
            'specificQuery': {
                'messageTypeCriteria': 'REQUEST'
            }
        }

        if self._config.node_mnemonics:
            result.update(nodeId=self._config.node_mnemonics)

        return result

    def _extract_attachments(self, message_content) -> List[str]:
        """Извлекает вложения из основного содержимого сообщения."""
        attachment_header = getattr(
            message_content.AttachmentHeaderList,
            'AttachmentHeader',
            ()
        )
        return [ah.filePath for ah in attachment_header]

    def _extract_incoming_message_data(
        self,
        adapter_message: CompoundValue,
    ) -> Optional[model.MessageMetadataInterface]:

        request_msg = adapter_message.Message
        smev_metadata = adapter_message.smevMetadata

        if not all((request_msg, smev_metadata)):
            return

        msg_content = (
            getattr(request_msg, 'RequestContent', None) or
            getattr(request_msg, 'ResponseContent', None)
        ).content

        msg_metadata = (
            getattr(request_msg, 'RequestMetadata', None) or
            getattr(request_msg, 'ResponseMetadata', None)
        )

        assert smev_metadata.Recipient == self._config.app_mnemonics

        # полезная нагрузка ответа
        # не уверен что стоит трогать `_value_1`, но иного способа не вижу
        primary_content = msg_content.MessagePrimaryContent._value_1
        etree.indent(primary_content, '  ')

        message = model.Message(
            # client_id ответа
            client_id=msg_metadata.clientId,
            # message_id ответа
            message_id=smev_metadata.MessageId,
            # вид сведений
            message_type=primary_content.nsmap[primary_content.prefix],
            body=etree.tostring(
                primary_content,
                pretty_print=True,
                encoding='utf-8'
            ).decode('utf-8').strip(),
            reference_message_id=getattr(
                smev_metadata,
                'ReferenceMessageID',
                None
            ),
            attachments=self._extract_attachments(msg_content),
        )
        return model.IncomingMessage(
            message=message
        )
