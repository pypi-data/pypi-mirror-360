from typing import Annotated

from fast_depends.dependencies import model

from unchained import context
from unchained.base import BaseUnchained
from unchained.settings.base import UnchainedSettings
from unchained.states import BaseState


def _get_app():
    return context.app.get()


AppDependency = Annotated[BaseUnchained, model.Depends(_get_app)]


def _get_settings(app: AppDependency) -> UnchainedSettings:
    return app.settings


def _get_state(app: AppDependency) -> BaseState:
    return app.state


SettingsDependency = Annotated[UnchainedSettings, model.Depends(_get_settings)]
StateDependency = Annotated[BaseState, model.Depends(_get_state)]


# from unchained.dependencies.query_params import QueryParams
# QueryParamsDependency = Annotated[str, QueryParams()]

# from unchained.dependencies.header import Header
# HeaderDependency = Annotated[str, Header()]
