import io
import logging
import os
import re
import tarfile
import tempfile
from pathlib import Path
from typing import Dict, Optional, List, Tuple, Generator, Any, Union, cast

import docker
from docker.errors import APIError, NotFound, BuildError, ImageNotFound, DockerException
from docker.models.containers import Container
from docker.models.images import Image
from dotenv import dotenv_values
from r00logger import log, log_script
from .helpers.exceptions import *



# Определяем тип вывода для exec_run
ExecOutput = Union[bytes, Generator[bytes, None, None]]
ExecResult = Tuple[Optional[int], ExecOutput] # None для exit_code при detach=True
ExecResultDemux = Tuple[Optional[int], Tuple[bytes, bytes]] # (exit_code, (stdout, stderr)) при demux=True

class DockerClient:
    """
    Клиент для взаимодействия с Docker Engine с использованием Docker SDK.
    Ориентирован на Docker SDK v7.1.0+
    """
    RUNNING_STATUS = 'running'
    EXITED_STATUS = 'exited'

    def __init__(self, image_name='', timeout: int = 60,  **kwargs):
        """
        Инициализирует Docker SDK клиент.

        Args:
            timeout: Таймаут по умолчанию для операций Docker SDK (в секундах).
            **kwargs: Дополнительные аргументы для docker.from_env()
                      (например, base_url, tls, version='auto').
        """
        self.image = image_name
        self.container_name = self.generate_container_name()
        try:
            # Передаем kwargs в from_env, чтобы разрешить base_url, tls и т.д.
            self._client = docker.from_env(timeout=timeout, **kwargs)
            # Проверяем соединение
            self._client.ping()
            api_version = self._client.version().get("ApiVersion", "N/A")
            log.trace(f"Docker SDK клиент успешно инициализирован. API Version: {api_version}")
        except DockerException as e:
            log.error(f"Не удалось инициализировать Docker SDK клиент: {e}")
            raise DockerError(f"Не удалось подключиться к Docker Engine: {e}") from e
        except Exception as e: # Перехват непредвиденных ошибок при инициализации
             log.exception(f"Непредвиденная ошибка при инициализации DockerClient: {e}")
             raise DockerError(f"Непредвиденная ошибка при инициализации DockerClient: {e}") from e

    # --- Приватные хелперы ---
    def _get_container(self) -> Container:
        """Вспомогательный метод для получения объекта контейнера."""
        try:
            # Использование cast для type hinting, т.к. SDK может не иметь идеальных стабов
            container = cast(Container, self._client.containers.get(self.container_name))
            return container
        except NotFound:
            raise ContainerNotFoundError(f"Контейнер '{self.container_name}' не найден.")
        except APIError as e:
            log.error(f"Ошибка API при поиске контейнера {self.container_name}: {e.explanation}")
            raise DockerOperationError(f"Ошибка API при поиске контейнера {self.container_name}: {e.explanation}") from e

    def generate_container_name(self) -> str:
        """
        Генерирует предсказуемое имя контейнера из имени образа Docker.
        Пример: 'r00ft1h/horizon_pie:v2' -> 'r00ft1h_horizon_pie_v2'
        """
        return re.sub(r'[^a-zA-Z0-9]', '_', self.image)

    def get_image(self, name_or_id: str) -> Image:
        """Вспомогательный метод для получения объекта образа."""
        try:
            image = cast(Image, self._client.images.get(name_or_id))
            log.debug(f"Найден образ: {name_or_id}")
            return image
        except:
            log.warning(f"Образ не найден: {name_or_id}")
            return None

    # --- Методы управления контейнерами ---

    def run(self,
            command: Optional[Union[List[str], str]] = None,
            *, # Делаем остальные аргументы именованными
            remove: bool = False,
            detach: bool = True, # Запускаем в фоне по умолчанию
            platform: Optional[str] = None, # Добавлено
            env: Optional[Dict[str, str]] = None,
            volumes: Optional[Dict[str, Dict[str, str]]] = None,
            ports: Optional[Dict[str, Optional[Union[int, Tuple[str, int], List[int]]]]] = None,
            network: Optional[str] = None, # Для подключения к конкретной сети
            network_mode: Optional[str] = None, # Для 'bridge', 'host', 'none', 'container:...'
            force: bool = False,
            entrypoint: Optional[Union[str, List[str]]] = None,
            stdout: bool = True, # Параметры для случая detach=False
            stderr: bool = False,
            stream: bool = False, # Параметры для случая detach=False
            **kwargs: Any # Дополнительные аргументы для client.containers.run
           ) -> Union[Container, bytes, Generator[bytes, None, None]]:
        """
        Запускает новый контейнер. Похож на `docker run`.

        Args:
            command: Команда для выполнения внутри контейнера.
            remove: Удалять ли контейнер после его остановки (`--rm`).
            detach: Запускать ли контейнер в фоновом режиме (`-d`).
            platform: Платформа для запуска (e.g., "linux/amd64").
            env: Словарь переменных окружения.
            volumes: Словарь для монтирования томов (формат SDK).
                     Пример: {'/home/user/data': {'bind': '/data', 'mode': 'rw'}}
            ports: Словарь для проброса портов (формат SDK).
                   Пример: {'80/tcp': 8080, '5432/tcp': ('127.0.0.1', 5432)}
            network: Имя сети для подключения. Несовместимо с network_mode='host'.
            network_mode: 'bridge', 'host', 'none', 'container:<name|id>'. Несовместимо с network.
            force: Принудительно удалить существующий контейнер с таким же именем перед запуском.
            entrypoint: Переопределить ENTRYPOINT образа.
            stdout: Возвращать stdout, если detach=False.
            stderr: Возвращать stderr, если detach=False.
            stream: Возвращать генератор логов, если detach=False.
            kwargs: Дополнительные параметры для `docker.models.containers.ContainerCollection.run`.
                    (например, healthcheck, labels, mounts=[Mount(...)], etc.)

        Returns:
            - Объект контейнера (Container), если detach=True.
            - Строку (bytes) с логами stdout/stderr, если detach=False и stream=False.
            - Генератор логов (bytes), если detach=False и stream=True.

        Raises:
            ContainerNotFoundError: Если `force=True` и не удалось найти/удалить контейнер.
            DockerOperationError: Если произошла ошибка API Docker.
            ImageNotFoundError: Если образ не найден.
            DockerError: Другие ошибки Docker.
        """
        self.remove_container()
        # Чтобы контейнер не завершался сразу в detach режиме, если нет команды
        effective_command = command
        if detach and not command:
             # Используем стандартный трюк, если пользователь не указал команду
             effective_command = ["sleep", "infinity"]
             log.debug("Добавлена команда 'sleep infinity' для предотвращения завершения контейнера в detach режиме.")

        # Проверка конфликта network и network_mode
        if network and network_mode:
            raise DockerError("Параметры 'network' и 'network_mode' не могут использоваться одновременно.")

        try:
            container = self._client.containers.run(# type: ignore
                image=self.image,
                command=effective_command,
                name=self.container_name,
                remove=remove,
                detach=detach,
                platform=platform,
                environment=env,
                volumes=volumes,
                ports=ports,
                network=network,
                network_mode=network_mode,
                entrypoint=entrypoint,
                stdout=stdout,
                stderr=stderr,
                stream=stream,
                **kwargs
            )

            if detach:
                # container здесь - это объект Container
                log.info(f"Контейнер '{container.name}' ({container.short_id}) успешно запущен в detach режиме.")
                return cast(Container, container) # Возвращаем объект контейнера
            else:
                # container здесь - это bytes или generator
                log.debug(f"Контейнер '{self.container_name}' запущен в foreground режиме. Возвращаем вывод/логи.")
                return container # Возвращаем логи (bytes или generator)

        except ImageNotFound as e:
            log.error(f"Образ '{self.image}' не найден.")
            raise ImageNotFoundError(f"Образ '{self.image}' не найден.") from e
        except APIError as e:
            log.error(f"Ошибка API при запуске контейнера из образа '{self.image}': {e.explanation}")
            raise DockerOperationError(f"Ошибка API при запуске контейнера: {e.explanation}") from e
        except Exception as e:
             log.exception(f"Непредвиденная ошибка при запуске контейнера: {e}")
             raise DockerError(f"Непредвиденная ошибка при запуске контейнера: {e}") from e

    def start_container(self) -> None:
        """Запускает остановленный контейнер."""
        try:
            container = self._get_container()
        except:
            log.error(f"Контейнер '{self.container_name}' не найден для запуска.")
            return None
        try:
            container.start()
            log.trace(f"Контейнер '{self.container_name}' запущен.")
        except APIError as e:
            if e.response.status_code == 304: # Not Modified - уже запущен
                log.warning(f"Контейнер '{self.container_name}' уже запущен.")
                return
            log.error(f"Ошибка API при запуске контейнера {self.container_name}: {e.explanation}")
            raise DockerOperationError(f"Ошибка API при запуске контейнера {self.container_name}: {e.explanation}") from e

    def stop_container(self, timeout: int = 1) -> None:
        """Останавливает контейнер (SIGTERM, потом SIGKILL)."""
        try:
            container = self._get_container()
            container.stop(timeout=timeout)
            log.trace(f"Контейнер '{self.container_name}' остановлен.")
        except APIError as e:
            if e.response.status_code == 304:
                 return
            log.error(f"Ошибка API при остановке контейнера {self.container_name}: {e.explanation}")
            raise DockerOperationError(f"Ошибка API при остановке контейнера {self.container_name}: {e.explanation}") from e
        except ContainerNotFoundError:
            return

    def kill_container(self, signal: Optional[Union[str, int]] = None) -> None:
        """Принудительно останавливает контейнер (SIGKILL по умолчанию)."""
        signal_str = signal or 'SIGKILL'
        try:
            container = self._get_container()
            container.kill(signal=signal)
            log.debug(f"Контейнер '{self.container_name}' принудительно остановлен (сигнал: {signal_str}).")
        except APIError as e:
            # Ошибка, если контейнер уже не запущен
            if 'is not running' in str(e.explanation).lower():
                 log.warning(f"Контейнер '{self.container_name}' уже не был запущен.")
                 return
            log.error(f"Ошибка API при принудительной остановке контейнера {self.container_name}: {e.explanation}")
            raise DockerOperationError(f"Ошибка API при принудительной остановке {self.container_name}: {e.explanation}") from e
        except ContainerNotFoundError:
             log.warning(f"Контейнер '{self.container_name}' для принудительной остановки не найден.")
             # Не пробрасываем ошибку

    def remove_container(self, force: bool = True, remove_volume: bool = False) -> None:
        """
        Удаляет контейнер.

        Args:
            force: Принудительно удалить (даже если запущен).
            remove_volume: Удалить анонимные тома, связанные с контейнером (`-v`).
        """
        try:
            container = self._get_container()
            container.remove(force=force, v=remove_volume)
            log.trace(f"Контейнер '{self.container_name}' удален.")
        except ContainerNotFoundError:
             log.warning(f"Контейнер '{self.container_name}' для удаления не найден.")
        except APIError as e:
            if e.response.status_code == 409 and not force:
                 msg = f"Не удалось удалить контейнер '{self.container_name}', т.к. он запущен. Используйте force=True."
                 log.error(msg)
                 raise DockerOperationError(msg) from e
            elif e.response.status_code == 404:
                 log.warning(f"Контейнер '{self.container_name}' не найден при попытке удаления (возможно, уже удален).")
            else:
                log.error(f"Ошибка API при удалении контейнера {self.container_name}: {e.explanation}")
                raise DockerOperationError(f"Ошибка API при удалении контейнера {self.container_name}: {e.explanation}") from e

    def list_containers(self, all: bool = True, filters: Optional[Dict[str, str]] = None, **kwargs) -> List[Container]:
        """
        Возвращает список контейнеров. Аналог `docker ps`.

        Args:
            all: Показывать все контейнеры (включая остановленные). По умолчанию True.
            filters: Фильтры (см. документацию Docker API / `docker ps --filter`).
            **kwargs: Дополнительные параметры для `client.containers.list`.

        Returns:
            Список объектов Container.
        """
        log.trace(f"Получение списка контейнеров (all={all}, filters={filters})...")
        try:
            containers = self._client.containers.list(all=all, filters=filters, **kwargs)
            log.trace(f"Найдено контейнеров: {len(containers)}")
            # Убедимся, что возвращаем список Container
            return cast(List[Container], containers)
        except APIError as e:
            log.error(f"Ошибка API при получении списка контейнеров: {e.explanation}")
            raise DockerOperationError(f"Ошибка API при получении списка контейнеров: {e.explanation}") from e

    def get_container_status(self) -> str:
        """Возвращает статус контейнера ('created', 'running', 'paused', 'restarting', 'removing', 'exited', 'dead')."""
        container = self._get_container()
        try:
            container.reload() # Обновляем состояние
            log.trace(f"Статус контейнера {self.container_name}: {container.status}")
            return container.status
        except APIError as e:
            log.error(f"Ошибка API при получении статуса {self.container_name}: {e.explanation}")
            raise DockerOperationError(f"Ошибка API при получении статуса {self.container_name}: {e.explanation}") from e

    def get_container_health(self) -> Optional[str]:
         """
         Возвращает статус healthcheck контейнера, если он определен.
         Возможные значения: 'starting', 'healthy', 'unhealthy', None.
         """
         log.trace(f"Получение статуса healthcheck для контейнера {self.container_name}...")
         try:
            info = self.get_container_info(self.container_name)
            health_status = info.get("State", {}).get("Health", {}).get("Status")
            log.debug(f"Статус healthcheck для {self.container_name}: {health_status}")
            return health_status
         except DockerError as e:
              log.error(f"Не удалось получить информацию о healthcheck для {self.container_name}: {e}")
              return None # Возвращаем None при ошибке получения информации

    def is_container_running(self) -> bool:
        """Проверяет, запущен ли контейнер."""
        try:
            return self.get_container_status() == self.RUNNING_STATUS
        except ContainerNotFoundError:
            return False # Если не найден, точно не запущен

    def exec_run(self,
                 command: Union[str, List[str]],
                 *, # Именованные аргументы
                 stdout: bool = True,
                 stderr: bool = True,
                 stdin: bool = False, # Добавлено для полноты
                 tty: bool = False,
                 privileged: bool = False,
                 user: str = '',
                 detach: bool = False,
                 stream: bool = False,
                 socket: bool = False, # Добавлено для полноты
                 demux: bool = False, # Добавлено
                 environment: Optional[Union[Dict[str, str], List[str]]] = None,
                 workdir: Optional[str] = None,
                 **kwargs: Any
                ) -> Union[ExecResult, ExecResultDemux]:
        """
        Выполняет команду внутри запущенного контейнера. Аналог `docker exec`.

        Args:
            command: Команда для выполнения (строка или список строк).
            stdout: Включить stdout в вывод.
            stderr: Включить stderr в вывод.
            stdin: Присоединить stdin.
            tty: Аллоцировать псевдо-TTY.
            privileged: Запустить команду с привилегиями.
            user: Пользователь для выполнения команды.
            detach: Запустить команду в фоне (результат и код выхода будут недоступны).
            stream: Возвращать генератор для потокового вывода.
            socket: Возвращать сокет соединения (взаимоисключающий со stream).
            demux: Разделять stdout и stderr (только если stream=False и socket=False).
            environment: Переменные окружения для команды.
            workdir: Рабочая директория внутри контейнера.
            kwargs: Дополнительные аргументы для `container.exec_run`.

        Returns:
            - Если detach=True: (None, None)
            - Если demux=True: Кортеж (exit_code, (stdout_bytes, stderr_bytes))
            - Иначе: Кортеж (exit_code, output), где output - bytes (если stream=False, socket=False)
                      или generator (если stream=True) или socket (если socket=True).

        Raises:
            ContainerNotFoundError: Если контейнер не найден.
            DockerOperationError: Если контейнер не запущен или произошла ошибка API.
        """
        cmd_str = command if isinstance(command, str) else ' '.join(command)
        container = self._get_container()
        if container.status != self.RUNNING_STATUS:
            msg = f"Контейнер '{self.container_name}' не запущен (статус: {container.status}). Невозможно выполнить команду."
            log.error(msg)
            raise DockerOperationError(msg)

        if stream and socket:
             raise ValueError("Параметры 'stream' и 'socket' не могут быть True одновременно.")

        try:
            # container.exec_run возвращает кортеж (exit_code, output)
            # output зависит от stream, socket, demux
            exec_result = container.exec_run(
                cmd=command,
                stdout=stdout,
                stderr=stderr,
                stdin=stdin,
                tty=tty,
                privileged=privileged,
                user=user,
                detach=detach,
                stream=stream,
                socket=socket,
                environment=environment,
                workdir=workdir,
                demux=demux,
                **kwargs
            )

            if detach:
                log.trace(f"Команда запущена в detach режиме для {self.container_name}.")
                # В документации SDK не указано, что возвращается ID, просто (None, None)
                return None, None
            else:
                 # exec_result здесь - это кортеж (exit_code, output)
                 exit_code, output = exec_result
                 return exit_code, output.decode('utf-8', errors='replace') if isinstance(output, bytes) else output

        except APIError as e:
            log.error(f"Ошибка API при выполнении команды в {self.container_name}: {e.explanation}")
            raise DockerOperationError(f"Ошибка API при выполнении команды в {self.container_name}: {e.explanation}") from e
        except Exception as e: # Ловим другие возможные ошибки
             log.exception(f"Непредвиденная ошибка при выполнении команды в {self.container_name}: {e}")
             raise DockerError(f"Непредвиденная ошибка при выполнении команды в {self.container_name}: {e}") from e

    def exec_script_in_container(self,
                                 script_content: str,
                                 script_name: str = "temp_script.sh",
                                 shell: str = '/bin/sh', # Можно указать shell
                                 workdir: Optional[str] = None,
                                 user: str = '',
                                 remove_script: bool = True
                                ) -> Tuple[int, bytes]:
        """
        Копирует скрипт в контейнер и выполняет его с помощью указанной оболочки.

        Args:
            script_content: Содержимое скрипта (строка).
            script_name: Имя файла для скрипта внутри контейнера (в /tmp/).
            shell: Путь к оболочке для выполнения скрипта (e.g., '/bin/bash', '/bin/sh').
            workdir: Рабочая директория для выполнения скрипта.
            user: Пользователь для выполнения скрипта.
            remove_script: Удалять ли скрипт после выполнения.

        Returns:
            Кортеж (exit_code, output_bytes) результата выполнения скрипта.

        Raises:
            DockerOperationError: Если не удалось скопировать или выполнить скрипт.
        """
        container_script_path = f"/tmp/{script_name}"
        temp_host_file = None
        try:
            # Используем NamedTemporaryFile для автоматического удаления при ошибке/завершении
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".sh", encoding='utf-8') as tmp_script:
                tmp_script.write(script_content)
                temp_host_file = tmp_script.name

            self.copy_to_container(temp_host_file, container_script_path)
            content_script = Path(temp_host_file).read_text(encoding='utf-8')

            # Выполняем скрипт через shell
            # Передаем путь к скрипту как аргумент shell'у
            log.trace(f"Выполнение скрипта в контейнере:\n{content_script}")
            exec_exit_code, exec_output_gen = self.exec_run(
                [shell, container_script_path],
                user=user,
                workdir=workdir,
                stream=False # Получаем весь вывод сразу
            )

            # exec_output_gen здесь - это bytes, т.к. stream=False
            exec_output = cast(bytes, exec_output_gen)
            output = exec_output.decode("utf-8", errors="replace") if isinstance(exec_output, bytes) else exec_output

            log.trace(f"Скрипт {container_script_path} выполнен в контейнере через {shell} с кодом: {exec_exit_code}")
            return exec_exit_code, output

        except Exception as e:
            log.error(f"Ошибка выполнения скрипта в контейнере {self.container_name}: {e}")
            # Оборачиваем в наше исключение
            raise DockerOperationError(f"Ошибка выполнения скрипта в контейнере {self.container_name}: {e}") from e
        finally:
            # Удаляем скрипт из контейнера, если нужно
            if remove_script:
                try:
                    # Используем try-except, т.к. контейнер мог быть удален
                    rm_exit_code, _ = self.exec_run(f"rm -f {container_script_path}", user=user)
                    if rm_exit_code != 0:
                         log.warning(f"Не удалось удалить временный скрипт {container_script_path} из контейнера (код: {rm_exit_code}).")
                except (DockerError, ContainerNotFoundError) as e_rm: # Ловим наши исключения
                    log.warning(f"Ошибка при попытке удаления скрипта {container_script_path} (возможно, контейнер уже удален): {e_rm}")
                except Exception as e_rm_unexp: # Другие ошибки
                     log.warning(f"Непредвиденная ошибка при удалении скрипта {container_script_path}: {e_rm_unexp}")
            # Удаляем временный файл с хоста
            if temp_host_file and os.path.exists(temp_host_file):
                try:
                    os.remove(temp_host_file)
                except OSError as e_os:
                    log.warning(f"Не удалось удалить временный файл {temp_host_file} с хоста: {e_os}")


    def copy_to_container(self, host_path: str,  container_path: str) -> None:
        """
        Копирует файл или директорию с хоста в контейнер.

        Args:
            host_path: Путь к файлу или директории на хосте.
            container_path: Путь назначения в контейнере.
                            - Если заканчивается на '/', считается директорией назначения.
                            - Иначе считается полным путем к файлу назначения.

        Raises:
            FileNotFoundError: Если host_path не существует.
            ContainerNotFoundError: Если контейнер не найден.
            DockerOperationError: Если произошла ошибка API Docker или IO.
        """
        host_path = str(host_path)
        container_path = str(container_path)

        if not os.path.exists(host_path):
            raise FileNotFoundError(f"Путь на хосте не найден: {host_path}")

        container = self._get_container()

        # Определяем имя файла/директории, которое будет в архиве
        basename = os.path.basename(host_path)
        is_dir = os.path.isdir(host_path)

        # Определяем директорию назначения внутри контейнера
        if container_path.endswith('/'):
            container_dest_dir = container_path
            container_dest_filename = os.path.join(container_dest_dir, basename) # Куда попадет файл/папка
        else:
            container_dest_dir = os.path.dirname(container_path)
            container_dest_filename = container_path # Полный путь назначения файла

        # Создаем TAR-архив в памяти
        tar_stream = io.BytesIO()
        try:
            with tarfile.open(fileobj=tar_stream, mode='w') as tar:
                # Добавляем файл/директорию в корень архива с его оригинальным именем
                tar.add(host_path, arcname=basename)
        except Exception as e:
             log.exception(f"Ошибка создания tar-архива для {host_path}: {e}")
             raise DockerOperationError(f"Ошибка создания tar-архива: {e}") from e
        tar_stream.seek(0)

        try:
            # put_archive копирует содержимое архива (файл/папку с именем `basename`)
            # в директорию `container_dest_dir`
            success = container.put_archive(container_dest_dir, tar_stream)

            if not success:
                 # Теоретически, API может вернуть False без исключения
                 raise DockerOperationError(f"Docker API сообщил о неудаче при копировании в {self.container_name}:{container_dest_dir} (put_archive вернул False)")

            path_after_put = os.path.join(container_dest_dir, basename)

            # Переименовываем только если не копировали директорию и
            # имя файла назначения не совпадает с тем, что получилось после put_archive
            if not is_dir and not container_path.endswith('/') and path_after_put != container_dest_filename:
                # Используем exec_run для переименования
                # Учитываем, что container_dest_dir может быть корневым "/"
                if container_dest_dir == "/": path_after_put = "/" + basename

                mv_code, mv_out = self.exec_run(['mv', path_after_put, container_dest_filename])
                if mv_code != 0:
                    err_msg = f"Не удалось переименовать скопированный файл: код {mv_code}, вывод: {mv_out.decode(errors='ignore') if isinstance(mv_out, bytes) else mv_out}"
                    log.error(err_msg)
                    # Попытаться удалить скопированный файл? Сложно надежно реализовать.
                    raise DockerOperationError(err_msg)

            log.trace(f"Файл '{host_path}' скопирован в контейнер {container_path}")


        except APIError as e:
            # Проверяем, не связана ли ошибка с отсутствием директории
            explanation = str(e.explanation).lower()
            if 'no such file or directory' in explanation or 'not a directory' in explanation:
                 log.error(f"Ошибка API при копировании в {self.container_name}: возможно, директория '{container_dest_dir}' не существует в контейнере.")
                 raise DockerOperationError(f"Ошибка API: директория '{container_dest_dir}' не существует в контейнере {self.container_name}.") from e
            else:
                log.error(f"Ошибка API при копировании в {self.container_name}:{container_path}: {e.explanation}")
                raise DockerOperationError(f"Ошибка API при копировании в {self.container_name}:{container_path}: {e.explanation}") from e
        except Exception as e:
             log.exception(f"Непредвиденная ошибка при копировании в контейнер {self.container_name}: {e}")
             raise DockerError(f"Непредвиденная ошибка при копировании в контейнер {self.container_name}: {e}") from e

    def copy_from_container(self, container_path: str, host_path: str) -> str:
        """
        Копирует файл или директорию из контейнера на хост.
        :param container_path: Путь к файлу в контейнере.
        :param host_path: Путь к файлу на хосте
        :return: Путь на хосте
        """
        container = self._get_container()
        container_path = str(container_path)
        host_path = str(host_path)

        try:
            bits, stat = container.get_archive(container_path)
            container_resource_name = stat['name'] # Имя файла/папки внутри архива
            host_dest_dir: str
            rename_to: Optional[str] = None

            if os.path.exists(host_path) and os.path.isdir(host_path):
                # Копируем внутрь существующей директории
                host_dest_dir = host_path
            elif not os.path.exists(host_path) and host_path.endswith(os.sep):
                 # Копируем в новую директорию (создадим)
                 host_dest_dir = host_path
            else:
                 # Копируем и переименовываем (или создаем файл/папку с таким именем)
                 host_dest_dir = os.path.dirname(host_path)
                 rename_to = host_path # Полный путь назначения

            # Создаем директорию назначения на хосте, если её нет
            if host_dest_dir and not os.path.exists(host_dest_dir):
                os.makedirs(host_dest_dir, exist_ok=True)
            elif not host_dest_dir: # Если копируем в текущую директорию
                 host_dest_dir = "."

            # Распаковываем TAR архив из потока
            tar_stream = io.BytesIO()
            for chunk in bits:
                tar_stream.write(chunk)
            tar_stream.seek(0)

            extracted_path = os.path.join(host_dest_dir, container_resource_name)

            with tarfile.open(fileobj=tar_stream) as tar:
                tar.extractall(path=host_dest_dir)

            # Переименовываем, если нужно
            if rename_to and os.path.normpath(extracted_path) != os.path.normpath(rename_to):
                if os.path.exists(rename_to): # Удаляем существующий файл/папку перед переименованием
                     if os.path.isdir(rename_to):
                         import shutil
                         shutil.rmtree(rename_to)
                     else:
                         os.remove(rename_to)
                os.rename(extracted_path, rename_to)
            log.trace(f"Файл '{container_resource_name}' скопирован в '{rename_to or extracted_path}'.")
            return rename_to or extracted_path

        except NotFound as e:
             log.error(f"Путь не найден в контейнере {self.container_name}: {container_path}")
             raise DockerOperationError(f"Путь не найден в контейнере {self.container_name}: {container_path}") from e
        except APIError as e:
            log.error(f"Ошибка API при копировании из {self.container_name}:{container_path}: {e.explanation}")
            raise DockerOperationError(f"Ошибка API при копировании из {self.container_name}:{container_path}: {e.explanation}") from e
        except (OSError, tarfile.TarError, FileExistsError) as e:
             log.exception(f"Ошибка IO/архива/файловой системы при копировании из {self.container_name} в {host_path}: {e}")
             raise DockerOperationError(f"Ошибка IO/архива/файловой системы при копировании из {self.container_name}: {e}") from e

    # --- Методы управления образами ---

    def commit_container(self,
                         name_or_id: str,
                         repository: Optional[str] = None,
                         tag: Optional[str] = None,
                         message: Optional[str] = None,
                         author: Optional[str] = None,
                         pause: bool = True, # Добавлено в SDK
                         changes: Optional[str] = None,
                         conf: Optional[Dict[str, Any]] = None
                         ) -> Image:
        """
        Создает новый образ из изменений контейнера. Аналог `docker commit`.

        Args:
            name_or_id: Имя или ID контейнера.
            repository: Имя репозитория для образа.
            tag: Тег для образа (по умолчанию 'latest', если указан repository).
            message: Сообщение коммита.
            author: Автор образа.
            pause: Приостановить контейнер перед коммитом (по умолчанию True).
            changes: Dockerfile инструкции для применения при коммите (например, "CMD /bin/bash").
            conf: Конфигурация Docker для образа.

        Returns:
            Объект созданного образа (`docker.models.images.Image`).

        Raises:
            ContainerNotFoundError: Если контейнер не найден.
            DockerOperationError: Если произошла ошибка API Docker.
        """
        log.trace(f"Создание образа из контейнера {name_or_id} (репозиторий: {repository}, тег: {tag})...")
        container = self._get_container(name_or_id)
        try:
            # SDK использует commit на объекте Container
            image = container.commit(
                repository=repository,
                tag=tag,
                message=message,
                author=author,
                pause=pause,
                changes=changes,
                conf=conf
            )
            log.debug(f"Образ {image.tags[0] if image.tags else image.short_id} успешно создан.")
            return cast(Image, image)
        except APIError as e:
            log.error(f"Ошибка API при создании образа из {name_or_id}: {e.explanation}")
            raise DockerOperationError(f"Ошибка API при создании образа из {name_or_id}: {e.explanation}") from e

    def login_to_registry(self, username: Optional[str] = None, password: Optional[str] = None, registry: Optional[str] = None, email: Optional[str] = None, reauth: bool = False, dockercfg_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Аутентифицируется в Docker реестре. Аналог `docker login`.

        Args:
            username: Имя пользователя.
            password: Пароль или токен доступа.
            registry: URL реестра (по умолчанию Docker Hub).
            email: Email (устарело, но может требоваться некоторыми реестрами).
            reauth: Принудительно повторить аутентификацию.
            dockercfg_path: Путь к кастомному файлу конфигурации Docker.

        Returns:
            Словарь с результатом от API Docker.

        Raises:
            DockerAuthenticationError: Если аутентификация не удалась.
            DockerOperationError: Другие ошибки API.
        """
        reg_str = f"'{registry}'" if registry else 'Docker Hub'
        user_str = f"'{username}'" if username else 'анонимно'
        try:
            # Используем метод login самого клиента SDK
            result = self._client.login(
                username=username,
                password=password,
                email=email,
                registry=registry,
                reauth=reauth,
                dockercfg_path=dockercfg_path
            )
            log.trace(f"Аутентификация в {reg_str} успешна (Status: {result.get('Status')}).")
            # SDK v7 возвращает Dict[str, str], но старые могли иначе
            return cast(Dict[str, Any], result)
        except APIError as e:
            log.error(f"Ошибка API при аутентификации: {e.explanation}")
            # Проверяем типичные сообщения об ошибках аутентификации
            if e.response.status_code == 401 or 'denied' in str(e.explanation).lower() or 'unauthorized' in str(e.explanation).lower():
                 raise DockerAuthenticationError(f"Ошибка аутентификации: {e.explanation}") from e
            else:
                raise DockerOperationError(f"Ошибка API при аутентификации: {e.explanation}") from e

    def push_image(self,
                   repository: str,
                   tag: Optional[str] = None,
                   stream: bool = True,
                   decode: bool = True, # Декодируем JSON по умолчанию
                   auth_config: Optional[Dict[str, str]] = None
                  ) -> Union[Generator[Dict[str, Any], None, None], str]:
        """
        Отправляет образ в реестр. Аналог `docker push`.
        Требует предварительной аутентификации через `login_to_registry` или наличия `auth_config`.

        Args:
            repository: Имя репозитория (может включать URL реестра).
            tag: Тег образа для отправки (если None, отправляются все теги репозитория).
            stream: Возвращать генератор с прогрессом отправки (по умолчанию True).
            decode: Декодировать JSON из потока (по умолчанию True, требует stream=True).
            auth_config: Словарь с данными для аутентификации (см. документацию Docker SDK).

        Returns:
            Генератор словарей с прогрессом (если stream=True) или строка с полным выводом.

        Raises:
            ImageNotFoundError: Если образ не найден локально.
            DockerAuthenticationError: Если ошибка аутентификации.
            DockerOperationError: Если произошла другая ошибка API.
        """
        full_image_name = f"{repository}:{tag}" if tag else repository
        log.trace(f"Отправка образа '{full_image_name}' в реестр...")
        try:
            # Используем images.push
            push_output = self._client.images.push(
                repository=repository,
                tag=tag,
                stream=stream,
                auth_config=auth_config,
                decode=decode
            )
            log.debug(f"Отправка образа '{full_image_name}' начата/завершена.")
            # Возвращаем как есть (генератор или строку)
            return cast(Union[Generator[Dict[str, Any], None, None], str], push_output)
        except APIError as e:
             log.error(f"Ошибка API при отправке образа '{full_image_name}': {e.explanation}")
             # Проверка на ошибки, связанные с отсутствием образа или аутентификацией
             if e.response.status_code == 404:
                 raise ImageNotFoundError(f"Образ '{full_image_name}' не найден локально для отправки.") from e
             elif e.response.status_code == 401 or 'denied' in str(e.explanation).lower():
                 raise DockerAuthenticationError(f"Ошибка аутентификации при отправке образа: {e.explanation}") from e
             else:
                raise DockerOperationError(f"Ошибка API при отправке образа '{full_image_name}': {e.explanation}") from e

    def pull_image(
            self,
            repository: str,
            tag: Optional[str] = None,
            platform: Optional[str] = None,
            all_tags: bool = False,
            ) -> Union[Image, List[Image]]:
        """
        Загружает образ из реестра. Аналог `docker pull`.

        Args:
            repository: Имя репозитория.
            tag: Тег (по умолчанию 'latest').
            platform: Платформа для загрузки ('linux/amd64').
            all_tags: Загрузить все теги для репозитория (игнорирует tag).

        Returns:
            Объект Image (если all_tags=False) или список объектов Image (если all_tags=True).

        Raises:
            ImageNotFoundError: Если образ/тег не найден в реестре.
            DockerOperationError: Если произошла другая ошибка API.
            NotFound: Может быть выброшено при ошибке 404 от API.
        """
        pull_target = f"{repository}:{tag or 'latest'}" if not all_tags else repository
        log.trace(f"Загрузка образа '{pull_target}' (all_tags={all_tags}, platform={platform or 'default'})...")

        try:
            # Высокоуровневый images.pull уже обрабатывает поток и возвращает Image или List[Image]
            pulled_object = self._client.images.pull(
                repository=repository,
                tag=tag,
                platform=platform,
                all_tags=all_tags,
            )

            # Проверка типа возвращаемого объекта и логирование
            if isinstance(pulled_object, list):
                log.debug(f"Загружено {len(pulled_object)} тегов для репозитория '{repository}'.")
            elif isinstance(pulled_object, Image):
                log.debug(f"Образ '{pull_target}' ({pulled_object.short_id}) успешно загружен.")
            else:
                log.warning(
                    f"Загрузка образа '{pull_target}' завершена, но тип результата не Image или List[Image]: {type(pulled_object)}")

            return pulled_object

        except NotFound as e:  # API может вернуть 404 как NotFound
            log.error(f"Образ '{pull_target}' не найден в реестре или произошла ошибка при загрузке (NotFound).")
            raise ImageNotFoundError(f"Образ '{pull_target}' не найден в реестре.") from e
        except APIError as e:
            log.error(f"Ошибка API при загрузке образа '{pull_target}': {e.explanation}")
            if e.response.status_code == 404:
                raise ImageNotFoundError(f"Образ '{pull_target}' не найден в реестре.") from e
            raise DockerOperationError(f"Ошибка API при загрузке образа '{pull_target}': {e.explanation}") from e
        except Exception as e:  # Ловим другие возможные ошибки
            log.exception(f"Непредвиденная ошибка при загрузке образа {pull_target}: {e}")
            raise DockerError(f"Непредвиденная ошибка при загрузке образа {pull_target}: {e}") from e

    def build_image(self,
                    *, # Только именованные аргументы
                    path: Optional[str] = None,
                    fileobj: Optional[Any] = None, # File-like object
                    tag: Optional[str] = None,
                    quiet: bool = False,
                    nocache: bool = False,
                    rm: bool = True, # Удалять промежуточные контейнеры по умолчанию
                    timeout: Optional[int] = None,
                    custom_context: bool = False,
                    gzip: bool = False,
                    dockerfile: str = 'Dockerfile',
                    pull: bool = False, # Пытаться обновить базовые образы
                    forcerm: bool = False,
                    buildargs: Optional[Dict[str, str]] = None,
                    container_limits: Optional[Dict[str, Any]] = None,
                    shmsize: Optional[int] = None,
                    labels: Optional[Dict[str, str]] = None,
                    cache_from: Optional[List[str]] = None,
                    target: Optional[str] = None,
                    network_mode: Optional[str] = None,
                    squash: Optional[bool] = None, # Добавлено
                    extra_hosts: Optional[Dict[str, str]] = None, # Добавлено
                    platform: Optional[str] = None, # Добавлено
                    isolation: Optional[str] = None, # Добавлено
                    use_config_proxy: bool = True,
                    stream_logs: bool = True, # Управляет возвратом генератора логов
                    decode_logs: bool = True # Декодировать JSON в логах
                   ) -> Tuple[Optional[Image], Optional[Generator[Dict[str, Any], None, None]]]:
        """
        Собирает Docker образ. Аналог `docker build`.

        Args:
            path: Путь к директории с контекстом сборки (содержит Dockerfile).
            fileobj: Файловый объект с Dockerfile (вместо path).
            tag: Тег для нового образа (например, 'myimage:latest').
            quiet: Подавлять вывод сборки.
            nocache: Не использовать кеш при сборке.
            rm: Удалять промежуточные контейнеры после сборки (по умолчанию True).
            timeout: Таймаут HTTP запроса.
            custom_context: True, если fileobj содержит весь tar-контекст.
            gzip: True, если fileobj/контекст сжат gzip.
            dockerfile: Имя Dockerfile относительно path.
            pull: Пытаться загрузить более новые версии базовых образов.
            forcerm: Всегда удалять промежуточные контейнеры.
            buildargs: Аргументы сборки (ARG в Dockerfile).
            container_limits: Ограничения ресурсов для контейнеров сборки.
            shmsize: Размер /dev/shm для контейнеров сборки (в байтах).
            labels: Метки для результирующего образа.
            cache_from: Список образов для кеша сборки.
            target: Целевая стадия сборки (для multi-stage).
            network_mode: Сетевой режим для команд RUN во время сборки.
            squash: "Сплющить" слои в один.
            extra_hosts: Дополнительные записи /etc/hosts для контейнеров сборки.
            platform: Целевая платформа сборки ('linux/amd64').
            isolation: Технология изоляции (для Windows).
            use_config_proxy: Использовать настройки прокси из конфига Docker.
            stream_logs: Возвращать генератор логов сборки (по умолчанию True).
            decode_logs: Декодировать JSON из логов (требует stream_logs=True).

        Returns:
            Кортеж (Image | None, logs_generator | None).
            - Image: объект собранного образа (если успешно). None при ошибке.
            - logs_generator: генератор логов сборки (если stream_logs=True). None иначе.

        Raises:
            DockerOperationError: Если произошла ошибка API или сборки.
            FileNotFoundError: Если Dockerfile или путь не найдены (когда используется path).
            TypeError: Если не указан ни path, ни fileobj.
        """
        log.trace(f"Запрос на сборку образа (тег: {tag or 'не указан'})...")

        if not path and not fileobj:
             raise TypeError("Необходимо указать 'path' или 'fileobj' для сборки.")

        # Проверка существования пути и Dockerfile, если не используется fileobj
        if path and not fileobj and not custom_context:
            if not os.path.isdir(path):
                 raise FileNotFoundError(f"Директория контекста сборки не найдена: {path}")
            dockerfile_path = os.path.join(path, dockerfile)
            if not os.path.isfile(dockerfile_path):
                raise FileNotFoundError(f"Dockerfile не найден: {dockerfile_path}")

        image: Optional[Image] = None
        log_generator: Optional[Generator[Dict[str, Any], None, None]] = None

        try:
            # SDK images.build возвращает генератор логов И объект образа (если успешно)
            # Переименовал decode -> decode_logs для ясности
            response_generator = self._client.images.build(
                path=path,
                fileobj=fileobj,
                tag=tag,
                quiet=quiet,
                nocache=nocache,
                rm=rm,
                timeout=timeout,
                custom_context=custom_context,
                encoding='gzip' if gzip else None, # encoding ожидает строку
                pull=pull,
                forcerm=forcerm,
                dockerfile=dockerfile,
                buildargs=buildargs,
                container_limits=container_limits,
                shmsize=shmsize,
                labels=labels,
                cache_from=cache_from,
                target=target,
                network_mode=network_mode,
                squash=squash,
                extra_hosts=extra_hosts,
                platform=platform,
                isolation=isolation,
                use_config_proxy=use_config_proxy,
                decode=decode_logs # Передаем наш параметр
            )

            # Обрабатываем генератор, чтобы получить image_id и логи
            image_id = None
            processed_logs = []

            def log_processor() -> Generator[Dict[str, Any], None, None]:
                nonlocal image_id
                for chunk in response_generator:
                    # chunk уже декодирован, если decode_logs=True
                    log_entry = chunk if isinstance(chunk, dict) else {} # Безопасность
                    # Ищем ID образа в логах
                    if 'stream' in log_entry and 'Successfully built' in log_entry['stream']:
                        parts = log_entry['stream'].strip().split()
                        if len(parts) > 2:
                            potential_id = parts[2]
                            # Простая проверка на hex-подобную строку
                            if all(c in '0123456789abcdef' for c in potential_id):
                                 image_id = potential_id # Сохраняем ID
                                 log.trace(f"Обнаружен ID собранного образа: {image_id}")
                    # Можно делать yield chunk здесь, если нужен стриминг логов наружу
                    if stream_logs:
                         yield log_entry
                    else:
                         processed_logs.append(log_entry) # Сохраняем, если не стримим

            # Запускаем обработку генератора
            if stream_logs:
                 log_generator = log_processor() # Возвращаем генератор
                 # Примечание: image будет None, пока генератор не будет полностью потреблен
                 # Это ограничение SDK (или асинхронной природы сборки).
                 # Вызывающий код должен обработать генератор, чтобы сборка завершилась.
                 # Мы не можем получить Image здесь, не заблокировав выполнение.
                 log.debug("Сборка образа: Возвращен генератор логов. Объект Image будет доступен после его обработки.")
            else:
                 # Потребляем генератор полностью, чтобы сборка завершилась
                 for _ in log_processor():
                     pass
                 # Теперь image_id должен быть установлен (если сборка успешна)
                 if image_id:
                     try:
                         image = self.get_image(image_id)
                         log.info(f"Сборка образа '{tag or image.short_id}' успешно завершена.")
                     except ImageNotFoundError:
                         log.error(f"Сборка завершена, но не удалось найти образ с ID {image_id}.")
                 else:
                      log.error("Сборка завершена, но не удалось извлечь ID образа из логов.")

            # Возвращаем (возможно None, Image) и (возможно None, генератор)
            return image, log_generator

        except BuildError as e:
             log.error(f"Ошибка сборки образа: {e.msg}")
             # Можно попытаться извлечь логи из e.build_log, если нужно
             # raise DockerOperationError(f"Ошибка сборки образа: {e.msg}\nЛог: {e.build_log}") from e
             raise DockerOperationError(f"Ошибка сборки образа: {e.msg}") from e
        except APIError as e:
             log.error(f"Ошибка API при сборке образа: {e.explanation}")
             raise DockerOperationError(f"Ошибка API при сборке образа: {e.explanation}") from e
        except TypeError as e:
             # Может возникнуть, если fileobj используется вместе с path
             log.error(f"Ошибка TypeError при вызове build (проверьте аргументы path/fileobj): {e}")
             raise DockerOperationError(f"Ошибка TypeError при вызове build: {e}") from e
        except FileNotFoundError as e: # Пробрасываем FileNotFoundError
             log.error(f"Ошибка пути при сборке: {e}")
             raise e
        except Exception as e:
             log.exception(f"Непредвиденная ошибка при сборке образа: {e}")
             raise DockerError(f"Непредвиденная ошибка при сборке образа: {e}") from e

    def remove_image(self, name_or_id: str, force: bool = False, noprune: bool = False) -> None:
        """
        Удаляет образ. Аналог `docker rmi`.

        Args:
            name_or_id: Имя (с тегом) или ID образа.
            force: Принудительное удаление (даже если используется контейнерами).
            noprune: Не удалять родительские слои без тегов.

        Raises:
            ImageNotFoundError: Если образ не найден.
            DockerOperationError: Если произошла ошибка API (например, образ используется).
        """
        log.trace(f"Запрос на удаление образа: {name_or_id} (force={force}, noprune={noprune})")
        try:
            # Используем client.images.remove
            self._client.images.remove(image=name_or_id, force=force, noprune=noprune)
            log.debug(f"Образ '{name_or_id}' успешно удален.")
        except ImageNotFound:
            log.warning(f"Образ '{name_or_id}' для удаления не найден.")
            raise ImageNotFoundError(f"Образ '{name_or_id}' не найден.") # Пробрасываем
        except APIError as e:
            # 409 Conflict обычно означает, что образ используется
            if e.response.status_code == 409:
                 log.error(f"Не удалось удалить образ '{name_or_id}', так как он используется контейнером(ами). Используйте force=True для принудительного удаления.")
                 raise DockerOperationError(f"Образ '{name_or_id}' используется контейнером(ами).", status_code=409) from e
            # 404 может быть возвращен, если имя некорректно или уже удален
            elif e.response.status_code == 404:
                 log.warning(f"Образ '{name_or_id}' не найден при попытке удаления.")
                 raise ImageNotFoundError(f"Образ '{name_or_id}' не найден.") from e
            else:
                log.error(f"Ошибка API при удалении образа {name_or_id}: {e.explanation}")
                raise DockerOperationError(f"Ошибка API при удалении образа {name_or_id}: {e.explanation}") from e

    def list_images(self, name: Optional[str] = None, all: bool = False, filters: Optional[Dict[str, Union[str, bool]]] = None) -> List[Image]:
        """
        Возвращает список образов. Аналог `docker images`.

        Args:
            name: Фильтр по имени репозитория (может включать тег).
            all: Показывать промежуточные слои (по умолчанию False).
            filters: Фильтры (dangling=True/False, label="key=value", etc.).

        Returns:
            Список объектов Image.
        """
        log.trace(f"Получение списка образов (name={name}, all={all}, filters={filters})...")
        try:
            images = self._client.images.list(name=name, all=all, filters=filters)
            log.debug(f"Найдено образов: {len(images)}")
            return cast(List[Image], images)
        except APIError as e:
            log.error(f"Ошибка API при получении списка образов: {e.explanation}")
            raise DockerOperationError(f"Ошибка API при получении списка образов: {e.explanation}") from e

    def load_image(self, data: bytes) -> List[Image]:
         """
         Загружает образ из tar-архива (переданного как bytes). Аналог `docker load`.

         Args:
             data: Бинарные данные tar-архива образа.

         Returns:
             Список загруженных образов (обычно один).

         Raises:
             DockerOperationError: Если произошла ошибка API.
         """
         log.trace("Загрузка образа из данных...")
         try:
             # Возвращает генератор, который нужно потребить. SDK 7.0+ упростил это.
             loaded_images_info = self._client.images.load(data)
             # В SDK 7.0+ load возвращает список словарей с 'loadedImage'
             # Но для совместимости и ясности, получим реальные объекты Image
             loaded_image_names = []
             if isinstance(loaded_images_info, list): # Проверка на новый формат
                 for item in loaded_images_info:
                      if isinstance(item, dict) and 'loadedImage' in item:
                           loaded_image_names.append(item['loadedImage'])
             elif hasattr(loaded_images_info, '__iter__'): # Обработка старого генератора логов
                  # Потребляем генератор и ищем 'Loaded image:'
                  for line in loaded_images_info:
                      if isinstance(line, dict) and 'stream' in line:
                           s = line['stream']
                           if 'Loaded image:' in s:
                               parts = s.strip().split('Loaded image: ')
                               if len(parts) > 1:
                                   loaded_image_names.append(parts[1])
             else:
                  log.warning("Неожиданный формат ответа от client.images.load()")

             images = []
             for name in set(loaded_image_names): # Используем set для уникальности
                 try:
                     images.append(self.get_image(name))
                 except ImageNotFoundError:
                     log.warning(f"Не удалось получить объект для загруженного образа: {name}")

             log.debug(f"Образ(ы) успешно загружен(ы): {', '.join(loaded_image_names) or 'Нет информации'}")
             return images
         except APIError as e:
              log.error(f"Ошибка API при загрузке образа: {e.explanation}")
              raise DockerOperationError(f"Ошибка API при загрузке образа: {e.explanation}") from e
         except Exception as e:
              log.exception(f"Непредвиденная ошибка при загрузке образа: {e}")
              raise DockerError(f"Непредвиденная ошибка при загрузке образа: {e}") from e


    # --- Методы очистки ---

    def prune_stopped_containers(self, filters: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Удаляет все остановленные контейнеры."""
        log.trace("Удаление остановленных контейнеров...")
        try:
            prune_info = self._client.containers.prune(filters=filters)
            reclaimed = prune_info.get('SpaceReclaimed')
            reclaimed_str = f"{reclaimed} байт" if reclaimed is not None else "N/A"
            log.debug(f"Остановленные контейнеры удалены ({len(prune_info.get('ContainersDeleted', []))} шт.). Освобождено места: {reclaimed_str}.")
            return prune_info
        except APIError as e:
            log.error(f"Ошибка API при удалении остановленных контейнеров: {e.explanation}")
            raise DockerOperationError(f"Ошибка API при удалении остановленных контейнеров: {e.explanation}") from e

    def prune_images(self, filters: Optional[Dict[str, Union[str, bool]]] = None) -> Dict[str, Any]:
        """Удаляет неиспользуемые образы (dangling по умолчанию)."""
        dangling_only = filters.get('dangling', True) if filters else True
        filter_type = "промежуточных (dangling)" if dangling_only else "всех неиспользуемых"
        log.trace(f"Удаление {filter_type} образов...")
        try:
            # Убедимся, что dangling передается как bool
            effective_filters = filters or {}
            if 'dangling' in effective_filters:
                effective_filters['dangling'] = bool(effective_filters['dangling'])

            prune_info = self._client.images.prune(filters=effective_filters)
            reclaimed = prune_info.get('SpaceReclaimed')
            reclaimed_str = f"{reclaimed} байт" if reclaimed is not None else "N/A"
            log.debug(f"Неиспользуемые образы удалены ({len(prune_info.get('ImagesDeleted', []))} шт.). Освобождено места: {reclaimed_str}.")
            return prune_info
        except APIError as e:
            log.error(f"Ошибка API при удалении образов: {e.explanation}")
            raise DockerOperationError(f"Ошибка API при удалении образов: {e.explanation}") from e

    def prune_volumes(self, filters: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Удаляет неиспользуемые тома."""
        log.trace("Удаление неиспользуемых томов...")
        try:
            prune_info = self._client.volumes.prune(filters=filters)
            reclaimed = prune_info.get('SpaceReclaimed')
            reclaimed_str = f"{reclaimed} байт" if reclaimed is not None else "N/A"
            log.debug(f"Неиспользуемые тома удалены ({len(prune_info.get('VolumesDeleted', []))} шт.). Освобождено места: {reclaimed_str}.")
            return prune_info
        except APIError as e:
            log.error(f"Ошибка API при удалении томов: {e.explanation}")
            raise DockerOperationError(f"Ошибка API при удалении томов: {e.explanation}") from e

    def prune_networks(self, filters: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Удаляет неиспользуемые сети."""
        log.trace("Удаление неиспользуемых сетей...")
        try:
            prune_info = self._client.networks.prune(filters=filters)
            log.debug(f"Неиспользуемые сети удалены ({len(prune_info.get('NetworksDeleted', []))} шт.).")
            return prune_info
        except APIError as e:
            log.error(f"Ошибка API при удалении сетей: {e.explanation}")
            raise DockerOperationError(f"Ошибка API при удалении сетей: {e.explanation}") from e

    def system_prune(self, prune_volumes: bool = False) -> None:
        """
        Выполняет полную очистку системы Docker (контейнеры, сети, образы).

        Args:
            prune_volumes: Включить ли удаление неиспользуемых томов.
        """
        log.trace(f"Полная очистка системы Docker (включая тома: {prune_volumes})...")
        try:
            self.prune_stopped_containers()
            self.prune_networks()
            # Удаляем все неиспользуемые образы (не только dangling)
            self.prune_images(filters={'dangling': False})
            if prune_volumes:
                self.prune_volumes()
            log.debug("Полная очистка системы Docker завершена.")
        except DockerError as e:
             log.error(f"Ошибка во время очистки системы: {e}")
             # Не пробрасываем дальше, т.к. это комплексная операция

    # --- Методы получения информации ---

    def get_container_logs(self,
                           name_or_id: str,
                           stdout: bool = True,
                           stderr: bool = True,
                           since: Optional[Union[str, int, float]] = None,
                           until: Optional[Union[str, int, float]] = None,
                           follow: bool = False, # Stream logs
                           tail: Union[str, int] = "all",
                           timestamps: bool = False
                          ) -> Union[Generator[bytes, None, None], bytes]:
        """
        Получает логи контейнера.

        Args:
            name_or_id: Имя или ID контейнера.
            stdout: Включить stdout.
            stderr: Включить stderr.
            since: Показать логи после этой временной метки (int/float epoch, datetime, str).
            until: Показать логи до этой временной метки.
            follow: Следовать за логами (возвращает генератор).
            tail: Количество последних строк логов ('all' или int).
            timestamps: Добавить временные метки.

        Returns:
            Генератор байтовых строк (если follow=True) или байтовая строка со всеми логами.
        """
        log.trace(f"Получение логов для контейнера {name_or_id}...")
        container = self._get_container(name_or_id)
        try:
            # Используем container.logs
            log_stream = container.logs(
                stdout=stdout,
                stderr=stderr,
                since=since,
                until=until,
                stream=follow,
                tail=tail,
                timestamps=timestamps
            )
            # Возвращаем генератор или байты как есть
            return cast(Union[Generator[bytes, None, None], bytes], log_stream)
        except APIError as e:
            log.error(f"Ошибка API при получении логов {name_or_id}: {e.explanation}")
            raise DockerOperationError(f"Ошибка API при получении логов {name_or_id}: {e.explanation}") from e

    def get_container_top(self, name_or_id: str, ps_args: Optional[str] = None) -> Dict[str, Any]:
        """
        Показывает запущенные процессы внутри контейнера. Аналог `docker top`.

        Args:
            name_or_id: Имя или ID контейнера.
            ps_args: Аргументы для команды ps (например, '-ef').

        Returns:
            Словарь с информацией о процессах (ключи 'Titles', 'Processes').
        """
        log.trace(f"Получение процессов (top) для контейнера {name_or_id}...")
        container = self._get_container(name_or_id)
        try:
            # Используем container.top
            top_info = container.top(ps_args=ps_args)
            return cast(Dict[str, Any], top_info)
        except APIError as e:
             log.error(f"Ошибка API при вызове top для {name_or_id}: {e.explanation}")
             raise DockerOperationError(f"Ошибка API при вызове top для {name_or_id}: {e.explanation}") from e

    def get_container_info(self, name_or_id: str) -> Dict[str, Any]:
         """
         Получает подробную информацию о контейнере (аналог `docker inspect`).

         Args:
             name_or_id: Имя или ID контейнера.

         Returns:
             Словарь с атрибутами контейнера.
         """
         log.trace(f"Получение информации (inspect) для контейнера {name_or_id}...")
         container = self._get_container(name_or_id)
         try:
            container.reload() # Обновляем данные
            return cast(Dict[str, Any], container.attrs)
         except APIError as e:
              log.error(f"Ошибка API при получении информации о контейнере {name_or_id}: {e.explanation}")
              raise DockerOperationError(f"Ошибка API при получении информации о контейнере {name_or_id}: {e.explanation}") from e

    def get_image_info(self, name_or_id: str) -> Dict[str, Any]:
         """
         Получает подробную информацию об образе (аналог `docker image inspect`).

         Args:
             name_or_id: Имя или ID образа.

         Returns:
             Словарь с атрибутами образа.
         """
         log.trace(f"Получение информации (inspect) для образа {name_or_id}...")
         image = self.get_image(name_or_id)
         try:
            # reload() нет для Image, attrs должны быть актуальны
            return cast(Dict[str, Any], image.attrs)
         except APIError as e: # Хотя ImageNotFound уже обработан в get_image
              log.error(f"Ошибка API при получении информации об образе {name_or_id}: {e.explanation}")
              raise DockerOperationError(f"Ошибка API при получении информации об образе {name_or_id}: {e.explanation}") from e

    def get_client_info(self) -> Dict[str, Any]:
         """
         Возвращает информацию о Docker Engine (аналог `docker info`).
         """
         log.trace("Получение информации о Docker Engine...")
         try:
             info = self._client.info()
             return cast(Dict[str, Any], info)
         except APIError as e:
              log.error(f"Ошибка API при получении информации о Docker Engine: {e.explanation}")
              raise DockerOperationError(f"Ошибка API при получении информации о Docker Engine: {e.explanation}") from e

    def get_client_version(self) -> Dict[str, Any]:
         """
         Возвращает информацию о версиях Docker Engine и API (аналог `docker version`).
         """
         log.debug("Получение информации о версиях Docker...")
         try:
             version_info = self._client.version()
             return cast(Dict[str, Any], version_info)
         except APIError as e:
              log.error(f"Ошибка API при получении информации о версиях Docker: {e.explanation}")
              raise DockerOperationError(f"Ошибка API при получении информации о версиях Docker: {e.explanation}") from e