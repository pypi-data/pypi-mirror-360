"""Cofactr graph API client."""
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# Python Modules
from enum import Enum
import json
from typing import Any, Dict, List, Literal, NamedTuple, Optional, Union
from urllib.parse import quote, urlencode

# 3rd Party Modules
import httpx
from more_itertools import batched, flatten
from tenacity import (
    retry,
    retry_any,
    retry_if_exception_message,
    retry_if_exception_type,
    stop_after_attempt,
    wait_chain,
    wait_fixed,
)

# Local Modules
from cofactr.schema import (
    OfferSchemaName,
    OrderSchemaName,
    OrgSchemaName,
    ProductSchemaName,
    SupplierSchemaName,
    schema_to_offer,
    schema_to_order,
    schema_to_org,
    schema_to_product,
    schema_to_supplier,
)
from cofactr.schema.types import Completion, OrderInV0, PartInV0, PartialPartInV0

Protocol = Literal["http", "https"]

_MAX_BATCH_SIZE = 250
_MAX_SUB_BATCH_SIZE = 25
_REQUIRED_FIELDS = ["id", "deprecated_ids"]


class SearchStrategy(str, Enum):
    """Search strategy."""

    DEFAULT = "default"
    MPN_SKU_MFR = "mpn_sku_mfr"


drop_none_values = lambda d: {k: v for k, v in d.items() if v is not None}

BATCH_LIMIT = 500


class RetrySettings(NamedTuple):
    """Retry settings for GraphAPI methods.
    TODO: Consider extending to other 5xx errors if and when encountered.
    """

    reraise: bool = True
    retry: retry_any = (
        retry_if_exception_type(httpx.ConnectTimeout)
        | retry_if_exception_type(httpx.ReadTimeout)
        | retry_if_exception_message(match=r"Server error '502 Bad Gateway'")
    )
    stop: stop_after_attempt = stop_after_attempt(3)
    wait: wait_chain = wait_chain(*[wait_fixed(wait=wait) for wait in [1, 3, 5]])


def _get_ids_from_dict(entity):
    """Get IDs from dictionary."""

    return [entity["id"], *(entity.get("deprecated_ids") or [])]


def _get_ids_from_class(entity):
    """Get IDs from class."""

    return [entity.id, *(getattr(entity, "deprecated_ids", None) or [])]


def get_products(
    url,
    client_id,
    api_key,
    query,
    fields,
    before,
    after,
    limit,
    external,
    force_refresh,
    schema,
    filtering,
    search_strategy: SearchStrategy,
    stale_delta: Optional[str],
    timeout: Optional[int] = None,
    owner_id: Optional[str] = None,
    reference: Optional[str] = None,
    options: Optional[Dict] = None,
) -> httpx.Response:
    """Get products."""

    options = options or {}

    res = httpx.get(
        f"{url}/products/",
        headers=drop_none_values(
            {
                "X-CLIENT-ID": client_id,
                "X-API-KEY": api_key,
            }
        ),
        params=drop_none_values(
            {
                "owner_id": owner_id,
                "q": query,
                "fields": fields,
                "before": before,
                "after": after,
                "limit": limit,
                "external": external,
                "force_refresh": force_refresh,
                "schema": schema,
                "filtering": json.dumps(filtering) if filtering else None,
                "search_strategy": search_strategy.value,
                "stale_delta": stale_delta,
                "ref": reference,
                **options,
            }
        ),
        timeout=timeout,
        follow_redirects=True,
    )

    res.raise_for_status()

    return res


def get_orgs(
    url,
    client_id,
    api_key,
    query,
    before,
    after,
    limit,
    schema,
    timeout,
    filtering,
    owner_id,
) -> httpx.Response:
    """Get orgs."""

    res = httpx.get(
        f"{url}/orgs",
        headers=drop_none_values(
            {
                "X-CLIENT-ID": client_id,
                "X-API-KEY": api_key,
            }
        ),
        params=drop_none_values(
            {
                "owner_id": owner_id,
                "q": query,
                "before": before,
                "after": after,
                "limit": limit,
                "schema": schema,
                "filtering": json.dumps(filtering) if filtering else None,
            }
        ),
        timeout=timeout,
        follow_redirects=True,
    )

    res.raise_for_status()

    return res


def get_suppliers(
    url,
    client_id,
    api_key,
    query,
    before,
    after,
    limit,
    schema,
    timeout,
    filtering,
    owner_id,
) -> httpx.Response:
    """Get orgs."""

    res = httpx.get(
        f"{url}/orgs/suppliers",
        headers=drop_none_values(
            {
                "X-CLIENT-ID": client_id,
                "X-API-KEY": api_key,
            }
        ),
        params=drop_none_values(
            {
                "owner_id": owner_id,
                "q": query,
                "before": before,
                "after": after,
                "limit": limit,
                "schema": schema,
                "filtering": json.dumps(filtering) if filtering else None,
            }
        ),
        timeout=timeout,
        follow_redirects=True,
    )

    res.raise_for_status()

    return res


