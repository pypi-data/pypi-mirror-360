from urllib.request import Request

from .lib import Base


class TusService(Base):
    """Сервис для работы с файл сервисом."""

    @staticmethod
    def __init_tus_init_header(
            filesize: str,
            filename: str,
            filetype: str,
    ) -> dict:
        """Создание header для инициализации загрузки по TUS.

        :param filesize: Размер файла
        :param filename: Название файла
        :param filetype: MIME тип файла

        :return: dict
        """
        tus_header = {
            'Upload-Length': filesize,
            'Upload-Metadata': f'filename {filename},'
                               f'filetype {filetype}',
            'Tus-Resumable': '1.0.0',
            'Content-Length': '0',
        }
        return tus_header

    @staticmethod
    def __init_tus_chunk_upload_header(chunk_size: str) -> dict:
        """Создание header для продолжения загрузки по TUS.

        :param chunk_size: Чанк для загрузки

        :return: dict
        """
        chunk_header = {
            'Content-Type': 'application/offset+octet-stream',
            'Upload-Offset': '0',
            'Content-Length': chunk_size,
            'Tus-Resumable': '1.0.0',
        }
        return chunk_header

    def init_upload(
            self,
            filesize: str,
            filename: str,
            filetype: str,
    ) -> Request:
        """Инициализация загрузки по TUS.

        :param filesize: Размер файла
        :param filename: Название файла
        :param filetype: MIME тип файла

        :return: Request
        """
        init_header = self.__init_tus_init_header(
            filesize=filesize,
            filename=filename,
            filetype=filetype,
        )
        self.client.session.headers.update(init_header)
        return self._make_request(
            endpoint='elph/store/tus',
            method='POST',
            tus_path=True,
        )

    def upload_chunk(self, chunk: bytes, file_id: str) -> Request:
        """Загрузка чанка по TUS.

        :param chunk: Чанк
        :param file_id: id файла

        :return: Request
        """
        upload_header = self.__init_tus_chunk_upload_header(str(chunk))
        self.client.session.headers.update(upload_header)
        return self._make_request(
            endpoint=f'elph/store/tus/{file_id}',
            payload=chunk,
            method='PATCH',
            tus_path=True,
        )

    def get_upload_status(self, file_id: str) -> Request:
        """Получение статуса загрузки файла по TUS.

        :param file_id: id файла

        :return: Request
        """
        self.client.session.headers.update(
            {
                'Tus-Resumable': '1.0.0',
            },
        )
        return self._make_request(
            endpoint=f'elph/store/tus/{file_id}',
            method='HEAD',
            tus_path=True,
        )
