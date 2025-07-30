from typing import ClassVar

try:
    import grpc
    from grpc import aio as grpc_aio

    GRPC_AVAILABLE = True
except ImportError:
    GRPC_AVAILABLE = False
    grpc = None
    grpc_aio = None

try:
    from http import HTTPStatus

    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False
    HTTPStatus = None


from archipy.models.dtos.error_dto import ErrorDetailDTO
from archipy.models.types.error_message_types import ErrorMessageType
from archipy.models.types.language_type import LanguageType


class BaseError(Exception):
    """Base exception class for all custom errors.

    This class provides a standardized way to handle errors with support for:
    - Localization of error messages
    - Additional context data
    - Integration with HTTP and gRPC status codes

    Attributes:
        error (ErrorDetailDTO): The error details including message and status codes.
        lang (LanguageType): The language for the error message.
        additional_data (dict[str, Any] | None): Additional context data for the error.
        http_status_code (ClassVar[int]): HTTP status code for the error.
        grpc_status_code (ClassVar[int]): gRPC status code for the error.
    """

    http_status_code: ClassVar[int] = 500
    grpc_status_code: ClassVar[grpc.StatusCode] = grpc.StatusCode.INTERNAL

    def __init__(
        self,
        error: ErrorDetailDTO | ErrorMessageType | None = None,
        lang: LanguageType = LanguageType.FA,
        additional_data: dict | None = None,
        *args: object,
    ) -> None:
        """Initialize the error with message and optional context.

        Args:
            error: The error detail or message. Can be:
                - ErrorDetail: Direct error detail object
                - ExceptionMessageType: Enum member containing error detail
                - None: Will use UNKNOWN_ERROR
            lang: Language code for the error message (defaults to Persian).
            additional_data: Additional context data for the error.
            *args: Additional arguments for the base Exception class.
        """
        if isinstance(error, ErrorMessageType):
            self.error_detail = error.value
        elif isinstance(error, ErrorDetailDTO):
            self.error_detail = error
        else:
            self.error_detail = ErrorMessageType.UNKNOWN_ERROR.value

        self.lang = lang
        self.additional_data = additional_data or {}

        # Initialize base Exception with the message
        super().__init__(self.get_message(), *args)

    def get_message(self) -> str:
        """Gets the localized error message based on the language setting.

        Returns:
            str: The error message in the current language.
        """
        return self.error_detail.message_fa if self.lang == LanguageType.FA else self.error_detail.message_en

    def to_dict(self) -> dict:
        """Converts the exception to a dictionary format for API responses.

        Returns:
            dict: A dictionary containing error details and additional data.
        """
        response = {
            "error": self.error_detail.code,
            "detail": self.error_detail.model_dump(mode="json", exclude_none=True),
        }

        # Add additional data if present
        detail = response["detail"]
        if isinstance(detail, dict) and self.additional_data:
            detail.update(self.additional_data)

        return response

    @property
    def http_status_code_value(self) -> int | None:
        """Gets the HTTP status code if HTTP support is available.

        Returns:
            Optional[int]: The HTTP status code or None if HTTP is not available.
        """
        return self.error_detail.http_status if HTTP_AVAILABLE else None

    @property
    def grpc_status_code_value(self) -> int | None:
        """Gets the gRPC status code if gRPC support is available.

        Returns:
            Optional[int]: The gRPC status code or None if gRPC is not available.
        """
        return self.error_detail.grpc_status if GRPC_AVAILABLE else None

    def __str__(self) -> str:
        """String representation of the exception.

        Returns:
            str: A formatted string containing the error code and message.
        """
        return f"[{self.error_detail.code}] {self.get_message()}"

    def __repr__(self) -> str:
        """Detailed string representation of the exception.

        Returns:
            str: A detailed string representation including all error details.
        """
        return (
            f"{self.__class__.__name__}("
            f"code='{self.error_detail.code}', "
            f"message='{self.get_message()}', "
            f"http_status={self.http_status_code_value}, "
            f"grpc_status={self.grpc_status_code_value}, "
            f"additional_data={self.additional_data}"
            f")"
        )

    @property
    def code(self) -> str:
        """Gets the error code.

        Returns:
            str: The error code.
        """
        return self.error_detail.code

    @property
    def message(self) -> str:
        """Gets the current language message.

        Returns:
            str: The error message in the current language.
        """
        return self.get_message()

    @property
    def message_en(self) -> str:
        """Gets the English message.

        Returns:
            str: The English error message.
        """
        return self.error_detail.message_en

    @property
    def message_fa(self) -> str:
        """Gets the Persian message.

        Returns:
            str: The Persian error message.
        """
        return self.error_detail.message_fa

    def _get_grpc_status_code(self) -> grpc.StatusCode | int:
        """Gets the proper gRPC status code for this error.

        Returns:
            grpc.StatusCode | int: The gRPC status code enum value or integer code.
        """
        if not GRPC_AVAILABLE:
            return 13  # INTERNAL

        # Use the class-level grpc_status_code if available
        if hasattr(self.__class__, "grpc_status_code") and self.__class__.grpc_status_code is not None:
            status_code = self.__class__.grpc_status_code
        else:
            # Fallback to error detail if available
            status_code = self.grpc_status_code_value or grpc.StatusCode.INTERNAL

        # Convert int to StatusCode enum if necessary
        if isinstance(status_code, int):
            try:
                status_code = grpc.StatusCode(status_code)
            except ValueError:
                status_code = grpc.StatusCode.INTERNAL

        return status_code

    async def abort_grpc_async(self, context: object) -> None:
        """Aborts an async gRPC call with the appropriate status code and message.

        Args:
            context: The gRPC ServicerContext to abort.

        Raises:
            ValueError: If context is None or doesn't have abort method.
        """
        if context is None:
            raise ValueError("gRPC context cannot be None")

        if not GRPC_AVAILABLE or not hasattr(context, "abort"):
            raise ValueError("Invalid gRPC context: missing abort method")

        status_code = self._get_grpc_status_code()
        message = self.get_message()

        await context.abort(status_code, message)

    def abort_grpc_sync(self, context: object) -> None:
        """Aborts a sync gRPC call with the appropriate status code and message.

        Args:
            context: The gRPC ServicerContext to abort.

        Raises:
            ValueError: If context is None or doesn't have abort method.
        """
        if context is None:
            raise ValueError("gRPC context cannot be None")

        if not GRPC_AVAILABLE or not hasattr(context, "abort"):
            raise ValueError("Invalid gRPC context: missing abort method")

        status_code = self._get_grpc_status_code()
        message = self.get_message()

        context.abort(status_code, message)

    @classmethod
    async def abort_with_error_async(
        cls,
        context: object,
        error: ErrorDetailDTO | ErrorMessageType | None = None,
        lang: LanguageType = LanguageType.FA,
        additional_data: dict | None = None,
    ) -> None:
        """Creates an error instance and immediately aborts the async gRPC context.

        Args:
            context: The async gRPC ServicerContext to abort.
            error: The error detail or message type.
            lang: Language code for the error message.
            additional_data: Additional context data for the error.

        Raises:
            ValueError: If context is None or invalid.
        """
        instance = cls(error=error, lang=lang, additional_data=additional_data)
        await instance.abort_grpc_async(context)

    @classmethod
    def abort_with_error_sync(
        cls,
        context: object,
        error: ErrorDetailDTO | ErrorMessageType | None = None,
        lang: LanguageType = LanguageType.FA,
        additional_data: dict | None = None,
    ) -> None:
        """Creates an error instance and immediately aborts the sync gRPC context.

        Args:
            context: The sync gRPC ServicerContext to abort.
            error: The error detail or message type.
            lang: Language code for the error message.
            additional_data: Additional context data for the error.

        Raises:
            ValueError: If context is None or invalid.
        """
        instance = cls(error=error, lang=lang, additional_data=additional_data)
        instance.abort_grpc_sync(context)