class GraphAPI:  # pylint: disable=too-many-instance-attributes
    """A client-side representation of the Cofactr graph API."""

    PROTOCOL: Protocol = "https"
    HOST = "graph.cofactr.com"
    retry_settings = RetrySettings()

    def __init__(
        self,
        protocol: Optional[Protocol] = PROTOCOL,
        host: Optional[str] = HOST,
        default_product_schema: Union[
            ProductSchemaName, str
        ] = ProductSchemaName.FLAGSHIP,
        default_order_schema: Union[OrderSchemaName, str] = OrderSchemaName.FLAGSHIP,
        default_org_schema: Union[OrgSchemaName, str] = OrgSchemaName.FLAGSHIP,
        default_offer_schema: Union[OfferSchemaName, str] = OfferSchemaName.FLAGSHIP,
        default_supplier_schema: Union[
            SupplierSchemaName, str
        ] = SupplierSchemaName.FLAGSHIP,
        client_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.url = f"{protocol}://{host}"
        self.default_product_schema = default_product_schema
        self.default_order_schema = default_order_schema
        self.default_org_schema = default_org_schema
        self.default_offer_schema = default_offer_schema
        self.default_supplier_schema = default_supplier_schema
        self.client_id = client_id
        self.api_key = api_key

    def check_health(self):
        """Check the operational status of the service."""

        res = httpx.get(self.url)

        res.raise_for_status()

        return res.json()

    @retry(
        reraise=retry_settings.reraise,
        retry=retry_settings.retry,
        stop=retry_settings.stop,
        wait=retry_settings.wait,
    )
    def get_products(
        self,
        query: Optional[str] = None,
        fields: Optional[str] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        limit: Optional[int] = None,
        external: Optional[bool] = True,
        force_refresh: bool = False,
        schema: Optional[Union[ProductSchemaName, str]] = None,
        filtering: Optional[List[Dict]] = None,
        timeout: Optional[int] = None,
        owner_id: Optional[str] = None,
        search_strategy: SearchStrategy = SearchStrategy.DEFAULT,
        stale_delta: Optional[str] = None,
        reference: Optional[str] = None,
        options: Optional[Dict] = None,
    ):
        """Get products.

        Args:
            query: Search query.
            fields: Used to filter properties that the response should contain. A field can be a
                concrete property like "mpn" or an abstract group of properties like "assembly".
                Example: `"id,aliases,labels,statements{spec,assembly},offers"`.
            before: Upper page boundry, expressed as a product ID.
            after: Lower page boundry, expressed as a product ID.
            limit: Restrict the results of the query to a particular number of documents.
            external: Whether to query external sources.
            force_refresh: Whether to force re-ingestion from external sources. Overrides
                `external`.
            schema: Response schema.
            filtering: Filter products.
                Example: `[{"field":"id","operator":"IN","value":["CCCQSA3G9SMR","CCV1F7A8UIYH"]}]`.
            timeout: Time to wait (in seconds) for the server to issue a response.
            owner_id: Specifies which private data to access.
            search_strategy: Search strategy used to find products.
            stale_delta: How much time has to pass before data is treated as stale. Use "inf" or
                "infinite" to indicate data should not be refreshed, no matter how old.
                Examples: "5h", "1d", "1w", "inf"
            reference: Arbitrary note to associate with the request.
            options: Extra configuration options.
        """

        if not schema:
            schema = self.default_product_schema

        schema_class: Optional[ProductSchemaName] = (
            schema if isinstance(schema, ProductSchemaName) else None
        )

        if (schema_class and fields) and (
            schema_class is not ProductSchemaName.INTERNAL
        ):
            raise ValueError(
                "Field expansion is not supported for the targeted schema."
            )

        schema_value = schema_class.value if schema_class else schema

        res = get_products(
            url=self.url,
            client_id=self.client_id,
            api_key=self.api_key,
            query=query,
            fields=fields,
            external=external,
            force_refresh=force_refresh,
            before=before,
            after=after,
            limit=limit,
            schema=schema_value,
            filtering=filtering,
            search_strategy=search_strategy,
            stale_delta=stale_delta,
            timeout=timeout,
            owner_id=owner_id,
            reference=reference,
            options=options,
        )

        extracted_products = res.json()
        res_data = extracted_products and extracted_products.get("data")

        if res_data and schema_class:
            # Handle schemas that have parsers.
            Product = schema_to_product.get(  # pylint: disable=invalid-name
                schema_class
            )

            if Product:
                extracted_products["data"] = [Product(**data) for data in res_data]

        return extracted_products

    @retry(
        reraise=retry_settings.reraise,
        retry=retry_settings.retry,
        stop=retry_settings.stop,
        wait=retry_settings.wait,
    )
    def get_products_by_searches(
        self,
        queries: List[str],
        external: bool = True,
        force_refresh: bool = False,
        schema: Optional[Union[ProductSchemaName, str]] = None,
        timeout: Optional[int] = None,
        owner_id: Optional[str] = None,
        search_strategy: SearchStrategy = SearchStrategy.DEFAULT,
        stale_delta: Optional[str] = None,
        reference: Optional[str] = None,
        options: Optional[Dict] = None,
        fields: Optional[str] = None,
    ):
        """Search for products associated with each query.

        Args:
            queries: Queries to find products for.
            external: Whether to query external sources in order to refresh data if applicable.
            force_refresh: Whether to force re-ingestion from external sources. Overrides
                `external`.
            schema: Response schema.
            timeout: Time to wait (in seconds) for the server to issue a response.
            owner_id: Specifies which private data to access.
            search_strategy: Search strategy used to find products.
            stale_delta: How much time has to pass before data is treated as stale. Use "inf" or
                "infinite" to indicate data should not be refreshed, no matter how old.
                Examples: "5h", "1d", "1w", "inf"
            reference: Arbitrary note to associate with the request.
            options: Extra configuration options.
            fields: Used to filter properties that the response should contain. A field can be a
                concrete property like "mpn" or an abstract group of properties like "assembly".
                Example: `"id,aliases,labels,statements{spec,assembly},offers"`.

        Returns:
            A dictionary mapping each MPN to a list of matching products.
        """

        if not queries:
            return {}

        if not schema:
            schema = self.default_product_schema

        schema_class: Optional[ProductSchemaName] = (
            schema if isinstance(schema, ProductSchemaName) else None
        )

        if (schema_class and fields) and (
            schema_class is not ProductSchemaName.INTERNAL
        ):
            raise ValueError(
                "Field expansion is not supported for the targeted schema."
            )

        schema_value = schema_class.value if schema_class else schema

        options = options or {}

        invariant_query_params = drop_none_values(
            {
                "schema": schema_value,
                "external": bool(external),
                "force_refresh": force_refresh,
                "stale_delta": stale_delta,
                "fields": fields,
                "search_strategy": search_strategy.value,
            }
        )

        query_to_products: Dict[str, Any] = {}

        for query_batch in batched(queries, n=_MAX_BATCH_SIZE):
            res = httpx.post(
                f"{self.url}/batch/products/",
                headers=drop_none_values(
                    {
                        "X-CLIENT-ID": self.client_id,
                        "X-API-KEY": self.api_key,
                    }
                ),
                json={
                    "batch": [
                        {
                            "method": "GET",
                            "relative_url": (
                                f"?q={quote(query)}&{urlencode(invariant_query_params)}"
                            ),
                        }
                        for query in query_batch
                    ]
                },
                params=drop_none_values(
                    {"owner_id": owner_id, "ref": reference, **options}
                ),
                timeout=timeout,
                follow_redirects=True,
            )

            res.raise_for_status()

            responses = res.json()

            if isinstance(responses, list):
                for query, response in zip(query_batch, responses):
                    matches = []

                    if response["code"] == 200:
                        matches = response["body"]["data"]

                    query_to_products[query] = matches

        if schema_class:
            Product = schema_to_product[schema_class]  # pylint: disable=invalid-name

            for query, products in query_to_products.items():
                query_to_products[query] = [
                    Product(**product_data) for product_data in products
                ]

        return query_to_products

    @retry(
        reraise=retry_settings.reraise,
        retry=retry_settings.retry,
        stop=retry_settings.stop,
        wait=retry_settings.wait,
    )
    def get_products_by_ids(
        self,
        ids: List[str],
        external: Optional[bool] = True,
        force_refresh: bool = False,
        schema: Optional[Union[ProductSchemaName, str]] = None,
        timeout: Optional[int] = None,
        owner_id: Optional[str] = None,
        stale_delta: Optional[str] = None,
        reference: Optional[str] = None,
        options: Optional[Dict] = None,
        fields: Optional[str] = None,
    ):
        """Get a batch of products by IDs.

        Note: Multiple requests are made if more than 250 IDs are provided.

        Args:
            ids: Cofactr product IDs to match on.
            external: Whether to query external sources in order to refresh data if applicable.
            force_refresh: Whether to force re-ingestion from external sources. Overrides
                `external`.
            schema: Response schema.
            timeout: Time to wait (in seconds) for the server to issue a response.
            owner_id: Specifies which private data to access.
            stale_delta: How much time has to pass before data is treated as stale. Use "inf" or
                "infinite" to indicate data should not be refreshed, no matter how old.
                Examples: "5h", "1d", "1w", "inf"
            reference: Arbitrary note to associate with the request.
            options: Extra configuration options.
            fields: Used to filter properties that the response should contain. A field can be a
                concrete property like "mpn" or an abstract group of properties like "assembly".
                Example: `"id,aliases,labels,statements{spec,assembly},offers"`.
        """

        if not ids:
            return {}

        if not schema:
            schema = self.default_product_schema

        schema_class: Optional[ProductSchemaName] = (
            schema if isinstance(schema, ProductSchemaName) else None
        )

        if (schema_class and fields) and (
            schema_class is not ProductSchemaName.INTERNAL
        ):
            raise ValueError(
                "Field expansion is not supported for the targeted schema."
            )

        # schema_value = schema_class.value if schema_class else schema
        parsed_fields = fields.split(",") if fields else []

        if fields:
            for required_field in _REQUIRED_FIELDS:
                if required_field not in parsed_fields:
                    fields = f"{required_field},{fields}"

        batched_products = [
            self.get_products(
                external=external,
                force_refresh=force_refresh,
                schema=schema,
                filtering=[{"field": "id", "operator": "IN", "value": batched_ids}],
                limit=_MAX_BATCH_SIZE,
                timeout=timeout,
                owner_id=owner_id,
                stale_delta=stale_delta,
                reference=reference,
                options=options,
                fields=fields,
            )
            for batched_ids in batched(ids, n=_MAX_BATCH_SIZE)
        ]

        products = list(flatten([res["data"] for res in batched_products]))

        get_ids = _get_ids_from_class if schema_class else _get_ids_from_dict

        id_to_product = {
            id_: product for product in products for id_ in get_ids(entity=product)
        }
        target_id_to_product = {
            id_: id_to_product[id_] for id_ in ids if id_ in id_to_product
        }

        fields_to_drop = [
            required_field
            for required_field in _REQUIRED_FIELDS
            if required_field not in parsed_fields
        ]

        if not schema_class:
            for field in fields_to_drop:
                for _, product in target_id_to_product.items():
                    product.pop(field, None)

        return target_id_to_product

    @retry(
        reraise=retry_settings.reraise,
        retry=retry_settings.retry,
        stop=retry_settings.stop,
        wait=retry_settings.wait,
    )
    def get_canonical_product_ids(
        self,
        ids: List[str],
        timeout: Optional[int] = None,
        owner_id: Optional[str] = None,
        reference: Optional[str] = None,
        options: Optional[Dict] = None,
    ):
        """Get the canonical product ID for each of the given IDs, which may or may not be
        deprecated.
        """

        if not ids:
            return {}

        batched_products = [
            self.get_products(
                fields="id,deprecated_ids",
                external=False,
                force_refresh=False,
                schema=ProductSchemaName.INTERNAL,
                filtering=[{"field": "id", "operator": "IN", "value": batched_ids}],
                limit=_MAX_BATCH_SIZE,
                timeout=timeout,
                owner_id=owner_id,
                reference=reference,
                options=options,
            )
            for batched_ids in batched(ids, n=_MAX_BATCH_SIZE)
        ]

        id_to_canonical_id = {}

        for res in batched_products:
            products = res.get("data", [])

            for product in products:
                canonical_id = product["id"]

                for key in [canonical_id, *(product.get("deprecated_ids") or [])]:
                    id_to_canonical_id[key] = canonical_id

        return {id_: id_to_canonical_id.get(id_) for id_ in ids}

    @retry(
        reraise=retry_settings.reraise,
        retry=retry_settings.retry,
        stop=retry_settings.stop,
        wait=retry_settings.wait,
    )
    def get_orgs(
        self,
        query: Optional[str] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        limit: Optional[int] = None,
        schema: Optional[Union[OrgSchemaName, str]] = None,
        timeout: Optional[int] = None,
        filtering: Optional[List[Dict]] = None,
        owner_id: Optional[str] = None,
    ):
        """Get organizations.

        Args:
            query: Search query.
            before: Upper page boundry, expressed as a product ID.
            after: Lower page boundry, expressed as a product ID.
            limit: Restrict the results of the query to a particular number of documents.
            schema: Response schema.
            timeout: Time to wait (in seconds) for the server to issue a response.
            filtering: Filter orgs.
                Example: `[{"field":"id","operator":"IN","value":["622fb450e4c292d8287b0af5"]}]`.
            owner_id: Specifies which private data to access.
        """

        if not schema:
            schema = self.default_org_schema

        schema_class: Optional[OrgSchemaName] = (
            schema if isinstance(schema, OrgSchemaName) else None
        )
        schema_value = schema_class.value if schema_class else schema

        res = get_orgs(
            url=self.url,
            client_id=self.client_id,
            api_key=self.api_key,
            query=query,
            before=before,
            after=after,
            limit=limit,
            schema=schema_value,
            timeout=timeout,
            filtering=filtering,
            owner_id=owner_id,
        )

        res_json = res.json()
        res_data = res_json and res_json.get("data")

        if res_data and schema_class:
            Org = schema_to_org[schema_class]  # pylint: disable=invalid-name

            res_json["data"] = [Org(**data) for data in res_data]

        return res_json

    @retry(
        reraise=retry_settings.reraise,
        retry=retry_settings.retry,
        stop=retry_settings.stop,
        wait=retry_settings.wait,
    )
    def get_suppliers(
        self,
        query: Optional[str] = None,
        before: Optional[str] = None,
        after: Optional[str] = None,
        limit: Optional[int] = None,
        schema: Optional[Union[SupplierSchemaName, str]] = None,
        timeout: Optional[int] = None,
        filtering: Optional[List[Dict]] = None,
        owner_id: Optional[str] = None,
    ):
        """Get suppliers.

        Args:
            query: Search query.
            before: Upper page boundry, expressed as a product ID.
            after: Lower page boundry, expressed as a product ID.
            limit: Restrict the results of the query to a particular number of documents.
            schema: Response schema.
            timeout: Time to wait (in seconds) for the server to issue a response.
            filtering: Filter suppliers.
                Example: `[{"field":"id","operator":"IN","value":["622fb450e4c292d8287b0af5"]}]`.
            owner_id: Specifies which private data to access.
        """

        if not schema:
            schema = self.default_supplier_schema

        schema_class: Optional[SupplierSchemaName] = (
            schema if isinstance(schema, SupplierSchemaName) else None
        )
        schema_value = schema_class.value if schema_class else schema

        res = get_suppliers(
            url=self.url,
            client_id=self.client_id,
            api_key=self.api_key,
            query=query,
            before=before,
            after=after,
            limit=limit,
            schema=schema_value,
            timeout=timeout,
            filtering=filtering,
            owner_id=owner_id,
        )

        res_json = res.json()
        res_data = res_json and res_json.get("data")

        if res_data and schema_class:
            Supplier = schema_to_supplier[schema_class]  # pylint: disable=invalid-name

            res_json["data"] = [Supplier(**data) for data in res_data]

        return res_json

    @retry(
        reraise=retry_settings.reraise,
        retry=retry_settings.retry,
        stop=retry_settings.stop,
        wait=retry_settings.wait,
    )
    def get_suppliers_by_ids(
        self,
        ids: List[str],
        schema: Optional[Union[SupplierSchemaName, str]] = None,
        timeout: Optional[int] = None,
        owner_id: Optional[str] = None,
    ):
        """Get a batch of suppliers by IDs.

        Note: Multiple requests are made if more than 250 IDs are provided.

        Args:
            ids: Cofactr org IDs to match on.
            schema: Response schema.
            timeout: Time to wait (in seconds) for the server to issue a response.
            owner_id: Specifies which private data to access.
        """

        if not ids:
            return {}

        if not schema:
            schema = self.default_supplier_schema

        schema_class: Optional[SupplierSchemaName] = (
            schema if isinstance(schema, SupplierSchemaName) else None
        )

        batched_suppliers = [
            self.get_suppliers(
                schema=schema,
                filtering=[{"field": "id", "operator": "IN", "value": batched_ids}],
                limit=_MAX_BATCH_SIZE,
                timeout=timeout,
                owner_id=owner_id,
            )
            for batched_ids in batched(ids, n=_MAX_BATCH_SIZE)
        ]

        suppliers = list(
            flatten([suppliers["data"] for suppliers in batched_suppliers])
        )

        get_ids = _get_ids_from_class if schema_class else _get_ids_from_dict

        id_to_supplier = {
            id_: supplier for supplier in suppliers for id_ in get_ids(entity=supplier)
        }
        target_id_to_supplier = {
            id_: id_to_supplier[id_] for id_ in ids if id_ in id_to_supplier
        }

        return target_id_to_supplier

    @retry(
        reraise=retry_settings.reraise,
        retry=retry_settings.retry,
        stop=retry_settings.stop,
        wait=retry_settings.wait,
    )
    def autocomplete_orgs(
        self,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        types: Optional[str] = None,
        timeout: Optional[int] = None,
        owner_id: Optional[str] = None,
    ) -> Dict[Literal["data"], Completion]:
        """Autocomplete organizations.

        Args:
            query: Search query.
            before: Upper page boundry, expressed as a product ID.
            after: Lower page boundry, expressed as a product ID.
            limit: Restrict the results of the query to a particular number of
                documents.
            types: Filter for types of organizations.
                Example: "supplier" filters to suppliers.
                Example: "supplier|manufacturer" filters to orgs that are a
                    supplier or a manufacturer.
            timeout: Time to wait (in seconds) for the server to issue a response.
            owner_id: Specifies which private data to access.
        """

        res = httpx.get(
            f"{self.url}/orgs/autocompletions/",
            headers=drop_none_values(
                {
                    "X-CLIENT-ID": self.client_id,
                    "X-API-KEY": self.api_key,
                }
            ),
            params=drop_none_values(
                {
                    "owner_id": owner_id,
                    "q": query,
                    "limit": limit,
                    "types": types,
                }
            ),
            timeout=timeout,
            follow_redirects=True,
        )

        res.raise_for_status()

        return res.json()

    @retry(
        reraise=retry_settings.reraise,
        retry=retry_settings.retry,
        stop=retry_settings.stop,
        wait=retry_settings.wait,
    )
    def autocomplete_classifications(
        self,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        types: Optional[str] = None,
        timeout: Optional[int] = None,
        owner_id: Optional[str] = None,
    ) -> Dict[Literal["data"], Completion]:
        """Autocomplete classifications.

        Args:
            query: Search query.
            before: Upper page boundry, expressed as a product ID.
            after: Lower page boundry, expressed as a product ID.
            limit: Restrict the results of the query to a particular number of
                documents.
            types: Filter for types of organizations.
                Example: "part_classification" filters to part classification classes.
            timeout: Time to wait (in seconds) for the server to issue a response.
            owner_id: Specifies which private data to access.
        """

        res = httpx.get(
            f"{self.url}/classes/autocompletions/",
            headers=drop_none_values(
                {
                    "X-CLIENT-ID": self.client_id,
                    "X-API-KEY": self.api_key,
                }
            ),
            params=drop_none_values(
                {
                    "owner_id": owner_id,
                    "q": query,
                    "limit": limit,
                    "types": types,
                }
            ),
            timeout=timeout,
            follow_redirects=True,
        )

        res.raise_for_status()

        return res.json()

    @retry(
        reraise=retry_settings.reraise,
        retry=retry_settings.retry,
        stop=retry_settings.stop,
        wait=retry_settings.wait,
    )
    def get_product(
        self,
        id: str,
        fields: Optional[str] = None,
        external: Optional[bool] = True,
        force_refresh: bool = False,
        schema: Optional[Union[ProductSchemaName, str]] = None,
        timeout: Optional[int] = None,
        owner_id: Optional[str] = None,
        stale_delta: Optional[str] = None,
        reference: Optional[str] = None,
        options: Optional[Dict] = None,
    ):
        """Get product.

        Args:
            fields: Used to filter properties that the response should contain. A field can be a
                concrete property like "mpn" or an abstract group of properties like "assembly".
                Example: "id,aliases,labels,statements{spec,assembly},offers"
            external: Whether to query external sources in order to update information for the
                given product.
            force_refresh: Whether to force re-ingestion from external sources. Overrides
                `external`.
            schema: Response schema.
            timeout: Time to wait (in seconds) for the server to issue a response.
            owner_id: Specifies which private data to access.
            stale_delta: How much time has to pass before data is treated as stale. Use "inf" or
                "infinite" to indicate data should not be refreshed, no matter how old.
                Examples: "5h", "1d", "1w", "inf"
            reference: Arbitrary note to associate with the request.
            options: Extra configuration options.
        """

        if not schema:
            schema = self.default_product_schema

        schema_class: Optional[ProductSchemaName] = (
            schema if isinstance(schema, ProductSchemaName) else None
        )

        if (schema_class and fields) and (
            schema_class is not ProductSchemaName.INTERNAL
        ):
            raise ValueError(
                "Field expansion is not supported for the targeted schema."
            )

        schema_value = schema_class.value if schema_class else schema

        options = options or {}

        res = httpx.get(
            f"{self.url}/products/{id}",
            headers=drop_none_values(
                {
                    "X-CLIENT-ID": self.client_id,
                    "X-API-KEY": self.api_key,
                }
            ),
            params=drop_none_values(
                {
                    "owner_id": owner_id,
                    "fields": fields,
                    "external": external,
                    "force_refresh": force_refresh,
                    "schema": schema_value,
                    "stale_delta": stale_delta,
                    "ref": reference,
                    **options,
                }
            ),
            timeout=timeout,
            follow_redirects=True,
        )

        res.raise_for_status()

        res_json = res.json()
        res_data = res_json and res_json.get("data")

        if res_data and schema_class:
            Product = schema_to_product[schema_class]  # pylint: disable=invalid-name

            res_json["data"] = Product(**res_data)

        return res_json

    @retry(
        reraise=retry_settings.reraise,
        retry=retry_settings.retry,
        stop=retry_settings.stop,
        wait=retry_settings.wait,
    )
    def create_product(
        self,
        data: PartInV0,
        schema: Optional[Union[ProductSchemaName, str]] = None,
        timeout: Optional[int] = None,
        reference: Optional[str] = None,
        options: Optional[Dict] = None,
        fields: Optional[str] = None,
    ):
        """Create product.

        Args:
            data: Data defining the product to create.
            schema: Response schema.
            timeout: Time to wait (in seconds) for the server to issue a response.
            reference: Arbitrary note to associate with the request.
            options: Extra configuration options.
            fields: Used to filter properties that the response should contain. A field can be a
                concrete property like "mpn" or an abstract group of properties like "assembly".
                Example: "id,aliases,labels,statements{spec,assembly},offers"

        Returns:
            The newly created product, represented in the given schema.
        """

        if not schema:
            schema = self.default_product_schema

        schema_class: Optional[ProductSchemaName] = (
            schema if isinstance(schema, ProductSchemaName) else None
        )

        if (schema_class and fields) and (
            schema_class is not ProductSchemaName.INTERNAL
        ):
            raise ValueError(
                "Field expansion is not supported for the targeted schema."
            )

        schema_value = schema_class.value if schema_class else schema

        options = options or {}

        res = httpx.post(
            f"{self.url}/products/",
            json=data,
            headers=drop_none_values(
                {
                    "X-CLIENT-ID": self.client_id,
                    "X-API-KEY": self.api_key,
                }
            ),
            params=drop_none_values(
                {"schema": schema_value, "fields": fields, "ref": reference, **options}
            ),
            timeout=timeout,
            follow_redirects=True,
        )

        res.raise_for_status()

        res_json = res.json()
        res_data = res_json and res_json.get("data")

        if res_data and schema_class:
            Product = schema_to_product[schema_class]  # pylint: disable=invalid-name

            res_json["data"] = (
                Product(**res_json["data"]) if (res_json and res_data) else None
            )

        return res_json

    @retry(
        reraise=retry_settings.reraise,
        retry=retry_settings.retry,
        stop=retry_settings.stop,
        wait=retry_settings.wait,
    )
    def update_product(
        self,
        product_id: str,
        data: PartialPartInV0,
        timeout: Optional[int] = None,
        owner_id: Optional[str] = None,
        reference: Optional[str] = None,
        options: Optional[Dict] = None,
    ):
        """Update product.

        Args:
            product_id: Cofactr ID of product to update.
            data: Data defining product updates. A value of `None` represents delete.
            timeout: Time to wait (in seconds) for the server to issue a response.
            owner_id: Data owner ID.
            reference: Arbitrary note to associate with the request.
            options: Extra configuration options.
        """

        options = options or {}

        res = httpx.patch(
            f"{self.url}/products/{product_id}",
            json={
                "owner_id": owner_id,
                "schema": "flagship",
                "data": data,
            },
            headers=drop_none_values(
                {
                    "X-CLIENT-ID": self.client_id,
                    "X-API-KEY": self.api_key,
                }
            ),
            params=drop_none_values({"ref": reference, **options}),
            timeout=timeout,
            follow_redirects=True,
        )

        res.raise_for_status()

    @retry(
        reraise=retry_settings.reraise,
        retry=retry_settings.retry,
        stop=retry_settings.stop,
        wait=retry_settings.wait,
    )
    def set_custom_product_ids(
        self,
        id_to_custom_id: Dict[str, Optional[str]],
        timeout: Optional[int] = None,
        owner_id: Optional[str] = None,
        reference: Optional[str] = None,
        options: Optional[Dict] = None,
    ):
        """Set custom product IDs.

        Args:
            id_to_custom_id: Map from Cofactr product ID to desired custom ID.
            timeout: Time to wait (in seconds) for the server to issue a response.
            owner_id: Data owner ID.
            reference: Arbitrary note to associate with the request.
            options: Extra configuration options.
        """

        if not id_to_custom_id:
            return

        options = options or {}

        res = httpx.post(
            f"{self.url}/actions/custom-product-id-mappings/",
            json={
                "owner_id": owner_id,
                "id_to_custom_id": id_to_custom_id,
            },
            headers=drop_none_values(
                {
                    "X-CLIENT-ID": self.client_id,
                    "X-API-KEY": self.api_key,
                }
            ),
            params=drop_none_values({"ref": reference, **options}),
            timeout=timeout,
            follow_redirects=True,
        )

        res.raise_for_status()

    @retry(
        reraise=retry_settings.reraise,
        retry=retry_settings.retry,
        stop=retry_settings.stop,
        wait=retry_settings.wait,
    )
    def get_offers(
        self,
        product_id: str,
        fields: Optional[str] = None,
        external: Optional[bool] = True,
        force_refresh: bool = False,
        schema: Optional[Union[OfferSchemaName, str]] = None,
        timeout: Optional[int] = None,
        owner_id: Optional[str] = None,
        stale_delta: Optional[str] = None,
        reference: Optional[str] = None,
        options: Optional[Dict] = None,
    ):
        """Get product.

        Args:
            product_id: ID of the product to get offers for.
            fields: Used to filter properties that the response should contain.
            external: Whether to query external sources in order to update information.
            force_refresh: Whether to force re-ingestion from external sources. Overrides
                `external`.
            schema: Response schema.
            timeout: Time to wait (in seconds) for the server to issue a response.
            owner_id: Specifies which private data to access.
            stale_delta: How much time has to pass before data is treated as stale. Use "inf" or
                "infinite" to indicate data should not be refreshed, no matter how old.
                Examples: "5h", "1d", "1w", "inf"
            reference: Arbitrary note to associate with the request.
            options: Extra configuration options.
        """

        if not schema:
            schema = self.default_offer_schema

        options = options or {}

        schema_class: Optional[OfferSchemaName] = (
            schema if isinstance(schema, OfferSchemaName) else None
        )

        if (schema_class and fields) and (schema_class is not OfferSchemaName.INTERNAL):
            raise ValueError(
                "Field expansion is not supported for the targeted schema."
            )

        schema_value = schema_class.value if schema_class else schema

        res = httpx.get(
            f"{self.url}/products/{product_id}/offers",
            headers=drop_none_values(
                {
                    "X-CLIENT-ID": self.client_id,
                    "X-API-KEY": self.api_key,
                }
            ),
            params=drop_none_values(
                {
                    "owner_id": owner_id,
                    "fields": fields,
                    "external": external,
                    "force_refresh": force_refresh,
                    "schema": schema_value,
                    "stale_delta": stale_delta,
                    "ref": reference,
                    **options,
                }
            ),
            timeout=timeout,
            follow_redirects=True,
        )

        res.raise_for_status()

        res_json = res.json()
        res_data = res_json and res_json.get("data")

        if res_json and schema_class:
            Offer = schema_to_offer[schema_class]  # pylint: disable=invalid-name

            res_json["data"] = [Offer(**data) for data in res_data]

        return res_json

    @retry(
        reraise=retry_settings.reraise,
        retry=retry_settings.retry,
        stop=retry_settings.stop,
        wait=retry_settings.wait,
    )
    def get_org(
        self,
        id: str,
        schema: Optional[Union[OrgSchemaName, str]] = None,
        timeout: Optional[int] = None,
        owner_id: Optional[str] = None,
    ):
        """Get organization."""

        if not schema:
            schema = self.default_org_schema

        schema_class: Optional[OrgSchemaName] = (
            schema if isinstance(schema, OrgSchemaName) else None
        )
        schema_value = schema_class.value if schema_class else schema

        res = httpx.get(
            f"{self.url}/orgs/{id}",
            headers=drop_none_values(
                {
                    "X-CLIENT-ID": self.client_id,
                    "X-API-KEY": self.api_key,
                }
            ),
            params=drop_none_values({"owner_id": owner_id, "schema": schema_value}),
            timeout=timeout,
            follow_redirects=True,
        )

        res.raise_for_status()

        res_json = res.json()
        res_data = res_json and res_json.get("data")

        if res_json and schema_class:
            Org = schema_to_org[schema_class]  # pylint: disable=invalid-name

            res_json["data"] = (
                Org(**res_json["data"]) if (res_json and res_data) else None
            )

        return res_json

    @retry(
        reraise=retry_settings.reraise,
        retry=retry_settings.retry,
        stop=retry_settings.stop,
        wait=retry_settings.wait,
    )
    def get_supplier(
        self,
        id: str,
        schema: Optional[Union[SupplierSchemaName, str]] = None,
        timeout: Optional[int] = None,
        owner_id: Optional[str] = None,
    ):
        """Get supplier."""

        if not schema:
            schema = self.default_supplier_schema

        schema_class: Optional[SupplierSchemaName] = (
            schema if isinstance(schema, SupplierSchemaName) else None
        )
        schema_value = schema_class.value if schema_class else schema

        res = httpx.get(
            f"{self.url}/orgs/{id}",
            headers=drop_none_values(
                {
                    "X-CLIENT-ID": self.client_id,
                    "X-API-KEY": self.api_key,
                }
            ),
            params=drop_none_values({"owner_id": owner_id, "schema": schema_value}),
            timeout=timeout,
            follow_redirects=True,
        )

        res.raise_for_status()

        res_json = res.json()
        res_data = res_json and res_json.get("data")

        if res_data and schema_class:
            Supplier = schema_to_supplier[schema_class]  # pylint: disable=invalid-name

            res_json["data"] = (
                Supplier(**res_json["data"])
                if (res_json and res_json.get("data"))
                else None
            )

        return res_json

    @retry(
        reraise=retry_settings.reraise,
        retry=retry_settings.retry,
        stop=retry_settings.stop,
        wait=retry_settings.wait,
    )
    def get_orders(
        self,
        schema: Optional[Union[OrderSchemaName, str]] = None,
        timeout: Optional[int] = None,
        filtering: Optional[List[Dict]] = None,
        owner_id: Optional[str] = None,
        is_sandbox: bool = False,
    ):
        """Get orders.

        Args:
            schema: Response schema.
            timeout: Time to wait (in seconds) for the server to issue a response.
            filtering: Filter orders.
                Example: `[{"field":"id","operator":"IN","value":["622fb450e4c292d8287b0af5:12345678"]}]`.
            owner_id: Specifies which private data to access.
            is_sandbox: If True, the order will be executed in a sandbox environment: Real orders
                will not be queried.
        """

        if not schema:
            schema = self.default_order_schema

        schema_class: Optional[OrderSchemaName] = (
            schema if isinstance(schema, OrderSchemaName) else None
        )
        schema_value = schema_class.value if schema_class else schema

        res = httpx.get(
            f"{self.url}/orders/",
            headers=drop_none_values(
                {
                    "X-CLIENT-ID": self.client_id,
                    "X-API-KEY": self.api_key,
                }
            ),
            params=drop_none_values(
                {
                    "owner_id": owner_id,
                    "external": True,
                    "schema": schema_value,
                    "filtering": json.dumps(filtering) if filtering else None,
                    "is_sandbox": is_sandbox,
                }
            ),
            timeout=timeout,
            follow_redirects=True,
        )

        res.raise_for_status()

        res_json = res.json()
        res_data = res_json.get("data")

        if res_data and schema_class:
            Order = schema_to_order[schema_class]  # pylint: disable=invalid-name

            res_json["data"] = [Order(**data) for data in res_data]

        return res_json

    def get_orders_by_ids(
        self,
        ids: List[str],
        schema: Optional[Union[OrderSchemaName, str]] = None,
        timeout: Optional[int] = None,
        owner_id: Optional[str] = None,
        is_sandbox: bool = False,
    ):
        """Get a batch of orders by IDs.

        Args:
            ids: Cofactr order IDs to match on.
            schema: Response schema.
            timeout: Time to wait (in seconds) for the server to issue a response.
            owner_id: Specifies which private data to access.
            is_sandbox: If True, the order will be executed in a sandbox environment: Real orders
                will not be queried.
        """

        if not ids:
            return {}

        if not schema:
            schema = self.default_order_schema

        schema_class: Optional[OrderSchemaName] = (
            schema if isinstance(schema, OrderSchemaName) else None
        )

        batched_orders = [
            self.get_orders(
                schema=schema,
                filtering=[{"field": "id", "operator": "IN", "value": batched_ids}],
                timeout=timeout,
                owner_id=owner_id,
                is_sandbox=is_sandbox,
            )
            for batched_ids in batched(ids, n=_MAX_BATCH_SIZE)
        ]

        orders = list(flatten([res["data"] for res in batched_orders]))

        get_ids = _get_ids_from_class if schema_class else _get_ids_from_dict

        id_to_order = {id_: order for order in orders for id_ in get_ids(entity=order)}
        target_id_to_order = {
            id_: id_to_order[id_] for id_ in ids if id_ in id_to_order
        }

        return target_id_to_order

    def create_order(
        self,
        data: OrderInV0,
        timeout: Optional[int] = None,
        is_sandbox: bool = False,
    ):
        """Create order.

        Args:
            data: Data defining the order to create.
            timeout: Time to wait (in seconds) for the server to issue a response.
            is_sandbox: If True, the order will be executed in a sandbox environment: A real order
                will not be placed.

        Returns:
            ID of the created order.
        """

        res = httpx.post(
            f"{self.url}/orders/",
            headers=drop_none_values(
                {
                    "X-CLIENT-ID": self.client_id,
                    "X-API-KEY": self.api_key,
                }
            ),
            json=data,
            params=drop_none_values(
                {
                    "is_sandbox": is_sandbox,
                }
            ),
            timeout=timeout,
            follow_redirects=True,
        )

        res.raise_for_status()

        location = res.headers.get("location")

        if not location:
            raise ValueError("No resource location found in order creation response.")

        # Remove `/orders/` to get the ID from the resource path.
        return location[8:]

    def create_get_products_by_ids_job(
        self,
        ids: List[str],
        external: Optional[bool] = True,
        force_refresh: bool = False,
        schema: Optional[Union[ProductSchemaName, str]] = None,
        timeout: Optional[int] = None,
        owner_id: Optional[str] = None,
        stale_delta: Optional[str] = None,
        reference: Optional[str] = None,
        options: Optional[dict] = None,
        fields: Optional[str] = None,
    ) -> List[str]:
        """Create batch product request job.

        Note: Multiple jobs are created if more than 250 IDs are provided.

        Args:
            ids: Cofactr product IDs to match on.
            external: Whether to query external sources in order to refresh data if applicable.
            force_refresh: Whether to force re-ingestion from external sources. Overrides
                `external`.
            schema: Response schema.
            timeout: Time to wait (in seconds) for the server to issue a response.
            owner_id: Specifies which private data to access.
            stale_delta: How much time has to pass before data is treated as stale. Use "inf" or
                "infinite" to indicate data should not be refreshed, no matter how old.
                Examples: "5h", "1d", "1w", "inf"
            reference: Arbitrary note to associate with the request.
            options: Extra configuration options.
            fields: Used to filter properties that the response should contain. A field can be a
                concrete property like "mpn" or an abstract group of properties like "assembly".
                Example: "id,aliases,labels,statements{spec,assembly},offers"

        Returns:
            A list with one ID for each job that was created.
        """

        if not schema:
            schema = self.default_product_schema

        schema_class: Optional[ProductSchemaName] = (
            schema if isinstance(schema, ProductSchemaName) else None
        )

        if (schema_class and fields) and (
            schema_class is not ProductSchemaName.INTERNAL
        ):
            raise ValueError(
                "Field expansion is not supported for the targeted schema."
            )

        schema_value = schema_class.value if schema_class else schema

        options = options or {}

        invariant_query_params = drop_none_values(
            {
                "schema": schema_value,
                "external": bool(external),
                "force_refresh": force_refresh,
                "stale_delta": stale_delta,
                "fields": fields,
            }
        )

        job_ids = []

        for id_batch in batched(ids, n=_MAX_BATCH_SIZE):
            res = httpx.post(
                f"{self.url}/jobs/batch-products-requests/",
                headers=drop_none_values(
                    {
                        "X-CLIENT-ID": self.client_id,
                        "X-API-KEY": self.api_key,
                    }
                ),
                json={
                    "batch": [
                        {
                            "method": "GET",
                            "relative_url": (
                                f"?filtering={filtering}&{urlencode(invariant_query_params)}"
                            ),
                        }
                        for ids_ in batched(id_batch, n=_MAX_SUB_BATCH_SIZE)
                        if (
                            filtering := quote(
                                json.dumps(
                                    [{"field": "id", "operator": "IN", "value": ids_}]
                                )
                            )
                        )
                    ]
                },
                params=drop_none_values(
                    {"owner_id": owner_id, "ref": reference, **options}
                ),
                timeout=timeout,
                follow_redirects=True,
            )
            res.raise_for_status()

            location = res.headers.get("location")

            if not location:
                raise ValueError("No resource location found in job creation response.")

            # Remove `/jobs/` to get the ID from the resource path.
            job_ids.append(location[6:])

        return job_ids
