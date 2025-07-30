"""Schema definitions."""
# Standard Modules
from enum import Enum
from typing import Callable, Dict

# Local Modules
from cofactr.helpers import identity
from cofactr.schema.flagship import (
    FlagshipOffer,
    FlagshipOrderStatus,
    FlagshipPart,
    FlagshipSeller,
)
from cofactr.schema.flagship_v2 import (
    FlagshipV2Offer,
    FlagshipV2OrderStatus,
    FlagshipV2Part,
    FlagshipV2Seller,
)
from cofactr.schema.flagship_v3 import FlagshipV3Offer, FlagshipV3Part, FlagshipV3Seller
from cofactr.schema.flagship_v4 import FlagshipV4Part, FlagshipV4Offer, FlagshipV4Seller
from cofactr.schema.flagship_v5 import FlagshipV5Offer, FlagshipV5Part, FlagshipV5Seller
from cofactr.schema.flagship_v6 import FlagshipV6Offer, FlagshipV6Part, FlagshipV6Seller
from cofactr.schema.flagship_v7 import FlagshipV7Offer, FlagshipV7Part, FlagshipV7Seller
from cofactr.schema.flagship_v8 import FlagshipV8Offer, FlagshipV8Seller
from cofactr.schema.flagship_v9 import FlagshipV9Offer
from cofactr.schema.flagship_alts_v0 import FlagshipAltsV0Part
from cofactr.schema.flagship_cache_v0 import FlagshipCacheV0Part
from cofactr.schema.flagship_cache_v1 import FlagshipCacheV1Part
from cofactr.schema.flagship_cache_v2 import FlagshipCacheV2Part
from cofactr.schema.flagship_cache_v3 import FlagshipCacheV3Part
from cofactr.schema.flagship_cache_v4 import FlagshipCacheV4Part
from cofactr.schema.flagship_cache_v5 import FlagshipCacheV5Part
from cofactr.schema.flagship_cache_v6 import FlagshipCacheV6Part
from cofactr.schema.logistics import LogisticsOffer, LogisticsPart
from cofactr.schema.logistics_v2 import (
    LogisticsV2Part,
    LogisticsV2Offer,
    LogisticsV2Seller,
)
from cofactr.schema.logistics_v3 import LogisticsV3Part
from cofactr.schema.logistics_v4 import LogisticsV4Part
from cofactr.schema.price_solver_v0 import PriceSolverV0Part
from cofactr.schema.price_solver_v1 import PriceSolverV1Part
from cofactr.schema.price_solver_v2 import PriceSolverV2Part
from cofactr.schema.price_solver_v3 import PriceSolverV3Part
from cofactr.schema.price_solver_v4 import PriceSolverV4Part
from cofactr.schema.price_solver_v5 import PriceSolverV5Part
from cofactr.schema.price_solver_v6 import PriceSolverV6Part
from cofactr.schema.price_solver_v7 import PriceSolverV7Part
from cofactr.schema.price_solver_v8 import PriceSolverV8Part
from cofactr.schema.price_solver_v9 import PriceSolverV9Part
from cofactr.schema.price_solver_v10 import PriceSolverV10Part
from cofactr.schema.price_solver_v11 import PriceSolverV11Part


class ProductSchemaName(str, Enum):
    """Product schema name."""

    INTERNAL = "internal"
    FLAGSHIP = "flagship"
    FLAGSHIP_V2 = "flagship-v2"
    FLAGSHIP_V3 = "flagship-v3"
    FLAGSHIP_V4 = "flagship-v4"
    FLAGSHIP_V5 = "flagship-v5"
    FLAGSHIP_V6 = "flagship-v6"
    FLAGSHIP_V7 = "flagship-v7"
    FLAGSHIP_ALTS_V0 = "flagship-alts-v0"
    FLAGSHIP_CACHE_V0 = "flagship-cache-v0"
    FLAGSHIP_CACHE_V1 = "flagship-cache-v1"
    FLAGSHIP_CACHE_V2 = "flagship-cache-v2"
    FLAGSHIP_CACHE_V3 = "flagship-cache-v3"
    FLAGSHIP_CACHE_V4 = "flagship-cache-v4"
    FLAGSHIP_CACHE_V5 = "flagship-cache-v5"
    FLAGSHIP_CACHE_V6 = "flagship-cache-v6"
    LOGISTICS = "logistics"
    LOGISTICS_V2 = "logistics-v2"
    LOGISTICS_V3 = "logistics-v3"
    LOGISTICS_V4 = "logistics-v4"
    PRICE_SOLVER_V0 = "price-solver-v0"
    PRICE_SOLVER_V1 = "price-solver-v1"
    PRICE_SOLVER_V2 = "price-solver-v2"
    PRICE_SOLVER_V3 = "price-solver-v3"
    PRICE_SOLVER_V4 = "price-solver-v4"
    PRICE_SOLVER_V5 = "price-solver-v5"
    PRICE_SOLVER_V6 = "price-solver-v6"
    PRICE_SOLVER_V7 = "price-solver-v7"
    PRICE_SOLVER_V8 = "price-solver-v8"
    PRICE_SOLVER_V9 = "price-solver-v9"
    PRICE_SOLVER_V10 = "price-solver-v10"
    PRICE_SOLVER_V11 = "price-solver-v11"


