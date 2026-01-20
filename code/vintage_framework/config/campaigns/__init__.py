"""
Campaign Configurations
=======================

Each product has its own configuration file defining:
- Campaign MNEs and their metadata
- Success type and measurement logic
- Data source specifications
- Filter criteria

To add a new product:
1. Create a new file (e.g., credit_card.py)
2. Define CAMPAIGN_CONFIG dict following the pattern in vvd.py
3. Import in this __init__.py
"""

from .vvd import CAMPAIGN_CONFIG as VVD_CAMPAIGNS

# Registry of all campaign configs by product
CAMPAIGN_REGISTRY = {
    "VVD": VVD_CAMPAIGNS,
    # Future: Add more products here
    # "CC": CC_CAMPAIGNS,
    # "MTG": MTG_CAMPAIGNS,
}


def get_campaign_config(product: str, mne: str) -> dict:
    """
    Retrieve configuration for a specific campaign.

    Args:
        product: Product code (e.g., "VVD")
        mne: Campaign mnemonic (e.g., "VCN")

    Returns:
        Campaign configuration dictionary

    Raises:
        KeyError: If product or MNE not found
    """
    if product not in CAMPAIGN_REGISTRY:
        raise KeyError(f"Product '{product}' not found. Available: {list(CAMPAIGN_REGISTRY.keys())}")

    campaigns = CAMPAIGN_REGISTRY[product]

    if mne not in campaigns:
        raise KeyError(f"MNE '{mne}' not found for product '{product}'. Available: {list(campaigns.keys())}")

    return campaigns[mne]


def list_campaigns(product: str = None) -> dict:
    """
    List available campaigns.

    Args:
        product: Optional product filter

    Returns:
        Dictionary of campaigns (filtered by product if specified)
    """
    if product:
        return {product: list(CAMPAIGN_REGISTRY.get(product, {}).keys())}
    return {p: list(c.keys()) for p, c in CAMPAIGN_REGISTRY.items()}
