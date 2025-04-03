# modal.enter

    
    
    def enter(
        _warn_parentheses_missing=None,
        *,
        snap: bool = False,
    ) -> Callable[[Union[Callable[[Any], Any], _PartialFunction]], _PartialFunction]:

Copy

Decorator for methods which should be executed when a new container is
started.

See the lifeycle function guide for more information.