schema_to_product: Dict[ProductSchemaName, Callable] = {
    ProductSchemaName.FLAGSHIP: FlagshipPart,
    ProductSchemaName.FLAGSHIP_V2: FlagshipV2Part,
    ProductSchemaName.FLAGSHIP_V3: FlagshipV3Part,
    ProductSchemaName.FLAGSHIP_V4: FlagshipV4Part,
    ProductSchemaName.FLAGSHIP_V5: FlagshipV5Part,
    ProductSchemaName.FLAGSHIP_V6: FlagshipV6Part,
    ProductSchemaName.FLAGSHIP_V7: FlagshipV7Part,
    ProductSchemaName.FLAGSHIP_ALTS_V0: FlagshipAltsV0Part,
    ProductSchemaName.FLAGSHIP_CACHE_V0: FlagshipCacheV0Part,
    ProductSchemaName.FLAGSHIP_CACHE_V1: FlagshipCacheV1Part,
    ProductSchemaName.FLAGSHIP_CACHE_V2: FlagshipCacheV2Part,
    ProductSchemaName.FLAGSHIP_CACHE_V3: FlagshipCacheV3Part,
    ProductSchemaName.FLAGSHIP_CACHE_V4: FlagshipCacheV4Part,
    ProductSchemaName.FLAGSHIP_CACHE_V5: FlagshipCacheV5Part,
    ProductSchemaName.FLAGSHIP_CACHE_V6: FlagshipCacheV6Part,
    ProductSchemaName.LOGISTICS: LogisticsPart,
    ProductSchemaName.LOGISTICS_V2: LogisticsV2Part,
    ProductSchemaName.LOGISTICS_V3: LogisticsV3Part,
    ProductSchemaName.LOGISTICS_V4: LogisticsV4Part,
    ProductSchemaName.PRICE_SOLVER_V0: PriceSolverV0Part,
    ProductSchemaName.PRICE_SOLVER_V1: PriceSolverV1Part,
    ProductSchemaName.PRICE_SOLVER_V2: PriceSolverV2Part,
    ProductSchemaName.PRICE_SOLVER_V3: PriceSolverV3Part,
    ProductSchemaName.PRICE_SOLVER_V4: PriceSolverV4Part,
    ProductSchemaName.PRICE_SOLVER_V5: PriceSolverV5Part,
    ProductSchemaName.PRICE_SOLVER_V6: PriceSolverV6Part,
    ProductSchemaName.PRICE_SOLVER_V7: PriceSolverV7Part,
    ProductSchemaName.PRICE_SOLVER_V8: PriceSolverV8Part,
    ProductSchemaName.PRICE_SOLVER_V9: PriceSolverV9Part,
    ProductSchemaName.PRICE_SOLVER_V10: PriceSolverV10Part,
    ProductSchemaName.PRICE_SOLVER_V11: PriceSolverV11Part,
}


class OfferSchemaName(str, Enum):
    """Offer schema name."""

    INTERNAL = "internal"
    FLAGSHIP = "flagship"
    FLAGSHIP_V2 = "flagship-v2"
    FLAGSHIP_V3 = "flagship-v3"
    FLAGSHIP_V4 = "flagship-v4"
    FLAGSHIP_V5 = "flagship-v5"
    FLAGSHIP_V6 = "flagship-v6"
    FLAGSHIP_V7 = "flagship-v7"
    FLAGSHIP_V8 = "flagship-v8"
    FLAGSHIP_V9 = "flagship-v9"
    LOGISTICS = "logistics"
    LOGISTICS_V2 = "logistics-v2"


