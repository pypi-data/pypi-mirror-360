from typing import Generic, List, Optional, TypeVar, ClassVar, Callable, Iterator, Dict, Any
from typing_extensions import Annotated
from pydantic import ConfigDict, Field, BaseModel, PrivateAttr

T = TypeVar('T', bound=BaseModel)


class Pageable(BaseModel, Generic[T]):
    items: List[T]
    total: Optional[Annotated[int, Field(strict=True, ge=0)]]
    page: Optional[Annotated[int, Field(strict=True, ge=1)]]
    size: Optional[Annotated[int, Field(strict=True, ge=1)]]
    pages: Optional[Annotated[int, Field(strict=True, ge=0)]] = None
    __client_fields__: ClassVar[List[str]] = ["items"]
    _list_method: Optional[Callable[..., "Pageable[T]"]] = PrivateAttr(default=None)
    _list_method_args: Optional[Dict[str, Any]] = PrivateAttr(default=None)
    __properties: ClassVar[List[str]] = ["items", "total", "page", "size", "pages"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    def iter_pages(self) -> Iterator["Pageable[T]"]:
        """ Iterate over all pages."""
        if self._list_method is None:
            raise ValueError("No list method defined for pagination")

        if self._list_method_args is None:
            raise ValueError("No list method arguments defined for pagination")

        current_page = self.page or 1
        size = self.size or 10

        # Prepare base arguments for the list method, excluding pagination parameters
        # and private attributes.  This allows _list_method to be called without needing to
        # pass pagination parameters explicitly each time.
        base_args = {
            k: v for k, v in self._list_method_args.items()
            if k not in {"page", "size", "self"} and not k.startswith("__")
        }

        while True:
            page = self._list_method(**base_args, page=current_page, size=size)

            if page.total == 0:
                break

            yield page

            current_page += 1

            if page.pages and current_page > page.pages:
                break

    def iter_items(self) -> Iterator[T]:
        """ Iterate over all items across all pages."""
        for page in self.iter_pages():
            yield from page.items

    # WARNING: This method overrides Pydantic's default `__iter__()` behavior,
    # which normally yields `(field_name, value)` pairs.
    def __iter__(self) -> Iterator[T]: # type: ignore[override]
        """Default iteration is over items, not pages."""
        return self.iter_items()
