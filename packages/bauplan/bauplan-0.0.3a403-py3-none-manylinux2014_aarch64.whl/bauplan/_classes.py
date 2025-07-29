from typing import Any, List, Optional


class Model:
    """
    Represents a model (dataframe/table representing a DAG step) as an input
    to a function.

    e.g.

    .. code-block:: python

        @bauplan.model()
        def some_parent_model():
            return pyarrow.Table.from_pydict({'bar': [1, 2, 3]})

        @bauplan.model()
        def your_cool_model(
            # parent models are passed as inputs, using bauplan.Model
            # class
            parent_0=bauplan.Model(
                'some_parent_model',
                columns=['bar'],
                filter='bar > 1',
            )
        ):
            # Can return a pandas dataframe or a pyarrow table
            return pyarrow.Table.from_pandas(
                pd.DataFrame({
                    'foo': parent_0['bar'] * 2,
                })
            )

    Bauplan can wrap other engines for the processing of some models, exposing a
    common interface and unified API for the user while dispatching the relevant
    operations to the underlying engine.

    The authentication and authorization happens securely and transparently through ssm;
    the user is asked to specify a connector type and the credentials through the
    relevant keywords:

    .. code-block:: python

        @bauplan.model()
        def your_cool_model(
            parent_0=bauplan.Model(
                'some_parent_model',
                columns=['bar'],
                filter='bar > 1',
                connector='dremio',
                connector_config_key='bauplan',
            )
        ):
            # parent_0 inside the function body
            # will still be an Arrow table: the user code
            # should still be the same as the data is moved
            # transparently by Bauplan from an engine to the function.
            return pyarrow.Table.from_pandas(
                pd.DataFrame({
                    'foo': parent_0['bar'] * 2,
                })
            )

    :param name: The name of the model.
    :param columns: The list of columns in the model. If the arg is not provided, the model will load all columns.
    :param filter: The optional filter for the model. Defaults to None.
    :param ref: The optional reference to the model. Defaults to None.
    :param connector: The connector type for the model (defaults to Bauplan SQL). Allowed values are 'snowflake' and 'dremio'.
    :param connector_config_key: The key name if the SSM key is custom with the pattern bauplan/connectors/<connector_type>/<key>.
    :param connector_config_uri: Full SSM uri if completely custom path, e.g. ssm://us-west-2/123456789012/baubau/dremio.
    """

    def __init__(
        self,
        name: str,
        columns: Optional[List[str]] = None,
        filter: Optional[str] = None,
        ref: Optional[str] = None,
        connector: Optional[str] = None,
        connector_config_key: Optional[str] = None,
        connector_config_uri: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.columns = columns
        self.filter = filter
        self.ref = ref
        self.connector = connector
        self.connector_config_key = connector_config_key
        self.connector_config_uri = connector_config_uri