schema_to_offer: Dict[OfferSchemaName, Callable] = {
    OfferSchemaName.INTERNAL: identity,
    OfferSchemaName.FLAGSHIP: FlagshipOffer,
    OfferSchemaName.FLAGSHIP_V2: FlagshipV2Offer,
    OfferSchemaName.FLAGSHIP_V3: FlagshipV3Offer,
    OfferSchemaName.FLAGSHIP_V4: FlagshipV4Offer,
    OfferSchemaName.FLAGSHIP_V5: FlagshipV5Offer,
    OfferSchemaName.FLAGSHIP_V6: FlagshipV6Offer,
    OfferSchemaName.FLAGSHIP_V7: FlagshipV7Offer,
    OfferSchemaName.FLAGSHIP_V8: FlagshipV8Offer,
    OfferSchemaName.FLAGSHIP_V9: FlagshipV9Offer,
    OfferSchemaName.LOGISTICS: LogisticsOffer,
    OfferSchemaName.LOGISTICS_V2: LogisticsV2Offer,
}


class OrgSchemaName(str, Enum):
    """Organization schema name."""

    INTERNAL = "internal"
    FLAGSHIP = "flagship"
    FLAGSHIP_V2 = "flagship-v2"
    FLAGSHIP_V3 = "flagship-v3"
    FLAGSHIP_V4 = "flagship-v4"
    FLAGSHIP_V5 = "flagship-v5"
    FLAGSHIP_V6 = "flagship-v6"
    FLAGSHIP_V7 = "flagship-v7"
    FLAGSHIP_V8 = "flagship-v8"
    LOGISTICS = "logistics"
    LOGISTICS_V2 = "logistics-v2"


schema_to_org: Dict[OrgSchemaName, Callable] = {
    OrgSchemaName.INTERNAL: identity,
    OrgSchemaName.FLAGSHIP: FlagshipSeller,
    OrgSchemaName.FLAGSHIP_V2: FlagshipV2Seller,
    OrgSchemaName.FLAGSHIP_V3: FlagshipV3Seller,
    OrgSchemaName.FLAGSHIP_V4: FlagshipV4Seller,
    OrgSchemaName.FLAGSHIP_V5: FlagshipV5Seller,
    OrgSchemaName.FLAGSHIP_V6: FlagshipV6Seller,
    OrgSchemaName.FLAGSHIP_V7: FlagshipV7Seller,
    OrgSchemaName.FLAGSHIP_V8: FlagshipV8Seller,
    OrgSchemaName.LOGISTICS: FlagshipSeller,
    OrgSchemaName.LOGISTICS_V2: LogisticsV2Seller,
}


class SupplierSchemaName(str, Enum):
    """Supplier schema name."""

    INTERNAL = "internal"
    FLAGSHIP = "flagship"
    FLAGSHIP_V2 = "flagship-v2"
    FLAGSHIP_V3 = "flagship-v3"
    FLAGSHIP_V4 = "flagship-v4"
    FLAGSHIP_V5 = "flagship-v5"
    FLAGSHIP_V6 = "flagship-v6"
    FLAGSHIP_V7 = "flagship-v7"
    FLAGSHIP_V8 = "flagship-v8"
    LOGISTICS = "logistics"
    LOGISTICS_V2 = "logistics-v2"


schema_to_supplier: Dict[SupplierSchemaName, Callable] = {
    SupplierSchemaName.INTERNAL: identity,
    SupplierSchemaName.FLAGSHIP: FlagshipSeller,
    SupplierSchemaName.FLAGSHIP_V2: FlagshipV2Seller,
    SupplierSchemaName.FLAGSHIP_V3: FlagshipV3Seller,
    SupplierSchemaName.FLAGSHIP_V4: FlagshipV4Seller,
    SupplierSchemaName.FLAGSHIP_V5: FlagshipV5Seller,
    SupplierSchemaName.FLAGSHIP_V6: FlagshipV6Seller,
    SupplierSchemaName.FLAGSHIP_V7: FlagshipV7Seller,
    SupplierSchemaName.FLAGSHIP_V8: FlagshipV8Seller,
    SupplierSchemaName.LOGISTICS: FlagshipSeller,
    SupplierSchemaName.LOGISTICS_V2: LogisticsV2Seller,
}


class OrderSchemaName(str, Enum):
    """Order schema name."""

    FLAGSHIP = "flagship"
    FLAGSHIP_V2 = "flagship-v2"


schema_to_order: Dict[OrderSchemaName, Callable] = {
    OrderSchemaName.FLAGSHIP: FlagshipOrderStatus,
    OrderSchemaName.FLAGSHIP_V2: FlagshipV2OrderStatus,
}
