1. Bump version in `pyproject.toml` and `manifest.json`
1. Deploy to staging (use API token from TestPyPI
```
cd composer-trade-mcp
rm -r dist; uv build; uv publish --publish-url https://test.pypi.org/legacy/
```
1. Deploy to prod (use API token from PyPI)
```
cd composer-trade-mcp
rm -r dist; uv build; uv publish
```
1. Generate DXT
```
npx @anthropic-ai/dxt pack
```
1. Upload `composer-trade-mcp.dxt` to [Google Cloud Storage](https://console.cloud.google.com/storage/browser/www.investcomposer.com/downloads;tab=objects?hl=en&inv=1&invt=Ab1spg&project=leverheads-278521&prefix=&forceOnObjectsSortingFiltering=false)
