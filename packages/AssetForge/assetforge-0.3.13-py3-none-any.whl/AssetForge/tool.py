import AssetForge

if __name__ == "__main__":
    tools = [AssetForge.common.LinkingTool(), AssetForge.common.CopyingTool(), AssetForge.common.CompressionTool()]
    AssetForge.common.main_func(tools)