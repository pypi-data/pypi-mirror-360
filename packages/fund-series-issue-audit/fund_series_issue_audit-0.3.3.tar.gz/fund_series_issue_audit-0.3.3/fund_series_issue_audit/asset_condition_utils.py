from .audit_asset import AssetVectors

ASSET_VECTORS = AssetVectors()

def get_asset_vector_string(fund_code, assets=ASSET_VECTORS):
    try:
        av_str = str(assets.vector[str(fund_code)])
    except:
        av_str = None
    return av_str