import typing
from uuid import UUID

from .block import Block
from .node import Node, _NodeMessage
from .proto import Symbol_pb2
from .util import DeserializationError, _IndexedAttribute

if typing.TYPE_CHECKING:  # pragma: no cover
    # Ignore flake8 "imported but unused" errors.
    from .ir import IR  # noqa: F401
    from .module import Module  # noqa: F401


Payload = typing.Union[Block, int]
"""A type hint representing the possible Symbol payloads."""


class Symbol(Node):
    """Represents a symbol, which maps a name to an object in the IR.

    :ivar ~.name: The name of this symbol.
    :ivar ~.at_end: True if this symbol is at the end of its referent, rather
        than at the beginning. Has no meaning for integral symbols.
    """

    name = _IndexedAttribute[str]()(lambda self: self.module)
    _payload = _IndexedAttribute[typing.Optional[Payload]]()(
        lambda self: self.module
    )

    def __init__(
        self,
        name: str,
        uuid: typing.Optional[UUID] = None,
        payload: typing.Optional[Payload] = None,
        at_end: bool = False,
        module: typing.Optional["Module"] = None,
    ):
        """
        :param name: The name of this symbol.
        :param uuid: The UUID of this ``Symbol``,
            or None if a new UUID needs generated via :func:`uuid.uuid4`.
            Defaults to None.
        :param payload: The value this symbol points to.
            May be an address, a Node, or None.
        :param at_end: True if this symbol is at the end of its referent,
            rather than at the beginning.
        :param module: The :class:`Module` this symbol belongs to.
        """

        super().__init__(uuid)
        self._module: typing.Optional["Module"] = None
        self.name = name
        self.at_end = at_end
        self._payload = payload
        # Use the property setter to ensure correct invariants.
        self.module = module

    @property
    def value(self) -> typing.Optional[int]:
        """The value of a Symbol, which is an integer or None.
        ``value`` and ``referent`` are mutually exclusive.
        """

        if not isinstance(self._payload, Block):
            return self._payload
        return None

    @value.setter
    def value(self, value: typing.Optional[int]) -> None:
        self._payload = value

    @property
    def referent(self) -> typing.Optional[Block]:
        """The object referred to by a Symbol, which is :class:`Block`
        or None. ``value`` and ``referent`` are mutually exclusive.
        """

        if isinstance(self._payload, Block):
            return self._payload
        return None

    @referent.setter
    def referent(self, referent: typing.Optional[Block]) -> None:
        self._payload = referent

    @classmethod
    def _decode_protobuf(
        cls,
        proto_symbol: _NodeMessage,
        uuid: UUID,
        ir: typing.Optional["IR"],
    ) -> "Symbol":
        assert ir
        assert isinstance(proto_symbol, Symbol_pb2.Symbol)
        symbol = cls(
            name=proto_symbol.name, at_end=proto_symbol.at_end, uuid=uuid
        )
        if proto_symbol.HasField("value"):
            symbol.value = proto_symbol.value
        if proto_symbol.HasField("referent_uuid"):
            referent_uuid = UUID(bytes=proto_symbol.referent_uuid)
            referent = ir.get_by_uuid(referent_uuid)
            if not isinstance(referent, Block):
                raise DeserializationError(
                    "Symbol: UUID %s is not a block" % referent_uuid
                )
            symbol.referent = referent
        symbol._add_to_uuid_cache(ir._local_uuid_cache)
        return symbol

    def _to_protobuf(self) -> Symbol_pb2.Symbol:
        proto_symbol = Symbol_pb2.Symbol()
        proto_symbol.uuid = self.uuid.bytes
        if self.value is not None:
            proto_symbol.value = self.value
        elif self.referent is not None:
            proto_symbol.referent_uuid = self.referent.uuid.bytes
        proto_symbol.name = self.name
        proto_symbol.at_end = self.at_end
        return proto_symbol

    def deep_eq(self, other: object) -> bool:
        # Do not move __eq__. See docstring for Node.deep_eq for more info.
        if not isinstance(other, Symbol):
            return False
        if self.value != other.value:
            return False
        if self.referent is None:
            if other.referent is not None:
                return False
        else:
            if not self.referent.deep_eq(other.referent):
                return False
        return (
            self.name == other.name
            and self.at_end == other.at_end
            and self.uuid == other.uuid
        )

    def __repr__(self) -> str:
        return (
            "Symbol("
            "uuid={uuid!r}, "
            "name={name!r}, "
            "payload={payload!r}, "
            "at_end={at_end!r}, "
            ")".format(name=self.name, payload=self._payload, **self.__dict__)
        )

    @property
    def module(self) -> typing.Optional["Module"]:
        return self._module

    @module.setter
    def module(self, value: typing.Optional["Module"]) -> None:
        if self._module is not None:
            self._module.symbols.discard(self)
        if value is not None:
            value.symbols.add(self)

    def _add_to_uuid_cache(self, cache: typing.Dict[UUID, Node]) -> None:
        """Update the UUID cache when this node is added."""

        cache[self.uuid] = self

    def _remove_from_uuid_cache(self, cache: typing.Dict[UUID, Node]) -> None:
        """Update the UUID cache when this node is removed."""

        del cache[self.uuid]

    @property
    def ir(self) -> typing.Optional["IR"]:
        """Get the IR this node ultimately belongs to."""
        if self.module is None:
            return None
        return self.module.ir
