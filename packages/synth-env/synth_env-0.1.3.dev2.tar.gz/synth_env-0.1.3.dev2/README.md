# Synth Monorepo

git subtree add --prefix=synth-sdk git@github.com:synth-laboratories/synth-python-sdk.git main --squash
git subtree add --prefix=synth-ai git@github.com:synth-laboratories/synth-ai.git main --squash
git subtree add --prefix=docs git@github.com:synth-laboratories/mintlify-docs.git main --squash

pip install -e synth-ai

bash backend/scripts/local_install.sh
bash backend/scripts/provision-resource.sh local-setup --with-research


supabase gen types typescript --local --schema public,auth > types_db.ts

mv types_db.ts /Users/joshuapurtell/Documents/GitHub/frontend/src/types_db.ts

git submodule update --remote contracts

#uv add --package backend python-multipart 


TESTING / CI+CD
cd backend && uv pip install -e '.[research]'


LOGGING


CODE PRIORITIES



mypy

code cov